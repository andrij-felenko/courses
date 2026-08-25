# ⚙️ Промислова реалізація обмежувачів частоти подій

У користувацьких інтерфейсах та клієнтських системах наївні реалізації дебаунсу через просте скидання `clearTimeout` ламаються за перших же нестандартних умов. Серед типових аварійних сценаріїв: втрата фінального стану форми при закритті вікна, нескінченне відкладання виклику при безперервному вводі тексту (голодування обробника), витік оперативної пам'яті через утримання замикань на видалені вузли DOM, а також взаємне блокування та гонки асинхронних промісів при швидкому наборі пошукових запитів.

Нижче наведено повний розбір архітектури типізованого обмежувача подій мовою TypeScript, спроєктованого за принципами надійності промислового рівня.

## Задача й архітектурні інваріанти

Надійний обмежувач частоти викликів повинен забезпечувати набір суворих математичних та поведінкових гарантій:

1. **Точність монотонного часу.** Використання `performance.now()` замість `Date.now()`. Системний годинник `Date.now()` може змінюватися в довільний бік внаслідок корекції часу операційною системою через протокол NTP або ручного переведення годинника користувачем. Якщо годинник стрибне назад, різниця `now - lastCallTime` стане від'ємною, що без спеціальної обробки призведе до блокування таймера на невизначений термін. Монотонний таймер `performance.now()` гарантує неперервне зростання значення від моменту старту середовища.
2. **Підтримка комбінованих фаз спрацьовування.** Можливість виконання функції на передньому фронті (`leading: true`), на задньому фронті після затишшя (`trailing: true`) або в обох точках одночасно. У разі ввімкнення обох прапорців функція має виконатися негайно на першу подію, а після завершення серії подій — виконатися повторно з останніми актуальними аргументами.
3. **Гарантія максимального очікування (`maxWait`).** Запобігання голодуванню (starvation). Якщо події надходять частіше, ніж заданий інтервал затишшя `wait`, звичайний trailing debounce скидатиме таймер нескінченно, і функція ніколи не виконається. Параметр `maxWait` задає жорстку верхню межу затримки від моменту першого виклику.
4. **Повний контроль життєвого циклу.** Надання методів `.cancel()` для безпечного скасування запланованих таймерів при знищенні компонентів інтерфейсу, `.flush()` для негайного примусового виконання відкладеної роботи перед закриттям документа та `.isPending()` для перевірки наявності запланованого стану.
5. **Коректне керування контекстом `this` та пам'яттю.** Фіксація останніх актуальних параметрів виклику з обов'язковим обнуленням посилань на масив аргументів і контекст `this` одразу після виконання цільової функції. Це унеможливлює витоки пам'яті через утримання великих структур даних у замиканні.

## Повна реалізація універсального ядра

Нижче наведено повний вихідний код типізованого модуля, що об'єднує дебаунс та тротлінг на спільній кодовій базі:

:::tabs
```ts
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
```
```js
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
```
:::

## Анатомія алгоритму та розбір станів

Робота наведеного ядра ґрунтується на синхронізації трьох часових міток:

- `lastCallTime` — момент останнього виклику функції-обгортки клієнтським кодом. Оновлюється на кожну подію вхідного потоку.
- `lastInvokeTime` — момент останнього фактичного виконання цільової функції `fn`. Оновлюється лише тоді, коли функція реально викликається через `invoke()`.
- `timerId` — числовий дескриптор активного макрозадачного таймера браузера або середовища Node.js.

Коли настає тік таймера `timerExpired()`, функція не виконує цільовий код сліпо. Вона обчислює дві дельти:

```
timeSinceLastCall   = now() − lastCallTime
timeSinceLastInvoke = now() − lastInvokeTime
```

Якщо `timeSinceLastCall < wait`, це означає, що після запуску таймера користувач згенерував нову подію (наприклад, натиснув ще одну клавішу). У такому разі інтервал затишшя ще не витримано. Таймер не знищується, а перераховує залишок часу через `remainingWait()` і перезапускається рівно на той час, якого бракує до повного вікна `wait`. Якщо ж активовано `maxWait`, таймер перевіряє, що `timeSinceLastInvoke` не перевищує ліміт: якщо ліміт вичерпано, функція викликається примусово, перериваючи нескінченний цикл відкладання.

## Спеціалізований тротлінг кадрової розгортки: `rafThrottle`

Для маніпуляцій із деревом DOM, синхронізації положення курсора, скролу та відмальовки графіки таймери `setTimeout` створюють мікросмикання (джиттер) через невідповідність тактової частоти таймерів ОС частоті вертикальної синхронізації дисплея (VSync).

Коли монітор працює на частоті 60 Гц, новий кадр відмальовується кожні 16.67 мс, а на частоті 120 Гц — кожні 8.33 мс. Таймер `setTimeout(fn, 16)` потрапляє у випадкові моменти відносно фази кадру. Якщо колбек таймера виконається відразу після початку розрахунку стилів, його зміни DOM потраплять лише в наступний кадр, створивши затримку у 33 мс і візуальний ривок анімації.

Нижче наведено спеціалізовану реалізацію на базі `requestAnimationFrame`:

:::tabs
```ts
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
```
```js
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
```
:::

## Пастки, крайові випадки та архітектурні дефекти

### 1. Асинхронні перегони (Race Conditions) при живому пошуку

Якщо функція, що передається в `debounce`, виконує мережевий запит `fetch`, звичайний дебаунс лише зменшує кількість відправлених HTTP-пакетів, але не контролює порядок повернення відповідей з мережі. Запит на пошук короткого слова `"ки"` може оброблятися базою даних довше (наприклад, 400 мс через великий обсяг збігів), ніж наступний уточнений запит на слово `"київ"` (50 мс).

Якщо перший запит завершиться останнім у часі, його колбек перезапише актуальні результати пошуку для `"київ"` застарілими даними для `"ки"`.

**Архітектурне вирішення:** комбінація `debounce` зі стандартним механізмом скасування запитів `AbortController`:

```ts
class SearchService {
  private abortController: AbortController | null = null;

  public search = debounce(async (query: string) => {
    // Скасовуємо попередній незавершений мережевий запит
    if (this.abortController) {
      this.abortController.abort();
    }
    this.abortController = new AbortController();

    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
        signal: this.abortController.signal,
      });
      const data = await response.json();
      this.renderResults(data);
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        console.error('Помилка пошуку:', err);
      }
    }
  }, 300);

  private renderResults(data: any): void {
    // Оновлення списку результатів у DOM
  }
}
```

### 2. Витік пам'яті через замикання при знищенні компонентів

Якщо компонент інтерфейсу підписується на подію `window.addEventListener('resize', handler)`, де `handler` створено через `debounce(fn, 500)`, закриття діалогового вікна чи перехід на інший екран без виклику `cancel()` призводить до важкого витоку пам'яті. Запланований таймер `setTimeout` залишається у глобальній черзі макрозадач рушія JavaScript і тримає посилання на функцію `handler`. Функція `handler` через своє лексичне замикання утримує екземпляр компонента, його внутрішній стан та ціле піддерево відмонтованих DOM-вузлів.

**Архітектурне вирішення:** обов'язкове очищення у деструкторах або хуках життєвого циклу:

```ts
import { useEffect, useMemo, useRef } from 'react';

export function useDebouncedCallback<TArgs extends any[]>(
  callback: (...args: TArgs) => void,
  delay: number
) {
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  const debounced = useMemo(
    () => debounce((...args: TArgs) => callbackRef.current(...args), delay),
    [delay]
  );

  useEffect(() => {
    // Гарантоване скасування таймера при демонтажі компонента
    return () => debounced.cancel();
  }, [debounced]);

  return debounced;
}
```

### 3. Пул синтетичних подій (Synthetic Event Pooling)

У старих версіях бібліотеки React (до версії 17) об'єкти подій `SyntheticEvent` повторно використовувалися для мінімізації навантаження на збирач сміття (Garbage Collector). Щойно синхронний обробник завершував роботу, React очищав усі поля об'єкта події, встановлюючи їх у `null`. Якщо такий об'єкт події передавався у `debounced`-функцію, спроба прочитати `event.target.value` через 300 мс викидала помилку `TypeError: Cannot read properties of null`.

**Архітектурне вирішення:** збереження необхідних скалярних примітивів (рядків, чисел) до входу у функцію обмежувача або явний виклик методу `event.persist()`:

```ts
const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
  // Витягуємо скалярний рядок ДО передачі в асинхронну чергу
  const nextValue = e.target.value;
  debouncedSearch(nextValue);
};
```
