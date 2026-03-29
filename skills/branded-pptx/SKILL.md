---
name: branded-pptx
description: "Create highly branded PowerPoint presentations from a template .pptx file. Use when the user provides a branded template and wants to generate new slides that look like a professional consultant created them — on-brand, on-layout, using the template's themes, slide masters, and layouts. Triggers on: 'branded deck', 'use this template to create', 'make a presentation matching this brand', 'on-brand slides', or any request to produce a .pptx that must follow an existing template's visual identity. REQUIRES the anthropic pptx skill (or equivalent) as a baseline — this skill does not replicate pptx reading/writing/editing capabilities, it layers brand-aware intelligence on top."
---

# Branded PPTX

Create presentations that look like a brand team designed them, not like AI generated them.

## Prerequisite

This skill depends on the **pptx** skill (anthropic/skills) for all file operations — reading, unpacking, editing XML, creating slides, QA, and image conversion. Load `/pptx` before proceeding. This skill provides the brand analysis layer and slide creation strategy on top.

## Workflow

### 1. Analyze the Template

**Always run this first.** The template is the single source of brand truth.

```bash
python3.12 scripts/analyze_template.py template.pptx --output-dir ./runs --run-id
```

This creates a self-contained timestamped run folder:
```
runs/2026-03-29T14-30-45/
├── template.pptx           # Copy of original template
├── brand-manifest.md       # Master index — read this first
├── theme.md                # Colors, fonts
├── layouts.md              # Layout inventory with dimensions
├── slide-masters.md        # Master backgrounds
├── slides.md               # Example slides with shape inventory
└── output/                 # Place generated .pptx and .pdf here
```

All working files (unpacked PPTX, thumbnails, output.pptx, output.pdf) go in this run folder.

**Read `brand-manifest.md` first** — it has everything needed for slide planning. Read the detailed files only when you need specifics.

Also generate thumbnails for visual reference:
```bash
python3.12 <pptx-skill>/scripts/thumbnail.py template.pptx <run-folder>/template-grid
```

### 2. Study the Brand System

Before creating any slides, internalize:

1. **Color palette**: From `theme.md` — which colors map to which semantic roles
2. **Typography**: Major (heading) and minor (body) fonts from the theme
3. **Layout inventory**: From `layouts.md` — available structures, placeholder-driven vs free-form
4. **Shape dimensions and capacity**: From `layouts.md` and `slides.md` — how much text fits in each text area, where shapes are positioned
5. **Visual patterns**: From `slides.md` + thumbnails — how the brand team intended each layout to be used
6. **Visual data elements**: From `slides.md` — which shapes contain embedded images/charts that text replacement cannot update

The example slides in the template are the gold standard.

### 3. Plan the Deck

For each content section, select a layout by matching content type to layout structure:

| Content Type | Look For |
|---|---|
| Cover / title | `title` or `ctrTitle` layout |
| Section break | `secHdr` layout |
| Single topic with bullets | `obj` layout (title + body) |
| Comparison / two topics | `twoObj` layout |
| Visual + text | `picTx` or image-bearing layouts |
| Data / metrics | Layouts with chart or table placeholders |
| Free-form / custom | `blank` or `titleOnly` layout |
| Blank-layout template | All examples use `blank` — duplicate the closest example slide |

**Vary layouts deliberately.** A branded deck is never 15 slides of the same layout.

#### Blank Layout + Custom Shapes Pattern

Many professional templates (McKinsey, BCG, Bain style) do NOT use standard placeholder layouts. Instead, all slides use BLANK layout with free-form positioned shapes.

When `brand-manifest.md` reports "Template Style: Blank Layout + Custom Shapes":
1. **Do not use placeholder-based layouts.** The custom layouts exist but are not how the brand team builds slides.
2. **Duplicate example slides** as the primary strategy. Each example slide IS the layout — its shapes are the structure.
3. **Use the Shape Inventory** from `slides.md` to identify which shapes carry editable text, which are decorative, and which carry visual data.
4. **Respect exact positions and sizes.** Since there is no placeholder inheritance, the shape's position values are the truth. Do not reposition shapes.
5. **Check text capacity** before writing content. If text exceeds the estimated character count, shorten it rather than overflowing.

### 4. Build Slides

Use the pptx skill's template editing workflow:
1. Unpack the template into the run folder
2. Duplicate/add slides using the planned layout mapping
3. Edit content in each slide XML — **fill placeholders or edit shapes in-place**
4. Clean and pack

**Brand fidelity rules during editing:**

- **Use theme colors** via `schemeClr` references, never hardcoded hex
- **Fill placeholders** or **edit shapes in-place** — preserve the inheritance chain and positioning
- **Match content density** to what the example slides demonstrate
- **Preserve decorative elements** in layouts (accent bars, background shapes, dividers)
- **Mirror the example** — replicate its visual pattern: same emphasis structure, similar content length
- **Respect inheritance** — let styles cascade from theme → master → layout → slide
- **Check text capacity** before writing content. Use the capacity estimates from the manifest to ensure content fits
- **Flag visual data elements** — images and charts carry embedded data values. Options: replace the image, remove the shape, or flag for manual update

For blank-layout templates:
1. Duplicate the example slide closest to your target content
2. Identify editable text shapes by `shape_type: textbox` and non-empty text in the Shape Inventory
3. Replace text within existing `<a:r>` runs — preserve all `<a:rPr>` attributes
4. Do NOT add new shapes or reposition existing ones

For detailed OOXML structure: read [references/ooxml-brand-structure.md](references/ooxml-brand-structure.md).

### 5. QA for Brand Compliance

After building, run the pptx skill's standard QA process AND check brand-specific issues:

**Content QA** (via pptx skill):
```bash
python3.12 -m markitdown output.pptx
```

**Visual QA** — use subagents with this extended prompt:

```
Visually inspect these slides against the template thumbnails. Assume there are brand issues — find them.

Look for standard issues (overlaps, overflow, alignment) PLUS:
- Text overflow: compare text length against capacity estimates in the manifest
- Slides that don't match the visual pattern of example slides using the same layout
- Text boxes that appear free-floating rather than in template shapes
- Colors that don't match the brand palette
- Font inconsistencies (wrong typeface, wrong weight)
- Content density mismatches (too many or too few items vs examples)
- Missing decorative elements that the layout should provide
- Layouts repeated too many times without variety
- Visual data staleness: shapes flagged as [VISUAL DATA] — verify their content matches new data
- Shape position drift: for blank-layout slides, verify shapes haven't moved from template positions
```

Compare each output slide against the closest matching example slide from the template.

## Dependencies

This skill requires the **pptx** skill (`anthropic/skills`) or equivalent for all PPTX file operations.

System dependencies:
- **Python 3.12+** (`python3.12`) — required for native type syntax
- `pip install defusedxml` — XML parsing for analyze_template.py
- `pip install "markitdown[pptx]"` — text extraction (via pptx skill)
- `pip install Pillow` — thumbnails (via pptx skill)
- `pip install lxml` — pack.py validation (via pptx skill)
- LibreOffice (`soffice`) — PDF conversion (`brew install --cask libreoffice`)
- Poppler (`pdftoppm`) — PDF to images (`brew install poppler`)
