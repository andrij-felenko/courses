#!/usr/bin/env node
/* ============================================================================
   manifest7.js — ЄДИНЕ місце, де тулінг читає й пише маніфест схеми 7.

   НАВІЩО ОКРЕМИЙ МОДУЛЬ. У світі v6 кожен скрипт розбирав маніфест сам:
   `checks/_lib.js` виконував `.js` у пісочниці, `manifest-patch.js` правив ТЕКСТ
   файла рядок за рядком, `linkcheck.js` мав свій обхід, `finish-batch.js` — свій.
   Чотири розбори однієї схеми означали чотири різні уявлення про неї; саме тому
   правило «нову групу створюєш сам» тихо не працювало — один зі скриптів про це
   не знав. У v7 маніфест став JSON, і немає жодної причини тримати чотири розбори.

   ДЕРЕВО (канон v7 §1, остаточно 2026-08-25):

     root/<вид>/<книга>/manifest.json     { schema:7, kind, slug, title, groups:[слуг…] }
     root/<вид>/<книга>/<група>.json      { schema:7, kind, book, slug, title, scope,
                                            chapters:[ {slug,title,topics:[…]} ],
                                            megachapters?:[{title,chapters:[слуг…]}] }
                                            ⚠️ megachapters поки НЕ рендериться — відкладений
                                            пункт B6 у CANON-v7-apply.md; жодна книга його не вживає.
     root/<вид>/<книга>/<тема>/           тека теми — ПЛАСКО під книгою

   Тема в маніфесті — або власна:
     { slug, title, basic:{status}, detailed:{status}, hist|comp|math|proj|api:[{file,status}] }
   або вказівник на чужу (тільки в курсах):
     { ref:"<книга>/<тема>", title }

   ⚠️ Група й розділ живуть ТІЛЬКИ в маніфесті — у шляху їх немає. Тому
   перегрупувати книгу це правка JSON, а не рух файлів.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const CONTENT = path.join(ROOT, "root");
const SHELF = path.join(CONTENT, "shelf.json");
const INSERT_TYPES = ["hist", "comp", "math", "proj", "api"];

/* ── полиця ────────────────────────────────────────────────────────────────── */
let _shelf = null;
function shelf() {
  if (_shelf) return _shelf;
  try { _shelf = JSON.parse(fs.readFileSync(SHELF, "utf8")); }
  catch { _shelf = { schema: 7, kinds: [] }; }
  return _shelf;
}

/** Усі книги дерева: слуг → { kind, dir, bookDir }. Береться з shelf.json, а як книги
 *  там ще немає (перенос у польоті) — з самого диска, щоб тулінг не сліп на пів дня. */
function books() {
  const out = new Map();
  for (const k of shelf().kinds || [])
    for (const b of k.books || []) out.set(b, { kind: k.kind, dir: k.dir, bookDir: path.join(CONTENT, k.dir, b) });
  let dirs = [];
  try { dirs = fs.readdirSync(CONTENT, { withFileTypes: true }).filter((e) => e.isDirectory()); } catch { }
  for (const kd of dirs) {
    let bs = [];
    try { bs = fs.readdirSync(path.join(CONTENT, kd.name), { withFileTypes: true }).filter((e) => e.isDirectory()); } catch { }
    for (const b of bs) if (!out.has(b.name)) out.set(b.name, { kind: kd.name, dir: kd.name, bookDir: path.join(CONTENT, kd.name, b.name) });
  }
  return out;
}

/** Тека книги за слугом (`sf-algorithms` → `<repo>/root/eng/sf-algorithms`). */
function bookDirOf(slug) { const b = books().get(slug); return b ? b.bookDir : null; }

/** З теки ТЕМИ дістати теку книги. Тема лежить пласко: `root/<вид>/<книга>/<тема>`. */
function bookDirOfTopic(topicDir) {
  const rel = path.relative(ROOT, path.resolve(topicDir)).split(/[\\/]/).filter(Boolean);
  if (rel.length < 4 || rel[0] !== "root") return null;
  return path.join(ROOT, rel[0], rel[1], rel[2]);
}

/** Чи це взагалі дерево v7? Потрібно скриптам, що поки живуть на два світи. */
function isV7(dir) {
  const rel = path.relative(ROOT, path.resolve(dir)).split(/[\\/]/).filter(Boolean);
  return rel[0] === "root";
}

/* ── читання ───────────────────────────────────────────────────────────────── */
/** Прочитати книгу цілком: шапка + усі файли груп. Немає маніфесту — вертає null. */
function loadBook(bookDir) {
  const mfPath = path.join(bookDir, "manifest.json");
  if (!fs.existsSync(mfPath)) return null;
  let manifest;
  try { manifest = JSON.parse(fs.readFileSync(mfPath, "utf8")); } catch (e) { return null; }
  const groups = new Map();
  for (const g of manifest.groups || []) {
    const gp = path.join(bookDir, g + ".json");
    if (!fs.existsSync(gp)) continue;
    try { groups.set(g, { path: gp, data: JSON.parse(fs.readFileSync(gp, "utf8")) }); } catch { }
  }
  return { bookDir, mfPath, manifest, groups };
}

/** Плаский перелік тем книги з адресою кожної: {slug,title,group,chapter,node,own}. */
function allTopics(book) {
  const out = [];
  if (!book) return out;
  for (const [gslug, g] of book.groups)
    for (const ch of g.data.chapters || [])
      for (const t of ch.topics || [])
        out.push({ slug: t.slug || null, ref: t.ref || null, title: t.title || "", group: gslug, chapter: ch.slug, node: t, own: !!t.slug });
  return out;
}

function findTopic(book, slug) { return allTopics(book).find((t) => t.slug === slug) || null; }

/** Слуги груп і розділів — для перевірки «чи створюємо нове». */
function groupSlugs(book) { return new Set(book ? [...book.groups.keys()] : []); }
function chapterSlugs(book, group) {
  const g = book && book.groups.get(group);
  return new Set(g ? (g.data.chapters || []).map((c) => c.slug) : []);
}

/* ── запис ─────────────────────────────────────────────────────────────────── */
const st = (v) => ({ status: v });

function ensureManifest(bookDir) {
  const mfPath = path.join(bookDir, "manifest.json");
  if (fs.existsSync(mfPath)) return;
  const slug = path.basename(bookDir);
  const kindDir = path.basename(path.dirname(bookDir));
  const k = (shelf().kinds || []).find((x) => x.dir === kindDir);
  write(mfPath, { schema: 7, kind: (k && k.kind) || kindDir, slug, title: slug, groups: [] });
}

/* Формат корпусу — ДВА пробіли й кінцевий перевід рядка. Писали одним — і правка
   одного статусу переформатувала б увесь файл, роздувши diff до нечитабельного. */
function write(p, data) {
  const tmp = p + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2) + "\n", "utf8");
  fs.renameSync(tmp, p);
}

/**
 * Застосувати операції до книги. Операції — ті самі за змістом, що в manifest-patch.js,
 * плюс `group` і `chapter`, яких у v6 не було (і через брак яких нова група тихо гинула).
 *
 *   { op:"group",     slug, title, scope? }
 *   { op:"chapter",   group, slug, title }
 *   { op:"topic",     group, chapter, slug, title, basic?, detailed?,
 *                     groupTitle?, groupScope?, chapterTitle? }   ← створить і групу, і розділ
 *   { op:"status",    slug, ver:"basic"|"detailed", status }
 *   { op:"status-if", slug, ver, from, to }
 *   { op:"insert",    slug, type, file, status }
 *   { op:"remove",    slug }                                  ← зняти тему з маніфесту
 *   { op:"relocate",  slug, group, chapter, groupTitle?, chapterTitle? }  ← інший розділ
 *   { op:"retitle",   slug, title }                           ← змінити назву теми
 *   { op:"ref",       group, chapter, ref, title }                ← крок-вказівник (курси)
 *
 * dry:true — нічого не пише, лише вертає звіт. Ідемпотентно: повтор не дублює.
 */
function applyOps(bookDir, ops, opt) {
  const dry = !!(opt && opt.dry);
  if (!dry) ensureManifest(bookDir);
  let book = loadBook(bookDir);
  if (!book) return { errors: [`нема маніфесту: ${path.join(bookDir, "manifest.json")}`], changed: 0 };

  const rep = { group: 0, chapter: 0, topic: 0, ref: 0, status: 0, insert: 0, removed: 0, moved: 0, retitled: 0, skipped: [], errors: [] };
  const touched = new Set();
  const touchGroup = (g) => touched.add(g);

  const getGroup = (slug, title, scope) => {
    if (book.groups.has(slug)) return book.groups.get(slug);
    const data = { schema: 7, kind: book.manifest.kind, book: book.manifest.slug, slug, title: title || slug, scope: scope || "", chapters: [] };
    const g = { path: path.join(bookDir, slug + ".json"), data, fresh: true };
    book.groups.set(slug, g);
    if (!(book.manifest.groups || []).includes(slug)) (book.manifest.groups = book.manifest.groups || []).push(slug);
    rep.group++; touchGroup(slug); touched.add("__manifest__");
    return g;
  };
  const getChapter = (g, slug, title) => {
    let ch = (g.data.chapters || []).find((c) => c.slug === slug);
    if (ch) return ch;
    ch = { slug, title: title || slug, topics: [] };
    (g.data.chapters = g.data.chapters || []).push(ch);
    rep.chapter++; touchGroup(g.data.slug);
    return ch;
  };

  for (const o of ops) {
    try {
      if (o.op === "group") {
        if (book.groups.has(o.slug)) { rep.skipped.push(`група «${o.slug}» уже є`); continue }
        getGroup(o.slug, o.title, o.scope);

      } else if (o.op === "chapter") {
        const g = book.groups.get(o.group);
        if (!g) { rep.errors.push(`нема групи «${o.group}» для розділу «${o.slug}»`); continue }
        if ((g.data.chapters || []).some((c) => c.slug === o.slug)) { rep.skipped.push(`розділ «${o.slug}» уже є`); continue }
        getChapter(g, o.slug, o.title);

      } else if (o.op === "topic") {
        if (findTopic(book, o.slug)) { rep.skipped.push(`тема «${o.slug}» уже є`); continue }
        const g = getGroup(o.group, o.groupTitle, o.groupScope);
        const ch = getChapter(g, o.chapter, o.chapterTitle);
        const node = { slug: o.slug, title: o.title || o.slug, basic: st(o.basic || "empty"), detailed: st(o.detailed || "pending") };
        ch.topics.push(node); rep.topic++; touchGroup(g.data.slug);

      } else if (o.op === "ref") {
        const g = getGroup(o.group, o.groupTitle, o.groupScope);
        const ch = getChapter(g, o.chapter, o.chapterTitle);
        if ((ch.topics || []).some((t) => t.ref === o.ref)) { rep.skipped.push(`ref «${o.ref}» уже є`); continue }
        ch.topics.push({ ref: o.ref, title: o.title || o.ref }); rep.ref++; touchGroup(g.data.slug);

      } else if (o.op === "status" || o.op === "status-if") {
        const t = findTopic(book, o.slug);
        if (!t) { rep.errors.push(`нема теми «${o.slug}» для статусу`); continue }
        const cur = (t.node[o.ver] && t.node[o.ver].status) || "empty";
        if (o.op === "status-if" && cur !== o.from) { rep.skipped.push(`«${o.slug}».${o.ver} = ${cur} ≠ ${o.from}`); continue }
        const to = o.op === "status" ? o.status : o.to;
        if (cur === to) { rep.skipped.push(`«${o.slug}».${o.ver} уже ${to}`); continue }
        t.node[o.ver] = st(to); rep.status++; touchGroup(t.group);

      } else if (o.op === "insert") {
        const t = findTopic(book, o.slug);
        if (!t) { rep.errors.push(`нема теми «${o.slug}» для вставки «${o.file}»`); continue }
        if (!INSERT_TYPES.includes(o.type)) { rep.errors.push(`невідомий тип вставки «${o.type}»`); continue }
        const arr = (t.node[o.type] = t.node[o.type] || []);
        const cur = arr.find((x) => x.file === o.file);
        if (cur) { if (cur.status === o.status) { rep.skipped.push(`вставка «${o.file}» уже ${o.status}`); continue } cur.status = o.status; }
        else arr.push({ file: o.file, status: o.status });
        rep.insert++; touchGroup(t.group);

      } else if (o.op === "remove") {
        /* Зняти тему. Потрібно там, де матеріал переїхав: злився з іншою темою, став
           вставкою або пішов у чужу книгу. Запис теми лишався б у черзі назавжди —
           файлу нема, писати нема чого, а `pending` вічно проситься в батч. */
        const t = findTopic(book, o.slug);
        if (!t) { rep.skipped.push(`теми «${o.slug}» нема — знімати нічого`); continue }
        const g = book.groups.get(t.group);
        const ch = (g.data.chapters || []).find((c) => c.slug === t.chapter);
        const i = (ch.topics || []).indexOf(t.node);
        if (i < 0) { rep.errors.push(`тему «${o.slug}» не знайдено в розділі «${t.chapter}»`); continue }
        ch.topics.splice(i, 1); rep.removed++; touchGroup(t.group);

      } else if (o.op === "relocate") {
        /* Перекласти тему в інший розділ ТІЄЇ Ж книги — з усіма статусами й вставками:
           переносимо сам вузол, а не його копію. Між книгами так не можна: там два
           різні маніфести, і це робиться парою «topic у цільову + remove з джерела». */
        const t = findTopic(book, o.slug);
        if (!t) { rep.errors.push(`нема теми «${o.slug}» для перекладання`); continue }
        if (t.group === o.group && t.chapter === o.chapter) { rep.skipped.push(`«${o.slug}» уже в «${o.group}/${o.chapter}»`); continue }
        const from = book.groups.get(t.group);
        const fromCh = (from.data.chapters || []).find((c) => c.slug === t.chapter);
        const i = (fromCh.topics || []).indexOf(t.node);
        if (i < 0) { rep.errors.push(`тему «${o.slug}» не знайдено в «${t.chapter}»`); continue }
        const g = getGroup(o.group, o.groupTitle, o.groupScope);
        const ch = getChapter(g, o.chapter, o.chapterTitle);
        fromCh.topics.splice(i, 1);
        ch.topics.push(t.node);
        rep.moved++; touchGroup(t.group); touchGroup(g.data.slug);

      } else if (o.op === "retitle") {
        const t = findTopic(book, o.slug);
        if (!t) { rep.errors.push(`нема теми «${o.slug}» для перейменування`); continue }
        if (t.node.title === o.title) { rep.skipped.push(`«${o.slug}» уже має цю назву`); continue }
        t.node.title = o.title; rep.retitled++; touchGroup(t.group);

      } else rep.errors.push(`невідома операція «${o.op}»`);
    } catch (e) { rep.errors.push(`${o.op} «${o.slug || o.ref || ""}»: ${e.message}`); }
  }

  rep.changed = rep.group + rep.chapter + rep.topic + rep.ref + rep.status + rep.insert + rep.removed + rep.moved + rep.retitled;
  if (!dry && rep.changed) {
    if (touched.has("__manifest__")) write(book.mfPath, book.manifest);
    for (const gslug of touched) { const g = book.groups.get(gslug); if (g) write(g.path, g.data); }
  }
  return rep;
}

module.exports = {
  ROOT, CONTENT, INSERT_TYPES,
  shelf, books, bookDirOf, bookDirOfTopic, isV7,
  loadBook, allTopics, findTopic, groupSlugs, chapterSlugs,
  applyOps,
};

/* ── близькі слуги: «а це часом не те саме поняття?» ───────────────────────────
   Евристики перенесено з manifest-patch.js ДОСЛІВНО — це не нові правила, а ті самі
   чотири сигнали, на яких корпус уже набрав понад тридцять пар дублів:
     (1) вкладеність ПО МЕЖАХ сегментів      aslr ↔ rop-and-aslr
     (2) вкладеність БЕЗ дефісів             dma-buf ↔ dmabuf-sharing
     (3) спільне РІДКІСНЕ слово (≤3 тем)     streaming-threads ↔ threads-and-queues
     (4) той самий слуг в ІНШІЙ книзі        vdso у programming ↔ sys-unix
   Не блокує: об'єднувати чи ні — рішення людське (AUTHORING §6).                */
const _STOP = new Set(["and", "vs", "the", "of", "in", "to", "a", "for", "with", "model", "basics", "types", "api"]);
const _words = (s) => s.split("-").filter((x) => x.length > 2 && !_STOP.has(x));
const _segIn = (a, b) => (b + "-").includes(a + "-") && ("-" + b).includes("-" + a);
const _norm = (s) => s.replace(/-/g, "");

/** Усі теми корпусу: слуг → книга. Один прохід по всіх книгах v7. */
let _ALL = null;
function allSlugsInCorpus() {
  if (_ALL) return _ALL;
  _ALL = new Map();
  for (const [bslug, b] of books()) {
    const bk = loadBook(b.bookDir);
    if (!bk) continue;
    for (const t of allTopics(bk)) if (t.own && !_ALL.has(t.slug)) _ALL.set(t.slug, bslug);
  }
  return _ALL;
}

/** Підказки про можливий дубль для НОВОГО слуга. Порожньо — сигналів немає. */
function dupeHints(slug, bookSlug) {
  const corpus = allSlugsInCorpus();
  const own = [], foreign = [];
  for (const [s, bk] of corpus) { if (s === slug && bk !== bookSlug) foreign.push(bk); }
  const mineBook = [...corpus.entries()].filter(([, bk]) => bk === bookSlug).map(([s]) => s).filter((s) => s !== slug);

  const freq = new Map();
  for (const s of mineBook) for (const w of new Set(_words(s))) freq.set(w, (freq.get(w) || 0) + 1);
  const mine = new Set(_words(slug));
  const nMine = _norm(slug);

  for (const s of mineBook) {
    if (_segIn(s, slug) || _segIn(slug, s)) { own.push([s, "вкладений слуг"]); continue }
    const nS = _norm(s);
    if (nMine.length >= 5 && nS.length >= 5 && (nS === nMine || nS.startsWith(nMine) || nMine.startsWith(nS)
        || nS.endsWith(nMine) || nMine.endsWith(nS))) { own.push([s, "збіг без дефісів"]); continue }
    const other = new Set(_words(s));
    const shared = [...mine].filter((x) => other.has(x));
    if (shared.length && shared.some((w) => (freq.get(w) || 0) <= 3)) own.push([s, `спільне рідкісне «${shared[0]}»`]);
  }

  const out = own.map(([s, why]) => `«${slug}» схожа на: ${s} — ${why} (§4)`);
  for (const bk of new Set(foreign)) out.push(`«${slug}» ВЖЕ Є в книзі «${bk}» — вирішіть, чия це тема (§1)`);
  return out;
}

module.exports.allSlugsInCorpus = allSlugsInCorpus;
module.exports.dupeHints = dupeHints;
