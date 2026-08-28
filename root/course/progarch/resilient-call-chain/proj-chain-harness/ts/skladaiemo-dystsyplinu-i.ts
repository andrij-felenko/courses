const MIN_WORK = 25;

function makeDisciplined(): Call {
  const budget = new Budget(0.10);
  // C-клієнт: таймаут ВСЕРЕДИНІ запобіжника. БЕЗ повтору.
  const cClient = withBreaker(withTimeout(rawCallC, 300), { failsToOpen: 5, cooldown: 200 });
  // B: трохи власної роботи й ОДИН виклик до C. Відмову віддає вгору.
  const bHop: Call = async (ctx) => {
    if (ctx.deadline - ctx.now < MIN_WORK) return doomed();
    ctx.now += 5;
    return cClient(ctx);
  };
  // A: ПОВТОР ЛИШЕ ТУТ — під бюджетом і поки є час.
  const aRetry = withRetry(bHop, { tries: 3, minWork: MIN_WORK }, budget);
  return async (ctx) => { ctx.now += 5; return aRetry(ctx); };
}

// Драйвер: жене n запитів, вмикає «інцидент» на середину прогону, рахує p99.
async function benchmark(chain: Call, n: number): Promise<{ cCalls: number; p99: number }> {
  cCalls = 0; seed = 1;                                     // однакові умови «до» і «після»
  const lat: number[] = [];
  for (let i = 0; i < n; i++) {
    sick = i >= n * 0.3 && i < n * 0.6;                     // 30% прогону — C хворіє
    const ctx: Ctx = { now: 0, deadline: 1000 };
    await chain(ctx);
    lat.push(ctx.now);                                      // наскрізна затримка = витрачений час
  }
  lat.sort((a, b) => a - b);
  return { cCalls, p99: lat[Math.ceil(0.99 * n) - 1] };
}

await runStorm();
console.log("наївно:     ", await benchmark(naiveChain, 10_000));
console.log("дисципліна: ", await benchmark(makeDisciplined(), 10_000));
