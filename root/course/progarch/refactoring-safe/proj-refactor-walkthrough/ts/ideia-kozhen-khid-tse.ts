const koval: Account = {
  customer: "Родина Коваль",
  active: true,
  lines: [
    { meter: "Кухня",  tariff: "day",   kWh: 150 },
    { meter: "Бойлер", tariff: "night", kWh: 320 },
    { meter: "Гараж",  tariff: "day",   kWh: 80  },
  ],
};

const EXPECTED = [
  "Рахунок — Родина Коваль",
  "  Кухня: 150 кВт·год — 390.00 грн",
  "  Бойлер: 320 кВт·год — 384.00 грн",
  "  Гараж: 80 кВт·год — 200.00 грн",
  "Разом: 974.00 грн",
  "Бонусні кіловати: 120",
  "",
].join("\n");

test("statement — золотий зразок", () => {
  expect(statement(koval)).toBe(EXPECTED);
});
