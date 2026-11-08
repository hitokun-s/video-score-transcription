# Notation and rendering details

## ABC pitfalls observed in real video transcriptions

- No blank line between the ABC header and body: a blank line can terminate the tune and produce an almost empty PDF/XML without a process failure.
- `L:1/8`: a unit is half a quarter-note beat. Bracket chords share duration. Accidentals apply according to the notation's measure/octave rules, not globally to a pitch class.
- Declare voices and grouping explicitly, e.g. `%%score { ( RH R2 ) | LH }`. Use a secondary voice with invisible `x` rests for sustained notes over moving notes. Overlay `&` may parse differently across renderers and converters; inspect the converted result.
- Repeated inline voice selectors can reset clefs in some pipelines. Explicitly specify the correct clef at each system and at actual mid-system changes. Verify that left-hand bass passages do not acquire many unexpected ledger lines.
- Group eighth notes into intended beams rather than putting arbitrary whitespace between every pair. Do not force four bars on the final line when five fit better.
- Unsupported decorations can silently disappear. Check warnings and choose supported symbols or clear text (for example `Ped.` / `pedal simile`), documenting any simplification.

## Renderer setup

Use an existing Node project with `abcjs` and `playwright-core`, or install these in a separate task-tools directory (not into an unrelated application merely for rendering). The renderer uses `--deps DIR` to find them, so it works from an installed skill outside the project.

```sh
npm install --prefix ./task-tools abcjs playwright-core
node /path/to/skill/scripts/render-abc.mjs score.abc score.pdf --deps ./task-tools --chrome /path/to/chrome
```

Chrome/Chromium must be installed separately or supplied with `--chrome` / `CHROME`. Browser sandbox overrides should follow the host environment's permissions; `--no-sandbox` is an explicit option, not the default.

abcjs may set a fixed height/overflow on the rendering container. Moving its SVGs into page sections requires clearing those styles, otherwise the PDF can silently lose the end. Keep each system intact, reserve top space for overhanging notation and reject an oversized system instead of clipping it. The helper writes `score.render.json` with warnings and layout sizes; it does not replace visual proofreading.

```sh
pdfinfo score.pdf
pdftoppm -scale-to 1400 -png score.pdf preview
```

## Other editable formats

Use an available, maintained ABC-to-MusicXML converter, music21 or another existing notation tool. The companion scripts do not bundle a third-party converter. Inspect its license before redistributing it. In an existing repository, use the already-provided converter when suitable.

Validate MusicXML by walking measure cursors (including backup/forward), voices, divisions and ties, and comparing note onsets, durations and spelled pitches with the authored data. In polyphonic measures, summing every note's duration is incorrect. Export MIDI from the same corrected source; distinguish that playback MIDI from the independent audio-model MIDI.
