# Draw.io XML Format Reference

## File Structure

Every `.drawio` file follows this XML structure:

```xml
<mxfile host="Electron" agent="Mozilla/5.0..." version="29.3.0">
  <diagram name="Page-1" id="page-1">
    <mxGraphModel dx="1709" dy="747" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="2200" pageHeight="1400" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- All diagram elements go here -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### Required Root Cells

Every diagram MUST include these two cells first:
```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />
```

- Cell `0` is the absolute root
- Cell `1` is the default parent for all top-level elements

---

## Shape Elements (Vertices)

All shapes are `mxCell` elements with `vertex="1"`.

### Rounded Rectangle (PRIMARY - Use This)

```xml
<mxCell id="box-example" value="Label Text" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1e1e1e;strokeWidth=2;fontSize=14;fontColor=#1e1e1e;arcSize=15;align=center;verticalAlign=middle;fontFamily=Helvetica;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="160" height="60" as="geometry" />
</mxCell>
```

**Key style properties:**
- `rounded=1;arcSize=15` - Rounded corners (15% arc)
- `whiteSpace=wrap;html=1` - Enable text wrapping
- `align=center;verticalAlign=middle` - Center text
- `fontFamily=Helvetica` - Consistent font
- `fillColor=#ffffff` - White background
- `strokeWidth=2` - Standard border thickness

**Sizing guide:**
- Single line: 120-150 wide x 50 tall
- Two lines: 150-160 wide x 60 tall
- Three+ lines: 160-180 wide x 70-80 tall

### Color-Coded Box (Matching Stroke and Font)

When using semantic colors, match BOTH strokeColor AND fontColor:

```xml
<!-- Blue (Deterministic) -->
<mxCell id="box-det" value="Deterministic" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1971c2;strokeWidth=2;fontSize=14;fontColor=#1971c2;arcSize=15;" vertex="1" parent="1">

<!-- Red (Agentic) -->
<mxCell id="box-agent" value="Agentic" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e03131;strokeWidth=2;fontSize=14;fontColor=#e03131;arcSize=15;" vertex="1" parent="1">

<!-- Orange (Mix) -->
<mxCell id="box-mix" value="Mix" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#f08c00;strokeWidth=2;fontSize=14;fontColor=#f08c00;arcSize=15;" vertex="1" parent="1">
```

### Database Cylinder (Persistent Data Store)

For persistent data stores — databases, object stores, queues — use `shape=cylinder3` to visually distinguish storage from services/processes. **Use a cylinder whenever a data store is a first-class element**, especially when one service owns multiple distinct stores; rendering them as labeled rectangles loses the service-vs-storage distinction.

```xml
<mxCell id="store-events" value="Events&#xa;(Postgres)" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffffff;strokeColor=#1971c2;strokeWidth=2;fontSize=14;fontColor=#1971c2;fontFamily=Helvetica;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="80" height="80" as="geometry" />
</mxCell>
```

**Key style properties:**
- `shape=cylinder3` — cylinder with top ellipse rendered as the "lid"
- `boundedLbl=1;backgroundOutline=1` — keeps the label inside the body, not on top of the lid
- `size=15` — controls the lid height
- Standard sizing: 80×80 (single store) or 100×80 (two-line label). One color rule still applies: match `strokeColor` AND `fontColor`.

When a service owns multiple stores, draw the service box once and connect it to each cylinder — do not encode multiple stores as a single rectangle's text label.

### Dashed Box (Optional / Unknown — use sparingly)

Reserve dashed boxes for elements whose existence is uncertain or explicitly optional. Do **not** use a dashed box for "noteworthy," "indirect," "secondary," or "human-in-the-loop" — those have dedicated treatments (see `diagram-style.md`). Dashed must mean exactly one thing in the diagram or the signal collapses.

```xml
<mxCell id="box-optional" value="Optional&#xa;Component" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1e1e1e;strokeWidth=2;fontSize=14;fontColor=#1e1e1e;arcSize=15;dashed=1;dashPattern=8 8;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="120" height="50" as="geometry" />
</mxCell>
```

### Text Only (No Border)

```xml
<mxCell id="text-label" value="Text Label" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=12;fontColor=#1e1e1e;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="80" height="20" as="geometry" />
</mxCell>
```

---

## Swimlanes/Containers (Frames)

Swimlanes group related elements. All children use the swimlane's ID as their parent.

### Swimlane Structure

```xml
<!-- Container frame -->
<mxCell id="frame-main" value="Frame Title" style="swimlane;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1e1e1e;strokeWidth=2;fontSize=14;fontStyle=0;fontColor=#1e1e1e;startSize=30;rounded=0;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="920" height="820" as="geometry" />
</mxCell>

<!-- Child element INSIDE swimlane (relative coordinates) -->
<mxCell id="box-child" value="Child Box" style="rounded=1;..." vertex="1" parent="frame-main">
  <mxGeometry x="190" y="50" width="160" height="60" as="geometry" />
</mxCell>
```

**Critical points:**
- `parent="frame-main"` - Child references swimlane ID
- Child coordinates are RELATIVE to swimlane origin
- `startSize=30` - Header height for title
- `rounded=0` - Swimlanes have square corners
- `fontStyle=0` - Normal text (not italic)

### Legend INSIDE Frame (Top-Right Corner)

Position legend items inside the frame, top-right:

```xml
<!-- Legend items as children of the frame -->
<mxCell id="legend-user" value="User" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1e1e1e;strokeWidth=2;fontSize=12;fontColor=#1e1e1e;arcSize=15;" vertex="1" parent="frame-main">
  <mxGeometry x="740" y="50" width="100" height="30" as="geometry" />
</mxCell>

<mxCell id="legend-det" value="Deterministic" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1971c2;strokeWidth=2;fontSize=12;fontColor=#1971c2;arcSize=15;" vertex="1" parent="frame-main">
  <mxGeometry x="740" y="90" width="100" height="30" as="geometry" />
</mxCell>

<mxCell id="legend-agent" value="Agentic" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e03131;strokeWidth=2;fontSize=12;fontColor=#e03131;arcSize=15;" vertex="1" parent="frame-main">
  <mxGeometry x="740" y="130" width="100" height="30" as="geometry" />
</mxCell>

<mxCell id="legend-mix" value="Mix" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#f08c00;strokeWidth=2;fontSize=12;fontColor=#f08c00;arcSize=15;" vertex="1" parent="frame-main">
  <mxGeometry x="740" y="170" width="100" height="30" as="geometry" />
</mxCell>
```

---

## Connectors/Edges (Arrows)

Edges connect shapes. They are `mxCell` elements with `edge="1"`.

### Basic Edge Structure

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
- `edgeStyle=orthogonalEdgeStyle` - Right-angle routing
- `rounded=0` - Sharp corners on bends
- `orthogonalLoop=1;jettySize=auto` - Loop handling
- `strokeWidth=2` - Match box stroke width
- `endArrow=classic;endFill=1` - Standard arrowhead

### Color-Coded Edges

Match edge color to semantic meaning:

```xml
<!-- Blue edge (deterministic flow) -->
style="...strokeColor=#1971c2;..."

<!-- Red edge (agentic flow) -->
style="...strokeColor=#e03131;..."

<!-- Dashed red edge (indirect/noteworthy response) -->
style="...strokeColor=#e03131;dashed=1;dashPattern=8 8;..."
```

### Feedback Loops (CRITICAL PATTERN)

For arrows that loop back to an earlier element, use same-side exit and entry:

```xml
<!-- Left-side feedback: exits left, enters left of target above -->
<mxCell id="edge-feedback-left" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#e03131;strokeWidth=2;endArrow=classic;exitX=0;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="frame-main" source="box-lower" target="box-upper">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- Right-side feedback: exits right, enters right of target above -->
<mxCell id="edge-feedback-right" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#e03131;strokeWidth=2;endArrow=classic;exitX=1;exitY=0.5;entryX=1;entryY=0.5;" edge="1" parent="frame-main" source="box-lower" target="box-upper">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**Key insight:** Draw.io auto-routes feedback loops correctly when:
- Both exit and entry are on the SAME side (both left or both right)
- Use `exitX=0` / `entryX=0` for left side
- Use `exitX=1` / `entryX=1` for right side
- No waypoints needed!

### Connection Points Reference

| Position | exitX/entryX | exitY/entryY |
|----------|--------------|--------------|
| Top-center | 0.5 | 0 |
| Bottom-center | 0.5 | 1 |
| Left-center | 0 | 0.5 |
| Right-center | 1 | 0.5 |

---

## Edge Labels (Two Methods)

### Method 1: Value on Edge (Simple)

```xml
<mxCell id="edge-labeled" value="Label Text" style="edgeStyle=orthogonalEdgeStyle;..." edge="1" parent="frame-main" source="box-a" target="box-b">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### Method 2: Separate edgeLabel Cell (Styled)

For styled labels (italic, colored), create a separate cell:

```xml
<!-- The edge -->
<mxCell id="edge-main" style="edgeStyle=orthogonalEdgeStyle;..." edge="1" parent="frame-main" source="box-a" target="box-b">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- The label (parent is the edge!) -->
<mxCell id="edge-main-label" connectable="0" parent="edge-main" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];" value="&lt;span style=&quot;color: rgb(224, 49, 49); font-size: 12px; font-style: italic;&quot;&gt;Human Readable&lt;br&gt;Handoffs&lt;/span&gt;" vertex="1">
  <mxGeometry relative="1" x="-0.2" as="geometry">
    <mxPoint as="offset" />
  </mxGeometry>
</mxCell>
```

**Critical attributes:**
- `connectable="0"` - Not connectable
- `parent="edge-main"` - Parent is the EDGE, not the frame
- `vertex="1"` - Technically a vertex
- `style="edgeLabel;..."` - Edge label style
- Geometry `x` value: position along edge (-1 to 1, 0 = center)
- Use HTML `<span style="...">` for color and italic

---

## Style Property Reference

### Box Styles

| Property | Value | Description |
|----------|-------|-------------|
| `rounded` | 0, 1 | Rounded corners |
| `arcSize` | 15 | Corner radius (use 15) |
| `fillColor` | #ffffff | Background (white) |
| `strokeColor` | #hex | Border color |
| `strokeWidth` | 2 | Border thickness |
| `fontSize` | 14, 12 | Text size |
| `fontColor` | #hex | Text color (match strokeColor) |
| `fontStyle` | 0 | 0=normal, 1=bold, 2=italic |
| `fontFamily` | Helvetica | Font face |
| `align` | center | Horizontal alignment |
| `verticalAlign` | middle | Vertical alignment |
| `whiteSpace` | wrap | Enable wrapping |
| `html` | 1 | Enable HTML |
| `dashed` | 1 | Dashed border |
| `dashPattern` | 8 8 | Dash pattern |

### Edge Styles

| Property | Value | Description |
|----------|-------|-------------|
| `edgeStyle` | orthogonalEdgeStyle | Routing algorithm |
| `rounded` | 0 | Sharp corners on bends |
| `orthogonalLoop` | 1 | Loop handling |
| `jettySize` | auto | Connector stubs |
| `strokeColor` | #hex | Line color |
| `strokeWidth` | 2 | Line thickness |
| `endArrow` | classic | Arrowhead style |
| `endFill` | 1 | Fill arrowhead |
| `exitX/exitY` | 0-1 | Exit point |
| `entryX/entryY` | 0-1 | Entry point |

---

## ID Conventions

| Element | Pattern | Example |
|---------|---------|---------|
| Frame | `frame-{name}` | `frame-main` |
| Box | `box-{name}` | `box-ailog` |
| Edge | `edge-{src}-{tgt}` | `edge-spec-ailog` |
| Legend | `legend-{type}` | `legend-det` |
| Text | `text-{desc}` | `text-title` |
