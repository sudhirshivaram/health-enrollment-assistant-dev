# Phase 1: Simple RAG Architecture

**Phase Duration:** Week 1-2
**Goal:** Build a basic working RAG system that can answer simple questions from PDFs

---

## High-Level Overview

```
User asks question → System searches PDFs → Finds relevant info → LLM generates answer
```

Simple, straightforward pipeline. No intelligence, no decision making, just basic retrieval.

---

## Detailed Architecture Diagram

```
================================================================================
                        PHASE 1: SIMPLE RAG SYSTEM
================================================================================


                            [USER INTERFACE]
                            (Gradio Web App)
                                  |
                                  | User types question
                                  | e.g., "Is metformin covered?"
                                  |
                                  v
                          +----------------+
                          |  QUERY INPUT   |
                          |                |
                          | Input: string  |
                          | Output: string |
                          +----------------+
                                  |
                                  |
                                  v
================================================================================
                          QUERY PROCESSING
================================================================================

                          +------------------+
                          | QUERY EMBEDDING  |
                          |                  |
                          | Tool: sentence-  |
                          |       transformers|
                          | Model: all-MiniLM|
                          |        -L6-v2    |
                          |                  |
                          | Input: "Is metf.."|
                          | Output: [0.23,   |
                          |         0.45,    |
                          |         -0.12,   |
                          |         ... ]    |
                          |    (384 dims)    |
                          +------------------+
                                  |
                                  |
                                  v
================================================================================
                          RETRIEVAL STAGE
================================================================================

                          +------------------+
                          | VECTOR SEARCH    |
                          |    (FAISS)       |
                          |                  |
                          | Action:          |
                          | - Compare query  |
                          |   embedding with |
                          |   all document   |
                          |   embeddings     |
                          | - Find top K     |
                          |   similar chunks |
                          |                  |
                          | Input: embedding |
                          | Output: top 5    |
                          |         chunks   |
                          +------------------+
                                  |
                                  |
                                  v
                          +------------------+
                          | RETRIEVED DOCS   |
                          |                  |
                          | Chunk 1: "Metf.. |
                          |   Tier 1, $10"   |
                          | Chunk 2: "Generic|
                          |   drugs include."|
                          | Chunk 3: ...     |
                          | Chunk 4: ...     |
                          | Chunk 5: ...     |
                          |                  |
                          | Each chunk has:  |
                          | - Text content   |
                          | - Metadata (state|
                          |   doc_type, page)|
                          +------------------+
                                  |
                                  |
                                  v
================================================================================
                          GENERATION STAGE
================================================================================

                          +------------------+
                          | PROMPT BUILD     |
                          |                  |
                          | Combines:        |
                          | 1. System prompt |
                          | 2. User query    |
                          | 3. Retrieved     |
                          |    context       |
                          |                  |
                          | Template:        |
                          | "You are an      |
                          | insurance helper.|
                          | Use this context:|
                          | {chunks}         |
                          | Answer: {query}" |
                          +------------------+
                                  |
                                  |
                                  v
                          +------------------+
                          |  LLM GENERATION  |
                          |                  |
                          | Model: Gemini    |
                          |        2.0 Flash |
                          |                  |
                          | Input: Prompt    |
                          |        with ctx  |
                          |                  |
                          | Output: Natural  |
                          |         language |
                          |         answer   |
                          +------------------+
                                  |
                                  |
                                  v
                          +------------------+
                          | RESPONSE FORMAT  |
                          |                  |
                          | Answer: "Yes,    |
                          | metformin is     |
                          | covered as Tier  |
                          | 1 medication..."  |
                          |                  |
                          | Sources:         |
                          | - NC Formulary   |
                          |   Page 23        |
                          +------------------+
                                  |
                                  |
                                  v
                            [USER SEES ANSWER]
                            (in Gradio UI)


================================================================================
                          DATA PIPELINE (OFFLINE)
================================================================================

This runs ONCE to prepare data, before any user queries.


    +----------------------+
    |  RAW PDF FILES       |
    |                      |
    | - NC-formulary.pdf   |
    | - NC-faq.pdf         |
    | - TX-formulary.pdf   |  <-- Start here
    | - TX-faq.pdf         |
    +----------------------+
            |
            | Feed into parser
            |
            v
    +----------------------+
    |  PDF PARSER          |
    |                      |
    | Tool: PyPDF2 or      |
    |       pdfplumber     |
    |                      |
    | Action:              |
    | - Read PDF           |
    | - Extract text       |
    | - Extract metadata   |
    |   (page numbers)     |
    +----------------------+
            |
            | Raw text extracted
            |
            v
    +----------------------+
    |  TEXT CLEANING       |
    |                      |
    | Action:              |
    | - Remove extra spaces|
    | - Fix line breaks    |
    | - Remove headers/    |
    |   footers            |
    | - Normalize text     |
    +----------------------+
            |
            | Clean text
            |
            v
    +----------------------+
    |  TEXT CHUNKING       |
    |                      |
    | Strategy: Fixed size |
    | with overlap         |
    |                      |
    | Chunk size: 500 chars|
    | Overlap: 50 chars    |
    |                      |
    | Why overlap?         |
    | - Preserve context   |
    | - Don't break mid-   |
    |   sentence           |
    +----------------------+
            |
            | Text chunks created
            |
            v
    +----------------------+
    |  METADATA TAGGING    |
    |                      |
    | For each chunk, add: |
    | - source_file        |
    | - state (NC, TX)     |
    | - doc_type (form/faq)|
    | - page_number        |
    | - chunk_id           |
    |                      |
    | Example:             |
    | {                    |
    |   text: "Metformin..",|
    |   state: "NC",       |
    |   doc_type: "form",  |
    |   page: 23           |
    | }                    |
    +----------------------+
            |
            | Chunks with metadata
            |
            v
    +----------------------+
    |  EMBEDDING           |
    |  GENERATION          |
    |                      |
    | Model: sentence-     |
    |        transformers  |
    |        all-MiniLM-   |
    |        L6-v2         |
    |                      |
    | For each chunk:      |
    | text → [0.23, 0.45,  |
    |         -0.12, ...]  |
    |     (384 dimensions) |
    +----------------------+
            |
            | Embeddings created
            |
            v
    +----------------------+
    |  FAISS INDEX         |
    |  CREATION            |
    |                      |
    | Action:              |
    | - Create FAISS index |
    | - Add all embeddings |
    | - Save to disk       |
    |                      |
    | Output files:        |
    | - index.faiss        |
    | - metadata.json      |
    +----------------------+
            |
            | Ready for queries!
            |
            v
    [ System ready to answer questions ]


================================================================================
                          COMPONENT BREAKDOWN
================================================================================

### 1. USER INTERFACE (Gradio)

**What it does:**
- Provides web interface for users
- Text input box for questions
- Display area for answers

**Technology:** Gradio (Python library)

**Why Gradio:**
- Quick to set up (5 lines of code)
- Automatic web interface
- Good for demos and prototypes


### 2. QUERY EMBEDDING (sentence-transformers)

**What it does:**
- Converts user's text question into a vector (list of numbers)
- This vector represents the meaning of the question

**Technology:** sentence-transformers library
**Model:** all-MiniLM-L6-v2

**Why this model:**
- Small (80MB)
- Fast (milliseconds)
- Free
- Good quality
- 384 dimensions (compact)

**Example:**
```
Input:  "Is metformin covered?"
Output: [0.234, -0.123, 0.567, ..., 0.891]  (384 numbers)
```


### 3. VECTOR SEARCH (FAISS)

**What it does:**
- Compares query vector with all document vectors
- Finds the K most similar chunks
- Returns top matches

**Technology:** FAISS (Facebook AI Similarity Search)

**Why FAISS:**
- Very fast (millions of vectors in milliseconds)
- Works locally (no internet needed)
- Free and open source
- Industry standard

**Parameters:**
- K = 5 (retrieve top 5 chunks)
- Can be adjusted based on results


### 4. LLM GENERATION (Gemini 2.0 Flash)

**What it does:**
- Reads the retrieved chunks
- Reads the user's question
- Generates a natural language answer

**Technology:** Google Gemini 2.0 Flash API

**Why Gemini:**
- Free tier (generous limits)
- Fast responses (1-2 seconds)
- Good quality answers
- Easy API

**Free tier limits:**
- 15 requests per minute
- 1 million tokens per minute
- 1500 requests per day


### 5. PDF PROCESSING (PyPDF2/pdfplumber)

**What it does:**
- Reads PDF files
- Extracts text content
- Extracts page numbers

**Technology:** PyPDF2 or pdfplumber

**Why these:**
- Simple to use
- Pure Python (no external dependencies)
- Handle most PDFs well


================================================================================
                          DATA FLOW EXAMPLE
================================================================================

Let's walk through a real example:

**User Question:** "Is metformin covered in North Carolina?"


STEP 1: Query Embedding
------------------------
Input:  "Is metformin covered in North Carolina?"
Process: sentence-transformers converts to vector
Output: [0.234, -0.123, 0.567, ..., 0.891] (384 numbers)


STEP 2: Vector Search in FAISS
-------------------------------
Process: Compare query vector with all 10,000 document chunk vectors
Action:  Find 5 most similar chunks
Output:
  Chunk 1 (similarity: 0.89): "Metformin is covered as Tier 1..."
  Chunk 2 (similarity: 0.82): "North Carolina formulary includes..."
  Chunk 3 (similarity: 0.78): "Tier 1 medications have $10 copay..."
  Chunk 4 (similarity: 0.75): "Generic diabetes medications..."
  Chunk 5 (similarity: 0.71): "Prior authorization not required..."


STEP 3: Prompt Construction
----------------------------
System: "You are a health insurance assistant. Answer based on context."

Context:
  [Chunk 1 text]
  [Chunk 2 text]
  [Chunk 3 text]
  [Chunk 4 text]
  [Chunk 5 text]

Question: "Is metformin covered in North Carolina?"


STEP 4: LLM Generation
-----------------------
Input:  Full prompt with context
Process: Gemini 2.0 Flash generates answer
Output: "Yes, metformin is covered in North Carolina as a Tier 1
         medication with a $10 copay. Prior authorization is not
         required for this generic diabetes medication."


STEP 5: Display to User
------------------------
User sees:
  Answer: [LLM output]

  Sources:
  - North Carolina Formulary 2026, Page 23
  - North Carolina FAQ, Page 5


================================================================================
                          FILE STRUCTURE
================================================================================

```
health-enrollment-assistant-dev/
│
├── src/
│   ├── ingestion/
│   │   ├── pdf_parser.py          # Parse PDFs
│   │   ├── text_cleaner.py        # Clean extracted text
│   │   ├── chunker.py             # Split into chunks
│   │   └── embedder.py            # Generate embeddings
│   │
│   ├── retrieval/
│   │   ├── faiss_indexer.py       # Create/manage FAISS index
│   │   └── retriever.py           # Search and retrieve
│   │
│   ├── generation/
│   │   ├── llm_client.py          # Gemini API client
│   │   └── prompt_builder.py      # Build prompts
│   │
│   └── app/
│       └── gradio_app.py          # User interface
│
├── data/
│   ├── raw/
│   │   └── pdfs/                  # Original PDFs
│   │
│   └── processed/
│       ├── index.faiss            # FAISS vector index
│       └── metadata.json          # Chunk metadata
│
├── config/
│   └── config.yaml                # Configuration
│
├── requirements.txt               # Python dependencies
└── .env                          # API keys (not committed)
```


================================================================================
                          CONFIGURATION
================================================================================

### Key Parameters

```yaml
# Chunking
chunk_size: 500              # Characters per chunk
chunk_overlap: 50            # Overlap between chunks

# Retrieval
top_k: 5                     # Number of chunks to retrieve

# Embedding
model_name: "sentence-transformers/all-MiniLM-L6-v2"
embedding_dim: 384

# LLM
llm_provider: "gemini"
model: "gemini-2.0-flash"
temperature: 0.3             # Lower = more focused
max_tokens: 500              # Response length limit

# UI
interface: "gradio"
port: 7860
share: false                 # Create public link?
```


================================================================================
                          WHAT PHASE 1 CAN DO
================================================================================

### Handles Well

1. Simple coverage questions
   - "Is Lipitor covered?"
   - "What tier is metformin?"

2. Educational questions
   - "What are generic drugs?"
   - "What is prior authorization?"

3. State-specific questions (if state mentioned)
   - "Is metformin covered in North Carolina?"


### Cannot Handle

1. Multi-state comparisons
   - "Compare metformin costs in NC vs TX"

2. Complex queries
   - "My drug isn't covered, what are my options?"

3. Alternative suggestions
   - "Show me cheaper alternatives to Advair"

4. Queries without state mentioned
   - System doesn't know which state to search


### Why It's Limited

- No query classification
- No state routing
- No document type selection
- Single retrieval round
- No validation or confidence scoring

These limitations are addressed in Phase 2 and beyond.


================================================================================
                          SUCCESS CRITERIA
================================================================================

Phase 1 is successful when:

1. System can ingest PDFs and create FAISS index
2. User can ask a question in Gradio interface
3. System retrieves relevant chunks
4. LLM generates accurate answer
5. Sources are cited properly
6. Response time < 5 seconds
7. Answers are factually correct for simple queries


================================================================================
                          NEXT STEPS
================================================================================

After understanding this architecture:

1. Set up development environment
2. Install dependencies (requirements.txt)
3. Build data ingestion pipeline
4. Create FAISS index from sample PDFs
5. Build retrieval system
6. Integrate Gemini LLM
7. Create Gradio interface
8. Test with sample queries
9. Evaluate and iterate


================================================================================
```

## Summary

Phase 1 is a **straight-line pipeline** with no branching or decision making:
- User asks → Embed query → Search FAISS → Retrieve chunks → LLM answers

It's simple, fast to build, and teaches us:
- How the data works
- What queries users ask
- What retrieval quality looks like
- What we need to improve

This foundation makes Phase 2 and beyond much easier.
