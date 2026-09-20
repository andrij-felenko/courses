/**
 * edge_worker.ts
 *
 * Реалізація фасаду EdgeRateLimiter та точки входу Cloudflare Worker (EdgeWorker).
 * Виконує перевірку ліміту в оперативній пам'яті V8-ізоляту за мікросекунди,
 * повертає HTTP-відповідь клієнту без мережевих затримок та планує
 * фонову синхронізацію дельт через ctx.waitUntil.
 */

import { CentralCoordinatorClient } from './central_coordinator.ts';
import { RateLimitHeaderFormatter } from './rate_limit_headers.ts';
import { TokenLeaseBucket } from './token_lease_bucket.ts';
import type {
  EdgeRateLimiterConfig,
  ExecutionContext,
  RateLimitVerdict,
  WorkerEnv,
} from './types.ts';

/**
 * Фасад граничного обмежувача: координує локальні бакети в пам'яті ізоляту,
 * клієнт зв'язку з центром та форматер заголовків для атомарного ухвалення рішення.
 */
export class EdgeRateLimiter {
  public readonly config: EdgeRateLimiterConfig;
  public readonly coordinatorClient: CentralCoordinatorClient;
  public readonly headerFormatter: RateLimitHeaderFormatter;

  /** Таблиця локальних бакетів оренди в пам'яті V8-ізоляту (по одному на клієнта) */
  private readonly buckets: Map<string, TokenLeaseBucket> = new Map();

  constructor(
    config: EdgeRateLimiterConfig,
    coordinatorClient: CentralCoordinatorClient
  ) {
    this.config = config;
    this.coordinatorClient = coordinatorClient;
    this.headerFormatter = new RateLimitHeaderFormatter(
      config.globalLimit,
      config.windowSeconds
    );
  }

  /**
   * Отримує існуючий або створює новий локальний бакет для клієнта.
   */
  public getOrCreateBucket(clientId: string): TokenLeaseBucket {
    let bucket = this.buckets.get(clientId);
    if (!bucket) {
      bucket = new TokenLeaseBucket(clientId, this.config);
      this.buckets.set(clientId, bucket);
    }
    return bucket;
  }

  /**
   * Атомарна перевірка та списання квоти в оперативній пам'яті ізоляту.
   * Виконується за частки мілісекунди без мережевих блокувань.
   * Якщо необхідно поповнити оренду, повертає фоновий Promise для ctx.waitUntil.
   */
  public checkRateLimit(clientId: string): {
    verdict: RateLimitVerdict;
    backgroundSyncPromise?: Promise<void>;
  } {
    const startTime = performance.now();
    const bucket = this.getOrCreateBucket(clientId);
    const now = Date.now();

    const consumeResult = bucket.tryConsume(1, now);
    const localLatencyMs = performance.now() - startTime;

    let backgroundSyncPromise: Promise<void> | undefined;

    // Якщо локальний бакет сигналізує про необхідність фонового поповнення квоти
    if (consumeResult.shouldRefill) {
      bucket.markRefilling(true);
      backgroundSyncPromise = this.executeBackgroundSync(bucket, clientId);
    }

    // Розрахунок орієнтовного часу до оновлення вікна (секунди)
    const expiresAt = bucket.getExpiresAt();
    const resetSeconds =
      expiresAt > now
        ? Math.ceil((expiresAt - now) / 1000)
        : this.config.windowSeconds;

    const verdict: RateLimitVerdict = {
      allowed: consumeResult.allowed,
      clientId,
      remaining: consumeResult.remaining,
      limit: this.config.globalLimit,
      resetSeconds,
      isFallback: consumeResult.isFallback,
      localLatencyMs,
      reason: consumeResult.reason,
    };

    return { verdict, backgroundSyncPromise };
  }

  /**
   * Асинхронне фонове завдання: скидає накопичену дельту в центр та отримує свіжий блок оренди.
   * Передається у Cloudflare Workers через ctx.waitUntil, не сповільнюючи відповідь користувачу.
   */
  private async executeBackgroundSync(
    bucket: TokenLeaseBucket,
    clientId: string
  ): Promise<void> {
    const deltaToCommit = bucket.getBufferedDelta();
    const requestedBatch = this.config.leaseBatchSize;

    try {
      const result = await this.coordinatorClient.syncAndAcquireLease(
        clientId,
        deltaToCommit,
        requestedBatch
      );

      if (result.success && result.newLease) {
        if (result.isFallback) {
          // Застосування аварійного блоку Fail-Open
          bucket.applyFallbackLease(
            result.newLease.grantedTokens,
            this.config.leaseTtlMs
          );
        } else {
          // Успішна фіксація в центральному координаторі
          bucket.commitSyncSuccess(result.newLease, deltaToCommit);
        }
      } else {
        bucket.commitSyncFailure();
      }
    } catch {
      bucket.commitSyncFailure();
    }
  }

  /**
   * Прогріває або встановлює початковий блок оренди (корисно при ініціалізації чи стендовому тестуванні).
   */
  public prewarmBucket(
    clientId: string,
    tokens: number,
    ttlMs: number = this.config.leaseTtlMs
  ): void {
    const bucket = this.getOrCreateBucket(clientId);
    const now = Date.now();
    bucket.setLease({
      leaseId: `prewarmed-${now}`,
      clientId,
      grantedTokens: tokens,
      remainingTokens: tokens,
      expiresAt: now + ttlMs,
      issuedAt: now,
    });
  }
}

/**
 * Точка входу Cloudflare Worker (обробник fetch).
 * Перехоплює вхідний HTTP-запит, ідентифікує клієнта, миттєво перевіряє ліміт
 * та делегує фонову синхронізацію середовищу через ctx.waitUntil.
 */
export class EdgeWorker {
  private readonly limiter: EdgeRateLimiter;

  constructor(limiter: EdgeRateLimiter) {
    this.limiter = limiter;
  }

  /**
   * Головний метод обробки HTTP-запитів Cloudflare Worker.
   */
  public async fetch(
    request: Request,
    _env?: WorkerEnv,
    ctx?: ExecutionContext
  ): Promise<Response> {
    const clientId = this.extractClientId(request);

    // Миттєве локальне ухвалення рішення в оперативній пам'яті V8-ізоляту
    const { verdict, backgroundSyncPromise } =
      this.limiter.checkRateLimit(clientId);

    // Якщо сформовано фонову задачу поповнення оренди — реєструємо її через ctx.waitUntil
    if (backgroundSyncPromise) {
      if (ctx && typeof ctx.waitUntil === 'function') {
        ctx.waitUntil(backgroundSyncPromise);
      } else {
        // У разі роботи в автономному середовищі без контексту воркера (локальний тест)
        backgroundSyncPromise.catch((err) => {
          console.error(
            `[EdgeWorker] Непередбачена помилка фонової синхронізації: ${err}`
          );
        });
      }
    }

    // Формуємо обов'язкові стандартні заголовки RateLimit
    const responseHeaders = this.limiter.headerFormatter.format(verdict);
    responseHeaders['Content-Type'] = 'application/json; charset=utf-8';
    responseHeaders['X-Edge-Latency-Ms'] = verdict.localLatencyMs.toFixed(3);

    // Якщо квоту вичерпано — повертаємо 429 Too Many Requests із заголовком Retry-After
    if (!verdict.allowed) {
      return new Response(
        JSON.stringify(
          {
            error: 'Too Many Requests',
            status: 429,
            clientId: verdict.clientId,
            reason: verdict.reason,
            retryAfterSeconds: verdict.resetSeconds,
          },
          null,
          2
        ),
        {
          status: 429,
          statusText: 'Too Many Requests',
          headers: responseHeaders,
        }
      );
    }

    // Дозволений запит: повертаємо відповідь зі статусом 200 OK
    return new Response(
      JSON.stringify(
        {
          status: 200,
          message: 'Запит успішно авторизовано на периферійному вузлі Cloudflare Worker',
          clientId: verdict.clientId,
          remainingTokens: verdict.remaining,
          edgeLatencyMs: verdict.localLatencyMs,
        },
        null,
        2
      ),
      {
        status: 200,
        statusText: 'OK',
        headers: responseHeaders,
      }
    );
  }

  /**
   * Видобуває стабільний ідентифікатор клієнта із заголовків або URL.
   * Використовує стандартний заголовок Cloudflare CF-Connecting-IP або X-Forwarded-For.
   */
  private extractClientId(request: Request): string {
    const cfIp = request.headers.get('CF-Connecting-IP');
    if (cfIp && cfIp.trim() !== '') {
      return cfIp.trim();
    }

    const xff = request.headers.get('X-Forwarded-For');
    if (xff && xff.trim() !== '') {
      return xff.split(',')[0].trim();
    }

    const auth = request.headers.get('Authorization');
    if (auth && auth.trim() !== '') {
      return `auth:${auth.trim().slice(-8)}`;
    }

    try {
      const url = new URL(request.url);
      const queryClient = url.searchParams.get('clientId');
      if (queryClient && queryClient.trim() !== '') {
        return queryClient.trim();
      }
    } catch {
      // Ігноруємо помилки парсингу відносного URL
    }

    return 'anonymous-edge-client';
  }
}
