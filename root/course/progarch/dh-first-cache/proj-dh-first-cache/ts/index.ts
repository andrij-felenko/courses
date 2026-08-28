// ── Порт: звужений зріз DeviceRepository з DH v3 (реєстр + живий стан) ──
interface Device { id: string; name: string; room: string; kind: string; }
interface HomeRegistry { homeId: string; plan: string; threshold: number; devices: Device[]; }
interface LiveState { deviceId: string; on: boolean; celsius: number; }

interface DeviceRepository {
  loadRegistry(homeId: string): Promise<HomeRegistry>;                 // повільний зріз — кешуємо
  loadState(deviceId: string): Promise<LiveState>;                     // живий зріз — повз кеш
  renameDevice(homeId: string, deviceId: string, name: string): Promise<void>;
  pairDevice(homeId: string, d: Device): Promise<void>;
}

// ── TTL-кеш зі ВСТАВНИМ годинником (щоб тести й стенд кермували часом) ──
class TtlCache<V> {
  private store = new Map<string, { value: V; expires: number }>();
  constructor(private ttlMs: number, private now: () => number = Date.now) {}
  get(key: string): V | undefined {
    const e = this.store.get(key);
    if (!e) return undefined;
    if (this.now() >= e.expires) { this.store.delete(key); return undefined; }   // протухла → промах
    return e.value;
  }
  set(key: string, value: V): void { this.store.set(key, { value, expires: this.now() + this.ttlMs }); }
  invalidate(key: string): void { this.store.delete(key); }
  get size(): number { return this.store.size; }
}

// ── Кеш реєстру: cache-aside + закликання + скид-на-запис, ПОВЕРХ того самого порту ──
class CachedRegistry implements DeviceRepository {
  private cache: TtlCache<HomeRegistry>;
  private inflight = new Map<string, Promise<HomeRegistry>>();   // рейси в польоті (один на ключ)
  loads = 0;                                                     // скільки читань дійшло до джерела

  constructor(private inner: DeviceRepository, ttlMs: number, now: () => number = Date.now) {
    this.cache = new TtlCache(ttlMs, now);
  }

  loadRegistry(homeId: string): Promise<HomeRegistry> {
    const hit = this.cache.get(homeId);
    if (hit) return Promise.resolve(hit);            // влучили — джерело не турбуємо
    const racing = this.inflight.get(homeId);
    if (racing) return racing;                        // хтось уже везе те саме — чекаємо на нього
    const flight = this.fill(homeId);                 // ПЕРШИЙ промах — єдиний похід у джерело
    this.inflight.set(homeId, flight);                // синхронно, без await між get і set → гонки нема
    return flight;
  }

  private async fill(homeId: string): Promise<HomeRegistry> {
    this.loads++;
    try {
      const fresh = await this.inner.loadRegistry(homeId);   // промах → джерело (переживаємо порожнечу)
      this.cache.set(homeId, fresh);
      return fresh;
    } finally {
      this.inflight.delete(homeId);                          // рейс завершено — прибрати слот
    }
  }

  loadState(deviceId: string): Promise<LiveState> {          // повз кеш: on/off і °C мусять бути свіжі
    return this.inner.loadState(deviceId);
  }

  async renameDevice(homeId: string, deviceId: string, name: string): Promise<void> {
    await this.inner.renameDevice(homeId, deviceId, name);   // спершу джерело правди — база…
    this.cache.invalidate(homeId);                           // …тоді скид: наступне читання перечитає свіже
  }
  async pairDevice(homeId: string, d: Device): Promise<void> {
    await this.inner.pairDevice(homeId, d);                  // спарювання додало пристрій…
    this.cache.invalidate(homeId);                           // …тож стара копія реєстру протухла
  }
}
