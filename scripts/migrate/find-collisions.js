/* scripts/migrate/find-collisions.js — пре-прохід перед міграцією (локальний, 0 токенів).
   Шукає дві різні біди:
     A) ОДНАКОВИЙ SLUG у різних книгах  → ризик зіткнення шляхів у root/<вид>/<книга>/<тема>/
     B) ОДНАКОВА НАЗВА при різних слугах → семантичний дубль (шляхи не зіткнуться, але це одне й те саме)
   Міряє прозу кожної статті, щоб підказати «одна двічі» (обсяги близькі) vs «різні кути».
   Пише scripts/migrate/collisions.json — вхід для агента-класифікатора. */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const KINDS = {
  // chemistry ПЕРЕЇХАЛА в course/basic-chemistry — старий manifest.js ще на місці, але теми там уже немає
  book: ["physics","math","electronics","programming","communications","algorithms","philosophy"],
  catalog: ["boards","connect","sensors","power","actuators","instruments","components"],
  reference: ["unix-linux","cpp-standards","build-systems","media-vision","qgroundcontrol"],
};
const COURSE = { "course": ["basic-chemistry"] };   // хімія вже переїхала

function loadJs(f, key) { const w = { __BOOKS__: [], __GUIDES__: [] };
  try { new Function("window", fs.readFileSync(f, "utf8"))(w) } catch (e) { return null } return (w[key] || [])[0]; }
function words(file) { if (!fs.existsSync(file)) return 0;
  return fs.readFileSync(file, "utf8")
    .replace(/```[\s\S]*?```/g, " ").replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
    .replace(/[#>*_`|-]/g, " ").split(/\s+/).filter(w => w.length > 1).length; }

const all = [];
for (const [kind, slugs] of Object.entries(KINDS))
  for (const s of slugs) {
    const m = loadJs(path.join(R, kind, s, "manifest.js"), "__BOOKS__"); if (!m) continue;
    for (const sec of m.sections || []) for (const t of sec.topics || []) {
      const dir = path.join(R, kind, s, sec.slug, t.slug);
      all.push({ book: s, kindDir: kind, section: sec.slug, slug: t.slug, title: t.title,
        pathRel: kind + "/" + s + "/" + sec.slug + "/" + t.slug,
        words: words(path.join(dir, t.slug + "-d.md")) || words(path.join(dir, t.slug + ".md")) });
    }
  }
// нове дерево: manifest.json зі схемою groups→chapters→topics
for (const [kind, slugs] of Object.entries(COURSE))
  for (const s of slugs) {
    const f = path.join(R, kind, s, "manifest_v2.json");
    if (!fs.existsSync(f)) continue;
    const m = JSON.parse(fs.readFileSync(f, "utf8"));
    for (const g of m.groups || []) for (const c of g.chapters || []) for (const t of c.topics || []) {
      const dir = path.join(R, kind, s, t.slug);
      all.push({ book: s, kindDir: kind, section: g.slug + "/" + c.slug, slug: t.slug, title: t.title,
        pathRel: kind + "/" + s + "/" + t.slug,
        words: words(path.join(dir, t.slug + "-d.md")) || words(path.join(dir, t.slug + ".md")) });
    }
  }

// власні статті курсів (у guide вони теж теми й теж можуть зіткнутися)
for (const g of ["embedded","embedded-ultra","progarch","unix"]) {
  const m = loadJs(path.join(R, "guide", g, "manifest.js"), "__GUIDES__"); if (!m) continue;
  for (const mo of m.modules || []) for (const c of mo.chapters || []) for (const st of c.steps || []) {
    if (!st.slug) continue;                                    // ref-крок — не стаття
    const dir = path.join(R, "guide", g, mo.slug, st.slug);
    all.push({ book: g, kindDir: "guide", section: mo.slug, slug: st.slug, title: st.title,
      pathRel: "guide/" + g + "/" + mo.slug + "/" + st.slug,
      words: words(path.join(dir, st.slug + "-d.md")) || words(path.join(dir, st.slug + ".md")) });
  }
}

const norm = t => String(t || "").toLowerCase().replace(/[«»"'`\u2019\u02bc()]/g, "").replace(/\s+/g, " ").trim();
function group(keyfn) { const g = {}; for (const a of all) { const k = keyfn(a); if (k) (g[k] = g[k] || []).push(a) } return g; }

const A = [], B = [];
for (const [slug, arr] of Object.entries(group(a => a.slug)))
  if (new Set(arr.map(a => a.book)).size > 1)
    A.push({ key: slug, kind: "same-slug", items: arr.map(a => ({ path: a.pathRel, title: a.title, words: a.words })) });
for (const [t, arr] of Object.entries(group(a => norm(a.title))))
  if (new Set(arr.map(a => a.slug)).size > 1)
    B.push({ key: t, kind: "same-title", items: arr.map(a => ({ path: a.pathRel, slug: a.slug, words: a.words })) });

const out = { generated: "pre-migration", totalTopics: all.length, sameSlug: A, sameTitle: B };
fs.writeFileSync(path.join(__dirname, "collisions.json"), JSON.stringify(out, null, 2) + "\n", "utf8");
console.log("тем у корпусі: " + all.length);
console.log("A. однаковий SLUG у різних книгах: " + A.length + " груп (" + A.reduce((n, g) => n + g.items.length, 0) + " статей)");
console.log("B. однакова НАЗВА, різні слуги:    " + B.length + " груп (" + B.reduce((n, g) => n + g.items.length, 0) + " статей)");
// підказка «одна двічі»: обсяги в межах ±25%
const близькі = A.filter(g => { const w = g.items.map(i => i.words).filter(Boolean); if (w.length < 2) return false;
  return Math.min(...w) / Math.max(...w) > 0.75; });
console.log("   з них обсяги близькі (±25%) — ймовірно ОДНА стаття двічі: " + близькі.length);
console.log("написано scripts/migrate/collisions.json");
