class Unavailable extends Error {
  constructor(op: string, key: string) {
    super(`${op}(${key}): залежність недоступна, чесного щабля не лишилось`);
  }
}

// Обгортка віддає НАЙВИЩИЙ щабель, що policy тримає чесно.
async function withFallback<T>(
  key: string,
  policy: Policy<T>,
  primary: () => Promise<T>,
): Promise<Served<T>> {
  try {
    // ① Живий щабель. Таймаут і запобіжник — усередині primary().
    const value = await primary();
    policy.cache?.put(key, value);           // тримаємо копію теплою (якщо кеш увімкнено)
    recordRung(policy.op, "live");           // метрика на КОЖНОМУ виході, навіть успішному
    return { value, rung: "live", stale: false };
  } catch (err) {
    // КЛЮЧОВЕ: fallback — лише на «залежність мовчить». Баг/валідація летять далі.
    if (!isDependencyDown(err)) throw err;

    // ② Кеш у межах бюджету застарілості.
    const hit = policy.cache?.get(key);
    if (hit && Date.now() - hit.at <= policy.staleBudgetMs) {
      recordRung(policy.op, "cache", Date.now() - hit.at);
      return { value: hit.value, rung: "cache", stale: true };
    }

    // ③ Розумний дефолт. Для ґейта САМЕ ТУТ живе fail-open/fail-closed.
    if (policy.smartDefault) {
      recordRung(policy.op, "default");
      return { value: policy.smartDefault(), rung: "default", stale: true };
    }

    // ④ Чесна вузька відмова. Не брехня простроченим кешем — прямо «недоступно».
    recordRung(policy.op, "unavailable");
    throw new Unavailable(policy.op, key);
  }
}
