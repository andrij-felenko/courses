import { AsyncBatcher } from './async-batcher.ts';
import { TokenLeaseManager } from './token-lease.ts';
import type {
  CentralRateLimitBackend,
  ExecutionContext,
  RateLimitConfig,
  RateLimitDecision,
} from './types.ts';

/**
 * Периферійний обмежувач частоти з оптимістичним локальним списанням
 * та асинхронним фоновим батчингом.
 */
export class EdgeRateLimiter {
  private readonly backend: CentralRateLimitBackend;
  private readonly config: RateLimitConfig;
  private readonly leaseManager: TokenLeaseManager;
  private readonly batcher: AsyncBatcher;

  constructor(backend: CentralRateLimitBackend, config: RateLimitConfig) {
    this.backend = backend;
    this.config = config;
    this.leaseManager = new TokenLeaseManager(config);
    this.batcher = new AsyncBatcher(backend, config);
  }

  /**
   * Перевірити запит на межі мережі з мінімальною затримкою.
   */
  async check(key: string, ctx?: ExecutionContext): Promise<RateLimitDecision> {
    const start = performance.now();

    // 1. Спроба списати токен із локальної оренди (наносекунди/мікросекунди)
    const localResult = this.leaseManager.consume(key);

    if (localResult.success) {
      // Фіксуємо списання в буфері асинхронного батчера
      this.batcher.record(key, 1);

      // Якщо буфер заповнився або час сплив — скидаємо батч у фоні
      if (this.batcher.shouldFlush() && ctx) {
        ctx.waitUntil(this.batcher.flush().catch((err) => {
          console.error('[Edge RateLimiter] Фонова помилка скидання:', err);
        }));
      }

      // Якщо локальний запас добігає кінця — замовляємо нову оренду асинхронно
      if (this.leaseManager.needsRefill(key) && ctx) {
        ctx.waitUntil(this.refillLeaseInBackground(key));
      }

      return {
        allowed: true,
        remaining: localResult.remaining,
        limit: this.config.limit,
        resetInMs: localResult.resetInMs,
        source: 'local-lease',
        reason: `Запит схвалено локально за ${(performance.now() - start).toFixed(3)} мс (залишок: ${localResult.remaining})`,
      };
    }

    // 2. Локальних токенів немає: виконуємо синхронне поповнення оренди з центрального сховища
    try {
      const lease = await this.backend.requestLease(key, this.config.leaseSize, this.config.windowMs);
      this.leaseManager.replenish(key, lease.grantedTokens, lease.ttlMs);

      // Повторюємо списання після поповнення
      const retryResult = this.leaseManager.consume(key);
      if (retryResult.success) {
        this.batcher.record(key, 1);
        return {
          allowed: true,
          remaining: retryResult.remaining,
          limit: this.config.limit,
          resetInMs: retryResult.resetInMs,
          source: 'local-lease',
          reason: `Оренду оновлено у центрі (${(performance.now() - start).toFixed(1)} мс), запит дозволено`,
        };
      }
    } catch (err) {
      // 3. Аварійний режим при недоступності центрального координатора (Fail-Open)
      console.warn(`[Edge RateLimiter] Відмова центрального бекенда: ${err}. Перехід у fallback.`);
      return {
        allowed: true,
        remaining: 0,
        limit: this.config.limit,
        resetInMs: this.config.windowMs,
        source: 'fallback',
        reason: 'Аварійний режим Fail-Open: центральний координатор недоступний, запит пропущено',
      };
    }

    // Ліміт вичерпано повністю
    return {
      allowed: false,
      remaining: 0,
      limit: this.config.limit,
      resetInMs: localResult.resetInMs,
      source: 'local-lease',
      reason: `Вичерпано квоту запитів. Спробуйте через ${Math.ceil(localResult.resetInMs / 1000)} сек.`,
    };
  }

  /**
   * Фонове поповнення оренди без блокування клієнтського запиту.
   */
  private async refillLeaseInBackground(key: string): Promise<void> {
    try {
      const lease = await this.backend.requestLease(key, this.config.leaseSize, this.config.windowMs);
      this.leaseManager.replenish(key, lease.grantedTokens, lease.ttlMs);
    } catch (err) {
      console.warn(`[Edge RateLimiter] Не вдалося фоново оновити оренду: ${err}`);
    }
  }

  /**
   * Примусове скидання буфера (використовується при завершенні життєвого циклу).
   */
  async flush(): Promise<void> {
    await this.batcher.flush();
  }
}
