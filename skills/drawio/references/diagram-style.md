# Draw.io Diagram Style Guide

These are **recommendations** based on the best example diagram. Follow them ~90% of the time for consistency.

## Core Principles

### 1. Use Swimlanes (Frames) for Grouping

Every diagram should have a swimlane container:

```xml
<mxCell id="frame-main" value="Diagram Title" style="swimlane;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1e1e1e;strokeWidth=2;fontSize=14;fontStyle=0;fontColor=#1e1e1e;startSize=30;rounded=0;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="920" height="820" as="geometry" />
</mxCell>
```

**Swimlane benefits:**
- Clear visual boundary
- Elements move together
- Title in header
- Professional appearance

### 2. Legend Inside Frame (Top-Right)

Position legend items INSIDE the frame, top-right corner:

```
┌─────────────────────────────────────────┐
│ Frame Title                   [User]    │
│                               [Determ.] │
│                               [Agentic] │
│   [Content flows here]        [Mix]     │
│                                         │
└─────────────────────────────────────────┘
```

Legend items:
- 100x30 size
- 40px vertical spacing between items
- fontSize=12
- Same `parent="frame-id"` as other elements

### 3. Color-Coded Elements

Match BOTH strokeColor AND fontColor:

| Role | Hex | Example |
|------|-----|---------|
| User/Default | `#1e1e1e` | Input, output |
| Deterministic | `#1971c2` | Predictable logic |
| Agentic | `#e03131` | AI-driven, dynamic |
| Mix | `#f08c00` | Hybrid components |

### 4. Consistent Box Styling

Standard box template:
```
rounded=1;arcSize=15;fillColor=#ffffff;strokeWidth=2;
whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontFamily=Helvetica;
```

### 5. Dashed Only for Return/Response Calls

Reserve `dashed=1;dashPattern=8 8;` for **return/response direction only** (replies flowing back to a caller).

Avoid using dashes for multiple unrelated semantics. Use these alternatives instead:
- Noteworthy / exception path → solid edge + red `strokeColor` + italic edge label annotation
- Secondary output → solid edge with `strokeWidth=1` (or neutral color)
- Human-in-the-loop → explicit HITL lane/box/icon + solid edge
- Optional / unknown → solid edge with `?` in label text

---

## Layout Patterns

### Vertical Flow (PRIMARY)

Top-to-bottom progression:

```
    [Input]
       ↓
    [Process]
       ↓
    [Output]
```

- exitX=0.5;exitY=1 (bottom)
- entryX=0.5;entryY=0 (top)

### Feedback Loops

Use same-side exit/entry for loops:

```
┌──────────────┐
│  [Box A]  ←──┼── Feedback from B
│     ↓       │
│  [Box B]  ───┼── exits right, enters right of A
└──────────────┘
```

**Left-side feedback:** `exitX=0;exitY=0.5;entryX=0;entryY=0.5;`
**Right-side feedback:** `exitX=1;exitY=0.5;entryX=1;entryY=0.5;`

### Fan-Out Pattern

One source to multiple targets:

```
         ┌→ [Target 1]
[Source] ┼→ [Target 2]
         └→ [Target 3]
```

Use explicit exitY values: 0.25, 0.5, 0.75

---

## Spacing Guidelines

| Measurement | Value |
|-------------|-------|
| Grid size | 10px |
| Frame padding | 40px from edges |
| Frame start size | 30px (header) |
| Box width | 120-180px |
| Box height | 50-80px |
| Legend box | 100x30px |
| Vertical gap | 30-50px |
| Horizontal gap | 40-80px |

**Tip:** Snap all coordinates to multiples of 10.

---

## Typography

| Element | fontSize | fontStyle |
|---------|----------|-----------|
| Frame title | 14 | 0 (normal) |
| Box labels | 14 | 0 (normal) |
| Detailed boxes | 12 | 0 (normal) |
| Legend items | 12 | 0 (normal) |
| Edge labels | 12 | 2 (italic) |

**Never use italic for box text** - only for edge labels.

---

## Edge Label Styling

For styled edge labels, use HTML spans:

```xml
value="&lt;span style=&quot;color: rgb(224, 49, 49); font-size: 12px; font-style: italic;&quot;&gt;Label Text&lt;/span&gt;"
```

Edge labels should be:
- Italic (font-style: italic)
- Same color as the edge (match strokeColor)
- fontSize 12px

---

## Checklist

Before finalizing:

- [ ] Single swimlane frame with title
- [ ] Legend inside frame (top-right)
- [ ] Colors match for strokeColor AND fontColor
- [ ] Dashed lines used only for return/response calls
- [ ] Feedback loops use same-side exit/entry
- [ ] Edge labels are italic
- [ ] All boxes have `rounded=1;arcSize=15`
- [ ] Edges have `rounded=0` (sharp corners on bends)
- [ ] Consistent strokeWidth=2 everywhere
