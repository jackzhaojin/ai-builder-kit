# hlx-admin-api-executor-guarded

A [Claude Code plugin](https://docs.anthropic.com/en/docs/claude-code) for executing AEM Edge Delivery Services (Helix 5) Admin API operations with enforced guardrails.

## What This Does

Bundles two things into a single installable plugin:

1. **`hlx-admin-api-executor` skill**: an interactive workflow for planning, executing, and documenting Admin API operations one step at a time (GET/SET/GET pattern, full request/response traceability)
2. **PreToolUse guard hook**: intercepts any `curl` write to `admin.hlx.page` or `api.aem.live` and asks for your approval before it runs

The skill provides the workflow structure. The hook enforces it: every write waits for your yes at the tool level, whatever the model decides.

## What Gets Guarded

Any `Bash` tool call containing:
- `curl` with a write: `-X` or `--request` set to **POST**, **PUT**, **DELETE** or **PATCH** (also `-XPOST` and `--request=DELETE`), or a request body or upload, which curl sends as POST or PUT (`-d`, `--data*`, `-F`, `--form*`, `--json`, `-T`, `--upload-file`)
- Targeting `admin.hlx.page`, `api.aem.live` or `${BASE_URL}`

GET requests pass through without prompting. The hook fails open: if JSON parsing fails, the command is allowed.

## Installation

One step (Claude Code 2.1.275 or later):

```
/plugin install hlx-admin-api-executor-guarded --marketplace jackzhaojin/ai-builder-kit
```

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

Load it for one session straight from the folder, no install:

```bash
claude --plugin-dir /path/to/ai-builder-kit/plugins/hlx-admin-api-executor-guarded
```

### Updating

The plugin carries an explicit `version` in `.claude-plugin/plugin.json`, so an install only moves when that number changes. Pull it with `/plugin update` or `claude plugin update hlx-admin-api-executor-guarded@ai-builder-kit`.

### Skills only, no hook

Install the skill on its own (`hlx-admin-api-executor@ai-builder-kit`) or every skill in the kit (`ai-builder-kit@ai-builder-kit`). Neither registers a hook. A project can declare it in its `.claude/settings.json`, so everyone who opens the project gets it:

```json
{
  "extraKnownMarketplaces": {
    "ai-builder-kit": { "source": { "source": "github", "repo": "jackzhaojin/ai-builder-kit" } }
  },
  "enabledPlugins": { "hlx-admin-api-executor@ai-builder-kit": true }
}
```

### Use the hook without the plugin

The guard is one script. Copy `hooks/guard-admin-api.sh` to your project's `.claude/hooks/`, then register it in `.claude/settings.json` (or `settings.local.json` to keep it to yourself):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/guard-admin-api.sh", "timeout": 5 }
        ]
      }
    ]
  }
}
```

Pair it with either skills-only install above.

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
    hlx-admin-api-executor -> ../../../skills/hlx-admin-api-executor   # symlink
```

The skill is not copied into this folder. `skills/hlx-admin-api-executor` is a symlink to the canonical skill in the repo's `skills/` folder, so the standalone skill, the `ai-builder-kit` bundle and this plugin all ship the same files. When Claude Code installs the plugin from the GitHub marketplace, it copies the symlink's target into the plugin cache, so the installed plugin is self-contained.

Because the symlink keeps changes to the skill out of this folder's commit history, bump `version` in `.claude-plugin/plugin.json` whenever the hook or the skill changes. `scripts/check-repo.mjs --base <ref>` (run in CI) fails if you forget.
