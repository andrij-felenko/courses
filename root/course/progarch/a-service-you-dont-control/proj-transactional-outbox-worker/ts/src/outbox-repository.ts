import type { OutboxMessage, CreateOutboxParams } from './types.ts';
import crypto from 'node:crypto';

/**
 * Репозиторій таблиці Outbox з підтримкою конкурентної вибірки SKIP LOCKED.
 * Імітує поведінку PostgreSQL:
 * SELECT * FROM outbox WHERE status = 'PENDING' AND next_retry_at <= NOW()
 * ORDER BY next_retry_at ASC FOR UPDATE SKIP LOCKED LIMIT $1;
 */
export class OutboxRepository {
  // Пам'ять таблиці аутбоксу
  private readonly messages = new Map<string, OutboxMessage>();
  // Множина заблокованих записів у транзакціях воркерів
  private readonly lockedIds = new Set<string>();

  /**
   * Атомарно зберігає намір відправки повідомлення в тій самій транзакції, що й бізнес-сутність.
   */
  async saveWithinTransaction<T>(params: CreateOutboxParams<T>): Promise<OutboxMessage<T>> {
    const id = crypto.randomUUID();
    const now = Date.now();
    const idempotencyKey = params.idempotencyKey || `idem-${id}`;

    const record: OutboxMessage<T> = {
      id,
      aggregateType: params.aggregateType,
      aggregateId: params.aggregateId,
      eventType: params.eventType,
      payload: params.payload,
      idempotencyKey,
      attempts: 0,
      maxAttempts: params.maxAttempts ?? 3,
      nextRetryAt: now,
      status: 'PENDING',
      createdAt: now,
      updatedAt: now,
    };

    this.messages.set(id, record as OutboxMessage);
    return record;
  }

  /**
   * Конкурентна вибірка готових задач через семантику SKIP LOCKED.
   * Пропускає записи, що вже обробляються іншими воркерами.
   */
  async fetchBatchSkipLocked(limit: number, workerId: string): Promise<OutboxMessage[]> {
    const now = Date.now();
    const batch: OutboxMessage[] = [];

    // Емуляція індексного пошуку: status = 'PENDING' AND next_retry_at <= NOW()
    for (const record of this.messages.values()) {
      if (batch.length >= limit) break;

      if (
        record.status === 'PENDING' &&
        record.nextRetryAt <= now &&
        !this.lockedIds.has(record.id)
      ) {
        // Блокуємо рядок (FOR UPDATE SKIP LOCKED)
        this.lockedIds.add(record.id);
        record.status = 'PROCESSING';
        record.lockedBy = workerId;
        record.updatedAt = now;
        batch.push({ ...record });
      }
    }

    return batch;
  }

  /**
   * Фіксація успішної доставки повідомлення до зовнішнього сервісу.
   */
  async markCompleted(id: string): Promise<void> {
    const record = this.messages.get(id);
    if (record) {
      record.status = 'COMPLETED';
      record.updatedAt = Date.now();
      record.lockedBy = undefined;
    }
    this.lockedIds.delete(id);
  }

  /**
   * Планування повторної спроби при тимчасовому збої.
   */
  async scheduleRetry(
    id: string,
    attempts: number,
    nextRetryAt: number,
    error: string
  ): Promise<void> {
    const record = this.messages.get(id);
    if (record) {
      record.status = 'PENDING';
      record.attempts = attempts;
      record.nextRetryAt = nextRetryAt;
      record.lastError = error;
      record.updatedAt = Date.now();
      record.lockedBy = undefined;
    }
    this.lockedIds.delete(id);
  }

  /**
   * Ізоляція отруйного або безнадійного повідомлення в Dead Letter Queue (DLQ).
   */
  async moveToDeadLetter(id: string, reason: string): Promise<void> {
    const record = this.messages.get(id);
    if (record) {
      record.status = 'DEAD_LETTER';
      record.lastError = reason;
      record.updatedAt = Date.now();
      record.lockedBy = undefined;
    }
    this.lockedIds.delete(id);
  }

  getAll(): OutboxMessage[] {
    return Array.from(this.messages.values());
  }

  getMetrics() {
    let pending = 0;
    let processing = 0;
    let completed = 0;
    let deadLetter = 0;

    for (const r of this.messages.values()) {
      if (r.status === 'PENDING') pending++;
      else if (r.status === 'PROCESSING') processing++;
      else if (r.status === 'COMPLETED') completed++;
      else if (r.status === 'DEAD_LETTER') deadLetter++;
    }

    return { total: this.messages.size, pending, processing, completed, deadLetter };
  }
}
