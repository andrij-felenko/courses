interface FeatureFlagSDK {
  // Оцінка булевого прапорця
  boolVariation(
    flagKey: string, 
    context: EvaluationContext, 
    defaultValue: boolean
  ): boolean;

  // Оцінка мультиваріантного прапорця (строкові конфігурації)
  stringVariation(
    flagKey: string, 
    context: EvaluationContext, 
    defaultValue: string
  ): string;

  // Оцінка складної JSON-конфігурації для динамічного налаштування
  jsonVariation<T>(
    flagKey: string, 
    context: EvaluationContext, 
    defaultValue: T
  ): T;

  // Оцінка з поверненням детального причинно-наслідкового звіту
  evaluateDetail<T>(
    flagKey: string, 
    context: EvaluationContext, 
    defaultValue: T
  ): EvaluationDetail<T>;
}

interface EvaluationDetail<T> {
  value: T;
  variationIndex?: number;
  reason: "OFF_FALLBACK" | "TARGET_MATCH" | "PERCENTAGE_ROLLOUT" | "RULE_MATCH" | "DEFAULT";
  ruleId?: string;
}
