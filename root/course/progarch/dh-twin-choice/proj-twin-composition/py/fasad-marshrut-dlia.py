# ── ФАСАД: маршрутизує команду й ТРИ різні читання ──
class TwinService:
    def __init__(self, store: ShardStore, audit: AuditLog):
        self._store, self._audit = store, audit
        self._live: dict[str, HomeSession] = {}    # реєстр гарячих сесій (хто на зв'язку)

    # активувати (чи знайти) живу сесію — саме ТУТ відбувається гідратація
    def _activate(self, home_id: str) -> HomeSession:
        s = self._live.get(home_id)
        if s is None:
            s = HomeSession(home_id, self._store, self._audit)
            s.hydrate()
            self._live[home_id] = s
        return s

    # КОМАНДА: завжди крізь живу сесію (серіалізація + наскрізний запис)
    def command(self, home_id: str, cmd: dict) -> None:
        self._activate(home_id).tell(cmd)

    # ЧИТАННЯ: тепле → з актора (read-your-writes); холодне → прямо зі шарда по ключу
    def show(self, home_id: str) -> Twin:
        s = self._live.get(home_id)
        return s.snapshot() if s else self._store.get(home_id)    # дім спить → повз актор

    # ІСТОРІЯ: завжди з журналу — не чіпає ні актор, ні поточний стан
    def history(self, home_id: str, since: float, until: float) -> list[LockEvent]:
        return self._audit.read(home_id, since, until)

    def release(self, home_id: str) -> None:       # засинання: відпустити сесію
        self._live.pop(home_id, None)
