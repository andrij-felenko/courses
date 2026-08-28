// ТАЙМАУТ: спрацьовує на витраченому ЧАСІ, байдуже, ok спроба чи ні.
function withTimeout(inner: Call, limit: number): Call {
  return async (ctx) => {
    const r = await inner(ctx);
    if (r.latency > limit) {
      ctx.now += limit;                                    // прочекали рівно стелю
      return { ok: false, kind: "timeout", retryable: true, latency: limit };
    }
    ctx.now += r.latency;                                  // встигли — платимо реальну ціну
    return r;
  };
}

// ЗАПОБІЖНИК: автомат closed → open → half. Стан живе в замиканні.
type BState = "closed" | "open" | "half";
function withBreaker(inner: Call, o: { failsToOpen: number; cooldown: number }): Call {
  let state: BState = "closed", fails = 0, openedAt = 0;
  return async (ctx) => {
    if (state === "open") {
      if (ctx.now - openedAt < o.cooldown)                 // ще кулдаун — КОРОТИМО
        return { ok: false, kind: "circuit-open", retryable: false, latency: 0 };
      state = "half";                                      // час на одну пробу
    }
    const r = await inner(ctx);                            // (це withTimeout(rawCallC))
    if (r.ok) { state = "closed"; fails = 0; return r; }   // одужав
    fails++;
    if (state === "half" || fails >= o.failsToOpen) {      // проба впала / досить невдач
      state = "open"; openedAt = ctx.now; fails = 0;
    }
    return r;
  };
}

// ПОВТОР ПІД БЮДЖЕТОМ, свідомий дедлайну й сигналу «не повторюй».
class Budget {
  private calls = 0; private retries = 0;
  constructor(private ratio = 0.10) {}
  allow(): boolean { return this.retries < this.ratio * this.calls; } // ≤10% трафіку
  record(isRetry: boolean) { this.calls++; if (isRetry) this.retries++; }
}
const doomed = (): Res => ({ ok: false, kind: "deadline", retryable: false, latency: 0 });

function withRetry(inner: Call, o: { tries: number; minWork: number }, b: Budget): Call {
  return async (ctx) => {
    if (ctx.deadline - ctx.now < o.minWork) return doomed();   // приречена робота
    let r = await inner(ctx); b.record(false);
    let attempt = 1;
    while (!r.ok && r.retryable && attempt < o.tries          // помилка ВАРТА повтору
           && ctx.deadline - ctx.now >= o.minWork             // ще є час
           && b.allow()) {                                    // бюджет дозволяє
      b.record(true); r = await inner(ctx); attempt++;
    }
    return r;
  };
}
