/* make-outline.js — повний кістяк курсу одним файлом, щоб агент бачив усе одразу.
   node scripts/migrate/make-outline.js <курс> */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const M = require("./_manifest.js");
const NL = String.fromCharCode(10);
const C = process.argv[2];
if (!C) { console.error("ужиток: node scripts/migrate/make-outline.js embedded"); process.exit(2); }
const base = fs.existsSync(path.join(R, "guide", C)) ? "guide/" + C : "root/course/" + C;
const raw = { __BOOKS__: [], __GUIDES__: [] };
const src = M.read(base, R);
const file = src.file;
let mods;
if (file.endsWith(".json")) { const j = JSON.parse(fs.readFileSync(file, "utf8"));
  mods = (j.groups || []).map(g => ({ title: g.title, slug: g.slug,
    chapters: (g.chapters || []).map(c => ({ title: c.title, steps: c.topics || [] })) }));
} else { new Function("window", fs.readFileSync(file, "utf8"))(raw);
  const g0 = raw.__GUIDES__[0];
  mods = (g0.modules || []).map(m => ({ title: m.title, slug: m.slug, chapters: m.chapters || [] })); }

const L = [];
let nStep = 0, nCh = 0;
mods.forEach((m, i) => {
  let s = 0; (m.chapters || []).forEach(c => s += (c.steps || []).length);
  L.push("");
  L.push("## Модуль " + (i + 1) + ". " + m.title + "   [" + s + " кроків, слуг: " + m.slug + "]");
  (m.chapters || []).forEach(c => { nCh++;
    L.push("  ### " + (c.title || "(без назви)"));
    (c.steps || []).forEach(st => { nStep++;
      L.push("      - " + (st.title || st.slug || st.ref) + (st.ref ? "   [ref → " + st.ref + "]" : "   [власна стаття]")); });
  });
});
const head = ["# Кістяк курсу «" + src.title + "» (" + C + ")", "",
  "Модулів: " + mods.length + " · розділів: " + nCh + " · кроків: " + nStep, ""];
const out = head.concat(L).join(NL) + NL;
const dst = path.join(__dirname, "outline-" + C + ".md");
fs.writeFileSync(dst, out, "utf8");
console.log("outline-" + C + ".md   модулів " + mods.length + ", розділів " + nCh + ", кроків " + nStep + "   (" + Math.round(out.length / 1024) + " КБ)");
