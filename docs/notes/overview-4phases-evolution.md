# Health Enrollment Assistant - 4 Phases Evolution Overview

**Document Purpose:** High-level summary of the system's evolution from Simple RAG to Full Agentic architecture.

**Date Created:** 2025-12-17

---

## Evolution Strategy: Progressive Complexity

We are building the system in 4 progressive phases, starting simple and adding intelligence incrementally.

```
Phase 1 (Simple) → Phase 2 (Routing) → Phase 3 (Light Agents) → Phase 4 (Full Agentic)
```

---

## Phase 1: Simple RAG (Week 1-2)

### What It Does
Basic retrieval pipeline - like a smart search engine.

### Architecture
```
User Query → Embedding → Vector Search (FAISS) → Retrieve Documents → LLM → Response
```

### Characteristics
- Linear pipeline
- No decision making
- One retrieval step
- Simple to implement

### Good For
- Straightforward questions
- "Is metformin covered?"
- "What are generic drugs?"

### Limitations
- Cannot handle complex queries
- No state routing
- No query classification
- One-size-fits-all approach

---

## Phase 2: Smart Routing (Week 3-4)

### What It Does
Adds intelligent routing with if/else logic to send queries to the right data sources.

### Architecture
```
User Query
    ↓
Query Classifier (Coverage? Educational? Hybrid?)
    ↓
State Router (NC? TX? FL?)
    ↓
Document Type Selector (Formulary? FAQ? Both?)
    ↓
Targeted Vector Search
    ↓
LLM Generation → Response
```

### Characteristics
- Deterministic decision making
- Routes to correct state
- Selects appropriate document type
- More efficient searches

### Good For
- State-specific queries
- Routing to formulary vs FAQ
- Reducing irrelevant results

### Limitations
- Still rigid, rule-based
- Cannot handle truly complex queries
- No multi-round searching
- No self-correction

---

## Phase 3: Light Agents (Week 5-6)

### What It Does
Introduces LLM-based agents that make intelligent decisions and can perform multi-round searches.

### Architecture
```
User Query
    ↓
Orchestrator Agent (LLM-based decision maker)
    ↓
┌─────────┬────────────┬──────────────┬───────────────┐
│Query    │State       │Document      │Retrieval      │
│Agent    │Agent       │Agent         │Agent          │
└─────────┴────────────┴──────────────┴───────────────┘
    ↓
Validation Agent (checks quality)
    ↓
Response Agent → Response + Confidence Score
```

### Agents Introduced
1. **Query Agent** - Understands intent, extracts entities
2. **State Agent** - Identifies state(s), handles multi-state
3. **Document Agent** - Classifies and routes to correct sources
4. **Retrieval Agent** - Performs multi-round search if needed
5. **Validation Agent** - Checks answer quality
6. **Response Agent** - Synthesizes final answer

### Characteristics
- LLM-based decision making
- Multi-round searches possible
- Quality validation
- Confidence scoring

### Good For
- Moderately complex queries
- Multi-state questions
- Queries needing multiple data sources

### Limitations
- Not fully autonomous
- Limited comparison capabilities
- No alternative suggestions
- No query decomposition

---

## Phase 4: Full Agentic (Week 7-8)

### What It Does
Complete autonomous agent system with self-correction, query decomposition, and advanced capabilities.

### Architecture
```
User Query
    ↓
ORCHESTRATOR AGENT (Central coordinator)
    ↓
┌────────┬────────┬──────────┬───────────┬────────────┬─────────────┬─────────────┐
│Query   │State   │Document  │Retrieval  │Comparison  │Alternative  │Explanation  │
│Agent   │Agent   │Agent     │Agent      │Agent       │Finder       │Agent        │
└────────┴────────┴──────────┴───────────┴────────────┴─────────────┴─────────────┘
    ↓
Self-Correction Loop (agent reviews own work)
    ↓
Validation Agent
    ↓
Response Generation Agent
    ↓
Response with:
- Answer
- Sources
- Confidence score
- Alternatives
- Follow-up questions
```

### All Agents
1. **Query Agent** - Intent, entity extraction, query decomposition
2. **State Agent** - Multi-state handling
3. **Document Agent** - Source routing
4. **Retrieval Agent** - Multi-round, adaptive search
5. **Comparison Agent** - Compare options, costs, coverage
6. **Alternative Finder Agent** - Suggest similar covered drugs
7. **Explanation Agent** - Explain insurance terms simply
8. **Validation Agent** - Quality assurance
9. **Response Generation Agent** - Final synthesis

### New Capabilities
- Complex query decomposition
- Multi-state comparisons
- Cost calculations
- Alternative drug suggestions
- Self-correction and validation
- Confidence scoring
- Follow-up question generation

### Good For
- Highly complex queries
- Multi-step reasoning
- Comparisons across states
- Finding alternatives
- Educational explanations

### Characteristics
- Fully autonomous
- Self-correcting
- Handles any query complexity
- Most flexible and intelligent

---

## Query Complexity Examples

### Simple Query (Phase 1 handles)
**Query:** "Is metformin covered in North Carolina?"
**Answer:** Direct lookup → "Yes, Tier 1, $10 copay"

### Moderate Query (Phase 2-3 handles)
**Query:** "What are generic drugs in Texas?"
**Process:** Route to TX FAQ → Retrieve educational content → Explain

### Complex Query (Phase 3-4 handles)
**Query:** "My drug Humira isn't on the formulary in Texas. What are my options?"
**Process:**
1. Confirm Humira not covered (formulary search)
2. Find appeals process (FAQ search)
3. Search for similar covered biologics
4. Compare alternatives
5. Synthesize comprehensive answer

### Very Complex Query (Phase 4 handles)
**Query:** "Compare metformin costs between North Carolina and Texas, and show me cheaper alternatives if Texas is more expensive"
**Process:**
1. Multi-state parallel search (NC + TX)
2. Extract costs from both states
3. Compare costs
4. If TX more expensive → search for alternatives
5. Rank alternatives by cost
6. Generate comparison report

---

## Data Architecture (All Phases)

### Ingestion Pipeline
```
Oscar Health PDFs
    ↓
PDF Parser (PyPDF2/pdfplumber)
    ↓
Text Extraction & Cleaning
    ↓
Chunking (semantic with overlap)
    ↓
Metadata Tagging (state, doc type, drug name)
    ↓
Embedding Generation (sentence-transformers)
    ↓
Vector Store (FAISS)
```

### Storage Structure
```
data/
├── raw/
│   ├── formularies/
│   │   ├── NC-2026-formulary.pdf
│   │   └── TX-2026-formulary.pdf
│   └── faqs/
│       ├── NC-2026-faq.pdf
│       └── TX-2026-faq.pdf
└── processed/
    ├── embeddings/
    │   ├── NC-formulary.faiss
    │   └── NC-faq.faiss
    └── metadata/
        ├── NC-formulary-metadata.json
        └── NC-faq-metadata.json
```

---

## Technology Stack

### Core Components
- **Framework:** LlamaIndex (RAG orchestration)
- **LLM:** Google Gemini 2.0 Flash (free tier)
- **Vector DB:** FAISS (local, free)
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **PDF Parsing:** PyPDF2 / pdfplumber
- **Frontend:** Gradio (MVP) → Streamlit (advanced)

### Fallback LLMs
- OpenAI GPT-4o-mini
- Anthropic Claude 3.5 Haiku

### Deployment
- **MVP:** HuggingFace Spaces (1-2 states)
- **Multi-state:** Railway/Render
- **Production:** AWS/Azure

---

## Design Principles

1. **Progressive Complexity** - Start simple, add intelligence incrementally
2. **State Isolation** - Separate data/indexes per state
3. **Modular Architecture** - Components can be upgraded independently
4. **Metadata-Rich** - Every chunk has metadata for filtering
5. **Source Transparency** - Always cite sources, build trust

---

## When to Stop

You don't have to complete all 4 phases. Stop when:
- Phase 1 is enough → Basic queries work fine
- Phase 2 is enough → Routing solves most problems
- Phase 3 is enough → Light agents handle complexity
- Phase 4 needed → Maximum flexibility required

---

## Timeline Estimate

- **Phase 1:** 2-3 weeks
- **Phase 2:** 1-2 weeks
- **Phase 3:** 2-3 weeks
- **Phase 4:** 1-2 weeks

**Total:** 6-9 weeks for complete system

---

## Current Status

- Architecture designed ✓
- Documentation complete ✓
- Ready to start Phase 1 implementation

---

**Next Action:** Begin Phase 1 - Simple RAG implementation
