import * as path from "node:path";
import { ManifestAuditor } from "./manifest-auditor.ts";
import { ContainerOrchestrator } from "./container-orchestrator.ts";
import { MigrationVerifier } from "./migration-verifier.ts";
import { SmokeRunner } from "./smoke-runner.ts";
import { AcceptanceReporter } from "./acceptance-reporter.ts";

export interface ValidatorOptions {
  projectDir: string;
  reportPath: string;
  forceSimulation: boolean;
  systemName: string;
}

/**
 * Головний координатор процесу технічного аудиту системи «із чистого аркуша».
 */
export class CleanSlateValidator {
  private reporter = new AcceptanceReporter();
  private orchestrator = new ContainerOrchestrator();

  public async runAudit(options: ValidatorOptions): Promise<boolean> {
    const { projectDir, reportPath, forceSimulation, systemName } = options;

    try {
      // 1. Фаза 1: Статичний аудит маніфестів
      const startManifest = Date.now();
      const manifestAuditor = new ManifestAuditor();
      const manifestResult = manifestAuditor.auditDirectory(projectDir);

      this.reporter.recordPhase({
        phase: "manifest_audit",
        title: "Аудит герметичності маніфестів",
        passed: manifestResult.passed,
        durationMs: Date.now() - startManifest,
        details: manifestResult,
        error: manifestResult.passed ? undefined : `${manifestResult.violations.length} дефектів у залежностях`,
      });

      // 2. Фаза 2: Холодний запуск ефемерного середовища
      const startInfra = Date.now();
      let containerInfo;
      let infraError: string | undefined;

      try {
        containerInfo = await this.orchestrator.startPostgres({ forceSimulation });
      } catch (err) {
        infraError = err instanceof Error ? err.message : String(err);
      }

      this.reporter.recordPhase({
        phase: "container_orchestration",
        title: "Холодний старт ефемерної інфраструктури",
        passed: Boolean(containerInfo),
        durationMs: Date.now() - startInfra,
        details: containerInfo ?? {},
        error: infraError,
      });

      // 3. Фаза 3: Валідація міграцій БД
      const startMigrations = Date.now();
      const migrationVerifier = new MigrationVerifier();
      const migrationResult = await migrationVerifier.verifyMigrations();

      this.reporter.recordPhase({
        phase: "database_migrations",
        title: "Ідемпотентність міграцій БД (up-down-up)",
        passed: migrationResult.passed,
        durationMs: Date.now() - startMigrations,
        details: migrationResult,
        error: migrationResult.error,
      });

      // 4. Фаза 4: Інтеграційний smoke-тест сервісу
      const startSmoke = Date.now();
      const smokeRunner = new SmokeRunner();
      const smokeResult = await smokeRunner.runSuite({ autoMockServer: true });

      this.reporter.recordPhase({
        phase: "smoke_testing",
        title: "Димове тестування зондів та SLA",
        passed: smokeResult.passed,
        durationMs: Date.now() - startSmoke,
        details: smokeResult,
        error: smokeResult.passed ? undefined : `${smokeResult.totalChecks - smokeResult.passedChecks} тестів впало`,
      });
    } finally {
      this.orchestrator.stopAll();
    }

    const report = this.reporter.generateReport(systemName);
    this.reporter.saveReportJson(reportPath, report);
    this.reporter.printConsoleSummary(report);

    return report.gatePassed;
  }
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  let projectDir = process.cwd();
  let reportPath = path.join(projectDir, "acceptance-report.json");
  let forceSimulation = true; // За замовчуванням безпечний режим емуляції для навчання
  let systemName = "Handover-Candidate-System";

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--project-dir" && args[i + 1]) {
      projectDir = path.resolve(args[++i]);
    } else if (args[i] === "--output" && args[i + 1]) {
      reportPath = path.resolve(args[++i]);
    } else if (args[i] === "--docker") {
      forceSimulation = false;
    } else if (args[i] === "--system" && args[i + 1]) {
      systemName = args[++i];
    } else if (args[i] === "--help") {
      console.log(`
Використання: node cli.js [параметри]
Параметри:
  --project-dir <path>   Шлях до кодової бази для аудиту (за замовчуванням: поточна директорія)
  --output <path>        Шлях для збереження JSON-звіту (за замовчуванням: acceptance-report.json)
  --docker               Використовувати реальний Docker CLI замість внутрішньої емуляції
  --system <name>        Назва системи для акта приймання
  --help                 Показати цю довідку
`);
      process.exit(0);
    }
  }

  const validator = new CleanSlateValidator();
  const passed = await validator.runAudit({
    projectDir,
    reportPath,
    forceSimulation,
    systemName,
  });

  process.exitCode = passed ? 0 : 1;
}

main().catch((err) => {
  console.error("Критична помилка виконання валідатора:", err);
  process.exitCode = 1;
});
