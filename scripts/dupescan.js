#!/usr/bin/env node
/* СКАНЕР ДУБЛІВ ПО ВСЬОМУ КОРПУСУ — локальний, токенів не їсть.

   Ужиток:  node scripts/dupescan.js [--book <слуг>] [--strong] [--md <файл>]

   Навіщо. `manifest-patch.js` стереже дублі лише в мить заведення НОВОЇ теми. Те,
   що зайшло в корпус раніше за цей сторож (або повз нього), не бачить ніхто — і
   так у корпусі опинилися пари на кшталт `cryptographic-hash` ↔
   `cryptographic-hash-functions`, обидві написані, обидві в одному розділі.
   Фаза оцінки рівнів знаходила такі пари агентами; це те саме, але даром.

   Ті самі чотири сигнали, що й у manifest7.dupeHints, плюс два власні:
     (1) вкладеність ПО МЕЖАХ сегментів      rsa ↔ rsa-cryptosystem
     (2) збіг без дефісів                    dns-sec ↔ dnssec
     (3) різниця лише в числі                flash-filesystem ↔ flash-filesystems
     (4) той самий слуг в ІНШІЙ книзі
     (5) спільне РІДКІСНЕ слово (≤3 тем)     — найшумніший, лише без --strong
     (6) майже однакова НАЗВА теми           — ловить те, чого слуги не показують

   --strong лишає тільки (1)-(4) і (6): це те, що майже напевно дубль.
   Нічого не змінює: об'єднувати — рішення людське (AUTHORING §6).                */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("./lib/manifest7.js");

const argv = process.argv.slice(2);
const val = (k) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : null; };
const STRONG = argv.includes("--strong");
const ONLY = val("book");
const MD = val("md");

const STOP = new Set(["and", "vs", "the", "of", "in", "to", "a", "for", "with", "model", "basics", "types", "api", "i", "ta", "y"]);
const words = (s) => s.split("-").filter((x) => x.length > 2 && !STOP.has(x));
const segIn = (a, b) => a !== b && (b + "-").includes(a + "-") && ("-" + b).includes("-" + a);
const norm = (s) => s.replace(/-/g, "");
const depl = (s) => s.replace(/(ies)$/, "y").replace(/(es|s)$/, "");
/* назва → порівнюваний вигляд: без регістру, без пунктуації, «геш»→«хеш», без службових */
/* Короткі токени НЕ викидаємо: саме вони й розрізняють «І-складова» від «Д-складова»
   та «D-тригер» від «JK-тригер». Раніше фільтр w.length>2 їх з'їдав і давав хибні дублі. */
const tnorm = (t) => (t || "").toLowerCase().replace(/ґ/g, "г").replace(/геш/g, "хеш")
  .replace(/[^\p{L}\p{N}]+/gu, " ").trim().split(/\s+/)
  .filter((w) => !["для", "про", "або", "що", "як", "the", "and", "i", "й", "та"].includes(w))
  .sort().join(" ");

/* ── збір корпусу ─────────────────────────────────────────────────────────── */
const all = [];                    // {book, kind, slug, title, group, chapter, status}
for (const [bslug, rec] of M7.books()) {
  if (ONLY && bslug !== ONLY) continue;
  const b = M7.loadBook(rec.bookDir); if (!b) continue;
  for (const t of M7.allTopics(b)) {
    if (!t.own) continue;
    all.push({ book: bslug, kind: rec.kind, slug: t.slug, title: t.title || "",
      group: t.group, chapter: t.chapter,
      status: (t.node.detailed && t.node.detailed.status) || "—" });
  }
}

const byBook = new Map();
for (const t of all) { if (!byBook.has(t.book)) byBook.set(t.book, []); byBook.get(t.book).push(t); }

const hits = [];
const seen = new Set();
const push = (a, b, why, weight) => {
  const k = [a.book + "/" + a.slug, b.book + "/" + b.slug].sort().join("|");
  if (seen.has(k)) return; seen.add(k);
  hits.push({ a, b, why, weight, same: a.book === b.book && a.group === b.group && a.chapter === b.chapter });
};

/* (4) той самий слуг у різних книгах */
const bySlug = new Map();
for (const t of all) { if (!bySlug.has(t.slug)) bySlug.set(t.slug, []); bySlug.get(t.slug).push(t); }
for (const [, list] of bySlug) if (list.length > 1)
  for (let i = 0; i < list.length; i++) for (let j = i + 1; j < list.length; j++)
    push(list[i], list[j], "той самий слуг у різних книгах", 3);

/* усередині книги */
for (const [, list] of byBook) {
  const freq = new Map();
  for (const t of list) for (const w of new Set(words(t.slug))) freq.set(w, (freq.get(w) || 0) + 1);
  for (let i = 0; i < list.length; i++) for (let j = i + 1; j < list.length; j++) {
    const A = list[i], B = list[j];
    if (segIn(A.slug, B.slug) || segIn(B.slug, A.slug)) { push(A, B, "вкладений слуг", 3); continue; }
    const nA = norm(A.slug), nB = norm(B.slug);
    if (nA.length >= 5 && nA === nB) { push(A, B, "той самий слуг без дефісів", 3); continue; }
    if (depl(A.slug) === depl(B.slug)) { push(A, B, "різниця лише в числі", 3); continue; }
    const tA = tnorm(A.title), tB = tnorm(B.title);
    if (tA && tA === tB) { push(A, B, "ОДНАКОВА НАЗВА", 4); continue; }
    const sh = words(A.slug).filter((w) => new Set(words(B.slug)).has(w));
    if (sh.length) {
      /* Слово, що в цілій книзі трапляється РІВНО у цих двох темах, — сильний сигнал:
         так ловляться gilbert-elliott-model ↔ gilbert-elliott-channel і
         viterbi-algorithm ↔ viterbi-decoder, де слуги не вкладені один в одний.
         Три й більше тем на слово — це вже родина понять, а не дубль: у слабкі. */
      const only2 = sh.filter((w) => (freq.get(w) || 0) <= 2);
      /* Мало того, що слово рідкісне, — воно має бути ЯДРОМ обох слугів. Інакше дві
         цілком різні теми, що ділять один термін, лізуть у сильні сотнями (заміряно:
         1600 сигналів проти 368). Поріг — спільне покриває половину коротшого слуга. */
      const cover = only2.length / Math.min(words(A.slug).length, words(B.slug).length);
      if (only2.length && cover >= 0.5) push(A, B, `слово «${only2.join("», «")}» є ЛИШЕ в цих двох темах`, 3);
      else if (!STRONG && sh.some((w) => (freq.get(w) || 0) <= 3)) push(A, B, `спільне рідкісне «${sh[0]}»`, 1);
    }
  }
}

hits.sort((x, y) => (y.weight - x.weight) || (Number(y.same) - Number(x.same)) || x.a.book.localeCompare(y.a.book));
const strong = hits.filter((h) => h.weight >= 3);
console.log(`\n=== СКАНЕР ДУБЛІВ ===  тем у корпусі ${all.length}, книг ${byBook.size}`);
console.log(`сильних сигналів: ${strong.length}${STRONG ? "" : `, слабких: ${hits.length - strong.length}`}`);
console.log(`з них в ОДНОМУ розділі: ${strong.filter((h) => h.same).length}\n`);

const line = (h) => `  ${h.same ? "ОДИН РОЗДІЛ" : "різні      "}  ${h.why}\n` +
  `      ${h.a.book}/${h.a.slug} [${h.a.status}] «${h.a.title}»\n` +
  `      ${h.b.book}/${h.b.slug} [${h.b.status}] «${h.b.title}»`;
for (const h of (STRONG ? strong : hits)) console.log(line(h));

if (MD) {
  const L = ["# Сканер дублів по корпусу", "",
    `Прогін по ${all.length} темах у ${byBook.size} книгах. Механічні сигнали, **нічого не змінено** —`,
    "об'єднувати чи ні вирішує людина (`AUTHORING §6`).", "",
    `Сильних сигналів: **${strong.length}**, з них у тому самому розділі: **${strong.filter((h) => h.same).length}**.`, "",
    "| сигнал | один розділ | A | B |", "|---|---|---|---|"];
  for (const h of strong) L.push(`| ${h.why} | ${h.same ? "**так**" : "ні"} | \`${h.a.book}/${h.a.slug}\` [${h.a.status}]<br>«${h.a.title}» | \`${h.b.book}/${h.b.slug}\` [${h.b.status}]<br>«${h.b.title}» |`);
  fs.mkdirSync(path.dirname(MD), { recursive: true });
  fs.writeFileSync(MD, L.join("\n"), "utf8");
  console.log(`\nзаписано: ${MD}`);
}
