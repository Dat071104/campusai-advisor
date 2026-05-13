# CampusAI Advisor

CampusAI Advisor is a web-first AI academic advising and RAG chatbot MVP for university students. The current foundation provides a runnable Streamlit shell, environment-based settings, PDF ingestion, text chunking, local FastEmbed embeddings, and ChromaDB persistence for later retrieval and Groq answer generation.

## Current Scope

Implemented now:

- Python package under `src/campusai`
- Minimal Streamlit app placeholder
- Environment settings loader with safe placeholders
- Project dependency declaration in `pyproject.toml`
- Basic smoke test for settings loading
- Local data folders for future documents and vector store files
- PDF loading from `data/raw`
- Page-level text extraction with source metadata
- Text chunking
- Local embeddings with FastEmbed
- Persistent local vector storage with ChromaDB
- CLI indexing command

Not implemented yet:

- Real Groq API calls
- Chat/RAG answer generation
- Retrieval UI and citation cards
- Authentication, databases, queues, or microservices

## Setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Create a local `.env` only when you are ready to run later Groq-backed phases:

```bash
copy .env.example .env
```

Then paste real Groq keys into `.env` manually. Never commit `.env`.

## Run The App

```bash
streamlit run src/campusai/app.py
```

The current app is a Phase 1 placeholder. It shows student-profile fields, document upload controls, chat input, and explicit "not yet implemented" states without calling Groq or processing documents.

## Index Local PDFs

Put academic PDFs in `data/raw`, then run:

```bash
python -m campusai.index_documents
```

or, after editable install:

```bash
campusai-index
```

The first real indexing run may download the configured FastEmbed model. Indexed chunks are stored in `data/vector_db`, which is intentionally ignored by Git.

Default indexing settings:

```text
RAW_DATA_DIR=data/raw
VECTOR_STORE_PATH=data/vector_db
CHROMA_COLLECTION=campusai_documents
EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DIM=384
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

## Verify

```bash
pytest
python -c "from campusai.config import get_settings; print(get_settings().groq_model)"
```

## Project Layout

```text
src/campusai/
  app.py
  config.py
  index_documents.py
  ingestion/
  services/
  rag/
  ui/
tests/
data/raw/
data/vector_db/
sample_docs/
```

## Next Phase

Phase 2 audit should verify the ingestion/indexing pipeline. After that, the next implementation step is retrieval, citation formatting, and Groq-backed answer generation.
