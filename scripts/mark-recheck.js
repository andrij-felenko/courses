#!/usr/bin/env node
/* mark-recheck.js — одноразова міграція: усі DONE-версії статей (basic/detailed) у маніфестах
   book/ · catalog/ · guide/ → status "recheck" (черга recheck-кампанії).
   Вставки НЕ чіпає (у них об'єкт {file,status} — префікс не basic/detailed).
   Тільки "done" → "recheck"; pending/empty/update/deeper — не чіпає.
   Запуск:  node scripts/mark-recheck.js            (dry-run: лише лічить)
            node scripts/mark-recheck.js --apply     (застосувати запис) */
"use strict";
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
const APPLY = process.argv.includes("--apply");

function manifests() {
  const out = [];
  for (const kind of ["book", "catalog", "reference", "guide"]) {
    const base = path.join(ROOT, kind);
    if (!fs.existsSync(base)) continue;
    for (const d of fs.readdirSync(base)) {
      const mf = path.join(base, d, "manifest.js");
      if (fs.existsSync(mf)) out.push(mf);
    }
  }
  return out;
}

// ТІЛЬКИ версії basic/detailed (об'єкт лише зі status); вставки {file:"…",status:"done"} — не матчаться (перед { стоїть не basic/detailed)
const RE = /((?:basic|detailed)\s*:\s*\{\s*status\s*:\s*)"done"(\s*\})/g;

let totalFiles = 0, totalHits = 0;
for (const mf of manifests()) {
  const src = fs.readFileSync(mf, "utf8");
  let hits = 0;
  const out = src.replace(RE, (m, a, b) => { hits++; return a + '"recheck"' + b; });
  if (hits) {
    totalFiles++; totalHits += hits;
    console.log(`${APPLY ? "✎" : "•"} ${path.relative(ROOT, mf).replace(/\\/g, "/")}: ${hits} версій done→recheck`);
    if (APPLY) fs.writeFileSync(mf, out);
  }
}
console.log(`\n${APPLY ? "ЗАСТОСОВАНО" : "DRY-RUN (без запису; додай --apply)"}: ${totalHits} версій у ${totalFiles} маніфестах`);
