// TypeScript / Node.js: Порівняння in-memory виклику та мережевого RPC клієнта
import { PerformanceObserver, performance } from 'perf_hooks';

interface DiscountRequest {
  userId: string;
  amountCents: number;
}

interface DiscountResponse {
  discountCents: number;
  promoCode: string;
}

// 1. У моноліті: прямий синхронний/асинхронний виклик модуля в пам'яті
export class InProcessDiscountModule {
  async calculateDiscount(req: DiscountRequest): Promise<DiscountResponse> {
    if (req.amountCents <= 0) {
      throw new Error('Invalid amount');
    }
    const discount = req.amountCents > 10000 ? Math.floor(req.amountCents * 0.1) : 0;
    return { discountCents: discount, promoCode: 'IN_PROC_TS' };
  }
}

// 2. У виділеному сервісі: HTTP/gRPC Клієнт з AbortController (таймаут) та Fallback
export class RemoteDiscountServiceClient {
  constructor(
    private readonly endpoint: string,
    private readonly timeoutMs: number = 200
  ) {}

  async calculateDiscount(req: DiscountRequest): Promise<DiscountResponse> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    try {
      // Імітація мережевого запиту (fetch / gRPC client) з таймаутом та серіалізацією JSON
      // Накладні витрати: серіалізація + TLS handshake/reuse + DNS lookup + RTT
      const response = await fetch(`${this.endpoint}/v1/discount`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`);
      }

      return (await response.json()) as DiscountResponse;
    } catch (err: any) {
      if (err.name === 'AbortError') {
        throw new Error('Service RPC Timeout');
      }
      throw err;
    } finally {
      clearTimeout(timer);
    }
  }
}
