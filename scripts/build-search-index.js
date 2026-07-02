#!/usr/bin/env node
/* ============================================================================
   build-search-index.js — генератор пошукового індексу для сайту-бібліотеки.
   Обходить book/ · catalog/ · guide/ (через маніфести), читає доступні статті
   (`status:"done"`) разом із вставками (hist/comp/math/proj) і власними
   статтями курсів, і пише ДВА файли в корінь репо:

     search-index.json     — Рівень 1: назви (книга · галузь · тема) + заголовки
                             статей. Малий → вантажиться на кожній сторінці.
     search-fulltext.json  — Рівень 2: унікальні токени тіла КОЖНОЇ статті
                             (паралельний масив до Рівня 1) → довантажується на
                             першу спробу пошуку в тексті.

   Запуск:  node scripts/build-search-index.js
   Без сервера й без залежностей (лише вбудований fs/path).
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const OUT_INDEX = path.join(ROOT, "search-index.json");
const OUT_FULL = path.join(ROOT, "search-fulltext.json");

/* --- реєстр книг/курсів (books-index.js) ------------------------------------ */
function loadRegistry() {
  const src = fs.readFileSync(path.join(ROOT, "books-index.js"), "utf8");
  const sb = {};                       // books-index.js робить window.SUBJECT_BOOKS = [...]
  new Function("window", src)(sb);
  return { books: sb.SUBJECT_BOOKS || [], guides: sb.GUIDE_COURSES || [] };
}

/* --- маніфест книги/курсу як об'єкт ----------------------------------------- */
function loadManifest(file, key) {
  if (!fs.existsSync(file)) return null;
  const src = fs.readFileSync(file, "utf8");
  const sb = {};
  try { new Function("window", src)(sb); } catch (e) { return null; }
  return (sb[key] || [])[0] || null;
}

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
  const parts = String(text).toLowerCase().split(/[^0-9a-zа-яіїєґ]+/);
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

/* --- book/ та catalog/ ------------------------------------------------------ */
function indexBook(slug, kind) {
  const base = kind === "catalog" ? "catalog" : "book";
  const man = loadManifest(path.join(ROOT, base, slug, "manifest.js"), "__BOOKS__");
  if (!man) return false;
  const bt = man.title || slug;
  (man.sections || []).forEach((sec) => {
    (sec.topics || []).forEach((t) => {
      if (!t.slug) return;
      const basicDone = t.basic && t.basic.status === "done";
      if (!basicDone) return;   // недоступні читачу — не індексуємо
      const dir = path.join(ROOT, base, slug, sec.slug, t.slug);
      const inserts = []
        .concat((t.hist || []), (t.comp || []), (t.math || []), (t.proj || []))
        .map((o) => (typeof o === "string" ? o : o && o.file))
        .filter((f) => f && typeof f === "string");
      const detailed = t.detailed && t.detailed.status === "done" ? t.slug + "-d.md" : null;
      addArticle(
        { k: kind, b: slug, bt: bt, sec: sec.title || sec.slug, title: t.title || t.slug,
          href: "read.html?book=" + slug + "#ch=" + t.slug },
        dir, t.slug + ".md", detailed, inserts
      );
    });
  });
  return true;
}

/* --- guide/ (лише власні статті `{slug}`; кроки `{ref}` — вказівники) -------- */
function indexGuide(slug) {
  const man = loadManifest(path.join(ROOT, "guide", slug, "manifest.js"), "__GUIDES__");
  if (!man) return;
  const gt = man.title || slug;
  (man.sections || man.modules || []).forEach((mod) => {
    const steps = (mod.topics && mod.topics.length) ? mod.topics : (mod.chapters || []).flatMap((c) => c.steps || []);
    steps.forEach((s) => {
      if (s.ref || !s.slug) return;             // ref → book-атом (уже проіндексований)
      const basicDone = s.basic && s.basic.status === "done";
      if (!basicDone) return;
      // власні статті курсу лежать як книжкові: guide/<курс>/<модуль>/<slug>/<slug>.md
      const dir = path.join(ROOT, "guide", slug, mod.slug, s.slug);
      const inserts = []
        .concat((s.hist || []), (s.comp || []), (s.math || []), (s.proj || []))
        .map((o) => (typeof o === "string" ? o : o && o.file))
        .filter((f) => f && typeof f === "string");
      const detailed = s.detailed && s.detailed.status === "done" ? s.slug + "-d.md" : null;
      addArticle(
        { k: "guide", b: slug, bt: gt, sec: mod.title || mod.slug, title: s.title || s.slug,
          href: "read.html?guide=" + slug + "&module=" + mod.slug + "#ch=" + s.slug },
        dir, s.slug + ".md", detailed, inserts
      );
    });
  });
}

/* --- прогін ----------------------------------------------------------------- */
const reg = loadRegistry();
reg.books.forEach((s) => { if (!indexBook(s, "book")) indexBook(s, "catalog"); });
// каталоги (окремий список у CLAUDE.md; спробуємо теку catalog/ якщо є)
["pcb-board", "sensor-board"].forEach((s) => indexBook(s, "catalog"));
reg.guides.forEach((s) => indexGuide(s));

fs.writeFileSync(OUT_INDEX, JSON.stringify(entries));
fs.writeFileSync(OUT_FULL, JSON.stringify({ docs: docs }));

const kb = (p) => (fs.statSync(p).size / 1024).toFixed(0);
console.log("Статей проіндексовано: " + entries.length);
console.log("Файлів прочитано: " + filesRead + " (не знайдено: " + missing + ")");
console.log("search-index.json    : " + kb(OUT_INDEX) + " KB");
console.log("search-fulltext.json : " + kb(OUT_FULL) + " KB");
