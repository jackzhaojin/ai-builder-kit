#!/usr/bin/env bash
# Re-transcribe short windows around slide cuts, straight from the rendered MP4's audio, and print them.
# Confirms two things at once: the muxed audio is in sync, and each cut really sits on its anchor line.
#
# Usage: bash check_anchors.sh <out.mp4> <slide-timeline.json> [max-cuts] [half-window-s]
#   max-cuts     : how many cuts to sample, spread evenly (default 5; 0 = all)
#   half-window  : seconds either side of the cut (default 2.5)
# Output: <mp4-dir>/anchor-check/cut_<ms>.txt, and the text printed. The anchor line should appear in the
# SECOND half of each window (the slide changes as that sentence starts).
set -euo pipefail
MP4="${1:?usage: check_anchors.sh <out.mp4> <slide-timeline.json> [max-cuts] [half-window-s]}"
TL="${2:?usage: check_anchors.sh <out.mp4> <slide-timeline.json> [max-cuts] [half-window-s]}"
MAX="${3:-5}"; HALF="${4:-2.5}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="$(dirname "$MP4")/anchor-check"; mkdir -p "$OUT"

python3 - "$TL" "$MAX" "$HERE" <<'PY' > "$OUT/_cuts.tsv"
import sys
sys.path.insert(0, sys.argv[3])
from _common import load_timeline
tl = load_timeline(sys.argv[1]); mx = int(sys.argv[2])
cuts = [c for c in tl["cues"] if c["start"] > 0]
if mx and len(cuts) > mx:
    step = len(cuts) / mx
    cuts = [cuts[int(i * step)] for i in range(mx)]
for c in cuts:
    print(f"{c['start']:.3f}\t{c.get('anchor', '')}")
PY

while IFS=$'\t' read -r t anchor; do
  ms=$(python3 -c "print(int(round($t*1000)))")
  wav="$OUT/cut_${ms}.wav"     # integer-ms name: mlx_whisper truncates output names at the first dot
  ss=$(python3 -c "print(max(0.0, $t-$HALF))"); dur=$(python3 -c "print(2*$HALF)")
  ffmpeg -nostdin -loglevel error -y -ss "$ss" -i "$MP4" -t "$dur" -vn -ac 1 -ar 16000 "$wav"
  uvx --from mlx-whisper mlx_whisper "$wav" --model mlx-community/whisper-small-mlx --language en \
    --output-format txt --verbose False --output-dir "$OUT" >/dev/null 2>&1
  echo "== cut @ ${t}s  (window ${HALF}s either side; expected anchor: ${anchor:-n/a}) =="
  cat "$OUT/cut_${ms}.txt"; echo
  rm -f "$wav"
done < "$OUT/_cuts.tsv"
rm -f "$OUT/_cuts.tsv"
