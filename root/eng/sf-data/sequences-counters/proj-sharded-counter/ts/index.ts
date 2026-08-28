export class ShardedCounter {
  private readonly buffer: BigUint64Array;
  private readonly mask: number;

  constructor(numShards: number = 16) {
    let power = 1;
    while (power < numShards) {
      power <<= 1;
    }
    // Використання SharedArrayBuffer для безпечного атомарного доступу між Web Workers
    const sab = new SharedArrayBuffer(power * 8);
    this.buffer = new BigUint64Array(sab);
    this.mask = power - 1;
  }

  public add(workerId: number, delta: bigint = 1n): void {
    const slot = workerId & this.mask;
    Atomics.add(this.buffer, slot, delta);
  }

  public get(): bigint {
    let total = 0n;
    for (let i = 0; i < this.buffer.length; i++) {
      total += Atomics.load(this.buffer, i);
    }
    return total;
  }
}
