/* chemistry/m2-bonds/manifest.js — per-module маніфест Модуля 2. Складає scripts/bookbuild.js.
   Хімія: вставок нема (histories[]/extras[] порожні), є лише теми. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: 2, slug: "m2-bonds", title: "Як атоми тримаються разом",
  chapters: [
    { n: "1", title: "Хімічний зв'язок", dir: "m2-bonds/r1-bonding", main: "r1-bonding.md", status: "done",
      scope: "Чому атоми з'єднуються; іонний, ковалентний і металічний зв'язок",
      topics: [
        { mrt: "2.1.1", title: "Чому атоми з'єднуються", status: "done" },
        { mrt: "2.1.2", title: "Іонний і ковалентний зв'язок", status: "done" },
        { mrt: "2.1.3", title: "Металічний зв'язок", status: "done" }
      ] },
    { n: "2", title: "Формули, валентність і моль", dir: "m2-bonds/r2-formulas", main: "r2-formulas.md", status: "done",
      scope: "Читання хімічних формул, валентність як «руки» атома, моль і молярна маса",
      topics: [
        { mrt: "2.2.1", title: "Мова формул", status: "done" },
        { mrt: "2.2.2", title: "Валентність — скільки рук", status: "done" },
        { mrt: "2.2.3", title: "Моль: рахуємо атоми вагою", status: "done" }
      ] },
    { n: "3", title: "Як влаштовані тверді речовини", dir: "m2-bonds/r3-structure", main: "r3-structure.md", status: "done",
      scope: "Молекулярні та ґраткові речовини; чому властивості визначаються типом зв'язку",
      topics: [
        { mrt: "2.3.1", title: "Молекули чи ґратка", status: "done" },
        { mrt: "2.3.2", title: "Чому речовини такі різні", status: "done" }
      ] }
  ]
});
