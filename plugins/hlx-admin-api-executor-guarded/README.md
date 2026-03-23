# hlx-admin-api-executor-guarded

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) for executing AEM Edge Delivery Services (Helix 5) Admin API operations with enforced guardrails.

## What This Does

Bundles two things into a single installable plugin:

1. **`hlx-admin-api-executor` skill** — interactive workflow for planning, executing, and documenting Admin API operations one step at a time (GET/SET/GET pattern, full request/response traceability)
2. **PreToolUse guard hook** — intercepts any destructive `curl` command targeting `admin.hlx.page` and requires explicit user approval before execution

The skill provides the workflow structure. The hook enforces it — destructive operations are blocked at the tool level regardless of what the model decides.

## What Gets Guarded

Any `Bash` tool call containing:
- `curl` with `--request` or `-X` set to **POST**, **PUT**, **DELETE**, or **PATCH**
- Targeting `admin.hlx.page` or `${BASE_URL}`

GET requests pass through without prompting. The hook fails open — if JSON parsing fails, the command is allowed.

## Installation

### From the ai-builder-kit marketplace

Add the marketplace to your Claude Code settings (global `~/.claude/settings.json`):

```json
{
  "extraKnownMarketplaces": {
    "ai-builder-kit": {
      "source": {
        "source": "git",
        "url": "https://github.com/jackzhaojin/ai-builder-kit.git"
      }
    }
  }
}
```

Then install via the Claude Code UI:

```
/plugin
```

Select **Discover**, find `hlx-admin-api-executor-guarded`, and install. Run `/reload-plugins` to activate.

### From a local clone

```bash
claude plugin add /path/to/ai-builder-kit/plugins/hlx-admin-api-executor-guarded
```

## Usage

Invoke the skill with:

```
/hlx-admin-api-executor-guarded:hlx-admin-api-executor
```

Or describe what you want to do and Claude will pick it up automatically when working with the AEM Admin API.

The skill guides you through:
- Planning operations with full endpoint details
- Executing one API call at a time with human review
- Documenting every request/response in an `EXECUTION.md` log
- Verifying changes with the GET/SET/GET pattern

## Requirements

- `jq` (used by the guard hook for JSON parsing)
- `curl` (for API requests)
- An AEM Admin API auth token (see skill instructions for setup)

## Plugin Structure

```
hlx-admin-api-executor-guarded/
  .claude-plugin/
    plugin.json
  hooks/
    hooks.json          # PreToolUse hook registration
    guard-admin-api.sh  # Guard script
  skills/
    hlx-admin-api-executor/
      SKILL.md          # Skill instructions
      assets/           # Templates for execution logs, env setup, auth
      references/       # Full endpoint catalog
```
