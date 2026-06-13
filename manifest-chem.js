/* manifest-chem.js — кореневий ІНДЕКС книги (генерується трансформом index-from-manifest.js).
   Мета книги + список модулів. Зовнішній модуль — рядок-URL "<slug>/manifest.js"
   (власний per-module файл, що робить window.__MODREG__.push({…})); ще не
   винесені модулі лишаються inline-обʼєктами. Складанням опікується
   scripts/bookbuild.js (assembleBook). Нумерація — М.Р.Т. */
window.BOOK_META = {
  "title": "Хімія",
  "subtitle": "Коротка книжка, щоб зрозуміти, про що вся шкільна хімія — від атома до молекул життя. База 7–11 класів: просто, але до глибини.",
  "shortTitle": "Хімія",
  "libraryHref": "index.html",
  "basePath": "chemistry/"
};

window.BOOK_MODULES = [
  "m1-atoms/manifest.js",
  "m2-bonds/manifest.js",
  "m3-reactions/manifest.js",
  "m4-inorganic/manifest.js",
  "m5-organic/manifest.js",
  "m6-counting/manifest.js"
];
