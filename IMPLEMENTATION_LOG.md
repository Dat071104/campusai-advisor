# Implementation and Debug Log

Use this file as project memory. Every implementation session, debugging session, dependency change, architecture decision, and recurring error should be recorded here.

This file exists so the next AI model does not repeat the same mistake with fresh confidence. Humanity already has enough of that.

## How to use this file

Add a new entry after each meaningful session.

Use this format:

```md
## YYYY-MM-DD HH:mm - Phase / Task

### Context
What were we trying to do?

### Files touched
- file/path.py
- file/path.md

### Commands run
```bash
command here
```

### Result
What worked?

### Error messages
Paste exact errors if any.

### Root cause
What caused the issue?

### Fix applied
What changed?

### Verification
How did we confirm it works?

### Next step
What should the next model or session do?

### Do not repeat
Any trap to avoid next time.
```

## Decision log

### Decision 001 - Build web-first

Status: accepted

Reason: A web demo is easiest to show in a CV, interview, GitHub README, and demo video.

### Decision 002 - Use Groq for chat generation

Status: accepted

Reason: The user has a Groq API key and wants Groq instead of Gemini or OpenAI-hosted models.

### Decision 003 - Use local embeddings for MVP

Status: accepted

Reason: Local embeddings reduce API-key dependency and simplify cost control during development.

### Decision 004 - Avoid microservices during MVP

Status: accepted

Reason: The 3-day MVP needs an end-to-end demo, not distributed failure modes.

### Decision 005 - Keep extension path clean

Status: accepted

Reason: V2 may migrate to Next.js, FastAPI, PostgreSQL + pgvector, and background workers, so modules should not be welded together.

## Known traps

### Trap 001 - Building too much before the app runs

Avoid adding auth, Redis, Celery, Next.js, Kubernetes, or advanced analytics before the basic RAG demo works.

### Trap 002 - Letting the LLM invent academic rules

Document-backed claims must be retrieved from documents. General career advice must be labeled as general advice.

### Trap 003 - Forgetting to update project memory

After debugging, update this file. Otherwise the next session will rediscover the same bug like a goldfish with a terminal.

## Session entries

## 2026-05-12 22:28 - Phase 1 / Project foundation

### Context
Created the initial runnable CampusAI Advisor MVP foundation after root/path preflight passed.

### Files touched
- .gitignore
- .env.example
- README.md
- pyproject.toml
- src/campusai/__init__.py
- src/campusai/config.py
- src/campusai/app.py
- src/campusai/services/__init__.py
- src/campusai/rag/__init__.py
- src/campusai/ui/__init__.py
- tests/test_config.py
- data/raw/.gitkeep
- sample_docs/.gitkeep
- IMPLEMENTATION_LOG.md

### Commands run
```bash
Get-Location | Select-Object -ExpandProperty Path
python --version
python -m pip install -e ".[dev]"
pytest
python -c "from campusai.config import get_settings; from campusai import __version__; print(__version__); print(get_settings().groq_model)"
python -m compileall src tests
rg --files -g '!__pycache__' -g '!*.pyc'
```

### Result
The project now has a clean Python package layout, Streamlit placeholder UI, environment-backed settings, dependency metadata, placeholder `.env.example`, setup documentation, and a passing config smoke test.

### Error messages
None.

### Root cause
No bug was being fixed. This was the first implementation step after the documentation-only setup.

### Fix applied
Added Phase 1 foundation files only. No real `.env` file or secrets were created. No Groq API calls, document ingestion, embeddings, or vector search were implemented.

### Verification
`pytest` passed with 1 test. Config import smoke check printed version `0.1.0` and default model `llama-3.3-70b-versatile`. `compileall` completed for `src` and `tests`.

### Next step
Run Phase 1 audit, then implement document loading and chunking as the next Day 1 increment.

### Do not repeat
Do not add Groq calls, full RAG, databases, Redis, Celery, Docker, or auth before the MVP document pipeline is working.

---

## 2026-05-12 00:00 - Documentation calibration / rule audit cleanup

### Context
We reviewed and calibrated the project rule, workflow, skill, and routing docs before any implementation work.

### Files touched
- AGENTS.md
- PROJECT_RULES.md
- PROJECT_CONTEXT.md
- DEVELOPMENT_WORKFLOW.md
- IMPLEMENTATION_LOG.md
- MODEL_ROUTING_GUIDE.md
- skills/zone-brain/SKILL.md
- skills/campusai-ui/SKILL.md
- .cursor/rules/000-campusai-core.mdc
- .cursor/rules/010-zone-brain-python.mdc

### Commands run
```text
Read and inspected project docs and rule files; no code execution or dependency changes.
```

### Result
The documentation set is now more explicit about secrets handling, workflow phases, Cursor/Codex handoff, and MVP UI defaults.

### Error messages
None.

### Root cause
The original docs were mostly solid but lacked a few explicit guardrails and had one workflow reference mismatch risk.

### Fix applied
Added a dedicated secrets policy, clarified the workflow into plan/execute/audit/fix/verify/log, added Cursor/Codex handoff language, tightened Zone Brain re-scope guidance, and made Streamlit the default MVP UI path.

### Verification
Confirmed the updated docs still reference `scripts/scan_deps.py` from Zone Brain and preserve the 3-day MVP direction.

### Next step
Begin Phase 1 implementation only after the first feature task is chosen.

### Do not repeat
Do not skip the workflow/log docs before editing Python or UI code.

---
