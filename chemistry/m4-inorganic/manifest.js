/* chemistry/m4-inorganic/manifest.js — per-module маніфест Модуля 4. Складає scripts/bookbuild.js.
   Хімія: вставок нема (histories[]/extras[] порожні), є лише теми. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: 4, slug: "m4-inorganic", title: "Розчини, кислоти, солі й метали",
  chapters: [
    { n: "1", title: "Вода і розчини", dir: "m4-inorganic/r1-solutions", main: "r1-solutions.md", status: "done",
      scope: "Вода як розчинник, концентрація, насичений розчин, іонна дисоціація",
      topics: [
        { mrt: "4.1.1", title: "Чому вода розчиняє", status: "done" },
        { mrt: "4.1.2", title: "Скільки влізе", status: "done" },
        { mrt: "4.1.3", title: "Іони в розчині", status: "done" }
      ] },
    { n: "2", title: "Кислоти й основи", dir: "m4-inorganic/r2-acids-bases", main: "r2-acids-bases.md", status: "done",
      scope: "Кислоти (H⁺), основи (OH⁻), pH, індикатори",
      topics: [
        { mrt: "4.2.1", title: "Кислоти: спільний секрет", status: "done" },
        { mrt: "4.2.2", title: "Основи: протилежний табір", status: "done" },
        { mrt: "4.2.3", title: "pH та індикатори", status: "done" }
      ] },
    { n: "3", title: "Оксиди, солі та карта неорганіки", dir: "m4-inorganic/r3-salt-families", main: "r3-salt-families.md", status: "done",
      scope: "Оксиди металів і неметалів, нейтралізація, генетичний ланцюжок неорганіки",
      topics: [
        { mrt: "4.3.1", title: "Оксиди: все, що обнялося з киснем", status: "done" },
        { mrt: "4.3.2", title: "Солі й нейтралізація", status: "done" },
        { mrt: "4.3.3", title: "Карта неорганіки", status: "done" }
      ] },
    { n: "4", title: "Метали й елементи навколо нас", dir: "m4-inorganic/r4-metals-elements", main: "r4-metals-elements.md", status: "done",
      scope: "Ряд активності, корозія та захист заліза, портрети головних елементів",
      topics: [
        { mrt: "4.4.1", title: "Ряд активності й іржа", status: "done" },
        { mrt: "4.4.2", title: "Екскурсія елементами", status: "done" }
      ] }
  ]
});
