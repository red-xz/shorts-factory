#!/bin/bash
# make_9x16.sh — take any clip and make it a proper vertical Shorts clip:
# 1080x1920, 24fps, with a slow breathing zoom so the frame is never
# completely static. Crops the sides off landscape footage (center crop).
#
# Usage:
#   make_9x16.sh input.mp4 output.mp4
#   make_9x16.sh input.mp4 output.mp4 --no-zoom   # plain scale+crop, no zoom
#
# The zoom breathes 1.00x -> 1.08x -> 1.00x over 6 seconds, so the
# direction of movement changes every 3 seconds. That 3-second rule is
# the whole point: a static shot longer than ~3s is where people swipe.
set -e

if [ $# -lt 2 ]; then
  echo "usage: $0 input.mp4 output.mp4 [--no-zoom]" >&2
  exit 1
fi

IN="$1"
OUT="$2"
ZOOM=1
[ "${3:-}" = "--no-zoom" ] && ZOOM=0

if [ ! -f "$IN" ]; then
  echo "no such file: $IN" >&2
  exit 1
fi

BASE="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"

# Breathing zoom done with scale+eval=frame, not zoompan: same 1.00x ->
# 1.08x -> 1.00x over 6 seconds, roughly 50x faster than zoompan at
# 1080x1920 (zoompan took minutes for a few seconds of video).
if [ "$ZOOM" = 1 ]; then
  VF="$BASE,scale=w='1080*(1+0.08*abs(sin(PI*t/6)))':h='1920*(1+0.08*abs(sin(PI*t/6)))':eval=frame,crop=1080:1920,fps=24"
else
  VF="$BASE,fps=24"
fi

ffmpeg -y -v error -i "$IN" -vf "$VF" \
  -map 0:v:0 -map 0:a? \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 192k -ar 48000 "$OUT"

ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate -show_entries format=duration \
  -of default=noprint_wrappers=1 "$OUT"
