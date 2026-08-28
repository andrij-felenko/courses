// Ідіоматичний TypeScript: дискриміновані об'єднання, суворе типування

export type DecisionRoute = 
  | { kind: 'FAST_TRACK_DELEGATE'; rationale: string }
  | { kind: 'TIMEBOXED_SPIKE'; spikeDays: number; rationale: string }
  | { kind: 'PRE_MORTEM_WORKSHOP'; rationale: string }
  | { kind: 'ARCH_REVIEW_BOARD'; rationale: string }
  | { kind: 'REJECTED_NO_METRICS'; rationale: string };

export interface DecisionVector {
  readonly title: string;
  readonly reversibilityScore: number; // 0.0 .. 1.0
  readonly innovationTokens: number;  // 0 .. 3
  readonly hasMeasurementData: boolean;
  readonly riskSeverity: number;      // 1 .. 5
  readonly touchesPublicApi: boolean;
  readonly isPerformanceOptimization: boolean;
}

export class DecisionEvaluator {
  private static readonly MAX_TOKENS = 3;

  constructor(private readonly currentProjectTokens: number = 1) {}

  public evaluate(vec: DecisionVector): DecisionRoute {
    if (this.currentProjectTokens + vec.innovationTokens > DecisionEvaluator.MAX_TOKENS) {
      throw new Error(`Перевищено бюджет інноваційних жетонів! Лишилося: ${DecisionEvaluator.MAX_TOKENS - this.currentProjectTokens}`);
    }

    // Евристика: Measure First
    if (vec.isPerformanceOptimization && !vec.hasMeasurementData) {
      return {
        kind: 'REJECTED_NO_METRICS',
        rationale: 'Відхилено: оптимізація продуктивності заборонена без надання профілів і метрик.'
      };
    }

    const publicImpact = vec.touchesPublicApi ? 0.3 : 0.0;
    const tokenImpact = vec.innovationTokens * 0.1;
    const oneWayIndex = (1.0 - vec.reversibilityScore) * 0.5 + publicImpact + tokenImpact;

    if (oneWayIndex >= 0.6 || vec.riskSeverity >= 4) {
      return {
        kind: 'ARCH_REVIEW_BOARD',
        rationale: `One-Way Door (Індекс: ${oneWayIndex.toFixed(2)}). Потрібна повноцінна захист RFC на Arch Review Board.`
      };
    }

    if (vec.riskSeverity === 3 || (oneWayIndex >= 0.3 && !vec.hasMeasurementData)) {
      return {
        kind: 'PRE_MORTEM_WORKSHOP',
        rationale: 'Помірний ризик/невизначеність. Обов’язкова 30-хвилинна сесія Pre-Mortem.'
      };
    }

    if (vec.reversibilityScore < 0.7 || vec.innovationTokens > 0) {
      return {
        kind: 'TIMEBOXED_SPIKE',
        spikeDays: 2,
        rationale: 'Необхідно купити інформацію: Timeboxed спайк на 2 дні.'
      };
    }

    return {
      kind: 'FAST_TRACK_DELEGATE',
      rationale: 'Two-Way Door: Висока зворотність. Делегувати розробнику без бюрократії.'
    };
  }
}
