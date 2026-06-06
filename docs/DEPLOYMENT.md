# Deployment — Streamlit Community Cloud (CampusAI Advisor)

The default deployment is a **single Streamlit app**. Optional local FastAPI backend mode exists for V2/local multi-service work, but Streamlit Community Cloud should keep using the root `streamlit_app.py` entrypoint without Docker.

## 1. GitHub repository requirement

- Push the project to a **GitHub** repository that Streamlit Community Cloud can access.
- **Do not** commit: `.env`, `.env.local`, private uploads, `data/vector_db/` artifacts, API keys, or large generated caches.
- Keep `.env.example` with **placeholders only**.

## 2. Streamlit Community Cloud

1. Sign in at [Streamlit Community Cloud](https://streamlit.io/cloud).
2. **New app** → select your GitHub repo, branch, and entrypoint file (see below).
3. Python version: use **3.10+** (see Recommended Python version).

## 3. App entrypoint

Main file:

```text
streamlit_app.py
```

In Community Cloud, set the main file path to this file relative to the repository root.

## 4. Dependencies

Cloud installs should use the root `requirements.txt` so Streamlit Community Cloud uses pip/uv instead of treating `pyproject.toml` as Poetry metadata.

Local editable install (development):

```bash
python -m pip install -e ".[dev]"
```

Runtime packages needed by the app are listed in both `pyproject.toml` and `requirements.txt` (`streamlit`, `chromadb`, `fastembed`, `pymupdf`, `openai`, `python-dotenv`, etc.).

## 5. Secrets on Community Cloud (not `.env` in git)

- **Never** commit `.env`.
- In Streamlit Community Cloud: **App settings → Secrets** (Advanced), define secrets as TOML, for example:

```toml
GROQ_API_KEY = "your_key_here"
```

- Map variable names to match `src/campusai/config.py` / `.env.example` (`GROQ_API_KEY`, `GROQ_MODEL`, etc.).

**Do not** add `.streamlit/secrets.toml` to the repository for real keys.

## 6. Local `.env` vs deployed secrets

| Environment | Configuration |
|-------------|----------------|
| **Local dev** | `.env` file (gitignored), loaded by `python-dotenv` |
| **Streamlit Cloud** | **Secrets** UI / environment provided by the platform |

Same variable names; different storage. Never print secrets in logs or UI.

For Streamlit Community Cloud, leave `CAMPUSAI_API_BASE_URL` unset unless you have deployed a separate backend. The normal Cloud path runs direct in-process RAG from Streamlit.

## 6.1 Docker Compose secrets

Docker Compose is for local multi-service testing and does not load the project `.env` file by default. The compose file maps `GROQ_API_KEY` only from the Docker-specific `CAMPUSAI_DOCKER_GROQ_API_KEY` variable, which should stay empty for normal no-key validation.

If you intentionally test live Groq in Docker, set `CAMPUSAI_DOCKER_GROQ_API_KEY` only in your local shell or an ignored `docker.env` file. Do not commit `docker.env`, do not put real keys in `docker-compose.yml`, and do not paste `docker compose config` output while any real secret-bearing environment variable is set.

## 7. Recommended Python version

- **Python 3.10 or newer** (see `pyproject.toml`: `requires-python = ">=3.10"`).

## 8. Regenerate / fetch public dataset

From a checkout with network access:

```bash
python -m campusai.fetch_public_dataset --timeout 20
```

Use `--skip-network` for offline-only local manifest refresh. Output includes generated, gitignored public-source artifacts under `data/processed/source_manifest.json`, `data/raw/api/mit_fireroad/`, and `data/raw/documents/berkeley/`.

## 9. Index documents before or after deploy

Indexing is **CLI-driven** in the MVP:

```bash
python -m campusai.index_documents
```

Place PDFs (and processed text sources) under `data/raw` as documented in the README.

**Deployment note:** On Community Cloud, the filesystem may be **ephemeral**. Rebuilding the vector index on each session or using a persisted drive (if available) is a product decision for V2. For demos, pre-index locally and accept limits, or run indexing as a documented manual step.

## 10. Known deployment limitations

- **Vector DB persistence** on Community Cloud may be **limited or ephemeral**; Chroma data under `data/vector_db` might not survive restarts unless you use a durable strategy outside this MVP.
- **First FastEmbed model load** can be **slow** and bandwidth-heavy.
- **Public fetch endpoints** (MIT / Berkeley) may be **temporarily unavailable**; the fetch CLI handles failures per source but does not guarantee fresh data.

---

## Related docs

- **README.md** — Local setup, env vars, demo questions, smoke test.
- **DEMO_SCRIPT.md** — Interview and recording flow.
