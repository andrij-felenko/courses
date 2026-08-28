export class BatchEventBuffer {
  private buffer: UsageEvent[] = [];
  private maxBatchSize: number;
  private maxDelayMs: number;
  private lastFlushTime: number;

  constructor(maxBatchSize: number = 500, maxDelayMs: number = 100) {
    this.maxBatchSize = maxBatchSize;
    this.maxDelayMs = maxDelayMs;
    this.lastFlushTime = Date.now();
  }

  public push(event: UsageEvent): boolean {
    this.buffer.push(event);
    const now = Date.now();
    if (this.buffer.length >= this.maxBatchSize || now - this.lastFlushTime >= this.maxDelayMs) {
      return true;
    }
    return false;
  }

  public extractBatch(): UsageEvent[] {
    const batch = this.buffer;
    this.buffer = [];
    this.lastFlushTime = Date.now();
    return batch;
  }

  public get pendingCount(): number {
    return this.buffer.length;
  }
}
