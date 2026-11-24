#!/usr/bin/env python3
"""build_short.py — assemble a faceless Short from scenes.

Takes a project folder with a scenes.json file and produces one finished
1080x1920 mp4. Each scene is a video clip + a narration file + timed
caption pop-ins. When the narration runs longer than the clip (it almost
always does), the scene is stretched with a zoom-hold tail: the last
frame, held with a slow breathing zoom, so nothing ever freezes.

scenes.json looks like this:

    {
      "title": "petrov-1983",
      "audio_delay": 0.5,
      "hook": {"image": "hook.png", "scene": 0, "y": 1520, "start": 0, "end": 3},
      "scenes": [
        {
          "clip": "clip1.mp4",
          "audio": "s1.mp3",
          "length": 11.5,
          "captions": [
            {"text": "SEPTEMBER 26, 1983", "start": 0.5, "end": 3.0, "color": "gold"},
            {"text": "FIVE MISSILES WERE COMING", "start": 4.0, "end": 7.0}
          ]
        }
      ]
    }

Rules that come from getting burned:

- Caption text must not contain "%" — ffmpeg's drawtext treats it as a
  format escape and mangles the caption. Write "PERCENT" instead.
- Narration is delayed 0.5s into each scene (audio_delay). The picture
  lands first, then the voice. Without the delay the first word gets
  clipped by the scene cut.
- A scene's length should leave ~0.5s of breathing room after the
  narration ends. Measure narration with ffprobe before you set lengths.

Usage:
    build_short.py project_dir [--out out.mp4] [--workdir edit]
"""
import argparse
import json
import os
import subprocess
import sys

FPS = 24
WIDTH, HEIGHT = 1080, 1920
DEFAULT_FONT = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"

GOLD = "0xFFC800"
WHITE = "white"

# Zoom breathing 1.00 -> 1.08 -> 1.00 over 6s (direction changes every 3s).
# Done with scale+eval=frame rather than zoompan: identical movement,
# roughly 50x faster at 1080x1920.
ZOOM = (
    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
    "scale=w='1080*(1+0.08*abs(sin(PI*t/6)))'"
    ":h='1920*(1+0.08*abs(sin(PI*t/6)))':eval=frame,"
    "crop=1080:1920,fps=24"
)


def run(cmd, **kw):
    print("  $", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, **kw)


def probe_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def caption_size(text, size):
    """Hand-tuned sizes in the original builds were 40-64 depending on
    how long the line was. This guesses the same way; pass an explicit
    size in scenes.json to override."""
    if size:
        return size
    n = len(text)
    if n <= 14:
        return 64
    if n <= 20:
        return 56
    if n <= 28:
        return 48
    if n <= 34:
        return 44
    return 40


def main():
    ap = argparse.ArgumentParser(description="Assemble a Short from scenes.json")
    ap.add_argument("project", help="project folder containing scenes.json")
    ap.add_argument("--out", help="output mp4 (default: <title>-FINAL.mp4)")
    ap.add_argument("--workdir", default="edit",
                    help="working folder inside the project (default: edit)")
    ap.add_argument("--font", default=DEFAULT_FONT, help="caption font file")
    args = ap.parse_args()

    project = os.path.abspath(args.project)
    with open(os.path.join(project, "scenes.json")) as f:
        spec = json.load(f)

    if not os.path.exists(args.font):
        sys.exit(f"font not found: {args.font} (pass --font to use another)")

    work = os.path.join(project, args.workdir)
    os.makedirs(work, exist_ok=True)

    title = spec.get("title", os.path.basename(project))
    out = args.out or os.path.join(project, f"{title}-FINAL.mp4")
    delay = spec.get("audio_delay", 0.5)
    delay_ms = int(round(delay * 1000))
    hook = spec.get("hook")
    here = os.path.dirname(os.path.abspath(__file__))

    segments = []
    boundaries = []
    total = 0.0

    for i, scene in enumerate(spec["scenes"], start=1):
        clip = os.path.join(project, scene["clip"])
        length = float(scene["length"])
        clip_dur = probe_duration(clip)
        tail_len = length - clip_dur

        print(f"--- S{i}: {length:.2f}s (clip {clip_dur:.2f}s) ---")

        inputs = ["-i", clip]
        n_inputs = 1
        tail = None
        if tail_len > 0.05:
            tail = os.path.join(work, f"s{i}_tail.mp4")
            run([os.path.join(here, "zoom_hold.sh"), clip,
                 str(round(tail_len, 2)), tail])
            inputs += ["-i", tail]
            n_inputs += 1

        hook_idx = None
        if hook and hook.get("scene", 0) == i - 1:
            hook_idx = n_inputs
            inputs += ["-loop", "1", "-i",
                       os.path.join(project, hook["image"])]
            n_inputs += 1

        audio = scene.get("audio")
        audio_idx = n_inputs
        if audio:
            inputs += ["-i", os.path.join(project, audio)]
        else:
            # No narration for this scene: silent audio so the final
            # concat still lines up.
            inputs += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]

        # Caption text goes through files, not the command line — shell
        # and ffmpeg escaping both mangle quotes and colons otherwise.
        dt_parts = []
        dt = f"fontfile={args.font}:fontcolor={WHITE}:borderw=3:bordercolor=black"
        dtg = f"fontfile={args.font}:fontcolor={GOLD}:borderw=3:bordercolor=black"
        for j, cap in enumerate(scene.get("captions", [])):
            text = cap["text"]
            if "%" in text:
                sys.exit(f"S{i} caption {j + 1}: '%' breaks drawtext, "
                         f"write PERCENT instead: {text!r}")
            capfile = os.path.join(work, f"t_cap{i}_{j}.txt")
            with open(capfile, "w") as f:
                f.write(text)
            style = dtg if cap.get("color") == "gold" else dt
            size = caption_size(text, cap.get("size"))
            y = cap.get("y", 120)
            dt_parts.append(
                f"drawtext={style}:textfile={capfile}:fontsize={size}"
                f":x=(w-text_w)/2:y={y}"
                f":enable='between(t,{cap['start']},{cap['end']})'")

        fc = [f"[0:v]{ZOOM}[base]"]
        last = "base"
        if tail is not None:
            fc.append("[base][1:v]concat=n=2:v=1:a=0[v0]")
            last = "v0"
        if hook_idx is not None:
            y = hook.get("y", 1520)
            fc.append(f"[{last}][{hook_idx}:v]overlay=0:{y}"
                      f":enable='between(t,{hook.get('start', 0)},"
                      f"{hook.get('end', 3)})'[v1]")
            last = "v1"
        if dt_parts:
            fc.append(f"[{last}]" + ",".join(dt_parts) + "[v]")
            last = "v"
        if audio:
            # Single adelay value applies to every channel, mono or stereo.
            fc.append(f"[{audio_idx}:a]adelay={delay_ms},"
                      f"apad,atrim=0:{length}[a]")
        else:
            fc.append(f"[{audio_idx}:a]atrim=0:{length}[a]")

        seg = os.path.join(work, f"seg{i}.mp4")
        run(["ffmpeg", "-y", "-v", "error"] + inputs + [
            "-filter_complex", ";".join(fc),
            "-map", f"[{last}]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", "24",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", str(length), seg])
        segments.append(seg)
        total += length
        boundaries.append(total)
        print(f"    -> {seg} ({probe_duration(seg):.2f}s)")

    listfile = os.path.join(work, "list.txt")
    with open(listfile, "w") as f:
        for seg in segments:
            f.write(f"file '{seg}'\n")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", listfile, "-c", "copy", out])

    print(f"\nDone: {out}")
    print(f"Total {total:.2f}s, scene boundaries at "
          + " / ".join(f"{b:.2f}" for b in boundaries))
    print(f"Final duration: {probe_duration(out):.2f}s")


if __name__ == "__main__":
    main()
