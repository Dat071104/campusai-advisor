# Development Workflow

## Goal

Build a working CampusAI Advisor MVP in 3 days, then leave a clean extension path for production-grade improvements.

The workflow is optimized for AI-assisted coding in Cursor or VS Code. It assumes multiple model sessions may be used, so every phase must leave readable context behind.

## Global workflow loop

For every task:

1. Read `AGENTS.md`, `PROJECT_RULES.md`, `PROJECT_CONTEXT.md`, and this workflow.
2. Check `IMPLEMENTATION_LOG.md` for previous errors and decisions.
3. Define the smallest useful task.
4. Decide the current phase.
   - Plan
   - Execute
   - Audit
   - Fix
   - Verify
   - Log
5. If debugging or refactoring Python, use `skills/zone-brain/SKILL.md`.
6. Implement only the current task.
7. Run the relevant verification command.
8. If verification fails, stop, audit the failure, and fix the smallest root cause before continuing.
9. Update `IMPLEMENTATION_LOG.md`.
10. Stop with a clear next step.

## Day 0: Root setup

Target state:

```text
Root project contains the rule files, workflow files, Cursor rules, local skills, and zone-brain script.
```

Checklist:

```text
[ ] Extract this pack into an empty project root.
[ ] Confirm `.cursor/rules` exists.
[ ] Confirm `skills/zone-brain/SKILL.md` exists.
[ ] Confirm `skills/campusai-ui/SKILL.md` exists.
[ ] Confirm `scripts/scan_deps.py` exists.
[ ] Create or initialize Git repo.
[ ] Create `.gitignore` before adding generated files.
[ ] Create `.env.example` but never commit `.env`.
```

Recommended first Cursor prompt:

```text
Read AGENTS.md, PROJECT_RULES.md, PROJECT_CONTEXT.md, DEVELOPMENT_WORKFLOW.md, and IMPLEMENTATION_LOG.md. Summarize the project goal, current constraints, and the safest next implementation step. Do not write code yet.
```

## Day 1: Foundation and document pipeline

Target state:

```text
The app can load documents, extract text, split chunks, embed chunks, and store them in a local vector store.
```

Tasks:

```text
[ ] Create project structure.
[ ] Add dependency manager setup.
[ ] Add `.env.example`.
[ ] Implement settings/config loading.
[ ] Implement PDF/text document loading.
[ ] Implement chunking.
[ ] Implement local embedding service.
[ ] Implement vector store wrapper.
[ ] Add sample academic documents.
[ ] Add basic tests for settings and chunking.
[ ] Update README setup section.
[ ] Update IMPLEMENTATION_LOG.md.
```

Acceptance criteria:

```text
[ ] A sample document can be indexed.
[ ] Chunks are created with metadata.
[ ] Embeddings are generated locally.
[ ] The vector store persists or can be recreated.
[ ] Tests for chunking/settings pass.
```

## Day 2: RAG chain and advising behavior

Target state:

```text
The system can answer questions using retrieved chunks and Groq, with citations.
```

Tasks:

```text
[ ] Implement retriever.
[ ] Implement citation formatter.
[ ] Implement Groq LLM client.
[ ] Implement academic advisor prompt.
[ ] Implement `answer_question(question, student_profile)`.
[ ] Add fallback when no relevant sources are found.
[ ] Add simple profile-aware advice formatting.
[ ] Add tests for citation formatting and fallback behavior.
[ ] Update IMPLEMENTATION_LOG.md.
```

Acceptance criteria:

```text
[ ] Asking a question returns an answer.
[ ] Answer includes citations when sources exist.
[ ] Answer refuses to invent document-backed policy when no source exists.
[ ] Student profile influences advice.
```

## Day 3: Web UI, demo polish, and deployment readiness

Target state:

```text
The project has a usable web demo and a recruiter-friendly README.
```

Tasks:

```text
[ ] Build web UI using Streamlit or selected web framework.
[ ] Add student profile form.
[ ] Add upload/index flow.
[ ] Add chat interface.
[ ] Add citation display.
[ ] Add loading/error states.
[ ] Polish UI using `skills/campusai-ui/SKILL.md`.
[ ] Write README with architecture, setup, screenshots, and demo script.
[ ] Prepare deployment instructions.
[ ] Add CV bullets.
[ ] Record final known issues in IMPLEMENTATION_LOG.md.
```

Acceptance criteria:

```text
[ ] App can run locally.
[ ] Demo question works.
[ ] Citations are visible.
[ ] README explains the product and architecture.
[ ] Known limitations are documented honestly.
```

## V2 roadmap

Only start V2 after the MVP demo works.

### V2.1: Next.js frontend

Move from Streamlit to a product-style frontend.

```text
frontend/ Next.js + TypeScript + Tailwind
backend/ FastAPI
```

### V2.2: Production database

Move from local vector store to structured storage.

```text
PostgreSQL + pgvector
Supabase or managed Postgres
Alembic migrations
structured document/chunk tables
```

### V2.3: Background jobs

Move slow indexing out of the request/UI path.

```text
Redis
Celery or RQ
job status table
retry logic
```

### V2.4: Multi-user workspace

Add real product behavior.

```text
auth
roles
workspace documents
per-user chat history
admin upload permissions
```

### V2.5: Observability

Make the system easier to debug.

```text
structured logs
latency metrics
token/cost tracking
retrieval quality logging
error monitoring
```

### V2.6: Evaluation

Measure RAG quality.

```text
golden Q&A set
citation correctness checks
retrieval hit rate
answer groundedness review
regression tests
```

## Microservices extension rule

Do not split into microservices until these are true:

```text
[ ] MVP works end-to-end.
[ ] Module boundaries are stable.
[ ] Tests exist for each boundary.
[ ] Deployment complexity is worth it.
[ ] There is a clear reason to scale services independently.
```

Potential future services:

```text
document-ingestion-service
retrieval-service
advisor-service
user-profile-service
evaluation-service
```

Until then, keep a modular monolith. It is less glamorous, which is exactly why it tends to work.
