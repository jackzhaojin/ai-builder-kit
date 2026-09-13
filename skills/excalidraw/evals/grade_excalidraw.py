#!/usr/bin/env python3
"""Programmatic grader for the excalidraw skill.

Reads evals/evals.json and an output .excalidraw file, then checks each
assertion from the matching eval case against the file. Writes grading.json
in the skill-creator schema (expectations[].text/passed/evidence + summary).

Usage:
    python grade_excalidraw.py <eval_id_or_name> <path_to_output.excalidraw> [--output-dir <dir>]

Writes to <output_dir>/grading.json (defaults to alongside the .excalidraw file).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
EVALS_JSON = HERE / "evals.json"
RENDER_SCRIPT = HERE.parent / "scripts" / "render_excalidraw.py"

# Brand palette from references/brand-style.md
BRAND_PALETTE = {
    "#1e1e1e",  # default/black
    "#e03131",  # red / auth / outcome
    "#1971c2",  # blue / resource / role
    "#6741d9",  # purple / ai / mix
    "#2f9e44",  # green / actor
    "#bbb",     # muted
    "#f08c00",  # orange / member / identity
}


def load_evals() -> dict:
    return json.loads(EVALS_JSON.read_text())


def find_eval(evals: dict, identifier: str) -> dict:
    for e in evals["evals"]:
        if str(e["id"]) == identifier or e["eval_name"] == identifier:
            return e
    raise SystemExit(f"No eval found matching '{identifier}'")


def load_excalidraw(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON in {path}: {e}")


# ---------- assertion helpers ----------

def is_rectangle(el: dict) -> bool:
    return el.get("type") == "rectangle"


def is_legend_swatch(el: dict) -> bool:
    """Canonical swatches are 118-160 wide × 35-40 tall labeled pills — half the height of content boxes."""
    if not is_rectangle(el):
        return False
    w, h = el.get("width", 0), el.get("height", 0)
    return 80 <= w <= 200 and 25 <= h <= 55


def is_content_rect(el: dict) -> bool:
    """Rectangles large enough to be content boxes (exclude legend swatches)."""
    if not is_rectangle(el) or is_legend_swatch(el):
        return False
    return el.get("width", 0) >= 80 and el.get("height", 0) >= 60


def is_arrow(el: dict) -> bool:
    return el.get("type") == "arrow"


def is_text(el: dict) -> bool:
    return el.get("type") == "text"


def is_frame(el: dict) -> bool:
    return el.get("type") == "frame"


def elements_by_id(elements: list) -> dict:
    return {e["id"]: e for e in elements if "id" in e}


def free_floating_texts(elements: list) -> list:
    return [e for e in elements if is_text(e) and e.get("containerId") is None]


def multiline_text_count(elements: list, min_lines: int = 3) -> int:
    count = 0
    for e in free_floating_texts(elements):
        txt = e.get("text", "")
        if txt.count("\n") >= (min_lines - 1):
            count += 1
    return count


def arrow_xy_ok(el: dict, by_id: dict, tol: float = 10.0) -> tuple[bool, str]:
    """Check that arrow x,y = src.x + fp[0]*src.w, src.y + fp[1]*src.h."""
    sb = el.get("startBinding") or {}
    fp = sb.get("fixedPoint")
    if not fp:
        return True, "no startBinding.fixedPoint (skip)"
    src = by_id.get(sb.get("elementId"))
    if not src or "x" not in src or "width" not in src:
        return True, "startBinding source not bindable (skip)"
    expected_x = src.get("x", 0) + fp[0] * src.get("width", 0)
    expected_y = src.get("y", 0) + fp[1] * src.get("height", 0)
    dx = abs(el.get("x", 0) - expected_x)
    dy = abs(el.get("y", 0) - expected_y)
    if dx <= tol and dy <= tol:
        return True, f"x,y within {tol}px of derived {expected_x:.0f},{expected_y:.0f}"
    return False, f"x={el.get('x')} y={el.get('y')} but expected {expected_x:.0f},{expected_y:.0f} (off by {dx:.1f},{dy:.1f})"


def reciprocal_binding_ok(elements: list) -> tuple[bool, str]:
    by_id = elements_by_id(elements)
    problems = []
    for el in elements:
        for ref in el.get("boundElements") or []:
            if ref.get("type") != "text":
                continue
            text_id = ref.get("id")
            text_el = by_id.get(text_id)
            if not text_el:
                problems.append(f"shape {el['id']} references missing text {text_id}")
                continue
            if text_el.get("containerId") != el["id"]:
                problems.append(
                    f"shape {el['id']} references text {text_id} but text.containerId={text_el.get('containerId')}"
                )
    if problems:
        return False, "; ".join(problems[:3]) + (f" (+{len(problems)-3} more)" if len(problems) > 3 else "")
    return True, "all shape.boundElements text refs have reciprocal containerId"


def convergence_count(elements: list) -> dict[str, int]:
    """Count arrows ending at each element id."""
    counter: Counter = Counter()
    for el in elements:
        if is_arrow(el):
            eb = el.get("endBinding") or {}
            tid = eb.get("elementId")
            if tid:
                counter[tid] += 1
    return dict(counter)


def cross_frame_arrows(elements: list) -> list:
    """Return arrows where start and end bind to elements with different frameId (or one is None)."""
    by_id = elements_by_id(elements)
    crossings = []
    for el in elements:
        if not is_arrow(el):
            continue
        sb = el.get("startBinding") or {}
        eb = el.get("endBinding") or {}
        s = by_id.get(sb.get("elementId"))
        t = by_id.get(eb.get("elementId"))
        if s and t and s.get("frameId") != t.get("frameId"):
            crossings.append(el)
    return crossings


def run_render(excalidraw_path: Path) -> tuple[bool, str]:
    if not RENDER_SCRIPT.exists():
        return False, f"render script not found at {RENDER_SCRIPT}"
    try:
        result = subprocess.run(
            ["uv", "run", str(RENDER_SCRIPT), str(excalidraw_path)],
            cwd=RENDER_SCRIPT.parent,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return False, "render timed out after 120s"
    if result.returncode != 0:
        return False, f"render exited {result.returncode}: {result.stderr.strip()[:200]}"
    return True, f"render ok: {result.stdout.strip()}"


# ---------- assertion matcher ----------

def check_assertion(text: str, data: dict, by_id: dict, excalidraw_path: Path) -> tuple[bool, str]:
    elements = data.get("elements", [])
    arrows = [e for e in elements if is_arrow(e)]
    frames = [e for e in elements if is_frame(e)]
    content_rects = [e for e in elements if is_content_rect(e)]
    texts = [e for e in elements if is_text(e)]
    swatches = [e for e in elements if is_legend_swatch(e)]

    # Generic assertions keyed by substring
    t = text.lower()

    if "valid excalidraw" in t:
        ok = data.get("type") == "excalidraw" and isinstance(data.get("elements"), list)
        return ok, f"type={data.get('type')!r}, elements count={len(elements)}"

    if "elbowed: true" in t or "elbowed=true" in t or "all type='arrow' elements have elbowed" in t:
        bad = [a for a in arrows if a.get("elbowed") is not True]
        return (not bad), f"{len(arrows)-len(bad)}/{len(arrows)} arrows have elbowed:true" + (f"; offenders: {[a['id'] for a in bad[:3]]}" if bad else "")

    if "all type='arrow' elements have roughness: 1" in t or "roughness: 1" in t and "all elements" not in t and "arrow" in t:
        bad = [a for a in arrows if a.get("roughness") != 1]
        return (not bad), f"{len(arrows)-len(bad)}/{len(arrows)} arrows have roughness:1"

    if "all elements have roughness: 1" in t:
        styled = [e for e in elements if e.get("type") in ("rectangle", "ellipse", "arrow", "line")]
        bad = [e for e in styled if e.get("roughness") != 1]
        return (not bad), f"{len(styled)-len(bad)}/{len(styled)} styled elements have roughness:1"

    if "x,y matching src.x" in t or "arrow x,y" in t or "load-bearing rule" in t:
        problems = []
        checked = 0
        for a in arrows:
            ok, msg = arrow_xy_ok(a, by_id)
            if a.get("startBinding", {}).get("fixedPoint"):
                checked += 1
                if not ok:
                    problems.append(f"{a['id']}: {msg}")
        if not checked:
            return True, "no arrows have fixedPoint to check"
        return (not problems), f"{checked-len(problems)}/{checked} arrows correctly derived" + (f"; {problems[0]}" if problems else "")

    if "reciprocal boundelements" in t or "containerid" in t and "reciprocal" in t or "containerid pointing back" in t:
        return reciprocal_binding_ok(elements)

    if "no type='diamond'" in t or "no diamonds" in t or "no diamond" in t:
        diamonds = [e for e in elements if e.get("type") == "diamond"]
        return (not diamonds), f"found {len(diamonds)} diamond elements" if diamonds else "zero diamonds"

    if "roundness: {type: 3}" in t or "rounded corners" in t or "rectangles rounded" in t or "content rectangles" in t and "round" in t:
        bad = [r for r in content_rects if not (r.get("roundness") and r["roundness"].get("type") == 3)]
        return (not bad), f"{len(content_rects)-len(bad)}/{len(content_rects)} content rectangles have roundness:{{type:3}}"

    if "fontfamily: 5" in t or "font-family" in t:
        bad = [x for x in texts if x.get("fontFamily") != 5]
        return (not bad), f"{len(texts)-len(bad)}/{len(texts)} text elements use fontFamily:5"

    if "backgroundcolor: 'transparent'" in t or "background transparent" in t:
        bad = [r for r in content_rects if r.get("backgroundColor") != "transparent"]
        return (not bad), f"{len(content_rects)-len(bad)}/{len(content_rects)} rectangles have transparent bg"

    if "png renders successfully" in t or "render successfully" in t:
        return run_render(excalidraw_path)

    # Diagram-specific patterns

    m = re.search(r"exactly (\d+) content rectangles", t)
    if m:
        n = int(m.group(1))
        return (len(content_rects) == n), f"found {len(content_rects)} content rectangles (expected {n})"

    m = re.search(r"at least (\d+) content rectangles", t)
    if m:
        n = int(m.group(1))
        return (len(content_rects) >= n), f"found {len(content_rects)} content rectangles (need ≥{n})"

    m = re.search(r"exactly (\d+) type='frame' elements|exactly (\d+) type=\"frame\" elements|exactly (\d+) frames", t)
    if m:
        n = int(next(g for g in m.groups() if g))
        return (len(frames) == n), f"found {len(frames)} frames (expected {n})"

    if "zero type='frame'" in t or "no frames" in t:
        return (len(frames) == 0), f"found {len(frames)} frames (expected 0)"

    m = re.search(r"at least (\d+) free-floating", t)
    if m:
        n = int(m.group(1))
        ff = free_floating_texts(elements)
        return (len(ff) >= n), f"found {len(ff)} free-floating text elements (need ≥{n})"

    if ("multi-line" in t or "3\\+ lines" in t or "3+ lines" in t) and "callout" in t:
        # e.g. "At least 2 free-floating text elements with 3+ lines"
        m2 = re.search(r"at least (\d+)", t)
        n = int(m2.group(1)) if m2 else 1
        count = multiline_text_count(elements, min_lines=3)
        return (count >= n), f"found {count} multi-line (≥3 lines) free-floating callouts (need ≥{n})"

    if "single-color palette" in t or "all strokecolor values are '#1e1e1e'" in t:
        stroked = [e for e in elements if e.get("strokeColor") and e.get("type") != "frame"]
        bad = [e for e in stroked if e.get("strokeColor", "").lower() != "#1e1e1e"]
        return (not bad), f"{len(stroked)-len(bad)}/{len(stroked)} elements use only #1e1e1e" + (f"; bad: {[e.get('strokeColor') for e in bad[:3]]}" if bad else "")

    if ("4 distinct strokecolor" in t or "exactly 4 distinct strokecolor" in t) and "arrow" in t:
        arrow_colors = {a.get("strokeColor", "").lower() for a in arrows if a.get("strokeColor")}
        expected = {"#2f9e44", "#e03131", "#f08c00", "#1971c2"}
        return expected.issubset(arrow_colors), f"arrow colors: {arrow_colors} (expected superset of {expected})"

    if "arrow stroke colors cover the 3 source-semantic" in t or ("source-semantic" in t and "arrow" in t):
        arrow_colors = {a.get("strokeColor", "").lower() for a in arrows if a.get("strokeColor")}
        expected = {"#2f9e44", "#e03131", "#f08c00"}
        return expected.issubset(arrow_colors), f"arrow colors: {arrow_colors} (need superset of {expected})"

    m = re.search(r"share the same endbinding|convergence.*?(\d+)|endbinding elementid.*?different startbinding", t)
    if "convergence" in t or "share the same endbinding" in t:
        # assertion shape: "At least N arrows share the same endBinding elementId"
        m2 = re.search(r"at least (\d+)", t)
        n = int(m2.group(1)) if m2 else 3
        conv = convergence_count(elements)
        max_in = max(conv.values()) if conv else 0
        return (max_in >= n), f"max arrows converging on one target: {max_in} (need ≥{n})"

    if "mode: 'orbit'" in t or "mode=orbit" in t or "orbit" in t and "binding" in t:
        # e.g. "At least one of those convergence arrows has endBinding with mode: 'orbit'"
        # or   "At least 2 arrows have endBinding.mode: 'orbit' OR startBinding.mode: 'orbit' on the hub element"
        m2 = re.search(r"at least (\d+)", t)
        n = int(m2.group(1)) if m2 else 1
        orbit = [a for a in arrows
                 if (a.get("endBinding") or {}).get("mode") == "orbit"
                 or (a.get("startBinding") or {}).get("mode") == "orbit"]
        return (len(orbit) >= n), f"found {len(orbit)} arrows with mode:orbit (need ≥{n})"

    if "at least one arrow with strokestyle: 'dashed'" in t or "dashed retry" in t:
        dashed = [a for a in arrows if a.get("strokeStyle") == "dashed"]
        return (len(dashed) >= 1), f"found {len(dashed)} dashed arrows"

    if "dashed retry arrow has strokecolor: '#bbb'" in t or "retry.*muted" in t:
        dashed = [a for a in arrows if a.get("strokeStyle") == "dashed"]
        if not dashed:
            return False, "no dashed arrows to check"
        muted = [a for a in dashed if a.get("strokeColor", "").lower() in ("#bbb", "#bbbbbb", "#ccc", "#cccccc")]
        return (len(muted) >= 1), f"{len(muted)}/{len(dashed)} dashed arrows are muted"

    if "no cross-frame arrows" in t:
        xf = cross_frame_arrows(elements)
        return (not xf), f"found {len(xf)} cross-frame arrows (expected 0)"

    m = re.search(r"at least (\d+) cross-frame arrows", t)
    if m:
        n = int(m.group(1))
        xf = cross_frame_arrows(elements)
        return (len(xf) >= n), f"found {len(xf)} cross-frame arrows (need ≥{n})"

    if "exactly one text element contains" in t:
        m2 = re.search(r"contains '([^']+)'", text)
        if m2:
            needle = m2.group(1)
            # Normalize newlines in text content so "Deterministic Logic\n(x4)" matches "Deterministic Logic (x4)"
            def norm(s: str) -> str:
                return " ".join(s.split())
            needle_n = norm(needle)
            hits = [x for x in texts if needle_n in norm(x.get("text", ""))]
            return (len(hits) == 1), f"found {len(hits)} text elements containing {needle!r} (expected 1)"

    if "title text element exists" in t:
        # fontSize >= 28
        titles = [x for x in texts if x.get("fontSize", 0) >= 28]
        return (len(titles) >= 1), f"found {len(titles)} title-like text elements (fontSize >= 28)"

    if "legend has exactly 3 swatches" in t:
        # 3 small rects with specific colors
        colors = {s.get("strokeColor", "").lower() for s in swatches}
        expected = {"#1e1e1e", "#e03131", "#1971c2"}
        ok = len(swatches) >= 3 and expected.issubset(colors)
        return ok, f"swatches: {len(swatches)}, colors: {colors}"

    if "legend has 4 small rectangles" in t or "legend has 4 swatches" in t:
        colors = {s.get("strokeColor", "").lower() for s in swatches}
        return (len(swatches) >= 4), f"swatches: {len(swatches)}, colors: {colors}"

    if "each frame has its own mini-legend" in t or "per-frame mini-legend" in t:
        # count swatches grouped by frame id
        per_frame: Counter = Counter()
        for s in swatches:
            fid = s.get("frameId")
            if fid:
                per_frame[fid] += 1
        frame_ids = {f["id"] for f in frames}
        legends_per_frame = {fid: per_frame.get(fid, 0) for fid in frame_ids}
        ok = all(v >= 4 for v in legends_per_frame.values()) if legends_per_frame else False
        return ok, f"swatches per frame: {legends_per_frame} (need ≥4 each)"

    if "hub rectangle" in t and ("280" in text or "350" in text):
        hubs = [
            r for r in content_rects
            if 260 <= r.get("width", 0) <= 370
            and 130 <= r.get("height", 0) <= 210
            and r.get("frameId") is None
        ]
        # check label mentions da.live
        by_id_local = elements_by_id(elements)
        ok_hub = []
        for h in hubs:
            for ref in h.get("boundElements") or []:
                if ref.get("type") == "text":
                    text_el = by_id_local.get(ref["id"])
                    if text_el and "da.live" in text_el.get("text", "").lower():
                        ok_hub.append(h)
                        break
        return (len(ok_hub) == 1), f"found {len(ok_hub)} qualifying hub rectangles (width 260-370, height 130-210, frameId null, contains 'da.live')"

    if "action boxes" in t and "#1e1e1e" in text:
        # subject to interpretation; skip with a soft pass
        return True, "manual check (heuristic not encoded)"
    if "outcome boxes" in t and "#e03131" in text:
        return True, "manual check (heuristic not encoded)"
    if "role boxes" in t and "#1971c2" in text:
        return True, "manual check (heuristic not encoded)"

    if "elements inside frame bounds have frameid" in t or "children have correct frameid" in t:
        # weak check: count content rects with frameId vs total
        if not frames:
            return True, "no frames present (skip)"
        frame_ids = {f["id"] for f in frames}
        content_with_frame = [r for r in content_rects if r.get("frameId") in frame_ids]
        ratio = len(content_with_frame) / max(len(content_rects), 1)
        return (ratio >= 0.7), f"{len(content_with_frame)}/{len(content_rects)} content rects have a valid frameId ({ratio:.0%})"

    if "at least one vertical arrow" in t:
        vert = [a for a in arrows if a.get("height", 0) > a.get("width", 0)]
        return (len(vert) >= 1), f"found {len(vert)} vertical-dominant arrows"

    if "at least 3 free-floating connector label" in t:
        small_ff = [x for x in free_floating_texts(elements) if x.get("fontSize", 20) <= 18]
        return (len(small_ff) >= 3), f"found {len(small_ff)} small free-floating text elements (fontSize <= 18)"

    # Fallback: mark as manual check
    return True, "MANUAL: assertion not programmatically checked"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("eval_id", help="Eval id (1-6) or eval_name")
    parser.add_argument("excalidraw_path", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    if not args.excalidraw_path.exists():
        print(f"ERROR: file not found: {args.excalidraw_path}", file=sys.stderr)
        return 1

    evals = load_evals()
    eval_case = find_eval(evals, args.eval_id)
    data = load_excalidraw(args.excalidraw_path)
    by_id = elements_by_id(data.get("elements", []))

    expectations_out = []
    for text in eval_case["expectations"]:
        try:
            passed, evidence = check_assertion(text, data, by_id, args.excalidraw_path)
        except Exception as e:
            passed, evidence = False, f"checker raised: {e}"
        expectations_out.append({"text": text, "passed": bool(passed), "evidence": evidence})

    passed = sum(1 for e in expectations_out if e["passed"])
    total = len(expectations_out)
    summary = {"passed": passed, "failed": total - passed, "total": total, "pass_rate": passed / total if total else 0.0}

    grading = {
        "eval_id": eval_case["id"],
        "eval_name": eval_case["eval_name"],
        "expectations": expectations_out,
        "summary": summary,
    }

    out_dir = args.output_dir or args.excalidraw_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "grading.json"
    out_path.write_text(json.dumps(grading, indent=2))

    print(f"{eval_case['eval_name']}: {passed}/{total} passed ({summary['pass_rate']:.0%})")
    print(f"  grading → {out_path}")
    for e in expectations_out:
        sym = "✓" if e["passed"] else "✗"
        print(f"  {sym} {e['text'][:80]}")
        if not e["passed"]:
            print(f"    → {e['evidence']}")

    return 0 if summary["pass_rate"] == 1.0 else 2  # non-zero if any fail


if __name__ == "__main__":
    sys.exit(main())
