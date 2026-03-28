---
name: ai-knowledge-harvester
description: Harvests AI documentation from any repository and organizes it into a centralized private knowledge repo using a project-first taxonomy. Use this skill when the user wants to collect AI docs (specs, prompt logs, CLAUDE.md files, gap analyses, kickoff prompts, agent configs) from a source repo and move them into their private ai-knowledge repository. Triggers on phrases like "harvest AI docs from", "move my AI docs to", "collect my prompt logs", "sync AI docs to knowledge repo", "organize my ai-docs folder", or any request to consolidate AI documentation across repositories into a single searchable private store. Also trigger when the user mentions they want to keep their AI docs private while open sourcing their code.
---

# AI Knowledge Harvester

Collects AI documentation from a source repository and organizes it into a centralized private
`ai-knowledge` repository using a consistent project-first taxonomy. Stages changes for review
— never pushes automatically.

---

## What This Skill Does

1. Scans a source repository for AI documentation files
2. Determines the project name and classifies each file by type
3. Copies files into the correct taxonomy location in the destination repo
4. Adds or updates YAML frontmatter on each file
5. Creates or updates `README.md` at each folder level (1 level deep manifest)
6. Stages all changes with a descriptive commit message
7. **Stops before pushing** — you review and push manually

---

## Parameters

The user must provide (or you must ask for):

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `source_repo` | Path to the repo with AI docs | *(required)* | `/Users/jackjin/dev/ciam-demo-private` |
| `knowledge_repo` | Path to the private ai-knowledge repo | Sibling folder `ai-knowledge` next to `source_repo` (i.e., `{source_repo}/../ai-knowledge`) | `/Users/jackjin/dev/ai-knowledge` |
| `project_name` | Override project name | Repo folder name | `ciam-demo` |

If `source_repo` is missing, ask before proceeding. Don't guess paths.
For `knowledge_repo`, default to the sibling `ai-knowledge` folder unless the user specifies otherwise. Verify the path exists before proceeding.

---

## The Taxonomy

The destination repo uses this structure. Each folder has a `README.md` that describes its
purpose and lists what's inside — **one level deep only**. The root README lists projects,
each project README lists its type folders, each type folder README lists its documents.
No README recurses deeper than its immediate children.

```
ai-knowledge/
├── README.md                       # Repo purpose + list of projects (1 level deep)
├── projects/
│   ├── README.md                   # Lists all projects with one-line descriptions
│   └── {project-name}/
│       ├── README.md               # Project overview, why private, lists type folders
│       ├── specs/
│       │   ├── README.md           # What specs are + list of spec files
│       │   └── YYYY-MM-DD-{slug}.md
│       ├── prompt-logs/
│       │   ├── README.md           # What prompt logs are + list of log files
│       │   └── YYYY-MM-DD-{slug}.md
│       └── working-docs/
│           ├── README.md           # What working docs are + list of doc files
│           └── YYYY-MM-DD-{slug}.md
└── shared/
    ├── README.md                   # What shared resources are
    └── skills/
        └── README.md               # List of skills
```

### Document Type Classification

Classify each file into one of three types based on content and filename signals:

| Type | Folder | Signals |
|------|--------|---------|
| `spec` | `specs/` | Contains "specification", "spec", "requirements", "architecture", "decisions" in name or content headers. Relatively stable reference docs. |
| `prompt-log` | `prompt-logs/` | Contains "prompt log", "prompt-log", session transcripts with `→ Response` / `→ Action` patterns, timestamped conversation records. |
| `working-doc` | `working-docs/` | Gap analyses, kickoff prompts, CLAUDE.md files, AGENTS.md, operational guides, anything that evolves over time. When in doubt, use this. |

---

## Step-by-Step Execution

### Step 1: Validate inputs

Verify both paths exist before doing anything else:
```bash
ls "{source_repo}"
ls "{knowledge_repo}"
```

If either doesn't exist, stop and tell the user clearly.

### Step 2: Discover AI documents in the source repo

Scan these locations (in priority order — some repos use one, some use all):

```bash
# Primary AI doc locations
find "{source_repo}/ai-docs" -name "*.md" 2>/dev/null
find "{source_repo}" -name "CLAUDE.md" 2>/dev/null
find "{source_repo}" -name "AGENTS.md" 2>/dev/null
find "{source_repo}" -name "claude-gap.md" 2>/dev/null
find "{source_repo}" -name "*prompt-log*" -name "*.md" 2>/dev/null
find "{source_repo}" -name "*spec*.md" 2>/dev/null
find "{source_repo}" -name "*kickoff*" -name "*.md" 2>/dev/null

# Also check for ai-docs in subdirectories (monorepos)
find "{source_repo}" -path "*/ai-docs/*.md" 2>/dev/null
```

Exclude from collection:
- `node_modules/`, `.git/`, `dist/`, `build/`
- Files already in the knowledge repo
- README.md at repo root (that's public documentation)
- `.env` files, lock files, generated files

Present the discovered files to the user as a list before proceeding:
```
Found 7 AI documents in ciam-demo-private:
  [spec]        ai-docs/spring-boot-claims-spec.md
  [spec]        ai-docs/ciam-specification.md
  [spec]        ai-docs/nextjs-claims-app-spec.md
  [prompt-log]  ai-docs/prompt-log-0-pre-execution-doc-alignment.md
  [prompt-log]  ai-docs/prompt-log-2-private-repo-refactor.md
  [working-doc] ai-docs/claude-gap.md
  [working-doc] ai-docs/claude-code-kickoff-prompt.md

Destination: ai-knowledge/projects/ciam-demo/

Proceed? (or adjust any classifications above)
```

Wait for confirmation before copying.

### Step 3: Prepare the destination

Create the project folder structure if it doesn't exist:

```bash
mkdir -p "{knowledge_repo}/projects/{project_name}/specs"
mkdir -p "{knowledge_repo}/projects/{project_name}/prompt-logs"
mkdir -p "{knowledge_repo}/projects/{project_name}/working-docs"
mkdir -p "{knowledge_repo}/shared/skills"
```

### Step 4: Create or update README.md files

Every folder gets a README.md that describes its purpose and lists contents **one level deep only**.
Create missing READMEs; update existing ones by appending new entries (never remove existing entries).

**Root README** (`{knowledge_repo}/README.md`) — create if missing:
```markdown
# AI Knowledge

Private repository for AI documentation — specs, prompt logs, and working docs
collected from across all projects.

## Structure

- `projects/` — AI docs organized by project
- `shared/` — Cross-project resources (skills, templates)
```

**Projects README** (`{knowledge_repo}/projects/README.md`) — create if missing, add new project entry:
```markdown
# Projects

| Project | Description |
|---------|-------------|
| [{project-name}](./{project-name}/) | {one-line description} |
```

**Project README** (`{knowledge_repo}/projects/{project_name}/README.md`) — create if missing.
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

**Type folder READMEs** (`specs/README.md`, `prompt-logs/README.md`, `working-docs/README.md`) — create if missing, update with new file entries:

```markdown
# {Type Name}

{One sentence explaining what this type is — e.g., "Stable reference documents written once and consumed by agents at task start."}

## Documents

| Date | Title | Status |
|------|-------|--------|
| YYYY-MM-DD | [{title}](./{filename}) | {status} |
```

### Step 5: Copy and add frontmatter

For each file:

1. Determine the destination path:
   - Filename format: `YYYY-MM-DD-{original-slug}.md`
   - Use the file's git commit date if available: `git log -1 --format="%as" -- "{file}"`
   - Fall back to today's date if no git history

2. Read the file content

3. Check if it already has YAML frontmatter (starts with `---`)
   - If yes: preserve existing frontmatter, add any missing standard fields
   - If no: prepend new frontmatter block

4. Standard frontmatter fields:
```yaml
---
title: {extracted from first # heading, or filename if no heading}
project: {project_name}
type: spec | prompt-log | working-doc
date: YYYY-MM-DD
tags: []
why_private: {one phrase — e.g., "contains unpublished architecture decisions"}
status: stable | active | archived
source_repo: {github URL or local path of source repo}
harvested: YYYY-MM-DD
---
```

5. Write the file to the destination path

6. Do NOT modify the source file. This is read-only access to the source repo.

### Step 6: Stage changes

In the knowledge repo:
```bash
cd "{knowledge_repo}"
git add README.md projects/README.md projects/{project_name}/
git status
```

Show the user the staged files. Then prepare (but DO NOT run) the commit command:

```bash
# Ready to commit when you are:
git commit -m "harvest({project_name}): add {N} docs from {source_repo_name}

Types: {N} specs, {N} prompt-logs, {N} working-docs
Source: {source_repo_name}
Harvested: {today's date}"
```

Tell the user:
```
Staged {N} files for {project_name}. Review with:
  cd {knowledge_repo} && git diff --cached

When ready to commit:
  git commit -m "harvest(ciam-demo): add 7 docs from ciam-demo-private"

To push (after reviewing):
  git push origin main
```

**Never run git push. Never run git commit automatically. Always stop here.**

---

## Handling Edge Cases

**File already exists in destination:**
Check if the destination file exists. If it does:
- Compare dates — if source is newer, overwrite and note it
- If source is older, skip and tell the user
- Never silently overwrite without reporting it

**Ambiguous file type:**
When you can't classify a file confidently, default to `working-doc` and tell the user
which files you defaulted on. They can rename/move after review.

**Monorepo with multiple sub-projects:**
If the source repo contains multiple sub-projects (e.g., `claims-api/`, `claims-web/`),
ask whether to treat them as one project or separate projects in the knowledge repo.

**File with no date in git history:**
Use today's date and add a note in the frontmatter: `date_note: "no git history — using harvest date"`

**Binary files, images, PDFs:**
Skip them by default. Mention that they were found but skipped. Ask if the user wants to
handle them separately.

---

## After Harvesting

Once staged, remind the user of three things:

1. **Review the diff** before committing — `git diff --cached` in the knowledge repo
2. **Update README.md files** if any placeholders need improving (especially the project-level "Why Private" section)
3. **Add tags** to frontmatter if the auto-generated ones are thin

The knowledge repo is now ready for an agent to query at task start by reading
`projects/{project_name}/` and filtering by `type: spec` for context loading.

---

## Reference Files

- `spirit.md` — The history and purpose behind this skill. Read it for context on
  why the taxonomy was designed this way and what comes next.
- `references/conversation-context.md` — The design session that produced this skill,
  including all decisions made and the reasoning behind them.
