# Element Templates (Jack's style)

Copy-paste JSON templates with Jack's brand values baked in: `roughness: 1`, `fontFamily: 5` (Nunito), `strokeWidth: 2`, transparent fills. Pull semantic colors from `brand-style.md` based on the element's purpose.

Minimal format relies on `restoreElements()` auto-fills (see `json-format.md`). Omitting `seed`, `version`, `versionNonce`, `updated` is fine; Excalidraw fills them.

## Table of contents
- [Free-floating text (section titles, annotations)](#free-floating-text-section-titles-annotations)
- [Labeled rectangle (shape + text pair)](#labeled-rectangle-shape--text-pair)
- [Rounded rectangle (soft container)](#rounded-rectangle-soft-container)
- [Ellipse / marker dot](#ellipse--marker-dot)
- [Line (divider, connector backbone)](#line-divider-connector-backbone)
- [Frame (subsystem grouping)](#frame-subsystem-grouping)
- [Arrow (standard)](#arrow-standard)
- [Legend swatch + label](#legend-swatch--label)

## Free-floating text (section titles, annotations)

```json
{
  "type": "text",
  "id": "section-title",
  "x": 100, "y": 100,
  "width": 280, "height": 30,
  "text": "Section Title",
  "originalText": "Section Title",
  "fontSize": 24,
  "fontFamily": 5,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "containerId": null,
  "lineHeight": 1.25
}
```

Sizing notes: `fontSize` 24 for section titles, 20 for default body, 16 for small captions. `height` should be `fontSize * lineHeight` (25 for body, 30 for title).

**Width estimation for free-floating text** (no container): `width ≈ longest_line_char_count * fontSize * 0.55`. Excalidraw auto-fits the bbox on load, but your initial width must not clip the rendered text or collide with adjacent elements. Example: 20-char label at `fontSize: 20` → `width ≈ 220`.

**Font size by label line count** (labels inside the default 200×100 box):
- 1–2 lines → `fontSize: 20`
- 3 lines → `fontSize: 18`
- 4+ lines → `fontSize: 16` (and ask: is this really one idea? See `brand-style.md` "One idea per box")

Dropping below `fontSize: 14` to fit a label means the label has too many ideas — split the box or reduce the label.

## Labeled rectangle (shape + text pair)

**Two elements** — shape with `boundElements`, text with `containerId`.

```json
// Shape
{
  "type": "rectangle",
  "id": "elem1",
  "x": 100, "y": 100,
  "width": 180, "height": 100,
  "strokeColor": "#1971c2",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "boundElements": [{ "id": "elem1-text", "type": "text" }],
  "roundness": null
}

// Text
{
  "type": "text",
  "id": "elem1-text",
  "x": 130, "y": 135,
  "width": 120, "height": 25,
  "text": "Component",
  "originalText": "Component",
  "fontSize": 20,
  "fontFamily": 5,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "#1971c2",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "containerId": "elem1",
  "lineHeight": 1.25
}
```

Text stroke color matches the container stroke color. `fontFamily: 5` everywhere (Nunito).

## Rounded rectangle (soft container)

Same as rectangle, but with `"roundness": { "type": 3 }`. Use for "softer" concepts — inputs, end-user actors, optional stages. Keep sharp-cornered rectangles for structural / technical components.

```json
{
  "type": "rectangle",
  "id": "input",
  "x": 100, "y": 100,
  "width": 180, "height": 100,
  "strokeColor": "#f08c00",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "boundElements": [{ "id": "input-text", "type": "text" }],
  "roundness": { "type": 3 }
}
```

## Ellipse / marker dot

Small ellipses for timeline milestones or free-floating labels.

```json
{
  "type": "ellipse",
  "id": "milestone1",
  "x": 200, "y": 200,
  "width": 16, "height": 16,
  "strokeColor": "#2f9e44",
  "backgroundColor": "#2f9e44",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "boundElements": null
}
```

Larger ellipses (for assembly-line steps like `[ Validate ]`) use same pattern as labeled rectangle but `"type": "ellipse"`.

## Line (divider, connector backbone)

Structural — not arrows. Use for section dividers or manually-drawn trunk lines.

```json
{
  "type": "line",
  "id": "divider1",
  "x": 100, "y": 300,
  "width": 1400, "height": 0,
  "strokeColor": "#bbb",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "dashed",
  "roughness": 1,
  "opacity": 100,
  "points": [[0, 0], [1400, 0]],
  "boundElements": null
}
```

## Frame (subsystem grouping)

Use instead of dashed rectangles. Children set `"frameId"` matching the frame's `id`.

```json
{
  "type": "frame",
  "id": "frame-ingest",
  "x": 100, "y": 100,
  "width": 700, "height": 400,
  "name": "Ingestion",
  "strokeColor": "#1e1e1e",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100
}
```

Children inside the frame:
```json
{ "frameId": "frame-ingest", "...": "..." }
```

## Arrow (standard)

See `arrows.md` for the full routing rules. Default recipe — assume `src` is a rectangle at `(160, 100)` size `(120, 100)` and `dst` is at `(400, 100)` size `(120, 100)`. Arrow exits `src` right-center, enters `dst` left-center.

```json
{
  "type": "arrow",
  "id": "arrow1",
  "x": 280, "y": 150,
  "width": 120, "height": 0,
  "strokeColor": "#1971c2",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "opacity": 100,
  "elbowed": true,
  "points": [[0, 0], [120, 0]],
  "startBinding": { "elementId": "src", "focus": 0, "gap": 5, "fixedPoint": [1, 0.5] },
  "endBinding":   { "elementId": "dst", "focus": 0, "gap": 5, "fixedPoint": [0, 0.5] },
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```

**`x`, `y` derivation (load-bearing — do not set to 0,0!):**
- `x = src.x + fixedPoint[0] * src.width = 160 + 1 * 120 = 280`
- `y = src.y + fixedPoint[1] * src.height = 100 + 0.5 * 100 = 150`
- `width, height` match the `points` bbox: max_x - min_x, max_y - min_y.

**After creating the arrow, register it on BOTH endpoints** — append to each shape's `boundElements`:

```json
// On src and dst:
"boundElements": [
  { "id": "label1", "type": "text" },  // existing label (if labeled_rect)
  { "id": "arrow1", "type": "arrow" }  // NEW: arrow id + type
]
```

Missing this silently breaks bindings on re-render.

Arrow stroke color matches source element's semantic color.

## Legend swatch + label

Pair of small rectangle + free-floating text. Several of these in a row in the top-left.

```json
// Swatch (small square)
{
  "type": "rectangle",
  "id": "legend-green",
  "x": 40, "y": 40,
  "width": 18, "height": 18,
  "strokeColor": "#2f9e44",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 1,
  "boundElements": null
}

// Label
{
  "type": "text",
  "id": "legend-green-text",
  "x": 64, "y": 42,
  "width": 60, "height": 18,
  "text": "actor",
  "originalText": "actor",
  "fontSize": 14,
  "fontFamily": 5,
  "textAlign": "left",
  "verticalAlign": "middle",
  "strokeColor": "#2f9e44",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 1,
  "containerId": null,
  "lineHeight": 1.25
}
```

Position legends in the top-left, outside the main diagram flow. Use the semantic colors from `brand-style.md` (green actor, red actor-auth, blue resource, orange member, purple AI).

---

## Properties you can safely omit (restoreElements auto-fills)

From `json-format.md`: `seed`, `version`, `versionNonce`, `updated`, `index`, `isDeleted` (unless true), `groupIds` (unless non-empty), `locked` (unless true), `link` (unless set), `frameId` (unless parented to a frame), `angle` (unless rotated). Keep them out for smaller JSON.
