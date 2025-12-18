"""
Pipeline Orchestrator

Runs the complete data ingestion pipeline:
1. Parse PDFs
2. Clean text
3. Chunk text
4. Tag metadata
5. Generate embeddings
6. Build FAISS index
7. Save to disk

Usage:
    python src/ingestion/run_pipeline.py
"""

import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.pdf_parser import parse_pdf, get_pdf_info
from ingestion.text_cleaner import clean_pages
from ingestion.chunker import chunk_pages, get_chunk_stats
from ingestion.metadata_tagger import tag_chunks, get_metadata_summary
from ingestion.embedder import Embedder
from ingestion.faiss_indexer import build_index_from_chunks, save_index


def load_config(config_path: str = "config/config.yaml") -> Dict:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to config file

    Returns:
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    print(f"Loaded configuration from: {config_path}")
    return config


def find_pdf_files(directory: str) -> List[str]:
    """
    Find all PDF files in a directory.

    Args:
        directory: Directory to search

    Returns:
        List of PDF file paths
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    pdf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                pdf_files.append(pdf_path)

    print(f"\nFound {len(pdf_files)} PDF files in {directory}")
    for pdf in pdf_files:
        print(f"  - {os.path.basename(pdf)}")

    return pdf_files


def run_ingestion_pipeline(
    config_path: str = "config/config.yaml",
    pdf_dir: str = None,
    output_dir: str = None
) -> None:
    """
    Run the complete ingestion pipeline.

    Args:
        config_path: Path to configuration file
        pdf_dir: Directory with PDF files (overrides config)
        output_dir: Directory to save output (overrides config)
    """
    print("=" * 70)
    print("HEALTH ENROLLMENT ASSISTANT - DATA INGESTION PIPELINE")
    print("=" * 70)

    # Load configuration
    print("\n[1/7] Loading configuration...")
    config = load_config(config_path)

    # Get directories
    if pdf_dir is None:
        pdf_dir = config['paths']['raw_data']
    if output_dir is None:
        output_dir = config['paths']['processed_data']

    print(f"  Input directory: {pdf_dir}")
    print(f"  Output directory: {output_dir}")

    # Find PDF files
    print("\n[2/7] Finding PDF files...")
    pdf_files = find_pdf_files(pdf_dir)

    if not pdf_files:
        print("\nNo PDF files found. Exiting.")
        return

    # Parse PDFs
    print("\n[3/7] Parsing PDFs...")
    all_pages = []

    for pdf_path in pdf_files:
        print(f"\n  Processing: {os.path.basename(pdf_path)}")

        # Get info
        info = get_pdf_info(pdf_path)
        print(f"    Pages: {info['num_pages']}, Size: {info['file_size_mb']} MB")

        # Parse
        parser = config.get('pdf', {}).get('parser', 'pdfplumber')
        pages = parse_pdf(pdf_path, parser=parser)
        print(f"    Extracted: {len(pages)} pages")

        all_pages.extend(pages)

    print(f"\n  Total pages extracted: {len(all_pages)}")

    # Clean text
    print("\n[4/7] Cleaning text...")
    cleaned_pages = clean_pages(all_pages)
    print(f"  Cleaned: {len(cleaned_pages)} pages")

    # Chunk text
    print("\n[5/7] Chunking text...")
    chunking_config = config.get('chunking', {})
    chunk_size = chunking_config.get('chunk_size', 500)
    chunk_overlap = chunking_config.get('chunk_overlap', 50)

    chunks = chunk_pages(
        cleaned_pages,
        chunk_size=chunk_size,
        overlap=chunk_overlap,
        smart=True
    )

    stats = get_chunk_stats(chunks)
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Avg chunk size: {stats['avg_chunk_size']} chars")
    print(f"  Size range: [{stats['min_chunk_size']}, {stats['max_chunk_size']}]")

    # Tag metadata
    print("\n[6/7] Tagging metadata...")
    tagged_chunks = tag_chunks(chunks)

    summary = get_metadata_summary(tagged_chunks)
    print(f"  States: {summary['states']}")
    print(f"  Doc types: {summary['doc_types']}")
    print(f"  Unique pages: {summary['unique_pages']}")

    # Generate embeddings
    print("\n[7/7] Generating embeddings...")
    embedding_config = config.get('embedding', {})
    model_name = embedding_config.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2')

    embedder = Embedder(model_name=model_name)

    embedded_chunks = embedder.embed_chunks(
        tagged_chunks,
        batch_size=32,
        show_progress=True
    )

    # Build FAISS index
    print("\n[8/7] Building FAISS index...")
    dimension = embedding_config.get('dimension', 384)
    index, metadata = build_index_from_chunks(embedded_chunks, dimension=dimension)

    # Save index
    print("\n[9/7] Saving to disk...")
    os.makedirs(output_dir, exist_ok=True)

    index_path = config['paths'].get('faiss_index', 'data/processed/index.faiss')
    metadata_path = config['paths'].get('metadata', 'data/processed/metadata.json')

    # Extract directory and filenames from paths
    index_dir = os.path.dirname(index_path)
    index_name = os.path.basename(index_path)
    metadata_name = os.path.basename(metadata_path)

    save_index(index, metadata, index_dir, index_name, metadata_name)

    # Final summary
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"\nProcessed:")
    print(f"  - {len(pdf_files)} PDF files")
    print(f"  - {len(all_pages)} pages")
    print(f"  - {len(chunks)} chunks")
    print(f"  - {len(embedded_chunks)} embeddings")
    print(f"\nOutput:")
    print(f"  - Index: {index_path}")
    print(f"  - Metadata: {metadata_path}")
    print(f"\nReady for retrieval!")


if __name__ == "__main__":
    """
    Run the pipeline from command line.

    Usage:
        python src/ingestion/run_pipeline.py
    """
    import argparse

    parser = argparse.ArgumentParser(description='Run data ingestion pipeline')
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to config file (default: config/config.yaml)'
    )
    parser.add_argument(
        '--pdf-dir',
        type=str,
        default=None,
        help='PDF directory (overrides config)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=None,
        help='Output directory (overrides config)'
    )

    args = parser.parse_args()

    try:
        run_ingestion_pipeline(
            config_path=args.config,
            pdf_dir=args.pdf_dir,
            output_dir=args.output_dir
        )
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
