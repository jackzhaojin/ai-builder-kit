# ffmpeg notes and gotchas for the slides+audio render

## The xfade chain (what build_video.py generates)

One looped PNG input per cue (`-loop 1 -framerate FPS -t DUR -i slide.png`), each normalized with
`scale=W:H:force_original_aspect_ratio=decrease,pad=W:H:...,format=yuv420p,fps=FPS,setsar=1,setpts=PTS-STARTPTS`,
then chained: `[s0][s1]xfade=transition=fade:duration=F:offset=T1[x1]; [x1][s2]xfade=...:offset=T2[x2]; ...`
and finally `fade=t=in:st=0:d=0.8,fade=t=out:st=TOTAL-1.2:d=1.2`.

Duration math: with cut k starting at T_k and fade F, input k needs `(T_{k+1} - T_k) + F` seconds (first
input `T_1 + F`, last input `TOTAL - T_last`). The chained stream is `T_{k+1} + F` long after k transitions,
so every offset is just `T_k` in output time and the final length equals the audio length exactly.

The audio is mapped straight from the source file (`-map N:a -c:a copy` when it is already AAC). Video
starts at t=0 and the audio start_time is 0, so sync is structural; the validator still checks both.

## Encoding settings

`libx264 -crf 18 -preset medium -pix_fmt yuv420p -profile:v high -level 4.1 -r 30 -movflags +faststart`.
Stills compress extremely well: about 80 MB for 18 minutes at 1080p. Encode runs ~5x realtime on Apple
Silicon. `-shortest` guards against a trailing audio frame making the container longer than the video.

## Gotchas

1. **Seeking to the very end fails.** The video stream ends about one frame before the audio (33367 frames =
   1112.233 s vs audio 1112.259 s). Seek to `duration - 0.25` at most when grabbing a tail frame.
2. **mlx_whisper output naming.** Output files are named from the input basename up to the FIRST dot, so
   `cut_89.3.wav` produces `cut_89.txt`. Name windows with integers (`cut_089300.wav`).
3. **`moov atom not found` while encoding is not an error.** With faststart the index is written last; wait
   for ffmpeg to exit before probing the file.
4. **Non-AAC sources.** WAV/MP3/FLAC narration is encoded to AAC 192k; the validator then compares with a
   tolerance instead of demanding bit-identical samples. `<out>.build.json` records which path was taken.
5. **Decks that are not 16:9.** `pdftoppm -scale-to-x W -scale-to-y H` keeps the aspect ratio and the build's
   pad step letterboxes on black. If the deck is 4:3, consider rendering at 1440x1080 and setting width/height
   in the timeline to 1920x1080 so the pad happens in the build (crisper than scaling twice).
6. **Long filtergraphs.** Always go through `-filter_complex_script <file>`; 17+ inputs on the command line
   is fine but the graph itself is easier to read and audit as a file.
7. **Non-Apple-Silicon transcription.** Replace the mlx_whisper call in `prep.sh` with
   `uvx --from openai-whisper whisper audio-16k.wav --model turbo --word_timestamps True --output_format json`.
   The JSON shape (`segments[].words[]`) is the same.
8. **macOS has no `timeout`.** Run long encodes in the background and wait on an `EXIT=` marker in a log.
