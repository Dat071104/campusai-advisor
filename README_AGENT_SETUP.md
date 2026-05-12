# Agent Setup Pack

This folder is meant to be extracted directly into the root of a new CampusAI Advisor project.

## Included files

```text
AGENTS.md
PROJECT_RULES.md
PROJECT_CONTEXT.md
DEVELOPMENT_WORKFLOW.md
IMPLEMENTATION_LOG.md
MODEL_ROUTING_GUIDE.md
README_AGENT_SETUP.md
.cursor/rules/000-campusai-core.mdc
.cursor/rules/010-zone-brain-python.mdc
.cursor/rules/020-campusai-ui.mdc
skills/zone-brain/SKILL.md
skills/campusai-ui/SKILL.md
scripts/scan_deps.py
```

## First Cursor prompt

Use this before coding:

```text
Read AGENTS.md, PROJECT_RULES.md, PROJECT_CONTEXT.md, DEVELOPMENT_WORKFLOW.md, IMPLEMENTATION_LOG.md, and MODEL_ROUTING_GUIDE.md. Summarize the project, current constraints, and the safest first implementation step. Do not write code yet.
```

## Root-ready extraction

Extract this pack into an empty root folder, then start coding inside that same folder.

Recommended root shape after extraction:

```text
campus-ai-advisor/
  AGENTS.md
  PROJECT_RULES.md
  PROJECT_CONTEXT.md
  DEVELOPMENT_WORKFLOW.md
  IMPLEMENTATION_LOG.md
  MODEL_ROUTING_GUIDE.md
  README_AGENT_SETUP.md
  .cursor/
  skills/
  scripts/
```

After project code is generated, add your normal app folders:

```text
campus-ai-advisor/
  app/ or src/
  data/
  tests/
  README.md
  pyproject.toml or package.json
```
