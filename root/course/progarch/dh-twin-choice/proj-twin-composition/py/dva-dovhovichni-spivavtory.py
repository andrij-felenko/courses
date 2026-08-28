import time
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Twin:
    home_id: str
    version: int = 0
    bolt: str = "unlocked"
    last_cmd: str = ""

@dataclass(frozen=True)
class LockEvent:
    home_id: str
    action: str            # "locked" | "unlocked"
    by: str
    at: float

# ── 1. ШАРД-СХОВИЩЕ: джерело правди, рядок на home_id, CAS по version ──
class ShardStore:
    def __init__(self):
        self._rows: dict[str, Twin] = {}
    def seed(self, t: Twin) -> None:                 # початкове завантаження/міграція
        self._rows[t.home_id] = t
    def get(self, home_id: str) -> Twin:
        return self._rows.get(home_id) or Twin(home_id)
    # запис проходить, ЛИШЕ якщо version та сама, що ми читали (інакше хтось випередив)
    def put_cas(self, nxt: Twin, expected_version: int) -> bool:
        if self.get(nxt.home_id).version != expected_version:
            return False
        self._rows[nxt.home_id] = nxt                # у реалі — транзакція + fsync
        return True

# ── 3. ЖУРНАЛ АУДИТУ: append-only, лише замки й доступ ──
class AuditLog:
    def __init__(self):
        self._events: list[LockEvent] = []
    def append(self, e: LockEvent) -> None:          # append-only: ніколи не UPDATE/DELETE
        self._events.append(e)
    def read(self, home_id: str, since: float, until: float) -> list[LockEvent]:
        return [e for e in self._events if e.home_id == home_id and since <= e.at < until]
