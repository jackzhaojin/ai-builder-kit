"""Shared helpers for the podcast-slides-video scripts (kept tiny so each script stays readable)."""
import json, os, subprocess


def parse_time(v):
    """Accept seconds (number) or 'm:ss', 'mm:ss.s', 'h:mm:ss' strings. Returns float seconds."""
    if isinstance(v, (int, float)):
        return float(v)
    parts = [float(p) for p in str(v).strip().split(":")]
    secs = 0.0
    for p in parts:
        secs = secs * 60 + p
    return secs


def fmt_time(s, decimals=1):
    m = int(s // 60)
    sec = s - m * 60
    return f"{m:02d}:{sec:0{3 + decimals}.{decimals}f}" if decimals else f"{m:02d}:{int(sec):02d}"


def load_timeline(path):
    tl = json.load(open(path))
    here = os.path.dirname(os.path.abspath(path))

    def resolve(p):
        return p if os.path.isabs(p) else os.path.normpath(os.path.join(here, p))

    tl["_dir"] = here
    tl["_audio"] = resolve(tl["audio"])
    tl.setdefault("fade", 0.6)
    tl.setdefault("fps", 30)
    tl.setdefault("width", 1920)
    tl.setdefault("height", 1080)
    tl.setdefault("fade_in", 0.8)
    tl.setdefault("fade_out", 1.2)
    for c in tl["cues"]:
        c["start"] = parse_time(c["start"])
        c["_slide"] = resolve(c["slide"])
    tl["cues"].sort(key=lambda c: c["start"])
    return tl


def ffprobe_json(path, entries):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "json", path])
    return json.loads(out.decode())


def media_duration(path):
    return float(ffprobe_json(path, "format=duration")["format"]["duration"])
