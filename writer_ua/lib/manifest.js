#!/usr/bin/env node
/* ============================================================================
   manifest.js — ЧИТАЧ І ПИСАР МАНІФЕСТУ КОНВЕЄРА writer_ua. Схема 7.

   Дерево:

     root/<вид>/<книга>/manifest.json   { schema:7, kind, slug, title, groups:[слуг…] }
     root/<вид>/<книга>/<група>.json    { schema:7, kind, book, slug, title, scope,
                                          chapters:[ {slug,title,topics:[…]} ] }
     root/<вид>/<книга>/<тема>/         тека теми — ПЛАСКО під книгою

   Тема — або власна:
     { slug, title, basic:{status}, detailed:{status}, hist|comp|math|proj|api:[{file,status}] }
   або вказівник на чужу (лише в курсах):
     { ref:"<книга>/<тема>", title }

   ГРУПА Й РОЗДІЛ ЖИВУТЬ ТІЛЬКИ ТУТ. У шляху їх немає, тож перегрупувати книгу —
   це правка JSON, а не рух тисяч тек.

   ⛔ КНИГИ, ТОМУ Й КУРСУ НЕ СТВОРЮЄ НІКОЛИ. Немає manifest.json — операції не
   застосовуються, у звіті стоїть помилка. Групу й розділ усередині НАЯВНОЇ книги
   заводить сама: асиметрія навмисна, бо книгу заводить автор, а розділ — це робота.

   ЗАПИС АТОМАРНИЙ: тимчасовий файл і перейменування. Або старий вміст, або новий;
   напівзаписаного маніфесту не буває. Відступ — два пробіли й кінцевий перевід
   рядка: інакше правка одного статусу переформатувала б увесь файл, і diff перестав
   би показувати, що саме змінилося.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const CONTENT = path.join(ROOT, "root");
const SHELF = path.join(CONTENT, "shelf.json");

const INSERT_TYPES = ["hist", "comp", "math", "proj", "api"];
const VERSIONS = ["basic", "detailed"];
const STATUSES = ["done", "pending", "empty", "update", "deeper", "recheck"];
const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/;

/* ── полиця й книги ────────────────────────────────────────────────────────── */

let _shelf = null;
function shelf() {
  if (_shelf) return _shelf;
  try { _shelf = JSON.parse(fs.readFileSync(SHELF, "utf8")); }
  catch { _shelf = { schema: 7, kinds: [] }; }
  return _shelf;
}

/**
 * Книги полиці: слуг → { kind, dir, bookDir }.
 *
 * Без падбеку на скан диска: гола тека без manifest.json книгою не є.
 */
function books() {
  const out = new Map();
  for (const k of shelf().kinds || [])
    for (const b of k.books || []) {
      const bookDir = path.join(CONTENT, k.dir, b);
      if (fs.existsSync(path.join(bookDir, "manifest.json")))
        out.set(b, { kind: k.kind, dir: k.dir, bookDir });
    }
  return out;
}

const bookDirOf = (slug) => { const b = books().get(slug); return b ? b.bookDir : null; };

/* ── читання ───────────────────────────────────────────────────────────────── */

/** Книга цілком: шапка плюс усі файли груп. Немає маніфесту — null. */
function loadBook(bookDir) {
  if (!bookDir) return null;
  const mfPath = path.join(bookDir, "manifest.json");
  if (!fs.existsSync(mfPath)) return null;
  let manifest;
  try { manifest = JSON.parse(fs.readFileSync(mfPath, "utf8")); } catch { return null; }
  const groups = new Map();
  for (const g of manifest.groups || []) {
    const gp = path.join(bookDir, g + ".json");
    if (!fs.existsSync(gp)) continue;
    try { groups.set(g, { path: gp, data: JSON.parse(fs.readFileSync(gp, "utf8")) }); } catch { }
  }
  return { bookDir, mfPath, manifest, groups };
}

/** Плаский перелік тем: { slug, ref, title, group, chapter, node, own }. */
function allTopics(book) {
  const out = [];
  if (!book) return out;
  for (const [gslug, g] of book.groups)
    for (const ch of g.data.chapters || [])
      for (const t of ch.topics || [])
        out.push({
          slug: t.slug || null, ref: t.ref || null, title: t.title || "",
          group: gslug, chapter: ch.slug, node: t, own: !!t.slug,
        });
  return out;
}

const findTopic = (book, slug) => allTopics(book).find((t) => t.own && t.slug === slug) || null;

/** Слуги груп книги. Приймає і слуг книги, і вже завантажену книгу. */
function groupSlugs(book) {
  const b = typeof book === "string" ? loadBook(bookDirOf(book)) : book;
  return new Set(b ? [...b.groups.keys()] : []);
}

/** Слуги розділів однієї групи. */
function chapterSlugs(book, group) {
  const b = typeof book === "string" ? loadBook(bookDirOf(book)) : book;
  const g = b && b.groups.get(group);
  return new Set(g ? (g.data.chapters || []).map((c) => c.slug) : []);
}

/** Назви групи й розділу — людські. Саме вони йдуть у завдання, а не слуги. */
function place(book, t) {
  const g = book.groups.get(t.group);
  return {
    group: (g && g.data.title) || t.group,
    chapter: ((g && (g.data.chapters || []).find((c) => c.slug === t.chapter) || {}).title) || t.chapter,
  };
}

/* ── запис ─────────────────────────────────────────────────────────────────── */

const clampLevel = (n) => {
  const v = Number(n);
  return Number.isInteger(v) && v >= 1 && v <= 5 ? v : null;
};

/**
 * Прибрати до вузла статусу два поля, що живуть поруч зі статусом:
 *
 *   level   — глибина. Носить її ЛИШЕ `deeper`: на решті статусів вона нічого не
 *             означає, а лежачи там, пережила б власну підставу й прийшла б у
 *             наступний батч чужим числом.
 *   recode  — борг «код перенесено механічно й ще не переписаний як проєкт».
 *             Це не статус, тому зміна статусу його НЕ стирає; знімається лише
 *             явним `recode:false`.
 */
function decorate(node, status, level, recode) {
  if (status === "deeper" && level) node.level = level;
  if (recode) node.recode = true;
  return node;
}

function writeJson(p, data) {
  const tmp = p + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2) + "\n", "utf8");
  fs.renameSync(tmp, p);
}

/**
 * Застосувати операції до однієї книги:
 *
 *   { op:"group",     slug, title, scope? }
 *   { op:"chapter",   group, slug, title, groupTitle? }
 *   { op:"topic",     slug, title, group, chapter, groupTitle?, chapterTitle?,
 *                     basic?="empty", detailed?="pending" }
 *   { op:"ref",       ref, title, group, chapter, groupTitle?, chapterTitle? }
 *   { op:"status",    slug, ver, status }
 *   { op:"status-if", slug, ver, from, to }    ← переставити, лише якщо стоїть from
 *   { op:"insert",    slug, type, file, status }
 *   { op:"insert-remove", slug, type, file } ← зняти вставку з переліку теми
 *   { op:"remove",    slug }                   ← зняти тему з маніфесту
 *   { op:"relocate",  slug, group, chapter, groupTitle?, chapterTitle? }
 *   { op:"retitle",   slug, title }
 *   { op:"rename",    slug, to, title? }       ← інший слуг, статуси й вставки цілі
 *
 * Ідемпотентно: повтор нічого не дублює й лягає в skipped. dry:true — порахувати,
 * нічого не записавши; звіт тоді від самого писаря, а не переказ його правил.
 */
function applyOps(bookDir, ops, opt) {
  const dry = !!(opt && opt.dry);
  const rep = {
    group: 0, chapter: 0, topic: 0, ref: 0, status: 0, insert: 0,
    removed: 0, moved: 0, retitled: 0, renamed: 0, skipped: [], errors: [], changed: 0,
  };
  const book = loadBook(bookDir);
  if (!book) {
    rep.errors.push(`нема маніфесту: ${path.join(String(bookDir), "manifest.json")} — книгу заводить автор`);
    return rep;
  }

  const touched = new Set();
  let headDirty = false;

  const getGroup = (slug, title, scope) => {
    if (!SLUG_RE.test(String(slug || ""))) throw new Error(`слуг групи «${slug}» не є слугом`);
    if (book.groups.has(slug)) return book.groups.get(slug);
    if (!title) throw new Error(`групи «${slug}» немає — потрібна її назва`);
    const data = {
      schema: 7, kind: book.manifest.kind, book: book.manifest.slug,
      slug, title, scope: scope || "", chapters: [],
    };
    book.groups.set(slug, { path: path.join(bookDir, slug + ".json"), data });
    if (!(book.manifest.groups || []).includes(slug))
      (book.manifest.groups = book.manifest.groups || []).push(slug);
    rep.group++; touched.add(slug); headDirty = true;
    return book.groups.get(slug);
  };

  const getChapter = (g, slug, title) => {
    if (!SLUG_RE.test(String(slug || ""))) throw new Error(`слуг розділу «${slug}» не є слугом`);
    let ch = (g.data.chapters || []).find((c) => c.slug === slug);
    if (ch) return ch;
    if (!title) throw new Error(`розділу «${slug}» немає — потрібна його назва`);
    ch = { slug, title, topics: [] };
    (g.data.chapters = g.data.chapters || []).push(ch);
    rep.chapter++; touched.add(g.data.slug);
    return ch;
  };

  /* Вузол теми разом із розділом, у якому лежить: перенос і зняття рухають САМ вузол,
     а не його копію, тож статуси обох версій і всі вставки їдуть із темою. */
  const nodeOf = (slug) => {
    for (const [gslug, g] of book.groups)
      for (const ch of g.data.chapters || []) {
        const i = (ch.topics || []).findIndex((t) => t.slug === slug);
        if (i >= 0) return { gslug, ch, i, node: ch.topics[i] };
      }
    return null;
  };

  for (const o of ops) {
    try {
      switch (o.op) {

        case "group": {
          if (book.groups.has(o.slug)) { rep.skipped.push(`група «${o.slug}» уже є`); break; }
          getGroup(o.slug, o.title, o.scope);
          break;
        }

        case "chapter": {
          const g = getGroup(o.group, o.groupTitle);
          if (chapterSlugs(book, o.group).has(o.slug)) { rep.skipped.push(`розділ «${o.slug}» уже є`); break; }
          getChapter(g, o.slug, o.title);
          break;
        }

        case "topic": {
          if (findTopic(book, o.slug)) { rep.skipped.push(`тема «${o.slug}» уже є`); break; }
          if (!SLUG_RE.test(String(o.slug || ""))) throw new Error(`слуг «${o.slug}» не є слугом`);
          const g = getGroup(o.group, o.groupTitle);
          const ch = getChapter(g, o.chapter, o.chapterTitle);
          ch.topics.push({
            slug: o.slug, title: o.title || o.slug,
            basic: { status: o.basic || "empty" },
            detailed: { status: o.detailed || "pending" },
          });
          rep.topic++; touched.add(g.data.slug);
          break;
        }

        case "ref": {
          const g = getGroup(o.group, o.groupTitle);
          const ch = getChapter(g, o.chapter, o.chapterTitle);
          if ((ch.topics || []).some((t) => t.ref === o.ref)) { rep.skipped.push(`ref «${o.ref}» уже є`); break; }
          ch.topics.push({ ref: o.ref, title: o.title || o.ref });
          rep.ref++; touched.add(g.data.slug);
          break;
        }

        case "status":
        case "status-if": {
          if (!VERSIONS.includes(o.ver)) { rep.errors.push(`невідома версія «${o.ver}»`); break; }
          const to = o.op === "status" ? o.status : o.to;
          if (!STATUSES.includes(to)) { rep.errors.push(`невідомий статус «${to}»`); break; }
          const t = findTopic(book, o.slug);
          if (!t) { rep.errors.push(`нема теми «${o.slug}»`); break; }
          const was = t.node[o.ver] || {};
          const cur = was.status || "empty";
          if (o.op === "status-if" && cur !== o.from) {
            rep.skipped.push(`«${o.slug}».${o.ver} = ${cur} ≠ ${o.from}`); break;
          }
          const lvl = "level" in o ? clampLevel(o.level) : undefined;
          const rc = "recode" in o ? !!o.recode : undefined;
          if (cur === to && (lvl === undefined || lvl === (was.level || null)) &&
            (rc === undefined || rc === !!was.recode)) {
            rep.skipped.push(`«${o.slug}».${o.ver} уже ${to}`); break;
          }
          t.node[o.ver] = decorate({ status: to }, to,
            lvl !== undefined ? lvl : (was.level || null),
            rc !== undefined ? rc : !!was.recode);
          rep.status++; touched.add(t.group);
          break;
        }

        case "insert": {
          if (!INSERT_TYPES.includes(o.type)) { rep.errors.push(`невідомий тип вставки «${o.type}»`); break; }
          if (!STATUSES.includes(o.status)) { rep.errors.push(`невідомий статус «${o.status}»`); break; }
          const t = findTopic(book, o.slug);
          if (!t) { rep.errors.push(`нема теми «${o.slug}» для вставки «${o.file}»`); break; }
          const arr = (t.node[o.type] = t.node[o.type] || []);
          const cur = arr.find((x) => x.file === o.file);
          const lvl = "level" in o ? clampLevel(o.level) : undefined;
          const rc = "recode" in o ? !!o.recode : undefined;
          if (cur && cur.status === o.status && (lvl === undefined || lvl === (cur.level || null)) &&
            (rc === undefined || rc === !!cur.recode)) {
            rep.skipped.push(`вставка «${o.file}» уже ${o.status}`); break;
          }
          const node = decorate({ file: o.file, status: o.status }, o.status,
            lvl !== undefined ? lvl : (cur ? cur.level || null : null),
            rc !== undefined ? rc : !!(cur && cur.recode));
          if (cur) arr[arr.indexOf(cur)] = node; else arr.push(node);
          rep.insert++; touched.add(t.group);
          break;
        }

        /* Зняти вставку з переліку теми. Потрібне там, де вставку знесли з диска: сам
           лише статус тут не рятує, бо запис лишається й обіцяє файл, якого немає. */
        case "insert-remove": {
          if (!INSERT_TYPES.includes(o.type)) { rep.errors.push(`невідомий тип вставки «${o.type}»`); break; }
          const t = findTopic(book, o.slug);
          if (!t) { rep.errors.push(`нема теми «${o.slug}»`); break; }
          const arr = t.node[o.type] || [];
          const i = arr.findIndex((x) => x.file === o.file);
          if (i < 0) { rep.skipped.push(`вставки «${o.file}» у «${o.slug}» немає`); break; }
          arr.splice(i, 1);
          if (!arr.length) delete t.node[o.type];
          rep.removed++; touched.add(t.group);
          break;
        }

        case "remove": {
          const at = nodeOf(o.slug);
          if (!at) { rep.skipped.push(`теми «${o.slug}» у маніфесті немає`); break; }
          at.ch.topics.splice(at.i, 1);
          rep.removed++; touched.add(at.gslug);
          break;
        }

        case "relocate": {
          const at = nodeOf(o.slug);
          if (!at) { rep.errors.push(`нема теми «${o.slug}» для перекладання`); break; }
          if (at.gslug === o.group && at.ch.slug === o.chapter) {
            rep.skipped.push(`«${o.slug}» уже в ${o.group}/${o.chapter}`); break;
          }
          const g = getGroup(o.group, o.groupTitle);
          const ch = getChapter(g, o.chapter, o.chapterTitle);
          at.ch.topics.splice(at.i, 1);
          ch.topics.push(at.node);
          rep.moved++; touched.add(at.gslug); touched.add(g.data.slug);
          break;
        }

        case "retitle": {
          const t = findTopic(book, o.slug);
          if (!t) { rep.errors.push(`нема теми «${o.slug}» для зміни назви`); break; }
          if (t.node.title === o.title) { rep.skipped.push(`«${o.slug}» уже зветься так`); break; }
          t.node.title = o.title;
          rep.retitled++; touched.add(t.group);
          break;
        }

        /* Слуг міняється НА МІСЦІ. Знести й завести наново означало б стерти статуси
           обох версій і весь перелік вставок — тема приїхала б на той самий рядок
           порожньою. */
        case "rename": {
          if (!SLUG_RE.test(String(o.to || ""))) throw new Error(`слуг «${o.to}» не є слугом`);
          const at = nodeOf(o.slug);
          if (!at) { rep.errors.push(`нема теми «${o.slug}» для зміни слуга`); break; }
          if (findTopic(book, o.to)) { rep.errors.push(`слуг «${o.to}» у книзі вже зайнятий`); break; }
          at.node.slug = o.to;
          if (o.title) at.node.title = o.title;
          rep.renamed++; touched.add(at.gslug);
          break;
        }

        default: rep.errors.push(`невідома операція «${o.op}»`);
      }
    } catch (e) { rep.errors.push(`${o.op} «${o.slug || o.ref || ""}»: ${e.message}`); }
  }

  rep.changed = rep.group + rep.chapter + rep.topic + rep.ref + rep.status +
    rep.insert + rep.removed + rep.moved + rep.retitled + rep.renamed;

  if (!dry && rep.changed) {
    if (headDirty) writeJson(book.mfPath, book.manifest);
    for (const gslug of touched) { const g = book.groups.get(gslug); if (g) writeJson(g.path, g.data); }
  }
  return rep;
}

module.exports = {
  ROOT, CONTENT, INSERT_TYPES, VERSIONS, STATUSES, SLUG_RE,
  shelf, books, bookDirOf, loadBook, allTopics, findTopic,
  groupSlugs, chapterSlugs, place, applyOps,
};
