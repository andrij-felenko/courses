type Twin = { homeId: string; version: number; bolt: "locked" | "unlocked"; lastCmd: string };
type Cmd = { kind: "lock" | "unlock"; seq: number; by: string };
type LockEvent = { homeId: string; action: string; by: string; at: number };

const emptyTwin = (homeId: string): Twin => ({ homeId, version: 0, bolt: "unlocked", lastCmd: "" });

// ── 1. ШАРД-СХОВИЩЕ: джерело правди, рядок на home_id, CAS по version ──
class ShardStore {
  private rows = new Map<string, Twin>();
  seed(t: Twin): void { this.rows.set(t.homeId, t); }          // початкове завантаження/міграція
  get(homeId: string): Twin { return this.rows.get(homeId) ?? emptyTwin(homeId); }
  // запис проходить, ЛИШЕ якщо version та сама, що ми читали (інакше хтось випередив)
  putCas(next: Twin, expectedVersion: number): boolean {
    if (this.get(next.homeId).version !== expectedVersion) return false;
    this.rows.set(next.homeId, next);         // у реалі — транзакція + fsync (журнал попереднього запису)
    return true;
  }
}

// ── 3. ЖУРНАЛ АУДИТУ: append-only, лише замки й доступ ──
class AuditLog {
  private events: LockEvent[] = [];
  append(e: LockEvent): void { this.events.push(e); }          // append-only: ніколи не UPDATE/DELETE
  read(homeId: string, since: number, until: number): LockEvent[] {
    return this.events.filter(e => e.homeId === homeId && e.at >= since && e.at < until);
  }
}
