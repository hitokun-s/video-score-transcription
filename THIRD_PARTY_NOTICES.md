# Third-party notices

The repository's original instructions, helper scripts, test generators and configuration are licensed under MIT; see [LICENSE](LICENSE).

## Installed dependencies

Dependencies are installed separately. Their source, binaries and license texts are not vendored in this repository. `package-lock.json` records the Node dependency graph; each installed package includes its applicable license and notices.

| Component                                                  | Purpose                                           | License / terms                                |
| ---------------------------------------------------------- | ------------------------------------------------- | ---------------------------------------------- |
| [abcjs](https://github.com/paulrosen/abcjs)                | Render ABC notation                               | MIT                                            |
| [playwright-core](https://github.com/microsoft/playwright) | Control the browser for PDF export                | Apache-2.0                                     |
| [ESLint](https://github.com/eslint/eslint), @eslint/js     | JavaScript linting                                | MIT                                            |
| [Prettier](https://github.com/prettier/prettier)           | JavaScript, Markdown and configuration formatting | MIT                                            |
| [globals](https://github.com/sindresorhus/globals)         | ESLint environment definitions                    | MIT                                            |
| [Ruff](https://github.com/astral-sh/ruff)                  | Python linting and formatting                     | MIT                                            |
| [Pillow](https://github.com/python-pillow/Pillow)          | Contact sheets                                    | HPND; see the installed distribution's LICENSE |

## External tools and optional models

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) is an external downloader. Its source uses the Unlicense; distribution bundles can contain separately licensed components.
- [FFmpeg](https://ffmpeg.org/legal.html) is invoked as an external executable. Its license depends on the build and enabled components; consult the binary's build configuration and upstream licensing information.
- Chrome/Chromium is supplied by the user or execution environment, under the selected browser distribution's terms.
- [ByteDance piano_transcription](https://github.com/bytedance/piano_transcription) and [piano_transcription_inference](https://github.com/qiuqiangkong/piano_transcription_inference) are optional audio-analysis integrations. Neither implementation nor model weights are included. Check the upstream package and the specific checkpoint's license before use or redistribution; this project's MIT license does not license them.
- MusicXML converters and alternative engravers are selected separately by the user or agent. No third-party converter is bundled.

## Input media and generated results

The project's MIT license covers its original software and documentation, not third-party recordings, compositions, sheet music, or rights in their transcriptions. Users must have the necessary rights for their intended use and any sharing of source media or output scores.

Tests generate synthetic test-pattern video and original scale exercises at runtime. The repository contains no downloaded performance media or third-party score fixtures.

Related-project links are acknowledgments, not endorsements. No code from those projects is incorporated into the helper scripts.
