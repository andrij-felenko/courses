test("вартовий гасить сліпе гріння після 3 застиглих", () => {   // БАЖАНЕ, не вада
  const heater = new SpyHeater();
  const stuck = new FreshnessGuard(
    new FakeSensor(...Array(5).fill({ celsius: 19.9, ok: true })), 3);
  for (let i = 0; i < 5; i++) tick(stuck, heater, { threshold: 20.0 });
  expect(heater.calls).toEqual(["on", "on", "on", "off", "off"]);   // гріє, поки вірить
});

test("вартовий перемикається саме на 4-му однаковому вимірі", () => {   // регресія
  const guard = new FreshnessGuard(
    new FakeSensor(...Array(4).fill({ celsius: 19.9, ok: true })), 3);
  const oks = [0, 1, 2, 3].map(() => guard.read().ok);
  expect(oks).toEqual([true, true, true, false]);
});
