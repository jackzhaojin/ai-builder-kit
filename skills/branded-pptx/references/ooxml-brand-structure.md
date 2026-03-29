# OOXML Brand Structure Reference

## Hierarchy

```
Theme (ppt/theme/themeN.xml)
  └─ Slide Master (ppt/slideMasters/slideMasterN.xml)
       └─ Slide Layout (ppt/slideLayouts/slideLayoutN.xml)
            └─ Slide (ppt/slides/slideN.xml)
```

Each level inherits from the one above. A slide inherits from its layout, which inherits from its master, which inherits from its theme. **Brand fidelity means respecting this chain.**

## Theme (`a:theme`)

The theme defines the brand's visual DNA:

- **Color scheme** (`a:clrScheme`): 12 semantic color slots
  - `dk1`, `dk2` — dark colors (text on light backgrounds)
  - `lt1`, `lt2` — light colors (text on dark backgrounds, backgrounds)
  - `accent1`–`accent6` — brand accent colors
  - `hlink`, `folHlink` — hyperlink colors
- **Font scheme** (`a:fontScheme`): major (headings) + minor (body) typefaces
- **Format scheme** (`a:fmtScheme`): fill, line, and effect styles

**Rule**: Never hardcode colors when theme colors are available. Use `schemeClr` references (e.g., `<a:schemeClr val="accent1"/>`) to stay on-brand even if the theme changes.

## Slide Master (`p:sldMaster`)

Masters define the shared visual frame:
- Background fills/patterns
- Default placeholder positions and styles
- Logo placement, footer areas, slide number positions
- Color mapping overrides (`p:clrMap`)

**Rule**: Content added to a master appears on every slide using that master. Only put persistent brand elements here (logos, footer bars).

## Slide Layout (`p:sldLayout`)

Layouts are the reusable slide templates. Each layout:
- Belongs to exactly one master
- Defines placeholder types, positions, and sizes
- May include decorative shapes (dividers, accent bars, background elements)
- Has a `type` attribute (e.g., `title`, `obj`, `twoObj`, `secHdr`, `blank`)

### Common Layout Types
| Type | Typical Use |
|------|-------------|
| `title` | Title slide / cover |
| `obj` | Title + content (single body) |
| `twoObj` | Two-column content |
| `secHdr` | Section header / divider |
| `twoTxTwoObj` | Text + object pairs |
| `titleOnly` | Title with free-form content area |
| `blank` | No placeholders, fully custom |
| `picTx` | Picture with text |
| `custom` | Template-specific layouts |

### Placeholder Types
| Type | Purpose |
|------|---------|
| `title` | Slide title |
| `ctrTitle` | Centered title (title slides) |
| `subTitle` | Subtitle |
| `body` | Main content area |
| `dt` | Date/time |
| `ftr` | Footer text |
| `sldNum` | Slide number |
| `pic` | Picture placeholder |
| `tbl` | Table placeholder |
| `chart` | Chart placeholder |

**Rule**: When creating slides, always use the layout's placeholders rather than creating free-floating text boxes. Placeholders inherit the brand's typography, positioning, and spacing. Free-floating boxes break the inheritance chain.

## Shape Positioning (`a:xfrm`)

Every shape has position and size defined by `<a:xfrm>` inside its `<p:spPr>`:

```xml
<p:spPr>
  <a:xfrm>
    <a:off x="457200" y="914400"/>   <!-- position: 0.5", 1.0" -->
    <a:ext cx="7315200" cy="1371600"/> <!-- size: 8.0" x 1.5" -->
  </a:xfrm>
</p:spPr>
```

**Units**: EMU (English Metric Units)
- 914400 EMU = 1 inch
- 12700 EMU = 1 point
- To convert: `inches = emu / 914400`, `points = emu / 12700`

**Group shapes** (`p:grpSp`) use `<a:chOff>` and `<a:chExt>` to define a child coordinate space. Children are positioned relative to the group's internal coordinate system, then scaled to the group's actual size.

## Font Sizes in OOXML

Font sizes in `<a:rPr>` use hundredths of a point:

```xml
<a:rPr sz="2400" b="1">  <!-- 24pt bold -->
  <a:latin typeface="Cardo"/>  <!-- explicit font override -->
</a:rPr>
```

- `sz="2400"` = 24pt, `sz="1400"` = 14pt, `sz="1000"` = 10pt
- Font inheritance: run `<a:rPr>` → paragraph `<a:pPr>` → shape defaults → layout → master → theme
- `<a:latin typeface="...">` overrides the theme font for that run

**Capacity estimation**: For a text box of width W points and font size S points:
- Characters per line ≈ W / (S × 0.6)
- Max lines ≈ height in points / (S × 1.3)
- These are estimates — actual capacity varies with specific characters and kerning

## Visual Data Elements

Some shapes carry embedded data values that **text replacement cannot update**:

**`p:pic` (pictures)**: Images that may contain baked-in data — infographics, donut charts rendered as PNG/JPEG, data visualizations. Replacing the text label next to a chart image does NOT change the chart itself.

**`p:graphicFrame` (graphic frames)**: Native OOXML charts (`<c:chart>`), tables (`<a:tbl>`), diagrams (`<dgm:relIds>`). These store data in separate XML parts. Updating them requires editing the chart's data spreadsheet or table cells directly.

**Identification**: The `analyze_template.py` script flags these with `[VISUAL DATA]` in the shape inventory. When planning content, decide for each visual data element:
1. Replace the embedded image/chart with a new one
2. Remove the shape if the data is irrelevant
3. Flag it for manual update post-generation

## The Blank Layout Pattern

Professional consulting templates (McKinsey, BCG, Bain, Deloitte) commonly build all slides on the BLANK layout with precisely positioned free-form shapes rather than using typed placeholder layouts.

**Why**: Gives the brand team pixel-perfect control over every element — custom accent bars, positioned image frames, multi-zone text areas — without being constrained by OOXML's limited placeholder types.

**Implications for AI-generated slides**:
- There is **no placeholder inheritance** — each shape's position, font, and color are explicitly set
- The example slides in the template ARE the layouts — duplicate them, don't start from blank
- Every shape's `<a:xfrm>` position is load-bearing — do not reposition
- Font styles in `<a:rPr>` are the source of truth, not inherited from the theme
- Decorative shapes (colored bars, background rectangles, accent lines) are brand elements — preserve them exactly

**Strategy**: Use the Shape Inventory in `slides.md` to identify textbox shapes with editable content, then edit text in-place while preserving all XML attributes.

## Key Brand Fidelity Rules

1. **Match content to layout**: Choose the layout whose structure fits the content
2. **Respect placeholders**: Fill them, don't replace them with free-form shapes
3. **Use theme colors**: Reference `schemeClr` values, not hardcoded hex
4. **Mirror example slides**: Replicate their visual pattern (spacing, emphasis, content density)
5. **Preserve decorative elements**: Accent shapes in layouts are brand elements, not clutter
6. **Maintain content density**: Match the bullet count and text length of example slides
7. **Vary layouts**: Use multiple layouts strategically, not one layout repeated
8. **Check content capacity**: Estimate whether text fits the target box before writing — width in points / (font size × 0.6) gives approximate characters per line
9. **Handle visual data explicitly**: Images and charts carry embedded data — text replacement does not update them
10. **Blank-layout slides are position-critical**: Every shape's x/y/cx/cy defines the design — do not reposition
