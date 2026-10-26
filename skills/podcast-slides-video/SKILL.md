---
name: podcast-slides-video
description: >-
  Build a YouTube-ready MP4 from narrated audio plus a slide deck: a NotebookLM audio overview or
  podcast about a talk, a recorded voice track, a narrated walkthrough, matched to the deck's slides
  (PDF or PPTX) with slide changes cut to the transcript. Use this whenever the user has an audio
  file and slides and wants a video out of them, even if they never say "video": "put my slides to
  this audio", "turn the NotebookLM podcast into something I can upload", "sync the deck to the
  narration", "make a YouTube version of my talk from the deck and this recording", "the audio kind
  of maps to the slides". Produces the MP4, a cue sheet that is the auditable edit decision list, a
  validation pass with a contact sheet, and a YouTube chapter list. Not for editing existing video
  footage (use video-trim for that) and not for generating narration.
---

# Podcast + slides -> YouTube video

Turn "audio that talks about a deck" into a video where the right slide is on screen while it is
being talked about. The only judgment step is placing the cuts; everything else is a bundled script.
Working files go in a gitignored folder next to the source material (the user's convention is
`local-only/` or `trim-work/`; ask only if the project has neither and nothing obvious fits).

## Requirements

`ffmpeg`, `ffprobe`, `pdftoppm`, `pdftotext` (Homebrew ffmpeg + poppler), `uvx` (from uv) for MLX
Whisper on demand, Python 3 (the validator's Pillow and numpy come from its inline metadata via `uv run`).
LibreOffice `soffice` only if the deck arrives as PPTX. Apple Silicon assumed for whisper; see
references/ffmpeg-notes.md item 7 otherwise.

## Workflow

### 1. Probe and set up (1 min)

Confirm the audio duration and the deck page count, and that the deck is the version the audio was
made from (a NotebookLM overview generated from draft N does not always match deck N+1; say so if the
transcript talks about slides that no longer exist). Pick the workdir and make sure it is gitignored.

### 2. Mechanical prep (2 to 4 min, mostly whisper)

```bash
bash scripts/prep.sh "<audio>" "<deck.pdf|pptx>" "<workdir>"
```
Renders `slides/slide-NN.png` at 1920x1080, dumps `deck-text.txt`, extracts 16 kHz mono audio, transcribes
with whisper large-v3-turbo (word timestamps), writes `transcript.md` (one timestamped segment per line).
Run it in the background and do step 3's deck reading while it transcribes.

### 3. Cut the cue sheet (the judgment step)

Read `deck-text.txt` (and look at the slide PNGs, at least a contact sheet), then read `transcript.md` end
to end. Write `<workdir>/slide-timeline.json`: one cue per slide change, each with `start` (when the
crossfade into the slide begins), `anchor` (the transcript line it is timed to), `note` (why), and
`chapter` on cues that should start a YouTube chapter. Start from `assets/slide-timeline.example.json`.

Read `references/cutting-guide.md` before writing the cues. The short version: cut on the sentence that
introduces the next slide's idea, about 0.3 s before it; hold the title card through the cold open; going
back to an earlier slide is fine when the audio does; cut the closing recap as a montage of 8 to 18 s
per slide; nothing under 5 s; no invented visuals for stretches that have no slide.

### 4. Render (about 1/5 of the audio length)

```bash
python3 scripts/build_video.py <workdir>/slide-timeline.json -o <workdir>/<name>.mp4 --dry-run   # check the math
python3 scripts/build_video.py <workdir>/slide-timeline.json -o <workdir>/<name>.mp4             # background it
```
Name the output after the deck plus a date stamp (the user's convention: `<topic>-v<yyyy-mm-dd>-vN`).
The script writes the filtergraph and a `.build.json` sidecar next to the MP4 for audit. Source audio is
stream-copied when it is AAC, so there is no generation loss.

### 5. Validate (2 min) - do not skip, do not hand-wave

```bash
uv run scripts/validate_video.py <workdir>/slide-timeline.json <workdir>/<name>.mp4
bash scripts/check_anchors.sh <workdir>/<name>.mp4 <workdir>/slide-timeline.json 5
```
The validator must end with `ALL CHECKS PASSED`: container params, the correct slide on screen after and
before every cut, the fade-out ramp, and audio identical to the source. Open the `.cue-check.png` contact
sheet it writes and actually look at it. `check_anchors.sh` re-transcribes five windows from the finished
MP4; each anchor sentence should appear in the second half of its window. If a cut is off, fix the cue
sheet and re-render; do not patch the video.

### 6. Chapters and hand-off

```bash
python3 scripts/make_chapters.py <workdir>/slide-timeline.json > <workdir>/youtube-chapters.txt
```
Send the MP4 and the contact sheet to the user. Write a short README in the workdir (inputs, outputs, how
to re-render) so the folder explains itself later, and append an entry to the project's memory/log file if
it keeps one. Do not upload anywhere. Mention anything in the audio a careful colleague would flag (a
quote attributed to the deck that is only in the talk track, a number the user's guardrails care about),
without changing the audio: it is the user's pick.

## Bundled scripts

- `scripts/prep.sh` - deck to PNGs + text, audio to 16 kHz wav, whisper transcript, readable transcript.
- `scripts/transcript_dump.py` - whisper JSON to `[mm:ss.s - mm:ss.s] text` lines.
- `scripts/build_video.py` - cue sheet to MP4 via an xfade chain; `--dry-run` prints durations + command.
- `scripts/validate_video.py` - every check above + contact sheet; exit 1 on failure.
- `scripts/check_anchors.sh` - re-transcribe windows around cuts from the MP4.
- `scripts/make_chapters.py` - YouTube chapter list from cues carrying `chapter`.
- `assets/slide-timeline.example.json` - cue sheet template with every field.
- `references/cutting-guide.md` - how to place cuts; read before step 3.
- `references/ffmpeg-notes.md` - the xfade math, encoder settings, gotchas (tail seek, whisper naming, non-AAC sources, 4:3 decks).
