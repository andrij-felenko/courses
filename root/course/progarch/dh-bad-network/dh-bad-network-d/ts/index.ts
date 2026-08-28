async function sendCommand(cmd: Command): Promise<Result> {
  const key = uuid();                        // ОДИН ключ на команду — крізь усі спроби
  const deadline = now() + 10_000;           // весь бюджет — 10 с, монотонний годинник
  let backoff = 500;
  while (true) {
    const left = deadline - now();
    if (left <= 0) throw new Timeout("бюджет вичерпано");   // чесне «не знаю»
    try {
      return await post("/hub/command", cmd, key, Math.min(left, 3_000));
    } catch (e) {
      if (!isRetryable(e)) throw e;          // 4xx — не мережа, повторювати нема сенсу
      const pause = Math.min(backoff + Math.random() * backoff, left);
      await sleep(pause);                    // відступ + розкид
      backoff *= 2;                          // 0.5 → 1 → 2 → 4 с
    }
  }
}
