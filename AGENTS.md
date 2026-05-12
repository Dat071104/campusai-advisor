# Agent Instructions: CampusAI Advisor

Read these files before planning or editing code:

1. `PROJECT_RULES.md`
2. `PROJECT_CONTEXT.md`
3. `DEVELOPMENT_WORKFLOW.md`
4. `IMPLEMENTATION_LOG.md`
5. `MODEL_ROUTING_GUIDE.md`

Use the project-local skills when relevant:

- `skills/zone-brain/SKILL.md` for Python debugging, refactoring, dependency-zone analysis, or affected-file discovery.
- `skills/campusai-ui/SKILL.md` for web UI, Streamlit UI, chat UI, upload/index flows, citation cards, landing pages, and dashboard polish.

## Operating rules

- Keep the 3-day MVP scope unless the user explicitly asks for a V2 change.
- Prefer working, testable increments over large rewrites.
- You may install libraries if they clearly reduce complexity or improve reliability, but document the reason in `IMPLEMENTATION_LOG.md`.
- Do not hardcode secrets, API keys, tokens, database URLs, or credentials.
- Do not commit `.env`, `.env.local`, uploaded private documents, vector database artifacts, or generated cache files.
- Use Groq for LLM chat generation unless the user changes the provider.
- Use local embeddings for the MVP unless the user changes the provider.
- Do not invent university policies, course rules, prerequisites, graduation conditions, or tuition information.
- If retrieved documents do not support an answer, say that the system does not have enough source evidence.
- Update `IMPLEMENTATION_LOG.md` after each meaningful implementation or debugging session.
- If verification fails, pause and re-audit the smallest likely cause before making broad changes.

## Before coding

1. Summarize the current objective.
2. Identify the current phase from `DEVELOPMENT_WORKFLOW.md`.
3. List files likely to be changed.
4. Confirm whether `skills/zone-brain` should be used.
5. Make the smallest coherent implementation step.

## After coding

1. List files changed.
2. List commands run.
3. Report tests, lint, build, or manual verification results.
4. Add an entry to `IMPLEMENTATION_LOG.md`.
5. Name the next recommended task.
