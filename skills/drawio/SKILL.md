---
name: drawio
description: Generate draw.io diagrams (`.drawio` XML files) from detailed user prompts, in Jack's brand style. Use when the user asks to create, visualize, draw, or diagram architectures, workflows, pipelines, systems, or processes in draw.io / diagrams.net / XML form. Requires a description of what to diagram — does not analyze codebases automatically. Ask clarifying questions if diagram type, complexity, or subsystems are unclear. Every diagram is exported to PNG via the draw.io CLI and visually validated in a render-view-fix loop before delivery.
---

# Draw.io Diagram Generator

Generate `.drawio` XML files in Jack's brand style (swimlane frames for grouping, 4-color semantic palette, `rounded=1`/`arcSize=15` boxes, orthogonal edges, matching stroke+font colors). Every diagram is exported to PNG via the **draw.io CLI** (macOS: `/Applications/draw.io.app/Contents/MacOS/draw.io`) and **you Read the PNG and check it** before declaring done. **Never pass `-e` / `--embed-diagram`** — it breaks Claude Code's image reader.

## File Index — READ ALL OF THESE BEFORE GENERATING

Before writing any XML, read every `references/*.md` file below. They are small, and the rules interact — edge `exitX/entryX` lives in `connectors.md`, but the whitespace and frame-padding rules in `diagram-style.md` determine where those connection points should land; the validation checklist in `validation.md` catches the silent-binding failures that cause invisible arrows and edges whose `parent` doesn't match their source box's parent. Round-1 agents who skipped files produced edges that rendered as straight lines through the wrong frame, legends outside the swimlane, and italic box text.

| Path | Purpose |
|------|---------|
| `references/xml-format.md` | `mxfile` structure, `mxCell` elements (vertices + edges), swimlanes, waypoints, loops, bidirectional edges. Read first — the skeleton must be correct before style matters. |
| `references/diagram-style.md` | Palette, roughness, Helvetica, layout patterns (vertical / feedback / fan-out), spacing grid, legend placement, box sizing. Read this to get the look right — every diagram follows these rules regardless of complexity. |
| `references/connectors.md` | Edge anatomy, `exitX/entryX` recipe, **same-side feedback-loop rule**, fan-out stagger, arrow types, edge-label placement. Read before placing any edge; same-side rule is the #1 source of "my loop looks weird" bugs. |
| `references/brand-colors.md` | 4-color semantic palette (User/Det/Agentic/Mix) with BOTH `strokeColor` AND `fontColor` matched, and dashed usage narrowed to response/return semantics. Read when picking colors. |
| `references/validation.md` | Technical + style validation checklist (unique IDs, source/target valid, edge parent matches source parent, `fontStyle=0` on boxes, etc). Run through before declaring the diagram done. |
| `references/cli.md` | draw.io CLI export reference: platform paths, flags, **the `-e` flag is forbidden** (breaks Claude Code's image reader), PNG vs SVG tradeoffs. Read before running any export. |
| `references/examples/agent-sdk-harness.{drawio,png,svg}` | **Best example.** Single-swimlane comparison diagram, feedback loops via same-side exit/entry, dashed retry edges, italic edge labels, 4-color semantic palette, legend top-right. Study the JSON *and* the PNG side by side — the PNG shows the visual, the XML shows the coordinates, parent bindings, and edge routing Jack uses. You cannot match Jack's style without seeing both. |
| `references/examples/multi-container-3tier.{drawio,png,svg}` | Multi-container pattern: 3 side-by-side swimlane frames with cross-frame edges at `parent="1"` (not inside any frame), local-to-frame edges at `parent="frame-id"`. Study when the diagram has ≥ 2 subsystems that talk to each other. |
| `references/examples/sample-input.md` | Canonical *input* structure for diagram generation. Use it as the target shape for user-provided markdown/specs before writing XML. |

## Quick Start

1. Ask the user for missing info (type, complexity, subsystems) — see **Required Information**.
2. Reconcile prompt claims vs source document claims before diagramming.
3. **Read every `references/*.md` file.** Do not skip any. Rules interact across files.
4. **Plan sections first** (Step 0). Pick the visual pattern; sketch frame layout; verify no edge has to cross a third frame.
5. Generate XML. For multi-frame diagrams, **build one frame per edit** — place frame + its internal boxes + its internal edges, render + look, then add the next frame. Cross-frame edges come last.
6. Export to PNG via the CLI (`-x -f png -b 10`, **no `-e`**) and **Read the PNG**.
7. Iterate 2–4 times fixing anything the render shows that the XML didn't.

## Required Information

Ensure you have:

1. **Diagram type**: process (workflow, timeline, steps) OR architecture (components, services, infrastructure).
2. **Complexity**: simple (5–10 boxes) / medium (15–25) / complex (30+).
3. **Components** and how they connect.
4. **Subsystems** (if 2+): each becomes a swimlane frame. For each frame, list which other frames it sends edges to.

When required info is missing, ask **multiple-choice questions with a recommended default** instead of open-ended prompts. Keep it fast and concrete:

1. "Diagram type?" → Architecture (**Recommended**) / Process
2. "Layout?" → Multi-frame by subsystem (**Recommended**) / Single frame / Hybrid
3. "Cross-cutting infra placement?" → Shared bar/lane (**Recommended**) / Inside each frame / Omit
4. "Exceptions/unknowns style?" → Solid line + annotation (**Recommended**) / Dedicated callout box / Minimal labels
5. "Color semantic axis?" → Determinism (default palette, **Recommended**) / Ownership / Lifecycle / None

Then ask the user:

```
To create your diagram, I need:
1. Process or architecture?
2. Complexity: simple (5–10 boxes), medium (15–25), complex (30+)?
3. Main components / steps?
4. If multiple subsystems: what are the frames, and which connect to which?
```

## Workflow

### Step 0: Plan Sections First

**For any diagram with ≥ 8 boxes or 2+ subsystems.** The single most important step — layout decisions made here determine whether the diagram will work.

1. **Pick a flow direction** (soft preference, not a rule):
   - Timelines, chronological sequences, phased rollouts usually read better **left-to-right**.
   - Technical request/response flows, pipelines, and data transforms often lean **top-to-bottom**.
   - Holding one direction per frame tends to look cleaner; mix only if there's a good reason (loops, callbacks, sidebars).

2. **Pick a visual pattern** that matches the argument the diagram makes: assembly line, fan-out, convergence, hub with spokes, side-by-side comparison, tree, loop. Jack's two canonical examples cover the two most common:
   - **Single-frame feedback process** → `agent-sdk-harness.drawio`.
   - **Multi-container architecture with cross-frame flow** → `multi-container-3tier.drawio`.

3. **List subsystems** — each becomes a swimlane frame (`style="swimlane;..."`). For each frame, note which other frames it exchanges edges with, and which edge each cross-frame arrow exits from.

4. **Sketch the frame layout** mentally or on paper. Every cross-frame edge should have a direct path (orthogonal, one or two bends) that does NOT cross a third frame's bounding box.

5. **Check the signs the layout is wrong** (`references/diagram-style.md`):
   - Two frames that exchange many edges are separated by a third frame.
   - Frames < 100px apart with edges squeezing between them.
   - An edge would need to jump over another frame to reach its target.
   - Dead whitespace > 300px between neighboring frames with no edges across.

6. **Reconcile prompt vs source before finalizing layout.** If the prompt asserts grouping, ownership, or dependency claims that conflict with the source markdown/spec, stop and ask for confirmation before generating XML. Prefer source-of-truth documents over summary prompt labels when they disagree.

**Fix by moving frames, not by hand-routing waypoints.** Edge XML is determined by layout.

### Step 1: Read ALL References

Read every `references/*.md` listed in the File Index at the top of this document. Short files, interacting rules — skipping any one of them is the main cause of round-1 failures (edges whose `parent` doesn't match, legends outside swimlanes, italic box text, colors that don't match font).

### Step 2: Study the canonical example(s) (MANDATORY)

Not optional. For the pattern you picked in Step 0, open **both the `.drawio` XML and the `.png`** side by side:

| Example | Pattern | When to pick it |
|---------|---------|-----------------|
| `references/examples/agent-sdk-harness.{drawio,png}` | Single swimlane, ~30 boxes, feedback loops via same-side exit/entry, dashed retry edges (response-direction), italic HTML edge labels, 4-color legend top-right | Process/architecture that reads as one coherent subsystem. Most common default. Pick when the whole thing is "how one system works." |
| `references/examples/multi-container-3tier.{drawio,png}` | 3 side-by-side swimlane frames, cross-frame edges at `parent="1"`, per-frame internal edges at `parent="frame-id"`, 1-color default with accent boxes | Architecture where 2–4 subsystems pass data between each other. Pick when the argument is "this container does X, this container does Y, and here's how they talk." |
| `references/examples/sample-input.md` | High-quality source markdown with explicit subsystems, ownership, data stores, and style intents | Use as a checklist/template when user input is ambiguous or incomplete. |

The PNG shows the visual target. The XML shows the exact attribute patterns — parent bindings, edge routing, `exitX/entryX` values, legend coordinates — that Jack's diagrams use. You cannot match Jack's style without seeing both.

### Step 3: Generate XML

Standard defaults (see `references/xml-format.md`, `diagram-style.md`):
- Wrapper: `mxfile > diagram > mxGraphModel > root` with `mxCell id="0"` and `mxCell id="1" parent="0"` first
- Frame: `style="swimlane;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1e1e1e;strokeWidth=2;fontSize=14;fontStyle=0;fontColor=#1e1e1e;startSize=30;rounded=0;"`
- Box: `rounded=1;arcSize=15;fillColor=#ffffff;strokeWidth=2;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontFamily=Helvetica;fontStyle=0` (default 160×60 — tighten before growing)
- Edge: `edgeStyle=orthogonalEdgeStyle;rounded=0;strokeWidth=2;endArrow=classic;endFill=1`
- Color rule: `strokeColor` AND `fontColor` must match for every color-coded element.

**Key parent rules** (easy to get wrong):
- Elements **inside a frame** → `parent="frame-id"` with coordinates relative to the frame's origin (NOT the page).
- Edges **between two boxes in the same frame** → `parent="frame-id"` (same as the boxes).
- Edges **between two boxes in different frames** → `parent="1"` (top-level).
- Legend items → same parent as the frame's content (inside the frame, top-right).

**Build one frame per edit** for multi-frame (≥ 2 frame) diagrams. Namespace box IDs per frame (`s1-box-*`, `s2-box-*`) so future edits don't accidentally collide. Add cross-frame edges **last**, after all frames are in place.

Write the `.drawio` file directly. Do **not** generate helper/build scripts (`.py`, `.js`, XSLT transforms) unless the user explicitly asks for a reusable generator.

### Step 4: Export PNG via the CLI (Versioned Artifacts)

```sh
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -b 10 -o path/to/diagram.png path/to/diagram.drawio
```

For iterative runs, never overwrite artifacts. Use version-suffixed filenames:
- `diagram-v1.drawio`, `diagram-v1.png`
- `diagram-v2.drawio`, `diagram-v2.png`
- etc.

The latest version can also be copied/symlinked to `diagram.drawio` + `diagram.png` if needed, but keep all intermediate versions.

**Never pass `-e` / `--embed-diagram`** — it embeds the full XML into the image and breaks Claude Code's Read tool for images. See `references/cli.md` for platform-specific paths (Linux, Windows, WSL2) and SVG fallback.

If the user wants both formats, run the export twice (`-f png` and `-f svg`). PNG is what you (the model) Read in Step 5; SVG is for the human to view with adaptive light/dark theming.

### Step 5: View the PNG (MANDATORY)

`Read` the resulting `.png` and look at it. Check, in this order:

1. **Edges don't cross non-endpoint boxes (HARD FAIL).** Trace every edge with your eyes from source to target. If an edge's routed path passes *through* a box that is NOT its source and NOT its target, that is a hard fail — redo the layout. The draw.io auto-router is not smart enough to avoid non-endpoint boxes; you control this by where you place the boxes. Fixing this is Step 0 (move the offending box or frame), not adding waypoints.
2. **Max 2 turns per edge.** An orthogonal edge should have at most 2 elbow bends between source and target. If an edge looks like it makes a U-turn, snakes around, or zig-zags, either the layout is wrong (boxes are in the wrong order) or you're routing around something that shouldn't be in the way. Fix by moving boxes, not by accepting a 4-turn path.
3. **Converging arrows merge into ONE bind point on the target.** When 3+ edges end at the same target box, **every edge enters at the exact same connection point** — identical `entryX` AND identical `entryY`. The arrowheads visually stack at one spot; the tails fan out to reach their sources. *Good:* 4 arrows all entering the target at `entryX=0;entryY=0.5` (left-middle), arrowheads overlapping. *Bad:* 4 arrows entering at staggered `entryY` positions (0.2, 0.4, 0.6, 0.8) — this looks like a spray array, not a convergence. *Worse:* 4 arrows coming in from N/S/E/W (octopus). **Multiple edges sharing the same bind point is correct, not a bug.** Don't stagger entries to give each arrow its own landing spot.
4. **Edges land on the correct side.** Bottom→top for vertical flow, right→left for horizontal, same-side for feedback loops.
5. **Text**: clipped, overflowing a box, or bleeding into the box border? Italic where it shouldn't be?
6. **Alignment**: same-row boxes share Y + height? same-column boxes share X + width? `gridSize=10` respected (coordinates snap to multiples of 10)?
7. **Spacing**: < 30px cramps between boxes, or > 200px dead whitespace inside a frame?
8. **Frames**: subsystems read as visually distinct swimlanes (black border, 30px title header, clear internal layout)?
9. **Legend**: if 2+ semantic colors are used, is there a legend (top-right inside the frame for single-frame, top-left at the canvas level for multi-frame)?
10. **Colors**: every color-coded box has matching stroke AND font — no blue-box-with-black-text leaks?
11. **Edge labels sit near their arrow body.** A free-floating label 300px away from the arrow it annotates is visually orphaned; it should be within ~40px of the arrow's midpoint.

**Do not ship a diagram you haven't looked at.** Claiming "done" without Reading the PNG is the single biggest regression the eval caught. The first three checks above are the ones that were missing from iteration 1 and caused visually-wrong-but-XML-valid outputs.

### Step 6: Fix & re-render (loop 2–4 times, keep every version)

If anything is wrong, edit the XML and re-export. Typical fixes:
- Edge crossing a third frame → **Step 0 (re-plan the layout)**, not a new waypoint.
- Feedback loop looks weird → switch to same-side exit/entry (`exitX=0;exitY=0.5;entryX=0;entryY=0.5`).
- Edge drawn straight line through a box → edge `parent` doesn't match the connected boxes' parent; fix `parent`.
- Colors don't match → set BOTH `strokeColor` AND `fontColor`.
- Italic text on boxes → `fontStyle=0` (not `2`).

Re-Read the PNG after each fix. Increment version suffix on each pass; never overwrite prior `.drawio` / `.png` outputs.

### Step 7: Technical validation

Run through the checklist in `references/validation.md` before declaring done:
- All IDs unique
- Every edge's `source` and `target` exist in the document
- Edge `parent` matches both endpoints' parent (or `parent="1"` for cross-frame)
- Every vertex has `vertex="1"` and a child `<mxGeometry>`; every edge has `edge="1"` and a child `<mxGeometry relative="1">`
- Edge labels (if any) have `connectable="0"` and `parent="edge-id"` (parent is the edge, not the frame)
- No diamonds (bindings break on diamond shapes — use rounded rectangles)

## Critical Rules

1. **Edges must not cross non-endpoint boxes.** If you trace an edge with your eyes and it passes *through* a box that is neither its source nor its target, the diagram fails. The draw.io router won't help you — this is controlled by where you place boxes and frames. Fix is **layout, not waypoints**: move the offending box, widen a gap, or reorder so the routing space is clear. This is the most-missed quality gate and is checked first in Step 5.
2. **Max 2 turns per edge. Converging arrows merge into ONE bind point.** An orthogonal edge should have at most 2 elbow bends. If 3+ edges land at the same target, **they all enter at the exact same connection point** — identical `entryX` AND identical `entryY`, not staggered. The arrowheads visually stack at one spot on the target; the tails fan out to the sources. Multiple edges sharing one bind point is not a bug — it's the correct pattern. *Good:* 4 arrows all targeting `entryX=0;entryY=0.5`. *Bad:* 4 arrows at entryY 0.2/0.4/0.6/0.8 (spray array). *Worse:* 4 arrows arriving from N/S/E/W (octopus). Fix by using the same bind point on the target for every converging edge.
3. **Plan sections first (Step 0).** Everything downstream depends on frame placement; fixing layout afterward is 10× more work than fixing it upfront. Rules 1 and 2 are almost always caused by skipping Step 0.
4. **Render and Read the PNG before shipping.** No unlooked-at diagrams. The XML can validate as perfect and still look broken — rules 1 and 2 in particular can only be caught by looking.
5. **Never pass `-e` to the CLI.** It breaks Claude Code's image reader — a `.png` with embedded XML becomes unreadable by the Read tool. Keep the `.drawio` file as the editable source of truth alongside the exported image.
6. **Build one frame per edit** for 2+ frame diagrams. Place the frame + its internal boxes + its internal edges, render + look, then move to the next frame. Cross-frame edges come last, after all frames exist.
7. **Edge `parent` must match context.** Internal edge → same `parent` as its endpoints' frame. Cross-frame edge → `parent="1"`. Getting this wrong causes edges that render as straight lines through the wrong part of the canvas.
8. **Match `strokeColor` AND `fontColor`** on every color-coded element. A blue box with black text is a bug, not a style choice.
9. **Same-side exit/entry for feedback loops.** Draw.io auto-routes correctly when both ends of a loop use the same side (`exitX=0;entryX=0` for left, `exitX=1;entryX=1` for right). No waypoints needed.
10. **Never use diamond shapes.** Edge bindings break on diamonds. Use `rounded=1` rectangles for decisions too.
11. **`fontStyle=0` on boxes, `fontStyle=2` (italic) only on edge labels.** Boxes default to italic when omitted — this is the #1 text-style regression.
12. **Legend inside the frame, top-right (single-frame diagrams); top-left at canvas level (multi-frame).** Legend items 100×30, `fontSize=12`, 40px vertical spacing.
13. **One box size per diagram.** Pick a standard (usually 160×60 for one-line labels, 180×80 for two-line) and hold it. Legend swatches (100×30) are the one intentional exception.
14. **Snap to 10px grid.** `gridSize=10` at the `mxGraphModel` level; every coordinate should be a multiple of 10.
15. **Keep the `.drawio` file.** It's the re-editable source of truth. Never try to round-trip edits through the exported image.
16. **No helper-file detours.** When the deliverable is a diagram, create the `.drawio` file itself. Do not create `.py`/`.xslt`/`.js` builder files unless the user explicitly asks for one.

## Quick Reference

### Brand Colors

| Role | Hex | Usage |
|------|-----|-------|
| User/Default | `#1e1e1e` | Input, output, standard elements |
| Deterministic | `#1971c2` | Predictable logic, scripted flows |
| Agentic | `#e03131` | AI-driven, dynamic, unpredictable |
| Mix | `#f08c00` | Hybrid components |

### Standard Style Snippets

```
Box: rounded=1;arcSize=15;fillColor=#ffffff;strokeWidth=2;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontFamily=Helvetica;fontStyle=0
Edge: edgeStyle=orthogonalEdgeStyle;rounded=0;strokeWidth=2;endArrow=classic;endFill=1
Frame: swimlane;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1e1e1e;strokeWidth=2;fontSize=14;fontStyle=0;fontColor=#1e1e1e;startSize=30;rounded=0
Dashed (response/return only): append dashed=1;dashPattern=8 8;
Feedback-left loop: append exitX=0;exitY=0.5;entryX=0;entryY=0.5;
Feedback-right loop: append exitX=1;exitY=0.5;entryX=1;entryY=0.5;
```

### Page Defaults

```
<mxGraphModel dx="1908" dy="840" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2200" pageHeight="1400" math="0" shadow="0">
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Edge draws as straight diagonal line | Edge `parent` doesn't match boxes' parent | Set edge `parent="frame-id"` for internal, `parent="1"` for cross-frame |
| Edge doesn't render at all | `source` or `target` ID doesn't exist | Verify both IDs; check for typos |
| Feedback loop routed around the whole frame | Exit/entry on different sides | Use same-side (both `exitX=0;entryX=0` or both `exitX=1;entryX=1`) |
| Italic box text | `fontStyle` omitted or `=2` | Set `fontStyle=0` on boxes |
| Colors don't match | Only `strokeColor` set | Set BOTH `strokeColor` AND `fontColor` |
| PNG is unreadable by Claude | `-e` / `--embed-diagram` flag passed | Re-export WITHOUT `-e` |
| Legend outside the frame | Legend items `parent="1"` instead of frame | Set `parent="frame-id"` on every legend item |
| Multi-frame diagram's cross-edge hidden | Cross-frame edge inside a frame | Move to `parent="1"` |
