#!/usr/bin/env node
/* ============================================================================
   dupes.js — ПІДКАЗКИ ПРО МОЖЛИВИЙ ДУБЛЬ ПОНЯТТЯ. Локально, точно, нуль токенів.

   ⛔ ЦЕ НЕ СУДДЯ. Об'єднувати теми — рішення людське, тому модуль лише показує
   схоже й ніколи нічого не блокує. Але й агент цього робити не може: він бачить
   заголовки, отже дає «схоже», а не «є».

   Чотири сита, кожне вирісши з реального дубля в корпусі:

     вкладений слуг ПО МЕЖАХ СЕГМЕНТІВ    aslr ↔ rop-and-aslr
     вкладеність БЕЗ дефісів              dma-buf ↔ dmabuf-sharing
     спільне РІДКІСНЕ слово               рідкісне в межах книги, не в мові
     той самий слуг в ІНШІЙ книзі         vdso у двох книгах — чия це тема

   Межа сегментів обов'язкова: без неї `cache` збігався б із кожним слугом, де
   трапилось це буквосполучення, і підказка потонула б у шумі.
   ========================================================================== */
"use strict";
const MF = require("./manifest.js");

const words = (slug) => String(slug).split("-").filter(Boolean);
const norm = (slug) => String(slug).replace(/-/g, "");

/** Чи лежить `b` усередині `a` цілими сегментами: `rop-and-aslr` ⊃ `aslr`. */
function segIn(a, b) {
  const A = words(a), B = words(b);
  if (!B.length || B.length > A.length) return false;
  for (let i = 0; i + B.length <= A.length; i++)
    if (B.every((w, j) => A[i + j] === w)) return true;
  return false;
}

/** Слуг → перелік книг, де він є. Не Map «слуг → одна книга»: саме той самий слуг
    у двох книгах і є найдорожчим випадком, і його не можна загубити. */
function corpus() {
  const out = new Map();
  for (const [bslug, b] of MF.books()) {
    const book = MF.loadBook(b.bookDir);
    if (!book) continue;
    for (const t of MF.allTopics(book)) {
      if (!t.own) continue;
      if (!out.has(t.slug)) out.set(t.slug, []);
      out.get(t.slug).push(bslug);
    }
  }
  return out;
}

/** Усі власні слуги корпусу — переліком, для перевірок поза цим модулем. */
const allSlugs = () => corpus();

/**
 * Підказки для слуга, який збираються завести в книгу `bookSlug`. Рядками, готовими
 * до показу. Порожній масив — схожого не знайдено.
 */
function hints(slug, bookSlug) {
  const all = corpus();
  const mine = [...all.entries()]
    .filter(([s, bks]) => bks.includes(bookSlug) && s !== slug)
    .map(([s]) => s);

  /* Рідкісність рахується В МЕЖАХ КНИГИ: «пам'ять» у книзі про пам'ять — слово
     службове, а в книзі про мережі воно вже сигнал. */
  const freq = new Map();
  for (const s of mine) for (const w of new Set(words(s))) freq.set(w, (freq.get(w) || 0) + 1);

  const my = new Set(words(slug));
  const nMy = norm(slug);
  const out = [];

  for (const s of mine) {
    if (segIn(s, slug) || segIn(slug, s)) { out.push(`«${slug}» схожа на: ${s} — вкладений слуг`); continue; }
    const nS = norm(s);
    if (nMy.length >= 5 && nS.length >= 5 &&
      (nS === nMy || nS.startsWith(nMy) || nMy.startsWith(nS) || nS.endsWith(nMy) || nMy.endsWith(nS))) {
      out.push(`«${slug}» схожа на: ${s} — збіг без дефісів`); continue;
    }
    const shared = [...my].filter((w) => words(s).includes(w));
    const rare = shared.find((w) => (freq.get(w) || 0) <= 3);
    if (rare) out.push(`«${slug}» схожа на: ${s} — спільне рідкісне «${rare}»`);
  }

  for (const bk of (all.get(slug) || []).filter((b) => b !== bookSlug))
    out.push(`«${slug}» ВЖЕ Є в книзі «${bk}» — вирішіть, чия це тема`);

  return out;
}

module.exports = { hints, allSlugs, segIn, words, norm };
