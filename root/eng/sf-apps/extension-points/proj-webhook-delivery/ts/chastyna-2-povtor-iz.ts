const BASE_MS = 1_000;        // база: 1 секунда
const CAP_MS = 300_000;       // стеля: 5 хвилин
const MAX_ATTEMPTS = 10;      // далі — здаємося (див. частину про dead-letter)

// Скільки чекати ПЕРЕД спробою №attempt (0-based): повне тремтіння.
function backoffDelay(attempt: number): number {
  const window = Math.min(CAP_MS, BASE_MS * 2 ** attempt);
  return Math.random() * window;               // random(0, window)
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Стукаємо, доки не вийде або доки не вичерпаємо спроби.
// Повертаємо true — доставлено; false — вичерпано (піде в dead-letter).
async function deliverWithRetry(
  url: string, d: SignedDelivery, deliveryId: string,
): Promise<boolean> {
  for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
    if (attempt > 0) await sleep(backoffDelay(attempt - 1));

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { ...d.headers, "Idempotency-Key": deliveryId },
        body: d.body,
        signal: AbortSignal.timeout(10_000),     // ЖОРСТКИЙ тайм-аут: мрець не висне вічно
      });
      if (res.ok) return true;                    // 2xx — доставлено
      if (res.status >= 400 && res.status < 500 && res.status !== 429) {
        return false;   // 4xx (крім 429) — НАША помилка, повтор не зарадить
      }
      // 5xx чи 429 — тимчасово; провалюємося у наступну ітерацію (повтор)
    } catch {
      // мережа впала / тайм-аут — теж тимчасово, повторюємо
    }
  }
  return false;                                   // спроби вичерпано
}
