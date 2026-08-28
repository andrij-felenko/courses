interface FeatureProvider {
  readonly metadata: { name: string };
  readonly hooks?: Hook[];

  // Події життєвого циклу провайдера
  initialize?(context?: EvaluationContext): Promise<void>;
  shutdown?(): Promise<void>;
  onContextChange?(oldContext: EvaluationContext, newContext: EvaluationContext): Promise<void>;

  // Обов'язкові внутрішні методи резолюції типів
  resolveBooleanEvaluation(flagKey: string, defaultValue: boolean, context: EvaluationContext): Promise<ResolutionDetails<boolean>>;
  resolveStringEvaluation(flagKey: string, defaultValue: string, context: EvaluationContext): Promise<ResolutionDetails<string>>;
  resolveNumberEvaluation(flagKey: string, defaultValue: number, context: EvaluationContext): Promise<ResolutionDetails<number>>;
  resolveObjectEvaluation<T extends object>(flagKey: string, defaultValue: T, context: EvaluationContext): Promise<ResolutionDetails<T>>;
}
