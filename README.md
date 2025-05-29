# Document Extraction System

This project is a document extraction system that utilizes PyMuPDF for extracting content from PDF files and interacts with the DeepSeek API to process the extracted content. The system is specifically designed to extract key information from Chinese legal documents and financial statements, with outputs saved in JSON format and convertible to Excel.

## Project Structure

```
document-extraction-system
├── src
│   ├── main.py               # Command-line entry point
│   ├── pdf_extractor.py      # PDF extraction functionalities using PyMuPDF
│   ├── llm_client.py         # Interaction with the DeepSeek API using OpenAI client
│   ├── json_handler.py       # JSON file handling and Excel conversion
│   ├── batch_processor.py    # Multi-threaded batch processing engine
│   └── config.py             # Configuration settings (API keys, prompts)
├── streamlit_app.py          # Streamlit web interface
├── tests
│   ├── __init__.py           # Marks the tests directory as a package
│   ├── test_pdf_extractor.py # Unit tests for PDFExtractor
│   ├── test_llm_client.py    # Unit tests for LLMClient
│   └── test_json_handler.py  # Unit tests for JSONHandler
├── data
│   ├── input                 # Directory for input PDF files
│   └── output                # Directory for output JSON files and Excel reports
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Features

- **🌐 Web Interface**: Modern Streamlit-based web interface for easy document processing
- **⚡ Multi-threaded Processing**: Concurrent processing of multiple PDF files for improved performance
- **📄 PDF Text Extraction**: Extract text content from PDF files using PyMuPDF
- **🤖 AI-Powered Analysis**: Process extracted content using DeepSeek API for structured data extraction
- **📊 Real-time Progress Tracking**: Live progress updates during batch processing with success/failure metrics
- **🧵 Configurable Threading**: Adjustable number of worker threads (1-16) based on system capabilities
- **📈 Batch Processing**: Process multiple PDF files automatically with detailed reporting
- **📋 Excel Export**: Convert all extracted JSON data to Excel format for easy analysis
- **🇨🇳 Chinese Language Support**: Optimized for Chinese legal and financial documents
- **📋 Structured Output**: Extract specific fields like dates, amounts, company names, etc.
- **⏱️ Performance Metrics**: Processing time tracking and throughput statistics

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd document-extraction-system
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Configure API settings**:
   Edit `src/config.py` and add your DeepSeek API key:
   ```python
   DEEPSEEK_API_KEY = "your_api_key_here"
   ```

4. **Create data directories**:
   ```bash
   mkdir -p data/input data/output
   ```

## Usage

The system provides two interfaces:

### 🌐 Web Interface (Recommended)

Launch the Streamlit web application:
```bash
streamlit run streamlit_app.py
```

**Web Interface Features:**
- **📝 Extraction Prompt Configuration**: Customize the AI extraction prompt
- **📄 Single File Processing**: Upload and process individual PDF files
- **📚 Batch Processing**: 
  - Select multiple files from a directory
  - Configure number of threads (1-16)
  - Real-time progress tracking
  - Live success/failure metrics
- **📊 Results & Export**: View processing results and export to Excel

**Multi-threading Configuration:**
- Adjustable worker threads (default: 4)
- Real-time processing metrics
- Estimated completion time
- Thread-safe progress updates

### 💻 Command Line Interface

The system supports multiple CLI operation modes:

#### 1. Process a Single PDF File
```bash
python src/main.py <path_to_pdf_file>
```

#### 2. Test PDF Extraction (Debug Mode)
```bash
python src/main.py test <path_to_pdf_file>
```

#### 3. Multi-threaded Batch Processing
```bash
python src/main.py batch [input_directory]
```
If no input directory is specified, it defaults to `data/input/`

**Batch Processing Features:**
- Concurrent processing using configurable worker threads
- Automatic rate limiting to respect API limits
- Comprehensive error handling and logging
- Detailed processing statistics and summaries

#### 4. Convert JSON Outputs to Excel
```bash
python src/main.py excel
```

#### 5. Preview Extracted Data
```bash
python src/main.py preview
```

## Examples

### Web Interface Examples

1. **Start the web application**:
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Configure threading for batch processing**:
   - Navigate to "Batch Processing" tab
   - Set number of threads (recommended: 4-8 for most systems)
   - Select files to process
   - Monitor real-time progress

### Command Line Examples

1. **Process a single legal document**:
   ```bash
   python src/main.py data/input/court_decision.pdf
   ```

2. **Test extraction without API call**:
   ```bash
   python src/main.py test data/input/sample.pdf
   ```

3. **Multi-threaded batch processing**:
   ```bash
   python src/main.py batch data/input/
   ```

4. **Convert all processed files to Excel**:
   ```bash
   python src/main.py excel
   ```

## Performance Optimization

### Multi-threading Configuration

The system uses configurable multi-threading for optimal performance:

- **Default threads**: 4 workers
- **Recommended range**: 4-8 threads for most systems
- **Maximum**: 16 threads (adjust based on API rate limits)
- **Rate limiting**: Built-in delays to respect API constraints

### Performance Metrics

The system provides detailed performance tracking:
- Processing time per file
- Average throughput (files/second)
- Success/failure rates
- Text extraction statistics
- Memory usage optimization

## Output Format

The system extracts the following information from Chinese legal documents:

- **案件号** (Case Number)
- **原告居住城市** (Plaintiff's City of Residence)
- **原告代理律师所属律所** (Plaintiff's Law Firm)
- **原告委托代理人姓名** (Plaintiff's Attorney Name)
- **虚假陈述实施日** (False Statement Implementation Date)
- **原告主张虚假陈述揭露日** (Plaintiff's Claimed Disclosure Date)
- **被告主张虚假陈述揭露日** (Defendant's Claimed Disclosure Date)
- **法院认定虚假陈述揭露日** (Court-Determined Disclosure Date)
- **虚假陈述基准日** (False Statement Base Date)
- **更正日** (Correction Date)
- **投资者买入/卖出股票日期** (Investor Buy/Sell Dates)
- **法院立案/裁判日期** (Court Filing/Judgment Dates)
- **诉讼请求金额** (Litigation Claim Amount)
- **实际支持金额** (Actual Support Amount)
- **被告名称** (Defendant Name)
- **虚假陈述种类** (Type of False Statement)
- **投资者未获赔偿理由** (Reason for Non-compensation)
- **是否采取第三方核定计算书** (Third-party Verification Used)
- **法院计算投资者损失时使用的方法** (Court's Loss Calculation Method)
- **重大性** (Materiality)
- **是否连带中介机构** (Intermediary Institution Liability)
- **是否连带高管或自然人** (Executive/Individual Liability)
- **省份** (Province)

## Dependencies

### Core Dependencies
- **PyMuPDF**: PDF text extraction
- **OpenAI**: API client for DeepSeek integration
- **pandas**: Data manipulation and Excel export
- **openpyxl**: Excel file format support

### Web Interface Dependencies
- **Streamlit**: Web application framework
- **threading**: Multi-threading support
- **concurrent.futures**: Advanced threading capabilities

### Development Dependencies
- **pytest**: Unit testing framework
- **logging**: Comprehensive logging system

## Configuration

### API Configuration
```python
# src/config.py
DEEPSEEK_API_KEY = "your_api_key_here"
DEEPSEEK_API_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"
```

### Performance Configuration
```python
# Threading settings
MAX_WORKERS = 4  # Adjust based on system capabilities
API_RATE_LIMIT = 60  # requests per minute
REQUEST_DELAY = 1.0  # seconds between requests
```

## Workflow

1. **🔧 Configure**: Set up API credentials and processing parameters
2. **📄 Extract**: PyMuPDF extracts text from PDF files
3. **🧵 Process**: Multi-threaded processing with DeepSeek API analysis
4. **📊 Structure**: AI outputs structured JSON data with predefined fields
5. **📈 Monitor**: Real-time progress tracking and performance metrics
6. **📋 Export**: JSON data converted to Excel for analysis

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Adjust `REQUEST_DELAY` in config.py
2. **Memory Issues**: Reduce `MAX_WORKERS` for large files
3. **Threading Errors**: Check system thread limits

### Performance Tips

1. **Optimal Thread Count**: Start with 4 threads, adjust based on performance
2. **Large Batches**: Process in smaller batches for better memory management
3. **API Efficiency**: Monitor API usage to avoid rate limiting

## Contributing

Contributions are welcome! Please consider:

- Multi-threading optimizations
- UI/UX improvements for the Streamlit interface
- Additional document format support
- Performance enhancements

Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.