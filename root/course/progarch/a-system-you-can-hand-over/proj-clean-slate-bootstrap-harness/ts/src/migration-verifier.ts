export interface MigrationScript {
  version: string;
  name: string;
  upSql: string;
  downSql: string;
}

export interface MigrationStepResult {
  version: string;
  name: string;
  phase: "UP_1" | "DOWN" | "UP_2";
  durationMs: number;
  success: boolean;
  affectedEntities: string[];
  error?: string;
}

export interface MigrationAuditResult {
  passed: boolean;
  totalMigrations: number;
  steps: MigrationStepResult[];
  activeTables: string[];
  error?: string;
}

/**
 * Валідатор схеми даних та міграцій за парадигмою Clean-Slate.
 * Перевіряє двосторонню ідемпотентність за формулою UP -> DOWN -> UP:
 * 1. UP_1: Застосування міграцій з чистого аркуша
 * 2. DOWN: Повний відкат у зворотній послідовності та контроль відсутності залишкових об'єктів
 * 3. UP_2: Повторне застосування міграцій для гарантії детермінізму структури
 */
export class MigrationVerifier {
  private activeTables: Set<string> = new Set();

  /**
   * Еталонні навчальні міграції для верифікації чистого старту системи
   */
  public static getDefaultMigrations(): MigrationScript[] {
    return [
      {
        version: "001",
        name: "init_tenants_and_contracts",
        upSql: "CREATE TABLE tenants (id UUID PRIMARY KEY, name VARCHAR(255) NOT NULL, created_at TIMESTAMP DEFAULT NOW()); CREATE TABLE contracts (id UUID PRIMARY KEY, tenant_id UUID REFERENCES tenants(id), title VARCHAR(255) NOT NULL);",
        downSql: "DROP TABLE contracts; DROP TABLE tenants;",
      },
      {
        version: "002",
        name: "create_acceptance_deliverables",
        upSql: "CREATE TABLE deliverables (id UUID PRIMARY KEY, contract_id UUID REFERENCES contracts(id), status VARCHAR(50) NOT NULL, artifact_hash VARCHAR(128));",
        downSql: "DROP TABLE deliverables;",
      },
      {
        version: "003",
        name: "add_audit_log_index",
        upSql: "CREATE TABLE audit_logs (id BIGSERIAL PRIMARY KEY, entity_name VARCHAR(100), action VARCHAR(50), payload_json TEXT, logged_at TIMESTAMP DEFAULT NOW());",
        downSql: "DROP TABLE audit_logs;",
      },
    ];
  }

  public async verifyMigrations(scripts: MigrationScript[] = MigrationVerifier.getDefaultMigrations()): Promise<MigrationAuditResult> {
    const steps: MigrationStepResult[] = [];
    this.activeTables.clear();

    try {
      // 1. Фаза UP_1: Застосування з чистого аркуша
      for (const script of scripts) {
        const step = this.applyMigrationStep(script, "UP_1", script.upSql);
        steps.push(step);
        if (!step.success) {
          throw new Error(`Збій на першій фазі UP_1 (${script.version}_${script.name}): ${step.error}`);
        }
      }

      const tablesAfterFirstUp = Array.from(this.activeTables).sort();
      if (tablesAfterFirstUp.length === 0) {
        throw new Error("Фаза UP_1 не створила жодної таблиці бази даних.");
      }

      // 2. Фаза DOWN: Відкат у зворотній послідовності (LIFO)
      const reversedScripts = [...scripts].reverse();
      for (const script of reversedScripts) {
        const step = this.applyMigrationStep(script, "DOWN", script.downSql);
        steps.push(step);
        if (!step.success) {
          throw new Error(`Збій на фазі відкату DOWN (${script.version}_${script.name}): ${step.error}`);
        }
      }

      if (this.activeTables.size > 0) {
        const remaining = Array.from(this.activeTables).join(", ");
        throw new Error(`Після відкату виявлено залишковий бруд у схемі (залишились таблиці: ${remaining}). Міграції неідемпотентні!`);
      }

      // 3. Фаза UP_2: Повторне накочування міграцій
      for (const script of scripts) {
        const step = this.applyMigrationStep(script, "UP_2", script.upSql);
        steps.push(step);
        if (!step.success) {
          throw new Error(`Збій на повторній фазі UP_2 (${script.version}_${script.name}): ${step.error}`);
        }
      }

      const tablesAfterSecondUp = Array.from(this.activeTables).sort();
      const isConsistent = JSON.stringify(tablesAfterFirstUp) === JSON.stringify(tablesAfterSecondUp);

      if (!isConsistent) {
        throw new Error("Структура таблиць після повторного накатування не збігається з початковим станом UP_1.");
      }

      return {
        passed: true,
        totalMigrations: scripts.length,
        steps,
        activeTables: tablesAfterSecondUp,
      };
    } catch (err) {
      return {
        passed: false,
        totalMigrations: scripts.length,
        steps,
        activeTables: Array.from(this.activeTables),
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }

  private applyMigrationStep(script: MigrationScript, phase: "UP_1" | "DOWN" | "UP_2", sql: string): MigrationStepResult {
    const start = Date.now();
    const affected: string[] = [];

    try {
      const createMatches = sql.matchAll(/CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z0-9_]+)/gi);
      for (const m of createMatches) {
        const table = m[1].toLowerCase();
        if (this.activeTables.has(table)) {
          throw new Error(`Конфлікт створення: таблиця "${table}" вже існує в схемі.`);
        }
        this.activeTables.add(table);
        affected.push(table);
      }

      const dropMatches = sql.matchAll(/DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?([a-zA-Z0-9_]+)/gi);
      for (const m of dropMatches) {
        const table = m[1].toLowerCase();
        if (!this.activeTables.has(table)) {
          throw new Error(`Конфлікт відкату: таблиця "${table}" не знайдена для видалення.`);
        }
        this.activeTables.delete(table);
        affected.push(table);
      }

      return {
        version: script.version,
        name: script.name,
        phase,
        durationMs: Date.now() - start,
        success: true,
        affectedEntities: affected,
      };
    } catch (err) {
      return {
        version: script.version,
        name: script.name,
        phase,
        durationMs: Date.now() - start,
        success: false,
        affectedEntities: affected,
        error: err instanceof Error ? err.message : String(err),
      };
    }
  }
}
