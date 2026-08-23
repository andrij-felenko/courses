/* split-manifests.js — розбиває root/<вид>/<книга>/manifest.json на:
     manifest.json      — шапка книги + перелік слугів томів
     <слуг-тому>.json   — один том: слуг, назва, scope, розділи з темами
   Ідемпотентний: якщо маніфест уже розбитий (немає groups), нічого не робить. */
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..", "..", "root");

let done = 0, skipped = 0;
for (const kind of fs.readdirSync(ROOT)) {
  const kdir = path.join(ROOT, kind);
  if (!fs.statSync(kdir).isDirectory()) continue;
  for (const book of fs.readdirSync(kdir)) {
    const bdir = path.join(kdir, book);
    const mf = path.join(bdir, "manifest.json");
    if (!fs.existsSync(mf)) continue;
    const m = JSON.parse(fs.readFileSync(mf, "utf8"));
    if (!Array.isArray(m.groups)) { skipped++; continue; }

    const slugs = [];
    for (const g of m.groups) {
      const vol = { schema: m.schema, kind: m.kind, book: m.slug,
        slug: g.slug, title: g.title, scope: g.scope || "", chapters: g.chapters };
      fs.writeFileSync(path.join(bdir, g.slug + ".json"), JSON.stringify(vol, null, 2) + "\n");
      slugs.push(g.slug);
    }
    const head = { schema: m.schema, kind: m.kind, slug: m.slug, title: m.title, groups: slugs };
    fs.writeFileSync(mf, JSON.stringify(head, null, 2) + "\n");
    console.log(kind + "/" + book + ": " + slugs.length + " томів винесено");
    done++;
  }
}
console.log("книг розбито: " + done + (skipped ? ", уже розбитих: " + skipped : ""));
