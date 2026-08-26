#!/usr/bin/env node
/* ============================================================================
   build-search-index.js (v7) — генератор пошукового індексу для сайту-бібліотеки.
   Обходить дерево root/ через root/shelf.json (види sci·eng·course·hw·sys →
   книги → групи → розділи → теми), читає доступні статті (`status:"done"`)
   разом із вставками (hist/comp/math/proj) і пише ДВА файли поруч із рушієм:

     search-index.json     — Рівень 1: назви (книга · галузь · тема) + заголовки
                             статей. Малий → вантажиться на кожній сторінці.
     search-fulltext.json  — Рівень 2: унікальні токени тіла КОЖНОЇ статті
                             (паралельний масив до Рівня 1) → довантажується на
                             першу спробу пошуку в тексті.

   Запуск:  node src/front/build-search-index.js
   Без сервера й без залежностей (лише вбудований fs/path).
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");        // корінь репо (скрипт живе в src/front/)
const CONTENT = path.join(ROOT, "root");              // дерево контенту v7
const OUT_INDEX = path.join(__dirname, "search-index.json");   // поруч із рушієм — його ж і фетчить search.js
const OUT_FULL = path.join(__dirname, "search-fulltext.json");

/* --- дерево v7: shelf.json → книги → групи ---------------------------------- */
function readJSON(file) {
  try { return JSON.parse(fs.readFileSync(file, "utf8")); } catch (e) { return null; }
}
function groupFile(g) { return (g === "." ? "_" : g) + ".json"; }

/* Написано ⟺ текст існує. `recheck`, `update` і `deeper` — це ГОТОВІ статті, лише
   позначені чернеткою: читач їх бачить, рушій їх віддає (`bookbuild.js:_written`).
   Доки тут стояло вузьке `=== "done"`, пошук мовчки не знав половини корпусу —
   2302 статті були на сайті, але не знаходилися. Означення має бути одне на всіх. */
function written(s) { return s === "done" || s === "update" || s === "deeper" || s === "recheck"; }

/* --- slugify (дзеркало book.js) --------------------------------------------- */
function slugify(s) {
  return String(s).toLowerCase().replace(/[^\wа-яіїєґ]+/gi, "-").replace(/^-+|-+$/g, "").slice(0, 48);
}

/* --- очищення markdown до плоского тексту ----------------------------------- */
function stripMd(t) {
  return String(t)
    .replace(/```[\s\S]*?```/g, " ")          // блоки коду
    .replace(/`[^`]*`/g, " ")                 // інлайн-код
    .replace(/\$\$[\s\S]*?\$\$/g, " ")        // блокові формули
    .replace(/\$[^$\n]*\$/g, " ")             // інлайн-формули
    .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")    // зображення
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")  // лінки → текст
    .replace(/[*_~>#|]+/g, " ")               // розмітка
    .replace(/\s+/g, " ")
    .trim();
}

/* --- токенізація: унікальні слова (укр/лат/цифри), довжина ≥ 3 --------------- */
function tokenize(text) {
  const seen = new Set();
  const parts = String(text).toLowerCase().replace(/['’ʼ`]/g, "").split(/[^0-9a-zа-яіїєґ]+/);   // прибрати апостроф ДО поділу (дзеркало norm() у search.js), інакше «зʼєднання» губиться
  for (const w of parts) if (w.length >= 3) seen.add(w);
  return seen;
}

/* --- заголовки статті: [{ t, a }] (a — якір лише для рівня ## ) -------------- */
function extractHeadings(md) {
  const out = [];
  const lines = md.split(/\r?\n/);
  let inFence = false;
  for (const ln of lines) {
    if (/^```/.test(ln)) { inFence = !inFence; continue; }
    if (inFence) continue;
    const m = ln.match(/^(#{1,4})\s+(.+?)\s*#*\s*$/);
    if (!m) continue;
    const level = m[1].length;
    const text = stripMd(m[2]);
    if (!text || level === 1) continue;         // H1 = назва статті (вже маємо з маніфесту)
    let anchor = "";
    if (level === 2) {
      const num = text.match(/^(\d+(?:\.\d+){1,2})\s+(.*)$/);   // «1.2 …» / «1.2.3 …»
      anchor = num ? "sec-" + num[1].split(".").join("-") : "h-" + slugify(text);
    }
    out.push({ t: num2plain(text), a: anchor });
  }
  return out;
}
function num2plain(text) { const m = text.match(/^\d+(?:\.\d+){1,2}\s+(.*)$/); return m ? m[1] : text; }

/* ---------------------------------------------------------------------------- */
const entries = [];   // Рівень 1
const docs = [];      // Рівень 2 (паралельний: docs[i] ↔ entries[i])
let filesRead = 0, missing = 0;

function readFileSafe(p) {
  try { filesRead++; return fs.readFileSync(p, "utf8"); }
  catch (e) { missing++; return ""; }
}

/* зібрати статтю: основний md + (опц.) детальний + вставки → entry + doc */
function addArticle(meta, dir, mainFile, detailedFile, insertFiles) {
  const mainMd = readFileSafe(path.join(dir, mainFile));
  if (!mainMd) return;
  let headings = extractHeadings(mainMd);
  const tokens = tokenize(stripMd(mainMd) + " " + meta.title);

  const insertHeads = [];
  for (const f of insertFiles) {
    const md = readFileSafe(path.join(dir, f));
    if (!md) continue;
    for (const h of extractHeadings(md)) { h.a = ""; insertHeads.push(h); }   // вставки — попапи, без прямого якоря
    for (const w of tokenize(stripMd(md))) tokens.add(w);
  }
  if (detailedFile) {
    const md = readFileSafe(path.join(dir, detailedFile));
    if (md) for (const w of tokenize(stripMd(md))) tokens.add(w);
  }
  headings = headings.concat(insertHeads);

  entries.push({
    k: meta.k, b: meta.b, bt: meta.bt, sec: meta.sec,
    title: meta.title, href: meta.href,
    h: headings.slice(0, 40)
  });
  // Рівень 2 — унікальні токени, відсортовані, з обмеженням (стрим розміру)
  docs.push(Array.from(tokens).sort().slice(0, 800).join(" "));
}

/* --- обхід дерева v7 --------------------------------------------------------
   Теми лежать ПЛАСКО під книгою: root/<dir>/<book>/<topic>/<topic>.md.
   Крок-`ref` не індексуємо — це вказівник на тему іншої книги, яка вже в індексі. */
function indexBook(kind, dir, slug) {
  const bookDir = path.join(CONTENT, dir, slug);
  const man = readJSON(path.join(bookDir, "manifest.json"));
  if (!man) return false;
  const bt = man.title || slug;
  for (const g of man.groups || []) {
    const grp = readJSON(path.join(bookDir, groupFile(g)));
    if (!grp) continue;
    const secTitle = grp.title || grp.slug || "";
    for (const c of grp.chapters || []) {
      for (const t of c.topics || []) {
        if (!t || !t.slug) continue;                       // ref/місток — не стаття цієї книги
        // Доступна читачу ⟺ готова ХОЧ ОДНА версія. За каноном v6+ основна — ДЕТАЛЬНА,
        // базова часто `empty`, тож фільтр лише по basic лишав такі теми поза пошуком.
        const bDone = written(t.basic && t.basic.status);
        const dDone = written(t.detailed && t.detailed.status);
        if (!bDone && !dDone) continue;
        const tdir = path.join(bookDir, t.slug);
        const inserts = []
          .concat((t.hist || []), (t.comp || []), (t.math || []), (t.proj || []), (t.api || []))
          .map((o) => (typeof o === "string" ? o : o && o.file))
          .filter((f) => f && typeof f === "string");
        // головний файл — базова, якщо є; інакше детальна (вона й буде тим, що читач бачить)
        const mainFile = bDone ? t.slug + ".md" : t.slug + "-d.md";
        const detailed = (bDone && dDone) ? t.slug + "-d.md" : null;
        addArticle(
          { k: kind, b: slug, bt: bt, sec: secTitle, title: t.title || t.slug,
            href: "read.html?book=" + slug + "#ch=" + t.slug },
          tdir, mainFile, detailed, inserts
        );
      }
    }
  }
  return true;
}

/* --- прогін ----------------------------------------------------------------- */
const shelf = readJSON(path.join(CONTENT, "shelf.json"));
if (!shelf || !shelf.kinds) { console.error("root/shelf.json не прочитався"); process.exit(1); }
for (const k of shelf.kinds) {
  for (const slug of k.books || []) {
    if (!indexBook(k.kind, k.dir, slug)) console.warn("  пропущено (нема manifest.json): " + k.dir + "/" + slug);
  }
}

fs.writeFileSync(OUT_INDEX, JSON.stringify(entries));
fs.writeFileSync(OUT_FULL, JSON.stringify({ docs: docs }));

const kb = (p) => (fs.statSync(p).size / 1024).toFixed(0);
console.log("Статей проіндексовано: " + entries.length);
console.log("Файлів прочитано: " + filesRead + " (не знайдено: " + missing + ")");
console.log("search-index.json    : " + kb(OUT_INDEX) + " KB");
console.log("search-fulltext.json : " + kb(OUT_FULL) + " KB");
