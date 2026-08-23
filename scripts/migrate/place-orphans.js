/* place-orphans.js <курс> — заводить написані статті-сироти в томи нового змісту.
   План лежить у scripts/migrate/plan-orphans-<курс>.json:
     [{ vol, chapter:{slug,title}, after|into, afterTopic, topics:[ {own}|{ref,title?} ] }]
   Крок own-статті береться з СТАРОГО guide-маніфесту цілком (статуси версій і вставок),
   назва — з поля title плану, якщо стара була заглушкою («DH», «Варіант А», «Компакт-вибір»).
   Назви ref-кроків — з маніфестів книг. Скрипт сам перевіряє, що жодна сирота не лишилась
   і жодна не заведена двічі. */
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..", "..");
process.chdir(ROOT);

const course = process.argv[2];
if (!course) { console.error("вкажи курс"); process.exit(1); }
const DIR = "root/course/" + course;
const PLAN = JSON.parse(fs.readFileSync("scripts/migrate/plan-orphans-" + course + ".json", "utf8"));

/* назви ref-цілей із книг */
global.window = { __BOOKS__: [], __GUIDES__: [] };
for (const r of ["book", "catalog", "reference"]) {
  if (!fs.existsSync(r)) continue;
  for (const b of fs.readdirSync(r)) {
    const mf = r + "/" + b + "/manifest.js";
    if (fs.existsSync(mf)) require(path.resolve(mf));
  }
}
const refTitle = {};
for (const bk of window.__BOOKS__)
  for (const s of bk.sections || [])
    for (const t of s.topics || []) refTitle[bk.slug + "/" + t.slug] = t.title;

/* старі кроки курсу — джерело статусів */
require(path.resolve("guide/" + course + "/manifest.js"));
const oldStep = {};
for (const g of window.__GUIDES__) {
  if (g.slug !== course) continue;
  for (const m of g.modules || [])
    for (const ch of m.chapters || [])
      for (const st of ch.steps || []) if (st.slug) oldStep[st.slug] = st;
}

/* сироти = теки без кроку в новому змісті */
const man = JSON.parse(fs.readFileSync(DIR + "/manifest.json", "utf8"));
const vols = {};
const claimed = new Set();
for (const s of man.groups) {
  vols[s] = JSON.parse(fs.readFileSync(DIR + "/" + s + ".json", "utf8"));
  for (const ch of vols[s].chapters) for (const t of ch.topics) if (t.slug) claimed.add(t.slug);
}
const orphans = new Set(fs.readdirSync(DIR)
  .filter(x => fs.statSync(DIR + "/" + x).isDirectory() && !claimed.has(x)));

/* збірка кроку */
const placed = new Set();
function mkTopic(spec) {
  if (spec.ref) return { ref: spec.ref, title: spec.title || refTitle[spec.ref] || "?" };
  const s = spec.own;
  if (!orphans.has(s)) { console.error("НЕ СИРОТА або нема теки: " + s); process.exit(1); }
  if (placed.has(s)) { console.error("ДВІЧІ: " + s); process.exit(1); }
  placed.add(s);
  const st = JSON.parse(JSON.stringify(oldStep[s] || { slug: s, title: s, basic: { status: "empty" }, detailed: { status: "done" } }));
  if (spec.title) st.title = spec.title;
  const out = { slug: st.slug, title: st.title };
  for (const k of ["basic", "detailed", "hist", "comp", "math", "proj", "api"]) if (st[k]) out[k] = st[k];
  return out;
}

/* застосування */
let newCh = 0, added = 0, dropped = 0;
for (const op of PLAN) {
  const v = vols[op.vol];
  if (!v) { console.error("нема тому " + op.vol); process.exit(1); }

  if (op.drop) {                                   // прибрати ненаписані винаходи, чию роль
    for (const ch of v.chapters) {                 // перебирають написані статті
      const before = ch.topics.length;
      ch.topics = ch.topics.filter(t => !(t.slug && op.drop.includes(t.slug)));
      dropped += before - ch.topics.length;
    }
  }

  const topics = (op.topics || []).map(mkTopic);
  added += topics.filter(t => t.slug).length;

  if (op.chapter) {                                // новий розділ
    const ch = { slug: op.chapter.slug, title: op.chapter.title, topics: topics };
    let at = v.chapters.length;
    if (op.after) { const i = v.chapters.findIndex(c => c.slug === op.after);
      if (i < 0) { console.error("нема розділу " + op.after); process.exit(1); } at = i + 1; }
    if (op.before) { const i = v.chapters.findIndex(c => c.slug === op.before);
      if (i < 0) { console.error("нема розділу " + op.before); process.exit(1); } at = i; }
    v.chapters.splice(at, 0, ch);
    newCh++;
    console.log("  + розділ «" + ch.title + "» у томі «" + v.title + "» — " + topics.length + " кроків");
  } else {                                         // у наявний розділ
    const ch = v.chapters.find(c => c.slug === op.into);
    if (!ch) { console.error("нема розділу " + op.into); process.exit(1); }
    let at = op.atStart ? 0 : ch.topics.length;
    if (op.afterTopic) { const i = ch.topics.findIndex(t => (t.slug || t.ref) === op.afterTopic);
      if (i < 0) { console.error("нема кроку " + op.afterTopic + " у " + op.into); process.exit(1); } at = i + 1; }
    ch.topics.splice(at, 0, ...topics);
    console.log("  → «" + ch.title + "» (том «" + v.title + "»): +" + topics.length);
  }
}

const left = [...orphans].filter(s => !placed.has(s));
if (left.length) { console.error("\nНЕ ЗАВЕДЕНО (" + left.length + "): " + left.join(" · ")); process.exit(1); }

for (const s of man.groups) fs.writeFileSync(DIR + "/" + s + ".json", JSON.stringify(vols[s], null, 2) + "\n");
console.log("\n" + course + ": заведено " + added + " статей, нових розділів " + newCh +
  (dropped ? ", прибрано ненаписаних кроків " + dropped : "") + "; сиріт не лишилось");
