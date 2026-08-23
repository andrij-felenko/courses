/* Пара 9: rcu-mechanism (devices) → rcu-read-copy-update (processes).
   Проза двох статей майже дослівно однакова (різняться два речення) — злиття без втрат.
   Переїжджають лише 3 вставки й 1 унікальна фігура; проза-дубль лишається в git-історії. */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const R = path.resolve(__dirname, "../.."), APPLY = process.argv.includes("--apply");
const SRC = "reference/unix-linux/devices/rcu-mechanism";
const DST = "reference/unix-linux/processes/rcu-read-copy-update";
const MOVES = [
  [SRC + "/api-rcu-primitives.md",  DST + "/api-rcu-primitives.md"],
  [SRC + "/hist-rcu-lineage.md",    DST + "/hist-rcu-lineage.md"],
  [SRC + "/proj-rcu-list-module.md", DST + "/proj-rcu-list-module.md"],
  [SRC + "/img/module-unload.svg",  DST + "/img/module-unload.svg"],
];
const bad = [];
for (const [a, b] of MOVES) {
  if (!fs.existsSync(path.join(R, a))) bad.push("нема: " + a);
  if (fs.existsSync(path.join(R, b))) bad.push("зайнято: " + b);
}
if (bad.length) { console.error("СТОП:\n  " + bad.join("\n  ")); process.exit(1); }
console.log("передумови OK: " + MOVES.length + " файлів");
if (!APPLY) { MOVES.forEach(m => console.log("  " + m[0] + "  ->  " + m[1])); process.exit(0); }
for (const [a, b] of MOVES) {
  const r = cp.spawnSync("git", ["mv", a, b], { cwd: R, encoding: "utf8" });
  if (r.status !== 0) { console.error("СТОП git mv " + a + ": " + (r.stderr || "").trim()); process.exit(1); }
}
const OLD = "/reference/unix-linux/devices/rcu-mechanism/";
const NEW = "/reference/unix-linux/processes/rcu-read-copy-update/";
let f = 0;
for (const e of fs.readdirSync(path.join(R, DST))) {
  if (!e.endsWith(".md")) continue;
  const p = path.join(R, DST, e), s = fs.readFileSync(p, "utf8");
  if (s.indexOf(OLD) < 0) continue;
  fs.writeFileSync(p, s.split(OLD).join(NEW), "utf8"); f++;
}
console.log("перенесено " + MOVES.length + ", шляхів переписано у " + f + " файлах");
