# Mode 1: Repo Scan — Detailed Execution

## Table of Contents

- [Step 1: Validate inputs and detect structure](#step-1-validate-inputs-and-detect-structure)
- [Step 2: Discover AI documents](#step-2-discover-ai-documents)
- [Step 3: Prepare the destination](#step-3-prepare-the-destination)
- [Step 4: Create/update READMEs](#step-4-createupdate-readmes)
- [Step 5: Copy and add frontmatter](#step-5-copy-and-add-frontmatter)
- [Step 6: Stage changes](#step-6-stage-changes)

---

## Step 1: Validate inputs and detect structure

Verify both paths exist:
```bash
ls "{source_repo}"
ls "{knowledge_repo}"
```

**Determine project name** (in priority order):
1. User-provided `project_name` parameter
2. GitHub remote repo name: `git -C "{source_repo}" remote get-url origin` → extract repo name
3. Fall back to local folder name

**Detect monorepo vs simple repo:**
- Look for sub-project directories (e.g., `local/`, `server/`, `packages/`, or directories containing their own `ai-docs/` or `CLAUDE.md`)
- If sub-projects found → monorepo: `{repo}/{sub-project}/`
- If no sub-projects → simple repo: `{repo}/{repo}/` (repeat name)

## Step 2: Discover AI documents

Scan these locations — check **all levels** including nested subdirectories:

```bash
# CLAUDE.md and AGENTS.md at any level
find "{source_repo}" -name "CLAUDE.md" 2>/dev/null
find "{source_repo}" -name "AGENTS.md" 2>/dev/null

# ai-docs directories at any level (monorepo pattern)
find "{source_repo}" -path "*/ai-docs/*.md" 2>/dev/null

# local-ai-docs directories (gitignored, flagged for harvest)
find "{source_repo}" -path "*/local-ai-docs/*.md" 2>/dev/null

# local/ subdirectories with ai-docs (common harness pattern)
find "{source_repo}/local" -path "*/ai-docs/*.md" 2>/dev/null

# local-only/ directories (gitignored but still on disk)
find "{source_repo}" -path "*/local-only/*.md" 2>/dev/null

# Named patterns at any level
find "{source_repo}" -name "*prompt-log*" -name "*.md" 2>/dev/null
find "{source_repo}" -name "*spec*.md" 2>/dev/null
find "{source_repo}" -name "*kickoff*" -name "*.md" 2>/dev/null
find "{source_repo}" -name "*gap*.md" 2>/dev/null
find "{source_repo}" -name "*prd*.md" 2>/dev/null

# Harness prompt templates (secondary priority)
find "{source_repo}" -path "*/prompts/*.md" 2>/dev/null
find "{source_repo}" -path "*/src/prompts/*.md" 2>/dev/null
```

### Exclusions — do NOT harvest

**Integral project files** — if a file is instrumental to how the capability works, do not harvest it. The test: if you deleted it, would the project break or lose functionality?

- `docs/` directories — integral project documentation, even if AI-generated
- `src/prompts/` and other harness code — these are executable, not just documentation
- Skill SKILL.md files that are actively loaded by agents — these are code, not docs
- Config files, templates, assets that other code references
- `node_modules/`, `.git/`, `dist/`, `build/`, `output/`
- Files already in the knowledge repo
- README.md files (public documentation, not AI docs)
- `.env` files, lock files, generated files
- Files > 50MB

### Noted exceptions — harvest as duplicates

`CLAUDE.md` and `AGENTS.md` are the exception. They are both:
- Instrumental to the project (Claude Code reads them at session start)
- AI documentation worth preserving in the knowledge repo

**Harvest these as duplicates** — copy them to ai-knowledge but NEVER delete them from the source repo. Mark them in frontmatter with `duplicate: true` so it's clear the source file must remain in place. These are noted exceptions, not the rule.

### Sub-project detection for monorepos

Group discovered files by their sub-project. Determine sub-project from the directory path:
- `local/{sub-project}/ai-docs/file.md` → sub-project is `{sub-project}`
- `server/{sub-project}/docs/file.md` → sub-project is `{sub-project}`
- `{sub-project}/CLAUDE.md` → sub-project is `{sub-project}`
- Root-level files → sub-project is the repo name itself

### Present to user before proceeding

For monorepos, group by sub-project:

```
Found 60+ AI documents in jack-dev-server-configs:

  generic-harness-v1/ (20 files)
    [prompt-log]      ai-docs/init/prompt-log.md
    [spec]            ai-docs/init/CONSOLIDATED_SPEC.md
    [working-doc]     CLAUDE.md
    [harness-prompt]  src/prompts/spec_prompt.md
    ...

  study-harness/ (10 files)
    [prompt-log]      ai-docs/prompt-log-2026-02-28-0-planning.md
    [spec]            ai-docs/prd-v1.0.md
    ...

Destination: ai-knowledge/projects/jack-dev-server-configs/{sub-project}/

Proceed? (or adjust any classifications above)
```

Wait for confirmation before copying.

## Step 3: Prepare the destination

Use two-tier structure. Only create type folders that will contain files.

```bash
# Tier 1: repo
mkdir -p "{knowledge_repo}/projects/{project_name}"

# Tier 2: each sub-project, with only the type folders that have docs
mkdir -p "{knowledge_repo}/projects/{project_name}/{sub_project}/specs"
mkdir -p "{knowledge_repo}/projects/{project_name}/{sub_project}/prompt-logs"
mkdir -p "{knowledge_repo}/projects/{project_name}/{sub_project}/working-docs"
mkdir -p "{knowledge_repo}/projects/{project_name}/{sub_project}/harness-prompts"
```

## Step 4: Create/update READMEs

Follow the README templates in [taxonomy.md](taxonomy.md). Create missing READMEs;
update existing ones by appending new entries (never remove existing entries).

**Always update the Harvest Log** in the sub-project README — append a new row with today's
date, document counts by type, and the source.

## Step 5: Copy and add frontmatter

For each file:

1. **Determine destination path**: `YYYY-MM-DD-{seq}-{original-slug}.md`
   - Use git commit date: `git log -1 --format="%as" -- "{file}"`
   - Fall back to today's date if no git history
   - `{seq}` is a two-digit sequence number (`01`, `02`) for chronological ordering within the same date

2. **Read the file content**

3. **Handle existing frontmatter**:
   - If file starts with `---`: preserve existing, add missing standard fields
   - If no frontmatter: prepend new block

4. **Standard frontmatter** (see [taxonomy.md](taxonomy.md) for full spec):
```yaml
---
title: {from first # heading or filename}
project: {project_name}
sub_project: {sub_project}
type: spec | prompt-log | working-doc | harness-prompt
date: YYYY-MM-DD
tags: []
why_private: {one phrase}
status: stable | active | archived
source_repo: {github URL or local path}
source_tool: {claude-code | claude-web | chatgpt | other}
harvested: YYYY-MM-DD
---
```

5. **Write to destination** — do NOT modify the source file

## Step 6: Stage and commit

```bash
cd "{knowledge_repo}"
git add README.md projects/README.md projects/{project_name}/
git status
git commit -m "harvest({project_name}): add {N} docs from {source_repo_name}

Sub-projects: {list}
Types: {N} specs, {N} prompt-logs, {N} working-docs, {N} harness-prompts
Harvested: {today's date}"
```

**Never push. Commit locally, user pushes when ready.**

## Step 7: Offer source cleanup (after commit)

**Only after the user has committed the harvest in the knowledge repo**, offer to clean up
the source files. This is optional — the user decides.

```
Harvest committed. Would you like me to clean up the source AI docs?

For each harvested file, I can:
  - Delete it from the source repo (if it's NOT gitignored — will show in git diff)
  - Leave gitignored files as-is (they're already hidden from git)

I'll stage the deletions as a separate commit in the source repo for your review.
You review the diff before committing. I never push.
```

**What to DELETE (safe to remove — duplicated in ai-knowledge):**
- `ai-docs/` directories and all their contents — pure AI documentation with no runtime purpose
- `local-ai-docs/` directories — these exist specifically for harvest staging, safe to clear after harvest
- Standalone prompt log files outside `ai-docs/` that aren't referenced by anything

**What to NEVER DELETE:**
- `CLAUDE.md` / `AGENTS.md` — harvested as duplicates but must stay in place (Claude Code needs them)
- `src/prompts/` — harness code that gets executed
- `docs/` — integral project documentation
- Skill SKILL.md files actively loaded by agents
- Template/asset files, config files, anything other code references
- Anything instrumental to how the capability works

**Cleanup rules:**
- Only offer cleanup after the harvest is committed (not just staged)
- Gitignored files (e.g., in `local-only/`): ask if user wants them deleted, but note they're already hidden from git
- Non-gitignored files: delete and stage the removal as a new commit in the source repo
- Never delete and harvest in the same commit — these are separate operations
- Never push the cleanup commit — user reviews first
- Present the DELETE vs KEEP lists to the user before doing anything

```bash
# In the source repo, after user confirms:
cd "{source_repo}"
git rm -r "{ai-docs-dir1}" "{ai-docs-dir2}" ...
git rm "{standalone-prompt-log}" ...
git status
# Show what will be committed, but DO NOT commit
```
