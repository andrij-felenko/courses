import { EventEmitter } from "events";

interface DeviceState {
  id: string;
  type: string;
  status: string;
  value: number;
}

interface HomeState {
  homeId: string;
  devices: DeviceState[];
  version: number;
}

// Singleflight група для TypeScript (схлопування паралельних промахів)
class SingleflightTS {
  private inFlight = new Map<string, Promise<HomeState>>();

  async doCall(key: string, fetcher: () => Promise<HomeState>): Promise<HomeState> {
    const existing = this.inFlight.get(key);
    if (existing) {
      console.log(`[Singleflight TS] Coalesced request for key: ${key}`);
      return existing;
    }

    const promise = (async () => {
      try {
        return await fetcher();
      } finally {
        this.inFlight.delete(key);
      }
    })();

    this.inFlight.set(key, promise);
    return promise;
  }
}

export class TieredCacheNodeTS {
  private l1Memory = new Map<string, HomeState>();
  private redisStore = new Map<string, HomeState>();
  private pubsub = new EventEmitter();
  private singleflight = new SingleflightTS();

  constructor() {
    // Підписка на мережеві події вимивання L1
    this.pubsub.on("evict", (key: string, version: number) => {
      const current = this.l1Memory.get(key);
      if (!current || version >= current.version) {
        this.l1Memory.delete(key);
        console.log(`[L1 TS Evict] Key evicted: ${key} (v${version})`);
      }
    });
  }

  // ── Read Path ─────────────────────────────────────────────────────────────
  async getHomeState(
    homeId: string,
    originDBFetch: (id: string) => Promise<HomeState>
  ): Promise<HomeState> {
    const cacheKey = `dh:home:${homeId}`;

    // 1. Перевірка L1 Process Memory
    if (this.l1Memory.has(cacheKey)) {
      const cached = this.l1Memory.get(cacheKey)!;
      console.log(`[L1 TS HIT] Key: ${cacheKey} (v${cached.version})`);
      return cached;
    }

    // 2. Перевірка L2 Redis Cluster
    if (this.redisStore.has(cacheKey)) {
      const redisVal = this.redisStore.get(cacheKey)!;
      console.log(`[L2 TS HIT] Key: ${cacheKey} (v${redisVal.version})`);
      this.l1Memory.set(cacheKey, redisVal);
      return redisVal;
    }

    // 3. L1/L2 MISS: Singleflight DB Fetch
    return this.singleflight.doCall(cacheKey, async () => {
      console.log(`[Origin DB Fetch TS] Executing single query for: ${cacheKey}`);
      const freshState = await originDBFetch(homeId);
      
      this.redisStore.set(cacheKey, freshState);
      this.l1Memory.set(cacheKey, freshState);
      return freshState;
    });
  }

  // ── Write Path ────────────────────────────────────────────────────────────
  async updateHomeState(
    newState: HomeState,
    originDBSave: (state: HomeState) => Promise<void>
  ): Promise<void> {
    const cacheKey = `dh:home:${newState.homeId}`;

    // 1. Запис у базу даних
    await originDBSave(newState);

    // 2. Запис у L2 Redis
    this.redisStore.set(cacheKey, newState);

    // 3. Локальна інвалідація та трансляція у Pub/Sub
    this.pubsub.emit("evict", cacheKey, newState.version);

    // 4. Виклик L3 Edge Purge API
    console.log(`[L3 CDN Purge TS] Soft Purge header: Surrogate-Key home-${newState.homeId}`);
  }
}
