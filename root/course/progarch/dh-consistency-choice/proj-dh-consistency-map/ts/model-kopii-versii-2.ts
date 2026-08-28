type Pending = { at: number; to: Replica; key: string; rec: Rec };

// Кластер копій із ОДНИМ лідером і реплікаційним лагом до кожної репліки.
class Cluster {
  private clock = 0;                      // логічний час у «тиках»
  private queue: Pending[] = [];          // реплікації в дорозі, кожна з тиком доставки
  private nextVersion: Version = 1;

  constructor(
    readonly replicas: Replica[],
    private readonly leader: Replica,
    private readonly lag: (to: Replica) => number,   // тиків, поки запис доїде до копії
  ) {}

  now(): number { return this.clock; }

  // Запис через лідера: карбує версію, кладе В СЕБЕ негайно, на репліки — з лагом.
  write(key: string, value: unknown): Version {
    const rec: Rec = { value, version: this.nextVersion++ };
    this.leader.apply(key, rec);
    for (const to of this.replicas) {
      if (to === this.leader) continue;
      this.queue.push({ at: this.clock + this.lag(to), to, key, rec });
    }
    return rec.version;
  }

  // Просунути час і доставити дозрілі реплікації — лише копіям на зв'язку.
  // Відрізаній копії кадр лишається в черзі (майбутня робота анти-ентропії).
  advance(ticks: number): void {
    this.clock += ticks;
    const kept: Pending[] = [];
    for (const p of this.queue) {
      if (p.at <= this.clock && p.to.linked) p.to.apply(p.key, p.rec);
      else kept.push(p);
    }
    this.queue = kept;
  }
}
