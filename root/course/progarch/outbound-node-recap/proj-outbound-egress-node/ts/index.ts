import { createHmac } from "node:crypto";

export interface OutboundMessage {
  id: string;
  destinationUrl: string;
  payloadJson: string;
  attempt: number;
  maxAttempts: number;
  secret: string;
}

export enum CircuitState { CLOSED, OPEN, HALF_OPEN }

export class CircuitBreaker {
  private state = CircuitState.CLOSED;
  private failureCount = 0;
  private nextAttemptTime = 0;

  constructor(private threshold = 3, private resetTimeoutMs = 10000) {}

  canExecute(now: number): boolean {
    if (this.state === CircuitState.OPEN) {
      if (now >= this.nextAttemptTime) {
        this.state = CircuitState.HALF_OPEN;
        return true;
      }
      return false;
    }
    return true;
  }

  onSuccess(): void {
    this.failureCount = 0;
    this.state = CircuitState.CLOSED;
  }

  onFailure(now: number): void {
    this.failureCount++;
    if (this.failureCount >= this.threshold) {
      this.state = CircuitState.OPEN;
      this.nextAttemptTime = now + this.resetTimeoutMs;
    }
  }

  getState(): CircuitState { return this.state; }
}

export class EgressGateway {
  private cb = new CircuitBreaker();

  async processMessage(
    msg: OutboundMessage,
    transport: (url: string, body: string, headers: Record<string, string>) => Promise<number>
  ): Promise<"SENT" | "RETRY" | "DLQ"> {
    const now = Date.now();
    if (!this.cb.canExecute(now)) {
      return "RETRY"; // Circuit Breaker відсікає виклики до впалого сервісу
    }

    const signature = createHmac("sha256", msg.secret)
      .update(`${now}.${msg.payloadJson}`)
      .digest("hex");

    const headers = {
      "Content-Type": "application/json",
      "X-Signature": `t=${now},v1=${signature}`,
      "X-Idempotency-Key": msg.id,
    };

    try {
      const statusCode = await transport(msg.destinationUrl, msg.payloadJson, headers);
      if (statusCode >= 200 && statusCode < 300) {
        this.cb.onSuccess();
        return "SENT";
      }
      if (statusCode >= 400 && statusCode < 500 && statusCode !== 429) {
        return "DLQ"; // Помилка конфігурації (4xx) — повтор не допоможе
      }
      this.cb.onFailure(Date.now());
    } catch (err) {
      this.cb.onFailure(Date.now());
    }

    if (msg.attempt + 1 >= msg.maxAttempts) {
      return "DLQ"; // Отруйне повідомлення вичерпало спроби
    }
    return "RETRY";
  }

  calculateBackoff(attempt: number, baseMs = 100, maxMs = 5000): number {
    const temp = Math.min(maxMs, baseMs * Math.pow(2, attempt));
    const jitter = temp * 0.5 * Math.random();
    return Math.floor(temp + jitter);
  }
}
