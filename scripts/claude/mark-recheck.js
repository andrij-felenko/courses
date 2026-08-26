#!/usr/bin/env node
/* ⚠️ ЛЕГАСІ КАМПАНІЇ RECHECK (завершена 2026-07-25). Читає ПРИБРАНЕ дерево v6
   (book/ + guide/ + catalog/ + manifest.js із window.__BOOKS__), тож на дереві v7
   не працює — не запускай, доки не переписано. Живий конвеєр ревізії сьогодні:
   review-batch.js → review-queue.js → review-apply.js. */
/* ============================================================================
   mark-recheck.js — позначити написані версії статусом `recheck`.

   `recheck` (AUTHORING §9) = «передивитися за чинними правилами й привести у
   відповідність». Скрипт масово переводить `done` → `recheck`, коли канон
   змінився й корпус треба перечитати.

   ЩО ЗМІНИЛОСЯ. Раніше він різав ТЕКСТ `.js`-маніфесту регуляркою по
   `basic:{status:"done"}`. У v7 маніфест — JSON, і правка йде операціями через
   `scripts/lib/manifest7.js`: те саме, але без ризику зіпсувати файл.

   Ужиток:  node scripts/claude/mark-recheck.js                (звіт по всіх книгах)
            node scripts/claude/mark-recheck.js --apply
            node scripts/claude/mark-recheck.js --book sf-apps --apply
   ========================================================================== */
"use strict";
const path = require("path");
const M = require("../lib/manifest7.js");

const argv = process.argv.slice(2);
const APPLY = argv.includes("--apply");
const val = (n) => { const i = argv.indexOf("--" + n); return i >= 0 ? argv[i + 1] : null; };
const ONLY = val("book");

let books = 0, hits = 0, changed = 0;
for (const [bslug, meta] of M.books()) {
  if (ONLY && bslug !== ONLY) continue;
  const bk = M.loadBook(meta.bookDir);
  if (!bk) continue;
  books++;

  const ops = [];
  for (const t of M.allTopics(bk)) {
    if (!t.own) continue;
    for (const ver of ["basic", "detailed"]) {
      const st = (t.node[ver] && t.node[ver].status) || "empty";
      if (st === "done") ops.push({ op: "status", slug: t.slug, ver, status: "recheck" });
    }
  }
  if (!ops.length) continue;
  hits += ops.length;
  const rep = M.applyOps(meta.bookDir, ops, { dry: !APPLY });
  changed += rep.status || 0;
  console.log(`  ${bslug.padEnd(22)} done→recheck: ${String(ops.length).padStart(4)}${(rep.errors || []).length ? "   ✖ помилок " + rep.errors.length : ""}`);
  (rep.errors || []).forEach((e) => console.error(`     ✖ ${e}`));
}

console.log(`\n${APPLY ? "ЗАСТОСОВАНО" : "ЗВІТ (нічого не записано)"} · книг ${books} · версій ${hits}`);
if (!APPLY && hits) console.log(`Щоб записати: node scripts/claude/mark-recheck.js${ONLY ? " --book " + ONLY : ""} --apply`);
