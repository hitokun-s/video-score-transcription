#!/usr/bin/env node
// Dependencies resolve from --deps or the caller's cwd, not from the installed skill.
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const args = process.argv.slice(2);
if (args.includes("--help") || args.length < 2) {
  console.log(
    "Usage: node render-abc.mjs INPUT.abc OUTPUT.pdf [--deps DIR] [--chrome PATH] [--no-sandbox]\nRequires abcjs and playwright-core in DIR (default cwd), plus Chrome/Chromium.",
  );
  process.exit(args.includes("--help") ? 0 : 1);
}
const [input, output, ...options] = args;
let deps = process.cwd(),
  chrome = process.env.CHROME,
  noSandbox = false;
for (let i = 0; i < options.length; i++) {
  if (options[i] === "--no-sandbox") noSandbox = true;
  else if (["--deps", "--chrome"].includes(options[i]) && options[i + 1]) {
    const value = options[++i];
    if (options[i - 1] === "--deps") deps = value;
    else chrome = value;
  } else throw new Error(`Unknown/incomplete option: ${options[i]}`);
}
const require = createRequire(path.join(path.resolve(deps), "package.json"));
const { chromium } = require("playwright-core");
const js = fs.readFileSync(
  require.resolve("abcjs/dist/abcjs-basic-min.js"),
  "utf8",
);
const abc = fs.readFileSync(input, "utf8");
if (!chrome)
  chrome = [
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
  ].find((p) => fs.existsSync(p));
fs.mkdirSync(path.dirname(path.resolve(output)), { recursive: true });
const browser = await chromium.launch({
  ...(chrome ? { executablePath: chrome } : {}),
  args: noSandbox ? ["--no-sandbox"] : [],
});
try {
  const page = await browser.newPage();
  await page.setContent(
    '<html><head><meta charset="utf-8"><style>@page{size:A4;margin:12mm 10mm}body{margin:0}.sheet{break-after:page;padding-top:24px}.sheet:last-child{break-after:auto}svg{display:block;overflow:visible}</style></head><body><div id="paper"></div></body></html>',
  );
  await page.addScriptTag({ content: js });
  const report = await page.evaluate((abc) => {
    const tunes = ABCJS.renderAbc("paper", abc, {
      staffwidth: 700,
      oneSvgPerLine: true,
      paddingtop: 8,
      paddingbottom: 12,
    });
    const noteCount = tunes.reduce(
      (sum, t) =>
        sum +
        t.lines.reduce(
          (n, l) =>
            n +
            (l.staff || []).reduce(
              (m, s) =>
                m +
                s.voices
                  .flat()
                  .filter((e) => e.el_type === "note" && e.pitches?.length)
                  .length,
              0,
            ),
          0,
        ),
      0,
    );
    if (!noteCount)
      throw new Error(
        "No pitched notes rendered; check ABC structure and blank lines.",
      );
    const root = document.querySelector("#paper"),
      svgs = [...root.querySelectorAll("svg")];
    const sizes = svgs.map((svg) => ({
      height: svg.getBoundingClientRect().height,
      label: svg.getAttribute("aria-label"),
    }));
    root.replaceChildren();
    root.removeAttribute("style");
    root.removeAttribute("class");
    root.style.overflow = "visible";
    let sheet,
      used = Infinity;
    for (const [i, svg] of svgs.entries()) {
      const h = sizes[i].height;
      if (h + 24 > 990)
        throw new Error(
          "A score system exceeds the printable height; split or rescale it.",
        );
      if (used + h > 990) {
        sheet = document.createElement("div");
        sheet.className = "sheet";
        root.append(sheet);
        used = 24;
      }
      sheet.append(svg);
      used += h;
    }
    return {
      warnings: tunes.flatMap((t) => t.warnings || []),
      note_events: noteCount,
      sizes,
      pages: root.children.length,
    };
  }, abc);
  await page.pdf({
    path: output,
    preferCSSPageSize: true,
    printBackground: true,
  });
  const reportPath = output.replace(/\.pdf$/i, "") + ".render.json";
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
  console.log(
    `${output}: ${report.pages} page sections, ${report.note_events} note events, ${report.warnings.length} warnings; ${reportPath}`,
  );
} finally {
  await browser.close();
}
