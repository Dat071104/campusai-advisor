# CampusAI Advisor

CampusAI Advisor is a web-first AI academic advising and RAG chatbot MVP for university students. The Phase 1 foundation provides a runnable Streamlit shell, environment-based settings, and a clean Python package layout for the later document ingestion, retrieval, citation, and Groq answer-generation phases.

## Phase 1 Scope

Implemented now:

- Python package under `src/campusai`
- Minimal Streamlit app placeholder
- Environment settings loader with safe placeholders
- Project dependency declaration in `pyproject.toml`
- Basic smoke test for settings loading
- Local data folders for future documents and vector store files

Not implemented in Phase 1:

- Real Groq API calls
- Document ingestion
- Embeddings
- Vector search
- Full RAG answers
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
  services/
  rag/
  ui/
tests/
data/raw/
data/vector_db/
sample_docs/
```

## Next Phase

Phase 1 audit should verify the foundation. After that, the next implementation step is document loading and chunking with focused tests.
