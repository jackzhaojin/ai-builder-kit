# ai-builder-kit

A collection of skills, plugins, and hooks for AI coding agents. Works as a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces), a [Codex plugin marketplace](https://developers.openai.com/codex/plugins), and a plain skills repo for `npx skills`. Every skill is a portable `SKILL.md`, so the same folder works in Claude Code, Codex, and any agent that follows the [Agent Skills spec](https://agentskills.io).

## Available Skills

| Skill | Last Modified | Description |
|-------|--------------|-------------|
| [ai-knowledge-harvester](skills/ai-knowledge-harvester/) | 2026-03-28 | Harvest AI docs from repos into a centralized private knowledge repository |
| [conversation-logger](skills/conversation-logger/) | 2026-05-17 | Log Claude Code / Codex sessions as per-session `YYYY-MM-DD-{N}-{slug}.md` files (date + zero-based stage counter + topic slug — folder sort = chronological order). New day = new file. |
| [chat-conversation-logger](skills/chat-conversation-logger/) | 2026-05-17 | Log Claude.ai chat conversations as `YYYY-MM-DD-{N}-{slug}.md` files with verbatim prompts, attachment metadata, and per-turn tool record. Stage prefix `{N}` is always present so listings stay chronologically sorted. |
| [branded-pptx](skills/branded-pptx/) | 2026-03-29 | Create branded PowerPoint decks from templates — analyzes themes, slide masters, layouts with shape dimensions, text capacity, and visual data tracking. Timestamped run folders. **Requires**: [pptx](https://github.com/anthropics/skills) skill + Python 3.12+ |
| [drawio](skills/drawio/) | 2026-04-27 | Generate `.drawio` XML diagrams in Jack's brand style (swimlane frames, 4-color semantic palette, rounded boxes + cylinders for data stores, orthogonal edges, dashed reserved for return/response). Step 0 interview with multiple-choice defaults; render-view-fix loop with versioned-iteration artifacts (`-v1`, `-v2`, …). Ships with two worked output examples, a sample-input reference, and an evals harness. |
| [hlx-admin-api-executor](skills/hlx-admin-api-executor/) | 2026-10-25 | Interactive AEM Edge Delivery Services Admin API executor |
| [playwright-demo-video](skills/playwright-demo-video/) | 2026-06-11 | Generate polished demo videos (MP4) from Playwright specs — on-screen captions, ElevenLabs AI voiceover with exact timestamp sync, freeze-frame merge, background music. Includes auto-discover mode that scans a project and generates a demo spec. **Requires**: ffmpeg, Node.js 18+, Playwright in the target project, ElevenLabs API key (for voiceover) |
| [excalidraw](skills/excalidraw/) | 2026-09-13 | Generate `.excalidraw` diagrams in Jack's brand style (hand-drawn roughness, Nunito, 7-color semantic palette, frames for grouping) with a mandatory render-view-fix loop. Ships core references, six worked examples with PNG previews, and an evals harness. **Requires**: `uv` (installs Playwright itself on first run) plus a one-time `uv run --with playwright playwright install chromium` |
| [podcast-slides-video](skills/podcast-slides-video/) | 2026-09-07 | Build a YouTube-ready MP4 from narrated audio (NotebookLM overview, recorded talk) plus a slide deck (PDF or PPTX), with slide changes cut to the transcript. Produces the MP4, an auditable cue sheet, a validation contact sheet, and a YouTube chapter list. **Requires**: ffmpeg/ffprobe, `uv` (runs mlx-whisper on Apple Silicon), poppler `pdftoppm`, LibreOffice `soffice` for PPTX input, Python with Pillow and numpy |

## Available Plugins

| Plugin | Last Modified | Description |
|--------|--------------|-------------|
| [hlx-admin-api-executor-guarded](plugins/hlx-admin-api-executor-guarded/) | 2026-10-25 | AEM Edge Delivery Services Admin API executor with PreToolUse guardrails |
| [ai-builder-kit](.claude-plugin/marketplace.json) | 2026-09-13 | Bundle of every skill above as one plugin, for Claude Code (`ai-builder-kit@ai-builder-kit`) and Codex (`.agents/plugins/marketplace.json`). Skills only, no hooks |

## Getting Started

Pick one path. They all read the same `skills/` folder.

### Option A: `npx skills` (any agent, one skill at a time)

```bash
npx skills add jackzhaojin/ai-builder-kit --list                       # see what is available
npx skills add jackzhaojin/ai-builder-kit --skill excalidraw            # into this project
npx skills add jackzhaojin/ai-builder-kit --skill excalidraw -g -a claude-code codex   # global, Claude Code + Codex
npx skills add jackzhaojin/ai-builder-kit -g -y                         # everything, global
npx skills update -g -y                                                 # pull updates later
```

Codex and OpenCode read `~/.agents/skills` directly, so a global install shows up in both with no extra step.

### Option B: Claude Code plugin marketplace

Every skill is a plugin of the same name, and `ai-builder-kit` is a bundle of all of them. Install the bundle or individual skills, not both, or the skills load twice.

```bash
claude plugin marketplace add jackzhaojin/ai-builder-kit
claude plugin install excalidraw@ai-builder-kit                # one skill
claude plugin install ai-builder-kit@ai-builder-kit            # every skill
claude plugin install hlx-admin-api-executor-guarded@ai-builder-kit   # skill + enforced hook
```

Or in a session: `/plugin` > **Marketplaces** > **Add** > `jackzhaojin/ai-builder-kit`, then **Discover**. The same marketplace can be pinned for a team in `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ai-builder-kit": {
      "source": { "source": "git", "url": "https://github.com/jackzhaojin/ai-builder-kit.git" }
    }
  }
}
```

Plugin entries carry no pinned version, so `/plugin update` picks up every push to `main`.

### Option C: Codex and the ChatGPT desktop app

The repo ships `.agents/plugins/marketplace.json` with one plugin, `ai-builder-kit`, that bundles all skills (portable manifest in `plugin.json`).

```bash
codex plugin marketplace add jackzhaojin/ai-builder-kit
```

Then restart the ChatGPT desktop app, open the Plugins Directory, choose the **AI Builder Kit** marketplace, and install. For single skills in Codex, use Option A with `-a codex`.

## Keeping it up to date

Skill entries carry no pinned version, so every push to `main` is an update. Pull it with whichever path you installed from:

| Installed with | Update with |
|----------------|-------------|
| `npx skills` | `npx skills update -g -y` (global) or `npx skills update -p -y` (inside a project) |
| Claude Code marketplace | `/plugin update` in a session, or `claude plugin marketplace update ai-builder-kit` followed by `claude plugin update <name>@ai-builder-kit` |
| Codex marketplace | `codex plugin marketplace upgrade ai-builder-kit`, or reinstall from the Plugins Directory in the desktop app |

## Repo layout

| Path | Purpose |
|------|---------|
| `skills/<name>/SKILL.md` | The skills. Flat layout, one folder per skill |
| `plugins/` | Bundles that need hooks (Claude Code only) |
| `.claude-plugin/marketplace.json` | Claude Code marketplace: one entry per skill, a bundle, and the hook plugins |
| `.agents/plugins/marketplace.json` | Codex marketplace: the bundle |
| `plugin.json` | Portable Agent Plugins manifest for the bundle |
