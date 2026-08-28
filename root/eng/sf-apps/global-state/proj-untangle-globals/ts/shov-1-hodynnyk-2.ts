const build = (clock: Clock) => new Billing(clock);   // поки що залежність рівно одна
const utc = (y: number, m: number, d: number, h = 0, mi = 0, s = 0) =>
  new Date(Date.UTC(y, m - 1, d, h, mi, s));

test("запізнілий платіж не посуває день списання", () => {
  const svc = build(new FixedClock(utc(2026, 3, 3, 9)));      // платіж на 2-й день пільги
  const sub: Subscription = { id: "s-1", planPrice: 100, paidUntil: utc(2026, 3, 1) };
  expect(svc.renew(sub).status).toBe("ok");
  expect(sub.paidUntil).toEqual(utc(2026, 3, 31));            // + рівно 30д від СТРОКУ
});

test("на секунду пізніше межі", () => {
  const svc = build(new FixedClock(utc(2026, 3, 4, 0, 0, 1)));
  const sub: Subscription = { id: "s-1", planPrice: 100, paidUntil: utc(2026, 3, 1) };
  expect(svc.renew(sub).status).toBe("expired");
  expect(sub.paidUntil).toEqual(utc(2026, 3, 1));             // згасла — строк не рухаємо
});

test("дванадцять продовжень без дрейфу", () => {
  const sub: Subscription = { id: "s-1", planPrice: 100, paidUntil: utc(2026, 1, 1) };
  for (let i = 0; i < 12; i++) {
    build(new FixedClock(addDays(sub.paidUntil, 2))).renew(sub);           // щоразу +2д
  }
  expect(sub.paidUntil).toEqual(addDays(utc(2026, 1, 1), 360));            // дрейф 0
});
