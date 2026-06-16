#!/usr/bin/env node
/* ============================================================================
   wordcount.js — лічильник ПРОЗИ за §2 AUTHORING (без код-блоків, фігур, розмітки).
   Рахує головні файли тем (де ім'я файлу = ім'я теки розділу): <slug>/<slug>.md.
   Вставки (-h/-m/-c/-a/-p) рахує окремо. Універсальний — параметр: тека книги.

   Запуск:  node scripts/wordcount.js book/chemistry
            node scripts/wordcount.js book/chemistry --all   (показати всі, не лише підсумок)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const root = process.argv[2];
const showAll = process.argv.includes("--all");
if (!root) { console.error("Вкажи теку книги, напр.: node scripts/wordcount.js book/chemistry"); process.exit(1); }

function walk(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.isFile() && e.name.endsWith(".md")) out.push(p);
  }
  return out;
}

// проза = текст без: код-блоків ``` ```, рядків-зображень ![...], підписів *Рис...*,
// заголовків #, маркерів цитат/таблиць; емодзі-callout-и (🔧🏠🧪📜💡▶️) лишаємо як прозу.
function proseWords(md) {
  let inCode = false;
  let words = 0, figs = 0;
  for (let line of md.split(/\r?\n/)) {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; continue; }
    if (inCode) continue;
    if (/^!\[/.test(t)) { figs++; continue; }                 // рядок-зображення
    if (/^\*Рис\.?\s/i.test(t)) continue;                      // підпис фігури
    if (/^#{1,6}\s/.test(t)) line = t.replace(/^#{1,6}\s/, ""); // заголовок → лишаємо текст
    if (/^\|.*\|/.test(t)) continue;                           // рядок таблиці
    let s = line
      .replace(/`[^`]*`/g, " ")                                // інлайн-код
      .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
      .replace(/\[[^\]]*\]\([^)]*\)/g, (m) => m.replace(/\]\([^)]*\)/, "").replace(/^\[/, "")) // лінк → текст
      .replace(/^>\s*/, "")                                    // маркер цитати
      .replace(/^[-*]\s+/, "")                                 // маркер списку
      .replace(/[*_#>`~]/g, " ");
    const m = s.match(/[\p{L}\p{N}’'\-]+/gu);
    if (m) words += m.length;
  }
  return { words, figs };
}

const files = walk(root, []);
const topics = [];
for (const f of files) {
  const base = path.basename(f, ".md");
  const dir = path.basename(path.dirname(f));
  const isMain = base === dir;                                 // головний файл теми
  const kind = isMain ? "topic" : (base.match(/-(h|m|c|a|p)(-|$)/) ? "insert" : "other");
  const { words, figs } = proseWords(fs.readFileSync(f, "utf8"));
  topics.push({ f, branch: path.basename(path.dirname(path.dirname(f))), slug: dir, kind, words, figs });
}

const mains = topics.filter((t) => t.kind === "topic").sort((a, b) => a.words - b.words);
// межі §2 для короткого курсу (Хімія): 700–1100 звичайна, до 1500 важка
function band(w) {
  if (w < 500) return "✖ дуже мало (<500)";
  if (w < 700) return "▽ нижче норми (500–700)";
  if (w <= 1100) return "✓ норма (700–1100)";
  if (w <= 1500) return "✓ важка (1100–1500)";
  return "▲ понад курс (>1500)";
}

console.log(`\n== ПРОЗА головних тем у ${root} ==  (тем: ${mains.length})\n`);
if (showAll) {
  for (const t of mains) console.log(`${String(t.words).padStart(5)}w  ${String(t.figs).padStart(2)}f  ${band(t.words).padEnd(26)} ${t.branch}/${t.slug}`);
}
const buckets = {};
for (const t of mains) { const b = band(t.words); (buckets[b] = buckets[b] || []).push(t.slug); }
console.log("\n-- Підсумок за смугами §2 --");
for (const b of ["✖ дуже мало (<500)", "▽ нижче норми (500–700)", "✓ норма (700–1100)", "✓ важка (1100–1500)", "▲ понад курс (>1500)"]) {
  if (buckets[b]) console.log(`${String(buckets[b].length).padStart(3)}  ${b}`);
}
const ins = topics.filter((t) => t.kind === "insert");
if (ins.length) console.log(`\nВставок (-h/-m/-c): ${ins.length}`);
const all = mains.map((t) => t.words);
console.log(`\nМедіана прози: ${all.length ? all[Math.floor(all.length / 2)] : 0}w · мін ${Math.min(...all)} · макс ${Math.max(...all)}`);
