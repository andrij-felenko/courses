/**
 * lockfile-validator.ts — Перевірка цілісності lockfile-файлів,
 * виявлення нефіксованих плаваючих версій, контроль хешів цілісності
 * та виявлення неоголошених зовнішніх джерел.
 */

import type {
  AcceptancePolicy,
  DependencyViolation,
  LockfileAuditResult,
} from './types.ts';

export class LockfileValidator {
  /**
   * Аналізує дерево залежностей та маніфест пакетів на предмет
   * детермінованості складання та відсутності плаваючих версій.
   */
  public validate(
    packageJsonRaw: string,
    lockfileRaw: string,
    policy: AcceptancePolicy
  ): LockfileAuditResult {
    const floatingVersions: DependencyViolation[] = [];
    const untrustedRegistries: { name: string; resolvedUrl: string }[] = [];
    const missingIntegrityHashes: string[] = [];

    let pkgJson: Record<string, unknown> = {};
    try {
      pkgJson = JSON.parse(packageJsonRaw);
    } catch {
      return {
        passed: false,
        totalDependencies: 0,
        floatingVersions: [
          { name: 'package.json', version: 'invalid', reason: 'Невалідний JSON у package.json' },
        ],
        untrustedRegistries: [],
        missingIntegrityHashes: [],
      };
    }

    let lockJson: Record<string, unknown> = {};
    try {
      lockJson = JSON.parse(lockfileRaw);
    } catch {
      return {
        passed: false,
        totalDependencies: 0,
        floatingVersions: [],
        untrustedRegistries: [],
        missingIntegrityHashes: ['lockfile має невалідний JSON або пошкоджений'],
      };
    }

    // 1. Перевірка прямого маніфесту package.json на плаваючі версії (^, ~, *, latest)
    if (policy.strictVersionPinning) {
      const depGroups = ['dependencies', 'devDependencies', 'peerDependencies'];
      for (const group of depGroups) {
        const deps = pkgJson[group] as Record<string, string> | undefined;
        if (!deps || typeof deps !== 'object') continue;

        for (const [depName, versionSpec] of Object.entries(deps)) {
          if (
            versionSpec.startsWith('^') ||
            versionSpec.startsWith('~') ||
            versionSpec.includes('*') ||
            versionSpec.includes('>') ||
            versionSpec.includes('<') ||
            versionSpec === 'latest'
          ) {
            floatingVersions.push({
              name: depName,
              version: versionSpec,
              reason: `Плаваючий діапазон версій заборонено контрактом відчуження: '${versionSpec}'`,
            });
          }
        }
      }
    }

    // 2. Аудит структури package-lock.json (npm v2/v3 підтримує поле 'packages', v1 'dependencies')
    let totalDependencies = 0;
    const disallowedRegistries = policy.disallowedPackageRegistries ?? ['http://'];

    const packages = (lockJson.packages as Record<string, Record<string, unknown>>) || {};
    const legacyDeps = (lockJson.dependencies as Record<string, Record<string, unknown>>) || {};

    const entriesToCheck: Array<{ name: string; info: Record<string, unknown> }> = [];

    if (Object.keys(packages).length > 0) {
      for (const [pkgPath, info] of Object.entries(packages)) {
        if (!pkgPath) continue; // Пропуск кореневого порожнього ключа ""
        const cleanName = pkgPath.replace(/^node_modules\//, '');
        entriesToCheck.push({ name: cleanName, info });
      }
    } else {
      for (const [name, info] of Object.entries(legacyDeps)) {
        entriesToCheck.push({ name, info });
      }
    }

    totalDependencies = entriesToCheck.length;

    for (const { name, info } of entriesToCheck) {
      // Перевірка цілісності: чи є SHA-хеш (integrity)
      const integrity = info.integrity as string | undefined;
      if (!integrity || !integrity.startsWith('sha')) {
        missingIntegrityHashes.push(
          `Пакет '${name}' не містить обов'язкового криптографічного хешу цілісності (integrity)`
        );
      }

      // Перевірка джерела завантаження (resolved)
      const resolved = info.resolved as string | undefined;
      if (resolved) {
        for (const disallowed of disallowedRegistries) {
          if (resolved.toLowerCase().includes(disallowed.toLowerCase())) {
            untrustedRegistries.push({
              name,
              resolvedUrl: resolved,
            });
            break;
          }
        }
      }
    }

    const passed =
      floatingVersions.length === 0 &&
      untrustedRegistries.length === 0 &&
      missingIntegrityHashes.length === 0;

    return {
      passed,
      totalDependencies,
      floatingVersions,
      untrustedRegistries,
      missingIntegrityHashes,
    };
  }
}
