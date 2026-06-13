/* chemistry/m6-counting/manifest.js — per-module маніфест Модуля 6. Складає scripts/bookbuild.js.
   Хімія: вставок нема (histories[]/extras[] порожні), є лише теми. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: 6, slug: "m6-counting", title: "Формули й розрахунки задач",
  chapters: [
    { n: "1", title: "Кількість речовини: моль", dir: "m6-counting/r1-why-numbers", main: "r1-why-numbers.md", status: "done",
      scope: "Сталі відношення у складі речовин — звідки взагалі можна рахувати; моль як одиниця кількості речовини; формули n = m/M і N = n·Nₐ.",
      topics: [
        { mrt: "6.1.1", title: "Сталі відношення — звідси всі числа", status: "done" },
        { mrt: "6.1.2", title: "Головні формули кількості речовини: n = m/M і N = n·Nₐ", status: "done" }
      ] },
    { n: "2", title: "Масова частка", dir: "m6-counting/r2-proportion", main: "r2-proportion.md", status: "done",
      scope: "Масова частка речовини в суміші/розчині та масова частка елемента у формулі сполуки.",
      topics: [
        { mrt: "6.2.1", title: "Масова частка речовини: ω = m(речовини)/m(суміші)·100%", status: "done" },
        { mrt: "6.2.2", title: "Масова частка елемента у формулі: ω(Е) = n·Aᵣ/Mᵣ·100%", status: "done" }
      ] },
    { n: "3", title: "Розрахунки за рівнянням", dir: "m6-counting/r3-by-equation", main: "r3-by-equation.md", status: "done",
      scope: "Коефіцієнти рівняння як молярні відношення; повний метод розрахунку маси продукту за масою реагенту.",
      topics: [
        { mrt: "6.3.1", title: "Рівняння — пропорція в молях", status: "done" },
        { mrt: "6.3.2", title: "Розрахунок за рівнянням: грами → молі → молі → грами", status: "done" }
      ] },
    { n: "4", title: "Складніші задачі: гази, надлишок, вихід", dir: "m6-counting/r4-twists", main: "r4-twists.md", status: "done",
      scope: "Молярний об'єм газу; знаходження обмежувального реагенту; вихід продукту реакції; фінал книги.",
      topics: [
        { mrt: "6.4.1", title: "Об'єм газу: V = n·Vₘ (Vₘ = 22,4 л/моль)", status: "done" },
        { mrt: "6.4.2", title: "Надлишок і нестача: за чим рахувати", status: "done" },
        { mrt: "6.4.3", title: "Вихід продукту: η = m(практ)/m(теор)·100% (+ ФІНАЛ КНИГИ; без ▶️)", status: "done" }
      ] }
  ]
});
