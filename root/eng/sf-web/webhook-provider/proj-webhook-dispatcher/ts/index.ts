import crypto from "node:crypto";
import http from "node:http";
import https from "node:https";

export interface OutboxEvent {
  id: string;
  tenantId: string;
  destinationUrl: string;
  secretKey: string;
  eventType: string;
  payload: Record<string, unknown>;
  attempts: number;
  maxAttempts: number;
}

export interface DeliveryResult {
  statusCode?: number;
  durationMs: number;
  error?: string;
  body?: string;
}

// ── 1. Експоненційний відступ із повним джитером ────────────────────────────
export function calculateFullJitterBackoff(
  attempt: number,
  baseDelayMs = 1000,
  maxDelayMs = 3600000
): number {
  const maxCeiling = Math.min(maxDelayMs, baseDelayMs * Math.pow(2, attempt));
  return Math.floor(Math.random() * maxCeiling);
}

// ── 2. Криптографічний підпис HMAC-SHA256 ──────────────────────────────────
export function generateWebhookHeaders(
  event: OutboxEvent,
  rawPayload: string,
  timestamp = Math.floor(Date.now() / 1000)
): Record<string, string> {
  const signaturePayload = `t=${timestamp}.${rawPayload}`;
  const signature = crypto
    .createHmac("sha256", event.secretKey)
    .update(signaturePayload)
    .digest("hex");

  return {
    "Content-Type": "application/json",
    "User-Agent": "WebhookEngine/2.0 (+https://provider.example.com)",
    "X-Event-Id": event.id,
    "X-Event-Type": event.eventType,
    "X-Delivery-Attempt": String(event.attempts + 1),
    "X-Timestamp": String(timestamp),
    "X-Signature-256": `t=${timestamp},v1=${signature}`,
  };
}

// ── 3. Запобіжник (Circuit Breaker) для хостів ─────────────────────────────
export enum CircuitState {
  CLOSED,
  OPEN,
  HALF_OPEN,
}

export class HostCircuitBreaker {
  private state = CircuitState.CLOSED;
  private consecutiveFailures = 0;
  private lastStateChange = Date.now();
  private readonly failureThreshold: number;
  private readonly cooldownMs: number;

  constructor(failureThreshold = 5, cooldownMs = 60000) {
    this.failureThreshold = failureThreshold;
    this.cooldownMs = cooldownMs;
  }

  public canAttempt(): boolean {
    const now = Date.now();
    if (this.state === CircuitState.OPEN) {
      if (now - this.lastStateChange >= this.cooldownMs) {
        this.state = CircuitState.HALF_OPEN;
        this.lastStateChange = now;
        return true;
      }
      return false;
    }
    return true;
  }

  public recordSuccess(): void {
    this.consecutiveFailures = 0;
    this.state = CircuitState.CLOSED;
    this.lastStateChange = Date.now();
  }

  public recordFailure(): void {
    this.consecutiveFailures++;
    if (
      this.state === CircuitState.HALF_OPEN ||
      this.consecutiveFailures >= this.failureThreshold
    ) {
      this.state = CircuitState.OPEN;
      this.lastStateChange = Date.now();
    }
  }

  public getState(): CircuitState {
    return this.state;
  }
}

// ── 4. Диспетчер доставки та керування пулом ────────────────────────────────
export class WebhookDispatcher {
  private breakers = new Map<string, HostCircuitBreaker>();
  private httpAgent: http.Agent;
  private httpsAgent: https.Agent;

  constructor(maxSockets = 100) {
    this.httpAgent = new http.Agent({ keepAlive: true, maxSockets });
    this.httpsAgent = new https.Agent({ keepAlive: true, maxSockets });
  }

  private getHost(urlStr: string): string {
    try {
      return new URL(urlStr).hostname;
    } catch {
      return urlStr;
    }
  }

  private getBreaker(host: string): HostCircuitBreaker {
    let cb = this.breakers.get(host);
    if (!cb) {
      cb = new HostCircuitBreaker();
      this.breakers.set(host, cb);
    }
    return cb;
  }

  public async deliver(event: OutboxEvent, timeoutMs = 10000): Promise<DeliveryResult> {
    const host = this.getHost(event.destinationUrl);
    const breaker = this.getBreaker(host);

    if (!breaker.canAttempt()) {
      return {
        durationMs: 0,
        error: `CircuitBreaker: delivery paused for host ${host} (state: OPEN)`,
      };
    }

    const payloadStr = JSON.stringify(event.payload);
    const headers = generateWebhookHeaders(event, payloadStr);
    const startTime = Date.now();

    try {
      const url = new URL(event.destinationUrl);
      const isHttps = url.protocol === "https:";
      const agent = isHttps ? this.httpsAgent : this.httpAgent;

      const result = await new Promise<DeliveryResult>((resolve) => {
        const req = (isHttps ? https : http).request(
          url,
          {
            method: "POST",
            headers,
            agent,
            timeout: timeoutMs,
          },
          (res) => {
            let resBody = "";
            res.setEncoding("utf8");
            res.on("data", (chunk) => (resBody += chunk));
            res.on("end", () => {
              const durationMs = Date.now() - startTime;
              resolve({
                statusCode: res.statusCode,
                durationMs,
                body: resBody.slice(0, 1024),
              });
            });
          }
        );

        req.on("timeout", () => {
          req.destroy(new Error(`HTTP request timed out after ${timeoutMs}ms`));
        });

        req.on("error", (err) => {
          const durationMs = Date.now() - startTime;
          resolve({
            durationMs,
            error: err.message,
          });
        });

        req.write(payloadStr);
        req.end();
      });

      if (result.statusCode && result.statusCode >= 200 && result.statusCode < 300) {
        breaker.recordSuccess();
      } else if (
        !result.statusCode ||
        result.statusCode >= 500 ||
        result.statusCode === 429 ||
        result.statusCode === 408
      ) {
        breaker.recordFailure();
      }

      return result;
    } catch (err: any) {
      breaker.recordFailure();
      return {
        durationMs: Date.now() - startTime,
        error: err?.message ?? "Unknown network error",
      };
    }
  }

  public classifyOutcome(
    result: DeliveryResult,
    event: OutboxEvent
  ): { nextStatus: "delivered" | "failed" | "dead_letter"; retryDelayMs?: number } {
    if (result.statusCode && result.statusCode >= 200 && result.statusCode < 300) {
      return { nextStatus: "delivered" };
    }

    const isPermanentClientError =
      result.statusCode &&
      result.statusCode >= 400 &&
      result.statusCode < 500 &&
      result.statusCode !== 408 &&
      result.statusCode !== 429;

    const nextAttempt = event.attempts + 1;

    if (isPermanentClientError || nextAttempt >= event.maxAttempts) {
      return { nextStatus: "dead_letter" };
    }

    const retryDelayMs = calculateFullJitterBackoff(nextAttempt);
    return { nextStatus: "failed", retryDelayMs };
  }
}
