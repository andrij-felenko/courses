export interface RafThrottledFunction<TArgs extends any[]> {
  (...args: TArgs): void;
  cancel(): void;
}

/**
 * Тротлінг викликів строго перед фазою відмальовки браузера
 */
export function rafThrottle<TArgs extends any[]>(
  fn: (...args: TArgs) => void
): RafThrottledFunction<TArgs> {
  let rafId: number | null = null;
  let lastArgs: TArgs | null = null;
  let lastThis: any = null;

  function throttled(this: any, ...args: TArgs): void {
    lastArgs = args;
    lastThis = this;

    if (rafId === null) {
      rafId = requestAnimationFrame(() => {
        const argsToInvoke = lastArgs!;
        const contextToInvoke = lastThis;

        rafId = null;
        lastArgs = null;
        lastThis = null;

        fn.apply(contextToInvoke, argsToInvoke);
      });
    }
  }

  throttled.cancel = (): void => {
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    lastArgs = null;
    lastThis = null;
  };

  return throttled;
}
