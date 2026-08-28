#!/usr/bin/env node
/* Перелічити ФАКТ під чинні смуги — без агентів і без токенів.
   Ужиток: node scripts/levels-recount.js [--apply]

   Голоси оцінювачів не чіпає: рівень поставили люди-агенти, і він лишається.
   Перераховує лише те, що міряється лічильником: слова прози, рядки коду,
   рівень, який ВИТРИМУЄ наявний обсяг, і Δ між оцінкою та фактом.

   Робити це варто саме тепер: код виїхав з огорож у файли, а директиви `:::code`
   більше не рахуються прозою — тобто вперше слова означають слова.

   Δ = рівень оцінки − рівень факту:
     Δ ≥ 2  тонко, тема просить `deeper`;
     Δ = 1  допуск, у межах похибки оцінки;
     Δ ≤ 0  написано не мілкіше за оцінку.                                       */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("./lib/manifest7.js");
const L = require("./checks/_lib.js");

const APPLY = process.argv.includes("--apply");
const DIR = path.join(__dirname, "_levels");

/* Рівень, який витримує обсяг: найвищий, чия підлога ще не перевищена. */
function levelOfSize(kind, n) {
  let lv = 0;
  for (let i = 1; i <= L.LEVELS; i++) if (n >= L.bandOf(kind, i).floor) lv = i;
  return lv;
}
function levelOfCode(n) {
  let lv = 0;
  for (let i = 1; i <= L.LEVELS; i++) if (n >= L.CODE_FLOOR.low[i - 1]) lv = i;
  return lv;
}

/* тека теми за книгою й слугом */
const dirCache = new Map();
function topicDir(book, slug) {
  const k = book + "/" + slug;
  if (dirCache.has(k)) return dirCache.get(k);
  const rec = M7.books().get(book);
  const d = rec ? path.join(rec.bookDir, slug) : null;
  dirCache.set(k, d);
  return d;
}

const hist = { t: {}, i: {} };
const add = (h, d) => { h[d] = (h[d] || 0) + 1; };
let nT = 0, nI = 0, missT = 0, missI = 0;
const deeperT = [], deeperI = [];

/* ── теми: обсяг детальної проти смуги detailed ───────────────────────────── */
for (const f of fs.readdirSync(DIR)) {
  if (!f.endsWith(".json") || f.startsWith("_")) continue;
  const p = path.join(DIR, f);
  const j = JSON.parse(fs.readFileSync(p, "utf8"));
  for (const t of j.topics || []) {
    const d = topicDir(j.book, t.slug);
    const md = d && path.join(d, t.slug + "-d.md");
    if (!md || !fs.existsSync(md)) { t.words = null; t.realLevel = null; t.delta = null; missT++; continue; }
    t.words = L.proseWords(L.read(md));
    t.realLevel = levelOfSize("detailed", t.words);
    t.delta = t.level - t.realLevel;
    add(hist.t, t.delta); nT++;
    if (t.delta >= 2) deeperT.push({ book: j.book, slug: t.slug, level: t.level, words: t.words, real: t.realLevel, d: t.delta });
  }
  if (APPLY) {
    fs.writeFileSync(p, JSON.stringify(j, null, 1), "utf8");
    fs.writeFileSync(path.join(DIR, f.replace(/\.json$/, ".tsv")),
      ["слуг\tназва\tгрупа\tрозділ\tA\tB\tC\tсередня\tрівень\tслів\tРфакт\tΔ",
        ...(j.topics || []).map((x) => [x.slug, x.title, x.group, x.chapter, ...(x.votes || ["", "", ""]),
          x.mean, x.level, x.words ?? "", x.realLevel ?? "", x.delta ?? ""].join("\t"))].join("\n") + "\n", "utf8");
  }
}

/* ── вставки: проза за своєю смугою + код у теках проєктів ────────────────── */
const IDIR = path.join(DIR, "inserts");
for (const f of fs.readdirSync(IDIR)) {
  if (!f.endsWith(".json")) continue;
  const p = path.join(IDIR, f);
  const j = JSON.parse(fs.readFileSync(p, "utf8"));
  for (const i of j.inserts || []) {
    const d = topicDir(j.book, i.topic);
    const md = d && path.join(d, i.file);
    if (!md || !fs.existsSync(md)) { i.words = null; i.real = null; i.delta = null; missI++; continue; }
    const band = L.bandOf(i.type, i.level);
    i.words = L.proseWords(L.read(md));
    i.real = levelOfSize(i.type, i.words);
    i.delta = i.level - i.real;
    i.floor = band.floor; i.max = band.max;
    if (L.NEEDS_CODE.has(i.type)) {
      const dirs = L.langDirsOf(d, i.file);
      i.code = dirs.reduce((a, x) => a + L.codeLinesOfDir(x.dir).lines, 0);
      i.codeFloor = L.CODE_FLOOR.low[i.level - 1];
      i.codeReal = levelOfCode(i.code);
      i.codeDelta = i.level - i.codeReal;
    } else { i.code = null; i.codeFloor = null; i.codeReal = null; i.codeDelta = null; }
    add(hist.i, i.delta); nI++;
    if (i.delta >= 2) deeperI.push({ book: j.book, topic: i.topic, file: i.file, type: i.type, level: i.level, words: i.words, real: i.real, d: i.delta });
  }
  if (APPLY) {
    fs.writeFileSync(p, JSON.stringify(j, null, 1), "utf8");
    fs.writeFileSync(path.join(IDIR, f.replace(/\.json$/, ".tsv")),
      ["тема\tгрупа\tфайл\tтип\tA\tB\tC\tсередня\tрівень\tслів\tпідлога\tРфакт\tΔ\tкоду\tпідлКод\tРкод\tΔкод",
        ...(j.inserts || []).map((x) => [x.topic, x.group, x.file, x.type, ...(x.votes || ["", "", ""]),
          x.mean, x.level, x.words ?? "", x.floor ?? "", x.real ?? "", x.delta ?? "",
          x.code ?? "", x.codeFloor ?? "", x.codeReal ?? "", x.codeDelta ?? ""].join("\t"))].join("\n") + "\n", "utf8");
  }
}

const show = (h, n) => [-4, -3, -2, -1, 0, 1, 2, 3, 4].filter((d) => h[d])
  .map((d) => `${d > 0 ? "+" : ""}${d}: ${h[d]} (${Math.round(h[d] / n * 100)}%)`).join(" · ");

console.log(`\n=== ФАКТ ПРОТИ ОЦІНКИ ===${APPLY ? "" : "   (показ, нічого не записано)"}\n`);
console.log(`теми:    ${nT} виміряно${missT ? `, ${missT} без файла` : ""}`);
console.log(`  Δ  ${show(hist.t, nT)}`);
console.log(`  тонко (Δ≥2): ${deeperT.length} (${Math.round(deeperT.length / nT * 100)}%)`);
console.log(`\nвставки: ${nI} виміряно${missI ? `, ${missI} без файла` : ""}`);
console.log(`  Δ  ${show(hist.i, nI)}`);
console.log(`  тонко (Δ≥2): ${deeperI.length} (${Math.round(deeperI.length / nI * 100)}%)`);

const byType = {};
for (const x of deeperI) byType[x.type] = (byType[x.type] || 0) + 1;
console.log("  за типом: " + Object.entries(byType).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(" · "));

if (APPLY) {
  const out = path.join(DIR, "_deeper.json");
  fs.writeFileSync(out, JSON.stringify({ topics: deeperT, inserts: deeperI }, null, 1), "utf8");
  console.log(`\nсписок на deeper → ${path.relative(process.cwd(), out).replace(/\\/g, "/")}`);
} else console.log("\n(додай --apply, щоб переписати списки й скласти _deeper.json)");
