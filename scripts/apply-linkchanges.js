#!/usr/bin/env node
/* apply-linkchanges.js — ФІНАЛЬНИЙ прохід recheck-кампанії (локальний find-replace лінків):
   (1) застосувати накопичені зміни-лінків зі scripts/_recheck-linkchanges.json (кожен {from,to} —
       ПОВНА ціль лінка book:/guide:; міняємо лише як ЦІЛУ ціль у «](target)» / «](target#anchor)»,
       щоб не зачепити довші лінки-надмножини);
   (2) НОРМАЛІЗУВАТИ застарілий синтаксис детальної версії: будь-який лінк «…/<x>-d.md» → «…/detail»
       (нова єдина адреса детальної; рушій розуміє /detail і -d.md, але канон — /detail).
   Обидва — по всіх .md дерева root/.
   Запуск:  node scripts/apply-linkchanges.js           (dry-run)
            node scripts/apply-linkchanges.js --apply    (запис)   →   потім: node scripts/linkcheck.js */
"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const APPLY = process.argv.includes("--apply");
const SCRIPTS = path.join(ROOT, "scripts");
// усі per-book файли змін-лінків: _recheck-linkchanges.json + _recheck-linkchanges-<book>.json
const LINKFILES = fs.readdirSync(SCRIPTS).filter((f) => /^_recheck-linkchanges.*\.json$/.test(f)).map((f) => path.join(SCRIPTS, f));

let changes = [];
for (const lf of LINKFILES) {
  let arr;
  try { arr = JSON.parse(fs.readFileSync(lf, "utf8")); } catch (e) { console.error(`Битий JSON у ${path.basename(lf)}:`, e.message); process.exit(1); }
  if (!Array.isArray(arr)) { console.error(`Очікував масив {from,to} у ${path.basename(lf)}`); process.exit(1); }
  changes = changes.concat(arr);
}
if (!LINKFILES.length) console.log("(Нема файлів _recheck-linkchanges*.json — застосовуємо лише нормалізацію -d.md → /detail.)");
else console.log(`Файлів змін-лінків: ${LINKFILES.length} (${LINKFILES.map((f) => path.basename(f)).join(", ")})`);
// дедуп + відсів тотожних/порожніх
const seen = new Set();
changes = changes.filter((c) => c && c.from && c.to && c.from !== c.to && !seen.has(c.from + "→" + c.to) && seen.add(c.from + "→" + c.to));
console.log(`Змін-лінків із файлу: ${changes.length}`);

function esc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
// ціль саме як target у ](target) або ](target#anchor) — межа після from: «)» або «#»
const rules = changes.map((c) => ({ re: new RegExp("\\]\\(" + esc(c.from) + "([)#\\s])", "g"), from: c.from, to: c.to }));
// нормалізація: book:/guide: …/<останній-сегмент>-d.md → …/detail (межа: ) # або пробіл-перед-тайтлом)
const NORM_DETAIL = /\]\(((?:book|guide):[^)#\s]*)\/[^/)#\s]+-d\.md([)#\s])/g;

function walk(dir, out) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.isFile() && e.name.endsWith(".md")) out.push(p);
  }
  return out;
}
const files = walk(path.join(ROOT, "root"), []);

let ruleHits = 0, normHits = 0, filesChanged = 0;
const perRule = new Map();
for (const f of files) {
  const orig = fs.readFileSync(f, "utf8");
  let src = orig;
  for (const r of rules) src = src.replace(r.re, (m, tail) => { ruleHits++; perRule.set(r.from, (perRule.get(r.from) || 0) + 1); return "](" + r.to + tail; });
  src = src.replace(NORM_DETAIL, (m, pre, tail) => { normHits++; return "](" + pre + "/detail" + tail; });
  if (src !== orig) { filesChanged++; if (APPLY) fs.writeFileSync(f, src); }
}
if (changes.length) {
  console.log(`\nПер-зміна (скільки лінків знайдено):`);
  for (const c of changes) console.log(`  ${String(perRule.get(c.from) || 0).padStart(3)}×  ${c.from} → ${c.to}`);
  const zero = changes.filter((c) => !perRule.get(c.from));
  if (zero.length) console.log(`\n⚠️ ${zero.length} змін БЕЗ жодного збігу (лінк уже інший, або ціль ще не згадана) — перевір вручну.`);
}
console.log(`\nНормалізація «…-d.md → …/detail»: ${normHits} лінків.`);
console.log(`\n${APPLY ? "ЗАСТОСОВАНО" : "DRY-RUN (без запису; додай --apply)"}: ${ruleHits} змін-лінків + ${normHits} нормалізацій у ${filesChanged} файлах.${APPLY ? " Далі: node scripts/linkcheck.js" : ""}`);
