interface Client {
  // Булеві прапорці (увімкнено / вимкнено)
  getBooleanValue(flagKey: string, defaultValue: boolean, context?: EvaluationContext): Promise<boolean>;
  getBooleanDetails(flagKey: string, defaultValue: boolean, context?: EvaluationContext): Promise<EvaluationDetails<boolean>>;

  // Рядкові прапорці (вибір варіанта, ключа API або текстового повідомлення)
  getStringValue(flagKey: string, defaultValue: string, context?: EvaluationContext): Promise<string>;
  getStringDetails(flagKey: string, defaultValue: string, context?: EvaluationContext): Promise<EvaluationDetails<string>>;

  // Числові прапорці (таймаути, ліміти черг, порогові значення)
  getNumberValue(flagKey: string, defaultValue: number, context?: EvaluationContext): Promise<number>;
  getNumberDetails(flagKey: string, defaultValue: number, context?: EvaluationContext): Promise<EvaluationDetails<number>>;

  // Структуровані об'єктні прапорці (конфігураційні JSON-схеми, словники)
  getObjectValue<T extends object>(flagKey: string, defaultValue: T, context?: EvaluationContext): Promise<T>;
  getObjectDetails<T extends object>(flagKey: string, defaultValue: T, context?: EvaluationContext): Promise<EvaluationDetails<T>>;

  // Управління хуками на рівні екземпляра клієнта
  addHooks(...hooks: Hook[]): void;
}
