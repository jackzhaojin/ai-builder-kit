# Section Layout (Step 0)

The single most important step for any multi-subsystem diagram. **Layout is the root cause of most broken diagrams** — not arrow JSON, not validation, not color choice. Plan frames before placing any shape.

## Table of contents
- [Why layout comes first](#why-layout-comes-first)
- [The algorithm](#the-algorithm)
- [Flow direction (soft preference)](#flow-direction-soft-preference)
- [Frame spacing](#frame-spacing)
- [Cross-frame arrow paths](#cross-frame-arrow-paths)
- [Signs the layout is wrong](#signs-the-layout-is-wrong)
- [Worked example: hub with spokes](#worked-example-hub-with-spokes)
- [Worked example: side-by-side architectures](#worked-example-side-by-side-architectures)

## Why layout comes first

Excalidraw's arrow router is smart but not magic. If you place two frames at opposite corners of the canvas with three other frames in between, **no arrow recipe** will produce a clean path between them. You'll end up with:
- 5+ waypoint arrays fighting the elbowed router.
- Arrows cutting through the middle of third frames.
- Zigzag paths that make the diagram look incoherent.

The fix is always the same: move a frame. You cannot fix a layout problem at the arrow layer. Arrow JSON is determined by layout; plan the layout so the arrow rules in `arrows.md` (max 4 points, midpoint-routed, no third-frame crossings) can all be followed.

## The algorithm

For any diagram with 2+ subsystems (roughly: any diagram with 8+ elements, or any diagram with frames):

1. **List subsystems.** Each becomes one frame. Write the name of each.
2. **List cross-frame arrows.** For each, note: source frame, target frame, which edge of source frame it exits, which edge of target frame it enters.
3. **Pick a canvas arrangement.** See the patterns below. Pick based on arrow topology:
   - **All-to-one** (N frames funneling to one) → hub with spokes.
   - **Linear pipeline** (A → B → C → D) → row (left-to-right) or column (top-to-bottom).
   - **Parallel subsystems** (A and B both produce outputs independently) → side-by-side.
   - **Loop / feedback** (A → B → C → A) → cycle layout (row with a return arrow below).
4. **Place frames with ≥200px clearance** between adjacent frames along the arrow's axis. Less tight than that and arrows squeeze between; more than ~400px is visual dead space.
5. **Trace each cross-frame arrow on paper.** Does the path cross a third frame's bounding box? If yes, swap frame positions. Does the path have more than 4 points? Swap frame positions.
6. **Only then** start filling in elements within each frame.

## Flow direction (soft preference)

These are tendencies, not rules. Use whichever direction genuinely serves the content.

- **Left-to-right** tends to read better for: timelines, chronological sequences, phased rollouts, transformation pipelines (input → output).
- **Top-to-bottom** often leans better for: network traffic, technical request/response sequences, assembly-line processing stages.

Holding one direction per diagram usually looks cleaner. Mix freely if there's a good reason (loops, callbacks, sidebars explaining a main flow).

## Frame spacing

| Distance | Effect |
|----------|--------|
| < 80px between frames | Arrows collide / overlap / squeeze between frames — **broken** |
| 150–250px | Comfortable clearance for 3-point arrows — **good default** |
| 400px+ | Dead whitespace — reader loses the connection — reduce |

Frames themselves are sized by their content: internal padding 20–100px (flexes with content density), box 200×100, row gap ~100px AND column gap ~100px (constant inter-box rhythm — see `brand-style.md` measured ranges).

Frame `y` should be **≥ 40**. Excalidraw renders the frame `name` above the stroke box; if the frame starts too close to the top of the canvas, the label clips off the page.

### Frame height formula

Compute frame height from the content, not by guessing:

```
frame_height = top_pad + N_rows * box_h + (N_rows - 1) * row_gap + bottom_pad
```

With defaults (`top_pad = 50`, `row_gap = 100`, `box_h = 100`, `bottom_pad = 50`):

| Rows | Height |
|------|--------|
| 2 | 400 |
| 3 | 600 |
| 4 | 800 |
| 5 | 1000 |

Frame width is analogous: `left_pad + N_cols * box_w + (N_cols - 1) * col_gap + right_pad`. If your content doesn't fit the resulting frame, shrink `row_gap` or `col_gap` before you shrink `box_w/box_h` — consistency of inter-box rhythm matters more than perfect padding.

## Cross-frame arrow paths

Every cross-frame arrow should take one of these shapes:

**Shape A — straight across a gap** (frames in the same row):
```
┌─Frame A─┐        ┌─Frame B─┐
│ [elem] ─┼────────┼─> [elem]│
└─────────┘        └─────────┘
```

**Shape B — one bend** (frames diagonally offset):
```
┌─Frame A─┐
│ [elem] ─┼──┐
└─────────┘  │
             │    ┌─Frame B─┐
             └────┼─> [elem]│
                  └─────────┘
```

**Shape C — two bends** (frames in different rows AND columns, going through empty canvas):
```
┌─Frame A─┐
│ [elem] ─┼──┐
└─────────┘  │
             │
             └──┐
                │  ┌─Frame B─┐
                └──┼─> [elem]│
                   └─────────┘
```

**Never** route an arrow through a third frame. If the only way to reach Frame B from Frame A is across Frame C, the layout is wrong.

## Signs the layout is wrong

Stop and re-plan the layout if:
- You're writing a 5th point in a `points` array.
- A waypoint coordinate falls inside a third frame's bounding box.
- Two frames that exchange many arrows sit > 1 frame-width apart.
- Two frames sit < 150px apart with arrows squeezing between them.
- An arrow has to make 3+ bends to reach its target.
- You're reaching for `fixedPoint` values that place arrows at weird corners of shapes (like `[0.8, 0.2]`) to dodge other elements.

Fix by moving frames — not by tweaking the arrow.

## Worked example: hub with spokes

`examples/summit-2026-v2-simple.excalidraw` uses this layout. Four subsystem frames around a central hub shape.

```
        ┌─── Frame: Authors ────┐
        │  [A1] [A2] [A3]       │
        └──────────┬────────────┘
                   │
                   ▼
┌─Frame B─┐    ┌──────────┐    ┌─Frame D─┐
│ [B1]    │──→ │   Hub    │ ←──│ [D1]    │
│ [B2]    │    │ (central │    │ [D2]    │
└─────────┘    │  shape)  │    └─────────┘
                   ▲
                   │
        ┌──────────┴────────────┐
        │  Frame: Consumers     │
        │  [C1] [C2] [C3]       │
        └───────────────────────┘
```

- Hub is a plain rectangle (not a frame), sized large enough to be the visual center.
- Each surrounding frame sits 200–300px from the hub.
- Arrows exit each frame from the edge closest to the hub, bind to the hub with `mode: "orbit"` on the hub-side binding.
- Orbit mode distributes arrows around the hub's edges automatically — no manual `fixedPoint` stagger needed.

## Worked example: side-by-side architectures

`examples/agent-sdk-and-harness.excalidraw` uses this layout. Two independent sectional diagrams running in parallel columns with a thin divider line between them.

```
   Column A                          Column B
┌─Frame A1─┐                      ┌─Frame B1─┐
│          │                      │          │
└──────────┘        │             └──────────┘
     │              │                  │
     ▼              │                  ▼
┌─Frame A2─┐        │             ┌─Frame B2─┐
│          │   divider line       │          │
└──────────┘        │             └──────────┘
     │              │                  │
     ▼              │                  ▼
┌─Frame A3─┐        │             ┌─Frame B3─┐
│          │                      │          │
└──────────┘                      └──────────┘
```

- Each column is self-contained: no cross-column arrows.
- Divider is a single `type: "line"` element with `strokeStyle: "dashed"`.
- Each column's internal flow is top-to-bottom (technical sequence).
- Column headers live outside the top frame, free-floating.

Because there are no cross-column arrows, the only layout rule within each column is the standard "200px clearance between frames."
