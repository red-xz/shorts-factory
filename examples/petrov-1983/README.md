# Example: Petrov, 1983

One complete Short, start to finish — the same files a real video
uses, with placeholder media so it runs anywhere.

## What's here

- `script.md` — the full six-scene script, with the narration text and
  the captions for each scene.
- `scenes.json` — the build spec: clips, audio, scene lengths, caption
  timings. This is what `build_short.py` reads.
- `build.sh` — generates placeholder clips and tone audio, builds the
  video, then verifies it.

## Run it

```bash
./build.sh
```

Takes a minute or two. Output
is `petrov-1983-FINAL.mp4`, 56 seconds, 1080x1920, six scenes with a
hook overlay on the first three seconds and caption pop-ins throughout.

## Make it real

1. Replace `clip1.mp4`–`clip6.mp4` with real clips (any video
   generation model, or real footage — the builder doesn't care).
2. Replace `s1.mp3`–`s6.mp3` with real narration. See
   `docs/tts-pipeline.md` for how the timing works.
3. Measure the real narration durations with ffprobe and update the
   `length` values in `scenes.json` — narration + 0.5s delay + ~0.5s
   breathing room per scene.
4. Re-time the captions to the real sentence boundaries
   (`silencedetect`, same doc).
5. Run `python3 ../../scripts/build_short.py .` directly — no need
   for `build.sh` once the media is real.
