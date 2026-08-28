#!/usr/bin/env node
/* ============================================================================
   newtopics-judge-prep.js — з payload-у аудиту робить ПАКЕТИ для суддів.

   Мета — щоб агент не читав ні репо, ні канон: усе потрібне лежить в одному
   файлі. Тому в пакет кладемо (а) нові теми з локальними ознаками, (б) сусідів
   по РОЗДІЛУ — лише слуг і назву, без тіл. Книги з великим внеском дістають свій
   пакет, хвіст із 1–6 тем групується, щоб не наймати агента на одну тему.

   Запуск:  node scripts/newtopics-judge-prep.js [--big 10] [--out scripts/_judge]
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const argv = process.argv.slice(2);
const val = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d };
const BIG = Number(val("--big", 10));
const OUT = path.resolve(ROOT, val("--out", "scripts/_judge"));

const NEW = JSON.parse(fs.readFileSync(path.join(ROOT, "scripts/_newtopics-audit.json"), "utf8"));

/* сусіди по розділу — з поточних маніфестів, лише слуг + назва */
const CH = new Map();                    // "<книга>/<розділ>" -> [{slug,title,st}]
const BOOKMETA = new Map();
for (const kind of fs.readdirSync(path.join(ROOT, "root"))) {
  const kdir = path.join(ROOT, "root", kind);
  if (!fs.statSync(kdir).isDirectory()) continue;
  for (const book of fs.readdirSync(kdir)) {
    const bdir = path.join(kdir, book);
    if (!fs.statSync(bdir).isDirectory()) continue;
    let title = book;
    try { title = JSON.parse(fs.readFileSync(path.join(bdir, "manifest.json"), "utf8")).title || book } catch (e) { }
    BOOKMETA.set(book, { kind, title });
    for (const f of fs.readdirSync(bdir)) {
      if (!f.endsWith(".json") || f === "manifest.json") continue;
      let j; try { j = JSON.parse(fs.readFileSync(path.join(bdir, f), "utf8")) } catch (e) { continue }
      for (const ch of (j.chapters || [])) {
        const key = book + "/" + ch.slug;
        const list = CH.get(key) || CH.set(key, []).get(key);
        for (const t of (ch.topics || [])) {
          if (t.ref || !t.slug) continue;
          const ds = (t.detailed && t.detailed.status) || "empty";
          const bs = (t.basic && t.basic.status) || "empty";
          list.push({ slug: t.slug, title: t.title || t.slug, written: ds !== "empty" && ds !== "pending" || bs !== "empty" && bs !== "pending" });
        }
      }
    }
  }
}

/* збірка по книгах */
const byBook = {};
for (const n of NEW) (byBook[n.book] = byBook[n.book] || []).push(n);

function pack(books) {
  const items = [];
  const chapters = {};
  for (const b of books)
    for (const n of byBook[b]) {
      const key = n.book + "/" + n.chapter;
      if (!chapters[key]) chapters[key] = { book: n.book, kindOfBook: BOOKMETA.get(n.book) ? BOOKMETA.get(n.book).kind : n.kind, bookTitle: BOOKMETA.get(n.book) ? BOOKMETA.get(n.book).title : n.book, chapter: n.chapter, chapterTitle: n.chapterTitle, existing: (CH.get(key) || []).filter((t) => !byBook[n.book].some((x) => x.slug === t.slug)).map((t) => t.slug + " — " + t.title) };
      items.push({ id: n.book + "/" + n.slug, book: n.book, chapter: n.chapter, slug: n.slug, title: n.title,
        mentionsInBookProse: n.mentions, similarNearby: n.near, localFlags: n.flags });
    }
  return { chapters: Object.values(chapters), topics: items };
}

const big = Object.keys(byBook).filter((b) => byBook[b].length >= BIG).sort((a, b) => byBook[b].length - byBook[a].length);
const tail = Object.keys(byBook).filter((b) => byBook[b].length < BIG);
// хвіст — групами по видах, щоб один агент бачив споріднені книги
const tailByKind = {};
for (const b of tail) (tailByKind[(BOOKMETA.get(b) || { kind: "?" }).kind] = tailByKind[(BOOKMETA.get(b) || { kind: "?" }).kind] || []).push(b);

fs.mkdirSync(OUT, { recursive: true });
for (const f of fs.readdirSync(OUT)) if (f.startsWith("pack-")) fs.unlinkSync(path.join(OUT, f));

const packs = [];
for (const b of big) packs.push({ name: b, books: [b] });
for (const [kind, books] of Object.entries(tailByKind)) {
  // не більше ~25 тем на пакет
  let cur = [];
  let n = 0;
  for (const b of books) {
    if (n && n + byBook[b].length > 25) { packs.push({ name: "hvist-" + kind + "-" + (packs.length), books: cur }); cur = []; n = 0 }
    cur.push(b); n += byBook[b].length;
  }
  if (cur.length) packs.push({ name: "hvist-" + kind, books: cur });
}

let total = 0;
for (const p of packs) {
  const data = pack(p.books);
  const file = path.join(OUT, "pack-" + p.name + ".json");
  fs.writeFileSync(file, JSON.stringify(data, null, 1), "utf8");
  const kb = Math.round(fs.statSync(file).size / 1024);
  total += data.topics.length;
  console.log(("pack-" + p.name).padEnd(30) + String(data.topics.length).padStart(4) + " тем · книг " + String(p.books.length).padStart(2) + " · " + String(kb).padStart(4) + " КБ");
}
console.log("\n  пакетів " + packs.length + " · тем " + total + " → " + path.relative(ROOT, OUT));
