# Brand Colors

Same color palette as excalidraw skill for visual consistency.

## Primary Palette

| Role | Hex | Usage |
|------|-----|-------|
| User/Default | `#1e1e1e` | Input, output, standard elements |
| Deterministic | `#1971c2` | Predictable logic, scripted flows |
| Agentic | `#e03131` | AI-driven, dynamic, unpredictable |
| Mix | `#f08c00` | Hybrid components, both human and AI |

## Color Application

**CRITICAL:** For color-coded elements, set BOTH strokeColor AND fontColor to the same value:

```xml
<!-- User/Default (black) -->
strokeColor=#1e1e1e;fontColor=#1e1e1e;

<!-- Deterministic (blue) -->
strokeColor=#1971c2;fontColor=#1971c2;

<!-- Agentic (red) -->
strokeColor=#e03131;fontColor=#e03131;

<!-- Mix (orange) -->
strokeColor=#f08c00;fontColor=#f08c00;
```

## Complete Box Examples

### User/Default Box
```xml
<mxCell id="box-input" value="User Input" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1e1e1e;strokeWidth=2;fontSize=14;fontColor=#1e1e1e;arcSize=15;" vertex="1" parent="frame-main">
```

### Deterministic Box (Blue)
```xml
<mxCell id="box-det" value="Deterministic&#xa;Processor" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1971c2;strokeWidth=2;fontSize=14;fontColor=#1971c2;arcSize=15;" vertex="1" parent="frame-main">
```

### Agentic Box (Red)
```xml
<mxCell id="box-agent" value="AI Agent" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e03131;strokeWidth=2;fontSize=14;fontColor=#e03131;arcSize=15;" vertex="1" parent="frame-main">
```

### Mix Box (Orange)
```xml
<mxCell id="box-mix" value="Human + AI" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#f08c00;strokeWidth=2;fontSize=14;fontColor=#f08c00;arcSize=15;" vertex="1" parent="frame-main">
```

### Indirect/Noteworthy Box (Dashed)
```xml
<mxCell id="box-indirect" value="Indirect&#xa;Response" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e03131;strokeWidth=2;fontSize=14;fontColor=#e03131;arcSize=15;dashed=1;dashPattern=8 8;" vertex="1" parent="frame-main">
```

---

## Edge Colors

Match edge strokeColor to semantic meaning:

```xml
<!-- Default edge -->
strokeColor=#1e1e1e;

<!-- Deterministic flow -->
strokeColor=#1971c2;

<!-- Agentic flow -->
strokeColor=#e03131;

<!-- Mixed flow -->
strokeColor=#f08c00;
```

---

## Legend Template

Inside the frame, top-right corner:

```xml
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

## Standard Properties

All elements share these base properties:

```
fillColor=#ffffff
strokeWidth=2
rounded=1
arcSize=15
whiteSpace=wrap
html=1
align=center
verticalAlign=middle
fontFamily=Helvetica
```
