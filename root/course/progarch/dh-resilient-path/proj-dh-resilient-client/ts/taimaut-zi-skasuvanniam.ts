// Спільна мова помилок: прапорець retryable тече ВГОРУ по стосу.
class TimeoutError_ extends Error { readonly retryable = true; }
class Upstream5xx extends Error { readonly retryable = true;  constructor(readonly status: number) { super(`5xx ${status}`); } }
class Upstream4xx extends Error { readonly retryable = false; constructor(readonly status: number) { super(`4xx ${status}`); } }
const isRetryable = (e: unknown): boolean => !!(e as { retryable?: boolean })?.retryable;

// ТАЙМАУТ: скасовує виклик (abort), а не просто кидає його напризволяще.
function withTimeout<T>(ms: number, fn: (signal: AbortSignal) => Promise<T>): Promise<T> {
  const ac = new AbortController();
  const timer = setTimeout(() => ac.abort(), ms);
  return fn(ac.signal)
    .catch((e) => { throw ac.signal.aborted ? new TimeoutError_() : e; })
    .finally(() => clearTimeout(timer));
}

// ПОВТОР: до tries спроб, поки помилка ВАРТА повтору. Останню відмову — кидає далі
// (не ковтає!), тож її бачить запобіжник, що стоїть зовні.
async function withRetry<T>(tries: number, fn: () => Promise<T>): Promise<T> {
  let last: unknown;
  for (let i = 0; i < tries; i++) {
    try { return await fn(); }
    catch (e) { last = e; if (!isRetryable(e) || i === tries - 1) throw e; }
  }
  throw last;
}
