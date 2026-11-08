# Video Score Transcription

An Agent Skill for Codex and Claude Code: recover notation from videos with audible performances and synchronized score changes, optionally cross-check it against piano audio, and produce an editable score and a proofread PDF.

The agent does the musical reading and correction. This is not a new transcription model or an unattended one-command converter. The included helpers extract timestamped frames/contact sheets and render ABC to PDF with explicit pagination. Audio-model setup, discrepancy review and notation validation are documented workflows.

## Supported videos

**The video must contain an audible musical performance, and the displayed sheet music must change in sync with the passage being played.** Synchronized page/system switches or scrolling notation are supported. The agent checks the correspondence at multiple points before transcribing.

Static-score videos, silent score videos, unrelated or unsynchronized audio, hands-only footage, piano-roll-only graphics, and audio-only input are outside this skill's supported workflow. Audio-model inference is optional; synchronized performance audio is required.

## Install

Clone the repository, then copy it into your agent's skill directory:

```sh
git clone https://github.com/hitokun-s/video-score-transcription.git
mkdir -p ~/.agents/skills ~/.claude/skills
cp -R video-score-transcription ~/.agents/skills/video-score-transcription
cp -R video-score-transcription ~/.claude/skills/video-score-transcription
```

Install locations:

- Codex: `~/.agents/skills/` (or the skill directory configured by your Codex environment).
- Claude Code: `~/.claude/skills/`.

The same folder works in both; `agents/openai.yaml` is optional Codex UI metadata. Start a new session if the skill is not discovered.

Example requests:

```text
Codex: $video-score-transcription Turn the score in this video into PDF and MusicXML, and cross-check the audio.
Claude Code: /video-score-transcription Transcribe the score in this video into an editable score and PDF.
```

Supply a URL or local file for a qualifying synchronized performance-and-score video. The skill can also be selected from ordinary requests about converting a video's visible sheet music into notation.

## Tools

- Download/extraction: yt-dlp, FFmpeg/ffprobe, Python 3; Pillow for contact sheets.
- Included PDF helper: Node.js, abcjs, playwright-core and Chrome/Chromium. Dependencies are resolved from `--deps`, not the skill's installation folder.
- Optional audio check: ByteDance piano_transcription_inference and its dependencies/checkpoint.
- MusicXML/MIDI export: use the agent's available notation pipeline. A converter is not bundled.

```sh
python3 scripts/extract-frames.py video.mp4 output/frames --interval 2
npm install --prefix ./task-tools abcjs playwright-core
node scripts/render-abc.mjs score.abc score.pdf --deps ./task-tools --chrome /path/to/chrome
```

See [SKILL.md](SKILL.md) for the workflow and [notation details](references/notation-and-output.md) / [audio checks](references/audio-check.md) for conditional instructions.

## Validation and limits

The helper tests run on Linux using a generated FFmpeg test pattern and an original scale-exercise score. They check timestamped extraction, existing-output protection, invalid sampling arguments, multi-page PDF rendering, note-event counts, and empty-score rejection. These are helper integration tests, not an end-to-end transcription benchmark. Other operating systems and end-to-end invocation inside Claude Code have not been tested.

Inspect the actual score and rendered pages. Audio agreement cannot validate note spelling, written rhythm, voices or layout. Fast scrolling, poor resolution and missing passages may require additional frames or user input. State unsupported/omitted details explicitly.

## Related projects

- [Kengraver](https://github.com/katiahayati/kengraver): an agent skill for scanned-score transcription, MusicXML encoding and rendered proofreading.
- [Rescored](https://github.com/calebyhan/rescored): a YouTube audio transcription/editing application.
- [ByteDance piano_transcription](https://github.com/bytedance/piano_transcription): the optional piano audio model.
- [abcjs](https://github.com/paulrosen/abcjs): notation rendering.

This skill focuses on video-frame coverage and visual/audio discrepancy review. No source video, third-party score, model weights, browser binary or third-party converter is bundled.

## Development

```sh
npm ci
python3 -m pip install -r requirements-dev.txt
ruff check .
ruff format --check .
npm run lint
npm run format:check
python3 -m unittest discover -s tests -v
```

The tests generate their own synthetic video and notation. FFmpeg, Pillow and Chrome/Chromium are required for the integration tests. Set `CHROME` to the browser executable if it is not on a standard Linux path. In environments that require disabling Chrome's sandbox, explicitly set `RENDER_NO_SANDBOX=1` when running tests.

## License

Original skill instructions, helper code and test generators are available under the MIT license. See [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The license does not grant rights to input recordings, compositions, sheet music or transcriptions of third-party works. Those materials are not included in this repository. Dependencies and optional model checkpoints retain their own terms.
