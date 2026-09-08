/**
 * Базові типи та контракти конфігурації для стійкого HTTP-шлюзу.
 */

export type CircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export type CallResult = 'SUCCESS' | 'FAILURE' | 'SLOW';

export interface TimeoutConfig {
  /** Максимальний час на встановлення TCP/TLS з'єднання (мс) */
  connectionTimeoutMs: number;
  /** Максимальний час очікування відповіді після надсилання запиту (мс) */
  readTimeoutMs: number;
  /** Загальний дедлайн на всю операцію включно з повторними спробами (мс) */
  totalTimeoutMs: number;
}

export interface BulkheadConfig {
  /** Максимальна кількість одночасних активних викликів */
  maxConcurrent: number;
  /** Максимальний розмір черги очікування викликів */
  maxQueueSize: number;
}

export interface CircuitBreakerConfig {
  /** Поріг частки збоїв (від 0.0 до 1.0), після якого ланцюг розмикається */
  failureRateThreshold: number;
  /** Поріг частки повільних викликів (від 0.0 до 1.0) */
  slowCallRateThreshold: number;
  /** Тривалість виклику (мс), після якої він класифікується як повільний (slow call) */
  slowCallDurationMs: number;
  /** Загальна тривалість часового ковзного вікна (мс) */
  windowDurationMs: number;
  /** Кількість дискретних часових кошиків у ковзному вікні */
  bucketCount: number;
  /** Мінімальна кількість викликів для активації розрахунку порогів */
  minCalls: number;
  /** Час очікування в розімкненому стані перед переходом у HALF_OPEN (мс) */
  waitDurationInOpenStateMs: number;
  /** Кількість пробних запитів, дозволених у стані HALF_OPEN */
  permittedNumberOfCallsInHalfOpenState: number;
}

export interface RetryConfig {
  /** Максимальна кількість повторних спроб */
  maxAttempts: number;
  /** Базова затримка перед першим повтором (мс) */
  baseDelayMs: number;
  /** Верхня стеля інтервалу затримки (мс) */
  maxDelayMs: number;
}

export interface ClientConfig {
  timeouts: TimeoutConfig;
  bulkhead: BulkheadConfig;
  circuitBreaker: CircuitBreakerConfig;
  retry: RetryConfig;
}

export interface WindowSnapshot {
  totalCalls: number;
  successCount: number;
  failureCount: number;
  slowCount: number;
  failureRate: number;
  slowCallRate: number;
}

// ---------------- Доменні помилки стійкості ----------------

export class TimeoutError extends Error {
  readonly level: 'connection' | 'read' | 'total';

  constructor(level: 'connection' | 'read' | 'total', message: string) {
    super(message);
    this.name = 'TimeoutError';
    this.level = level;
  }
}

export class BulkheadFullError extends Error {
  constructor(message = 'Перебірка переповнена: вичерпано ліміт одночасних запитів та черги') {
    super(message);
    this.name = 'BulkheadFullError';
  }
}

export class CircuitOpenError extends Error {
  constructor(message = 'Запобіжник розімкнено: сервіс тимчасово недоступний (fail-fast)') {
    super(message);
    this.name = 'CircuitOpenError';
  }
}

export class MaxRetriesExceededError extends Error {
  readonly lastError: unknown;

  constructor(lastError: unknown, attempts: number) {
    super(`Вичерпано максимальну кількість повторних спроб (${attempts})`);
    this.name = 'MaxRetriesExceededError';
    this.lastError = lastError;
  }
}
