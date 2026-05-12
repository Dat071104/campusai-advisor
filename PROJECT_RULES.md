# Project Rules

## Project identity

Project name: `CampusAI Advisor`

Purpose: Build a web-first AI academic advising and RAG chatbot for university students. The MVP should let a student ask questions about school documents, study paths, course prerequisites, academic policies, and career direction, with answers grounded in uploaded documents and shown with citations.

The project is a portfolio project for Backend + AI Integration. It must demonstrate practical engineering: document ingestion, chunking, embeddings, vector search, LLM orchestration, citation handling, UI flow, deployment readiness, and clean documentation.

## MVP goal

Build a 3-day MVP that can be shown in a demo video and linked in a CV.

The MVP must support:

- Web UI
- Student profile context
- Document upload or document ingestion
- Document chunking
- Embedding generation
- Vector retrieval
- Groq-powered answer generation
- Citations or source references
- Basic academic/study advising behavior
- Clear README and demo script

## Preferred MVP architecture

Use the simplest architecture that can work well in 3 days.

Recommended MVP shape:

```text
Web UI
  -> application service layer
    -> document ingestion
    -> chunking
    -> embeddings
    -> vector store
    -> retrieval
    -> Groq LLM client
    -> answer + citations
```

For a fast MVP, a Streamlit web app is acceptable. For V2, a Next.js frontend and FastAPI backend can be introduced.

## Provider decisions

Default LLM provider:

```text
Groq
```

Default Groq configuration:

```env
GROQ_API_KEY=your_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile
```

Default embedding approach:

```text
Local embeddings first, using FastEmbed or another lightweight local embedding library.
```

Reason: this avoids requiring another paid embedding provider during the MVP.

## Allowed libraries

Agents may install libraries when needed, but must obey these rules:

1. Prefer stable, common libraries.
2. Avoid adding heavy frameworks unless they clearly reduce implementation time.
3. Explain why each new dependency is needed.
4. Update dependency files and setup docs.
5. Record dependency changes in `IMPLEMENTATION_LOG.md`.

Examples of acceptable MVP libraries:

```text
fastapi
streamlit
pydantic
python-dotenv
openai
pymupdf
chromadb
fastembed
rank-bm25
pytest
ruff
```

## Do not do during MVP

Do not add these unless the user explicitly asks:

```text
Kubernetes
Terraform
AWS production infrastructure
multi-service orchestration
Redis
Celery
RabbitMQ
authentication system
payment system
multi-tenant enterprise permissions
complex admin analytics
custom domain
mobile app
```

These are V2 or later concerns. Building them during the MVP is how projects become impressive ruins.

## Extension path

Design code so that future migration is possible:

- Streamlit UI can later become a Next.js frontend.
- Direct function calls can later become FastAPI endpoints.
- ChromaDB can later become PostgreSQL + pgvector.
- Synchronous indexing can later become Redis/Celery background jobs.
- Single-user demo can later become multi-user workspace.
- Basic citation matching can later become evaluation-driven RAG quality checks.

Do not implement all of that now. Keep boundaries clean enough that future work is not painful.

## RAG rules

The assistant must:

- Retrieve relevant document chunks before answering document-specific questions.
- Include citations or source references when using document evidence.
- Avoid pretending that a policy exists if it was not retrieved.
- State uncertainty clearly.
- Separate document-grounded answers from general study/career advice.

A good answer format:

```text
Answer
Why this applies to you
Sources
Caveat / what is not found in documents
```

## Academic advising rules

Use the student profile when available:

```text
major
academic year
career goal
completed courses
interests
weak areas
preferred learning style
```

Use deterministic logic for prerequisite checks when structured course data exists. Use the LLM mainly to explain recommendations and summarize tradeoffs.

Do not let the LLM invent prerequisites or graduation rules.

## Code quality rules

- Keep files small.
- Prefer service modules over giant app files.
- Keep IO, retrieval, LLM calls, and UI separate where practical.
- Add type hints where useful.
- Add basic tests for chunking, citation formatting, settings loading, and retrieval utilities.
- Avoid global mutable state unless it is a controlled cache.
- Use environment variables for secrets and runtime config.

## Secrets and environment rules

- Never commit real secrets, API keys, tokens, database URLs, or private credentials.
- Never hardcode secrets in source, docs, screenshots, or logs.
- Keep `.env` and `.env.local` out of version control.
- Commit `.env.example` with placeholder values only.
- Redact secrets before sharing debug output or implementation logs.
- If a command or tool output exposes a secret, stop and replace it before continuing.

## Documentation rules

Maintain these files:

- `README.md` for public project explanation.
- `PROJECT_CONTEXT.md` for AI handoff context.
- `DEVELOPMENT_WORKFLOW.md` for phase plan.
- `IMPLEMENTATION_LOG.md` for implementation and debugging history.
- `PROJECT_RULES.md` for architecture and scope boundaries.

Whenever a major decision changes, update the relevant file.
