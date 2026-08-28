type Res = { status: number; body: unknown };
type Resolve = (dep: string) => Promise<string>;                          // реєстр виявлення
type Transport = (addr: string, path: string, body: unknown, s: AbortSignal) => Promise<Res>;

interface Limits { pool: number; queue: number; wait: number; timeout: number;
                   tries: number; failsToOpen: number; cooldown: number; }

class ServiceClient {
  private readonly bulkhead: Bulkhead;
  private readonly breaker: CircuitBreaker;
  constructor(
    private readonly dep: string,
    private readonly resolve: Resolve,
    private readonly transport: Transport,
    private readonly lim: Limits,
  ) {
    this.bulkhead = new Bulkhead(lim.pool, lim.queue, lim.wait);          // СВІЙ пул
    this.breaker  = new CircuitBreaker({ failsToOpen: lim.failsToOpen, cooldown: lim.cooldown }); // СВІЙ запобіжник
  }

  // Уся політика в ОДНОМУ стосі, ззовні всередину. Порядок — не косметика.
  call<T>(path: string, body: unknown): Promise<T> {
    return this.bulkhead.run(() =>                       // 1. слот із пулу цієї залежності / BulkheadFull
      this.breaker.call(() =>                            // 2. відкритий? → CircuitOpen, БЕЗ виклику
        withRetry(this.lim.tries, () =>                  // 3. повтор УСЕРЕДИНІ — відмови лічить запобіжник
          withTimeout(this.lim.timeout, (signal) =>      //   4. стеля на СПРОБУ + скасування
            this.send<T>(path, body, signal)))));        //     резолв адреси + HTTP
  }

  private async send<T>(path: string, body: unknown, signal: AbortSignal): Promise<T> {
    const addr = await this.resolve(this.dep);           // готовий екземпляр з реєстру
    const res = await this.transport(addr, path, body, signal);
    if (res.status >= 500) throw new Upstream5xx(res.status);   // минуще → повтор + лічба запобіжника
    if (res.status >= 400) throw new Upstream4xx(res.status);   // по суті → не повторюємо
    return res.body as T;
  }
}
