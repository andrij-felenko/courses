import { createHash } from "crypto";

export type CurrencyMicros = bigint; // 1 USD = 1_000_000n micros

export interface UsageEvent {
  eventId: string;
  idempotencyKey: string;
  tenantId: string;
  metricName: string;
  quantity: bigint;
  occurredAt: Date;
  properties?: Record<string, unknown>;
}

export enum IngestStatus {
  Accepted = "ACCEPTED",
  Duplicate = "DUPLICATE_IGNORED",
  Invalid = "INVALID_DATA",
}

export class EventIngestEngine {
  private seenKeys = new Set<string>();

  public ingestEvent(event: UsageEvent): IngestStatus {
    if (!event.tenantId || !event.metricName || event.quantity <= 0n) {
      return IngestStatus.Invalid;
    }

    if (this.seenKeys.has(event.idempotencyKey)) {
      return IngestStatus.Duplicate;
    }

    this.seenKeys.add(event.idempotencyKey);
    return IngestStatus.Accepted;
  }

  public static generateKey(tenantId: string, requestId: string, source: string): string {
    return createHash("sha256")
      .update(`${tenantId}:${requestId}:${source}`)
      .digest("hex");
  }
}
