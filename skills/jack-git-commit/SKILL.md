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
| `Skill:` | Skill(s) invoked during the work | `Skill: jack-git-commit, drawio` |
| `Plugin:` | Plugin(s) used | `Plugin: ai-builder-kit/executive-loop` |
| `MCP:` | MCP server(s) used | `MCP: claude-in-chrome, context7` |
| `Tools:` | Claude tools / notable Bash commands used | `Tools: WebSearch, WebFetch, Bash(rg, jq, gh pr view)` |
| `Co-Authored-By:` | Attribution desired | `Co-Authored-By: Claude <noreply@anthropic.com>` |

Only include fields you actually know. Zero footer fields is fine — but if a skill, plugin, MCP server, or notable tool *was* used to produce the change, **always** record it. These are provenance: which capability authored what.

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

#### 3a. Always sweep in prompt logs and session records

Prompt logs (`ai-docs/**/prompt-log*.md`, `ai-docs/**/*session*.md`, `.claude/projects/**/session-*.md`) and retros (`ai-docs/**/retro-*.md`) are the **provenance trail** for the commits around them. They should NEVER be filtered out as "unrelated" — git history is only queryable if the why-we-did-this note lands in the same branch as the what-we-did diff.

Before proposing the commit:

```bash
git status --porcelain | grep -E '^\?\? .*(prompt-log|retro-|session).*\.md$' || true
```

If any match:
- Stage them into the current commit (do not split into a separate commit unless the user explicitly asks)
- Mention them in the commit body under a `Provenance:` line if space allows
- If the user said "commit only X," still ASK before dropping a prompt log — never silently exclude

This rule exists because on 2026-04-11 a prompt log for v2.1.6 was left untracked for two commits, breaking the "git log is the ledger" guarantee.

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

### 4a. Record skills, plugins, MCP servers, and tools used

Before composing the message, recall what capabilities produced the staged changes:

- **Skill(s)** invoked this session that shaped the diff (e.g., `drawio`, `pptx`, `excalidraw`, `playwright-cli`)
- **Plugin(s)** active during the work
- **MCP server(s)** whose tools were called to produce or verify the change (e.g., `context7` for docs lookups, `claude-in-chrome` for browser testing, `stitch` for design)
- **Tools** — Claude built-in tools (`WebSearch`, `WebFetch`, `Agent`, `NotebookEdit`, etc.) and **notable Bash commands** that materially shaped the change (e.g., `rg`, `jq`, `gh pr view`, `curl`, `npm test`, `pytest`, `terraform plan`)

Add each as a footer line (`Skill:`, `Plugin:`, `MCP:`, `Tools:`). If none were used, omit. Never fabricate — only list what was actually invoked in the conversation that produced this commit.

**What counts as "notable" for `Tools:`:**
- ✅ External research (`WebSearch`, `WebFetch`, `gh`, `curl` to a real API)
- ✅ Verification / test runs whose output influenced the diff (`npm test`, `pytest`, `terraform plan`, `cargo check`)
- ✅ Code analysis that drove decisions (`rg`/`grep`, `jq`, `ast-grep`)
- ✅ Spawned `Agent` subagents
- ❌ Trivial built-ins: `Read`, `Edit`, `Write`, `ls`, `cat`, `git status/diff/log`, `mkdir`

When in doubt: if the tool's *output* shaped what you wrote, record it. If it was just navigation, skip it.

### 5. Generate message and present

```
Proposed commit:

  feat(vendor): add Kimi wire protocol support

  Implements bidirectional streaming for Kimi agent SDK,
  replacing the CLI fallback with native wire communication.

  Goal: P1-multi-vendor-workers
  Step: 2/4
  Worker: claude
  Skill: jack-git-commit
  MCP: context7
  Tools: WebSearch, Bash(rg, npm test)

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
3. **Always sweep prompt logs & retros** — `ai-docs/**/prompt-log*.md`, `ai-docs/**/retro-*.md`, session records. These are provenance, not "unrelated files." Never silently exclude them.
4. **Atomic** — one logical change per commit; flag mixed concerns
5. **Respect hooks** — never `--no-verify`
6. **Don't fabricate** — only include metadata you actually know
7. **Always record capability provenance** — if a skill, plugin, MCP server, or notable tool/Bash command materially shaped the change, add `Skill:` / `Plugin:` / `MCP:` / `Tools:` footer lines. Never silently omit.
8. **Ask when uncertain** — unclear intent → ask before committing
9. **Universal** — same format for human, Claude, Codex, Kimi
