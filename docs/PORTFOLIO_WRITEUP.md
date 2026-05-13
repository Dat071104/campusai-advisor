# CampusAI Advisor — Portfolio write-up (short)

**One-liner:** A university-focused **RAG** academic advising demo that retrieves **locally embedded** document chunks, labels **source authority**, and generates answers with **Groq** only when the user submits a question—never on startup.

**What to highlight in a CV or interview**

- End-to-end **ingestion → chunk → embed (FastEmbed) → ChromaDB → retrieve → cite → LLM** pipeline in Python.
- **Citation cards** with page metadata and explicit **heuristic vs public vs catalog-style** authority language so the product does not fake official policy.
- **Operational caution:** conservative Groq **timeouts**, **retries**, and **minimum spacing** between live calls; **single API key** (no rotation workaround).
- **Honest failure modes:** missing index, missing API key, empty retrieval, rate limits, and timeouts surface as user-visible messages.

**What it is not (MVP honesty)**

- Not a production registrar or policy system.
- No authentication, multi-tenant workspaces, or background job queues.
- Streamlit Community Cloud persistence of vector state may require a V2 storage strategy.

**Suggested repo story**

“I shipped a portfolio-grade RAG advising MVP: local embeddings, vector search, authority-aware citations, and a deployable Streamlit UI with documented limits.”
