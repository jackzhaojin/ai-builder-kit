---
date: {YYYY-MM-DD}
time: "{HH:MM}"
platform: claude-ai
model: {model-id-if-known}
topic: {topic-slug}
tags: [{tag-1}, {tag-2}, {tag-3}]
prompt_count: {N}
status: {complete | in-progress | blocked | exploration}
---

# {Human-readable title} — Conversation Log

**Date**: {YYYY-MM-DD HH:MM}
**Platform**: Claude.ai
**Topic**: {one-line summary of what this chat was about}

---

## Session: {Session theme}

### Prompt 1: {Descriptive title}

**Inputs**: {text only | text + N images | text + 1 file (type, size) | text + pasted document (~N words)}

> {Full user prompt — captured verbatim, no edits, no paraphrasing.
> Preserve typos, voice-to-text artifacts, casual phrasing. The way the user wrote it is part of the record.}

→ Response: {1–2 lines on what Claude decided/answered.}
→ Action: {1–2 lines on artifacts created, files written, decisions made.} {✅ | ⚠️ | ❌ | 🚧}
→ Tools: {comma-separated tool names — e.g. web_search, image_search, create_file. Or "none".}

---

### Prompt 2: {Descriptive title}

**Inputs**: text + 1 image

> {Full user prompt}

📎 *Attachment: {filename-or-description.png}*

→ Response: {1–2 lines}
→ Action: {1–2 lines} ✅
→ Tools: {…}

---

### Prompt 3: {Descriptive title}

**Inputs**: text + pasted code (Python, ~150 lines)

> {Full user prompt}

📎 *Pasted code: {what the code does}*

→ Response: {1–2 lines}
→ Action: {1–2 lines}
→ Tools: {…}

---

<!--
  Continue numbering through every user turn.
  
  The /log invocation itself is NOT logged — it's the trigger, not content.
  Add an HTML comment at the bottom of the log noting this, so that future-you
  reading the log understands why the chat had one more user turn than the
  prompt_count says.
  
  Start a new "## Session N:" header only on a clear theme shift in a long chat.
  
  Optional closing block (only for major milestones, 2–3 lines max):

---

**Session summary**: {N} prompts. {What got built / decided in one sentence.}
-->
