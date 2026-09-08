/**
 * Типи даних, статуси та інтерфейси для сервісу Transactional Outbox.
 */

export type OutboxStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'DEAD_LETTER';

export interface OutboxMessage<T = unknown> {
  id: string;
  aggregateType: string;
  aggregateId: string;
  eventType: string;
  payload: T;
  idempotencyKey: string;
  attempts: number;
  maxAttempts: number;
  nextRetryAt: number;
  status: OutboxStatus;
  lastError?: string;
  createdAt: number;
  updatedAt: number;
  lockedBy?: string;
}

export interface WorkerConfig {
  workerId: string;
  batchSize: number;
  pollIntervalMs: number;
  baseDelayMs: number;
  maxDelayMs: number;
  defaultMaxAttempts: number;
}

export interface CreateOutboxParams<T = unknown> {
  aggregateType: string;
  aggregateId: string;
  eventType: string;
  payload: T;
  idempotencyKey?: string;
  maxAttempts?: number;
}

// ---------------- Доменні класи помилок ----------------

export class NonRetryableError extends Error {
  readonly statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = 'NonRetryableError';
    this.statusCode = statusCode;
  }
}

export class RetryableError extends Error {
  readonly statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = 'RetryableError';
    this.statusCode = statusCode;
  }
}
