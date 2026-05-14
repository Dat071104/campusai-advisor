# CampusAI Advisor

## 1. Problem

University students juggle **course planning**, **prerequisites**, and **policy-heavy documents**, but generic chatbots can **hallucinate** requirements or pretend unofficial notes are official. Recruiters also need a **credible demo**: grounded answers, visible sources, and honest limits.

## 2. Solution

**CampusAI Advisor** is a portfolio MVP: **local document ingestion** (PDF, Markdown, plain text), **FastEmbed** embeddings, **ChromaDB** retrieval, **authority-labeled citations**, and **Groq**-backed answers **only after** you submit a question in Streamlit (no LLM calls on startup). **Project-facing defaults are English**; users may still ask in other languages and can request a non-English answer explicitly.

## 3. Features

- Streamlit UI with **student profile** context, **dataset/index status**, and **citation cards** (source, page, authority; chunk id in a collapsed technical section).
- **CLI indexing** of **PDF**, **Markdown (`.md`)**, and **plain text (`.txt`)** files discovered recursively under `data/raw/` into a persistent local vector store (gitignored).
- **Public dataset adapter** (MIT FireRoad, Berkeley CS guide references, local heuristic rules) via `python -m campusai.fetch_public_dataset` and `data/processed/source_manifest.json`.
- **Groq** OpenAI-compatible client with **timeouts**, **retries**, **max tokens**, and **minimum spacing** between live requests.
- Clear **empty states**: no index, no API key, no retrieval hits, rate limits, and timeouts.

## 4. Tech stack

| Layer | Choice |
|--------|--------|
| Language | Python 3.10+ |
| UI | Streamlit |
| Embeddings | FastEmbed (local) |
| Vector DB | ChromaDB (local path) |
| PDF | PyMuPDF |
| LLM | Groq (OpenAI-compatible client) |
| Config | `python-dotenv` |
| Tests | pytest |

## 5. Architecture

```text
data/raw (PDFs + Markdown + .txt + staged public files)
    -> chunking + page metadata
    -> FastEmbed embeddings
    -> ChromaDB (data/vector_db)
    -> Retriever (top_k)
    -> Citations + authority labels (manifest-aware)
    -> Prompt builder
    -> Groq chat (manual submit only)
    -> Streamlit answer + citation UI
```

Optional manifest path: `data/processed/source_manifest.json` (public sources + heuristics metadata).

## 6. Dataset sources

- **MIT FireRoad** — public structured course/requirement data (see adapter under `src/campusai/datasets/`).
- **UC Berkeley CS Guide** — public HTML/PDF references (not your institution’s official catalog).
- **Local heuristic advisor rules** — `data/raw/documents/local/campusai_local_advisor_rules.md`; **study guidance only**, not official policy.

Run:

```bash
python -m campusai.fetch_public_dataset --timeout 20
```

## 7. Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
```

Copy environment template (local only):

```bash
copy .env.example .env
```

Edit `.env` and set `GROQ_API_KEY` when you are ready for live LLM answers. **Never commit `.env`.**

## 8. Environment variables

See **`.env.example`** for placeholders. Important keys:

| Variable | Role |
|----------|------|
| `GROQ_API_KEY` | Enables live Groq completions |
| `GROQ_MODEL`, `GROQ_BASE_URL` | Model and endpoint |
| `RAW_DATA_DIR` | Input directory for PDF, Markdown, and `.txt` indexing |
| `VECTOR_STORE_PATH`, `CHROMA_COLLECTION` | Chroma persistence |
| `EMBEDDING_MODEL`, `EMBEDDING_DIM` | FastEmbed model |
| `GROQ_TIMEOUT_SECONDS`, `GROQ_MIN_SECONDS_BETWEEN_REQUESTS`, `GROQ_MAX_RETRIES`, `GROQ_MAX_TOKENS` | Safety defaults |
| `RAG_TOP_K` | Retrieval breadth |

## 9. Run commands

```bash
python -m campusai.fetch_public_dataset
python -m campusai.index_documents
# If an older index only contains PDF chunks, reset the Chroma collection then reindex:
python -m campusai.index_documents --reset
# Verify retrieval (embeddings + Chroma only; no Groq, no API key required):
python -m campusai.debug_retrieval "What should I learn before Machine Learning?"
streamlit run src/campusai/app.py
```

Verify (no Groq calls):

```bash
python -m pytest
python -m compileall src tests
python -m campusai.debug_retrieval "What should I learn before Machine Learning?"
python -c "import campusai.app; print('app import ok')"
```

## 10. Demo questions

Try these after indexing and (optionally) configuring Groq:

```text
What should I learn before Machine Learning?
What are Berkeley CS lower division requirements?
Are local advisor rules official university policy?
What does MIT FireRoad data say about Computer Science requirements?
```

Scripted flows: **`DEMO_SCRIPT.md`**.

## 11. Safety and limitations

- **Heuristic local rules** are labeled in citations; they are **not** official university policy.
- **No invented policies**: if retrieval is empty, the chain returns a **no-evidence** style message.
- **Single Groq key** by design — no backup key rotation (rate-limit discipline).
- **Streamlit Community Cloud**: vector persistence may be **ephemeral**; first embedding model load can be **slow**; public HTTP sources may be **down** — see **`docs/DEPLOYMENT.md`**.
- Cloud packaging uses the root `requirements.txt` so Streamlit Community Cloud installs with pip/uv instead of treating `pyproject.toml` as Poetry metadata.

## 12. Future improvements (V2+)

- Upload-to-index inside Streamlit, job status, and user workspaces.
- FastAPI + Next.js UI, PostgreSQL + pgvector, background indexing.
- Evaluation harness for citation correctness and retrieval hit rate.

## 13. CV bullets

- Built **CampusAI Advisor**, a **RAG** academic advising MVP in Python with **local embeddings**, **ChromaDB** retrieval, **authority-aware citations**, **Groq** generation behind manual submit, and a **Streamlit** demo suitable for portfolio and interview walkthroughs.
- Implemented **public dataset staging** (FireRoad / Berkeley references), **CLI indexing**, and **operational safeguards** (timeouts, spacing, retries) without committing secrets.

---

## Manual live smoke test

**Run only after** a local `.env` is configured with a real `GROQ_API_KEY` (never paste keys into chat, README, screenshots, or logs).

1. Start the app: `streamlit run src/campusai/app.py`.
2. Confirm **Dataset & index status** shows a **ready** vector index (index documents first if needed).
3. Ask **exactly one** safe test question first:  
   `What should I learn before Machine Learning?`
4. **Do not spam** the API; wait a few seconds before a second question.
5. If you hit **rate limit** or **timeout**, wait several minutes and retry.
6. Confirm citations show **source**, **page** (when available), and **authority** labels.

---

## Documentation map

| File | Purpose |
|------|---------|
| `DEMO_SCRIPT.md` | 2- and 5-minute demo, interview lines, limitations |
| `docs/DEPLOYMENT.md` | Streamlit Community Cloud, secrets, indexing caveats |
| `docs/PORTFOLIO_WRITEUP.md` | Short portfolio blurb |
| `IMPLEMENTATION_LOG.md` | Session history and decisions |

## Project layout

```text
src/campusai/
  app.py                 # Streamlit entrypoint
  config.py
  index_documents.py
  fetch_public_dataset.py
  datasets/
  ingestion/
  rag/
  services/
tests/
data/raw/
data/processed/
data/vector_db/          # gitignored local Chroma files
.streamlit/config.toml   # non-secret theme defaults
```

## Current scope note

In-app **PDF upload is staged**; indexing uses **`python -m campusai.index_documents`** reading from `data/raw`.
