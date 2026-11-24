# TTS pipeline — narration, timed to scenes

This toolkit doesn't do text-to-speech itself. It takes narration
audio files — one per scene — and lines them up with the video. This
doc is how those files get made and timed, because the timing is
where most Shorts quietly go wrong.

## The shape of the work

1. Write the script scene by scene (see `templates/script-template.md`).
2. Generate one audio file per scene: `s1.mp3`, `s2.mp3`, ... `s6.mp3`.
   One file per scene, not one file for the whole video — scenes get
   re-timed constantly, and re-generating one scene is cheap.
3. Measure each file's real duration with ffprobe. Never trust the
   estimate from the TTS tool.
4. Set each scene's length to narration + ~0.5s of breathing room,
   plus the 0.5s delay (below). The narration ends before the scene
   ends, always.
5. Find the sentence boundaries inside each file with silencedetect
   (below) and time the captions to them.

## Choosing a voice

Any TTS service works — a cloud voice API, a local model, whatever you
already use. What matters is consistency: one voice for the whole
channel, the same speed every time, so a viewer who watches three
videos in a row hears the same narrator. Switching voices between
videos makes the channel feel like a compilation, not a channel.

For this channel's history Shorts: a male documentary voice, English,
slightly faster than conversational (around 1.1x–1.15x). Slower sounds
authoritative but loses younger viewers; faster sounds rushed to the
older viewers who are actually the biggest audience. Test on your own
audience, then lock it in and stop changing it.

## The 0.5s delay

Every scene's narration starts 0.5 seconds after the scene starts
(`audio_delay` in `scenes.json`, applied by `build_short.py`). Two
reasons: the picture lands first so the first word isn't stepped on by
the cut, and the cut itself gets a half-second of clean picture to
register. It sounds like nothing. Removing it makes every scene feel
like it's starting mid-sentence.

## Finding sentence boundaries

Captions are timed to the words as spoken, so you need to know when
each sentence starts and ends inside the audio file. `silencedetect`
finds the gaps:

```bash
ffmpeg -i s1.mp3 -af silencedetect=noise=-40dB:d=0.25 -f null - 2>&1 \
  | grep -E "silence_(start|end)"
```

The gaps between `silence_end` and the next `silence_start` are the
sentences. Add the 0.5s delay to get scene time. A caption for a
sentence runs from its start to its end, sometimes held a beat longer
if it's the scene's key line.

## What goes wrong

- **Narration longer than the scene.** The last words get cut by
  `atrim`. Fix by lengthening the scene (the zoom-hold tail grows),
  not by speeding up the audio — sped-up narration sounds wrong
  immediately.
- **Narration much shorter than the scene.** Dead air at the end of a
  scene, which `check_short.sh` catches as silence. Fix by shortening
  the scene, or by adding a line to the narration.
- **Re-generating one scene changes its length.** Every re-generation
  shifts timings by a second or two. Re-measure, re-time the captions
  for that scene, rebuild. Don't guess.
- **The voice reads the punctuation.** Dashes and ellipses in the
  script become pauses of unpredictable length. Write the script the
  way you want it spoken, with short sentences, and read it aloud
  once before generating.
