/* scripts/migrate/move-chemistry.js — кроки 5–6: перенос тек + збереження шляхів.
   Дефолт — суха прогонка. Реальний перенос: --apply
     1) git mv book/chemistry/<секція>/<тема>  →  course/basic-chemistry/<тема>
     2) у перенесених .md: /book/chemistry/<секція>/<тема>/  →  /course/basic-chemistry/<тема>/
     3) по ВСЬОМУ корпусу: ](book:chemistry/…/<slug>)  →  ](root:basic-chemistry/<slug>)   (2 і 3 сегменти)
   Тег ідентичності — окремим прапорцем --tag (поки не чіпаємо рідер). */
const fs = require("fs"), path = require("path"), cp = require("child_process");
const R = path.resolve(__dirname, "../..");
const APPLY = process.argv.includes("--apply"), TAG = process.argv.includes("--tag");
const moves = JSON.parse(fs.readFileSync(path.join(__dirname, "moves-chemistry.json"), "utf8"));

/* ---- 0. передумови ---- */
const bad = [];
for (const m of moves) {
  if (!fs.existsSync(path.join(R, m.from))) bad.push("нема джерела: " + m.from);
  if (fs.existsSync(path.join(R, m.to))) bad.push("ціль уже існує: " + m.to);
}
if (bad.length) { console.error("✖ ПЕРЕДУМОВИ НЕ ВИКОНАНІ:\n  " + bad.join("\n  ")); process.exit(1); }
console.log("✓ передумови: " + moves.length + " джерел на місці, жодної цілі не зайнято");

/* ---- допоміжне: усі .md корпусу (без .git, node_modules і КОПІЙ РЕПО у .claude/worktrees) ---- */
const SKIP = new Set([".git", "node_modules", ".claude", ".github"]);
function walk(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) { if (!SKIP.has(e.name)) walk(p, out); }
    else if (e.name.endsWith(".md")) out.push(p);
  }
  return out;
}

if (!APPLY) {
  console.log("\n-- СУХА ПРОГОНКА (додай --apply, щоб виконати) --");
  moves.slice(0, 3).forEach(m => console.log("  git mv " + m.from + "  →  " + m.to));
  console.log("  … і ще " + (moves.length - 3));
  let img = 0;
  for (const m of moves) for (const f of walk(path.join(R, m.from), []))
    img += (fs.readFileSync(f, "utf8").match(new RegExp("/book/chemistry/[a-z0-9-]+/" + m.slug + "/", "g")) || []).length;
  const all = walk(R, []); let lk = 0, lf = 0;
  for (const f of all) {
    const n = (fs.readFileSync(f, "utf8").match(/\]\(book:chemistry\/[^)]+\)/g) || []).length;
    if (n) { lk += n; lf++; }
  }
  console.log("\n  img-шляхів на правку:   " + img);
  console.log("  book:-лінків на правку: " + lk + "  у " + lf + " файлах");
  process.exit(0);
}

/* ---- 1. перенос ---- */
fs.mkdirSync(path.join(R, "course/basic-chemistry"), { recursive: true });
for (const m of moves) {
  const r = cp.spawnSync("git", ["mv", m.from, m.to], { cwd: R, encoding: "utf8" });
  if (r.status !== 0) { console.error("✖ git mv " + m.from + ": " + (r.stderr || "").trim()); process.exit(1); }
}
console.log("✓ перенесено тек: " + moves.length);

/* ---- 2. img-шляхи в перенесених файлах ---- */
let nImg = 0, fImg = 0;
for (const m of moves) for (const f of walk(path.join(R, m.to), [])) {
  const src = fs.readFileSync(f, "utf8");
  const re = new RegExp("/book/chemistry/[a-z0-9-]+/" + m.slug + "/", "g");
  const hit = (src.match(re) || []).length;
  if (!hit) continue;
  fs.writeFileSync(f, src.replace(re, "/course/basic-chemistry/" + m.slug + "/"), "utf8");
  nImg += hit; fImg++;
}
console.log("✓ img-шляхів переписано: " + nImg + "  у " + fImg + " файлах");

/* ---- 3. book:-лінки по всьому корпусу (2 і 3 сегменти → канонічна коротка форма) ---- */
let nLk = 0, fLk = 0;
for (const f of walk(R, [])) {
  const src = fs.readFileSync(f, "utf8");
  let hit = 0;
  const out = src.replace(/\]\(book:chemistry\/([a-z0-9\/-]+)\)/g, (_, tail) => {
    hit++; return "](root:basic-chemistry/" + tail.split("/").pop() + ")";
  });
  if (!hit) continue;
  fs.writeFileSync(f, out, "utf8"); nLk += hit; fLk++;
}
console.log("✓ лінків переписано: " + nLk + "  у " + fLk + " файлах");

/* ---- 4. тег ідентичності (опційно) ---- */
if (TAG) {
  let n = 0;
  for (const m of moves) for (const f of walk(path.join(R, m.to), [])) {
    const src = fs.readFileSync(f, "utf8");
    if (src.startsWith("<!-- id:")) continue;
    fs.writeFileSync(f, "<!-- id: basic-chemistry/" + m.slug + " -->\n" + src, "utf8"); n++;
  }
  console.log("✓ тегів ідентичності додано: " + n);
}
console.log("\nДалі: node scripts/linkcheck.js  ·  python scripts/svgcheck.py course/basic-chemistry --links");
