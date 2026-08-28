import { performance } from "perf_hooks";

interface CacheEntry<T> {
  value: T;
  expiry: number; // мілісекунди
  deltaSec: number;
}

export class StampedeGuard<T> {
  private cache = new Map<string, CacheEntry<T>>();
  private inFlight = new Map<string, Promise<T>>();

  constructor(private beta: number = 1.0) {}

  private shouldRecomputeXFetch(entry: CacheEntry<T>): boolean {
    const now = Date.now();
    if (now >= entry.expiry) return true;
    if (entry.deltaSec <= 0) return false;

    const u = Math.max(0.0001, Math.random());
    const shiftMs = -entry.deltaSec * this.beta * Math.log(u) * 1000;
    return now + shiftMs > entry.expiry;
  }

  async get(key: string, ttlSec: number, fetcher: () => Promise<T>): Promise<T> {
    const entry = this.cache.get(key);
    if (entry && !this.shouldRecomputeXFetch(entry)) {
      return entry.value;
    }

    // Single-Flight: повертаємо активний Promise, якщо він уже виконується
    const activePromise = this.inFlight.get(key);
    if (activePromise) {
      return activePromise;
    }

    const leaderPromise = (async () => {
      const start = performance.now();
      try {
        const result = await fetcher();
        const deltaSec = (performance.now() - start) / 1000;

        this.cache.set(key, {
          value: result,
          expiry: Date.now() + ttlSec * 1000,
          deltaSec,
        });

        return result;
      } finally {
        this.inFlight.delete(key);
      }
    })();

    this.inFlight.set(key, leaderPromise);
    return leaderPromise;
  }
}
