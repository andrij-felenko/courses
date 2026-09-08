/**
 * Алгоритм експоненційного відступу з рандомізованим тремтінням Full Jitter:
 * t = Math.random() * min(maxDelay, baseDelay * 2^attempt).
 * Усуває фазову синхронізацію повторних викликів від пулу воркерів.
 */
export function calculateFullJitter(
  attempt: number,
  baseDelayMs: number,
  maxDelayMs: number
): number {
  const exponentialCap = Math.min(maxDelayMs, baseDelayMs * Math.pow(2, attempt));
  return Math.floor(Math.random() * exponentialCap);
}

export function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) return reject(signal.reason);
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener('abort', () => {
      clearTimeout(timer);
      reject(signal.reason);
    }, { once: true });
  });
}
