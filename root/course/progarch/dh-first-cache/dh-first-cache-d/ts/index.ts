// In-process TTL-кеш — найпростіше, що працює для ОДНОГО процесу
class TtlCache<V> {
  private store = new Map<string, { value: V; expires: number }>();
  constructor(private ttlMs: number) {}
  get(key: string): V | undefined {
    const e = this.store.get(key);
    if (!e || Date.now() > e.expires) { this.store.delete(key); return undefined; }
    return e.value;
  }
  set(key: string, value: V) { this.store.set(key, { value, expires: Date.now() + this.ttlMs }); }
  invalidate(key: string) { this.store.delete(key); }
}

const registry = new TtlCache<HomeRegistry>(5 * 60_000);  // TTL 5 хв — бюджет несвіжості реєстру

// ЧИТАННЯ реєстру — cache-aside
async function getRegistry(homeId: string): Promise<HomeRegistry> {
  const hit = registry.get(homeId);
  if (hit) return hit;                              // влучили — жодного дотику до бази
  const fresh = await repo.loadRegistry(homeId);   // промах → джерело (переживаємо порожній кеш)
  registry.set(homeId, fresh);
  return fresh;
}

// ЗАПИС — скид копії, щоб зміна проступила негайно, а не за TTL
async function renameDevice(homeId: string, deviceId: string, name: string): Promise<void> {
  await repo.renameDevice(homeId, deviceId, name);  // джерело правди — база
  registry.invalidate(homeId);                       // наступне читання перечитає свіже
}

// ЖИВИЙ СТАН — повз кеш: on/off мусить бути свіжим (ворота 3)
const getLiveState = (deviceId: string) => repo.loadState(deviceId);
