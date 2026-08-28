const policy = { threshold: 25, windowMs: 5 * 60_000 };    // 5 хв
const now = 1_000_000;

// стійка спека у вікні → вмикаємо (жодної підробки не треба)
assert.equal(decideCooling(
  [{ at: now - 60_000, celsius: 26 }, { at: now - 10_000, celsius: 27 }], now, policy), "on");

// один давній сплеск ПОЗА вікном → ігноруємо
assert.equal(decideCooling(
  [{ at: now - 10 * 60_000, celsius: 40 }], now, policy), "off");
