# Project Context

## User context

The project owner is a Computer Science student in Vietnam aiming for Backend + AI Integration roles. The project is intended as a polished portfolio project for internship/fresher applications.

The project should show practical ability in:

- backend architecture
- RAG pipelines
- document processing
- LLM integration
- vector search
- user-facing web demo
- deployment readiness
- clean technical storytelling

## Product concept

`CampusAI Advisor` is an AI academic advising web app for university students.

Students can ask questions such as:

- What courses should I take next semester if I want to become an AI Engineer?
- What prerequisites do I need before Machine Learning?
- What does the academic policy say about graduation requirements?
- Summarize this syllabus.
- Based on my completed courses, should I focus on Backend, AI, Data, or Security?

The product should combine:

1. RAG document Q&A
2. Student profile context
3. Study/career advising
4. Citation-based answers
5. Simple web UI

## MVP positioning

The MVP is not a full university system. It is a portfolio-grade demo proving the owner can build a real AI-backed product.

The demo must be understandable to recruiters:

```text
I built a university-focused AI academic advising assistant using RAG. It ingests academic documents, chunks and embeds them, retrieves relevant context, generates grounded answers with citations, and personalizes advice based on the student's profile.
```

## Current intended stack

MVP stack:

```text
Python
Streamlit as the default MVP UI
Groq API for chat generation
OpenAI-compatible client for Groq
FastEmbed or local embeddings
ChromaDB or local vector store
PyMuPDF for PDF extraction
pytest / ruff for basic quality
```

V2 stack, when the MVP works:

```text
Next.js + TypeScript + Tailwind
FastAPI backend
PostgreSQL + pgvector
Redis + Celery/RQ workers
Supabase or managed Postgres
Vercel + Render/Fly/Railway deployment
```

## Key constraint

The current goal is a 3-day MVP. The agent should not build an enterprise platform while pretending that complexity is ambition. Humans do this enough already.

## Required behavior

The AI system must:

- Answer in Vietnamese or English depending on the UI/user setting.
- Cite sources when answering from documents.
- Say when evidence is missing.
- Personalize advice using student profile fields.
- Keep general career advice separate from document-backed policy claims.

## Main demo story

1. Open the web app.
2. Fill student profile: Computer Science, year 2, interested in Backend + AI.
3. Upload curriculum, syllabus, or academic policy documents.
4. Index documents.
5. Ask: "What should I study next semester if I want to become an AI Engineer?"
6. Show answer with profile-aware advice and source citations.
7. Ask: "What prerequisite knowledge do I need before Machine Learning?"
8. Show cited answer from document chunks.
9. Show README architecture and clean GitHub repo.

## CV summary

Suggested CV bullet:

```text
Built CampusAI Advisor, a university-focused RAG academic advising web app using Python, Groq, local embeddings, and vector search. Implemented document ingestion, chunking, semantic retrieval, source citations, student-profile-aware recommendations, and a deployable web demo.
```
