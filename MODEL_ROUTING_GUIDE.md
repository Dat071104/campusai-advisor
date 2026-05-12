# Model Routing Guide

Use this guide when choosing a model in Cursor or VS Code.

## General rule

Use the strongest reasoning model for architecture, debugging, and cross-file refactors. Use faster models for boilerplate, copy, README edits, and small UI changes.

## Recommended routing

| Task type | Recommended model type | Notes |
|---|---|---|
| Architecture planning | strongest reasoning / x-high | Ask it to compare tradeoffs before coding. |
| RAG pipeline design | strong reasoning | Retrieval, citations, chunking, and LLM calls need careful boundaries. |
| Weird bugs | strongest reasoning / x-high | Use zone-brain first if Python codebase is non-trivial. |
| Cross-file refactor | strongest reasoning | Require a file-change plan first. |
| UI polish | strong frontend/creative model | Use `skills/campusai-ui/SKILL.md`. |
| Boilerplate | fast/medium model | Keep scope narrow. |
| README/docs | fast/medium model | Ask for concise project-specific writing. |
| Test generation | medium/strong reasoning | Focus on behavior, not brittle implementation details. |

## Prompt for strong reasoning models

```text
Read AGENTS.md, PROJECT_RULES.md, PROJECT_CONTEXT.md, DEVELOPMENT_WORKFLOW.md, and IMPLEMENTATION_LOG.md first.

You may choose implementation details and install libraries if justified. Keep the MVP scope. Do not change architecture direction without explaining the tradeoff first. Prefer incremental, testable implementation over massive rewrites.

Before editing code, give:
1. the current phase,
2. the files you expect to touch,
3. the verification command you will run.
```

## Prompt for fast models

```text
Do only the requested small edit. Do not refactor unrelated code. Do not add dependencies. Preserve existing behavior. Update IMPLEMENTATION_LOG.md only if the edit changes implementation behavior or fixes a bug.
```

## Cursor and Codex handoff

Use Cursor for local editing, file operations, and quick iteration inside the workspace.
Use Codex-style reasoning for deep planning, architecture review, hard debugging, and cross-file analysis.

Keep handoffs simple:

- Cursor reads the docs, edits the files, and runs local verification.
- Codex-style reasoning produces the plan, identifies risks, and suggests the smallest safe change.
- If the task expands beyond the current plan, re-audit before continuing.

## When to switch models

Switch to a stronger reasoning model when:

```text
- the same bug fails twice,
- the change touches more than 5 files,
- architecture boundaries are unclear,
- retrieval/citation correctness is involved,
- deployment errors are vague,
- the model starts guessing.
```

Switch to a faster model when:

```text
- only copy/text is changing,
- a single UI component is being polished,
- README formatting is being updated,
- a simple test needs to be added.
```
