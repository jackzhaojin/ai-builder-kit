# chat-conversation-logger

A Claude.ai skill that turns the current chat into a timestamped, second-brain-ready markdown file with one prompt to Claude.

This is the Claude.ai counterpart to the existing Claude Code `conversation-logger` skill. Same lab-notebook philosophy (verbatim user prompts, compressed Claude responses), adapted to a chat environment with no history file and richer multimodal inputs.

## Install

Drop the packaged `.skill` file into your Claude.ai skills, or unzip the folder into your local skills directory and ensure Claude can read `SKILL.md`.

## Use

In any Claude.ai chat where you want an archive of the work, send one of:

- `/log`
- `log this conversation`
- `log this session`
- `save conversation log`
- `convo log`
- `archive this chat`

Claude will produce a downloadable markdown file named `YYYY-MM-DD-HHMM-{topic-slug}.md` with full prompts, attachment metadata, and a structured per-turn record of what Claude did and which tools it used.

## What's in the package

```
chat-conversation-logger/
├── SKILL.md                                    Instructions Claude follows
├── README.md                                   This file
├── assets/
│   └── init-conversation-log-template.md       Markdown template Claude fills in
├── references/
│   ├── action-shorthand.md                     Canonical tool names for the → Tools line
│   └── examples.md                             Two fully-worked example logs
└── scripts/
    └── validate_log.py                         Optional: lint a generated log
```

## Validating logs you already have

```bash
python scripts/validate_log.py path/to/your/log.md
```

Exit code 0 means the log conforms to the format. Issues are printed to stderr. Useful as a CI step if you want to lint a folder of historical logs before bulk-ingesting them into your second brain.

## Design notes

- **Manual invocation only** — the description tells Claude not to trigger on its own initiative. Logging should be your decision, not Claude's.
- **No per-prompt timestamps** — Claude.ai doesn't expose them and inventing them is dishonest. Sequential numbering with descriptive titles instead.
- **Datetime in the filename** is the timeline anchor — the same topic built across three separate chats stays distinguishable on a sorted directory listing.
- **Frontmatter** (`date`, `time`, `topic`, `tags`, `prompt_count`, `status`) is structured for downstream ingestion. Filter, search, and cluster from any second-brain tool that reads YAML frontmatter (Obsidian, Logseq, custom pipelines).

## Differences from the Claude Code `conversation-logger`

| | Claude Code | Claude.ai |
|---|---|---|
| Timestamps | Read from `~/.claude/history.jsonl` | None (sequential numbering) |
| Per-turn detail | 1-line response + 1-line action | 1–2 lines each + new `→ Tools:` line |
| Attachment handling | Rare in Claude Code | First-class — `**Inputs**:` line + 📎 markers |
| Tool surface | Read/Write/Bash/WebSearch | Plus artifacts, image search, MCP, memory tools |
| Output | Appended to `prompt-log.md` | New file per session, datetime-stamped |
| Trigger | `disable-model-invocation: true` flag | Description-only (Claude.ai validator restricts frontmatter keys) |
