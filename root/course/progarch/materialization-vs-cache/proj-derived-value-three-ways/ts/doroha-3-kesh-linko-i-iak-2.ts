// Крос-процесна однополітність: замок у кеші. SET NX — атомарно «взяв або ні».
async function monthlyKwhLocked(home: string, month: string, tries = 5): Promise<number> {
  const key = `kwh:${home}:${month}`;
  const hit = await cache.get(key);
  if (hit !== null) return Number(hit);

  const lock = `lock:${key}`;
  const got = await cache.set(lock, "1", { nx: true, ttlSeconds: 10 }); // атомарний замок
  if (!got) {
    if (tries <= 0) return computeFromSource(home, month);  // не крутись вічно — порахуй сам
    await sleep(50);                                        // хтось рахує — почекай і перечитай
    return monthlyKwhLocked(home, month, tries - 1);
  }
  try {
    const kwh = await computeFromSource(home, month);
    await cache.set(key, kwh, { ttlSeconds: 300 });
    return kwh;
  } finally {
    await cache.del(lock);                                  // (обережно — див. пастки)
  }
}
