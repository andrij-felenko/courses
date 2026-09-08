import type { CircuitBreakerConfig, CircuitState, WindowSnapshot } from './types.ts';
import { CircuitOpenError } from './types.ts';
import { SlidingWindow } from './sliding-window.ts';

/**
 * Скінченний автомат захисту (Circuit Breaker) із ковзним вікном вимірювання.
 * Керує станами CLOSED (норма), OPEN (розрив, fail-fast) та HALF_OPEN (пробне зондування).
 */
export class CircuitBreaker {
  private readonly config: CircuitBreakerConfig;
  private state: CircuitState = 'CLOSED';
  private lastStateChangeTime: number = Date.now();
  private readonly window: SlidingWindow;

  // Лічильники для тестових зондів у стані HALF_OPEN
  private halfOpenCalls = 0;
  private halfOpenSuccesses = 0;

  constructor(config: CircuitBreakerConfig) {
    this.config = config;
    this.window = new SlidingWindow(config.windowDurationMs, config.bucketCount);
  }

  getState(): CircuitState {
    return this.state;
  }

  /**
   * Перевіряє, чи дозволено виконання запиту через запобіжник.
   * У стані OPEN виконує швидке відсікання за 0 мс без виклику мережі.
   */
  tryAcquirePermission(): void {
    const now = Date.now();

    if (this.state === 'OPEN') {
      if (now - this.lastStateChangeTime >= this.config.waitDurationInOpenStateMs) {
        this.transitionTo('HALF_OPEN');
      } else {
        throw new CircuitOpenError();
      }
    }

    if (this.state === 'HALF_OPEN') {
      if (this.halfOpenCalls >= this.config.permittedNumberOfCallsInHalfOpenState) {
        throw new CircuitOpenError('Запобіжник у стані HALF_OPEN: вичерпано квоту пробних викликів');
      }
      this.halfOpenCalls++;
    }
  }

  /**
   * Фіксує успішне виконання запиту.
   */
  onSuccess(durationMs: number): void {
    if (this.state === 'HALF_OPEN') {
      this.halfOpenSuccesses++;
      if (this.halfOpenSuccesses >= this.config.permittedNumberOfCallsInHalfOpenState) {
        this.transitionTo('CLOSED');
      }
      return;
    }

    if (this.state === 'CLOSED') {
      const isSlow = durationMs >= this.config.slowCallDurationMs;
      this.window.record(isSlow ? 'SLOW' : 'SUCCESS');
      this.evaluateState();
    }
  }

  /**
   * Фіксує помилку виконання запиту.
   */
  onError(durationMs: number): void {
    if (this.state === 'HALF_OPEN') {
      // Будь-який збій зонда миттєво повертає контур у розімкнений стан
      this.transitionTo('OPEN');
      return;
    }

    if (this.state === 'CLOSED') {
      this.window.record('FAILURE');
      this.evaluateState();
    }
  }

  getSnapshot(): WindowSnapshot {
    return this.window.getSnapshot();
  }

  private evaluateState(): void {
    const snapshot = this.window.getSnapshot();
    if (snapshot.totalCalls < this.config.minCalls) {
      return; // Захист від шуму: вибірка ще недостатня
    }

    if (
      snapshot.failureRate >= this.config.failureRateThreshold ||
      snapshot.slowCallRate >= this.config.slowCallRateThreshold
    ) {
      this.transitionTo('OPEN');
    }
  }

  private transitionTo(newState: CircuitState): void {
    this.state = newState;
    this.lastStateChangeTime = Date.now();
    this.window.reset();
    this.halfOpenCalls = 0;
    this.halfOpenSuccesses = 0;
  }
}
