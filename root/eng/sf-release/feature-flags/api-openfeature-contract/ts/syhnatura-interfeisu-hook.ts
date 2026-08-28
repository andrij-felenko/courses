interface Hook {
  // Виконується ДО резолюції: може додати контекстні атрибути
  before?(hookContext: HookContext, hints?: HookHints): Promise<EvaluationContext | void>;

  // Виконується після успішної резолюції
  after?(hookContext: HookContext, details: EvaluationDetails<any>, hints?: HookHints): Promise<void>;

  // Виконується у разі виникнення помилки або викидання винятку
  error?(hookContext: HookContext, error: Error, hints?: HookHints): Promise<void>;

  // Виконується завжди (як блок finally)
  finally?(hookContext: HookContext, hints?: HookHints): Promise<void>;
}
