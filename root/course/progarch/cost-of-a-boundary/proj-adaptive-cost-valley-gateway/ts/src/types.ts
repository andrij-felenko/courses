export type EntityId = string | number;

export type FieldMask = Set<string>;

export type ItemRecord = Record<string, unknown>;

export interface BatchRequestItem<T = ItemRecord> {
  id: EntityId;
  fields?: FieldMask;
  enqueueTimeMs: number;
  resolve: (value: T) => void;
  reject: (reason: unknown) => void;
}

export interface BoundaryConfig {
  /** Базова затримка перетину межі в мілісекундах (фіксовані накладні витрати) */
  baseLatencyMs: number;
  /** Штраф за обсяг переданих даних у мілісекундах на байт */
  perByteLatencyMs: number;
  /** Шанс штучної відмови для тестування стійкості (0.0 .. 1.0) */
  failureRate?: number;
}

export interface AdaptiveTimerConfig {
  /** Мінімальний розмір вікна накопичення (мс) для низького навантаження */
  minWindowMs: number;
  /** Максимальний розмір вікна накопичення (мс) для пікового навантаження */
  maxWindowMs: number;
  /** Оптимальний цільовий розмір батчу (точка «долини витрат») */
  targetBatchSize: number;
  /** Коефіцієнт згладжування швидкості надходження (0.0 .. 1.0) */
  smoothingFactor: number;
  /** Максимальна кількість елементів для негайного скидання */
  maxBatchSize: number;
}

export interface BatchExecutionMetrics {
  batchId: number;
  batchSize: number;
  uniqueIdsCount: number;
  requestedFieldCount: number;
  unifiedFieldCount: number;
  windowDelayMs: number;
  boundaryLatencyMs: number;
  payloadBytes: number;
  timestamp: number;
}

export interface AggregatedStats {
  totalRequests: number;
  totalBatches: number;
  callsSaved: number;
  reductionRatioPct: number;
  avgBatchSize: number;
  totalUnbatchedEstimatedLatencyMs: number;
  totalBatchedActualLatencyMs: number;
  savedLatencyMs: number;
  totalPayloadBytes: number;
}
