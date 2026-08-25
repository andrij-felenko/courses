#!/usr/bin/env node
/* ============================================================================
   stats.js — числа корпусу, пораховані з дерева `root/` просто зараз.

   НАВІЩО. Числа в CLAUDE.md і BOOKS.md були набрані руками, а єдиний генератор
   (`scripts/migrate/books-md.js`) читав старе дерево `book/`+`catalog/`+`reference/`
   і після переїзду на v7 рахує нулі. Наслідок передбачуваний: BOOKS.md обіцяв
   5271 тему, коли в маніфестах їх 6555, а CLAUDE.md описував курси числами,
   старшими за дві перебудови. Цифра в прозі застаріває мовчки — тому єдине
   надійне місце для неї це скрипт, а в прозі має стояти згенерований блок.

   Ужиток:
     node scripts/stats.js              звіт у консоль
     node scripts/stats.js --md         той самий звіт як markdown-блок
     node scripts/stats.js --apply      вписати блок у файли з маркерами

   МАРКЕРИ. Скрипт переписує рівно те, що лежить між рядками

       <!-- STATS:BEGIN --> … <!-- STATS:END -->

   у кожному файлі зі списку TARGETS. Решти файла не торкається. Немає маркерів —
   скрипт каже про це й нічого не пише: додати блок у потрібне місце має людина.

   ЩО ВВАЖАЄМО НАПИСАНИМ. Статуси `done`/`update`/`deeper`/`recheck` означають,
   що файл на диску є (рушій показує їх, чернетки — з позначкою). `pending` —
   треба написати, `empty` — писати не треба. Тому «написано» ≠ «done».
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const M = require("./lib/manifest7.js");

const WRITTEN = new Set(["done", "update", "deeper", "recheck"]);
const TARGETS = ["CLAUDE.md", "BOOKS.md"];
const BEGIN = "<!-- STATS:BEGIN -->";
const END = "<!-- STATS:END -->";
/* Другий блок — поіменний реєстр книг. Його маркери має тільки BOOKS.md:
   у CLAUDE.md шістдесят шість рядків не потрібні, там доречне зведення. */
const B_BEGIN = "<!-- STATS:BOOKS:BEGIN -->";
const B_END = "<!-- STATS:BOOKS:END -->";

/* ── збір ──────────────────────────────────────────────────────────────────── */
function collect() {
  const shelf = M.shelf();
  const kinds = [];
  for (const k of shelf.kinds) {
    const kind = { kind: k.kind, dir: k.dir, shelf: k.shelf, words: k.words || {}, books: [] };
    for (const slug of k.books) {
      const dir = path.join(M.CONTENT, k.dir, slug);
      const book = M.loadBook(dir);
      if (!book) { kind.books.push({ slug, missing: true }); continue; }
      const b = { slug, title: book.manifest.title, groups: 0, chapters: 0,
                  topics: 0, written: 0, done: 0, pending: 0, refs: 0 };
      for (const [, g] of book.groups) {
        b.groups++;
        for (const c of g.data.chapters || []) {
          b.chapters++;
          for (const t of c.topics || []) {
            if (t.ref) { b.refs++; continue; }
            b.topics++;
            const bs = (t.basic || {}).status, ds = (t.detailed || {}).status;
            if (WRITTEN.has(bs) || WRITTEN.has(ds)) b.written++;
            if (bs === "done" || ds === "done") b.done++;
            if (bs === "pending" || ds === "pending") b.pending++;
          }
        }
      }
      b.steps = b.topics + b.refs;
      kind.books.push(b);
    }
    kinds.push(kind);
  }
  return kinds;
}

const sum = (arr, f) => arr.reduce((n, x) => n + (x[f] || 0), 0);

/* ── звіт ──────────────────────────────────────────────────────────────────── */
function report(kinds) {
  const out = [];
  const all = kinds.flatMap((k) => k.books.filter((b) => !b.missing));
  for (const k of kinds) {
    const bs = k.books.filter((b) => !b.missing);
    const miss = k.books.filter((b) => b.missing).map((b) => b.slug);
    out.push("");
    out.push(`${k.shelf}  (${k.kind})  книг ${bs.length}`);
    for (const b of bs.slice().sort((x, y) => y.topics - x.topics)) {
      const ref = b.refs ? `  ref ${String(b.refs).padStart(4)}` : "";
      out.push(`   ${b.slug.padEnd(20)} груп ${String(b.groups).padStart(2)}` +
               `  розд ${String(b.chapters).padStart(3)}` +
               `  тем ${String(b.topics).padStart(4)}` +
               `  написано ${String(b.written).padStart(4)}` +
               `  чекає ${String(b.pending).padStart(4)}${ref}`);
    }
    if (miss.length) out.push(`   ⚠ нема на диску: ${miss.join(", ")}`);
  }
  out.push("");
  out.push(`РАЗОМ: книг ${all.length} · груп ${sum(all, "groups")} · розділів ${sum(all, "chapters")}` +
           ` · тем ${sum(all, "topics")} · написано ${sum(all, "written")}` +
           ` (з них done ${sum(all, "done")}) · чекає письма ${sum(all, "pending")}` +
           ` · ref-кроків у курсах ${sum(all, "refs")}`);
  return out.join("\n");
}

/* ── markdown-блок ─────────────────────────────────────────────────────────── */
function markdown(kinds) {
  const all = kinds.flatMap((k) => k.books.filter((b) => !b.missing));
  const L = [];
  L.push(BEGIN);
  L.push("<!-- згенеровано `node scripts/stats.js --apply` — руками не правити -->");
  L.push("");
  L.push("**Числа корпусу.** Пораховано з маніфестів `root/`; «написано» = файл на диску");
  L.push("(`done`/`update`/`deeper`/`recheck`), «чекає» = `pending`.");
  L.push("");
  L.push("| вид | книг | груп | розділів | тем | написано | чекає |");
  L.push("|---|---:|---:|---:|---:|---:|---:|");
  for (const k of kinds) {
    const bs = k.books.filter((b) => !b.missing);
    if (!bs.length) continue;
    L.push(`| ${k.shelf} \`${k.kind}\` | ${bs.length} | ${sum(bs, "groups")} | ${sum(bs, "chapters")}` +
           ` | ${sum(bs, "topics")} | ${sum(bs, "written")} | ${sum(bs, "pending")} |`);
  }
  L.push(`| **разом** | **${all.length}** | **${sum(all, "groups")}** | **${sum(all, "chapters")}**` +
         ` | **${sum(all, "topics")}** | **${sum(all, "written")}** | **${sum(all, "pending")}** |`);

  const courses = (kinds.find((k) => k.kind === "course") || { books: [] }).books.filter((b) => !b.missing);
  if (courses.length) {
    L.push("");
    L.push("**Курси** — крок це або `ref` на чужу статтю, або власна стаття курсу:");
    L.push("");
    L.push("| курс | назва | томів | розділів | кроків | ref | власних | написано |");
    L.push("|---|---|---:|---:|---:|---:|---:|---:|");
    for (const c of courses)
      L.push(`| \`${c.slug}\` | ${c.title} | ${c.groups} | ${c.chapters} | ${c.steps}` +
             ` | ${c.refs} | ${c.topics} | ${c.written} |`);
  }
  L.push(END);
  return L.join("\n");
}

/* ── поіменний реєстр книг ─────────────────────────────────────────────────── */
function booksMarkdown(kinds) {
  const L = [];
  L.push(B_BEGIN);
  L.push("<!-- згенеровано `node scripts/stats.js --apply` — руками не правити -->");
  for (const k of kinds) {
    const bs = k.books.filter((b) => !b.missing).sort((x, y) => y.topics - x.topics);
    if (!bs.length) continue;
    L.push("");
    L.push(`### ${k.shelf} \`${k.kind}\` — ${k.words.book || "книга"} · ${k.words.group || "група"} · ${k.words.chapter || "розділ"}`);
    L.push("");
    L.push("| слуг | назва | груп | тем | написано | чекає |");
    L.push("|---|---|---:|---:|---:|---:|");
    for (const b of bs)
      L.push(`| \`${b.slug}\` | ${b.title} | ${b.groups} | ${b.topics} | ${b.written} | ${b.pending} |`);
  }
  L.push(B_END);
  return L.join("\n");
}

/* ── запис у файли з маркерами ─────────────────────────────────────────────── */
function replaceBlock(src, begin, end, block) {
  const a = src.indexOf(begin), b = src.indexOf(end);
  if (a < 0 || b < 0 || b < a) return null;
  return src.slice(0, a) + block + src.slice(b + end.length);
}

function apply(block, booksBlock) {
  let touched = 0;
  for (const rel of TARGETS) {
    const p = path.join(M.ROOT, rel);
    if (!fs.existsSync(p)) { console.log(`   — ${rel}: нема файла`); continue; }
    const src = fs.readFileSync(p, "utf8");
    let next = replaceBlock(src, BEGIN, END, block);
    if (next === null) { console.log(`   — ${rel}: нема маркерів ${BEGIN} … ${END}, пропущено`); continue; }
    /* Другий блок необовʼязковий: нема маркерів — просто не чіпаємо файл. */
    const withBooks = replaceBlock(next, B_BEGIN, B_END, booksBlock);
    if (withBooks !== null) next = withBooks;
    if (next === src) { console.log(`   = ${rel}: без змін`); continue; }
    fs.writeFileSync(p, next, "utf8");
    console.log(`   ✓ ${rel}: оновлено${withBooks !== null ? " (зведення + реєстр книг)" : " (зведення)"}`);
    touched++;
  }
  return touched;
}

/* ── головне ───────────────────────────────────────────────────────────────── */
const argv = process.argv.slice(2);
const kinds = collect();
if (argv.includes("--apply")) {
  console.log("stats --apply:");
  apply(markdown(kinds), booksMarkdown(kinds));
} else if (argv.includes("--md")) {
  console.log(markdown(kinds));
  console.log("");
  console.log(booksMarkdown(kinds));
} else {
  console.log(report(kinds));
}
