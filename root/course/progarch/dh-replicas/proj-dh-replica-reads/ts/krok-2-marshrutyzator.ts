class ReadRouter {
  c: Cluster; lagWindow: number; classify: boolean; sticky: boolean; pin: boolean; rng: Rng;
  lastWrite = new Map<number, number>();
  constructor(c: Cluster, lagWindow = 1.5, classify = true, sticky = true, pin = true, rng = new Rng(7)) {
    this.c = c; this.lagWindow = lagWindow; this.classify = classify;
    this.sticky = sticky; this.pin = pin; this.rng = rng;
  }
  noteWrite(home: number): void {             // застосунок щойно писав у цей дім
    this.lastWrite.set(home, this.c.clock.t);
  }
  route(home: number, kind: Kind): Leader | Follower {
    if (!this.classify) return this.follower(home);          // наївний режим
    if (kind === "lock") return this.c.leader;               // безпека: замок з лідера
    if (kind === "device_state" && this.sticky) {
      if (this.c.clock.t - (this.lastWrite.get(home) ?? -1e9) < this.lagWindow)
        return this.c.leader;                                // read-your-writes
    }
    return this.follower(home);                              // реєстр, телеметрія, давній стан
  }
  private follower(home: number): Follower {
    const n = this.c.followers.length;
    // прив'язка: сесія (тут — дім) завжди на ТУ САМУ копію → монотонні читання
    return this.pin ? this.c.followers[home % n] : this.c.followers[this.rng.index(n)];
  }
}
