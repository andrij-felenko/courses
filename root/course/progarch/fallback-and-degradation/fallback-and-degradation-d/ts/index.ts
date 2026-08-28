// Один щабель драбини: жива відповідь → інакше кеш у межах бюджету застарілості.
async function readState(id: string): Promise<Reading> {
  try {
    const fresh = await device.read(id);      // запобіжник/таймаут — усередині
    cache.put(id, fresh, now());               // тримаємо копію теплою
    return fresh;
  } catch {
    const c = cache.get(id);
    if (c && now() - c.at <= STALE_BUDGET_MS) {
      metrics.inc("fallback.cache", { id });   // деградуємо ГОЛОСНО (нижче)
      return { ...c.value, stale: true };
    }
    throw new Unavailable(id);                  // кеш надто старий — чесна відмова
  }
}
