"""
Embedding Generator Module

Converts text chunks into numerical vectors (embeddings) for semantic search.

Uses sentence-transformers library with all-MiniLM-L6-v2 model:
- 384-dimensional vectors
- Fast inference (~50ms per text)
- Good quality for semantic similarity
"""

import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer


class Embedder:
    """
    Handles text-to-embedding conversion using sentence-transformers.

    The model is loaded once and reused for all embeddings.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedder with a specific model.

        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2)

        Model Details:
            - Size: ~80MB
            - Speed: Fast (~50ms per text on CPU)
            - Output: 384 dimensions
            - Quality: Good for general semantic similarity
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        print(f"Model loaded. Embedding dimension: {self.dimension}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.

        Args:
            text: Input text string

        Returns:
            numpy array of shape (384,) - the embedding vector

        Example:
            >>> embedder = Embedder()
            >>> embedding = embedder.embed_text("Metformin is a diabetes medication")
            >>> embedding.shape
            (384,)
        """
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def embed_texts(self, texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batched for efficiency).

        Args:
            texts: List of text strings
            batch_size: Number of texts to process at once (default: 32)
            show_progress: Show progress bar (default: True)

        Returns:
            numpy array of shape (num_texts, 384) - matrix of embeddings

        Example:
            >>> texts = ["Text 1", "Text 2", "Text 3"]
            >>> embeddings = embedder.embed_texts(texts)
            >>> embeddings.shape
            (3, 384)
        """
        # Generate embeddings in batches
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings

    def embed_chunks(self, chunks: List[Dict], batch_size: int = 32, show_progress: bool = True) -> List[Dict]:
        """
        Add embeddings to chunk dictionaries.

        Args:
            chunks: List of chunk dictionaries from metadata_tagger
            batch_size: Batch size for processing
            show_progress: Show progress bar

        Returns:
            List of chunks with 'embedding' field added

        Example:
            >>> chunks = [{"text": "...", "state": "NC", ...}, ...]
            >>> chunks_with_embeddings = embedder.embed_chunks(chunks)
            >>> chunks_with_embeddings[0]['embedding'].shape
            (384,)
        """
        # Extract text from all chunks
        texts = [chunk['text'] for chunk in chunks]

        # Generate embeddings for all texts
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embed_texts(texts, batch_size=batch_size, show_progress=show_progress)

        # Add embeddings to chunks
        chunks_with_embeddings = []
        for i, chunk in enumerate(chunks):
            chunk_copy = chunk.copy()
            chunk_copy['embedding'] = embeddings[i]
            chunks_with_embeddings.append(chunk_copy)

        print(f"Embeddings generated: {embeddings.shape}")
        return chunks_with_embeddings

    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this model.

        Returns:
            Integer dimension (384 for all-MiniLM-L6-v2)
        """
        return self.dimension


def create_embedder(model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> Embedder:
    """
    Factory function to create an Embedder instance.

    Args:
        model_name: HuggingFace model name

    Returns:
        Initialized Embedder object
    """
    return Embedder(model_name)


def get_embedding_stats(embeddings: np.ndarray) -> Dict:
    """
    Get statistics about embeddings.

    Useful for validation and debugging.

    Args:
        embeddings: numpy array of embeddings (shape: num_texts x dimension)

    Returns:
        Dictionary with statistics
    """
    return {
        "num_embeddings": embeddings.shape[0],
        "dimension": embeddings.shape[1],
        "mean": float(np.mean(embeddings)),
        "std": float(np.std(embeddings)),
        "min": float(np.min(embeddings)),
        "max": float(np.max(embeddings)),
        "memory_mb": embeddings.nbytes / (1024 * 1024)
    }


if __name__ == "__main__":
    """
    Test the embedder with sample text.
    """
    print("TESTING EMBEDDER")
    print("=" * 60)

    # Create embedder
    embedder = create_embedder()

    print("\n")
    print("TEST 1: Single text embedding")
    print("=" * 60)

    sample_text = "Metformin is covered as a Tier 1 medication with a $10 copay."
    embedding = embedder.embed_text(sample_text)

    print(f"\nText: {sample_text}")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding (first 10 values): {embedding[:10]}")
    print(f"Embedding range: [{embedding.min():.3f}, {embedding.max():.3f}]")

    print("\n")
    print("TEST 2: Multiple texts embedding (batched)")
    print("=" * 60)

    sample_texts = [
        "Metformin is covered as Tier 1 with $10 copay.",
        "Lisinopril is covered as Tier 1 with $10 copay.",
        "Atorvastatin is covered as Tier 2 with $25 copay.",
        "What are generic drugs?",
        "How do I file an appeal?"
    ]

    embeddings = embedder.embed_texts(sample_texts, show_progress=False)

    print(f"\nNumber of texts: {len(sample_texts)}")
    print(f"Embeddings shape: {embeddings.shape}")
    print(f"\nFirst text: {sample_texts[0][:50]}...")
    print(f"First embedding (first 10 values): {embeddings[0][:10]}")

    print("\n")
    print("TEST 3: Embedding chunks with metadata")
    print("=" * 60)

    sample_chunks = [
        {
            "text": "Metformin is covered as Tier 1.",
            "source": "NC-formulary.pdf",
            "page_num": 23,
            "chunk_index": 0,
            "state": "NC",
            "doc_type": "formulary",
            "chunk_id": "NC-form-p23-c0"
        },
        {
            "text": "What are generic drugs?",
            "source": "NC-FAQ.pdf",
            "page_num": 5,
            "chunk_index": 0,
            "state": "NC",
            "doc_type": "faq",
            "chunk_id": "NC-faq-p5-c0"
        }
    ]

    chunks_with_embeddings = embedder.embed_chunks(sample_chunks, show_progress=False)

    print(f"\nChunks processed: {len(chunks_with_embeddings)}")
    print(f"\nFirst chunk:")
    print(f"  Text: {chunks_with_embeddings[0]['text'][:50]}...")
    print(f"  State: {chunks_with_embeddings[0]['state']}")
    print(f"  Doc Type: {chunks_with_embeddings[0]['doc_type']}")
    print(f"  Embedding shape: {chunks_with_embeddings[0]['embedding'].shape}")
    print(f"  Embedding (first 5 values): {chunks_with_embeddings[0]['embedding'][:5]}")

    print("\n")
    print("TEST 4: Embedding statistics")
    print("=" * 60)

    stats = get_embedding_stats(embeddings)
    print(f"\nEmbedding Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    print("\n")
    print("TEST 5: Semantic similarity")
    print("=" * 60)

    # Test similarity between similar and different texts
    text1 = "Metformin is a diabetes medication"
    text2 = "Metformin treats diabetes"  # Similar
    text3 = "Lisinopril is for blood pressure"  # Different

    emb1 = embedder.embed_text(text1)
    emb2 = embedder.embed_text(text2)
    emb3 = embedder.embed_text(text3)

    # Cosine similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    sim_1_2 = cosine_similarity(emb1, emb2)
    sim_1_3 = cosine_similarity(emb1, emb3)

    print(f"\nText 1: {text1}")
    print(f"Text 2: {text2}")
    print(f"Text 3: {text3}")
    print(f"\nSimilarity (1 vs 2 - similar topics): {sim_1_2:.4f}")
    print(f"Similarity (1 vs 3 - different topics): {sim_1_3:.4f}")
    print(f"\nExpected: Similarity (1 vs 2) > Similarity (1 vs 3)")
    print(f"Result: {'✓ PASS' if sim_1_2 > sim_1_3 else '✗ FAIL'}")

    print("\n")
    print("EMBEDDER TESTS COMPLETE")
    print("=" * 60)
