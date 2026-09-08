import type { OutboxMessage, WorkerConfig } from './types.ts';
import { NonRetryableError, RetryableError } from './types.ts';
import { OutboxRepository } from './outbox-repository.ts';
import { IdempotentHttpClient } from './http-client.ts';
import { calculateFullJitter, sleep } from './backoff.ts';

/**
 * Фоновий воркер для опитування аутбоксу та відправки повідомлень.
 * Забезпечує паралельну обробку через SKIP LOCKED, розрахунок ретраїв Full Jitter
 * та своєчасну ізоляцію відмов у Dead Letter Queue.
 */
export class OutboxWorker {
  private readonly config: WorkerConfig;
  private readonly repository: OutboxRepository;
  private readonly httpClient: IdempotentHttpClient;
  private readonly targetUrl: string;
  private isRunning = false;
  private currentLoopPromise: Promise<void> | null = null;
  private abortController: AbortController | null = null;

  constructor(
    config: WorkerConfig,
    repository: OutboxRepository,
    httpClient: IdempotentHttpClient,
    targetUrl: string
  ) {
    this.config = config;
    this.repository = repository;
    this.httpClient = httpClient;
    this.targetUrl = targetUrl;
  }

  start(): void {
    if (this.isRunning) return;
    this.isRunning = true;
    this.abortController = new AbortController();
    this.currentLoopPromise = this.pollLoop(this.abortController.signal);
  }

  async stop(): Promise<void> {
    if (!this.isRunning) return;
    this.isRunning = false;
    this.abortController?.abort();
    if (this.currentLoopPromise) {
      await this.currentLoopPromise.catch(() => {});
    }
  }

  private async pollLoop(signal: AbortSignal): Promise<void> {
    while (this.isRunning && !signal.aborted) {
      try {
        const batch = await this.repository.fetchBatchSkipLocked(
          this.config.batchSize,
          this.config.workerId
        );

        if (batch.length === 0) {
          await sleep(this.config.pollIntervalMs, signal);
          continue;
        }

        // Паралельна обробка повідомлень у вибірці
        await Promise.allSettled(batch.map((msg) => this.processMessage(msg)));
      } catch (err) {
        if (signal.aborted) break;
        await sleep(this.config.pollIntervalMs, signal);
      }
    }
  }

  private async processMessage(msg: OutboxMessage): Promise<void> {
    try {
      await this.httpClient.post(this.targetUrl, msg.payload, msg.idempotencyKey);

      await this.repository.markCompleted(msg.id);
      console.log(`[${this.config.workerId}] ✓ Успішно доставлено: ${msg.aggregateId} (${msg.eventType})`);
    } catch (err) {
      if (err instanceof NonRetryableError) {
        // Фатальна помилка клієнта 4xx: повтор безглуздий, переносимо одразу в DLQ
        await this.repository.moveToDeadLetter(msg.id, `Клієнтський збій: ${err.message}`);
        console.log(`[${this.config.workerId}] ⛔ [DLQ] Фатальна помилка 4xx для ${msg.aggregateId}: ${err.message}`);
        return;
      }

      // Тимчасовий збій (5xx або мережевий таймаут)
      const nextAttempt = msg.attempts + 1;

      if (nextAttempt >= msg.maxAttempts) {
        // Вичерпано встановлений ліміт повторних спроб
        const reason = `Вичерпано спроби (${nextAttempt}/${msg.maxAttempts}): ${(err as Error).message}`;
        await this.repository.moveToDeadLetter(msg.id, reason);
        console.log(`[${this.config.workerId}] ⛔ [DLQ] Вичерпано спроби для ${msg.aggregateId}: ${reason}`);
      } else {
        // Розраховуємо експоненційний відступ з випадковим тремтінням
        const delayMs = calculateFullJitter(
          nextAttempt,
          this.config.baseDelayMs,
          this.config.maxDelayMs
        );
        const nextRetryAt = Date.now() + delayMs;

        await this.repository.scheduleRetry(msg.id, nextAttempt, nextRetryAt, (err as Error).message);
        console.log(`[${this.config.workerId}] ↻ [RETRY] Тимчасовий збій для ${msg.aggregateId}. Спроба ${nextAttempt}/${msg.maxAttempts}, відступ ${delayMs} мс`);
      }
    }
  }
}
