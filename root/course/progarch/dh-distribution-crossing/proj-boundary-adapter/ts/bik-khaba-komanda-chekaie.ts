class NetworkCloud implements CloudLink {
  private buf: Report[] = [];
  private wake?: () => void;
  constructor(private wire: Wire) {}

  // КОМАНДА: бюджет часу + повтор із джитером; ключ СТАЛИЙ крізь спроби.
  async send(cmd: Command): Promise<Result> {
    const deadline = performance.now() + 10_000; // монотонний бюджет, НЕ Date.now()
    for (let attempt = 0; ; attempt++) {
      const left = deadline - performance.now();
      if (left <= 0) throw new Unreachable();               // бюджет вичерпано
      const ac = new AbortController();
      const timer = setTimeout(() => ac.abort(), left);     // таймаут спроби = залишок бюджету
      try {
        return await this.wire.postCmd(cmd, ac.signal);     // той самий cmd.key щоразу
      } catch (e) {
        if (!(e instanceof Unreachable)) throw e;           // не мережа — не повторюємо
        const wait = Math.random() * Math.min(3000, 100 * 2 ** attempt); // повний джитер
        if (performance.now() + wait > deadline) throw new Unreachable();
        await sleep(wait);
      } finally {
        clearTimeout(timer);
      }
    }
  }

  // ЗВІТ (гарячий шлях): у буфер і НЕГАЙНО назад — мережі не торкаємось.
  emit(rep: Report): void {
    this.buf.push(rep);
    this.wake?.();            // штовхнути флашер, якщо він дрімає
    this.wake = undefined;
  }

  // Фоновий флашер: доки хмара мовчить — тримає; ожила — досилає по черзі.
  async flushLoop(signal: AbortSignal): Promise<void> {
    while (!signal.aborted) {
      await this.drain();
      await new Promise<void>((res) => {                    // чекати сигналу АБО 500 мс
        this.wake = res;
        const t = setTimeout(res, 500);
        signal.addEventListener("abort", () => { clearTimeout(t); res(); }, { once: true });
      });
    }
  }

  private async drain(): Promise<void> {
    while (this.buf.length > 0) {
      const head = this.buf[0];                             // не знімаємо, поки не підтверджено
      const ac = new AbortController();
      const timer = setTimeout(() => ac.abort(), 2000);
      try {
        await this.wire.postReport(head, ac.signal);
      } catch {
        return;                                             // хмара мовчить/ACK не дійшов — лишаємо
      } finally {
        clearTimeout(timer);
      }
      this.buf.shift();                                     // ACK отримано — АЖ ТЕПЕР знімаємо голову
    }
  }

  pending(): number { return this.buf.length; }
  readState(dev: string): Promise<string> { return this.wire.getState(dev, AbortSignal.timeout(2000)); }
}
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
