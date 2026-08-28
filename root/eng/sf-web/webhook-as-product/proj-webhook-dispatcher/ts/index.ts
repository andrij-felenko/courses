import crypto from "node:crypto";
import http from "node:http";
import https from "node:https";
import { performance } from "node:perf_hooks";

// ── 1. Типи даних та інтерфейси ─────────────────────────────────────────────

export type ApiVersion = "2026-03-01" | "2024-11-15" | "2022-08-01";

export interface CanonicalEvent {
  id: string;
  type: string;
  created: number; // Unix timestamp у секундах UTC
  apiVersion: ApiVersion; // Завжди найсвіжіша версія ядра
  data: Record<string, unknown>;
  livemode: boolean;
}

export interface EndpointSubscription {
  id: string;
  url: string;
  pinnedVersion: ApiVersion;
  primarySecret: string;
  secondarySecret?: string; // Активний під час 24-годинного вікна ротації
  consecutiveFailures: number;
  status: "healthy" | "degraded" | "disabled";
  disabledAt?: number;
}

export interface DeliveryAttemptLog {
  deliveryId: string;
  eventId: string;
  endpointId: string;
  url: string;
  attemptNumber: number;
  httpStatus?: number;
  errorCode?: string;
  durationMs: number;
  requestHeaders: Record<string, string>;
  requestPayload: string;
  responseHeaders?: Record<string, string>;
  responseBodySnippet?: string;
  timestamp: number;
}

// ── 2. Двигун трансформації схем (Version Pinning) ─────────────────────────

type SchemaTransformer = (payload: Record<string, unknown>) => Record<string, unknown>;

// Реєстр спадних трансформаторів: версія N -> версія N-1
const VERSION_TRANSFORMERS: Record<string, SchemaTransformer> = {
  "2026-03-01->2024-11-15": (data) => {
    const cloned = JSON.parse(JSON.stringify(data));
    // У версії 2026-03 ціна стала об'єктом pricing: { amountDecimal: 50.00, currency: "usd" }
    // У версії 2024-11 це було плоске цілочисельне поле amount_cents = 5000
    if (cloned.pricing && typeof cloned.pricing === "object") {
      const p = cloned.pricing as { amountDecimal?: number; currency?: string };
      cloned.amount = Math.round((p.amountDecimal ?? 0) * 100);
      cloned.currency = p.currency;
      delete cloned.pricing;
    }
    return cloned;
  },
  "2024-11-15->2022-08-01": (data) => {
    const cloned = JSON.parse(JSON.stringify(data));
    // У версії 2024-11 адреса була вкладеною { shipping: { address_line: "..." } }
    // У версії 2022-08 адреса була плоским рядком shipping_address
    if (cloned.shipping && typeof cloned.shipping === "object") {
      const s = cloned.shipping as { address_line?: string };
      cloned.shipping_address = s.address_line ?? "";
      delete cloned.shipping;
    }
    // Перейменування поля amount -> amount_cents
    if ("amount" in cloned) {
      cloned.amount_cents = cloned.amount;
      delete cloned.amount;
    }
    return cloned;
  },
};

const ORDERED_VERSIONS: ApiVersion[] = ["2026-03-01", "2024-11-15", "2022-08-01"];

export function transformEventToPinnedVersion(
  event: CanonicalEvent,
  targetVersion: ApiVersion
): Record<string, unknown> {
  const srcIdx = ORDERED_VERSIONS.indexOf(event.apiVersion);
  const dstIdx = ORDERED_VERSIONS.indexOf(targetVersion);

  if (srcIdx === -1 || dstIdx === -1 || srcIdx > dstIdx) {
    throw new Error(`Неможливо трансформувати версію ${event.apiVersion} до ${targetVersion}`);
  }

  let transformedData = JSON.parse(JSON.stringify(event.data));

  // Послідовне проходження крізь сходинки міграцій
  for (let i = srcIdx; i < dstIdx; i++) {
    const stepKey = `${ORDERED_VERSIONS[i]}->${ORDERED_VERSIONS[i + 1]}`;
    const transformer = VERSION_TRANSFORMERS[stepKey];
    if (transformer) {
      transformedData = transformer(transformedData);
    }
  }

  return {
    id: event.id,
    object: "event",
    api_version: targetVersion,
    created: event.created,
    type: event.type,
    livemode: event.livemode,
    data: {
      object: transformedData,
    },
  };
}

// ── 3. Генератор двопідписного HMAC заголовка ───────────────────────────────

export function generateWebhookSignatureHeader(
  rawPayload: string,
  timestamp: number,
  primarySecret: string,
  secondarySecret?: string
): string {
  const signedPayload = `${timestamp}.${rawPayload}`;

  const primaryHmac = crypto
    .createHmac("sha256", primarySecret)
    .update(signedPayload, "utf8")
    .digest("hex");

  let header = `t=${timestamp},v1=${primaryHmac}`;

  // Якщо активне вікно ротації — додаємо другий v1 підпис
  if (secondarySecret) {
    const secondaryHmac = crypto
      .createHmac("sha256", secondarySecret)
      .update(signedPayload, "utf8")
      .digest("hex");
    header += `,v1=${secondaryHmac}`;
  }

  return header;
}

// ── 4. Виконавець HTTP-доставки з телеметрією ────────────────────────────────

export async function executeDeliveryAttempt(
  endpoint: EndpointSubscription,
  event: CanonicalEvent,
  attemptNumber: number
): Promise<DeliveryAttemptLog> {
  const deliveryId = `deliv_${crypto.randomBytes(12).toString("hex")}`;
  const now = Math.floor(Date.now() / 1000);

  // 1. Трансформація схеми під версію ендпоінта
  const finalPayloadObj = transformEventToPinnedVersion(event, endpoint.pinnedVersion);
  const rawPayload = JSON.stringify(finalPayloadObj);

  // 2. Розрахунок підписів (з підтримкою двоетапної ротації)
  const signatureHeader = generateWebhookSignatureHeader(
    rawPayload,
    now,
    endpoint.primarySecret,
    endpoint.secondarySecret
  );

  const headers: Record<string, string> = {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(rawPayload, "utf8").toString(),
    "User-Agent": "Platform-WebhookDispatcher/2.0",
    "Webhook-Id": event.id,
    "Webhook-Delivery": deliveryId,
    "Webhook-Signature": signatureHeader,
  };

  const startTime = performance.now();

  return new Promise((resolve) => {
    const urlObj = new URL(endpoint.url);
    const isHttps = urlObj.protocol === "https:";
    const transport = isHttps ? https : http;

    const req = transport.request(
      endpoint.url,
      {
        method: "POST",
        headers,
        timeout: 5000, // Суворий таймаут 5 секунд
      },
      (res) => {
        const responseChunks: Buffer[] = [];
        let totalBytes = 0;
        const MAX_LOG_BYTES = 4096; // Зберігаємо щонайбільше 4 КБ тіла для аудиту

        res.on("data", (chunk: Buffer) => {
          if (totalBytes < MAX_LOG_BYTES) {
            responseChunks.push(chunk);
          }
          totalBytes += chunk.length;
        });

        res.on("end", () => {
          const durationMs = Math.round(performance.now() - startTime);
          const fullBodyBuffer = Buffer.concat(responseChunks);
          const snippet = fullBodyBuffer.slice(0, MAX_LOG_BYTES).toString("utf8");

          const resHeaders: Record<string, string> = {};
          for (const [k, v] of Object.entries(res.headers)) {
            if (v) resHeaders[k] = Array.isArray(v) ? v.join(", ") : v;
          }

          resolve({
            deliveryId,
            eventId: event.id,
            endpointId: endpoint.id,
            url: endpoint.url,
            attemptNumber,
            httpStatus: res.statusCode,
            durationMs,
            requestHeaders: headers,
            requestPayload: rawPayload,
            responseHeaders: resHeaders,
            responseBodySnippet: snippet,
            timestamp: Date.now(),
          });
        });
      }
    );

    req.on("timeout", () => {
      req.destroy(new Error("ETIMEDOUT"));
    });

    req.on("error", (err: NodeJS.ErrnoException) => {
      const durationMs = Math.round(performance.now() - startTime);
      resolve({
        deliveryId,
        eventId: event.id,
        endpointId: endpoint.id,
        url: endpoint.url,
        attemptNumber,
        errorCode: err.code || "REQUEST_FAILED",
        durationMs,
        requestHeaders: headers,
        requestPayload: rawPayload,
        timestamp: Date.now(),
      });
    });

    req.write(rawPayload);
    req.end();
  });
}

// ── 5. Автомат станів кінцевої точки (Circuit Breaker) ───────────────────────

export function updateEndpointCircuitBreaker(
  endpoint: EndpointSubscription,
  attempt: DeliveryAttemptLog
): void {
  const isSuccess = attempt.httpStatus !== undefined && attempt.httpStatus >= 200 && attempt.httpStatus < 300;

  if (isSuccess) {
    endpoint.consecutiveFailures = 0;
    endpoint.status = "healthy";
    return;
  }

  endpoint.consecutiveFailures += 1;

  // Незворотні коди помилок вимикають ендпоінт швидше
  const isFatalStatus = attempt.httpStatus === 410 || attempt.httpStatus === 404;

  if (isFatalStatus || endpoint.consecutiveFailures >= 50) {
    endpoint.status = "disabled";
    endpoint.disabledAt = Date.now();
  } else if (endpoint.consecutiveFailures >= 5) {
    endpoint.status = "degraded";
  }
}
