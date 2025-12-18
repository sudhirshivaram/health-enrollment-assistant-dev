"""
Text Cleaner Module

Cleans messy text extracted from PDFs to improve quality for embeddings and search.

Handles common PDF extraction issues:
- Extra spaces between characters
- Broken line breaks
- Multiple consecutive spaces/newlines
- Special character encoding issues
- Headers and footers
"""

import re
from typing import List


def remove_extra_spaces(text: str) -> str:
    """
    Remove extra spaces between characters and words.

    Fixes issues like:
        "M e t f o r m i n" -> "Metformin"
        "T ier  1" -> "Tier 1"
        "For m ular y" -> "Formulary"

    Args:
        text: Input text with potential extra spaces

    Returns:
        Text with normalized spacing
    """
    # First, handle spaced-out words (single letters with spaces)
    # "M e t f o r m i n" -> "Metformin"
    # Pattern: letter + space + letter (repeated)
    while re.search(r'\b(\w\s+){2,}\w\b', text):
        text = re.sub(r'\b((\w)\s+(?=\w))', r'\2', text)

    # Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)

    return text


def fix_line_breaks(text: str) -> str:
    """
    Fix broken line breaks that split sentences unnaturally.

    PDFs often break lines for visual layout, not logical sentence breaks.

    Strategy:
    - Keep double line breaks (paragraph separators)
    - Keep line breaks after punctuation (., !, ?, :)
    - Join lines that break mid-sentence

    Args:
        text: Input text with potential broken lines

    Returns:
        Text with properly joined sentences
    """
    lines = text.split('\n')
    result_lines = []
    current_paragraph = []

    for line in lines:
        line = line.strip()

        if not line:
            # Empty line - end current paragraph
            if current_paragraph:
                result_lines.append(' '.join(current_paragraph))
                current_paragraph = []
                result_lines.append('')  # Keep paragraph break
            continue

        # Check if line ends with sentence-ending punctuation
        ends_with_punctuation = line.endswith(('.', '!', '?', ':'))

        if ends_with_punctuation:
            # Add to current paragraph and end the sentence
            current_paragraph.append(line)
            result_lines.append(' '.join(current_paragraph))
            current_paragraph = []
        else:
            # Add to current paragraph (will be joined)
            current_paragraph.append(line)

    # Don't forget last paragraph if exists
    if current_paragraph:
        result_lines.append(' '.join(current_paragraph))

    # Join with newlines
    result = '\n'.join(result_lines)

    return result


def normalize_whitespace(text: str) -> str:
    """
    Normalize all whitespace to single spaces or newlines.

    Removes:
    - Multiple consecutive newlines (keeps max 2 for paragraph breaks)
    - Tabs, carriage returns
    - Spaces at start/end of lines

    Args:
        text: Input text with irregular whitespace

    Returns:
        Text with normalized whitespace
    """
    # Replace tabs with spaces
    text = text.replace('\t', ' ')

    # Replace carriage returns
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')

    # Remove spaces at start and end of each line
    lines = [line.strip() for line in text.split('\n')]

    # Remove empty lines, but keep one blank line for paragraphs
    cleaned_lines = []
    prev_empty = False

    for line in lines:
        if line:
            cleaned_lines.append(line)
            prev_empty = False
        elif not prev_empty:
            # Keep one blank line for paragraph separation
            cleaned_lines.append('')
            prev_empty = True

    return '\n'.join(cleaned_lines)


def fix_encoding_issues(text: str) -> str:
    """
    Fix common encoding issues from PDF extraction.

    Common problems:
    - "â€"" should be "-" (em dash)
    - "â€™" should be "'" (apostrophe)
    - "â€œ" should be '"' (quote)

    Args:
        text: Input text with potential encoding issues

    Returns:
        Text with fixed encoding
    """
    # Common replacements
    replacements = {
        'â€"': '-',      # Em dash
        'â€"': '--',     # Double dash
        'â€™': "'",      # Apostrophe
        'â€œ': '"',      # Left quote
        'â€\x9d': '"',   # Right quote
        'â€¢': '•',      # Bullet
        'Â': '',         # Non-breaking space artifact
        '\u2013': '-',   # En dash
        '\u2014': '--',  # Em dash
        '\u2018': "'",   # Left single quote
        '\u2019': "'",   # Right single quote
        '\u201c': '"',   # Left double quote
        '\u201d': '"',   # Right double quote
        '\u2022': '•',   # Bullet point
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def remove_common_headers_footers(text: str, patterns: List[str] = None) -> str:
    """
    Remove common header and footer patterns.

    Examples:
    - "Oscar Health Insurance | Page 23 | January 2026"
    - "Page 23"
    - "Confidential"

    Args:
        text: Input text with potential headers/footers
        patterns: List of regex patterns to remove (optional)

    Returns:
        Text with headers/footers removed
    """
    if patterns is None:
        # Default patterns to remove
        patterns = [
            r'Page \d+',                    # "Page 23"
            r'\| Page \d+ \|',              # "| Page 23 |"
            r'Oscar Health Insurance',      # Company name
            r'Confidential',                # Common footer
            r'\d{1,2}/\d{1,2}/\d{4}',      # Dates like "11/18/2024"
        ]

    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)

    return text


def remove_page_numbers(text: str) -> str:
    """
    Remove standalone page numbers.

    Removes patterns like:
    - "23" (alone on a line)
    - "Page 23"
    - "23 of 100"

    Args:
        text: Input text

    Returns:
        Text with page numbers removed
    """
    # Remove "Page X" or "X of Y"
    text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\b\d+\s+of\s+\d+\b', '', text)

    # Remove standalone numbers that are likely page numbers
    # (number alone on a line at start or end)
    text = re.sub(r'^\d+$', '', text, flags=re.MULTILINE)

    return text


def clean_text(text: str, remove_headers: bool = True) -> str:
    """
    Main cleaning function that applies all cleaning operations.

    Pipeline:
    1. Fix encoding issues
    2. Remove headers/footers (optional)
    3. Remove page numbers
    4. Fix line breaks
    5. Remove extra spaces
    6. Normalize whitespace

    Args:
        text: Raw text from PDF extraction
        remove_headers: Whether to remove common headers/footers

    Returns:
        Cleaned text ready for chunking and embedding

    Example:
        >>> raw = "Oscar   Health\\n\\nT ier  1:   M e t f o r m i n\\n\\nPage 23"
        >>> clean = clean_text(raw)
        >>> print(clean)
        Tier 1: Metformin
    """
    if not text or not text.strip():
        return ""

    # Step 1: Fix encoding issues first
    text = fix_encoding_issues(text)

    # Step 2: Remove headers/footers (optional)
    if remove_headers:
        text = remove_common_headers_footers(text)
        text = remove_page_numbers(text)

    # Step 3: Fix line breaks
    text = fix_line_breaks(text)

    # Step 4: Remove extra spaces
    text = remove_extra_spaces(text)

    # Step 5: Normalize whitespace
    text = normalize_whitespace(text)

    # Final cleanup: strip leading/trailing whitespace
    text = text.strip()

    return text


def clean_pages(pages: List[dict]) -> List[dict]:
    """
    Clean text from multiple pages (from PDF parser output).

    Args:
        pages: List of page dictionaries from pdf_parser.parse_pdf()
               Format: [{"page_num": 1, "text": "...", "source": "file.pdf"}, ...]

    Returns:
        List of page dictionaries with cleaned text

    Example:
        >>> pages = parse_pdf("document.pdf")
        >>> cleaned_pages = clean_pages(pages)
    """
    cleaned = []

    for page in pages:
        cleaned_page = page.copy()
        cleaned_page['text'] = clean_text(page['text'])

        # Only keep pages that have text after cleaning
        if cleaned_page['text']:
            cleaned.append(cleaned_page)

    return cleaned


if __name__ == "__main__":
    """
    Test the text cleaner with sample messy text.
    """
    # Sample messy text (like what we get from PDFs)
    messy_text = """
    Oscar   Health    Insurance


    North    Carolina    Drug    For m ular y


    T ier  1:   Generic   Medications

    M e t f o r m i n â€" diabetes   medication
    Copay:   $ 1 0


    Page 23
    """

    print("BEFORE CLEANING:")
    print("=" * 60)
    print(messy_text)
    print("\n")

    # Clean the text
    cleaned = clean_text(messy_text)

    print("AFTER CLEANING:")
    print("=" * 60)
    print(cleaned)
    print("\n")

    # Show character count reduction
    print(f"Original length: {len(messy_text)} characters")
    print(f"Cleaned length: {len(cleaned)} characters")
    print(f"Reduction: {len(messy_text) - len(cleaned)} characters ({100 * (1 - len(cleaned)/len(messy_text)):.1f}%)")
