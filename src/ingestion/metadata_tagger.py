"""
Metadata Tagger Module

Adds metadata tags to text chunks for better filtering and retrieval.

Metadata includes:
- State (NC, TX, FL, etc.)
- Document type (formulary, faq, network)
- Source file
- Page number
- Chunk ID (unique identifier)
"""

import re
from typing import List, Dict, Optional


def extract_state_from_filename(filename: str) -> Optional[str]:
    """
    Extract state code from filename.

    Common patterns:
    - "NC-formulary.pdf" -> "NC"
    - "Oscar_4T_NC_STND_Member_Doc.pdf" -> "NC"
    - "texas-faq-2026.pdf" -> "TX"

    Args:
        filename: PDF filename

    Returns:
        Two-letter state code (uppercase) or None if not found
    """
    # State abbreviations (all 50 US states)
    states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    ]

    # State name to abbreviation mapping (common ones)
    state_names = {
        'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR',
        'california': 'CA', 'colorado': 'CO', 'connecticut': 'CT', 'delaware': 'DE',
        'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
        'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS',
        'kentucky': 'KY', 'louisiana': 'LA', 'maine': 'ME', 'maryland': 'MD',
        'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN', 'mississippi': 'MS',
        'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
        'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY',
        'north carolina': 'NC', 'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK',
        'oregon': 'OR', 'pennsylvania': 'PA', 'rhode island': 'RI', 'south carolina': 'SC',
        'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX', 'utah': 'UT',
        'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
        'wisconsin': 'WI', 'wyoming': 'WY'
    }

    filename_upper = filename.upper()

    # First, try to find state abbreviation (most common)
    for state in states:
        # Look for state code as separate word or with underscores/hyphens
        pattern = rf'\b{state}\b|_{state}_|_{state}\.|-{state}-|-{state}\.'
        if re.search(pattern, filename_upper):
            return state

    # Second, try to find full state name
    filename_lower = filename.lower()
    for state_name, state_code in state_names.items():
        if state_name in filename_lower:
            return state_code

    return None


def extract_doc_type_from_filename(filename: str) -> str:
    """
    Extract document type from filename.

    Types:
    - formulary: Drug formulary/coverage documents
    - faq: Frequently asked questions
    - network: Provider network documents
    - summary: Summary of benefits
    - unknown: Cannot determine

    Args:
        filename: PDF filename

    Returns:
        Document type string
    """
    filename_lower = filename.lower()

    # Check for formulary keywords
    if any(keyword in filename_lower for keyword in ['formulary', 'drug', 'medication', 'tier']):
        return 'formulary'

    # Check for FAQ keywords
    if any(keyword in filename_lower for keyword in ['faq', 'question', 'answer']):
        return 'faq'

    # Check for network keywords
    if any(keyword in filename_lower for keyword in ['network', 'provider', 'doctor', 'physician']):
        return 'network'

    # Check for summary keywords
    if any(keyword in filename_lower for keyword in ['summary', 'benefit', 'coverage']):
        return 'summary'

    return 'unknown'


def generate_chunk_id(
    source: str,
    page_num: int,
    chunk_index: int
) -> str:
    """
    Generate unique chunk ID.

    Format: {source_prefix}-p{page}-c{chunk}
    Example: "NC-form-p23-c2"

    Args:
        source: Source filename
        page_num: Page number
        chunk_index: Chunk index within page

    Returns:
        Unique chunk ID string
    """
    # Extract prefix from source (remove extension, clean up)
    source_prefix = source.replace('.pdf', '').replace('.PDF', '')
    # Simplify long names
    source_prefix = source_prefix[:20]  # Limit to 20 chars
    # Remove special characters
    source_prefix = re.sub(r'[^a-zA-Z0-9-_]', '-', source_prefix)

    return f"{source_prefix}-p{page_num}-c{chunk_index}"


def add_metadata_to_chunk(
    chunk: Dict,
    state: Optional[str] = None,
    doc_type: Optional[str] = None
) -> Dict:
    """
    Add metadata to a single chunk.

    Args:
        chunk: Chunk dictionary with 'text', 'source', 'page_num', 'chunk_index'
        state: State code (if not provided, will try to extract from source)
        doc_type: Document type (if not provided, will try to extract from source)

    Returns:
        Chunk with added metadata fields
    """
    # Extract metadata from source if not provided
    if state is None:
        state = extract_state_from_filename(chunk['source'])

    if doc_type is None:
        doc_type = extract_doc_type_from_filename(chunk['source'])

    # Generate chunk ID
    chunk_id = generate_chunk_id(
        chunk['source'],
        chunk['page_num'],
        chunk['chunk_index']
    )

    # Add all metadata
    chunk['state'] = state if state else 'unknown'
    chunk['doc_type'] = doc_type
    chunk['chunk_id'] = chunk_id

    return chunk


def tag_chunks(
    chunks: List[Dict],
    state: Optional[str] = None,
    doc_type: Optional[str] = None
) -> List[Dict]:
    """
    Add metadata to multiple chunks.

    Args:
        chunks: List of chunk dictionaries from chunker.chunk_pages()
        state: Optional state code (overrides auto-detection)
        doc_type: Optional document type (overrides auto-detection)

    Returns:
        List of chunks with metadata added

    Example:
        >>> chunks = chunk_pages(clean_pages(parse_pdf("NC-form.pdf")))
        >>> tagged = tag_chunks(chunks)
        >>> tagged[0]['state']
        'NC'
        >>> tagged[0]['doc_type']
        'formulary'
    """
    tagged_chunks = []

    for chunk in chunks:
        tagged_chunk = add_metadata_to_chunk(chunk, state, doc_type)
        tagged_chunks.append(tagged_chunk)

    return tagged_chunks


def filter_chunks_by_metadata(
    chunks: List[Dict],
    state: Optional[str] = None,
    doc_type: Optional[str] = None,
    page_num: Optional[int] = None
) -> List[Dict]:
    """
    Filter chunks by metadata.

    Useful for testing and debugging.

    Args:
        chunks: List of tagged chunks
        state: Filter by state code
        doc_type: Filter by document type
        page_num: Filter by page number

    Returns:
        Filtered list of chunks

    Example:
        >>> # Get only NC formulary chunks
        >>> nc_form = filter_chunks_by_metadata(chunks, state='NC', doc_type='formulary')
    """
    filtered = chunks

    if state:
        filtered = [c for c in filtered if c.get('state') == state]

    if doc_type:
        filtered = [c for c in filtered if c.get('doc_type') == doc_type]

    if page_num is not None:
        filtered = [c for c in filtered if c.get('page_num') == page_num]

    return filtered


def get_metadata_summary(chunks: List[Dict]) -> Dict:
    """
    Get summary of metadata across all chunks.

    Useful for validation and debugging.

    Args:
        chunks: List of tagged chunks

    Returns:
        Summary dictionary with counts and distributions
    """
    states = {}
    doc_types = {}
    pages = set()

    for chunk in chunks:
        # Count states
        state = chunk.get('state', 'unknown')
        states[state] = states.get(state, 0) + 1

        # Count doc types
        doc_type = chunk.get('doc_type', 'unknown')
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        # Track pages
        page_num = chunk.get('page_num')
        if page_num:
            pages.add(page_num)

    return {
        'total_chunks': len(chunks),
        'states': states,
        'doc_types': doc_types,
        'unique_pages': len(pages),
        'page_range': f"{min(pages)}-{max(pages)}" if pages else "N/A"
    }


if __name__ == "__main__":
    """
    Test the metadata tagger.
    """
    print("TESTING METADATA EXTRACTION")
    print("=" * 60)

    # Test state extraction
    test_filenames = [
        "Oscar_4T_NC_STND_Member_Doc__January_2026__as_of_11182025.pdf",
        "Texas-Drug-Formulary-2026.pdf",
        "florida-faq-2026.pdf",
        "CA_Provider_Network.pdf",
        "unknown-document.pdf"
    ]

    print("\nState extraction from filenames:")
    for filename in test_filenames:
        state = extract_state_from_filename(filename)
        doc_type = extract_doc_type_from_filename(filename)
        print(f"  {filename[:40]:<40} -> State: {state or 'None':<4} Type: {doc_type}")

    print("\n")
    print("TESTING CHUNK TAGGING")
    print("=" * 60)

    # Sample chunks (like what we'd get from chunker)
    sample_chunks = [
        {
            "text": "Metformin is covered as Tier 1...",
            "source": "Oscar_4T_NC_STND_Member_Doc__January_2026__as_of_11182025.pdf",
            "page_num": 23,
            "chunk_index": 0
        },
        {
            "text": "Lisinopril is covered as Tier 1...",
            "source": "Oscar_4T_NC_STND_Member_Doc__January_2026__as_of_11182025.pdf",
            "page_num": 23,
            "chunk_index": 1
        },
        {
            "text": "What are generic drugs?...",
            "source": "NC-FAQ-2026.pdf",
            "page_num": 5,
            "chunk_index": 0
        }
    ]

    # Tag the chunks
    tagged = tag_chunks(sample_chunks)

    print("\nTagged chunks:")
    for i, chunk in enumerate(tagged):
        print(f"\nChunk {i}:")
        print(f"  ID: {chunk['chunk_id']}")
        print(f"  State: {chunk['state']}")
        print(f"  Doc Type: {chunk['doc_type']}")
        print(f"  Source: {chunk['source'][:40]}")
        print(f"  Page: {chunk['page_num']}")
        print(f"  Text: {chunk['text'][:50]}...")

    print("\n")
    print("METADATA SUMMARY")
    print("=" * 60)

    summary = get_metadata_summary(tagged)
    print(f"\nTotal chunks: {summary['total_chunks']}")
    print(f"States: {summary['states']}")
    print(f"Doc types: {summary['doc_types']}")
    print(f"Unique pages: {summary['unique_pages']}")
    print(f"Page range: {summary['page_range']}")
