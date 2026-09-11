import {
  PACE_LAYER_NAMES,
  PACE_RANK,
  type DependencyGraph,
  type LintReport,
  type TempoViolation,
} from './types.ts';

/**
 * CLI-репортер результатів перевірки темпів для терміналу та CI/CD пайплайнів.
 * Візуалізує карту темпів, формує деталізовані звіти про порушення та повертає код виходу.
 */
export class CiConsoleReporter {
  /**
   * Генерує структурований звіт LintReport на базі графа та списку порушень.
   */
  public generateReport(
    graph: DependencyGraph,
    violations: TempoViolation[],
    durationMs: number
  ): LintReport {
    const hasCritical = violations.some((v) => v.severity === 'CRITICAL');
    const exitCode = hasCritical ? 1 : 0;

    return {
      timestamp: new Date().toISOString(),
      analyzedModulesCount: graph.modules.size,
      totalDependenciesCount: graph.edges.length,
      violations,
      hasCriticalViolations: hasCritical,
      exitCode,
      executionDurationMs: durationMs,
    };
  }

  /**
   * Друкує повний звіт у консоль.
   */
  public printReport(report: LintReport, graph: DependencyGraph): void {
    console.log('\n' + '='.repeat(80));
    console.log('  TEMPO-LINTER :: Digital Homes Architectural Stability Gate');
    console.log('='.repeat(80));
    console.log(`Час сканування: ${report.timestamp}`);
    console.log(`Проаналізовано модулів: ${report.analyzedModulesCount}`);
    console.log(`Виявлено міжмодульних імпортів: ${report.totalDependenciesCount}`);
    console.log(`Тривалість перевірки: ${report.executionDurationMs} мс`);

    // 1. Друк карти темпів (Pace Map)
    this.printPaceMap(graph);

    // 2. Друк виявлених порушень
    this.printViolations(report.violations);

    // 3. Підсумковий статус CI/CD
    console.log('\n' + '-'.repeat(80));
    if (report.hasCriticalViolations) {
      console.error('❌ CI/CD PIPELINE BLOCKED: Виявлено критичні інверсії темпів!');
      console.error('   Повільні стабільні шари імпортують волатильні модулі.');
      console.error(`   Рекомендація: виправте залежності за вказаними планами. Код виходу: ${report.exitCode}`);
    } else if (report.violations.length > 0) {
      console.warn('⚠️  CI/CD PIPELINE PASSED WITH WARNINGS: Виявлено потенційні ризики темпів.');
      console.warn(`   Код виходу: ${report.exitCode}`);
    } else {
      console.log('✅ CI/CD PIPELINE PASSED: Усі залежності спрямовані правильно (від швидких до повільних).');
      console.log(`   Код виходу: ${report.exitCode}`);
    }
    console.log('='.repeat(80) + '\n');
  }

  /**
   * Виводить таблицю класифікації модулів за шарами темпів.
   */
  private printPaceMap(graph: DependencyGraph): void {
    console.log('\n[ КАРТА АРХІТЕКТУРНИХ ТЕМПІВ (PACE MAP) ]');
    console.log('-'.repeat(80));
    console.log(
      'Модуль'.padEnd(32) +
      'Шар темпу'.padEnd(16) +
      'Ранг'.padEnd(8) +
      'Змін/міс'.padEnd(12) +
      'Комітів'
    );
    console.log('-'.repeat(80));

    // Сортуємо від найповільнішого до найшвидшого
    const sortedModules = Array.from(graph.modules.values()).sort(
      (a, b) => PACE_RANK[a.layer] - PACE_RANK[b.layer]
    );

    for (const mod of sortedModules) {
      const rankStr = `${PACE_RANK[mod.layer]}/5`;
      const freqStr = `${mod.monthlyFrequency.toFixed(1)}/міс`;
      console.log(
        mod.name.padEnd(32) +
        mod.layer.padEnd(16) +
        rankStr.padEnd(8) +
        freqStr.padEnd(12) +
        mod.commitsCount.toString()
      );
    }
  }

  /**
   * Виводить список знайдених інверсій темпів із планом виправлення.
   */
  private printViolations(violations: TempoViolation[]): void {
    console.log('\n[ РЕЗУЛЬТАТ ПЕРЕВІРКИ ПРАВИЛА TEMPO-INVERSION ]');
    console.log('-'.repeat(80));

    if (violations.length === 0) {
      console.log('Жодного порушення не зафіксовано. Архітектурні межі чисті.');
      return;
    }

    violations.forEach((v, index) => {
      const icon = v.severity === 'CRITICAL' ? '⛔ [CRITICAL]' : '⚠️  [WARNING]';
      console.log(`\n${icon} Порушення #${index + 1}:`);
      console.log(`  Файл:        ${v.sourceFile}:${v.lineNumber}`);
      console.log(`  Напрямок:    ${v.sourceModule} (${v.sourceLayer}) ➔ ${v.targetModule} (${v.targetLayer})`);
      console.log(`  Діагноз:     ${v.message}`);
      console.log(`  Виправлення:`);
      console.log(`  ${v.remediation}`);
    });
  }
}
