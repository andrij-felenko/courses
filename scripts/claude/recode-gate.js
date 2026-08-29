#!/usr/bin/env node
/* Гейт переписаного коду: чи став код справжнім проєктом.
   Ужиток: node scripts/claude/recode-gate.js --batch scripts/_finish/_recode-<книга>.json
           node scripts/claude/recode-gate.js --batch … --ops        # операції для manifest-patch
           node scripts/claude/recode-gate.js --batch … --json       # машинний звіт

   Судить ТРИ речі, і всі три — механічні:
     1. код виїхав з огорож у теки мов;
     2. кожна мова дотягла до підлоги свого рівня (скрипти підлоги не мають);
     3. є тека `c/` — є й `cpp/` (§5), бо пара мов перевіряється наявністю теки,
        а не збігом імен файлів: ідіоматичний C++ ділиться на модулі інакше.

   ⛔ Підлоги НЕ показуються письменникові — ні в завданні, ні в доборі. Показане
   число стає ціллю: заміряно двічі, в обидва боки (див. _lib.js). Тому гейт каже
   «тонко, розшир», а не «допиши 180 рядків». Числа тут — для людини й для звіту.  */
"use strict";
const fs = require("fs");
const path = require("path");
const L = require("../checks/_lib.js");

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const has = (k) => argv.includes(k);

const BATCH = arg("--batch", "");
if (!BATCH) { console.error("треба --batch <файл черги>"); process.exit(2); }
let units = [];
try { units = JSON.parse(fs.readFileSync(BATCH, "utf8")); }
catch (e) { console.error("не читається черга: " + e.message); process.exit(2); }

const FENCE = /^\s*```(.*)$/;
/* Скільки коду справжньою мовою ЩЕ лишилося в огорожах (блоки ≥ EXTRACT_MIN). */
const fencedLeft = L.fencedCodeLeft;   /* одна функція на гейт і на 06-ту */

const rows = [];
for (const u of units) {
  const p = path.join(u.dir, u.file);
  const md = fs.existsSync(p) ? L.read(p) : "";
  const dirs = L.langDirsOf(u.dir, u.file).map((d) => Object.assign({}, d, L.codeLinesOfDir(d.dir)));
  const left = fencedLeft(md);
  const has_c = dirs.some((d) => d.lang === "c");
  const has_cpp = dirs.some((d) => d.lang === "cpp");

  const thin = [];
  for (const d of dirs) {
    const floor = L.codeFloorFor(d.tier, u.level);
    if (floor && d.lines < floor) thin.push({ lang: d.lang, lines: d.lines, floor });
  }

  const problems = [];
  /* Нема коду взагалі — нема й боргу: файл із самою прозою тека проєкту не потрібна. */
  if (left && !dirs.length) problems.push(`код не виїхав з огорож: ${left} рядків, теки проєкту немає`);
  else if (left) problems.push(`код дубльовано: ${left} рядків лишилося в огорожах ПОРУЧ із теками проєкту`);
  if (has_c && !has_cpp) problems.push("є тека c/, немає cpp/ — §5 вимагає пари");
  for (const t of thin) problems.push(`мова ${t.lang}: тонко`);

  rows.push({
    dir: u.dir, file: u.file, slug: u.slug, level: u.level || null,
    ver: u.ver || null, type: u.type || null, status: u.status || "",
    langs: dirs.map((d) => ({ lang: d.lang, tier: d.tier, lines: d.lines, files: d.files, tests: d.tests })),
    fencedLeft: left, thin, problems, ok: problems.length === 0,
  });
}

/* ── операції для manifest-patch: знімаємо recode лише з тих, хто пройшов ──── */
if (has("--ops")) {
  const ops = [];
  for (const r of rows) {
    if (!r.ok || !r.status) continue;
    if (r.ver) ops.push({ op: "status", slug: r.slug, ver: r.ver, status: r.status, recode: false });
    else if (r.type) ops.push({ op: "insert", slug: r.slug, type: r.type, file: r.file, status: r.status, recode: false });
  }
  console.log(JSON.stringify(ops, null, 1));
  process.exit(0);
}

if (has("--json")) { console.log(JSON.stringify({ total: rows.length, ok: rows.filter((r) => r.ok).length, rows }, null, 1)); process.exit(rows.some((r) => !r.ok) ? 1 : 0); }

/* ── людський звіт ────────────────────────────────────────────────────────── */
const ok = rows.filter((r) => r.ok).length;
console.log(`\n=== ГЕЙТ ПЕРЕПИСАНОГО КОДУ === ${ok} з ${rows.length} готові\n`);
for (const r of rows) {
  const mark = r.ok ? "✓" : "✖";
  const lv = r.level ? `Р${r.level}` : "Р?";
  console.log(`  ${mark} ${lv}  ${r.slug}/${r.file}`);
  for (const l of r.langs) {
    const floor = L.codeFloorFor(l.tier, r.level);
    const v = !floor ? "скрипт" : (l.lines >= floor ? "✓" : `тонко (${l.lines}/${floor})`);
    console.log(`        ${l.lang.padEnd(8)} ${String(l.lines).padStart(5)} рядків у ${l.files} файлах${l.tests ? `, тестів ${l.tests}` : ""}   ${v}`);
  }
  for (const p of r.problems) console.log(`        ← ${p}`);
}
const bad = rows.filter((r) => !r.ok);
if (bad.length) {
  console.log(`\nне готові: ${bad.length}`);
  console.log("добір: «тонко» → показати сам МЕХАНІЗМ, який назвала проза (те, що згорнуто в заглушку);");
  console.log("«завелико» → ВИКИНУТИ те, що механізму не показує: шари на майбутнє, конфігурованість,");
  console.log("оборонні гілки поза предметом, файли без межі в тексті. ⛔ Не називай чисел.");
  process.exit(1);
}
console.log("\nусі готові — можна знімати recode: node scripts/claude/recode-gate.js --batch … --ops");
