#!/usr/bin/env node
/* РІВЕНЬ ЗА ОЦІНКОЮ ПРОТИ РІВНЯ ЗА РОЗМІРОМ — локально, токенів не їсть.

   Ужиток: node scripts/levels-actual.js [--apply]

   Агенти сказали, наскільки глибоко тему ТРЕБА розкрити. Цей скрипт міряє, наскільки
   вона розкрита НАСПРАВДІ — самим лише лічильником прози детальної версії, тим самим
   `proseWords`, що й перевірка 06. Далі переводить обсяг у рівень за тією ж зонною
   шкалою, що й підлога:

       рівень_за_розміром = 1 + floor((слова − lo) / ((hi − lo) / 5)),  обрізано до 1..5

   Тобто «Р3 за розміром» означає рівно те саме, що «текст лежить у третій зоні смуги»
   — у тій, куди його поклала б підлога Р3.

   Δ = рівень оцінки − рівень за розміром:
     Δ = 0   написане відповідає оцінці;
     Δ > 0   НЕДОПИС: тема важливіша, ніж написано (Δ=2 — на дві зони);
     Δ < 0   написано глибше, ніж оцінено — або текст роздутий, або оцінку занижено.

   Нічого не змінює в корпусі: лише дописує колонки у scripts/_levels/*.tsv (з --apply).  */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("./lib/manifest7.js");
const L = require("./checks/_lib.js");

const APPLY = process.argv.includes("--apply");
const DIR = path.join(__dirname, "_levels");

/* обсяг → рівень за тією самою зонною шкалою, що й підлога */
function levelOfWords(kind, w) {
  const b = L.bandOf(kind);
  const zone = (b.hi - b.lo) / L.LEVELS;
  return Math.max(1, Math.min(L.LEVELS, 1 + Math.floor((w - b.lo) / zone)));
}

const all = [];
for (const f of fs.readdirSync(DIR).filter((x) => x.endsWith(".json") && !x.startsWith("_")).sort()) {
  const j = JSON.parse(fs.readFileSync(path.join(DIR, f), "utf8"));
  const rec = M7.books().get(j.book); if (!rec) continue;
  const b = M7.loadBook(rec.bookDir); if (!b) continue;
  const st = new Map();
  for (const t of M7.allTopics(b)) if (t.own) st.set(t.slug, (t.node.detailed && t.node.detailed.status) || "—");

  for (const t of j.topics) {
    const p = path.join(rec.bookDir, t.slug, `${t.slug}-d.md`);
    let words = null, real = null;
    if (fs.existsSync(p)) { words = L.proseWords(L.read(p)); real = levelOfWords("detailed", words); }
    t.words = words; t.realLevel = real;
    t.delta = (real === null || t.level === null) ? null : t.level - real;
    all.push({ book: j.book, kind: j.kind, slug: t.slug, title: t.title, group: t.group,
               chapter: t.chapter, status: st.get(t.slug) || "—", votes: t.votes,
               mean: t.mean, level: t.level, words, real, delta: t.delta, spread: t.spread });
  }
  if (APPLY) {
    fs.writeFileSync(path.join(DIR, f), JSON.stringify(j, null, 2), "utf8");
    const head = "слуг\tназва\tгрупа\tA\tB\tC\tсередня\tрівень\tслів\tРфакт\tΔ";
    const body = j.topics.map((t) => [t.slug, t.title, t.group, ...t.votes.map((v) => v ?? ""),
      t.mean, t.level, t.words ?? "", t.realLevel ?? "", t.delta ?? ""].join("\t"));
    fs.writeFileSync(path.join(DIR, `${j.book}.tsv`), [head, ...body].join("\n"), "utf8");
  }
}

/* ── звіт ─────────────────────────────────────────────────────────────────── */
const have = all.filter((r) => r.words !== null);
const miss = all.length - have.length;
const bandDetailed = L.bandOf("detailed");
console.log(`\n=== ОЦІНКА ПРОТИ РОЗМІРУ ===  тем ${all.length}, з детальною на диску ${have.length}${miss ? `, без файлу ${miss}` : ""}`);
console.log(`смуга детальної ${bandDetailed.lo}–${bandDetailed.hi}, зона ${Math.round((bandDetailed.hi - bandDetailed.lo) / L.LEVELS)} слів\n`);

const w = have.map((r) => r.words).sort((a, b) => a - b);
const q = (p) => w[Math.floor((w.length - 1) * p)];
console.log(`обсяг детальних: min ${w[0]} · q25 ${q(.25)} · медіана ${q(.5)} · q75 ${q(.75)} · max ${w[w.length - 1]}`);

const cross = {};
for (const r of have) { const k = `${r.level}|${r.real}`; cross[k] = (cross[k] || 0) + 1; }
console.log(`\n            рівень за розміром →`);
console.log(`оцінка ↓    Р1     Р2     Р3     Р4     Р5      разом`);
for (let a = 1; a <= 5; a++) {
  const row = [1, 2, 3, 4, 5].map((b) => cross[`${a}|${b}`] || 0);
  console.log(`   Р${a}   ` + row.map((n) => String(n).padStart(5)).join("  ") + `   ${String(row.reduce((x, y) => x + y, 0)).padStart(6)}`);
}
const tot = [1, 2, 3, 4, 5].map((b) => [1, 2, 3, 4, 5].reduce((s, a) => s + (cross[`${a}|${b}`] || 0), 0));
console.log(` разом  ` + tot.map((n) => String(n).padStart(5)).join("  "));

const d = {};
for (const r of have) d[r.delta] = (d[r.delta] || 0) + 1;
console.log(`\nΔ (оцінка − розмір):`);
for (const k of Object.keys(d).map(Number).sort((a, b) => b - a))
  console.log(`  ${k > 0 ? "+" : ""}${k}  ${String(d[k]).padStart(5)}  ${(d[k] / have.length * 100).toFixed(1)}%  ${k > 0 ? "недопис" : k < 0 ? "написано глибше" : "збіг"}`);
const under = have.filter((r) => r.delta > 0), deep = have.filter((r) => r.delta >= 2);
console.log(`\nнедопис (Δ>0): ${under.length} (${(under.length / have.length * 100).toFixed(0)}%), з них на дві зони й більше: ${deep.length}`);
console.log(`сумарний недобір до підлоги свого рівня: ${have.reduce((s, r) => s + Math.max(0, L.bandOf("detailed", r.level).floor - r.words), 0).toLocaleString("uk")} слів`);

if (APPLY) {
  const head = ["книга","вид","група","розділ","слуг","назва","статус","A","B","C","середня","рівень","слів","Рфакт","Δ"];
  all.sort((x, y) => x.book.localeCompare(y.book) || (y.delta ?? -9) - (x.delta ?? -9) || y.mean - x.mean);
  fs.writeFileSync(path.join(DIR, "_ALL.tsv"), [head.join("\t"), ...all.map((r) => [r.book, r.kind, r.group, r.chapter,
    r.slug, r.title, r.status, ...r.votes.map((v) => v ?? ""), r.mean, r.level, r.words ?? "", r.real ?? "", r.delta ?? ""].join("\t"))].join("\n"), "utf8");
  fs.writeFileSync(path.join(DIR, "_ALL.json"), JSON.stringify({ topics: all.length, rows: all }, null, 1), "utf8");
  console.log(`\nзаписано: _ALL.tsv, _ALL.json і 54 файли по книгах`);
}
