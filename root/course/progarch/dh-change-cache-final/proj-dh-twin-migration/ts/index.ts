// TypeScript: BFF Twin Cache Invalidator & Singleflight Coalescer
export interface DeviceTwinState {
  homeId: string;
  deviceId: string;
  stateJson: string;
  version: number;
  observedAtMs: number;
  updatedAtMs: number;
}

export enum MigrationPhase {
  Phase0_Baseline = 0,
  Phase1_DualWrite = 1,
  Phase2_ReadPrimaryV_Backfill = 2,
  Phase3_Contract = 3,
}

export class SingleflightCache {
  private cache = new Map<string, { state: DeviceTwinState; expiresAtMs: number }>();
  private inFlight = new Map<string, Promise<DeviceTwinState>>();

  async getOrFetch(
    homeId: string,
    nowMs: number,
    fetcher: (id: string) => Promise<DeviceTwinState>
  ): Promise<DeviceTwinState> {
    const cached = this.cache.get(homeId);
    if (cached && cached.expiresAtMs > nowMs) {
      return cached.state;
    }

    if (this.inFlight.has(homeId)) {
      return this.inFlight.get(homeId)!;
    }

    const promise = fetcher(homeId)
      .then((state) => {
        const jitter = Math.floor(Math.random() * 1000);
        this.cache.set(homeId, { state, expiresAtMs: nowMs + 5000 + jitter });
        return state;
      })
      .finally(() => {
        this.inFlight.delete(homeId);
      });

    this.inFlight.set(homeId, promise);
    return promise;
  }

  invalidateIfNewer(homeId: string, version: number): void {
    const cached = this.cache.get(homeId);
    if (cached && version >= cached.state.version) {
      this.cache.delete(homeId);
    }
  }
}
