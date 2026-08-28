export type FreshnessStatus = 'FRESH' | 'STALE_REVALIDATING' | 'STALE_DEGRADED' | 'EXPIRED';

export interface FreshnessEnvelope<T> {
  data: T;
  dataTimestampIso: string;
  fetchedAtMs: number;
  ttlMs: number;
  staleGraceMs: number;
}

export interface SWREvaluation<T> {
  data: T;
  status: FreshnessStatus;
  lagMs: number;
  shouldRevalidate: boolean;
}

export class SWRCacheManager<T> {
  private cache = new Map<string, FreshnessEnvelope<T>>();

  public set(key: string, data: T, ttlMs: number, staleGraceMs: number, timestampIso?: string): void {
    this.cache.set(key, {
      data,
      dataTimestampIso: timestampIso || new Date().toISOString(),
      fetchedAtMs: Date.now(),
      ttlMs,
      staleGraceMs
    });
  }

  public evaluate(key: string): SWREvaluation<T> | null {
    const item = this.cache.get(key);
    if (!item) return null;

    const now = Date.now();
    const ageMs = now - item.fetchedAtMs;
    const dataTimeMs = new Date(item.dataTimestampIso).getTime();
    const lagMs = now - dataTimeMs;

    let status: FreshnessStatus = 'FRESH';
    let shouldRevalidate = false;

    if (ageMs <= item.ttlMs) {
      status = 'FRESH';
    } else if (ageMs <= item.ttlMs + item.staleGraceMs) {
      status = 'STALE_REVALIDATING';
      shouldRevalidate = true;
    } else if (ageMs <= item.ttlMs + item.staleGraceMs * 5) {
      status = 'STALE_DEGRADED';
      shouldRevalidate = true;
    } else {
      status = 'EXPIRED';
    }

    return {
      data: item.data,
      status,
      lagMs,
      shouldRevalidate
    };
  }

  // Виконати оптимістичне оновлення з гарантованим відкатом
  public async executeOptimisticUpdate(
    key: string,
    optimisticValue: T,
    serverMutation: () => Promise<T>,
    onError: (err: Error, rollbackValue: T | undefined) => void
  ): Promise<T> {
    const previousState = this.cache.get(key);

    // 1. Оптимістичний запис локально
    this.set(key, optimisticValue, 5000, 15000);

    try {
      // 2. Виклик мутації на сервері
      const confirmedValue = await serverMutation();
      this.set(key, confirmedValue, 10000, 30000);
      return confirmedValue;
    } catch (error) {
      // 3. Відкат при помилці
      if (previousState) {
        this.cache.set(key, previousState.data, previousState.ttlMs, previousState.staleGraceMs);
      } else {
        this.cache.delete(key);
      }
      onError(error as Error, previousState?.data);
      throw error;
    }
  }
}
