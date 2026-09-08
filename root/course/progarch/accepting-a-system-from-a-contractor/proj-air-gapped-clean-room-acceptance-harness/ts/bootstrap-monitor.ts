/**
 * bootstrap-monitor.ts — Моніторинг бюджету часу підняття сервісів «з чистого аркуша»,
 * контроль таймінгу готовності портів (cold-start SLA) та перевірка виділених ресурсів.
 */

import * as net from 'node:net';
import type { BootstrapAuditResult } from './types.ts';

export class BootstrapMonitor {
  /**
   * Опитує доступність TCP-порту сервісу з фіксованим таймаутом та інтервалом спроб.
   */
  public async pollTcpPort(
    host: string,
    port: number,
    timeoutMs: number,
    pollIntervalMs: number = 200
  ): Promise<{ reachable: boolean; elapsedMs: number }> {
    const startTime = performance.now();

    while (performance.now() - startTime < timeoutMs) {
      const isUp = await new Promise<boolean>((resolve) => {
        const socket = new net.Socket();
        socket.setTimeout(pollIntervalMs);

        socket.on('connect', () => {
          socket.destroy();
          resolve(true);
        });

        socket.on('timeout', () => {
          socket.destroy();
          resolve(false);
        });

        socket.on('error', () => {
          socket.destroy();
          resolve(false);
        });

        socket.connect(port, host);
      });

      if (isUp) {
        return {
          reachable: true,
          elapsedMs: Math.round(performance.now() - startTime),
        };
      }

      await new Promise((r) => setTimeout(r, pollIntervalMs));
    }

    return {
      reachable: false,
      elapsedMs: Math.round(performance.now() - startTime),
    };
  }

  /**
   * Вимірює тривалість холодного старту та порівнює результат із контрактним бюджетом SLA.
   */
  public async measureColdStart(
    readinessCheck: () => Promise<boolean>,
    budgetMs: number,
    pollIntervalMs: number = 200
  ): Promise<BootstrapAuditResult> {
    const start = performance.now();

    while (performance.now() - start < budgetMs + 2000) {
      try {
        const isReady = await readinessCheck();
        if (isReady) {
          const elapsed = Math.round(performance.now() - start);
          const isWithinBudget = elapsed <= budgetMs;

          return {
            passed: isWithinBudget,
            coldStartTimeMs: elapsed,
            budgetMs,
            isWithinBudget,
            error: isWithinBudget
              ? undefined
              : `Перевищено контрактний бюджет часу холодного старту: ${elapsed}мс > ${budgetMs}мс`,
          };
        }
      } catch {
        // Сервіс ще не відповідає, очікуємо наступної спроби
      }

      await new Promise((r) => setTimeout(r, pollIntervalMs));
    }

    const elapsed = Math.round(performance.now() - start);
    return {
      passed: false,
      coldStartTimeMs: elapsed,
      budgetMs,
      isWithinBudget: false,
      error: `Таймаут підняття сервісу: перевищено максимальний ліміт очікування (${elapsed}мс)`,
    };
  }
}
