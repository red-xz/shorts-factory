#!/usr/bin/env python3
"""burn_captions.py — burn subtitles into a finished Short.

Two modes:

1. Burn an .ass file you already have:
       burn_captions.py in.mp4 subs.ass out.mp4

2. Turn an .srt into a styled .ass first, then burn it:
       burn_captions.py in.mp4 subs.srt out.mp4 --style pop

The built-in styles are tuned for 1080x1920 and for the older viewers
this channel actually gets: big type, thick black outline, high
contrast. --style pop puts lines near the bottom third (above the
like/comment buttons), --style top puts them near the top (use it when
the bottom of the frame is busy).

If your font isn't found, pass --fontsdir with the folder it lives in.
"""
import argparse
import os
import re
import subprocess
import sys

STYLES = {
    # name: (font, size, primary colour, outline, alignment, margin_v)
    # ASS colours are &HAABBGGRR; alignment 2 = bottom-centre, 8 = top-centre.
    "pop": ("Noto Sans Black", 54, "&H00FFFFFF", 4, 2, 420),
    "top": ("Noto Sans Black", 54, "&H00FFFFFF", 4, 8, 160),
    "gold": ("Noto Sans Black", 54, "&H0000C8FF", 4, 2, 420),
}

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: {name},{font},{size},{colour},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,{outline},0,{align},40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def srt_time_to_ass(t):
    # 00:00:03,500 -> 0:00:03.50
    h, m, rest = t.split(":")
    s, ms = rest.split(",")
    return f"{int(h)}:{m}:{s}.{ms[:2]}"


def srt_to_ass(srt_path, style_name):
    with open(srt_path, encoding="utf-8") as f:
        text = f.read()

    font, size, colour, outline, align, margin_v = STYLES[style_name]
    out = [ASS_HEADER.format(name=style_name, font=font, size=size,
                             colour=colour, outline=outline, align=align,
                             margin_v=margin_v)]

    # Blocks: index line, "start --> end" line, one or more text lines.
    blocks = re.split(r"\n\s*\n", text.strip())
    for block in blocks:
        lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
        if len(lines) < 3:
            continue
        m = re.match(r"(\S+)\s*-->\s*(\S+)", lines[1])
        if not m:
            continue
        start, end = srt_time_to_ass(m.group(1)), srt_time_to_ass(m.group(2))
        caption = "\\N".join(lines[2:])
        out.append(f"Dialogue: 0,{start},{end},{style_name},,0,0,0,,{caption}\n")

    return "".join(out)


def main():
    ap = argparse.ArgumentParser(description="Burn subtitles into a video")
    ap.add_argument("input", help="input mp4")
    ap.add_argument("subs", help=".ass or .srt subtitle file")
    ap.add_argument("output", help="output mp4")
    ap.add_argument("--style", default="pop", choices=list(STYLES),
                    help="style for .srt input (default: pop)")
    ap.add_argument("--fontsdir", default="/usr/share/fonts/truetype/noto",
                    help="folder with the caption font")
    ap.add_argument("--keep-ass", help="also save the generated .ass here")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        sys.exit(f"no such file: {args.input}")
    if not os.path.exists(args.subs):
        sys.exit(f"no such file: {args.subs}")

    ass = args.subs
    if args.subs.lower().endswith(".srt"):
        ass = args.keep_ass or args.output + ".ass"
        with open(ass, "w", encoding="utf-8") as f:
            f.write(srt_to_ass(args.subs, args.style))
        print(f"wrote {ass} (style: {args.style})")

    # The subtitles filter wants its path escaped; single quotes inside
    # the filter string are the usual trip-up, so escape them.
    sub_path = os.path.abspath(ass).replace("'", r"\'")
    vf = f"subtitles='{sub_path}'"
    if args.fontsdir and os.path.isdir(args.fontsdir):
        vf += f":fontsdir='{args.fontsdir}'"

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", args.input,
           "-vf", vf, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "copy", args.output]
    print("  $", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("wrote", args.output)


if __name__ == "__main__":
    main()
