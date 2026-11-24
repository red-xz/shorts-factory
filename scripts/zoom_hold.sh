#!/bin/bash
# zoom_hold.sh — stretch a clip past its own length by holding one frame
# with a slow breathing zoom. This is how a 10-second generated clip
# becomes a 14-second scene: the narration almost always runs longer
# than the clip, and a frozen last frame looks dead. A zooming hold
# doesn't.
#
# Usage:
#   zoom_hold.sh clip.mp4 4.0 tail.mp4          # hold the LAST frame 4s
#   zoom_hold.sh clip.mp4 4.0 tail.mp4 8.5      # hold the frame at t=8.5s
#
# Same zoom as make_9x16.sh: 1.00x -> 1.08x -> 1.00x over 6 seconds.
set -e

if [ $# -lt 3 ]; then
  echo "usage: $0 clip.mp4 seconds out.mp4 [frame_time|last]" >&2
  exit 1
fi

CLIP="$1"
HOLD="$2"
OUT="$3"
FT="${4:-last}"

if [ ! -f "$CLIP" ]; then
  echo "no such file: $CLIP" >&2
  exit 1
fi

FRAME=$(mktemp /tmp/zoom_hold_XXXXXX.png)
trap 'rm -f "$FRAME"' EXIT

if [ "$FT" = "last" ]; then
  ffmpeg -y -v error -sseof -0.05 -i "$CLIP" -frames:v 1 "$FRAME"
else
  ffmpeg -y -v error -ss "$FT" -i "$CLIP" -frames:v 1 "$FRAME"
fi

# Same breathing zoom as make_9x16.sh, done with scale+eval=frame
# (zoompan is far too slow at this size — see that script's comment).
ffmpeg -y -v error -loop 1 -i "$FRAME" -vf \
  "scale=1080:1920,scale=w='1080*(1+0.08*abs(sin(PI*t/6)))':h='1920*(1+0.08*abs(sin(PI*t/6)))':eval=frame,crop=1080:1920,fps=24" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 24 -t "$HOLD" "$OUT"

ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
