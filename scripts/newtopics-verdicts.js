#!/usr/bin/env node
/* ============================================================================
   newtopics-verdicts.js — звіт по вироках суддів + ПЕРЕВІРКА цілей.

   Агент бачив лише свій пакет, тож ціль merge/insert/move він міг назвати з
   голови. Тут кожна ціль звіряється з корпусом: слуг має існувати (для merge й
   insert — у тій самій книзі, для move — книга має існувати й бути іншого виду).
   Ціль, якої нема, — це не вирок, а здогад: такі позначаємо ✖ і не виконуємо.

   Запуск:  node scripts/newtopics-verdicts.js <task.output> [--json out.json]
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const argv = process.argv.slice(2);
const SRC = argv.find((a) => !a.startsWith("--"));
const jsonAt = argv.indexOf("--json");
const jsonOut = jsonAt >= 0 ? argv[jsonAt + 1] : path.join(ROOT, "scripts/_newtopics-verdicts.json");

/* витягаємо масив verdicts із виводу задачі (він у JSON-і результату) */
const raw = fs.readFileSync(SRC, "utf8");
const i = raw.indexOf('"verdicts"');
if (i < 0) { console.error("нема verdicts у " + SRC); process.exit(1) }
let depth = 0, start = raw.indexOf("[", i), end = -1;
for (let k = start; k < raw.length; k++) {
  if (raw[k] === "[") depth++;
  else if (raw[k] === "]") { depth--; if (!depth) { end = k + 1; break } }
}
const V = JSON.parse(raw.slice(start, end));

/* індекс корпусу */
const SLUGS = new Map();          // book -> Set(slug)
const BOOKS = new Map();          // book -> kind
for (const kind of fs.readdirSync(path.join(ROOT, "root"))) {
  const kdir = path.join(ROOT, "root", kind);
  if (!fs.statSync(kdir).isDirectory()) continue;
  for (const book of fs.readdirSync(kdir)) {
    const bdir = path.join(kdir, book);
    if (!fs.statSync(bdir).isDirectory()) continue;
    BOOKS.set(book, kind);
    const set = SLUGS.set(book, new Set()).get(book);
    for (const f of fs.readdirSync(bdir)) {
      if (!f.endsWith(".json") || f === "manifest.json") continue;
      let j; try { j = JSON.parse(fs.readFileSync(path.join(bdir, f), "utf8")) } catch (e) { continue }
      for (const ch of (j.chapters || [])) for (const t of (ch.topics || [])) if (t.slug) set.add(t.slug);
    }
  }
}
const KINDS = new Set(fs.readdirSync(path.join(ROOT, "root")).filter((d) => fs.statSync(path.join(ROOT, "root", d)).isDirectory()));

/* перевірка цілей */
for (const v of V) {
  const [book] = v.id.split("/");
  v.book = book;
  if (v.verdict === "keep" || v.verdict === "drop" || v.verdict === "unsure") { v.targetOk = null; continue }
  if (!v.target) { v.targetOk = false; v.targetNote = "ціль не названо"; continue }
  if (v.verdict === "move") {
    if (KINDS.has(v.target)) { v.targetOk = "kind"; v.targetNote = "названо ВИД, не книгу" }
    else if (BOOKS.has(v.target)) { v.targetOk = true; v.targetNote = "книга " + BOOKS.get(v.target) + "/" + v.target }
    else { v.targetOk = false; v.targetNote = "такої книги нема" }
    continue;
  }
  const set = SLUGS.get(book) || new Set();
  v.targetOk = set.has(v.target);
  if (!v.targetOk) {
    const other = [...BOOKS.keys()].filter((b) => b !== book && (SLUGS.get(b) || new Set()).has(v.target));
    v.targetNote = other.length ? "слуга нема в " + book + ", але є в " + other.join(", ") : "такого слуга нема ніде";
  }
}

/* звіт */
const order = { merge: 1, move: 2, insert: 3, drop: 4, unsure: 5, keep: 9 };
const act = V.filter((v) => v.verdict !== "keep").sort((a, b) => (order[a.verdict] - order[b.verdict]) || a.id.localeCompare(b.id));
const cnt = {};
for (const v of V) cnt[v.verdict] = (cnt[v.verdict] || 0) + 1;

console.log("\n== ВИРОКИ ==  усього " + V.length + " · " + Object.entries(cnt).map(([k, n]) => k + " " + n).join(" · "));
console.log("\nДО ДІЇ (" + act.length + "):\n");
let lastV = "";
for (const v of act) {
  if (v.verdict !== lastV) { console.log("-- " + v.verdict.toUpperCase() + " --"); lastV = v.verdict }
  const mark = v.targetOk === true ? "✓" : v.targetOk === null ? " " : v.targetOk === "kind" ? "▲" : "✖";
  const tgt = v.target ? " → " + v.target : "";
  console.log("  " + mark + " " + (v.id + tgt).padEnd(74) + " " + v.reason + (v.targetOk === true || v.targetOk === null ? "" : "   [" + v.targetNote + "]"));
}
const bad = act.filter((v) => v.targetOk === false || v.targetOk === "kind");
console.log("\n  цілей не існує або названо неточно: " + bad.length + " — ці вироки виконувати НЕ можна без уточнення");
fs.writeFileSync(jsonOut, JSON.stringify(V, null, 1), "utf8");
console.log("  повний список → " + path.relative(ROOT, jsonOut));
