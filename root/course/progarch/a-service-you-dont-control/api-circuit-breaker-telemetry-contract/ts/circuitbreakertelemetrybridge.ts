import { Tracer, Span, SpanStatusCode } from '@opentelemetry/api';

// Контракт колектора метрик запобіжника
export interface CircuitBreakerMetricsCollector {
  recordCallDuration(name: string, durationSeconds: number, kind: string): void;
  incrementCallsTotal(name: string, kind: string): void;
  updateStateGauge(name: string, stateNumericValue: number): void;
  updateSlidingWindowMetrics(name: string, failureRate: number, slowCallRate: number, bufferedCalls: number): void;
  publishStateTransition(event: StateTransitionEvent): void;
}

// Реалізація телеметричного приймача
export class CircuitBreakerTelemetryBridge {
  constructor(
    private readonly metrics: CircuitBreakerMetricsCollector,
    private readonly tracer: Tracer
  ) {}

  // Фіксація стану автомата в числовому датчику
  public reportState(name: string, state: CircuitBreakerState): void {
    const stateMap: Record<CircuitBreakerState, number> = {
      CLOSED: 0,
      OPEN: 1,
      HALF_OPEN: 2,
      FORCED_OPEN: 3,
      FORCED_CLOSED: 4,
      DISABLED: 5,
    };
    this.metrics.updateStateGauge(name, stateMap[state]);
  }

  // Обгортання виконання операції з реєстрацією метрик і трасуванням
  public traceExecution<T>(
    breakerName: string,
    state: CircuitBreakerState,
    action: () => Promise<T>,
    fallback?: (error: Error) => Promise<T>
  ): Promise<T> {
    const span = this.tracer.startSpan(`CircuitBreaker:${breakerName}`);
    span.setAttribute('circuit_breaker.name', breakerName);
    span.setAttribute('circuit_breaker.state', state);

    const startTime = performance.now();

    // Якщо контур розімкнений — негайно фіксуємо відмову в спані
    if (state === 'OPEN' || state === 'FORCED_OPEN') {
      span.addEvent('circuit_breaker.call_rejected', {
        reason: 'Circuit breaker is OPEN (Fast Fail)',
      });
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: `Call rejected by circuit breaker: ${breakerName}`,
      });
      this.metrics.incrementCallsTotal(breakerName, 'not_permitted');
      span.end();

      const notPermittedError = new Error(`Circuit breaker '${breakerName}' is OPEN`);
      if (fallback) {
        return this.executeFallback(breakerName, fallback, notPermittedError);
      }
      return Promise.reject(notPermittedError);
    }

    // Якщо запит дозволено — виконуємо з вимірюванням латентності
    return action()
      .then((result) => {
        const duration = (performance.now() - startTime) / 1000;
        this.metrics.recordCallDuration(breakerName, duration, 'successful');
        this.metrics.incrementCallsTotal(breakerName, 'successful');
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
      })
      .catch((error: Error) => {
        const duration = (performance.now() - startTime) / 1000;
        this.metrics.recordCallDuration(breakerName, duration, 'failed');
        this.metrics.incrementCallsTotal(breakerName, 'failed');
        span.recordException(error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error.message,
        });

        if (fallback) {
          return this.executeFallback(breakerName, fallback, error);
        }
        throw error;
      })
      .finally(() => {
        span.end();
      });
  }

  private executeFallback<T>(
    breakerName: string,
    fallback: (error: Error) => Promise<T>,
    cause: Error
  ): Promise<T> {
    const fallbackSpan = this.tracer.startSpan(`CircuitBreaker:${breakerName}:fallback`);
    fallbackSpan.setAttribute('circuit_breaker.name', breakerName);
    fallbackSpan.setAttribute('circuit_breaker.is_fallback', true);

    return fallback(cause)
      .then((fallbackResult) => {
        this.metrics.incrementCallsTotal(breakerName, 'fallback_success');
        fallbackSpan.setStatus({ code: SpanStatusCode.OK });
        return fallbackResult;
      })
      .catch((fallbackError: Error) => {
        this.metrics.incrementCallsTotal(breakerName, 'fallback_failed');
        fallbackSpan.recordException(fallbackError);
        fallbackSpan.setStatus({
          code: SpanStatusCode.ERROR,
          message: fallbackError.message,
        });
        throw fallbackError;
      })
      .finally(() => {
        fallbackSpan.end();
      });
  }
}
