---
name: excalidraw
description: Generate Excalidraw .excalidraw diagram files. Use when the user asks to create, visualize, draw, or diagram architectures, workflows, pipelines, systems, processes, or concepts. Requires a description of what to diagram — does not analyze codebases automatically. Ask clarifying questions if type, complexity, or sections are unclear.
---

# Excalidraw Diagram Generator

Generate `.excalidraw` JSON files in Jack's brand style (`roughness: 1`, Nunito, 7-color semantic palette, Excalidraw frames for grouping). Every diagram is rendered to PNG and visually validated via a Playwright render-view-fix loop before delivery.

## File Index — READ ALL OF THESE BEFORE GENERATING

Before writing any JSON, read every `references/*.md` file below. They are small, and the rules interact — arrow `x,y` lives in `arrows.md`, but the whitespace rules in `brand-style.md` determine where those coordinates should be; the validation checklist in `validation.md` catches the silent-binding failures hinted at in `element-templates.md`. Round-1 agents who skipped files produced broken arrows and wrong-sized boxes for rules that were documented.

| Path | Purpose |
|------|---------|
| `references/brand-style.md` | Palette, roughness, Nunito, alignment grid, measured whitespace rules, legend patterns, layout shapes. Read this first — every diagram follows these rules regardless of complexity. |
| `references/arrows.md` | Elbowed-arrow recipe, the load-bearing `x, y` derivation formula, midpoint routing, fan-out / convergence / hub-orbit patterns, anti-pattern warnings. Read before placing any arrow; the `x, y` rule is the #1 source of invisible-arrow bugs. |
| `references/element-templates.md` | Copy-paste JSON templates (with Jack's values pre-filled) for text, rectangle, ellipse, line, frame, arrow, legend swatch. Read when generating JSON directly — the arrow template shows the correct `x, y` derivation and reciprocal `boundElements` registration. |
| `references/section-layout.md` | Frame placement algorithm, cross-frame arrow-shape rules, frame-height formula, worked examples. Read for any multi-frame or ≥ 30-element diagram — the Step 0 planning depends on it. |
| `references/visual-patterns.md` | Pattern library: assembly line, fan-out, convergence, hub, tree, side-by-side, gap, loop, cloud. Read once during Step 0 to pick the diagram's overall shape before placing elements. |
| `references/json-format.md` | Excalidraw JSON schema, required vs optional fields, minimal-JSON optimization tricks. Read when debugging JSON-level issues or stripping auto-regenerated metadata. |
| `references/validation.md` | Technical validation checklist: unique IDs, arrow binding sanity, text containerId matches, no diamonds, etc. Run through this before declaring the diagram done. |
| `references/prompt-templates.md` | Prompt templates users copy when requesting a diagram (simple / medium / complex). Skim to understand what a well-structured input looks like; share with users who don't know how to describe what they want. |
| `scripts/render_excalidraw.py` | Renders `.excalidraw` → PNG via headless Chromium + the real @excalidraw/excalidraw library. MANDATORY after every edit; run with `uv run <skill-dir>/scripts/render_excalidraw.py <file>` (uv installs Playwright on first run, cached outside the skill folder). |
| `scripts/analyze.js` | Read-only diagnostic that prints element counts, field distributions, and optimization potential. Run when inspecting an unfamiliar diagram before editing. |
| `scripts/cleanup_excalidraw.py` | Strips `isDeleted: true` elements from the JSON in place. Run before committing so the file only contains live elements. |
| `scripts/optimize_excalidraw.py` | Strips auto-regenerated metadata and null fields (20–50% size reduction). Run before committing to keep the diffs readable. |

## Quick Start

1. Ask the user for missing info (type, complexity, subsystems) — see **Required Information**.
2. **Read every `references/*.md` file.** Do not skip any. Rules interact across files, and the most common round-1 failures were documented rules that were never loaded.
3. **Plan sections first** (Step 0). The layout decision determines whether the diagram will work.
4. Generate JSON. For 30+ element diagrams, build one frame per edit (section-by-section).
5. Render the PNG (`scripts/render_excalidraw.py`) and **look at it**.
6. Iterate 2–4 times fixing anything the render shows that the JSON didn't.

## Required Information

Ensure you have:

1. **Diagram type**: process (workflow, timeline, steps) OR architecture (components, services, infrastructure).
2. **Complexity**: simple (5–10 elements) / medium (15–25) / complex (30+).
3. **Components** and how they connect.
4. **Subsystems** (if 2+): each becomes a frame. For each frame, list which other frames it sends arrows to.

Ask the user:

```
To create your diagram, I need:
1. Process or architecture?
2. Complexity: simple (5–10 boxes), medium (15–25), complex (30+)?
3. Main components / steps?
4. If multiple subsystems: what are the frames, and which connect to which?
```

See `references/prompt-templates.md` for structured prompt templates users can copy.

## Workflow

### Step 0: Plan Sections First

**For any diagram with ≥ 8 elements or 2+ subsystems.** The single most important step.

1. **Consider a flow direction** (soft preference, not a rule):
   - Timelines, chronological sequences, phased rollouts usually read better **left-to-right**.
   - Network traffic, technical request/response sequences, pipeline stages often lean **top-to-bottom**.
   - Holding one direction per diagram tends to look cleaner, but mix if there's a good reason (loops, callbacks, sidebars).

2. **Pick a visual pattern** that matches the argument the diagram makes (see `references/visual-patterns.md`): assembly line, timeline, fan-out, convergence, hub with spokes, tree, side-by-side, gap, loop, cloud.

3. **List subsystems** — each becomes a frame. For each frame, note which other frames it exchanges arrows with, and which edge each cross-frame arrow exits from.

4. **Sketch the frame layout** mentally or on paper. Every cross-frame arrow should have a direct path (one or two bends, midpoint-routed) that does NOT cross a third frame.

5. **Check the signs the layout is wrong** (`references/section-layout.md`):
   - Two frames that exchange many arrows are > 1 frame-width apart.
   - An arrow from A to C passes through B's bounding box.
   - An arrow would need 4+ waypoints to reach its target.
   - Frames < 150px apart with arrows squeezing between.

**Fix by moving frames, not by adding arrow waypoints.** Arrow JSON is determined by layout.

### Step 1: Read ALL References

Read every `references/*.md` listed in the File Index at the top of this document. Short files, interacting rules — skipping any one of them is the main cause of round-1 failures (invisible arrows, wrong-size boxes, missing legends, broken bindings).

### Step 2: Study 2–3 canonical examples (MANDATORY)

Not optional. Pick the 2–3 examples whose patterns most resemble what you're building and **view both the `.png` and the `.excalidraw` JSON** for each. The PNG shows the intended visual; the JSON shows the exact coordinates, frame sizes, and arrow routing Jack uses. You cannot match Jack's style without seeing it.

| Example | Pattern | When to pick it |
|---------|---------|-----------------|
| `references/examples/authoring-patterns.{excalidraw,png}` | Linear assembly line, 3 parallel rows fan-in to shared trunk, no frames, 1 color | Simple left-to-right pipeline diagram with 3–5 rows of input-to-output flow and free-floating column headers. Pick when the argument is "things happen in this order" and no subsystems need grouping. |
| `references/examples/agentic-ai-auth.{excalidraw,png}` | Row-grid (5 rows × 4 cols) + top-left 2×2 legend, dense 170×75 boxes, 4 semantic colors per row | Row-by-row architecture comparison where each row shows the same concept evolving across columns (e.g. "actor → auth → identity → resource"). Pick when you need a table-like grid with semantic color per column and a compact legend. |
| `references/examples/multi-frame-process.{excalidraw,png}` | 2 side-by-side frames, timeline rows of action→outcome→role, top-left 3-color legend | Multi-phase process where each phase has its own frame and the same internal structure repeats (top row actions, middle row outcomes, bottom row roles). Pick when chronology or "phase A vs phase B" is the argument. |
| `references/examples/summit-2026-v2-simple.{excalidraw,png}` | **Hub + 3 orbiting frames**, `mode: "orbit"` arrow bindings, central black rectangle | Architecture where multiple independent subsystems all talk to one central coordinator (event bus, shared document, gateway). Pick when the argument is "everything coordinates through this one thing" — the hub shape is the visual. |
| `references/examples/agent-sdk-and-harness.{excalidraw,png}` | **Side-by-side** 2 frames, each with its own top-right mini-legend (User/Det/Agentic/Mix), no cross-frame arrows | Two parallel architectures worth comparing directly (e.g. old vs new, SDK A vs SDK B). Pick when the frames do NOT exchange arrows — they're independent and the comparison itself is the point. |
| `references/examples/prompts-to-harness.{excalidraw,png}` | **2 multi-step process frames** side-by-side, tight frame padding, dashed retry loop-back, free-floating multi-line Requirements/Outcomes text | Complex process with verbose annotations (requirements lists, outcome notes), 6+ inputs converging into one flow, or iterative loops. Pick when content is dense enough that annotations need room outside boxes. |

### Step 3: Generate JSON

Standard defaults:
- `backgroundColor: "transparent"`, `strokeWidth: 2`, `fontFamily: 5`, `roughness: 1`
- Box 200×100 default, ~100px between rows AND between columns (constant rhythm — see `brand-style.md` measured ranges)
- Labeled shape = TWO elements (shape with `boundElements` + text with `containerId`)
- Arrows: `elbowed: true`, max 4 points, midpoint-routed, stroke = source element's semantic color

Write the `.excalidraw` file directly. Do **not** generate helper/build scripts (`.py`, `.js`, etc.) unless the user explicitly asks for a reusable generator or asks you to modify an existing helper.

For **complex diagrams (30+ elements)**: build one frame per edit. Namespace element IDs per section (e.g. `s1_*`, `s2_*`) or seeds per section (`100xxx`, `200xxx`). Add cross-section arrows last, once all frames are placed.

### Step 4: Run the render

```bash
uv run <skill-dir>/scripts/render_excalidraw.py path/to/diagram.excalidraw
```

`<skill-dir>` is wherever this SKILL.md lives, for example `.claude/skills/excalidraw` or `~/.agents/skills/excalidraw`. First run on a machine: `uv run --with playwright playwright install chromium` downloads the browser. Never create a `.venv` inside the skill folder.

### Step 5: View the PNG (MANDATORY)

`Read` the resulting `.png` and check:

- **Arrows**: any arrow crossing through shapes or third frames? Do arrows land on the correct edge?
- **Text**: clipped, overflowing a container, or overlapping another element?
- **Alignment**: same-row elements share Y + height? same-column elements share X + width?
- **Spacing**: < 150px cramps between frames? > 400px dead whitespace?
- **Frames**: subsystems read as visually distinct groups?
- **Legend**: if multiple colors, is there a legend in the top-left?

On large/tall diagrams, mis-bound connectors and label overlaps are often invisible at full-diagram zoom. Crop zoomed regions of the PNG (e.g. PIL `Image.crop(...)`) and view those crops to confirm each arrow lands on its box edge and labels don't collide — don't trust the full thumbnail alone for binding QA.

### Step 6: Fix & re-render (loop 2–4 times)

If anything is wrong, edit the JSON and re-render.

**If an arrow crosses a third frame, the fix is Step 0 (re-plan the section layout), not a new arrow JSON.**

Do not ship a diagram you haven't looked at.

### Step 7: Technical validation

See `references/validation.md` — run through the JSON-level checklist (IDs unique, arrows bound both ends, text `containerId` matches shape `boundElements`, no diamonds, etc.).

Before committing, optionally run:

```bash
python scripts/cleanup_excalidraw.py path/to/diagram.excalidraw    # strip isDeleted
python scripts/optimize_excalidraw.py path/to/diagram.excalidraw   # strip auto-regen metadata (-20 to -50%)
```

## Critical Rules

1. **Whitespace is pretty.** Jack's canonical diagrams run 10–27% shape area / 73–90% whitespace (measured across all 6 examples). Default box 200×100. **~100px inter-box rhythm is constant** (row gaps AND column gaps). Frame padding flexes with content: ~80–100px L/R when airy, 20–60px when content is verbose (see `multi-frame-process`, `prompts-to-harness`). Top padding always ~20px (frame name sits there). One idea per box. No embedded code-snippet callouts. No subheads inside frames. No captions below boxes unless the label truly can't fit the meaning. **Reduce before you add.** See `references/brand-style.md` § "Whitespace is pretty" for the full measured ranges.
2. **One box size per diagram.** Pick a standard (usually `200×100`, or `~170×75` for dense 4+-column row-grids) and use it for every content box. Don't vary box size to fit a label — tighten the label. Exceptions are meaningful and few: legend swatches are smaller, a container/region shape can be bigger if it represents something fundamentally different. Consistency = readability.
3. **Plan sections first (Step 0).** Everything else depends on this.
4. **Follow the prompt literally.** Don't add column headers, subheads, or explanatory sub-boxes unless the prompt explicitly lists them. Don't expand `(xN)` labels into N boxes — it's one box with an annotation (see `brand-style.md`).
5. **Labels need TWO elements**: shape with `boundElements: [{id, type:"text"}]` + text with `containerId: shapeId`.
6. **Arrows**: `elbowed: true` + `fixedPoint` bindings + 2–4 point paths. Max 4 points. Midpoint-routed. **`x, y` = absolute canvas coord of the first point** (source-edge anchor). See `arrows.md` Hard Rules.
7. **Register every arrow on BOTH endpoints.** Append `{id: arrowId, type: "arrow"}` to source shape's and destination shape's `boundElements`. Missing this silently breaks bindings.
8. **If an arrow needs 5+ waypoints, move a frame** — don't add waypoints.
9. **Never use diamonds.** Arrow bindings break on diamond shapes. Use rectangles.
10. **Container discipline**: default to no container. Aim for < 30% of text elements inside boxes. Prefer free-floating text + lines for section titles, annotations. Rectangles are for structural components, not every label.
11. **Legend top-left** when 2+ semantic colors used; **per-frame mini-legend top-right** when multiple frames share the same palette.
12. **Frame, not dashed rectangle**, for subsystem grouping. Children set `frameId`.
13. **Rounded corners by default** (`roundness: {"type": 3}`). Sharp only for flagged container/boundary shapes.
14. **Render before shipping.** No unlooked-at diagrams.
15. **No helper-file detours by default.** When the deliverable is a diagram, create the `.excalidraw` file itself. Do not create `.py`/`.js` builder files unless the user explicitly asks for one.

## Visual Pattern Library (one-line summaries)

Full details in `references/visual-patterns.md`.

| Pattern | Argues |
|---------|--------|
| Assembly line | "Things happen in this order; each step does this." |
| Timeline | "These things happened at these times." |
| Fan-out | "One thing produces these several." |
| Convergence | "These several produce this one thing." |
| Hub with spokes | "Everything coordinates through this." |
| Tree / hierarchy | "Contains these contains these." |
| Side-by-side | "Compare A vs B." |
| Gap / break | "These two regions are meaningfully separate." |
| Loop / cycle | "This process can repeat." |
| Cloud / boundary | "This whole region is one unit." |

## Scripts Reference

All scripts live in `scripts/`. Run from the skill root.

| Script | When to run | Effect |
|--------|-------------|--------|
| `render_excalidraw.py <file>` | After every generation/edit (MANDATORY, via `uv run`) | Renders .excalidraw → PNG via headless Chromium + @excalidraw/excalidraw |
| `analyze.js <file>` | Inspecting an existing diagram before editing | Read-only diagnostic: element counts, field distributions, optimization potential (Node stdlib) |
| `cleanup_excalidraw.py <file>` | Before committing | Strips `isDeleted: true` elements in place (Python stdlib) |
| `optimize_excalidraw.py <file>` | Before committing | Strips auto-regenerated metadata + null fields in place (20–50% size reduction, Python stdlib) |

**First-run setup** (only for `render_excalidraw.py`): the script carries inline uv metadata, so `uv run` installs the Playwright package into uv's cache automatically. Download the browser once per machine:

```bash
uv run --with playwright playwright install chromium
```

## Troubleshooting / Alternate Export

The default `scripts/render_excalidraw.py` produces PNG via Chromium. If it fails or you need **SVG output** / **dark-mode** / **batch export**, fall back to `excalidraw-brute-export-cli`. In particular, if Chromium hangs with `Page.wait_for_function: Timeout 30000ms exceeded`, don't keep retrying it — go straight to the brute-export fallback, which is reliable:

```bash
# From any directory — global install, no hard-coded path:
npx -y excalidraw-brute-export-cli -i path/to/diagram.excalidraw -o path/to/out.png -f png -s 2 -b true
```

Flags: `-f png|svg`, `-s 1|2|3` (scale), `-b true|false` (white background), `-d true|false` (dark mode). First-run: `npx playwright install firefox` (once per machine).

This is a fallback — Cole's `render_excalidraw.py` is the default for everything the skill generates.

(File Index moved to the top of this document — skim it there.)
