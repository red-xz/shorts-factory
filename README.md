# shorts-factory

The toolkit I use to put together faceless YouTube Shorts — the
assembly half of the job. It takes video clips, narration audio, and a
build spec, and turns them into a finished 1080x1920 video with
caption pop-ins, a hook overlay, and zoom-hold tails where the
narration runs longer than the clip.

It grew out of making history Shorts for my channel (three a day, six
scenes each, for months). Every script here is a cleaned-up version of
something that shipped in a real video — the Radium Girls build is
where most of this comes from. Nothing in here is theoretical; if a
script is in this repo, it has produced a video that went up.

## What it does — and what it doesn't

It assembles and edits. It does not generate video clips, write
scripts, or do text-to-speech. You bring:

- video clips (from a video-generation model, or real footage — the
  builder doesn't care where they came from),
- narration audio, one file per scene, from any TTS service,
- a `scenes.json` saying how they fit together.

It gives you back a finished Short. If you're looking for something
that makes videos from a prompt, this isn't it — that's the generation
model's job, and this repo stays out of its way on purpose.

## How a Short is put together here

Six scenes, 60–90 seconds. Each scene is one clip (usually 10s) plus
narration (usually 10–16s). The narration almost always outruns the
clip, so the scene is stretched with a zoom-hold tail: the last frame,
held with a slow breathing zoom. A frozen frame looks dead; a zooming
hold doesn't, and viewers don't notice the join.

Three rules run through everything:

1. **Nothing stays still for more than ~3 seconds.** Every clip and
   every tail runs an oscillating zoom (1.00x–1.08x, 6-second
   period), and captions pop in 3–6 times per scene. A static stretch
   is where people swipe.
2. **The hook lands in the first 3 seconds.** A fact, not a question,
   with a promise of what's coming later. "They were told to lick the
   paintbrush — every single day. Stay with me, because five dying
   women took them to court."
3. **The narration is delayed 0.5s into each scene.** The picture
   lands first, then the voice. Without the delay every scene feels
   like it starts mid-sentence.

## Quick start

You need ffmpeg and Python 3 with Pillow. The example runs end to end
with placeholder media so you can see the whole flow:

```bash
git clone https://github.com/red-xz/shorts-factory.git
cd shorts-factory/examples/petrov-1983
./build.sh
```

That generates six test-pattern clips and tone audio, builds the
56-second Short, and verifies it. Output is `petrov-1983-FINAL.mp4`.
To make it real, swap in your own clips and narration — see
`examples/petrov-1983/README.md`.

## The scripts

| Script | What it does |
|---|---|
| `scripts/build_short.py` | The assembler. Reads `scenes.json`, builds zoom-hold tails, overlays the hook, burns caption pop-ins, lines up the audio, concats everything. |
| `scripts/make_9x16.sh` | Any clip → 1080x1920, 24fps, with the breathing zoom. |
| `scripts/zoom_hold.sh` | Hold one frame with a breathing zoom for N seconds. The tail-maker. |
| `scripts/burn_captions.py` | Burn an .ass file into a video, or convert an .srt to a styled .ass first. Big high-contrast type, tuned for 1080x1920. |
| `scripts/make_hook.py` | Render the opening hook as a transparent PNG (PIL, proper text shaping — never ffmpeg drawtext for the hook). |
| `scripts/check_short.sh` | Verify a finished video: size, fps, audio present, and 2-second loudness slices across the whole file. |

## The templates

- `templates/s1-test.md` — the topic checklist. Named person or
  animal, extreme stakes, payoff held to the end, US resonance. All
  four or the topic gets dropped.
- `templates/hooks.md` — hook and title patterns, with real examples
  from the channel and the ones that didn't work.
- `templates/script-template.md` — the six-scene shape, blank, ready
  to fill in.

## The docs

- `docs/tts-pipeline.md` — how narration gets made and timed:
  one file per scene, measuring real durations, finding sentence
  boundaries with silencedetect.
- `docs/timing.md` — the scene arithmetic, the 3-second rule, and how
  to check a finished video (including the frame checks automation
  can't do).

## Things I learned the hard way

- **Never put `%` in a caption.** ffmpeg's drawtext treats it as a
  format escape. Write PERCENT. This one cost a rebuild.
- **10-second loudness windows hide silence.** A video once shipped
  with 8 seconds of digital silence that every 10s window read as
  fine. `check_short.sh` uses 2-second slices for exactly that reason.
- **The hook is a PNG, not drawtext.** Proper shaping, a real stroke,
  no filter escaping fights. Render it with PIL and overlay it.
- **Caption text goes through files, not the command line.** Shell
  and ffmpeg escaping both mangle quotes and colons. `build_short.py`
  writes each caption to a text file first.
- **Measure narration, don't trust estimates.** Every TTS
  re-generation shifts timings by a second or two. Re-measure with
  ffprobe, re-time the captions, rebuild.

## Requirements

- ffmpeg 6+ with libx264 and libfdk-aac or the built-in aac encoder
- Python 3.9+, Pillow (`pip install pillow`)
- A heavy black font for captions — Noto Sans Black is the default,
  any bold sans works (pass `--font`)

## License

MIT. Use it for your own channel, sell videos made with it, whatever
— just don't sell the toolkit itself as yours.
