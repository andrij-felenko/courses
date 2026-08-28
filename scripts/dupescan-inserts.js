#!/usr/bin/env node
/* СКАНЕР ДУБЛІВ ВСТАВОК — локальний, токенів не їсть.

   Ужиток: node scripts/dupescan-inserts.js [--book <слуг>] [--md <файл>]

   Три сигнали, від найтвердішого:
     (1) ТЕ САМЕ ІМ'Я ФАЙЛУ у різних темах книги — `hist-haynes-shockley.md` ×4;
     (2) ОДНАКОВИЙ H1 у двох вставок — те саме виведення під двома іменами;
     (3) СПІЛЬНІ РІДКІСНІ СЛОВА в H1: слово, що в книзі трапляється рівно у двох
         заголовках вставок і становить ≥½ коротшого — так ловиться один сюжет,
         переказаний під різними назвами (шість переказів Xerox PARC у sf-distributed
         жодним іменем файлу не видно).

   Нічого не змінює: об'єднувати — рішення людське (AUTHORING §6).                */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("./lib/manifest7.js");
const L = require("./checks/_lib.js");

const argv = process.argv.slice(2);
const val = (k) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : null; };
const ONLY = val("book"), MD = val("md");

const STOP = new Set(["для","про","або","що","як","the","and","від","до","та","і","й","у","в","з","на","із","між","при","під","над"]);
const words = (t) => (t||"").toLowerCase().replace(/ґ/g,"г").replace(/[^\p{L}\p{N}]+/gu," ")
  .trim().split(/\s+/).filter((w)=>w.length>3 && !STOP.has(w));
const tnorm = (t) => words(t).slice().sort().join(" ");

const hits = [];
for (const [bslug, rec] of M7.books()) {
  if (ONLY && bslug !== ONLY) continue;
  const b = M7.loadBook(rec.bookDir); if (!b) continue;
  const list = [];
  for (const t of M7.allTopics(b)) {
    if (!t.own) continue;
    for (const type of M7.INSERT_TYPES) for (const ins of t.node[type] || []) {
      const p = path.join(rec.bookDir, t.slug, ins.file);
      const m = fs.existsSync(p) ? L.read(p).match(/^#\s+(.+)$/m) : null;
      list.push({ book: bslug, topic: t.slug, file: ins.file, type,
                  status: ins.status, h1: m ? m[1].trim() : "" });
    }
  }
  /* (1) те саме ім'я */
  const byFile = new Map();
  for (const r of list) { if (!byFile.has(r.file)) byFile.set(r.file, []); byFile.get(r.file).push(r); }
  for (const [f, v] of byFile) if (v.length > 1)
    hits.push({ book: bslug, why: `те саме ім'я файлу ×${v.length}`, w: 3, items: v });

  /* (2) однаковий H1 */
  const byH1 = new Map();
  for (const r of list) { const k = tnorm(r.h1); if (!k) continue; if (!byH1.has(k)) byH1.set(k, []); byH1.get(k).push(r); }
  for (const [, v] of byH1) if (v.length > 1 && new Set(v.map((x)=>x.file)).size > 1)
    hits.push({ book: bslug, why: `ОДНАКОВИЙ заголовок ×${v.length}`, w: 3, items: v });

  /* (3) спільне рідкісне слово в H1 */
  const freq = new Map();
  for (const r of list) for (const w of new Set(words(r.h1))) freq.set(w, (freq.get(w)||0)+1);
  const seen = new Set();
  for (let i = 0; i < list.length; i++) for (let j = i+1; j < list.length; j++) {
    const A = list[i], B = list[j];
    if (A.file === B.file || tnorm(A.h1) === tnorm(B.h1)) continue;
    const wa = words(A.h1), wb = new Set(words(B.h1));
    const sh = wa.filter((w)=>wb.has(w) && (freq.get(w)||0) <= 2);
    if (!sh.length) continue;
    if (sh.length / Math.min(wa.length, wb.size) < 0.5) continue;
    const k = [A.book+"/"+A.topic+"/"+A.file, B.book+"/"+B.topic+"/"+B.file].sort().join("|");
    if (seen.has(k)) continue; seen.add(k);
    hits.push({ book: bslug, why: `слова «${sh.join("», «")}» лише в цих двох заголовках`, w: 2, items: [A, B] });
  }
}

hits.sort((a,b)=> b.w-a.w || a.book.localeCompare(b.book));
const strong = hits.filter((h)=>h.w>=3);
console.log(`\n=== СКАНЕР ДУБЛІВ ВСТАВОК ===`);
console.log(`сигналів: ${hits.length} (тверді ${strong.length}, за заголовками ${hits.length-strong.length})`);
const per = {}; hits.forEach((h)=>per[h.book]=(per[h.book]||0)+1);
console.log(`книг зачеплено: ${Object.keys(per).length}\n`);
Object.entries(per).sort((a,b)=>b[1]-a[1]).slice(0,12)
  .forEach(([b,n])=>console.log(`  ${b.padEnd(22)} ${String(n).padStart(4)}`));

if (MD) {
  const L2 = ["# Сканер дублів вставок", "",
    `Тверді сигнали: **${strong.length}**, за схожими заголовками: **${hits.length-strong.length}**.`,
    "Нічого не змінено — об'єднувати вирішує людина.", ""];
  for (const h of hits) {
    L2.push(`### ${h.book} — ${h.why}`);
    for (const it of h.items) L2.push(`- \`${it.topic}/${it.file}\` [${it.status}] — «${it.h1}»`);
    L2.push("");
  }
  fs.mkdirSync(path.dirname(MD), { recursive: true });
  fs.writeFileSync(MD, L2.join("\n"), "utf8");
  console.log(`\nзаписано: ${MD}`);
}
