// Наївний повтор: до n спроб, поки помилка «варта повтору». Без бюджету, без змови.
async function retryNaive(fn: () => Promise<Res>, n: number): Promise<Res> {
  let r = await fn();
  for (let i = 1; i < n && !r.ok && r.retryable; i++) r = await fn();
  return r;
}

// Одна спроба до C, обгорнута лише таймаутом (стеля 300 мс).
const attemptC: Call = (ctx) => withTimeout(rawCallC, 300)(ctx);

// A повторює B (×3), B повторює C (×3), C-клієнт повторює спробу (×3).
const naiveChain: Call = (ctx) =>
  retryNaive(() =>                         // A→B  ×3
    retryNaive(() =>                       //   B→C  ×3
      retryNaive(() => attemptC(ctx),      //     C-клієнт  ×3
      3), 3), 3);
