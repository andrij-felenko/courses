export interface PolicyConfig<T> {
  perAttemptTimeoutMs: number;
  overallTimeoutMs: number;
  maxRetries: number;
  initialBackoffMs: number;
  circuitThreshold: number;
  circuitResetTimeMs: number;
  fallbackHandler?: FallbackHandler<T>;
}

export class PolicyBuilder<T> {
  private config: PolicyConfig<T> = {
    perAttemptTimeoutMs: 500,
    overallTimeoutMs: 2000,
    maxRetries: 2,
    initialBackoffMs: 50,
    circuitThreshold: 5,
    circuitResetTimeMs: 10000,
  };

  withTimeouts(perAttemptMs: number, overallMs: number): this {
    this.config.perAttemptTimeoutMs = perAttemptMs;
    this.config.overallTimeoutMs = overallMs;
    return this;
  }

  withRetry(maxRetries: number, initialBackoffMs: number): this {
    this.config.maxRetries = maxRetries;
    this.config.initialBackoffMs = initialBackoffMs;
    return this;
  }

  withFallback(handler: FallbackHandler<T>): this {
    this.config.fallbackHandler = handler;
    return this;
  }

  build(): ResilientExecutor<T> {
    return new ResilientExecutor<T>({ ...this.config });
  }
}

export class ResilientExecutor<T> {
  private consecutiveFailures = 0;
  private circuitOpenUntil = 0;

  constructor(private readonly config: PolicyConfig<T>) {}

  async execute(action: (signal: AbortSignal) => Promise<T>): Promise<ResilientResult<T>> {
    const startTime = Date.now();

    // 1. Перевірка автомату Circuit Breaker
    if (Date.now() < this.circuitOpenUntil) {
      return this.handleFallback(
        new Error('Circuit breaker is OPEN'),
        BoundaryStatus.CIRCUIT_OPEN,
        0,
        startTime
      );
    }

    const overallController = new AbortController();
    const overallTimer = setTimeout(
      () => overallController.abort(),
      this.config.overallTimeoutMs
    );

    let lastError: Error = new Error('Unknown error');
    let attempts = 0;

    try {
      while (attempts <= this.config.maxRetries) {
        attempts++;
        if (overallController.signal.aborted) break;

        const attemptController = new AbortController();
        const perAttemptTimer = setTimeout(
          () => attemptController.abort(),
          this.config.perAttemptTimeoutMs
        );

        // Об'єднуємо сигнали переривання
        const onAbort = () => attemptController.abort();
        overallController.signal.addEventListener('abort', onAbort);

        try {
          const value = await action(attemptController.signal);
          clearTimeout(perAttemptTimer);
          overallController.signal.removeEventListener('abort', onAbort);
          this.consecutiveFailures = 0;

          return {
            value,
            isFallback: false,
            status: BoundaryStatus.SUCCESS,
            attempts,
            executionTimeMs: Date.now() - startTime,
          };
        } catch (err: any) {
          clearTimeout(perAttemptTimer);
          overallController.signal.removeEventListener('abort', onAbort);
          lastError = err;

          if (overallController.signal.aborted) break;

          // Експоненційний відступ із випадковим дрижанням (Jitter)
          if (attempts <= this.config.maxRetries) {
            const backoff = this.config.initialBackoffMs * Math.pow(2, attempts);
            const jitter = Math.random() * (backoff / 2);
            await new Promise((res) => setTimeout(res, backoff / 2 + jitter));
          }
        }
      }
    } finally {
      clearTimeout(overallTimer);
    }

    // Реєстрація збою у стані Circuit Breaker
    this.consecutiveFailures++;
    if (this.consecutiveFailures >= this.config.circuitThreshold) {
      this.circuitOpenUntil = Date.now() + this.config.circuitResetTimeMs;
    }

    const finalStatus = overallController.signal.aborted
      ? BoundaryStatus.TIMEOUT
      : BoundaryStatus.RETRIES_EXCEEDED;

    return this.handleFallback(lastError, finalStatus, attempts, startTime);
  }

  private async handleFallback(
    error: Error,
    status: BoundaryStatus,
    attempts: number,
    startTime: number
  ): Promise<ResilientResult<T>> {
    if (this.config.fallbackHandler) {
      try {
        const fallbackVal = await this.config.fallbackHandler(error, {
          attemptCount: attempts,
          status,
        });
        return {
          value: fallbackVal,
          isFallback: true,
          status: BoundaryStatus.FALLBACK_APPLIED,
          attempts,
          executionTimeMs: Date.now() - startTime,
          originalError: error,
        };
      } catch (fbErr: any) {
        // Якщо фаллбек також дав збій — повертаємо вихідний статус помилки
      }
    }

    return {
      value: undefined as unknown as T,
      isFallback: false,
      status,
      attempts,
      executionTimeMs: Date.now() - startTime,
      originalError: error,
    };
  }
}
