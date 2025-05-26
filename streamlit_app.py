import streamlit as st
import os
import sys
import glob
import time
import json
import pandas as pd
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.pdf_extractor import PDFExtractor
from src.llm_client import LLMClient
from src.json_handler import JSONHandler
from src.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL, MODEL_NAME, EXTRACTION_PROMPT, DEFAULT_OUTPUT_DIR

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
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">📄 Document Extraction System</h1>', unsafe_allow_html=True)
    
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
        input_dir = st.text_input("Input Directory", value="./data/input")
        output_dir = st.text_input("Output Directory", value=DEFAULT_OUTPUT_DIR)
    
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
                process_single_file(uploaded_file, api_key, api_url, model_name, extraction_prompt, output_dir, test_mode, show_preview)
    
    with tab3:
        st.markdown('<h2 class="section-header">📚 Batch Processing</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Input Directory")
            st.info(f"Looking for PDF files in: `{input_dir}`")
            
            # Show files in directory
            if os.path.exists(input_dir):
                pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
                if pdf_files:
                    st.markdown(f"**Found {len(pdf_files)} PDF files:**")
                    for file in pdf_files[:10]:  # Show first 10 files
                        st.text(f"• {os.path.basename(file)}")
                    if len(pdf_files) > 10:
                        st.text(f"... and {len(pdf_files) - 10} more files")
                else:
                    st.warning("No PDF files found in the input directory")
            else:
                st.error("Input directory does not exist")
        
        with col2:
            st.markdown("### Batch Options")
            max_files = st.number_input("Max files to process", min_value=1, value=10)
            
            if st.button("🔄 Process All Files", type="primary"):
                if os.path.exists(input_dir):
                    process_batch_files(input_dir, api_key, api_url, model_name, extraction_prompt, output_dir, max_files)
                else:
                    st.error("Please create the input directory first")
    
    with tab4:
        st.markdown('<h2 class="section-header">📊 Results & Export</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Export Options")
            if st.button("📋 Convert to Excel"):
                convert_results_to_excel(output_dir)
            
            if st.button("👀 Preview Results"):
                preview_results(output_dir)
        
        with col2:
            st.markdown("### Quick Stats")
            show_stats(output_dir)

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

def process_batch_files(input_dir, api_key, api_url, model_name, extraction_prompt, output_dir, max_files):
    """Process multiple PDF files"""
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))[:max_files]
    
    if not pdf_files:
        st.warning("No PDF files found")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    start_time = time.time()
    successful = 0
    failed = 0
    
    os.makedirs(output_dir, exist_ok=True)
    
    for i, pdf_file in enumerate(pdf_files):
        status_text.text(f"Processing {i+1}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
        
        try:
            # Extract text
            pdf_extractor = PDFExtractor(pdf_file)
            extracted_text = pdf_extractor.extract_text()
            
            # Process with LLM
            llm_client = LLMClient(api_key, api_url, model_name)
            response = llm_client.send_request(extracted_text, extraction_prompt)
            
            # Save result
            file_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_path = os.path.join(output_dir, f"{file_name}_output.json")
            
            json_handler = JSONHandler()
            json_handler.save_to_json(response, output_path)
            
            if response.get("success"):
                successful += 1
                results_container.success(f"✅ {os.path.basename(pdf_file)}")
            else:
                failed += 1
                results_container.error(f"❌ {os.path.basename(pdf_file)}: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            failed += 1
            results_container.error(f"❌ {os.path.basename(pdf_file)}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(pdf_files))
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    st.markdown(f"""
    <div class="success-box">
    🎉 Batch processing completed!<br>
    📊 Total files: {len(pdf_files)}<br>
    ✅ Successful: {successful}<br>
    ❌ Failed: {failed}<br>
    ⏱️ Total time: {processing_time:.2f} seconds
    </div>
    """, unsafe_allow_html=True)

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