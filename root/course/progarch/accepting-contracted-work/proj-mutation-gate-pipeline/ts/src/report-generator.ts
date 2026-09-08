import * as fs from "node:fs";
import * as path from "node:path";
import { MutationRunSummary, MutantResult } from "./mutation-runner.ts";
import { QualityGateEvaluation } from "./quality-gate.ts";

/** Структура підсумкового паспорта приймання робіт */
export interface AcceptancePassport {
  schemaVersion: string;
  generatedAt: string;
  targetFiles: string[];
  evaluation: QualityGateEvaluation;
  summary: {
    totalMutants: number;
    killed: number;
    survived: number;
    timedOut: number;
    durationMs: number;
  };
  survivedMutants: Array<{
    id: string;
    file: string;
    line: number;
    column: number;
    mutator: string;
    original: string;
    replacement: string;
  }>;
}

/**
 * GithubReportGenerator: експортує машинозчитуваний JSON-паспорт аудиту
 * та формує діагностичні команди (annotations/summary) для GitHub Actions.
 */
export class GithubReportGenerator {
  private readonly outputPath: string;

  constructor(outputPath: string = "acceptance-mutation-report.json") {
    this.outputPath = outputPath;
  }

  /**
   * Формує та зберігає підсумковий JSON-паспорт мутаційного приймання
   */
  public savePassport(
    summary: MutationRunSummary,
    evaluation: QualityGateEvaluation,
    targetFiles: string[]
  ): AcceptancePassport {
    const survived = summary.mutants.filter((m) => m.status === "Survived");

    const passport: AcceptancePassport = {
      schemaVersion: "1.0.0",
      generatedAt: new Date().toISOString(),
      targetFiles: [...targetFiles],
      evaluation,
      summary: {
        totalMutants: summary.totalMutants,
        killed: summary.killed,
        survived: summary.survived,
        timedOut: summary.timedOut,
        durationMs: summary.durationMs,
      },
      survivedMutants: survived.map((m) => ({
        id: m.id,
        file: m.fileName,
        line: m.location.start.line,
        column: m.location.start.column,
        mutator: m.mutatorName,
        original: m.original,
        replacement: m.replacement,
      })),
    };

    const dir = path.dirname(path.resolve(this.outputPath));
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(
      this.outputPath,
      JSON.stringify(passport, null, 2),
      "utf-8"
    );

    return passport;
  }

  /**
   * Виводить анотації в stdout згідно з синтаксисом GitHub Actions Workflow Commands
   */
  public emitGithubAnnotations(survivedMutants: MutantResult[]): void {
    const lf = String.fromCharCode(10);
    for (const m of survivedMutants) {
      const line = m.location.start.line;
      const col = m.location.start.column;
      const msg = `Вцілілий мутант [${m.mutatorName}]: заміна '${m.original}' на '${m.replacement}' не виявлена жодним тестом підрядника.`;
      process.stdout.write(`::error file=${m.fileName},line=${line},col=${col}::${msg}${lf}`);
    }
  }

  /**
   * Формує Markdown-звіт для збереження у GITHUB_STEP_SUMMARY
   */
  public generateMarkdownSummary(passport: AcceptancePassport): string {
    const lf = String.fromCharCode(10);
    const statusBadge = passport.evaluation.isPassing
      ? "PASSED (Приймання дозволено)"
      : "FAILED (Блокування злиття)";

    const lines: string[] = [
      "## Паспорт мутаційного аудиту приймання коду (Stryker Gate)",
      "",
      `**Статус гейта:** ${statusBadge}`,
      `**Mutation Score:** ${passport.evaluation.actualScore}% (норматив DoD: ${passport.evaluation.requiredThreshold}%)`,
      `**Вбито мутантів:** ${passport.summary.killed} / ${passport.summary.totalMutants}`,
      `**Вціліло мутантів:** ${passport.summary.survived}`,
      "",
      "### Змінені файли підрядника під аудитом:",
    ];

    for (const file of passport.targetFiles) {
      lines.push("  - " + file);
    }
    lines.push("");

    if (passport.survivedMutants.length > 0) {
      lines.push("### Перелік вцілілих мутацій (дефекти у тестах підрядника):");
      lines.push("| Файл | Рядок | Оператор | Початковий код | Мутація |");
      lines.push("| :--- | :--- | :--- | :--- | :--- |");
      for (const s of passport.survivedMutants) {
        lines.push(
          "| " + s.file + " | " + s.line + ":" + s.column + " | " + s.mutator + " | " + s.original + " | " + s.replacement + " |"
        );
      }
      lines.push("");
    }

    return lines.join(lf);
  }
}
