#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow", "numpy"]
# ///
"""Validate a rendered slides+audio MP4 against its cue sheet. Exit 1 on any failure.

Usage: uv run validate_video.py slide-timeline.json out.mp4

Checks, and why each exists:
 1. container: expected size, h264 yuv420p, fps, aac; duration == audio duration (+-0.1 s); both streams
    start at 0. (YouTube re-encodes anything, but a wrong fps or pix_fmt shows up as stutter or green frames.)
 2. every cue: the frame 0.4 s after the crossfade completes matches the cued slide, and the frame 0.3 s
    before the cut still matches the previous slide. Match = nearest slide PNG by mean-abs-diff on a
    160x90 grayscale thumbnail; the winner must be clearly ahead of the runner-up. This catches off-by-one
    cues, a wrong PNG path, and xfade offset math errors in one pass.
 3. fade-out: luma at -1.4 s / -0.8 s / -0.25 s must ramp down (the fade ends at the audio end, so the very
    last frame is near-black but not zero; do not seek past the last video frame, which ends ~1 frame early).
 4. audio: decoded PCM of the MP4 track vs the source. Stream-copied audio must be sample-identical;
    re-encoded audio must match in length (+-50 ms) and be close (mean abs error small).
 5. writes <out>.cue-check.png: one frame per cue, for a human to eyeball.
Pillow and numpy come from the inline metadata above: uv installs them into a cached environment, never next
to the skill.
"""
import io, json, os, subprocess, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import load_timeline, media_duration, ffprobe_json
from PIL import Image, ImageDraw
import numpy as np

tl_path, mp4 = sys.argv[1], sys.argv[2]
tl = load_timeline(tl_path)
fade, fps, W, H = float(tl["fade"]), int(tl["fps"]), int(tl["width"]), int(tl["height"])
audio = tl["_audio"]
build = {}
bp = os.path.splitext(mp4)[0] + ".build.json"
if os.path.exists(bp):
    build = json.load(open(bp))
fails = []

p = ffprobe_json(mp4, "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,start_time,sample_rate,channels")
vdur = float(p["format"]["duration"]); adur = media_duration(audio)
v = [s for s in p["streams"] if s["codec_type"] == "video"][0]
au = [s for s in p["streams"] if s["codec_type"] == "audio"][0]
print(f"[container] {v['codec_name']} {v['width']}x{v['height']} {v['pix_fmt']} {v['r_frame_rate']} | "
      f"audio {au['codec_name']} {au['sample_rate']}Hz ch={au['channels']} | dur {vdur:.3f}s vs source {adur:.3f}s")
if not (v["codec_name"] == "h264" and v["width"] == W and v["height"] == H and v["pix_fmt"] == "yuv420p" and v["r_frame_rate"] == f"{fps}/1"):
    fails.append("video stream params differ from timeline (size/fps/pix_fmt/codec)")
if au["codec_name"] != "aac": fails.append("audio not aac")
if abs(vdur - adur) > 0.1: fails.append(f"duration mismatch {vdur:.3f} vs {adur:.3f}")
if abs(float(v.get("start_time", 0))) > 0.02 or abs(float(au.get("start_time", 0))) > 0.05:
    fails.append(f"non-zero start_time v={v.get('start_time')} a={au.get('start_time')}")

def fp(img):
    return np.asarray(img.convert("L").resize((160, 90), Image.BILINEAR), dtype=np.float32)

slide_files = sorted({c["_slide"] for c in tl["cues"]} | set(glob.glob(os.path.join(os.path.dirname(tl["cues"][0]["_slide"]), "*.png"))))
slides = {f: fp(Image.open(f)) for f in slide_files}

def frame_at(t):
    png = subprocess.check_output(["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", mp4,
                                   "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"])
    if not png: raise RuntimeError(f"no frame at {t:.3f}s")
    return Image.open(io.BytesIO(png)).convert("RGB")

def nearest(img):
    f = fp(img)
    d = sorted(((float(np.abs(f - s).mean()), n) for n, s in slides.items()))
    return d[0], (d[1] if len(d) > 1 else (1e9, None))

def clear(d0, d1):
    return d1 > d0 * 2.0 or d0 < 2.0

cues = tl["cues"]; sheet = []
print("[cues]")
for i, c in enumerate(cues):
    want = c["_slide"]
    img = frame_at(c["start"] + fade + 0.4); (d0, n0), (d1, n1) = nearest(img)
    ok = n0 == want and clear(d0, d1)
    print(f"  cue {i:2d} @{c['start']:8.2f}s  want {os.path.basename(want)}  got {os.path.basename(n0)} "
          f"(d={d0:.1f}, runner-up {os.path.basename(n1) if n1 else '-'} d={d1:.1f})  {'OK' if ok else 'FAIL'}")
    if not ok: fails.append(f"cue {i}: wrong slide after cut")
    sheet.append((f"cue {i} @{c['start']:.1f}s -> {os.path.basename(want)}", img))
    if i > 0:
        prev = cues[i - 1]["_slide"]
        imb = frame_at(c["start"] - 0.3); (d0b, n0b), (d1b, _) = nearest(imb)
        okb = n0b == prev and clear(d0b, d1b)
        print(f"        pre-cut @{c['start'] - 0.3:8.2f}s  want {os.path.basename(prev)}  got {os.path.basename(n0b)} (d={d0b:.1f})  {'OK' if okb else 'FAIL'}")
        if not okb: fails.append(f"cue {i}: previous slide not on screen before cut")

lum = [float(np.asarray(frame_at(vdur - dt).convert("L")).mean()) for dt in (1.4, 0.8, 0.25)]
ramp_ok = lum[0] > lum[1] > lum[2] and lum[2] < 0.25 * lum[0]
print(f"[tail] mean luma at -1.4s/-0.8s/-0.25s = {lum[0]:.1f}/{lum[1]:.1f}/{lum[2]:.1f} (fade-out ramp) {'OK' if ramp_ok else 'FAIL'}")
if not ramp_ok: fails.append("no fade-out ramp at tail")

def pcm(path):
    raw = subprocess.check_output(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path, "-vn", "-f", "s16le", "-ac", "2", "-ar", "44100", "-"])
    return np.frombuffer(raw, dtype=np.int16)
x, y = pcm(mp4), pcm(audio); n = min(len(x), len(y))
diff = np.abs(x[:n].astype(np.int32) - y[:n].astype(np.int32))
copied = build.get("audio_copied", au["codec_name"] == "aac")
print(f"[audio] samples mp4={len(x)} src={len(y)} (delta {len(x) - len(y)})  max|diff|={diff.max()}  mean|diff|={diff.mean():.3f}  ({'stream copy' if copied else 're-encoded'})")
if abs(len(x) - len(y)) > 44100 * 0.05 * 2: fails.append("audio length differs from source by >50ms")
if copied and diff.max() > 64: fails.append("stream-copied audio differs from source")
if not copied and diff.mean() > 200: fails.append("re-encoded audio differs too much from source")

cw, ch = 480, 270; cols = 4; rows = (len(sheet) + cols - 1) // cols
img = Image.new("RGB", (cols * (cw + 8) + 8, rows * (ch + 28) + 8), "#222"); d = ImageDraw.Draw(img)
for i, (label, fr) in enumerate(sheet):
    x0 = 8 + (i % cols) * (cw + 8); y0 = 8 + (i // cols) * (ch + 28)
    img.paste(fr.resize((cw, ch)), (x0, y0 + 20)); d.text((x0, y0 + 4), label, fill="white")
out = os.path.splitext(mp4)[0] + ".cue-check.png"; img.save(out); print("[sheet]", out)

if fails:
    print("FAILURES:"); [print("  -", f) for f in fails]; sys.exit(1)
print("ALL CHECKS PASSED")
