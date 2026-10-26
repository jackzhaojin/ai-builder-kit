# CLAUDE.md

This file provides guidance to AI coding agents working in this repository. Claude Code reads it as CLAUDE.md; `AGENTS.md` is a symlink to it for Codex and others.

## What This Repo Is

A collection of skills, plugins, and hooks for AI coding agents, distributed three ways from the same `skills/` folder: `npx skills add jackzhaojin/ai-builder-kit` (any agent), the Claude Code plugin marketplace (`.claude-plugin/marketplace.json`), and the Codex plugin marketplace (`.agents/plugins/marketplace.json` plus the portable `plugin.json`).

## Architecture

### Skills vs Plugins

- **Skills** (`skills/`): Standalone SKILL.md + optional scripts/references/assets. Self-contained, single-purpose. Installed individually.
- **Plugins** (`plugins/`): Bundle a skill + hooks (e.g., PreToolUse guardrails). Have `.claude-plugin/plugin.json` metadata. Installed as a unit.

### Key Directories

| Path | Purpose |
|------|---------|
| `skills/` | Standalone skills (each has SKILL.md) |
| `plugins/` | Bundled skill + hook packages |
| `.claude-plugin/marketplace.json` | Claude Code marketplace: one entry per skill (`source: ./skills/<name>`, `strict: false`), the `ai-builder-kit` bundle (`source: ./`), and the hook plugins |
| `.agents/plugins/marketplace.json` | Codex marketplace: the `ai-builder-kit` bundle pointing at the repo root |
| `.codex-plugin/plugin.json` | Codex manifest for the bundle. Codex finds the skills through its `"skills": "./skills/"` key |
| `plugin.json` | The same bundle in the portable [Agent Plugins](https://agent-plugins.org) format. Neither Claude Code nor Codex reads it today; keep `name`, `version` and `description` in sync with `.codex-plugin/plugin.json` (the check script enforces it) |
| `scripts/check-repo.mjs` | Convention checks `claude plugin validate` does not cover (README rows, marketplace entries, frontmatter, symlinks, version bumps, manifest sync) |
| `.github/workflows/validate.yml` | CI: check-repo, the Claude Code validator and ShellCheck on every push to `main` and every PR |
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
├── .claude-plugin/plugin.json   # Metadata (name, version, author). Version is required
├── hooks/hooks.json             # Hook registration, exec form: "command": "bash", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/x.sh"]
├── hooks/*.sh                   # Hook implementations (executable)
└── skills/<name> -> ../../../skills/<name>   # Symlink to the canonical skill, never a copy
```

Claude Code dereferences a symlink that points elsewhere in the marketplace when it installs from GitHub, so the cached plugin is self-contained (verified 2026-10-25 against a git-hosted install). A local-path marketplace skips such links, so test hook plugins with `claude --plugin-dir plugins/<name>`, which follows them in place.

The symlink means a change to the skill does not touch the plugin folder, so the folder's commit SHA does not move. That is why hook plugins pin `version` in their `plugin.json` (and only there, not in the marketplace entry): bump it whenever the hook or a linked skill changes. `node scripts/check-repo.mjs --base <ref>` fails when you forget, and CI runs it against the previous commit.

## Development

### Testing a skill locally

Claude Code does not load `skills/` from a repo root, only `.claude/skills/`. To try a skill while editing it, symlink it into the target project: `.claude/skills/<name>` for Claude Code, `.agents/skills/<name>` for Codex and OpenCode. Do not `npx skills add` a local path over an existing GitHub install of the same skill; the lock file would then point at the clone instead of GitHub.

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

Requires `uv` (the script's inline metadata pulls Python 3.12+ and defusedxml) and the [anthropic pptx skill](https://github.com/anthropics/skills) installed globally. Test templates go in `local-only/` (gitignored):

```bash
uv run skills/branded-pptx/scripts/analyze_template.py \
  local-only/test/template.pptx --output-dir local-only/test/runs --run-id
```

Each run creates a timestamped folder with manifests, template copy, and `output/` for generated .pptx/.pdf.

### Testing playwright-demo-video

Requires ffmpeg/ffprobe (`brew install ffmpeg`), Node.js 18+, and a target web project with Playwright installed. Voiceover needs `ELEVENLABS_API_KEY`. Pipeline scripts are zero-dependency Node (`node --check skills/playwright-demo-video/scripts/*.mjs` to syntax-check). Demo output goes in the target project, not this repo.

## Release checklist

1. Edit the skill. Keep `SKILL.md` under 500 lines; move detail to `references/`.
2. Validate: `node scripts/check-repo.mjs`, `claude plugin validate skills --strict` and `claude plugin validate .claude-plugin/marketplace.json --strict`. Codex has no validator CLI; check-repo confirms the Codex and portable manifests agree. CI runs all of this plus ShellCheck.
3. New skill: add a README.md row (alphabetical, with the Last Modified date) and a `.claude-plugin/marketplace.json` entry (copy an existing skill entry, no `version`). Changed skill: bump its Last Modified date, and if a hook plugin symlinks it, bump that plugin's `version`.
4. Commit in Conventional Commits format with provenance footers (the `jack-git-commit` skill), push only when told.
5. Consumers get it on their next update (see "Keeping it up to date" in README.md). Jack's laptop: run the `update-skills` skill or `../jack-dev-server-configs/local/update-skills.sh`.

## Conventions

- SKILL.md descriptions must include trigger phrases ("Use when the user says...")
- Keep SKILL.md body under 500 lines; split detail into `references/` files
- Edge cases go in situation → action tables, not prose
- Safety rules in bold with "Never..." prefix
- Skills that depend on other skills declare it in SKILL.md description and body (no formal dependency mechanism exists yet)
- Adding a skill: create `skills/<name>/SKILL.md`, add a README.md table row (with Last Modified date), and add a marketplace entry to `.claude-plugin/marketplace.json` (copy an existing skill entry). The Codex bundle picks it up automatically.
- Do not add `version` to skill entries in `.claude-plugin/marketplace.json`: with no version, Claude Code keys updates on the commit SHA, so every push to main reaches users on `/plugin update`
- Validate before committing: `node scripts/check-repo.mjs`, `claude plugin validate .claude-plugin/marketplace.json --strict` and `claude plugin validate skills --strict`
- Share files with symlinks, never copies, and keep the Claude-side path canonical: `skills/<name>` is the real folder, hook plugins link to it, and `AGENTS.md` is a symlink to `CLAUDE.md`
- Hook commands use exec form (`"command": "bash", "args": [...]`) so a path with spaces cannot split; the validator warns on unquoted `${CLAUDE_PLUGIN_ROOT}`
- Keep skills Codex-compatible: only `name` and `description` in frontmatter are portable, Codex ignores Claude-only keys such as `allowed-tools` and `context`, and the SKILL.md body should not depend on Claude-only tools without a plain-shell fallback
- Python scripts in skills carry PEP 723 inline metadata (`# /// script` block) and run with `uv run <script>`; never create or commit a `.venv`, `node_modules` or `pyproject.toml` inside a skill folder. OpenCode scans every nested `SKILL.md`, and a Playwright venv once leaked three skills
- Pin CDN imports in render templates (see `skills/excalidraw/scripts/render_template.html`); an unpinned "latest" broke rendering on 2026-09-13
- Do not commit or push unless explicitly instructed
