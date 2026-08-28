test("бонусів нема неактивному", () => {
  const off: Account = { customer: "X", active: false,
    lines: [{ meter: "M", tariff: "night", kWh: 900 }] };
  expect(statement(off)).toContain("Бонусні кіловати: 0");
});
test("бонусів нема бізнесу", () => {
  const biz: Account = { customer: "ТОВ", active: true,
    lines: [{ meter: "Піч", tariff: "business", kWh: 900 }] };
  expect(statement(biz)).toContain("Бонусні кіловати: 0");
});
// обидва — зелено (закріпили поведінку ДО перебудови умови)
