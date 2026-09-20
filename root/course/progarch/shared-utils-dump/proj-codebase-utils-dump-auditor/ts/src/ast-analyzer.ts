import * as ts from 'typescript';
import {
  FunctionParameterInfo,
  FunctionSignatureInfo,
  TypeLeakDetail,
} from './types';

/**
 * Аналізатор синтаксичного дерева утилітарних файлів.
 * Використовує TypeScript Compiler API та TypeChecker для вилучення
 * експортованих функцій і семантичного виявлення доменних витоків.
 */
export class AstAnalyzer {
  private readonly checker: ts.TypeChecker;
  private readonly domainKeywords: string[];

  /**
   * Стандартні примітивні та утилітарні типи мови, які є доменно-нейтральними.
   */
  private static readonly BUILTIN_NEUTRAL_TYPES = new Set<string>([
    'string',
    'number',
    'boolean',
    'symbol',
    'bigint',
    'undefined',
    'null',
    'void',
    'never',
    'any',
    'unknown',
    'object',
    'Date',
    'RegExp',
    'Array',
    'ReadonlyArray',
    'Map',
    'Set',
    'Promise',
    'Record',
    'Partial',
    'Required',
    'Readonly',
    'Pick',
    'Omit',
    'Exclude',
    'Extract',
    'NonNullable',
    'ReturnType',
    'InstanceType',
  ]);

  constructor(
    private readonly program: ts.Program,
    customDomainKeywords: string[] = []
  ) {
    this.checker = program.getTypeChecker();
    this.domainKeywords = [
      'order',
      'customer',
      'tier',
      'invoice',
      'payment',
      'cart',
      'product',
      'user',
      'account',
      'subscription',
      'discount',
      'billing',
      'shipping',
      'basket',
      ...customDomainKeywords.map((k) => k.toLowerCase()),
    ];
  }

  /**
   * Аналізує конкретний вихідний файл утиліт і повертає список сигнатур усіх експортованих функцій.
   */
  public analyzeSourceFile(sourceFile: ts.SourceFile): FunctionSignatureInfo[] {
    const exportedFunctions: FunctionSignatureInfo[] = [];

    const visit = (node: ts.Node): void => {
      // 1. Оголошення функції: function foo(...)
      if (ts.isFunctionDeclaration(node)) {
        if (this.hasExportModifier(node) && node.name) {
          const signatureInfo = this.extractFunctionSignature(
            node,
            node.name.text,
            sourceFile
          );
          if (signatureInfo) {
            exportedFunctions.push(signatureInfo);
          }
        }
      }

      // 2. Експортовані змінні: export const foo = (...) => ...
      if (ts.isVariableStatement(node) && this.hasExportModifier(node)) {
        for (const declaration of node.declarationList.declarations) {
          if (
            ts.isIdentifier(declaration.name) &&
            declaration.initializer &&
            (ts.isArrowFunction(declaration.initializer) ||
              ts.isFunctionExpression(declaration.initializer))
          ) {
            const signatureInfo = this.extractFunctionSignature(
              declaration.initializer,
              declaration.name.text,
              sourceFile
            );
            if (signatureInfo) {
              exportedFunctions.push(signatureInfo);
            }
          }
        }
      }

      ts.forEachChild(node, visit);
    };

    visit(sourceFile);
    return exportedFunctions;
  }

  /**
   * Аналізує перелік цільових файлів утиліт.
   */
  public analyzeFiles(filePaths: string[]): FunctionSignatureInfo[] {
    const results: FunctionSignatureInfo[] = [];
    for (const filePath of filePaths) {
      const normalized = filePath.replace(/\\/g, '/');
      const sourceFile =
        this.program.getSourceFile(filePath) ||
        this.program.getSourceFile(normalized);

      if (sourceFile) {
        results.push(...this.analyzeSourceFile(sourceFile));
      }
    }
    return results;
  }

  /**
   * Вилучає метадані сигнатури функції, типи аргументів і результат,
   * а також перевіряє наявність витоків предметної області.
   */
  private extractFunctionSignature(
    funcNode:
      | ts.FunctionDeclaration
      | ts.ArrowFunction
      | ts.FunctionExpression,
    functionName: string,
    sourceFile: ts.SourceFile
  ): FunctionSignatureInfo | null {
    const startPos = funcNode.getStart(sourceFile);
    const { line, character } = sourceFile.getLineAndCharacterOfPosition(startPos);

    const parameters: FunctionParameterInfo[] = [];
    const leakedTypes: TypeLeakDetail[] = [];

    // Інспектуємо параметри функції
    for (const param of funcNode.parameters) {
      const paramName = param.name.getText(sourceFile);
      const isOptional = Boolean(param.questionToken || param.initializer);

      let typeName = 'any';
      if (param.type) {
        typeName = param.type.getText(sourceFile);
      } else {
        const paramType = this.checker.getTypeAtLocation(param);
        typeName = this.checker.typeToString(paramType);
      }

      parameters.push({
        name: paramName,
        typeName,
        isOptional,
      });

      // Перевіряємо тип параметра на доменний витік
      const paramTypeObj = this.checker.getTypeAtLocation(param);
      const leak = this.detectDomainLeak(
        paramTypeObj,
        typeName,
        'parameter',
        paramName
      );
      if (leak) {
        leakedTypes.push(leak);
      }
    }

    // Інспектуємо значення, що повертається
    let returnTypeName = 'void';
    const signature = this.checker.getSignatureFromDeclaration(funcNode);

    if (signature) {
      const returnType = this.checker.getReturnTypeOfSignature(signature);
      returnTypeName = this.checker.typeToString(returnType);

      const leak = this.detectDomainLeak(
        returnType,
        returnTypeName,
        'return',
        'return'
      );
      if (leak) {
        leakedTypes.push(leak);
      }
    } else if (funcNode.type) {
      returnTypeName = funcNode.type.getText(sourceFile);
    }

    const relativePath = this.getRelativePath(sourceFile.fileName);

    return {
      name: functionName,
      filePath: sourceFile.fileName,
      relativeFilePath: relativePath,
      line: line + 1,
      character: character + 1,
      parameters,
      returnTypeName,
      isExported: true,
      leakedDomainTypes: leakedTypes,
    };
  }

  /**
   * Семантичний детектор доменних типів.
   * Виявляє, чи тип належить до сутностей бізнес-моделі (Order, CustomerTier тощо),
   * а не до системних або мовних примітивів.
   */
  private detectDomainLeak(
    type: ts.Type,
    typeNameString: string,
    location: 'parameter' | 'return',
    identifierName: string
  ): TypeLeakDetail | null {
    // 1. Якщо це базовий нейтральний примітив або дженерик-параметр (T, K, V)
    const cleanTypeName = typeNameString.replace(/[\[\]]/g, '').trim();
    if (AstAnalyzer.BUILTIN_NEUTRAL_TYPES.has(cleanTypeName)) {
      return null;
    }
    if (/^[A-Z]$/.test(cleanTypeName)) {
      // Поодинокі літери на зразок T, U, V, R є параметрами типізації дженериків
      return null;
    }

    // 2. Перевірка за декларацією типу через TypeChecker
    const symbol = type.aliasSymbol ?? type.getSymbol();
    if (symbol && symbol.declarations && symbol.declarations.length > 0) {
      for (const decl of symbol.declarations) {
        const declFile = decl.getSourceFile().fileName.replace(/\\/g, '/');

        // Якщо тип оголошено у файлах домену/моделей проєкту, а не в node_modules чи lib.d.ts
        if (
          !declFile.includes('node_modules') &&
          !declFile.includes('lib.d.ts') &&
          (declFile.includes('/domain/') ||
            declFile.includes('/models/') ||
            declFile.includes('/entities/') ||
            !declFile.includes('/utils/'))
        ) {
          return {
            location,
            identifierName,
            typeName: typeNameString,
            declaredInFile: declFile,
            reason: `Тип "${typeNameString}" оголошено в доменному каталозі (${declFile}). Утиліта не повинна залежати від бізнес-сутностей.`,
          };
        }
      }
    }

    // 3. Евристична перевірка за ключовими словами бізнес-домену
    const lowerName = cleanTypeName.toLowerCase();
    for (const kw of this.domainKeywords) {
      if (lowerName.includes(kw)) {
        return {
          location,
          identifierName,
          typeName: typeNameString,
          reason: `Назва типу "${typeNameString}" містить доменний термін "${kw}". Це свідчить про витік бізнес-логіки у спільний utils.`,
        };
      }
    }

    return null;
  }

  /**
   * Перевіряє наявність модифікатора export у вузлі AST.
   */
  private hasExportModifier(node: ts.Node): boolean {
    const flags = ts.getCombinedModifierFlags(node as ts.Declaration);
    return Boolean(flags & ts.ModifierFlags.Export);
  }

  /**
   * Нормалізує шлях до файла у відносний формат.
   */
  private getRelativePath(absolutePath: string): string {
    const normalized = absolutePath.replace(/\\/g, '/');
    const parts = normalized.split('/');
    const srcIndex = parts.lastIndexOf('src');
    if (srcIndex !== -1) {
      return parts.slice(srcIndex).join('/');
    }
    return parts.slice(-2).join('/');
  }
}
