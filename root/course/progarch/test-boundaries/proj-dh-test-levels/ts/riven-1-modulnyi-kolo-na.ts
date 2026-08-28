test('модульний: нижче порога → грій вмикається', () => {
  const heater = new SpyHeater();
  decide(new FakeSensor(18), heater, 20);   // «давач дає 18 °C» — це НАШЕ припущення
  expect(heater.isOn).toBe(true);
});

test('модульний: рівно на порозі → грій не вмикається', () => {
  const heater = new SpyHeater();
  decide(new FakeSensor(20), heater, 20);   // 20 < 20 — хибно
  expect(heater.isOn).toBe(false);          // ловить «<=» замість «<»
});
