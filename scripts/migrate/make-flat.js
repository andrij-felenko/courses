/* make-flat.js — ПЛАСКИЙ перелік кроків курсу: без модулів, без розділів, без нумерації.
   Щоб агент будував структуру з нуля й не спирався на нинішню.
   node scripts/migrate/make-flat.js <курс> */
const fs = require("fs"), path = require("path");
const R = path.resolve(__dirname, "../..");
const M = require("./_manifest.js");
const NL = String.fromCharCode(10);
const C = process.argv[2];
if (!C) { console.error("ужиток: node scripts/migrate/make-flat.js embedded"); process.exit(2); }
const base = fs.existsSync(path.join(R, "guide", C)) ? "guide/" + C : "root/course/" + C;
const src = M.read(base, R);
const rows = src.topics.map(t => "- " + (t.title || t.slug || t.ref));
const head = ["# Усі теми курсу «" + src.title + "» — пласким списком", "",
  "Тут " + rows.length + " тем. Структури немає навмисно: ні модулів, ні розділів, ні порядку,",
  "який щось означає. Групуй і впорядковуй сам, від змісту.", ""];
const dst = path.join(__dirname, "flat-" + C + ".md");
fs.writeFileSync(dst, head.concat(rows).join(NL) + NL, "utf8");
console.log("flat-" + C + ".md   тем " + rows.length + "   (" + Math.round((head.join("").length + rows.join("").length) / 1024) + " КБ)");
