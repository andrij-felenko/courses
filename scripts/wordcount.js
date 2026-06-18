#!/usr/bin/env node
/* ============================================================================
   wordcount.js — лічильник ПРОЗИ за AUTHORING.md §3 (без код-блоків, фігур, розмітки).
   Класифікує файли за іменем (нейминг §2):
     <slug>/<slug>.md       → базова стаття   (1000–3500)
     <slug>/<slug>-d.md     → детальна стаття (2500–13000; каталог — до 25000)
     <slug>/<type>-<name>.md (type ∈ hist/comp/math/proj) → вставка (1000–10000)
   Універсальний — параметр: тека книги/каталогу/курсу.

   Запуск:  node scripts/wordcount.js book/chemistry
            node scripts/wordcount.js book/chemistry --all   (показати всі, не лише підсумок)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const root = process.argv[2];
const showAll = process.argv.includes("--all");
if (!root) { console.error("Вкажи теку, напр.: node scripts/wordcount.js book/chemistry"); process.exit(1); }
const CEIL_DETAILED = /(^|[\\/])catalog([\\/]|$)/.test(root) ? 25000 : 13000;   // каталог — до 25000

function walk(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.isFile() && e.name.endsWith(".md")) out.push(p);
  }
  return out;
}

// проза = текст без код-блоків ``` ```, рядків-зображень ![...], підписів фігур,
// заголовків #, рядків таблиць; емодзі-callout-и (🔧🏠🧪📜💡▶️) лишаємо як прозу.
function proseWords(md) {
  let inCode = false, words = 0, figs = 0;
  for (let line of md.split(/\r?\n/)) {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; continue; }
    if (inCode) continue;
    if (/^!\[/.test(t)) { figs++; continue; }                  // рядок-зображення
    if (/^\*[^*]*\.\*?$/.test(t) && /^\*.+\.\*$/.test(t) && figs > 0 && t.length < 200) { /* підпис фігури курсивом */ }
    if (/^#{1,6}\s/.test(t)) line = t.replace(/^#{1,6}\s/, "");  // заголовок → лишаємо текст
    if (/^\|.*\|/.test(t)) continue;                            // рядок таблиці
    let s = line
      .replace(/`[^`]*`/g, " ")
      .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
      .replace(/\[[^\]]*\]\([^)]*\)/g, (m) => m.replace(/\]\([^)]*\)/, "").replace(/^\[/, ""))
      .replace(/^>\s*/, "").replace(/^[-*]\s+/, "").replace(/[*_#>`~]/g, " ");
    const m = s.match(/[\p{L}\p{N}’'\-]+/gu);
    if (m) words += m.length;
  }
  return { words, figs };
}

function classify(base, dir) {
  if (base === dir) return "basic";
  if (base === dir + "-d") return "detailed";
  if (/^(hist|comp|math|proj)-/.test(base)) return "insert";
  return "other";
}
function band(kind, w) {
  if (kind === "insert") return w < 1000 ? "▽ мала вставка (<1000)" : w <= 10000 ? "✓ вставка (1000–10000)" : "▲ завелика (>10000) — поділити";
  if (kind === "detailed") return w < 2500 ? "▽ детальна нижче (<2500)" : w <= CEIL_DETAILED ? `✓ детальна (2500–${CEIL_DETAILED})` : `▲ понад (>${CEIL_DETAILED})`;
  if (kind === "basic") return w < 1000 ? "✖ мало (<1000)" : w <= 3500 ? "✓ базова (1000–3500)" : "▲ понад базову (>3500) — на детальну?";
  return "· інше";
}

const files = walk(root, []);
const items = [];
for (const f of files) {
  const base = path.basename(f, ".md");
  const dir = path.basename(path.dirname(f));
  const kind = classify(base, dir);
  const { words, figs } = proseWords(fs.readFileSync(f, "utf8"));
  items.push({ branch: path.basename(path.dirname(path.dirname(f))), slug: dir, base, kind, words, figs });
}

const ORDER = ["basic", "detailed", "insert"];
const LABEL = { basic: "БАЗОВІ", detailed: "ДЕТАЛЬНІ", insert: "ВСТАВКИ" };
console.log(`\n== ПРОЗА у ${root} ==  (файлів .md: ${items.length})`);
for (const kind of ORDER) {
  const grp = items.filter((t) => t.kind === kind).sort((a, b) => a.words - b.words);
  if (!grp.length) continue;
  console.log(`\n-- ${LABEL[kind]} (${grp.length}) --`);
  if (showAll) for (const t of grp) console.log(`${String(t.words).padStart(6)}w ${String(t.figs).padStart(2)}f  ${band(t.kind, t.words).padEnd(30)} ${t.branch}/${t.slug}${t.kind === "insert" ? "/" + t.base : ""}`);
  const buckets = {};
  for (const t of grp) { const b = band(t.kind, t.words); (buckets[b] = buckets[b] || []).push(t.slug); }
  for (const b of Object.keys(buckets)) console.log(`${String(buckets[b].length).padStart(4)}  ${b}`);
  const ws = grp.map((t) => t.words);
  console.log(`     медіана ${ws[Math.floor(ws.length / 2)]}w · мін ${Math.min(...ws)} · макс ${Math.max(...ws)}`);
}
const other = items.filter((t) => t.kind === "other");
if (other.length) console.log(`\n· інших .md (не базова/детальна/вставка): ${other.length}`);
