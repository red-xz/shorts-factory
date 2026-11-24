# Timing — how a scene is put together

A scene has three things that have to agree: the clip, the narration,
and the captions. They are measured separately and assembled by
`build_short.py`, and the assembly only works if the numbers are real.

## The arithmetic

```
scene length = narration duration + 0.5s delay + ~0.5s breathing room
tail length  = scene length - clip duration
```

The clip is usually 10 seconds (that's what the generation models
produce). The narration is usually 10–16 seconds. So a typical scene
is 11–17 seconds long, with a 1–7 second zoom-hold tail on the end.

If the narration is shorter than the clip, there is no tail — the clip
gets trimmed to the scene length. That almost never happens, and when
it does it usually means the scene's script is too thin.

## The 3-second rule

Nothing on screen stays unchanged for more than about 3 seconds. That
is enforced three ways:

1. **The zoom breathes.** Every clip and every tail runs the
   oscillating zoom (1.00x–1.08x, 6-second period), so the direction
   of movement changes every 3 seconds.
2. **Captions pop in.** 3–6 captions per scene, staggered, each timed
   to a sentence. Every pop-in is a visual change.
3. **The hook and the end card.** The hook PNG covers the first 3
   seconds of S1; the end card (question + like/comment/subscribe)
   covers the last ~5 seconds of S6.

A scene with no caption for 6 seconds and no camera movement is a
scene people leave. The zoom alone isn't enough — it has to be zoom
plus captions.

## Checking the finished video

`scripts/check_short.sh` runs the checks that catch the mistakes
you can't see in an edit timeline:

- Resolution is exactly 1080x1920, 24fps.
- An audio stream exists.
- Audio loudness in 2-second slices across the whole file. A 10-second
  window once hid 8 seconds of digital silence in a shipped video;
  2-second slices don't hide anything. Anything below −60 dB is
  flagged, and slices touching a scene boundary get called out
  separately — a silent stretch across a cut is the defect that
  actually costs viewers.

Run it with the scene boundaries from the build output:

```bash
scripts/check_short.sh petrov-1983-FINAL.mp4 11.5 25.5 41.5 55.5 69.5
```

## Frame checks

Automated checks catch silence and wrong sizes. They don't catch a
caption overlapping someone's face, a hook PNG in the wrong place, or
a scene that starts on a frozen frame. Before a video ships, pull
frames at every scene boundary, plus and minus half a second, and
look at them. The boundary is where the defects live — a caption from
the last scene bleeding into the next, a tail that starts on the wrong
frame, a cut that lands mid-word.

```bash
for t in 11.0 11.5 12.0 25.0 25.5 26.0; do
  ffmpeg -y -v error -ss $t -i final.mp4 -frames:v 1 check_$t.png
done
```
