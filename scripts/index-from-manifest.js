/* index-from-manifest.js — трансформ кореневого manifest → ІНДЕКС книги.
   Виносить задані модулі у рядок-URL "<slug>/manifest.js" (свій per-module
   файл), решту лишає inline-обʼєктами. Детермінований — без ручного копіювання.

   Запуск:  node scripts/index-from-manifest.js <manifest.js> <N...>
   напр.:   node scripts/index-from-manifest.js manifest.js 1
*/
"use strict";
const fs = require("fs");
const args = process.argv.slice(2);
const file = args[0];
const ext = new Set(args.slice(1).map(Number));        // номери модулів → зовнішні
if (!file) { console.error("Вкажи файл manifest.js"); process.exit(1); }

const src = fs.readFileSync(file, "utf8");
const window = {};
eval(src);                                             // задає window.BOOK
const BOOK = window.BOOK;
if (!BOOK || !BOOK.modules) { console.error("У файлі немає window.BOOK.modules"); process.exit(1); }

const meta = {
  title: BOOK.title,
  subtitle: BOOK.subtitle,
  shortTitle: BOOK.shortTitle,
  libraryHref: BOOK.libraryHref,
  basePath: BOOK.basePath,
};
const indent = (s) => s.replace(/\n/g, "\n  ");
const modEntry = (m) => ext.has(m.n)
  ? JSON.stringify(`${m.slug}/manifest.js`)
  : indent(JSON.stringify(m, null, 2));

const out =
`/* ${file} — кореневий ІНДЕКС книги (генерується трансформом index-from-manifest.js).
   Мета книги + список модулів. Зовнішній модуль — рядок-URL "<slug>/manifest.js"
   (власний per-module файл, що робить window.__MODREG__.push({…})); ще не
   винесені модулі лишаються inline-обʼєктами. Складанням опікується
   scripts/bookbuild.js (assembleBook). Нумерація — М.Р.Т. */
window.BOOK_META = ${JSON.stringify(meta, null, 2)};

window.BOOK_MODULES = [
  ${BOOK.modules.map(modEntry).join(",\n  ")}
];
`;
fs.writeFileSync(file, out);
console.log(`OK: ${file} → індекс. Зовнішні модулі: ${[...ext].join(", ") || "—"}. Усього модулів: ${BOOK.modules.length}.`);
