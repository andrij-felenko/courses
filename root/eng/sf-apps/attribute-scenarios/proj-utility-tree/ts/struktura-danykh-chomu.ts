// Трибальна шкала: Н=1, С=2, В=3 (низько / середньо / високо).
type Rank = 1 | 2 | 3;

interface Scenario {
  title: string;
  importance: Rank;   // цінність для успіху системи
  difficulty: Rank;   // архітектурна складність досягти
}

interface Attribute {
  name: string;            // якісний атрибут — гілка дерева
  scenarios: Scenario[];   // листя цієї гілки
}

interface UtilityTree {
  root: string;            // «Корисність системи»
  attributes: Attribute[];
}

const tree: UtilityTree = {
  root: "Корисність системи",
  attributes: [
    { name: "Продуктивність", scenarios: [
      { title: "Профіль за 200 мс у пік, p95",   importance: 3, difficulty: 3 },
      { title: "Річний звіт рахується за < 5 с",  importance: 2, difficulty: 1 },
      { title: "Пошук у піку віддає за < 300 мс", importance: 3, difficulty: 2 },
    ]},
    { name: "Доступність", scenarios: [
      { title: "Переживає втрату вузла БД, перерва ≤ 30 с", importance: 3, difficulty: 3 },
      { title: "Переживає втрату дата-центру без втрати даних", importance: 3, difficulty: 3 },
      { title: "Подія в журналі не губиться", importance: 2, difficulty: 2 },
    ]},
    { name: "Змінюваність", scenarios: [
      { title: "Нова валюта за ≤ 2 дні, без правки ядра платежів", importance: 3, difficulty: 2 },
      { title: "Новий канал сповіщень за ≤ тиждень", importance: 1, difficulty: 2 },
    ]},
  ],
};
