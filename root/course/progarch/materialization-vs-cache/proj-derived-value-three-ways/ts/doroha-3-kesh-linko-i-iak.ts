// Однополітність у процесі: збіг промахів за ключем склеюється в ОДИН скан.
const inFlight = new Map<string, Promise<number>>();

async function monthlyKwh(home: string, month: string): Promise<number> {
  const key = `kwh:${home}:${month}`;

  const hit = await cache.get(key);
  if (hit !== null) return Number(hit);               // влучання — дешево, з пам'яті

  const running = inFlight.get(key);
  if (running) return running;                        // уже рахують — приєднайся

  const compute = (async () => {
    try {
      const kwh = await computeFromSource(home, month); // ЄДИНИЙ важкий скан
      const ttl = 300 + Math.floor(Math.random() * 60); // TTL із розкидом (jitter)
      await cache.set(key, kwh, { ttlSeconds: ttl });
      return kwh;
    } finally {
      inFlight.delete(key);                           // звільни ключ у будь-якому разі
    }
  })();

  inFlight.set(key, compute);                         // зареєструй ДО await
  return compute;
}
