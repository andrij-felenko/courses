#!/usr/bin/env node
/* ============================================================================
   retarget-books.js — привести короткі лінки прози до правила v7 §2.

   ЩО СТАЛОСЯ. Перенос у `root/` перейменував книги: `electronics` розпалася на
   `hw-analog`/`hw-components`/`hw-digital`/`hw-power`, `physics` на `ph-*`,
   `programming` на `sf-*`, `unix-linux` став `sys-unix`. Проза лишилася зі старими
   слугами, і перший сегмент лінка почав називати книгу, якої немає в природі.

   ЧОМУ МАПУ НЕ ТРЕБА ВИГАДУВАТИ. Слуг теми унікальний по корпусу (6410 із 6420),
   тож де тема живе тепер — знає сам корпус: `manifest7.allSlugsInCorpus()`.

   ЩО РОБИТЬ. Перезаписує ПЕРШИЙ сегмент на справжню книгу й заразом зводить лінк
   до канонної форми §2 — `root:<книга>/<тема>[/<файл>.md | /detail | /basic]`.
   Тим самим зникає й давніший борг: ~2000 лінків із зайвим сегментом галузі
   (`root:algorithms/complexity-computability/ac0-circuits/…`).

   ДЕ ОБЕРЕЖНО. Десять слугів живуть у двох книгах (майже все — власна стаття курсу
   поряд з атомом книги, що канон дозволяє). Для них: якщо книга з лінка серед
   кандидатів — не чіпаємо взагалі; якщо ні — лишаємо як є й друкуємо.

   Ужиток:  node scripts/retarget-books.js           (звіт, нічого не пише)
            node scripts/retarget-books.js --apply
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const M = require("./lib/manifest7.js");

const APPLY = process.argv.includes("--apply");
const TAIL_WORDS = new Set(["detail", "basic"]);

/* слуг → усі книги, де він є (не лише перша) */
const where = new Map();
for (const [bslug, meta] of M.books()) {
  const bk = M.loadBook(meta.bookDir);
  if (!bk) continue;
  for (const t of M.allTopics(bk)) {
    if (!t.own) continue;
    if (!where.has(t.slug)) where.set(t.slug, []);
    where.get(t.slug).push(bslug);
  }
}

let files = 0, touched = 0;
let ok = 0, fixed = 0, ambiguous = 0, gone = 0;
const goneSlugs = new Map(), ambigSlugs = new Map(), pairs = new Map();

function retarget(m, body) {
  const hash = body.indexOf("#");
  const frag = hash >= 0 ? body.slice(hash) : "";
  const core = hash >= 0 ? body.slice(0, hash) : body;
  const segs = core.split("/").filter(Boolean);
  if (segs.length < 2) return m;

  const last = segs[segs.length - 1];
  const hasTail = last.endsWith(".md") || TAIL_WORDS.has(last);
  const slug = hasTail ? segs[segs.length - 2] : last;
  const tail = hasTail ? "/" + last : "";
  const named = segs[0];
  if (!slug) return m;

  const cands = where.get(slug);
  if (!cands) { gone++; goneSlugs.set(slug, (goneSlugs.get(slug) || 0) + 1); return m; }

  let real;
  if (cands.length > 1) {
    if (cands.includes(named)) { ok++; return m; }        // книга з лінка й так вірна
    /* Слуг у двох книгах — майже завжди це власна стаття КУРСУ поряд з атомом книги
       (канон дозволяє). Лінк у прозі, що назвав книгу, мав на увазі атом, а не крок
       курсу, тож беремо не-курс. Якщо ж обидва кандидати — книги, не вгадуємо. */
    const nonCourse = cands.filter((c) => (M.books().get(c) || {}).kind !== "course");
    if (nonCourse.length !== 1) { ambiguous++; ambigSlugs.set(slug, cands.join(" · ")); return m; }
    real = nonCourse[0];
  } else real = cands[0];
  const want = `](root:${real}/${slug}${tail}${frag})`;
  if (m === want) { ok++; return m; }
  fixed++;
  if (named !== real) pairs.set(`${named} → ${real}`, (pairs.get(`${named} → ${real}`) || 0) + 1);
  return want;
}

function walk(d) {
  let e; try { e = fs.readdirSync(d, { withFileTypes: true }) } catch { return }
  for (const x of e) {
    const p = path.join(d, x.name);
    if (x.isDirectory()) { if (x.name === "img" || x.name === ".git") continue; walk(p); continue }
    if (!x.name.endsWith(".md")) continue;
    files++;
    const src = fs.readFileSync(p, "utf8");
    const out = src.replace(/\]\(root:([^)\s]+)\)/g, (m, body) => retarget(m, body));
    if (out === src) continue;
    touched++;
    if (APPLY) { fs.writeFileSync(p + ".tmp", out); fs.renameSync(p + ".tmp", p) }
  }
}
walk(path.join(M.ROOT, "root"));

console.log(`${APPLY ? "ЗАСТОСОВАНО" : "ЗВІТ (нічого не записано)"} · .md переглянуто ${files}, змінено ${touched}`);
console.log(`  ✔ уже правильні:        ${ok}`);
console.log(`  ↻ перецілено:           ${fixed}`);
console.log(`  ~ неоднозначні (слуг у двох книгах, книга з лінка не збіглася): ${ambiguous}`);
console.log(`  ✖ теми немає ніде:      ${gone}`);
if (pairs.size) {
  console.log(`\nнайчастіші перейменування:`);
  [...pairs.entries()].sort((a, b) => b[1] - a[1]).slice(0, 12).forEach(([k, v]) => console.log(`   ${String(v).padStart(6)}  ${k}`));
}
if (ambigSlugs.size) {
  console.log(`\nнеоднозначні слуги (лишені як є):`);
  [...ambigSlugs.entries()].forEach(([s, b]) => console.log(`   ~ ${s}  →  ${b}`));
}
if (goneSlugs.size) {
  console.log(`\nтеми, яких немає ніде (${goneSlugs.size} слугів, ${gone} лінків) — лишені як є:`);
  [...goneSlugs.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15).forEach(([s, n]) => console.log(`   ✖ ${String(n).padStart(4)}  ${s}`));
}
if (!APPLY) console.log(`\nЩоб записати: node scripts/retarget-books.js --apply`);
