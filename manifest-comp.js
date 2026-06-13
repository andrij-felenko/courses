/* manifest-comp.js — кореневий ІНДЕКС книги (генерується трансформом index-from-manifest.js).
   Мета книги + список модулів. Зовнішній модуль — рядок-URL "<slug>/manifest.js"
   (власний per-module файл, що робить window.__MODREG__.push({…})); ще не
   винесені модулі лишаються inline-обʼєктами. Складанням опікується
   scripts/bookbuild.js (assembleBook). Нумерація — М.Р.Т. */
window.BOOK_META = {
  "title": "Компоненти",
  "subtitle": "Каталог компонентів за секторами — давачі, живлення, зв'язок, приводи, пам'ять, інтерфейси, захист, пасивні, активні, дисплеї. Той самий матеріал, що в прикладних темах інших книг, але згрупований за фізичними пристроями.",
  "shortTitle": "Компоненти",
  "libraryHref": "index.html",
  "basePath": "components/"
};

window.BOOK_MODULES = [
  "sensors/manifest.js",
  "power/manifest.js",
  "comms/manifest.js",
  "actuators/manifest.js",
  "memory/manifest.js",
  "interfaces/manifest.js",
  "protection/manifest.js",
  "passive/manifest.js",
  "active/manifest.js",
  "displays/manifest.js"
];
