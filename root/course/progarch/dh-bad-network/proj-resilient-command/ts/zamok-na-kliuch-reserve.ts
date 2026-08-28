type Entry = { result: Result; storedAt: number };

class IdempotentExecutor {
  private done     = new Map<string, Entry>();          // завершені: ключ → результат + час
  private inflight = new Map<string, Promise<Result>>(); // саме в роботі: ключ → її проміс

  constructor(
    private execute: (c: Command) => Promise<Result>,
    private ttlMs = 24 * 3_600_000,                     // Stripe теж радить ~24 год (нижче — чому)
    private now: () => number = () => Date.now(),
  ) {}

  async handle(key: string, cmd: Command): Promise<Result> {
    // 1. Уже завершене й ще свіже → віддати збережене, НЕ виконувати.
    const seen = this.done.get(key);
    if (seen && this.now() - seen.storedAt < this.ttlMs) return seen.result;

    // 2. Той самий ключ уже в роботі → приєднатися до ЙОГО промісу, не запускати другий execute.
    const running = this.inflight.get(key);
    if (running) return running;

    // 3. Ми перші. Критична секція БЕЗ await: створюємо проміс і реєструємо його
    //    синхронно — конкурент із кроку 2 неодмінно застане його на місці.
    const p = (async () => {
      try {
        const result = await this.execute(cmd);            // ЄДИНЕ справжнє виконання
        this.done.set(key, { result, storedAt: this.now() });
        return result;
      } finally {
        this.inflight.delete(key);                         // прибрати з «у роботі» будь-як
      }
    })();
    this.inflight.set(key, p);                             // ← ДО будь-якого await у handle
    return p;
  }
}
