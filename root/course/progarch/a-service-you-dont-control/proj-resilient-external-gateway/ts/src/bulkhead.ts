import type { BulkheadConfig } from './types.ts';
import { BulkheadFullError } from './types.ts';

/**
 * Перебірка (Bulkhead) на основі асинхронного семафора.
 * Ізолює ресурси процесу, обмежуючи максимальну кількість паралельних
 * запитів до зовнішньої служби для запобігання голодуванню за законом Літтла.
 */
export class Bulkhead {
  private readonly config: BulkheadConfig;
  private activeCalls = 0;
  private readonly waitingQueue: Array<() => void> = [];

  constructor(config: BulkheadConfig) {
    this.config = config;
  }

  /**
   * Запитує дозвіл на виконання. Повертає функцію вивільнення слота.
   * Якщо ліміт вичерпано, очікує в черзі. Якщо черга заповнена — миттєво відхиляє.
   */
  async acquire(): Promise<() => void> {
    if (this.activeCalls < this.config.maxConcurrent) {
      this.activeCalls++;
      return this.createReleaser();
    }

    if (this.waitingQueue.length >= this.config.maxQueueSize) {
      throw new BulkheadFullError();
    }

    return new Promise<() => void>((resolve) => {
      this.waitingQueue.push(() => {
        this.activeCalls++;
        resolve(this.createReleaser());
      });
    });
  }

  /**
   * Виконує асинхронну дію під захистом перебірки з автоматичним вивільненням слота.
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    const release = await this.acquire();
    try {
      return await fn();
    } finally {
      release();
    }
  }

  private createReleaser(): () => void {
    let released = false;
    return () => {
      if (released) return;
      released = true;
      this.activeCalls--;

      if (this.waitingQueue.length > 0) {
        const next = this.waitingQueue.shift();
        if (next) next();
      }
    };
  }

  getMetrics() {
    return {
      activeCalls: this.activeCalls,
      queueDepth: this.waitingQueue.length,
      availableSlots: Math.max(0, this.config.maxConcurrent - this.activeCalls),
    };
  }
}
