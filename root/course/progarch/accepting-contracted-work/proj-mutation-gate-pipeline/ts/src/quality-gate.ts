import { MutationRunSummary, MutantResult } from "./mutation-runner.ts";

/** Результат оцінки мутаційного гейта якості */
export interface QualityGateEvaluation {
  isPassing: boolean;
  requiredThreshold: number;
  actualScore: number;
  survivedCount: number;
  totalDetected: number;
  reasons: string[];
}

/**
 * MutationQualityGate: виконує арбітраж результатів мутаційного тестування,
 * порівнюючи показник Mutation Score з порогом у Definition of Done (за замовчуванням 80%).
 */
export class MutationQualityGate {
  private readonly threshold: number;

  constructor(threshold: number = 80) {
    if (threshold < 0 || threshold > 100) {
      throw new Error(
        "Порогове значення Mutation Score має перебувати в межах від 0 до 100%."
      );
    }
    this.threshold = threshold;
  }

  /**
   * Оцінює звіт мутаційного тестування та формує інженерний вердикт
   */
  public evaluate(summary: MutationRunSummary): QualityGateEvaluation {
    const actualScore = summary.mutationScore;
    const totalDetected = summary.killed + summary.survived + summary.timedOut;
    const survivedMutants = summary.mutants.filter((m) => m.status === "Survived");
    const reasons: string[] = [];

    let isPassing = true;

    if (totalDetected === 0) {
      reasons.push(
        "Мутаційні оператори не згенерували жодного валідного мутанта для аналізу."
      );
    } else if (actualScore < this.threshold) {
      isPassing = false;
      const deficit = (this.threshold - actualScore).toFixed(2);
      reasons.push(
        `Mutation Score становить ${actualScore}%, що нижче встановленого в контракті порогу ${this.threshold}% (дефіцит: ${deficit}%).`
      );
    }

    if (survivedMutants.length > 0) {
      reasons.push(
        `Виявлено ${survivedMutants.length} вцілілих мутантів: тести підрядника мають сліпі зони та пропускають зміни в логіці.`
      );
    }

    if (isPassing && totalDetected > 0) {
      reasons.push(
        `Mutation Score ${actualScore}% успішно задовольняє вимогу Definition of Done (>= ${this.threshold}%).`
      );
    }

    return {
      isPassing,
      requiredThreshold: this.threshold,
      actualScore,
      survivedCount: survivedMutants.length,
      totalDetected,
      reasons,
    };
  }

  /**
   * Отримує список вцілілих мутантів, які потребують виправлення тестами
   */
  public getSurvivedMutants(summary: MutationRunSummary): MutantResult[] {
    return summary.mutants.filter((m) => m.status === "Survived");
  }
}
