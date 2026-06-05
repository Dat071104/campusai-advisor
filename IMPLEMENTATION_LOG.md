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

## 2026-06-05 22:35 - Verify / Docker pre-push gate recovery

### Context
Reran the previously blocked Docker pre-push gate on local `main` after Docker Desktop Linux engine became available. The gate was no-key/mock-safe with `GROQ_API_KEY`, `CAMPUSAI_DOCKER_GROQ_API_KEY`, and dotenv disabled.

### Files touched
- Dockerfile
- IMPLEMENTATION_LOG.md

### Commands run
```bash
git status --short
git branch --show-current
git log --oneline -10
git log --oneline origin/main..HEAD
git diff --stat origin/main..HEAD
git fetch origin
git rev-list --left-right --count origin/main...HEAD
docker version
docker compose down --remove-orphans
docker compose build
docker compose up -d
docker compose ps
Invoke-RestMethod http://localhost:8000/health
Invoke-RestMethod http://localhost:8000/status
Invoke-WebRequest http://localhost:8501 -UseBasicParsing
docker compose down --remove-orphans
```

### Result
Docker Desktop Linux engine was available. Initial Docker build failed because editable install ran before required project metadata/source files were copied into the image. After the minimal Dockerfile copy-order fix, Docker build, compose up, FastAPI smoke, and Streamlit smoke passed.

### Error messages
```text
ERROR: file:///app (from -r requirements.txt (line 1)) does not appear to be a Python project: neither 'setup.py' nor 'pyproject.toml' found.
error: error in 'egg_base' option: 'src' does not exist or is not a directory
```

### Root cause
`requirements.txt` starts with `-e .`, so Docker's `pip install -r requirements.txt` needs `pyproject.toml`, `README.md`, and `src/` present before the install step. The Dockerfile copied some of those files only after dependency installation.

### Fix applied
Moved `COPY pyproject.toml`, `COPY README.md`, and `COPY src ./src` before the pip install step in `Dockerfile`.

### Verification
- `docker compose build`: passed.
- `docker compose up -d`: passed.
- `docker compose ps`: `fastapi-backend` and `streamlit-ui` both `Up`.
- `GET http://localhost:8000/health`: `{"status":"ok"}`.
- `GET http://localhost:8000/status`: `status=ok`, `has_groq_key=false`, `has_index=false`.
- `GET http://localhost:8501`: HTTP 200.
- `docker compose down --remove-orphans`: completed.

### Next step
Commit the Dockerfile/log fix, fetch `origin/main` again, verify no remote divergence, then push `main` if git hygiene remains clean.

### Do not repeat
When Docker installs from `requirements.txt` with `-e .`, copy project metadata and package source before running pip.

## 2026-06-05 17:30 - Repo hygiene / Secret-safe Docker and public fetch hardening

### Context
Batch 1-3 from the public-repo audit: harden Docker Compose so it does not expand local `.env` Groq keys, handle MIT FireRoad partial HTTP reads gracefully, add a public license, and clean local audit-log clutter. Real Groq keys had appeared in previous audit output, so they must be revoked/rotated outside this repo.

### Files touched
- .gitignore
- .dockerignore
- Dockerfile
- docker-compose.yml
- docker.env.example
- LICENSE
- README.md
- docs/DEPLOYMENT.md
- src/campusai/datasets/fireroad.py
- tests/test_public_dataset.py
- IMPLEMENTATION_LOG.md

### Commands run
```bash
git status --short
git branch --show-current
git remote -v
git log --oneline -5
python --version
Test-Path .\.env
git check-ignore -v .env
git ls-files .env
python -m compileall src tests
python -m pytest
python -m pytest tests -q
python -m campusai.fetch_public_dataset --timeout 20
```

### Result
Baseline compile/test passed before editing. Docker Compose no longer uses `env_file: .env`; Docker live LLM mode is explicit through `CAMPUSAI_DOCKER_GROQ_API_KEY`, empty by default. FireRoad JSON download now catches `http.client.IncompleteRead` and returns a graceful per-request failure instead of crashing. MIT license was added. Local audit logs were removed and ignored.

### Error messages
Previous audit evidence showed `docker compose config` expanded local `.env` values. Do not paste compose config output when real secret-bearing environment variables are set.

### Root cause
Compose `env_file: .env` caused local app secrets to be included in resolved Compose config output. FireRoad downloads handled URL/timeouts/OS errors but not partial HTTP reads.

### Fix applied
Mapped Docker `GROQ_API_KEY` from a Docker-specific variable with an empty default, added Docker secret-safety documentation, added ignore patterns for local agent workspace and audit logs, made settings honor `PYTHON_DOTENV_DISABLED`, caught `IncompleteRead`, and added regression tests.

### Verification
Passed before commit:
- `python -m compileall src tests`
- `python -m pytest`: 63 passed.
- `python -m campusai.fetch_public_dataset --timeout 20`: completed without traceback.
- `python -m campusai.index_documents --reset`: indexed 39 chunks.
- `python -m campusai.debug_retrieval "What should I learn before Machine Learning?"`: rank 1 `campusai_local_advisor_rules.md`.
- Streamlit HTTP smoke for `src/campusai/app.py` and `streamlit_app.py`: HTTP 200.
- FastAPI smoke `/health`, `/docs`, `/status`: passed; `has_groq_key=False` with `PYTHON_DOTENV_DISABLED=1`.
- Docker Compose safe config scan: no `gsk_` or `sk-` secret patterns; `GROQ_API_KEY` appears only as an empty variable name.
- Docker daemon unavailable, so Docker build/up was blocked rather than failed.

### Next step
Commit and push the explicit Batch 1-3 files if final staged diff and secret scan stay clean.

### Do not repeat
Do not run or paste resolved Compose config while local secrets are present. Do not read or print `.env`; verify only ignore/tracked status.

## 2026-05-16 15:40 - V2.3 fix / Restore optional FastAPI backend boundary

### Context
V2.3 Docker Compose preflight expected `src/campusai/api/app.py`, `/health`, `/status`, `/debug/retrieval`, `/ask`, and Streamlit backend mode via `CAMPUSAI_API_BASE_URL`, but the branch only had the single-process Streamlit/RAG app. `Test-Path .\src\campusai\api\app.py` returned `False`.

### Files touched
- .env.example
- README.md
- docs/API.md
- docs/DEPLOYMENT.md
- pyproject.toml
- requirements.txt
- src/campusai/api/__init__.py
- src/campusai/api/app.py
- src/campusai/app.py
- src/campusai/config.py
- src/campusai/services/api_client.py
- tests/test_answer_chain.py
- tests/test_api_app.py
- tests/test_api_client.py
- tests/test_config.py
- tests/test_language_runtime.py
- tests/test_retriever.py

### Commands run
```bash
$env:PYTHONIOENCODING='utf-8'; python scripts/scan_deps.py --root . --seed "api,fastapi,streamlit,config,rag,answer_chain,retriever,index" --hops 3 --output context
python -m compileall src tests
python -m pytest
Test-Path .\src\campusai\api\app.py
python -c "from campusai.api.app import app; print([route.path for route in app.routes if route.path in {'/health','/status','/debug/retrieval','/ask'}])"
python -m campusai.debug_retrieval "What is TDTU Software Engineering?"
git status --short
```

### Result
Added the missing optional FastAPI backend and Streamlit API-client mode while preserving the default direct local Streamlit workflow when `CAMPUSAI_API_BASE_URL` is unset.

### Error messages
Zone Brain included `.venv_verify` site-packages and reported a noisy zone size of 7421 files because the virtualenv lives under the project root.

### Root cause
The V2.3 prompt described a backend architecture that was not present in the checked-in code. The repo had no `campusai.api.app`, no API routes, no `CAMPUSAI_API_BASE_URL` setting, and no Streamlit-to-backend client.

### Fix applied
Added `campusai.api.app` with `/health`, `/status`, `/status/build-index`, `/debug/retrieval`, and `/ask`; added `CampusAIBackendClient`; added `CAMPUSAI_API_BASE_URL` to settings and `.env.example`; wired Streamlit to use backend mode only when configured; added FastAPI/Uvicorn dependencies; documented API usage; and added tests for API health/status and backend response decoding.

### Verification
- `python -m compileall src tests`: passed.
- `python -m pytest`: 61 passed.
- `Test-Path .\src\campusai\api\app.py`: `True`.
- API route import smoke listed `/health`, `/status`, `/debug/retrieval`, and `/ask`.
- Retrieval smoke still ranked `tdtu_software_engineering_curriculum.md` first for `What is TDTU Software Engineering?`.

### Next step
Run the V2.3 Docker Compose preflight again, then add `Dockerfile`, `.dockerignore`, `docker-compose.yml`, and Docker beginner docs if the preflight stays green.

### Do not repeat
Do not assume an architecture exists because docs or prompts describe it; verify files and import paths first. Keep `CAMPUSAI_API_BASE_URL` unset for Streamlit Cloud and normal local single-process runs.

## 2026-05-14 00:00 - Phase 5A / Streamlit Cloud dependency resolution

### Context
Streamlit Community Cloud failed during dependency installation. The deploy log showed Streamlit cloning the repo and then processing dependencies with Poetry, which failed because it tried to install the project as `campusai-advisor` even though the import package is `campusai` under `src/`.

### Files touched
- requirements.txt
- streamlit_app.py
- README.md
- docs/DEPLOYMENT.md
- IMPLEMENTATION_LOG.md

### Commands run
```bash
# pending verification commands in this session
```

### Result
Root-level pip/uv packaging path was added for Streamlit Cloud, along with a stable root entrypoint.

### Error messages
`The current project could not be installed: No file/folder found for package campusai-advisor`

### Root cause
Streamlit Community Cloud interpreted `pyproject.toml` as Poetry metadata because there was no higher-priority root `requirements.txt`. Poetry then tried to install the project package name instead of the actual import package layout under `src/`.

### Fix applied
Added a root `requirements.txt` with `-e .` plus the runtime dependencies, and added a root `streamlit_app.py` that imports and runs `campusai.app.main`. Updated deployment docs and README to point Streamlit Cloud at the new entrypoint and to note that `requirements.txt` intentionally exists so Cloud uses pip/uv instead of Poetry.

### Verification
Pending. Run editable install, requirements install, import smoke, pytest, compileall, and debug retrieval. No Groq calls allowed.

### Next step
Confirm local install and smoke checks pass, then hand off for Phase 5A audit.

### Do not repeat
Do not convert the project to Poetry, do not add `tool.poetry`, do not remove `pyproject.toml`, and do not commit secrets.

## 2026-05-13 14:00 - Phase 4 / UI polish, demo script, deployment docs

### Context
Phase 4 portfolio prep: polish Streamlit UI (sections, citations, warnings), add demo and deployment documentation, Streamlit theme config, README restructure, and verification without Groq calls.

### Files touched
- src/campusai/app.py
- README.md
- DEMO_SCRIPT.md
- docs/DEPLOYMENT.md
- docs/PORTFOLIO_WRITEUP.md
- .streamlit/config.toml
- IMPLEMENTATION_LOG.md

### Commands run
```bash
python -m pytest
python -m compileall src tests
python -c "import campusai.app; print('app import ok')"
```

### Result
Streamlit layout now foregrounds title, dataset/index metrics, help expander, and structured Q&A with cleaner citation cards and explicit heuristic vs policy messaging. Added demo script, Community Cloud deployment guide, portfolio write-up, and dark theme defaults.

### Verification
- `python -m pytest`: 17 passed.
- `python -m compileall src tests`: ok.
- `import campusai.app`: ok; no Groq calls; no `.env` printed.

### Next step
`READY_FOR_PHASE_4_AUDIT` — manual UI pass and optional Community Cloud trial deploy.

### Do not repeat
Do not add `.streamlit/secrets.toml` to git, do not embed API keys in docs, and do not call Groq during automated verification.

---

## 2026-05-13 12:30 - Phase 3A / Remove unused backup Groq key placeholders

### Context
Phase 3 audit blocked on unused backup Groq key settings/placeholders. The Groq client only uses one primary key, and backup-key placeholders conflicted with the rate-limit safety intent.

### Files touched
- .env.example
- README.md
- src/campusai/config.py
- tests/test_answer_chain.py
- tests/test_retriever.py
- IMPLEMENTATION_LOG.md

### Commands run
```bash
python -m pytest
python -m compileall src tests
$env:PYTHON_DOTENV_DISABLED='1'; python -m pytest; Remove-Item Env:PYTHON_DOTENV_DISABLED
```

### Result
Phase 3A fix completed. Backup Groq key settings/placeholders were removed while keeping the single primary `GROQ_API_KEY` flow intact.

### Error messages
None.

### Root cause
`Settings` and `.env.example` still exposed `GROQ_API_KEY_2` and `GROQ_API_KEY_3` even though the client did not use backup keys.

### Fix applied
Removed `GROQ_API_KEY_2` and `GROQ_API_KEY_3` from runtime settings, environment example placeholders, and test fixtures. Updated setup wording to mention a single Groq key.

### Verification
- `python -m pytest` passed: 17 tests.
- `python -m compileall src tests` passed.
- `$env:PYTHON_DOTENV_DISABLED='1'; python -m pytest; Remove-Item Env:PYTHON_DOTENV_DISABLED` passed: 17 tests.
- Grep confirmed no `GROQ_API_KEY_2` or `GROQ_API_KEY_3` references remain in `src`, `tests`, `.env.example`, or `README.md`.

### Next step
Run Phase 3A audit.

### Do not repeat
Do not add fallback keys, key rotation, or multiple-key guidance to bypass Groq rate limits.

---

## 2026-05-13 12:00 - Phase 3 / Retrieval and RAG answer flow

### Context
Implemented the first usable CampusAI retrieval and RAG answer flow after root/path and secret preflight passed. The phase used existing ChromaDB and FastEmbed infrastructure, added Groq only behind manual question submission, and kept `.env` local/untracked.

### Files touched
- README.md
- pyproject.toml
- src/campusai/app.py
- src/campusai/config.py
- src/campusai/rag/vector_store.py
- src/campusai/rag/retriever.py
- src/campusai/rag/citations.py
- src/campusai/rag/prompts.py
- src/campusai/rag/answer_chain.py
- src/campusai/services/groq_client.py
- tests/test_retriever.py
- tests/test_citations.py
- tests/test_answer_chain.py
- IMPLEMENTATION_LOG.md

### Commands run
```bash
git rev-parse --show-toplevel
git ls-files --error-unmatch .env
python scripts/scan_deps.py --root . --seed "retriever,vector,search,groq,llm,client,chain,citation,config,streamlit,app" --hops 2 --output context
python -m pytest
python -m compileall src tests
python -m campusai.index_documents
python -c "import campusai.app; from campusai.config import get_settings; print('app import ok'); print(get_settings().has_groq_key)"
```

### Result
Added retrieval, citation formatting, prompt construction, Groq chat client with conservative free-tier safeguards, RAG answer orchestration, and Streamlit question-answer UI with profile context, warnings, spinner, citations, and no-index/missing-key handling.

### Error messages
Initial Zone Brain scan failed on Windows cp1252 output because the script prints emoji. Re-ran with `PYTHONIOENCODING=utf-8` successfully. Initial tests found a circular import through `ingestion.__init__` and `vector_store`; this was fixed by moving `TextChunk` import behind `TYPE_CHECKING` in `vector_store.py`.

### Root cause
The retrieval code imported the vector store, which imported `campusai.ingestion.chunker`; package initialization also imported `indexer`, which imported the vector store again. This created a partial module initialization cycle.

### Fix applied
Added `TYPE_CHECKING` guarded typing in `vector_store.py`, avoiding runtime import of ingestion code from the vector store. Added unit tests for retriever, citations, answer-chain fallbacks, prompt authority instructions, and secret redaction. Added `openai` dependency for the OpenAI-compatible Groq client.

### Verification
- `python -m pytest` passed: 17 tests.
- `python -m compileall src tests` passed.
- `python -m campusai.index_documents` completed and indexed 10 chunks from 8 pages across 1 PDF file.
- App import smoke check passed without printing secrets.
- Linter diagnostics reported no errors on edited files.

### Next step
Run Phase 3 audit focused on retrieval quality, citation authority correctness, UI manual behavior, and Groq rate-limit/missing-key behavior.

### Do not repeat
Do not rotate multiple Groq keys, do not call Groq in tests, do not call Groq at app startup, do not expose `.env`, and do not make local heuristic advisor rules look official.

---

## 2026-05-13 00:00 - Phase 2.5 / Public dataset adapter

### Context
Added a public dataset adapter layer for MIT FireRoad, Berkeley CS Guide, and local heuristic advisor rules without calling Groq or creating real secrets.

### Files touched
- src/campusai/datasets/__init__.py
- src/campusai/datasets/fireroad.py
- src/campusai/datasets/berkeley.py
- src/campusai/datasets/local_rules.py
- src/campusai/fetch_public_dataset.py
- data/raw/documents/local/campusai_local_advisor_rules.md
- tests/test_public_dataset.py
- README.md
- IMPLEMENTATION_LOG.md

### Commands run
```bash
Read AGENTS.md, PROJECT_RULES.md, PROJECT_CONTEXT.md, DEVELOPMENT_WORKFLOW.md, IMPLEMENTATION_LOG.md, and MODEL_ROUTING_GUIDE.md
```

### Result
Dataset adapter scaffolding and a CLI entrypoint were added. The local heuristic rules file now exists in the expected raw-documents location. The implementation is intentionally safe: it does not call Groq, does not create `.env`, and handles live HTTP failures gracefully.

### Error messages
None yet.

### Root cause
This was the next phase increment after the document ingestion/indexing pipeline.

### Fix applied
Created modular dataset adapters, a fetch CLI, a manifest writer, a local heuristic rules document, and tests for manifest shape, FireRoad markdown conversion, and local rules existence.

### Verification
Pending. The next step is to run pytest, compileall, and the dataset fetch command.

### Next step
Run the safe verification commands and note whether live network fetch succeeds or requires manual fallback.

### Do not repeat
Do not add real secrets, do not call Groq, and do not expand into answer generation yet.

---

## 2026-05-13 00:30 - Phase 2.5 recovery / Dataset fetch hang

### Context
The Phase 2.5 dataset fetch command previously hung while running `python -m campusai.fetch_public_dataset`. Pytest and compileall had already passed before the hang, so this recovery continued from the existing partial implementation instead of restarting the phase.

### Files touched
- src/campusai/fetch_public_dataset.py
- src/campusai/datasets/fireroad.py
- src/campusai/datasets/berkeley.py
- IMPLEMENTATION_LOG.md

### Commands run
```bash
python -m pytest
python -m compileall src tests
python -m campusai.fetch_public_dataset --timeout 20 --max-courses 100
```

### Result
The live dataset fetch command completed cleanly. It generated or reused local advisor rules, fetched MIT FireRoad catalog and selected requirements, downloaded Berkeley CS Guide HTML/PDF, and wrote the manifest.

### Error messages
None during verification after the fix.

### Root cause
The CLI did not expose recovery controls for bounded public fetches, and progress was only printed after all fetches finished. Even though adapter methods had timeout parameters, the entrypoint did not make timeout behavior visible/configurable and a slow public endpoint could appear to hang without showing which source was in progress.

### Fix applied
Added CLI options `--timeout`, `--skip-network`, and `--max-courses`; added progress output before every public fetch; preserved local advisor rules generation independently from network fetches; reported individual fetch failures/timeouts without failing the whole phase; and limited saved MIT FireRoad catalog data when `--max-courses` is provided.

### Verification
- `python -m pytest` passed: 8 tests.
- `python -m compileall src tests` passed.
- `python -m campusai.fetch_public_dataset --timeout 20 --max-courses 100` exited with status 0.

### Remaining limitations
Network success still depends on public endpoint availability and response speed. The command now exits cleanly on per-request timeout/failure and supports `--skip-network` for offline/local-only manifest generation, but it does not guarantee public datasets are fresh when endpoints are unavailable.

### Do not repeat
Do not call Groq, do not create `.env`, do not add real secrets, do not modify `scripts/scan_deps.py`, and do not implement RAG answer generation in this phase.

---


## 2026-05-12 22:44 - Phase 2 / Document ingestion and local indexing

### Context
Implemented the Phase 2 local document ingestion and indexing pipeline without creating `.env`, adding secrets, or calling Groq.

### Files touched
- .env.example
- README.md
- pyproject.toml
- src/campusai/config.py
- src/campusai/app.py
- src/campusai/index_documents.py
- src/campusai/ingestion/__init__.py
- src/campusai/ingestion/pdf_loader.py
- src/campusai/ingestion/chunker.py
- src/campusai/ingestion/indexer.py
- src/campusai/rag/embeddings.py
- src/campusai/rag/vector_store.py
- tests/test_chunker.py
- tests/test_ingestion_smoke.py
- IMPLEMENTATION_LOG.md

### Commands run
```bash
Get-Location | Select-Object -ExpandProperty Path
python -m pip install -e ".[dev]"
pytest
python -m compileall src tests
python -m campusai.index_documents
git status --short
```

### Result
PDF discovery/loading, page metadata extraction, chunking, FastEmbed embedding wrapper, ChromaDB vector-store wrapper, indexing service, and `python -m campusai.index_documents` command are implemented. Empty `data/raw` is handled without crashing.

### Error messages
None. Pip emitted cache deserialization warnings, but dependency installation completed successfully.

### Root cause
No bug was being fixed. This was the next MVP implementation increment after Phase 1 foundation.

### Fix applied
Added Phase 2 pipeline modules and tests. Added direct dependencies `pymupdf`, `fastembed`, and `chromadb`. Tests use fakes for embeddings and vector storage so they do not require network, model downloads, real PDFs, or API keys.

### Verification
`pytest` passed with 5 tests. `compileall` completed for `src` and `tests`. `python -m campusai.index_documents` returned `No PDF files found in data\raw.` with exit code 0.

### Next step
Run Phase 2 audit, then implement retrieval, citation formatting, and Groq-backed answer generation in the next phase.

### Do not repeat
Do not run real indexing with private documents unless the user has placed safe local PDFs in `data/raw`. Do not call Groq or add real keys before the answer-generation phase.

---

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

## 2026-05-13 - Phase 4A fix — English runtime + study-path retrieval

### Context
Manual live smoke test: Groq answered successfully but output was Vietnamese-first and retrieval surfaced mostly irrelevant Berkeley scheduling/policy chunks for an ML prerequisites-style question.

### Files touched
- `src/campusai/rag/prompts.py`
- `src/campusai/rag/answer_chain.py`
- `src/campusai/rag/retriever.py`
- `src/campusai/rag/citations.py`
- `src/campusai/services/groq_client.py`
- `src/campusai/app.py`
- `README.md`
- `DEMO_SCRIPT.md`
- `IMPLEMENTATION_LOG.md`
- `tests/test_retriever.py`
- `tests/test_answer_chain.py`
- `tests/test_citations.py`
- `tests/test_language_runtime.py`

### Commands run
```bash
python -m pytest tests/ -q
python -m compileall src tests -q
python -m campusai.index_documents
python -c "import campusai.app; print('app import ok')"
```

### Result
All tests passed (40). Compile and app import succeeded. Indexing succeeded against current `data/raw` PDFs. No live Groq call in automation.

### Error messages
None.

### Root cause
- **Language:** `SYSTEM_PROMPT` and several fallbacks were Vietnamese-first, so the model followed that default even for English questions.
- **Retrieval:** Pure top-k vector similarity favored dense Berkeley guide/policy chunks over the shorter local advisor markdown for study-order questions; no intent-aware reranking.

### Fix applied
- English default system and user prompt scaffolding; explicit rule to use another language only when the user asks.
- English runtime strings in `answer_chain`, `groq_client`, `citations`, and Streamlit placeholder.
- Lightweight study-path / ML-prep intent detection: widened fetch + post-retrieval rerank that boosts chunks whose paths match `campusai_local_advisor_rules` / `documents/local` and heuristic authority, without changing behavior for generic catalog/policy queries.
- Prompt **retrieval note** when study-path intent fires but no local advisor chunk appears in the retrieved set, to discourage confident answers from unrelated snippets.
- Tests for intent, rerank ordering, English system prompt, missing-key message, and a diacritic scan over `rag/*.py` + `groq_client.py`.

### Verification
pytest, compileall, `campusai.index_documents`, `import campusai.app`.

### Next step
Phase 4A audit re-run (manual smoke with `What should I learn before Machine Learning?`) and watch citations favor local advisor rules when indexed.

### Do not repeat
Keep project-facing text English by default; smoke-test retrieval with the English ML study-path question and expect local heuristic chunks to rank above unrelated Berkeley scheduling text when that file is in the index.

---

## 2026-05-15 00:00 - Phase 5C / TDTU and Vietnam local knowledge pack

### Context
Built a first structured local knowledge pack for TDTU official facts and Vietnam CS/IT career heuristics under `data/raw/documents/tdtu/` and `data/raw/documents/local/`.

### Files touched
- data/raw/documents/tdtu/tdtu_fit_overview_contacts.md
- data/raw/documents/tdtu/tdtu_software_engineering_curriculum.md
- data/raw/documents/tdtu/tdtu_computer_science_curriculum.md
- data/raw/documents/tdtu/tdtu_information_systems_curriculum.md
- data/raw/documents/tdtu/tdtu_computer_networks_curriculum.md
- data/raw/documents/tdtu/tdtu_academic_regulations_graduation.md
- data/raw/documents/tdtu/tdtu_admissions_open_day.md
- data/raw/documents/tdtu/tdtu_student_handbook_international.md
- data/raw/documents/local/vietnam_it_career_context_2026.md
- data/raw/documents/local/local_backend_ai_advisor_heuristics.md
- IMPLEMENTATION_LOG.md

### Commands run
```bash
# pending verification commands in this session
```

### Result
Added clean RAG-ingestion Markdown sources with YAML metadata blocks, short sections, and explicit official-vs-heuristic separation.

### Error messages
None yet.

### Root cause
This was the next content-expansion phase after the ingestion pipeline started supporting Markdown and text sources.

### Fix applied
Created TDTU official fact files, graduation/policy notes, admission-context notes, international handbook context, a Vietnam IT career-context note, and a practical backend+AI heuristic roadmap.

### Verification
Pending. Run compileall, pytest, indexing, and retrieval debug checks to confirm the new documents are ingested and retrievable.

### Next step
Run the validation commands and confirm the three target retrieval queries return the intended source files.

### Do not repeat
Do not mix official policy with heuristic advice, do not invent claims without URLs, and do not index secrets or vector DB files.

---

## 2026-05-16 00:00 - Phase 5C fix / Map Markdown source_authority into retrieval metadata

### Context
The new TDTU and local Vietnam Markdown knowledge pack indexed successfully, but `python -m campusai.debug_retrieval` showed blank `authority:` values for the new Markdown files even when they contained structured metadata such as `source_authority`, `source_type`, and `official_policy`.

### Files touched
- src/campusai/ingestion/text_loader.py
- src/campusai/ingestion/pdf_loader.py
- src/campusai/ingestion/chunker.py
- src/campusai/rag/retriever.py
- tests/test_text_loader.py
- tests/test_ingestion_smoke.py
- tests/test_retriever.py
- IMPLEMENTATION_LOG.md

### Commands run
```bash
python -m compileall src tests
python -m pytest
python -m campusai.index_documents --reset
python -m campusai.debug_retrieval "What should a Backend + AI student learn?"
python -m campusai.debug_retrieval "What is TDTU Software Engineering?"
python -m campusai.debug_retrieval "What are TDTU graduation requirements?"
git status --short
git ls-files .env .streamlit/secrets.toml data/vector_db
```

### Result
Markdown metadata now maps `source_authority` into chunk metadata `authority`, preserves the special local advisor rules override, and threads simple metadata fields through retrieval without affecting PDF ingestion.

### Error messages
None after sequential verification. An earlier parallelized verification attempt produced false `No vector index found...` results because retrieval checks overlapped the reset/index command instead of waiting for it to finish.

### Root cause
The text loader only assigned metadata from filename-based defaults and never parsed the YAML metadata blocks in the new Markdown knowledge pack, so `source_authority` never reached Chroma chunk metadata or retrieval output.

### Fix applied
Added a small fenced-YAML metadata parser in the text loader, mapped `source_authority`, `source_type`, `official_policy`, `university`, `country`, and `language` into page/chunk metadata, kept the `campusai_local_advisor_rules.md` hardcoded heuristic override, and added regression tests for loader, ingestion, and retrieval metadata parsing.

### Verification
- `python -m compileall src tests`: passed.
- `python -m pytest`: 54 passed.
- `python -m campusai.index_documents --reset`: indexed 40 chunks from 19 pages across 1 PDF and 11 markdown/text files.
- `python -m campusai.debug_retrieval "What should a Backend + AI student learn?"`: rank 1 `local_backend_ai_advisor_heuristics.md`, authority `heuristic_advice`.
- `python -m campusai.debug_retrieval "What is TDTU Software Engineering?"`: rank 1 `tdtu_software_engineering_curriculum.md`, authority `official_curriculum`.
- `python -m campusai.debug_retrieval "What are TDTU graduation requirements?"`: rank 1 `tdtu_academic_regulations_graduation.md`, authority `official_policy`.
- `git ls-files .env .streamlit/secrets.toml data/vector_db`: no output.

### Next step
Run the full Phase 5C verification sequence and confirm the three target retrieval queries show the expected authority values.

### Do not repeat
Do not rely on filename-only metadata when shipping structured Markdown knowledge packs; parse the document metadata block and preserve official-vs-heuristic authority labels end to end.

---

## 2026-05-16 00:30 - Phase 5C fix / Repair mojibake in TDTU Markdown knowledge docs

### Context
The TDTU and Vietnam local knowledge-pack Markdown files indexed and retrieved correctly, but several official program names and quoted phrases were stored with mojibake, making the source text look broken before commit.

### Files touched
- data/raw/documents/tdtu/tdtu_software_engineering_curriculum.md
- data/raw/documents/tdtu/tdtu_computer_science_curriculum.md
- data/raw/documents/tdtu/tdtu_computer_networks_curriculum.md
- data/raw/documents/tdtu/tdtu_information_systems_curriculum.md
- data/raw/documents/tdtu/tdtu_fit_overview_contacts.md
- data/raw/documents/tdtu/tdtu_academic_regulations_graduation.md
- data/raw/documents/tdtu/tdtu_admissions_open_day.md
- data/raw/documents/local/vietnam_it_career_context_2026.md
- IMPLEMENTATION_LOG.md

### Commands run
```bash
Select-String -Path data/raw/documents/tdtu/*.md,data/raw/documents/local/*.md -Pattern "Ã|â|á»|áº|Æ|Ä|�"
python -m compileall src tests
python -m pytest
python -m campusai.index_documents --reset
python -m campusai.debug_retrieval "What is TDTU Software Engineering?"
python -m campusai.debug_retrieval "What is the TDTU Computer Science program?"
python -m campusai.debug_retrieval "What are TDTU graduation requirements?"
python -m campusai.debug_retrieval "What should a Backend + AI student learn?"
git status --short
git ls-files .env .streamlit/secrets.toml data/vector_db
```

### Result
The corrupted Vietnamese program names, faculty/location names, apostrophes, and quoted phrases were repaired in the Markdown knowledge docs while preserving metadata fields and authority separation.

### Error messages
The provided `Select-String` pattern still returned the correctly encoded address line in `tdtu_fit_overview_contacts.md` because the pattern is broad enough to match valid Vietnamese Unicode characters, not just mojibake.

### Root cause
The Markdown content was authored or pasted with mixed encoding damage, so some Vietnamese strings and smart punctuation were stored as mojibake even though the metadata structure and retrieval logic were correct.

### Fix applied
Rewrote the affected Markdown knowledge docs in UTF-8 with correct Vietnamese names such as `Kỹ thuật phần mềm`, `Khoa học máy tính`, `Mạng máy tính và truyền thông dữ liệu`, `Hệ thống thông tin`, `Khoa Công nghệ thông tin`, `Phòng C004`, and `Nguyễn Hữu Thọ`. Replaced broken smart quotes with ASCII quotes where needed and kept all metadata fields unchanged.

### Verification
- `python -m compileall src tests`: passed.
- `python -m pytest`: 54 passed.
- `python -m campusai.index_documents --reset`: indexed 40 chunks from 19 pages across 1 PDF and 11 markdown/text files.
- `python -m campusai.debug_retrieval "What is TDTU Software Engineering?"`: rank 1 `tdtu_software_engineering_curriculum.md`, authority `official_curriculum`.
- `python -m campusai.debug_retrieval "What is the TDTU Computer Science program?"`: rank 1 `tdtu_computer_science_curriculum.md`, authority `official_curriculum`.
- `python -m campusai.debug_retrieval "What are TDTU graduation requirements?"`: rank 1 `tdtu_academic_regulations_graduation.md`, authority `official_policy`.
- `python -m campusai.debug_retrieval "What should a Backend + AI student learn?"`: rank 1 `local_backend_ai_advisor_heuristics.md`, authority `heuristic_advice`.
- `git ls-files .env .streamlit/secrets.toml data/vector_db`: no output.

### Next step
Run a narrower mojibake detector if the team wants an automated content check that does not flag valid Vietnamese text.

### Do not repeat
When validating multilingual Markdown content, do not rely on an over-broad mojibake regex alone; check actual rendered retrieval output as the source-of-truth for readability.

---

## 2026-05-13 - Phase 4B fix — index Markdown/TXT + reset + debug retrieval

### Context
Manual smoke test: `campusai_local_advisor_rules.md` existed under `data/raw/documents/local/` but retrieval kept surfacing Berkeley PDF chunks. Indexing CLI reported only PDF page counts, implying Markdown/text was never ingested.

### Files touched
- `src/campusai/ingestion/pdf_loader.py`
- `src/campusai/ingestion/text_loader.py`
- `src/campusai/ingestion/chunker.py`
- `src/campusai/ingestion/indexer.py`
- `src/campusai/index_documents.py`
- `src/campusai/debug_retrieval.py`
- `src/campusai/rag/vector_store.py`
- `src/campusai/rag/retriever.py`
- `src/campusai/app.py`
- `pyproject.toml`
- `README.md`
- `DEMO_SCRIPT.md`
- `IMPLEMENTATION_LOG.md`
- `tests/test_chunker.py`
- `tests/test_ingestion_smoke.py`
- `tests/test_retriever.py`
- `tests/test_text_loader.py`
- `tests/test_vector_store.py`

### Commands run
```bash
python -m pytest
python -m compileall src tests
python -m campusai.index_documents --reset
python -m campusai.debug_retrieval "What should I learn before Machine Learning?"
```

### Root cause
The indexer only discovered `*.pdf` under `RAW_DATA_DIR` and never loaded `.md`/`.txt`, so local advisor heuristics were absent from Chroma despite the file on disk.

### Fix applied
- Recursive Markdown + plain-text discovery and UTF-8 loading with rich metadata (`document_type`, `authority`, `source_type`, `is_official_policy` for `campusai_local_advisor_rules.md`).
- Extended `DocumentPage` / `TextChunk` metadata (PDFs keep `document_type="pdf"`).
- `python -m campusai.index_documents --reset` clears the Chroma collection before upsert when requested.
- `python -m campusai.debug_retrieval` dry-run (no Groq, no API key) prints ranked chunks with previews; reconfigures UTF-8 stdout on Windows so PDF unicode previews do not crash the CLI.
- Tests for text loader, chunk metadata, ingestion of Markdown-only trees, Chroma reset, and rerank behavior.

### Verification
- `python -m pytest`: 48 passed.
- `python -m compileall src tests`: ok.
- `python -m campusai.index_documents --reset`: reported 11 chunks from 9 pages (1 PDF + 1 markdown/text file).
- `python -m campusai.debug_retrieval "What should I learn before Machine Learning?"`: rank 1 `campusai_local_advisor_rules.md`, authority `heuristic`.

### Next step
Phase 4B audit: optional live Groq smoke after confirming `debug_retrieval` shows local advisor chunks at the top.

### Do not repeat
Assume “indexing” includes every source type you ship on disk; extend discovery when adding new raw formats, and use `debug_retrieval` before blaming the LLM for missing context.
---

## 2026-05-16 00:49 - Phase 5C fix / Harden graduation-policy reranking against unrelated official policy docs

### Context
The Phase 5C target query was `What are TDTU graduation requirements?`. The expected outcome was rank 1 `tdtu_academic_regulations_graduation.md` with authority `official_policy`, while keeping Software Engineering, Computer Science, and Backend + AI retrieval behavior intact.

### Files touched
- src/campusai/rag/retriever.py
- tests/test_retriever.py
- IMPLEMENTATION_LOG.md

### Commands run
```bash
python scripts/scan_deps.py --root . --seed "retriever,graduation,policy,search,debug_retrieval,text_loader" --hops 2 --output context
python -m compileall src tests
python -m pytest
python -m campusai.index_documents --reset
python -m campusai.debug_retrieval "What is TDTU Software Engineering?"
python -m campusai.debug_retrieval "What is the TDTU Computer Science program?"
python -m campusai.debug_retrieval "What are TDTU graduation requirements?"
python -m campusai.debug_retrieval "What should a Backend + AI student learn?"
git status --short
git ls-files .env .streamlit/secrets.toml data/vector_db
```

### Result
Graduation-policy retrieval is now explicitly hardened against unrelated `official_policy` documents such as international handbook content, while preserving the expected top-ranked documents for the three other validation queries.

### Error messages
`python scripts/scan_deps.py ...` initially failed on Windows with:
`UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f50d'`

### Root cause
The retriever already had a graduation-policy rerank path, but it did not broadly penalize handbook/international-policy sources unless their filenames matched a narrow `international_student` pattern. That left room for unrelated `official_policy` chunks to remain more competitive than they should be for generic graduation-requirement queries.

### Fix applied
Added shared international-query markers so graduation-policy reranking does not trigger for explicitly international-student questions, and added a stronger deboost for handbook/international source filenames during graduation-policy reranking. Added regression tests for both behaviors.

### Verification
- `python -m compileall src tests`: passed.
- `python -m pytest`: 58 passed.
- `python -m campusai.index_documents --reset`: `Indexed 39 chunks from 19 pages across 1 PDF file(s) and 11 markdown/text file(s).`
- `python -m campusai.debug_retrieval "What is TDTU Software Engineering?"`: rank 1 `tdtu_software_engineering_curriculum.md`, authority `official_curriculum`.
- `python -m campusai.debug_retrieval "What is the TDTU Computer Science program?"`: rank 1 `tdtu_computer_science_curriculum.md`, authority `official_curriculum`.
- `python -m campusai.debug_retrieval "What are TDTU graduation requirements?"`: rank 1 `tdtu_academic_regulations_graduation.md`, authority `official_policy`.
- `python -m campusai.debug_retrieval "What should a Backend + AI student learn?"`: rank 1 `local_backend_ai_advisor_heuristics.md`, authority `heuristic_advice`.
- `git ls-files .env .streamlit/secrets.toml data/vector_db`: no output.

### Next step
READY_FOR_AUDIT: optional follow-up is a narrower content cleanup for the remaining mojibake in some curriculum body text, but it is not required for the graduation-ranking fix.

### Do not repeat
When using Zone Brain on Windows, set `PYTHONIOENCODING=utf-8` first if the scanner prints emoji; otherwise the dependency scan can fail before producing useful context.

---

## 2026-05-16 14:31 - Phase 5C / API endpoint test-fix for monkeypatched dependencies

### Context
`tests/test_api_app.py` had two failing tests: the debug retrieval endpoint returned an empty `results` list, and the ask endpoint returned empty `citations`. The tests monkeypatch module-level factories `get_retriever` and `get_answer_chain` with simple dummy implementations.

### Files touched
- src/campusai/api/app.py
- IMPLEMENTATION_LOG.md

### Commands run
```bash
python scripts/scan_deps.py --root . --seed "api_app,answer_chain,retriever,debug_retrieval,fastapi" --hops 2 --output context
python -m pytest tests/test_api_app.py -q
python -m compileall src tests
python -m pytest
git status --short
```

### Result
The FastAPI endpoints now honor monkeypatched test factories and the full test suite passes.

### Error messages
- `IndexError: list index out of range` in `test_debug_retrieval_endpoint`
- `assert []` in `test_ask_endpoint_without_groq`
- After the first patch, the tests surfaced a more specific compatibility error:
  `TypeError: <lambda>() takes 0 positional arguments but 1 was given`

### Root cause
FastAPI had captured the original dependency callables at route-definition time via `Depends(get_retriever)` and `Depends(get_answer_chain)`. Monkeypatching the module attributes in tests did not replace those already-bound dependency callables, so the routes kept using the real production services instead of the dummy test doubles. After adding runtime indirection, the wrappers still assumed production-style `factory(settings)` signatures, while the tests used zero-argument lambdas.

### Fix applied
Added runtime resolver wrappers in `src/campusai/api/app.py`:
- `_resolve_settings()` to indirect settings lookup at request time
- `_resolve_retriever()` and `_resolve_answer_chain()` to call the current module-level factories at request time
- `_call_factory()` to support both production factories that accept `settings` and zero-argument monkeypatched test doubles

### Verification
- `python -m pytest tests/test_api_app.py -q`: `4 passed in 0.61s`
- `python -m compileall src tests`: passed
- `python -m pytest`: `62 passed in 7.76s`

### Next step
Continue the current API workstream or run an audit on the new FastAPI module and docs if that branch is about to be merged.

### Do not repeat
When tests monkeypatch FastAPI dependency factories, avoid binding route dependencies directly to the production factory if the test strategy expects module-level monkeypatching to take effect.
