# Script template — the 6-scene shape

Most Shorts here are six scenes, 60–90 seconds total. Six is not a
magic number; it's what fits one story with a beginning, a middle, and
a payoff without rushing. Shorter stories get four scenes. Never pad a
four-scene story to six — the padding is where viewers leave.

Each scene is one video clip (usually 10 seconds, generated) plus
narration. The narration almost always runs longer than the clip, so
the scene is stretched with a zoom-hold tail (see
`scripts/build_short.py`). Plan for that: a scene's length is set by
its narration, not by its clip.

## The shape

| Scene | Job | Length |
|---|---|---|
| S1 | Hook + promise. The impossible fact, then "stay with me, because..." | 10–12s |
| S2 | Place and time. Where, when, who — the proof that this is real | 12–14s |
| S3 | The mechanism. How the thing worked, or how it went wrong | 14–16s |
| S4 | The turn. Someone pushes back, or the situation gets worse | 12–14s |
| S5 | The climax. The court case, the decision, the escape | 12–14s |
| S6 | The payoff + question + like/comment/subscribe | 16–18s |

## Writing rules

- **One idea per sentence.** Narration is spoken, not read. If a
  sentence needs a comma to survive, split it.
- **Write the captions from the narration, not the other way round.**
  Captions are the 3–6 loudest phrases in each scene, timed to the
  words as they're spoken. A caption that appears before its words
  feels like a spoiler; one that appears after feels like an echo.
- **The last line of S6 restates the hook.** "Five dying women took on
  a giant" at the end answers "five dying women took them to court"
  from the start. The viewer leaves with one sentence in their head,
  not six scenes.
- **Numbers beat adjectives.** "Ten thousand dollars each" lands.
  "A huge amount of money" doesn't.
- **No "%" anywhere in captions.** ffmpeg's drawtext treats it as a
  format escape. Write "PERCENT".

## Blank script

Copy this, fill it in, then generate narration per scene (see
`docs/tts-pipeline.md`) and measure the real durations before setting
scene lengths in `scenes.json`.

```
TITLE:
HOOK (on-screen text, 2 lines):
HOOK (first narration line):
PROMISE (why stay):

S1 — [clip: what the viewer sees]
Narration:
Captions: / /

S2 — [clip:]
Narration:
Captions: / /

S3 — [clip:]
Narration:
Captions: / /

S4 — [clip:]
Narration:
Captions: / /

S5 — [clip:]
Narration:
Captions: / /

S6 — [clip:]
Narration:
Question to viewer:
Captions: / /
```
