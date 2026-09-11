import type { BatchDelta, CentralRateLimitBackend } from './types.ts';

interface CentralClientQuota {
  allocatedTokens: number;
  consumedTokens: number;
  windowStart: number;
}

/**
 * In-memory емулятор центрального координатора лімітів (аналог Redis / Durable Object).
 * Демонструє затримку WAN-мережі та об'єднання розподілених лічильників.
 */
export class MockCentralBackend implements CentralRateLimitBackend {
  private readonly clientQuotas = new Map<string, CentralClientQuota>();
  private networkLatencyMs = 25; // 25 мс симуляція RTT до центрального регіону
  private failRequests = false;

  setSimulateLatency(ms: number): void {
    this.networkLatencyMs = ms;
  }

  setSimulateFailure(fail: boolean): void {
    this.failRequests = fail;
  }

  async requestLease(
    key: string,
    requestedTokens: number,
    windowMs: number
  ): Promise<{ grantedTokens: number; ttlMs: number }> {
    await this.delay(this.networkLatencyMs);

    if (this.failRequests) {
      throw new Error('Центральне сховище недоступне (Network timeout)');
    }

    const now = Date.now();
    let quota = this.clientQuotas.get(key);

    if (!quota || now - quota.windowStart >= windowMs) {
      quota = {
        allocatedTokens: 0,
        consumedTokens: 0,
        windowStart: now,
      };
      this.clientQuotas.set(key, quota);
    }

    // Виділяємо токени з центрального бюджету
    quota.allocatedTokens += requestedTokens;
    const remainingTtl = Math.max(100, windowMs - (now - quota.windowStart));

    return {
      grantedTokens: requestedTokens,
      ttlMs: remainingTtl,
    };
  }

  async commitBatch(deltas: ReadonlyArray<BatchDelta>): Promise<void> {
    await this.delay(this.networkLatencyMs);

    if (this.failRequests) {
      throw new Error('Центральне сховище недоступне під час коміту батчу');
    }

    for (const delta of deltas) {
      const quota = this.clientQuotas.get(delta.key);
      if (quota) {
        quota.consumedTokens += delta.count;
      }
    }
  }

  getSnapshot(key: string): CentralClientQuota | undefined {
    return this.clientQuotas.get(key);
  }

  private delay(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
