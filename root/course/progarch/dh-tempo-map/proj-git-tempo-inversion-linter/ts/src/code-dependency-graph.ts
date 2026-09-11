import type {
  DependencyEdge,
  DependencyGraph,
  ModuleMetrics,
  SourceFile,
} from './types.ts';

/**
 * Парсер і генератор графа залежностей між архітектурними модулями.
 * Сканує директиви ES-імпортів та CommonJS require, виявляючи зв'язки між модулями.
 */
export class CodeDependencyGraph {
  private readonly modulePrefixes: { name: string; prefix: string }[];

  constructor(moduleMetrics: Map<string, ModuleMetrics>) {
    this.modulePrefixes = Array.from(moduleMetrics.values()).map((m) => ({
      name: m.name,
      prefix: m.path.replace(/\\/g, '/').replace(/\/$/, ''),
    }));
  }

  /**
   * Будує граф залежностей на базі переданого списку вихідних файлів системи.
   */
  public buildGraph(
    sourceFiles: SourceFile[],
    moduleMetrics: Map<string, ModuleMetrics>
  ): DependencyGraph {
    const edges: DependencyEdge[] = [];

    for (const file of sourceFiles) {
      const normalizedPath = file.path.replace(/\\/g, '/');
      const sourceModule = this.resolveModuleForPath(normalizedPath);
      if (!sourceModule) continue;

      const fileEdges = this.extractDependenciesFromFile(
        file,
        sourceModule,
        normalizedPath
      );
      edges.push(...fileEdges);
    }

    return {
      modules: moduleMetrics,
      edges,
    };
  }

  /**
   * Витягує залежності з одного файлу.
   */
  private extractDependenciesFromFile(
    file: SourceFile,
    sourceModuleName: string,
    sourceFilePath: string
  ): DependencyEdge[] {
    const edges: DependencyEdge[] = [];
    const lines = file.content.split('\n');

    // Регулярні вирази для пошуку імпортів
    // 1) import ... from '...'
    const esImportRegex = /import\s+(?:([\w*\s{},]+)\s+from\s+)?['"]([^'"]+)['"]/g;
    // 2) require('...')
    const cjsRequireRegex = /(?:const|let|var)\s+([\w*\s{},]+)\s*=\s*require\(['"]([^'"]+)['"]\)/g;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i] || '';
      const lineNumber = i + 1;

      // Пропускаємо коментарі
      const trimmed = line.trim();
      if (trimmed.startsWith('//') || trimmed.startsWith('/*')) continue;

      // Перевірка ES-імпортів
      let match: RegExpExecArray | null;
      while ((match = esImportRegex.exec(line)) !== null) {
        const rawSymbols = match[1] || '';
        const importSpecifier = match[2] || '';
        const targetModule = this.resolveTargetModule(
          sourceFilePath,
          importSpecifier
        );

        if (targetModule && targetModule !== sourceModuleName) {
          edges.push({
            sourceModule: sourceModuleName,
            targetModule,
            importPath: importSpecifier,
            importedSymbols: this.parseImportedSymbols(rawSymbols),
            sourceFile: sourceFilePath,
            lineNumber,
          });
        }
      }

      // Перевірка CommonJS require
      while ((match = cjsRequireRegex.exec(line)) !== null) {
        const rawSymbols = match[1] || '';
        const importSpecifier = match[2] || '';
        const targetModule = this.resolveTargetModule(
          sourceFilePath,
          importSpecifier
        );

        if (targetModule && targetModule !== sourceModuleName) {
          edges.push({
            sourceModule: sourceModuleName,
            targetModule,
            importPath: importSpecifier,
            importedSymbols: this.parseImportedSymbols(rawSymbols),
            sourceFile: sourceFilePath,
            lineNumber,
          });
        }
      }
    }

    return edges;
  }

  /**
   * Визначає, якому модулю належить файл за його шляхом.
   */
  private resolveModuleForPath(filePath: string): string | null {
    for (const mod of this.modulePrefixes) {
      if (filePath.startsWith(mod.prefix)) {
        return mod.name;
      }
    }
    return null;
  }

  /**
   * Резолвить імпортований шлях (відносний або аліас) до імені цільового модуля.
   */
  private resolveTargetModule(
    currentFilePath: string,
    importSpecifier: string
  ): string | null {
    // Ігноруємо зовнішні пакети node_modules
    if (!importSpecifier.startsWith('.') && !importSpecifier.startsWith('/') && !importSpecifier.startsWith('@digital-homes/')) {
      return null;
    }

    // Обробка аліасу @digital-homes/<module-name>
    if (importSpecifier.startsWith('@digital-homes/')) {
      const aliasName = importSpecifier.replace('@digital-homes/', '').split('/')[0];
      for (const mod of this.modulePrefixes) {
        if (mod.name.endsWith(aliasName || '')) {
          return mod.name;
        }
      }
    }

    // Обробка відносних шляхів (../, ./)
    if (importSpecifier.startsWith('.')) {
      const currentDirParts = currentFilePath.split('/').slice(0, -1);
      const specifierParts = importSpecifier.split('/');

      const resolvedParts = [...currentDirParts];
      for (const part of specifierParts) {
        if (part === '.') continue;
        if (part === '..') {
          resolvedParts.pop();
        } else {
          resolvedParts.push(part);
        }
      }

      const resolvedPath = resolvedParts.join('/');
      return this.resolveModuleForPath(resolvedPath);
    }

    return null;
  }

  /**
   * Парсить список імпортованих сутностей.
   */
  private parseImportedSymbols(symbolsStr: string): string[] {
    if (!symbolsStr) return [];
    return symbolsStr
      .replace(/[{}\n\r]/g, '')
      .split(',')
      .map((s) => s.trim())
      .filter((s) => s.length > 0);
  }
}
