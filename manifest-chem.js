/* ──────────────────────────────────────────────────────────────────────────
   manifest-chem.js — структура книги «Хімія»
   Працює так само, як manifest.js для embedded: єдине джерело правди для
   навігації. Розділ з'являється в книзі, коли status:"done" (це робить
   loop після останньої теми розділу — або вручну).

   Нумерація — М.Р («2.1» = модуль 2, розділ 1); теми всередині файлів — М.Р.Т.
   Історичних файлів тут НЕМАЄ свідомо: у цій книзі історії — мікро-вставки
   `> 📜 …` прямо в тексті тем, тому histories: [] всюди.
   ────────────────────────────────────────────────────────────────────────── */
window.BOOK = {
  title: "Хімія",
  subtitle: "Коротка книжка, щоб зрозуміти, про що вся шкільна хімія — " +
            "від атома до молекул життя. База 7–11 класів: просто, але до глибини.",
  shortTitle: "Хімія",

  // посилання «← Бібліотека» у сайдбарі (стартова сторінка зі списком книг)
  libraryHref: "index.html",

  // Контент лежить у chemistry/ поруч з embedded/; обгортка — у корені репо.
  basePath: "chemistry/",

  modules: [
    {
      n: 1, title: "З чого все зроблено", slug: "m1-atoms",
      chapters: [
        { n: "1", status: "done", title: "Хімія і речовини",
          dir: "m1-atoms/r1-substances", main: "r1-substances.md", histories: [] },
        { n: "2", status: "done", title: "Атом",
          dir: "m1-atoms/r2-atom", main: "r2-atom.md", histories: [] },
        { n: "3", status: "done", title: "Періодична таблиця",
          dir: "m1-atoms/r3-table", main: "r3-table.md", histories: [] }
      ]
    },
    {
      n: 2, title: "Як атоми тримаються разом", slug: "m2-bonds",
      chapters: [
        { n: "1", status: "done", title: "Хімічний зв'язок",
          dir: "m2-bonds/r1-bonding", main: "r1-bonding.md", histories: [] },
        { n: "2", status: "done", title: "Формули, валентність і моль",
          dir: "m2-bonds/r2-formulas", main: "r2-formulas.md", histories: [] },
        { n: "3", status: "done", title: "Як влаштовані тверді речовини",
          dir: "m2-bonds/r3-structure", main: "r3-structure.md", histories: [] }
      ]
    },
    {
      n: 3, title: "Реакції", slug: "m3-reactions",
      chapters: [
        { n: "1", status: "done", title: "Що таке реакція насправді",
          dir: "m3-reactions/r1-essence", main: "r1-essence.md", histories: [] },
        { n: "2", status: "done", title: "Енергія: чому горить і гріє",
          dir: "m3-reactions/r2-energy", main: "r2-energy.md", histories: [] },
        { n: "3", status: "done", title: "Швидкість і рівновага",
          dir: "m3-reactions/r3-rate-equilibrium", main: "r3-rate-equilibrium.md", histories: [] }
      ]
    },
    {
      n: 4, title: "Розчини, кислоти, солі й метали", slug: "m4-inorganic",
      chapters: [
        { n: "1", status: "done", title: "Вода і розчини",
          dir: "m4-inorganic/r1-solutions", main: "r1-solutions.md", histories: [] },
        { n: "2", status: "done", title: "Кислоти й основи",
          dir: "m4-inorganic/r2-acids-bases", main: "r2-acids-bases.md", histories: [] },
        { n: "3", status: "done", title: "Оксиди, солі та карта неорганіки",
          dir: "m4-inorganic/r3-salt-families", main: "r3-salt-families.md", histories: [] },
        { n: "4", status: "done", title: "Метали й елементи навколо нас",
          dir: "m4-inorganic/r4-metals-elements", main: "r4-metals-elements.md", histories: [] }
      ]
    },
    {
      n: 5, title: "Органіка: хімія життя", slug: "m5-organic",
      chapters: [
        { n: "1", status: "done", title: "Карбон і його ланцюги",
          dir: "m5-organic/r1-carbon", main: "r1-carbon.md", histories: [] },
        { n: "2", status: "done", title: "Кисень приєднується: спирти, кислоти, жири",
          dir: "m5-organic/r2-oxygen-compounds", main: "r2-oxygen-compounds.md", histories: [] },
        { n: "3", status: "done", title: "Молекули життя",
          dir: "m5-organic/r3-life-molecules", main: "r3-life-molecules.md", histories: [] }
      ]
    },
    {
      n: 6, title: "Формули й розрахунки задач", slug: "m6-counting",
      chapters: [
        { n: "1", status: "done", title: "Кількість речовини: моль",
          dir: "m6-counting/r1-why-numbers", main: "r1-why-numbers.md", histories: [] },
        { n: "2", status: "done", title: "Масова частка",
          dir: "m6-counting/r2-proportion", main: "r2-proportion.md", histories: [] },
        { n: "3", status: "done", title: "Розрахунки за рівнянням",
          dir: "m6-counting/r3-by-equation", main: "r3-by-equation.md", histories: [] },
        { n: "4", status: "done", title: "Складніші задачі: гази, надлишок, вихід",
          dir: "m6-counting/r4-twists", main: "r4-twists.md", histories: [] }
      ]
    }
  ]
};
