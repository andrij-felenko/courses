from collections import deque
from dataclasses import dataclass

SNAP_EVERY = 100                     # знімок на диск — раз на сотню команд

@dataclass
class LockState:
    bolt: str = "unlocked"
    version: int = 5
    last_cmd: str = ""

class HomeActor:
    def __init__(self, home_id, lock=None):
        self.home_id = home_id
        self.lock = lock or LockState()
        self._box = deque()          # ← пошта: єдина черга дому
        self._since_snapshot = 0

    # ЄДИНИЙ вхід ззовні: покласти команду в пошту й піти. Стан ніхто не чіпає напряму.
    def tell(self, cmd):
        self._box.append(cmd)

    # ЄДИНИЙ виконавець дому: бере по одній, доводить до кінця, і лише тоді наступну.
    # (у справжньому рантаймі цей цикл крутиться безперервно, сам собою.)
    def drain(self):
        while self._box:
            self._apply(self._box.popleft())

    def _apply(self, cmd):
        # жодного read-modify-write: стан ось тут, і виконавець його один
        self.lock = LockState(
            bolt="locked" if cmd["kind"] == "lock" else "unlocked",
            version=self.lock.version + 1,
            last_cmd=f"{cmd['by']}#{cmd['seq']}",
        )
        self._since_snapshot += 1
        if self._since_snapshot >= SNAP_EVERY:
            save_snapshot(self.home_id, self.lock)     # періодичний знімок на диск
            self._since_snapshot = 0

# сценарій: дві «замкни» майже водночас — обидві лягають у ту саму пошту
a = HomeActor("home42")
a.tell({"kind": "lock", "seq": 6, "by": "A"})
a.tell({"kind": "lock", "seq": 7, "by": "B"})   # у скриньці тепер ДВІ
a.drain()                                        # виконавець бере по одній: version 5 → 6 → 7
