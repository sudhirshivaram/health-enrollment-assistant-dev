# Health Enrollment Assistant - Overall System Architecture

## Complete System Evolution (All Phases)

```
                                    USER INTERFACE
                                    (Gradio/Streamlit)
                                          |
                                          |
                                    User Query Input
                                          |
                                          v
================================================================================
                            PHASE 1: SIMPLE RAG (Week 1-2)
================================================================================

    User Query
        |
        v
    [Query Embedding]
    (sentence-transformers)
        |
        v
    [Vector Search - FAISS]
        |
        v
    [Retrieve Top-K Documents]
    (Formulary PDFs + FAQ PDFs)
        |
        v
    [Prompt Construction]
    (Query + Retrieved Context)
        |
        v
    [LLM Generation]
    (Google Gemini 2.0 Flash)
        |
        v
    Response with Sources


                        DATA SOURCES (Phase 1)
                        ----------------------
    [Formulary PDFs] --> [PDF Parser] --> [Text Chunks] --> [Embeddings] --> [FAISS Index]
    [FAQ PDFs]       --> [PDF Parser] --> [Text Chunks] --> [Embeddings] --> [FAISS Index]


================================================================================
                    PHASE 2: SMART ROUTING (Week 3-4)
================================================================================

    User Query
        |
        v
    [Query Classifier]  <-- Simple if/else or lightweight model
        |
        |-----> Determines Query Type:
        |         - Coverage Query (formulary)
        |         - Educational Query (FAQ)
        |         - Hybrid Query (both)
        |
        v
    [State Router]  <-- Extracts/identifies state
        |
        |-----> Routes to correct state's data:
        |         - North Carolina
        |         - Texas
        |         - Florida
        |         - etc.
        |
        v
    [Document Type Selector]
        |
        |-----> Selects data source:
        |         - Formulary only
        |         - FAQ only
        |         - Both
        |
        v
    [Targeted Vector Search]
    (Search only relevant documents)
        |
        v
    [LLM Generation with Context]
        |
        v
    Response with Sources


                        DATA SOURCES (Phase 2)
                        ----------------------
    State 1: NC    --> [Formulary FAISS] + [FAQ FAISS]
    State 2: TX    --> [Formulary FAISS] + [FAQ FAISS]
    State 3: FL    --> [Formulary FAISS] + [FAQ FAISS]
    ...
    (Separate indexes per state + document type)


================================================================================
                    PHASE 3: LIGHT AGENTS (Week 5-6)
================================================================================

    User Query
        |
        v
    [Orchestrator Agent]  <-- LLM-based decision maker
        |
        |-----> Analyzes query complexity
        |-----> Decides strategy
        |
        v
    +------------------+------------------+------------------+
    |                  |                  |                  |
    v                  v                  v                  v
[Query Agent]    [State Agent]    [Document Agent]    [Retrieval Agent]
    |                  |                  |                  |
    |                  |                  |                  |
    v                  v                  v                  v
Understands      Identifies       Classifies         Performs
intent,          state(s),        doc types,         multi-round
extracts         handles          routes to          search if
entities         multi-state      correct            needed
                 queries          sources
    |                  |                  |                  |
    +------------------+------------------+------------------+
                        |
                        v
                [Validation Agent]  <-- Checks answer quality
                        |
                        v
                [Response Agent]  <-- Synthesizes final answer
                        |
                        v
                Response with Sources + Confidence Score


================================================================================
                    PHASE 4: FULL AGENTIC (Week 7-8)
================================================================================

    User Query
        |
        v
    [ORCHESTRATOR AGENT]
    (Central decision maker)
        |
        |-----> Decomposes complex queries
        |-----> Plans multi-step execution
        |-----> Coordinates sub-agents
        |
        v
    +--------+--------+--------+--------+--------+--------+
    |        |        |        |        |        |        |
    v        v        v        v        v        v        v
[Query]  [State] [Document] [Retrieval] [Comparison] [Alternative] [Explanation]
Agent    Agent   Agent      Agent       Agent        Finder        Agent
                                                     Agent
    |        |        |        |        |        |        |
    |        |        |        |        |        |        |
    +--------+--------+--------+--------+--------+--------+
                        |
                        v
                [Self-Correction Loop]
                (Agent reviews its own answers)
                        |
                        v
                [Validation Agent]
                        |
                        v
                [Response Generation Agent]
                        |
                        v
            Response with:
            - Answer
            - Sources
            - Confidence score
            - Alternative suggestions
            - Follow-up questions


                    ADVANCED CAPABILITIES (Phase 4)
                    --------------------------------
    - Multi-state comparisons
    - Cost calculations
    - Alternative drug suggestions
    - Complex query decomposition
    - Self-correction and validation
    - Confidence scoring
    - Follow-up question generation


================================================================================
                            DATA ARCHITECTURE
================================================================================

                        INGESTION PIPELINE
                        ------------------

    Oscar Health PDFs
        |
        |-----> [Formulary PDFs by State]
        |-----> [FAQ PDFs by State]
        |-----> [Provider Network PDFs] (Future)
        |
        v
    [PDF Parser]
    (PyPDF2 / pdfplumber)
        |
        v
    [Text Extraction & Cleaning]
        |
        v
    [Chunking Strategy]
    (Semantic chunking with overlap)
        |
        v
    [Metadata Tagging]
    - State
    - Document type
    - Drug name (if formulary)
    - Section (if FAQ)
        |
        v
    [Embedding Generation]
    (sentence-transformers)
        |
        v
    [Vector Store]
    (FAISS - local file storage)


                        STORAGE STRUCTURE
                        -----------------

    data/
    ├── raw/
    │   ├── formularies/
    │   │   ├── NC-2026-formulary.pdf
    │   │   ├── TX-2026-formulary.pdf
    │   │   └── ...
    │   └── faqs/
    │       ├── NC-2026-faq.pdf
    │       ├── TX-2026-faq.pdf
    │       └── ...
    │
    └── processed/
        ├── embeddings/
        │   ├── NC-formulary.faiss
        │   ├── NC-faq.faiss
        │   ├── TX-formulary.faiss
        │   └── ...
        │
        └── metadata/
            ├── NC-formulary-metadata.json
            ├── NC-faq-metadata.json
            └── ...


================================================================================
                        TECHNOLOGY STACK
================================================================================

    FRAMEWORK:          LlamaIndex (RAG orchestration)
    LLM:                Google Gemini 2.0 Flash (free tier)
                        + OpenAI GPT-4o-mini (fallback)
                        + Anthropic Claude Haiku (fallback)

    VECTOR DB:          FAISS (local, Phase 1-2)
                        → Pinecone (cloud, Phase 3-4 optional)

    EMBEDDINGS:         sentence-transformers/all-MiniLM-L6-v2

    PDF PARSING:        PyPDF2 / pdfplumber

    FRONTEND:           Gradio (Phase 1-2)
                        → Streamlit (Phase 3-4 for richer UI)

    DEPLOYMENT:         HuggingFace Spaces (MVP - 1-2 states)
                        → Railway/Render (Multi-state)
                        → AWS/Azure (Production)


================================================================================
                        KEY DESIGN PRINCIPLES
================================================================================

1. PROGRESSIVE COMPLEXITY
   - Start simple, add intelligence incrementally
   - Each phase builds on previous phase
   - Can stop at any phase if it meets needs

2. STATE ISOLATION
   - Each state has separate data/indexes
   - Prevents cross-state confusion
   - Easier to add new states

3. MODULAR ARCHITECTURE
   - Each component can be upgraded independently
   - Easy to swap LLMs, vector DBs, etc.
   - Testing is easier

4. METADATA-RICH
   - Every document chunk has metadata
   - Enables filtering and routing
   - Improves retrieval accuracy

5. SOURCE TRANSPARENCY
   - Always cite sources
   - Show which PDF page
   - Build user trust


================================================================================
                        QUERY FLOW EXAMPLES
================================================================================

EXAMPLE 1: Simple Coverage Query (Phase 1 handles well)
--------------------------------------------------------
Query: "Is metformin covered in North Carolina?"

Phase 1 Flow:
    Query → Embed → FAISS Search → Retrieve formulary chunks
    → LLM generates answer → "Yes, Tier 1, $10 copay"


EXAMPLE 2: Educational Query (Phase 1 handles well)
----------------------------------------------------
Query: "What are generic drugs?"

Phase 1 Flow:
    Query → Embed → FAISS Search → Retrieve FAQ chunks
    → LLM generates answer → Educational explanation


EXAMPLE 3: Complex Hybrid Query (Needs Phase 3+)
-------------------------------------------------
Query: "My drug Humira isn't on the formulary in Texas. What are my options?"

Phase 3 Flow:
    Query → Orchestrator Agent
        ↓
    Query Agent: Identifies drug (Humira), state (TX), problem (not covered)
        ↓
    Document Agent: Routes to TX formulary + TX FAQ
        ↓
    Retrieval Agent:
        - Round 1: Confirm Humira not in formulary
        - Round 2: Find FAQ section "drug not on formulary"
        - Round 3: Search for similar biologics that ARE covered
        ↓
    Comparison Agent: Finds alternatives (Enbrel, Remicade)
        ↓
    Response Agent: Synthesizes answer with:
        - Confirmation Humira not covered
        - Appeals process from FAQ
        - Alternative covered drugs
        - Contact information


EXAMPLE 4: Multi-State Comparison (Needs Phase 4)
--------------------------------------------------
Query: "Compare metformin costs between North Carolina and Texas"

Phase 4 Flow:
    Query → Orchestrator Agent
        ↓
    State Agent: Identifies NC + TX (multi-state query)
        ↓
    Retrieval Agent:
        - Parallel search in NC formulary
        - Parallel search in TX formulary
        ↓
    Comparison Agent:
        - Extract NC tier + cost
        - Extract TX tier + cost
        - Compare differences
        ↓
    Response Agent:
        "In North Carolina: Tier 1, $10 copay
         In Texas: Tier 1, $15 copay
         Texas is $5 more expensive"


================================================================================
```

## Document Status

This is the complete system architecture showing evolution across all 4 phases.

Next step: Break this down into individual phase diagrams for clearer implementation focus.
