// ── Щасливий шлях: законні переходи ведуть куди слід ──
test("чернетку можна активувати, тоді ввести в пільговий період", () => {
  const p = new Policy("P-1", new Date(), Money.of(120_00, "UAH"));
  p.activate();
  expect(p.status).toBe(PolicyStatus.Active);
  p.enterGracePeriod();
  expect(p.status).toBe(PolicyStatus.Grace);
});

test("платіж у межах премії приймається й додається до суми", () => {
  const p = new Policy("P-2", new Date(), Money.of(100_00, "UAH"));
  p.activate();
  p.addPayment(Money.of(40_00, "UAH"), new Date());
  expect(p.paidTotal().cents).toBe(40_00);
});

// ── Охорона інваріантів: заборонене кидає, стан НЕ псується ──
test("не можна ввести в пільговий період чернетку", () => {
  const p = new Policy("P-3", new Date(), Money.of(100_00, "UAH"));
  expect(() => p.enterGracePeriod()).toThrow(DomainError);
  expect(p.status).toBe(PolicyStatus.Draft);      // стан лишився недоторканим
});

test("платіж понад премію відхиляється, сума не міняється", () => {
  const p = new Policy("P-4", new Date(), Money.of(100_00, "UAH"));
  p.activate();
  p.addPayment(Money.of(80_00, "UAH"), new Date());
  expect(() => p.addPayment(Money.of(30_00, "UAH"), new Date())).toThrow(DomainError);
  expect(p.paidTotal().cents).toBe(80_00);        // невдалий платіж не додався
});

test("платіж у чужій валюті відхиляє сам Money", () => {
  const p = new Policy("P-5", new Date(), Money.of(100_00, "UAH"));
  p.activate();
  expect(() => p.addPayment(Money.of(10_00, "USD"), new Date())).toThrow(DomainError);
});
