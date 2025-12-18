"""
Text Chunker Module

Splits cleaned text into smaller chunks for embedding and retrieval.

Why chunking?
- Embeddings work best on smaller text segments (500-1000 chars)
- Smaller chunks = more precise retrieval
- Overlap between chunks preserves context across boundaries
"""

from typing import List, Dict


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk in characters (default: 500)
        overlap: Number of characters to overlap between chunks (default: 50)

    Returns:
        List of text chunks

    Example:
        >>> text = "This is a long document..." * 100
        >>> chunks = chunk_text(text, chunk_size=500, overlap=50)
        >>> len(chunks)
        10
        >>> chunks[0][-50:]  # Last 50 chars of chunk 0
        >>> chunks[1][:50]   # First 50 chars of chunk 1
        # These should be identical (the overlap)
    """
    if not text or len(text) == 0:
        return []

    # If text is shorter than chunk size, return as single chunk
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        # Calculate end position
        end = start + chunk_size

        # Get the chunk
        chunk = text[start:end]

        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk)

        # Move start position (accounting for overlap)
        start = end - overlap

        # Prevent infinite loop if overlap >= chunk_size
        if overlap >= chunk_size:
            start = end

    return chunks


def chunk_text_smart(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]:
    """
    Split text into chunks, trying to break at sentence boundaries.

    This is "smarter" than simple chunking because it tries to:
    - Break at sentence boundaries (., !, ?, :) when possible
    - Avoid cutting words in half
    - Preserve semantic meaning

    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks with smart boundaries

    Example:
        >>> text = "First sentence. Second sentence. Third sentence."
        >>> chunks = chunk_text_smart(text, chunk_size=30, overlap=5)
        # Chunks will break at sentence boundaries when possible
    """
    if not text or len(text) == 0:
        return []

    if len(text) <= chunk_size:
        return [text]

    # Split into sentences first
    import re
    # Split on sentence-ending punctuation followed by space
    sentences = re.split(r'([.!?:]\s+)', text)

    # Rejoin sentences with their punctuation
    sentences = [''.join(sentences[i:i+2]) for i in range(0, len(sentences), 2)]
    sentences = [s for s in sentences if s.strip()]

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding this sentence would exceed chunk size
        if len(current_chunk) + len(sentence) > chunk_size:
            # Save current chunk if it's not empty
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

                # Start new chunk with overlap from previous
                if overlap > 0 and len(current_chunk) > overlap:
                    current_chunk = current_chunk[-overlap:] + sentence
                else:
                    current_chunk = sentence
            else:
                # Current chunk is empty, so just use this sentence
                # Even if it's longer than chunk_size
                current_chunk = sentence
        else:
            # Add sentence to current chunk
            current_chunk += sentence

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 500,
    overlap: int = 50,
    smart: bool = True
) -> List[Dict]:
    """
    Chunk text from multiple pages (from PDF parser output).

    Args:
        pages: List of page dictionaries from text_cleaner.clean_pages()
               Format: [{"page_num": 1, "text": "...", "source": "file.pdf"}, ...]
        chunk_size: Target chunk size in characters
        overlap: Overlap between chunks
        smart: Use smart chunking (sentence boundaries) vs simple chunking

    Returns:
        List of chunk dictionaries with metadata:
        [
            {
                "text": "chunk text...",
                "source": "file.pdf",
                "page_num": 1,
                "chunk_index": 0
            },
            ...
        ]

    Example:
        >>> pages = clean_pages(parse_pdf("doc.pdf"))
        >>> chunks = chunk_pages(pages, chunk_size=500, overlap=50)
    """
    all_chunks = []
    chunk_func = chunk_text_smart if smart else chunk_text

    for page in pages:
        page_text = page.get('text', '')

        if not page_text.strip():
            continue

        # Chunk the page text
        page_chunks = chunk_func(page_text, chunk_size, overlap)

        # Add metadata to each chunk
        for i, chunk_text in enumerate(page_chunks):
            chunk_dict = {
                "text": chunk_text,
                "source": page.get('source', 'unknown'),
                "page_num": page.get('page_num', 0),
                "chunk_index": i
            }
            all_chunks.append(chunk_dict)

    return all_chunks


def get_chunk_stats(chunks: List[Dict]) -> Dict:
    """
    Get statistics about chunks.

    Useful for validation and debugging.

    Args:
        chunks: List of chunk dictionaries

    Returns:
        Dictionary with statistics:
        {
            "total_chunks": 150,
            "avg_chunk_size": 487,
            "min_chunk_size": 120,
            "max_chunk_size": 500,
            "total_chars": 73050
        }
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0,
            "total_chars": 0
        }

    chunk_sizes = [len(chunk['text']) for chunk in chunks]

    return {
        "total_chunks": len(chunks),
        "avg_chunk_size": sum(chunk_sizes) // len(chunk_sizes),
        "min_chunk_size": min(chunk_sizes),
        "max_chunk_size": max(chunk_sizes),
        "total_chars": sum(chunk_sizes)
    }


if __name__ == "__main__":
    """
    Test the chunker with sample text.
    """
    # Sample text (simulating cleaned PDF text)
    sample_text = """
    Oscar Health Insurance

    North Carolina Drug Formulary

    Tier 1: Generic Medications

    Metformin - diabetes medication. This is a commonly prescribed medication
    for type 2 diabetes. It works by reducing glucose production in the liver.
    Copay: $10

    Lisinopril - blood pressure medication. Used to treat high blood pressure
    and heart failure. It belongs to a class of drugs called ACE inhibitors.
    Copay: $10

    Atorvastatin - cholesterol medication. Helps lower cholesterol and reduce
    the risk of heart disease. Also known by the brand name Lipitor.
    Copay: $10
    """

    print("SAMPLE TEXT:")
    print("=" * 60)
    print(sample_text)
    print(f"\nTotal length: {len(sample_text)} characters")
    print("\n")

    # Test simple chunking
    print("SIMPLE CHUNKING (chunk_size=200, overlap=30):")
    print("=" * 60)
    simple_chunks = chunk_text(sample_text, chunk_size=200, overlap=30)
    for i, chunk in enumerate(simple_chunks):
        print(f"\nChunk {i} ({len(chunk)} chars):")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)

    print("\n")

    # Test smart chunking
    print("SMART CHUNKING (chunk_size=200, overlap=30):")
    print("=" * 60)
    smart_chunks = chunk_text_smart(sample_text, chunk_size=200, overlap=30)
    for i, chunk in enumerate(smart_chunks):
        print(f"\nChunk {i} ({len(chunk)} chars):")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)

    print("\n")

    # Show statistics
    print("STATISTICS:")
    print("=" * 60)
    print(f"Simple chunking: {len(simple_chunks)} chunks")
    print(f"Smart chunking: {len(smart_chunks)} chunks")

    # Test with page format
    print("\n")
    print("CHUNKING WITH PAGE METADATA:")
    print("=" * 60)

    pages = [
        {
            "page_num": 1,
            "text": sample_text,
            "source": "test-formulary.pdf"
        }
    ]

    chunks_with_metadata = chunk_pages(pages, chunk_size=200, overlap=30)

    print(f"\nTotal chunks with metadata: {len(chunks_with_metadata)}")
    print(f"\nFirst chunk:")
    print(chunks_with_metadata[0])

    stats = get_chunk_stats(chunks_with_metadata)
    print(f"\nChunk statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
