/* catalog/pcb-board/manifest.js — книга-каталог «Плати живлення й захисту» (тип "catalog").
   Схема — AUTHORING.md §2. Статуси: done | empty | update | deeper | recheck. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "catalog", slug: "pcb-board", title: "Плати живлення й захисту",
  sections: [
    { slug: "power", title: "Живлення", scope: "Модулі перетворення та стабілізації живлення.",
      topics: [
        { slug: "ldo-regulator", title: "LDO-стабілізатор", status: "empty" },
        { slug: "buck-converter", title: "Понижувач (buck)", status: "empty" },
        { slug: "boost-converter", title: "Підвищувач (boost)", status: "empty" },
      ] },
    { slug: "protection", title: "Захист", scope: "Модулі захисту входів і ліній.",
      topics: [
        { slug: "tvs-esd", title: "TVS/ESD-захист", status: "empty" },
      ] },
  ]
});
