# Health Enrollment Assistant - Project Discussions

**Document Purpose:** Capture all discussions and decisions for the Health Enrollment Assistant RAG/Agent system to avoid repeating questions.

**Date Started:** 2025-12-17

---

## Project Origin & Vision

### Initial Context

An insurance agent shared information about Oscar Health Insurance tools:

1. **Oscar Doctor Lookup (Atrium Network):**
   https://www.hioscar.com/search/?networkId=043&year=2026

2. **Oscar Formulary Lookup:**
   https://www.hioscar.com/search-documents/drug-formularies/

### The Vision

Build an intelligent insurance assistant that helps people during enrollment by answering questions about:

1. **Drug Formulary Coverage**
   - Which medications are covered
   - Cost tier levels (Tier 1, 2, 3, 4)
   - Prior authorization requirements
   - Quantity limits and restrictions

2. **State-Specific FAQs**
   - Educational content (PDFs per state) answering:
     - "What are generic drugs?"
     - "What are specialty drugs?"
     - "Are there any restrictions on my coverage?"
     - "What if my drug is not on the Formulary?"
     - "Can the Formulary change?"

3. **Provider Search** (Future Phase)
   - Finding in-network doctors/hospitals
   - Provider specialties and locations

### Key User Questions the System Should Answer

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
- "What is the appeals process in California?"

**Hybrid Questions:**
- "My drug isn't on the formulary - what are my options in Florida?"
- "Show me cheaper alternatives to Advair that are covered"
- "What tier 1 diabetes medications are available?"

---

## Core Architecture Decision: Simple RAG vs Agentic RAG

### Discussion Summary

We explored two architectural approaches:

#### Approach 1: Simple RAG (Traditional)
```
User Query → Embedding → Vector Search → Retrieve Docs → LLM Response
```

**Characteristics:**
- Linear pipeline
- One retrieval step
- No decision making
- Simple to implement

**Good for:** Straightforward questions like "Is metformin covered?"

**Struggles with:** Complex queries like "Compare coverage across states" or "Find cheapest diabetes medication"

#### Approach 2: Agentic RAG (Intelligent)
```
User Query → Orchestrator Agent
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
Query          State      Document
Understanding  Router     Classifier
Agent          Agent      Agent
    ↓           ↓           ↓
         Retrieval Agent
                ↓
         Response Agent
```

**Characteristics:**
- Agents make decisions
- Multiple retrieval rounds if needed
- Can handle complex queries
- Self-correcting

**Potential Sub-Agents:**
1. **Query Understanding Agent** - Classifies intent, extracts entities
2. **State Router Agent** - Identifies which state(s) for the query
3. **Document Type Classifier Agent** - Routes to formulary, FAQ, or both
4. **Provider/Network Agent** - Routes to correct network (future)
5. **Retrieval Agent** - Performs document search, multiple rounds
6. **Validation Agent** - Checks answer quality, requests more context
7. **Response Generation Agent** - Synthesizes final answer with sources

**Additional Agent Ideas:**
- Query decomposition agent (breaks complex questions)
- Comparison agent (handles "cheaper alternatives")
- Cost calculator agent (estimates costs)
- Alternative finder agent (suggests similar covered drugs)
- Explanation agent (explains insurance terms simply)

### DECISION: Option A - Progressive Evolution

**Chosen Approach:** Start simple, evolve to agentic

```
Phase 1: Simple RAG → Phase 2: Smart Routing → Phase 3: Light Agents → Phase 4: Full Agentic
```

**Rationale:**
1. Learn fundamentals first
2. Understand the data and patterns
3. See what queries actually need agent intelligence
4. Avoid over-engineering
5. Better for learning - understand each layer

**Implementation Plan:**

**Phase 1: Simple RAG (Week 1-2)**
- Get basic retrieval working
- Understand the data
- Prove the concept
- Learn the patterns

**Phase 2: Add Intelligence (Week 3-4)**
- Add query classification (simple if/else first)
- Add state routing
- Add document type selection
- Still mostly deterministic

**Phase 3: Full Agentic (Week 5-6)**
- Orchestrator agent making decisions
- Multiple sub-agents
- Self-correction
- Complex query handling

---

## Project Guidelines & Principles

### Development Approach
1. **Go slow** - Step by step, no rushing
2. **No emojis in code** - Keep code professional
3. **Explain everything** - Help understand code as we build
4. **Clear reasoning** - Explain why we choose specific technologies

### Documentation Strategy

As we progress, we will maintain:

1. **Architecture** - System design, component diagrams, data flow
2. **FAQs** - Common questions and answers as they come up
3. **Suggested Readings** - Resources, links, papers we reference
4. **Additional Notes** - Learnings, gotchas, future ideas
5. **Decision Log** - Why we chose X over Y (with reasoning)
6. **Setup Guide** - Step-by-step environment setup
7. **Code Explanations** - What each module does and why

All documentation will be created in the project folder structure under `/docs/` as we progress.

---

## Technology Stack Decisions

### LLM Ecosystem Options Discussed

**Option A: LlamaIndex**
- Pro: Built specifically for RAG applications
- Pro: Simpler API, less boilerplate
- Pro: Great for beginners, easier to understand
- Pro: Excellent documentation
- Con: Less flexible for complex customization

**Option B: LangChain**
- Pro: More mature, larger ecosystem
- Pro: Very flexible, lots of integrations
- Pro: Good for complex workflows
- Con: More verbose, steeper learning curve
- Con: Can be overwhelming

**Option C: Build from scratch**
- Pro: Understand every component
- Pro: Full control
- Pro: Best for learning fundamentals
- Con: More code to maintain

**Recommended:** LlamaIndex (pending final decision when we start implementation)
- RAG-focused design matches use case
- Cleaner code = easier to understand
- Aligns with previous projects

### LLM Provider Options Discussed

**Google Gemini 2.0 Flash**
- Cost: FREE tier (15 RPM, 1M TPM, 1500 RPD)
- Speed: Very fast (~1-2 sec)
- Quality: Good for most tasks
- Best cost/performance ratio

**OpenAI GPT-4o-mini**
- Cost: $0.15/1M input, $0.60/1M output
- Speed: Fast
- Quality: Excellent
- Most reliable

**Anthropic Claude 3.5 Haiku**
- Cost: $0.80/1M input, $4.00/1M output
- Speed: Very fast
- Quality: Excellent reasoning

**Recommended:** Start with Gemini, add fallbacks later
- Free tier for development
- Add OpenAI/Claude as fallbacks in Phase 2
- Matches multi-tier fallback pattern from previous projects

### Vector Database Options Discussed

**FAISS (Local)**
- Cost: FREE
- Speed: Very fast
- Setup: Simple pip install
- No external dependencies

**Pinecone (Cloud)**
- Cost: Free tier 1 index, then $70/month
- Speed: Fast
- Setup: Requires API key
- Production-ready, managed service

**Recommended:** Start with FAISS
- No API keys needed
- Free forever
- Fast enough for single-state demo
- Easy to switch to Pinecone later

---

## Deployment Strategy

### Size Constraints

**Question:** Will this be too big for HuggingFace Spaces?

**Answer:**
- **MVP (1-2 states):** Yes, HuggingFace will work
- **Full system (all states):** No, too big

**Why:**
- HuggingFace limit: ~50GB
- Each state's PDFs + vectors: ~500MB-1GB
- Full system: 25+ GB (all 50 states)

### Deployment Phases

**Phase 1 (MVP):** HuggingFace Spaces (Free)
- Good for demos and testing
- 1-2 states only

**Phase 2 (Multi-state):** Railway or Render ($10-20/month)
- More resources
- Can handle multiple states

**Phase 3 (Production):** AWS/Azure (Scalable)
- Full production deployment
- All states, high availability

---

## Scope & Extensibility

### Insurance Providers

**Initial:** Oscar Health Insurance
- Formulary documents
- State-specific FAQs
- Provider network (Atrium)

**Future Extensibility:**
- Ambetter
- Aetna
- Blue Cross Blue Shield
- United Healthcare
- Cigna
- Other providers

**Why generic name chosen:** System should not be locked to one provider

### Functionality Scope

The system will handle THREE main areas:

1. **Drug Formulary Queries**
   - Coverage lookup
   - Tier information
   - Prior authorization
   - Restrictions

2. **Educational Content (State-specific FAQs)**
   - Generic vs specialty drugs
   - Coverage policies
   - Appeals process
   - State-specific regulations

3. **Provider Search** (Future Phase)
   - In-network doctors
   - Hospital search
   - Specialty matching

---

## Project Folder Structure

```
health-enrollment-assistant-dev/
│
├── docs/                          # All documentation
│   ├── architecture/              # System design, diagrams, component docs
│   ├── faqs/                      # Questions and answers as we go
│   ├── readings/                  # Links, papers, resources we reference
│   ├── notes/                     # Our discussion notes, learnings
│   └── decisions/                 # Why we chose X over Y
│
├── data/                          # Data files
│   ├── raw/                       # Original PDFs we download
│   └── processed/                 # Cleaned/extracted data
│
├── src/                           # Source code
│
├── notebooks/                     # Jupyter notebooks for exploration
│
├── tests/                         # Test files
│
└── README.md                      # Main project overview
```

---

## Key Decisions Made

### 1. Project Name
**Decision:** `health-enrollment-assistant-dev`

**Reasoning:**
- "health" - Specific to health insurance (not auto/home)
- "enrollment" - Captures use case (enrollment decision support)
- "assistant" - Indicates AI helper
- Generic enough to support multiple providers
- Clear about when/why it's used

### 2. Architecture Approach
**Decision:** Start Simple RAG, evolve to Agentic (Option A)

**Reasoning:**
- Learn fundamentals first
- Iterate based on real needs
- Avoid over-engineering
- Better for understanding each layer

### 3. Location
**Decision:** Create project in home directory (`~/`), not under `energy-consumption-dev`

**Reasoning:**
- Separate project from other work
- Clean organization
- Easier to find and manage

---

## Next Steps (When Ready to Start)

1. Run the script to create folder structure in home directory
2. Copy this discussion document to the new project
3. Copy the comprehensive project plan (insurance-rag-system.md)
4. Begin Phase 1: Simple RAG implementation
5. Start with decisions about:
   - LLM ecosystem (LlamaIndex vs LangChain)
   - LLM provider (Gemini vs OpenAI)
   - Vector DB (FAISS vs Pinecone)
   - Target state for MVP
   - PDF access/collection strategy

---

## Questions to Answer Before Implementation

These will be addressed step-by-step as we begin:

1. Confirm LLM ecosystem choice (LlamaIndex recommended)
2. Confirm LLM provider (Gemini recommended)
3. Confirm vector DB (FAISS recommended)
4. Choose target state for MVP
5. Determine PDF access (downloaded or need scraper)
6. Set up development environment
7. Create project repository

---

## Reference Links

**Oscar Health Resources:**
- Doctor Lookup: https://www.hioscar.com/search/?networkId=043&year=2026
- Drug Formularies: https://www.hioscar.com/search-documents/drug-formularies/

**Related Project Documentation:**
- Comprehensive Project Plan: `/project-ideas/insurance-rag-system.md`
- This Discussion Document: `/project-ideas/health-enrollment-discussions.md`

---

**Document Status:** Complete - Ready to move to project structure
**Next Action:** Run create-project-home.sh, then copy this document to new project
