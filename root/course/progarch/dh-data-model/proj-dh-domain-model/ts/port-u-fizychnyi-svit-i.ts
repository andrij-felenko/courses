// ── 3. Порт у фізичний світ + зведення бажаного до справжнього ──

// Що може відповісти фізичний замок на команду «замкнись».
type LockOutcome =
  | { kind: "acked"; state: LockState }   // відповів — і ось його справжній стан
  | { kind: "offline" };                  // не на зв'язку — правди не знаємо

// Порт: єдиний місток до заліза. Домен не знає, що там за протокол.
interface DeviceGateway {
  sendLock(id: DeviceId): LockOutcome;
}

// Чесний звіт про ОДИН прохід — об'єкт-значення (лише знімок, нічого не міняє).
class ReconcileReport {
  constructor(
    readonly desired: HomeMode,
    readonly locked: DeviceId[],
    readonly offline: DeviceId[],         // не підтвердили замкнення цього проходу
    readonly jammed: DeviceId[],          // потрібна людина
  ) {}
  get settled(): boolean { return this.offline.length === 0 && this.jammed.length === 0; }
  toString(): string {
    const off = this.offline.map(String).join(", ") || "—";
    const jam = this.jammed.length ? ` · заклинило: ${this.jammed.map(String).join(", ")}` : "";
    return `[${this.desired}] ${this.locked.length} замкнено · офлайн: ${off}${jam}`;
  }
}

// Зводить БАЖАНЕ (режим дому) до СПРАВЖНЬОГО (стан кожного замка).
// Це НЕ транзакція — це один прохід циклу, що доганяє.
class AwayReconciler {
  constructor(private readonly gateway: DeviceGateway) {}

  sweep(home: Home, locks: Map<string, Lock>): ReconcileReport {
    const wantsLocked = home.currentMode === "Away" || home.currentMode === "Night";
    const locked: DeviceId[] = [], offline: DeviceId[] = [], jammed: DeviceId[] = [];
    if (!wantsLocked) return new ReconcileReport(home.currentMode, locked, offline, jammed);

    for (const id of home.locks) {
      const lock = locks.get(id.value);
      if (!lock) continue;
      const out = this.gateway.sendLock(id);       // команда пішла в залізо
      if (out.kind === "offline") {
        offline.push(id);                          // лишаємо останнє відоме, повторимо
        continue;
      }
      lock.reportFromDevice(out.state);            // правда з поля
      if (out.state === "Locked") locked.push(id);
      else if (out.state === "Jammed") jammed.push(id);
      else offline.push(id);                       // відповів, але не замкнувся — у чергу на повтор
    }
    return new ReconcileReport(home.currentMode, locked, offline, jammed);
  }
}
