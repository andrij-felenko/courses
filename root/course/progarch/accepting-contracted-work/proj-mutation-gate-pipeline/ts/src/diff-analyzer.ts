import * as child_process from "node:child_process";
import * as fs from "node:fs";
import * as path from "node:path";

/** Опції налаштування аналізатора змін git diff */
export interface DiffAnalyzerOptions {
  baseBranch?: string;
  headBranch?: string;
  repoRoot?: string;
  fileExtensions?: string[];
  ignoredPatterns?: string[];
}

/**
 * GitDiffAnalyzer: виявляє змінені TypeScript-файли в поточному пул-реквесті
 * відносно базової гілки (за замовчуванням origin/main), відсікаючи тести,
 * декларації типів та сторонні залежності.
 */
export class GitDiffAnalyzer {
  private readonly baseBranch: string;
  private readonly headBranch: string;
  private readonly repoRoot: string;
  private readonly fileExtensions: string[];
  private readonly ignoredPatterns: string[];

  constructor(options: DiffAnalyzerOptions = {}) {
    this.baseBranch = options.baseBranch ?? "origin/main";
    this.headBranch = options.headBranch ?? "HEAD";
    this.repoRoot = options.repoRoot ?? process.cwd();
    this.fileExtensions = options.fileExtensions ?? [".ts", ".tsx"];
    this.ignoredPatterns = options.ignoredPatterns ?? [
      ".test.",
      ".spec.",
      ".d.ts",
      "node_modules/",
      "dist/",
      "coverage/",
    ];
  }

  /**
   * Виконує команду git diff та повертає очищений список цільових файлів
   */
  public getChangedFiles(): string[] {
    const rawDiff = this.executeGitDiff();
    if (!rawDiff.trim()) {
      return [];
    }

    const lines = rawDiff.split(String.fromCharCode(10));
    const filteredFiles: string[] = [];

    for (const rawLine of lines) {
      // Нормалізуємо роздільники шляхів без використання зворотних слешів
      const file = rawLine.trim().split(String.fromCharCode(92)).join("/");
      if (!file) {
        continue;
      }

      if (this.isTargetSourceFile(file)) {
        const fullPath = path.resolve(this.repoRoot, file);
        if (fs.existsSync(fullPath)) {
          filteredFiles.push(file);
        }
      }
    }

    return filteredFiles;
  }

  /**
   * Перевіряє, чи файл є цільовим модулем бізнес-логіки підрядника
   */
  public isTargetSourceFile(filePath: string): boolean {
    const hasValidExtension = this.fileExtensions.some((ext) =>
      filePath.endsWith(ext)
    );
    if (!hasValidExtension) {
      return false;
    }

    const isIgnored = this.ignoredPatterns.some((pattern) =>
      filePath.includes(pattern)
    );
    if (isIgnored) {
      return false;
    }

    return true;
  }

  /**
   * Викликає git diff через системний процес або повертає резервний список при автономному прогоні
   */
  private executeGitDiff(): string {
    const command = `git diff --name-only --diff-filter=ACMRTUXB ${this.baseBranch}...${this.headBranch}`;
    try {
      return child_process.execSync(command, {
        cwd: this.repoRoot,
        encoding: "utf-8",
        stdio: ["ignore", "pipe", "ignore"],
      });
    } catch {
      try {
        return child_process.execSync("git diff --name-only HEAD", {
          cwd: this.repoRoot,
          encoding: "utf-8",
          stdio: ["ignore", "pipe", "ignore"],
        });
      } catch {
        return "";
      }
    }
  }
}
