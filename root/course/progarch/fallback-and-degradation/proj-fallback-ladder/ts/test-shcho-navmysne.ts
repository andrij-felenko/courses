// Підроблена залежність із перемикачем: down=true → кидає, наче хаб замовк.
class FakeDevice {
  down = false;
  reading: Reading = { temperature: 21.5, stale: false };
  async read(id: string): Promise<Reading> {
    if (this.down) throw new TimeoutError(id); // ← навмисно «вимкнена» залежність
    return { ...this.reading };
  }
}

class MapCache<T> implements Cache<T> {
  private m = new Map<string, Entry<T>>();
  get(key: string) { return this.m.get(key); }
  put(key: string, value: T) { this.m.set(key, { value, at: Date.now() }); }
  seed(key: string, value: T, at: number) { this.m.set(key, { value, at }); } // шов для тесту
}
