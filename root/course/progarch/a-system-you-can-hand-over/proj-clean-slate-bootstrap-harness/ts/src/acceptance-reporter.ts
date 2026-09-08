import * as fs from "node:fs";
import * as path from "node:path";

export type AuditPhaseName =
  | "manifest_audit"
  | "container_orchestration"
  | "database_migrations"
  | "smoke_testing";

export interface PhaseRecord {
  phase: AuditPhaseName;
  title: string;
  passed: boolean;
  durationMs: number;
  details: unknown;
  error?: string;
}

export interface AcceptanceReport {
  schemaVersion: "1.0.0";
  timestamp: string;
  systemName: string;
  gateVerdict: "ACCEPTED" | "REJECTED";
  gatePassed: boolean;
  metrics: {
    totalPhases: number;
    passedPhases: number;
    failedPhases: number;
    totalDurationMs: number;
  };
  phases: PhaseRecord[];
}

/**
 * Репортер результатів технічного приймання.
 * Формує машинозчитуваний JSON-артефакт для CI/CD та форматований консольний звіт.
 */
export class AcceptanceReporter {
  private records: PhaseRecord[] = [];

  public recordPhase(record: PhaseRecord): void {
    this.records.push(record);
  }

  public generateReport(systemName: string): AcceptanceReport {
    const passedPhases = this.records.filter((r) => r.passed).length;
    const failedPhases = this.records.length - passedPhases;
    const gatePassed = failedPhases === 0;
    const totalDurationMs = this.records.reduce((acc, r) => acc + r.durationMs, 0);

    return {
      schemaVersion: "1.0.0",
      timestamp: new Date().toISOString(),
      systemName,
      gateVerdict: gatePassed ? "ACCEPTED" : "REJECTED",
      gatePassed,
      metrics: {
        totalPhases: this.records.length,
        passedPhases,
        failedPhases,
        totalDurationMs,
      },
      phases: [...this.records],
    };
  }

  public saveReportJson(filePath: string, report: AcceptanceReport): void {
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(filePath, JSON.stringify(report, null, 2), "utf8");
  }

  public printConsoleSummary(report: AcceptanceReport): void {
    console.log("\n=======================================================");
    console.log(` АКТ ТЕХНІЧНОГО ПРИЙМАННЯ СИСТЕМИ: ${report.systemName}`);
    console.log(` Час аудиту: ${report.timestamp}`);
    console.log("=======================================================");

    for (const p of report.phases) {
      const statusIcon = p.passed ? "[ПРОЙДЕНО]" : "[ВІДХИЛЕНО]";
      console.log(`${statusIcon.padEnd(12)} ${p.title.padEnd(40)} (${p.durationMs}мс)`);
      if (p.error) {
        console.log(`             └─ Дефект: ${p.error}`);
      }
    }

    console.log("-------------------------------------------------------");
    console.log(` Всього фаз: ${report.metrics.totalPhases} | Пройдено: ${report.metrics.passedPhases} | Провалено: ${report.metrics.failedPhases}`);
    console.log(` Загальний час: ${report.metrics.totalDurationMs}мс`);
    console.log(` ВЕРДИКТ ШЛЮЗУ: [${report.gateVerdict}]`);
    console.log("=======================================================\n");
  }
}
