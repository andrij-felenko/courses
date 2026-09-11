/**
 * Модель темпів змін за концепцією Pace Layering (Стюарт Бренд / архітектурний аналіз).
 * Кожен шар має свій ранг стабільності: чим нижчий ранг, тим повільніше змінюється шар.
 */
export const PaceLayer = {
  FOUNDATION: 'FOUNDATION',       // Ранг 1: Протоколи, апаратні драйвери, базові схеми (дуже повільний)
  CORE_DOMAIN: 'CORE_DOMAIN',     // Ранг 2: Бізнес-інваріанти, правила безпеки та автоматизації (повільний)
  SUPPORTING: 'SUPPORTING',       // Ранг 3: Реєстри сутностей, локальні сховища, сервіси конфігурації (помірний)
  INTEGRATION: 'INTEGRATION',     // Ранг 4: Зовнішні хмарні сервіси, партнерські API, голосові шлюзи (швидкий)
  VOLATILE_UI: 'VOLATILE_UI',     // Ранг 5: Мобільні екрани, віджети, експерименти, промо (дуже швидкий)
} as const;

export type PaceLayerType = (typeof PaceLayer)[keyof typeof PaceLayer];

/**
 * Числовий ранг стабільності (1 = найповільніший, 5 = найшвидший).
 */
export const PACE_RANK: Record<PaceLayerType, number> = {
  FOUNDATION: 1,
  CORE_DOMAIN: 2,
  SUPPORTING: 3,
  INTEGRATION: 4,
  VOLATILE_UI: 5,
};

/**
 * Текстовий опис шарів темпу для звітів.
 */
export const PACE_LAYER_NAMES: Record<PaceLayerType, string> = {
  FOUNDATION: 'Базовий фундамент (протоколи/залізо)',
  CORE_DOMAIN: 'Ядро домену (бізнес-інваріанти)',
  SUPPORTING: 'Допоміжний шар (реєстри/сховища)',
  INTEGRATION: 'Інтеграції (хмарні та партнерські API)',
  VOLATILE_UI: 'Користувацький інтерфейс (волатильний)',
};

/**
 * Запис окремого коміту для аналізу активності.
 */
export interface CommitRecord {
  hash: string;
  timestamp: number; // Unix timestamp в мілісекундах
  author: string;
  files: string[];
  linesAdded: number;
  linesDeleted: number;
}

/**
 * Емпіричні метрики волатильності окремого архітектурного модуля.
 */
export interface ModuleMetrics {
  name: string;
  path: string;
  commitsCount: number;
  totalChurn: number;
  monthlyFrequency: number;
  layer: PaceLayerType;
  description: string;
}

/**
 * Ребро орієнтованого графа залежностей (sourceModule імпортує targetModule).
 */
export interface DependencyEdge {
  sourceModule: string;
  targetModule: string;
  importPath: string;
  importedSymbols: string[];
  sourceFile: string;
  lineNumber: number;
}

/**
 * Структура графа залежностей системи.
 */
export interface DependencyGraph {
  modules: Map<string, ModuleMetrics>;
  edges: DependencyEdge[];
}

/**
 * Рівень критичності архітектурного порушення.
 */
export type ViolationSeverity = 'CRITICAL' | 'WARNING';

/**
 * Опис виявленого порушення інверсії темпів.
 */
export interface TempoViolation {
  sourceModule: string;
  sourceLayer: PaceLayerType;
  sourceFrequency: number;
  targetModule: string;
  targetLayer: PaceLayerType;
  targetFrequency: number;
  severity: ViolationSeverity;
  sourceFile: string;
  lineNumber: number;
  message: string;
  remediation: string;
}

/**
 * Підсумковий звіт перевірки для CI/CD гейта.
 */
export interface LintReport {
  timestamp: string;
  analyzedModulesCount: number;
  totalDependenciesCount: number;
  violations: TempoViolation[];
  hasCriticalViolations: boolean;
  exitCode: number;
  executionDurationMs: number;
}

/**
 * Віртуальний вихідний файл для аналізу парсером залежностей.
 */
export interface SourceFile {
  path: string;
  content: string;
}
