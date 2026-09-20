/**
 * rate_limit_headers.ts
 *
 * Генератор стандартизованих HTTP-заголовків RateLimit відповідно до специфікацій IETF.
 * Забезпечує прозоре інформування клієнтів (API consumers) про стан їхньої квоти,
 * залишок токенів, час скидання вікна та паузу перед повторним запитом (Retry-After).
 */

import type { RateLimitVerdict } from './types.ts';

/**
 * Клас для формування стандартних HTTP-заголовків обмеження частоти запитів:
 * - RateLimit-Limit: максимальний ліміт запитів у поточному вікні
 * - RateLimit-Remaining: кількість доступних запитів
 * - RateLimit-Reset: секунди до поновлення квоти
 * - RateLimit-Policy: опис діючої політики квотування
 * - Retry-After: пауза очікування при блокуванні (HTTP 429)
 */
export class RateLimitHeaderFormatter {
  private readonly globalLimit: number;
  private readonly windowSeconds: number;

  constructor(globalLimit: number, windowSeconds: number) {
    this.globalLimit = globalLimit;
    this.windowSeconds = windowSeconds;
  }

  /**
   * Формує словник HTTP-заголовків на основі отриманого вердикту.
   */
  public format(verdict: RateLimitVerdict): Record<string, string> {
    const remainingCount = Math.max(0, Math.floor(verdict.remaining));
    const resetSec = Math.max(1, Math.ceil(verdict.resetSeconds));

    const headers: Record<string, string> = {
      // Стандартні чернетки IETF HTTP RateLimit Headers
      'RateLimit-Limit': String(verdict.limit),
      'RateLimit-Remaining': String(remainingCount),
      'RateLimit-Reset': String(resetSec),
      'RateLimit-Policy': `${this.globalLimit};w=${this.windowSeconds}`,
      // Діагностичний заголовок архітектури крайового вузла
      'X-RateLimit-Scope': 'edge-token-lease',
    };

    if (verdict.isFallback) {
      headers['X-RateLimit-Fallback'] = 'fail-open-active';
    }

    // Якщо запит заблоковано через перевищення ліміту (HTTP 429),
    // обов'язково додаємо стандартний заголовок Retry-After (RFC 7231 / RFC 6585)
    if (!verdict.allowed) {
      headers['Retry-After'] = String(resetSec);
    }

    return headers;
  }

  /**
   * Допоміжний метод для застосування сформованих заголовків до стандартного об'єкта Headers.
   */
  public applyToHeaders(
    target: { set(name: string, value: string): void },
    verdict: RateLimitVerdict
  ): void {
    const headerMap = this.format(verdict);
    for (const [key, value] of Object.entries(headerMap)) {
      target.set(key, value);
    }
  }
}
