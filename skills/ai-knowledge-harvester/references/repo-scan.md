# Mode 1: Repo Scan — Detailed Execution

## Table of Contents

- [Step 1: Validate inputs](#step-1-validate-inputs)
- [Step 2: Discover AI documents](#step-2-discover-ai-documents)
- [Step 3: Prepare the destination](#step-3-prepare-the-destination)
- [Step 4: Create/update READMEs](#step-4-createupdate-readmes)
- [Step 5: Copy and add frontmatter](#step-5-copy-and-add-frontmatter)
- [Step 6: Stage changes](#step-6-stage-changes)

---

## Step 1: Validate inputs

Verify both paths exist before doing anything else:
```bash
ls "{source_repo}"
ls "{knowledge_repo}"
```

If either doesn't exist, stop and tell the user clearly.

## Step 2: Discover AI documents

Scan these locations (in priority order):

```bash
# Primary AI doc locations
find "{source_repo}/ai-docs" -name "*.md" 2>/dev/null
find "{source_repo}" -name "CLAUDE.md" 2>/dev/null
find "{source_repo}" -name "AGENTS.md" 2>/dev/null
find "{source_repo}" -name "claude-gap.md" 2>/dev/null
find "{source_repo}" -name "*prompt-log*" -name "*.md" 2>/dev/null
find "{source_repo}" -name "*spec*.md" 2>/dev/null
find "{source_repo}" -name "*kickoff*" -name "*.md" 2>/dev/null

# Monorepo sub-projects
find "{source_repo}" -path "*/ai-docs/*.md" 2>/dev/null
```

### Exclusions

- `node_modules/`, `.git/`, `dist/`, `build/`
- Files already in the knowledge repo
- README.md at repo root (public documentation)
- `.env` files, lock files, generated files

### Present to user before proceeding

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

## Step 3: Prepare the destination

```bash
mkdir -p "{knowledge_repo}/projects/{project_name}/specs"
mkdir -p "{knowledge_repo}/projects/{project_name}/prompt-logs"
mkdir -p "{knowledge_repo}/projects/{project_name}/working-docs"
mkdir -p "{knowledge_repo}/shared/skills"
```

## Step 4: Create/update READMEs

Follow the README templates in [taxonomy.md](taxonomy.md). Create missing READMEs;
update existing ones by appending new entries (never remove existing entries).

## Step 5: Copy and add frontmatter

For each file:

1. **Determine destination path**: `YYYY-MM-DD-{original-slug}.md`
   - Use git commit date: `git log -1 --format="%as" -- "{file}"`
   - Fall back to today's date if no git history

2. **Read the file content**

3. **Handle existing frontmatter**:
   - If file starts with `---`: preserve existing, add missing standard fields
   - If no frontmatter: prepend new block

4. **Standard frontmatter** (see [taxonomy.md](taxonomy.md) for full spec):
```yaml
---
title: {from first # heading or filename}
project: {project_name}
type: spec | prompt-log | working-doc
date: YYYY-MM-DD
tags: []
why_private: {one phrase}
status: stable | active | archived
source_repo: {github URL or local path}
harvested: YYYY-MM-DD
---
```

5. **Write to destination** — do NOT modify the source file

## Step 6: Stage changes

```bash
cd "{knowledge_repo}"
git add README.md projects/README.md projects/{project_name}/
git status
```

Show staged files. Prepare (but DO NOT run) the commit:

```bash
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
  git commit -m "harvest({project_name}): add {N} docs from {source_repo_name}"

To push (after reviewing):
  git push origin main
```

**Never run git push. Never run git commit automatically. Always stop here.**
