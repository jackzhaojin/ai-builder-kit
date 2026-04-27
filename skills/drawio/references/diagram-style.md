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

### 5. Shape Carries Meaning: Rectangles vs Cylinders

Use shape to distinguish two semantic roles:
- **Rounded rectangle** → process / service / component / step (anything that *acts*).
- **Cylinder (`shape=cylinder3`)** → persistent data store (database, object store, queue, log). Use whenever a data store is a first-class element, especially when one service owns multiple distinct stores. See `references/xml-format.md` for the recipe.

If a service has two distinct datasets, draw two cylinders connected to the service box — do not collapse them into one rectangle with a long text label.

### 6. Dashed = Return/Response/Feedback Edges Only

Reserve `dashed=1;dashPattern=8 8;` for **edges that flow back to a caller** (responses, replies, feedback, retry, async callbacks). One meaning, one visual.

Do **not** use dashed for: "indirect," "noteworthy," "secondary," "human-in-the-loop," or "optional/unknown." Each of those has its own dedicated treatment — see *Alternatives to Dashed* below. Overloading dashes with five meanings dilutes the signal until readers can't tell which one is meant.

#### Alternatives to Dashed

| Concept | Treatment |
|---------|-----------|
| Noteworthy / exception | Red stroke (`strokeColor=#e03131`) + italic edge label annotating the exception. No dash. |
| Secondary output | Thinner stroke (`strokeWidth=1`) or neutral color. No dash. |
| Human-in-the-loop | Dedicated HITL swimlane, or an explicit user/operator box wired into the flow. No dash. |
| Optional / unknown component | Dashed *box* (rare; see `xml-format.md`) **or** a `?` suffix in the box label. Optional *edges* should be omitted from the diagram and noted in the legend or caption. |
| Indirect flow | Reroute or relabel — if the diagram needs to say "this is indirect," that's usually a layout/labelling problem, not a stroke problem. |

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
- [ ] Cylinders (`shape=cylinder3`) used for persistent data stores; rectangles for services/processes
- [ ] Dashed (`dashed=1;dashPattern=8 8;`) used **only** on return/response/feedback edges — not on any other concept
- [ ] Feedback loops use same-side exit/entry
- [ ] Edge labels are italic
- [ ] All boxes have `rounded=1;arcSize=15`
- [ ] Edges have `rounded=0` (sharp corners on bends)
- [ ] Consistent strokeWidth=2 everywhere
