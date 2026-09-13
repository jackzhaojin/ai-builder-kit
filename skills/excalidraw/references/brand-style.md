# Jack's Brand & Style

Everything that makes a diagram look like it came from Jack's hand: colors, roughness, font, alignment grid, legends, spacing. These are load-bearing — deviate only when you have a specific reason.

## Table of contents
- [Whitespace is pretty (the #1 rule)](#whitespace-is-pretty-the-1-rule)
- [Fixed properties (every element)](#fixed-properties-every-element)
- [Color palette](#color-palette)
- [Semantic color mapping](#semantic-color-mapping)
- [Alignment grid](#alignment-grid)
- [Frames for grouping](#frames-for-grouping)
- [Legend pattern](#legend-pattern)
- [Solid vs dashed](#solid-vs-dashed)
- [Layout patterns](#layout-patterns)

## Whitespace is pretty (the #1 rule)

Jack's canonical diagrams run **10–27% shape area, 73–90% whitespace** (measured across all 6 example diagrams). The goal isn't to fit every possible annotation — it's to leave room for a human to *talk over* the diagram and point at things.

### The rules

- **One idea per box.** Labels are 1–4 words. Don't cram two concepts into one rectangle.
- **`(xN)` means ONE box, not N boxes.** Jack's idiom for multiplicity. When the label says "Deterministic Logic (x4)" or "Agentic Logic (x4)", render one box; the parenthetical is the annotation. Only expand into N boxes when each has a distinct label (e.g. Research / Build / Validate). Expanding `(x4)` into four stacked boxes breaks the airy feel.
  - **Literal syntax is mandatory:** `(x4)` — open-paren, lowercase `x`, digit, close-paren. Not `x4`, `×4`, `(×4)`, `[x4]`, or `{x4}`. Consistency across diagrams and grep-ability both depend on the exact form.
- **No evidence rectangles or code-snippet callouts embedded in the diagram.** If a viewer wants the code, they read the code. The diagram maps concepts.
- **No subheads inside frames.** The frame's `name` is the title. A redundant subhead like "runs locally, no browser yet" is noise.
- **No captions under boxes** unless the label genuinely can't fit the meaning.
- **Default box size: `200 × 100`.** Dense row-grids may go down to `~170 × 75`. Legend swatches are wider-and-shorter labeled pills: **`118–160 wide × 35–40 tall`** — never small color-only squares. Measured from all 6 canonical examples: `agent-sdk-and-harness`, `agentic-ai-auth`, `summit-2026-v2-simple` use `160 × 40`; `multi-frame-process` uses `118 × 35`. A swatch is always visibly shorter than the content box height (≤ half), which is what makes it read as annotation.
- **One size per diagram — consistency matters.** Pick a standard box size and use it for every content box. In `authoring-patterns` 10/10 rectangles are the same size; in `agent-sdk-and-harness` 18/29 share `200×100` (the others are legend swatches or containers). **Don't vary the box size to fit the label** — tighten the label instead. The only legitimate exceptions are (a) legend swatches (intentionally smaller), (b) an explicit container/region shape that represents a fundamentally different thing (e.g. the `400×290` system-boundary shape in `prompts-to-harness`). If a shape is the same kind of thing as its neighbors, it's the same size.
- **Dense row-grids need label breathing room.** In `~170 × 75` grids like `agentic-ai-auth`, leave ~10–12px of visual right-padding between the last character and any incoming arrowhead. If the label is too long to keep that breathing room, shorten the label or drop the font one step.
- **~100px is the inter-box rhythm.** Both row gaps and column gaps land at ~100px across all 6 examples (median 100px row, 90px column). This rhythm stays constant whether the frame is airy or dense.
- **Frame padding flexes with content** (see below). Airy frames: ~80–100px L/R, ~40–50px B. Verbose frames (`multi-frame-process`, `prompts-to-harness`): can shrink L/R to 20–60px because the content itself fills the frame. Top is always tight (~20px) because the frame `name` label sits there.
- **Between-frame gap: 40–100px** for stacks/side-by-side. Hub-and-spoke diagrams (`summit-2026-v2-simple`) can have 800+px between frames orbiting a central shape — that's the whole visual.
- **≤ 16 shapes per frame** even in dense subsystems. `agent-sdk-and-harness` goes up to 16; beyond that starts to feel crowded.
- **Reduce before you add.** Ask "what can I remove?" before "what should I add?" on every iteration.

When in doubt: imagine Jack standing in front of the rendered diagram with a pointer, explaining it. If there's no room for his arm to move, the diagram is too dense.

### Verbose content is allowed — frame padding absorbs it

When a subsystem has inherently dense/verbose content (lots of specific component names, detailed sub-processes, labels that genuinely can't shrink), let the **frame padding tighten** rather than shrinking the inter-box rhythm or the box size. Look at `multi-frame-process` (frame L padding 27px) and `prompts-to-harness` (frame L padding 40px) — both have tight frame borders around densely-labeled content, but **boxes are still 200 × 100 with 100px gaps**. The consistent inter-box rhythm is what makes the diagram feel like Jack's even when the content is heavy.

### Measured ranges across all 6 examples

| Dimension | Range | Median | Notes |
|-----------|-------|--------|-------|
| Shape area / canvas | 10–27% | ~15–20% | Lower for airy hub diagrams, higher for row-grids |
| Default rect | `200 × 100` | `200 × 100` | Dominant in 5/6 examples |
| Dense-grid rect (`agentic-ai-auth`) | `171 × 74` | — | Smaller only when content is a row-grid |
| Row gap (same-row shapes) | 31–1290px | 100px | 1290 is a between-group separator, not a neighbor gap |
| Col gap (same-col shapes) | 10–116px | 90px | 10-33 is for stacked legend swatches only |
| Frame L padding | 24–106px | 50px | Tighter when content is verbose |
| Frame R padding | 39–100px | 78px | Tighter when content is verbose |
| Frame T padding | 20–121px | 20px | Almost always 20 (frame label sits there) |
| Frame B padding | 20–160px | 50px | |
| Between-frame gap | 38–856px | 100px | Big gaps only in hub-and-spoke layouts |
| Max shapes per frame | up to 16 | — | |
| Elements per diagram | 33–87 | ~60 | |

## Fixed properties (every element)

```json
{
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "fontFamily": 5
}
```

- `roughness: 1` — hand-drawn is brand. Never `0`.
- `fontFamily: 5` — Nunito. Never monospace (`3`) or Virgil (`1`).
- Transparent backgrounds; colored strokes + colored text. No background highlighting.
- `strokeWidth: 2` for structural elements.
- **`roundness: {"type": 3}` on rectangles by default.** Sharp corners only for specific structural roles (explicit system-boundary containers, flagged "different kind of thing" shapes). Canonical examples use rounded throughout.

## Color palette

| Role | Hex | Usage |
|------|-----|-------|
| Default / Primary | `#1e1e1e` | Standard strokes, text, neutral flow |
| Emphasis / Red | `#e03131` | Highlight, errors, actor auth (credentials) |
| Info / Blue | `#1971c2` | Supporting elements, cloud resources |
| Special / Purple | `#6741d9` | Distinct components, AI/ML |
| Success / Green | `#2f9e44` | Success states, databases, human actors |
| Muted / Grey | `#bbb` | De-emphasized elements |
| Warning / Orange | `#f08c00` | Warnings, pending states, identity/members |

## Semantic color mapping

Use the same color consistently for the same *kind* of thing across every diagram:

| Semantic | Stroke | When to use |
|----------|--------|-------------|
| Actor / User | `#2f9e44` (green) | Humans, triggers, external entities initiating work |
| Actor Auth | `#e03131` (red) | Authentication, secrets, credentials, tokens |
| Resource | `#1971c2` (blue) | Azure/cloud resources, outputs, data stores |
| Member / Identity | `#f08c00` (orange) | Service principals, managed identities, agents-as-members |
| AI / Agent | `#6741d9` (purple) | LLM, agent, model inference, reasoning step |
| Default / Flow | `#1e1e1e` (black) | Neutral process steps, standard connections |
| Optional / Muted | `#bbb` (grey) | Dashed, optional, background-only elements |

Arrow stroke color should match the **source element's** semantic stroke color.

## Alignment grid

### Same row → same Y + height

```
Row 1: all boxes at y=100, height=100
Row 2: all boxes at y=240, height=100
Row 3: all boxes at y=380, height=100
```

### Same column → same X + width

```
Col 1: all boxes at x=100, width=150
Col 2: all boxes at x=300, width=150
Col 3: all boxes at x=500, width=150
```

### Default box height: `100`

Fits 3–4 comfortable lines of medium text (`fontSize: 20`). Deviate only for specific reasons (e.g. 3-line labels might use `80`).

### Spacing (measured across all 6 example diagrams)

| Gap | Range | Default |
|-----|-------|---------|
| Between rows (same-column shapes, edge to edge) | 10–116px | **~100px** |
| Between columns (same-row shapes, edge to edge) | 31–1290px | **~100px** |
| Frame padding — left | 24–106px | **~50–100px** (airy); ~20–40px if content is verbose |
| Frame padding — right | 39–100px | **~50–100px** (airy); ~40–60px if content is verbose |
| Frame padding — top | 20–121px | **~20px** (frame `name` label sits there) |
| Frame padding — bottom | 20–160px | **~40–50px** |
| Between frames (edge to edge) | 38–856px | **~100px** (side-by-side/stack); wider for hub diagrams |

**Key principle**: the **100px inter-box rhythm** is constant. Frame padding is the variable that absorbs content density. If content is verbose, tighten frame padding (20–40px). If content is light, let frame padding breathe (80–100px). Don't compress inter-box gaps to fit content — split into more frames instead, or let the frame grow.

## Frames for grouping

Use Excalidraw `frame` elements — **not dashed rectangles** — to group subsystems.

- Each major subsystem gets its own frame.
- Frame has a `name` describing the subsystem.
- Elements inside have `frameId` set to the frame's id.
- Leave 20–30px padding inside the frame.

```json
{
  "type": "frame",
  "id": "frame_ingest",
  "x": 100, "y": 100, "width": 600, "height": 400,
  "name": "Ingestion",
  "strokeColor": "#1e1e1e"
}
```

Children set `"frameId": "frame_ingest"`.

## Legend pattern

When a diagram uses multiple semantic colors, include a legend:

- **Position**: top-left corner, outside main diagram flow.
- **Format**: small colored boxes with labels (a mini-row of labeled swatches).
- **Style**: same `roughness: 1`, `strokeWidth: 2`, transparent fill as the rest of the diagram.

Example:

```
legend
  [green] actor        [blue] az resource
  [red]   actor auth   [orange] az member
```

### Per-frame mini-legend (when diagram has multiple frames)

When a diagram has multiple frames that each use the same semantic palette, place a small mini-legend in the **top-right corner of EACH frame** instead of a single global legend. See `examples/agent-sdk-and-harness.excalidraw` (both frames have their own top-right mini-legend) and `examples/summit-2026-v2-simple.excalidraw` Frame 3.

- Position inside the frame: top-right, ~20px from the frame's top and right edges.
- Same `roughness: 1`, `strokeWidth: 2`, transparent fill.
- 3–4 labeled-pill swatches (`160 × 40`, one per color), stacked vertically or laid out as a compact 2×2 grid.
- **Clearance:** the mini-legend needs ≥ 60px gap from any content box to its left and ≥ 40px below. In frames with a right-column content box (like `summit-2026-v2-simple` Frame 3's localStorage column), EITHER widen the frame by ~120px OR place the mini-legend above the first content row instead of top-right. If you crash into a content box on first render, the frame was too narrow — don't shrink the legend.

### Column group headers

Free-floating text labels above a column (or a span of columns) to announce what that column represents. Used in `examples/authoring-patterns.excalidraw` ("Authoring Interface", "Content Storage", "EDS Processing and compiling", "User").

- Plain text elements (no containing shape), centered over the column span.
- Same `fontSize` across all headers in a diagram (usually 20–24).
- No underline, no box, no color — `strokeColor: "#1e1e1e"`.
- For a span across multiple sub-columns, center the header over the midpoint of the span.

### Callout annotations (free-floating multi-line text)

Use for requirement lists, outcome notes, or context blocks that would bloat a rectangle. Jack's pattern: place the callout NEAR the related flow element, not inside one.

- `containerId: null` — no surrounding shape.
- `textAlign: "left"`, `verticalAlign: "top"`.
- Multi-line via `\n` in the text. Keep to 3–6 lines; if longer, split into two callouts.
- Width estimate: `width = longest_line_char_count * fontSize * 0.55` (upper bound; Excalidraw auto-fits bbox on load but initial width must not clip).
- Same `fontSize: 18–20`, `strokeColor: "#1e1e1e"`, `fontFamily: 5`.
- Position: 40–80px from the flow element it annotates, never overlapping content boxes.

Examples: `examples/prompts-to-harness.excalidraw` (Requirements list next to Harness Idealization, Outcomes list below Building cycle), `examples/multi-frame-process.excalidraw` (Reqs block above Frame 2).

## Solid vs dashed

- **Solid arrows** → primary flow, required connections.
- **Dashed arrows** (`strokeStyle: "dashed"`) → optional paths, async, callbacks.
- **Dashed rectangles** → avoid. Use `frame` elements instead.

## Layout patterns

### Pattern A: Horizontal flow (architecture)

Best for system architecture, left-to-right data flow.

```
[Title centered at top]

legend          [Source 1] ─→ [Process] ─→ [Identity] ─→ [Resource]
[colors]        [Source 2] ─→ [Process] ─→ [Identity] ─→ [Resource]
                [Source 3] ─→ [Process] ─→ [Identity] ─→ [Resource]
```

- All rows aligned, all columns aligned.
- Arrows flow left-to-right.
- Legend top-left.

### Pattern B: Framed subsystems (process)

Best for multi-subsystem processes.

```
┌─── Frame: Subsystem A ───────────────────┐
│  [Start] → [Process] → [End]             │
│     ↓                                     │
│  [Sub-process] → [Output]                │
└──────────────────────────────────────────┘
          │
          ▼
┌─── Frame: Subsystem B ───────────────────┐
│  [Input] → [Transform] → [Validate]      │
│                              ↓            │
│                         [Output]          │
└──────────────────────────────────────────┘
```

### Pattern C: Hub with spokes

Best for 3–4 subsystems that all talk to one central coordinator (see `examples/summit-2026-v2-simple.excalidraw`).

```
           [Frame A]
               │
[Frame D] ─ [ Hub ] ─ [Frame B]
               │
           [Frame C]
```

The hub has `mode: "orbit"` on incoming bindings so arrows distribute around its edges.

## Quick style checklist

- [ ] Every element has `roughness: 1`, `strokeWidth: 2`, transparent fill.
- [ ] Every text element has `fontFamily: 5`.
- [ ] Same-row elements share Y + height; same-column elements share X + width.
- [ ] Frame used for each subsystem; children have `frameId`.
- [ ] Legend top-left when diagram uses 2+ semantic colors.
- [ ] Arrow stroke matches source element's semantic color.
- [ ] Solid vs dashed distinction applied consistently.
