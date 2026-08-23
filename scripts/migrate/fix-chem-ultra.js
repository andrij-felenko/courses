/* fix-chem-ultra.js
   1) basic-chemistry — один том без назви: слуг ".", назва = назва книги.
   2) embedded-ultra — 22 «томи» (насправді модулі) зводяться у два.
   3) basic-chemistry — посилання в статтях у шестисегментну адресу:
        root:course/basic-chemistry/./<розділ>/<тема>/<версія>
      Плюс лагодяться забуті book:chemistry/… — книги chemistry вже немає. */
const fs = require("fs");
const path = require("path");
const ROOT = path.resolve(__dirname, "..", "..", "root");

/* ---------- 1. хімія: один том ---------- */
const CH = path.join(ROOT, "course", "basic-chemistry");
const chMan = JSON.parse(fs.readFileSync(path.join(CH, "manifest.json"), "utf8"));
if (chMan.groups.length !== 1 || chMan.groups[0] !== ".") {
  const chapters = [];
  for (const s of chMan.groups) {
    const v = JSON.parse(fs.readFileSync(path.join(CH, s + ".json"), "utf8"));
    for (const c of v.chapters) chapters.push(c);
    fs.unlinkSync(path.join(CH, s + ".json"));
  }
  const vol = { schema: chMan.schema, kind: chMan.kind, book: chMan.slug,
    slug: ".", title: chMan.title, scope: "", chapters: chapters };
  fs.writeFileSync(path.join(CH, "_.json"), JSON.stringify(vol, null, 2) + "\n");
  chMan.groups = ["."];
  fs.writeFileSync(path.join(CH, "manifest.json"), JSON.stringify(chMan, null, 2) + "\n");
  console.log("хімія: один том «" + chMan.title + "», розділів " + chapters.length +
    ", файл _.json (слуг \".\" — крапка в імені файлу неможлива)");
}

/* ---------- 2. embedded-ultra: два томи ---------- */
const EU = path.join(ROOT, "course", "embedded-ultra");
const euMan = JSON.parse(fs.readFileSync(path.join(EU, "manifest.json"), "utf8"));
if (euMan.groups.length > 2) {
  const parts = [
    { slug: "elektronika-y-mikrokontroler", title: "Електроніка й мікроконтролер", take: 13 },
    { slug: "zvyazok-i-aparat", title: "Зв'язок і апарат", take: 9 },
  ];
  let i = 0;
  const keep = [];
  for (const p of parts) {
    const chapters = [];
    for (let k = 0; k < p.take; k++, i++) {
      const s = euMan.groups[i];
      const v = JSON.parse(fs.readFileSync(path.join(EU, s + ".json"), "utf8"));
      for (const c of v.chapters) chapters.push(c);
      fs.unlinkSync(path.join(EU, s + ".json"));
    }
    const vol = { schema: euMan.schema, kind: euMan.kind, book: euMan.slug,
      slug: p.slug, title: p.title, scope: "", chapters: chapters };
    fs.writeFileSync(path.join(EU, p.slug + ".json"), JSON.stringify(vol, null, 2) + "\n");
    let n = 0; for (const c of chapters) n += c.topics.length;
    console.log("embedded-ultra: «" + p.title + "» — розділів " + chapters.length + ", кроків " + n);
    keep.push(p.slug);
  }
  euMan.groups = keep;
  fs.writeFileSync(path.join(EU, "manifest.json"), JSON.stringify(euMan, null, 2) + "\n");
}

/* ---------- 3. хімія: посилання в шестисегментну адресу ---------- */
const vol = JSON.parse(fs.readFileSync(path.join(CH, "_.json"), "utf8"));
const addr = Object.create(null);            // слуг теми → повна адреса
for (const c of vol.chapters)
  for (const t of c.topics) {
    const ver = (t.basic && t.basic.status !== "empty") ? "b" : "d";
    addr[t.slug] = "root:course/basic-chemistry/./" + c.slug + "/" + t.slug + "/" + ver;
  }

let files = 0, rewritten = 0, stale = [];
function walk(dir) {
  for (const f of fs.readdirSync(dir)) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) { walk(p); continue; }
    if (!/\.md$/.test(f)) continue;
    let s = fs.readFileSync(p, "utf8"), before = s;
    s = s.replace(/root:basic-chemistry\/([a-z0-9-]+)/g, function (m, slug) {
      if (!addr[slug]) { stale.push("root:basic-chemistry/" + slug); return m; }
      rewritten++; return addr[slug];
    });
    s = s.replace(/book:chemistry\/([a-z0-9-]+)/g, function (m, slug) {
      if (!addr[slug]) { stale.push("book:chemistry/" + slug); return m; }
      rewritten++; return addr[slug];
    });
    if (s !== before) { fs.writeFileSync(p, s); files++; }
  }
}
walk(CH);
console.log("посилань переписано " + rewritten + " у " + files + " файлах");
if (stale.length) {
  const u = Array.from(new Set(stale));
  console.log("не знайшлося цілі (" + u.length + "): " + u.join(" · "));
}
