#!/usr/bin/env python3
"""YouTube chapter list from the cue sheet. Usage: python3 make_chapters.py slide-timeline.json

A cue starts a chapter when it carries a "chapter" key (the title). Cues without one (e.g. the
individual slides of a recap montage) stay inside the previous chapter. The chapter time is the moment
the slide is fully on screen (start + fade). YouTube rules: first chapter at 00:00, at least three
chapters, each at least 10 s long; violations are printed as warnings on stderr, not fixed silently.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_timeline, fmt_time

tl = load_timeline(sys.argv[1] if len(sys.argv) > 1 else "slide-timeline.json")
rows = []
for c in tl["cues"]:
    if c.get("chapter"):
        t = 0.0 if c["start"] == 0 else c["start"] + float(tl["fade"])
        rows.append((t, c["chapter"]))
if not rows or rows[0][0] != 0:
    print("warning: first chapter must be at 00:00 (give the first cue a 'chapter')", file=sys.stderr)
if len(rows) < 3:
    print("warning: YouTube needs at least 3 chapters", file=sys.stderr)
for (a, ta), (b, tb) in zip(rows, rows[1:]):
    if b - a < 10:
        print(f"warning: chapter '{tb}' starts {b - a:.1f}s after '{ta}' (YouTube minimum is 10s)", file=sys.stderr)
for t, title in rows:
    print(f"{fmt_time(t, 0)} {title}")
