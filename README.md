# ai-builder-kit

A [Claude Code plugin marketplace](https://docs.anthropic.com/en/docs/claude-code) — a collection of plugins, skills, and hooks for AI-assisted workflows.

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [hlx-admin-api-executor-guarded](plugins/hlx-admin-api-executor-guarded/) | AEM Edge Delivery Services Admin API executor with PreToolUse guardrails |

## Getting Started

### Option A: Install with `npx skills` (Recommended)

List available skills:

```bash
npx skills add jackzhaojin/ai-builder-kit --list
```

Install a specific skill:

```bash
npx skills add jackzhaojin/ai-builder-kit --skill hlx-admin-api-executor
```

Install all skills:

```bash
npx skills add jackzhaojin/ai-builder-kit --yes
```

### Option B: Add as a Claude Code marketplace

1. In Claude Code, run `/plugin` and navigate to **Marketplaces** > **+ Add Marketplace**. Enter:

   ```
   https://github.com/jackzhaojin/ai-builder-kit.git
   ```

   Or add it directly to your `~/.claude/settings.json`:

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

2. Run `/plugin` in Claude Code, go to **Discover**, select a plugin, and choose your install scope:

   - **User scope** — available in all your projects
   - **Project scope** — available to all collaborators on the current repo
   - **Local scope** — available only to you in the current repo

3. After installing, run `/reload-plugins` to activate the plugin in your current session.
