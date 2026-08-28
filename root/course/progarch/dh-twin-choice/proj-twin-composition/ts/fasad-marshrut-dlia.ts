// ── ФАСАД: маршрутизує команду й ТРИ різні читання ──
class TwinService {
  private live = new Map<string, HomeSession>();   // реєстр гарячих сесій (хто на зв'язку)
  constructor(private store: ShardStore, private audit: AuditLog) {}

  // активувати (чи знайти) живу сесію — саме ТУТ відбувається гідратація
  private activate(homeId: string): HomeSession {
    let s = this.live.get(homeId);
    if (!s) { s = new HomeSession(homeId, this.store, this.audit); s.hydrate(); this.live.set(homeId, s); }
    return s;
  }

  // КОМАНДА: завжди крізь живу сесію (серіалізація + наскрізний запис)
  command(homeId: string, cmd: Cmd): void { this.activate(homeId).tell(cmd); }

  // ЧИТАННЯ: тепле → з актора (read-your-writes); холодне → прямо зі шарда по ключу
  show(homeId: string): Twin {
    const s = this.live.get(homeId);
    return s ? s.snapshot() : this.store.get(homeId);      // дім спить → повз актор
  }

  // ІСТОРІЯ: завжди з журналу — не чіпає ні актор, ні поточний стан
  history(homeId: string, since: number, until: number): LockEvent[] {
    return this.audit.read(homeId, since, until);
  }

  release(homeId: string): void { this.live.delete(homeId); }   // засинання: відпустити сесію
}
