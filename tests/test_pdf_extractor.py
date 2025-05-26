import pytest
from src.pdf_extractor import PDFExtractor

def test_extract_text():
    extractor = PDFExtractor()
    text = extractor.extract_text('data/input/sample.pdf')
    assert isinstance(text, str)
    assert len(text) > 0

def test_extract_images():
    extractor = PDFExtractor()
    images = extractor.extract_images('data/input/sample.pdf')
    assert isinstance(images, list)
    assert len(images) >= 0  # Assuming there can be zero images in a PDF