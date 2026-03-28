# Mode 2: Ad-Hoc Ingest — Detailed Execution

## Table of Contents

- [Step A: Receive and understand the content](#step-a-receive-and-understand-the-content)
- [Source tool detection](#source-tool-detection)
- [Step B: Prepare the file](#step-b-prepare-the-file)
- [Step C: Write, update READMEs, and stage](#step-c-write-update-readmes-and-stage)

---

## Step A: Receive and understand the content

Read what the user pasted. Determine:
- Single document or multiple?
- Source AI tool? (detect from format or ask)
- Related project? (ask if unclear)
- Document type? (spec / prompt-log / working-doc — ask if ambiguous)

**Ask when uncertain.** Don't guess project or type on ambiguous content.

Example interaction:
```
You pasted what looks like a ChatGPT conversation about authentication design.

Before I file this:
1. Which project does this belong to? (e.g., ciam-demo, or a new project name?)
2. I'd classify this as a prompt-log — sound right, or is it more of a spec/working-doc?
3. Any specific title, or should I use "chatgpt-auth-design-session"?
```

## Source tool detection

| Source | Format signals |
|--------|---------------|
| ChatGPT | "ChatGPT" header, "You said:" / "ChatGPT said:" turn markers |
| Claude web | "Human:" / "Assistant:" turn markers |
| Clo.ai | Various — ask if you can't tell |
| Copilot | Code-heavy with inline suggestions pattern |
| Raw markdown (no conversation markers) | Likely a spec or working doc, not a prompt log |

If the format doesn't match any known pattern, ask: "Where did this come from?"

## Step B: Prepare the file

1. **Clean up content**:
   - Normalize heading levels (one `#` title at top)
   - Preserve original conversation format — don't rewrite or summarize
   - If very long, keep as-is (these are archives, not summaries)

2. **Determine filename**: `YYYY-MM-DD-{slug}.md` using today's date

3. **Prepend frontmatter**:
```yaml
---
title: {title}
project: {project_name}
type: spec | prompt-log | working-doc
date: YYYY-MM-DD
tags: []
why_private: {reason}
status: stable | active | archived
source_tool: chatgpt | claude-web | clo-ai | copilot | other
source_repo: n/a
harvested: YYYY-MM-DD
---
```

Note `source_tool` instead of `source_repo` for ad-hoc ingests.

## Step C: Write, update READMEs, and stage

Follow the same Steps 3–6 from [repo-scan.md](repo-scan.md):
- Create project folder structure if needed
- Create/update README.md files at each level (see [taxonomy.md](taxonomy.md))
- Write the file to the correct type folder
- Stage changes, show the user, stop before committing

## Ad-Hoc Edge Cases

| Situation | Action |
|-----------|--------|
| Pasted content with no context | Ask project and type — don't assume. Default to `working-doc` only after user confirms they're unsure |
| Mixed-topic conversation | Ask: file as one doc or split? If one, ask which project |
| Non-markdown content (HTML, raw text) | Convert to clean markdown, preserve substance |
| "Save this conversation" (current session) | Summarize key decisions and outputs into a prompt-log or working-doc. Ask which project |
