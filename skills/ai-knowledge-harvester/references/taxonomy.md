# Taxonomy — Folder Structure, READMEs, and Frontmatter

## Table of Contents

- [Two-tier folder structure](#two-tier-folder-structure)
- [README templates](#readme-templates)
- [YAML frontmatter spec](#yaml-frontmatter-spec)
- [File size guidance](#file-size-guidance)

---

## Two-tier folder structure

The primary key is always the **GitHub repo name**. Within it, a second tier for sub-projects.

- **Simple repo**: repeat the repo name — `{repo}/{repo}/`
- **Monorepo**: one folder per sub-project — `{repo}/{sub-project}/`

```
ai-knowledge/
├── README.md
├── projects/
│   ├── README.md
│   ├── {github-repo}/                     # Tier 1: GitHub repo name (always)
│   │   ├── README.md                      # Repo overview, sub-project list
│   │   └── {sub-project}/                # Tier 2: sub-project or repo name repeated
│   │       ├── README.md                  # Sub-project overview, type folders
│   │       ├── specs/
│   │       │   ├── README.md
│   │       │   └── YYYY-MM-DD-{seq}-{slug}.md
│   │       ├── prompt-logs/
│   │       │   ├── README.md
│   │       │   └── YYYY-MM-DD-{seq}-{slug}.md
│   │       ├── working-docs/
│   │       │   ├── README.md
│   │       │   └── YYYY-MM-DD-{seq}-{slug}.md
│   │       └── harness-prompts/           # Optional — only when harness prompts exist
│   │           ├── README.md
│   │           └── YYYY-MM-DD-{seq}-{slug}.md
│   └── {another-repo}/
│       └── {another-repo}/               # Simple repo: name repeated
└── shared/
    ├── README.md
    └── skills/
```

Every README describes its folder and lists immediate children only. Never recurse deeper.
When updating READMEs, append new entries — never remove existing ones.
Only create type folders and their READMEs when documents exist for that type.

---

## README templates

### Root README (`ai-knowledge/README.md`)

```markdown
# AI Knowledge

Private repository for AI documentation — specs, prompt logs, and working docs
collected from across all projects.

## Structure

- `projects/` — AI docs organized by GitHub repo, then sub-project
- `shared/` — Cross-project resources (skills, templates)
```

### Projects README (`projects/README.md`)

```markdown
# Projects

| Repo | Description |
|------|-------------|
| [{github-repo}](./{github-repo}/) | {one-line description} |
```

### Repo README (`projects/{github-repo}/README.md`)

This is the **Tier 1** README. Lists sub-projects and repo-level context.

```markdown
# {github-repo}

{one-line description of the repo}

## Why Private

{one sentence: what makes this private}

## Sub-Projects

| Sub-Project | Description |
|-------------|-------------|
| [{sub-project}](./{sub-project}/) | {one-line description} |

## Open Source Candidate?

{yes/no and why}
```

### Sub-Project README (`projects/{github-repo}/{sub-project}/README.md`)

This is the **Tier 2** README. Lists type folders and harvest history.

```markdown
# {sub-project}

{one-line description}

## Harvest Log

| Date | Documents Added | Source |
|------|----------------|--------|
| YYYY-MM-DD | {N} specs, {N} prompt-logs, {N} working-docs | {source} |

## Contents

Only list type folders that contain documents. Do not list empty folders.

- `specs/` — Stable reference documents ({N} files)
- `prompt-logs/` — Session transcripts ({N} files)
- `working-docs/` — Living documents ({N} files)
- `harness-prompts/` — AI/agent prompt templates ({N} files)
```

### Type folder READMEs

Only create when the folder contains documents.

**Documents must be listed in chronological order.** This is critical for prompt logs
where the sequence of sessions tells a story (e.g., a design chat precedes the build session).
Include the `Source` column so readers can tell at a glance where each document came from.

```markdown
# {Type Name}

{One sentence description}

## Documents

| # | Date | Title | Source | Status |
|---|------|-------|--------|--------|
| 1 | YYYY-MM-DD | [{title}](./{filename}) | claude-web | stable |
| 2 | YYYY-MM-DD | [{title}](./{filename}) | claude-code | stable |
```

Type descriptions:
- **Specs**: Stable reference documents written once and consumed by agents at task start.
- **Prompt Logs**: Session transcripts — append-only, chronological records of AI interactions.
- **Working Docs**: Living documents that evolve over time — gap analyses, kickoff prompts, operational guides.
- **Harness Prompts**: AI-generated prompt templates, agent configurations, harness prompt files. Secondary priority — harvest but deprioritize vs human-authored docs.

---

## YAML frontmatter spec

Every harvested document carries this frontmatter:

```yaml
---
title: {from first # heading, or filename if no heading}
project: {github-repo}
sub_project: {sub-project name}
type: spec | prompt-log | working-doc | harness-prompt
date: YYYY-MM-DD
tags: []
why_private: {one phrase — e.g., "contains unpublished architecture decisions"}
status: stable | active | archived
source_repo: {github URL or local path — "n/a" for ad-hoc ingests}
source_tool: {always include: claude-code | claude-web | chatgpt | clo-ai | copilot | other}
duplicate: {true only for CLAUDE.md/AGENTS.md — source file must remain in place. Omit otherwise.}
harvested: YYYY-MM-DD
---
```

### Field notes

| Field | Mode 1 (Repo Scan) | Mode 2 (Ad-Hoc Ingest) |
|-------|---------------------|------------------------|
| `project` | GitHub remote repo name | Ask |
| `sub_project` | Detected sub-project or same as project | Ask |
| `source_repo` | GitHub URL or local path | `n/a` |
| `source_tool` | Detect or ask — always include | Detect or ask — always include |
| `date` | Git commit date (`git log -1 --format="%as"`) or today | Today's date |
| `date_note` | Add if no git history: `"no git history — using harvest date"` | Not needed |
| `status` | Infer: specs → `stable`, prompt-logs → `stable`, working-docs → `active` | Ask or infer |

### Filename format

`YYYY-MM-DD-{seq}-{slug}.md`

- `YYYY-MM-DD` — git commit date when available, otherwise today's date
- `{seq}` — two-digit sequence number for chronological ordering within the same date
- `{slug}` — from original filename (kebab-cased) or derived from title for ad-hoc ingests

---

## File size guidance

- **Markdown files up to 50MB**: Harvest them. Storage is free. Large prompt logs, summaries, and specs are all fine.
- **Files over 50MB**: Skip and mention to user.
- **Binary files, images, PDFs**: Skip by default, mention they were found.
