# Validation Checklist

## Technical Validation (Before Writing File)

- [ ] Every shape with label has `boundElements` + separate text element
- [ ] Text elements have `containerId` matching shape
- [ ] Multi-point arrows have `elbowed: true`, `roughness: 1`
- [ ] Arrow `x,y` = source shape edge point
- [ ] Arrow final point offset reaches target edge
- [ ] No diamond shapes
- [ ] No duplicate IDs
- [ ] Arrow bounding boxes match points

## Style Validation (Jack's Standards)

### Alignment
- [ ] All elements in same row share identical Y coordinate
- [ ] All elements in same row share identical height
- [ ] All elements in same column share identical X coordinate
- [ ] All elements in same column share identical width
- [ ] Grid spacing consistent: ~100px between rows AND between columns (constant inter-box rhythm — see `brand-style.md`)

### Structure
- [ ] Frames used to group related subsystems
- [ ] Each frame has descriptive title
- [ ] Elements inside frames have correct `frameId`
- [ ] Legend present when multiple colors used
- [ ] Legend positioned top-left, outside main flow

### Arrows
- [ ] Arrows ending at same column share X endpoint
- [ ] Multiple arrows from same source are staggered at start but aligned at end
- [ ] Solid lines for primary flow, dashed for optional/async
- [ ] On a large/tall diagram, crop zoomed regions of the rendered PNG (e.g. PIL `Image.crop(...)`) and view them — mis-bound connectors and label overlaps are invisible at full-diagram zoom

### Color Consistency
- [ ] Green (`#2f9e44`) = actors/users/triggers
- [ ] Red (`#e03131`) = auth/secrets/credentials
- [ ] Blue (`#1971c2`) = resources/outputs
- [ ] Orange (`#f08c00`) = identities/members
- [ ] Black (`#1e1e1e`) = default/neutral

## Common Bugs

| Issue | Fix |
|-------|-----|
| Labels don't appear | Use TWO elements (shape + text), not `label` property |
| Arrows curved | Add `elbowed: true`, `roughness: 1` |
| Arrows floating | Calculate x,y from shape edge, not center |
| Arrows overlapping | Stagger start positions across edge |
| Misaligned rows | Ensure all elements share same Y and height |
| Inconsistent spacing | Use ~100px rows AND ~100px columns (constant rhythm) |

## Validation Algorithm

```
// Technical validation
FOR each shape with boundElements:
  Verify text element exists with matching containerId

FOR each arrow:
  Verify x,y is within 15px of a shape edge
  Verify final point offset reaches target edge

Verify no duplicate IDs
Verify valid JSON

// Style validation
Group elements by Y coordinate (tolerance 5px) → verify same height
Group elements by X coordinate (tolerance 5px) → verify same width
FOR each frame:
  Verify child elements have frameId set
IF multiple stroke colors used:
  Verify legend exists
```
