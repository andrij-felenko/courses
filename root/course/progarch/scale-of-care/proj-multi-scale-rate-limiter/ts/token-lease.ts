import type { RateLimitConfig, TokenLease } from './types.ts';

/**
 * Менеджер локальної оренди токенів у пам'яті V8 ізоляту Cloudflare Worker.
 * Забезпечує миттєву перевірку за 0.05-0.2 мс без мережевих звернень.
 */
export class TokenLeaseManager {
  private readonly leases = new Map<string, TokenLease>();
  private readonly config: RateLimitConfig;

  constructor(config: RateLimitConfig) {
    this.config = config;
  }

  /**
   * Спробувати списати токен із локальної оренди.
   */
  consume(key: string): { success: boolean; remaining: number; resetInMs: number } {
    const now = Date.now();
    const lease = this.leases.get(key);

    if (!lease || lease.expiresAt <= now || lease.availableTokens <= 0) {
      return {
        success: false,
        remaining: 0,
        resetInMs: lease && lease.expiresAt > now ? lease.expiresAt - now : this.config.windowMs,
      };
    }

    lease.availableTokens -= 1;
    return {
      success: true,
      remaining: lease.availableTokens,
      resetInMs: lease.expiresAt - now,
    };
  }

  /**
   * Оновити або поповнити локальну оренду токенів.
   */
  replenish(key: string, tokens: number, ttlMs: number): void {
    const now = Date.now();
    const existing = this.leases.get(key);

    if (existing && existing.expiresAt > now) {
      existing.availableTokens += tokens;
      existing.expiresAt = Math.max(existing.expiresAt, now + ttlMs);
    } else {
      this.leases.set(key, {
        availableTokens: tokens,
        expiresAt: now + ttlMs,
      });
    }
  }

  /**
   * Перевірити, чи потребує клієнт термінового поповнення оренди.
   */
  needsRefill(key: string): boolean {
    const lease = this.leases.get(key);
    if (!lease) return true;
    const now = Date.now();
    return lease.expiresAt <= now || lease.availableTokens < Math.ceil(this.config.leaseSize * 0.3);
  }

  /**
   * Очистити протерміновані оренди для запобігання витоку пам'яті в довгоживучих ізолятах.
   */
  cleanup(): void {
    const now = Date.now();
    for (const [key, lease] of this.leases.entries()) {
      if (lease.expiresAt <= now && lease.availableTokens <= 0) {
        this.leases.delete(key);
      }
    }
  }
}
