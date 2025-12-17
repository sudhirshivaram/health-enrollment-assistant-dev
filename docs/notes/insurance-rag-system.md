# Insurance RAG System - Comprehensive Project Plan

## Project Overview

An intelligent insurance assistant powered by RAG (Retrieval-Augmented Generation) that helps users understand their Oscar Health insurance coverage, drug formularies, and state-specific policies through natural language queries.

---

## Problem Statement

**Current Pain Points:**
- Insurance formularies are complex, lengthy PDF documents
- Users struggle to find if specific medications are covered
- Understanding coverage tiers, restrictions, and requirements is difficult
- State-specific policies and FAQ information is scattered
- No easy way to get quick answers without reading entire documents

**Solution:**
A conversational AI system that can answer questions about drug coverage, costs, restrictions, and general insurance policies by intelligently searching across formulary documents and FAQ materials.

---

## Project Vision

### What Users Can Ask:

**Coverage Questions:**
- "Is Lipitor covered under my plan?"
- "What tier is metformin in North Carolina?"
- "Does Humira require prior authorization?"
- "What's the cost difference between brand and generic Lipitor?"

**Educational Questions:**
- "What are generic drugs?"
- "What's the difference between specialty drugs and regular drugs?"
- "How do drug tiers work?"
- "What is prior authorization?"

**State-Specific Policy Questions:**
- "What are the coverage restrictions in Texas?"
- "How often does the formulary change in my state?"
- "What are the appeals process in California?"

**Hybrid Questions:**
- "My drug isn't on the formulary - what are my options in Florida?"
- "Show me cheaper alternatives to Advair that are covered"
- "What tier 1 diabetes medications are available?"

---

## Data Sources

### 1. Drug Formulary Documents
**Source:** https://www.hioscar.com/search-documents/drug-formularies/

**Contains:**
- Medication names (brand and generic)
- Coverage tier levels (Tier 1, 2, 3, 4)
- Prior authorization requirements
- Quantity limits
- Step therapy requirements
- Coverage restrictions

**Format:** PDF documents organized by network and year

### 2. State-Specific FAQ Documents
**Source:** Oscar Health state-specific coverage documents

**Contains:**
- "What are generic drugs?"
- "What are specialty drugs?"
- "Are there any restrictions on my coverage?"
- "What if my drug is not on the Formulary?"
- "Can the Formulary change?"
- Appeals and exceptions process
- State-specific regulations
- Coverage policies

**Format:** PDF documents organized by state

### 3. Provider Network Data (Optional - Phase 2)
**Source:** https://www.hioscar.com/search/?networkId=043&year=2026

**Contains:**
- In-network doctors and providers
- Specialty information
- Location data
- Atrium Network coverage

---

## Technical Architecture

### High-Level Architecture

```
User Query → Query Processing → Hybrid Search → Reranking → LLM Generation → Response with Sources
                                        ↓
                                  Vector Database
                                  (FAISS/Pinecone)
                                        ↓
                                Document Store
                              (Formularies + FAQs)
```

### Components

#### 1. Data Ingestion Pipeline
- **PDF Processing:** PyPDF2, pdfplumber, or LlamaParse
- **Text Extraction:** Handle tables, multi-column layouts
- **Chunking Strategy:**
  - Formulary data: By drug entry or section
  - FAQ data: By question-answer pair or topic
- **Metadata Extraction:**
  - State
  - Document type (formulary vs FAQ)
  - Network ID
  - Year
  - Drug category (if applicable)

#### 2. Embedding & Vector Storage
- **Embedding Model:**
  - Option 1: OpenAI text-embedding-3-large (3072 dim)
  - Option 2: Jina AI embeddings (1024 dim)
  - Option 3: sentence-transformers (768 dim, free)
- **Vector Database:**
  - Option 1: FAISS (local, fast, free)
  - Option 2: Pinecone (managed, scalable)
  - Option 3: Weaviate (open source, self-hosted)

#### 3. Retrieval System
- **Hybrid Search:**
  - BM25 (keyword matching) - good for drug names
  - Vector search (semantic) - good for conceptual questions
  - Reciprocal Rank Fusion (RRF) to combine results
- **Metadata Filtering:**
  - Filter by state
  - Filter by document type (formulary vs FAQ)
  - Filter by year/network
- **Reranking:**
  - Cohere Rerank-3
  - Or cross-encoder models

#### 4. LLM Integration
- **Primary LLM Options:**
  - Google Gemini 2.0 Flash (fast, cost-effective)
  - OpenAI GPT-4o-mini
  - Anthropic Claude 3.5 Haiku
- **Fallback Architecture:**
  - Tier 1: Gemini (free tier)
  - Tier 2: Claude Haiku
  - Tier 3: GPT-4o-mini
  - Tier 4: Local LLaMA (if needed)
- **Prompt Engineering:**
  - System prompt with insurance domain context
  - Few-shot examples for common queries
  - Instruction to cite sources
  - Format for "not found" responses

#### 5. Frontend/Interface
- **Option 1:** Gradio (quick prototyping)
- **Option 2:** Streamlit (more customizable)
- **Option 3:** FastAPI backend + React frontend (production-grade)

**Features:**
- Chat interface
- State selector dropdown
- Document type filter (Formulary/FAQ/Both)
- Source citation display
- Confidence scores
- "Ask example questions" suggestions

---

## Tech Stack Recommendations

### MVP Stack (Fastest to Deploy)
```
Language: Python
Document Processing: PyPDF2, pdfplumber
Embeddings: sentence-transformers (free)
Vector DB: FAISS (local)
Search: BM25 (rank-bm25) + FAISS
LLM: Google Gemini 2.0 Flash (free tier)
Framework: LlamaIndex or LangChain
Frontend: Gradio
Deployment: HuggingFace Spaces
```

### Production Stack (Most Robust)
```
Language: Python
Document Processing: LlamaParse (better accuracy)
Embeddings: Jina AI or OpenAI
Vector DB: Pinecone or Weaviate
Search: Hybrid (BM25 + Vector) + Cohere Rerank
LLM: Multi-tier fallback (Gemini → Claude → GPT)
Framework: LangChain or custom
Frontend: Streamlit or FastAPI + React
Backend: FastAPI
Deployment: Railway or AWS
```

---

## Implementation Phases

### Phase 1: MVP - Single State Demo (2-3 weeks)
**Goal:** Prove the concept works

**Tasks:**
- [ ] Choose one state (e.g., North Carolina)
- [ ] Collect formulary PDF for one network
- [ ] Collect state FAQ PDF
- [ ] Build data ingestion pipeline
- [ ] Create embeddings and vector store
- [ ] Implement basic RAG pipeline
- [ ] Build simple Gradio interface
- [ ] Test with 20-30 sample questions
- [ ] Deploy to HuggingFace Spaces

**Deliverable:** Working demo for one state with basic Q&A

### Phase 2: Multi-State Expansion (1-2 weeks)
**Goal:** Scale to multiple states

**Tasks:**
- [ ] Collect formularies and FAQs for 3-5 states
- [ ] Implement state-based metadata filtering
- [ ] Add state selector in UI
- [ ] Test cross-state queries
- [ ] Add drug category filtering
- [ ] Improve chunking strategy based on Phase 1 learnings

**Deliverable:** Multi-state coverage with filtering

### Phase 3: Advanced Features (2-3 weeks)
**Goal:** Production-ready features

**Tasks:**
- [ ] Implement hybrid search (BM25 + Vector)
- [ ] Add reranking (Cohere or cross-encoder)
- [ ] Build query expansion system
- [ ] Add conversation memory (chat history)
- [ ] Implement cost tracking
- [ ] Add drug alternatives suggestion
- [ ] Build evaluation framework (RAGAS metrics)
- [ ] Add source citation with page numbers
- [ ] Improve UI/UX (better styling, examples)

**Deliverable:** Polished, feature-rich application

### Phase 4: Optimization & Documentation (1 week)
**Goal:** Portfolio-ready project

**Tasks:**
- [ ] Performance optimization (caching, indexing)
- [ ] Comprehensive documentation
  - [ ] README with screenshots
  - [ ] Architecture diagram
  - [ ] API documentation
  - [ ] Setup guide
- [ ] Write blog post or case study
- [ ] Record demo video
- [ ] Prepare presentation slides
- [ ] Add to portfolio website

**Deliverable:** Polished portfolio project with documentation

---

## Key Technical Challenges & Solutions

### Challenge 1: PDF Table Extraction
**Problem:** Formulary data is often in tables (drug name, tier, restrictions)

**Solutions:**
- Use `pdfplumber` with table extraction
- Use `camelot-py` for complex tables
- Consider LlamaParse for best accuracy (paid)
- Post-process with pandas for structured data

### Challenge 2: Chunking Strategy
**Problem:** Different document types need different chunking

**Solutions:**
- **Formulary:** Chunk by drug entry or category section
- **FAQ:** Chunk by Q&A pair or topic
- Keep metadata (state, doc type, page number) with each chunk
- Use semantic chunking (LangChain) for better context

### Challenge 3: Handling "Not Found" Queries
**Problem:** Drug not in formulary or info not in documents

**Solutions:**
- Confidence threshold for retrieval
- Explicit "not found" response template
- Suggest checking with insurance provider
- Recommend alternative search strategies

### Challenge 4: State-Specific vs General Questions
**Problem:** Some questions are general, some are state-specific

**Solutions:**
- Query classification (state-specific vs general)
- Metadata filtering based on query type
- Hybrid search that can handle both
- Clear indication in response about scope

### Challenge 5: Cost Management
**Problem:** LLM API costs can add up

**Solutions:**
- Multi-tier LLM fallback (free → paid)
- Caching for common queries
- Use smaller models (Gemini Flash, Haiku)
- Batch processing for embeddings
- Monitor usage with tracking

---

## Evaluation Metrics

### Retrieval Metrics
- **Precision@K:** Are the top K results relevant?
- **Recall@K:** Did we retrieve all relevant documents?
- **MRR (Mean Reciprocal Rank):** How high is the first relevant result?

### RAG-Specific Metrics (RAGAS)
- **Faithfulness:** Is the answer grounded in retrieved context?
- **Answer Relevancy:** Does the answer address the question?
- **Context Precision:** Are retrieved chunks relevant?
- **Context Recall:** Did we retrieve all necessary context?

### User-Focused Metrics
- **Response Time:** How fast is the answer?
- **Source Attribution:** Are sources properly cited?
- **User Satisfaction:** Thumbs up/down feedback

---

## Portfolio Value

### Why This Project Stands Out:

1. **Domain Expertise**
   - Healthcare/insurance domain knowledge
   - Highly valuable in job market
   - Shows ability to handle regulated industries

2. **Real-World Impact**
   - Solves actual user pain points
   - Could be used by insurance agents/customers
   - Demonstrates business value thinking

3. **Technical Complexity**
   - Multi-document type RAG
   - Metadata filtering and routing
   - Hybrid search implementation
   - Production-ready architecture

4. **Production Readiness**
   - Cost optimization strategies
   - Error handling
   - Multi-tier fallback
   - Proper evaluation framework

5. **Differentiation**
   - Most ML portfolios don't touch insurance
   - Combines document processing, search, and LLMs
   - Shows end-to-end system thinking

---

## Future Enhancements (Post-MVP)

### Feature Ideas:
- [ ] Drug interaction checker
- [ ] Cost comparison across plans
- [ ] Provider network integration (doctors who can prescribe)
- [ ] Coverage gap analysis
- [ ] Medication alternatives recommender
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Mobile app
- [ ] Email/SMS alerts for formulary changes
- [ ] Integration with pharmacy systems

### Technical Improvements:
- [ ] Fine-tune embeddings on insurance domain
- [ ] Build custom reranker
- [ ] Add graph database for drug relationships
- [ ] Implement active learning from user feedback
- [ ] A/B testing framework
- [ ] Real-time formulary updates

---

## Getting Started Checklist

### Immediate Next Steps:
- [ ] Choose target state(s) for MVP
- [ ] Download sample formulary PDFs
- [ ] Download sample FAQ PDFs
- [ ] Set up Python environment
- [ ] Install core libraries (LlamaIndex/LangChain, FAISS, sentence-transformers)
- [ ] Create project repository
- [ ] Set up basic project structure

### Project Structure:
```
insurance-rag-system/
├── data/
│   ├── raw/              # Original PDFs
│   ├── processed/        # Extracted text
│   └── vectors/          # Vector embeddings
├── src/
│   ├── ingestion/        # PDF processing
│   ├── retrieval/        # Search logic
│   ├── generation/       # LLM integration
│   └── evaluation/       # Testing & metrics
├── notebooks/            # Exploration
├── app/                  # Frontend (Gradio/Streamlit)
├── tests/                # Unit tests
├── docs/                 # Documentation
├── requirements.txt
└── README.md
```

---

## Resources & References

### Similar Projects (for inspiration):
- PowerGrid AI Tutor (your existing project)
- arXiv Paper Curator (your existing project)
- LlamaIndex documentation
- LangChain tutorials

### Useful Libraries:
- **Document Processing:** PyPDF2, pdfplumber, camelot-py, LlamaParse
- **RAG Frameworks:** LlamaIndex, LangChain, Haystack
- **Vector DBs:** FAISS, Pinecone, Weaviate, ChromaDB
- **Search:** rank-bm25, elasticsearch
- **Evaluation:** ragas, deepeval
- **UI:** Gradio, Streamlit, Chainlit

### Learning Resources:
- LlamaIndex docs: https://docs.llamaindex.ai/
- LangChain docs: https://python.langchain.com/
- RAGAS evaluation: https://docs.ragas.io/

---

## Success Criteria

### MVP Success:
✅ Can answer 80%+ of common coverage questions correctly
✅ Response time < 5 seconds
✅ Properly cites sources
✅ Deployed and accessible via URL
✅ Clean, professional UI

### Portfolio Success:
✅ Comprehensive documentation with screenshots
✅ Live demo accessible to recruiters
✅ GitHub repository with clean code
✅ Blog post or case study written
✅ Added to portfolio website with detailed description

---

## Timeline Estimate

**MVP (Phase 1):** 2-3 weeks part-time
**Multi-State (Phase 2):** 1-2 weeks
**Advanced Features (Phase 3):** 2-3 weeks
**Polish & Document (Phase 4):** 1 week

**Total:** 6-9 weeks part-time (~2-3 months)

---

## Contact & Questions

For questions or discussion about this project:
- Review this document
- Test existing RAG projects for inspiration
- Research insurance domain specifics
- Prototype data ingestion first

---

**Document Version:** 1.0
**Created:** 2025-12-17
**Last Updated:** 2025-12-17
**Status:** Planning Phase
