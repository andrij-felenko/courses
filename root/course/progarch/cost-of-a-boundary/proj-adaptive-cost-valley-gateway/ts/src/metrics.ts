import type { BatchExecutionMetrics, AggregatedStats } from './types.ts';

/**
 * Колектор та агрегатор метрик роботи шлюзу подолання межі.
 * Веде облік реальних переходів через межу, оцінює еквівалентні
 * накладні витрати без використання батчингу та розраховує коефіцієнт
 * усунення проблеми N+1.
 */
export class MetricsCollector {
  private readonly batches: BatchExecutionMetrics[] = [];
  private readonly baseBoundaryLatencyMs: number;

  constructor(baseBoundaryLatencyMs: number = 15) {
    this.baseBoundaryLatencyMs = baseBoundaryLatencyMs;
  }

  public recordBatch(metric: BatchExecutionMetrics): void {
    this.batches.push(metric);
  }

  public getHistory(): readonly BatchExecutionMetrics[] {
    return this.batches;
  }

  /**
   * Розраховує підсумкові агреговані показники ефективності конвеєра.
   */
  public getAggregatedStats(): AggregatedStats {
    const totalBatches = this.batches.length;
    if (totalBatches === 0) {
      return {
        totalRequests: 0,
        totalBatches: 0,
        callsSaved: 0,
        reductionRatioPct: 0,
        avgBatchSize: 0,
        totalUnbatchedEstimatedLatencyMs: 0,
        totalBatchedActualLatencyMs: 0,
        savedLatencyMs: 0,
        totalPayloadBytes: 0
      };
    }

    let totalRequests = 0;
    let totalBatchedActualLatencyMs = 0;
    let totalPayloadBytes = 0;

    for (const b of this.batches) {
      totalRequests += b.batchSize;
      totalBatchedActualLatencyMs += b.boundaryLatencyMs + b.windowDelayMs;
      totalPayloadBytes += b.payloadBytes;
    }

    const callsSaved = totalRequests - totalBatches;
    const reductionRatioPct = totalRequests > 0 ? (callsSaved / totalRequests) * 100 : 0;
    const avgBatchSize = totalRequests / totalBatches;

    // Теоретичний час, якби кожен запит перетинав межу окремо (N+1 проблема)
    // Кожен виклик платив би мінімум повну базову затримку межі
    const totalUnbatchedEstimatedLatencyMs = totalRequests * this.baseBoundaryLatencyMs;
    const savedLatencyMs = Math.max(0, totalUnbatchedEstimatedLatencyMs - totalBatchedActualLatencyMs);

    return {
      totalRequests,
      totalBatches,
      callsSaved,
      reductionRatioPct: Math.round(reductionRatioPct * 10) / 10,
      avgBatchSize: Math.round(avgBatchSize * 10) / 10,
      totalUnbatchedEstimatedLatencyMs,
      totalBatchedActualLatencyMs,
      savedLatencyMs,
      totalPayloadBytes
    };
  }

  public reset(): void {
    this.batches.length = 0;
  }
}
