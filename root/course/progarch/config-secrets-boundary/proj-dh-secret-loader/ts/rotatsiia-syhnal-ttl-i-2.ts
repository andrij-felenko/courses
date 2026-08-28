const cfg = await Config.load(manifest, store);

process.on("SIGHUP", () => { void cfg.reload(); });             // ротація за сигналом — БЕЗ релізу
setInterval(() => { void cfg.reload(); }, 5 * 60_000).unref();  // + TTL-перечит на всяк випадок

// ГАРЯЧИЙ шлях: знімок беруть ОДИН раз на одиницю роботи; поле-за-полем через await — НЕ читають.
async function handleReading(req: Reading): Promise<void> {
  const c = cfg.snapshot();                                     // цілісний знімок на весь запит
  await db.connect(c.dbHost as string, (c.dbPassword as Secret).expose());  // значення — лише тут
  // ...далі вся одиниця роботи бачить один узгоджений c
}
