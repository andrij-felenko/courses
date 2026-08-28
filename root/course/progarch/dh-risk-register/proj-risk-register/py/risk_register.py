# risk_register.py — реєстр Digital Homes як дані, що самі себе лінтять.
# Запуск у CI:  python risk_register.py   (ненульовий код виходу = білд червоний)

from dataclasses import dataclass
from datetime import date
import sys

# Щаблі, не проценти: три поділки на осі — стільки, скільки чесно можна оцінити.
P_SCORE = {"low": 1, "med": 2, "high": 3, "unknown": 3}
#                                          ^ невідома коштує як найгірша:
#   поки зрізом не збили туман, «відоме невідоме» тримаємо у верхньому куті.
I_SCORE = {"minor": 1, "major": 3, "catastrophic": 4}


@dataclass
class Risk:
    id: str
    what: str            # подія, не абстракція
    probability: str     # low | med | high | unknown
    impact: str          # minor | major | catastrophic
    trigger: str         # ознака-тригер; "" = ще нема
    owner: str           # жива людина; "" = ще нема
    reviewed: date       # коли рядок востаннє чіпали
    state: str           # open | watching | accepted | closed

    @property
    def exposure(self) -> int:
        return P_SCORE[self.probability] * I_SCORE[self.impact]

    @property
    def heavy(self) -> bool:
        # рідкісне ≠ нестрашне: у катастрофи хвіст без дна — важка й на низькій імовірності.
        return self.exposure >= 6 or self.impact == "catastrophic"

    @property
    def active(self) -> bool:
        return self.state in ("open", "watching")
