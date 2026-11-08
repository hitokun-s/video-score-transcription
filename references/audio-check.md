# Optional piano audio cross-check

ByteDance's [piano_transcription](https://github.com/bytedance/piano_transcription) and its [inference package](https://github.com/qiuqiangkong/piano_transcription_inference) estimate note/pedal events from piano audio. They output performance MIDI, not fully edited sheet music. Use an existing working environment/checkpoint when available; do not search unrelated personal directories or dump credentials.

## Acquisition and setup

Download a separate audio stream with yt-dlp `--no-playlist -f bestaudio`. If a stream returns HTTP 403, inspect available formats and try a supported alternative once; HLS audio (often format 234) can work, but IDs are not universal. Respect host network approvals. If access still fails, continue image transcription and disclose that audio checking was unavailable; do not loop through access workarounds.

```sh
ffmpeg -i audio.mp4 -ac 1 -ar 16000 audio.wav
```

Use an isolated Python environment with `piano-transcription-inference`, `librosa`, `soundfile`, `audioread`, and compatible PyTorch. The inference package may not declare `audioread` even though it imports it. Prefer a CPU build when no suitable GPU is available; check current installation instructions rather than hard-coding a torch version. Initial checkpoint download can be large. Local inference does not need a paid transcription API.

Minimal API usage after dependency setup:

```python
import soundfile as sf
from piano_transcription_inference import PianoTranscription

samples, rate = sf.read("audio.wav", dtype="float32")
assert rate == 16000 and samples.ndim == 1
model = PianoTranscription(device="cpu", checkpoint_path=None)
result = model.transcribe(samples, "audio-model.mid")
# Persist result['est_note_events'] as JSON with numeric types normalized.
```

## Compare evidence rather than copying MIDI

- Align score onset groups to performance onset groups, allowing tempo drift, arpeggiation, model extras/misses, repeats and rubato. A fixed BPM/time grid is often inappropriate for a human performance.
- A dynamic-programming sequence alignment of pitch sets can nominate discrepancies. Avoid treating small within-chord onset differences as distinct score beats; choose tolerance from the performance instead of a universal constant.
- Inspect every disagreement in its original score crop. Record measure, beat, frame/time, expected/model pitches and decision. Low bass may be missed and pedal resonances can be falsely retriggered.
- A high matched-note fraction only measures the chosen alignment's pitch/onset agreement. It does not validate durations, enharmonic spelling, pedal, voice assignment, articulation or page layout. Do not call it transcription accuracy.
- Report whether the model was actually run. Reading documentation or downloading audio alone does not count as an audio check.
