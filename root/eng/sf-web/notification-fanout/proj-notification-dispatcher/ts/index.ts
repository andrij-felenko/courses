import { EventEmitter } from "node:events";

export enum DeliveryStatus {
  Success = "SUCCESS",
  TokenExpired = "TOKEN_EXPIRED",     // 410 Gone / NotRegistered
  RateLimited = "RATE_LIMITED",       // 429 Too Many Requests
  InvalidPayload = "INVALID_PAYLOAD", // 400 Bad JSON
  NetworkError = "NETWORK_ERROR",
}

export interface DeviceNotification {
  deviceToken: string;
  title: string;
  body: string;
  payloadJson?: string;
}

export interface DeliveryResult {
  deviceToken: string;
  status: DeliveryStatus;
  errorMessage?: string;
}

export interface IPushProviderAdapter {
  sendBatch(batch: DeviceNotification[]): Promise<DeliveryResult[]>;
}

// Асинхронний обмежувач темпу (Token Bucket)
export class AsyncTokenBucket {
  private tokens: number;
  private lastRefill: number;

  constructor(
    private readonly ratePerSecond: number,
    private readonly capacity: number
  ) {
    this.tokens = capacity;
    this.lastRefill = Date.now();
  }

  async acquire(count = 1): Promise<void> {
    while (true) {
      this.refill();
      if (this.tokens >= count) {
        this.tokens -= count;
        return;
      }
      const waitMs = Math.ceil(((count - this.tokens) / this.ratePerSecond) * 1000);
      await new Promise((resolve) => setTimeout(resolve, Math.max(waitMs, 10)));
    }
  }

  private refill(): void {
    const now = Date.now();
    const elapsedSeconds = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsedSeconds * this.ratePerSecond);
    this.lastRefill = now;
  }
}

// Мок-адаптер з імітацією відповідей APNs / FCM
export class MockPushAdapter implements IPushProviderAdapter {
  async sendBatch(batch: DeviceNotification[]): Promise<DeliveryResult[]> {
    return batch.map((item) => {
      if (item.deviceToken.startsWith("invalid_")) {
        return {
          deviceToken: item.deviceToken,
          status: DeliveryStatus.TokenExpired,
          errorMessage: "410 Unregistered device token",
        };
      }
      if (item.deviceToken.startsWith("bad_")) {
        return {
          deviceToken: item.deviceToken,
          status: DeliveryStatus.InvalidPayload,
          errorMessage: "400 Malformed JSON structure",
        };
      }
      return {
        deviceToken: item.deviceToken,
        status: DeliveryStatus.Success,
      };
    });
  }
}

export class NotificationDispatcher extends EventEmitter {
  private readonly rateLimiter: AsyncTokenBucket;
  private readonly expiredTokensFeedback: string[] = [];
  private readonly deadLetterQueue: DeviceNotification[] = [];

  constructor(
    private readonly adapter: IPushProviderAdapter,
    maxRps: number,
    private readonly batchSize = 500
  ) {
    super();
    this.rateLimiter = new AsyncTokenBucket(maxRps, maxRps * 2);
  }

  async dispatchFanout(tokens: string[], title: string, body: string): Promise<void> {
    if (tokens.length === 0) return;

    // 1. Розбиття на батчі (Chunking)
    for (let i = 0; i < tokens.length; i += this.batchSize) {
      const chunkTokens = tokens.slice(i, i + this.batchSize);
      const batch: DeviceNotification[] = chunkTokens.map((token) => ({
        deviceToken: token,
        title,
        body,
      }));

      // 2. Контроль темпу
      await this.rateLimiter.acquire(batch.length);

      // 3. Відправка та обробка статусів
      const results = await this.adapter.sendBatch(batch);
      this.handleResults(results, batch);
    }
  }

  private handleResults(results: DeliveryResult[], originalBatch: DeviceNotification[]): void {
    const batchMap = new Map(originalBatch.map((item) => [item.deviceToken, item]));

    for (const res of results) {
      switch (res.status) {
        case DeliveryStatus.Success:
          break;
        case DeliveryStatus.TokenExpired:
          this.expiredTokensFeedback.push(res.deviceToken);
          this.emit("tokenExpired", res.deviceToken);
          break;
        case DeliveryStatus.InvalidPayload:
        case DeliveryStatus.RateLimited:
        case DeliveryStatus.NetworkError:
          const original = batchMap.get(res.deviceToken);
          if (original) {
            this.deadLetterQueue.push(original);
            this.emit("dlqItem", original, res.errorMessage);
          }
          break;
      }
    }
  }

  drainExpiredTokens(): string[] {
    return this.expiredTokensFeedback.splice(0, this.expiredTokensFeedback.length);
  }

  drainDeadLetterQueue(): DeviceNotification[] {
    return this.deadLetterQueue.splice(0, this.deadLetterQueue.length);
  }
}
