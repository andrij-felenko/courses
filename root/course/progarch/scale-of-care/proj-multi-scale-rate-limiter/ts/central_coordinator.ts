/**
 * central_coordinator.ts
 *
 * Модуль синхронізації з центральним регіоном.
 * Містить клієнт зв'язку із захистом від таймаутів та політикою Fail-Open,
 * а також автономний емулятор центрального сховища (MockCentralCoordinator)
 * із реалістичним моделюванням міжконтинентальної затримки світла (WAN latency).
 */

import type {
  CentralCoordinator,
  EdgeRateLimiterConfig,
  LeaseSyncResult,
  TokenLease,
} from './types.ts';

/**
 * Клієнт для взаємодії периферійного V8-ізоляту з центральним сховищем квот.
 * Реалізує контроль таймаутів та відмовостійку політику Fail-Open.
 */
export class CentralCoordinatorClient {
  private readonly coordinator: CentralCoordinator;
  private readonly config: EdgeRateLimiterConfig;

  constructor(coordinator: CentralCoordinator, config: EdgeRateLimiterConfig) {
    this.coordinator = coordinator;
    this.config = config;
  }

  /**
   * Виконує фонову синхронізацію: скидає накопичену дельту споживання та замовляє новий блок токенів.
   * У разі перевищення таймауту або мережевого збою застосовує аварійну політику Fail-Open.
   */
  public async syncAndAcquireLease(
    clientId: string,
    deltaToCommit: number,
    requestedTokens: number
  ): Promise<LeaseSyncResult> {
    try {
      // Обмежуємо тривалість очікування центрального регіону жорстким таймаутом
      const syncPromise = this.coordinator.requestLease(
        clientId,
        requestedTokens,
        deltaToCommit
      );

      const timeoutPromise = new Promise<LeaseSyncResult>((_, reject) => {
        setTimeout(() => {
          reject(
            new Error(
              `Перевищено таймаут очікування центрального координатора (${this.config.syncTimeoutMs} мс)`
            )
          );
        }, this.config.syncTimeoutMs);
      });

      return await Promise.race([syncPromise, timeoutPromise]);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);

      // Архітектурне рішення: Fail-Open vs Fail-Closed
      if (this.config.failOpen) {
        const fallbackCount =
          this.config.fallbackLeaseTokens ?? this.config.leaseBatchSize;
        const now = Date.now();

        // Створюємо тимчасовий аварійний блок для збереження доступності сайту
        const fallbackLease: TokenLease = {
          leaseId: `failopen-${now}-${Math.random().toString(36).slice(2, 8)}`,
          clientId,
          grantedTokens: fallbackCount,
          remainingTokens: fallbackCount,
          expiresAt: now + this.config.leaseTtlMs,
          issuedAt: now,
        };

        return {
          success: true,
          isFallback: true,
          newLease: fallbackLease,
          error: `[Fail-Open активовано]: ${errorMessage}`,
        };
      }

      return {
        success: false,
        isFallback: false,
        error: `[Fail-Closed відмова]: ${errorMessage}`,
      };
    }
  }
}

/**
 * Автономний in-memory емулятор центрального координатора (наприклад, Redis Cluster або DynamoDB у регіоні us-east-1).
 * Моделює міжрегіональну затримку світла у волоконно-оптичних лініях (WAN RTT) та збої доступності.
 */
export class MockCentralCoordinator implements CentralCoordinator {
  /** Симульована мережева затримка між периферійним воркером та центром (мс) */
  private networkLatencyMs: number;

  /** Прапорець емуляції аварійного стану центрального регіону (мережевий розкол/падіння БД) */
  private simulateFailure: boolean = false;

  /** Лічильник виданих блоків оренди */
  private leaseCounter: number = 0;

  /** Глобальний ліміт квоти на вікно */
  private readonly globalLimit: number;

  /** Розмір вікна в мілісекундах */
  private readonly windowMs: number;

  /** Час життя оренди (мс) */
  private readonly leaseTtlMs: number;

  /** Стан споживання квот клієнтами в центральній базі даних */
  private clientUsage: Map<
    string,
    { used: number; windowStart: number }
  > = new Map();

  /** Статистика для демонстраційного стенду */
  public metrics = {
    totalRequestsReceived: 0,
    totalDeltasCommitted: 0,
    totalLeasesGranted: 0,
    totalTokensGranted: 0,
  };

  constructor(
    globalLimit: number = 100,
    windowSeconds: number = 60,
    leaseTtlMs: number = 10000,
    networkLatencyMs: number = 80
  ) {
    this.globalLimit = globalLimit;
    this.windowMs = windowSeconds * 1000;
    this.leaseTtlMs = leaseTtlMs;
    this.networkLatencyMs = networkLatencyMs;
  }

  /**
   * Вмикає або вимикає симуляцію збою центрального координатора.
   */
  public setSimulateFailure(active: boolean): void {
    this.simulateFailure = active;
  }

  /**
   * Налаштовує симульовану затримку мережі (WAN RTT).
   */
  public setNetworkLatency(ms: number): void {
    this.networkLatencyMs = ms;
  }

  public getNetworkLatency(): number {
    return this.networkLatencyMs;
  }

  /**
   * Обробляє запит крайового вузла: фіксує дельту споживання та виділяє новий блок оренди.
   */
  public async requestLease(
    clientId: string,
    requestedTokens: number,
    deltaToCommit: number
  ): Promise<LeaseSyncResult> {
    // 1. Емуляція трансконтинентальної затримки світла (WAN RTT)
    if (this.networkLatencyMs > 0) {
      await new Promise((resolve) =>
        setTimeout(resolve, this.networkLatencyMs)
      );
    }

    // 2. Емуляція катастрофічного збою центрального координатора
    if (this.simulateFailure) {
      throw new Error(
        'Центральне сховище квот недоступне: Connection refused (WAN partition / DB crash)'
      );
    }

    this.metrics.totalRequestsReceived++;
    this.metrics.totalDeltasCommitted += deltaToCommit;

    const now = Date.now();
    let clientRecord = this.clientUsage.get(clientId);

    if (!clientRecord || now - clientRecord.windowStart >= this.windowMs) {
      clientRecord = { used: 0, windowStart: now };
      this.clientUsage.set(clientId, clientRecord);
    }

    // Фіксація локальної дельти споживання, надісланої воркером
    clientRecord.used += deltaToCommit;

    // Розрахунок залишкової глобальної квоти
    const remainingInWindow = Math.max(0, this.globalLimit - clientRecord.used);

    if (remainingInWindow <= 0) {
      return {
        success: false,
        error: 'Глобальну квоту клієнта повністю вичерпано в центральному регіоні',
        serverRemainingTokens: 0,
      };
    }

    // Видаємо блок токенів (не більше, ніж доступно у глобальній квоті)
    const tokensToGrant = Math.min(requestedTokens, remainingInWindow);
    clientRecord.used += tokensToGrant; // Резервуємо орендовані токени

    this.leaseCounter++;
    this.metrics.totalLeasesGranted++;
    this.metrics.totalTokensGranted += tokensToGrant;

    const newLease: TokenLease = {
      leaseId: `central-lease-${this.leaseCounter}-${Date.now().toString(36)}`,
      clientId,
      grantedTokens: tokensToGrant,
      remainingTokens: tokensToGrant,
      expiresAt: now + this.leaseTtlMs,
      issuedAt: now,
    };

    const serverRemaining = Math.max(0, this.globalLimit - clientRecord.used);

    return {
      success: true,
      newLease,
      serverRemainingTokens: serverRemaining,
      isFallback: false,
    };
  }

  /**
   * Повертає поточний стан глобального лічильника використання квоти.
   */
  public getClientUsage(clientId: string): { used: number; remaining: number } {
    const record = this.clientUsage.get(clientId);
    const used = record ? record.used : 0;
    return {
      used,
      remaining: Math.max(0, this.globalLimit - used),
    };
  }
}
