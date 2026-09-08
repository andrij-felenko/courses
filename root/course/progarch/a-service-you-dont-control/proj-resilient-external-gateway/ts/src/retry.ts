import type { RetryConfig } from './types.ts';
import { MaxRetriesExceededError } from './types.ts';

/**
 * Розраховує інтервал затримки за алгоритмом Full Jitter:
 * t = Math.random() * min(maxDelay, baseDelay * 2^attempt).
 * Рівномірно розсіює фази повторних спроб клієнтів, запобігаючи резонансним штормам.
 */
export function calculateFullJitter(attempt: number, baseDelayMs: number, maxDelayMs: number): number {
  const exponentialDelay = Math.min(maxDelayMs, baseDelayMs * Math.pow(2, attempt));
  return Math.floor(Math.random() * exponentialDelay);
}

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      return reject(signal.reason);
    }
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener('abort', () => {
      clearTimeout(timer);
      reject(signal.reason);
    }, { once: true });
  });
}

/**
 * Обгортка для виконання операції з повторними спробами та рандомізованим відступом.
 */
export async function withRetry<T>(
  fn: (attempt: number) => Promise<T>,
  config: RetryConfig,
  isRetryable: (err: unknown) => boolean,
  parentSignal?: AbortSignal
): Promise<T> {
  let lastError: unknown;

  for (let attempt = 0; attempt < config.maxAttempts; attempt++) {
    try {
      if (parentSignal?.aborted) {
        throw parentSignal.reason;
      }
      return await fn(attempt);
    } catch (err) {
      lastError = err;

      // Не повторюємо фатальні помилки (4xx, розімкнений Circuit Breaker тощо)
      if (!isRetryable(err) || attempt === config.maxAttempts - 1) {
        throw err;
      }

      const delayMs = calculateFullJitter(attempt, config.baseDelayMs, config.maxDelayMs);
      await sleep(delayMs, parentSignal);
    }
  }

  throw new MaxRetriesExceededError(lastError, config.maxAttempts);
}
