/* book/chemistry/manifest.js — книга-предмет «Хімія» (тип "book").
   Схема — AUTHORING.md §2: { type, slug, title, sections:[ {slug,title,scope, topics:[ {slug,title,status,levels,origin, hist/comp/math/proj:[{file,status}]} ]} ] }
   Статуси: done | empty | update | deeper | recheck. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "book", slug: "chemistry", title: "Хімія",
  sections: [
    { slug: "inorganic-chemistry", title: "Неорганічна хімія", scope: "Будова, властивості й реакції елементів та сполук без вуглець-водневого скелета — від солей до координаційних комплексів.",
      topics: [
        { slug: "element", title: "Елемент", status: "recheck", levels: ["basic"], origin: "chemistry/m1-atoms/r2-atom#1.2.3" },
        { slug: "periodic-table", title: "Періодична таблиця", status: "recheck", levels: ["basic"], origin: "chemistry/m1-atoms/r3-table#1.3.1", hist: [{ file: "periodic-table-h-mendeleev.md", status: "recheck" }] },
        { slug: "element-families", title: "Родини елементів", status: "recheck", levels: ["basic"], origin: "chemistry/m1-atoms/r3-table#1.3.2" },
        { slug: "formulas", title: "Формули", status: "recheck", levels: ["basic"], origin: "chemistry/m2-bonds/r2-formulas#2.2.1" },
        { slug: "valence", title: "Валентність", status: "recheck", levels: ["basic"], origin: "chemistry/m2-bonds/r2-formulas#2.2.2" },
        { slug: "acids", title: "Кислоти", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r2-acids-bases#4.2.1" },
        { slug: "bases", title: "Основи", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r2-acids-bases#4.2.2" },
        { slug: "oxides", title: "Оксиди", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r3-salt-families#4.3.1" },
        { slug: "salts", title: "Солі", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r3-salt-families#4.3.2" },
        { slug: "inorganic-map", title: "Карта неорганіки", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r3-salt-families#4.3.3" },
        { slug: "activity-corrosion", title: "Активність і іржа", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r4-metals-elements#4.4.1" },
        { slug: "elements-tour", title: "Елементи навколо", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r4-metals-elements#4.4.2" },
      ] },
    { slug: "organic-chemistry", title: "Органічна хімія", scope: "Хімія сполук вуглецю: класи, функційні групи, механізми та методи синтезу молекул.",
      topics: [
        { slug: "carbon", title: "Карбон", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r1-carbon#5.1.1" },
        { slug: "hydrocarbons", title: "Вуглеводні", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r1-carbon#5.1.2" },
        { slug: "alcohols-acids", title: "Спирти і кислоти", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r2-oxygen-compounds#5.2.1" },
        { slug: "esters-fats", title: "Естери і жири", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r2-oxygen-compounds#5.2.2" },
      ] },
    { slug: "physical-chemistry", title: "Фізична хімія", scope: "Фізичні закони, що керують речовиною й перетвореннями: термодинаміка, кінетика, рівновага та електрохімія.",
      topics: [
        { slug: "substances", title: "Речовини", status: "recheck", levels: ["basic"], origin: "chemistry/m1-atoms/r1-substances#1.1.1" },
        { slug: "mole", title: "Моль", status: "recheck", levels: ["basic"], origin: "chemistry/m2-bonds/r2-formulas#2.2.3" },
        { slug: "reaction", title: "Реакція", status: "recheck", levels: ["basic"], origin: "chemistry/m3-reactions/r1-essence#3.1.1" },
        { slug: "equations", title: "Рівняння", status: "recheck", levels: ["basic"], origin: "chemistry/m3-reactions/r1-essence#3.1.2" },
        { slug: "reaction-types", title: "Типи реакцій", status: "recheck", levels: ["basic"], origin: "chemistry/m3-reactions/r1-essence#3.1.3" },
        { slug: "reaction-energy", title: "Енергія реакцій", status: "recheck", levels: ["basic"], origin: "chemistry/m3-reactions/r2-energy#3.2.1" },
        { slug: "combustion", title: "Горіння", status: "recheck", levels: ["basic"], origin: "chemistry/m3-reactions/r2-energy#3.2.2" },
        { slug: "reaction-rate", title: "Швидкість реакції", status: "recheck", levels: ["basic"], origin: "chemistry/m3-reactions/r3-rate-equilibrium#3.3.1" },
        { slug: "catalysts", title: "Каталізатори", status: "recheck", levels: ["basic"], origin: "chemistry/m3-reactions/r3-rate-equilibrium#3.3.2" },
        { slug: "equilibrium", title: "Рівновага", status: "recheck", levels: ["basic"], origin: "chemistry/m3-reactions/r3-rate-equilibrium#3.3.3" },
        { slug: "dissolution", title: "Розчинення", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r1-solutions#4.1.1" },
        { slug: "solubility", title: "Розчинність", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r1-solutions#4.1.2" },
        { slug: "ions-solution", title: "Іони в розчині", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r1-solutions#4.1.3" },
        { slug: "fixed-ratios", title: "Сталі відношення", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r1-why-numbers#6.1.1" },
        { slug: "mole-formulas", title: "Формули моля", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r1-why-numbers#6.1.2" },
        { slug: "mole-proportion", title: "Пропорція в молях", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r3-by-equation#6.3.1" },
        { slug: "stoichiometry", title: "Стехіометрія", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r3-by-equation#6.3.2" },
        { slug: "gas-volume", title: "Об'єм газу", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r4-twists#6.4.1" },
        { slug: "excess-limiting", title: "Надлишок і нестача", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r4-twists#6.4.2" },
        { slug: "product-yield", title: "Вихід продукту", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r4-twists#6.4.3" },
      ] },
    { slug: "theoretical-chemistry", title: "Теоретична хімія", scope: "Квантовий і обчислювальний опис атомів і молекул: рівняння, моделі та симуляції структури й реакційності.",
      topics: [
        { slug: "atoms-molecules", title: "Атоми й молекули", status: "recheck", levels: ["basic"], origin: "chemistry/m1-atoms/r2-atom#1.2.1" },
        { slug: "inside-atom", title: "Будова атома", status: "recheck", levels: ["basic"], origin: "chemistry/m1-atoms/r2-atom#1.2.2" },
        { slug: "why-bond", title: "Хімічний зв'язок", status: "recheck", levels: ["basic"], origin: "chemistry/m2-bonds/r1-bonding#2.1.1" },
        { slug: "ionic-covalent", title: "Іонний і ковалентний", status: "recheck", levels: ["basic"], origin: "chemistry/m2-bonds/r1-bonding#2.1.2" },
        { slug: "metallic-bond", title: "Металічний зв'язок", status: "recheck", levels: ["basic"], origin: "chemistry/m2-bonds/r1-bonding#2.1.3" },
      ] },
    { slug: "analytical-chemistry", title: "Аналітична хімія", scope: "Методи виявлення, ідентифікації та вимірювання кількості речовин у зразках.",
      topics: [
        { slug: "mixtures", title: "Суміші", status: "recheck", levels: ["basic"], origin: "chemistry/m1-atoms/r1-substances#1.1.2" },
        { slug: "ph-indicators", title: "pH та індикатори", status: "recheck", levels: ["basic"], origin: "chemistry/m4-inorganic/r2-acids-bases#4.2.3" },
        { slug: "mass-fraction", title: "Масова частка", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r2-proportion#6.2.1" },
        { slug: "element-fraction", title: "Частка елемента", status: "recheck", levels: ["basic"], origin: "chemistry/m6-counting/r2-proportion#6.2.2" },
      ] },
    { slug: "biochemistry", title: "Біохімія", scope: "Хімічні процеси й молекули живих систем: метаболізм, ферменти та біополімери.",
      topics: [
        { slug: "carbohydrates", title: "Вуглеводи", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r3-life-molecules#5.3.1" },
        { slug: "fats-proteins", title: "Жири і білки", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r3-life-molecules#5.3.2" },
        { slug: "kitchen-chemistry", title: "Кухонна хімія", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r3-life-molecules#5.3.3" },
        { slug: "epilogue", title: "Куди далі", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r3-life-molecules#5.3.4" },
      ] },
    { slug: "polymer-chemistry", title: "Полімери", scope: "Синтез, структура та властивості макромолекул і пластиків, побудованих із повторюваних ланок.",
      topics: [
        { slug: "polymers", title: "Полімери", status: "recheck", levels: ["basic"], origin: "chemistry/m5-organic/r1-carbon#5.1.3" },
      ] },
    { slug: "solid-state-chemistry", title: "Твердотільна хімія", scope: "Хімія протяжних твердих тіл: структура кристалів, дефекти та функційні неорганічні матеріали.",
      topics: [
        { slug: "molecules-lattice", title: "Молекули чи ґратка", status: "recheck", levels: ["basic"], origin: "chemistry/m2-bonds/r3-structure#2.3.1" },
        { slug: "structure-properties", title: "Структура і властивості", status: "recheck", levels: ["basic"], origin: "chemistry/m2-bonds/r3-structure#2.3.2" },
      ] },
    { slug: "supramolecular-chemistry", title: "Супрамолекулярна хімія", scope: "Нековалентні взаємодії та самозбірка, що утримують молекули разом у більші ансамблі.",
      topics: [
      ] },
    { slug: "radiochemistry", title: "Радіохімія", scope: "Хімія радіоактивних елементів, ядерних перетворень та поведінки ізотопів.",
      topics: [
      ] },
    { slug: "geochemistry", title: "Геохімія", scope: "Розподіл і кругообіг хімічних елементів у Землі, її водах, атмосфері та породах.",
      topics: [
      ] },
  ]
});
