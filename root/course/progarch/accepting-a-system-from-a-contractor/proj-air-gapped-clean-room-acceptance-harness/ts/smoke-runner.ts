/**
 * smoke-runner.ts — Виконання наскрізних димових HTTP-сценаріїв для верифікації
 * критичних бізнес-транзакцій та зондів здоров'я переданого сервісу.
 */

import type { ProbeResult, SmokeAuditResult, SmokeEndpointConfig } from './types.ts';

export class SmokeRunner {
  /**
   * Виконує серію контрольних димових HTTP-запитів до розгорнутого сервісу.
   */
  public async run(
    baseUrl: string,
    endpoints: SmokeEndpointConfig[]
  ): Promise<SmokeAuditResult> {
    const cleanBase = baseUrl.replace(/\/+$/, '');
    const results: ProbeResult[] = [];
    let passedProbes = 0;

    for (const ep of endpoints) {
      const url = `${cleanBase}/${ep.path.replace(/^\/+/, '')}`;
      const start = performance.now();

      try {
        const headers: Record<string, string> = { ...ep.headers };
        let body: string | undefined = undefined;

        if (ep.payload && (ep.method === 'POST' || ep.method === 'PUT')) {
          headers['Content-Type'] = 'application/json';
          body = JSON.stringify(ep.payload);
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), ep.maxLatencyMs + 2000);

        const response = await fetch(url, {
          method: ep.method,
          headers,
          body,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        const latencyMs = Math.round(performance.now() - start);

        const isStatusMatch = response.status === ep.expectedStatus;
        const isLatencyMatch = latencyMs <= ep.maxLatencyMs;
        const passed = isStatusMatch && isLatencyMatch;

        let error: string | undefined;
        if (!isStatusMatch) {
          error = `Невідповідний статус-код HTTP: отримано ${response.status}, очікувалося ${ep.expectedStatus}`;
        } else if (!isLatencyMatch) {
          error = `Порушення SLA затримки: ${latencyMs}мс > ліміту ${ep.maxLatencyMs}мс`;
        }

        if (passed) passedProbes++;

        results.push({
          name: ep.name,
          url,
          status: response.status,
          latencyMs,
          passed,
          error,
        });
      } catch (err) {
        const latencyMs = Math.round(performance.now() - start);
        const message = err instanceof Error ? err.message : String(err);

        results.push({
          name: ep.name,
          url,
          status: 0,
          latencyMs,
          passed: false,
          error: `Мережева помилка виконання димового запиту: ${message}`,
        });
      }
    }

    const totalProbes = endpoints.length;
    const failedProbes = totalProbes - passedProbes;
    const passed = totalProbes > 0 && failedProbes === 0;

    return {
      passed,
      totalProbes,
      passedProbes,
      failedProbes,
      results,
    };
  }
}
