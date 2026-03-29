# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A Claude Code plugin marketplace — a collection of skills, plugins, and hooks for AI-assisted workflows. Distributed via `npx skills add jackzhaojin/ai-builder-kit` or the Claude Code plugin UI.

## Architecture

### Skills vs Plugins

- **Skills** (`skills/`): Standalone SKILL.md + optional scripts/references/assets. Self-contained, single-purpose. Installed individually.
- **Plugins** (`plugins/`): Bundle a skill + hooks (e.g., PreToolUse guardrails). Have `.claude-plugin/plugin.json` metadata. Installed as a unit.

### Key Directories

| Path | Purpose |
|------|---------|
| `skills/` | Standalone skills (each has SKILL.md) |
| `plugins/` | Bundled skill + hook packages |
| `.claude-plugin/marketplace.json` | Anthropic plugin registry metadata |
| `local-only/` | Local testing/scratch (gitignored) |
| `local-ai-docs/` | Private AI prompt logs (gitignored) |

### Skill Structure

```
skill-name/
├── SKILL.md           # Required. YAML frontmatter (name, description) + markdown body
├── scripts/           # Executable code (Python/Bash)
├── references/        # Deep-dive docs loaded on-demand
└── assets/            # Templates, files used in output
```

SKILL.md frontmatter fields: `name` (slug), `description` (trigger phrases + when-to-use), optionally `context: fork` and `disable-model-invocation: true`.

### Plugin Structure

```
plugin-name/
├── .claude-plugin/plugin.json   # Metadata (name, version, author)
├── hooks/hooks.json             # PreToolUse hook registration
├── hooks/*.sh                   # Hook implementations
└── skills/                      # Bundled skills
```

## Development

### Testing a skill locally

Skills in `skills/` are automatically available when working in this repo. To test a skill from another project, symlink it into `~/.claude/skills/`.

### Testing a plugin locally

Enable in `.claude/settings.local.json`:
```json
{
  "enabledPlugins": {
    "plugin-name@ai-builder-kit": true
  }
}
```

### Installing skills from this repo

```bash
npx skills add jackzhaojin/ai-builder-kit --list          # List available
npx skills add jackzhaojin/ai-builder-kit --skill <name>   # Install one
```

### Testing branded-pptx

Requires Python 3.12+ (`python3.12`) and the [anthropic pptx skill](https://github.com/anthropics/skills) installed globally. Test templates go in `local-only/` (gitignored):

```bash
python3.12 skills/branded-pptx/scripts/analyze_template.py \
  local-only/test/template.pptx --output-dir local-only/test/runs --run-id
```

Each run creates a timestamped folder with manifests, template copy, and `output/` for generated .pptx/.pdf.

## Conventions

- SKILL.md descriptions must include trigger phrases ("Use when the user says...")
- Keep SKILL.md body under 500 lines; split detail into `references/` files
- Edge cases go in situation → action tables, not prose
- Safety rules in bold with "Never..." prefix
- Skills that depend on other skills declare it in SKILL.md description and body (no formal dependency mechanism exists yet)
- Update the README.md table when adding/modifying skills (include Last Modified date)
- Do not commit or push unless explicitly instructed
