export class SnowflakeGenerator {
  private readonly epoch = 1288834974657n;
  private readonly workerBits = 5n;
  private readonly datacenterBits = 5n;
  private readonly sequenceBits = 12n;

  private readonly maxWorkerId = (1n << this.workerBits) - 1n;
  private readonly maxDatacenterId = (1n << this.datacenterBits) - 1n;
  private readonly sequenceMask = (1n << this.sequenceBits) - 1n;

  private readonly workerShift = this.sequenceBits;
  private readonly datacenterShift = this.sequenceBits + this.workerBits;
  private readonly timestampShift = this.sequenceBits + this.workerBits + this.datacenterBits;

  private sequence = 0n;
  private lastTimestamp = 0n;

  constructor(
    private readonly workerId: bigint,
    private readonly datacenterId: bigint
  ) {
    if (workerId > this.maxWorkerId || datacenterId > this.maxDatacenterId) {
      throw new RangeError('Worker or Datacenter ID out of allowed bounds');
    }
  }

  public nextId(): bigint {
    let now = BigInt(Date.now());

    if (now < this.lastTimestamp) {
      const drift = this.lastTimestamp - now;
      if (drift < 5n) {
        while (now <= this.lastTimestamp) {
          now = BigInt(Date.now());
        }
      } else {
        throw new Error(`Clock regression detected: ${drift}ms`);
      }
    }

    if (now === this.lastTimestamp) {
      this.sequence = (this.sequence + 1n) & this.sequenceMask;
      if (this.sequence === 0n) {
        while (now <= this.lastTimestamp) {
          now = BigInt(Date.now());
        }
      }
    } else {
      this.sequence = 0n;
    }

    this.lastTimestamp = now;

    return (
      ((now - this.epoch) << this.timestampShift) |
      (this.datacenterId << this.datacenterShift) |
      (this.workerId << this.workerShift) |
      this.sequence
    );
  }
}
