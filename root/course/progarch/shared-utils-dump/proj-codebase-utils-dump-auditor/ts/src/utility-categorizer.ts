import {
  ArchitecturalPrinciple,
  AuditSummary,
  CallGraphNode,
  CategorizedUtility,
  FunctionSignatureInfo,
  UtilityCategory,
} from './types';

/**
 * Архітектурний класифікатор утиліт за принципами чистої архітектури.
 * Зіставляє топологію міжмодульних зв'язків та семантичний профіль типів,
 * реалізуючи правила розподілу за принципами CRP (Common Reuse Principle)
 * та REP (Reuse/Release Equivalence Principle).
 */
export class UtilityCategorizer {
  constructor(private readonly minModuleFanInForLibrary: number = 2) {}

  /**
   * Класифікує масив проаналізованих утиліт на основі побудованого графа викликів.
   */
  public categorize(
    functions: FunctionSignatureInfo[],
    callGraph: Map<string, CallGraphNode>
  ): CategorizedUtility[] {
    const results: CategorizedUtility[] = [];

    for (const fn of functions) {
      const node = callGraph.get(fn.name) ?? {
        functionName: fn.name,
        declaringFilePath: fn.filePath,
        callSites: [],
        callCount: 0,
        consumerModules: [],
        consumerFiles: [],
      };

      const categorized = this.evaluateUtility(fn, node);
      results.push(categorized);
    }

    return results;
  }

  /**
   * Обчислює підсумкову статистику аудиту.
   */
  public summarize(categorized: CategorizedUtility[]): AuditSummary {
    let deadCodeCount = 0;
    let inlineCandidateCount = 0;
    let repatriationCount = 0;
    let libraryCandidateCount = 0;

    for (const item of categorized) {
      switch (item.category) {
        case UtilityCategory.DEAD_CODE:
          deadCodeCount++;
          break;
        case UtilityCategory.INLINE_CANDIDATE:
          inlineCandidateCount++;
          break;
        case UtilityCategory.DOMAIN_REPATRIATION:
          repatriationCount++;
          break;
        case UtilityCategory.CRP_REP_LIBRARY:
          libraryCandidateCount++;
          break;
      }
    }

    const hasViolations =
      deadCodeCount > 0 || inlineCandidateCount > 0 || repatriationCount > 0;

    return {
      totalAnalyzed: categorized.length,
      deadCodeCount,
      inlineCandidateCount,
      repatriationCount,
      libraryCandidateCount,
      hasViolations,
    };
  }

  /**
   * Застосовує архітектурне дерево рішень до однієї функції.
   */
  private evaluateUtility(
    fn: FunctionSignatureInfo,
    node: CallGraphNode
  ): CategorizedUtility {
    const leakedTypeNames = fn.leakedDomainTypes.map((t) => t.typeName);

    // ПРАВИЛО 1: Мертвий код (Dead Code)
    // Функція взагалі не має споживачів у кодовій базі
    if (node.callCount === 0) {
      return {
        functionName: fn.name,
        declaringFilePath: fn.relativeFilePath,
        line: fn.line,
        category: UtilityCategory.DEAD_CODE,
        callCount: 0,
        consumerModules: [],
        leakedDomainTypes: leakedTypeNames,
        violatedPrinciple: ArchitecturalPrinciple.CLEAN_CODE,
        rationale:
          `Функція "${fn.name}" експортується у спільному каталозі utils, але жодного разу ` +
          `не викликається у проєкті (0 викликів). Мертвий код роздуває публічний API, ` +
          `створює хибне враження про затребуваність рішення та збільшує розмір збірки.`,
        recommendation:
          `Видалити функцію з кодової бази або зняти модифікатор export.`,
      };
    }

    // ПРАВИЛО 2: Репатріація в домен (Domain Repatriation)
    // Сигнатура оперує доменними типами або бізнес-сутністями
    if (fn.leakedDomainTypes.length > 0) {
      const typesList = leakedTypeNames.join(', ');
      return {
        functionName: fn.name,
        declaringFilePath: fn.relativeFilePath,
        line: fn.line,
        category: UtilityCategory.DOMAIN_REPATRIATION,
        callCount: node.callCount,
        consumerModules: node.consumerModules,
        leakedDomainTypes: leakedTypeNames,
        violatedPrinciple: ArchitecturalPrinciple.REP,
        rationale:
          `Функція "${fn.name}" містить витік бізнес-домену: у сигнатурі виявлено типи ` +
          `предметної області (${typesList}). Розміщення бізнес-правил у каталозі спільних ` +
          `утиліт порушує принцип Reuse/Release Equivalence (REP) та межі Bounded Contexts: ` +
          `будь-яка зміна бізнес-моделі змушує оновлювати спільні утиліти, від яких залежить увесь застосунок.`,
        recommendation:
          `Репатріювати функцію у відповідний доменний модуль (наприклад, у контекст замовлень ` +
          `чи сутність домену) і видалити зі спільних утиліт.`,
      };
    }

    // ПРАВИЛО 3: Кандидат на інлайнінг (Inline Candidate / CRP Violation)
    // Функція викликається лише в одному модулі або рівно 1 раз
    if (
      node.callCount === 1 ||
      (node.consumerModules.length === 1 &&
        node.consumerModules.length < this.minModuleFanInForLibrary)
    ) {
      const soleModule = node.consumerModules[0] ?? 'єдиний споживач';
      return {
        functionName: fn.name,
        declaringFilePath: fn.relativeFilePath,
        line: fn.line,
        category: UtilityCategory.INLINE_CANDIDATE,
        callCount: node.callCount,
        consumerModules: node.consumerModules,
        leakedDomainTypes: [],
        violatedPrinciple: ArchitecturalPrinciple.CRP,
        rationale:
          `Функція "${fn.name}" використовується виключно в одному місці (модуль "${soleModule}"). ` +
          `Розміщення одноразового хелпера у спільному каталозі прямо порушує Common Reuse Principle (CRP): ` +
          `"компоненти, що не використовуються разом, не повинні пакуватися разом". Інші підсистеми ` +
          `змушені неявно залежати від змін коду, який їм не потрібен.`,
        recommendation:
          `Виконати інлайнінг функції: перенести її безпосередньо в модуль "${soleModule}" ` +
          `як приватний локальний хелпер.`,
      };
    }

    // ПРАВИЛО 4: Справжня спільна бібліотека (CRP / REP Compliant)
    // Доменно-нейтральна, високий міжмодульний розкид споживання (fan-in >= 2)
    return {
      functionName: fn.name,
      declaringFilePath: fn.relativeFilePath,
      line: fn.line,
      category: UtilityCategory.CRP_REP_LIBRARY,
      callCount: node.callCount,
      consumerModules: node.consumerModules,
      leakedDomainTypes: [],
      violatedPrinciple: ArchitecturalPrinciple.NONE,
      rationale:
        `Функція "${fn.name}" є доменно-нейтральною (оперує примітивами чи узагальненими типами) ` +
        `та має високий міжмодульний розкид споживання (${node.consumerModules.length} модулі: ` +
        `${node.consumerModules.join(', ')}). Вона повністю задовольняє принципам CRP та REP.`,
      recommendation:
        `Легітимна спільна утиліта. Зберегти у спільному каталозі або виділити ` +
        `в окрему автономну бібліотеку з чітким семантичним версіонуванням.`,
    };
  }
}
