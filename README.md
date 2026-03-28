# ai-builder-kit

A [Claude Code plugin marketplace](https://docs.anthropic.com/en/docs/claude-code) — a collection of plugins, skills, and hooks for AI-assisted workflows.

## Available Skills

| Skill | Last Modified | Description |
|-------|--------------|-------------|
| [ai-knowledge-harvester](skills/ai-knowledge-harvester/) | 2026-03-28 | Harvest AI docs from repos into a centralized private knowledge repository |
| [conversation-logger](skills/conversation-logger/) | 2026-03-28 | Log Claude Code conversation sessions with timestamps in structured markdown |
| [hlx-admin-api-executor](skills/hlx-admin-api-executor/) | 2026-03-22 | Interactive AEM Edge Delivery Services Admin API executor |

## Available Plugins

| Plugin | Last Modified | Description |
|--------|--------------|-------------|
| [hlx-admin-api-executor-guarded](plugins/hlx-admin-api-executor-guarded/) | 2026-03-22 | AEM Edge Delivery Services Admin API executor with PreToolUse guardrails |

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
