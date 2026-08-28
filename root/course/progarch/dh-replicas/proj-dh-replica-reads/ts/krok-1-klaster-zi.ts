class Rng {                                   // детермінований ГВЧ (LCG)
  s: number;
  constructor(seed: number) { this.s = seed >>> 0; }
  next(): number { this.s = (Math.imul(1664525, this.s) + 1013904223) >>> 0; return this.s / 4294967296; }
  below(p: number): boolean { return this.next() < p; }
  index(n: number): number { return Math.floor(this.next() * n); }
  pick<T>(xs: T[]): T { return xs[Math.floor(this.next() * xs.length)]; }
}

type Kind = "lock" | "device_state" | "registry" | "telemetry";
type Cell = [string, number];                 // [значення, seq]
type Row = [number, number, number, number, string];  // seq, t, home, device, value

class Clock { t = 0; advance(dt: number) { this.t += dt; } }

class Leader {
  state = new Map<string, Cell>();
  log: Row[] = [];
  applyWrite(home: number, device: number, value: string, t: number): number {
    const seq = this.log.length;              // монотонний номер запису
    this.state.set(`${home}:${device}`, [value, seq]);
    this.log.push([seq, t, home, device, value]);
    return seq;
  }
  get(home: number, device: number): Cell | undefined { return this.state.get(`${home}:${device}`); }
}

class Follower {
  state = new Map<string, Cell>();
  cursor = 0;
  leader: Leader; lag: number;
  constructor(leader: Leader, lag: number) { this.leader = leader; this.lag = lag; }
  replicate(now: number): void {              // доганяємо лідера до межі now − lag
    const log = this.leader.log;
    while (this.cursor < log.length && log[this.cursor][1] <= now - this.lag) {
      const [seq, , home, device, value] = log[this.cursor];
      this.state.set(`${home}:${device}`, [value, seq]);
      this.cursor++;
    }
  }
  get(home: number, device: number): Cell | undefined { return this.state.get(`${home}:${device}`); }
}

class Cluster {
  clock = new Clock();
  leader = new Leader();
  followers: Follower[];
  constructor(lags: number[]) { this.followers = lags.map(l => new Follower(this.leader, l)); }
  tick(dt: number): void { this.clock.advance(dt); for (const f of this.followers) f.replicate(this.clock.t); }
  write(home: number, device: number, value: string): number {
    return this.leader.applyWrite(home, device, value, this.clock.t);
  }
}
