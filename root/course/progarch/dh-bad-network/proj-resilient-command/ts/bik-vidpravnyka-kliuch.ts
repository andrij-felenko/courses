type Command = { type: string; [k: string]: unknown };
type Result  = { ok: boolean; [k: string]: unknown };

class RetryableError extends Error {}   // мережа, таймаут, 5xx, 429 — «не знаю», варте повтору
class TerminalError  extends Error {}   // 4xx — команда негодяща, повтор не врятує

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Одна спроба зі СВОЄЮ стелею. Ключ їде заголовком Idempotency-Key.
async function post(url: string, cmd: Command, key: string, timeoutMs: number): Promise<Result> {
  const ctl = new AbortController();
  const timer = setTimeout(() => ctl.abort(), timeoutMs);   // стеля саме цієї спроби
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/json", "Idempotency-Key": key },
      body: JSON.stringify(cmd),
      signal: ctl.signal,
    });
    if (res.status >= 500 || res.status === 429) throw new RetryableError(`${res.status}`); // мине
    if (res.status >= 400) throw new TerminalError(`${res.status}`);                          // вирок
    return (await res.json()) as Result;
  } catch (e) {
    if (e instanceof TerminalError) throw e;
    throw new RetryableError(String(e)); // AbortError (таймаут) і падіння fetch — усе це «не знаю»
  } finally {
    clearTimeout(timer);
  }
}

async function sendCommand(url: string, cmd: Command): Promise<Result> {
  const key = crypto.randomUUID();               // ОДИН ключ на команду — крізь усі спроби
  const deadline = performance.now() + 10_000;   // весь бюджет 10 с, МОНОТОННИЙ годинник
  let backoff = 500;
  for (;;) {
    const left = deadline - performance.now();
    if (left <= 0) throw new RetryableError("бюджет вичерпано — чесне «не знаю»");
    try {
      return await post(url, cmd, key, Math.min(left, 3_000)); // стеля спроби ≤ залишку бюджету
    } catch (e) {
      if (e instanceof TerminalError) throw e;   // 4xx — повторювати нема сенсу
      const pause = Math.min(backoff + Math.random() * backoff, deadline - performance.now());
      if (pause <= 0) throw new RetryableError("бюджет вичерпано перед повтором");
      await sleep(pause);                        // відступ + розкид
      backoff *= 2;                              // 0.5 → 1 → 2 → 4 с
    }
  }
}
