# Document Extraction System

This project is a document extraction system that utilizes PyMuPDF for extracting content from PDF files and interacts with the DeepSeek API to process the extracted content. The system is specifically designed to extract key information from Chinese legal documents and financial statements, with outputs saved in JSON format and convertible to Excel.

## Project Structure

```
document-extraction-system
├── src
│   ├── main.py               # Entry point of the application
│   ├── pdf_extractor.py      # PDF extraction functionalities using PyMuPDF
│   ├── llm_client.py         # Interaction with the DeepSeek API using OpenAI client
│   ├── json_handler.py       # JSON file handling and Excel conversion
│   └── config.py             # Configuration settings (API keys, prompts)
├── tests
│   ├── __init__.py           # Marks the tests directory as a package
│   ├── test_pdf_extractor.py # Unit tests for PDFExtractor
│   ├── test_llm_client.py    # Unit tests for LLMClient
│   └── test_json_handler.py   # Unit tests for JSONHandler
├── data
│   ├── input                 # Directory for input PDF files
│   └── output                # Directory for output JSON files and Excel reports
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Features

- **PDF Text Extraction**: Extract text content from PDF files using PyMuPDF
- **AI-Powered Analysis**: Process extracted content using DeepSeek API for structured data extraction
- **Batch Processing**: Process multiple PDF files automatically
- **Excel Export**: Convert all extracted JSON data to Excel format for easy analysis
- **Chinese Language Support**: Optimized for Chinese legal and financial documents
- **Structured Output**: Extract specific fields like dates, amounts, company names, etc.

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

The system supports multiple operation modes:

### 1. Process a Single PDF File
```bash
python src/main.py <path_to_pdf_file>
```

### 2. Test PDF Extraction (Debug Mode)
```bash
python src/main.py test <path_to_pdf_file>
```

### 3. Batch Process All PDFs
```bash
python src/main.py batch [input_directory]
```
If no input directory is specified, it defaults to `data/input/`

### 4. Convert JSON Outputs to Excel
```bash
python src/main.py excel
```

### 5. Preview Extracted Data
```bash
python src/main.py preview
```

## Examples

1. **Process a single legal document**:
   ```bash
   python src/main.py data/input/court_decision.pdf
   ```

2. **Test extraction without API call**:
   ```bash
   python src/main.py test data/input/sample.pdf
   ```

3. **Process all PDFs in the input directory**:
   ```bash
   python src/main.py batch
   ```

4. **Convert all processed files to Excel**:
   ```bash
   python src/main.py excel
   ```

## Output Format

The system extracts the following information from Chinese legal documents:

- **虚假陈述实施日** (False Statement Implementation Date)
- **虚假陈述揭露日** (False Statement Disclosure Date)
- **更正日** (Correction Date)
- **立案日期** (Case Filing Date)
- **裁判日期** (Judgment Date)
- **诉讼请求金额** (Litigation Claim Amount)
- **实际支持金额** (Actual Support Amount)
- **被告名称** (Defendant Name)
- **虚假陈述种类** (Type of False Statement)
- **是否采取第三方核定计算书** (Third-party Verification Used)
- **重大性** (Materiality)
- **是否连带中介结构** (Intermediary Liability)
- **省份** (Province)

## Dependencies

- **PyMuPDF**: PDF text extraction
- **OpenAI**: API client for DeepSeek integration
- **pandas**: Data manipulation and Excel export
- **openpyxl**: Excel file format support

## Workflow

1. **Extract**: PyMuPDF extracts text from PDF files
2. **Process**: DeepSeek API analyzes the text using custom prompts
3. **Structure**: AI outputs structured JSON data with predefined fields
4. **Export**: JSON data can be converted to Excel for analysis

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.