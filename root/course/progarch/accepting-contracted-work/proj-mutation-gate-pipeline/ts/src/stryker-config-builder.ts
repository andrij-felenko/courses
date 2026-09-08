/** Конфігурація мутаційних порогів Stryker */
export interface StrykerThresholds {
  high: number;
  low: number;
  break: number;
}

/** Параметри динамічної конфігурації Stryker */
export interface StrykerDynamicConfig {
  mutate: string[];
  testRunner: string;
  reporters: string[];
  coverageAnalysis: "perTest" | "all" | "off";
  timeoutMS: number;
  concurrency: number;
  thresholds: StrykerThresholds;
  tempDirName: string;
  cleanTempDir: boolean;
}

/** Опції побудовника конфігурації */
export interface BuilderOptions {
  testRunner?: string;
  threshold?: number;
  timeoutMS?: number;
  concurrency?: number;
}

/**
 * StrykerConfigBuilder: динамічно формує конфігурацію для Stryker Mutator,
 * обмежуючи зону дії мутацій виключно зміненими файлами підрядника.
 */
export class StrykerConfigBuilder {
  private readonly testRunner: string;
  private readonly threshold: number;
  private readonly timeoutMS: number;
  private readonly concurrency: number;

  constructor(options: BuilderOptions = {}) {
    this.testRunner = options.testRunner ?? "vitest";
    this.threshold = options.threshold ?? 80;
    this.timeoutMS = options.timeoutMS ?? 5000;
    this.concurrency = options.concurrency ?? 4;
  }

  /**
   * Створює готовий об'єкт конфігурації під вказаний список цільових файлів
   */
  public build(targetFiles: string[]): StrykerDynamicConfig {
    if (targetFiles.length === 0) {
      throw new Error(
        "Неможливо побудувати конфігурацію Stryker: список цільових файлів порожній."
      );
    }

    return {
      mutate: [...targetFiles],
      testRunner: this.testRunner,
      reporters: ["clear-text", "json", "progress"],
      coverageAnalysis: "perTest",
      timeoutMS: this.timeoutMS,
      concurrency: this.concurrency,
      thresholds: {
        high: this.threshold,
        low: Math.max(0, this.threshold - 20),
        break: this.threshold,
      },
      tempDirName: ".stryker-tmp",
      cleanTempDir: true,
    };
  }

  /**
   * Серіалізує конфігурацію у формат JSON для запису на диск
   */
  public serialize(config: StrykerDynamicConfig): string {
    return JSON.stringify(config, null, 2);
  }
}
