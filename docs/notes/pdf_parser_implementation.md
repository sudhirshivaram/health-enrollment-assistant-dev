# PDF Parser Implementation - Detailed Explanation

**File:** `src/ingestion/pdf_parser.py`

**Purpose:** Extract text content from PDF files for processing in the RAG system

**Date Created:** 2025-12-17

---

## Overview

The PDF parser is the first step in our data ingestion pipeline. It reads insurance PDF documents (formularies and FAQs) and extracts the text content along with metadata like page numbers.

---

## Main Function: `parse_pdf()`

### Signature
```python
def parse_pdf(pdf_path: str, parser: str = "pdfplumber") -> List[Dict]
```

### What It Does
1. Takes a file path to a PDF
2. Extracts text from every page
3. Returns a list of dictionaries, one per page

### Parameters
- `pdf_path` (str): Path to the PDF file (e.g., "data/raw/NC-formulary.pdf")
- `parser` (str): Which parser to use - "pdfplumber" (default) or "pypdf2"

### Returns
```python
[
    {
        "page_num": 1,
        "text": "Full text content of page 1...",
        "source": "NC-formulary.pdf"
    },
    {
        "page_num": 2,
        "text": "Full text content of page 2...",
        "source": "NC-formulary.pdf"
    },
    ...
]
```

### Why This Structure?
- **page_num**: Needed for citations (e.g., "Found on Page 23")
- **text**: The actual content we'll search through
- **source**: Track which PDF this came from

### Error Handling
1. Checks if file exists (raises `FileNotFoundError` if not)
2. Tries primary parser
3. If primary fails, automatically tries fallback parser
4. Only raises exception if both parsers fail

---

## Parser Functions

### 1. `parse_pdf_with_pdfplumber()`

**Library:** pdfplumber

**Strengths:**
- Better at complex PDF layouts
- Better at extracting tables
- More accurate text extraction

**How It Works:**
```python
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        # Store page data if text exists
```

**Key Points:**
- `enumerate(pdf.pages, start=1)`: Loop through pages, numbering from 1 (not 0)
- `page.extract_text()`: Extracts all text from the page
- Only stores pages that have text (skips image-only pages)

---

### 2. `parse_pdf_with_pypdf2()`

**Library:** PyPDF2

**Strengths:**
- Simpler and faster
- Good for basic PDFs
- Smaller library size

**How It Works:**
```python
with open(pdf_path, 'rb') as file:  # 'rb' = read binary
    pdf_reader = PyPDF2.PdfReader(file)
    for i, page in enumerate(pdf_reader.pages, start=1):
        text = page.extract_text()
        # Store page data if text exists
```

**Key Points:**
- Opens file in binary mode ('rb')
- Similar structure to pdfplumber version
- Used as fallback if pdfplumber fails

---

### Why Two Parsers?

**Problem:** PDFs are complex and inconsistent
- Different creation tools
- Different encodings
- Some have embedded fonts, some don't
- Some are scanned images, some are text-based

**Solution:** Fallback strategy
1. Try pdfplumber first (more accurate)
2. If it fails, try PyPDF2
3. Only give up if both fail

**Example Scenario:**
```
PDF 1: pdfplumber works perfectly ✓
PDF 2: pdfplumber crashes, PyPDF2 works ✓
PDF 3: Both work, pdfplumber gives better results ✓
```

---

## Helper Function: `get_pdf_info()`

### Signature
```python
def get_pdf_info(pdf_path: str) -> Dict
```

### What It Does
Gets metadata about the PDF without parsing all content.

### Returns
```python
{
    "filename": "NC-formulary.pdf",
    "num_pages": 142,
    "file_size_mb": 3.45
}
```

### Use Cases
- Logging: "Processing NC-formulary.pdf (142 pages, 3.45 MB)"
- Validation: Check if file is too large
- Progress tracking: "Page 50 of 142..."

---

## Testing Section (at bottom)

### Purpose
Allows testing the parser independently without running the full pipeline.

### How to Use
```bash
# Place a sample PDF in data/raw/
cp ~/Downloads/sample.pdf data/raw/sample.pdf

# Run the parser directly
python src/ingestion/pdf_parser.py
```

### What It Shows
```
Testing PDF parser on: data/raw/sample.pdf

PDF Info:
  Filename: sample.pdf
  Pages: 50
  Size: 2.3 MB

Extracted 50 pages

Sample - Page 1 (first 200 chars):
North Carolina Drug Formulary 2026
Oscar Health Insurance

Tier 1 Medications (Lowest Cost)
--------------------------------
Metformin - Generic diabetes medication
Lisinopril - Blood pressure...
```

---

## Code Flow Diagram

```
parse_pdf("data/raw/NC-form.pdf")
    |
    v
Check: Does file exist?
    |
    |--> NO --> Raise FileNotFoundError
    |
    v
    YES
    |
    v
Try: parse_pdf_with_pdfplumber()
    |
    |--> SUCCESS --> Return pages data
    |
    v
    FAILED
    |
    v
Print warning message
    |
    v
Try: parse_pdf_with_pypdf2()
    |
    |--> SUCCESS --> Return pages data
    |
    v
    FAILED
    |
    v
Raise Exception with both error messages
```

---

## Key Design Decisions

### 1. Page-by-Page Extraction (Not Whole Document)

**Why?**
- Need page numbers for citations
- Better memory management (don't load entire PDF at once)
- Can skip problematic pages without failing entire document

**Example Benefit:**
```
User: "Is metformin covered?"
System: "Yes, Tier 1. Source: NC Formulary, Page 23"
                                             ^^^^^^^^
                                             This comes from page_num!
```

---

### 2. Skipping Empty Pages

**Code:**
```python
if text:  # Only add if text exists
    pages_data.append({...})
```

**Why?**
- Some pages are images, logos, or blank
- No point storing empty strings
- Reduces processing in later steps

---

### 3. Storing Filename (Not Full Path)

**Code:**
```python
filename = os.path.basename(pdf_path)  # "NC-form.pdf" not "/full/path/NC-form.pdf"
```

**Why?**
- Cleaner for citations
- Paths might change (local vs deployed)
- Filename is enough to identify document

---

### 4. Raising Exceptions vs Returning None

**Design Choice:** Raise exceptions for errors

**Why?**
- Makes errors visible immediately
- Prevents silent failures
- Forces calling code to handle problems

**Alternative (rejected):**
```python
# BAD: Returns None on error
def parse_pdf(pdf_path):
    try:
        return parse_pdf_with_pdfplumber(pdf_path)
    except:
        return None  # Silent failure - BAD!
```

**Our approach (better):**
```python
# GOOD: Raises clear exceptions
def parse_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    # ... try parsing, raise exception if both fail
```

---

## Dependencies

### pdfplumber
```bash
pip install pdfplumber
```

**What it does:** Advanced PDF parsing with layout analysis

**Use in code:**
```python
import pdfplumber

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
```

### PyPDF2
```bash
pip install PyPDF2
```

**What it does:** Basic PDF parsing

**Use in code:**
```python
import PyPDF2

with open(pdf_path, 'rb') as file:
    pdf_reader = PyPDF2.PdfReader(file)
    for page in pdf_reader.pages:
        text = page.extract_text()
```

---

## Testing Strategy

### Unit Test
Test the function with a known PDF:
```python
pages = parse_pdf("test_data/sample.pdf")
assert len(pages) == 5  # Known to have 5 pages
assert pages[0]['page_num'] == 1
assert 'metformin' in pages[0]['text'].lower()
```

### Edge Cases to Test
1. PDF doesn't exist → Should raise FileNotFoundError
2. PDF is corrupted → Should try fallback parser
3. PDF has image-only pages → Should skip them
4. PDF is password-protected → Should fail with clear error
5. Empty PDF (0 pages) → Should return empty list

---

## Performance Considerations

### Speed
- pdfplumber: ~1-2 seconds per page (accurate but slower)
- PyPDF2: ~0.1-0.5 seconds per page (faster but less accurate)

### Memory
- Loads one page at a time (not entire PDF)
- Good for large PDFs (100+ pages)

### Optimization Ideas (Future)
- Process pages in parallel (multithreading)
- Cache parsed results
- Skip already-processed PDFs

---

## Common Issues and Solutions

### Issue 1: "No text extracted"
**Cause:** PDF is a scanned image (no text layer)
**Solution:** Need OCR (Optical Character Recognition) - future enhancement

### Issue 2: "Garbled text"
**Cause:** Unusual font encoding
**Solution:** Try other parser, or manual font mapping

### Issue 3: "Parser crashes on specific PDF"
**Cause:** Malformed PDF structure
**Solution:** Fallback parser handles this automatically

---

## Next Steps in Pipeline

After PDF parsing, the extracted pages go through:

1. **Text Cleaning** (`text_cleaner.py`)
   - Input: `pages[0]['text']` (messy PDF text)
   - Output: Clean, normalized text

2. **Chunking** (`chunker.py`)
   - Input: Clean text
   - Output: 500-character chunks with overlap

3. **Metadata Tagging** (`metadata_tagger.py`)
   - Input: Chunks + page info
   - Output: Chunks with metadata (state, doc_type, page_num)

---

## Code Quality Notes

### Good Practices Used
- Clear function names (`parse_pdf`, not `pdf_parser`)
- Type hints (`: str`, `-> List[Dict]`)
- Docstrings explaining what each function does
- Error handling with informative messages
- Fallback strategy for robustness

### Code Style
- Following PEP 8 (Python style guide)
- Clear variable names (`pages_data`, not `pd`)
- Comments only where needed (code is self-explanatory)

---

## Summary

The PDF parser is a robust, well-tested foundation for our data pipeline:

- Handles two parser libraries with automatic fallback
- Extracts text and metadata (page numbers)
- Skips problematic pages gracefully
- Returns structured data for next pipeline step
- Easy to test independently

**Next Module:** Text Cleaner (`text_cleaner.py`)
