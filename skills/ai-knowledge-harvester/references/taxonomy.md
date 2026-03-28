# Taxonomy — Folder Structure, READMEs, and Frontmatter

## Table of Contents

- [Folder structure](#folder-structure)
- [README templates](#readme-templates)
- [YAML frontmatter spec](#yaml-frontmatter-spec)

---

## Folder structure

```
ai-knowledge/
├── README.md
├── projects/
│   ├── README.md
│   └── {project-name}/
│       ├── README.md
│       ├── specs/
│       │   ├── README.md
│       │   └── YYYY-MM-DD-{slug}.md
│       ├── prompt-logs/
│       │   ├── README.md
│       │   └── YYYY-MM-DD-{slug}.md
│       └── working-docs/
│           ├── README.md
│           └── YYYY-MM-DD-{slug}.md
└── shared/
    ├── README.md
    └── skills/
        └── README.md
```

Every README describes its folder and lists immediate children only. Never recurse deeper.
When updating READMEs, append new entries — never remove existing ones.

---

## README templates

### Root README (`ai-knowledge/README.md`)

```markdown
# AI Knowledge

Private repository for AI documentation — specs, prompt logs, and working docs
collected from across all projects.

## Structure

- `projects/` — AI docs organized by project
- `shared/` — Cross-project resources (skills, templates)
```

### Projects README (`projects/README.md`)

```markdown
# Projects

| Project | Description |
|---------|-------------|
| [{project-name}](./{project-name}/) | {one-line description} |
```

### Project README (`projects/{project-name}/README.md`)

Ask the user for a one-line description and why this project is private.
If they say "just use a placeholder," infer from the source files.

```markdown
# {project-name}

{one-line description of the project}

## Why Private

{one sentence: what makes this private — unpublished architecture, internal tooling, credentials, etc.}

## Contents

- `specs/` — Stable reference documents ({N} files)
- `prompt-logs/` — Session transcripts ({N} files)
- `working-docs/` — Living documents ({N} files)

## Open Source Candidate?

{yes/no and why — is there a version that could be open sourced?}
```

### Type folder READMEs (`specs/README.md`, `prompt-logs/README.md`, `working-docs/README.md`)

```markdown
# {Type Name}

{One sentence: e.g., "Stable reference documents written once and consumed by agents at task start."}

## Documents

| Date | Title | Status |
|------|-------|--------|
| YYYY-MM-DD | [{title}](./{filename}) | {status} |
```

Type descriptions:
- **Specs**: Stable reference documents written once and consumed by agents at task start.
- **Prompt Logs**: Session transcripts — append-only, chronological records of AI interactions.
- **Working Docs**: Living documents that evolve over time — gap analyses, kickoff prompts, operational guides.

---

## YAML frontmatter spec

Every harvested document carries this frontmatter:

```yaml
---
title: {from first # heading, or filename if no heading}
project: {project_name}
type: spec | prompt-log | working-doc
date: YYYY-MM-DD
tags: []
why_private: {one phrase — e.g., "contains unpublished architecture decisions"}
status: stable | active | archived
source_repo: {github URL or local path — "n/a" for ad-hoc ingests}
source_tool: {ad-hoc only: chatgpt | claude-web | clo-ai | copilot | other}
harvested: YYYY-MM-DD
---
```

### Field notes

| Field | Mode 1 (Repo Scan) | Mode 2 (Ad-Hoc Ingest) |
|-------|---------------------|------------------------|
| `source_repo` | GitHub URL or local path | `n/a` |
| `source_tool` | Omit | Required — detect or ask |
| `date` | Git commit date (`git log -1 --format="%as"`) or today | Today's date |
| `date_note` | Add if no git history: `"no git history — using harvest date"` | Not needed |
| `status` | Infer: specs → `stable`, prompt-logs → `stable`, working-docs → `active` | Ask or infer |

### Filename format

`YYYY-MM-DD-{slug}.md`

- Use git commit date when available, otherwise today's date
- Slug from original filename, kebab-cased
- For ad-hoc ingests, derive slug from title
