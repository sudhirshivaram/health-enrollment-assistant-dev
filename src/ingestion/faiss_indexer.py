"""
FAISS Index Builder Module

Creates and manages FAISS indexes for fast vector similarity search.

FAISS (Facebook AI Similarity Search):
- Fast similarity search in high-dimensional spaces
- Handles millions of vectors efficiently
- CPU and GPU support
"""

import os
import json
import numpy as np
import faiss
from typing import List, Dict, Tuple


def create_faiss_index(dimension: int, index_type: str = "flat") -> faiss.Index:
    """
    Create a FAISS index.

    Args:
        dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
        index_type: Type of index to create
            - "flat": Exact search (slower but perfect accuracy)
            - "ivf": Approximate search (faster but slightly less accurate)

    Returns:
        FAISS index object

    Note:
        For Phase 1 with small data (<100k vectors), "flat" is recommended.
        It's simple, accurate, and fast enough.
    """
    if index_type == "flat":
        # IndexFlatL2: Exact L2 (Euclidean) distance search
        # Best for: Small datasets, exact results needed
        index = faiss.IndexFlatL2(dimension)
        print(f"Created FAISS Flat index (dimension: {dimension})")

    elif index_type == "ivf":
        # IndexIVFFlat: Inverted file index (approximate search)
        # Best for: Large datasets (>100k vectors)
        quantizer = faiss.IndexFlatL2(dimension)
        n_centroids = 100  # Number of clusters
        index = faiss.IndexIVFFlat(quantizer, dimension, n_centroids)
        print(f"Created FAISS IVF index (dimension: {dimension}, centroids: {n_centroids})")
        print("Note: IVF index needs training before adding vectors")

    else:
        raise ValueError(f"Unknown index_type: {index_type}. Use 'flat' or 'ivf'")

    return index


def add_embeddings_to_index(
    index: faiss.Index,
    embeddings: np.ndarray
) -> faiss.Index:
    """
    Add embeddings to FAISS index.

    Args:
        index: FAISS index object
        embeddings: numpy array of shape (num_vectors, dimension)

    Returns:
        Updated FAISS index

    Example:
        >>> index = create_faiss_index(384)
        >>> embeddings = np.random.rand(100, 384).astype('float32')
        >>> index = add_embeddings_to_index(index, embeddings)
        >>> index.ntotal
        100
    """
    # FAISS requires float32
    if embeddings.dtype != np.float32:
        embeddings = embeddings.astype('float32')

    # Add vectors to index
    index.add(embeddings)

    print(f"Added {len(embeddings)} vectors to index")
    print(f"Total vectors in index: {index.ntotal}")

    return index


def build_index_from_chunks(
    chunks: List[Dict],
    dimension: int = 384,
    index_type: str = "flat"
) -> Tuple[faiss.Index, List[Dict]]:
    """
    Build FAISS index from chunks with embeddings.

    Args:
        chunks: List of chunk dicts with 'embedding' field
        dimension: Embedding dimension
        index_type: Type of FAISS index

    Returns:
        Tuple of (faiss_index, metadata_list)

    Example:
        >>> chunks = [
        ...     {"text": "...", "embedding": np.array([...]), "state": "NC"},
        ...     {"text": "...", "embedding": np.array([...]), "state": "NC"}
        ... ]
        >>> index, metadata = build_index_from_chunks(chunks)
    """
    if not chunks:
        raise ValueError("No chunks provided")

    if 'embedding' not in chunks[0]:
        raise ValueError("Chunks must have 'embedding' field. Run embedder first.")

    # Extract embeddings
    embeddings = np.array([chunk['embedding'] for chunk in chunks])

    # Create index
    index = create_faiss_index(dimension, index_type)

    # Add embeddings
    index = add_embeddings_to_index(index, embeddings)

    # Prepare metadata (everything except embedding)
    metadata = []
    for chunk in chunks:
        meta = {k: v for k, v in chunk.items() if k != 'embedding'}
        metadata.append(meta)

    return index, metadata


def save_index(
    index: faiss.Index,
    metadata: List[Dict],
    output_dir: str,
    index_name: str = "index.faiss",
    metadata_name: str = "metadata.json"
) -> None:
    """
    Save FAISS index and metadata to disk.

    Args:
        index: FAISS index object
        metadata: List of metadata dictionaries
        output_dir: Directory to save files
        index_name: Name of FAISS index file
        metadata_name: Name of metadata file

    Saves:
        - {output_dir}/{index_name}: FAISS index (binary)
        - {output_dir}/{metadata_name}: Metadata (JSON)

    Example:
        >>> save_index(index, metadata, "data/processed")
        Saves:
            data/processed/index.faiss
            data/processed/metadata.json
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save FAISS index
    index_path = os.path.join(output_dir, index_name)
    faiss.write_index(index, index_path)
    print(f"Saved FAISS index to: {index_path}")

    # Save metadata
    metadata_path = os.path.join(output_dir, metadata_name)
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to: {metadata_path}")

    # Print statistics
    index_size_mb = os.path.getsize(index_path) / (1024 * 1024)
    metadata_size_mb = os.path.getsize(metadata_path) / (1024 * 1024)
    print(f"\nIndex size: {index_size_mb:.2f} MB")
    print(f"Metadata size: {metadata_size_mb:.2f} MB")
    print(f"Total vectors: {index.ntotal}")


def load_index(
    index_path: str,
    metadata_path: str
) -> Tuple[faiss.Index, List[Dict]]:
    """
    Load FAISS index and metadata from disk.

    Args:
        index_path: Path to FAISS index file
        metadata_path: Path to metadata JSON file

    Returns:
        Tuple of (faiss_index, metadata_list)

    Example:
        >>> index, metadata = load_index(
        ...     "data/processed/index.faiss",
        ...     "data/processed/metadata.json"
        ... )
        >>> index.ntotal
        1000
    """
    # Load FAISS index
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"Index file not found: {index_path}")

    index = faiss.read_index(index_path)
    print(f"Loaded FAISS index from: {index_path}")
    print(f"Total vectors: {index.ntotal}")

    # Load metadata
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    print(f"Loaded metadata from: {metadata_path}")
    print(f"Total metadata entries: {len(metadata)}")

    # Validate
    if index.ntotal != len(metadata):
        print(f"WARNING: Index has {index.ntotal} vectors but metadata has {len(metadata)} entries")

    return index, metadata


def search_index(
    index: faiss.Index,
    metadata: List[Dict],
    query_embedding: np.ndarray,
    top_k: int = 5
) -> List[Dict]:
    """
    Search FAISS index for similar vectors.

    Args:
        index: FAISS index
        metadata: Metadata list
        query_embedding: Query vector (shape: (dimension,))
        top_k: Number of results to return

    Returns:
        List of top K results with metadata and scores

    Example:
        >>> query_emb = embedder.embed_text("Is metformin covered?")
        >>> results = search_index(index, metadata, query_emb, top_k=5)
        >>> results[0]
        {
            'text': '...',
            'state': 'NC',
            'score': 0.95,
            'rank': 0
        }
    """
    # Ensure correct shape and type
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)

    if query_embedding.dtype != np.float32:
        query_embedding = query_embedding.astype('float32')

    # Search index
    # Returns: distances and indices of top K nearest neighbors
    distances, indices = index.search(query_embedding, top_k)

    # Convert to results with metadata
    results = []
    for rank, (idx, distance) in enumerate(zip(indices[0], distances[0])):
        if idx == -1:  # FAISS returns -1 for invalid results
            continue

        result = metadata[idx].copy()
        result['score'] = float(distance)  # L2 distance
        result['rank'] = rank
        results.append(result)

    return results


def get_index_stats(index: faiss.Index, metadata: List[Dict]) -> Dict:
    """
    Get statistics about FAISS index.

    Args:
        index: FAISS index
        metadata: Metadata list

    Returns:
        Dictionary with statistics
    """
    # Count by state
    states = {}
    for meta in metadata:
        state = meta.get('state', 'unknown')
        states[state] = states.get(state, 0) + 1

    # Count by doc_type
    doc_types = {}
    for meta in metadata:
        doc_type = meta.get('doc_type', 'unknown')
        doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

    return {
        'total_vectors': index.ntotal,
        'dimension': index.d,
        'states': states,
        'doc_types': doc_types,
        'is_trained': index.is_trained
    }


if __name__ == "__main__":
    """
    Test the FAISS indexer with sample data.
    """
    print("TESTING FAISS INDEXER")
    print("=" * 60)

    # Create sample chunks with embeddings
    print("\n1. Creating sample chunks with embeddings...")

    sample_chunks = [
        {
            "text": "Metformin is covered as Tier 1 with $10 copay.",
            "state": "NC",
            "doc_type": "formulary",
            "chunk_id": "NC-form-p23-c0",
            "page_num": 23,
            "embedding": np.random.rand(384).astype('float32')
        },
        {
            "text": "Lisinopril is covered as Tier 1 with $10 copay.",
            "state": "NC",
            "doc_type": "formulary",
            "chunk_id": "NC-form-p24-c0",
            "page_num": 24,
            "embedding": np.random.rand(384).astype('float32')
        },
        {
            "text": "What are generic drugs? They are lower-cost alternatives.",
            "state": "NC",
            "doc_type": "faq",
            "chunk_id": "NC-faq-p5-c0",
            "page_num": 5,
            "embedding": np.random.rand(384).astype('float32')
        },
        {
            "text": "Prior authorization is required for specialty medications.",
            "state": "NC",
            "doc_type": "faq",
            "chunk_id": "NC-faq-p8-c0",
            "page_num": 8,
            "embedding": np.random.rand(384).astype('float32')
        },
        {
            "text": "Atorvastatin is covered as Tier 2 with $25 copay.",
            "state": "TX",
            "doc_type": "formulary",
            "chunk_id": "TX-form-p10-c0",
            "page_num": 10,
            "embedding": np.random.rand(384).astype('float32')
        }
    ]

    print(f"Created {len(sample_chunks)} sample chunks")

    # Build index
    print("\n2. Building FAISS index...")
    index, metadata = build_index_from_chunks(sample_chunks, dimension=384)

    # Get statistics
    print("\n3. Index statistics:")
    stats = get_index_stats(index, metadata)
    print(f"  Total vectors: {stats['total_vectors']}")
    print(f"  Dimension: {stats['dimension']}")
    print(f"  States: {stats['states']}")
    print(f"  Doc types: {stats['doc_types']}")

    # Save index
    print("\n4. Saving index to disk...")
    output_dir = "data/processed/test"
    save_index(index, metadata, output_dir)

    # Load index
    print("\n5. Loading index from disk...")
    loaded_index, loaded_metadata = load_index(
        os.path.join(output_dir, "index.faiss"),
        os.path.join(output_dir, "metadata.json")
    )

    # Verify loaded index
    print("\n6. Verifying loaded index...")
    assert loaded_index.ntotal == index.ntotal, "Index size mismatch"
    assert len(loaded_metadata) == len(metadata), "Metadata size mismatch"
    print("✓ Loaded index matches original")

    # Search test
    print("\n7. Testing search...")
    query_embedding = np.random.rand(384).astype('float32')
    results = search_index(loaded_index, loaded_metadata, query_embedding, top_k=3)

    print(f"\nTop 3 search results:")
    for result in results:
        print(f"\n  Rank {result['rank']}:")
        print(f"    Text: {result['text'][:60]}...")
        print(f"    State: {result['state']}")
        print(f"    Doc Type: {result['doc_type']}")
        print(f"    Score (L2 distance): {result['score']:.4f}")

    # Clean up test files
    print("\n8. Cleaning up test files...")
    import shutil
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        print(f"Removed test directory: {output_dir}")

    print("\n" + "=" * 60)
    print("FAISS INDEXER TESTS COMPLETE")
    print("=" * 60)
