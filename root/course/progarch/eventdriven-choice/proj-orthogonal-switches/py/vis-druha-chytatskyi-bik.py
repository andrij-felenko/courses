@dataclass
class DashRow:
    status: str = "ВІДЧИНЕНО"
    last_actor: str = "—"
    unlocked_today: int = 0

# ── Вісь 2: ЧИТАЦЬКИЙ БІК ──
class Read(Protocol):
    def notify(self, e: DoorEvent) -> None: ...
    def dashboard(self, truth: Truth) -> DashRow: ...

class FoldOnRead:                       # ВИМК — та сама модель
    def notify(self, e: DoorEvent) -> None: pass          # нічого не тримаємо
    def dashboard(self, truth: Truth) -> DashRow:
        s = truth.state()
        return DashRow(status="ЗАЧИНЕНО" if s.locked else "ВІДЧИНЕНО",
                       last_actor=s.last_actor or "—",
                       unlocked_today=-1)                  # без історії не порахувати

class Projection:                       # УВІМК — окрема проєкція (CQRS)
    def __init__(self): self._row = DashRow()
    def notify(self, e: DoorEvent) -> None:
        self._row.status = "ЗАЧИНЕНО" if e.type == "DoorLocked" else "ВІДЧИНЕНО"
        self._row.last_actor = e.actor
        if e.type == "DoorUnlocked":
            self._row.unlocked_today += 1                 # ⚠ див. пастку нижче
    def dashboard(self, truth: Truth) -> DashRow:
        return self._row                                  # готове, без обчислень
