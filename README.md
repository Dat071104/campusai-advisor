# CampusAI Advisor

CampusAI Advisor is a web-first AI academic advising and RAG chatbot MVP for university students. The current MVP provides a runnable Streamlit app, environment-based settings, PDF ingestion, text chunking, local FastEmbed embeddings, ChromaDB persistence, retrieval, citation formatting, and Groq-backed answer generation when a local `GROQ_API_KEY` is configured.

## Current Scope

Implemented now:

- Python package under `src/campusai`
- Streamlit question-answering UI with student profile sidebar
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
- Local vector retrieval over indexed chunks
- Citation formatting with source authority labels
- Groq OpenAI-compatible chat client with missing-key fallback and free-tier rate safeguards
- RAG answer chain that answers in Vietnamese by default and refuses unsupported policy claims

Not implemented yet:

- Upload-to-index flow inside Streamlit
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

Then paste your real Groq key into `.env` manually. Never commit `.env`.

## Run The App

```bash
streamlit run src/campusai/app.py
```

The app shows student-profile fields, dataset/index status, a question form, answer output, and citation cards. It does not call Groq on startup; it only attempts a live Groq call after you manually submit a question and relevant chunks are retrieved.

Free-tier safety defaults:

```text
GROQ_TIMEOUT_SECONDS=30
GROQ_MIN_SECONDS_BETWEEN_REQUESTS=3
GROQ_MAX_RETRIES=2
GROQ_MAX_TOKENS=900
RAG_TOP_K=5
```

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

## Manual RAG Test Questions

After indexing documents and configuring `.env`, run the app and try:

```text
Trước khi học Machine Learning thì nên học gì?
Berkeley CS lower division requirements gồm những gì?
Local advisor rules có phải chính sách chính thức không?
MIT FireRoad data nói gì về Computer Science requirements?
```

Expected behavior: answers are in Vietnamese by default, citations are visible, local heuristic rules are labeled as not official policy, and missing evidence is stated clearly.

## Verify

```bash
python -m pytest
python -m compileall src tests
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

## Public Dataset Adapter

Phase 2.5 adds a public, verifiable dataset adapter layer that fetches or prepares:

- MIT FireRoad public course and requirement data
- UC Berkeley CS Guide HTML/PDF sources
- Local heuristic advisor rules for study-path context

Run the fetch command when you want to stage the public dataset files:

```bash
python -m campusai.fetch_public_dataset
```

The command writes a source manifest to `data/processed/source_manifest.json` and stores raw MIT FireRoad JSON under `data/raw/api/mit_fireroad/`. If a live fetch fails, the command preserves the failure gracefully and may leave manual download steps for the Berkeley source.

## Next Phase

Phase 3 audit should verify retrieval quality, citation correctness, Groq missing-key behavior, and Streamlit manual question flow before demo polish.
