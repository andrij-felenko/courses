// 1. Спеціалізовані помилки контракту швидкої відмови
export class CircuitBreakerOpenException extends Error {
  constructor(
    public readonly breakerName: string,
    public readonly waitDurationRemainingMs: number,
  ) {
    super(`Запобіжник '${breakerName}' перебуває у стані OPEN. Запит відхилено (Fast Fail). Залишок очікування: ${waitDurationRemainingMs} мс`);
    this.name = 'CircuitBreakerOpenException';
  }
}

// 2. Сигнатура функції запасного сценарію
export type FallbackHandler<T> = (error: Error) => Promise<T> | T;

// 3. Опції індивідуального виконання запиту
export interface ExecutionOptions<T> {
  readonly fallback?: FallbackHandler<T>;
  readonly timeoutMs?: number;
  readonly signal?: AbortSignal;
}

// 4. Програмний контракт захищеного виклику (Execution API)
export interface CircuitBreakerExecutor {
  readonly name: string;

  /**
   * Виконує цільову дію під захистом запобіжника.
   * У разі відкритого стану миттєво запускає fallback або викидає CircuitBreakerOpenException.
   */
  execute<T>(action: () => Promise<T>, options?: ExecutionOptions<T>): Promise<T>;

  /**
   * Функціональний декоратор для створення захищених клієнтських методів.
   */
  decorate<Args extends unknown[], R>(
    fn: (...args: Args) => Promise<R>,
    options?: ExecutionOptions<R>,
  ): (...args: Args) => Promise<R>;
}
