# Excalidraw skill

Generate `.excalidraw` diagram files in Jack's brand style (`roughness: 1` hand-drawn, Nunito, 7-color semantic palette, frames for grouping) with a mandatory render-view-fix loop so diagrams are visually validated before delivery.

## First-run setup

The render pipeline needs Playwright + Chromium; everything else runs on stdlib. `scripts/render_excalidraw.py` carries inline uv metadata, so `uv run` installs Playwright into uv's cache (outside the skill folder) the first time it runs. Download the browser once per machine:

```bash
uv run --with playwright playwright install chromium
```

The renderer pins `@excalidraw/excalidraw@0.18.1` from jsdelivr in `scripts/render_template.html`; bump the version there when upgrading, and keep it pinned so a CDN rebuild of "latest" cannot break rendering.

Do not run `uv sync` or create a `.venv` inside the skill: agents such as OpenCode scan every nested `SKILL.md`, and the Playwright package ships three skills of its own that would leak into the agent.

## Usage

Invoke the skill by asking Claude for a diagram:

```
Create a process diagram showing our build pipeline from git push to deploy.
```

Or with the structured templates in `references/prompt-templates.md` (copy the one that matches your target complexity).

Claude follows this workflow (see `SKILL.md`):
1. **Plan sections first** (Step 0) — most important step.
2. Read core references (brand-style, arrows, element-templates).
3. Generate JSON (section-by-section for 30+ element diagrams).
4. Run `scripts/render_excalidraw.py` to produce a PNG.
5. View the PNG and fix what the render reveals.
6. Loop 2–4 times until the PNG looks right.

## Customize the brand

Edit `references/brand-style.md` to change:
- **Palette** — 7-color semantic mapping (actor / auth / resource / member / AI / neutral / muted).
- **Defaults** — roughness, font family, stroke width, default box height.
- **Alignment grid** — row/column spacing rules.
- **Layout patterns** — horizontal flow / framed subsystems / hub with spokes.

Everything else in the skill references these values, so a single edit cascades.

## File layout

```
.
├── SKILL.md                     Workflow, critical rules, scripts reference
├── README.md                    (this file)
├── .gitignore                   Ignore .venv, *.png, uv.lock, __pycache__
├── references/
│   ├── brand-style.md           Palette + alignment grid + legend
│   ├── arrows.md                Arrow recipe + fan-out/convergence + anti-pattern
│   ├── element-templates.md     Copy-paste JSON per element type
│   ├── section-layout.md        Frame placement (Step 0)
│   ├── visual-patterns.md       Pattern library
│   ├── json-format.md           JSON schema + minimal-format optimization
│   ├── validation.md            Technical validation checklist
│   ├── prompt-templates.md      User-facing prompt templates (simple / medium / complex)
│   └── examples/                6 canonical .excalidraw + .png pairs
└── scripts/
    ├── render_excalidraw.py     Render PNG via headless Chromium (mandatory)
    ├── render_template.html     HTML shim that loads @excalidraw/excalidraw
    ├── analyze.js               Read-only diagnostic
    ├── cleanup_excalidraw.py    Strip isDeleted elements
    └── optimize_excalidraw.py   Strip auto-regen metadata
```

## Fallback: SVG / dark-mode / batch export

Cole's `render_excalidraw.py` covers 95% of the render-view-fix loop — it produces PNG only. If you need SVG, dark-mode, or batch rendering of a whole directory, fall back to `excalidraw-brute-export-cli` (Firefox-based, outside the skill):

```bash
# Global install (no hard-coded path, works from any directory):
npx -y excalidraw-brute-export-cli -i in.excalidraw -o out.png -f png -s 2 -b true
```

Flags: `-f png|svg`, `-s` scale, `-b` white bg, `-d` dark mode. First run: `npx playwright install firefox` once per machine.

## Credit

The render pipeline (`render_excalidraw.py`, `render_template.html`) is adapted from [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill). Everything else — brand, arrow patterns, example diagrams, section-layout methodology — is Jack's.
