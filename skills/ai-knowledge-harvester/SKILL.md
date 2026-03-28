---
name: ai-knowledge-harvester
description: "Harvests AI documentation into a centralized private knowledge repo using a project-first taxonomy. Two modes: (1) Repo scan - collects AI docs (specs, prompt logs, CLAUDE.md files, gap analyses, kickoff prompts, agent configs) from a source repo. (2) Ad-hoc ingest - captures pasted content exported from ChatGPT, Claude web, Clo.ai, or any AI interface. Triggers on phrases like 'harvest AI docs from', 'move my AI docs to', 'collect my prompt logs', 'sync AI docs to knowledge repo', 'organize my ai-docs folder', 'save this conversation', 'store this export', 'add this to my knowledge repo', or any request to consolidate AI documentation across repositories and AI tools into a single searchable private store. Also trigger when the user pastes a large markdown block that looks like an AI conversation export or asks to file away content from an AI session."
---

# AI Knowledge Harvester

Collect AI documentation into a centralized private `ai-knowledge` repository. Two modes,
same output: classified, frontmattered markdown in a two-tier project taxonomy.

## Capabilities

| Capability | Description |
|------------|-------------|
| **Repo scan** | Scan a source repo for AI docs (CLAUDE.md, specs, prompt logs, gap analyses, kickoff prompts) and copy them into the knowledge repo |
| **Ad-hoc ingest** | Capture pasted content from ChatGPT, Claude web, Clo.ai, Copilot, or any AI tool and file it into the knowledge repo |
| **Monorepo support** | Two-tier taxonomy: `{github-repo}/{sub-project}` — handles monorepos and simple repos alike |
| **Auto-classify** | Classify documents as `spec`, `prompt-log`, `working-doc`, or `harness-prompt` based on content signals |
| **Frontmatter** | Add standardized YAML frontmatter to every document for future indexing |
| **README manifests** | Create/update README.md at each folder level (1 level deep only) for discoverability |
| **Safe staging** | Stage changes for review — never commit or push automatically |

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `source_repo` | Mode 1 only | — | Path to the repo with AI docs |
| `knowledge_repo` | No | `{source_repo}/../ai-knowledge` | Path to the private ai-knowledge repo |
| `project_name` | No | GitHub remote repo name | Top-level project (the GitHub repo name) |
| `sub_project` | No | Same as `project_name` for simple repos, or detected sub-project name for monorepos | Second tier in taxonomy |

For Mode 2 (ad-hoc), also determine `doc_type`, `title`, `source_tool`, and `why_private`
from content or by asking the user. See [references/ad-hoc-ingest.md](references/ad-hoc-ingest.md).

## Document Types

| Type | Folder | Priority | Signals |
|------|--------|----------|---------|
| `spec` | `specs/` | Primary | "specification", "requirements", "architecture", "decisions" — stable reference docs |
| `prompt-log` | `prompt-logs/` | Primary | Session transcripts, conversation exports, "→ Response / → Action" patterns |
| `working-doc` | `working-docs/` | Primary | Gap analyses, kickoff prompts, CLAUDE.md, AGENTS.md, operational guides. **Default when uncertain.** |
| `harness-prompt` | `harness-prompts/` | Secondary | AI-generated prompts, agent configuration templates, harness prompt files in `src/prompts/`. Optional — harvest but deprioritize. |

## Two-Tier Taxonomy

The primary key is always the **GitHub repo name**. Within it, a second tier for sub-projects.

- **Simple repo**: `{repo}/{repo}/` — repeat the name (e.g., `ai-builder-kit/ai-knowledge-harvester/`)
- **Monorepo**: `{repo}/{sub-project}/` — one folder per sub-project (e.g., `jack-dev-server-configs/generic-harness-v1/`)

```
ai-knowledge/
├── README.md
├── projects/
│   ├── README.md
│   ├── {github-repo}/                    # Top tier: GitHub repo name
│   │   ├── README.md                     # Repo overview, why private, sub-project list
│   │   └── {sub-project}/               # Second tier: sub-project (or repo name repeated)
│   │       ├── README.md                 # Sub-project overview, type folder list
│   │       ├── specs/
│   │       │   ├── README.md
│   │       │   └── YYYY-MM-DD-{seq}-{slug}.md
│   │       ├── prompt-logs/
│   │       │   ├── README.md
│   │       │   └── YYYY-MM-DD-{seq}-{slug}.md
│   │       ├── working-docs/
│   │       │   ├── README.md
│   │       │   └── YYYY-MM-DD-{seq}-{slug}.md
│   │       └── harness-prompts/          # Optional — only if harness prompts exist
│   │           ├── README.md
│   │           └── YYYY-MM-DD-{seq}-{slug}.md
│   └── {another-repo}/
│       └── ...
└── shared/
    ├── README.md
    └── skills/
```

Each README describes its folder's purpose and lists immediate children only — never recurses deeper.
For full README templates and frontmatter spec, see [references/taxonomy.md](references/taxonomy.md).

## Core Workflow

### Mode 1: Repo Scan

1. Validate `source_repo` and `knowledge_repo` paths exist
2. Determine project name from GitHub remote, detect sub-projects (monorepo or simple)
3. Discover AI docs — scan `ai-docs/`, `local-ai-docs/`, `local-only/`, `local/`, nested subdirectories
4. Present classified list to user, wait for confirmation
5. Create project folder structure, write files with frontmatter
6. Create/update README.md files at each level (1 level deep)
7. Stage changes, show user the diff command — **stop before committing**
8. After user commits harvest, offer to clean up source files (optional, separate commit)

For detailed steps, scan patterns, and exclusion rules:
see [references/repo-scan.md](references/repo-scan.md).

### Mode 2: Ad-Hoc Ingest

1. Read pasted content — detect source tool, classify type, identify project + sub-project
2. **Ask the user** if project, sub-project, type, or title is ambiguous — don't guess
3. Clean up formatting, prepend frontmatter with `source_tool` field
4. Write to correct type folder, update READMEs, stage — **stop before committing**

For detailed steps, source detection hints, and example interactions:
see [references/ad-hoc-ingest.md](references/ad-hoc-ingest.md).

## Edge Cases

| Situation | Action |
|-----------|--------|
| File already exists in destination | Compare dates — newer overwrites (with note), older skips |
| Ambiguous file type | Default to `working-doc`, tell the user |
| Monorepo with sub-projects | Use two-tier: `{repo}/{sub-project}/` — detect sub-projects from directory structure |
| Simple repo (not a monorepo) | Repeat repo name: `{repo}/{repo}/` |
| Multiple docs on same date | Use sequence numbers in filename (`01`, `02`) to preserve chronological order |
| No git history for date | Use today's date, add `date_note` in frontmatter |
| Large markdown files (up to 50MB) | Harvest them — storage is free. Only skip files >50MB |
| Binary files / images / PDFs | Skip, mention them, ask if user wants to handle separately |
| Pasted content with no context | Ask project and type — don't assume |
| Mixed-topic paste | Ask: file as one doc or split? |
| Non-markdown paste | Convert to clean markdown, preserve substance |
| "Save this conversation" | Summarize current session as prompt-log or working-doc, ask project |
| `local-ai-docs/` found in repo | Harvest everything in it — this folder exists specifically for AI docs awaiting harvest. Recommend adding to `.gitignore` if not already ignored |

## Safety Rules

- **Never push.** Never commit automatically. Always stop at staging.
- **Never modify source files during harvest.** Read-only access to source repos during harvest.
- **Cleanup is separate.** Only offer source file deletion after harvest is committed. Stage deletions as a separate commit in the source repo. Never push.
- **Never silently overwrite.** Report every file action.
- **Ask when uncertain.** Project, type, and title must be confirmed when ambiguous.

## Why This Skill Exists

For the design rationale — why GitHub+markdown over Notion/CosmosDB, why project-first
taxonomy, the open source philosophy, and what comes next — see [references/spirit.md](references/spirit.md).
