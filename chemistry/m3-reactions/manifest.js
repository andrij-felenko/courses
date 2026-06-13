/* chemistry/m3-reactions/manifest.js — per-module маніфест Модуля 3. Складає scripts/bookbuild.js.
   Хімія: вставок нема (histories[]/extras[] порожні), є лише теми. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: 3, slug: "m3-reactions", title: "Реакції",
  chapters: [
    { n: "1", title: "Що таке реакція насправді", dir: "m3-reactions/r1-essence", main: "r1-essence.md", status: "done",
      scope: "Атоми лише перегруповуються; рівняння як рецепт; чотири типи реакцій і ідея окиснення-відновлення.",
      topics: [
        { mrt: "3.1.1", title: "Реакція = перегрупування", status: "done" },
        { mrt: "3.1.2", title: "Рівняння — це рецепт", status: "done" },
        { mrt: "3.1.3", title: "Чотири типи реакцій — і хто краде електрони", status: "done" }
      ] },
    { n: "2", title: "Енергія: чому горить і гріє", dir: "m3-reactions/r2-energy", main: "r2-energy.md", status: "done",
      scope: "Енергія хімічних зв'язків, бар'єр активації, трикутник вогню і безпека на кухні.",
      topics: [
        { mrt: "3.2.1", title: "Чому горить і чому треба чиркнути", status: "done" },
        { mrt: "3.2.2", title: "Горіння і як його зупинити", status: "done" }
      ] },
    { n: "3", title: "Швидкість і рівновага", dir: "m3-reactions/r3-rate-equilibrium", main: "r3-rate-equilibrium.md", status: "done",
      scope: "Зіткнення частинок, каталізатори, оборотні реакції і динамічна рівновага.",
      topics: [
        { mrt: "3.3.1", title: "Що прискорює реакцію", status: "done" },
        { mrt: "3.3.2", title: "Каталізатори", status: "done" },
        { mrt: "3.3.3", title: "Реакції туди й назад", status: "done" }
      ] }
  ]
});
