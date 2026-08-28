from dataclasses import dataclass
from typing import Callable

MAX_OFFSET_MS = 500   # терпимий відрив чужого годинника вперед, мс
C_MAX = 1 << 16       # 16 бітів під лічильник


class ClockTooFarAhead(Exception):
    """Чужий годинник неправдоподібно попереду — мітку відкидаємо."""


@dataclass
class HLC:
    phys: Callable[[], int]   # джерело настінного часу, мс від епохи
    l: int = 0                # фізична частина мітки
    c: int = 0                # лічильник

    def now(self) -> tuple[int, int]:
        """Локальна подія або відправлення — одне правило."""
        l_prev = self.l
        self.l = max(l_prev, self.phys())
        self.c = self.c + 1 if self.l == l_prev else 0
        self._guard()
        return self.l, self.c

    def update(self, l_m: int, c_m: int) -> tuple[int, int]:
        """Отримання повідомлення з міткою (l_m, c_m)."""
        pt = self.phys()
        if l_m > pt + MAX_OFFSET_MS:
            raise ClockTooFarAhead   # не отруюємо свій l чужим годинником
        l_prev = self.l
        self.l = max(l_prev, l_m, pt)
        if self.l == l_prev == l_m:
            self.c = max(self.c, c_m) + 1
        elif self.l == l_prev:
            self.c += 1
        elif self.l == l_m:
            self.c = c_m + 1
        else:                        # self.l == pt — фізичний обігнав усіх
            self.c = 0
        self._guard()
        return self.l, self.c

    def _guard(self) -> None:
        if self.c >= C_MAX:
            raise OverflowError("лічильник переповнено: фізичний час стоїть надто довго")


def less(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a < b   # кортеж порівнюється лексикографічно: спершу l, потім c
