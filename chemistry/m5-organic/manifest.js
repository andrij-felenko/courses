/* chemistry/m5-organic/manifest.js — per-module маніфест Модуля 5. Складає scripts/bookbuild.js.
   Хімія: вставок нема (histories[]/extras[] порожні), є лише теми. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: 5, slug: "m5-organic", title: "Органіка: хімія життя",
  chapters: [
    { n: "1", title: "Карбон і його ланцюги", dir: "m5-organic/r1-carbon", main: "r1-carbon.md", status: "done",
      scope: "Чому Карбон утворює мільйони сполук, вуглеводні як паливо, полімери з мономерів.",
      topics: [
        { mrt: "5.1.1", title: "Чому Карбон особливий", status: "done" },
        { mrt: "5.1.2", title: "Вуглеводні: паливо світу", status: "done" },
        { mrt: "5.1.3", title: "Полімери", status: "done" }
      ] },
    { n: "2", title: "Кисень приєднується: спирти, кислоти, жири", dir: "m5-organic/r2-oxygen-compounds", main: "r2-oxygen-compounds.md", status: "done",
      scope: "Спирти і карбонові кислоти як сходинки окиснення; естери, жири і принцип дії мила.",
      topics: [
        { mrt: "5.2.1", title: "Спирти і кислоти: окиснення по сходинках", status: "done" },
        { mrt: "5.2.2", title: "Естери і жири", status: "done" }
      ] },
    { n: "3", title: "Молекули життя", dir: "m5-organic/r3-life-molecules", main: "r3-life-molecules.md", status: "done",
      scope: "Вуглеводи, жири і білки як молекули клітини; кухня як хімічна лабораторія; місток до Модуля 6.",
      topics: [
        { mrt: "5.3.1", title: "Вуглеводи", status: "done" },
        { mrt: "5.3.2", title: "Жири і білки", status: "done" },
        { mrt: "5.3.3", title: "Кухня — твоя лабораторія", status: "done" },
        { mrt: "5.3.4", title: "Куди далі (епілог; фігури не обов'язкові)", status: "done" }
      ] }
  ]
});
