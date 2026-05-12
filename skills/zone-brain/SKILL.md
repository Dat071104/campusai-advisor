---
name: zone-brain
description: "python codebase navigation and debugging workflow for CampusAI. Use when working on Python files, debugging, refactoring, tracing imports, finding affected files, or deciding which files to read before editing. It combines a markdown workflow with scripts/scan_deps.py to generate .zone_context.md from dependency analysis. Do not use for simple README edits or non-Python-only UI copy changes."
---

# Zone Brain

Use this local skill to avoid reading the whole codebase when debugging or refactoring Python.

The paired script is:

```text
scripts/scan_deps.py
```

This skill is only complete when both files exist:

```text
skills/zone-brain/SKILL.md
scripts/scan_deps.py
```

The markdown tells the agent what to do. The Python script performs the dependency scan. Yes, both are needed. Apparently even automation needs organs.

## When to use

Use Zone Brain when:

- Debugging Python modules.
- Refactoring Python modules.
- Tracing RAG pipeline behavior.
- Finding affected files for a change.
- Fixing retrieval, embeddings, chunking, ingestion, Groq client, settings, or citation logic.
- The project has more than 10 Python files and the relevant files are not obvious.

Do not use Zone Brain for:

- README edits.
- Project planning.
- UI copy changes.
- One-file edits where the target file is obvious.
- Pure TypeScript/Next.js debugging. This script only traces Python imports.

## Workflow

### Step 1: Pick a seed

Choose keywords related to the task.

Examples:

| Task | Seed |
|---|---|
| Upload bug | `upload,document,ingest` |
| Retrieval bug | `retriever,vector,search` |
| Chunking bug | `chunk,split,document` |
| Groq error | `groq,llm,client,chain` |
| Citation bug | `citation,source,chunk` |
| Settings bug | `settings,config,env` |
| UI calls Python services | `ui,streamlit,app` |
| Advisor logic | `advisor,profile,recommendation` |

### Step 2: Run dependency scan

Run from project root:

```bash
python scripts/scan_deps.py --root . --seed "retriever,vector,search" --hops 2 --output context
```

Use `--hops 2` by default.

Use `--hops 1` for narrow bugs.

Use `--hops 3` for interface refactors or unclear data flow.

### Step 3: Read generated context

The script writes:

```text
.zone_context.md
```

Attach or read this file before editing:

```text
@.zone_context.md
```

The file includes:

- seed files,
- affected zone size,
- dependency read order,
- relevant file contents.

### Step 4: Edit only the affected zone

Do not randomly open the whole repo. Work inside the zone unless there is clear evidence that a missing file matters.

If additional files are needed, explain why.

### Step 5: Verify

Run the smallest useful verification command:

```bash
pytest
ruff check .
python -m <module>
streamlit run <app_file>
```

Use commands that actually apply to the project.

### Step 6: Update project memory

Append to:

```text
IMPLEMENTATION_LOG.md
```

Record:

- seed used,
- zone size,
- files changed,
- error/root cause,
- verification result,
- next step.

## Output requirements

When reporting back, include:

```text
Zone seed: ...
Zone size: X files
Files changed: ...
Verification: ...
Log updated: yes/no
```

## Limitations

The script traces Python imports using AST and simple fallback parsing.

It does not fully handle:

- dynamic imports,
- config-only dependencies,
- environment variable dependencies,
- frontend TypeScript imports,
- runtime-only Streamlit state,
- notebooks.

If a bug is clearly caused by config or UI, include those files manually.
