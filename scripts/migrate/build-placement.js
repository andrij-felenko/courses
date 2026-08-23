/* build-placement.js — з результату батчу робить файли розкладки для migrate-book.js.
   node scripts/migrate/build-placement.js <votes.json>
   votes.json — те, що повернув воркфлоу place-batch: { results: [ { file, placements: [...] } ] }
   На виході: scripts/migrate/placements/<kind>-<book>.json  (по одному на цільову книгу) */
const fs = require("fs"), path = require("path");
const NL = String.fromCharCode(10);
const VF = process.argv[2];
if (!VF) { console.error("ужиток: node scripts/migrate/build-placement.js <votes.json>"); process.exit(2); }
const V = JSON.parse(fs.readFileSync(VF, "utf8"));

/* довідка про теми з файлів-шматків: from, title */
/* довідка ключується ШМАТКОМ + слугом: один слуг живе у 20 випадках у двох книгах,
   глобальний ключ віддав би обом однакове джерело */
const meta = {}, chunkTopics = {};
for (const r of V.results || []) {
  const c = JSON.parse(fs.readFileSync(path.resolve(path.dirname(VF), "..", "..", r.file), "utf8"));
  meta[r.file] = {};
  chunkTopics[r.file] = (c.topics || []).map(t => t.slug);
  for (const t of c.topics || []) meta[r.file][t.slug] = t;
}
/* ЗВІРКА ВХІД == ВИХІД: жодна тема не має зникнути між шматком і розкладкою */
const lost = [];
for (const r of V.results || []) {
  const got = new Set((r.placements || []).filter(p => p.kind && p.book && p.group && p.chapter).map(p => p.slug));
  for (const s2 of chunkTopics[r.file]) if (!got.has(s2)) lost.push(r.file + "  ->  " + s2);
}
if (lost.length) {
  console.error("СТОП — теми зникли між шматком і розкладкою (" + lost.length + "):");
  lost.slice(0, 20).forEach(l => console.error("   " + l));
  if (lost.length > 20) console.error("   … і ще " + (lost.length - 20));
  console.error("Розкладка неповна: або агент пропустив тему, або сегмент лишився без кворуму.");
  process.exit(1);
}

const books = {};
let skipped = 0;
for (const r of V.results || []) for (const p of r.placements || []) {
  if (!p.kind || !p.book || !p.group || !p.chapter) { skipped++; continue; }
  const m = meta[r.file][p.slug];
  if (!m) { skipped++; continue; }
  const key = p.kind + "/" + p.book;
  const B = books[key] = books[key] || { target: { kind: p.kind, book: p.book, title: p.bookTitle || p.book }, groups: [] };
  let G = B.groups.find(g => g.slug === p.group);
  if (!G) { G = { slug: p.group, title: p.groupTitle || p.group, scope: "", chapters: [] }; B.groups.push(G); }
  let C = G.chapters.find(c => c.slug === p.chapter);
  if (!C) { C = { slug: p.chapter, title: p.chapter === "." ? "" : (p.chapterTitle || p.chapter), topics: [] }; G.chapters.push(C); }
  C.topics.push({ slug: p.slug, title: m.title, from: m.from });
}

const dir = path.join(__dirname, "placements");
fs.mkdirSync(dir, { recursive: true });
const rows = [];
for (const key of Object.keys(books)) {
  const B = books[key], f = path.join(dir, key.split("/").join("-") + ".json");
  fs.writeFileSync(f, JSON.stringify(B, null, 2) + NL, "utf8");
  let n = 0, ch = 0; B.groups.forEach(g => { ch += g.chapters.length; g.chapters.forEach(c => n += c.topics.length); });
  rows.push({ key, groups: B.groups.length, chapters: ch, topics: n, file: path.relative(path.join(__dirname, "../.."), f) });
}
rows.sort((a, b) => b.topics - a.topics);
console.log("книг-цілей: " + rows.length + (skipped ? "   пропущено записів: " + skipped : ""));
rows.forEach(r => console.log("  " + r.key.padEnd(26) + "груп " + String(r.groups).padStart(3) +
  "  розділів " + String(r.chapters).padStart(3) + "  тем " + String(r.topics).padStart(4) + "   " + r.file));
console.log(NL + "далі, по книзі: node scripts/migrate/migrate-book.js <файл> [--apply]");
