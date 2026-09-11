import type { BatchDelta, CentralRateLimitBackend, RateLimitConfig } from './types.ts';

/**
 * Асинхронний батчер: накопичує локальні списання токенів і скидає їх пачками.
 */
export class AsyncBatcher {
  private buffer: BatchDelta[] = [];
  private lastFlushTime = Date.now();
  private isFlushing = false;
  private readonly backend: CentralRateLimitBackend;
  private readonly config: RateLimitConfig;

  constructor(backend: CentralRateLimitBackend, config: RateLimitConfig) {
    this.backend = backend;
    this.config = config;
  }

  /**
   * Зареєструвати споживання токена в буфері батчера.
   */
  record(key: string, count = 1): void {
    const existing = this.buffer.find((item) => item.key === key);
    if (existing) {
      (existing as { count: number }).count += count;
    } else {
      this.buffer.push({
        key,
        count,
        timestamp: Date.now(),
      });
    }
  }

  /**
   * Перевірити, чи настав час скинути накопичені дані до центральної бази.
   */
  shouldFlush(): boolean {
    if (this.buffer.length === 0) return false;
    const now = Date.now();
    const exceedsSize = this.buffer.length >= this.config.maxBatchSize;
    const exceedsTime = now - this.lastFlushTime >= this.config.flushIntervalMs;
    return exceedsSize || exceedsTime;
  }

  /**
   * Асинхронно передати накопичені батчі до центрального сховища.
   * Викликається у фоні через ExecutionContext.waitUntil.
   */
  async flush(): Promise<{ flushedCount: number; durationMs: number }> {
    if (this.buffer.length === 0 || this.isFlushing) {
      return { flushedCount: 0, durationMs: 0 };
    }

    this.isFlushing = true;
    const start = Date.now();
    const toFlush = [...this.buffer];
    this.buffer = [];

    try {
      await this.backend.commitBatch(toFlush);
      this.lastFlushTime = Date.now();
      return {
        flushedCount: toFlush.reduce((acc, item) => acc + item.count, 0),
        durationMs: Date.now() - start,
      };
    } catch (err) {
      console.warn(`[Edge RateLimiter] Помилка фонового скидання батчу: ${err}. Відновлення буфера.`);
      this.buffer.unshift(...toFlush);
      throw err;
    } finally {
      this.isFlushing = false;
    }
  }

  get pendingItemsCount(): number {
    return this.buffer.length;
  }
}
