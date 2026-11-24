#!/bin/bash
# build.sh — run the Petrov example end to end.
#
# The clips and narration here are placeholders so the example runs
# anywhere with just ffmpeg: test-pattern clips with a scene label, and
# a low sine tone per scene standing in for real TTS. The pipeline
# itself — zoom-hold tails, hook overlay, caption pop-ins, audio delay,
# concat, verification — is the real one.
#
# To make it a real video: drop in real clip1.mp4..clip6.mp4 and real
# s1.mp3..s6.mp3, measure the narration durations, fix the scene
# lengths in scenes.json, and run build_short.py directly.
set -e
cd "$(dirname "$0")"
ROOT="$(cd ../.. && pwd)"
FONT=/usr/share/fonts/truetype/noto/NotoSans-Black.ttf

echo "== placeholder clips (6s each) =="
HUES="0 60 120 180 240 300"
i=1
for HUE in $HUES; do
  ffmpeg -y -v error -f lavfi -i testsrc2=size=1080x1920:rate=24:d=6 \
    -vf "hue=h=$HUE,drawtext=fontfile=$FONT:text='SCENE $i':fontsize=90:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=900" \
    -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p clip$i.mp4
  i=$((i + 1))
done

echo "== placeholder narration (sine tone, one pitch per scene) =="
# Durations match the script: scene length = tone + 0.5s delay + 0.5s room.
DURS="7 8 9 8 8 10"
FREQS="440 494 523 587 659 698"
i=1
for D in $DURS; do
  F=$(echo "$FREQS" | cut -d' ' -f$i)
  ffmpeg -y -v error -f lavfi -i "sine=frequency=$F:duration=$D" \
    -af "volume=0.15" -c:a libmp3lame -b:a 128k s$i.mp3
  i=$((i + 1))
done

echo "== hook PNG =="
python3 "$ROOT/scripts/make_hook.py" \
  --line "SEPTEMBER 26, 1983" --line "ONE MAN DECIDED" hook.png

echo "== build =="
python3 "$ROOT/scripts/build_short.py" .

echo "== verify (boundaries 8 / 17 / 27 / 36 / 45 / 56) =="
"$ROOT/scripts/check_short.sh" petrov-1983-FINAL.mp4 8 17 27 36 45
