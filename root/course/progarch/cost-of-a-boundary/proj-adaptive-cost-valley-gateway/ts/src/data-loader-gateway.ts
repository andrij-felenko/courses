import type {
  EntityId,
  ItemRecord,
  FieldMask,
  BatchRequestItem,
  BatchExecutionMetrics
} from './types.ts';
import { BoundarySimulator } from './boundary-simulator.ts';
import { AdaptiveBatchTimer } from './adaptive-batcher.ts';
import { MetricsCollector } from './metrics.ts';

/**
 * Механізм об'єднання та фільтрації полів (Sparse Fieldsets).
 * Запобігає надвибірці (overfetching) даних через системну межу:
 * об'єднує розрізнені вимоги різних клієнтів в єдиний запит,
 * а після отримання відповіді проєктує лише запитані поля індивідуальним клієнтам.
 */
export class FieldMaskProjector {
  /**
   * Об'єднує множини полів від кількох споживачів у спільну сукупну маску.
   */
  public static unionMasks(masks: (FieldMask | undefined)[]): FieldMask | undefined {
    const union = new Set<string>();
    let hasAnyDefined = false;

    for (const mask of masks) {
      if (mask && mask.size > 0) {
        hasAnyDefined = true;
        for (const field of mask) {
          union.add(field);
        }
      }
    }

    // Якщо хоч один клієнт не вказав маску (попросив повний об'єкт), ми змушені просити все
    return hasAnyDefined ? union : undefined;
  }

  /**
   * Проєктує запис на персональну маску полів клієнта.
   */
  public static project(item: ItemRecord, requestedFields?: FieldMask): ItemRecord {
    if (!requestedFields || requestedFields.size === 0) {
      return { ...item };
    }

    const projected: ItemRecord = { id: item.id };
    for (const field of requestedFields) {
      if (field in item) {
        projected[field] = item[field];
      }
    }
    return projected;
  }
}

/**
 * Асинхронний клієнтський шлюз на базі розширеного патерну DataLoader.
 * Прозоро збирає поодинокі виклики бізнес-коду через Promise-колектор,
 * застосовує динамічний адаптивний таймер для формування пакету та
 * захищає від N+1 проблеми без переписування коду споживачів.
 */
export class DataLoaderGateway<T = ItemRecord> {
  private readonly boundary: BoundarySimulator;
  private readonly timer: AdaptiveBatchTimer;
  private readonly metrics: MetricsCollector;
  private readonly maxBatchSize: number;

  private pendingQueue: BatchRequestItem<T>[] = [];
  private scheduledTimer: NodeJS.Timeout | null = null;
  private batchCounter: number = 0;

  constructor(
    boundary: BoundarySimulator,
    timer: AdaptiveBatchTimer,
    metrics: MetricsCollector,
    maxBatchSize: number = 50
  ) {
    this.boundary = boundary;
    this.timer = timer;
    this.metrics = metrics;
    this.maxBatchSize = maxBatchSize;
  }

  /**
   * Головний метод доступу до сутності: виглядає для клієнта як звичайний поодинокий
   * асинхронний виклик, але під капотом потрапляє в Promise-колектор.
   */
  public load(id: EntityId, fields?: string[]): Promise<T> {
    this.timer.recordArrival();

    const fieldMask = fields && fields.length > 0 ? new Set<string>(fields) : undefined;

    return new Promise<T>((resolve, reject) => {
      this.pendingQueue.push({
        id,
        fields: fieldMask,
        enqueueTimeMs: Date.now(),
        resolve,
        reject
      });

      // Якщо черга досягла ліміту максимального розміру — негайний виклик (fast-flush)
      if (this.pendingQueue.length >= this.maxBatchSize) {
        this.flushImmediate();
      } else if (!this.scheduledTimer) {
        // Плануємо закриття вікна на основі адаптивного таймера
        const delayMs = this.timer.getCurrentWindowMs();
        this.scheduledTimer = setTimeout(() => {
          this.flushImmediate();
        }, delayMs);
      }
    });
  }

  /**
   * Негайне закриття вікна та відправка накопиченого пакета через межу.
   */
  public flushImmediate(): void {
    if (this.scheduledTimer) {
      clearTimeout(this.scheduledTimer);
      this.scheduledTimer = null;
    }

    if (this.pendingQueue.length === 0) {
      return;
    }

    // Забираємо поточні елементи черги на обробку
    const currentBatch = this.pendingQueue;
    this.pendingQueue = [];

    // Асинхронне виконання без блокування прийому нових запитів
    void this.processBatch(currentBatch);
  }

  private async processBatch(batch: BatchRequestItem<T>[]): Promise<void> {
    const batchId = ++this.batchCounter;
    const startTime = Date.now();

    // Збираємо унікальні ID та множину об'єднаних полів
    const uniqueIds = Array.from(new Set(batch.map((b) => b.id)));
    const allMasks = batch.map((b) => b.fields);
    const unifiedMask = FieldMaskProjector.unionMasks(allMasks);

    const totalRequestedFieldsCount = batch.reduce(
      (acc, item) => acc + (item.fields ? item.fields.size : 0),
      0
    );

    try {
      // Перетин дорогої системної межі
      const { data, payloadBytes, latencyMs } = await this.boundary.fetchBatch(
        uniqueIds,
        unifiedMask
      );

      // Роздаємо проєкції кожному очікуючому промісу
      for (const req of batch) {
        const fullItem = data.get(req.id);
        if (!fullItem) {
          req.reject(new Error(`Сутність з ID "${req.id}" не знайдена за межею.`));
        } else {
          const projected = FieldMaskProjector.project(fullItem, req.fields) as T;
          req.resolve(projected);
        }
      }

      // Оновлюємо статистику адаптивного таймера
      this.timer.adjustAfterBatch(batch.length);

      // Фіксуємо метрики виконання батчу
      const executionMetrics: BatchExecutionMetrics = {
        batchId,
        batchSize: batch.length,
        uniqueIdsCount: uniqueIds.length,
        requestedFieldCount: totalRequestedFieldsCount,
        unifiedFieldCount: unifiedMask ? unifiedMask.size : 0,
        windowDelayMs: Math.max(0, startTime - batch[0].enqueueTimeMs),
        boundaryLatencyMs: latencyMs,
        payloadBytes,
        timestamp: Date.now()
      };

      this.metrics.recordBatch(executionMetrics);
    } catch (err) {
      // У разі системної помилки коректно відхиляємо всі проміси пачки
      for (const req of batch) {
        req.reject(err);
      }
    }
  }
}
