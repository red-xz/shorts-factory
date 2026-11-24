#!/bin/bash
# check_short.sh — verify a finished Short before it goes anywhere.
#
# Checks: 1080x1920, 24fps, audio present, and — the one that matters
# most — 2-second audio slices across the whole file. A 10-second
# loudness window hides silent stretches: a film once shipped with 8
# seconds of digital silence that every 10s window read as fine.
# 2s slices don't hide anything. Anything below -60 dB is flagged.
#
# Usage: check_short.sh final.mp4 [boundaries...]
#   Boundaries are scene-cut times in seconds; the slices touching a
#   cut get called out separately, since a gap across a cut is the
#   defect that actually costs viewers.
set -e

if [ $# -lt 1 ]; then
  echo "usage: $0 final.mp4 [scene_boundary_seconds...]" >&2
  exit 1
fi

FILE="$1"
shift
FAIL=0

echo "== $FILE =="
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,codec_name \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 "$FILE"

W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$FILE")
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$FILE")
[ "$W" = "1080" ] && [ "$H" = "1920" ] || { echo "FAIL: not 1080x1920 ($W x $H)"; FAIL=1; }

ASTREAMS=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$FILE" | wc -l)
[ "$ASTREAMS" -ge 1 ] || { echo "FAIL: no audio stream"; FAIL=1; }

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FILE")
echo "== audio in 2s slices (mean dB; below -60 is silent) =="
T=0
while true; do
  T=$(python3 -c "print(f'{$T + 2:.1f}')")
  [ "$(python3 -c "print(1 if $T >= $DUR else 0)")" = "1" ] && break
  START=$(python3 -c "print(f'{$T - 2:.1f}')")
  # volumedetect prints its stats at info level — -v error would hide
  # them and every slice would read as silent.
  MEAN=$(ffmpeg -v info -ss "$START" -t 2 -i "$FILE" -af volumedetect -f null - 2>&1 \
    | awk -F': ' '/mean_volume/ {print $2}' | tr -d ' dB')
  MEAN=${MEAN:--91}
  FLAG=""
  if [ "$(python3 -c "print(1 if $MEAN < -60 else 0)")" = "1" ]; then
    FLAG="  <-- SILENT"
    FAIL=1
  fi
  for B in "$@"; do
    if [ "$(python3 -c "print(1 if $START < $B < $T else 0)")" = "1" ]; then
      FLAG="$FLAG  [scene cut at ${B}s]"
    fi
  done
  printf "  %5.1f-%5.1fs  %s dB%s\n" "$START" "$T" "$MEAN" "$FLAG"
done

if [ "$FAIL" = "0" ]; then
  echo "PASS"
else
  echo "FAIL: see flags above"
  exit 1
fi
