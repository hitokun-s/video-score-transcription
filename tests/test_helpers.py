"""Integration checks using generated media, with no third-party score fixtures."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HelpersTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.work = Path(self.directory.name)

    def run_command(self, args, **kwargs):
        return subprocess.run(args, capture_output=True, text=True, **kwargs)

    @unittest.skipUnless(
        shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg is required"
    )
    def test_frames_and_existing_output(self):
        source = self.work / "synthetic.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-f",
                "lavfi",
                "-i",
                "testsrc2=size=160x90:rate=10",
                "-t",
                "1.1",
                "-c:v",
                "mpeg4",
                str(source),
            ],
            check=True,
        )
        output = self.work / "frames"
        command = [
            sys.executable,
            str(ROOT / "scripts/extract-frames.py"),
            str(source),
            str(output),
            "--interval",
            "0.5",
        ]
        result = self.run_command(command)
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual([f["seek_seconds"] for f in manifest["frames"]], [0, 0.5, 1])
        for frame in manifest["frames"]:
            self.assertGreater((output / frame["file"]).stat().st_size, 0)
        self.assertTrue((output / "contact-001.jpg").is_file())
        rerun = self.run_command(command)
        self.assertNotEqual(rerun.returncode, 0)
        self.assertIn("must be empty", rerun.stderr)

    def test_invalid_sampling_arguments(self):
        for option, value in [
            ("--interval", "0"),
            ("--interval", "nan"),
            ("--start", "-1"),
            ("--end", "inf"),
        ]:
            with self.subTest(option=option, value=value):
                result = self.run_command(
                    [
                        sys.executable,
                        str(ROOT / "scripts/extract-frames.py"),
                        "unused.mp4",
                        str(self.work / "frames"),
                        option,
                        value,
                    ]
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("error:", result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required")
    def test_pdf_and_empty_score_rejection(self):
        source = self.work / "synthetic.abc"
        # Eighty bars of original scale exercises exercise multiple page boundaries.
        source.write_text(
            "X:1\nT:Generated scale exercise\nM:4/4\nL:1/8\nK:C\n"
            + "\n".join(["CDEF GABc | cBAG FEDC | CDEF GABc | cBAG FEDC |"] * 20)
            + "\n"
        )
        output = self.work / "score.pdf"
        command = [
            "node",
            str(ROOT / "scripts/render-abc.mjs"),
            str(source),
            str(output),
            "--deps",
            str(ROOT),
        ]
        if os.environ.get("RENDER_NO_SANDBOX") == "1":
            command.append("--no-sandbox")
        result = self.run_command(command)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.work / "score.render.json").read_text())
        self.assertEqual(report["note_events"], 640)
        self.assertGreaterEqual(report["pages"], 2)
        self.assertEqual(report["warnings"], [])
        self.assertTrue(output.read_bytes().startswith(b"%PDF-"))
        if shutil.which("pdfinfo"):
            details = subprocess.check_output(["pdfinfo", str(output)], text=True)
            page_line = next(
                line for line in details.splitlines() if line.startswith("Pages:")
            )
            self.assertEqual(int(page_line.split(":")[1]), report["pages"])
        source.write_text("X:1\nT:Empty\nM:4/4\nK:C\n")
        rejected = self.run_command(command)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("No pitched notes", rejected.stderr)


if __name__ == "__main__":
    unittest.main()
