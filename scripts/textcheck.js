#!/usr/bin/env node
/* ============================================================================
   textcheck.js — локальний гейт тексту статей (без залежностей).
   Класи: (1) гомогліфи латиниці в кириличних словах — ЄДИНИЙ клас, що --apply
   виправляє автоматично; (2) сирий LaTeX поза кодом; (3) склейки кирилиця+
   латиниця та русизми/канцеляризми зі словника; (4) осиротілі/биті SVG і
   теки без figs.py; (5) недобір обсягу (рахунок РАЗОМ із кодом, на відміну
   від wordcount.js).

   Запуск:  node scripts/textcheck.js <тека> [--apply]
   Дефолт — лише звіт; --apply застосовує ЛИШЕ клас (1).
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const root = process.argv[2];
const apply = process.argv.includes("--apply");
if (!root) { console.error("Вкажи теку, напр.: node scripts/textcheck.js book/algorithms"); process.exit(1); }

function walk(dir, out) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.isFile() && e.name.endsWith(".md")) out.push(p);
  }
  return out;
}

/* --- карта гомогліфів (§ завдання) --------------------------------------- */
const LOWER_MAP = { a: "а", o: "о", e: "е", c: "с", p: "р", x: "х", i: "і", y: "у" }; // s навмисно НІ
const UPPER_MAP = { A: "А", B: "В", C: "С", E: "Е", H: "Н", K: "К", M: "М", O: "О", P: "Р", T: "Т", X: "Х" };
const HOMO_MAP = Object.assign({}, LOWER_MAP, UPPER_MAP);
const CYR = "а-яА-ЯіїєґІЇЄҐ";
const WORD_RE = new RegExp(`[A-Za-z${CYR}]+`, "g");
const HAS_CYR_RE = new RegExp(`[${CYR}]`);
const HAS_MAPPABLE_LATIN_RE = new RegExp(`[${Object.keys(HOMO_MAP).join("")}]`);

/* --- захищені зони в рядку: інлайн-код, ціль markdown-лінка, URL, шлях ---- */
function protectedRanges(line) {
  const ranges = [];
  const push = (s, e) => { if (e > s) ranges.push([s, e]); };
  let m;
  const reCode = /`[^`]*`/g;
  while ((m = reCode.exec(line))) push(m.index, m.index + m[0].length);
  const reLinkDest = /\]\(([^)]*)\)/g;
  while ((m = reLinkDest.exec(line))) push(m.index + 2, m.index + 2 + m[1].length);
  const reUrl = /https?:\/\/[^\s)]+/g;
  while ((m = reUrl.exec(line))) push(m.index, m.index + m[0].length);
  const rePath = /(^|[\s(])(\/[\w\-./]+)/g;
  while ((m = rePath.exec(line))) push(m.index + m[1].length, m.index + m[0].length);
  return ranges;
}
function isProtected(ranges, s, e) {
  return ranges.some(([a, b]) => s < b && e > a);
}

/* --- клас (1): гомогліфи --------------------------------------------------- */
function scanHomoglyphs(lines) {
  const hits = [];       // {lineNo, from, to}
  let inFence = false;
  lines.forEach((line, idx) => {
    if (/^\s*```/.test(line)) { inFence = !inFence; return; }
    if (inFence) return;
    const prot = protectedRanges(line);
    let m;
    WORD_RE.lastIndex = 0;
    while ((m = WORD_RE.exec(line))) {
      const tok = m[0], s = m.index, e = s + tok.length;
      if (isProtected(prot, s, e)) continue;
      if (!HAS_CYR_RE.test(tok) || !HAS_MAPPABLE_LATIN_RE.test(tok)) continue;
      // безпека: якщо в токені лишається латинська літера БЕЗ відповідника (l,s,d,n,t,h,w,r,k,f,…),
      // це не гомогліф-описка, а вклеєне справжнє англійське слово (closed, worked, FORTRAN…) —
      // такий випадок лишаємо класу (3) на ручний розгляд, а не калічимо напівзаміною.
      let hasUnmapped = false;
      for (const ch of tok) if (/[A-Za-z]/.test(ch) && !HOMO_MAP[ch]) { hasUnmapped = true; break; }
      if (hasUnmapped) continue;
      let fixed = "", changed = false;
      for (const ch of tok) {
        if (HOMO_MAP[ch]) { fixed += HOMO_MAP[ch]; changed = true; } else fixed += ch;
      }
      if (changed) hits.push({ lineNo: idx + 1, from: tok, to: fixed, col: s });
    }
  });
  return hits;
}
function applyHomoglyphs(lines, hits) {
  // застосовуємо по рядках, справа наліво, щоб не збити зсуви колонок
  const byLine = new Map();
  for (const h of hits) (byLine.get(h.lineNo) || byLine.set(h.lineNo, []).get(h.lineNo)).push(h);
  for (const [lineNo, arr] of byLine) {
    arr.sort((a, b) => b.col - a.col);
    let line = lines[lineNo - 1];
    for (const h of arr) line = line.slice(0, h.col) + h.to + line.slice(h.col + h.from.length);
    lines[lineNo - 1] = line;
  }
}

/* --- клас (2): сирий LaTeX поза кодом -------------------------------------- */
const LATEX_PATTERNS = [
  /\$[^$\n]+\$/g,
  /\\\([^)\n]*\\\)/g,
  /\\\[[^\]\n]*\\\]/g,
  /\\text\{[^}]*\}/g,
  /\\frac\{[^}]*\}\{[^}]*\}/g,
  /\\sqrt\{[^}]*\}/g,
  /\\mathbb\{[^}]*\}/g,
  /\\le\b/g,
  /\\ge\b/g,
  /\\in\b/g,
  /\\cdot\b/g,
  /\\log_2\b/g,
  /\\bmod\b/g,
];
function scanLatex(lines) {
  const hits = [];
  let inFence = false;
  lines.forEach((line, idx) => {
    if (/^\s*```/.test(line)) { inFence = !inFence; return; }
    if (inFence) return;
    // маскуємо інлайн-код, щоб не ловити $ у прикладах shell-коду
    const masked = line.replace(/`[^`]*`/g, (s) => " ".repeat(s.length));
    for (const re of LATEX_PATTERNS) {
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(masked))) hits.push({ lineNo: idx + 1, frag: m[0] });
    }
  });
  return hits;
}

/* --- клас (3): склейки кирилиця+латиниця та русизми ------------------------ */
const SPLICE_RE = new RegExp(`[${CYR}]{2,}[a-zA-Z]{3,}|[a-zA-Z]{3,}[${CYR}]{2,}`, "g");
const RUSISM_LIST = [
  "преємник", "розпреділ", "приймаюч", "учбов", "наглядн", "співпадан", "співпада", "міроприємст",
  "получ", "обраховув", "вияснит", "слідуюч", "в залежності", "по крайній мірі", "в кінці кінців",
  "дешежч", "багатаяд", "реаллок", "засув", "кольц", "у очікуванні", "прийшлось",
];
function scanSplicesAndRusisms(lines) {
  const splices = [], rusisms = [];
  let inFence = false;
  lines.forEach((line, idx) => {
    if (/^\s*```/.test(line)) { inFence = !inFence; return; }
    if (inFence) return;
    const prot = protectedRanges(line);
    let m;
    SPLICE_RE.lastIndex = 0;
    while ((m = SPLICE_RE.exec(line))) {
      const s = m.index, e = s + m[0].length;
      if (isProtected(prot, s, e)) continue;
      splices.push({ lineNo: idx + 1, frag: m[0] });
    }
    const low = line.toLowerCase();
    for (const term of RUSISM_LIST) {
      let from = 0, p;
      while ((p = low.indexOf(term, from)) !== -1) {
        if (!isProtected(prot, p, p + term.length)) {
          const cs = Math.max(0, p - 40), ce = Math.min(line.length, p + term.length + 40);
          rusisms.push({ lineNo: idx + 1, term, context: line.slice(cs, ce).trim() });
        }
        from = p + term.length;
      }
    }
  });
  return { splices, rusisms };
}

/* --- клас (4): SVG — осиротілі/биті/тека без figs.py ------------------------ */
function scanSvg(mdByDir) {
  const orphaned = [], broken = [], noFigs = [];
  for (const [dir, files] of mdByDir) {
    const imgDir = path.join(dir, "img");
    const referenced = new Set();
    for (const f of files) {
      const txt = fs.readFileSync(f, "utf8");
      const re = /img\/([A-Za-z0-9_\-]+\.svg)/g;
      let m;
      while ((m = re.exec(txt))) referenced.add(m[1]);
    }
    const actual = new Set();
    if (fs.existsSync(imgDir)) {
      for (const e of fs.readdirSync(imgDir, { withFileTypes: true })) {
        if (e.isFile() && e.name.endsWith(".svg")) actual.add(e.name);
      }
    }
    for (const r of referenced) if (!actual.has(r)) broken.push({ dir, file: r });
    for (const a of actual) if (!referenced.has(a)) orphaned.push({ dir, file: a });
    const hasFigsPy = fs.existsSync(path.join(dir, "figs.py"));
    if (!hasFigsPy) noFigs.push({ dir });
  }
  return { orphaned, broken, noFigs };
}

/* --- клас (5): недобір обсягу (слова РАЗОМ із кодом) ------------------------ */
function countAllWords(txt) {
  const m = txt.match(/[\p{L}\p{N}’'\-]+/gu);
  return m ? m.length : 0;
}
function classifyForVolume(file) {
  const base = path.basename(file, ".md");
  const dir = path.basename(path.dirname(file));
  if (base === dir + "-d") return { kind: "detailed", threshold: 1000 };
  if (base === dir) return { kind: "basic", threshold: 500 };
  if (/^(hist|comp|math|proj|api)-/.test(base)) return { kind: "insert", threshold: 400 };
  return null;
}
function scanVolume(files) {
  const rows = [];
  for (const f of files) {
    const cls = classifyForVolume(f);
    if (!cls) continue;
    const words = countAllWords(fs.readFileSync(f, "utf8"));
    if (words >= cls.threshold) continue;
    const nearMiss = words >= cls.threshold * 0.9;
    rows.push({ file: f, kind: cls.kind, words, threshold: cls.threshold, mark: nearMiss ? "~" : "✖" });
  }
  return rows;
}

/* ============================== ГОЛОВНЕ ==================================== */
const files = walk(root, []);
const mdByDir = new Map();
for (const f of files) {
  const d = path.dirname(f);
  (mdByDir.get(d) || mdByDir.set(d, []).get(d)).push(f);
}

let totalHomo = 0, totalLatex = 0, totalSplice = 0, totalRusism = 0;
const allHomoByFile = new Map();

console.log(`\n== textcheck: ${root} == (файлів .md: ${files.length})`);

console.log(`\n--- (1) ГОМОГЛІФИ ---`);
for (const f of files) {
  const rel = path.relative(process.cwd(), f);
  const raw = fs.readFileSync(f, "utf8");
  const lines = raw.split(/\r?\n/);
  const hits = scanHomoglyphs(lines);
  if (!hits.length) continue;
  totalHomo += hits.length;
  allHomoByFile.set(f, { lines, hits, hadCRLF: /\r\n/.test(raw) });
  for (const h of hits) console.log(`  ${rel}:${h.lineNo}  ${h.from} → ${h.to}`);
}
console.log(`  Разом: ${totalHomo}`);

if (apply && totalHomo) {
  for (const [f, { lines, hits, hadCRLF }] of allHomoByFile) {
    applyHomoglyphs(lines, hits);
    const eol = hadCRLF ? "\r\n" : "\n";
    fs.writeFileSync(f, lines.join(eol), "utf8");
  }
  console.log(`  → застосовано --apply: файлів змінено ${allHomoByFile.size}`);
}

console.log(`\n--- (2) LaTeX поза кодом ---`);
for (const f of files) {
  const rel = path.relative(process.cwd(), f);
  const lines = fs.readFileSync(f, "utf8").split(/\r?\n/);
  const hits = scanLatex(lines);
  totalLatex += hits.length;
  for (const h of hits) console.log(`  ${rel}:${h.lineNo}  ${h.frag}`);
}
console.log(`  Разом: ${totalLatex}`);

console.log(`\n--- (3) СКЛЕЙКИ / РУСИЗМИ ---`);
for (const f of files) {
  const rel = path.relative(process.cwd(), f);
  const lines = fs.readFileSync(f, "utf8").split(/\r?\n/);
  const { splices, rusisms } = scanSplicesAndRusisms(lines);
  totalSplice += splices.length; totalRusism += rusisms.length;
  for (const s of splices) console.log(`  [склейка] ${rel}:${s.lineNo}  ${s.frag}`);
  for (const r of rusisms) console.log(`  [русизм]  ${rel}:${r.lineNo}  «${r.term}» … ${r.context}`);
}
console.log(`  Разом: склейки ${totalSplice} · русизми ${totalRusism}`);

console.log(`\n--- (4) SVG ---`);
const { orphaned, broken, noFigs } = scanSvg(mdByDir);
for (const o of orphaned) console.log(`  [осиротіла] ${path.relative(process.cwd(), o.dir)}/img/${o.file}`);
for (const b of broken) console.log(`  [бита]      ${path.relative(process.cwd(), b.dir)} → img/${b.file} (нема файлу)`);
for (const n of noFigs) console.log(`  [без figs.py] ${path.relative(process.cwd(), n.dir)}`);
console.log(`  Разом: осиротілих ${orphaned.length} · битих ${broken.length} · без figs.py ${noFigs.length}`);

console.log(`\n--- (5) НЕДОБІР ОБСЯГУ (на перевірку, слова разом із кодом) ---`);
const volRows = scanVolume(files);
for (const r of volRows) console.log(`  ${r.mark} ${path.relative(process.cwd(), r.file)}  ${r.words}w / поріг ${r.threshold} (${r.kind})`);
console.log(`  Разом: ${volRows.length}`);

console.log(`\n== Підсумок ==  гомогліфи ${totalHomo} · LaTeX ${totalLatex} · склейки ${totalSplice} · русизми ${totalRusism} · SVG(осирот./бит./без-figs) ${orphaned.length}/${broken.length}/${noFigs.length} · недобір ${volRows.length}${apply ? "  [--apply застосовано до класу 1]" : ""}`);
