import * as fs from "node:fs";
import * as path from "node:path";

/** Рівень критичності виявленого дефекту в маніфестах залежностей */
export type ViolationSeverity = "ERROR" | "WARN";

/** Деталізований опис дефекту залежності */
export interface AuditViolation {
  packageName: string;
  sourceField: "dependencies" | "devDependencies" | "lockfile";
  declaredVersion: string;
  issue: string;
  severity: ViolationSeverity;
}

/** Підсумковий результат аудиту маніфестів */
export interface ManifestAuditResult {
  passed: boolean;
  totalDependenciesChecked: number;
  violations: AuditViolation[];
}

/**
 * Аудитор маніфестів package.json та package-lock.json на герметичність залежностей.
 * Виявляє плаваючі діапазони (^, ~, *), незафіксовані протоколи (file:, git:) та відсутність хешів цілісності.
 */
export class ManifestAuditor {
  private static readonly FLOATING_PREFIXES = ["^", "~", ">", "<", "*", "latest"];
  private static readonly UNSTABLE_PROTOCOLS = ["git://", "http://", "file:", "link:"];

  /**
   * Виконує статичний аудит файлів package.json та package-lock.json у вказаній директорії.
   */
  public auditDirectory(targetDir: string): ManifestAuditResult {
    const packageJsonPath = path.join(targetDir, "package.json");
    const packageLockPath = path.join(targetDir, "package-lock.json");
    const violations: AuditViolation[] = [];

    if (!fs.existsSync(packageJsonPath)) {
      return {
        passed: false,
        totalDependenciesChecked: 0,
        violations: [
          {
            packageName: "package.json",
            sourceField: "dependencies",
            declaredVersion: "absent",
            issue: `Маніфест package.json не знайдено за шляхом: ${packageJsonPath}`,
            severity: "ERROR",
          },
        ],
      };
    }

    let packageJson: {
      dependencies?: Record<string, string>;
      devDependencies?: Record<string, string>;
    };

    try {
      packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
    } catch (err) {
      return {
        passed: false,
        totalDependenciesChecked: 0,
        violations: [
          {
            packageName: "package.json",
            sourceField: "dependencies",
            declaredVersion: "corrupted",
            issue: `Помилка розбору JSON: ${err instanceof Error ? err.message : String(err)}`,
            severity: "ERROR",
          },
        ],
      };
    }

    let checkedCount = 0;
    checkedCount += this.checkDependencySection(packageJson.dependencies, "dependencies", violations);
    checkedCount += this.checkDependencySection(packageJson.devDependencies, "devDependencies", violations);

    this.checkLockfile(packageLockPath, violations);

    const hasErrors = violations.some((v) => v.severity === "ERROR");
    return {
      passed: !hasErrors,
      totalDependenciesChecked: checkedCount,
      violations,
    };
  }

  private checkDependencySection(
    section: Record<string, string> | undefined,
    field: "dependencies" | "devDependencies",
    violations: AuditViolation[]
  ): number {
    if (!section) return 0;
    let count = 0;

    for (const [pkg, rawVersion] of Object.entries(section)) {
      count++;
      const ver = rawVersion.trim();

      const isFloating = ManifestAuditor.FLOATING_PREFIXES.some(
        (prefix) => ver.startsWith(prefix) || ver === prefix
      );
      if (isFloating) {
        violations.push({
          packageName: pkg,
          sourceField: field,
          declaredVersion: ver,
          issue: "Плаваючий діапазон версії порушує герметичність збірки. Вимагається точна фіксація (exact pin).",
          severity: "ERROR",
        });
      }

      const isUnstable = ManifestAuditor.UNSTABLE_PROTOCOLS.some((proto) => ver.startsWith(proto));
      if (isUnstable) {
        violations.push({
          packageName: pkg,
          sourceField: field,
          declaredVersion: ver,
          issue: `Негерметичне джерело пакета (${ver}). Посилання на локальні шляхи або незахищені мережі заборонені.`,
          severity: "ERROR",
        });
      }
    }

    return count;
  }

  private checkLockfile(lockPath: string, violations: AuditViolation[]): void {
    if (!fs.existsSync(lockPath)) {
      violations.push({
        packageName: "package-lock.json",
        sourceField: "lockfile",
        declaredVersion: "absent",
        issue: "Файл package-lock.json відсутній. Повна відтворюваність дерева залежностей неможлива.",
        severity: "ERROR",
      });
      return;
    }

    try {
      const lockData = JSON.parse(fs.readFileSync(lockPath, "utf8"));
      const packagesMap: Record<string, { integrity?: string; resolved?: string }> =
        lockData.packages ?? lockData.dependencies;

      if (!packagesMap || Object.keys(packagesMap).length === 0) {
        violations.push({
          packageName: "package-lock.json",
          sourceField: "lockfile",
          declaredVersion: "empty",
          issue: "Файл package-lock.json порожній або не містить інформації про дерево пакетів.",
          severity: "ERROR",
        });
        return;
      }

      for (const [key, details] of Object.entries(packagesMap)) {
        if (!key || key === "") continue;
        if (!details.integrity) {
          violations.push({
            packageName: key,
            sourceField: "lockfile",
            declaredVersion: details.resolved ?? "unresolved",
            issue: "Відсутній криптографічний хеш цілісності (integrity sha512/sha256).",
            severity: "WARN",
          });
        }
      }
    } catch (err) {
      violations.push({
        packageName: "package-lock.json",
        sourceField: "lockfile",
        declaredVersion: "corrupted",
        issue: `Неможливо прочитати lockfile: ${err instanceof Error ? err.message : String(err)}`,
        severity: "ERROR",
      });
    }
  }
}
