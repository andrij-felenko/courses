/* make-chunks.js — ЛОКАЛЬНА підготовка до батчу розкладки (агентів не їсть).
   node scripts/migrate/make-chunks.js --book <тека книги> [--size 150]
   Робить два артефакти:
     scripts/migrate/destinations.json     — ЖИВА таблиця вже створених призначень (її читають обізнані агенти)
     scripts/migrate/chunks/<book>-N.json  — шматки ≤size тем із усім, що агентові треба знати */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const NL = String.fromCharCode(10);
const argv = process.argv.slice(2);
const get = k => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : null; };
const BOOK = get("--book"), SIZE = parseInt(get("--size") || "150", 10);
if (!BOOK) { console.error("ужиток: node scripts/migrate/make-chunks.js --book book/physics [--size 150]"); process.exit(2); }

/* --- 1. жива таблиця призначень: усе, що вже є в root/ --- */
const shelf = JSON.parse(fs.readFileSync(path.join(R, "root/shelf.json"), "utf8"));
const dest = { schema: 7, kinds: [] };
for (const K of shelf.kinds) {
  const entry = { kind: K.kind, shelf: K.shelf, words: K.words, asks: K.asks, books: [] };
  for (const b of K.books) {
    const mf = path.join(R, "root", K.dir, b, "manifest.json");
    if (!fs.existsSync(mf)) { entry.books.push({ book: b, groups: [] }); continue; }
    const m = JSON.parse(fs.readFileSync(mf, "utf8"));
    entry.books.push({ book: b, title: m.title,
      groups: (m.groups || []).map(g => ({ slug: g.slug, title: g.title,
        chapters: (g.chapters || []).map(c => ({ slug: c.slug, title: c.title, topics: (c.topics || []).length })) })) });
  }
  dest.kinds.push(entry);
}
fs.writeFileSync(path.join(__dirname, "destinations.json"), JSON.stringify(dest, null, 2) + NL, "utf8");
let nb = 0; dest.kinds.forEach(k => nb += k.books.length);
console.log("destinations.json: видів " + dest.kinds.length + ", книг уже в root/ " + nb);
/* --- 2. шматки книги (будь-яка форма маніфесту) --- */
const M = require("./_manifest.js");
let src;
try { src = M.read(BOOK, R); } catch (e) { console.error(e.message); process.exit(2); }
if (src.form === "guide" || src.form === "guide-legacy") {
  console.error("Це курс. Порядок кроків у курсі АВТОРСЬКИЙ — розкладати агентами нічого.");
  console.error("Вживай: node scripts/migrate/migrate-course.js " + BOOK + " [--apply]");
  process.exit(2);
}
const items = src.topics.filter(t => t.slug).map(t => ({
  slug: t.slug, title: t.title, from: t.dir,
  section: t.container, sectionTitle: t.containerTitle, scope: t.scope,
  written: fs.existsSync(path.join(R, t.dir)),
  manifestOnly: !fs.existsSync(path.join(R, t.dir)),   // ще не писана: переїжджає лише запис
  inserts: Object.keys(t.inserts).reduce((n, k) => n + t.inserts[k].length, 0),
}));
if (!items.length) { console.log("у книзі нема тем — шматків не буде"); process.exit(0); }

/* межі секцій де влазить; секцію понад SIZE ріжемо за порядком */
const chunks = []; let cur = [];
const secOrder = [];
items.forEach(i => { if (secOrder.indexOf(i.section) < 0) secOrder.push(i.section); });
for (const secSlug of secOrder) {
  const sec = items.filter(i => i.section === secSlug);
  if (!sec.length) continue;
  if (sec.length > SIZE) {
    if (cur.length) { chunks.push(cur); cur = []; }
    for (let i = 0; i < sec.length; i += SIZE) chunks.push(sec.slice(i, i + SIZE));
    continue;
  }
  if (cur.length + sec.length > SIZE) { chunks.push(cur); cur = []; }
  cur = cur.concat(sec);
}
if (cur.length) chunks.push(cur);

const dir = path.join(__dirname, "chunks");
fs.mkdirSync(dir, { recursive: true });
const tag = BOOK.split("/").join("-");
for (const f of fs.readdirSync(dir)) if (f.indexOf(tag + "-") === 0) fs.unlinkSync(path.join(dir, f));
chunks.forEach((c, i) => {
  const f = path.join(dir, tag + "-" + (i + 1) + ".json");
  fs.writeFileSync(f, JSON.stringify({
    book: BOOK, bookTitle: src.title, chunk: i + 1, of: chunks.length, topics: c
  }, null, 2) + NL, "utf8");
});
console.log("книга " + BOOK + ": тем " + items.length + ", шматків " + chunks.length +
  "   (" + chunks.map(c => c.length).join(", ") + ")");
console.log("файли: scripts/migrate/chunks/" + tag + "-1..." + chunks.length + ".json");
