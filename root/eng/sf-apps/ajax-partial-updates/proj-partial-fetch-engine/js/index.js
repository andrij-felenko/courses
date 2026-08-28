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
