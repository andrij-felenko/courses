test("read + залежність down + свіжий кеш → щабель cache, не падає й не бреше простроченим", async () => {
  const device = new FakeDevice();
  const policy: Policy<Reading> = { ...readPolicy, cache: new MapCache<Reading>() };

  await withFallback("dev-1", policy, () => device.read("dev-1")); // прогрів: жива → у кеш
  device.down = true;                                              // ← вимикаємо залежність

  const served = await withFallback("dev-1", policy, () => device.read("dev-1"));

  expect(served.rung).toBe("cache");           // встояли на ОЧІКУВАНОМУ щаблі
  expect(served.stale).toBe(true);             // і чесно позначили: це не свіже
  expect(served.value.temperature).toBe(21.5);
});

test("read + залежність down + ПРОСТРОЧЕНИЙ кеш → чесна відмова, а не стара брехня", async () => {
  const device = new FakeDevice();
  const cache = new MapCache<Reading>();
  cache.seed("dev-1", { temperature: 21.5, stale: false }, Date.now() - 5 * 60_000); // кешу 5 хв
  const policy: Policy<Reading> = { ...readPolicy, cache, staleBudgetMs: 60_000 };    // бюджет 1 хв
  device.down = true;

  // КЛЮЧОВЕ: система НЕ віддає прострочене значення — вона чесно падає вузько.
  await expect(withFallback("dev-1", policy, () => device.read("dev-1")))
    .rejects.toBeInstanceOf(Unavailable);
});

test("gate unlock + залежність down + fail-closed → deny, НЕ fail-open, кеш не чіпає", async () => {
  const authzDown = () => Promise.reject(new TimeoutError("authz")); // авторизація мовчить
  const served = await withFallback("u1:dev-1", unlockGatePolicy, authzDown);

  expect(served.rung).toBe("default");         // впав на дефолт-щабель…
  expect(served.value.allowed).toBe(false);    // …а дефолт — ЗАБОРОНА (fail-closed)
});
