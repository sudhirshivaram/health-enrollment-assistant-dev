# Phase 1: Simple RAG - Task Breakdown

**Goal:** Build a working RAG system that can answer simple questions from insurance PDFs

**Timeline:** 2-3 weeks

---

## Task Overview

Phase 1 has **3 main components** to build:

1. **Data Ingestion Pipeline** - Process PDFs into FAISS index
2. **Retrieval System** - Search and retrieve relevant chunks
3. **User Interface** - Gradio app with LLM integration

---

## PART 1: Data Ingestion Pipeline (Week 1)

Build the offline pipeline that processes PDFs once before any user queries.

### Task 1.1: PDF Parser
**File:** `src/ingestion/pdf_parser.py`

**What it does:**
- Read PDF files
- Extract text content
- Extract page numbers for citations

**Key functions:**
```python
def parse_pdf(pdf_path: str) -> List[Dict]:
    """
    Parse a PDF and return pages with text and metadata.

    Returns:
        [
            {"page_num": 1, "text": "...", "source": "NC-formulary.pdf"},
            {"page_num": 2, "text": "...", "source": "NC-formulary.pdf"},
            ...
        ]
    """
```

**Libraries:** pdfplumber (primary), PyPDF2 (fallback)

**Testing:** Parse a sample PDF and verify text extraction


### Task 1.2: Text Cleaner
**File:** `src/ingestion/text_cleaner.py`

**What it does:**
- Remove extra whitespace
- Fix broken line breaks
- Remove headers/footers (common in PDFs)
- Normalize text

**Key functions:**
```python
def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.
    """
```

**Testing:** Feed messy PDF text, verify it's cleaned


### Task 1.3: Text Chunker
**File:** `src/ingestion/chunker.py`

**What it does:**
- Split text into chunks (500 chars each)
- Add overlap (50 chars) to preserve context
- Avoid breaking mid-sentence if possible

**Key functions:**
```python
def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into overlapping chunks.

    Returns:
        ["chunk 1 text...", "chunk 2 text...", ...]
    """
```

**Testing:** Chunk sample text, verify size and overlap


### Task 1.4: Metadata Tagger
**File:** `src/ingestion/metadata_tagger.py`

**What it does:**
- Tag each chunk with metadata:
  - source_file
  - state (NC, TX, etc.)
  - doc_type (formulary or faq)
  - page_number
  - chunk_id

**Key functions:**
```python
def tag_chunks(chunks: List[str], metadata: Dict) -> List[Dict]:
    """
    Add metadata to each chunk.

    Returns:
        [
            {
                "text": "...",
                "source_file": "NC-formulary.pdf",
                "state": "NC",
                "doc_type": "formulary",
                "page": 23,
                "chunk_id": "NC-form-23-1"
            },
            ...
        ]
    """
```

**Testing:** Verify metadata is correctly attached


### Task 1.5: Embedding Generator
**File:** `src/ingestion/embedder.py`

**What it does:**
- Load sentence-transformers model
- Convert text chunks to embeddings (vectors)
- Return 384-dimensional vectors

**Key functions:**
```python
def generate_embeddings(chunks: List[str]) -> np.ndarray:
    """
    Generate embeddings for text chunks.

    Returns:
        numpy array of shape (num_chunks, 384)
    """
```

**Libraries:** sentence-transformers

**Testing:** Generate embeddings for sample text, verify shape


### Task 1.6: FAISS Index Builder
**File:** `src/ingestion/faiss_indexer.py`

**What it does:**
- Create FAISS index
- Add embeddings to index
- Save index to disk
- Save metadata separately (JSON)

**Key functions:**
```python
def create_index(embeddings: np.ndarray, dimension: int):
    """
    Create a FAISS index.
    """

def save_index(index, metadata: List[Dict], output_dir: str):
    """
    Save FAISS index and metadata to disk.

    Saves:
        - output_dir/index.faiss
        - output_dir/metadata.json
    """
```

**Libraries:** faiss

**Testing:** Create index with sample data, save and reload


### Task 1.7: Pipeline Orchestrator
**File:** `src/ingestion/run_pipeline.py`

**What it does:**
- Orchestrate the entire ingestion pipeline
- Load config from config.yaml
- Process all PDFs in data/raw/
- Save FAISS index to data/processed/

**Key functions:**
```python
def run_ingestion_pipeline(config_path: str):
    """
    Run the complete ingestion pipeline.

    Steps:
        1. Load config
        2. Find all PDFs in data/raw/
        3. Parse PDFs
        4. Clean text
        5. Chunk text
        6. Tag metadata
        7. Generate embeddings
        8. Create FAISS index
        9. Save index and metadata
    """
```

**Testing:** Run end-to-end with sample PDFs

---

## PART 2: Retrieval System (Week 1-2)

Build the system that searches FAISS and retrieves relevant chunks.

### Task 2.1: FAISS Loader
**File:** `src/retrieval/faiss_loader.py`

**What it does:**
- Load FAISS index from disk
- Load metadata from JSON

**Key functions:**
```python
def load_index(index_path: str, metadata_path: str):
    """
    Load FAISS index and metadata.

    Returns:
        (faiss_index, metadata_list)
    """
```

**Testing:** Load previously saved index


### Task 2.2: Retriever
**File:** `src/retrieval/retriever.py`

**What it does:**
- Take user query
- Generate query embedding
- Search FAISS for top K similar chunks
- Return chunks with metadata

**Key functions:**
```python
def retrieve(query: str, index, metadata: List[Dict], top_k: int = 5):
    """
    Retrieve top K relevant chunks for a query.

    Returns:
        [
            {
                "text": "...",
                "score": 0.89,
                "source_file": "NC-formulary.pdf",
                "page": 23,
                ...
            },
            ...
        ]
    """
```

**Testing:** Query with sample questions, verify results

---

## PART 3: LLM Integration (Week 2)

Connect to Gemini API and generate answers.

### Task 3.1: Prompt Builder
**File:** `src/generation/prompt_builder.py`

**What it does:**
- Build prompts from template
- Insert retrieved chunks as context
- Insert user query

**Key functions:**
```python
def build_prompt(query: str, retrieved_chunks: List[Dict], config: Dict) -> str:
    """
    Build prompt for LLM.

    Template:
        System: {system_prompt}
        Context: {chunks}
        Question: {query}
    """
```

**Testing:** Build prompt, verify format


### Task 3.2: LLM Client
**File:** `src/generation/llm_client.py`

**What it does:**
- Initialize Gemini API client
- Send prompt to Gemini
- Get response
- Handle errors and rate limits

**Key functions:**
```python
def initialize_client(api_key: str):
    """
    Initialize Gemini client.
    """

def generate_response(prompt: str, config: Dict) -> str:
    """
    Generate response from Gemini.

    Uses config for:
        - model name
        - temperature
        - max_tokens
    """
```

**Libraries:** google-generativeai

**Testing:** Send test prompt, verify response


### Task 3.3: Response Formatter
**File:** `src/generation/response_formatter.py`

**What it does:**
- Format LLM response
- Add source citations
- Format nicely for display

**Key functions:**
```python
def format_response(answer: str, sources: List[Dict]) -> str:
    """
    Format final response with sources.

    Output:
        Answer: {LLM response}

        Sources:
        - NC Formulary, Page 23
        - NC FAQ, Page 5
    """
```

**Testing:** Format sample response

---

## PART 4: User Interface (Week 2)

Build Gradio web interface.

### Task 4.1: Gradio App
**File:** `src/app/gradio_app.py`

**What it does:**
- Create Gradio interface
- Text input for user question
- Display area for answer
- Connect all components:
  - Load FAISS index
  - Retrieve chunks
  - Generate answer
  - Display response

**Key functions:**
```python
def answer_question(query: str, config: Dict) -> str:
    """
    Main function that handles user query.

    Steps:
        1. Retrieve relevant chunks
        2. Build prompt
        3. Call LLM
        4. Format response
        5. Return to user
    """

def launch_app(config_path: str):
    """
    Launch Gradio interface.
    """
```

**Libraries:** gradio

**Testing:** Run app, ask questions, verify answers

---

## PART 5: Configuration and Utils (Throughout)

### Task 5.1: Config Loader
**File:** `src/utils/config_loader.py`

**What it does:**
- Load config.yaml
- Validate configuration
- Provide easy access to settings

**Key functions:**
```python
def load_config(config_path: str) -> Dict:
    """
    Load and validate configuration.
    """
```

**Libraries:** pyyaml


### Task 5.2: Logger Setup
**File:** `src/utils/logger.py`

**What it does:**
- Set up logging
- Log to file and console
- Different log levels (INFO, DEBUG, ERROR)

**Testing:** Verify logs are written

---

## Implementation Order (Recommended)

Follow this order to build incrementally:

### Week 1: Data Pipeline

1. **Day 1-2:** PDF Parser + Text Cleaner
   - Parse sample PDF
   - Clean extracted text
   - Verify quality

2. **Day 3:** Chunker + Metadata Tagger
   - Chunk cleaned text
   - Add metadata
   - Verify chunks look good

3. **Day 4-5:** Embedder + FAISS Indexer
   - Generate embeddings
   - Create FAISS index
   - Save to disk

4. **Day 6:** Pipeline Orchestrator
   - Connect all components
   - Run end-to-end
   - Process sample PDFs

### Week 2: Retrieval + LLM + UI

5. **Day 7:** Retriever
   - Load FAISS index
   - Test queries
   - Verify retrieval works

6. **Day 8-9:** LLM Integration
   - Set up Gemini client
   - Build prompts
   - Test responses

7. **Day 10-11:** Gradio UI
   - Build interface
   - Connect all parts
   - Test end-to-end

8. **Day 12-14:** Testing + Refinement
   - Test with real questions
   - Fix bugs
   - Improve prompts
   - Tune parameters (chunk size, top_k, etc.)

---

## Testing Strategy

For each component:
1. **Unit test** - Test the function in isolation
2. **Integration test** - Test with other components
3. **End-to-end test** - Test complete flow

---

## Success Criteria

Phase 1 is complete when:

- [ ] Can process PDFs into FAISS index
- [ ] Can load index and retrieve relevant chunks
- [ ] Can generate accurate answers using Gemini
- [ ] Gradio UI works and is user-friendly
- [ ] Response time < 5 seconds
- [ ] Answers are factually correct for simple queries
- [ ] Sources are properly cited

---

## Files to Create (Summary)

**Ingestion (7 files):**
- `src/ingestion/pdf_parser.py`
- `src/ingestion/text_cleaner.py`
- `src/ingestion/chunker.py`
- `src/ingestion/metadata_tagger.py`
- `src/ingestion/embedder.py`
- `src/ingestion/faiss_indexer.py`
- `src/ingestion/run_pipeline.py`

**Retrieval (2 files):**
- `src/retrieval/faiss_loader.py`
- `src/retrieval/retriever.py`

**Generation (3 files):**
- `src/generation/prompt_builder.py`
- `src/generation/llm_client.py`
- `src/generation/response_formatter.py`

**App (1 file):**
- `src/app/gradio_app.py`

**Utils (2 files):**
- `src/utils/config_loader.py`
- `src/utils/logger.py`

**Total: 15 Python files**

---

## Next Steps

After understanding this breakdown:
1. Start with Task 1.1 (PDF Parser)
2. Build and test each component
3. Integrate gradually
4. Test end-to-end

Ready to start coding?
