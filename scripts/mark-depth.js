#!/usr/bin/env node
/* ============================================================================
   mark-depth.js — аудит повноти: виставляє status тем за обсягом прози (§2).
   Хімія (короткий курс): норма 700–1100. <700 → "deeper" (є текст, треба
   поглибити); ≥700 → "done". Чіпає лише теми зі статусом done/deeper/update
   (не empty). Друкує diff; пише лише з --apply.

   Запуск:  node scripts/mark-depth.js book/chemistry            (dry-run)
            node scripts/mark-depth.js book/chemistry --apply    (записати)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const root = process.argv[2];
const apply = process.argv.includes("--apply");
const NORM = 700;
if (!root) { console.error("Вкажи теку книги, напр.: node scripts/mark-depth.js book/chemistry"); process.exit(1); }

function walk(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out); else if (e.name.endsWith(".md")) out.push(p);
  }
  return out;
}
function proseWords(md) {
  let inCode = false, words = 0;
  for (let line of md.split(/\r?\n/)) {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; continue; }
    if (inCode || /^!\[/.test(t) || /^\*Рис\.?\s/i.test(t) || /^\|.*\|/.test(t)) continue;
    if (/^#{1,6}\s/.test(t)) line = t.replace(/^#{1,6}\s/, "");
    const s = line.replace(/`[^`]*`/g, " ").replace(/\[[^\]]*\]\([^)]*\)/g, (m) => m.replace(/\]\([^)]*\)/, "").slice(1))
      .replace(/^>\s*/, "").replace(/^[-*]\s+/, "").replace(/[*_#>`~]/g, " ");
    const m = s.match(/[\p{L}\p{N}’'\-]+/gu); if (m) words += m.length;
  }
  return words;
}
// slug → words (головні файли тем: ім'я файлу = ім'я теки)
const words = {};
for (const f of walk(root, [])) {
  const base = path.basename(f, ".md"), dir = path.basename(path.dirname(f));
  if (base === dir) words[dir] = proseWords(fs.readFileSync(f, "utf8"));
}

const mfile = path.join(root, "manifest.js");
const src = fs.readFileSync(mfile, "utf8");
let changed = 0; const log = [];
const out = src.split(/\n/).map((line) => {
  const sm = line.match(/slug:\s*"([^"]+)"/);
  const st = line.match(/status:\s*"(done|deeper|update)"/);
  if (!sm || !st || !(sm[1] in words)) return line;
  const slug = sm[1], w = words[slug];
  const next = w < NORM ? "deeper" : "done";
  if (next !== st[1]) { changed++; log.push(`  ${st[1]} → ${next}   ${String(w).padStart(4)}w  ${slug}`); }
  return line.replace(/status:\s*"(done|deeper|update)"/, `status: "${next}"`);
}).join("\n");

console.log(`\n== mark-depth ${root} (норма ≥${NORM}w) ==`);
console.log(log.length ? log.join("\n") : "  без змін");
console.log(`\nЗмін: ${changed}.` + (apply ? " ЗАПИСАНО." : " (dry-run — додай --apply, щоб записати)"));
if (apply && changed) fs.writeFileSync(mfile, out);
