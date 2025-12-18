"""
PDF Parser Module

Extracts text content from PDF files for processing.
Uses pdfplumber as primary parser, with PyPDF2 as fallback.
"""

import os
from typing import List, Dict, Optional
import pdfplumber
import PyPDF2


def parse_pdf_with_pdfplumber(pdf_path: str) -> List[Dict]:
    """
    Parse PDF using pdfplumber (better for complex layouts and tables).

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of dictionaries, one per page:
        [
            {
                "page_num": 1,
                "text": "extracted text from page 1",
                "source": "filename.pdf"
            },
            ...
        ]
    """
    pages_data = []
    filename = os.path.basename(pdf_path)

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()

            # Some pages might not have extractable text (images, etc.)
            if text:
                pages_data.append({
                    "page_num": i,
                    "text": text,
                    "source": filename
                })

    return pages_data


def parse_pdf_with_pypdf2(pdf_path: str) -> List[Dict]:
    """
    Parse PDF using PyPDF2 (simpler, faster, but less accurate).
    Used as fallback if pdfplumber fails.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of dictionaries, one per page
    """
    pages_data = []
    filename = os.path.basename(pdf_path)

    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        for i, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()

            if text:
                pages_data.append({
                    "page_num": i,
                    "text": text,
                    "source": filename
                })

    return pages_data


def parse_pdf(pdf_path: str, parser: str = "pdfplumber") -> List[Dict]:
    """
    Parse a PDF file and extract text from all pages.

    Args:
        pdf_path: Path to the PDF file
        parser: Which parser to use ("pdfplumber" or "pypdf2")

    Returns:
        List of dictionaries with page content and metadata

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If parsing fails with both parsers
    """
    # Validate file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Try primary parser
    try:
        if parser == "pdfplumber":
            return parse_pdf_with_pdfplumber(pdf_path)
        elif parser == "pypdf2":
            return parse_pdf_with_pypdf2(pdf_path)
        else:
            raise ValueError(f"Unknown parser: {parser}. Use 'pdfplumber' or 'pypdf2'")

    except Exception as e:
        # If primary parser fails, try fallback
        print(f"Warning: {parser} failed for {pdf_path}. Error: {str(e)}")
        print("Trying fallback parser...")

        try:
            if parser == "pdfplumber":
                return parse_pdf_with_pypdf2(pdf_path)
            else:
                return parse_pdf_with_pdfplumber(pdf_path)
        except Exception as fallback_error:
            raise Exception(
                f"Both parsers failed for {pdf_path}. "
                f"Primary error: {str(e)}. "
                f"Fallback error: {str(fallback_error)}"
            )


def get_pdf_info(pdf_path: str) -> Dict:
    """
    Get metadata information about a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Dictionary with PDF metadata:
        {
            "filename": "example.pdf",
            "num_pages": 50,
            "file_size_mb": 2.5
        }
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    filename = os.path.basename(pdf_path)
    file_size_bytes = os.path.getsize(pdf_path)
    file_size_mb = file_size_bytes / (1024 * 1024)

    # Get page count
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)

    return {
        "filename": filename,
        "num_pages": num_pages,
        "file_size_mb": round(file_size_mb, 2)
    }


if __name__ == "__main__":
    """
    Test the PDF parser with a sample file.

    Usage:
        python src/ingestion/pdf_parser.py
    """
    # This is for testing only
    # You would replace this with your actual PDF path

    test_pdf_path = "data/raw/Oscar_4T_NC_STND_Member_Doc__January_2026__as_of_11182025.pdf"

    if os.path.exists(test_pdf_path):
        print(f"Testing PDF parser on: {test_pdf_path}")

        # Get PDF info
        info = get_pdf_info(test_pdf_path)
        print(f"\nPDF Info:")
        print(f"  Filename: {info['filename']}")
        print(f"  Pages: {info['num_pages']}")
        print(f"  Size: {info['file_size_mb']} MB")

        # Parse PDF
        pages = parse_pdf(test_pdf_path)
        print(f"\nExtracted {len(pages)} pages")

        # Show first page as sample
        if pages:
            print(f"\nSample - Page 1 (first 200 chars):")
            print(pages[0]['text'][:200])
    else:
        print(f"Test file not found: {test_pdf_path}")
        print("Place a sample PDF in data/raw/ to test the parser")
