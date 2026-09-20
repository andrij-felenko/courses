import * as ts from 'typescript';
import { CallGraphNode, CallSite, FunctionSignatureInfo } from './types';

/**
 * Будівник орієнтованого графа міжмодульних викликів (Call Graph).
 * Трасує всі файли проєкту, реєструє виклики цільових функцій утиліт,
 * ідентифікує підсистеми споживачів та агрегує структурні метрики залежностей.
 */
export class CallGraphBuilder {
  private readonly checker: ts.TypeChecker;
  private readonly targetFunctionNames: Set<string>;
  private readonly targetMap: Map<string, FunctionSignatureInfo>;
  private readonly utilsFilesSet: Set<string>;

  constructor(
    private readonly program: ts.Program,
    targetFunctions: FunctionSignatureInfo[]
  ) {
    this.checker = program.getTypeChecker();
    this.targetFunctionNames = new Set(targetFunctions.map((fn) => fn.name));
    this.targetMap = new Map(targetFunctions.map((fn) => [fn.name, fn]));
    this.utilsFilesSet = new Set(
      targetFunctions.map((fn) => this.normalizePath(fn.filePath))
    );
  }

  /**
   * Створює орієнтований граф викликів для всіх зареєстрованих утилітарних функцій.
   */
  public build(): Map<string, CallGraphNode> {
    // Ініціалізуємо вузли графа для кожної цільової функції
    const callGraph = new Map<string, CallGraphNode>();
    for (const [name, target] of this.targetMap.entries()) {
      callGraph.set(name, {
        functionName: name,
        declaringFilePath: target.filePath,
        callSites: [],
        callCount: 0,
        consumerModules: [],
        consumerFiles: [],
      });
    }

    // Скануємо всі файли кодової бази проєкту
    for (const sourceFile of this.program.getSourceFiles()) {
      // Ігноруємо декларативні файли типів (*.d.ts)
      if (sourceFile.isDeclarationFile) {
        continue;
      }

      const normalizedFilePath = this.normalizePath(sourceFile.fileName);

      // Якщо цей файл є самим файлом утиліт, пропускаємо його,
      // оскільки нас цікавить споживання ЗОВНІШНІМИ модулями проєкту
      if (this.utilsFilesSet.has(normalizedFilePath)) {
        continue;
      }

      const callerModuleName = this.extractModuleName(normalizedFilePath);
      const relativeCallerPath = this.getRelativePath(normalizedFilePath);

      this.traceCallsInFile(
        sourceFile,
        callerModuleName,
        relativeCallerPath,
        callGraph
      );
    }

    // Агрегуємо структурні метрики споживання для кожного вузла
    for (const node of callGraph.values()) {
      node.callCount = node.callSites.length;
      node.consumerModules = Array.from(
        new Set(node.callSites.map((cs) => cs.callerModuleName))
      ).sort();
      node.consumerFiles = Array.from(
        new Set(node.callSites.map((cs) => cs.callerFilePath))
      ).sort();
    }

    return callGraph;
  }

  /**
   * Здійснює рекурсивний обхід AST вихідного файла для пошуку CallExpression.
   */
  private traceCallsInFile(
    sourceFile: ts.SourceFile,
    callerModuleName: string,
    relativeCallerPath: string,
    callGraph: Map<string, CallGraphNode>
  ): void {
    let currentEnclosingFunction: string | undefined = undefined;

    const visit = (node: ts.Node): void => {
      // Фіксуємо ім'я функції або методу споживача для точного контексту виклику
      const previousEnclosing = currentEnclosingFunction;
      if (
        ts.isFunctionDeclaration(node) ||
        ts.isMethodDeclaration(node) ||
        ts.isClassDeclaration(node)
      ) {
        if (node.name) {
          currentEnclosingFunction = node.name.getText(sourceFile);
        }
      }

      // Перевіряємо вузол виклику функції: foo(...) або utils.foo(...)
      if (ts.isCallExpression(node)) {
        const calledName = this.resolveCalledFunctionName(node);
        if (calledName && this.targetFunctionNames.has(calledName)) {
          const graphNode = callGraph.get(calledName);
          if (graphNode) {
            const start = node.getStart(sourceFile);
            const { line, character } =
              sourceFile.getLineAndCharacterOfPosition(start);

            const site: CallSite = {
              callerFilePath: sourceFile.fileName,
              relativeCallerPath,
              callerModuleName,
              callerFunctionName: currentEnclosingFunction,
              line: line + 1,
              character: character + 1,
            };

            graphNode.callSites.push(site);
          }
        }
      }

      ts.forEachChild(node, visit);
      currentEnclosingFunction = previousEnclosing;
    };

    visit(sourceFile);
  }

  /**
   * Розв'язує назву функції, яка викликається у вузлі CallExpression.
   * Підтримує прямі виклики foo() та виклики через простір імен utils.foo().
   */
  private resolveCalledFunctionName(node: ts.CallExpression): string | null {
    const expr = node.expression;

    // Прямий виклик: foo(...)
    if (ts.isIdentifier(expr)) {
      // Спочатку перевіряємо символ через TypeChecker
      let symbol = this.checker.getSymbolAtLocation(expr);
      if (symbol && symbol.flags & ts.SymbolFlags.Alias) {
        symbol = this.checker.getAliasedSymbol(symbol);
      }
      if (symbol) {
        return symbol.name;
      }
      return expr.text;
    }

    // Виклик через властивість: utils.foo(...)
    if (ts.isPropertyAccessExpression(expr)) {
      let symbol = this.checker.getSymbolAtLocation(expr.name);
      if (symbol && symbol.flags & ts.SymbolFlags.Alias) {
        symbol = this.checker.getAliasedSymbol(symbol);
      }
      if (symbol) {
        return symbol.name;
      }
      return expr.name.text;
    }

    return null;
  }

  /**
   * Визначає назву підсистеми/модуля зі шляху до файла.
   * Наприклад, "src/billing/invoice.ts" -> "billing".
   */
  private extractModuleName(filePath: string): string {
    const normalized = this.normalizePath(filePath);
    const parts = normalized.split('/').filter(Boolean);

    const srcIndex = parts.lastIndexOf('src');
    if (srcIndex !== -1 && srcIndex + 1 < parts.length) {
      const nextSegment = parts[srcIndex + 1];
      // Якщо наступний сегмент не є самим файлом
      if (!nextSegment.endsWith('.ts') && !nextSegment.endsWith('.js')) {
        return nextSegment;
      }
    }

    // Якщо файл у корені або структура плоска, повертаємо назву файла без розширення
    const fileName = parts[parts.length - 1] ?? 'unknown';
    return fileName.replace(/\.[^/.]+$/, '');
  }

  private normalizePath(p: string): string {
    return p.replace(/\\/g, '/');
  }

  private getRelativePath(absolutePath: string): string {
    const normalized = this.normalizePath(absolutePath);
    const parts = normalized.split('/');
    const srcIndex = parts.lastIndexOf('src');
    if (srcIndex !== -1) {
      return parts.slice(srcIndex).join('/');
    }
    return parts.slice(-2).join('/');
  }
}
