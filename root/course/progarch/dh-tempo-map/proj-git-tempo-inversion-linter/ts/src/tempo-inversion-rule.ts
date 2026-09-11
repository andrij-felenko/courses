import {
  PACE_LAYER_NAMES,
  PACE_RANK,
  type DependencyGraph,
  type TempoViolation,
  type ViolationSeverity,
} from './types.ts';

/**
 * Правило валідації архітектурних темпів (Tempo Inversion Rule).
 * Перевіряє, щоб повільні компоненти системи не залежали від швидких,
 * запобігаючи дестабілізації критичного ядра волатильними змінами.
 */
export class TempoInversionRule {
  /**
   * Перевіряє граф залежностей на наявність порушень інверсії темпів.
   */
  public evaluate(graph: DependencyGraph): TempoViolation[] {
    const violations: TempoViolation[] = [];

    for (const edge of graph.edges) {
      const sourceMetric = graph.modules.get(edge.sourceModule);
      const targetMetric = graph.modules.get(edge.targetModule);

      if (!sourceMetric || !targetMetric) {
        continue;
      }

      const sourceRank = PACE_RANK[sourceMetric.layer];
      const targetRank = PACE_RANK[targetMetric.layer];

      // Якщо джерело повільніше за ціль — зафіксовано інверсію темпів!
      if (sourceRank < targetRank) {
        const rankDiff = targetRank - sourceRank;
        const freqRatio =
          sourceMetric.monthlyFrequency > 0
            ? targetMetric.monthlyFrequency / sourceMetric.monthlyFrequency
            : targetMetric.monthlyFrequency;

        // Визначаємо рівень серйозності
        // Якщо розрив між шарами >= 2 або ціль змінюється втричі частіше -> CRITICAL
        const severity: ViolationSeverity =
          rankDiff >= 2 || freqRatio >= 3.0 ? 'CRITICAL' : 'WARNING';

        const sourceLayerName = PACE_LAYER_NAMES[sourceMetric.layer];
        const targetLayerName = PACE_LAYER_NAMES[targetMetric.layer];

        const symbolsList =
          edge.importedSymbols.length > 0
            ? `[${edge.importedSymbols.join(', ')}]`
            : edge.importPath;

        const message =
          `Інверсія темпів: стабільний модуль '${sourceMetric.name}' (${sourceLayerName}, ` +
          `${sourceMetric.monthlyFrequency} зм/міс) залежить від волатильного '${targetMetric.name}' ` +
          `(${targetLayerName}, ${targetMetric.monthlyFrequency} зм/міс). Імпортовано: ${symbolsList}`;

        const remediation = this.generateRemediationPlan(
          sourceMetric.name,
          targetMetric.name,
          edge.importedSymbols
        );

        violations.push({
          sourceModule: sourceMetric.name,
          sourceLayer: sourceMetric.layer,
          sourceFrequency: sourceMetric.monthlyFrequency,
          targetModule: targetMetric.name,
          targetLayer: targetMetric.layer,
          targetFrequency: targetMetric.monthlyFrequency,
          severity,
          sourceFile: edge.sourceFile,
          lineNumber: edge.lineNumber,
          message,
          remediation,
        });
      }
    }

    return violations;
  }

  /**
   * Формує архітектурні рекомендації щодо усунення інверсії темпів.
   */
  private generateRemediationPlan(
    sourceName: string,
    targetName: string,
    symbols: string[]
  ): string {
    const symbolHint =
      symbols.length > 0 ? ` (зокрема для ${symbols.join(', ')})` : '';

    return (
      `Застосуйте принцип інверсії залежностей (DIP)${symbolHint}:\n` +
      `  1. Оголосіть абстрактний порт або подію всередині повільного модуля '${sourceName}'.\n` +
      `  2. Перенесіть конкретну реалізацію адаптера у швидкий модуль '${targetName}' або шину подій.\n` +
      `  3. Приберіть прямий імпорт із '${sourceName}', щоб волатильні зміни '${targetName}' не провокували ретест ядра.`
    );
  }
}
