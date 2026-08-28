export type MacroPattern = 
  | 'ModularMonolith' 
  | 'Microservices' 
  | 'Serverless' 
  | 'DistributedMonolithRisk';

export interface SystemMetrics {
  teamCount: number;                 // Кількість команд
  domainBoundaryMaturity: number;    // Зрілість меж [0.0 ... 1.0]
  p99LatencyBudgetMs: number;        // Бюджет затримки (ms)
  independentScaleDriver: boolean;   // Асиметричний масштаб
  sharedDatabaseCoupling: boolean;   // Спільна БД
  highEventDrivenLoad: boolean;      // Подійне навантаження
}

export interface EvaluationResult {
  recommendedPattern: MacroPattern;
  scores: {
    modularMonolith: number;
    microservices: number;
    serverless: number;
  };
  warningFlags: string[];
  primaryRationale: string;
}

export class MacroPatternEvaluator {
  public static evaluate(metrics: SystemMetrics): EvaluationResult {
    const warningFlags: string[] = [];

    // Детекція пастки Розподіленого Моноліта
    if (metrics.sharedDatabaseCoupling && metrics.teamCount > 1) {
      warningFlags.push(
        'КРИТИЧНА ПОМИЛКА: Виявлено спільну базу даних поверх мережевих сервісів! ' +
        'Це утворює Розподілений Моноліт з максимальним операційним ризиком.'
      );
    }

    // Розрахунок бала для Модульного Моноліта
    let modularMonolith = 80.0;
    if (metrics.teamCount <= 3) modularMonolith += 15.0;
    if (metrics.domainBoundaryMaturity < 0.6) modularMonolith += 25.0;
    if (metrics.p99LatencyBudgetMs < 20.0) modularMonolith += 20.0;
    if (!metrics.independentScaleDriver) modularMonolith += 10.0;

    // Розрахунок бала для Мікросервісів
    let microservices = 20.0;
    if (metrics.teamCount >= 4) microservices += 30.0;
    if (metrics.domainBoundaryMaturity >= 0.7) microservices += 25.0;
    if (metrics.independentScaleDriver) microservices += 35.0;
    if (metrics.p99LatencyBudgetMs < 10.0) microservices -= 40.0;

    // Розрахунок бала для Серверлесу
    let serverless = 15.0;
    if (metrics.highEventDrivenLoad) serverless += 45.0;
    if (metrics.teamCount <= 2 && metrics.domainBoundaryMaturity >= 0.5) serverless += 20.0;
    if (metrics.p99LatencyBudgetMs < 50.0) serverless -= 30.0;

    let recommendedPattern: MacroPattern = 'ModularMonolith';
    let primaryRationale = '';

    if (metrics.sharedDatabaseCoupling && !metrics.independentScaleDriver && metrics.domainBoundaryMaturity < 0.5) {
      recommendedPattern = 'DistributedMonolithRisk';
      primaryRationale = 
        'ПРИСУД: Зійдіть з мережевих меж та консолідуйте код назад у Модульний Моноліт. ' +
        'Поточна конфігурація є розподіленим монолітом без жодних переваг автономії.';
    } else if (microservices > modularMonolith && microservices > serverless) {
      recommendedPattern = 'Microservices';
      primaryRationale = 
        'ПРИСУД: Виділення мікросервісів обґрунтовано високою зрілістю меж, ' +
        'великою кількістю команд та асиметричним профілем масштабування.';
    } else if (serverless > modularMonolith && serverless > microservices) {
      recommendedPattern = 'Serverless';
      primaryRationale = 
        'ПРИСУД: Серверлесс-архітектура рекомендована через виражену подійну природу ' +
        'навантаження та можливість повністю усунути інфраструктурний оверхед.';
    } else {
      recommendedPattern = 'ModularMonolith';
      primaryRationale = 
        'ПРИСУД: Модульний моноліт є оптимальним архітектурним дефолтом. ' +
        'Він забезпечує мінімальний мережевий податок, зберігає двобічні двері ' +
        'для рефакторингу та усуває Microservice Premium.';
    }

    return {
      recommendedPattern,
      scores: {
        modularMonolith,
        microservices,
        serverless,
      },
      warningFlags,
      primaryRationale,
    };
  }
}
