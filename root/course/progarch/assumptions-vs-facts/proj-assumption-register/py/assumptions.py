# assumptions.py — журнал припущень, що рахує й спиняє
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import yaml                                   # pip install pyyaml


class State(str, Enum):
    OPEN     = "open"        # ще не чіпали
    CHECKING = "checking"    # перевірка в роботі
    ACCEPTED = "accepted"    # свідомо прийняли під знак
    FACT     = "fact"        # доведено — доказ на руках
    BROKEN   = "broken"      # знак спрацював, припущення впало


LIVE = {State.OPEN, State.CHECKING, State.ACCEPTED}   # ще важать на рішення


@dataclass
class Assumption:
    id: str
    claim: str
    kind: str                # несуче | побутове | продуктове
    p_wrong: float           # 0..1
    loss: float              # людино-дні, якщо хибне
    cost_to_check: float     # людино-дні на перевірку
    method: str              # ЧИМ перевіряємо (не «перевірити», а як саме)
    signpost: str            # поріг, за яким припущення вважаємо зламаним
    state: State
    decision: str            # яке рішення (ADR) на ньому стоїть
    irreversible: bool       # чи веде те рішення до незворотного кроку

    def expected_loss(self) -> float:
        return self.p_wrong * self.loss if self.state in LIVE else 0.0

    def worth_checking(self) -> bool:
        # перевіряти має сенс, лише поки не прийняли й не довели
        if self.state not in (State.OPEN, State.CHECKING):
            return False
        return self.cost_to_check < self.expected_loss()
