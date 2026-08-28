export function rafThrottle(fn) {
  let rafId = null;
  let lastArgs = null;
  let lastThis = null;

  function throttled(...args) {
    lastArgs = args;
    lastThis = this;

    if (rafId === null) {
      rafId = requestAnimationFrame(() => {
        const argsToInvoke = lastArgs;
        const contextToInvoke = lastThis;

        rafId = null;
        lastArgs = null;
        lastThis = null;

        fn.apply(contextToInvoke, argsToInvoke);
      });
    }
  }

  throttled.cancel = () => {
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    lastArgs = null;
    lastThis = null;
  };

  return throttled;
}
