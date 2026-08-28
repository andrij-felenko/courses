# debt_gate.py — журнал боргу як дані, що звіряються з кодом і метриками.
# Запуск у CI:  python debt_gate.py   (ненульовий код виходу = білд червоний)

from dataclasses import dataclass
import re, sys
from pathlib import Path


@dataclass(frozen=True)
class Clause:            # машинний строк
    metric: str
    op: str             # ">" | ">=" | "<" | "<="
    threshold: float


@dataclass
class Debt:
    id: str             # ← ЗШИВАЧ: та сама мітка в коді (# DEBT(id)) і тут
    body: str           # тіло боргу — що саме тимчасове
    why: str            # чому взяли (дедлайн проти чесного рішення)
    seam: str           # за яким швом замкнено (де його весь видно)
    interest: str       # сигнал відсотка — куди дивитись, щоб побачити, як капає
    trigger: list       # ← СТРОК: list[Clause]; будь-яка істинна → час гасити
    repay: str          # план погашення — чим заміняємо
    test: str           # страховка — тест, що робить заміну безпечною
    owner: str          # жива людина/команда; "" = діра
    state: str          # "open" | "closed"
