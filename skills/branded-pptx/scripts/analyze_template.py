#!/usr/bin/env python3.12
"""Analyze a branded PPTX template and produce AI-readable manifests.

Extracts themes, slide masters, layouts, and example slides into structured
markdown files. Includes shape dimensions, font info, text capacity estimates,
and visual data element tracking for brand-faithful slide generation.

Usage:
    python3.12 analyze_template.py <template.pptx> [--output-dir <dir>] [--run-id]

Output (in <dir> or timestamped subfolder with --run-id):
    brand-manifest.md      - Master index with capacity reference and warnings
    theme.md               - Color schemes, fonts, and format schemes
    slide-masters.md       - Slide master descriptions and relationships
    layouts.md             - All slide layouts with shape dimensions and capacity
    slides.md              - Example slides with shape inventory and visual data flags

Dependencies:
    pip install defusedxml
"""

import argparse
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import defusedxml.minidom

EMU_PER_INCH = 914400
EMU_PER_PT = 12700
CHAR_WIDTH_RATIO = 0.6  # average char width as fraction of font size
LINE_HEIGHT_RATIO = 1.3  # line height as fraction of font size


def main():
    parser = argparse.ArgumentParser(description="Analyze branded PPTX template")
    parser.add_argument("template", help="Path to .pptx template file")
    parser.add_argument("--output-dir", help="Output directory (default: same as template)")
    parser.add_argument("--run-id", action="store_true",
                        help="Auto-create ISO 8601 timestamped subfolder")
    args = parser.parse_args()

    template_path = Path(args.template)
    if not template_path.exists() or template_path.suffix.lower() != ".pptx":
        print(f"Error: Invalid .pptx file: {args.template}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else template_path.parent

    if args.run_id:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        output_dir = output_dir / timestamp

    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy template into run folder so everything is self-contained
    run_template = output_dir / template_path.name
    if run_template != template_path.resolve():
        shutil.copy2(template_path, run_template)

    # Create output subdirectories
    (output_dir / "output").mkdir(exist_ok=True)

    print(f"Analyzing: {template_path.name}")
    if args.run_id:
        print(f"Run folder: {output_dir}")
    print(f"Output dir: {output_dir / 'output'} (place .pptx and .pdf here)")

    with zipfile.ZipFile(template_path, "r") as zf:
        theme_data = extract_themes(zf)
        master_data = extract_slide_masters(zf)
        layout_data = extract_layouts(zf, master_data)
        slide_data = extract_slides(zf, layout_data)
        meta = extract_metadata(zf)

    write_theme_md(output_dir, theme_data, template_path.name)
    write_masters_md(output_dir, master_data, template_path.name)
    write_layouts_md(output_dir, layout_data, template_path.name)
    write_slides_md(output_dir, slide_data, template_path.name)
    write_manifest(output_dir, template_path.name, meta, theme_data,
                   master_data, layout_data, slide_data)

    print(f"\nManifest files written to: {output_dir}")
    print(f"  brand-manifest.md  (master index)")
    print(f"  theme.md           ({len(theme_data)} theme(s))")
    print(f"  slide-masters.md   ({len(master_data)} master(s))")
    print(f"  layouts.md         ({len(layout_data)} layout(s))")
    print(f"  slides.md          ({len(slide_data)} slide(s))")


# ---------------------------------------------------------------------------
# Theme extraction
# ---------------------------------------------------------------------------

def extract_themes(zf: zipfile.ZipFile) -> list[dict]:
    themes = []
    theme_files = sorted(n for n in zf.namelist()
                         if re.match(r"ppt/theme/theme\d+\.xml", n))

    for tf in theme_files:
        dom = defusedxml.minidom.parseString(zf.read(tf))
        theme = {"file": tf, "name": "", "colors": {}, "fonts": {},
                 "format_scheme": ""}

        for elem in dom.getElementsByTagName("a:theme"):
            theme["name"] = elem.getAttribute("name") or Path(tf).stem

        for clr_scheme in dom.getElementsByTagName("a:clrScheme"):
            theme["color_scheme_name"] = clr_scheme.getAttribute("name")
            for child in clr_scheme.childNodes:
                if child.nodeType == child.ELEMENT_NODE:
                    color_name = child.localName
                    for gc in child.childNodes:
                        if gc.nodeType == gc.ELEMENT_NODE:
                            val = (gc.getAttribute("val")
                                   or gc.getAttribute("lastClr"))
                            if val:
                                theme["colors"][color_name] = {
                                    "type": gc.localName, "value": val}

        for font_scheme in dom.getElementsByTagName("a:fontScheme"):
            theme["font_scheme_name"] = font_scheme.getAttribute("name")
            for major in dom.getElementsByTagName("a:majorFont"):
                for latin in major.getElementsByTagName("a:latin"):
                    theme["fonts"]["major"] = latin.getAttribute("typeface")
            for minor in dom.getElementsByTagName("a:minorFont"):
                for latin in minor.getElementsByTagName("a:latin"):
                    theme["fonts"]["minor"] = latin.getAttribute("typeface")

        for fmt_scheme in dom.getElementsByTagName("a:fmtScheme"):
            theme["format_scheme"] = fmt_scheme.getAttribute("name")

        themes.append(theme)
    return themes


# ---------------------------------------------------------------------------
# Slide master extraction
# ---------------------------------------------------------------------------

def extract_slide_masters(zf: zipfile.ZipFile) -> list[dict]:
    masters = []
    master_files = sorted(
        n for n in zf.namelist()
        if re.match(r"ppt/slideMasters/slideMaster\d+\.xml", n))

    for mf in master_files:
        dom = defusedxml.minidom.parseString(zf.read(mf))
        master = {"file": mf, "name": Path(mf).stem,
                  "placeholders": [], "background": None}

        for sp in dom.getElementsByTagName("p:sp"):
            shape = _classify_shape(sp, "p:sp")
            if shape["placeholder"]:
                master["placeholders"].append(shape)

        for bg in dom.getElementsByTagName("p:bg"):
            master["background"] = _summarize_background(bg)

        rels_path = mf.replace("slideMasters/",
                               "slideMasters/_rels/") + ".rels"
        master["layout_files"] = []
        master["theme_file"] = None
        if rels_path in zf.namelist():
            rels_dom = defusedxml.minidom.parseString(zf.read(rels_path))
            for rel in rels_dom.getElementsByTagName("Relationship"):
                target = rel.getAttribute("Target")
                rel_type = rel.getAttribute("Type")
                if "slideLayout" in rel_type:
                    master["layout_files"].append(
                        target.replace("../slideLayouts/", ""))
                elif "theme" in rel_type:
                    master["theme_file"] = target.replace("../theme/", "")

        masters.append(master)
    return masters


# ---------------------------------------------------------------------------
# Layout extraction
# ---------------------------------------------------------------------------

def extract_layouts(zf: zipfile.ZipFile, masters: list[dict]) -> list[dict]:
    layouts = []
    layout_files = sorted(
        n for n in zf.namelist()
        if re.match(r"ppt/slideLayouts/slideLayout\d+\.xml", n))

    layout_master_map = {}
    for master in masters:
        for lf in master["layout_files"]:
            layout_master_map[lf] = master["name"]

    for lf in layout_files:
        dom = defusedxml.minidom.parseString(zf.read(lf))
        layout = {
            "file": lf,
            "filename": Path(lf).name,
            "name": "",
            "type": "",
            "master": layout_master_map.get(Path(lf).name, "unknown"),
            "shapes": [],
            "placeholders": [],
            "non_placeholder_shapes": [],
        }

        for cSld in dom.getElementsByTagName("p:cSld"):
            layout["name"] = cSld.getAttribute("name") or ""
        for sldLayout in dom.getElementsByTagName("p:sldLayout"):
            layout["type"] = sldLayout.getAttribute("type") or ""

        # Classify ALL shapes
        for tag in ("p:sp", "p:pic", "p:graphicFrame", "p:grpSp"):
            for elem in dom.getElementsByTagName(tag):
                # Skip nested shapes (inside groups) at top level
                if _is_nested(elem, dom):
                    continue
                shape = _classify_shape(elem, tag)
                layout["shapes"].append(shape)
                if shape["placeholder"]:
                    layout["placeholders"].append(shape)
                else:
                    layout["non_placeholder_shapes"].append(shape)

        layouts.append(layout)
    return layouts


# ---------------------------------------------------------------------------
# Slide extraction
# ---------------------------------------------------------------------------

def extract_slides(zf: zipfile.ZipFile, layouts: list[dict]) -> list[dict]:
    slides = []

    pres_dom = defusedxml.minidom.parseString(zf.read("ppt/presentation.xml"))
    rels_dom = defusedxml.minidom.parseString(
        zf.read("ppt/_rels/presentation.xml.rels"))

    rid_to_slide = {}
    for rel in rels_dom.getElementsByTagName("Relationship"):
        rid = rel.getAttribute("Id")
        target = rel.getAttribute("Target")
        if target.startswith("slides/slide"):
            rid_to_slide[rid] = target

    slide_order = []
    for sld_id in pres_dom.getElementsByTagName("p:sldId"):
        rid = sld_id.getAttribute("r:id")
        if rid in rid_to_slide:
            slide_order.append(rid_to_slide[rid])

    layout_name_map = {
        l["filename"]: l["name"] or l["type"] or l["filename"]
        for l in layouts}

    for idx, slide_path in enumerate(slide_order, 1):
        full_path = f"ppt/{slide_path}"
        if full_path not in zf.namelist():
            continue

        dom = defusedxml.minidom.parseString(zf.read(full_path))
        slide = {
            "number": idx,
            "file": full_path,
            "filename": Path(slide_path).name,
            "layout": None,
            "layout_file": None,
            "shapes": [],
            "visual_data_elements": [],
            "text_content": [],
        }

        # Find linked layout
        rels_path = full_path.replace("slides/", "slides/_rels/") + ".rels"
        if rels_path in zf.namelist():
            slide_rels = defusedxml.minidom.parseString(zf.read(rels_path))
            for rel in slide_rels.getElementsByTagName("Relationship"):
                target = rel.getAttribute("Target")
                rel_type = rel.getAttribute("Type")
                if "slideLayout" in rel_type:
                    layout_file = target.replace("../slideLayouts/", "")
                    slide["layout_file"] = layout_file
                    slide["layout"] = layout_name_map.get(
                        layout_file, layout_file)

        # Classify ALL shapes
        for tag in ("p:sp", "p:pic", "p:graphicFrame", "p:grpSp"):
            for elem in dom.getElementsByTagName(tag):
                if _is_nested(elem, dom):
                    continue
                shape = _classify_shape(elem, tag)
                slide["shapes"].append(shape)

                if shape["visual_data"]:
                    slide["visual_data_elements"].append(shape)

                if shape["text"]:
                    slide["text_content"].append({
                        "placeholder": shape["placeholder"],
                        "text": shape["text"],
                        "shape_name": shape["name"],
                        "xfrm": shape["xfrm"],
                        "font_info": shape["font_info"],
                        "capacity": shape["capacity"],
                    })

        slides.append(slide)
    return slides


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

def extract_metadata(zf: zipfile.ZipFile) -> dict:
    meta = {"slide_size": None}
    pres_dom = defusedxml.minidom.parseString(zf.read("ppt/presentation.xml"))
    for sz in pres_dom.getElementsByTagName("p:sldSz"):
        cx = int(sz.getAttribute("cx") or 0)
        cy = int(sz.getAttribute("cy") or 0)
        meta["slide_size"] = {
            "width_emu": cx, "height_emu": cy,
            "width_in": round(cx / EMU_PER_INCH, 2),
            "height_in": round(cy / EMU_PER_INCH, 2),
        }
    return meta


# ---------------------------------------------------------------------------
# Shape helpers
# ---------------------------------------------------------------------------

def _is_nested(elem, dom) -> bool:
    """Check if element is inside a p:grpSp (skip nested shapes at top level)."""
    parent = elem.parentNode
    while parent and parent != dom.documentElement:
        if parent.nodeName == "p:grpSp":
            return True
        parent = parent.parentNode
    return False


def _classify_shape(elem, tag: str) -> dict:
    """Classify any shape element into a structured record."""
    shape = {
        "id": "",
        "name": "",
        "tag": tag,
        "shape_type": "decorative",
        "placeholder": None,
        "is_textbox": False,
        "xfrm": None,
        "font_info": [],
        "capacity": None,
        "text": "",
        "visual_data": False,
        "children": [],
    }

    # Extract id and name from cNvPr
    for cNvPr in elem.getElementsByTagName("p:cNvPr"):
        shape["id"] = cNvPr.getAttribute("id") or ""
        shape["name"] = cNvPr.getAttribute("name") or ""
        break  # first one only

    # Extract position/size
    shape["xfrm"] = _extract_xfrm(elem)

    if tag == "p:sp":
        # Check placeholder
        shape["placeholder"] = _extract_placeholder(elem)

        # Check textbox
        for cNvSpPr in elem.getElementsByTagName("p:cNvSpPr"):
            if cNvSpPr.getAttribute("txBox") == "1":
                shape["is_textbox"] = True

        # Classify type
        if shape["placeholder"]:
            shape["shape_type"] = "placeholder"
        elif shape["is_textbox"]:
            shape["shape_type"] = "textbox"

        # Extract text and font info
        shape["text"] = _extract_text_runs(elem)
        shape["font_info"] = _extract_font_info(elem)
        shape["capacity"] = _estimate_capacity(shape["xfrm"],
                                               shape["font_info"])

    elif tag == "p:pic":
        shape["shape_type"] = "picture"
        shape["visual_data"] = True

    elif tag == "p:graphicFrame":
        # Check for chart vs table
        has_chart = len(elem.getElementsByTagName("c:chart")) > 0
        has_table = len(elem.getElementsByTagName("a:tbl")) > 0
        if has_chart:
            shape["shape_type"] = "chart"
            shape["visual_data"] = True
        elif has_table:
            shape["shape_type"] = "table"
            shape["visual_data"] = True
        else:
            shape["shape_type"] = "graphic"
            shape["visual_data"] = True

    elif tag == "p:grpSp":
        shape["shape_type"] = "group"
        # Recursively classify children
        for child_tag in ("p:sp", "p:pic", "p:graphicFrame"):
            for child in elem.getElementsByTagName(child_tag):
                # Only direct children of this group
                if child.parentNode == elem or (
                        child.parentNode and
                        child.parentNode.nodeName == "p:grpSp" and
                        child.parentNode == elem):
                    shape["children"].append(
                        _classify_shape(child, child_tag))

    return shape


def _extract_xfrm(elem) -> dict | None:
    """Extract position and size from a:xfrm within spPr or grpSpPr."""
    for pr_tag in ("p:spPr", "p:grpSpPr", "p:cNvPr"):
        for spPr in elem.getElementsByTagName(pr_tag):
            for xfrm in spPr.getElementsByTagName("a:xfrm"):
                result = {}
                for off in xfrm.getElementsByTagName("a:off"):
                    result["x_emu"] = int(off.getAttribute("x") or 0)
                    result["y_emu"] = int(off.getAttribute("y") or 0)
                for ext in xfrm.getElementsByTagName("a:ext"):
                    result["cx_emu"] = int(ext.getAttribute("cx") or 0)
                    result["cy_emu"] = int(ext.getAttribute("cy") or 0)

                if "x_emu" in result and "cx_emu" in result:
                    result["x_in"] = round(result["x_emu"] / EMU_PER_INCH, 2)
                    result["y_in"] = round(result["y_emu"] / EMU_PER_INCH, 2)
                    result["w_in"] = round(result["cx_emu"] / EMU_PER_INCH, 2)
                    result["h_in"] = round(result["cy_emu"] / EMU_PER_INCH, 2)
                    return result
    return None


def _extract_placeholder(sp) -> dict | None:
    """Extract placeholder info from a shape element."""
    for nvSpPr in sp.getElementsByTagName("p:nvSpPr"):
        for nvPr in nvSpPr.getElementsByTagName("p:nvPr"):
            for ph in nvPr.getElementsByTagName("p:ph"):
                return {
                    "type": ph.getAttribute("type") or "body",
                    "idx": ph.getAttribute("idx") or "",
                    "sz": ph.getAttribute("sz") or "",
                }
    return None


def _extract_font_info(sp) -> list[dict]:
    """Extract font specs from text runs in a shape."""
    fonts = []
    seen = set()

    for txBody in sp.getElementsByTagName("p:txBody"):
        for rPr in txBody.getElementsByTagName("a:rPr"):
            sz = rPr.getAttribute("sz")
            if not sz:
                continue
            size_pt = round(int(sz) / 100, 1)
            bold = rPr.getAttribute("b") == "1"
            italic = rPr.getAttribute("i") == "1"
            typeface = ""
            for latin in rPr.getElementsByTagName("a:latin"):
                typeface = latin.getAttribute("typeface") or ""
                break

            key = (size_pt, typeface, bold)
            if key not in seen:
                seen.add(key)
                fonts.append({
                    "size_pt": size_pt,
                    "typeface": typeface,
                    "bold": bold,
                    "italic": italic,
                })

    return fonts


def _extract_text_runs(sp) -> str:
    """Extract all text from a shape's text body."""
    parts = []
    for txBody in sp.getElementsByTagName("p:txBody"):
        for p in txBody.getElementsByTagName("a:p"):
            line_parts = []
            for r in p.getElementsByTagName("a:r"):
                for t in r.getElementsByTagName("a:t"):
                    if t.firstChild:
                        line_parts.append(t.firstChild.nodeValue)
            if line_parts:
                parts.append("".join(line_parts))
    return "\n".join(parts)


def _estimate_capacity(xfrm: dict | None,
                       font_info: list[dict]) -> dict | None:
    """Estimate text capacity given box dimensions and font size."""
    if not xfrm or not font_info:
        return None

    # Use the most common (first) font size
    font_pt = font_info[0]["size_pt"]
    if font_pt <= 0:
        return None

    width_pt = xfrm["cx_emu"] / EMU_PER_PT
    height_pt = xfrm["cy_emu"] / EMU_PER_PT

    chars_per_line = int(width_pt / (font_pt * CHAR_WIDTH_RATIO))
    max_lines = int(height_pt / (font_pt * LINE_HEIGHT_RATIO))
    total_chars = chars_per_line * max(max_lines, 1)

    return {
        "chars_per_line": chars_per_line,
        "max_lines": max_lines,
        "total_chars": total_chars,
        "font_pt": font_pt,
    }


def _summarize_background(bg) -> str:
    """Produce a short summary of a background element."""
    if bg.getElementsByTagName("a:solidFill"):
        for sf in bg.getElementsByTagName("a:solidFill"):
            for child in sf.childNodes:
                if child.nodeType == child.ELEMENT_NODE:
                    val = child.getAttribute('val') or child.getAttribute('lastClr')
                    return f"solid:{val}"
    if bg.getElementsByTagName("a:gradFill"):
        return "gradient"
    if bg.getElementsByTagName("a:blipFill"):
        return "image"
    return "other"


# ---------------------------------------------------------------------------
# Markdown writers
# ---------------------------------------------------------------------------

def _fmt_pos(xfrm: dict | None) -> str:
    """Format position as 'x, y in'."""
    if not xfrm:
        return "—"
    return f"{xfrm['x_in']}\", {xfrm['y_in']}\""


def _fmt_size(xfrm: dict | None) -> str:
    """Format size as 'w x h in'."""
    if not xfrm:
        return "—"
    return f"{xfrm['w_in']}\" x {xfrm['h_in']}\""


def _fmt_font(font_info: list[dict]) -> str:
    """Format font info as concise string."""
    if not font_info:
        return "—"
    f = font_info[0]
    parts = [f"{f['size_pt']}pt"]
    if f["typeface"]:
        parts.append(f["typeface"])
    if f["bold"]:
        parts.append("bold")
    return " ".join(parts)


def _fmt_capacity(cap: dict | None) -> str:
    """Format capacity as concise string."""
    if not cap:
        return "—"
    return f"~{cap['total_chars']} chars ({cap['chars_per_line']}/line x {cap['max_lines']} lines)"


def write_theme_md(output_dir: Path, themes: list[dict],
                   template_name: str):
    lines = [f"# Theme Analysis — {template_name}", ""]
    for theme in themes:
        lines.append(f"## {theme.get('name', 'Unnamed Theme')}")
        lines.append(f"- **File**: `{theme['file']}`")
        if theme.get("color_scheme_name"):
            lines.append(f"- **Color scheme**: {theme['color_scheme_name']}")
        if theme.get("font_scheme_name"):
            lines.append(f"- **Font scheme**: {theme['font_scheme_name']}")
        if theme.get("format_scheme"):
            lines.append(f"- **Format scheme**: {theme['format_scheme']}")
        lines.append("")

        if theme["colors"]:
            lines.append("### Colors")
            lines.append("| Role | Type | Value |")
            lines.append("|------|------|-------|")
            for role, info in theme["colors"].items():
                lines.append(f"| {role} | {info['type']} | `{info['value']}` |")
            lines.append("")

        if theme["fonts"]:
            lines.append("### Fonts")
            lines.append(f"- **Heading (major)**: {theme['fonts'].get('major', 'N/A')}")
            lines.append(f"- **Body (minor)**: {theme['fonts'].get('minor', 'N/A')}")
            lines.append("")

    (output_dir / "theme.md").write_text("\n".join(lines), encoding="utf-8")


def write_masters_md(output_dir: Path, masters: list[dict],
                     template_name: str):
    lines = [f"# Slide Masters — {template_name}", ""]
    for master in masters:
        lines.append(f"## {master['name']}")
        lines.append(f"- **File**: `{master['file']}`")
        if master["theme_file"]:
            lines.append(f"- **Theme**: `{master['theme_file']}`")
        if master["background"]:
            lines.append(f"- **Background**: {master['background']}")
        lines.append(f"- **Layouts**: {len(master['layout_files'])}")
        lines.append("")

        if master["placeholders"]:
            lines.append("### Placeholders")
            lines.append("| Type | Index | Position | Size |")
            lines.append("|------|-------|----------|------|")
            for sh in master["placeholders"]:
                ph = sh["placeholder"]
                lines.append(
                    f"| {ph['type']} | {ph['idx']} "
                    f"| {_fmt_pos(sh['xfrm'])} "
                    f"| {_fmt_size(sh['xfrm'])} |")
            lines.append("")

        if master["layout_files"]:
            lines.append("### Linked Layouts")
            for lf in sorted(master["layout_files"]):
                lines.append(f"- `{lf}`")
            lines.append("")

    (output_dir / "slide-masters.md").write_text(
        "\n".join(lines), encoding="utf-8")


def write_layouts_md(output_dir: Path, layouts: list[dict],
                     template_name: str):
    lines = [f"# Slide Layouts — {template_name}", ""]

    # Index table
    lines.append("## Layout Index")
    lines.append("| # | File | Name | Type | Placeholders | Other Shapes | Style |")
    lines.append("|---|------|------|------|--------------|--------------|-------|")
    for i, layout in enumerate(layouts, 1):
        name = layout["name"] or layout["type"] or "—"
        n_ph = len(layout["placeholders"])
        n_other = len(layout["non_placeholder_shapes"])
        style = "free-form" if n_other > n_ph else "placeholder-driven"
        lines.append(
            f"| {i} | `{layout['filename']}` | {name} "
            f"| {layout['type'] or '—'} | {n_ph} | {n_other} | {style} |")
    lines.append("")

    # Detail per layout
    for i, layout in enumerate(layouts, 1):
        name = layout["name"] or layout["type"] or layout["filename"]
        lines.append(f"## Layout {i}: {name}")
        lines.append(f"- **File**: `{layout['filename']}`")
        lines.append(f"- **Master**: {layout['master']}")
        if layout["type"]:
            lines.append(f"- **Type**: {layout['type']}")
        lines.append("")

        if layout["placeholders"]:
            lines.append("### Placeholders")
            lines.append("| Type | Index | Position | Size | Font | Capacity |")
            lines.append("|------|-------|----------|------|------|----------|")
            for sh in layout["placeholders"]:
                ph = sh["placeholder"]
                lines.append(
                    f"| {ph['type']} | {ph['idx']} "
                    f"| {_fmt_pos(sh['xfrm'])} "
                    f"| {_fmt_size(sh['xfrm'])} "
                    f"| {_fmt_font(sh['font_info'])} "
                    f"| {_fmt_capacity(sh['capacity'])} |")
            lines.append("")

        if layout["non_placeholder_shapes"]:
            lines.append("### Non-Placeholder Shapes")
            lines.append("| Name | Type | Position | Size |")
            lines.append("|------|------|----------|------|")
            for sh in layout["non_placeholder_shapes"]:
                lines.append(
                    f"| {sh['name']} | {sh['shape_type']} "
                    f"| {_fmt_pos(sh['xfrm'])} "
                    f"| {_fmt_size(sh['xfrm'])} |")
            lines.append("")

    (output_dir / "layouts.md").write_text("\n".join(lines), encoding="utf-8")


def write_slides_md(output_dir: Path, slides: list[dict],
                    template_name: str):
    lines = [f"# Example Slides — {template_name}", ""]

    # Index table
    lines.append("## Slide Index")
    lines.append("| # | File | Layout | Shapes | Visual Data |")
    lines.append("|---|------|--------|--------|-------------|")
    for slide in slides:
        n_vd = len(slide["visual_data_elements"])
        vd_label = f"{n_vd} element(s)" if n_vd else "—"
        lines.append(
            f"| {slide['number']} | `{slide['filename']}` "
            f"| {slide['layout'] or '—'} "
            f"| {len(slide['shapes'])} "
            f"| {vd_label} |")
    lines.append("")

    # Detail per slide
    for slide in slides:
        lines.append(f"## Slide {slide['number']}: `{slide['filename']}`")
        lines.append(f"- **Layout**: {slide['layout'] or 'unknown'} "
                     f"(`{slide['layout_file'] or '?'}`)")
        lines.append(f"- **Total shapes**: {len(slide['shapes'])}")
        if slide["visual_data_elements"]:
            lines.append(f"- **Visual data elements**: "
                         f"{len(slide['visual_data_elements'])} "
                         f"(images/charts that carry embedded data)")
        lines.append("")

        # Shape inventory
        if slide["shapes"]:
            lines.append("### Shape Inventory")
            lines.append("| Name | Type | Position | Size | Capacity |")
            lines.append("|------|------|----------|------|----------|")
            for sh in slide["shapes"]:
                vd_marker = " [VISUAL DATA]" if sh["visual_data"] else ""
                lines.append(
                    f"| {sh['name']}{vd_marker} | {sh['shape_type']} "
                    f"| {_fmt_pos(sh['xfrm'])} "
                    f"| {_fmt_size(sh['xfrm'])} "
                    f"| {_fmt_capacity(sh['capacity'])} |")
            lines.append("")

        # Text content
        if slide["text_content"]:
            lines.append("### Content")
            for tc in slide["text_content"]:
                ph = tc["placeholder"]
                label = f"[{ph['type']}]" if ph else tc["shape_name"]
                cap = tc["capacity"]
                cap_str = f" (capacity: ~{cap['total_chars']} chars)" if cap else ""
                font_str = f" | {_fmt_font(tc['font_info'])}" if tc["font_info"] else ""
                lines.append(f"**{label}**{font_str}{cap_str}")
                lines.append("```")
                lines.append(tc["text"])
                lines.append("```")
                lines.append("")

    (output_dir / "slides.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest(output_dir: Path, template_name: str, meta: dict,
                   themes: list[dict], masters: list[dict],
                   layouts: list[dict], slides: list[dict]):
    lines = [f"# Brand Manifest — {template_name}", ""]
    lines.append("Auto-generated by `analyze_template.py`. "
                 "Read this file first for slide planning.")
    lines.append("")

    # Run folder structure
    lines.append("## Run Folder Structure")
    lines.append("```")
    lines.append(f"{output_dir.name}/")
    lines.append(f"├── {template_name}        # Original template (source of truth)")
    lines.append("├── brand-manifest.md       # This file")
    lines.append("├── theme.md                # Colors, fonts")
    lines.append("├── layouts.md              # Layout inventory with dimensions")
    lines.append("├── slide-masters.md        # Master backgrounds")
    lines.append("├── slides.md               # Example slides with shape inventory")
    lines.append("└── output/                 # Place generated .pptx and .pdf here")
    lines.append("```")
    lines.append("")

    # Slide dimensions
    if meta.get("slide_size"):
        sz = meta["slide_size"]
        lines.append("## Slide Dimensions")
        lines.append(f"- **Size**: {sz['width_in']}\" x {sz['height_in']}\" "
                     f"({sz['width_emu']} x {sz['height_emu']} EMU)")
        lines.append("")

    # File index
    lines.append("## Files")
    lines.append("| File | Contents |")
    lines.append("|------|----------|")
    lines.append(f"| [theme.md](theme.md) | {len(themes)} theme(s) |")
    lines.append(f"| [slide-masters.md](slide-masters.md) "
                 f"| {len(masters)} master(s) |")
    lines.append(f"| [layouts.md](layouts.md) | {len(layouts)} layout(s) "
                 f"with shape dimensions |")
    lines.append(f"| [slides.md](slides.md) | {len(slides)} slide(s) "
                 f"with shape inventory |")
    lines.append("")

    # Colors
    if themes and themes[0]["colors"]:
        lines.append("## Brand Colors")
        lines.append("| Role | Value |")
        lines.append("|------|-------|")
        for role, info in themes[0]["colors"].items():
            lines.append(f"| {role} | `{info['value']}` |")
        lines.append("")

    # Fonts
    if themes and themes[0]["fonts"]:
        lines.append("## Brand Fonts")
        lines.append(f"- **Headings**: "
                     f"{themes[0]['fonts'].get('major', 'N/A')}")
        lines.append(f"- **Body**: "
                     f"{themes[0]['fonts'].get('minor', 'N/A')}")
        lines.append("")

    # Template style detection
    blank_slides = [s for s in slides
                    if s["layout"] and "blank" in s["layout"].lower()]
    if len(blank_slides) > len(slides) / 2:
        lines.append("## Template Style: Blank Layout + Custom Shapes")
        lines.append("")
        lines.append("Most example slides use BLANK layout with positioned "
                     "shapes (not standard placeholders). To create new slides:")
        lines.append("1. Duplicate the closest example slide")
        lines.append("2. Edit text within existing shapes (see Shape Inventory "
                     "in slides.md)")
        lines.append("3. Do NOT add new shapes or reposition existing ones")
        lines.append("4. Check text capacity before writing content")
        lines.append("")

    # Visual data warnings
    vd_slides = [s for s in slides if s["visual_data_elements"]]
    if vd_slides:
        lines.append("## Visual Data Warnings")
        lines.append("")
        lines.append("These slides contain images or charts with embedded "
                     "data values. Text replacement alone will NOT update "
                     "the visual — you must replace the image/chart or "
                     "flag for manual update.")
        lines.append("")
        for s in vd_slides:
            vd_names = [sh["name"] or sh["shape_type"]
                        for sh in s["visual_data_elements"]]
            lines.append(f"- **Slide {s['number']}** (`{s['filename']}`): "
                         f"{', '.join(vd_names)}")
        lines.append("")

    # Content capacity reference
    cap_entries = []
    for s in slides:
        for tc in s["text_content"]:
            if tc["capacity"] and tc["text"]:
                ph = tc["placeholder"]
                label = (f"[{ph['type']}]" if ph
                         else tc.get("shape_name", "text"))
                cap_entries.append({
                    "slide": s["number"],
                    "label": label,
                    "capacity": tc["capacity"],
                    "current_len": len(tc["text"]),
                })
    if cap_entries:
        lines.append("## Content Capacity Reference")
        lines.append("| Slide | Shape | Font | Capacity | Current |")
        lines.append("|-------|-------|------|----------|---------|")
        for e in cap_entries:
            cap = e["capacity"]
            lines.append(
                f"| {e['slide']} | {e['label']} "
                f"| {cap['font_pt']}pt "
                f"| ~{cap['total_chars']} chars "
                f"| {e['current_len']} chars |")
        lines.append("")

    # Layout selection guide
    lines.append("## Layout Selection Guide")
    lines.append("")
    for layout in layouts:
        name = layout["name"] or layout["type"] or layout["filename"]
        n_ph = len(layout["placeholders"])
        n_other = len(layout["non_placeholder_shapes"])
        ph_types = [sh["placeholder"]["type"]
                    for sh in layout["placeholders"]]
        style = "free-form" if n_other > n_ph else "placeholder-driven"
        desc = ", ".join(ph_types) if ph_types else "no placeholders"
        if n_other:
            desc += f" + {n_other} shapes"
        lines.append(f"- **{name}** (`{layout['filename']}`) "
                     f"[{style}]: {desc}")
    lines.append("")

    (output_dir / "brand-manifest.md").write_text(
        "\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
