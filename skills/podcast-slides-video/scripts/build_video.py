#!/usr/bin/env python3
"""Render a slides+audio MP4 from a cue sheet (slide-timeline.json).

Usage: python3 build_video.py slide-timeline.json -o out.mp4 [--dry-run] [--crf 18] [--preset medium]

Timeline keys: audio (path, relative to the json), fade (crossfade s, default 0.6), fps (30),
width/height (1920x1080), fade_in (0.8 s from black), fade_out (1.2 s to black),
cues: [{"slide": "slides/slide-01.png", "start": 0 | "m:ss.s", "anchor": "...", "note": "...", "chapter": "..."}]
  start = output time at which the crossfade INTO that slide begins. First cue must start at 0.
  Slides are shown until the next cue's start. Reusing a slide in several cues is fine.

Why an xfade chain and not the concat demuxer: xfade gives real crossfades between stills, and its
offset math lets the cue sheet speak in absolute output time. With transition k starting at T_k and
fade f: input durations d_0 = T_1 + f, d_k = (T_{k+1} - T_k) + f, d_last = total - T_last; the chain
length after k transitions is T_{k+1} + f, so every xfade offset is simply T_k and the final length is
exactly the audio length. The audio is stream-copied when it is already AAC (no generation loss);
anything else is encoded to AAC 192k. A sidecar <out>.build.json records what happened for the validator.
"""
import argparse, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_timeline, media_duration, ffprobe_json

ap = argparse.ArgumentParser()
ap.add_argument("timeline")
ap.add_argument("-o", "--output", required=True)
ap.add_argument("--dry-run", action="store_true", help="print durations + ffmpeg command, do not encode")
ap.add_argument("--crf", type=int, default=18)
ap.add_argument("--preset", default="medium")
args = ap.parse_args()

tl = load_timeline(args.timeline)
cues, fade, fps, W, H = tl["cues"], float(tl["fade"]), int(tl["fps"]), int(tl["width"]), int(tl["height"])
assert cues and cues[0]["start"] < 1e-6, "first cue must start at 0"
for a, b in zip(cues, cues[1:]):
    assert b["start"] - a["start"] > fade + 0.5, f"cues too close for a {fade}s crossfade: {a['start']} -> {b['start']}"
for c in cues:
    assert os.path.exists(c["_slide"]), f"missing slide: {c['_slide']}"

total = float(tl["total"]) if "total" in tl else media_duration(tl["_audio"])
T = [c["start"] for c in cues]; n = len(cues)
assert T[-1] < total - 1.0, "last cue starts after the audio ends"
durs = [(T[1] + fade) if (k == 0 and n > 1) else (total if n == 1 else ((T[k + 1] - T[k]) + fade if k < n - 1 else total - T[k]))
        for k in range(n)]

acodec = [s for s in ffprobe_json(tl["_audio"], "stream=codec_type,codec_name")["streams"] if s["codec_type"] == "audio"][0]["codec_name"]
audio_copy = acodec == "aac"

inputs = []
for c, d in zip(cues, durs):
    inputs += ["-loop", "1", "-framerate", str(fps), "-t", f"{d:.3f}", "-i", c["_slide"]]
inputs += ["-i", tl["_audio"]]

parts = [f"[{k}:v]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
         f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p,fps={fps},setsar=1,setpts=PTS-STARTPTS[s{k}]"
         for k in range(n)]
prev = "s0"
for k in range(1, n):
    out = f"x{k}"
    parts.append(f"[{prev}][s{k}]xfade=transition=fade:duration={fade}:offset={T[k]:.3f}[{out}]")
    prev = out
fi, fo = float(tl["fade_in"]), float(tl["fade_out"])
parts.append(f"[{prev}]fade=t=in:st=0:d={fi},fade=t=out:st={total - fo:.3f}:d={fo}[v]")
graph = ";\n".join(parts)

stem = os.path.splitext(args.output)[0]
os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
open(stem + ".filtergraph.txt", "w").write(graph + "\n")

cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"] + inputs + [
    "-filter_complex_script", stem + ".filtergraph.txt", "-map", "[v]", "-map", f"{n}:a",
    "-c:v", "libx264", "-crf", str(args.crf), "-preset", args.preset, "-pix_fmt", "yuv420p",
    "-r", str(fps), "-profile:v", "high", "-level", "4.1"]
cmd += ["-c:a", "copy"] if audio_copy else ["-c:a", "aac", "-b:a", "192k"]
cmd += ["-movflags", "+faststart", "-shortest", args.output]

print(f"audio {total:.3f}s ({acodec}, {'stream copy' if audio_copy else 'encode to aac'})  cues {n}  fade {fade}s  {W}x{H}@{fps}")
for c, d in zip(cues, durs):
    print(f"  {c['start']:8.2f}s  {os.path.basename(c['slide'])}  input {d:7.2f}s  {c.get('note', '')}")
if args.dry_run:
    print(" ".join(cmd)); sys.exit(0)
subprocess.check_call(cmd)
json.dump({"audio_copied": audio_copy, "audio_codec": acodec, "total": total, "cues": n,
           "width": W, "height": H, "fps": fps, "fade": fade, "fade_in": fi, "fade_out": fo},
          open(stem + ".build.json", "w"), indent=2)
print("wrote", args.output)
