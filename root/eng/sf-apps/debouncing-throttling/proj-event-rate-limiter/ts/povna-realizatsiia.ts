/**
 * Опції конфігурації поведінки дебаунсу
 */
export interface DebounceOptions {
  /** Викликати функцію на передньому фронті (негайно на першу подію) */
  leading?: boolean;
  /** Викликати функцію на задньому фронті (після паузи затишшя) */
  trailing?: boolean;
  /** Максимальний час очікування виклику в мілісекундах при безперервному потоці */
  maxWait?: number;
}

/**
 * Опції конфігурації тротлінгу
 */
export interface ThrottleOptions {
  /** Викликати функцію на старті кожного часового кванта */
  leading?: boolean;
  /** Викликати функцію наприкінці кванта з останніми отриманими аргументами */
  trailing?: boolean;
}

/**
 * Обгортка над функцією з методами контролю життєвого циклу
 */
export interface DebouncedFunction<TArgs extends any[], TReturn> {
  (...args: TArgs): TReturn | undefined;
  /** Скасувати запланований виклик та очистити ресурси */
  cancel(): void;
  /** Негайно виконати запланований виклик і повернути результат */
  flush(): TReturn | undefined;
  /** Перевірити, чи є активний запланований таймер */
  isPending(): boolean;
}

/**
 * Універсальна функція дебаунсу з підтримкою leading, trailing та maxWait
 */
export function debounce<TArgs extends any[], TReturn>(
  fn: (...args: TArgs) => TReturn,
  wait: number,
  options: DebounceOptions = {}
): DebouncedFunction<TArgs, TReturn> {
  let lastArgs: TArgs | undefined;
  let lastThis: any;
  let result: TReturn | undefined;
  let timerId: ReturnType<typeof setTimeout> | undefined;
  let lastCallTime: number | undefined;
  let lastInvokeTime = 0;

  const leading = Boolean(options.leading);
  const trailing = 'trailing' in options ? Boolean(options.trailing) : true;
  const maxWait = typeof options.maxWait === 'number' ? Math.max(options.maxWait, wait) : undefined;
  const hasMaxWait = maxWait !== undefined;

  // Отримання поточного монотонного часу високої точності
  const now = (): number => (typeof performance !== 'undefined' ? performance.now() : Date.now());

  // Виклик цільової функції з очищенням посилань на аргументи
  function invoke(time: number): TReturn {
    const args = lastArgs!;
    const thisArg = lastThis;

    lastArgs = undefined;
    lastThis = undefined;
    lastInvokeTime = time;
    result = fn.apply(thisArg, args);
    return result;
  }

  // Обчислення часу до наступного спрацьовування таймера
  function remainingWait(time: number): number {
    const timeSinceLastCall = time - (lastCallTime || 0);
    const timeSinceLastInvoke = time - lastInvokeTime;
    const timeWaiting = wait - timeSinceLastCall;

    return hasMaxWait
      ? Math.min(timeWaiting, maxWait! - timeSinceLastInvoke)
      : timeWaiting;
  }

  // Перевірка, чи настав час викликати цільову функцію
  function shouldInvoke(time: number): boolean {
    if (lastCallTime === undefined) {
      return true;
    }
    const timeSinceLastCall = time - lastCallTime;
    const timeSinceLastInvoke = time - lastInvokeTime;

    // Умови виклику:
    // 1. Минув інтервал затишшя wait
    // 2. Системний годинник пішов назад (коригування часу)
    // 3. Минув ліміт maxWait при безперервному потоці подій
    return (
      timeSinceLastCall >= wait ||
      timeSinceLastCall < 0 ||
      (hasMaxWait && timeSinceLastInvoke >= maxWait!)
    );
  }

  // Обробник тіку таймера
  function timerExpired(): void {
    const time = now();
    if (shouldInvoke(time)) {
      trailingEdge(time);
      return;
    }
    // Перезапуск таймера на залишок часу
    timerId = setTimeout(timerExpired, remainingWait(time));
  }

  // Обробка заднього фронту (trailing edge)
  function trailingEdge(time: number): TReturn | undefined {
    timerId = undefined;

    // Викликаємо, лише якщо був хоча б один виклик і увімкнено trailing
    if (trailing && lastArgs) {
      return invoke(time);
    }
    lastArgs = undefined;
    lastThis = undefined;
    return result;
  }

  // Обробка переднього фронту (leading edge)
  function leadingEdge(time: number): TReturn {
    lastInvokeTime = time;
    // Запуск фонового таймера для відліку затишшя або maxWait
    timerId = setTimeout(timerExpired, wait);
    return leading ? invoke(time) : result!;
  }

  // Скасування запланованого виконання
  function cancel(): void {
    if (timerId !== undefined) {
      clearTimeout(timerId);
    }
    lastInvokeTime = 0;
    lastArgs = undefined;
    lastCallTime = undefined;
    lastThis = undefined;
    timerId = undefined;
  }

  // Примусове негайне виконання відкладеного виклику
  function flush(): TReturn | undefined {
    return timerId === undefined ? result : trailingEdge(now());
  }

  // Перевірка активності
  function isPending(): boolean {
    return timerId !== undefined;
  }

  // Головна функція-обгортка
  function debounced(this: any, ...args: TArgs): TReturn | undefined {
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
        // Примусовий виклик по досягненню maxWait
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

/**
 * Тротлінг, побудований на базі універсального ядра дебаунсу
 */
export function throttle<TArgs extends any[], TReturn>(
  fn: (...args: TArgs) => TReturn,
  wait: number,
  options: ThrottleOptions = {}
): DebouncedFunction<TArgs, TReturn> {
  const leading = 'leading' in options ? Boolean(options.leading) : true;
  const trailing = 'trailing' in options ? Boolean(options.trailing) : true;

  return debounce(fn, wait, {
    leading,
    trailing,
    maxWait: wait,
  });
}
