/* Злиття «Фігури Ліссажу»: lissajous (базова) + lissajous-figures (детальна) → одна тема lissajous.
   Нічого не видаляє: усі файли переїжджають. Колізія фігури ratio-gallery.svg — перейменування.
   Суха прогонка за замовчуванням; застосувати: --apply */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const R = path.resolve(__dirname, "../..");
const APPLY = process.argv.includes("--apply");
const SEC = "book/physics/oscillations-waves";
const SRC = SEC + "/lissajous-figures", DST = SEC + "/lissajous";

const MOVES = [
  [SRC + "/lissajous-figures-d.md",   DST + "/lissajous-d.md"],
  [SRC + "/api-oscilloscope-xy.md",   DST + "/api-oscilloscope-xy.md"],
  [SRC + "/hist-lissajous-bowditch.md", DST + "/hist-lissajous-bowditch.md"],
  [SRC + "/math-lissajous-geometry.md", DST + "/math-lissajous-geometry.md"],
  [SRC + "/proj-lissajous-scope.md",  DST + "/proj-lissajous-scope.md"],
  [SRC + "/figs.py",                  DST + "/figs-detailed.py"],
  [SRC + "/img/lissajous-pendulum-light.svg", DST + "/img/lissajous-pendulum-light.svg"],
  [SRC + "/img/phase-ellipse-gallery.svg",    DST + "/img/phase-ellipse-gallery.svg"],
  [SRC + "/img/phase-measurement.svg",        DST + "/img/phase-measurement.svg"],
  [SRC + "/img/xy-mode-concept.svg",          DST + "/img/xy-mode-concept.svg"],
  [SRC + "/img/ratio-gallery.svg",            DST + "/img/ratio-gallery-xy.svg"],   // колізія імені
];

let bad = [];
for (const [a, b] of MOVES) {
  if (!fs.existsSync(path.join(R, a))) bad.push("нема джерела: " + a);
  if (fs.existsSync(path.join(R, b))) bad.push("ціль зайнята: " + b);
}
if (bad.length) { console.error("СТОП:\n  " + bad.join("\n  ")); process.exit(1); }
console.log("передумови OK: " + MOVES.length + " файлів, жодної зайнятої цілі");

if (!APPLY) { MOVES.forEach(function (m) { console.log("  " + m[0] + "  ->  " + m[1]) });
  console.log("\n(суха прогонка; --apply щоб виконати)"); process.exit(0); }

for (const [a, b] of MOVES) {
  const r = cp.spawnSync("git", ["mv", a, b], { cwd: R, encoding: "utf8" });
  if (r.status !== 0) { console.error("СТОП git mv " + a + ": " + (r.stderr || "").trim()); process.exit(1); }
}
console.log("перенесено: " + MOVES.length);

/* шляхи всередині перенесених .md і в figs-detailed.py */
const OLD = "/book/physics/oscillations-waves/lissajous-figures/img/";
const NEW = "/book/physics/oscillations-waves/lissajous/img/";
let n = 0, f = 0;
for (const e of fs.readdirSync(path.join(R, DST))) {
  if (!e.endsWith(".md") && !e.endsWith(".py")) continue;
  const p = path.join(R, DST, e);
  let s = fs.readFileSync(p, "utf8"), before = s;
  s = s.split(OLD).join(NEW);
  s = s.split(NEW + "ratio-gallery.svg").join(NEW + "ratio-gallery-xy.svg");
  if (e === "figs-detailed.py") s = s.split('"ratio-gallery.svg"').join('"ratio-gallery-xy.svg"');
  if (s === before) continue;
  fs.writeFileSync(p, s, "utf8"); f++;
  n += before.split(OLD).length - 1;
}
console.log("шляхів переписано у " + f + " файлах");
const left = fs.existsSync(path.join(R, SRC)) ? fs.readdirSync(path.join(R, SRC)) : [];
console.log("лишилось у " + SRC + ": " + (left.length ? left.join(", ") : "порожньо"));
