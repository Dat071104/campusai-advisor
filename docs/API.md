# CampusAI API

Minimal FastAPI backend for the CampusAI Advisor MVP.

## Run locally

```bash
uvicorn campusai.api.app:app --reload
```

## Endpoints

### `GET /health`
Returns basic service health.

### `GET /status`
Returns index and vector store status without exposing secrets.

### `GET /debug/retrieval?q=...`
Returns top retrieved chunks without calling Groq.

### `POST /ask`
Returns a RAG answer with citations and sources.

Example request:

```json
{
  "question": "What is TDTU Software Engineering?",
  "language": "English"
}
```

Example response:

```json
{
  "answer": "...",
  "citations": [],
  "sources": []
}
```
