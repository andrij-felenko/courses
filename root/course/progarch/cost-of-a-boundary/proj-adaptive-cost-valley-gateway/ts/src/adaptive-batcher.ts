import type { AdaptiveTimerConfig } from './types.ts';

/**
 * Динамічний адаптивний таймер накопичення пакетів.
 * Автоматично регулює часове вікно затримки між minWindowMs та maxWindowMs,
 * аналізуючи темп надходження вхідних запитів через експоненційно зважене
 * ковзне середнє (EWMA). Це дозволяє тримати затримку на дні «долини витрат»:
 * для одиночних запитів затримка мінімальна, а під час сплесків батч накопичується
 * до оптимального розміру без деградації латентності.
 */
export class AdaptiveBatchTimer {
  private readonly config: AdaptiveTimerConfig;
  private currentWindowMs: number;
  private lastArrivalTimeMs: number = 0;
  private ewmaIntervalMs: number = 20; // початкова оцінка інтервалу між викликами

  constructor(config: AdaptiveTimerConfig) {
    this.config = config;
    this.currentWindowMs = config.minWindowMs;
  }

  /**
   * Фіксує надходження чергового клієнтського запиту та оновлює оцінку інтенсивності потоку.
   */
  public recordArrival(): void {
    const now = Date.now();
    if (this.lastArrivalTimeMs > 0) {
      const delta = Math.max(1, now - this.lastArrivalTimeMs);
      // Оновлення EWMA інтервалу надходження: S_t = α * Y_t + (1 - α) * S_{t-1}
      this.ewmaIntervalMs =
        this.config.smoothingFactor * delta +
        (1 - this.config.smoothingFactor) * this.ewmaIntervalMs;

      this.recalculateWindow();
    }
    this.lastArrivalTimeMs = now;
  }

  /**
   * Повертає поточне розраховане вікно очікування в мілісекундах.
   */
  public getCurrentWindowMs(): number {
    return Math.round(this.currentWindowMs);
  }

  /**
   * Додаткове коригування таймера за фактичним розміром щойно відправленого батчу.
   * Якщо батч виявився значно меншим за цільовий при високій частоті надходження,
   * вікно злегка збільшується; якщо батч переповнюється — вікно скорочується.
   */
  public adjustAfterBatch(batchSize: number): void {
    if (batchSize >= this.config.targetBatchSize) {
      // Пакет достатньо великий — зменшуємо затримку для покращення відгуку
      this.currentWindowMs = Math.max(
        this.config.minWindowMs,
        this.currentWindowMs * 0.85
      );
    } else if (this.ewmaIntervalMs < 10 && batchSize < this.config.targetBatchSize / 2) {
      // Потік частий, але батч малий — даємо невеликий запас для групування
      this.currentWindowMs = Math.min(
        this.config.maxWindowMs,
        this.currentWindowMs * 1.15
      );
    }
  }

  /**
   * Перераховує вікно накопичення на основі поточної оцінки інтервалу EWMA.
   */
  private recalculateWindow(): void {
    // Якщо інтервал надходження дуже малий (високий темп), можемо зібрати цільовий батч за коротший час
    const estimatedTimeToFill = this.ewmaIntervalMs * this.config.targetBatchSize;

    // Обмежуємо значення вікна конфігураційними межами
    const bounded = Math.max(
      this.config.minWindowMs,
      Math.min(this.config.maxWindowMs, estimatedTimeToFill * 0.5)
    );

    this.currentWindowMs = bounded;
  }

  public reset(): void {
    this.currentWindowMs = this.config.minWindowMs;
    this.lastArrivalTimeMs = 0;
    this.ewmaIntervalMs = 20;
  }
}
