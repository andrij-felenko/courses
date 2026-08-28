#!/usr/bin/env node
/* Дозведення пропущених оцінок у наявні списки scripts/_levels/.
   Ужиток: node scripts/levels-merge-missing.js --votes <тека> [--apply]

   Читає out-missing-topics-{A,B,C}.txt і out-missing-inserts-{A,B,C}.txt (рядки
   `слуг=N` та `ім'я.md=N`), відновлює той самий порядок, у якому їх складав
   генератор входу, і ДОПИСУЄ результат у <книга>.json/tsv та inserts/<книга>.json/tsv.

   Наявних записів не чіпає: дозведення — це добір, а не переоцінка.               */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("./lib/manifest7.js");
const L = require("./checks/_lib.js");

const argv = process.argv.slice(2);
const arg = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const VOTES = arg("--votes", "");
const APPLY = argv.includes("--apply");
if (!VOTES) { console.error("треба --votes <тека з out-missing-*.txt>"); process.exit(2); }

const MISS = JSON.parse(fs.readFileSync(path.join(VOTES, "missing.json"), "utf8"));
const wantT = new Set(MISS.topics.map((x) => x.book + "/" + x.slug));
const wantI = new Set(MISS.inserts.map((x) => x.book + "/" + x.slug + "/" + x.file));
const RATERS = ["A", "B", "C"];
const r2 = (x) => Math.round(x * 100) / 100;

function readVotes(kind) {
  const out = {};
  for (const r of RATERS) {
    const p = path.join(VOTES, `out-missing-${kind}-${r}.txt`);
    const seq = [];
    for (const ln of fs.readFileSync(p, "utf8").split(/\r?\n/)) {
      const m = ln.match(/^\s*([^=\s]+)\s*=\s*([1-5])\s*$/);
      if (m) seq.push([m[1], +m[2]]);
    }
    out[r] = seq;
  }
  return out;
}

/* Порядок — точно той, що будував генератор входу: книги за абеткою, далі групи,
   розділи й теми в порядку маніфесту. Інакше голоси лягли б не на ті одиниці.   */
const books = [...new Set([...MISS.topics.map((x) => x.book), ...MISS.inserts.map((x) => x.book)])].sort();
const seqT = [], seqI = [];
for (const BOOK of books) {
  const rec = M7.books().get(BOOK);
  if (!rec) continue;
  const b = M7.loadBook(rec.bookDir);
  if (!b) continue;
  for (const [gslug, g] of b.groups) {
    for (const ch of g.data.chapters || []) {
      for (const t of ch.topics || []) {
        if (!t.slug) continue;
        const st = (t.detailed && t.detailed.status) || (t.basic && t.basic.status) || "";
        if (st === "pending" || st === "empty") continue;
        const dir = path.join(rec.bookDir, t.slug);
        if (wantT.has(BOOK + "/" + t.slug))
          seqT.push({ book: BOOK, kind: rec.kind, slug: t.slug, title: t.title || t.slug,
                      group: g.data.title || gslug, chapter: ch.title || ch.slug, dir, node: t });
        for (const type of M7.INSERT_TYPES) for (const i of t[type] || []) {
          const p = path.join(dir, i.file);
          if (!fs.existsSync(p)) continue;
          if (wantI.has(BOOK + "/" + t.slug + "/" + i.file))
            seqI.push({ book: BOOK, kind: rec.kind, topic: t.slug, title: t.title || t.slug,
                        group: g.data.title || gslug, file: i.file, type, path: p });
        }
      }
    }
  }
}

/* Рівень, який ВИТРИМУЄ наявний обсяг. */
function levelOfSize(kind, n) {
  let lv = 0;
  for (let i = 1; i <= L.LEVELS; i++) if (n >= L.bandOf(kind, i).floor) lv = i;
  return lv;
}
function levelOfCode(n) { let lv = 0; for (let i = 1; i <= L.LEVELS; i++) if (n >= L.CODE_FLOOR.low[i - 1]) lv = i; return lv; }

function fold(seq, votes, label) {
  const bad = RATERS.filter((r) => votes[r].length !== seq.length);
  if (bad.length) {
    console.error(`✖ ${label}: чекали ${seq.length}, маємо ` + bad.map((r) => `${r}=${votes[r].length}`).join(" "));
    return null;
  }
  return seq.map((ref, i) => {
    const v = RATERS.map((r) => votes[r][i][1]);
    const mean = r2(v.reduce((a, c) => a + c, 0) / v.length);
    return { ref, votes: v, mean, level: L.clampLevel(Math.round(mean)), spread: Math.max(...v) - Math.min(...v) };
  });
}

const T = fold(seqT, readVotes("topics"), "теми");
const I = fold(seqI, readVotes("inserts"), "вставки");
if (!T || !I) process.exit(1);

/* ── теми: обсяг детальної проти смуги detailed ───────────────────────────── */
const byBookT = {};
for (const r of T) {
  const d = path.join(r.ref.dir, r.ref.slug + "-d.md");
  const words = fs.existsSync(d) ? L.proseWords(L.read(d)) : null;
  const real = words === null ? null : levelOfSize("detailed", words);
  (byBookT[r.ref.book] = byBookT[r.ref.book] || []).push({
    slug: r.ref.slug, title: r.ref.title, group: r.ref.group, chapter: r.ref.chapter,
    votes: r.votes, mean: r.mean, level: r.level, spread: r.spread,
    words, realLevel: real, delta: real === null ? null : r.level - real,
  });
}

/* ── вставки: проза за своєю смугою + код для proj/api ────────────────────── */
const byBookI = {};
for (const r of I) {
  const md = L.read(r.ref.path);
  const words = L.proseWords(md);
  const band = L.bandOf(r.ref.type, r.level);
  const real = levelOfSize(r.ref.type, words);
  const dirs = L.langDirsOf(path.dirname(r.ref.path), r.ref.file);
  const code = L.NEEDS_CODE.has(r.ref.type)
    ? (dirs.length ? dirs.reduce((a, d) => a + L.codeLinesOfDir(d.dir).lines, 0) : L.codeLines(md)) : null;
  const codeReal = code === null ? null : levelOfCode(code);
  (byBookI[r.ref.book] = byBookI[r.ref.book] || []).push({
    topic: r.ref.topic, title: r.ref.title, group: r.ref.group, file: r.ref.file, type: r.ref.type,
    votes: r.votes, mean: r.mean, level: r.level, spread: r.spread,
    words, real, delta: r.level - real, floor: band.floor, max: band.max,
    code, codeFloor: band.needsCode ? L.CODE_FLOOR.low[r.level - 1] : null,
    codeReal, codeDelta: codeReal === null ? null : r.level - codeReal,
  });
}

/* ── дозапис ──────────────────────────────────────────────────────────────── */
const DIR = path.join(__dirname, "_levels");
function merge(sub, book, rows, keyOf, headers, rowOf) {
  const base = sub ? path.join(DIR, sub) : DIR;
  fs.mkdirSync(base, { recursive: true });
  const jp = path.join(base, `${book}.json`);
  let j = null;
  try { j = JSON.parse(fs.readFileSync(jp, "utf8")); } catch { }
  const listKey = sub ? "inserts" : "topics";
  if (!j) j = { book, kind: rows[0].kind || "", raters: RATERS, [listKey]: [] };
  const have = new Set((j[listKey] || []).map(keyOf));
  let added = 0;
  for (const r of rows) if (!have.has(keyOf(r))) { j[listKey].push(r); added++; }
  if (!APPLY) return added;
  fs.writeFileSync(jp, JSON.stringify(j, null, 1), "utf8");
  const tp = path.join(base, `${book}.tsv`);
  fs.writeFileSync(tp, [headers.join("\t"), ...j[listKey].map(rowOf)].join("\n") + "\n", "utf8");
  return added;
}

let addT = 0, addI = 0;
console.log("книга                 тем  вставок");
for (const book of books) {
  const rt = byBookT[book] || [], ri = byBookI[book] || [];
  const a = rt.length ? merge("", book, rt,
    (x) => x.slug,
    ["слуг", "назва", "група", "розділ", "A", "B", "C", "середня", "рівень", "слів", "Рфакт", "Δ"],
    (x) => [x.slug, x.title, x.group, x.chapter, ...(x.votes || ["", "", ""]), x.mean, x.level, x.words ?? "", x.realLevel ?? "", x.delta ?? ""].join("\t")) : 0;
  const b = ri.length ? merge("inserts", book, ri,
    (x) => x.topic + "/" + x.file,
    ["тема", "група", "файл", "тип", "A", "B", "C", "середня", "рівень", "слів", "підлога", "Рфакт", "Δ", "коду", "підлКод", "Ркод", "Δкод"],
    (x) => [x.topic, x.group, x.file, x.type, ...(x.votes || ["", "", ""]), x.mean, x.level, x.words ?? "", x.floor ?? "", x.real ?? "", x.delta ?? "", x.code ?? "", x.codeFloor ?? "", x.codeReal ?? "", x.codeDelta ?? ""].join("\t")) : 0;
  addT += a; addI += b;
  if (a || b) console.log("  " + book.padEnd(20) + String(a).padStart(4) + String(b).padStart(9));
}
console.log(`\n${APPLY ? "ДОПИСАНО" : "БУЛО Б ДОПИСАНО"}: тем ${addT} · вставок ${addI}`);
if (!APPLY) console.log("(додай --apply, щоб записати)");
