import type { ClientConfig } from './types.ts';
import {
  CircuitOpenError,
  BulkheadFullError,
  TimeoutError,
} from './types.ts';
import { Bulkhead } from './bulkhead.ts';
import { CircuitBreaker } from './circuit-breaker.ts';
import { withRetry } from './retry.ts';

/**
 * Фасадний стійкий HTTP-клієнт.
 * Компонує перебірку, трирівневі таймаути через AbortController,
 * ковзний запобіжник, Full Jitter ретраї та запасні варіанти Fallback.
 */
export class ResilientClient {
  private readonly config: ClientConfig;
  public readonly bulkhead: Bulkhead;
  public readonly circuitBreaker: CircuitBreaker;

  constructor(config: ClientConfig) {
    this.config = config;
    this.bulkhead = new Bulkhead(config.bulkhead);
    this.circuitBreaker = new CircuitBreaker(config.circuitBreaker);
  }

  /**
   * Виконує захищений запит з повною координацією шаблонів стійкості.
   */
  async execute<T>(
    endpointName: string,
    action: (signal: AbortSignal) => Promise<T>,
    fallback?: (err: unknown) => Promise<T>
  ): Promise<T> {
    try {
      // 1. Прохід крізь перебірку (Bulkhead): захист пулу від вичерпання
      return await this.bulkhead.execute(async () => {
        // 2. Перевірка дозволу запобіжника (Circuit Breaker): fail-fast при аварії
        this.circuitBreaker.tryAcquirePermission();

        // 3. Створення загального дедлайну операції через AbortController
        const totalAbortCtrl = new AbortController();
        const totalTimer = setTimeout(() => {
          totalAbortCtrl.abort(new TimeoutError('total', `Перевищено загальний дедлайн операції (${this.config.timeouts.totalTimeoutMs} мс)`));
        }, this.config.timeouts.totalTimeoutMs);

        const startTime = Date.now();

        try {
          // 4. Виконання повторних спроб з Full Jitter
          const result = await withRetry(
            async (_attempt) => {
              // Окремий таймаут на сокет для кожного окремого виклику
              const perCallAbortCtrl = new AbortController();
              const perCallTimer = setTimeout(() => {
                perCallAbortCtrl.abort(new TimeoutError('read', `Перевищено таймаут відповіді сокета (${this.config.timeouts.readTimeoutMs} мс)`));
              }, this.config.timeouts.readTimeoutMs);

              // Об'єднуємо сигнали дедлайну та локального таймауту
              const combinedSignal = AbortSignal.any([
                totalAbortCtrl.signal,
                perCallAbortCtrl.signal,
              ]);

              try {
                return await action(combinedSignal);
              } finally {
                clearTimeout(perCallTimer);
              }
            },
            this.config.retry,
            (err) => this.isRetryableError(err),
            totalAbortCtrl.signal
          );

          const durationMs = Date.now() - startTime;
          this.circuitBreaker.onSuccess(durationMs);
          return result;
        } catch (err) {
          const durationMs = Date.now() - startTime;
          this.circuitBreaker.onError(durationMs);
          throw err;
        } finally {
          clearTimeout(totalTimer);
        }
      });
    } catch (err) {
      // 5. Запасний варіант (Fallback): деградація на кеш або дефолт
      if (fallback) {
        return await fallback(err);
      }
      throw err;
    }
  }

  private isRetryableError(err: unknown): boolean {
    if (err instanceof CircuitOpenError || err instanceof BulkheadFullError) {
      return false; // Немає сенсу повторювати, якщо система сама блокує виклики
    }
    return true; // Мережеві збої та 5xx підлягають повторним спробам
  }
}
