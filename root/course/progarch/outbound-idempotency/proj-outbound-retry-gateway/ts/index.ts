// TypeScript: Асинхронний вихідний шлюз з fetch та AbortController
interface ChargeResult {
  id: string;
  status: string;
}

export class OutboundIdempotentClient {
  constructor(private readonly baseUrl: string) {}

  async postWithIdempotency<T>(
    path: string,
    idempotencyKey: string,
    body: Record<string, unknown>,
    maxRetries = 3
  ): Promise<T> {
    let backoffMs = 500;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      try {
        const response = await fetch(`${this.baseUrl}${path}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Idempotency-Key": idempotencyKey,
          },
          body: JSON.stringify(body),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (response.ok) {
          return (await response.json()) as T;
        }

        if (response.status === 409 || response.status >= 500) {
          console.warn(`[RETRY TS] HTTP ${response.status}. Retrying in ${backoffMs}ms...`);
          await new Promise((resolve) => setTimeout(resolve, backoffMs));
          backoffMs *= 2;
          continue;
        }

        throw new Error(`Non-retriable error HTTP ${response.status}`);
      } catch (err: unknown) {
        clearTimeout(timeoutId);
        console.warn(`[NETWORK_ERROR TS] Attempt ${attempt} failed:`, err);
        if (attempt === maxRetries) throw err;
        await new Promise((resolve) => setTimeout(resolve, backoffMs));
        backoffMs *= 2;
      }
    }

    throw new Error("Max retries exceeded");
  }
}
