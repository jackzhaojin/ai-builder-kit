---
name: ai-knowledge-harvester
description: "Harvests AI documentation into a centralized private knowledge repo using a project-first taxonomy. Two modes: (1) Repo scan - collects AI docs (specs, prompt logs, CLAUDE.md files, gap analyses, kickoff prompts, agent configs) from a source repo. (2) Ad-hoc ingest - captures pasted content exported from ChatGPT, Claude web, Clo.ai, or any AI interface. Triggers on phrases like 'harvest AI docs from', 'move my AI docs to', 'collect my prompt logs', 'sync AI docs to knowledge repo', 'organize my ai-docs folder', 'save this conversation', 'store this export', 'add this to my knowledge repo', or any request to consolidate AI documentation across repositories and AI tools into a single searchable private store. Also trigger when the user pastes a large markdown block that looks like an AI conversation export or asks to file away content from an AI session."
---

# AI Knowledge Harvester

Collect AI documentation into a centralized private `ai-knowledge` repository. Two modes,
same output: classified, frontmattered markdown in a project-first taxonomy.

## Capabilities

| Capability | Description |
|------------|-------------|
| **Repo scan** | Scan a source repo for AI docs (CLAUDE.md, specs, prompt logs, gap analyses, kickoff prompts) and copy them into the knowledge repo |
| **Ad-hoc ingest** | Capture pasted content from ChatGPT, Claude web, Clo.ai, Copilot, or any AI tool and file it into the knowledge repo |
| **Auto-classify** | Classify documents as `spec`, `prompt-log`, or `working-doc` based on content signals |
| **Frontmatter** | Add standardized YAML frontmatter to every document for future indexing |
| **README manifests** | Create/update README.md at each folder level (1 level deep only) for discoverability |
| **Safe staging** | Stage changes for review — never commit or push automatically |

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `source_repo` | Mode 1 only | — | Path to the repo with AI docs |
| `knowledge_repo` | No | `{source_repo}/../ai-knowledge` | Path to the private ai-knowledge repo |
| `project_name` | No | GitHub remote repo name (Mode 1) or ask user (Mode 2) | Project name in the taxonomy |

For Mode 2 (ad-hoc), also determine `doc_type`, `title`, `source_tool`, and `why_private`
from content or by asking the user. See [references/ad-hoc-ingest.md](references/ad-hoc-ingest.md).

## Document Types

| Type | Folder | Signals |
|------|--------|---------|
| `spec` | `specs/` | "specification", "requirements", "architecture", "decisions" — stable reference docs |
| `prompt-log` | `prompt-logs/` | Session transcripts, "→ Response / → Action" patterns, conversation exports |
| `working-doc` | `working-docs/` | Gap analyses, kickoff prompts, CLAUDE.md, AGENTS.md, operational guides. **Default when uncertain.** |

## Taxonomy Overview

```
ai-knowledge/
├── README.md                        # Repo purpose + list of projects
├── projects/
│   ├── README.md                    # All projects with one-line descriptions
│   └── {project-name}/
│       ├── README.md                # Project overview, why private, type folder list
│       ├── specs/
│       │   ├── README.md            # List of spec files
│       │   └── YYYY-MM-DD-{slug}.md
│       ├── prompt-logs/
│       │   ├── README.md            # List of prompt log files
│       │   └── YYYY-MM-DD-{slug}.md
│       └── working-docs/
│           ├── README.md            # List of working doc files
│           └── YYYY-MM-DD-{slug}.md
└── shared/
    ├── README.md
    └── skills/
        └── README.md
```

Each README describes its folder's purpose and lists immediate children only — never recurses deeper.
For full README templates and frontmatter spec, see [references/taxonomy.md](references/taxonomy.md).

## Core Workflow

### Mode 1: Repo Scan

1. Validate `source_repo` and `knowledge_repo` paths exist
2. Discover AI docs in source repo — present classified list to user, wait for confirmation
3. Create project folder structure in knowledge repo
4. Create/update README.md files at each level (1 level deep)
5. Copy each file, prepend frontmatter, write to correct type folder
6. Stage changes, show user the diff command — **stop before committing**

For detailed steps, scan patterns, and exclusion rules:
see [references/repo-scan.md](references/repo-scan.md).

### Mode 2: Ad-Hoc Ingest

1. Read pasted content — detect source tool, classify type, identify project
2. **Ask the user** if project, type, or title is ambiguous — don't guess
3. Clean up formatting, prepend frontmatter with `source_tool` field
4. Write to correct type folder, update READMEs, stage — **stop before committing**

For detailed steps, source detection hints, and example interactions:
see [references/ad-hoc-ingest.md](references/ad-hoc-ingest.md).

## Edge Cases

| Situation | Action |
|-----------|--------|
| File already exists in destination | Compare dates — newer overwrites (with note), older skips |
| Ambiguous file type | Default to `working-doc`, tell the user |
| Monorepo with sub-projects | Ask: one project or separate projects? |
| Multiple docs on same date | Use sequence numbers in filename (`01`, `02`) to preserve chronological order |
| No git history for date | Use today's date, add `date_note` in frontmatter |
| Binary files / images / PDFs | Skip, mention them, ask if user wants to handle separately |
| Pasted content with no context | Ask project and type — don't assume |
| Mixed-topic paste | Ask: file as one doc or split? |
| Non-markdown paste | Convert to clean markdown, preserve substance |
| "Save this conversation" | Summarize current session as prompt-log or working-doc, ask project |

## Safety Rules

- **Never push.** Never commit automatically. Always stop at staging.
- **Never modify source files.** Read-only access to source repos.
- **Never silently overwrite.** Report every file action.
- **Ask when uncertain.** Project, type, and title must be confirmed when ambiguous.

## Why This Skill Exists

For the design rationale — why GitHub+markdown over Notion/CosmosDB, why project-first
taxonomy, the open source philosophy, and what comes next — see [references/spirit.md](references/spirit.md).
