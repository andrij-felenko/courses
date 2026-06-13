/* chemistry/m1-atoms/manifest.js — per-module маніфест Модуля 1. Складає scripts/bookbuild.js.
   Хімія: вставок нема (histories[]/extras[] порожні), є лише теми. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: 1, slug: "m1-atoms", title: "З чого все зроблено",
  chapters: [
    { n: "1", title: "Хімія і речовини", dir: "m1-atoms/r1-substances", main: "r1-substances.md", status: "done",
      scope: "Хімічне перетворення vs фізичне; ознаки реакції; чисті речовини й суміші та способи їх розділення.",
      topics: [
        { mrt: "1.1.1", title: "Речовини й перетворення", status: "done" },
        { mrt: "1.1.2", title: "Чисті речовини й суміші", status: "done" }
      ] },
    { n: "2", title: "Атом", dir: "m1-atoms/r2-atom", main: "r2-atom.md", status: "done",
      scope: "Від «чому є запах» до будови атома: ядро, електронні оболонки, елемент як кількість протонів, ізотопи.",
      topics: [
        { mrt: "1.2.1", title: "Атоми й молекули", status: "done" },
        { mrt: "1.2.2", title: "Всередині атома", status: "done" },
        { mrt: "1.2.3", title: "Елемент — це номер", status: "done" }
      ] },
    { n: "3", title: "Періодична таблиця", dir: "m1-atoms/r3-table", main: "r3-table.md", status: "done",
      scope: "Як читати клітинку таблиці; період = кількість оболонок; група = зовнішня оболонка; родини елементів і їхні характери.",
      topics: [
        { mrt: "1.3.1", title: "Як читати таблицю", status: "done" },
        { mrt: "1.3.2", title: "Родини елементів", status: "done" }
      ] }
  ]
});
