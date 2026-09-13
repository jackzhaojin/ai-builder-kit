# Arrows

Jack's arrow style: **elbowed + fixedPoint bindings + short multi-waypoint paths**. Section-aware routing rules make it work on complex diagrams too.

## Table of contents
- [Default arrow recipe](#default-arrow-recipe)
- [Hard rules](#hard-rules)
- [Soft rules (guidance)](#soft-rules-guidance)
- [Fan-out pattern (one-into-many)](#fan-out-pattern-one-into-many)
- [Convergence pattern (many-into-one)](#convergence-pattern-many-into-one)
- [Staggering arrows leaving the same source](#staggering-arrows-leaving-the-same-source)
- [Anti-pattern: 5-waypoint arrows crossing frames](#anti-pattern-5-waypoint-arrows-crossing-frames)

## Default arrow recipe

```json
{
  "type": "arrow",
  "strokeColor": "<source element's semantic stroke color>",
  "backgroundColor": "transparent",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "elbowed": true,
  "points": [[0, 0], [W, 0]],
  "startBinding": { "elementId": "src", "focus": 0, "gap": 5, "fixedPoint": [1, 0.5] },
  "endBinding":   { "elementId": "dst", "focus": 0, "gap": 5, "fixedPoint": [0, 0.5] },
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

Key points:

- `elbowed: true` — Excalidraw's elbowed router handles the routing.
- `fixedPoint: [x, y]` — unit coordinates on the bound element's edge. `[1, 0.5]` = right-center, `[0, 0.5]` = left-center, `[0.5, 0]` = top-center, `[0.5, 1]` = bottom-center.
- `focus: 0` — centered along the edge; use `focus: -0.3` / `+0.3` to stagger multiple arrows on the same edge.
- `gap: 5` — default 5px gap between arrowhead and bound shape.
- `mode: "orbit"` on bindings when the bound shape is a "hub" with many incoming/outgoing arrows — it distributes arrows around the edges.
- Stroke color = **source element's** semantic stroke color.

## Hard rules

**Arrow `x, y` MUST equal the absolute canvas coordinate of the arrow's first point** (the source-edge anchor). `points` is a list of offsets from `(x, y)`. If you set `x, y = 0, 0`, the arrow renders at canvas origin and is invisible even though bindings look correct.

To derive `x, y`:
1. Take the source shape's `(sx, sy)` top-left and `(sw, sh)` size.
2. Take the source binding's `fixedPoint: [fx, fy]` in unit coords.
3. `x = sx + fx * sw`, `y = sy + fy * sh`. **Do NOT add `gap` to `x, y` yourself.** `gap: 5` is a binding property — the Excalidraw router applies the visual 5px offset at render time. If you pre-offset `x, y` by `gap`, the arrow renders 5px past where it should.

The ±0 tolerance matters: the grader accepts ±10px drift to absorb common confusions, but the canonical rule is that `x, y` equals the unit-point coordinate exactly. Example: source rect at `(400, 300)` size `(200, 100)`, arrow exits right-center (`fixedPoint: [1, 0.5]`). Arrow `x = 600, y = 350` exactly — not `605, 350`.

Example: source rectangle at `(400, 300)` size `(200, 100)`, arrow exits right-center (`fixedPoint: [1, 0.5]`), target at `x=700`. Arrow `x = 400 + 1*200 = 600`, `y = 300 + 0.5*100 = 350`. `points: [[0,0],[100,0]]`.

**Max 4 points in `points`.** 2 for a straight shot, 3 for one bend, 4 only for cross-section arrows. Never 5+. If you find yourself writing 5, the layout is wrong — move a frame.

### Worked 4-point cross-frame arrow (H-V-H)

Source rect at `(400, 300)` size `(200, 100)`. Destination rect at `(1000, 700)` size `(200, 100)`. Arrow exits source right-center (`fixedPoint: [1, 0.5]`), enters destination left-center (`fixedPoint: [0, 0.5]`). Midpoint X = 700.

```json
{
  "type": "arrow",
  "x": 600, "y": 350,
  "width": 400, "height": 400,
  "elbowed": true,
  "points": [[0, 0], [100, 0], [100, 400], [400, 400]],
  "startBinding": { "elementId": "src", "focus": 0, "gap": 5, "fixedPoint": [1, 0.5] },
  "endBinding":   { "elementId": "dst", "focus": 0, "gap": 5, "fixedPoint": [0, 0.5] }
}
```

Derivation:
- `x = src.x + 1 * src.width = 600`
- `y = src.y + 0.5 * src.height = 350`
- `points`: exit right → travel to midX (100 offset) → turn down 400 → travel to dst left (300 offset). Four points total.
- `width, height` = bbox of points array = `(400, 400)`.

Swap to V-H-V for top/bottom exits: exit bottom → travel to midY → turn horizontal → travel to dst top.

**Midpoint-waypoint rule.** For a bent arrow, waypoints lie at the midpoint between source-side `fixedPoint` and target-side `fixedPoint`. Horizontal → vertical → horizontal routing goes: source-edge → midX → midX (at target Y) → target-edge.

**Cross-section rule.** If start and end elements are in different frames, the arrow must (a) exit the source frame, (b) travel through empty canvas, (c) enter the destination frame. Explicit waypoints must lie outside both frame bounding boxes. If the path has to cross a third frame, the layout is wrong — move a frame (see section-layout.md).

**Arrow `x, y, width, height` must match the `points` bounding box.** If `points: [[0,0], [200, 0]]`, then `width: 200, height: 0`. Mismatch = the render places the arrow in the wrong spot.

**Stroke color follows source element's semantic color.** An arrow leaving an actor (green) box uses `#2f9e44`. An arrow leaving a resource (blue) box uses `#1971c2`. See `brand-style.md`.

**Register the arrow on BOTH endpoints.** After creating the arrow, append `{"id": "<arrowId>", "type": "arrow"}` to BOTH the source shape's and destination shape's `boundElements` arrays. Missing this causes bindings to silently break on re-render.

**`mode: "orbit"` on target binding when 3+ arrows converge on the same target** — regardless of whether target is a dedicated hub shape or a regular rectangle. Orbit distributes arrows around target edges instead of stacking on one `fixedPoint`. For a regular rectangle receiving many arrows, use `fixedPoint: [0.5, 0.5]` (center) + `mode: "orbit"` and let the router place entries.

**Orbit spacing is router-chosen.** `mode: "orbit"` guarantees separation, not exact pixel placement. Don't depend on evenly spaced entry points; if the distribution looks awkward, move the surrounding shapes or widen the gap instead of trying to micromanage the orbit result.

**Solid vs dashed.** Solid = primary flow. Dashed (`strokeStyle: "dashed"`) = optional / async / callback.

## Soft rules (guidance)

- For same-row horizontal arrows, prefer a straight 2-point path and let `focus: 0` + `fixedPoint: [1, 0.5]` → `[0, 0.5]` do the work.
- For same-frame one-bend arrows, use 3-point paths via midpoint.
- For cross-frame arrows, use 4-point paths: exit edge → first midpoint → second midpoint → entry edge.
- Prefer `focus` (−0.3 / 0 / +0.3) for staggering, `fixedPoint` for edge selection.

## Fan-out pattern (one-into-many)

One source, N targets, visually shared trunk. Used throughout Jack's diagrams (phase splits, AI-output fan-outs, branching decisions).

```
                 ┌──→ [ Target A ]
                 │
[ Source ]──┬────┼──→ [ Target B ]
            │    │
            │    └──→ [ Target C ]
```

Recipe:
- **N separate arrows**, one per source → target.
- **All N arrows share the same source `fixedPoint`** (e.g. `[0.5, 1]` for bottom-center, `[1, 0.5]` for right-center).
- Each arrow has a **3-point path**: source edge → shared trunk Y (or X) → target edge.
- Target-side `fixedPoint` varies per arrow (each target has its own entry edge).
- `elbowed: true`, `mode: "orbit"` on the source binding.

Because the elbowed router sees N arrows bound to the same `fixedPoint` on the same element, it visually overlaps the trunk segments — you get the "tree branch" shape for free, no explicit `type: "line"` trunk element needed.

**Example JSON** (3 targets fanning out from `src` bottom-center):

```json
// Arrow 1: src -> A
{ "type": "arrow", "elbowed": true, "points": [[0,0],[0,80],[-160,80]],
  "startBinding": {"elementId":"src","focus":0,"gap":5,"fixedPoint":[0.5,1],"mode":"orbit"},
  "endBinding":   {"elementId":"tgtA","focus":0,"gap":5,"fixedPoint":[1,0.5]}
}
// Arrow 2: src -> B
{ "type": "arrow", "elbowed": true, "points": [[0,0],[0,80]],
  "startBinding": {"elementId":"src","focus":0,"gap":5,"fixedPoint":[0.5,1],"mode":"orbit"},
  "endBinding":   {"elementId":"tgtB","focus":0,"gap":5,"fixedPoint":[0.5,0]}
}
// Arrow 3: src -> C
{ "type": "arrow", "elbowed": true, "points": [[0,0],[0,80],[160,80]],
  "startBinding": {"elementId":"src","focus":0,"gap":5,"fixedPoint":[0.5,1],"mode":"orbit"},
  "endBinding":   {"elementId":"tgtC","focus":0,"gap":5,"fixedPoint":[0,0.5]}
}
```

**Common mistake**: giving each arrow in a fan-out its own distinct source `fixedPoint`. That produces N visually-independent arrows radiating out — not the clean shared-trunk shape.

## Convergence pattern (many-into-one)

N sources, one target, shared trunk. Mirror of fan-out. Used for inputs merging into a pipeline, prerequisites funneling into a decision, multiple stakeholders feeding one output.

```
[ Source A ]──┐
              │
[ Source B ]──┼────→ [ Target ]
              │
[ Source C ]──┘
```

Recipe:
- N separate arrows.
- **All N arrows share the same target `fixedPoint`** (e.g. `[0, 0.5]` for left-center).
- Source-side `fixedPoint` varies per arrow.
- 3-point path per arrow: source edge → shared trunk → target edge.
- `elbowed: true`, `mode: "orbit"` on the target binding.

**Orbit works on regular rectangles too — the target does NOT need to be a dedicated hub shape.** Use `mode: "orbit"` whenever 3+ arrows converge on the same target, whether the target is a 280×140 hub or a regular 200×100 rectangle. Orbit auto-distributes entry points around the target edges so arrows don't stack on one `fixedPoint`.

## Staggering arrows leaving the same source

When you want multiple arrows leaving the same edge (not a fan-out) to land on *different* targets, keep `fixedPoint` at the edge center but vary `focus`:

```json
// 3 arrows leaving the right edge of `src`, staggered vertically
{ "startBinding": {"elementId":"src","focus":-0.3,"gap":5,"fixedPoint":[1,0.5]} }
{ "startBinding": {"elementId":"src","focus": 0.0,"gap":5,"fixedPoint":[1,0.5]} }
{ "startBinding": {"elementId":"src","focus": 0.3,"gap":5,"fixedPoint":[1,0.5]} }
```

`focus` ∈ `[-1, +1]` shifts the binding point along the edge. Use before reaching for different `fixedPoint` values — staggering via `focus` keeps the diagram feeling like it comes from one source.

**Prefer `focus` staggering (-0.3 / 0 / +0.3). Use different `fixedPoint` values only when arrows leave physically different edges** (e.g. one arrow from right-center, another from bottom-center). Shifting `fixedPoint` within the same edge produces visually disconnected arrows that look like unrelated siblings.

## Anti-pattern: 5-waypoint arrows crossing frames

Bad (from the broken `continuous-agent-architecture-ai-default` diagram):

```json
"points": [[0,0], [0,150], [-200,150], [-200,300], [-470,300]]
```

This arrow connects two elements in frames at opposite corners with three other frames in between. The 5 waypoints exist **because the layout forces the arrow to travel around 3 subsystems**. No arrow JSON change fixes this.

**Fix**: re-plan the frame layout so the two connected elements are in adjacent frames with a direct path (see section-layout.md, Step 0 of the workflow).

Warning signs to stop and re-plan:
- Writing a 5th point in a `points` array → the layout is wrong.
- A waypoint falls inside a third frame's bounding box → the layout is wrong.
- Two frames that exchange many arrows sit far apart → move them closer.
- Frames < 150px apart with arrows squeezing between → space them out.
