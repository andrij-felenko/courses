// Перебірка = семафор: ≤ limit одночасних; при переповненні або миттєва
// відмова (fail-fast, maxQueue = 0), або коротке очікування в обмеженій черзі.
class BulkheadFull extends Error { readonly retryable = false; }

class Bulkhead {
  private inFlight = 0;
  private readonly q: Array<{ ok: () => void; timer: ReturnType<typeof setTimeout> }> = [];

  constructor(
    private readonly limit: number,
    private readonly maxQueue = 0,     // 0 → fail-fast
    private readonly maxWait = 0,      // стеля очікування в черзі, мс
  ) {}

  async run<T>(fn: () => Promise<T>): Promise<T> {
    await this.acquire();
    try { return await fn(); }
    finally { this.release(); }
  }

  private acquire(): Promise<void> {
    if (this.inFlight < this.limit) { this.inFlight++; return Promise.resolve(); }
    if (this.q.length >= this.maxQueue) return Promise.reject(new BulkheadFull());
    return new Promise<void>((resolve, reject) => {          // паркуємось у черзі — але не назавжди
      const timer = setTimeout(() => {
        const i = this.q.findIndex((w) => w.timer === timer);
        if (i >= 0) { this.q.splice(i, 1); reject(new BulkheadFull()); }
      }, this.maxWait);
      this.q.push({ ok: resolve, timer });
    });
  }

  private release(): void {
    const w = this.q.shift();
    if (w) { clearTimeout(w.timer); w.ok(); }   // слот ПЕРЕХОДИТЬ наступному — лічильник не чіпаємо
    else this.inFlight--;                        // охочих нема — звільняємо слот
  }
}
