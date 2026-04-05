---
name: jack-git-commit
description: |
  Structured git commit skill for all agents and humans. Use when: committing code changes, the user says "commit", "/jack-git-commit", a worker completes a task and needs to commit, or any agent needs to record work in git. Generates Conventional Commit messages with traceable metadata footers (Goal, Step, Worker) so git log serves as a self-documenting work ledger. Enforces atomic commits, staged-only policy, and NEVER pushes.
---

# Jack Commit

Git history is the ledger. Every commit is queryable, traceable to its origin, and reviewable without external databases.

**NEVER push to remote.** Only push if the human explicitly says "push" in the current message. Do not offer or suggest pushing.

## Format

```
type(scope): summary

Body: why, not what. Skip if diff is self-explanatory.

Footer metadata (one per line, only what's known)
```

**Types:** Standard Conventional Commits — `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `style`, `perf`.

**Scope:** Infer from primary directory/module. Examples: `(vendor)`, `(executive-loop)`, `(skills)`. Omit if changes span too many areas.

**Summary:** Imperative mood, lowercase after colon, no period, max 72 chars total.

**Body:** Only when the *why* isn't obvious. What motivated the change, what was rejected, what edge case this covers.

### Footer Metadata

`Key: value` lines that make `git log --grep` a queryable ledger.

| Field | When | Example |
|-------|------|---------|
| `Goal:` | Worker executing a goal bundle | `Goal: P2-finance-dashboard` |
| `Step:` | Multi-step execution | `Step: 3/5` |
| `Worker:` | Autonomous agent commit | `Worker: claude`, `Worker: codex`, `Worker: kimi` |
| `Co-Authored-By:` | Attribution desired | `Co-Authored-By: Claude <noreply@anthropic.com>` |

Only include fields you actually know. Zero footer fields is fine.

## Workflow

### 1. Read state

```bash
git status --porcelain
git diff --staged --stat
git diff --staged
git log --oneline -5
```

Nothing staged and nothing modified → stop with "Nothing to commit."

### 2. Check .gitignore

Before staging, verify `.gitignore` exists and covers common entries. Warn the user if any of these are missing:

```
node_modules/
.env
.env.*
.DS_Store
dist/
*.log
```

If `.gitignore` doesn't exist at all, warn and ask before proceeding — don't commit without one.

### 3. Stage

- **Nothing staged?** → `git add -A` (default: commit everything)
- **Something already staged?** → Only commit what's staged, don't add more
- After staging, run `git status` to show what will be committed

### 4. Check for mixed concerns

Review the staged diff and group changes by logical intent. Present the analysis:

```
I see 2 separate concerns in these changes:

1. docs: README rewrite + new technical highlights (README.md, docs/**)
2. feat(skills): new jack-git-commit skill (.claude/skills/jack-git-commit/*)

Split into separate commits?
```

- List each concern with its type, description, and files
- User says no → commit as-is
- User says yes → unstage all, then stage and commit each concern one at a time

### 5. Generate message and present

```
Proposed commit:

  feat(vendor): add Kimi wire protocol support

  Implements bidirectional streaming for Kimi agent SDK,
  replacing the CLI fallback with native wire communication.

  Goal: P1-multi-vendor-workers
  Step: 2/4
  Worker: claude

Commit with this message?
```

### 6. Commit

```bash
git commit -m "$(cat <<'EOF'
<the approved message>
EOF
)"
```

HEREDOC for multi-line. Never `--no-verify`. Hook failure → show output and stop.

### 7. Confirm

```
Committed: feat(vendor): add Kimi wire protocol support
  3 files changed, 147 insertions(+), 12 deletions(-)
  Branch: feat-multi-vendor
```

## Rules

1. **Never push** unless human explicitly says "push" right now
2. **Stage smart** — nothing staged → `git add -A`; something staged → commit only that
3. **Atomic** — one logical change per commit; flag mixed concerns
4. **Respect hooks** — never `--no-verify`
5. **Don't fabricate** — only include metadata you actually know
6. **Ask when uncertain** — unclear intent → ask before committing
7. **Universal** — same format for human, Claude, Codex, Kimi
