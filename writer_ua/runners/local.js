#!/usr/bin/env node
/* ============================================================================
   local.js — ЛОКАЛЬНІ КРОКИ КОНВЕЄРА. Нуль токенів, нуль здогадів.

   Сюди зібрано все, що агентові робити не треба: підготовка контексту, розмір,
   умови здачі, збирання файла, операції в маніфест. Кожен із цих кроків або дає
   число, або дає текст, який runner підставляє в блок, — і жоден нічого не судить
   про зміст.

   ⛔ ПЕРЕВІРКА ДУБЛЯ ЖИВЕ ТУТ, А НЕ В АГЕНТА. «Стаття існує» — це факт: слуг є в
   маніфесті, файл є на диску. Агент статей не бачить і може судити лише за
   заголовками, тобто дати «схоже», а не «є».
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const M7 = require("../../scripts/lib/manifest7.js");
const L = require("../../scripts/checks/_lib.js");

/* ── людський шлях ─────────────────────────────────────────────────────────── */

/**
 * ⚠️ ПОСИЛАННЯ НА СТАТТЮ ЗАВЖДИ НЕСЕ ПОВНИЙ ШЛЯХ МОВОЮ. Сирий шлях на диску нічого
 * не каже тому, хто читає; «книга / група / розділ / тема» каже все одразу.
 */
function humanPath(rel) {
  const seg = rel.split("/");                       // root/<вид>/<книга>/<тема>/<файл>
  const b = M7.loadBook(M7.bookDirOf(seg[2]));
  if (!b) return rel;
  const t = M7.allTopics(b).find((x) => x.slug === seg[3]);
  const title = b.manifest.title || seg[2];
  if (!t) return `${title} / ${seg[3]}`;
  const g = b.groups.get(t.group);
  const gt = (g && g.data.title) || t.group;
  const ct = ((g && (g.data.chapters || []).find((c) => c.slug === t.chapter) || {}).title) || t.chapter;
  return `${title} / ${gt} / ${ct} / ${t.title}`;
}

/** Одиниця з маніфесту в тому вигляді, у якому її бачать запити. */
function unitOf(book, slug, type = "article", version = "ДЕТАЛЬНА") {
  const b = M7.loadBook(M7.bookDirOf(book));
  if (!b) throw new Error(`книги «${book}» немає (manifest.json не знайдено)`);
  const t = M7.allTopics(b).find((x) => x.slug === slug);
  if (!t) throw new Error(`теми «${slug}» у книзі «${book}» немає`);
  const g = b.groups.get(t.group);
  return {
    id: `${book}/${slug}:${type === "article" ? "detailed" : type}`,
    book, slug, type, version,
    title: t.title,
    bookTitle: b.manifest.title || book,
    groupTitle: (g && g.data.title) || t.group,
    chapterTitle: ((g && (g.data.chapters || []).find((c) => c.slug === t.chapter) || {}).title) || t.chapter,
    dir: path.join(M7.bookDirOf(book), slug),
  };
}

/* ── етап 1 · підготовка ───────────────────────────────────────────────────── */

const walkMd = (d, out = []) => {
  let e = [];
  try { e = fs.readdirSync(d, { withFileTypes: true }); } catch { return out; }
  for (const x of e) {
    const p = path.join(d, x.name);
    if (x.isDirectory()) walkMd(p, out);
    else if (x.name.endsWith(".md")) out.push(p);
  }
  return out;
};

/**
 * Згадки: абзац до, сама згадка, абзац після. Файли САМОЇ теми виключено — інакше
 * агент побачив би готовий текст і ціль стала б його переказом.
 *
 * ⚠️ Пошук іде за словом, і на омонімах він дає шум: на темі «Одержимість
 * примітивами» всі шість влучань виявилися про синхронізаційні та бітові примітиви.
 * Тому людський шлях стоїть ПЕРШИМ рядком — з нього доречність видно одразу.
 */
function mentions(u, re, { limit = 6, roots = ["root"] } = {}) {
  const out = [];
  for (const r of roots) {
    for (const f of walkMd(path.join(M7.ROOT, r))) {
      if (f.replace(/\\/g, "/").includes(`/${u.slug}/`)) continue;
      let txt = ""; try { txt = fs.readFileSync(f, "utf8"); } catch { continue; }
      if (!re.test(txt)) continue;
      const rel = path.relative(M7.ROOT, f).split(path.sep).join("/");
      const paras = txt.split(/\n\s*\n/);
      for (let i = 0; i < paras.length && out.length < limit; i++) {
        if (!re.test(paras[i]) || paras[i].length < 120) continue;
        const cut = (s, n) => String(s || "").replace(/\s+/g, " ").slice(0, n).trim();
        out.push(`— ${humanPath(rel)}\n  ${rel}\n[абзац до] ${cut(paras[i - 1], 280)}\n` +
          `[згадка] ${cut(paras[i], 380)}\n[абзац після] ${cut(paras[i + 1], 280)}`);
      }
      if (out.length >= limit) break;
    }
  }
  return out.join("\n\n");
}

/** Сусіди по розділу — для меж, назвами. */
function neighbours(u) {
  const b = M7.loadBook(M7.bookDirOf(u.book));
  const me = M7.allTopics(b).find((x) => x.slug === u.slug);
  return M7.allTopics(b)
    .filter((t) => t.own && t.chapter === me.chapter && t.slug !== u.slug)
    .map((t) => {
      const d = (t.node.detailed && t.node.detailed.status) || "empty";
      return `${t.title} [${d === "empty" || d === "pending" ? "ще не написана" : "НАПИСАНА"}]`;
    }).join("\n");
}

/** Усі книги репо назвами — для каркаса статті. */
const books = () => [...M7.books().entries()]
  .map(([slug, b]) => { const x = M7.loadBook(b.bookDir); return x ? (x.manifest.title || slug) : null; })
  .filter(Boolean).join("\n");

/** Що читач уже знає: у курсі — теми тому; у книзі — сусіди розділу. */
const preknow = (u) => neighbours(u);

/** ⛔ Дубль — точно й локально. Слуг є в книзі ⟺ тема існує. */
function isDuplicate(book, slug) {
  const b = M7.loadBook(M7.bookDirOf(book));
  const t = b && M7.allTopics(b).find((x) => x.own && x.slug === slug);
  if (!t) return { exists: false, written: false, hints: M7.dupeHints(slug, book) || [] };
  const d = (t.node.detailed && t.node.detailed.status) || "empty";
  return {
    exists: true, written: !(d === "empty" || d === "pending"),
    hints: M7.dupeHints(slug, book) || [],
  };
}

/* ── етап 5 · розмір ───────────────────────────────────────────────────────── */

/** Норми з рішення автора. Базова — без рівня. Четверте число — стеля. */
const BANDS = {
  basic: [500, 500, 500, 1500],
  detail: [1200, 2400, 4000, 10000],
  hist: [600, 1000, 1600, 5000],
  math: [600, 1200, 2000, 6000],
  comp: [800, 1400, 2200, 7000],
  proj: [800, 1200, 1800, 8000],
  api: [700, 1400, 2500, 12000],
};

/**
 * Скільки бракує — у ВІДСОТКАХ, і це число йде дописувачеві, а не письменникові:
 * показане число стає ціллю.
 */
function size(text, type, level) {
  const key = type === "article" ? "detail" : type;
  const band = BANDS[key] || BANDS.detail;
  const words = L.proseWords(text);
  const need = type === "basic" ? band[0] : band[Math.max(1, Math.min(3, level || 2)) - 1];
  const short = words < need ? Math.round((1 - words / need) * 100) : 0;
  return { words, need, ceiling: band[3], shortBy: short, over: words > band[3] };
}

/* ── етап 9-10 · зібрання й маніфест ───────────────────────────────────────── */

/** Розділи → один файл. Заголовки пишуть самі письменники, ми лише склеюємо. */
const assemble = (parts) => parts.map((p) => String(p || "").trim()).filter(Boolean).join("\n\n") + "\n";

function writeArticle(u, text) {
  fs.mkdirSync(u.dir, { recursive: true });
  const file = path.join(u.dir, u.type === "basic" ? `${u.slug}.md` : `${u.slug}-d.md`);
  fs.writeFileSync(file, text, "utf8");
  return path.relative(M7.ROOT, file).split(path.sep).join("/");
}

/** Операції для manifest7. Статус приходить ззовні — його вирішує не цей файл. */
const ops = (u, status) => [
  u.type === "article" || u.type === "basic"
    ? { op: "status", slug: u.slug, ver: u.type === "basic" ? "basic" : "detailed", status }
    : { op: "insert", slug: u.slug, type: u.type, file: `${u.type}-${u.slug}.md`, status },
];

/**
 * Ключ пошуку згадок із назви теми — ЦІЛА назва, а не перше слово. З першим словом
 * «Одержимість примітивами» ловила «одержимість простотою» з історії Arduino: пошук за
 * коротким словом дає омонім, і саме так у перший прогін заїхало шість чужих абзаців.
 */
function titleRe(title) {
  const esc = String(title).replace(/[-.*+?^${}()|[\]\\]/g, (c) => "\\" + c);
  return new RegExp(esc.replace(/\s+/g, "\\s+"), "i");
}

module.exports = {
  humanPath, titleRe, unitOf, mentions, neighbours, books, preknow, isDuplicate,
  size, BANDS, assemble, writeArticle, ops,
};
