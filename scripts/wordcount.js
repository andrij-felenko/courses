#!/usr/bin/env node
/* ============================================================================
   wordcount.js — лічильник ПРОЗИ за AUTHORING.md §3 (без код-блоків, фігур, розмітки).
   Класифікує файли за іменем (нейминг §2):
     <slug>/<slug>.md       → базова стаття   (540–1440)
     <slug>/<slug>-d.md     → детальна стаття (1080–9000; каталог — до 14400)
     <slug>/<type>-<name>.md (type ∈ hist/comp/math/proj/api) → вставка (540–8100)
   Плюс ЗАЛІЗО §3 «базова ≤ ½ детальної»: для кожної теми, де є ОБИДВІ версії, рахує
   відношення слів; базова, довша за половину своєї детальної, — ПОРУШЕННЯ (не попередження).
   Універсальний — параметр: тека книги/каталогу/довідника/курсу.

   Запуск:  node scripts/wordcount.js book/chemistry
            node scripts/wordcount.js book/chemistry --all   (показати всі, не лише підсумок)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const root = process.argv[2];
const showAll = process.argv.includes("--all");
if (!root) { console.error("Вкажи теку, напр.: node scripts/wordcount.js book/chemistry"); process.exit(1); }
const CEIL_DETAILED = /(^|[\\/])catalog([\\/]|$)/.test(root) ? 14400 : 9000;   // каталог — до 14400

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
  if (/^(hist|comp|math|proj|api)-/.test(base)) return "insert";
  return "other";
}
function band(kind, w) {
  if (kind === "insert") return w < 540 ? "▽ мала вставка (<540)" : w <= 8100 ? "✓ вставка (540–8100)" : "▲ завелика (>8100) — поділити";
  if (kind === "detailed") return w < 1080 ? "▽ детальна нижче (<1080)" : w <= CEIL_DETAILED ? `✓ детальна (1080–${CEIL_DETAILED})` : `▲ понад (>${CEIL_DETAILED})`;
  if (kind === "basic") return w < 540 ? "✖ мало (<540)" : w <= 1440 ? "✓ базова (540–1440)" : "▲ понад базову (>1440) — на детальну?";
  return "· інше";
}

const files = walk(root, []);
const items = [];
for (const f of files) {
  const base = path.basename(f, ".md");
  const dir = path.basename(path.dirname(f));
  const kind = classify(base, dir);
  const { words, figs } = proseWords(fs.readFileSync(f, "utf8"));
  items.push({ branch: path.basename(path.dirname(path.dirname(f))), slug: dir, dirPath: path.dirname(f), base, kind, words, figs });
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

/* --- ЗАЛІЗО §3: базова ≤ ½ детальної ------------------------------------- */
// Пара — це базова й детальна ОДНІЄЇ теми (одна тека). Порушення = базова довша за половину
// прози детальної: скоротити базову, а не сходиться — базової не писати (basic:empty, §3/§9).
const byDir = new Map();
for (const t of items) {
  if (t.kind !== "basic" && t.kind !== "detailed") continue;
  const e = byDir.get(t.dirPath) || { branch: t.branch, slug: t.slug };
  e[t.kind] = t.words;
  byDir.set(t.dirPath, e);
}
const pairs = [], lonelyBasic = [];
for (const e of byDir.values()) {
  if (e.basic == null) continue;
  if (e.detailed == null) { lonelyBasic.push(e); continue; }
  pairs.push({ ...e, ratio: e.detailed ? e.basic / e.detailed : Infinity });
}
pairs.sort((a, b) => b.ratio - a.ratio);
const bad = pairs.filter((p) => p.ratio > 0.5);
console.log(`\n-- ПАРИ базова↔детальна (§3: базова ≤ ½ детальної) --  пар: ${pairs.length}`);
if (pairs.length) {
  const rows = showAll ? pairs : bad;
  for (const p of rows) {
    const mark = p.ratio > 0.5 ? "✖ ПОРУШЕННЯ" : "✓";
    console.log(`  ${mark.padEnd(12)} ${String(Math.round(p.ratio * 100)).padStart(3)}%  база ${String(p.basic).padStart(5)}w / деталь ${String(p.detailed).padStart(6)}w  (стеля бази ${Math.floor(p.detailed / 2)}w)  ${p.branch}/${p.slug}`);
  }
  console.log(`  ✖ порушень ${bad.length} · ✓ у нормі ${pairs.length - bad.length}${!showAll && bad.length ? "" : !showAll ? " (усі пари — --all)" : ""}`);
  if (bad.length) console.log(`  → скоротити базову до ≤ половини детальної; не стискається без утрати суті — базової не писати (basic:empty, §3)`);
}
if (lonelyBasic.length) console.log(`\n· базових без детальної на диску: ${lonelyBasic.length}${showAll ? " — " + lonelyBasic.map((e) => `${e.branch}/${e.slug}`).join(", ") : " (--all покаже перелік)"}  · детальна — основна версія (§3)`);
