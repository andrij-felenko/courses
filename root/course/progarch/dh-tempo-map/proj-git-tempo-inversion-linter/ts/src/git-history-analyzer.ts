import {
  PaceLayer,
  type CommitRecord,
  type ModuleMetrics,
  type PaceLayerType,
} from './types.ts';

/**
 * Модуль визначення архітектурного компонента для зіставлення з історією комітів.
 */
export interface ModuleDefinition {
  name: string;
  pathPrefix: string;
  description: string;
}

/**
 * Аналізатор історії комітів git.
 * Витягує частоту змін (change frequency) та обсяг правок (churn),
 * на основі чого емпірично класифікує модулі за картою темпів (Pace Layers).
 */
export class GitHistoryAnalyzer {
  private readonly defaultWindowDays: number;

  constructor(defaultWindowDays: number = 90) {
    this.defaultWindowDays = defaultWindowDays;
  }

  /**
   * Розбирає текстовий вивід команди `git log --numstat --pretty=format:"COMMIT:%H|%at|%an"`
   * у структурований список записів комітів.
   */
  public parseGitLogOutput(rawGitLog: string): CommitRecord[] {
    const commits: CommitRecord[] = [];
    const lines = rawGitLog.split('\n');
    let currentCommit: Partial<CommitRecord> | null = null;

    for (const rawLine of lines) {
      const line = rawLine.trim();
      if (!line) continue;

      if (line.startsWith('COMMIT:')) {
        if (currentCommit && currentCommit.hash) {
          commits.push(currentCommit as CommitRecord);
        }
        const parts = line.substring(7).split('|');
        const hash = parts[0] || 'unknown';
        const timestampSec = parseInt(parts[1] || '0', 10);
        const author = parts[2] || 'unknown';

        currentCommit = {
          hash,
          timestamp: timestampSec * 1000,
          author,
          files: [],
          linesAdded: 0,
          linesDeleted: 0,
        };
      } else if (currentCommit) {
        // Формат рядка numstat: <added>\t<deleted>\t<filepath>
        const statParts = line.split(/\s+/);
        if (statParts.length >= 3) {
          const added = parseInt(statParts[0] || '0', 10) || 0;
          const deleted = parseInt(statParts[1] || '0', 10) || 0;
          const filePath = statParts.slice(2).join(' ');

          currentCommit.files = currentCommit.files || [];
          currentCommit.files.push(filePath);
          currentCommit.linesAdded = (currentCommit.linesAdded || 0) + added;
          currentCommit.linesDeleted = (currentCommit.linesDeleted || 0) + deleted;
        }
      }
    }

    if (currentCommit && currentCommit.hash) {
      commits.push(currentCommit as CommitRecord);
    }

    return commits;
  }

  /**
   * Агрегує статистику для списку модулів на базі наданої історії комітів.
   */
  public analyzeModules(
    moduleDefs: ModuleDefinition[],
    commits: CommitRecord[]
  ): Map<string, ModuleMetrics> {
    const metricsMap = new Map<string, ModuleMetrics>();

    // Розраховуємо часове вікно аналізу в місяцях
    const windowMonths = this.calculateObservationWindowMonths(commits);

    for (const def of moduleDefs) {
      let moduleCommitsCount = 0;
      let moduleChurn = 0;

      for (const commit of commits) {
        const touchesModule = commit.files.some((filePath) =>
          filePath.startsWith(def.pathPrefix)
        );

        if (touchesModule) {
          moduleCommitsCount++;
          moduleChurn += commit.linesAdded + commit.linesDeleted;
        }
      }

      // Нормалізуємо частоту комітів до середньомісячного показника
      const monthlyFrequency =
        windowMonths > 0
          ? parseFloat((moduleCommitsCount / windowMonths).toFixed(2))
          : moduleCommitsCount;

      const layer = this.classifyPaceLayer(monthlyFrequency);

      metricsMap.set(def.name, {
        name: def.name,
        path: def.pathPrefix,
        commitsCount: moduleCommitsCount,
        totalChurn: moduleChurn,
        monthlyFrequency,
        layer,
        description: def.description,
      });
    }

    return metricsMap;
  }

  /**
   * Класифікує темп модуля на основі емпіричної кількості змін на місяць.
   */
  public classifyPaceLayer(monthlyFrequency: number): PaceLayerType {
    if (monthlyFrequency < 2.0) {
      return PaceLayer.FOUNDATION;
    }
    if (monthlyFrequency < 6.0) {
      return PaceLayer.CORE_DOMAIN;
    }
    if (monthlyFrequency < 15.0) {
      return PaceLayer.SUPPORTING;
    }
    if (monthlyFrequency < 35.0) {
      return PaceLayer.INTEGRATION;
    }
    return PaceLayer.VOLATILE_UI;
  }

  /**
   * Визначає тривалість періоду спостереження в місяцях (30-денний місяць).
   */
  private calculateObservationWindowMonths(commits: CommitRecord[]): number {
    if (commits.length < 2) {
      return Math.max(1, this.defaultWindowDays / 30);
    }

    const timestamps = commits.map((c) => c.timestamp);
    const minTime = Math.min(...timestamps);
    const maxTime = Math.max(...timestamps);
    const diffDays = Math.max(1, (maxTime - minTime) / (1000 * 60 * 60 * 24));

    return Math.max(1, parseFloat((diffDays / 30).toFixed(2)));
  }
}
