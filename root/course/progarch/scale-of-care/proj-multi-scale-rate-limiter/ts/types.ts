/**
 * Результат оцінки ліміту запиту на периферійному вузлі.
 */
export interface RateLimitDecision {
  readonly allowed: boolean;
  readonly remaining: number;
  readonly limit: number;
  readonly resetInMs: number;
  readonly source: 'local-lease' | 'fallback';
  readonly reason: string;
}

/**
 * Конфігурація периферійного обмежувача частоти.
 */
export interface RateLimitConfig {
  readonly limit: number;          // Максимальна кількість запитів у вікні
  readonly windowMs: number;       // Тривалість вікна в мілісекундах
  readonly leaseSize: number;      // Розмір локальної пачки токенів, що орендується
  readonly flushIntervalMs: number;// Максимальний інтервал між асинхронними скиданнями
  readonly maxBatchSize: number;   // Максимальний розмір буфера до примусового скидання
}

/**
 * Стан активної оренди токенів для конкретного клієнта.
 */
export interface TokenLease {
  availableTokens: number;
  expiresAt: number;
}

/**
 * Дельта споживання для асинхронного батчингу.
 */
export interface BatchDelta {
  readonly key: string;
  readonly count: number;
  readonly timestamp: number;
}

/**
 * Контракт взаємодії з центральним сховищем/координатором (KV, Durable Object або Redis).
 */
export interface CentralRateLimitBackend {
  requestLease(key: string, requestedTokens: number, windowMs: number): Promise<{ grantedTokens: number; ttlMs: number }>;
  commitBatch(deltas: ReadonlyArray<BatchDelta>): Promise<void>;
}

/**
 * Стандартний контекст виконання Cloudflare Workers для фонових задач.
 */
export interface ExecutionContext {
  waitUntil(promise: Promise<unknown>): void;
}
