/**
 * reporters/summary-reporter.js — Форматування метрик k6 у машинозчитуваний звіт.
 * Створює структурований висновок для блокуючого шлюзу CI/CD Acceptance Gate.
 */

export class SummaryReporter {
  /**
   * Аналізує сирі метрики k6 та формує висновок щодо виконання контрактних SLA.
   * @param {object} data - Об'єкт підсумкових метрик від k6 handleSummary(data)
   * @param {string} projectName - Назва аудитованого проєкту
   * @returns {object}
   */
  generate(data, projectName = 'ContractorServiceAudit') {
    const metrics = (data && data.metrics) || {};

    // Отримання ключових агрегованих показників
    const reqDuration = metrics.http_req_duration ? metrics.http_req_duration.values : {};
    const reqFailed = metrics.http_req_failed ? metrics.http_req_failed.values : {};
    const checks = metrics.contract_checks_success ? metrics.contract_checks_success.values : {};
    const bizDuration = metrics.business_transaction_duration
      ? metrics.business_transaction_duration.values
      : {};

    const p95Latency = reqDuration['p(95)'] !== undefined ? Math.round(reqDuration['p(95)']) : 0;
    const p99Latency = reqDuration['p(99)'] !== undefined ? Math.round(reqDuration['p(99)']) : 0;
    const failureRate = reqFailed.rate !== undefined ? Number((reqFailed.rate * 100).toFixed(2)) : 0;
    const checksRate = checks.rate !== undefined ? Number((checks.rate * 100).toFixed(2)) : 100;
    const bizP95 = bizDuration['p(95)'] !== undefined ? Math.round(bizDuration['p(95)']) : 0;

    // Перевірка контрактних критеріїв
    const criteria = [
      {
        name: 'HTTP Error Rate (відсоток збоїв)',
        threshold: '< 1.0%',
        actual: `${failureRate}%`,
        passed: failureRate < 1.0,
      },
      {
        name: 'HTTP Latency p(95) (95-й процентиль затримки)',
        threshold: '< 400 мс',
        actual: `${p95Latency} мс`,
        passed: p95Latency < 400,
      },
      {
        name: 'HTTP Latency p(99) (99-й процентиль затримки)',
        threshold: '< 800 мс',
        actual: `${p99Latency} мс`,
        passed: p99Latency < 800,
      },
      {
        name: 'Business Transaction p(95) (створення замовлення)',
        threshold: '< 500 мс',
        actual: `${bizP95} мс`,
        passed: bizP95 < 500,
      },
      {
        name: 'Checks Success Rate (успішність валідацій)',
        threshold: '>= 99.0%',
        actual: `${checksRate}%`,
        passed: checksRate >= 99.0,
      },
    ];

    const allPassed = criteria.every((c) => c.passed);
    const verdict = allPassed ? 'ACCEPTED' : 'REJECTED';

    return {
      auditTimestamp: new Date().toISOString(),
      project: projectName,
      acceptanceVerdict: verdict,
      summary: allPassed
        ? 'Система повністю задовольняє контрактні вимоги навантаження та SLA.'
        : 'Виявлено порушення порогів навантаження! Підписання приймального акта заблоковано.',
      slaCriteria: criteria,
      rawMetrics: {
        totalRequests: reqDuration.count || 0,
        averageLatencyMs: Math.round(reqDuration.avg || 0),
        p95LatencyMs: p95Latency,
        p99LatencyMs: p99Latency,
        failureRatePercent: failureRate,
        checksSuccessPercent: checksRate,
      },
    };
  }

  /**
   * Створює текстовий звіт для виводу у stdout терміналу або CI Step Summary.
   * @param {object} report - Об'єкт звіту з generate()
   * @returns {string}
   */
  formatConsole(report) {
    const badge = report.acceptanceVerdict === 'ACCEPTED' ? '✅ ПРИЙНЯТО' : '❌ ВІДХИЛЕНО';
    const lines = [
      '',
      '==================================================================',
      `  ЗВІТ ПРИЙМАЛЬНОГО ТЕСТУВАННЯ НАВАНТАЖЕННЯ: ${report.project}`,
      '==================================================================',
      `Вердикт шлюзу: ${badge}`,
      `Час проведення: ${report.auditTimestamp}`,
      `Підсумок: ${report.summary}`,
      '',
      'Таблиця перевірки контрактних SLA:',
      '------------------------------------------------------------------',
    ];

    for (const c of report.slaCriteria) {
      const status = c.passed ? '[PASS]' : '[FAIL]';
      lines.push(
        `  ${status.padEnd(8)} ${c.name.padEnd(42)} Поріг: ${c.threshold.padEnd(10)} Факт: ${c.actual}`
      );
    }

    lines.push('------------------------------------------------------------------');
    lines.push(
      `Всього запитів: ${report.rawMetrics.totalRequests} | Сер. затримка: ${report.rawMetrics.averageLatencyMs}мс | p(95): ${report.rawMetrics.p95LatencyMs}мс | Відмови: ${report.rawMetrics.failureRatePercent}%`
    );
    lines.push('==================================================================\n');

    return lines.join('\n');
  }
}
