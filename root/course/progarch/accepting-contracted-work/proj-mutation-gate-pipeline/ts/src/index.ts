import { GitDiffAnalyzer } from "./diff-analyzer.ts";
import { StrykerConfigBuilder } from "./stryker-config-builder.ts";
import { MutationRunner } from "./mutation-runner.ts";
import { MutationQualityGate } from "./quality-gate.ts";
import { GithubReportGenerator } from "./report-generator.ts";

/** Опції запуску мутаційного гейта приймання */
export interface GateCliOptions {
  baseBranch?: string;
  threshold?: number;
  reportPath?: string;
}

/**
 * Головна функція запуску конвеєра мутаційного аудиту
 */
export async function runMutationGate(
  options: GateCliOptions = {}
): Promise<boolean> {
  const baseBranch = options.baseBranch ?? "origin/main";
  const threshold = options.threshold ?? 80;
  const reportPath = options.reportPath ?? "acceptance-mutation-report.json";

  const lf = String.fromCharCode(10);

  process.stdout.write(`=== Мутаційний шлюз приймання робіт від підрядника ===${lf}`);
  process.stdout.write(`Базова гілка порівняння: ${baseBranch}${lf}`);
  process.stdout.write(
    `Вимога Definition of Done: Mutation Score >= ${threshold}%${lf}${lf}`
  );

  // Крок 1: Диференційний аналіз змінених файлів
  process.stdout.write("[1/5] Виконання диференційного аналізу git diff... ");
  const analyzer = new GitDiffAnalyzer({ baseBranch });
  let changedFiles = analyzer.getChangedFiles();

  if (changedFiles.length === 0) {
    changedFiles = ["src/order-service.ts", "src/payment-handler.ts"];
    process.stdout.write(
      `(використано тестовий набір модулів: ${changedFiles.length} файлів)${lf}`
    );
  } else {
    process.stdout.write(`знайдено ${changedFiles.length} змінених файлів${lf}`);
  }

  for (const f of changedFiles) {
    process.stdout.write(`  • ${f}${lf}`);
  }

  // Крок 2: Побудова динамічної конфігурації Stryker
  process.stdout.write(`${lf}[2/5] Генерація конфігурації Stryker Mutator... `);
  const configBuilder = new StrykerConfigBuilder({ threshold });
  const strykerConfig = configBuilder.build(changedFiles);
  process.stdout.write(`успішно сформовано${lf}`);

  // Крок 3: Запуск мутаційного тестування
  process.stdout.write(`${lf}[3/5] Запуск мутаційного тестування підрядного коду...${lf}`);
  const runner = new MutationRunner();
  const summary = await runner.run(strykerConfig);

  process.stdout.write(`  Загалом мутантів: ${summary.totalMutants}${lf}`);
  process.stdout.write(`  Вбито (Killed): ${summary.killed}${lf}`);
  process.stdout.write(`  Вціліло (Survived): ${summary.survived}${lf}`);
  process.stdout.write(`  Таймаути (TimedOut): ${summary.timedOut}${lf}`);
  process.stdout.write(
    `  Підсумковий Mutation Score: ${summary.mutationScore}%${lf}`
  );

  // Крок 4: Оцінка якості Definition of Done
  process.stdout.write(
    `${lf}[4/5] Валідація результатів проти Definition of Done...${lf}`
  );
  const gate = new MutationQualityGate(threshold);
  const evaluation = gate.evaluate(summary);

  for (const reason of evaluation.reasons) {
    process.stdout.write(`  • ${reason}${lf}`);
  }

  // Крок 5: Генерація звітів та анотацій для CI
  process.stdout.write(
    `${lf}[5/5] Експорт машинозчитуваного паспорта приймання... `
  );
  const reportGenerator = new GithubReportGenerator(reportPath);
  reportGenerator.savePassport(summary, evaluation, changedFiles);
  process.stdout.write(`збережено в ${reportPath}${lf}`);

  const survivedMutants = gate.getSurvivedMutants(summary);
  if (survivedMutants.length > 0) {
    process.stdout.write(
      `${lf}Діагностика вцілілих мутантів (GitHub Actions annotations):${lf}`
    );
    reportGenerator.emitGithubAnnotations(survivedMutants);
  }

  process.stdout.write(
    `${lf}======================================================${lf}`
  );
  if (evaluation.isPassing) {
    process.stdout.write(
      `ВЕРДИКТ: ПРИЙМАННЯ УСПІШНЕ (Exit Code 0). Код готовий до злиття.${lf}`
    );
  } else {
    process.stdout.write(
      `ВЕРДИКТ: ПРИЙМАННЯ ЗАБЛОКОВАНО (Exit Code 1). Вимоги надійності порушено.${lf}`
    );
  }
  process.stdout.write(
    `======================================================${lf}`
  );

  return evaluation.isPassing;
}

// Автономний запуск при прямому виклику скрипта
runMutationGate()
  .then((isPassing) => {
    process.exitCode = isPassing ? 0 : 1;
  })
  .catch((err) => {
    process.stderr.write(
      `Фатальна помилка мутаційного шлюзу: ${err.message}${String.fromCharCode(10)}`
    );
    process.exitCode = 2;
  });
