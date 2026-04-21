# Validation Checklist

## Technical Validation

### XML Structure

- [ ] File starts with `<mxfile>` tag
- [ ] Contains `<diagram>` with `id` attribute
- [ ] Contains `<mxGraphModel>`
- [ ] Contains `<root>` element
- [ ] Root contains `<mxCell id="0" />`
- [ ] Root contains `<mxCell id="1" parent="0" />`
- [ ] File ends with `</mxfile>`

### Cell Validation

- [ ] Every cell has unique `id` attribute
- [ ] Every vertex has `vertex="1"`
- [ ] Every edge has `edge="1"`
- [ ] Top-level elements have `parent="1"`
- [ ] Swimlane children have `parent="frame-id"`
- [ ] Every cell has `<mxGeometry>` child

### Edge Validation

- [ ] Every edge has valid `source` attribute
- [ ] Every edge has valid `target` attribute
- [ ] Source and target IDs exist in document
- [ ] Edge mxGeometry has `relative="1"`
- [ ] Edge parent matches connected boxes' parent

### Edge Label Validation (if using styled labels)

- [ ] Label has `connectable="0"`
- [ ] Label has `parent="edge-id"` (parent is the edge!)
- [ ] Label has `vertex="1"`
- [ ] Label style includes `edgeLabel`

---

## Style Validation

### Box Styling

- [ ] All boxes use `rounded=1;arcSize=15`
- [ ] All boxes use `strokeWidth=2`
- [ ] All boxes use `fillColor=#ffffff`
- [ ] Color-coded boxes match strokeColor AND fontColor
- [ ] Indirect/noteworthy boxes use `dashed=1;dashPattern=8 8;`
- [ ] All boxes use `fontFamily=Helvetica`
- [ ] All boxes use `align=center;verticalAlign=middle`

### Edge Styling

- [ ] All edges use `edgeStyle=orthogonalEdgeStyle`
- [ ] All edges use `rounded=0` (sharp corners on bends)
- [ ] All edges use `strokeWidth=2`
- [ ] All edges use `endArrow=classic;endFill=1`
- [ ] Color matches semantic meaning
- [ ] Feedback loops use same-side exit/entry

### Frame/Swimlane

- [ ] Frame uses `swimlane` style
- [ ] Frame uses `startSize=30`
- [ ] Frame uses `rounded=0`
- [ ] Frame uses `fontStyle=0` (not italic)

### Legend

- [ ] Legend inside frame (same parent as content)
- [ ] Legend in top-right corner
- [ ] Legend items 100x30 size
- [ ] Legend items use fontSize=12
- [ ] Legend colors match strokeColor AND fontColor

---

## Color Consistency

| Role | strokeColor | fontColor |
|------|-------------|-----------|
| User/Default | `#1e1e1e` | `#1e1e1e` |
| Deterministic | `#1971c2` | `#1971c2` |
| Agentic | `#e03131` | `#e03131` |
| Mix | `#f08c00` | `#f08c00` |

**Critical:** strokeColor and fontColor MUST match for color-coded elements.

---

## Common Bugs

| Issue | Cause | Fix |
|-------|-------|-----|
| Edges not connecting | Invalid source/target ID | Verify IDs exist |
| Edge parent mismatch | Edge parent differs from boxes | Use same parent as connected boxes |
| Feedback loops broken | Different exit/entry sides | Use same side (both left or both right) |
| Edge labels not showing | Wrong parent | Set `parent="edge-id"` not frame |
| Italic text everywhere | fontStyle=2 | Use fontStyle=0 |
| Colors don't match | Only strokeColor set | Set both strokeColor AND fontColor |
| Legend outside frame | Wrong parent | Use `parent="frame-id"` |

---

## Visual Validation (after Read-the-PNG)

These rules cannot be checked from XML alone — only after you `Read` the rendered PNG. They are **the** reason Step 5 of the workflow is mandatory.

### Rule A — No edge crosses a non-endpoint box

For each edge in the PNG, trace its path with your eyes from source to target. The path must not pass through any box that is neither source nor target. If it does:

- **Fix**: layout change (move the offending box, widen the gap between frames, reorder sources).
- **Do not fix by adding waypoints.** Waypoints fight the auto-router; the real fix is positioning the boxes so the router has a clean path.

### Rule B — No edge has more than 2 turns

An orthogonal edge with `edgeStyle=orthogonalEdgeStyle` should bend at most twice between source and target. If it snakes or U-turns:

- **Fix**: same as Rule A. The offending edge is telling you the layout is wrong.

### Rule C — Converging arrows merge into one bind point

When 3+ arrows end at the same target:

- They must **all enter the target at the same connection point** — identical `entryX` AND identical `entryY`. Multiple edges sharing the same bind point is the correct pattern; arrowheads will visually stack at that one spot.
- Do NOT stagger entry positions along a side of the target (entryY=0.2 / 0.4 / 0.6 / 0.8 for 4 arrows looks like a spray array, not a convergence).
- Do NOT try to give each arrow a unique landing spot. Sharing a bind point is allowed and expected.
- Arrows should be the **same color and style**. Mixed colors converging into one point is confusing; either homogenize or split the convergence into separate logical groups.

If arrows arrive from 4 different sides of the target (octopus), reposition the sources so they approach from one side, then all hit the same bind point.

### Rule D — Edge labels sit near their arrow body

A free-floating label more than ~40px from the midpoint of its arrow is visually orphaned. Nudge `x` on the label's `mxGeometry` until it sits on or next to the arrow.

---

## Pre-Output Checklist

1. **Structure**
   - [ ] mxfile > diagram > mxGraphModel > root
   - [ ] Cells 0 and 1 present
   - [ ] Single swimlane frame

2. **IDs**
   - [ ] All unique
   - [ ] All source/target references valid
   - [ ] All parent references valid

3. **Boxes**
   - [ ] rounded=1;arcSize=15
   - [ ] strokeColor AND fontColor match
   - [ ] strokeWidth=2
   - [ ] fontFamily=Helvetica

4. **Edges**
   - [ ] edgeStyle=orthogonalEdgeStyle
   - [ ] rounded=0
   - [ ] Parent matches boxes' parent
   - [ ] Feedback uses same-side exit/entry

5. **Legend**
   - [ ] Inside frame (top-right)
   - [ ] Same parent as content
   - [ ] All semantic colors represented
