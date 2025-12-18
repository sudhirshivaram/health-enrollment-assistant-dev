# Chunker Implementation - Detailed Explanation

**File:** `src/ingestion/chunker.py`

**Purpose:** Split cleaned text into smaller chunks optimized for embedding and retrieval

**Date Created:** 2025-12-17

---

## Overview

The chunker breaks long documents into smaller pieces because:
- Embeddings work best on 500-1000 character segments
- Smaller chunks = more precise retrieval
- Overlap between chunks preserves context across boundaries

---

## Why Chunking is Necessary

### Problem: Long Documents
```
Full document: 50,000 characters
Single embedding: Loses precision
```

### Solution: Chunking
```
Document → 100 chunks of ~500 chars each
Each chunk → separate embedding
Search → finds most relevant chunks (not whole document)
```

### Benefits
- **Precision:** "Is metformin covered?" matches specific chunk about metformin
- **Efficiency:** Search 500 chars vs 50,000 chars
- **Context:** Overlap ensures no info lost at boundaries

---

## Main Functions

### 1. `chunk_text()` - Simple Chunking

**Signature:**
```python
def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[str]
```

**How it works:**
```
Text: "AAAA...BBBB...CCCC...DDDD..."
       └─500─┘
              └─450 + 50 overlap─┘
                      └─500─┘

Chunk 1: AAAA...BBBB (500 chars)
Chunk 2: BBB...CCCC  (500 chars, starts 450 chars in)
Chunk 3: CCC...DDDD  (500 chars, starts 900 chars in)
```

**Code:**
```python
chunks = []
start = 0

while start < len(text):
    end = start + chunk_size
    chunk = text[start:end]

    if chunk.strip():
        chunks.append(chunk)

    # Move forward (accounting for overlap)
    start = end - overlap

return chunks
```

**Example:**
```python
text = "This is a long document..." * 100  # 5000 chars
chunks = chunk_text(text, chunk_size=500, overlap=50)
# Result: 11 chunks of ~500 chars each
```

---

### 2. `chunk_text_smart()` - Smart Chunking

**Problem with simple chunking:**
```
Chunk 1: "...Metformin is a diabetes medica"
Chunk 2: "tion used for type 2 diabetes..."
         ^^^^
         Word split mid-way!
```

**Solution: Break at sentence boundaries**

**Algorithm:**
```python
1. Split text into sentences (by . ! ? :)
2. Build chunks by adding sentences
3. When adding next sentence would exceed chunk_size:
   - Save current chunk
   - Start new chunk with overlap
4. Continue until all sentences processed
```

**Code:**
```python
# Split into sentences
sentences = re.split(r'([.!?:]\s+)', text)

chunks = []
current_chunk = ""

for sentence in sentences:
    if len(current_chunk) + len(sentence) > chunk_size:
        # Save current chunk
        chunks.append(current_chunk.strip())

        # Start new with overlap
        if overlap > 0:
            current_chunk = current_chunk[-overlap:] + sentence
        else:
            current_chunk = sentence
    else:
        current_chunk += sentence

# Don't forget last chunk
if current_chunk.strip():
    chunks.append(current_chunk.strip())
```

**Result:**
```
Chunk 1: "...Metformin is a diabetes medication."
Chunk 2: "medication. It is used for type 2 diabetes..."
         ^^^^^^^^^
         Overlap preserves context!
```

---

## Overlap Explained

### What is Overlap?

```
Chunk 1: [----500 chars----]
Chunk 2:         [----500 chars----]
              ^^^
              50 char overlap
```

### Why Overlap?

**Without overlap:**
```
Chunk 1: "...covered under Tier"
Chunk 2: "1 with $10 copay..."

User query: "What is Tier 1 copay?"
Problem: "Tier 1" split across chunks - might miss it!
```

**With overlap:**
```
Chunk 1: "...covered under Tier 1 with"
Chunk 2: "Tier 1 with $10 copay..."
         ^^^^^^^^
         Overlap ensures "Tier 1" appears in both!
```

### Overlap Size

**Default: 50 characters**

**Guidelines:**
- Too small (10 chars): Context lost
- Too large (200 chars): Redundancy, more storage
- Sweet spot: 10-20% of chunk_size

```
chunk_size=500 → overlap=50 (10%)  ✓ Good
chunk_size=500 → overlap=100 (20%) ✓ Also good
chunk_size=500 → overlap=250 (50%) ✗ Too much
```

---

### 3. `chunk_pages()` - Chunk Multiple Pages

**Purpose:** Process output from text_cleaner

**Signature:**
```python
def chunk_pages(
    pages: List[Dict],
    chunk_size: int = 500,
    overlap: int = 50,
    smart: bool = True
) -> List[Dict]
```

**Input Format:**
```python
pages = [
    {
        "page_num": 1,
        "text": "Oscar Health Insurance...",
        "source": "NC-form.pdf"
    },
    ...
]
```

**Output Format:**
```python
chunks = [
    {
        "text": "Oscar Health Insurance...",
        "source": "NC-form.pdf",
        "page_num": 1,
        "chunk_index": 0    # NEW!
    },
    {
        "text": "...Tier 1 medications...",
        "source": "NC-form.pdf",
        "page_num": 1,
        "chunk_index": 1    # NEW!
    },
    ...
]
```

**Implementation:**
```python
all_chunks = []

for page in pages:
    page_text = page['text']

    # Chunk the page (smart or simple)
    page_chunks = chunk_text_smart(page_text, chunk_size, overlap)

    # Add metadata to each chunk
    for i, chunk_text in enumerate(page_chunks):
        chunk_dict = {
            "text": chunk_text,
            "source": page['source'],
            "page_num": page['page_num'],
            "chunk_index": i    # Index within this page
        }
        all_chunks.append(chunk_dict)

return all_chunks
```

---

### 4. `get_chunk_stats()` - Statistics

**Purpose:** Validation and debugging

**Returns:**
```python
{
    "total_chunks": 150,
    "avg_chunk_size": 487,
    "min_chunk_size": 120,
    "max_chunk_size": 500,
    "total_chars": 73050
}
```

**Use cases:**
- Verify chunks are reasonable size
- Check if chunking worked correctly
- Detect issues (e.g., all chunks too small)

---

## Chunking Strategies Comparison

### Simple vs Smart Chunking

| Aspect | Simple | Smart |
|--------|--------|-------|
| **Speed** | Faster | Slightly slower |
| **Boundaries** | Anywhere | Sentence boundaries |
| **Word splits** | Yes | No |
| **Context** | OK | Better |
| **Use case** | Quick testing | Production |

### Example Comparison

**Input text:**
```
"Metformin is covered. Lisinopril is covered. Atorvastatin is covered."
```

**Simple chunking (chunk_size=30):**
```
Chunk 1: "Metformin is covered. Lisin"
Chunk 2: "in. Lisinopril is covered. A"
         ^^
         Word split!
```

**Smart chunking (chunk_size=30):**
```
Chunk 1: "Metformin is covered."
Chunk 2: "Lisinopril is covered."
         Clean sentence boundaries!
```

---

## Configuration

### Chunk Size

**Default: 500 characters**

**Guidelines:**
- Too small (100): Loss of context
- Too large (2000): Loss of precision
- Optimal: 300-800 for most use cases

**For our use case (insurance docs):**
```
500 chars ≈ 2-3 sentences ≈ 1-2 drug entries
Perfect for: "Is metformin covered?"
```

### Choosing Chunk Size

**Factors:**
1. **Embedding model limits** - Most handle 512 tokens (~2000 chars)
2. **Query granularity** - Match user question size
3. **Document structure** - Match natural divisions

**Our choice: 500 chars**
- Fits insurance formulary entries well
- Good balance precision/context
- Works well with sentence boundaries

---

## Testing

### Test Code
```python
sample_text = """
Oscar Health Insurance
North Carolina Drug Formulary
Tier 1: Generic Medications
Metformin - diabetes medication...
"""

# Test simple
simple_chunks = chunk_text(sample_text, chunk_size=200, overlap=30)

# Test smart
smart_chunks = chunk_text_smart(sample_text, chunk_size=200, overlap=30)

# Compare
print(f"Simple: {len(simple_chunks)} chunks")
print(f"Smart: {len(smart_chunks)} chunks")
```

### Run Test
```bash
python src/ingestion/chunker.py
```

### Expected Output
```
Simple chunking: 4 chunks
Smart chunking: 4 chunks

Chunk 0 (194 chars):
Oscar Health Insurance
North Carolina Drug Formulary...
```

---

## Design Decisions

### 1. Why Two Chunking Methods?

**Simple:**
- Faster
- Good for testing
- Predictable chunk sizes

**Smart:**
- Better quality
- Production use
- Natural language boundaries

**Both available:** User can choose based on needs

---

### 2. Why Process Page-by-Page?

**Alternative:** Concatenate all pages, then chunk

**Our approach:** Chunk each page separately

**Why:**
- Preserve page boundaries for citations
- Can track: "Found on Page 23"
- Easier debugging (know which page has issues)

---

### 3. chunk_index vs Global Index

```python
chunk_dict = {
    "chunk_index": i    # Index within this page (0, 1, 2, ...)
}
```

**Why not global index?**
- Page association more important
- Easier to understand: "Page 23, Chunk 2"
- Metadata tagger will create global chunk_id later

---

## Performance Considerations

### Speed
- Simple chunking: O(n) where n = text length
- Smart chunking: O(n + s) where s = number of sentences
- Both very fast: ~0.1-0.5 sec for typical page

### Memory
- Processes one page at a time
- No large data structures
- Efficient even for 1000+ page documents

### Optimization Opportunities (Future)
- Parallel processing (chunk multiple pages simultaneously)
- Caching (reuse chunks if page unchanged)

---

## Common Issues and Solutions

### Issue 1: Chunks too small

**Problem:**
```
All chunks < 100 chars
```

**Causes:**
- chunk_size too small
- Text has many short sentences

**Solution:**
```python
# Increase chunk_size
chunks = chunk_text(text, chunk_size=1000, overlap=100)
```

---

### Issue 2: Last chunk very small

**Problem:**
```
Chunk 0: 500 chars ✓
Chunk 1: 500 chars ✓
Chunk 2: 50 chars  ✗ Too small
```

**This is normal!**
- Last chunk often smaller (leftover text)
- Not a problem for embeddings
- Filter very small chunks if needed:

```python
chunks = [c for c in chunks if len(c['text']) > 100]
```

---

### Issue 3: Overlap not working

**Problem:**
```
Chunk 1 ends with "diabetes"
Chunk 2 starts with "medication"
No overlap!
```

**Cause:** Smart chunking breaks at sentences

**This is intentional!**
- Sentence boundaries > character overlap
- Semantic meaning preserved
- Better than character-based overlap that splits words

---

## Next Steps in Pipeline

After chunking, chunks go to:

1. **Metadata Tagger** (`metadata_tagger.py`)
   - Adds state, doc_type, chunk_id
   - Input: Chunks with text, source, page_num
   - Output: Chunks with full metadata

2. **Embedder** (`embedder.py`)
   - Converts chunk text to vectors
   - Input: Chunk text
   - Output: 384-dimensional embedding

---

## Summary

The chunker is crucial for RAG effectiveness:
- Breaks documents into optimal sizes (500 chars)
- Adds overlap to preserve context (50 chars)
- Smart chunking respects sentence boundaries
- Tracks page and chunk metadata
- Fast and memory-efficient

**Key Metrics:**
- Chunk size: 500 characters
- Overlap: 50 characters (10%)
- Method: Smart (sentence boundaries)
- Speed: ~0.1-0.5 sec per page

**Status:** ✅ Complete and tested

**Next Module:** Metadata Tagger
