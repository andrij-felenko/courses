interface Service { handle(key: string): string; }

class Real implements Service {
  handle(key: string) { return expensive(key); }   // дорогий обрахунок
}

// ДО + ПІСЛЯ: заміряти час навколо делегації
class Timed implements Service {
  constructor(private inner: Service) {}
  handle(key: string) {
    const t0 = performance.now();                   // ДО
    const out = this.inner.handle(key);             // делегація
    log(`${key}: ${(performance.now() - t0).toFixed(1)} ms`);  // ПІСЛЯ
    return out;
  }
}

// ЗАМІСТЬ: на влучення кеш НЕ делегує — обриває ланцюг
class Cached implements Service {
  private c = new Map<string, string>();
  constructor(private inner: Service) {}
  handle(key: string) {
    const hit = this.c.get(key);
    if (hit !== undefined) return hit;              // обрив: без делегації
    const out = this.inner.handle(key);             // промах → делегуємо
    this.c.set(key, out);
    return out;
  }
}

const svc = new Timed(new Cached(new Real()));
