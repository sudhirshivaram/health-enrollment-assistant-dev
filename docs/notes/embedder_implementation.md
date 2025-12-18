# Embedder Implementation - Detailed Explanation

**File:** `src/ingestion/embedder.py`

**Purpose:** Convert text chunks into numerical vectors (embeddings) for semantic search

**Date Created:** 2025-12-17

---

## Overview

The embedder transforms text into 384-dimensional vectors that capture semantic meaning. This enables:
- **Semantic search**: Find chunks based on meaning, not just keywords
- **Similarity matching**: "diabetes medication" matches "treats diabetes"
- **Vector operations**: Fast similarity calculations in FAISS

---

## What are Embeddings?

### Concept

**Traditional keyword search:**
```
Query: "diabetes medication"
Matches: Documents containing exact words "diabetes" AND "medication"
Misses: Documents with "treats diabetes" (no word "medication")
```

**Embedding-based search:**
```
Query: "diabetes medication" → [0.23, -0.12, 0.45, ...] (384 numbers)
Doc 1: "treats diabetes"     → [0.25, -0.10, 0.43, ...] (similar!)
Doc 2: "blood pressure"      → [-0.15, 0.30, -0.20, ...] (different!)

Search: Find vectors closest to query vector
Result: Doc 1 found (even though words different!)
```

### Embedding Properties

**Dimensionality:** 384 numbers per text
- Each number represents some aspect of meaning
- Together they capture semantic content

**Similarity:**
```
Similar meanings → Similar vectors
"Metformin treats diabetes"     → [0.95 similarity]
"Metformin is diabetes drug"    → [0.96 similarity]

Different meanings → Different vectors
"Metformin treats diabetes"     → [0.15 similarity]
"Lisinopril lowers blood pressure"
```

---

## Model: all-MiniLM-L6-v2

### Why This Model?

**Characteristics:**
- **Size:** ~80MB (small, fast to load)
- **Speed:** ~50ms per text on CPU (fast inference)
- **Quality:** Good for general semantic similarity
- **Dimension:** 384 (compact)
- **Source:** HuggingFace sentence-transformers

**Alternatives (not chosen):**
- all-mpnet-base-v2: Better quality but slower, larger (438MB)
- all-MiniLM-L12-v2: Slightly better quality, slower
- OpenAI ada-002: High quality but costs money, API calls

**Our choice:** Best balance of speed, size, and quality for our use case

---

## Class: `Embedder`

### Initialization

```python
embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
```

**What happens:**
1. Downloads model from HuggingFace (first time only, ~80MB)
2. Loads model into memory
3. Gets embedding dimension (384)

**First run:**
```
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Downloading model... (80MB)
Model loaded. Embedding dimension: 384
```

**Subsequent runs:**
```
Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
Model loaded. Embedding dimension: 384  (instant, cached)
```

---

## Methods

### 1. `embed_text()` - Single Text

**Purpose:** Generate embedding for one text

**Usage:**
```python
text = "Metformin is a diabetes medication"
embedding = embedder.embed_text(text)
# Returns: numpy array of shape (384,)
```

**Output:**
```python
array([-0.119,  0.001,  0.020, ..., -0.085])  # 384 numbers
```

**When to use:**
- Testing
- Single query embedding
- Small-scale processing

---

### 2. `embed_texts()` - Multiple Texts (Batched)

**Purpose:** Generate embeddings for many texts efficiently

**Usage:**
```python
texts = [
    "Metformin is covered",
    "Lisinopril is covered",
    "Atorvastatin is covered",
    ...  # 1000 texts
]
embeddings = embedder.embed_texts(texts, batch_size=32)
# Returns: numpy array of shape (1000, 384)
```

**Why batching?**

**Without batching (slow):**
```python
# Process one at a time
for text in texts:  # 1000 texts
    emb = embed_text(text)  # 50ms each
# Total: 50,000ms = 50 seconds
```

**With batching (fast):**
```python
# Process 32 at a time
embeddings = embed_texts(texts, batch_size=32)
# Total: ~5 seconds (10x faster!)
```

**Parameters:**
- `batch_size=32`: Process 32 texts simultaneously (GPU/CPU parallelization)
- `show_progress=True`: Display progress bar

---

### 3. `embed_chunks()` - Chunks with Metadata

**Purpose:** Add embeddings to chunk dictionaries

**Input:**
```python
chunks = [
    {
        "text": "Metformin is covered...",
        "state": "NC",
        "doc_type": "formulary",
        "chunk_id": "NC-form-p23-c0",
        ...
    },
    ...
]
```

**Process:**
```python
chunks_with_embeddings = embedder.embed_chunks(chunks)
```

**Output:**
```python
[
    {
        "text": "Metformin is covered...",
        "state": "NC",
        "doc_type": "formulary",
        "chunk_id": "NC-form-p23-c0",
        "embedding": array([...])  # NEW! 384-dim vector
    },
    ...
]
```

**Implementation:**
```python
def embed_chunks(self, chunks):
    # Extract all text
    texts = [chunk['text'] for chunk in chunks]

    # Generate embeddings (batched, efficient)
    embeddings = self.embed_texts(texts)

    # Add to chunks
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = embeddings[i]

    return chunks
```

---

## Testing

### Test 1: Single Text

**Code:**
```python
text = "Metformin is covered as a Tier 1 medication with a $10 copay."
embedding = embedder.embed_text(text)
```

**Result:**
```
Embedding shape: (384,)
Embedding (first 10): [-0.119, 0.001, 0.020, ...]
Range: [-0.124, 0.163]
```

**Verification:** ✓ Shape correct, values in reasonable range

---

### Test 2: Multiple Texts (Batched)

**Code:**
```python
texts = [
    "Metformin is covered",
    "Lisinopril is covered",
    "Atorvastatin is covered",
    "What are generic drugs?",
    "How do I file an appeal?"
]
embeddings = embedder.embed_texts(texts)
```

**Result:**
```
Shape: (5, 384)
Each text → 384-dim vector
```

**Verification:** ✓ All 5 texts embedded correctly

---

### Test 3: Chunks with Metadata

**Code:**
```python
chunks = [
    {"text": "Metformin...", "state": "NC", ...},
    {"text": "Lisinopril...", "state": "NC", ...}
]
embedded_chunks = embedder.embed_chunks(chunks)
```

**Result:**
```
Chunks: 2
Each chunk now has 'embedding' field
Embedding shape: (384,)
```

**Verification:** ✓ Metadata preserved, embeddings added

---

### Test 4: Statistics

**Code:**
```python
stats = get_embedding_stats(embeddings)
```

**Result:**
```
{
    'num_embeddings': 5,
    'dimension': 384,
    'mean': -0.0001,
    'std': 0.0510,
    'min': -0.1612,
    'max': 0.2101,
    'memory_mb': 0.0073
}
```

**Verification:** ✓ Values normalized, memory reasonable

---

### Test 5: Semantic Similarity ⭐ IMPORTANT

**Code:**
```python
text1 = "Metformin is a diabetes medication"
text2 = "Metformin treats diabetes"  # Similar!
text3 = "Lisinopril is for blood pressure"  # Different!

emb1 = embedder.embed_text(text1)
emb2 = embedder.embed_text(text2)
emb3 = embedder.embed_text(text3)

# Cosine similarity
sim_1_2 = cosine_similarity(emb1, emb2)
sim_1_3 = cosine_similarity(emb1, emb3)
```

**Result:**
```
Similarity (1 vs 2 - similar topics):    0.9582  ← HIGH!
Similarity (1 vs 3 - different topics):  0.1497  ← LOW!

✓ PASS: Similar texts have high similarity
```

**This proves:** The embeddings capture semantic meaning!

---

## Cosine Similarity Explained

### What is it?

**Formula:**
```
similarity = (A · B) / (||A|| * ||B||)
```

**Range:** -1 to 1
- 1.0 = Identical meaning
- 0.0 = Unrelated
- -1.0 = Opposite meaning (rare)

### In Practice

**Our results:**
```
0.95-1.00: Nearly identical ("Metformin drug" vs "Metformin medication")
0.70-0.95: Very similar ("diabetes medication" vs "treats diabetes")
0.50-0.70: Somewhat related ("diabetes" vs "health")
0.00-0.50: Weakly related or unrelated
```

**Search threshold:**
- Retrieve chunks with similarity > 0.5
- Top-5 chunks = highest similarity scores

---

## Performance Considerations

### Speed

**Single text:**
- CPU: ~50ms
- GPU: ~10ms (if available)

**Batch (32 texts):**
- CPU: ~200ms (~6ms per text, 8x faster!)
- GPU: ~50ms (~1.5ms per text)

**1000 chunks:**
- Without batching: 50 seconds
- With batching (32): ~5 seconds
- **10x speedup from batching!**

### Memory

**Model:**
- ~80MB on disk
- ~200MB in RAM when loaded

**Embeddings:**
- 384 floats × 4 bytes = 1.5KB per embedding
- 1000 embeddings = 1.5MB
- 10,000 embeddings = 15MB
- **Very memory-efficient!**

---

## Design Decisions

### 1. Why sentence-transformers?

**Alternatives:**
- OpenAI API: Costs money, requires internet
- Custom training: Too complex, need data
- Word2Vec/GloVe: Outdated, lower quality

**sentence-transformers:** Best balance of quality, speed, cost (free!)

---

### 2. Why all-MiniLM-L6-v2?

**Comparison:**

| Model | Dimension | Size | Speed | Quality |
|-------|-----------|------|-------|---------|
| all-MiniLM-L6-v2 | 384 | 80MB | Fast | Good ✓ |
| all-mpnet-base-v2 | 768 | 438MB | Slow | Excellent |
| all-MiniLM-L12-v2 | 384 | 120MB | Medium | Very Good |

**Our choice:** L6-v2 for speed and size, quality sufficient for our use case

---

### 3. Why batch processing?

**GPU/CPU can process multiple texts in parallel:**
- Single text: 1 text/50ms = 20 texts/second
- Batch of 32: 32 texts/200ms = 160 texts/second
- **8x faster throughput!**

---

### 4. Why numpy arrays not lists?

**numpy arrays:**
- Efficient storage (contiguous memory)
- Fast mathematical operations
- FAISS requires numpy format
- Industry standard for ML

---

## Integration with Pipeline

### Input (from metadata tagger)
```python
chunks = [
    {
        "text": "Metformin is covered...",
        "state": "NC",
        "doc_type": "formulary",
        "chunk_id": "NC-form-p23-c0"
    },
    ...
]
```

### Process (embedder)
```python
embedder = Embedder()
embedded_chunks = embedder.embed_chunks(chunks)
```

### Output (to FAISS indexer)
```python
[
    {
        "text": "Metformin is covered...",
        "state": "NC",
        "doc_type": "formulary",
        "chunk_id": "NC-form-p23-c0",
        "embedding": array([...])  # Ready for FAISS!
    },
    ...
]
```

---

## Common Issues and Solutions

### Issue 1: Model download fails

**Error:**
```
ConnectionError: Unable to download model
```

**Solution:**
```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

---

### Issue 2: Out of memory

**Error:**
```
MemoryError: Unable to allocate array
```

**Cause:** Batch size too large

**Solution:**
```python
# Reduce batch size
embeddings = embedder.embed_texts(texts, batch_size=16)  # Was 32
```

---

### Issue 3: Slow embedding

**Problem:** Taking too long

**Solutions:**
1. Increase batch size (if memory allows)
2. Use GPU if available
3. Process in chunks, save progressively

---

## Next Steps in Pipeline

After embedding, chunks go to:

**FAISS Indexer** (`faiss_indexer.py`)
- Input: Chunks with embeddings
- Process: Create FAISS index for fast similarity search
- Output: Searchable index + metadata JSON

---

## Summary

The embedder is the heart of semantic search:
- Converts text to 384-dim vectors
- Uses sentence-transformers (all-MiniLM-L6-v2)
- Batched processing for efficiency (10x faster)
- Proven semantic similarity (0.96 for similar, 0.15 for different)
- Memory-efficient (1.5KB per embedding)
- Fast (6ms per text with batching)

**Key Metrics:**
- Model: all-MiniLM-L6-v2
- Dimension: 384
- Speed: ~6ms per text (batched)
- Quality: 0.95+ similarity for equivalent meanings

**Status:** ✅ Complete and tested

**Next Module:** FAISS Indexer
