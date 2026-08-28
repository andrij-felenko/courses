// cost-guard.ts — Сторож бюджету Unit Cost у CI/CD конвеєрі

export interface ResourceUsage {
  cpuMs: number;
  dbQueries: number;
  memoryMb: number;
  egressBytes: number;
}

export interface CloudPricing {
  costPerCpuMs: number;       // $ / ms CPU (наприклад, $0.00000002)
  costPerDbQuery: number;     // $ / query (наприклад, $0.000005)
  costPerEgressGb: number;    // $ / GB (наприклад, $0.09)
}

export interface BudgetConfig {
  maxUnitCostUsd: number;     // Максимально припустима вартість 1,000 запитів
  maxRegressionPct: number;   // Пороговий відсоток регресії (наприклад, 15%)
  minSampleRuns: number;      // Мінімальна кількість прогонів для усереднення
}

export interface TestProfile {
  endpoint: string;
  baselineCostUsd: number;
  runs: ResourceUsage[];
}

export interface GuardVerdict {
  ok: boolean;
  endpoint: string;
  currentCostUsd: number;
  baselineCostUsd: number;
  deltaPct: number;
  message: string;
}

export class CostFitnessGuard {
  constructor(
    private pricing: CloudPricing,
    private config: BudgetConfig
  ) {}

  /**
   * Обчислює точну вартість одного запиту на основі використаних ресурсів
   */
  public calculateSingleCost(usage: ResourceUsage): number {
    const cpuCost = usage.cpuMs * this.pricing.costPerCpuMs;
    const dbCost = usage.dbQueries * this.pricing.costPerDbQuery;
    const egressGb = usage.egressBytes / (1024 * 1024 * 1024);
    const egressCost = egressGb * this.pricing.costPerEgressGb;

    return cpuCost + dbCost + egressCost;
  }

  /**
   * Обчислює усереднену питому вартість 1,000 запитів із видаленням крайніх викидів
   */
  public calculateUnitCostPerK(runs: ResourceUsage[]): number {
    if (runs.length === 0) return 0;

    // Сортуємо прогони за вартістю для відсікання сплесків GC або мережі
    const costs = runs.map(r => this.calculateSingleCost(r)).sort((a, b) => a - b);
    
    // Якщо прогонів достатньо, відкидаємо найгірший 10% результат (викиди)
    const validCosts = costs.length >= 5 ? costs.slice(0, Math.floor(costs.length * 0.9)) : costs;
    const avgSingleCost = validCosts.reduce((sum, c) => sum + c, 0) / validCosts.length;

    return avgSingleCost * 1000;
  }

  /**
   * Перевіряє коміт на відповідність економічному бюджету й відсотку регресії
   */
  public evaluateCommit(profile: TestProfile): GuardVerdict {
    if (profile.runs.length < this.config.minSampleRuns) {
      return {
        ok: false,
        endpoint: profile.endpoint,
        currentCostUsd: 0,
        baselineCostUsd: profile.baselineCostUsd,
        deltaPct: 0,
        message: `[ERROR] Недостатньо прогонів тесту: отримано ${profile.runs.length}, потрібно щонайменше ${this.config.minSampleRuns}`,
      };
    }

    const currentCostUsd = this.calculateUnitCostPerK(profile.runs);

    // 1. Перевірка абсолютного ліміту бюджету
    if (currentCostUsd > this.config.maxUnitCostUsd) {
      return {
        ok: false,
        endpoint: profile.endpoint,
        currentCostUsd,
        baselineCostUsd: profile.baselineCostUsd,
        deltaPct: ((currentCostUsd - profile.baselineCostUsd) / profile.baselineCostUsd) * 100,
        message: `[FAIL] ${profile.endpoint}: Unit Cost $${currentCostUsd.toFixed(4)}/1k перевищує стелю $${this.config.maxUnitCostUsd.toFixed(4)}`,
      };
    }

    // 2. Перевірка відносного порогу регресії порівняно з еталоном (Baseline)
    const deltaPct = profile.baselineCostUsd > 0
      ? ((currentCostUsd - profile.baselineCostUsd) / profile.baselineCostUsd) * 100
      : 0;

    if (deltaPct > this.config.maxRegressionPct) {
      return {
        ok: false,
        endpoint: profile.endpoint,
        currentCostUsd,
        baselineCostUsd: profile.baselineCostUsd,
        deltaPct,
        message: `[FAIL] ${profile.endpoint}: Регресія витрат +${deltaPct.toFixed(1)}% перевищує поріг +${this.config.maxRegressionPct}% (база: $${profile.baselineCostUsd.toFixed(4)}, поточна: $${currentCostUsd.toFixed(4)})`,
      };
    }

    return {
      ok: true,
      endpoint: profile.endpoint,
      currentCostUsd,
      baselineCostUsd: profile.baselineCostUsd,
      deltaPct,
      message: `[PASS] ${profile.endpoint}: Unit Cost $${currentCostUsd.toFixed(4)}/1k (динаміка: ${deltaPct > 0 ? '+' : ''}${deltaPct.toFixed(1)}%)`,
    };
  }
}
