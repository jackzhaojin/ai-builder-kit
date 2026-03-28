---
name: conversation-logger
description: Log Claude Code conversation sessions with timestamps in structured markdown. Use when the user says "log this session", "convo log", or wants to create a record of prompts and responses for a project.
context: fork
---

# Conversation Logger

Log Claude Code sessions as timestamped markdown for project documentation.

## Why This Skill Exists

**The user's prompts are the primary value.** When reviewing past sessions, the user wants to see what *they* were thinking and asking—their mental journey through a problem. Claude's responses are secondary context.

This creates an asymmetric log:
- **User prompts**: Captured in full detail (the main record)
- **Claude responses**: Compressed to 1-2 lines (just enough to know what happened)
- **Summaries**: Avoided entirely (prompts tell the story)

Think of it like a lab notebook: the scientist's observations and questions are the record; the equipment readings are noted briefly. Don't over-document Claude's side—it's noise that buries the user's thought process.

## Quick Start

1. Determine log location from context or ask user
2. Create/append to `prompt-log.md` at determined location
3. Use template from `assets/init-prompt-log-template.md`

## File Location

**Filename**: `prompt-log.md`

**Location priority** (if clear from context):
1. `./ai-docs/{project-name}/` - if working on a specific project/agent
2. `./ai-docs/` - if exists
3. `./docs/` - if exists  
4. `./` - project root as fallback

**If location is not clear**: Ask the user where they'd like the log saved before creating it. Example: "Where should I save the prompt log? I see you have `./ai-docs/` - want me to create it there, or somewhere specific like `./ai-docs/content-authoring-eval/prompt-log.md`?"

## Logging Format

Each prompt gets a timestamp at the H3 level:

```markdown
### Prompt 1: Context Gathering (10:34 AM)

> {Full user prompt - preserve as-is, only trim if extremely long}

→ Response: {1 line what was decided/done, DO NOT GO LONG}
→ Action: {1 line files/tools used, DO NOT GO LONG}
```

## Timestamps — Use Real Data from History File

**CRITICAL: Do NOT guess timestamps.** Claude Code records every user prompt with an exact millisecond timestamp in `~/.claude/history.jsonl`.

### How to extract timestamps

1. Read `~/.claude/history.jsonl` (one JSON object per line)
2. Filter entries by the current `project` path (matches the working directory)
3. For the current session, filter by the most recent `sessionId`
4. Each entry has: `timestamp` (epoch ms), `display` (prompt text), `sessionId`, `project`

**Use this Bash command to extract timestamps for the current session:**
```bash
tail -100 ~/.claude/history.jsonl | python3 -c "
import sys, json
from datetime import datetime
for line in sys.stdin:
    d = json.loads(line)
    if d.get('project','') == 'PROJECT_PATH_HERE':
        ts = datetime.fromtimestamp(d['timestamp']/1000)
        prompt = d['display'][:100].replace('\n',' ')
        print(f'{ts.strftime(\"%I:%M %p\")}  {prompt}')
"
```

Replace `PROJECT_PATH_HERE` with the actual project path. Adjust `tail -100` if the session is longer.

### Format

Use 12-hour format with AM/PM: `(10:07 AM)`, `(2:15 PM)`

### Notes
- AskUserQuestion responses (multiple-choice answers) are NOT in history.jsonl — only text prompts are recorded
- If history.jsonl is unavailable or empty, fall back to calling `date` for the current time and note that earlier timestamps are approximate

## What to Capture

**PRIORITY: User input is the main value. Response/Actions = 1 LINE TOTAL.**

### User Prompts (PRIMARY FOCUS)
- **Capture the full user prompt** - this is the most important part
- Preserve file paths, code snippets, and specific instructions verbatim
- Only abbreviate if prompt exceeds ~500 words
- **If prompt is from AI agent with generic instructions**: Summarize the intent instead of logging full boilerplate (e.g., "Build phase 3 from plan.md" instead of full agent prompt)

### Response and Actions (TWO LINES MAX)

**CRITICAL: 1 line for response, 1 line for action. NEVER use bullet lists.**

```markdown
→ Response: Fixed blank screen bug in BatchEvaluationForm.
→ Action: Updated 2 files, created test helpers, committed.
```

**BAD (too verbose - NEVER do this):**
```markdown
#### Response and Actions
- **Response**: Implemented Phase 31 using pragmatic stub approach
- **Actions**:
  - Stubbed deterministic.ts
  - Removed playwright dependency
  - Created handoff document
```

**GOOD (correct format):**
```markdown
→ Response: Stubbed deterministic agents, removed Playwright dependency.
→ Action: Updated 4 files, simplified Dockerfile, created handoff. ✅
```

**Rules:**
- Use `→ Response:` and `→ Action:` format
- Each line 1-2 sentences max
- No bullet lists, no sub-items
- Include status emoji on action line if applicable (✅ ⚠️ ❌)

## Action Shorthand

| Action | Format |
|--------|--------|
| File read | `Read {filename}` |
| File write | `Created {filename}` or `Updated {filename}` |
| Web search | `WebSearch: {query}` |
| Tool use | `{ToolName}: {brief purpose}` |
| Questions | `Asked {N} questions` |

## Session Breaks

Start new session headers when:
- New day
- Significant time gap (>2 hours)
- Shifting to different phase of work

```markdown
## Session 2: Implementation (Dec 14, 2025)
```

## Session Summaries

**DO NOT** add verbose session status sections. The prompt log captures user prompts - that IS the record. No need for:
- ❌ "What Was Built" bullet lists
- ❌ Feature summaries or tables
- ❌ "Key Decisions" sections
- ❌ "Next Steps" lists

**If a summary is truly needed** (e.g., end of major milestone), keep it to 2-3 lines max:

```markdown
---

**Session 1 Summary**: Fixed 6 bugs, implemented 4-scenario support. Kanban app Tasks 18-20 complete.
```

The prompts themselves tell the story. Don't duplicate.
