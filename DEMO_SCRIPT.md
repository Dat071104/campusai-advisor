# CampusAI Advisor — Demo Script

Use this script for portfolio walkthroughs, screen recordings, and interviews. The app is **Streamlit**: `streamlit run src/campusai/app.py`.

## Before you demo

1. **Local `.env`**: Copy `.env.example` to `.env` and set `GROQ_API_KEY` only on your machine. Never commit `.env`, paste keys into chat, or show keys in screenshots.
2. **Index**: Stage PDFs and local advisor Markdown under `data/raw` (for example `data/raw/documents/local/campusai_local_advisor_rules.md`), run `python -m campusai.index_documents`. If you previously indexed **PDFs only** and need Markdown in the same Chroma collection, run `python -m campusai.index_documents --reset` once, then index again. Optional: `python -m campusai.fetch_public_dataset` to generate local public dataset artifacts and `data/processed/source_manifest.json`, then index again.
3. **Retrieval check (no Groq)**: Run `python -m campusai.debug_retrieval "What should I learn before Machine Learning?"` and confirm `campusai_local_advisor_rules.md` appears near the top.
4. **Rate limits**: Groq free tier is conservative. Wait a few seconds between live questions; if rate limited, wait and retry later.

---

## 2-minute demo flow

1. **Open the app** — Point out the title, one-line product explanation, and **Dataset & index status** (manifest + vector index + Groq key indicator).
2. **Sidebar** — Show **Student Profile** (major, year, goals) and **System Status** (embeddings model, paths). Mention that **local advisor rules are heuristic**, not official policy.
3. **Ask one question** — Use: *"What should I learn before Machine Learning?"* Wait for retrieval + answer.
4. **Citations** — Expand one citation: **source**, **page** (if present), **authority label**. Optionally open **Technical details** for chunk id.
5. **Close** — One sentence: RAG + local embeddings + Groq, citations for trust, honest limits when evidence is missing.

---

## 5-minute demo flow

1. **Problem & solution** (30s) — Students need quick, **source-grounded** guidance; CampusAI retrieves indexed chunks, labels source authority, and uses Groq only **after** you submit a question (not on startup).
2. **Architecture** (60s) — `data/raw` → chunk → FastEmbed → ChromaDB → retriever → prompt + citations → Groq client. No auth/DB in MVP.
3. **Public dataset layer** (45s) — `python -m campusai.fetch_public_dataset` stages MIT FireRoad / Berkeley guide references and local heuristic rules; manifest at `data/processed/source_manifest.json`.
4. **Indexing** (45s) — `python -m campusai.index_documents` (indexes PDF + `.md` + `.txt` under `data/raw`); use `--reset` if replacing a PDF-only index. Optional: `python -m campusai.debug_retrieval` to verify chunks before Groq.
5. **Live Q&A** (90s) — Run the four sample questions below; compare **official/catalog-style** vs **heuristic local** labels.
6. **Limitations** (30s) — Vector persistence on Streamlit Community Cloud may be ephemeral; public fetches can fail; model cold start.

---

## Sample questions (exact wording)

| # | Question |
|---|----------|
| 1 | What should I learn before Machine Learning? |
| 2 | What are Berkeley CS lower division requirements? |
| 3 | Are local advisor rules official university policy? |
| 4 | What does MIT FireRoad data say about Computer Science requirements? |

### Expected answer behavior

1. **ML prerequisites** — Retrieval prefers **heuristic local advisor** chunks for study-path phrasing when that file is indexed; answers stay **English by default** and treat local rules as **not official policy**. If nothing relevant is retrieved, the model should say **indexed context is insufficient** rather than invent prerequisites.
2. **Berkeley lower division** — Should cite indexed Berkeley-related chunks when present; authority should reflect **public / catalog-style** labeling, not your home university’s official policy.
3. **Local advisor rules vs policy** — Should state clearly that **heuristic local advisor sources are not official policy** (matches citation `authority_label` for heuristic sources).
4. **MIT FireRoad** — Should summarize only what appears in indexed FireRoad-related content; if not indexed, should say the system lacks source evidence.

### What to say in an interview

- “I built a **RAG** academic-advising demo: **local embeddings**, **ChromaDB** retrieval, **authority-labeled citations**, and **Groq** behind a manual submit with **rate-limit guards**.”
- “I separated **document-grounded** answers from **heuristic** local rules so the UI does not pretend unofficial text is policy.”
- “I did **not** add auth, microservices, or key rotation—MVP scope stayed deployable and honest about limits.”

### Known limitations

- No upload-to-index in Streamlit yet (CLI indexing).
- Single Groq key only; intentional **no backup key rotation** (rate-limit safety).
- Retrieval quality depends on chunking and what was indexed.
- Streamlit Community Cloud: **vector DB persistence** and **first FastEmbed download** can be slow or non-durable across restarts.
- Public dataset HTTP endpoints may be **temporarily unavailable**.

---

## Manual live smoke test (minimal)

**Only after** `.env` contains a valid `GROQ_API_KEY` locally.

1. Ask **exactly one** safe test question first: *What should I learn before Machine Learning?*
2. **Do not spam** requests; wait a few seconds between questions.
3. If you see a **rate limit** or **timeout** message, wait several minutes and retry.
4. Never paste API keys into chat, README, screenshots, or logs.

For a fuller checklist, see **README.md** → *Manual live smoke test*.
