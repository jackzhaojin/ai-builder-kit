---
name: chat-conversation-logger
description: "Log the current Claude.ai chat conversation as a timestamped, downloadable markdown file ready for an AI second brain. Captures the user's prompts verbatim — every word, plus attachment types — summarizes Claude's responses concisely, and notes every tool, artifact, and MCP call. Use this skill whenever the user types '/log', 'log this conversation', 'log this session', 'save conversation log', 'convo log', 'archive this chat', or any similar phrasing — even casually. This skill is manually invoked only: do NOT trigger on your own initiative without an explicit user request, even if the conversation seems like it might be useful to archive."
---

# Chat Conversation Logger

Archive Claude.ai chat sessions as structured, second-brain-ready markdown.

## Why This Skill Exists

The user's prompts are the primary value. When they review a logged session months later, what they want to see is *what they were thinking and asking* — their mental journey through a problem. Claude's responses are secondary context that confirms what happened.

This creates an asymmetric log:
- **User prompts**: captured 100% verbatim, plus attachment metadata
- **Claude's responses**: compressed to 2–3 lines (the gist, not the prose)
- **Tools and artifacts**: noted explicitly so the user can reconstruct *what was built*, not just what was said

Think of it as a lab notebook: the scientist's questions and observations are the record; the equipment readings are noted briefly. Don't over-document Claude's side — it's noise that buries the user's thought process.

The user has a parallel `conversation-logger` skill in Claude Code that does the same job there. This is the Claude.ai counterpart. The philosophy is identical; only the mechanics differ — no `~/.claude/history.jsonl` to read from, no per-message timestamps available, attachments matter more, and MCP/artifacts/search show up as tool calls instead of bash commands.

## How to Capture the Conversation in Claude.ai

Claude.ai does not expose a history file or per-message timestamps. The conversation context Claude has loaded *is* the source of truth. To produce the log:

1. Walk back through the loaded conversation from the start to the current turn.
2. For every **user turn**, record the full text verbatim. If the user attached files, pasted long blocks, or shared images, note each one in an `**Inputs**:` line above the prompt block.
3. For every **assistant turn**, write 2–3 lines summarizing what was decided/produced, plus a `→ Tools:` line listing the tools, artifacts, MCP calls, or web searches used. Skip purely conversational acknowledgments.
4. The current invocation (the `/log` request itself) is **not** logged — it's the trigger, not content.

If the conversation is very long (50+ turns), prefer fidelity on user prompts and brevity on Claude's side. Never paraphrase or "improve" a user prompt — copy the words.

### Verbatim means verbatim

Preserve typos, voice-to-text artifacts, autocorrect mishaps, casual phrasing, missing punctuation, and incomplete sentences. The way the user wrote it is part of the record — six months later, "claw code" instead of "Claude Code" tells the user this was a voice-dictated late-night thought, which is meaningful context. Don't silently fix anything. The only legitimate exception is redacting credentials (see Edge Cases below).

## Filename and Datetime

Filename pattern: `YYYY-MM-DD-HHMM-{topic-slug}.md`

Examples:
- `2026-04-26-1547-continuous-executive-agent-architecture.md`
- `2026-03-12-0930-eds-block-migration-with-make-com.md`
- `2026-04-02-2210-claude-certified-architect-study-plan.md`

Get the real datetime from the system at log-creation time:

```bash
date "+%Y-%m-%d-%H%M"
```

Choose the topic slug from the substantive subject of the chat — not from the user's literal first prompt, which is often vague ("hey can you help me with something"). Slug rules: lowercase, hyphen-separated, 3–8 words, descriptive enough to disambiguate from similar sessions. The user often builds the same topic 2–3 times across separate chats; the slug + datetime together must make them distinguishable on a timeline.

If you genuinely cannot tell the topic, ask the user one short question before generating the file.

## Log Structure

Use the template at `assets/init-conversation-log-template.md`. The high-level shape:

```markdown
---
date: 2026-04-26
time: "15:47"
platform: claude-ai
model: claude-opus-4-7
topic: continuous-executive-agent-architecture
tags: [agentic-ai, agent-sdk, multi-agent]
prompt_count: 12
status: in-progress
---

# {Human-readable title} — Conversation Log

**Date**: 2026-04-26 15:47
**Platform**: Claude.ai
**Topic**: {one-line summary of what this chat was about}

---

## Session: {Session theme}

### Prompt 1: {Descriptive title}

**Inputs**: text only

> {Full user prompt — verbatim, no edits}

→ Response: {1–2 lines on what Claude decided/answered.}
→ Action: {1–2 lines on artifacts created, files written, decisions made.}
→ Tools: {comma-separated list — e.g. web_search, image_search, create_file}
```

For two fully-worked end-to-end examples (one short clean session, one long multi-tool build session), see `references/examples.md`.

### Frontmatter fields (in priority order)

- `date` (YYYY-MM-DD) — required
- `time` ("HH:MM" 24-hour) — required
- `platform: claude-ai` — required, fixed value
- `model` — best-effort, e.g. `claude-opus-4-7`. If unknown, omit the field entirely rather than guessing.
- `topic` — same slug used in the filename
- `tags` — 2–5 short kebab-case tags inferred from the content (e.g. `agentic-ai`, `aem-eds`, `oauth`, `mcp-server`). Bias toward tags the user has used in past sessions if you can tell from context.
- `prompt_count` — integer count of user prompts logged (excluding the trigger)
- `status` — one of `complete`, `in-progress`, `blocked`, `exploration`. Default `complete` unless context indicates otherwise.

Frontmatter exists so future ingestion into a second brain (search, filter, cluster) is painless. Don't invent fields the user didn't ask for, but don't skip these.

## Capturing Inputs (the `**Inputs**:` line)

Above each user prompt, write a one-line summary of what came in with it. This matters more on Claude.ai than in Claude Code because chats are commonly multimodal.

| Input type | Inputs line example | Below the prompt |
|---|---|---|
| Text only | `**Inputs**: text only` | (nothing extra) |
| Image | `**Inputs**: text + 1 image` | `📎 *Attachment: {filename or description}*` |
| Multiple images | `**Inputs**: text + 3 images` | one 📎 line per image |
| File upload (PDF, .docx, .csv, etc.) | `**Inputs**: text + 1 file (PDF, 12 pages)` | `📎 *File: {filename} — {one-line summary}*` |
| Long pasted document | `**Inputs**: text + pasted document (~2,400 words)` | `📎 *Pasted: {one-line summary of what it was}*` |
| Code block paste | `**Inputs**: text + pasted code (Python, ~150 lines)` | `📎 *Pasted code: {what it does}*` |
| Mixed | `**Inputs**: text + 1 image + 1 PDF` | one 📎 line per item |

Keep the verbatim user prompt clean — put the attachment description on its own 📎 line below the blockquote, not inside it.

## Response, Action, Tools (the asymmetric body)

Three lines per turn, each starting with `→`. This is more detail than the Claude Code version (which uses a single line), but still tightly compressed.

```markdown
→ Response: Diagnosed the blank-screen bug as a missing useEffect dependency.
→ Action: Updated 2 React components, regenerated the artifact, all tests passing.
→ Tools: visualize:show_widget, web_search
```

Rules:

- **One sentence per `→` line** unless something genuinely needs two. Never bullet lists, never sub-items.
- `→ Response` = what Claude *said* or *decided* — the conclusion, not the reasoning chain.
- `→ Action` = what Claude *did* in the world — files created, artifacts rendered, tools invoked at a high level, decisions committed.
- `→ Tools` = the actual tool names called, comma-separated. If none, write `→ Tools: none`. See `references/action-shorthand.md` for the canonical list.
- Status emoji on the Action line if applicable: ✅ complete, ⚠️ partial, ❌ blocked, 🚧 in progress.

If a turn was a pure conversational exchange with no tool use and no decision (e.g. "thanks!" → "you're welcome"), you can collapse it into a single combined line under the prompt or omit it entirely.

## Sessions

A single chat is usually one session. Start a new `## Session N:` header only when there's a clear theme shift (e.g. you spent the first half debugging and the second half writing docs). For most logs, one session is right.

## Generating and Delivering the File

Use the existing computer-use tools:

1. Run `date "+%Y-%m-%d-%H%M"` via `bash_tool` to get the real datetime.
2. Read the template from `assets/init-conversation-log-template.md`.
3. Fill it in by walking the conversation as described above.
4. `create_file` to `/mnt/user-data/outputs/{filename}.md`.
5. (Optional) Run `python scripts/validate_log.py /mnt/user-data/outputs/{filename}.md` to lint the output. Mention any warnings to the user but don't block delivery on them — this is a sanity check, not a gate.
6. `present_files` with that path so the user can download it.
7. Briefly tell the user what was logged — prompt count, topic, filename — in 2–3 lines max. Don't summarize the conversation in chat; that's what the file is for.

## Edge Cases

**Mid-session logging.** If the user invokes `/log` partway through a chat and then keeps working, log everything up to and including the previous user turn. Treat the next `/log` as a separate session — name the second file with a `-part-2` suffix or a new topic slug if the topic shifted.

**Re-logging the same conversation.** If the user asks to re-log (e.g. they want a corrected version), regenerate fresh rather than trying to diff. Use the same datetime as the first log if it's within a few minutes; otherwise, use current time.

**Very long conversations.** Above ~50 user prompts, the file gets unwieldy. Don't drop content, but consider splitting into sessions by theme. Never silently truncate — if you must abbreviate, say so explicitly in a `> [Note: this session contained 80+ prompts; representative ones logged in full, repetitive iteration prompts collapsed to summaries]` block.

**Sensitive content.** If the conversation contains secrets the user pasted (API keys, tokens, passwords, OAuth client secrets, JWT bearer tokens), redact them in the log: `> [REDACTED: API key]`. Better to lose fidelity than to write a credential into a file the user might sync to cloud storage. This is the *only* legitimate edit to a verbatim prompt.

**You can't see the conversation.** If for some reason the conversation context is empty or you only see the trigger message, ask the user — don't fabricate. Say: "I can only see the trigger message — does this chat have prior turns you want logged, or should I treat this as a fresh session starting now?"

## What NOT to Add

The Claude Code version of this skill explicitly bans verbose session summaries — "What Was Built" lists, "Key Decisions" sections, "Next Steps" tables. Same rule here. The prompts ARE the record. Don't duplicate them in summary form.

If a closing summary feels truly necessary (end of a major milestone), 2–3 lines max:

```markdown
---

**Session summary**: 12 prompts. Built v1 of the executive loop harness, debugged the priority queue, drafted the adaptTo() submission abstract.
```

That's the ceiling. No tables. No bullet lists of accomplishments.
