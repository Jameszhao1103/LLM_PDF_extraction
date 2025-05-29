from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from pathlib import Path
from threading import Lock
import os
import time
import logging
import glob
import json

# Fix the imports - use relative imports since we're in the src directory
from .pdf_extractor import PDFExtractor
from .llm_client import LLMClient
from .json_handler import JSONHandler
from .config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL_NAME, EXTRACTION_PROMPT, DEFAULT_OUTPUT_DIR, MAX_WORKERS, API_RATE_LIMIT, REQUEST_DELAY

class BatchDocumentProcessor:
    def __init__(self, max_workers: int = MAX_WORKERS, output_dir: str = DEFAULT_OUTPUT_DIR):
        """
        Initialize batch processor
        
        Args:
            max_workers: Maximum number of concurrent threads
            output_dir: Directory to save results
        """
        self.max_workers = max_workers
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_lock = Lock()
        
        # Initialize clients
        self.llm_client = LLMClient(DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL_NAME)
        self.json_handler = JSONHandler()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('batch_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Rate limiting
        self.last_request_time = 0
        self.request_lock = Lock()
    
    def _rate_limit(self):
        """Apply rate limiting between API requests"""
        with self.request_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < REQUEST_DELAY:
                time.sleep(REQUEST_DELAY - time_since_last)
            self.last_request_time = time.time()
    
    def process_single_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a single PDF document
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing extraction results
        """
        try:
            self.logger.info(f"Processing: {pdf_path}")
            start_time = time.time()
            
            # Generate output path
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = self.output_dir / f"{pdf_name}_output.json"
            
            # Step 1: Extract text from PDF
            pdf_extractor = PDFExtractor(pdf_path)
            extracted_text = pdf_extractor.extract_text()
            
            if not extracted_text or len(extracted_text.strip()) == 0:
                raise Exception("No text extracted from PDF")
            
            # Step 2: Apply rate limiting and send to LLM
            self._rate_limit()
            response = self.llm_client.send_request(extracted_text, EXTRACTION_PROMPT)
            
            # Step 3: Save response to JSON file
            self.json_handler.save_to_json(response, str(output_path))
            
            processing_time = time.time() - start_time
            
            if response.get("success"):
                result = {
                    "file_name": os.path.basename(pdf_path),
                    "file_path": pdf_path,
                    "output_path": str(output_path),
                    "processing_time": processing_time,
                    "text_length": len(extracted_text),
                    "status": "success",
                    "extracted_data": response.get("content", "")
                }
                self.logger.info(f"✅ Successfully processed {pdf_path} in {processing_time:.2f}s")
            else:
                result = {
                    "file_name": os.path.basename(pdf_path),
                    "file_path": pdf_path,
                    "output_path": str(output_path),
                    "processing_time": processing_time,
                    "text_length": len(extracted_text),
                    "status": "llm_error",
                    "error": response.get("error", "Unknown LLM error")
                }
                self.logger.warning(f"⚠️ LLM error for {pdf_path}: {response.get('error')}")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = str(e)
            self.logger.error(f"❌ Error processing {pdf_path}: {error_msg}")
            return {
                "file_name": os.path.basename(pdf_path),
                "file_path": pdf_path,
                "output_path": None,
                "processing_time": processing_time,
                "text_length": 0,
                "status": "error",
                "error": error_msg
            }

    def process_batch(self, pdf_paths: List[str], save_results: bool = True) -> List[Dict[str, Any]]:
        """
        Process multiple PDF documents concurrently
        
        Args:
            pdf_paths: List of PDF file paths
            save_results: Whether to save results to files
            
        Returns:
            List of extraction results
        """
        results = []
        total_files = len(pdf_paths)
        
        if total_files == 0:
            self.logger.warning("No PDF files to process")
            return results
        
        self.logger.info(f"🚀 Starting batch processing of {total_files} files with {self.max_workers} workers")
        self.logger.info(f"📁 Output directory: {self.output_dir}")
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {executor.submit(self.process_single_document, path): path for path in pdf_paths}
            
            for future in as_completed(future_to_path):
                result = future.result()
                results.append(result)
        
        total_time = time.time() - start_time
        
        # Generate and log summary
        summary = self._generate_summary(results, total_time)
        self._log_summary(summary)
        
        if save_results:
            self._save_batch_results(results, summary)
        
        return results
    
    def process_directory(self, input_dir: str, pattern: str = "*.pdf") -> List[Dict[str, Any]]:
        """
        Process all PDF files in a directory
        
        Args:
            input_dir: Directory containing PDF files
            pattern: File pattern to match (default: "*.pdf")
            
        Returns:
            List of extraction results
        """
        pdf_pattern = os.path.join(input_dir, pattern)
        pdf_files = glob.glob(pdf_pattern)
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {input_dir}")
            return []
        
        self.logger.info(f"📂 Found {len(pdf_files)} PDF files in {input_dir}")
        return self.process_batch(pdf_files)
    
    def _save_batch_results(self, results: List[Dict[str, Any]], summary: Dict[str, Any]) -> None:
        """Save batch processing results to files"""
        timestamp = int(time.time())
        
        # Save detailed results
        detailed_file = self.output_dir / f"batch_results_{timestamp}.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save summary
        summary_file = self.output_dir / f"batch_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Results saved to: {detailed_file}")
        self.logger.info(f"📋 Summary saved to: {summary_file}")
    
    def _generate_summary(self, results: List[Dict[str, Any]], total_time: float) -> Dict[str, Any]:
        """Generate processing summary"""
        total_files = len(results)
        successful = sum(1 for r in results if r["status"] == "success")
        llm_errors = sum(1 for r in results if r["status"] == "llm_error")
        errors = sum(1 for r in results if r["status"] in ["error", "exception"])
        
        processing_times = [r.get("processing_time", 0) for r in results if r.get("processing_time")]
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        text_lengths = [r.get("text_length", 0) for r in results if r.get("text_length")]
        avg_text_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_files": total_files,
            "successful": successful,
            "llm_errors": llm_errors,
            "processing_errors": errors,
            "success_rate": f"{successful/total_files*100:.1f}%" if total_files > 0 else "0%",
            "total_processing_time": f"{total_time:.2f}s",
            "average_processing_time_per_file": f"{avg_time:.2f}s",
            "average_text_length": f"{avg_text_length:.0f} characters",
            "files_per_second": f"{total_files/total_time:.2f}" if total_time > 0 else "0",
            "failed_files": [
                {
                    "file_path": r["file_path"],
                    "error": r.get("error", "Unknown error"),
                    "status": r["status"]
                }
                for r in results if r["status"] != "success"
            ]
        }
    
    def _log_summary(self, summary: Dict[str, Any]) -> None:
        """Log processing summary"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("🎯 BATCH PROCESSING SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info(f"📊 Total files: {summary['total_files']}")
        self.logger.info(f"✅ Successful: {summary['successful']}")
        self.logger.info(f"⚠️ LLM errors: {summary['llm_errors']}")
        self.logger.info(f"❌ Processing errors: {summary['processing_errors']}")
        self.logger.info(f"📈 Success rate: {summary['success_rate']}")
        self.logger.info(f"⏱️ Total time: {summary['total_processing_time']}")
        self.logger.info(f"⚡ Average time per file: {summary['average_processing_time_per_file']}")
        self.logger.info(f"🚀 Files per second: {summary['files_per_second']}")
        self.logger.info("=" * 80)
        
        if summary['failed_files']:
            self.logger.warning(f"⚠️ {len(summary['failed_files'])} files failed to process")


def find_pdf_files(directory: str, recursive: bool = True) -> List[str]:
    """
    Find all PDF files in a directory
    
    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of PDF file paths
    """
    pdf_files = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
    else:
        pattern = os.path.join(directory, "*.pdf")
        pdf_files = glob.glob(pattern)
    
    return sorted(pdf_files)