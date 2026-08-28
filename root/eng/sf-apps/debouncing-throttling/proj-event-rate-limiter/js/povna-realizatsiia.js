/**
 * Універсальна реалізація debounce на чистому JavaScript (ES2022)
 */
export function debounce(fn, wait, options = {}) {
  let lastArgs;
  let lastThis;
  let result;
  let timerId;
  let lastCallTime;
  let lastInvokeTime = 0;

  const leading = Boolean(options.leading);
  const trailing = 'trailing' in options ? Boolean(options.trailing) : true;
  const maxWait = typeof options.maxWait === 'number' ? Math.max(options.maxWait, wait) : undefined;
  const hasMaxWait = maxWait !== undefined;

  const now = () => (typeof performance !== 'undefined' ? performance.now() : Date.now());

  function invoke(time) {
    const args = lastArgs;
    const thisArg = lastThis;

    lastArgs = undefined;
    lastThis = undefined;
    lastInvokeTime = time;
    result = fn.apply(thisArg, args);
    return result;
  }

  function remainingWait(time) {
    const timeSinceLastCall = time - (lastCallTime || 0);
    const timeSinceLastInvoke = time - lastInvokeTime;
    const timeWaiting = wait - timeSinceLastCall;

    return hasMaxWait
      ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke)
      : timeWaiting;
  }

  function shouldInvoke(time) {
    if (lastCallTime === undefined) {
      return true;
    }
    const timeSinceLastCall = time - lastCallTime;
    const timeSinceLastInvoke = time - lastInvokeTime;

    return (
      timeSinceLastCall >= wait ||
      timeSinceLastCall < 0 ||
      (hasMaxWait && timeSinceLastInvoke >= maxWait)
    );
  }

  function timerExpired() {
    const time = now();
    if (shouldInvoke(time)) {
      trailingEdge(time);
      return;
    }
    timerId = setTimeout(timerExpired, remainingWait(time));
  }

  function trailingEdge(time) {
    timerId = undefined;
    if (trailing && lastArgs) {
      return invoke(time);
    }
    lastArgs = undefined;
    lastThis = undefined;
    return result;
  }

  function leadingEdge(time) {
    lastInvokeTime = time;
    timerId = setTimeout(timerExpired, wait);
    return leading ? invoke(time) : result;
  }

  function cancel() {
    if (timerId !== undefined) {
      clearTimeout(timerId);
    }
    lastInvokeTime = 0;
    lastArgs = undefined;
    lastCallTime = undefined;
    lastThis = undefined;
    timerId = undefined;
  }

  function flush() {
    return timerId === undefined ? result : trailingEdge(now());
  }

  function isPending() {
    return timerId !== undefined;
  }

  function debounced(...args) {
    const time = now();
    const isInvoking = shouldInvoke(time);

    lastArgs = args;
    lastThis = this;
    lastCallTime = time;

    if (isInvoking) {
      if (timerId === undefined) {
        return leadingEdge(time);
      }
      if (hasMaxWait) {
        clearTimeout(timerId);
        timerId = setTimeout(timerExpired, wait);
        return invoke(time);
      }
    }

    if (timerId === undefined) {
      timerId = setTimeout(timerExpired, wait);
    }

    return result;
  }

  debounced.cancel = cancel;
  debounced.flush = flush;
  debounced.isPending = isPending;

  return debounced;
}

export function throttle(fn, wait, options = {}) {
  const leading = 'leading' in options ? Boolean(options.leading) : true;
  const trailing = 'trailing' in options ? Boolean(options.trailing) : true;

  return debounce(fn, wait, {
    leading,
    trailing,
    maxWait: wait,
  });
}
