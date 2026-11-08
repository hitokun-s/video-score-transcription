---
name: video-score-transcription
description: Transcribe a YouTube or local video that contains an audible musical performance and displayed sheet music that changes in sync with that performance. Extract timed score frames, read the notation, cross-check the corresponding piano audio when useful, and deliver editable notation and an engraved PDF. Use only for synchronized performance-and-score videos; exclude static score videos, silent score videos, hands-only videos, piano-roll-only videos, audio-only input, and speech transcription.
---

# Video score transcription

Produce a readable, complete PDF and editable notation from a video with an audible performance and sheet music that changes in synchronization with the performance. Both conditions are required. This skill works with Codex and Claude Code: use the host's shell and image-viewing tools; no particular MCP server or paid API is required. Resolve bundled paths relative to this SKILL.md, not the working directory. Write task artifacts to the user's workspace, not into the installed skill.

## Supported input: verify before transcription

The video must contain an audible musical performance, with conventional sheet music displayed and switched (or scrolled) in sync with the passage being played. Confirm this correspondence at several points, including score transitions. Brief fades and page-turn lead-ins are acceptable when the mapping remains clear.

A static score throughout the video, silent notation, unrelated/unsynchronized audio, audio-only input, hands-only footage, and piano-roll-only graphics are outside this skill's supported workflow. If the input fails these conditions, explain the mismatch and request a qualifying video, or obtain the user's direction for a separate transcription workflow. Do not silently turn this skill into a generic audio or scanned-score transcriber. Model inference remains optional; the presence of synchronized performance audio does not.

## Choose the evidence

1. Inspect the input and existing project tools. A URL with playlist parameters normally means the single supplied video unless the user requests the playlist. Download with yt-dlp `--no-playlist`; preserve source title, author/uploader, URL, duration, and commands in metadata. Prefer clear video up to 1080p, increasing only when notation needs it. Keep audio if requested or useful.
2. Start with frames about every two seconds. Use `scripts/extract-frames.py` for explicit seek times and a contact sheet. Inspect the contact sheet, then full-resolution score crops. Increase sampling around fast page turns, scrolling, fades, or occlusion. Do not infer coverage from the first and last frames alone.
3. Treat the synchronized score images as the primary evidence for pitches, note values, voices, rests, key/time signatures, articulations, repeats and written form. Use the audible performance to verify where each displayed passage belongs. Hand positions and inferred audio notes are supporting evidence.
4. Map each unique system/page to its source frame/time and measure range. Keep repeats in the written score distinct from repeated performance passages. Inventory gaps and unreadable measures before calling the result complete.

## Read and represent the music

- Determine each staff's clef and changes, key signature, meter, pickup and voice count. Use staff-line positions, not chord expectations, to read pitches. Recheck ledger lines, accidentals and octave changes on enlarged crops.
- Build explicit per-measure events with hand/staff, voice, beat onset, rational duration, spelled pitch (step/alter/octave), and rest/tie data as applicable. Preserve simultaneous voices: a whole note above moving half notes must not become sequential notes. MIDI pitch alone loses enharmonic spelling and is not sufficient notation data.
- Prefer an existing notation pipeline. ABC + abcjs is suitable for modest scores; MusicXML + a notation engraver is often better for complex polyphony. A JSON intermediate is useful when it makes corrections and checks reproducible, but do not invent a lossy universal schema.
- Preserve meaningful performance instructions. Record omissions such as fingering or simplified pedal notation; do not silently drop them or claim an exact facsimile. A guessed playback BPM must be labeled editorial, separate from printed tempo text.
- Keep uncertain readings with their measure/frame evidence and resolve them by zooming or comparison. Never substitute an invented passage just to fill a gap.

## Optional independent audio check

For piano, see [references/audio-check.md](references/audio-check.md). Use audio inference to find disagreements, then inspect the source again. A model may miss low bass, invent harmonics, retrigger sustained notes, or extend notes under pedal. Its MIDI is not a ground-truth score. Do not overwrite clear notation solely to agree with a model, nor report onset agreement as overall transcription accuracy.

## Engrave and validate

Read [references/notation-and-output.md](references/notation-and-output.md) when generating ABC, MusicXML or PDF. `scripts/render-abc.mjs` provides an abcjs/Chrome renderer with explicit pagination and render warnings. Dependencies are resolved from a caller-selected directory; see its `--help`.

Before delivery:

- Check every voice's measure duration against the local meter, allowing explicitly represented pickups, tuplets, incomplete endings and ties. Compare measure coverage with the source-system map.
- Check event pitches/counts after conversion, including clef changes, transposition and accidentals. Equal counts alone do not establish correctness.
- Inspect engraving warnings, PDF page count and rasterized pages, especially page boundaries, final barline, high ledger notes, dense voices and bass-clef transitions. Fix cut-off content, colliding notation and accidental blank/empty scores.
- If audio was used, retain its independent output and a discrepancy report with decisions. For long videos, work in reviewed sections rather than letting errors accumulate.

Return direct links to the PDF first, then editable ABC/MusicXML and optional MIDI/JSON. Briefly state coverage, checks and remaining uncertainties. Preserve source/frame artifacts and reproducible scripts locally; downloading a video does not imply publishing its media or score. Do not modify the host application or publish a repository unless requested.
