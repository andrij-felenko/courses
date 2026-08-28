from typing import Protocol

# ── Вісь 1: ДЖЕРЕЛО ПРАВДИ ──
class Truth(Protocol):
    def handle(self, cmd: Command) -> DoorEvent: ...
    def state(self) -> LockState: ...

class CrudTruth:                       # ВИМК — перезапис клітинки
    def __init__(self): self._s = INITIAL
    def handle(self, cmd: Command) -> DoorEvent:
        e = decide(self._s, cmd)
        self._s = apply(self._s, e)     # ← минуле стерто
        return e
    def state(self) -> LockState: return self._s

class EventTruth:                      # УВІМК — append-only журнал
    def __init__(self): self._log: list[DoorEvent] = []
    def handle(self, cmd: Command) -> DoorEvent:
        e = decide(self.state(), cmd)
        self._log.append(e)             # ← лише дописуємо
        return e
    def state(self) -> LockState:
        return reduce(apply, self._log, INITIAL)   # згортка щоразу
