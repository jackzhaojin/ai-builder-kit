# Cutting guide: turning a transcript into a cue sheet

The whole edit is one JSON file of cues. Each cue says "at output time T, crossfade into slide X, because the
speaker says Y." Getting the cues right is the only judgment step in the pipeline, so this file is about how
to make those calls well. Everything else is scripts.

## Read both documents fully first

1. `deck-text.txt` (from `pdftotext -layout`) tells you what each slide is about, in page order. Pair it with
   the slide PNGs when the text dump is ambiguous (charts, photo slides). Write yourself a one-line label per
   slide before reading the transcript: "slide 4 = Exhibit A radar chart", "slide 6 = Jobs quote".
2. `transcript.md`, end to end. Do not skim: the transitions you want are single sentences.

## Where a cut goes

Put the cut on the sentence that INTRODUCES the next slide's idea, not on the sentence that finishes the
previous one. Podcast hosts and narrators signal slide changes with phrases like "he includes this chart",
"the next thing he lays out", "then there's the job ad", "let's talk about the customer". Start the crossfade
about 0.3 s before that sentence begins so the new headline is fully on screen as the key word is spoken
("He was speaking in Columbus" with COLUMBUS already visible). With a 0.6 s fade, `start = anchor_time - 0.3`.

Record the anchor in the cue (`"anchor": "04:35.8 'Jin includes this radar chart'"`). It makes the cue sheet
auditable, and `check_anchors.sh` re-transcribes those windows from the finished MP4 so you can verify it.

## Structure patterns you will see

- **Body in deck order.** A NotebookLM audio overview of a talk usually walks the deck in order for its main
  body. Expect one cue per slide, 45 s to 2.5 min each.
- **Cold open before the source is named.** Hosts often open with a hook (an anecdote, a stat) before saying
  "we're looking at a presentation by ...". Hold the title card through the cold open; the viewer needs to see
  what they clicked on. 60 to 90 s on the title is fine.
- **Returning to an earlier slide.** If the audio spends a long stretch on a point whose best visual is an
  earlier slide (they cite that slide's footnote, or its headline is exactly the topic), cut back to it. The
  video serves the audio, not the deck's page order. Say why in the cue's `note`.
- **Two slides that share three points** (an overview card and a detail card): show the overview while the
  points are named, switch to the detail card when the audio starts listing the sub-items the detail card shows.
- **Recap / synthesis at the end.** Hosts summarize in 60 to 90 s, touching each idea for one sentence. Cut this
  as a short montage: the slide for each sentence being recapped, 8 to 18 s each. Below about 5 s a slide with
  crossfades on both sides reads as a flicker, so merge two recap sentences onto the better of their two slides
  rather than going shorter. Only the first montage cue gets a `chapter`.
- **A closing question or discussion with no slide.** Pick the slide whose card is the subject (a puzzle about
  accountability sits on the slide with the ACCOUNTABILITY card), then move to the thank-you slide for the
  outro line ("for everyone listening ...").
- **Content that has no slide at all.** Stay on the current slide; do not invent visuals. Mention it in the
  delivery summary if it is long.

## Dwell time sanity

- Minimum for a body slide: about 20 s. Minimum inside a montage: 5 s (8+ preferred).
- Maximum: nothing hard, but at 3+ minutes on one still, look for a legitimate reason to change (a detail
  slide, a return to an overview). Do not add motion or Ken Burns effects to fix a long dwell; a static slide
  with clean audio is the format.
- The last cue must start at least 1 s before the audio ends; the fade-out is 1.2 s.

## What the cue sheet is for later

It is the edit decision list. To move a cut, change one `start` and re-render. Keep `anchor` and `note` filled:
a person reading the file six months later should be able to see why each cut is where it is without
re-listening.
