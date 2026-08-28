type Grade = "В" | "С" | "Н";   // високо · середньо · низько

// Листок: сценарій, його нещадна міра з числом і дві людські оцінки.
interface Leaf {
  kind: "leaf";
  scenario: string;
  measure: string;      // саме це згодом стане фітнес-функцією
  importance: Grade;    // наскільки успіх системи від цього залежить
  difficulty: Grade;    // наскільки важко це дати саме цій структурі
}

// Гілка: якісний атрибут, що ще розгалужується.
interface Branch {
  kind: "branch";
  attribute: string;
  children: Node[];
}

type Node = Branch | Leaf;

const tree: Branch = {
  kind: "branch",
  attribute: "Корисність Digital Homes",
  children: [
    {
      kind: "branch",
      attribute: "Доступність",
      children: [
        {
          kind: "branch",
          attribute: "без хмари",
          children: [
            {
              kind: "leaf",
              scenario: "дім живий, коли впав інтернет",
              measure:
                "0 пропущених спрацювань за 24 год офлайн; " +
                "після відновлення 0 втрачених і 0 подвоєних подій",
              importance: "В",
              difficulty: "В",
            },
            {
              kind: "leaf",
              scenario: "апка бачить дім у локальній мережі без хмари",
              measure: "апка показує стан дому за ≤ 2 с без доступу до хмари",
              importance: "В",
              difficulty: "С",
            },
          ],
        },
      ],
    },
    {
      kind: "branch",
      attribute: "Надійність",
      children: [
        {
          kind: "leaf",
          scenario: "замок відчиняється рівно раз",
          measure:
            "за будь-якого числа повторів однієї команди — " +
            "рівно 1 фізичне відмикання",
          importance: "В",
          difficulty: "В",
        },
      ],
    },
    {
      kind: "branch",
      attribute: "Змінюваність",
      children: [
        {
          kind: "leaf",
          scenario: "новий тип пристрою — без правки ядра",
          measure: "додати драйвер пристрою, не змінивши жодного файлу рушія правил",
          importance: "В",
          difficulty: "В",
        },
        {
          kind: "leaf",
          scenario: "нове правило додає сам користувач",
          measure: "нова автоматизація з'являється без випуску нової версії",
          importance: "С",
          difficulty: "С",
        },
      ],
    },
    {
      kind: "branch",
      attribute: "Швидкодія",
      children: [
        {
          kind: "leaf",
          scenario: "фізичний вимикач → світло",
          measure: "світло спалахує за ≤ 100 мс у 99% натискань",
          importance: "В",
          difficulty: "С",
        },
        {
          kind: "leaf",
          scenario: "флот 5 млн домів: телеметрія встигає",
          measure: "запис телеметрії не відстає від темпу її надходження",
          importance: "С",
          difficulty: "В",
        },
      ],
    },
    {
      kind: "branch",
      attribute: "Безпека",
      children: [
        {
          kind: "leaf",
          scenario: "відеопотік — лише власнику",
          measure: "відео доступне тільки автентифікованому власнику дому",
          importance: "В",
          difficulty: "В",
        },
      ],
    },
  ],
};
