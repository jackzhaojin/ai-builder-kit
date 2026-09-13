#!/usr/bin/env bash
# Mechanical prep for a slides+audio video: render the deck to slide PNGs, dump the deck text,
# extract 16 kHz mono audio, transcribe with word timestamps, write a readable transcript.
#
# Usage: bash prep.sh <audio> <deck.pdf|deck.pptx> <workdir> [whisper-model]
#   audio   : m4a / mp3 / wav / mp4 ... anything ffmpeg reads (NotebookLM exports are .m4a)
#   deck    : PDF preferred. PPTX/KEY-exported-PPTX is converted to PDF with LibreOffice if installed.
#   workdir : created if missing. Everything lands here. Should be gitignored (media is big).
#   model   : default mlx-community/whisper-large-v3-turbo (best timestamps for clean podcast audio).
#             Use mlx-community/whisper-small-mlx for a quick pass. Non-Apple-Silicon: see references/ffmpeg-notes.md.
# Env: SLIDE_W / SLIDE_H override the 1920x1080 render size.
#
# Outputs in <workdir>: slides/slide-NN.png, deck-text.txt, audio-16k.wav, audio-16k.json, transcript.md
set -euo pipefail

AUDIO="${1:?usage: prep.sh <audio> <deck.pdf|pptx> <workdir> [model]}"
DECK="${2:?usage: prep.sh <audio> <deck.pdf|pptx> <workdir> [model]}"
WORKDIR="${3:?usage: prep.sh <audio> <deck.pdf|pptx> <workdir> [model]}"
MODEL="${4:-mlx-community/whisper-large-v3-turbo}"
W="${SLIDE_W:-1920}"; H="${SLIDE_H:-1080}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for tool in ffmpeg ffprobe pdftoppm pdftotext uvx; do
  command -v "$tool" >/dev/null || { echo "missing tool: $tool (brew install ffmpeg poppler uv)"; exit 1; }
done
mkdir -p "$WORKDIR/slides"

# 1. deck -> PDF if needed
case "${DECK##*.}" in
  pdf|PDF) PDF="$DECK" ;;
  pptx|PPTX|odp|key)
    command -v soffice >/dev/null || { echo "need LibreOffice (soffice) to convert $DECK to PDF"; exit 1; }
    echo "[deck] converting $(basename "$DECK") to PDF with LibreOffice"
    soffice --headless --convert-to pdf --outdir "$WORKDIR" "$DECK" >/dev/null
    PDF="$WORKDIR/$(basename "${DECK%.*}").pdf" ;;
  *) echo "unsupported deck format: $DECK"; exit 1 ;;
esac

# 2. slides -> PNG at the video size (pdftoppm keeps aspect; 16:9 decks fill the frame exactly)
echo "[deck] rendering $(pdfinfo "$PDF" | awk '/^Pages:/{print $2}') pages to ${W}x${H} PNGs"
rm -f "$WORKDIR"/slides/slide-*.png
pdftoppm -png -r 144 -scale-to-x "$W" -scale-to-y "$H" "$PDF" "$WORKDIR/slides/slide"
pdftotext -layout "$PDF" "$WORKDIR/deck-text.txt"

# 3. audio -> 16 kHz mono wav
echo "[audio] $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUDIO")s -> audio-16k.wav"
ffmpeg -nostdin -loglevel error -y -i "$AUDIO" -vn -ac 1 -ar 16000 "$WORKDIR/audio-16k.wav"

# 4. transcribe with word timestamps (model cached after first run)
echo "[audio] transcribing with $MODEL (word timestamps) ..."
uvx --from mlx-whisper mlx_whisper "$WORKDIR/audio-16k.wav" \
  --model "$MODEL" --language en --word-timestamps True \
  --output-format json --verbose False --output-dir "$WORKDIR" > "$WORKDIR/transcribe.log" 2>&1
python3 "$HERE/transcript_dump.py" "$WORKDIR/audio-16k.json" > "$WORKDIR/transcript.md"

echo "done."
echo "  slides:     $(ls "$WORKDIR"/slides/slide-*.png | wc -l | tr -d ' ') PNGs in $WORKDIR/slides/"
echo "  deck text:  $WORKDIR/deck-text.txt"
echo "  transcript: $WORKDIR/transcript.md ($(grep -c '^\[' "$WORKDIR/transcript.md") segments)"
echo "next: read deck-text.txt + transcript.md, write slide-timeline.json (see assets/slide-timeline.example.json)"
