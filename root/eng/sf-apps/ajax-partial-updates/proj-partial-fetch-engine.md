# ⚙️ Стійкий клієнтський рушій фонових запитів: стрімінг, гонки відповідей та DOM Morphing

У більшості навчальних прикладів фонові запити зводяться до банального виклику `fetch(url).then(res => res.json()).then(render)`. У реальних багатокомпонентних вебзастосунках такий наївний підхід негайно породжує каскад критичних архітектурних дефектів.

Коли користувач швидко взаємодіє з інтерфейсом (вводить пошуковий запит, клацає фільтри каталогу, перемикає вкладки), виникають такі типові проблеми:
1. **Гонка відповідей (Out-of-order responses):** повільний перший запит, що натрапив на затримку мережі, повертається пізніше за швидкий другий запит і безконтрольно перезаписує актуальний інтерфейс застарілими даними.
2. **Втрата фокусу та позиції каретки (Focus & Selection Loss):** наївна заміна фрагмента через `element.innerHTML = newHtml` повністю знищує реальні DOM-вузли. Якщо користувач у цей момент друкував у полі введення, фокус зникає, екран смикається, а курсор скидається на початок рядка.
3. **Зависання в разі мережевого збою:** тимчасовий обрив мобільного інтернету залишає інтерфейс у вічному стані завантаження, якщо в клієнті відсутня стратегія повторних спроб (*Retry Policy*).
4. **Марнотратне споживання трафіку й процесора:** якщо користувач змінив намір, попередній запит продовжує виконуватися, споживаючи заряд батареї мобільного пристрою та обчислювальні ресурси сервера.

Нижче наведено модульний клієнтський рушій часткового оновлення `PartialUpdateEngine`, який комплексно розв'язує перелічені проблеми на рівні єдиного надійного пайплайну.

---

## Архітектурний дизайн рушія

Архітектура `PartialUpdateEngine` спирається на п'ять фундаментальних підсистем:

```
[Подія UI] ──> [Диспетчер каналів: AbortController] ──> [Мережевий транспорт: Fetch + Backoff]
                                                                      │
                                                                      ▼
[Збереження фокусу] <── [DOM Morphing Engine] <── [Потоковий парсер ReadableStream]
```

1. **Менеджер ізольованих каналів (`channels Map`):** кожен інтерактивний віджет має свій унікальний ключ каналу (`channelKey`, наприклад, `search-box` або `cart-drawer`). Запити в різних каналах виконуються паралельно й незалежно, але всередині одного каналу поява нового наміру миттєво скасовує попередній незавершений запит через `AbortController.abort()`.
2. **Монотонне версіонування (`globalSequence`):** навіть якщо старий запит не вдалося скасувати миттєво на рівні сокета, перевірка `requestId === activeChannel.requestId` гарантує, що застаріла відповідь буде відкинута без модифікації стану.
3. **Експоненційний повтор із джитером (`executeWithRetry`):** у разі тимчасової помилки мережі або отримання статусів HTTP 503/504 рушій повторює спробу за формулою `t = base · 2ⁿ + random()`. Водночас клієнтські помилки HTTP 4xx (неправильні параметри, відсутність авторизації) не ретраяться, запобігаючи паразитному навантаженню.
4. **Потоковий декодер (`readStream`):** читання тіла відповіді здійснюється чанками за допомогою `ReadableStream` і `TextDecoder`, що дозволяє рендерити проміжний HTML без очікування фінального байта.
5. **Алгоритм точкового морфінгу DOM (`morphElement`):** замість грубого видалення вузлів алгоритм рекурсивно порівнює наявні DOM-елементи з віртуальним деревом нової розмітки. Він оновлює тільки змінені атрибути, додає відсутні вузли, а перед мутацією фіксує активний елемент `document.activeElement` та позиції виділення `selectionStart`/`selectionEnd`, повністю відновлюючи їх після завершення патчингу.

### Покроковий механізм збереження фокусу

При прямій заміні вузлів браузерний рушій змушений викликати подію `blur` на активному елементі, оскільки видалений вузол більше не належить дереву документа. Щоб уникнути цього дефекту, рушій виконує чотирифазну процедуру узгодження:
* **Фаза 1 (Snapshot):** перед початком звіряння рушій перевіряє `document.activeElement`. Якщо активний елемент знаходиться всередині оновлюваного контейнера і має унікальний ідентифікатор `id`, рушій запам'ятовує його селектор, а також зчитує властивості `selectionStart` та `selectionEnd`.
* **Фаза 2 (In-place Mutation):** під час обходу дерева, якщо теги збігаються (`realEl.tagName === virtEl.tagName`), реальний DOM-вузол не видаляється. Натомість синхронізуються лише його властивості (`setAttribute`, `removeAttribute`, `nodeValue`). Оскільки сам вузол залишається в DOM, браузер не втрачає прив'язку фокусу.
* **Фаза 3 (Child Reconciliation):** дочірні елементи зіставляються за індексами; зайві вузли видаляються, нові додаються в кінець списку.
* **Фаза 4 (Restoration):** якщо активний елемент усе ж зазнав перебудови, рушій знаходить його за збереженим селектором, викликає метод `focus()` і повертає каретку на точну позицію `setSelectionRange(start, end)`.

---

## Реалізація рушія

:::tabs
```ts
// TypeScript: Production-ready Partial Update & Morphing Engine

export interface FetchOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: string;
  maxRetries?: number;
  baseDelayMs?: number;
  onChunk?: (accumulatedHtml: string) => void;
}

export class PartialUpdateEngine {
  private channels = new Map<string, { controller: AbortController; requestId: number }>();
  private globalSequence = 0;

  /**
   * Виконує фоновий запит із прив'язкою до каналу та оновлює цільовий DOM-елемент.
   */
  async updateElement(
    channelKey: string,
    targetSelector: string,
    url: string,
    options: FetchOptions = {}
  ): Promise<boolean> {
    const targetEl = document.querySelector(targetSelector);
    if (!targetEl) {
      console.warn(`[PartialEngine] Цільовий селектор «${targetSelector}» не знайдено.`);
      return false;
    }

    // 1. Скасування попереднього незавершеного запиту на цьому каналі
    const existing = this.channels.get(channelKey);
    if (existing) {
      existing.controller.abort();
    }

    const currentRequestId = ++this.globalSequence;
    const controller = new AbortController();
    this.channels.set(channelKey, { controller, requestId: currentRequestId });

    try {
      const htmlPayload = await this.executeWithRetry(
        url,
        options,
        controller.signal,
        currentRequestId,
        channelKey
      );

      // Якщо за час запиту надійшов новіший намір — ігноруємо цей результат
      const activeChannel = this.channels.get(channelKey);
      if (!activeChannel || activeChannel.requestId !== currentRequestId) {
        return false;
      }

      // 2. Безпечна точкова підміна DOM зі збереженням фокусу
      this.morphElement(targetEl, htmlPayload);
      return true;
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Очікуване скасування — старий запит поступився місцем новому
        return false;
      }
      this.renderErrorState(targetEl, err.message);
      throw err;
    } finally {
      const current = this.channels.get(channelKey);
      if (current && current.requestId === currentRequestId) {
        this.channels.delete(channelKey);
      }
    }
  }

  /**
   * Виконання мережевого виклику з потоковим читанням та експоненційним повтором.
   */
  private async executeWithRetry(
    url: string,
    options: FetchOptions,
    signal: AbortSignal,
    requestId: number,
    channelKey: string
  ): Promise<string> {
    const maxRetries = options.maxRetries ?? 2;
    const baseDelay = options.baseDelayMs ?? 300;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(url, {
          method: options.method || 'GET',
          headers: {
            'Accept': 'text/html, application/xhtml+xml',
            ...(options.headers || {}),
          },
          body: options.body,
          signal,
        });

        if (!response.ok) {
          // Помилки клієнта (4xx) не ретраїмо, 503/504 — ретраїмо
          if (response.status >= 400 && response.status < 500) {
            throw new Error(`HTTP ${response.status}: Помилка запиту клієнта`);
          }
          if (attempt === maxRetries) {
            throw new Error(`HTTP ${response.status}: Сервер тимчасово недоступний`);
          }
          await this.delayBackoff(attempt, baseDelay, signal);
          continue;
        }

        // Потокове зчитування байтів
        if (response.body && options.onChunk) {
          return await this.readStream(response.body, options.onChunk, signal);
        }

        return await response.text();
      } catch (err: any) {
        if (err.name === 'AbortError') throw err;
        if (attempt === maxRetries) throw err;
        await this.delayBackoff(attempt, baseDelay, signal);
      }
    }

    throw new Error('Вичерпано ліміт спроб підключення');
  }

  /**
   * Потокове читання чанків через ReadableStream і TextDecoder.
   */
  private async readStream(
    stream: ReadableStream<Uint8Array>,
    onChunk: (accumulatedHtml: string) => void,
    signal: AbortSignal
  ): Promise<string> {
    const reader = stream.getReader();
    const decoder = new TextDecoder('utf-8');
    let accumulated = '';

    while (!signal.aborted) {
      const { done, value } = await reader.read();
      if (done) break;
      accumulated += decoder.decode(value, { stream: true });
      onChunk(accumulated);
    }

    accumulated += decoder.decode();
    return accumulated;
  }

  /**
   * Розрахунок затримки Exponential Backoff з додаванням випадкового джитера.
   */
  private async delayBackoff(attempt: number, baseMs: number, signal: AbortSignal): Promise<void> {
    const jitter = Math.random() * baseMs;
    const delay = Math.min(baseMs * Math.pow(2, attempt) + jitter, 4000);

    return new Promise((resolve, reject) => {
      const timer = setTimeout(resolve, delay);
      signal.addEventListener('abort', () => {
        clearTimeout(timer);
        reject(new DOMException('Aborted', 'AbortError'));
      }, { once: true });
    });
  }

  /**
   * Алгоритм DOM Morphing: порівняння та оновлення вузлів без скидання фокусу.
   */
  private morphElement(current: Element, newHtml: string): void {
    const template = document.createElement('template');
    template.innerHTML = newHtml.trim();
    const targetRoot = template.content.firstElementChild;

    if (!targetRoot) return;

    // Зберігаємо стан активного фокусу та позицію каретки
    const activeEl = document.activeElement as HTMLElement | null;
    let focusedSelector: string | null = null;
    let selectionStart: number | null = null;
    let selectionEnd: number | null = null;

    if (activeEl && current.contains(activeEl) && activeEl.id) {
      focusedSelector = `#${activeEl.id}`;
      if ('selectionStart' in activeEl) {
        const input = activeEl as HTMLInputElement;
        selectionStart = input.selectionStart;
        selectionEnd = input.selectionEnd;
      }
    }

    // Рекурсивна підміна вузлів
    this.reconcileNodes(current, targetRoot);

    // Відновлюємо фокус і каретку
    if (focusedSelector) {
      const restoredEl = document.querySelector(focusedSelector) as HTMLElement | null;
      if (restoredEl) {
        restoredEl.focus();
        if (selectionStart !== null && selectionEnd !== null && 'setSelectionRange' in restoredEl) {
          (restoredEl as HTMLInputElement).setSelectionRange(selectionStart, selectionEnd);
        }
      }
    }
  }

  /**
   * Точкове узгодження двох дерев елементів.
   */
  private reconcileNodes(realNode: Node, virtualNode: Node): void {
    if (realNode.nodeType === Node.TEXT_NODE && virtualNode.nodeType === Node.TEXT_NODE) {
      if (realNode.nodeValue !== virtualNode.nodeValue) {
        realNode.nodeValue = virtualNode.nodeValue;
      }
      return;
    }

    if (realNode.nodeType !== Node.ELEMENT_NODE || virtualNode.nodeType !== Node.ELEMENT_NODE) {
      realNode.parentNode?.replaceChild(virtualNode.cloneNode(true), realNode);
      return;
    }

    const realEl = realNode as Element;
    const virtEl = virtualNode as Element;

    if (realEl.tagName !== virtEl.tagName) {
      realEl.parentNode?.replaceChild(virtEl.cloneNode(true), realEl);
      return;
    }

    // Синхронізація атрибутів
    const realAttrs = Array.from(realEl.attributes);
    const virtAttrs = Array.from(virtEl.attributes);

    for (const attr of virtAttrs) {
      if (realEl.getAttribute(attr.name) !== attr.value) {
        realEl.setAttribute(attr.name, attr.value);
      }
    }
    for (const attr of realAttrs) {
      if (!virtEl.hasAttribute(attr.name)) {
        realEl.removeAttribute(attr.name);
      }
    }

    // Синхронізація дочірніх вузлів
    const realChildren = Array.from(realEl.childNodes);
    const virtChildren = Array.from(virtEl.childNodes);

    const maxLen = Math.max(realChildren.length, virtChildren.length);
    for (let i = 0; i < maxLen; i++) {
      if (!realChildren[i] && virtChildren[i]) {
        realEl.appendChild(virtChildren[i].cloneNode(true));
      } else if (realChildren[i] && !virtChildren[i]) {
        realEl.removeChild(realChildren[i]);
      } else if (realChildren[i] && virtChildren[i]) {
        this.reconcileNodes(realChildren[i], virtChildren[i]);
      }
    }
  }

  private renderErrorState(container: Element, message: string): void {
    const errorBox = document.createElement('div');
    errorBox.className = 'fetch-error-toast';
    errorBox.style.cssText = 'background: #fdecea; color: #c0392b; padding: 8px 12px; border-radius: 4px; margin-top: 8px; font-size: 13px;';
    errorBox.textContent = `Помилка оновлення: ${message}`;
    container.prepend(errorBox);

    setTimeout(() => errorBox.remove(), 4000);
  }
}
```
```js
// JavaScript (ES2022): Lightweight Runtime Engine

export class PartialUpdateEngine {
  constructor() {
    this.channels = new Map();
    this.globalSequence = 0;
  }

  async updateElement(channelKey, targetSelector, url, options = {}) {
    const targetEl = document.querySelector(targetSelector);
    if (!targetEl) return false;

    const existing = this.channels.get(channelKey);
    if (existing) {
      existing.controller.abort();
    }

    const currentRequestId = ++this.globalSequence;
    const controller = new AbortController();
    this.channels.set(channelKey, { controller, requestId: currentRequestId });

    try {
      const htmlPayload = await this.executeWithRetry(
        url,
        options,
        controller.signal
      );

      const activeChannel = this.channels.get(channelKey);
      if (!activeChannel || activeChannel.requestId !== currentRequestId) {
        return false;
      }

      this.morphElement(targetEl, htmlPayload);
      return true;
    } catch (err) {
      if (err.name === 'AbortError') return false;
      this.renderErrorState(targetEl, err.message);
      throw err;
    } finally {
      const current = this.channels.get(channelKey);
      if (current && current.requestId === currentRequestId) {
        this.channels.delete(channelKey);
      }
    }
  }

  async executeWithRetry(url, options, signal) {
    const maxRetries = options.maxRetries ?? 2;
    const baseDelay = options.baseDelayMs ?? 300;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        const response = await fetch(url, {
          method: options.method || 'GET',
          headers: {
            'Accept': 'text/html, application/xhtml+xml',
            ...(options.headers || {})
          },
          body: options.body,
          signal
        });

        if (!response.ok) {
          if (response.status >= 400 && response.status < 500) {
            throw new Error(`HTTP ${response.status}: Помилка клієнта`);
          }
          if (attempt === maxRetries) {
            throw new Error(`HTTP ${response.status}: Збій сервера`);
          }
          await this.delayBackoff(attempt, baseDelay, signal);
          continue;
        }

        return await response.text();
      } catch (err) {
        if (err.name === 'AbortError') throw err;
        if (attempt === maxRetries) throw err;
        await this.delayBackoff(attempt, baseDelay, signal);
      }
    }
  }

  async delayBackoff(attempt, baseMs, signal) {
    const jitter = Math.random() * baseMs;
    const delay = Math.min(baseMs * Math.pow(2, attempt) + jitter, 4000);

    return new Promise((resolve, reject) => {
      const timer = setTimeout(resolve, delay);
      signal.addEventListener('abort', () => {
        clearTimeout(timer);
        reject(new DOMException('Aborted', 'AbortError'));
      }, { once: true });
    });
  }

  morphElement(current, newHtml) {
    const template = document.createElement('template');
    template.innerHTML = newHtml.trim();
    const targetRoot = template.content.firstElementChild;
    if (!targetRoot) return;

    this.reconcileNodes(current, targetRoot);
  }

  reconcileNodes(realNode, virtualNode) {
    if (realNode.nodeType === Node.TEXT_NODE && virtualNode.nodeType === Node.TEXT_NODE) {
      if (realNode.nodeValue !== virtualNode.nodeValue) {
        realNode.nodeValue = virtualNode.nodeValue;
      }
      return;
    }

    if (realNode.nodeType !== Node.ELEMENT_NODE || virtualNode.nodeType !== Node.ELEMENT_NODE) {
      realNode.parentNode?.replaceChild(virtualNode.cloneNode(true), realNode);
      return;
    }

    if (realNode.tagName !== virtualNode.tagName) {
      realNode.parentNode?.replaceChild(virtualNode.cloneNode(true), realNode);
      return;
    }

    for (const attr of virtualNode.attributes) {
      if (realNode.getAttribute(attr.name) !== attr.value) {
        realNode.setAttribute(attr.name, attr.value);
      }
    }
    for (const attr of Array.from(realNode.attributes)) {
      if (!virtualNode.hasAttribute(attr.name)) {
        realNode.removeAttribute(attr.name);
      }
    }

    const realChildren = Array.from(realNode.childNodes);
    const virtChildren = Array.from(virtualNode.childNodes);
    const maxLen = Math.max(realChildren.length, virtChildren.length);

    for (let i = 0; i < maxLen; i++) {
      if (!realChildren[i] && virtChildren[i]) {
        realNode.appendChild(virtChildren[i].cloneNode(true));
      } else if (realChildren[i] && !virtChildren[i]) {
        realNode.removeChild(realChildren[i]);
      } else if (realChildren[i] && virtChildren[i]) {
        this.reconcileNodes(realChildren[i], virtChildren[i]);
      }
    }
  }

  renderErrorState(container, message) {
    const errorBox = document.createElement('div');
    errorBox.className = 'fetch-error-toast';
    errorBox.textContent = `Помилка: ${message}`;
    container.prepend(errorBox);
    setTimeout(() => errorBox.remove(), 4000);
  }
}
```
:::

---

## Практичні пастки та крайові випадки

Під час інтеграції фонового рушія слід враховувати такі підводні камені:

1. **Витік слухачів подій (Event Listener Leaks):** під час прямої заміни вузлів через `replaceChild` підвішені через `addEventListener` функції можуть залишатися в пам'яті, якщо на них посилаються зовнішні замикання. Використовуйте делегування подій на рівні кореневого контейнера (`document.addEventListener('click', handler)`) замість навішування обробників на кожен динамічний рядок таблиці.
2. **Простір імен SVG та MathML:** стандартний метод `document.createElement('svg')` створює невалідний HTML-елемент. Якщо оновлюваний фрагмент містить графіку, необхідно використовувати фабрику `document.createElementNS('http://www.w3.org/2000/svg', tagName)` або парсити фрагмент через `<template>`, як реалізовано вище.
3. **Специфіка `selectionStart` у нестандартних інпутах:** звернення до властивості `selectionStart` у полях `type="email"` або `type="number"` у браузерах на базі Chromium викликає виняток `DOMException`. Перевіряйте тип інпуту перед спробою зчитати координати курсора.
4. **Необроблені відхилення промісів (Unhandled Rejections):** коли `AbortController.abort()` перериває виконання виклику `fetch()`, середовище виконання генерує відхилений проміс із помилкою типу `AbortError`. Якщо клієнтський обробник не містить фільтрації за `err.name === 'AbortError'`, у глобальну консоль вилітатимуть повідомлення про критичний збій програми.
5. **Скидання внутрішньої прокрутки контейнерів (Scroll Retention):** якщо всередині оновлюваного блока знаходиться список із власним скролом (`overflow-y: auto`), алгоритм морфінгу повинен зчитувати властивості `scrollTop` і `scrollLeft` перед патчингом і повертати їх після завершення реконсиляції, інакше список щоразу смикатиметься до нульової координати.
6. **Робота з полями форматованого тексту (`contenteditable`):** у разі оновлення блоків зі змінним HTML-вмістом використання стандартних числових зсувів каретки є недостатнім — необхідно зберігати глобальний об'єкт `Range` через API `window.getSelection()`.
