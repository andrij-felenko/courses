/* mkbook-python.js — з опису scripts/migrate/final/books/book-python.md
   будує reference/python/manifest.js за схемою §2 (нова тема: basic:empty + detailed:pending). */
const fs = require("fs");
const path = require("path");
const NL = String.fromCharCode(10);

const src = path.resolve(__dirname, "final", "books", "book-python.md");
const L = fs.readFileSync(src, "utf8").split(/\r?\n/);

const secs = [];
let cur = null, wantScope = false;

for (const ln of L) {
  const h = ln.match(/^##\s+(\d+)\.\s+`([a-z0-9-]+)`\s+—\s+(.+?)\s*$/);
  if (h) { cur = { slug: h[2], title: h[3].trim(), scope: "", topics: [] }; secs.push(cur); wantScope = true; continue; }
  if (/^##\s/.test(ln)) { cur = null; continue; }
  if (!cur) continue;
  if (wantScope) {
    const m = ln.match(/^\*(.+)\*\s*$/);
    if (m) { cur.scope = m[1].trim(); wantScope = false; }
  }
  const t = ln.match(/^\|\s*`([a-z0-9-]+)`\s*\|\s*(.+?)\s*\|\s*$/);
  if (t) cur.topics.push({ slug: t[1], title: t[2].trim() });
}

let tot = 0, dup = 0;
const seen = Object.create(null);
for (const s of secs) {
  tot += s.topics.length;
  for (const t of s.topics) { if (seen[t.slug]) { dup++; console.log("  ДУБЛЬ: " + t.slug); } seen[t.slug] = 1; }
}
console.log("розділів " + secs.length + ", тем " + tot + (dup ? "  ДУБЛІ " + dup : "  дублів нема"));
for (const s of secs) console.log("  " + s.slug + " (" + s.topics.length + ") — " + s.title);

const q = JSON.stringify;
let o = "/* manifest */" + NL;
o += "(window.__BOOKS__ = window.__BOOKS__ || []).push({" + NL;
o += "  type: \"reference\", slug: \"python\", title: \"Python\"," + NL;
o += "  sections: [" + NL;
for (const s of secs) {
  o += "    { slug: " + q(s.slug) + ", title: " + q(s.title) + ", scope: " + q(s.scope) + "," + NL;
  o += "      topics: [" + NL;
  for (const t of s.topics) {
    o += "        { slug: " + q(t.slug) + ", title: " + q(t.title) +
         ", basic: { status: \"empty\" }, detailed: { status: \"pending\" } }," + NL;
  }
  o += "      ] }," + NL;
}
o += "  ]" + NL + "});" + NL;

const outDir = path.resolve(__dirname, "..", "..", "reference", "python");
fs.mkdirSync(outDir, { recursive: true });
fs.writeFileSync(path.join(outDir, "manifest.js"), o);
console.log("записано reference/python/manifest.js (" + o.length + " байтів)");
