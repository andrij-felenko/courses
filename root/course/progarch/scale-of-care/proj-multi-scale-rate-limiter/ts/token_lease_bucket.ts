/**
 * token_lease_bucket.ts
 *
 * Локальний бакет орендованих токенів у пам'яті V8-ізоляту крайового вузла.
 * Дозволяє списувати квоту за частки мілісекунди без мережевих викликів (zero WAN latency),
 * буферизує дельту фактично спожитих токенів та своєчасно визначає момент
 * для випереджального фонового оновлення блоку оренди.
 */

import type { EdgeRateLimiterConfig, TokenLease } from './types.ts';

export interface LocalConsumeResult {
  /** Чи успішно списано токен з локального орендованого блоку */
  allowed: boolean;
  /** Залишок токенів у поточному локальному блоці */
  remaining: number;
  /** Чи настав поріг для ініціації фонової синхронізації з центром */
  shouldRefill: boolean;
  /** Причина прийнятого локального рішення */
  reason: string;
  /** Чи є поточний блок аварійним (Fail-Open fallback) */
  isFallback: boolean;
}

/**
 * Керує локальною орендою блоків токенів у пам'яті V8-ізоляту для конкретного клієнта.
 */
export class TokenLeaseBucket {
  private readonly clientId: string;
  private readonly config: EdgeRateLimiterConfig;

  /** Поточний активний блок оренди токенів, отриманий від центру */
  private currentLease: TokenLease | null = null;

  /** Дельта спожитих токенів, ще не зафіксована у центральному координаторі */
  private bufferedDelta: number = 0;

  /** Прапорець наявності активної фонової задачі синхронізації (запобігає thundering herd) */
  private isRefilling: boolean = false;

  /** Час останньої активності бакета для очищення застарілого стану */
  private lastActivityAt: number = Date.now();

  constructor(clientId: string, config: EdgeRateLimiterConfig) {
    this.clientId = clientId;
    this.config = config;
  }

  /**
   * Перевіряє, чи має бакет дійсний блок оренди із ненульовим залишком.
   */
  public hasValidLease(now: number = Date.now()): boolean {
    if (!this.currentLease) {
      return false;
    }
    return now < this.currentLease.expiresAt && this.currentLease.remainingTokens > 0;
  }

  /**
   * Оптимістично списує вказану кількість токенів із локальної пам'яті V8-ізоляту.
   * Виконується синхронно за мікросекунди без блокування потоку виконання.
   */
  public tryConsume(tokens: number = 1, now: number = Date.now()): LocalConsumeResult {
    this.lastActivityAt = now;
    const isFallback = this.currentLease?.leaseId.startsWith('failopen-') ?? false;

    // Випадок 1: Блок оренди ще не ініціалізовано (холодний старт ізоляту)
    if (!this.currentLease) {
      this.currentLease = {
        leaseId: `bootstrap-${now}`,
        clientId: this.clientId,
        grantedTokens: 1,
        remainingTokens: 0,
        expiresAt: now + this.config.leaseTtlMs,
        issuedAt: now,
      };
      this.bufferedDelta += 1;
      return {
        allowed: true,
        remaining: 0,
        shouldRefill: !this.isRefilling,
        reason: 'Оптимістичний пропуск при холодному старті із запитом оренди нового блоку',
        isFallback: false,
      };
    }

    // Випадок 2: Термін дії поточної оренди вичерпано за часом (Lease TTL expired)
    if (now >= this.currentLease.expiresAt) {
      return {
        allowed: false,
        remaining: 0,
        shouldRefill: !this.isRefilling,
        reason: `Термін оренди токенів вичерпано (${new Date(this.currentLease.expiresAt).toISOString()})`,
        isFallback,
      };
    }

    // Випадок 3: Недостатньо токенів у поточному блоці оренди
    if (this.currentLease.remainingTokens < tokens) {
      return {
        allowed: false,
        remaining: this.currentLease.remainingTokens,
        shouldRefill: !this.isRefilling,
        reason: 'Локальний блок орендованих токенів вичерпано',
        isFallback,
      };
    }

    // Оптимістичне локальне списання без мережевих звернень
    this.currentLease.remainingTokens -= tokens;
    this.bufferedDelta += tokens;

    const remaining = this.currentLease.remainingTokens;
    const timeToExpiryMs = this.currentLease.expiresAt - now;

    // Визначаємо необхідність випереджального поповнення у фоні:
    // 1) Залишок токенів впав до або нижче refillThresholdTokens
    // 2) Або до завершення часу оренди лишилося менше 30% її тривалості
    const isBelowTokenThreshold = remaining <= this.config.refillThresholdTokens;
    const isNearExpiry = timeToExpiryMs < this.config.leaseTtlMs * 0.3;
    const shouldRefill = !this.isRefilling && (isBelowTokenThreshold || isNearExpiry);

    return {
      allowed: true,
      remaining,
      shouldRefill,
      reason: 'Токен успішно списано з локального орендованого блоку',
      isFallback,
    };
  }

  /**
   * Фіксує успішне поновлення оренди від центрального координатора.
   * Коригує буферизовану дельту на величину зафіксованих у центрі токенів,
   * зберігаючи нові списання, що могли відбутися під час польоту мережевого запиту.
   */
  public commitSyncSuccess(newLease: TokenLease, committedDelta: number): void {
    this.bufferedDelta = Math.max(0, this.bufferedDelta - committedDelta);
    this.currentLease = newLease;
    this.isRefilling = false;
  }

  /**
   * Фіксує невдалу спробу синхронізації з центром (скидає прапорець блокування).
   */
  public commitSyncFailure(): void {
    this.isRefilling = false;
  }

  /**
   * Застосовує аварійний блок оренди у разі спрацьовування стратегії Fail-Open.
   */
  public applyFallbackLease(fallbackTokens: number, ttlMs: number, now: number = Date.now()): void {
    this.currentLease = {
      leaseId: `failopen-lease-${now}-${Math.random().toString(36).substring(2, 7)}`,
      clientId: this.clientId,
      grantedTokens: fallbackTokens,
      remainingTokens: fallbackTokens,
      expiresAt: now + ttlMs,
      issuedAt: now,
    };
    this.isRefilling = false;
  }

  /**
   * Повертає поточну накопичену дельту споживання для передачі координатору.
   */
  public getBufferedDelta(): number {
    return this.bufferedDelta;
  }

  /**
   * Повертає кількість доступних токенів з урахуванням валідності за часом.
   */
  public getRemainingTokens(now: number = Date.now()): number {
    if (!this.currentLease || now >= this.currentLease.expiresAt) {
      return 0;
    }
    return this.currentLease.remainingTokens;
  }

  /**
   * Повертає час завершення поточної оренди в Unix ms.
   */
  public getExpiresAt(): number {
    return this.currentLease ? this.currentLease.expiresAt : 0;
  }

  /**
   * Встановлює стан завантаження оренди ззовні (наприклад, при прогріві бакета).
   */
  public setLease(lease: TokenLease): void {
    this.currentLease = lease;
    this.isRefilling = false;
  }

  public getClientId(): string {
    return this.clientId;
  }

  public getIsRefilling(): boolean {
    return this.isRefilling;
  }

  public markRefilling(value: boolean): void {
    this.isRefilling = value;
  }
}
