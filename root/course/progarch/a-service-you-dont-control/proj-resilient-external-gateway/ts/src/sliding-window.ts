import type { CallResult, WindowSnapshot } from './types.ts';

interface Bucket {
  startTime: number;
  successCount: number;
  failureCount: number;
  slowCount: number;
}

/**
 * Часове ковзне вікно з нарізкою на фіксовані кошики (Bucketed Sliding Window).
 * Забезпечує константну пам'ять O(B) та швидкий запис O(1),
 * дискретно зрізаючи застарілі періоди без збереження окремих викликів.
 */
export class SlidingWindow {
  private readonly windowDurationMs: number;
  private readonly bucketCount: number;
  private readonly bucketDurationMs: number;
  private readonly buckets: Bucket[] = [];

  constructor(windowDurationMs: number, bucketCount: number) {
    this.windowDurationMs = windowDurationMs;
    this.bucketCount = bucketCount;
    this.bucketDurationMs = Math.floor(windowDurationMs / bucketCount);
  }

  /**
   * Фіксує результат виконання виклику в поточному часовому кошику.
   */
  record(result: CallResult): void {
    const now = Date.now();
    this.pruneOldBuckets(now);
    const currentBucket = this.getOrCreateCurrentBucket(now);

    if (result === 'SUCCESS') {
      currentBucket.successCount++;
    } else if (result === 'FAILURE') {
      currentBucket.failureCount++;
    } else if (result === 'SLOW') {
      currentBucket.slowCount++;
    }
  }

  /**
   * Формує агрегований числовий зріз показників у поточному вікні.
   */
  getSnapshot(): WindowSnapshot {
    const now = Date.now();
    this.pruneOldBuckets(now);

    let successCount = 0;
    let failureCount = 0;
    let slowCount = 0;

    for (const b of this.buckets) {
      successCount += b.successCount;
      failureCount += b.failureCount;
      slowCount += b.slowCount;
    }

    const totalCalls = successCount + failureCount + slowCount;
    const failureRate = totalCalls > 0 ? (failureCount + slowCount) / totalCalls : 0;
    const slowCallRate = totalCalls > 0 ? slowCount / totalCalls : 0;

    return {
      totalCalls,
      successCount,
      failureCount,
      slowCount,
      failureRate,
      slowCallRate,
    };
  }

  /**
   * Повністю очищує збережені кошики (наприклад, при зміні стану автомата).
   */
  reset(): void {
    this.buckets.length = 0;
  }

  private pruneOldBuckets(now: number): void {
    const threshold = now - this.windowDurationMs;
    while (this.buckets.length > 0 && this.buckets[0].startTime < threshold) {
      this.buckets.shift();
    }
  }

  private getOrCreateCurrentBucket(now: number): Bucket {
    const bucketStartTime = Math.floor(now / this.bucketDurationMs) * this.bucketDurationMs;
    const lastBucket = this.buckets[this.buckets.length - 1];

    if (lastBucket && lastBucket.startTime === bucketStartTime) {
      return lastBucket;
    }

    const newBucket: Bucket = {
      startTime: bucketStartTime,
      successCount: 0,
      failureCount: 0,
      slowCount: 0,
    };
    this.buckets.push(newBucket);
    return newBucket;
  }
}
