#!/usr/bin/env node
/* ВСТАВКИ БАТЧУ — вхід для фази оцінки і застосування її результату.

   Ужиток:
     node scripts/antigravity/inserts.js --batch <файл> --list
     node scripts/antigravity/inserts.js --batch <файл> --apply <файл-із-рівнями>

   НАВІЩО ОКРЕМА ФАЗА. Тему оцінює агент, який її не писатиме, — інакше рівень стає
   зручним, а не чесним. Для вставок цього довго не було: рівень ставив сам письменник,
   бо до письма вставки не існує й оцінювати нема чого. Виходив рівно той конфлікт
   інтересів, який для тем прибрали свідомо.

   Момент, коли конфлікт знімається, є: щойно ВСІ письменники батчу відпрацювали, усі
   вставки лежать на диску з іменами. Тоді їх оцінює окремий агент — так само, як теми,
   і так само не той, хто писав. Аж ПІСЛЯ цього діють підлоги: спершу аналіз, потім межі.

   Письменник не оцінює нічого. Він пише й називає свої вставки у звіті — і все.

   Рівень вставки рівню теми НЕ дорівнює й від нього не залежить: у наріжної теми буває
   дотична історія, а у звичайної — несучий proj-, заради якого її й писали.            */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("../lib/manifest7.js");
const L = require("../checks/_lib.js");

const argv = process.argv.slice(2);
const val = (k) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : null; };
const has = (k) => argv.includes(`--${k}`);
const BATCH = val("batch");
if (!BATCH || (!has("list") && !val("apply"))) {
  console.error("Ужиток: node scripts/antigravity/inserts.js --batch <файл> --list | --apply <рівні.txt>");
  process.exit(L.USAGE);
}

let raw;
try { raw = JSON.parse(fs.readFileSync(BATCH, "utf8")); }
catch (e) { console.error(`не прочитати ${BATCH}: ${e.message}`); process.exit(3); }
const isArr = Array.isArray(raw);
const list = (isArr ? raw : (raw.topics || raw.units || [])).filter((x) => x && typeof x === "object" && x.dir);
if (!list.length) { console.error(`у ${BATCH} немає записів із "dir"`); process.exit(3); }

/* назви тем — з маніфесту, щоб оцінювач бачив, ЧОГО ця вставка стосується */
const titleOf = (dir) => {
  const bd = M7.bookDirOfTopic(path.resolve(L.ROOT, dir));
  if (!bd) return "";
  const b = M7.loadBook(bd); if (!b) return "";
  const t = M7.findTopic(b, path.basename(dir));
  return t ? t.title : "";
};
const h1 = (p) => { const m = L.read(p).match(/^#\s+(.+)$/m); return m ? m[1].trim() : ""; };

const rows = [];
for (const x of list) {
  const dir = path.resolve(L.ROOT, x.dir);
  let files = [];
  try { files = fs.readdirSync(dir).filter((f) => f.endsWith(".md")); } catch { continue; }
  const slug = path.basename(dir);
  for (const f of files.sort()) {
    const kind = L.classify(f, slug);
    if (!L.INSERT_TYPES.includes(kind)) continue;
    rows.push({ dir: x.dir, entry: x, slug, title: titleOf(x.dir), file: f, kind,
                words: L.proseWords(L.read(path.join(dir, f))), h1: h1(path.join(dir, f)),
                level: (x.inserts || {})[f] || null });
  }
}
if (!rows.length) { console.log("у темах батчу немає вставок — фаза оцінки вставок не потрібна"); process.exit(0); }

/* ── --list: вхід для оцінювача ───────────────────────────────────────────── */
if (has("list")) {
  console.log(`# ВСТАВКИ БАТЧУ ${path.basename(BATCH)} — ${rows.length} файлів\n`);
  let cur = "";
  for (const r of rows) {
    if (r.slug !== cur) { cur = r.slug; console.log(`\n## тема: ${r.title || r.slug}  (${r.slug})`); }
    console.log(`   ${r.file} | ${L.KIND_LABEL[r.kind]} | ${r.h1}`);
  }
  console.log(`\n(файлів рівно ${rows.length})`);
  process.exit(0);
}

/* ── --apply: рівні з файлу «<файл>.md=N» у батч-файл ──────────────────────── */
const src = val("apply");
let txt;
try { txt = fs.readFileSync(src, "utf8"); }
catch (e) { console.error(`не прочитати ${src}: ${e.message}`); process.exit(3); }
const got = new Map();
for (const line of txt.split(/\r?\n/)) {
  const m = line.trim().match(/^([^\s=|]+\.md)\s*=\s*([1-5])\s*$/);
  if (m) got.set(m[1], Number(m[2]));
}
let set = 0; const missing = [];
for (const r of rows) {
  const lv = got.get(r.file);
  if (!lv) { missing.push(`${r.dir}/${r.file}`); continue; }
  r.entry.inserts = r.entry.inserts || {};
  r.entry.inserts[r.file] = lv; set++;
}
fs.writeFileSync(BATCH, JSON.stringify(raw, null, 2), "utf8");
console.log(`\nпроставлено рівнів: ${set} з ${rows.length}`);
const hist = [1, 2, 3, 4, 5].map((n) => rows.filter((r) => got.get(r.file) === n).length);
hist.forEach((c, i) => console.log(`  Р${i + 1}  ${String(c).padStart(3)}  ${"█".repeat(c)}`));
const vals = rows.map((r) => got.get(r.file)).filter(Boolean);
if (vals.length) console.log(`  середня ${(vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2)}`);
if (missing.length) {
  console.log(`\n✖ БЕЗ РІВНЯ ${missing.length}:`);
  missing.slice(0, 15).forEach((m) => console.log(`    ${m}`));
  console.log(`\nОцінка неповна — пусти фазу оцінки вставок наново на ВЕСЬ список.`);
  process.exit(1);
}
console.log(`\nдалі: node scripts/antigravity/assess-gate.js --batch ${BATCH} --inserts`);
