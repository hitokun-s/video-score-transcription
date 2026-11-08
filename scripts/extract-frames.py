#!/usr/bin/env python3
"""Extract timed frames, a manifest, and contact sheets."""

import argparse
import json
import math
import subprocess
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--interval", type=float, default=2)
    p.add_argument("--start", type=float, default=0)
    p.add_argument("--end", type=float)
    args = p.parse_args()
    if (
        not math.isfinite(args.interval)
        or args.interval <= 0
        or not math.isfinite(args.start)
        or args.start < 0
    ):
        p.error("interval must be positive and start nonnegative (finite seconds)")
    if args.end is not None and not math.isfinite(args.end):
        p.error("end must be finite")
    source = args.video.resolve(strict=True)
    duration = float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=nw=1:nk=1",
                str(source),
            ],
            text=True,
        )
    )
    end = duration if args.end is None else min(args.end, duration)
    if not math.isfinite(end) or end <= args.start:
        p.error("end must be finite and greater than start")
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.iterdir()):
        p.error(
            "output directory must be empty; "
            "preserve earlier extracts in a separate directory"
        )
    records = []
    for i in range(math.ceil((end - args.start) / args.interval)):
        time = args.start + i * args.interval
        name = f"frame-{i + 1:05}.png"
        target = args.output / name
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-nostdin",
                "-ss",
                str(time),
                "-i",
                str(source),
                "-frames:v",
                "1",
                "-update",
                "1",
                str(target),
            ],
            check=True,
        )
        if not target.is_file():
            raise RuntimeError(f"No decoded frame at {time}s")
        records.append({"file": name, "seek_seconds": time})
    (args.output / "manifest.json").write_text(
        json.dumps(
            {
                "source": str(source),
                "duration_seconds": duration,
                "interval_seconds": args.interval,
                "timestamp_semantics": (
                    "requested seek time; selected decoded frame may differ "
                    "by one frame interval"
                ),
                "frames": records,
            },
            indent=2,
        )
        + "\n"
    )
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("Frames and manifest saved. Install Pillow for contact sheets.")
    else:
        # Multiple sheets keep long videos inspectable without giant image files.
        for offset in range(0, len(records), 24):
            batch = records[offset : offset + 24]
            sheet = Image.new("RGB", (960, math.ceil(len(batch) / 3) * 205), "white")
            draw = ImageDraw.Draw(sheet)
            for k, record in enumerate(batch):
                x, y = (k % 3) * 320, (k // 3) * 205
                with Image.open(args.output / record["file"]) as im:
                    im.thumbnail((320, 180))
                    sheet.paste(im, (x, y))
                draw.text(
                    (x + 4, y + 184),
                    f"{record['file']}  {record['seek_seconds']:.2f}s",
                    fill="black",
                )
            sheet.save(args.output / f"contact-{offset // 24 + 1:03}.jpg")
    print(f"{len(records)} frames saved to {args.output}")


if __name__ == "__main__":
    main()
