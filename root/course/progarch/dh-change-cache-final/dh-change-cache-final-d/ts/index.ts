// TypeScript: BFF Singleflight Cache & Versioned Invalidator
export interface DeviceTwinDTO {
  homeId: string;
  stateJson: string;
  versionSeq: number;
  observedAtMs: number;
  updatedAtMs: number;
}

export class SingleflightBffCache {
  private cache = new Map<string, { dto: DeviceTwinDTO; expiresAtMs: number }>();
  private inFlight = new Map<string, Promise<DeviceTwinDTO>>();

  async getOrFetch(
    homeId: string,
    nowMs: number,
    dbFetcher: (id: string) => Promise<DeviceTwinDTO>
  ): Promise<DeviceTwinDTO> {
    const hit = this.cache.get(homeId);
    if (hit && hit.expiresAtMs > nowMs) {
      return hit.dto;
    }

    if (this.inFlight.has(homeId)) {
      return this.inFlight.get(homeId)!;
    }

    const task = dbFetcher(homeId)
      .then((dto) => {
        const jitter = Math.floor(Math.random() * 500);
        this.cache.set(homeId, { dto, expiresAtMs: nowMs + 4000 + jitter });
        return dto;
      })
      .finally(() => {
        this.inFlight.delete(homeId);
      });

    this.inFlight.set(homeId, task);
    return task;
  }

  invalidateVersioned(homeId: string, versionSeq: number): void {
    const current = this.cache.get(homeId);
    if (current && versionSeq >= current.dto.versionSeq) {
      this.cache.delete(homeId);
    }
  }
}
