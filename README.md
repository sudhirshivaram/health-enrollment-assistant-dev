# Health Enrollment Assistant

An intelligent RAG-based system to help people understand health insurance coverage during enrollment.

## Overview

This system answers questions about:
- Drug formulary coverage (which medications are covered)
- Cost tier levels and copays
- Prior authorization requirements
- State-specific insurance FAQs
- Coverage policies and restrictions

**Current Status:** Phase 1 - Simple RAG implementation

## Architecture

The system evolves through 4 phases:
1. **Phase 1:** Simple RAG (current)
2. **Phase 2:** Smart Routing
3. **Phase 3:** Light Agents
4. **Phase 4:** Full Agentic System

See [docs/architecture/](docs/architecture/) for detailed diagrams.

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd health-enrollment-assistant-dev
```

### 2. Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

On Windows (PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Create virtual environment and install dependencies

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

### 5. Add your PDF documents

Place your insurance PDF files in:
- `data/raw/formularies/` - Drug formulary PDFs
- `data/raw/faqs/` - FAQ PDFs

### 6. Run data ingestion (coming soon)

```bash
python src/ingestion/run_pipeline.py
```

### 7. Start the application (coming soon)

```bash
python src/app/gradio_app.py
```

## Project Structure

```
health-enrollment-assistant-dev/
├── config/
│   └── config.yaml              # Configuration settings
├── data/
│   ├── raw/                     # Original PDF files
│   └── processed/               # Generated embeddings and indexes
├── docs/
│   ├── architecture/            # System architecture diagrams
│   └── notes/                   # Project discussions and plans
├── src/
│   ├── ingestion/               # PDF processing and embedding
│   ├── retrieval/               # FAISS search and retrieval
│   ├── generation/              # LLM integration
│   └── app/                     # Gradio user interface
├── tests/                       # Unit tests
├── notebooks/                   # Jupyter notebooks for exploration
├── .env                         # Environment variables (not committed)
├── .env.example                 # Template for environment variables
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Technology Stack

- **Framework:** LlamaIndex (planned)
- **LLM:** Google Gemini 2.0 Flash
- **Vector Database:** FAISS
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **PDF Processing:** PyPDF2 / pdfplumber
- **UI:** Gradio
- **Language:** Python 3.8+

## Configuration

Edit `config/config.yaml` to customize:
- Chunk size and overlap
- Number of retrieved documents (top_k)
- LLM temperature and max tokens
- UI settings

## Development

### Install dependencies

```bash
uv pip install -r requirements.txt
```

### Run tests (coming soon)

```bash
pytest tests/
```

### Launch Jupyter for exploration

```bash
jupyter notebook
```

## Documentation

- [Overall Architecture](docs/architecture/overall-system-architecture.md)
- [Phase 1 Architecture](docs/architecture/phase1-simple-rag-architecture.md)
- [4 Phases Evolution](docs/notes/overview-4phases-evolution.md)
- [Project Discussions](docs/notes/health-enrollment-discussions.md)
- [Full Project Plan](docs/notes/insurance-rag-system.md)

## License

[Your License Here]

## Contributing

[Contributing guidelines if applicable]
