/* manifest-math.js — кореневий ІНДЕКС книги (генерується трансформом index-from-manifest.js).
   Мета книги + список модулів. Зовнішній модуль — рядок-URL "<slug>/manifest.js"
   (власний per-module файл, що робить window.__MODREG__.push({…})); ще не
   винесені модулі лишаються inline-обʼєктами. Складанням опікується
   scripts/bookbuild.js (assembleBook). Нумерація — М.Р.Т. */
window.BOOK_META = {
  "title": "Математика",
  "subtitle": "Математика курсу — пояснена від першопричини: чому вектор розкладається на незалежні складові, звідки |R|=√(Rx²+Ry²), чому інтеграл — це сума. Наповнюється за посиланнями з інших книг.",
  "shortTitle": "Математика",
  "libraryHref": "index.html",
  "basePath": "math/"
};

window.BOOK_MODULES = [
  "linear-algebra/manifest.js",
  "vector-analysis/manifest.js",
  "trigonometry-phasors/manifest.js",
  "calculus/manifest.js",
  "statistics-errors/manifest.js",
  "discrete-logic/manifest.js",
  "number-systems/manifest.js"
];
