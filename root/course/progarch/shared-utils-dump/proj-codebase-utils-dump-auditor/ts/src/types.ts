/**
 * Доменна модель статичного аудитора звалища утиліт (Utils Dump Auditor).
 * Оголошує типи для категоризації функцій за принципами CRP/REP,
 * структурні вузли графа викликів, метадані сигнатур функцій
 * та моделі машинозчитуваних і консольних звітів.
 */

/**
 * Категорії утилітарних функцій згідно з топологією викликів
 * та архітектурними принципами компонентного дизайну.
 */
export enum UtilityCategory {
  /**
   * Мертвий код: функція експортована, але ніде в проєкті не викликається.
   * Порушує принципи чистоти коду та роздуває публічний API.
   */
  DEAD_CODE = 'DEAD_CODE',

  /**
   * Кандидат на інлайнінг: функція викликається лише в одному модулі або точці.
   * Порушує Common Reuse Principle (CRP), створюючи непотрібну спільну залежність.
   */
  INLINE_CANDIDATE = 'INLINE_CANDIDATE',

  /**
   * Репатріація в домен: функція оперує типами предметної області або
   * містить бізнес-правила конкретного контексту.
   * Порушує Reuse/Release Equivalence Principle (REP) та межі Bounded Contexts.
   */
  DOMAIN_REPATRIATION = 'DOMAIN_REPATRIATION',

  /**
   * Легітимна спільна бібліотека: доменно-нейтральна функція з широким
   * міжмодульним споживанням (fan-in >= 2), що задовольняє принципам CRP та REP.
   */
  CRP_REP_LIBRARY = 'CRP_REP_LIBRARY',
}

/**
 * Архітектурний принцип, порушений розміщенням функції в загальному каталозі utils.
 */
export enum ArchitecturalPrinciple {
  /**
   * Common Reuse Principle: компоненти, що не використовуються разом,
   * не повинні пакуватися разом.
   */
  CRP = 'CRP',

  /**
   * Reuse/Release Equivalence Principle: одиниця повторного використання
   * є одиницею випуску. Доменні типи не повинні бути зв'язані з життєвим циклом utils.
   */
  REP = 'REP',

  /**
   * Принцип чистоти кодової бази: видалення мертвого або неактивного коду.
   */
  CLEAN_CODE = 'CLEAN_CODE',

  /**
   * Порушень немає (код повністю відповідає правилам архітектури).
   */
  NONE = 'NONE',
}

/**
 * Інформація про виявлений витік типу предметної області в сигнатурі функції.
 */
export interface TypeLeakDetail {
  /** Локація витоку: параметр функції або значення, що повертається */
  location: 'parameter' | 'return';
  /** Назва параметра (або 'return' для результату) */
  identifierName: string;
  /** Текстове представлення типу (наприклад, 'Order', 'CustomerTier') */
  typeName: string;
  /** Шлях до файла, де оголошено цей тип (якщо доступно з AST) */
  declaredInFile?: string;
  /** Причина класифікації як доменного типу */
  reason: string;
}

/**
 * Опис параметра функції, вилученого з синтаксичного дерева AST.
 */
export interface FunctionParameterInfo {
  name: string;
  typeName: string;
  isOptional: boolean;
}

/**
 * Повна інформація про експортовану функцію, вилучена під час обходу AST.
 */
export interface FunctionSignatureInfo {
  /** Назва функції */
  name: string;
  /** Повний або нормалізований шлях до файла, де функцію оголошено */
  filePath: string;
  /** Відносний шлях від кореня проєкту */
  relativeFilePath: string;
  /** Номер рядка в коді (1-індексація) */
  line: number;
  /** Номер стовпця в коді (1-індексація) */
  character: number;
  /** Список параметрів */
  parameters: FunctionParameterInfo[];
  /** Текстове представлення типу значення, що повертається */
  returnTypeName: string;
  /** Чи є функція публічно експортованою */
  isExported: boolean;
  /** Знайдені витоки доменних типів у сигнатурі */
  leakedDomainTypes: TypeLeakDetail[];
}

/**
 * Точка виклику утилітарної функції в кодовій базі проєкту.
 */
export interface CallSite {
  /** Шлях до файла споживача */
  callerFilePath: string;
  /** Відносний шлях споживача від кореня проєкту */
  relativeCallerPath: string;
  /** Назва підсистеми / модуля (наприклад, 'billing', 'orders', 'catalog') */
  callerModuleName: string;
  /** Назва функції чи методу, всередині якого відбувається виклик */
  callerFunctionName?: string;
  /** Номер рядка виклику (1-індексація) */
  line: number;
  /** Номер стовпця виклику (1-індексація) */
  character: number;
}

/**
 * Вузол орієнтованого графа міжмодульних викликів для конкретної утиліти.
 */
export interface CallGraphNode {
  /** Назва функції утиліти */
  functionName: string;
  /** Файл оголошення функції */
  declaringFilePath: string;
  /** Усі зафіксовані точки виклику */
  callSites: CallSite[];
  /** Загальна кількість викликів */
  callCount: number;
  /** Унікальні модулі, які викликають цю утиліту */
  consumerModules: string[];
  /** Унікальні файли, які викликають цю утиліту */
  consumerFiles: string[];
}

/**
 * Результат аудиту та категоризації утилітарної функції.
 */
export interface CategorizedUtility {
  functionName: string;
  declaringFilePath: string;
  line: number;
  category: UtilityCategory;
  callCount: number;
  consumerModules: string[];
  leakedDomainTypes: string[];
  violatedPrinciple: ArchitecturalPrinciple;
  rationale: string;
  recommendation: string;
}

/**
 * Агрегована статистика аудиту каталогу утиліт.
 */
export interface AuditSummary {
  totalAnalyzed: number;
  deadCodeCount: number;
  inlineCandidateCount: number;
  repatriationCount: number;
  libraryCandidateCount: number;
  hasViolations: boolean;
}

/**
 * Повний звіт про аудит кодової бази для CI/CD конвеєрів та консолі.
 */
export interface AuditReport {
  timestamp: string;
  projectRoot: string;
  summary: AuditSummary;
  utilities: CategorizedUtility[];
  exitCode: number;
}

/**
 * Опції запуску та конфігурації аналізатора.
 */
export interface AnalyzerConfig {
  projectRoot: string;
  utilsPaths: string[];
  domainEntityKeywords?: string[];
  minModuleFanInForLibrary?: number;
  failOnViolations?: boolean;
}

/**
 * Опції командного рядка CLI.
 */
export interface CliOptions {
  demoMode: boolean;
  projectPath?: string;
  utilsPath?: string;
  jsonOutput: boolean;
  outputFilePath?: string;
  showHelp: boolean;
}
