from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Rec:
    value: Any
    version: int

class Replica:
    def __init__(self, rid: str):
        self.id = rid
        self.linked = True                 # чи доходять оновлення від лідера (False — у розкол)
        self._data: dict[str, Rec] = {}

    def local(self, key: str) -> Optional[Rec]:
        return self._data.get(key)

    # Монотонність версій: приймаємо лише СВІЖІШЕ; старий кадр не затирає нового.
    def apply(self, key: str, rec: Rec) -> None:
        cur = self._data.get(key)
        if cur is None or rec.version > cur.version:
            self._data[key] = rec
