#!/usr/bin/env python3
"""make_hook.py — render the opening hook as a transparent PNG.

The hook is the first thing a viewer reads, so it gets rendered with
PIL instead of ffmpeg drawtext: proper text shaping, a real stroke,
and it never fights with filter escaping. build_short.py overlays the
PNG on the first scene for the opening seconds.

Usage:
    make_hook.py --line "THE GLOWING PAINT" --line "WAS KILLING THEM" hook.png

Lines shrink automatically until they fit the frame width. One or two
lines is right; three starts to look crowded at this size.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

W = 1080
LINE_H = 108
MAX_TEXT_W = 1000
DEFAULT_FONT = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"


def draw_line(d, text, y, size, font_path):
    f = ImageFont.truetype(font_path, size)
    while d.textlength(text, font=f) > MAX_TEXT_W and size > 40:
        size -= 2
        f = ImageFont.truetype(font_path, size)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=(255, 255, 255, 255),
           stroke_width=6, stroke_fill=(0, 0, 0, 255))


def main():
    ap = argparse.ArgumentParser(description="Render a hook PNG")
    ap.add_argument("--line", action="append", required=True,
                    help="one line of hook text (repeat for 2 lines)")
    ap.add_argument("--font", default=DEFAULT_FONT)
    ap.add_argument("--size", type=int, default=72, help="starting font size")
    ap.add_argument("out", help="output PNG path")
    args = ap.parse_args()

    if not os.path.exists(args.font):
        raise SystemExit(f"font not found: {args.font}")
    if len(args.line) > 3:
        raise SystemExit("keep it to 3 lines max — more won't read in 3 seconds")

    img = Image.new("RGBA", (W, LINE_H * len(args.line) + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(args.line):
        draw_line(d, line, 6 + i * LINE_H, args.size, args.font)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    img.save(args.out)
    print("saved", args.out, img.size)


if __name__ == "__main__":
    main()
