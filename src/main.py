# filepath: /document-extraction-system/document-extraction-system/src/main.py

import os
import json
import sys
import glob
import time
from pdf_extractor import PDFExtractor
from llm_client import LLMClient
from json_handler import JSONHandler
from batch_processor import BatchDocumentProcessor, find_pdf_files
from config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL_NAME, EXTRACTION_PROMPT, DEFAULT_OUTPUT_DIR, MAX_WORKERS

def test_pdf_extraction(pdf_path):
    """Test function to check PDF extraction output"""
    start_time = time.time()
    
    pdf_extractor = PDFExtractor(pdf_path)
    extracted_text = pdf_extractor.extract_text()
    
    print(f"PDF file: {pdf_path}")
    print(f"Extracted text length: {len(extracted_text)} characters")
    print("\nExtracted text preview:")
    print("=" * 80)
    print(extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text)
    print("=" * 80)
    
    # Save to debug file
    with open("extracted_text_debug.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)
    print("\nFull extracted text saved to 'extracted_text_debug.txt'")
    
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"\n⏱️ Processed 1 PDF, took {processing_time:.2f} seconds")

def process_single_pdf(pdf_path):
    """Process a single PDF file"""
    try:
        print(f"\nProcessing: {pdf_path}")
        print("-" * 60)
        
        # Generate output path
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = f"{DEFAULT_OUTPUT_DIR}/{pdf_name}_output.json"
        
        # Step 1: Extract text from PDF
        pdf_extractor = PDFExtractor(pdf_path)
        extracted_text = pdf_extractor.extract_text()
        
        print(f"Extracted text length: {len(extracted_text)} characters")

        # Step 2: Send extracted text to LLM
        llm_client = LLMClient(DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL_NAME)
        response = llm_client.send_request(extracted_text, EXTRACTION_PROMPT)

        # Step 3: Save response to JSON file
        json_handler = JSONHandler()
        json_handler.save_to_json(response, output_path)
        
        if response.get("success"):
            print(f"✅ Successfully processed and saved to: {output_path}")
            return True
        else:
            print(f"❌ LLM Error: {response.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {str(e)}")
        return False

def convert_to_excel():
    """Convert all JSON outputs to Excel format"""
    start_time = time.time()
    
    json_handler = JSONHandler()
    success = json_handler.convert_outputs_to_excel(DEFAULT_OUTPUT_DIR)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    if success:
        print(f"\n🎉 Excel conversion completed successfully!")
        print(f"⏱️ Excel conversion took {processing_time:.2f} seconds")
    else:
        print(f"\n❌ Excel conversion failed!")
        print(f"⏱️ Process took {processing_time:.2f} seconds")

def preview_data():
    """Preview extracted data"""
    start_time = time.time()
    
    json_handler = JSONHandler()
    json_handler.preview_extracted_data(DEFAULT_OUTPUT_DIR)
    
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"\n⏱️ Preview completed, took {processing_time:.2f} seconds")

def process_batch_threaded(input_dir="../data/input"):
    """Process all PDF files in the input directory using multithreading"""
    print(f"🚀 Starting multi-threaded batch processing from {input_dir}")
    print("=" * 80)
    
    # Initialize batch processor
    processor = BatchDocumentProcessor(max_workers=MAX_WORKERS)
    
    # Find all PDF files
    pdf_files = find_pdf_files(input_dir)
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Process batch
    results = processor.process_batch(pdf_files)
    
    # Final summary
    successful = sum(1 for r in results if r["status"] == "success")
    llm_errors = sum(1 for r in results if r["status"] == "llm_error")
    errors = sum(1 for r in results if r["status"] in ["error", "exception"])
    
    print("\n" + "🎉" * 20)
    print("FINAL SUMMARY:")
    print("🎉" * 50)
    print(f"✅ Successful: {successful}")
    print(f"⚠️ LLM Errors: {llm_errors}")
    print(f"❌ Processing Errors: {errors}")
    print(f"📈 Success Rate: {successful/len(results)*100:.1f}%")
    print("🎉" * 50)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py <path_to_pdf_file>                    # Process single PDF")
        print("  python main.py test <path_to_pdf_file>               # Test PDF extraction")
        print("  python main.py batch [input_directory]              # Process all PDFs in directory (multi-threaded)")
        print("  python main.py excel                                 # Convert JSON outputs to Excel")
        print("  python main.py preview                               # Preview extracted data")
        sys.exit(1)
    
    # Check command type
    if sys.argv[1] == "test":
        if len(sys.argv) < 3:
            print("Usage: python main.py test <path_to_pdf_file>")
            sys.exit(1)
        test_pdf_extraction(sys.argv[2])
        return
    
    if sys.argv[1] == "batch":
        input_dir = sys.argv[2] if len(sys.argv) > 2 else "../data/input"
        process_batch_threaded(input_dir)
        return
    
    if sys.argv[1] == "excel":
        convert_to_excel()
        return
    
    if sys.argv[1] == "preview":
        preview_data()
        return
    
    # Single file processing
    start_time = time.time()
    
    pdf_path = sys.argv[1]
    
    # Generate output path
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = f"{DEFAULT_OUTPUT_DIR}/{pdf_name}_output.json"
    
    # Create output directory if it doesn't exist
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Extract text from PDF
    pdf_extractor = PDFExtractor(pdf_path)
    extracted_text = pdf_extractor.extract_text()
    
    print("=" * 50)
    print("EXTRACTED TEXT FROM PDF:")
    print("=" * 50)
    print(extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text)
    print("=" * 50)
    print(f"Text length: {len(extracted_text)} characters")
    print("=" * 50)

    # Step 2: Send extracted text to LLM
    llm_client = LLMClient(DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL_NAME)
    response = llm_client.send_request(extracted_text, EXTRACTION_PROMPT)

    # Step 3: Save response to JSON file
    json_handler = JSONHandler()
    json_handler.save_to_json(response, output_path)
    
    print(f"Output saved to: {output_path}")
    
    # Print LLM response preview
    if response.get("success"):
        print("\n" + "=" * 50)
        print("LLM RESPONSE PREVIEW:")
        print("=" * 50)
        content = response.get("content", "")
        print(content[:500] + "..." if len(content) > 500 else content)
        print("=" * 50)
    else:
        print(f"Error from LLM: {response.get('error')}")
    
    end_time = time.time()
    processing_time = end_time - start_time
    print(f"\n⏱️ Processed 1 PDF, took {processing_time:.2f} seconds")

if __name__ == "__main__":
    main()