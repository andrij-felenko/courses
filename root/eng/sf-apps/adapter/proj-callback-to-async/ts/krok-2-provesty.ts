import { readFile } from "node:fs";

function readFileAsync(
  path: string,
  opts: { signal?: AbortSignal; timeoutMs?: number } = {},
): Promise<Buffer> {
  const { signal, timeoutMs } = opts;
  return new Promise<Buffer>((resolve, reject) => {
    if (signal?.aborted) return reject(signal.reason);  // уже скасовано — навіть не починаємо

    let settled = false;

    const timer =
      timeoutMs != null
        ? setTimeout(() => finish(() => reject(new Error(`таймаут ${timeoutMs} мс`))), timeoutMs)
        : null;

    const onAbort = () => finish(() => reject(signal!.reason));
    signal?.addEventListener("abort", onAbort, { once: true });

    // ЄДИНА хвіртка виходу: перший результат виграє, решту глушимо, і ЗАВЖДИ прибираємо
    function finish(settle: () => void) {
      if (settled) return;                              // одноразовість — захист від подвійного виклику
      settled = true;
      if (timer) clearTimeout(timer);                   // прибрати таймер
      signal?.removeEventListener("abort", onAbort);    // зняти слухач — інакше витік
      settle();
    }

    readFile(path, (err, data) => {
      finish(() => (err ? reject(err) : resolve(data)));
    });
  });
}
