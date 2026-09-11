import { CiConsoleReporter } from './ci-console-reporter.ts';
import { CodeDependencyGraph } from './code-dependency-graph.ts';
import { GitHistoryAnalyzer, type ModuleDefinition } from './git-history-analyzer.ts';
import { TempoInversionRule } from './tempo-inversion-rule.ts';
import type {
  CommitRecord,
  DependencyGraph,
  LintReport,
  SourceFile,
} from './types.ts';

/**
 * Головний оркестратор лінтера архітектурних темпів.
 * Координує аналіз git-історії, побудову графа коду, валідацію правил та репортинг.
 */
export class TempoLinterEngine {
  private readonly gitAnalyzer: GitHistoryAnalyzer;
  private readonly rule: TempoInversionRule;
  private readonly reporter: CiConsoleReporter;

  constructor() {
    this.gitAnalyzer = new GitHistoryAnalyzer(90);
    this.rule = new TempoInversionRule();
    this.reporter = new CiConsoleReporter();
  }

  /**
   * Виконує повний цикл аналізу кодової бази та повертає звіт.
   */
  public run(
    modules: ModuleDefinition[],
    commits: CommitRecord[],
    sourceFiles: SourceFile[]
  ): { report: LintReport; graph: DependencyGraph } {
    const startTime = Date.now();

    // 1. Аналіз темпів змін за історією комітів
    const moduleMetrics = this.gitAnalyzer.analyzeModules(modules, commits);

    // 2. Статичний аналіз коду та побудова графа залежностей
    const depParser = new CodeDependencyGraph(moduleMetrics);
    const graph = depParser.buildGraph(sourceFiles, moduleMetrics);

    // 3. Перевірка правила інверсії темпів
    const violations = this.rule.evaluate(graph);

    // 4. Формування підсумкового звіту
    const durationMs = Date.now() - startTime;
    const report = this.reporter.generateReport(graph, violations, durationMs);

    return { report, graph };
  }

  /**
   * Запуск та друк результатів у термінал.
   */
  public runAndPrint(
    modules: ModuleDefinition[],
    commits: CommitRecord[],
    sourceFiles: SourceFile[]
  ): number {
    const { report, graph } = this.run(modules, commits, sourceFiles);
    this.reporter.printReport(report, graph);
    return report.exitCode;
  }
}

// ============================================================================
// ДЕМОНСТРАЦІЯ: Перевірка платформи «Digital Homes» (IoT Smart Home)
// ============================================================================

function createDigitalHomesDemo() {
  // 1. Архітектурні модулі платформи Digital Homes
  const modules: ModuleDefinition[] = [
    {
      name: 'core/device-protocols',
      pathPrefix: 'packages/device-protocols',
      description: 'Драйвери Zigbee, Matter, Z-Wave та апаратні протоколи',
    },
    {
      name: 'core/automation-engine',
      pathPrefix: 'packages/automation-engine',
      description: 'Ядро автоматизацій, сценарії безпеки та аварійні інваріанти',
    },
    {
      name: 'services/device-registry',
      pathPrefix: 'packages/device-registry',
      description: 'Сховище конфігурацій пристроїв та топології кімнат',
    },
    {
      name: 'integrations/voice-assistant',
      pathPrefix: 'packages/voice-assistant',
      description: 'Хмарні конектори до Amazon Alexa та Apple HomeKit',
    },
    {
      name: 'apps/mobile-dashboard',
      pathPrefix: 'packages/mobile-dashboard',
      description: 'Мобільний клієнт, віджети графіків, промо-кампанії',
    },
  ];

  // 2. Імітація історії комітів за останні 3 місяці
  // Демонструє кардинальну різницю в темпах змін між шарами
  const now = Date.now();
  const DAY_MS = 24 * 60 * 60 * 1000;
  const commits: CommitRecord[] = [];

  // device-protocols: 3 коміти за 90 днів (~1.0 зм/міс) -> FOUNDATION
  for (let i = 0; i < 3; i++) {
    commits.push({
      hash: `proto_${i}`,
      timestamp: now - (80 - i * 25) * DAY_MS,
      author: 'firmware-dev',
      files: ['packages/device-protocols/src/zigbee-driver.ts'],
      linesAdded: 15,
      linesDeleted: 2,
    });
  }

  // automation-engine: 9 комітів за 90 днів (~3.0 зм/міс) -> CORE_DOMAIN
  for (let i = 0; i < 9; i++) {
    commits.push({
      hash: `auto_${i}`,
      timestamp: now - (85 - i * 9) * DAY_MS,
      author: 'domain-lead',
      files: ['packages/automation-engine/src/rule-engine.ts'],
      linesAdded: 25,
      linesDeleted: 8,
    });
  }

  // device-registry: 28 комітів за 90 днів (~9.3 зм/міс) -> SUPPORTING
  for (let i = 0; i < 28; i++) {
    commits.push({
      hash: `reg_${i}`,
      timestamp: now - (88 - i * 3) * DAY_MS,
      author: 'backend-dev',
      files: ['packages/device-registry/src/registry-service.ts'],
      linesAdded: 40,
      linesDeleted: 15,
    });
  }

  // voice-assistant: 70 комітів за 90 днів (~23.3 зм/міс) -> INTEGRATION
  for (let i = 0; i < 70; i++) {
    commits.push({
      hash: `voice_${i}`,
      timestamp: now - (89 - i * 1.2) * DAY_MS,
      author: 'integrations-team',
      files: ['packages/voice-assistant/src/alexa-skill-handler.ts'],
      linesAdded: 60,
      linesDeleted: 35,
    });
  }

  // mobile-dashboard: 150 комітів за 90 днів (~50.0 зм/міс) -> VOLATILE_UI
  for (let i = 0; i < 150; i++) {
    commits.push({
      hash: `ui_${i}`,
      timestamp: now - (89 - i * 0.58) * DAY_MS,
      author: 'frontend-team',
      files: ['packages/mobile-dashboard/src/promo-banner.ts'],
      linesAdded: 110,
      linesDeleted: 70,
    });
  }

  // 3. Вихідні файли кодової бази із залежностями
  const sourceFiles: SourceFile[] = [
    // Легітимний імпорт: швидкий UI імпортує помірний device-registry
    {
      path: 'packages/mobile-dashboard/src/dashboard-controller.ts',
      content: `
import { DeviceRegistryService } from '../../device-registry/src/registry-service';

export class DashboardController {
  constructor(private registry: DeviceRegistryService) {}
  render() { return this.registry.getActiveDevices(); }
}
      `.trim(),
    },
    // Легітимний імпорт: допоміжний сервіс імпортує базовий драйвер протоколу
    {
      path: 'packages/device-registry/src/registry-service.ts',
      content: `
import { ZigbeeDriver } from '../../device-protocols/src/zigbee-driver';

export class DeviceRegistryService {
  constructor(private driver: ZigbeeDriver) {}
  getActiveDevices() { return this.driver.scanNetwork(); }
}
      `.trim(),
    },
    // АРХІТЕКТУРНЕ ПОРУШЕННЯ #1:
    // Повільне ядро (CORE_DOMAIN) імпортує експериментальний віджет із швидкого UI (VOLATILE_UI)!
    {
      path: 'packages/automation-engine/src/alert-service.ts',
      content: `
// Аварійний сервіс витоку води напряму залежить від промо-віджета мобільного додатка!
import { PromoBannerWidget } from '../../mobile-dashboard/src/promo-banner';

export class AlertService {
  notifyWaterLeak() {
    const banner = new PromoBannerWidget();
    banner.showEmergencyPopup('Увага: виявлено протікання води в системі!');
  }
}
      `.trim(),
    },
    // АРХІТЕКТУРНЕ ПОРУШЕННЯ #2:
    // Стабільний драйвер заліза (FOUNDATION) напряму імпортує хмарний Alexa Skill (INTEGRATION)!
    {
      path: 'packages/device-protocols/src/zigbee-driver.ts',
      content: `
// Драйвер низькорівневого контролера Zigbee зв'язаний з хмарним API Amazon Alexa!
import { AlexaSkillHandler } from '../../voice-assistant/src/alexa-skill-handler';

export class ZigbeeDriver {
  scanNetwork() { return ['sensor-01', 'valve-02']; }
  onFrameReceived(frame: unknown) {
    const alexa = new AlexaSkillHandler();
    alexa.dispatchVoiceNotification('Отримано апаратний кадр Zigbee');
  }
}
      `.trim(),
    },
    // Файли цільових компонентів
    {
      path: 'packages/voice-assistant/src/alexa-skill-handler.ts',
      content: `
export class AlexaSkillHandler {
  dispatchVoiceNotification(msg: string) { console.log('Alexa TTS:', msg); }
}
      `.trim(),
    },
    {
      path: 'packages/mobile-dashboard/src/promo-banner.ts',
      content: `
export class PromoBannerWidget {
  showEmergencyPopup(text: string) { console.log('UI Popup:', text); }
}
      `.trim(),
    },
  ];

  return { modules, commits, sourceFiles };
}

// Запуск утиліти
function main() {
  const engine = new TempoLinterEngine();
  const demoData = createDigitalHomesDemo();

  console.log('Запуск перевірки темпів змін для репозиторію Digital Homes...');
  const exitCode = engine.runAndPrint(
    demoData.modules,
    demoData.commits,
    demoData.sourceFiles
  );

  if (exitCode !== 0) {
    console.log(`[CI/CD Runner] Процес завершився з кодом ${exitCode}. Збірка зупинена.`);
  } else {
    console.log('[CI/CD Runner] Процес завершився успішно. Злиття дозволено.');
  }
}

main();
