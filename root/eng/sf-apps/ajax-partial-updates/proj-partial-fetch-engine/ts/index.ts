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
