import { AuditReport, CategorizedUtility, UtilityCategory } from './types';

/**
 * Генератор звітів статичного аудитора звалища утиліт.
 * Створює структурований JSON для інтеграції з CI/CD та форматований
 * консольний дашборд із детальними архітектурними рекомендаціями.
 */
export class ReportGenerator {
  /**
   * Генерує машинно-зчитуваний JSON-звіт.
   */
  public generateJson(report: AuditReport): string {
    return JSON.stringify(report, null, 2);
  }

  /**
   * Форматує наочний людино-зчитуваний консольний звіт українською мовою.
   */
  public generateConsoleReport(report: AuditReport): string {
    const lines: string[] = [];
    const divider = '─'.repeat(76);
    const doubleDivider = '═'.repeat(76);

    lines.push('');
    lines.push(doubleDivider);
    lines.push('  СТАТИЧНИЙ АУДИТ ЗВАЛИЩА СПІЛЬНИХ УТИЛІТ (UTILS DUMP AUDITOR)');
    lines.push('  Контроль меж підсистем та принципів компонентного дизайну CRP / REP');
    lines.push(doubleDivider);
    lines.push(`Час аудиту: ${report.timestamp}`);
    lines.push(`Корінь проєкту: ${report.projectRoot}`);
    lines.push(divider);

    // Підсумкова зведенка
    const s = report.summary;
    lines.push('ПІДСУМКОВА ЗВЕДЕНКА:');
    lines.push(`  Всього проаналізовано експортованих утиліт:  ${s.totalAnalyzed}`);
    lines.push(`  🛑 Мертвий код (Dead Code):                   ${s.deadCodeCount}`);
    lines.push(`  ⚠️  Витік доменної логіки (Repatriation):      ${s.repatriationCount}`);
    lines.push(`  💡 Одноразові хелпери (CRP Inline):          ${s.inlineCandidateCount}`);
    lines.push(`  ✅ Справжні спільні бібліотеки (CRP/REP):     ${s.libraryCandidateCount}`);
    lines.push(divider);

    // Деталізація за категоріями
    this.appendCategorySection(
      lines,
      '🛑 1. МЕРТВИЙ КОД (НЕ МАЄ ВИКЛИКІВ У ПРОЄКТІ)',
      report.utilities.filter((u) => u.category === UtilityCategory.DEAD_CODE),
      'Невикористані функції засмічують простір імен і збільшують транзитивний розмір.'
    );

    this.appendCategorySection(
      lines,
      '⚠️  2. ВИТІК БІЗНЕС-ДОМЕНУ (КАНДИДАТИ НА РЕПАТРІАЦІЮ ДОМЕНУ)',
      report.utilities.filter(
        (u) => u.category === UtilityCategory.DOMAIN_REPATRIATION
      ),
      'Порушення REP: сигнатури оперують сутностями домену, руйнуючи межі контекстів.'
    );

    this.appendCategorySection(
      lines,
      '💡 3. ОДНОРАЗОВІ ХЕЛПЕРИ (КАНДИДАТИ НА ІНЛАЙНІНГ)',
      report.utilities.filter(
        (u) => u.category === UtilityCategory.INLINE_CANDIDATE
      ),
      'Порушення CRP: функція потрібна лише одному модулю, але нав\'язана всім.'
    );

    this.appendCategorySection(
      lines,
      '✅ 4. ЛЕГІТИМНІ СПІЛЬНІ УТИЛІТИ (ВІДПОВІДАЮТЬ CRP ТА REP)',
      report.utilities.filter(
        (u) => u.category === UtilityCategory.CRP_REP_LIBRARY
      ),
      'Доменно-нейтральний код із широким міжмодульним споживанням.'
    );

    // Фінальний вердикт для CI/CD
    lines.push(doubleDivider);
    if (s.hasViolations) {
      lines.push('❌ [ВЕРДИКТ CI/CD: ПОМИЛКА]');
      lines.push(
        'Виявлено архітектурні дефекти! Каталог спільних утиліт перетворено на звалище.'
      );
      lines.push(
        'Злиття гілки (Pull Request / Merge) ЗАБЛОКОВАНО для захисту модульної структури.'
      );
      lines.push(`Код завершення процесу: ${report.exitCode}`);
    } else {
      lines.push('✅ [ВЕРДИКТ CI/CD: УСПІХ]');
      lines.push(
        'Архітектурний аудит пройдено успішно! Усі спільні утиліти відповідають критеріям CRP та REP.'
      );
      lines.push(`Код завершення процесу: ${report.exitCode}`);
    }
    lines.push(doubleDivider);
    lines.push('');

    return lines.join('\n');
  }

  private appendCategorySection(
    lines: string[],
    title: string,
    items: CategorizedUtility[],
    hint: string
  ): void {
    lines.push('');
    lines.push(title);
    lines.push(`   Контекст: ${hint}`);
    lines.push('   ' + '─'.repeat(72));

    if (items.length === 0) {
      lines.push('   (немає елементів у цій категорії)');
      return;
    }

    for (const item of items) {
      lines.push(`   • Функція:        ${item.functionName}()`);
      lines.push(`     Локація:        ${item.declaringFilePath}:${item.line}`);
      lines.push(`     К-сть викликів: ${item.callCount}`);
      if (item.consumerModules.length > 0) {
        lines.push(`     Споживачі:      [${item.consumerModules.join(', ')}]`);
      }
      if (item.leakedDomainTypes.length > 0) {
        lines.push(`     Витік типів:    [${item.leakedDomainTypes.join(', ')}]`);
      }
      lines.push(`     Порушення:      ${item.violatedPrinciple}`);
      lines.push(`     Діагноз:        ${item.rationale}`);
      lines.push(`     Рекомендація:   ${item.recommendation}`);
      lines.push('');
    }
  }
}
