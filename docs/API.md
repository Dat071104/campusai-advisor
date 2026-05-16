# CampusAI FastAPI Backend

The FastAPI backend is optional local/V2 infrastructure. Normal Streamlit local development and Streamlit Community Cloud still work without it.

## Run Locally

```bash
python -m uvicorn campusai.api.app:app --host 0.0.0.0 --port 8000
```

Then open:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Lightweight process health check |
| `GET` | `/status` | Runtime status without exposing secrets |
| `POST` | `/status/build-index?reset=true` | Rebuild local Chroma index from mounted/local `data/raw` |
| `POST` | `/debug/retrieval` | Return retrieved chunks without calling Groq |
| `POST` | `/ask` | Run retrieval and answer generation |

## Streamlit Backend Mode

Set this only when a backend is running:

```env
CAMPUSAI_API_BASE_URL=http://localhost:8000
```

Leave it unset for the normal direct Streamlit workflow and Streamlit Community Cloud.

## Secrets

Pass `GROQ_API_KEY` through local `.env`, Docker environment, or deployment secrets. Do not commit `.env`, `.streamlit/secrets.toml`, real keys, uploaded private documents, or `data/vector_db`.
