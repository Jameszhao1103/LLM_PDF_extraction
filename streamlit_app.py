import streamlit as st
import os
import sys
import glob
import time
import json
import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Import from src (since we're in the root directory)
from src.pdf_extractor import PDFExtractor
from src.llm_client import LLMClient
from src.json_handler import JSONHandler
from src.batch_processor import BatchDocumentProcessor
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL_NAME, EXTRACTION_PROMPT, DEFAULT_OUTPUT_DIR, MAX_WORKERS

# Page configuration
st.set_page_config(
    page_title="Document Extraction System",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e8b57;
        border-bottom: 2px solid #2e8b57;
        padding-bottom: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .directory-box {
        padding: 0.5rem;
        border-radius: 0.3rem;
        background-color: #e3f2fd;
        border: 1px solid #90caf9;
        color: #0d47a1;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">📄 Document Extraction System</h1>', unsafe_allow_html=True)
    
    # Initialize session state for directory
    if 'input_directory' not in st.session_state:
        st.session_state.input_directory = "./data/input"
    
    if 'output_directory' not in st.session_state:
        st.session_state.output_directory = DEFAULT_OUTPUT_DIR
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown('<h2 class="section-header">⚙️ Configuration</h2>', unsafe_allow_html=True)
        
        # API Configuration
        api_key = st.text_input("DeepSeek API Key", value=DEEPSEEK_API_KEY, type="password")
        api_url = st.text_input("API URL", value=DEEPSEEK_API_URL)
        model_name = st.text_input("Model Name", value=MODEL_NAME)
        
        st.markdown("---")
        
        # Directory settings
        st.markdown("### 📁 Directory Settings")
        
        # Input Directory Selection
        st.markdown("**Input Directory:**")
        input_dir_display = st.text_input(
            "Input Directory", 
            value=st.session_state.input_directory,
            key="input_dir_text",
            help="Enter the path to your PDF files directory"
        )
        
        # Output Directory Selection
        st.markdown("**Output Directory:**")
        output_dir_display = st.text_input(
            "Output Directory", 
            value=st.session_state.output_directory,
            key="output_dir_text",
            help="Enter the path where results will be saved"
        )
        
        # Update session state if text was manually changed
        if input_dir_display != st.session_state.input_directory:
            st.session_state.input_directory = input_dir_display
        
        if output_dir_display != st.session_state.output_directory:
            st.session_state.output_directory = output_dir_display
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 Extraction Prompt", "📄 Single File", "📚 Batch Processing", "📊 Results"])
    
    with tab1:
        st.markdown('<h2 class="section-header">🔧 Extraction Prompt Configuration</h2>', unsafe_allow_html=True)
        
        # Prompt configuration
        extraction_prompt = st.text_area(
            "Extraction Prompt",
            value=EXTRACTION_PROMPT,
            height=400,
            help="Configure the prompt that will be sent to the LLM for extraction"
        )
        
        if st.button("💾 Save Prompt Configuration"):
            st.success("Prompt configuration saved!")
    
    with tab2:
        st.markdown('<h2 class="section-header">📄 Single File Processing</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type="pdf",
                help="Upload a PDF file to extract information from"
            )
        
        with col2:
            st.markdown("### Process Options")
            test_mode = st.checkbox("Test Mode (Extract only)", help="Only extract text without LLM processing")
            show_preview = st.checkbox("Show text preview", value=True)
        
        if uploaded_file is not None:
            if st.button("🚀 Process File", type="primary"):
                process_single_file(uploaded_file, api_key, api_url, model_name, extraction_prompt, st.session_state.output_directory, test_mode, show_preview)
    
    with tab3:
        st.markdown('<h2 class="section-header">📚 Batch Processing</h2>', unsafe_allow_html=True)
        
        # Add a sub-tab for regular batch processing and failed job retry
        batch_tab1, batch_tab2 = st.tabs(["📄 Regular Batch", "🔄 Retry Failed"])
        
        with batch_tab1:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📋 Files Preview")
                input_dir = st.session_state.input_directory
                
                # Show files in directory
                if os.path.exists(input_dir):
                    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
                    if pdf_files:
                        st.markdown(f"**Found {len(pdf_files)} PDF files in `{input_dir}`:**")
                        
                        # Create a more detailed file list with checkboxes for selection
                        selected_files = []
                        
                        # Show all files with selection options
                        for i, file in enumerate(pdf_files):
                            file_name = os.path.basename(file)
                            file_size = os.path.getsize(file) / 1024  # Size in KB
                            
                            col_check, col_info = st.columns([1, 5])
                            with col_check:
                                is_selected = st.checkbox(
                                    "Select file", 
                                    key=f"file_{i}", 
                                    value=True,
                                    label_visibility="collapsed"
                                )
                            with col_info:
                                st.text(f"📄 {file_name} ({file_size:.1f} KB)")
                            
                            if is_selected:
                                selected_files.append(file)
                        
                        st.info(f"Selected {len(selected_files)} out of {len(pdf_files)} files for processing")
                        
                    else:
                        st.warning(f"No PDF files found in `{input_dir}`")
                        selected_files = []
                else:
                    st.error(f"Directory `{input_dir}` does not exist")
                    st.info("💡 Please enter a valid directory path in the sidebar")
                    selected_files = []
            
            with col2:
                st.markdown("### ⚙️ Batch Options")
                
                # Threading configuration
                st.markdown("**🧵 Multi-threading Settings:**")
                max_workers = st.number_input(
                    "Number of threads", 
                    min_value=1, 
                    max_value=16, 
                    value=MAX_WORKERS,
                    help="Number of concurrent threads for processing. More threads = faster processing but higher resource usage.",
                    key="regular_batch_threads"
                )
                
                # Update the global MAX_WORKERS for this session
                if max_workers != MAX_WORKERS:
                    st.info(f"Using {max_workers} threads (default: {MAX_WORKERS})")
                
                max_files = st.number_input(
                    "Max files to process", 
                    min_value=1, 
                    value=len(selected_files) if 'selected_files' in locals() else 10,
                    key="regular_batch_max_files"
                )
                
                # Show estimated processing time
                if 'selected_files' in locals() and selected_files:
                    estimated_time = len(selected_files[:max_files]) * 2 / max_workers  # Rough estimate
                    st.info(f"⏱️ Estimated time: ~{estimated_time:.1f} seconds")
                
                # Process selected files
                if st.button("🚀 Process Selected Files (Multi-threaded)", type="primary", key="process_selected"):
                    if 'selected_files' in locals() and selected_files:
                        # Update MAX_WORKERS temporarily
                        original_max_workers = MAX_WORKERS
                        import src.config as config
                        config.MAX_WORKERS = max_workers
                        
                        try:
                            # Limit to max_files
                            files_to_process = selected_files[:max_files]
                            process_selected_files(files_to_process, api_key, api_url, model_name, extraction_prompt, st.session_state.output_directory)
                        finally:
                            # Restore original value
                            config.MAX_WORKERS = original_max_workers
                    else:
                        st.error("No files selected or directory doesn't exist")
                
                # Quick action to process all files
                if st.button("🔄 Process All Files (Multi-threaded)", help="Process all PDF files in the directory using multi-threading", key="process_all"):
                    if os.path.exists(input_dir):
                        all_files = glob.glob(os.path.join(input_dir, "*.pdf"))[:max_files]
                        if all_files:
                            # Update MAX_WORKERS temporarily
                            original_max_workers = MAX_WORKERS
                            import src.config as config
                            config.MAX_WORKERS = max_workers
                            
                            try:
                                process_selected_files(all_files, api_key, api_url, model_name, extraction_prompt, st.session_state.output_directory)
                            finally:
                                # Restore original value
                                config.MAX_WORKERS = original_max_workers
                        else:
                            st.warning("No PDF files found")
                    else:
                        st.error("Please enter a valid directory path first")
        
        with batch_tab2:
            st.markdown("### 🔄 Retry Failed Jobs")
            st.markdown("This section allows you to reprocess PDF files that failed in previous batch operations.")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Get failed jobs
                failed_jobs = get_failed_jobs(st.session_state.output_directory)
                
                # Show failed jobs summary
                show_failed_jobs_summary(failed_jobs)
                
            with col2:
                st.markdown("### ⚙️ Retry Options")
                
                # Threading configuration for retry
                retry_max_workers = st.number_input(
                    "Number of threads for retry", 
                    min_value=1, 
                    max_value=16, 
                    value=MAX_WORKERS,
                    help="Number of concurrent threads for retry processing.",
                    key="retry_threads"
                )
                
                # Show estimated retry time
                if failed_jobs:
                    estimated_retry_time = len(failed_jobs) * 2 / retry_max_workers
                    st.info(f"⏱️ Estimated retry time: ~{estimated_retry_time:.1f} seconds")
                
                # Options for retry
                st.markdown("**🔧 Retry Settings:**")
                retry_with_modified_prompt = st.checkbox(
                    "Use current prompt for retry", 
                    value=True,
                    help="Use the current extraction prompt instead of the original one"
                )
                
                # Retry all failed jobs
                if st.button("🔄 Retry All Failed Jobs", type="primary", disabled=len(failed_jobs)==0, key="retry_all_failed"):
                    if failed_jobs:
                        process_failed_jobs(
                            failed_jobs, 
                            api_key, 
                            api_url, 
                            model_name, 
                            extraction_prompt if retry_with_modified_prompt else EXTRACTION_PROMPT,
                            st.session_state.output_directory,
                            retry_max_workers
                        )
                    else:
                        st.info("No failed jobs to retry!")
                
                # Manual refresh of failed jobs
                if st.button("🔍 Refresh Failed Jobs List", help="Scan for new failed jobs from recent batch operations"):
                    st.rerun()
    
    with tab4:
        st.markdown('<h2 class="section-header">📊 Results & Export</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Export Options")
            if st.button("📋 Convert to Excel"):
                convert_results_to_excel(st.session_state.output_directory)
            
            if st.button("👀 Preview Results"):
                preview_results(st.session_state.output_directory)
        
        with col2:
            st.markdown("### Quick Stats")
            show_stats(st.session_state.output_directory)

def get_failed_jobs(output_dir):
    """Collect all failed jobs from previous batch processing"""
    failed_files = []
    
    # Look for batch result files
    batch_result_files = glob.glob(os.path.join(output_dir, "batch_results_*.json"))
    
    if not batch_result_files:
        return []
    
    # Get the most recent batch result file
    batch_result_files.sort(key=os.path.getmtime, reverse=True)
    
    for batch_file in batch_result_files:
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            # Extract failed files
            for result in results:
                if result.get("status") in ["error", "llm_error", "exception"]:
                    # Check if the original PDF file still exists
                    pdf_path = result.get("file_path")
                    if pdf_path and os.path.exists(pdf_path):
                        failed_files.append({
                            "file_path": pdf_path,
                            "file_name": result.get("file_name", os.path.basename(pdf_path)),
                            "error": result.get("error", "Unknown error"),
                            "status": result.get("status", "unknown"),
                            "last_attempt": os.path.getmtime(batch_file)
                        })
        except Exception as e:
            st.warning(f"Could not read batch result file {batch_file}: {str(e)}")
    
    # Remove duplicates (keep most recent attempt)
    unique_failed = {}
    for failed in failed_files:
        file_path = failed["file_path"]
        if file_path not in unique_failed or failed["last_attempt"] > unique_failed[file_path]["last_attempt"]:
            unique_failed[file_path] = failed
    
    return list(unique_failed.values())

def show_failed_jobs_summary(failed_jobs):
    """Display a summary of failed jobs"""
    if not failed_jobs:
        st.info("🎉 No failed jobs found! All previous processing was successful.")
        return
    
    st.markdown(f"### 📋 Found {len(failed_jobs)} Failed Jobs")
    
    # Group by error type
    error_types = {}
    for job in failed_jobs:
        status = job.get("status", "unknown")
        if status not in error_types:
            error_types[status] = 0
        error_types[status] += 1
    
    # Show error type breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("❌ Processing Errors", error_types.get("error", 0))
    with col2:
        st.metric("🤖 LLM Errors", error_types.get("llm_error", 0))
    with col3:
        st.metric("⚠️ Exceptions", error_types.get("exception", 0))
    
    # Show detailed list
    with st.expander("📄 View Failed Files Details"):
        for i, job in enumerate(failed_jobs):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"📄 {job['file_name']}")
                st.caption(f"Error: {job['error'][:100]}..." if len(job['error']) > 100 else job['error'])
            with col2:
                status_color = {
                    "error": "🔴",
                    "llm_error": "🟡", 
                    "exception": "🟠"
                }.get(job['status'], "⚪")
                st.text(f"{status_color} {job['status']}")

def process_single_file(uploaded_file, api_key, api_url, model_name, extraction_prompt, output_dir, test_mode, show_preview):
    """Process a single uploaded PDF file"""
    with st.spinner("Processing file..."):
        start_time = time.time()
        
        try:
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extract text
            pdf_extractor = PDFExtractor(temp_path)
            extracted_text = pdf_extractor.extract_text()
            
            st.success(f"✅ Text extracted successfully! ({len(extracted_text)} characters)")
            
            if show_preview:
                with st.expander("📖 Text Preview"):
                    st.text_area("Extracted Text", extracted_text[:2000] + "..." if len(extracted_text) > 2000 else extracted_text, height=200)
            
            if not test_mode:
                # Process with LLM
                llm_client = LLMClient(api_key, api_url, model_name)
                response = llm_client.send_request(extracted_text, extraction_prompt)
                
                # Save result
                os.makedirs(output_dir, exist_ok=True)
                file_name = os.path.splitext(uploaded_file.name)[0]
                output_path = os.path.join(output_dir, f"{file_name}_output.json")
                
                json_handler = JSONHandler()
                json_handler.save_to_json(response, output_path)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                if response.get("success"):
                    st.markdown(f'<div class="success-box">✅ Processing completed successfully!<br>📁 Saved to: {output_path}<br>⏱️ Processing time: {processing_time:.2f} seconds</div>', unsafe_allow_html=True)
                    
                    # Show extracted data
                    content = response.get("content", "")
                    json_handler = JSONHandler()
                    extracted_data = json_handler.extract_json_from_content(content)
                    
                    if extracted_data:
                        st.markdown("### 📋 Extracted Information")
                        st.json(extracted_data)
                else:
                    st.markdown(f'<div class="error-box">❌ LLM processing failed: {response.get("error")}</div>', unsafe_allow_html=True)
            else:
                end_time = time.time()
                processing_time = end_time - start_time
                st.info(f"⏱️ Text extraction completed in {processing_time:.2f} seconds")
            
            # Clean up temp file
            os.remove(temp_path)
            
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)

def process_selected_files(selected_files, api_key, api_url, model_name, extraction_prompt, output_dir):
    """Process the selected PDF files using multi-threading"""
    if not selected_files:
        st.warning("No files selected")
        return
    
    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    # Initialize the batch processor with custom settings
    processor = BatchDocumentProcessor(max_workers=MAX_WORKERS, output_dir=output_dir)
    
    # Update the processor's LLM client with current settings if different from config
    if api_key != DEEPSEEK_API_KEY or api_url != DEEPSEEK_API_URL or model_name != MODEL_NAME:
        processor.llm_client = LLMClient(api_key, api_url, model_name)
    
    # Update extraction prompt if different
    if extraction_prompt != EXTRACTION_PROMPT:
        processor.extraction_prompt = extraction_prompt
    else:
        processor.extraction_prompt = EXTRACTION_PROMPT
    
    start_time = time.time()
    
    # Show initial status
    status_text.text(f"Starting batch processing of {len(selected_files)} files...")
    
    # Create a container for real-time updates
    with st.container():
        col1, col2, col3 = st.columns(3)
        successful_metric = col1.empty()
        failed_metric = col2.empty()
        progress_metric = col3.empty()
        
        # Initialize metrics
        successful_metric.metric("✅ Successful", 0)
        failed_metric.metric("❌ Failed", 0)
        progress_metric.metric("📊 Progress", "0%")
    
        # Process files with real-time updates
        results = process_files_with_progress(
            processor, selected_files, progress_bar, status_text, 
            successful_metric, failed_metric, progress_metric, results_container
        )
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Final summary
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    
    st.markdown(f"""
    <div class="success-box">
    🎉 Multi-threaded batch processing completed!<br>
    📊 Total files: {len(selected_files)}<br>
    ✅ Successful: {successful}<br>
    ❌ Failed: {failed}<br>
    🧵 Threads used: {MAX_WORKERS}<br>
    ⏱️ Total time: {processing_time:.2f} seconds<br>
    ⚡ Average time per file: {processing_time/len(selected_files):.2f} seconds
    </div>
    """, unsafe_allow_html=True)

def process_files_with_progress(processor, selected_files, progress_bar, status_text, 
                               successful_metric, failed_metric, progress_metric, results_container):
    """Process files with real-time progress updates"""
    results = []
    completed = 0
    successful_count = 0
    failed_count = 0
    
    # Create a thread-safe way to update progress
    progress_lock = threading.Lock()
    
    def update_progress(result):
        nonlocal completed, successful_count, failed_count
        with progress_lock:
            completed += 1
            if result["status"] == "success":
                successful_count += 1
                results_container.success(f"✅ {result['file_name']}")
            else:
                failed_count += 1
                error_msg = result.get('error', 'Unknown error')
                results_container.error(f"❌ {result['file_name']}: {error_msg}")
            
            # Update progress
            progress = completed / len(selected_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {completed}/{len(selected_files)}: {result['file_name']}")
            
            # Update metrics
            successful_metric.metric("✅ Successful", successful_count)
            failed_metric.metric("❌ Failed", failed_count)
            progress_metric.metric("📊 Progress", f"{progress*100:.1f}%")
    
    # Use ThreadPoolExecutor for processing
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Submit all tasks
        future_to_file = {
            executor.submit(process_single_file_custom, file_path, processor): file_path 
            for file_path in selected_files
        }
        
        # Process completed tasks
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                update_progress(result)
            except Exception as e:
                error_result = {
                    "file_name": os.path.basename(file_path),
                    "file_path": file_path,
                    "status": "exception",
                    "error": str(e),
                    "processing_time": 0,
                    "text_length": 0
                }
                results.append(error_result)
                update_progress(error_result)
    
    return results

def process_single_file_custom(pdf_path, processor):
    """Custom single file processing for Streamlit integration"""
    try:
        start_time = time.time()
        
        # Generate output path
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = processor.output_dir / f"{pdf_name}_output.json"
        
        # Extract text from PDF
        pdf_extractor = PDFExtractor(pdf_path)
        extracted_text = pdf_extractor.extract_text()
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            raise Exception("No text extracted from PDF")
        
        # Apply rate limiting and send to LLM
        processor._rate_limit()
        response = processor.llm_client.send_request(extracted_text, processor.extraction_prompt)
        
        # Save response to JSON file
        processor.json_handler.save_to_json(response, str(output_path))
        
        processing_time = time.time() - start_time
        
        if response.get("success"):
            return {
                "file_name": os.path.basename(pdf_path),
                "file_path": pdf_path,
                "output_path": str(output_path),
                "processing_time": processing_time,
                "text_length": len(extracted_text),
                "status": "success",
                "extracted_data": response.get("content", "")
            }
        else:
            return {
                "file_name": os.path.basename(pdf_path),
                "file_path": pdf_path,
                "output_path": str(output_path),
                "processing_time": processing_time,
                "text_length": len(extracted_text),
                "status": "llm_error",
                "error": response.get("error", "Unknown LLM error")
            }
            
    except Exception as e:
        processing_time = time.time() - start_time
        return {
            "file_name": os.path.basename(pdf_path),
            "file_path": pdf_path,
            "output_path": None,
            "processing_time": processing_time,
            "text_length": 0,
            "status": "error",
            "error": str(e)
        }

def convert_results_to_excel(output_dir):
    """Convert JSON results to Excel"""
    try:
        json_handler = JSONHandler()
        success = json_handler.convert_outputs_to_excel(output_dir)
        
        if success:
            st.success("✅ Successfully converted to Excel!")
            excel_path = os.path.join(output_dir, "extracted_data.xlsx")
            
            # Provide download button
            if os.path.exists(excel_path):
                with open(excel_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Excel File",
                        data=file,
                        file_name="extracted_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
        else:
            st.error("❌ Excel conversion failed")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def preview_results(output_dir):
    """Preview extracted results"""
    json_files = glob.glob(os.path.join(output_dir, "*_output.json"))
    
    if not json_files:
        st.warning("No result files found")
        return
    
    st.markdown(f"### 📋 Found {len(json_files)} result files")
    
    # Show first few results
    for json_file in json_files[:5]:
        with st.expander(f"📄 {os.path.basename(json_file)}"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get("success"):
                    json_handler = JSONHandler()
                    extracted_data = json_handler.extract_json_from_content(data.get("content", ""))
                    if extracted_data:
                        st.json(extracted_data)
                    else:
                        st.error("Failed to parse extracted data")
                else:
                    st.error(f"Processing failed: {data.get('error')}")
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

def show_stats(output_dir):
    """Show quick statistics"""
    if os.path.exists(output_dir):
        json_files = glob.glob(os.path.join(output_dir, "*_output.json"))
        
        successful = 0
        failed = 0
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get("success"):
                    successful += 1
                else:
                    failed += 1
            except:
                failed += 1
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Files", len(json_files))
        col2.metric("Successful", successful)
        col3.metric("Failed", failed)
    else:
        st.info("No output directory found")

if __name__ == "__main__":
    main()