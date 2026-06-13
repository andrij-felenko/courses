/* split-modules.js — розкласти legacy-manifest (window.BOOK) на per-module файли.
   Для КОЖНОГО модуля пише `<basePath><slug>/manifest.js`, що робить
   window.__MODREG__.push(<обʼєкт модуля>). Для книг-довідників (math/components),
   де розділ = самостійна тема, обʼєкт модуля переноситься як є (без topics[]).

   Запуск:  node scripts/split-modules.js <manifest.js> <basePath>
   напр.:   node scripts/split-modules.js manifest-math.js math/
*/
"use strict";
const fs = require("fs");
const path = require("path");
const [, , file, basePath] = process.argv;
if (!file || !basePath) { console.error("Вкажи <manifest.js> <basePath>"); process.exit(1); }

const window = {};
eval(fs.readFileSync(file, "utf8"));               // задає window.BOOK
const BOOK = window.BOOK;
if (!BOOK || !BOOK.modules) { console.error("немає window.BOOK.modules"); process.exit(1); }

let wrote = 0;
BOOK.modules.forEach(function (m) {
  if (!m.slug) { console.warn("модуль без slug, пропускаю: n=" + m.n); return; }
  const dir = path.join(basePath, m.slug);
  fs.mkdirSync(dir, { recursive: true });
  const body =
`/* ${basePath}${m.slug}/manifest.js — per-module маніфест (генерується split-modules.js).
   Книга-довідник: розділ = самостійна тема. Складає scripts/bookbuild.js. */
(window.__MODREG__ = window.__MODREG__ || []).push(
${JSON.stringify(m, null, 2)}
);
`;
  fs.writeFileSync(path.join(dir, "manifest.js"), body);
  wrote++;
});
console.log("OK: " + wrote + " per-module маніфестів під " + basePath);
