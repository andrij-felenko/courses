/* ⚠️ ЛЕГАСІ КАМПАНІЇ RECHECK (завершена 2026-07-25). Читає ПРИБРАНЕ дерево v6
   (book/ + guide/ + catalog/ + manifest.js із window.__BOOKS__), тож на дереві v7
   не працює — не запускай, доки не переписано. Живий конвеєр ревізії сьогодні:
   review-batch.js → review-queue.js → review-apply.js. */
/* scripts/recheck-index.js — допоміжник для recheck-аудиту.
   Парсить усі book/<book>/manifest.js і друкує JSON:
     { index:   { <book>: [<slug>, ...], ... },           // усі наявні slug-и (для валідації book:-лінків)
       titles:  { "<book>/<slug>": "<title>", ... },
       sections:{ <book>: [ {slug,title,scope}, ... ] },   // галузі книги (куди класти стаби)
       queue:   { <book>: [ {section, slug, title, status, levels, inserts:{hist,comp,math,proj}}, ... ] } }
   queue містить ЛИШЕ topic-и зі статусом recheck, у порядку маніфесту.
   Запуск:  node scripts/recheck-index.js            (усі книги)
            node scripts/recheck-index.js algorithms  (лише одна книга у queue) */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.resolve(__dirname, "..");
const BOOKS_DIR = path.join(ROOT, "book");
const onlyBook = process.argv[2] || null;

const books = [];
for (const slug of fs.readdirSync(BOOKS_DIR)) {
  const mf = path.join(BOOKS_DIR, slug, "manifest.js");
  if (!fs.existsSync(mf)) continue;
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync(mf, "utf8"), sandbox, { filename: mf });
  const arr = sandbox.window.__BOOKS__ || [];
  for (const b of arr) books.push(b);
}

const index = {}, titles = {}, sections = {}, queue = {}, lookup = {};
for (const b of books) {
  index[b.slug] = [];
  sections[b.slug] = (b.sections || []).map(s => ({ slug: s.slug, title: s.title, scope: s.scope }));
  queue[b.slug] = [];
  for (const sec of b.sections || []) {
    for (const t of sec.topics || []) {
      index[b.slug].push(t.slug);
      titles[`${b.slug}/${t.slug}`] = t.title;
      const inserts = {};
      for (const k of ["hist", "comp", "math", "proj"]) {
        if (Array.isArray(t[k]) && t[k].length) inserts[k] = t[k].map(x => ({ file: x.file, status: x.status }));
      }
      const rec = { book: b.slug, section: sec.slug, slug: t.slug, title: t.title, status: t.status, levels: t.levels || null, inserts };
      lookup[`${b.slug}/${sec.slug}/${t.slug}`] = rec;
      if (t.status === "recheck") queue[b.slug].push(rec);
    }
  }
}

const out = { index, titles, sections, lookup, queue: {} };
if (onlyBook) out.queue[onlyBook] = queue[onlyBook] || [];
else out.queue = queue;
process.stdout.write(JSON.stringify(out));
