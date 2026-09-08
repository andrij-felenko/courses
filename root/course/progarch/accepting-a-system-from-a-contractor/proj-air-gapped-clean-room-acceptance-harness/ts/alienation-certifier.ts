/**
 * alienation-certifier.ts — Формування та верифікація машинозчитуваного
 * сертифіката відчужуваності (Alienation Certificate) у форматі JSON
 * із фіксацією хешу репозиторію та вердиктів шлюзу.
 */

import * as crypto from 'node:crypto';
import * as fs from 'node:fs';
import * as path from 'node:path';
import type { AlienationCertificate, GateResults } from './types.ts';

export class AlienationCertifier {
  /**
   * Обчислює рекурсивний детермінований SHA-256 хеш вихідного коду репозиторію.
   */
  public computeRepositoryChecksum(dirPath: string): string {
    const hash = crypto.createHash('sha256');

    const scanDir = (currentDir: string): void => {
      const entries = fs.readdirSync(currentDir, { withFileTypes: true });
      // Детерміноване сортування за іменами файлів
      entries.sort((a, b) => a.name.localeCompare(b.name));

      for (const entry of entries) {
        const fullPath = path.join(currentDir, entry.name);

        if (
          entry.name === 'node_modules' ||
          entry.name === '.git' ||
          entry.name === 'dist' ||
          entry.name === 'coverage'
        ) {
          continue;
        }

        if (entry.isDirectory()) {
          scanDir(fullPath);
        } else if (entry.isFile()) {
          const relPath = path.relative(dirPath, fullPath).replace(/\\/g, '/');
          hash.update(relPath);
          const content = fs.readFileSync(fullPath);
          hash.update(content);
        }
      }
    };

    if (fs.existsSync(dirPath)) {
      scanDir(dirPath);
    } else {
      hash.update(dirPath);
    }

    return hash.digest('hex');
  }

  /**
   * Створює об'єкт сертифіката відчужуваності на основі вердиктів усіх фаз аудиту.
   */
  public generateCertificate(
    project: string,
    repositoryChecksum: string,
    gateResults: GateResults
  ): AlienationCertificate {
    const isAccepted =
      gateResults.lockfile.passed &&
      gateResults.bootstrap.passed &&
      gateResults.smoke.passed;

    const summary = isAccepted
      ? 'Усі контрактні вимоги приймального шлюзу виконано. Система придатна до відчуження та підписання акта.'
      : 'Приймальний шлюз заблоковано через виявлені дефекти або порушення контрактних SLA/залежностей.';

    return {
      version: '1.0.0-alienation',
      issuedAt: new Date().toISOString(),
      project,
      repositoryChecksum,
      acceptanceVerdict: isAccepted ? 'ACCEPTED' : 'REJECTED',
      gateResults,
      summary,
    };
  }

  /**
   * Генерує структурований звіт у форматі Markdown для передачі замовнику та включення в CI/CD.
   */
  public formatReportMarkdown(cert: AlienationCertificate): string {
    const statusEmoji = cert.acceptanceVerdict === 'ACCEPTED' ? '[PASS] ПРИЙНЯТО' : '[FAIL] ВІДХИЛЕНО';
    const alertBlock =
      cert.acceptanceVerdict === 'ACCEPTED'
        ? '> [!IMPORTANT]\n> Сертифікат відчужуваності підтверджено: система здатна розгортатися автономно без прихованих зв\'язків.'
        : '> [!WARNING]\n> Система не відповідає контрактним критеріям! Підписання фінального акта заблоковано.';

    const lines: string[] = [
      `# Сертифікат відчужуваності системи: ${cert.project}`,
      '',
      `**Фінальний вердикт**: \`${statusEmoji}\`  `,
      `**Дата видачі**: \`${cert.issuedAt}\`  `,
      `**Контрольний хеш репозиторію**: \`${cert.repositoryChecksum}\`  `,
      '',
      alertBlock,
      '',
      '## Результати перевірок приймального шлюзу (Acceptance Gate)',
      '',
      '| Етап аудиту | Статус | Деталі |',
      '| :--- | :---: | :--- |',
      `| 1. Цілісність lockfile та герметичність | ${cert.gateResults.lockfile.passed ? '**[PASS]**' : '**[FAIL]**'} | Перевірено ${cert.gateResults.lockfile.totalDependencies} залежностей |`,
      `| 2. Бюджет холодного старту (Cold-Start SLA) | ${cert.gateResults.bootstrap.passed ? '**[PASS]**' : '**[FAIL]**'} | Час: ${cert.gateResults.bootstrap.coldStartTimeMs}мс (бюджет: ${cert.gateResults.bootstrap.budgetMs}мс) |`,
      `| 3. Наскрізні димові тести (Smoke Scenarios) | ${cert.gateResults.smoke.passed ? '**[PASS]**' : '**[FAIL]**'} | Успішно ${cert.gateResults.smoke.passedProbes} із ${cert.gateResults.smoke.totalProbes} перевірок |`,
      '',
      '## Виявлені зауваження та дефекти',
      '',
    ];

    let hasViolations = false;

    if (cert.gateResults.lockfile.floatingVersions.length > 0) {
      hasViolations = true;
      lines.push('### Порушення фіксації версій у package.json:');
      for (const fv of cert.gateResults.lockfile.floatingVersions) {
        lines.push(`- ⚠️ \`${fv.name}\`: ${fv.reason}`);
      }
      lines.push('');
    }

    if (cert.gateResults.lockfile.untrustedRegistries.length > 0) {
      hasViolations = true;
      lines.push('### Недовірені реєстри пакетів:');
      for (const ur of cert.gateResults.lockfile.untrustedRegistries) {
        lines.push(`- ⚠️ \`${ur.name}\`: resolved URL \`${ur.resolvedUrl}\``);
      }
      lines.push('');
    }

    if (cert.gateResults.bootstrap.error) {
      hasViolations = true;
      lines.push('### Порушення SLA холодного старту:');
      lines.push(`- ⚠️ ${cert.gateResults.bootstrap.error}`);
      lines.push('');
    }

    const failedSmoke = cert.gateResults.smoke.results.filter((r) => !r.passed);
    if (failedSmoke.length > 0) {
      hasViolations = true;
      lines.push('### Збої димових перевірок:');
      for (const fs of failedSmoke) {
        lines.push(`- ⚠️ [${fs.name}] ${fs.url}: ${fs.error}`);
      }
      lines.push('');
    }

    if (!hasViolations) {
      lines.push('Жодних критичних зауважень не виявлено. Кодова база повністю відповідає вимогам відчужуваності.');
    }

    return lines.join('\n');
  }
}
