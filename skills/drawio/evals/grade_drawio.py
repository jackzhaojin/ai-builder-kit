#!/usr/bin/env python3
"""Programmatic grader for the drawio skill.

Reads evals/evals.json and an output .drawio file, then checks each
assertion from the matching eval case against the file. Writes grading.json
in the skill-creator schema (expectations[].text/passed/evidence + summary).

Usage:
    python3 grade_drawio.py <eval_id_or_name> <path_to_output.drawio> [--output-dir <dir>]

Writes to <output_dir>/grading.json (defaults to alongside the .drawio file).
The grader also looks for a sibling .png (same basename) and smoke-tests its
size; if missing, the PNG assertions fail with clear evidence.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).parent
EVALS_JSON = HERE / "evals.json"

BRAND_PALETTE = {
    "#1e1e1e",  # user/default/black
    "#1971c2",  # deterministic/blue
    "#e03131",  # agentic/red
    "#f08c00",  # mix/orange
}

SEMANTIC_STROKES = {"#1e1e1e", "#1971c2", "#e03131", "#f08c00"}


def load_evals() -> dict:
    return json.loads(EVALS_JSON.read_text())


def find_eval(evals: dict, identifier: str) -> dict:
    for e in evals["evals"]:
        if str(e["id"]) == identifier or e["eval_name"] == identifier:
            return e
    raise SystemExit(f"No eval found matching '{identifier}'")


def parse_drawio(path: Path):
    """Return (ok, tree_or_None, cells_or_None, error_message).

    Cells: list of dicts with the usual fields plus `waypoints` (count of <mxPoint>
    entries inside <Array as="points">) for edges. A waypoint is an explicit bend
    the author hand-placed; more than 2 waypoints almost always means the edge is
    snaking around an obstacle that shouldn't be there.
    """
    try:
        tree = ET.parse(path)
    except ET.ParseError as e:
        return False, None, None, f"XML parse error: {e}"
    root = tree.getroot()
    model = root.find(".//mxGraphModel/root")
    if model is None:
        return False, tree, None, "No <mxGraphModel><root> found"
    cells = []
    for c in model.findall("mxCell"):
        geom = c.find("mxGeometry")
        w = h = x = y = None
        rel = None
        waypoints = 0
        if geom is not None:
            def f(attr):
                v = geom.get(attr)
                try:
                    return float(v) if v is not None else None
                except ValueError:
                    return None
            w, h, x, y = f("width"), f("height"), f("x"), f("y")
            rel = geom.get("relative")
            # Count <Array as="points"><mxPoint .../></Array> waypoints on edges.
            for arr in geom.findall("Array"):
                if arr.get("as") == "points":
                    waypoints = len(arr.findall("mxPoint"))
                    break
        cells.append({
            "id": c.get("id"),
            "style": c.get("style") or "",
            "value": c.get("value") or "",
            "parent": c.get("parent"),
            "source": c.get("source"),
            "target": c.get("target"),
            "vertex": c.get("vertex") == "1",
            "edge": c.get("edge") == "1",
            "connectable": c.get("connectable"),
            "has_geom": geom is not None,
            "geom_relative": rel,
            "w": w, "h": h, "x": x, "y": y,
            "waypoints": waypoints,
        })
    return True, tree, cells, None


def style_kv(style: str) -> dict:
    """Parse a draw.io style string into a dict. Values are strings; flags map to '1'."""
    d = {}
    if not style:
        return d
    for part in style.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            d[k.strip().lower()] = v.strip()
        else:
            d[part.strip().lower()] = "1"
    return d


def is_frame(cell: dict) -> bool:
    return cell["vertex"] and "swimlane" in cell["style"].lower()


def is_legend_swatch(cell: dict) -> bool:
    if not cell["vertex"] or is_frame(cell):
        return False
    w, h = cell["w"], cell["h"]
    if w is None or h is None:
        return False
    return 70 <= w <= 125 and 18 <= h <= 45


def is_content_box(cell: dict) -> bool:
    if not cell["vertex"] or is_frame(cell) or is_legend_swatch(cell):
        return False
    return (cell["w"] or 0) >= 80 and (cell["h"] or 0) >= 40


def normalize_hex(v: str) -> str:
    if not v:
        return ""
    v = v.strip().lower()
    if v.startswith("#"):
        return v
    return v


# ---------- assertion runners ----------

def check_xml_wellformed(cells, tree, err):
    if not tree:
        return False, f"XML parse failed: {err}"
    return True, "XML is well-formed and contains mxGraphModel/root"


def check_mxfile_skeleton(cells, tree, err):
    if tree is None:
        return False, "no tree"
    root = tree.getroot()
    if root.tag != "mxfile":
        return False, f"root tag is {root.tag!r}, expected mxfile"
    diag = root.find("diagram")
    if diag is None:
        return False, "missing <diagram>"
    model = diag.find("mxGraphModel")
    if model is None:
        return False, "missing <mxGraphModel>"
    mroot = model.find("root")
    if mroot is None:
        return False, "missing <root>"
    return True, "mxfile > diagram > mxGraphModel > root skeleton present"


def check_root_cells_0_1(cells):
    ids = {c["id"]: c for c in cells}
    if "0" not in ids:
        return False, "missing mxCell id='0'"
    c1 = ids.get("1")
    if c1 is None:
        return False, "missing mxCell id='1'"
    if c1["parent"] != "0":
        return False, f"mxCell id='1' has parent={c1['parent']!r}, expected '0'"
    return True, "cells 0 and 1 present with id=1 parent=0"


def check_vertex_geom(cells):
    offenders = [c["id"] for c in cells if c["vertex"] and not c["has_geom"]]
    if offenders:
        return False, f"{len(offenders)} vertex cells missing mxGeometry: {offenders[:5]}"
    return True, f"all {sum(1 for c in cells if c['vertex'])} vertex cells have mxGeometry"


def check_edge_geom(cells):
    offenders = []
    for c in cells:
        if not c["edge"]:
            continue
        if not c["has_geom"]:
            offenders.append((c["id"], "no geom"))
        elif c["geom_relative"] != "1":
            offenders.append((c["id"], f"relative={c['geom_relative']!r}"))
    if offenders:
        return False, f"{len(offenders)} edge-geom issues: {offenders[:5]}"
    return True, f"all {sum(1 for c in cells if c['edge'])} edges have <mxGeometry relative='1'/>"


def check_unique_ids(cells):
    ids = [c["id"] for c in cells]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    if dupes:
        return False, f"{len(dupes)} duplicate ids: {dupes[:5]}"
    return True, f"all {len(ids)} ids unique"


def check_edge_endpoints_exist(cells):
    ids = {c["id"] for c in cells}
    bad = []
    for c in cells:
        if not c["edge"]:
            continue
        if c["source"] and c["source"] not in ids:
            bad.append((c["id"], "source", c["source"]))
        if c["target"] and c["target"] not in ids:
            bad.append((c["id"], "target", c["target"]))
    if bad:
        return False, f"{len(bad)} edges with missing endpoint refs: {bad[:5]}"
    total = sum(1 for c in cells if c["edge"])
    return True, f"all {total} edges have valid source+target refs"


def check_frame_count(cells, expected):
    n = sum(1 for c in cells if is_frame(c))
    if n == expected:
        return True, f"exactly {expected} swimlane frame(s)"
    return False, f"expected {expected} swimlane frames, found {n}"


def check_min_content_boxes(cells, minimum):
    n = sum(1 for c in cells if is_content_box(c))
    if n >= minimum:
        return True, f"{n} content boxes (≥ {minimum})"
    return False, f"only {n} content boxes, need ≥ {minimum}"


def check_rounded_arcsize(cells):
    """All content boxes should have rounded=1 and arcSize=15."""
    offenders = []
    for c in cells:
        if not is_content_box(c):
            continue
        s = style_kv(c["style"])
        if s.get("rounded") != "1":
            offenders.append((c["id"], f"rounded={s.get('rounded')!r}"))
            continue
        if s.get("arcsize") and s.get("arcsize") != "15":
            offenders.append((c["id"], f"arcSize={s.get('arcsize')!r}"))
    if offenders:
        return False, f"{len(offenders)} content boxes without rounded=1 arcSize=15: {offenders[:5]}"
    total = sum(1 for c in cells if is_content_box(c))
    return True, f"all {total} content boxes use rounded=1 (arcSize=15 where set)"


def check_no_italic_boxes(cells):
    offenders = []
    for c in cells:
        if not is_content_box(c) and not is_legend_swatch(c) and not is_frame(c):
            continue
        s = style_kv(c["style"])
        fs = s.get("fontstyle")
        if fs and fs != "0":
            offenders.append((c["id"], f"fontStyle={fs!r}"))
    if offenders:
        return False, f"{len(offenders)} boxes/frames with non-zero fontStyle: {offenders[:5]}"
    return True, "all boxes have fontStyle=0 or omitted"


def check_stroke_font_match(cells):
    """Every box with a semantic strokeColor must have matching fontColor."""
    offenders = []
    checked = 0
    for c in cells:
        if not (is_content_box(c) or is_legend_swatch(c)):
            continue
        s = style_kv(c["style"])
        stroke = normalize_hex(s.get("strokecolor", ""))
        font = normalize_hex(s.get("fontcolor", ""))
        if stroke in SEMANTIC_STROKES:
            checked += 1
            if font != stroke:
                offenders.append((c["id"], f"stroke={stroke} font={font or 'missing'}"))
    if offenders:
        return False, f"{len(offenders)}/{checked} color-coded boxes with stroke≠font: {offenders[:5]}"
    return True, f"all {checked} color-coded boxes have stroke=font (or no semantic stroke)"


def check_full_palette(cells):
    used = set()
    for c in cells:
        if not (is_content_box(c) or is_legend_swatch(c)):
            continue
        s = style_kv(c["style"])
        stroke = normalize_hex(s.get("strokecolor", ""))
        if stroke in SEMANTIC_STROKES:
            used.add(stroke)
    missing = SEMANTIC_STROKES - used
    if missing:
        return False, f"palette missing: {sorted(missing)}; used: {sorted(used)}"
    return True, f"all 4 semantic colors present: {sorted(used)}"


def check_legend_swatches(cells, frame_required):
    """At least 4 legend swatches exist; optionally required to be inside a frame."""
    swatches = [c for c in cells if is_legend_swatch(c)]
    if len(swatches) < 4:
        return False, f"only {len(swatches)} legend-sized swatches found, need ≥ 4"
    colors = set()
    for c in swatches:
        s = style_kv(c["style"])
        stroke = normalize_hex(s.get("strokecolor", ""))
        if stroke in SEMANTIC_STROKES:
            colors.add(stroke)
    if len(colors) < 4:
        return False, f"swatches cover only {len(colors)} semantic colors: {sorted(colors)}"
    if frame_required:
        frame_ids = {c["id"] for c in cells if is_frame(c)}
        inside = [c for c in swatches if c["parent"] in frame_ids]
        if len(inside) < 4:
            return False, f"only {len(inside)}/{len(swatches)} swatches are inside a frame (expected 4)"
    return True, f"{len(swatches)} legend swatches covering {len(colors)} colors (frame-scope OK)"


def check_dashed_edge_present(cells, minimum=1):
    n = sum(1 for c in cells if c["edge"] and style_kv(c["style"]).get("dashed") == "1")
    if n >= minimum:
        return True, f"{n} dashed edges (≥ {minimum})"
    return False, f"only {n} dashed edges, need ≥ {minimum}"


def check_dashed_cells_present(cells, minimum=2):
    n = sum(1 for c in cells if (c["edge"] or c["vertex"]) and style_kv(c["style"]).get("dashed") == "1")
    if n >= minimum:
        return True, f"{n} dashed cells (boxes+edges, ≥ {minimum})"
    return False, f"only {n} dashed cells, need ≥ {minimum}"


def check_same_side_feedback(cells, minimum=1):
    """Find edges where exitX==entryX and (exitX==0 or exitX==1) — same-side loop."""
    hits = []
    for c in cells:
        if not c["edge"]:
            continue
        s = style_kv(c["style"])
        ex = s.get("exitx")
        en = s.get("entryx")
        if ex is None or en is None:
            continue
        if ex == en and ex in {"0", "1"}:
            hits.append(c["id"])
    if len(hits) >= minimum:
        return True, f"{len(hits)} same-side feedback edges: {hits[:5]}"
    return False, f"only {len(hits)} same-side feedback edges, need ≥ {minimum}"


def check_edge_labels(cells, minimum=2):
    """Edge-label cells: connectable='0', parent is an edge, style contains 'edgelabel'."""
    edge_ids = {c["id"] for c in cells if c["edge"]}
    hits = []
    for c in cells:
        if c["vertex"] and "edgelabel" in c["style"].lower() and c["parent"] in edge_ids and c["connectable"] == "0":
            hits.append(c["id"])
    if len(hits) >= minimum:
        return True, f"{len(hits)} edge-label cells correctly parented to edges"
    return False, f"only {len(hits)} valid edge-label cells, need ≥ {minimum}"


def check_orthogonal_edges(cells):
    missing = []
    for c in cells:
        if not c["edge"]:
            continue
        s = style_kv(c["style"])
        if (s.get("edgestyle") or "").lower() != "orthogonaledgestyle":
            missing.append(c["id"])
    if missing:
        return False, f"{len(missing)} edges missing edgeStyle=orthogonalEdgeStyle: {missing[:5]}"
    total = sum(1 for c in cells if c["edge"])
    return True, f"all {total} edges use orthogonalEdgeStyle"


def check_cross_frame_edges(cells, minimum=3):
    """Cross-frame edges: source.parent != target.parent AND edge.parent == '1'."""
    by_id = {c["id"]: c for c in cells}
    hits_top = []
    misplaced = []
    for c in cells:
        if not c["edge"] or not c["source"] or not c["target"]:
            continue
        src = by_id.get(c["source"])
        dst = by_id.get(c["target"])
        if not src or not dst:
            continue
        if src["parent"] != dst["parent"]:
            if c["parent"] == "1":
                hits_top.append(c["id"])
            else:
                misplaced.append((c["id"], f"parent={c['parent']}"))
    evidence = f"{len(hits_top)} cross-frame edges at parent='1'"
    if misplaced:
        evidence += f"; {len(misplaced)} misplaced (not at parent=1): {misplaced[:3]}"
    if len(hits_top) >= minimum and not misplaced:
        return True, evidence
    if len(hits_top) >= minimum and misplaced:
        return False, evidence + " — some cross-frame edges are not at parent='1' (will render broken)"
    return False, evidence + f"; need ≥ {minimum}"


def check_internal_edges(cells, minimum=2):
    """Internal edges: source.parent == target.parent == edge.parent (and not '1')."""
    by_id = {c["id"]: c for c in cells}
    hits = []
    for c in cells:
        if not c["edge"] or not c["source"] or not c["target"]:
            continue
        src = by_id.get(c["source"])
        dst = by_id.get(c["target"])
        if not src or not dst:
            continue
        if src["parent"] and src["parent"] == dst["parent"] == c["parent"] and src["parent"] != "1":
            hits.append(c["id"])
    if len(hits) >= minimum:
        return True, f"{len(hits)} internal edges with parent matching endpoints"
    return False, f"only {len(hits)} internal edges, need ≥ {minimum}"


def check_max_waypoints(cells, limit=3):
    """No edge should have more than `limit` explicit waypoints.

    SKILL.md says 'max 2 turns per edge' as the aspiration. This grader lets 3
    waypoints through because edges targeting a frame (rather than a specific
    box) legitimately need one extra bend to reach the frame boundary cleanly.
    4+ waypoints is a hard fail — that's a snake, not a routed edge.
    """
    offenders = [(c["id"], c["waypoints"]) for c in cells if c["edge"] and c["waypoints"] > limit]
    if offenders:
        worst = max(o[1] for o in offenders)
        return False, f"{len(offenders)} edges with >{limit} waypoints (worst: {worst}): {offenders[:5]}"
    n_edges = sum(1 for c in cells if c["edge"])
    return True, f"all {n_edges} edges have ≤{limit} waypoints — routing is layout-driven, not hand-waypointed"


def check_convergence_alignment(cells, min_arrows=3):
    """When 3+ edges share a target, all of them must enter from the same side.

    'Same side' means matching entryX (if both specified) OR matching entryY — i.e.,
    the edges hit the target from one of its four sides, not from all directions.
    Edges that don't set an explicit entry anchor are exempt (the router picks the
    closest side, and for well-placed sources that's usually consistent anyway).
    """
    targets = {}
    for c in cells:
        if not c["edge"] or not c["target"]:
            continue
        targets.setdefault(c["target"], []).append(c)

    bad_targets = []
    checked_targets = []
    for tid, edges in targets.items():
        if len(edges) < min_arrows:
            continue
        anchored = []
        for e in edges:
            s = style_kv(e["style"])
            ex, ey = s.get("entryx"), s.get("entryy")
            # Exempt same-side feedback loops (exitX == entryX or exitY == entryY on an extreme edge).
            # These are a legitimate exception — their "octopus" appearance is the feedback-loop shape, not a convergence failure.
            exx, exy = s.get("exitx"), s.get("exity")
            is_feedback = (ex is not None and exx is not None and ex == exx and ex in {"0", "1"}) or \
                          (ey is not None and exy is not None and ey == exy and ey in {"0", "1"})
            if is_feedback:
                continue
            if ex is not None or ey is not None:
                anchored.append((e["id"], ex, ey))
        if len(anchored) < min_arrows:
            # Not enough anchored edges to judge; rely on router.
            continue
        checked_targets.append(tid)
        x_values = {a[1] for a in anchored if a[1] is not None}
        y_values = {a[2] for a in anchored if a[2] is not None}
        # Same side if all anchored edges share one entryX (all on left or right)
        # OR all share one entryY (all on top or bottom).
        same_side = (len(x_values) == 1) or (len(y_values) == 1)
        if not same_side:
            bad_targets.append((tid, f"{len(anchored)} arrows, entryX values={sorted(x_values)}, entryY values={sorted(y_values)}"))

    if bad_targets:
        return False, f"{len(bad_targets)} convergence targets with octopus (arrows from different sides): {bad_targets[:3]}"
    if not checked_targets:
        return True, f"no convergence pattern with ≥{min_arrows} anchored arrows to evaluate (router-driven; visual check required)"
    return True, f"all {len(checked_targets)} convergence targets pass bus alignment (arrows enter from one side)"


def check_frame_nonoverlap(cells):
    """Frames must not overlap each other's bounding boxes (> 5px overlap counts)."""
    frames = [c for c in cells if is_frame(c) and all(v is not None for v in (c["x"], c["y"], c["w"], c["h"]))]
    overlaps = []
    for i in range(len(frames)):
        for j in range(i + 1, len(frames)):
            a, b = frames[i], frames[j]
            # Only frames with the same parent share a coordinate system.
            if a["parent"] != b["parent"]:
                continue
            ax2, ay2 = a["x"] + a["w"], a["y"] + a["h"]
            bx2, by2 = b["x"] + b["w"], b["y"] + b["h"]
            ox = min(ax2, bx2) - max(a["x"], b["x"])
            oy = min(ay2, by2) - max(a["y"], b["y"])
            if ox > 5 and oy > 5:
                overlaps.append((a["id"], b["id"], f"ox={ox:.0f} oy={oy:.0f}"))
    if overlaps:
        return False, f"{len(overlaps)} frame pairs overlap: {overlaps[:3]}"
    return True, f"all {len(frames)} frames have non-overlapping bounding boxes"


def check_png_exists(drawio_path: Path):
    png = drawio_path.with_suffix(".png")
    if not png.exists():
        return False, f"PNG not found at {png.name}"
    size = png.stat().st_size
    if size < 10_000:
        return False, f"PNG only {size} bytes (< 10 KB) — likely failed render"
    return True, f"PNG exists ({size} bytes)"


# ---------- dispatcher ----------

def match_assertion(text: str, ctx: dict):
    """Given an assertion text, pick a checker and call it. Returns (passed, evidence)."""
    t = text.lower()
    cells, tree, err, drawio_path = ctx["cells"], ctx["tree"], ctx["err"], ctx["path"]

    # File validity
    if "well-formed xml" in t or "mxfile > diagram" in t:
        if "mxfile > diagram" in t:
            return check_mxfile_skeleton(cells, tree, err)
        return check_xml_wellformed(cells, tree, err)
    if "mxcell id='0' and mxcell id='1'" in t or "both mxcell id='0' and mxcell id='1'" in t:
        return check_root_cells_0_1(cells)
    if "vertex cell has a child mxgeometry" in t or "every mxcell with vertex='1' has a child mxgeometry" in t or ("vertex cell has" in t and "child mxgeometry" in t):
        return check_vertex_geom(cells)
    if "edge cell has a child mxgeometry" in t or "every mxcell with edge='1'" in t or ("edge cell has" in t and "mxgeometry" in t):
        return check_edge_geom(cells)
    if "ids are unique" in t:
        return check_unique_ids(cells)
    if "source and target reference an existing" in t:
        return check_edge_endpoints_exist(cells)

    # Frame count
    if "exactly one swimlane frame" in t or "exactly 1 swimlane" in t:
        return check_frame_count(cells, 1)
    if "exactly 3 swimlane" in t:
        return check_frame_count(cells, 3)

    # Content box minimum
    m = re.search(r"at least (\d+) content box", t)
    if m:
        return check_min_content_boxes(cells, int(m.group(1)))

    # Rounded corners
    if "rounded=1 and arcsize=15" in t:
        return check_rounded_arcsize(cells)

    # Italic text
    if "fontstyle=0" in t and ("italic" in t or "no italic" in t):
        return check_no_italic_boxes(cells)

    # Stroke/font match
    if "matching fontcolor" in t or "stroke and font must agree" in t or "strokecolor = fontcolor" in t:
        return check_stroke_font_match(cells)

    # Full palette
    if "full palette" in t or "all 4 semantic colors" in t or "4 semantic colors" in t and "appear" in t:
        return check_full_palette(cells)

    # Legend swatches
    if "legend swatches" in t or "legend exists" in t:
        frame_required = "inside the frame" in t or "inside one of the frames" in t
        return check_legend_swatches(cells, frame_required)

    # Dashed
    if "at least one edge uses dashed" in t or "dashed=1" in t and "edge" in t and "retry" in t:
        return check_dashed_edge_present(cells, 1)
    if "dashed=1 in their style" in t or ("cells have dashed=1" in t):
        return check_dashed_cells_present(cells, 2)

    # Same-side feedback
    if "same-side exit/entry" in t or "exitx=entryx" in t or "same-side" in t:
        return check_same_side_feedback(cells, 1)

    # Edge labels
    if "edge-label cells" in t or ("edgelabel" in t and "connectable" in t):
        return check_edge_labels(cells, 2)

    # Orthogonal
    if "orthogonaledgestyle" in t:
        return check_orthogonal_edges(cells)

    # Max waypoints per edge (≤2 turns → ≤2 waypoints)
    if "waypoint" in t or ("max" in t and "turns" in t) or "≤ 3" in t or "<= 3 waypoints" in t:
        return check_max_waypoints(cells, 3)

    # Convergence alignment (bus vs octopus)
    if "convergence" in t or ("same side" in t and "entry" in t) or "bus pattern" in t or "octopus" in t:
        return check_convergence_alignment(cells, 3)

    # Frame non-overlap
    if "non-overlap" in t or ("frames" in t and "overlap" in t):
        return check_frame_nonoverlap(cells)

    # Cross-frame edges
    if "cross-frame edges" in t and ("at least 3" in t or "≥ 3" in t):
        return check_cross_frame_edges(cells, 3)

    # Internal edges
    if "internal edges" in t:
        return check_internal_edges(cells, 2)

    # PNG
    if "png export file exists" in t or "png" in t and ">10" in t:
        return check_png_exists(drawio_path)

    return None, f"no checker matched for: {text[:80]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("eval_id_or_name")
    ap.add_argument("drawio_path")
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    drawio = Path(args.drawio_path).resolve()
    evals = load_evals()
    case = find_eval(evals, args.eval_id_or_name)
    outdir = Path(args.output_dir).resolve() if args.output_dir else drawio.parent

    if not drawio.exists():
        grading = {
            "eval_id": case["id"],
            "eval_name": case["eval_name"],
            "expectations": [{"text": t, "passed": False, "evidence": "output .drawio not found"} for t in case["expectations"]],
            "summary": {"passed": 0, "failed": len(case["expectations"]), "total": len(case["expectations"]), "pass_rate": 0.0},
        }
    else:
        ok, tree, cells, err = parse_drawio(drawio)
        ctx = {"tree": tree, "cells": cells or [], "err": err, "path": drawio}
        results = []
        for text in case["expectations"]:
            try:
                if cells is None:
                    passed, evidence = False, f"could not parse drawio: {err}"
                else:
                    passed, evidence = match_assertion(text, ctx)
                    if passed is None:
                        # No matcher -> score as failed with diagnostic evidence so the eval isn't silently green
                        passed, evidence = False, evidence
            except Exception as e:
                passed, evidence = False, f"grader exception: {type(e).__name__}: {e}"
            results.append({"text": text, "passed": bool(passed), "evidence": evidence})

        passed_ct = sum(1 for r in results if r["passed"])
        total = len(results)
        grading = {
            "eval_id": case["id"],
            "eval_name": case["eval_name"],
            "expectations": results,
            "summary": {
                "passed": passed_ct,
                "failed": total - passed_ct,
                "total": total,
                "pass_rate": passed_ct / total if total else 0.0,
            },
        }

    outdir.mkdir(parents=True, exist_ok=True)
    out_file = outdir / "grading.json"
    out_file.write_text(json.dumps(grading, indent=2))
    print(f"wrote {out_file}")
    print(f"  pass_rate: {grading['summary']['pass_rate']:.1%} ({grading['summary']['passed']}/{grading['summary']['total']})")


if __name__ == "__main__":
    main()
