/* guide/basic-chemistry/manifest.js — КУРС «Хімія» (тип "guide").
   Доріжка-надбудова: впорядковані ref-и на теми book/chemistry (власних статей курс не має).
   Схема v5 (AUTHORING §2): modules[] → chapters[] → steps[]; нумерація Модуль·Розділ·Крок — з порядку масивів. */
(window.__GUIDES__ = window.__GUIDES__ || []).push({
  type: "guide", slug: "basic-chemistry", title: "Хімія",
  modules: [
    { n: 1, slug: "m1-atoms", title: "З чого все зроблено", scope: "", chapters: [
      { title: "Хімія і речовини", steps: [
        { ref: "chemistry/physical-chemistry/substances", title: "Речовини" },
        { ref: "chemistry/analytical-chemistry/mixtures", title: "Суміші" },
      ] },
      { title: "Атом", steps: [
        { ref: "chemistry/theoretical-chemistry/atoms-molecules", title: "Атоми й молекули" },
        { ref: "chemistry/theoretical-chemistry/inside-atom", title: "Будова атома" },
        { ref: "chemistry/inorganic-chemistry/element", title: "Елемент" },
      ] },
      { title: "Періодична таблиця", steps: [
        { ref: "chemistry/inorganic-chemistry/periodic-table", title: "Періодична таблиця" },
        { ref: "chemistry/inorganic-chemistry/element-families", title: "Родини елементів" },
      ] },
    ] },
    { n: 2, slug: "m2-bonds", title: "Як атоми тримаються разом", scope: "", chapters: [
      { title: "Хімічний зв'язок", steps: [
        { ref: "chemistry/theoretical-chemistry/why-bond", title: "Хімічний зв'язок" },
        { ref: "chemistry/theoretical-chemistry/ionic-covalent", title: "Іонний і ковалентний" },
        { ref: "chemistry/theoretical-chemistry/metallic-bond", title: "Металічний зв'язок" },
      ] },
      { title: "Формули, валентність і моль", steps: [
        { ref: "chemistry/inorganic-chemistry/formulas", title: "Формули" },
        { ref: "chemistry/inorganic-chemistry/valence", title: "Валентність" },
        { ref: "chemistry/physical-chemistry/mole", title: "Моль" },
      ] },
      { title: "Як влаштовані тверді речовини", steps: [
        { ref: "chemistry/solid-state-chemistry/molecules-lattice", title: "Молекули чи ґратка" },
        { ref: "chemistry/solid-state-chemistry/structure-properties", title: "Структура і властивості" },
      ] },
    ] },
    { n: 3, slug: "m3-reactions", title: "Реакції", scope: "", chapters: [
      { title: "Що таке реакція насправді", steps: [
        { ref: "chemistry/physical-chemistry/reaction", title: "Реакція" },
        { ref: "chemistry/physical-chemistry/equations", title: "Рівняння" },
        { ref: "chemistry/physical-chemistry/reaction-types", title: "Типи реакцій" },
      ] },
      { title: "Енергія: чому горить і гріє", steps: [
        { ref: "chemistry/physical-chemistry/reaction-energy", title: "Енергія реакцій" },
        { ref: "chemistry/physical-chemistry/combustion", title: "Горіння" },
      ] },
      { title: "Швидкість і рівновага", steps: [
        { ref: "chemistry/physical-chemistry/reaction-rate", title: "Швидкість реакції" },
        { ref: "chemistry/physical-chemistry/catalysts", title: "Каталізатори" },
        { ref: "chemistry/physical-chemistry/equilibrium", title: "Рівновага" },
      ] },
    ] },
    { n: 4, slug: "m4-inorganic", title: "Розчини, кислоти, солі й метали", scope: "", chapters: [
      { title: "Вода і розчини", steps: [
        { ref: "chemistry/physical-chemistry/dissolution", title: "Розчинення" },
        { ref: "chemistry/physical-chemistry/solubility", title: "Розчинність" },
        { ref: "chemistry/physical-chemistry/ions-solution", title: "Іони в розчині" },
      ] },
      { title: "Кислоти й основи", steps: [
        { ref: "chemistry/inorganic-chemistry/acids", title: "Кислоти" },
        { ref: "chemistry/inorganic-chemistry/bases", title: "Основи" },
        { ref: "chemistry/analytical-chemistry/ph-indicators", title: "pH та індикатори" },
      ] },
      { title: "Оксиди, солі та карта неорганіки", steps: [
        { ref: "chemistry/inorganic-chemistry/oxides", title: "Оксиди" },
        { ref: "chemistry/inorganic-chemistry/salts", title: "Солі" },
        { ref: "chemistry/inorganic-chemistry/inorganic-map", title: "Карта неорганіки" },
      ] },
      { title: "Метали й елементи навколо нас", steps: [
        { ref: "chemistry/inorganic-chemistry/activity-corrosion", title: "Активність і іржа" },
        { ref: "chemistry/inorganic-chemistry/elements-tour", title: "Елементи навколо" },
      ] },
    ] },
    { n: 5, slug: "m5-organic", title: "Органіка: хімія життя", scope: "", chapters: [
      { title: "Карбон і його ланцюги", steps: [
        { ref: "chemistry/organic-chemistry/carbon", title: "Карбон" },
        { ref: "chemistry/organic-chemistry/hydrocarbons", title: "Вуглеводні" },
        { ref: "chemistry/polymer-chemistry/polymers", title: "Полімери" },
      ] },
      { title: "Кисень приєднується: спирти, кислоти, жири", steps: [
        { ref: "chemistry/organic-chemistry/alcohols-acids", title: "Спирти і кислоти" },
        { ref: "chemistry/organic-chemistry/esters-fats", title: "Естери і жири" },
      ] },
      { title: "Молекули життя", steps: [
        { ref: "chemistry/biochemistry/carbohydrates", title: "Вуглеводи" },
        { ref: "chemistry/biochemistry/fats-proteins", title: "Жири і білки" },
        { ref: "chemistry/biochemistry/kitchen-chemistry", title: "Кухонна хімія" },
        { ref: "chemistry/biochemistry/epilogue", title: "Куди далі" },
      ] },
    ] },
    { n: 6, slug: "m6-counting", title: "Формули й розрахунки задач", scope: "", chapters: [
      { title: "Кількість речовини: моль", steps: [
        { ref: "chemistry/physical-chemistry/fixed-ratios", title: "Сталі відношення" },
        { ref: "chemistry/physical-chemistry/mole-formulas", title: "Формули моля" },
      ] },
      { title: "Масова частка", steps: [
        { ref: "chemistry/analytical-chemistry/mass-fraction", title: "Масова частка" },
        { ref: "chemistry/analytical-chemistry/element-fraction", title: "Частка елемента" },
      ] },
      { title: "Розрахунки за рівнянням", steps: [
        { ref: "chemistry/physical-chemistry/mole-proportion", title: "Пропорція в молях" },
        { ref: "chemistry/physical-chemistry/stoichiometry", title: "Стехіометрія" },
      ] },
      { title: "Складніші задачі: гази, надлишок, вихід", steps: [
        { ref: "chemistry/physical-chemistry/gas-volume", title: "Об'єм газу" },
        { ref: "chemistry/physical-chemistry/excess-limiting", title: "Надлишок і нестача" },
        { ref: "chemistry/physical-chemistry/product-yield", title: "Вихід продукту" },
      ] },
    ] },
  ]
});
