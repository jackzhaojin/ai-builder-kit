# Conversation Context: The Design Session

**Date:** 2026-03-28
**Participants:** Jack (human), Claude (AI)
**Purpose:** Designing a private AI knowledge repository and the skill to populate it

---

## Key Decisions Made

| Decision | Chosen | Rejected | Why |
|----------|--------|----------|-----|
| Storage backend | GitHub private repo + Markdown | Notion, Cosmos DB, Airtable | Zero impedance mismatch with markdown, agent-native via git, free human browsing, no lock-in |
| Cloud agent auth | Fine-grained PAT in .env | GitHub OIDC | OIDC is for human login flows; PAT is simpler for machine-to-machine |
| Folder taxonomy | Project-first | Chronological-first, Type-first | Projects are the most durable taxonomy; outlive date schemes and type classifications |
| Index strategy | No central index; folder IS taxonomy | manifest.yaml, auto-generated index | Avoids constant maintenance of a shared file; frontmatter enables future index generation |
| Push behavior | Stage only, never push | Auto-push | Human reviews before any remote changes |
| Document types | specs / prompt-logs / working-docs | Single flat bucket | Different shapes, different retrieval patterns, different staleness curves |

---

## The Real Files That Informed the Design

From the ciam-demo project, Jack shared:

- `prompt-log-0-pre-execution-doc-alignment.md` — pre-build documentation session
- `prompt-log-2-private-repo-refactor.md` — public/private repo split session  
- `spring-boot-claims-spec.md` — Spring Boot backend spec with AI agent instructions
- `claude-gap.md` — spec vs implementation gap analysis
- `claude-code-kickoff-prompt.md` — agent team kickoff instructions
- `PUBLIC-MIRROR-INSTRUCTIONS.md` — mirror script documentation

These revealed three distinct document types with different usage patterns:
- **Specs**: stable, consumed at task start, rarely updated
- **Prompt logs**: append-only transcripts with consistent `→ Response / → Action` format
- **Working docs**: living documents that evolve (gap analysis, kickoff prompts)

---

## The Final Folder Structure

```
ai-knowledge/                          # Private GitHub repo
├── projects/
│   └── {project-name}/
│       ├── why-private.md             # Why this isn't open source
│       ├── specs/
│       │   └── YYYY-MM-DD-{name}.md
│       ├── prompt-logs/
│       │   └── YYYY-MM-DD-{name}.md
│       └── working-docs/
│           └── YYYY-MM-DD-{name}.md
└── shared/
    └── skills/
        └── {skill-name}/
```

---

## YAML Frontmatter Standard

Every document carries:

```yaml
---
title: Human-readable title
project: project-name
type: spec | prompt-log | working-doc
date: YYYY-MM-DD
tags: [relevant, tags]
why_private: one sentence explanation
status: stable | active | archived
source_repo: github.com/jackzhaojin/{repo-name}
---
```

---

## What This Enables Later

1. **Requirement 1 (now)**: Agent working on a task reads relevant context from the knowledge repo
   at task start. Fetches by project name, filters by type.

2. **Requirement 2 (future)**: Pattern mining across prompt logs to identify what prompting
   approaches work, extract reusable patterns, generate new skills. The consistent
   `→ Response / → Action` format in prompt logs is already structured enough for this.

---

## Quotes Worth Preserving

> "Ideally I still think that I want an index somehow so that AI can just read the index and
> understand where everything is."
> — Led to the frontmatter-as-index discussion; resolved by making folder structure the taxonomy

> "The nice about GitHub and Markdown documents is that GitHub does render markdown documents
> nicely, so as long as it's maintainable, it's browsable."
> — The moment GitHub won the storage decision

> "I want to kind of clean up all my private repositories and make everything as open source
> as possible... keeping what I think should be private in a centralized way."
> — The open source philosophy that shapes why-private.md

> "Things are evolving so fast."
> — Context for why the design stays simple and deferral of vector search is correct

> "This will be a private repository, right, that we'll be pushing to, but I'll be running
> this in both public and private repository that has AI documentations."
> — Defines the skill's multi-repo, single-destination pattern
