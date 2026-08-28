// hub.ts — обробіток команд ідемпотентний за command-id
type Command = { id: string; target: string; action: "open" | "close" };

class Lock {
  actuations = 0;                       // скільки разів фізично смикнули замок
  constructor(readonly target: string) {}
  actuate() { this.actuations++; }
}

export class Hub {
  private locks = new Map<string, Lock>();
  private seen = new Set<string>();     // command-id, уже застосовані
  lock(target: string): Lock {
    let l = this.locks.get(target);
    if (!l) this.locks.set(target, (l = new Lock(target)));
    return l;
  }
  handle(cmd: Command): void {
    if (this.seen.has(cmd.id)) return;  // дубль: той самий id — стан не рухаємо
    this.seen.add(cmd.id);
    if (cmd.action === "open") this.lock(cmd.target).actuate();
  }
}
