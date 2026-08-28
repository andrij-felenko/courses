type LockState = { bolt: "locked" | "unlocked"; version: number; lastCmd: string };
type Cmd = { kind: "lock" | "unlock"; seq: number; by: string };

const SNAP_EVERY = 100;   // знімок на диск — раз на сотню команд

class HomeActor {
  private box: Cmd[] = [];          // ← пошта: єдина черга дому
  private sinceSnapshot = 0;

  constructor(private homeId: string,
              private lock: LockState = { bolt: "unlocked", version: 5, lastCmd: "" }) {}

  // ЄДИНИЙ вхід ззовні: покласти команду в пошту й піти. Стан ніхто не чіпає напряму.
  tell(cmd: Cmd): void { this.box.push(cmd); }

  // ЄДИНИЙ виконавець дому: бере по одному, доводить до кінця, і лише тоді наступне.
  // (у справжньому рантаймі цей цикл крутиться безперервно, сам собою.)
  drain(): void {
    for (let cmd = this.box.shift(); cmd; cmd = this.box.shift()) this.apply(cmd);
  }

  private apply(cmd: Cmd): void {
    // жодного read-modify-write: стан ось тут, у полі, і виконавець його один
    this.lock = {
      bolt: cmd.kind === "lock" ? "locked" : "unlocked",
      version: this.lock.version + 1,
      lastCmd: `${cmd.by}#${cmd.seq}`,
    };
    if (++this.sinceSnapshot >= SNAP_EVERY) {
      saveSnapshot(this.homeId, this.lock);   // періодичний знімок на диск
      this.sinceSnapshot = 0;
    }
  }

  snapshot(): LockState { return this.lock; }
}

// сценарій: дві «замкни» майже водночас — обидві лягають у ту саму пошту
const a = new HomeActor("home42");
a.tell({ kind: "lock", seq: 6, by: "A" });
a.tell({ kind: "lock", seq: 7, by: "B" });   // у скриньці тепер ДВІ
a.drain();                                    // виконавець бере по одній: version 5 → 6 → 7
