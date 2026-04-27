# Draw.io Connectors Reference

## Basic Edge Structure

```xml
<mxCell id="edge-a-b" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#1e1e1e;strokeWidth=2;endArrow=classic;endFill=1;" edge="1" parent="frame-main" source="box-a" target="box-b">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Required attributes:**
- `edge="1"` - Marks as edge
- `parent="frame-main"` - Same parent as connected boxes
- `source="box-a"` - Source shape ID
- `target="box-b"` - Target shape ID

**Standard style:**
```
edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=2;endArrow=classic;endFill=1;
```

---

## Feedback Loops (KEY PATTERN)

For arrows that loop back to an earlier element:

### Left-Side Feedback
```xml
<mxCell id="edge-feedback" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#e03131;strokeWidth=2;endArrow=classic;exitX=0;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="frame-main" source="box-lower" target="box-upper">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Right-Side Feedback
```xml
<mxCell id="edge-feedback" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#e03131;strokeWidth=2;endArrow=classic;exitX=1;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="frame-main" source="box-lower" target="box-upper">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Key insight:** Draw.io auto-routes correctly when both exit and entry are on the SAME side. No waypoints needed!

---

## Connection Points

| Position | exitX/entryX | exitY/entryY |
|----------|--------------|--------------|
| Top-center | 0.5 | 0 |
| Bottom-center | 0.5 | 1 |
| Left-center | 0 | 0.5 |
| Right-center | 1 | 0.5 |

**Common flows:**
- Top-to-bottom: `exitX=0.5;exitY=1;entryX=0.5;entryY=0;`
- Left-to-right: `exitX=1;exitY=0.5;entryX=0;entryY=0.5;`
- Feedback left: `exitX=0;exitY=0.5;entryX=0;entryY=0.5;`
- Feedback right: `exitX=1;exitY=0.5;entryX=1;entryY=0.5;`

---

## Edge Routing Quality (MANDATORY VISUAL CHECKS)

Two rules that must hold in every diagram. Neither is enforced by the XML — they must be verified after rendering the PNG.

### Rule A: Edges must not cross non-endpoint boxes

If an edge's rendered path passes through a box that is neither its source nor its target, the diagram fails. The draw.io auto-router does not reroute around foreign boxes. Fix by **moving the offending box** or **reordering frames**, never by hand-placing waypoints.

```
Bad                               Good
──────────────────                ──────────────────
 ┌─────┐                           ┌─────┐
 │  A  │                           │  A  │
 └──┬──┘                           └──┬──┘
    │                                 │
  ┌─▼──┐          ┌─────┐            │        ┌─────┐
  │ B  ├──────────►  X  │            │        │  X  │
  └────┘          └─────┘           ┌┴────────►     │
    │              ▲                 │  B      └─────┘
    └──cuts────────┘                 │
       through                       │  (B now next to A,
       box B                         │   A→X routes clean)
```

### Rule B: Max 2 turns per edge

An orthogonal edge should have at most 2 elbow bends between source and target. U-turns, zig-zags, and 4-bend snakes are layout bugs, not routing bugs. The fix is the same as Rule A: move a box.

### Rule C: Converging arrows merge into ONE bind point on the target

When 3+ edges end at the same target box, **all incoming edges should enter the target at the exact same connection point** — same `entryX` AND same `entryY`. The arrowheads visually stack on top of each other at one shared spot on the target; the *tails* of the arrows fan out to reach their respective sources. From the target's perspective, the convergence looks like "one arrow with a branching tail", not like "N arrows landing at N different spots on my edge."

**Multiple edges sharing the same bind point is not a bug — it's the correct pattern.** Don't stagger the entry positions along one side of the target. Don't try to give each arrow its own unique landing spot. They all hit the same connector.

```
Good — arrowheads merge at one bind point    Bad — staggered entries (looks spray-arrayed)
──────────────────────────────────────────    ──────────────────────────────────────────
 ┌───┐                                         ┌───┐
 │ S1├──┐                                      │ S1├─────────►┌─────┐
 └───┘   ╲                                     └───┘          │  T  │◄── entryY=0.2
 ┌───┐    ╲                                    ┌───┐          │     │◄── entryY=0.4
 │ S2├─────╲                                   │ S2├─────────►│     │◄── entryY=0.6
 └───┘      ╲                                  └───┘          │     │◄── entryY=0.8
 ┌───┐       ╲                                 ┌───┐          └─────┘
 │ S3├────────▼──►┌─────┐                      │ S3├─────────►
 └───┘            │  T  │◄── all 4             └───┘
 ┌───┐            └─────┘    arrowheads        ┌───┐
 │ S4├─────────►              stacked          │ S4├─────────►
 └───┘                        at one                           (4 separate entry points —
                              entry point                       looks like the target is
                              (entryX=0,                        spray-arrayed, not fed)
                               entryY=0.5)

      Bad — octopus (arrows from all sides)
      ──────────────────────────────────────
                   ↓
        ┌───┐   ┌─────┐   ┌───┐
        │ S1├──►│  T  │◄──┤ S4│
        └───┘   └──▲──┘   └───┘
                   │
                ┌──┴──┐
                │ S2  │
                └─────┘
        Arrows arriving from N/S/E/W
```

**Implementation recipe for same-bind-point convergence:**
- Pick one side AND one position on that side. Typical: `entryX=0;entryY=0.5` (left-middle) or `entryX=0.5;entryY=0` (top-middle).
- **Every converging edge gets the same entryX and entryY values** — no staggering.
- Each source gets `exitX=1;exitY=0.5` (or whichever side faces the target). Source exit points don't need to be unique either, but staggering them slightly across sources usually helps if the sources are stacked vertically.
- All converging edges should be the **same color + same strokeWidth + same dash style**. Mixed styles into one bind point is confusing; either homogenize them or split the convergence into separate logical groups.
- Draw.io's orthogonal router will compute distinct approach paths from each source into the shared bind point. The arrowheads will visually overlap at the target; the tails will fan out.

**Why not stagger?** Staggering (distinct entryY per arrow) makes the target look "poked" by N independent arrows, which reads as "N unrelated inputs" rather than "one converged flow." Same-bind-point reads as "here are all the things that feed into this" — the correct mental model when the sources all contribute to the same logical input.

---

## Color-Coded Edges

Match edge color to semantic meaning:

| Role | strokeColor |
|------|-------------|
| Default | `#1e1e1e` |
| Deterministic | `#1971c2` |
| Agentic | `#e03131` |
| Mix | `#f08c00` |

---

## Dashed Edges

Use dashed connectors only for **return/response calls** (reply path back to a caller):
```
dashed=1;dashPattern=8 8;
```

Do **not** use dashed edges for optional/unknown, noteworthy exceptions, secondary outputs, or human-in-the-loop. Use solid edges plus explicit annotation/lane patterns for those semantics.

---

## Edge Labels

### Method 1: Value on Edge (Simple)

```xml
<mxCell id="edge-labeled" value="Label Text" style="..." edge="1" parent="frame-main" source="box-a" target="box-b">
```

### Method 2: Separate edgeLabel Cell (Styled)

For italic, colored labels:

```xml
<!-- The edge -->
<mxCell id="edge-main" style="..." edge="1" parent="frame-main" source="box-a" target="box-b">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- The label -->
<mxCell id="label-main" connectable="0" parent="edge-main" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];" value="&lt;span style=&quot;color: rgb(224, 49, 49); font-size: 12px; font-style: italic;&quot;&gt;Human Readable&lt;br&gt;Handoffs&lt;/span&gt;" vertex="1">
  <mxGeometry relative="1" x="-0.2" as="geometry">
    <mxPoint as="offset" />
  </mxGeometry>
</mxCell>
```

**Critical attributes:**
- `connectable="0"`
- `parent="edge-main"` (parent is the EDGE)
- `vertex="1"`
- Geometry `x`: position along edge (-1 to 1)

---

## Arrow Types

| Value | Use For |
|-------|---------|
| `classic` | Standard arrow (default) |
| `none` | Line only, no arrowhead |
| `block` | Block arrow |
| `open` | Open/unfilled arrow |

**Bidirectional:**
```
startArrow=classic;startFill=1;endArrow=classic;endFill=1;
```

---

## Style Properties Reference

| Property | Values | Description |
|----------|--------|-------------|
| `edgeStyle` | orthogonalEdgeStyle | Routing (always use this) |
| `rounded` | 0 | Sharp corners on bends |
| `orthogonalLoop` | 1 | Loop handling |
| `jettySize` | auto | Connector stubs |
| `strokeColor` | #hex | Line color |
| `strokeWidth` | 2 | Line thickness |
| `dashed` | 0, 1 | Dashed line |
| `dashPattern` | "8 8" | Dash pattern |
| `endArrow` | classic | Arrowhead style |
| `endFill` | 1 | Fill arrowhead |
| `exitX/exitY` | 0-1 | Exit point |
| `entryX/entryY` | 0-1 | Entry point |

---

## Quick Examples

### Standard Down Arrow
```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#1e1e1e;strokeWidth=2;endArrow=classic;endFill=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
```

### Blue Deterministic Flow
```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#1971c2;strokeWidth=2;endArrow=classic;endFill=1;"
```

### Red Dashed (Response/Return Path)
```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#e03131;strokeWidth=2;dashed=1;dashPattern=8 8;endArrow=classic;endFill=1;exitX=0;exitY=0.5;entryX=0;entryY=0.5;"
```
