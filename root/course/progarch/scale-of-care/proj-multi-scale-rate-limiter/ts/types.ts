/**
 * types.ts
 *
 * Доменні типи, інтерфейси та структури даних для розподіленого
 * граничного обмежувача частоти запитів (Edge Rate Limiter) на базі Token Lease.
 */

/**
 * Конфігурація крайового обмежувача частоти запитів.
 */
export interface EdgeRateLimiterConfig {
  /** Загальний ліміт запитів для клієнта в межах часового вікна */
  globalLimit: number;
  /** Тривалість глобального квотного вікна у секундах */
  windowSeconds: number;
  /** Розмір блоку токенів, що орендується у центрального координатора за один раз */
  leaseBatchSize: number;
  /** Максимальний час життя (TTL) орендованого блоку токенів у мілісекундах */
  leaseTtlMs: number;
  /** Залишок токенів у локальному бакеті, досягнення якого ініціює випереджальне фонове поповнення */
  refillThresholdTokens: number;
  /** Граничний таймаут мережевого запиту до центрального координатора (мс) */
  syncTimeoutMs: number;
  /** Чи активовано політику Fail-Open при аварії або недоступності центрального координатора */
  failOpen: boolean;
  /** Кількість аварійних токенів, що надаються за політикою Fail-Open при недоступності центру */
  fallbackLeaseTokens?: number;
}

/**
 * Стан орендованого блоку токенів (Token Lease) у пам'ять V8-ізоляту.
 */
export interface TokenLease {
  /** Унікальний ідентифікатор виданої оренди */
  leaseId: string;
  /** Ідентифікатор клієнта (IP, API-токен, Account ID) */
  clientId: string;
  /** Початкова кількість токенів, виділених у цьому блоці */
  grantedTokens: number;
  /** Поточний залишок невикористаних токенів у локальному блоці */
  remainingTokens: number;
  /** Мітка часу (Unix ms), після якої оренда вважається недійсною */
  expiresAt: number;
  /** Мітка часу видачі оренди (Unix ms) */
  issuedAt: number;
}

/**
 * Вердикт перевірки ліміту частоти запитів для формування HTTP-відповіді.
 */
export interface RateLimitVerdict {
  /** Чи дозволено пропуск вхідного HTTP-запиту */
  allowed: boolean;
  /** Ідентифікатор перевіреного клієнта */
  clientId: string;
  /** Оціночний залишок загальної квоти клієнта */
  remaining: number;
  /** Максимальний ліміт запитів у поточному вікні */
  limit: number;
  /** Кількість секунд до скидання лімітного вікна */
  resetSeconds: number;
  /** Чи ухвалено рішення в аварійному режимі (Fail-Open) через відмову координатора */
  isFallback: boolean;
  /** Час прийняття рішення на межі в мілісекундах (субмілісекундна пам'ять V8) */
  localLatencyMs: number;
  /** Пояснення прийнятого вердикту для інженерного аудиту та діагностики */
  reason: string;
}

/**
 * Результат мережевої синхронізації з центральним координатором.
 */
export interface LeaseSyncResult {
  /** Ознака успішності синхронізації */
  success: boolean;
  /** Новий або поновлений блок оренди токенів від центрального регіону */
  newLease?: TokenLease;
  /** Повідомлення про помилку у разі мережевого збою */
  error?: string;
  /** Залишок загальної квоти за даними центрального регіону */
  serverRemainingTokens?: number;
  /** Чи було застосовано аварійний блок Fail-Open */
  isFallback?: boolean;
}

/**
 * Інтерфейс центрального координатора (розподіленого сховища Redis / DynamoDB / Global Service).
 */
export interface CentralCoordinator {
  /**
   * Скидає накопичену дельту споживання та орендує наступний пакет токенів.
   *
   * @param clientId Ідентифікатор клієнта
   * @param requestedTokens Бажаний розмір нового блоку оренди
   * @param deltaToCommit Накопичена локально дельта спожитих токенів для фіксації в центрі
   */
  requestLease(
    clientId: string,
    requestedTokens: number,
    deltaToCommit: number
  ): Promise<LeaseSyncResult>;
}

/**
 * Контекст виконання периферійного воркера (Cloudflare Workers ExecutionContext).
 * Забезпечує виконання неблокуючих фонових завдань через waitUntil.
 */
export interface ExecutionContext {
  /**
   * Повідомляє середовище виконання Cloudflare Workers про необхідність продовжити
   * виконання фонового Promise після того, як HTTP-відповідь клієнту вже відправлена.
   */
  waitUntil(promise: Promise<unknown>): void;
  passThroughOnException?(): void;
}

/**
 * Змінні середовища та прив'язки Cloudflare Worker (Env bindings).
 */
export interface WorkerEnv {
  [key: string]: unknown;
}
