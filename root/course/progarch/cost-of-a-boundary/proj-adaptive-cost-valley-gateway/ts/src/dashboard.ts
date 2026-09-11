import { MetricsCollector } from './metrics.ts';

/**
 * Термінальний дашборд візуалізації метрик у реальному часі.
 * Будує зведені таблиці та шкали ефективності, наочно демонструючи
 * скорочення перетинів межі, адаптивну динаміку вікна та виграш
 * у продуктивності каналу.
 */
export class TerminalDashboard {
  private readonly metrics: MetricsCollector;

  constructor(metrics: MetricsCollector) {
    this.metrics = metrics;
  }

  /**
   * Відображає таблицю оброблених батчів та підсумкову картку показників.
   */
  public renderSummary(title: string): void {
    const stats = this.metrics.getAggregatedStats();
    const history = this.metrics.getHistory();

    console.log('\n' + '═'.repeat(78));
    console.log(`  📊 ДАШБОРД ЕФЕКТИВНОСТІ МЕЖІ: ${title}`);
    console.log('═'.repeat(78));

    // Таблиця потоку батчів
    console.log('\n  Хронологія пакетів через межу:');
    console.log('  ┌─────┬──────────┬──────────┬─────────────┬──────────────┬─────────────┐');
    console.log('  │ БАТЧ│ ЗАПИТІВ  │ УНІК. ID │ ВІКНО (мс)  │ ЗАТРИМКА(мс) │ РОЗМІР (B)  │');
    console.log('  ├─────┼──────────┼──────────┼─────────────┼──────────────┼─────────────┤');

    for (const b of history) {
      const idStr = String(b.batchId).padStart(3, ' ');
      const sizeStr = String(b.batchSize).padStart(8, ' ');
      const uniqStr = String(b.uniqueIdsCount).padStart(8, ' ');
      const winStr = String(b.windowDelayMs).padStart(11, ' ');
      const latStr = String(b.boundaryLatencyMs).padStart(12, ' ');
      const byteStr = String(b.payloadBytes).padStart(11, ' ');

      console.log(`  │ ${idStr} │ ${sizeStr} │ ${uniqStr} │ ${winStr} │ ${latStr} │ ${byteStr} │`);
    }

    console.log('  └─────┴──────────┴──────────┴─────────────┴──────────────┴─────────────┘');

    // Графічна шкала скорочення переходів
    const barWidth = 30;
    const filled = Math.min(barWidth, Math.round((stats.reductionRatioPct / 100) * barWidth));
    const empty = barWidth - filled;
    const progressBar = '█'.repeat(filled) + '░'.repeat(empty);

    console.log('\n  Підсумкова картка оптимізації архітектурної межі:');
    console.log(`  • Загальна кількість вхідних запитів:     ${stats.totalRequests}`);
    console.log(`  • Фактичних перетинів системної межі:      ${stats.totalBatches}`);
    console.log(`  • Заощаджено мережевих/міжпроцесних дій:   ${stats.callsSaved}`);
    console.log(`  • Скорочення викликів (N+1 ліквідовано):   [${progressBar}] ${stats.reductionRatioPct}%`);
    console.log(`  • Середній коефіцієнт групування:          ${stats.avgBatchSize} запитів/батч`);
    console.log(`  • Сумарний переданий обсяг даних:          ${(stats.totalPayloadBytes / 1024).toFixed(2)} КБ`);
    console.log(`  • Оціночний час без батчингу (N+1):       ~${stats.totalUnbatchedEstimatedLatencyMs} мс`);
    console.log(`  • Фактичний сумарний час конвеєра:         ${stats.totalBatchedActualLatencyMs} мс`);
    console.log(`  • Чистий виграш у пропускній здатності:    ~${stats.savedLatencyMs} мс накладних витрат`);
    console.log('═'.repeat(78) + '\n');
  }
}
