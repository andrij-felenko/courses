import { NonRetryableError, RetryableError } from './types.ts';

export interface HttpClientResponse<T = unknown> {
  status: number;
  data: T;
}

/**
 * HTTP-клієнт із підтримкою ідемпотентності та класифікацією збоїв.
 * Прокидає Idempotency-Key у кожен запит та диференціює помилки 4xx проти 5xx.
 */
export class IdempotentHttpClient {
  private readonly timeoutMs: number;

  constructor(timeoutMs = 2500) {
    this.timeoutMs = timeoutMs;
  }

  async post<TReq, TRes>(
    url: string,
    payload: TReq,
    idempotencyKey: string
  ): Promise<HttpClientResponse<TRes>> {
    const abortCtrl = new AbortController();
    const timer = setTimeout(() => {
      abortCtrl.abort(new Error(`Перевищено таймаут запиту (${this.timeoutMs} мс)`));
    }, this.timeoutMs);

    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': idempotencyKey,
        },
        body: JSON.stringify(payload),
        signal: abortCtrl.signal,
      });

      if (resp.ok) {
        const data = (await resp.json()) as TRes;
        return { status: resp.status, data };
      }

      const bodyText = await resp.text().catch(() => '');

      // 4xx (крім 429 Too Many Requests) — це фатальні помилки клієнта: повтори марні
      if (resp.status >= 400 && resp.status < 500 && resp.status !== 429) {
        throw new NonRetryableError(
          `Клієнтська помилка HTTP ${resp.status}: ${bodyText || resp.statusText}`,
          resp.status
        );
      }

      // 5xx або 429 — тимчасові відмови служби або обмеження швидкості: підлягають ретраю
      throw new RetryableError(
        `Тимчасова помилка сервера HTTP ${resp.status}: ${bodyText || resp.statusText}`,
        resp.status
      );
    } catch (err) {
      if (err instanceof NonRetryableError || err instanceof RetryableError) {
        throw err;
      }
      // Мережеві помилки сокета (ECONNREFUSED, ECONNRESET, Timeout) — повторювані
      throw new RetryableError(
        `Мережевий збій або обрив з'єднання: ${(err as Error).message}`
      );
    } finally {
      clearTimeout(timer);
    }
  }
}
