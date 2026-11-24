#!/bin/bash
# test.sh — run the example end to end and check the output.
# Takes a minute or two on a modest machine.
set -e
cd "$(dirname "$0")"

./examples/petrov-1983/build.sh

OUT=examples/petrov-1983/petrov-1983-FINAL.mp4
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$OUT")
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$OUT")
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")
[ "$W" = "1080" ] && [ "$H" = "1920" ] || { echo "FAIL: $W x $H"; exit 1; }
python3 -c "import sys; sys.exit(0 if 55 < $DUR < 57 else 1)" \
  || { echo "FAIL: duration $DUR, expected ~56s"; exit 1; }
echo "OK: $OUT is ${W}x${H}, ${DUR}s"
