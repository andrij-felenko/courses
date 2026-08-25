#!/usr/bin/env node
/* ============================================================================
   drop-todo-flags.js — прибрати `todo` й `hint` із кроків курсів.

   ЩО ЦЕ БУЛО. Поки курси проєктували, крок-`ref` міг вести на тему, якої ще не
   існувало. Такий крок помічали двома полями: `todo:"нова тема"` і `hint` —
   здогад, куди тему класти, у СТАРОМУ словнику (`electronics/signals`).

   ЧОМУ ЙДУТЬ. Записку виконали: усі теми заведено в книгах нового дерева зі
   своїми адресою й статусом. `hint` до того ж показує на книги, яких більше
   немає взагалі. Канон (§9) називає обидва поля знятими: канонний крок — це
   рівно `{ref, title}`, і власного статусу він не має — статус живе на ТЕМІ.

   ГЕЙТ. Поле знімається лише тоді, коли ціль `ref` СПРАВДІ є в маніфесті своєї
   книги. Не знайшлася — прапорці лишаються, і крок друкується: тема, про яку
   забули, має лишитися видимою, а не зникнути разом із запискою.

   Ужиток:  node scripts/drop-todo-flags.js            (звіт)
            node scripts/drop-todo-flags.js --apply
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const M = require("./lib/manifest7.js");

const APPLY = process.argv.includes("--apply");

/* індекс усіх тем корпусу: "<книга>/<тема>" → статус детальної */
const T = new Map();
for (const [bslug, meta] of M.books()) {
  const bk = M.loadBook(meta.bookDir);
  if (!bk) continue;
  for (const t of M.allTopics(bk)) {
    if (!t.own) continue;
    T.set(bslug + "/" + t.slug, {
      d: (t.node.detailed && t.node.detailed.status) || "empty",
      b: (t.node.basic && t.node.basic.status) || "empty",
      at: t.group + "/" + t.chapter,
    });
  }
}

let flagged = 0, cleared = 0, kept = 0, filesTouched = 0;
const byStatus = {}, orphans = [];

for (const [cslug, meta] of M.books()) {
  if (meta.kind !== "course") continue;
  for (const f of fs.readdirSync(meta.bookDir)) {
    if (!f.endsWith(".json") || f === "manifest.json") continue;
    const p = path.join(meta.bookDir, f);
    const g = JSON.parse(fs.readFileSync(p, "utf8"));
    let touched = false;

    for (const ch of g.chapters || []) {
      for (const t of ch.topics || []) {
        if (!("todo" in t) && !("hint" in t)) continue;
        flagged++;
        const tgt = t.ref && T.get(t.ref);
        if (!tgt) {
          kept++;
          orphans.push(`${cslug} · ${g.slug}/${ch.slug} → ${t.ref || "(без ref)"} — цілі в маніфесті немає`);
          continue;
        }
        byStatus[tgt.d] = (byStatus[tgt.d] || 0) + 1;
        cleared++;
        delete t.todo; delete t.hint;
        touched = true;
      }
    }

    if (touched) {
      filesTouched++;
      if (APPLY) {
        fs.writeFileSync(p + ".tmp", JSON.stringify(g, null, 2) + "\n", "utf8");
        fs.renameSync(p + ".tmp", p);
      }
    }
  }
}

console.log(`${APPLY ? "ЗАСТОСОВАНО" : "ЗВІТ (нічого не записано)"}`);
console.log(`  кроків із прапорцями: ${flagged}`);
console.log(`  прапорці знято:       ${cleared}   у ${filesTouched} файлах груп`);
console.log(`  лишено (цілі немає):  ${kept}`);
console.log(`\n  статус детальної в цілі:`);
Object.entries(byStatus).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => console.log(`     ${String(v).padStart(4)}  ${k}`));
if (orphans.length) {
  console.log(`\n  ⚠ кроки, де ціль не знайшлася — прапорці ЛИШЕНО:`);
  orphans.slice(0, 20).forEach((o) => console.log(`     ${o}`));
  if (orphans.length > 20) console.log(`     … і ще ${orphans.length - 20}`);
}
if (!APPLY) console.log(`\nЩоб записати: node scripts/drop-todo-flags.js --apply`);
