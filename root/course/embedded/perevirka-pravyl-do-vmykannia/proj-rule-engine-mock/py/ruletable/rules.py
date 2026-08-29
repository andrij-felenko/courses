"""Таблиця правил безпеки у формі, придатній для машинного перебору.

Правило тут — не гілка `if` усередині прошивки, а окремий запис: ім'я,
пріоритет, охоронна умова й готові виходи. Саме така форма дає перебрати всі
2^N станів і спитати таблицю про кожен, не запускаючи ані прошивки, ані заліза.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

# П'ять дискретних входів контуру. Порядок фіксований: за ним іде перебір.
INPUT_NAMES: tuple[str, ...] = (
    "level_low",
    "level_high",
    "pressure_ok",
    "flow_ok",
    "e_stop",
)


@dataclass(frozen=True)
class Inputs:
    """Комбінація дискретних входів."""

    level_low: bool = False    # нижній поплавець: у баку є рідина
    level_high: bool = False   # верхній поплавець: бак повний
    pressure_ok: bool = False  # тиск у контурі в межах
    flow_ok: bool = False      # крильчатка бачить протік
    e_stop: bool = False       # натиснуто грибок аварійної зупинки

    def flip(self, name: str) -> "Inputs":
        """Той самий стан з одним переключеним входом."""
        return replace(self, **{name: not getattr(self, name)})

    def physically_possible(self) -> bool:
        # Верхній поплавець спрацював, а нижній — ні. Так не буває: це обрив
        # проводу або залипання. Таблиця мусить мати відповідь і на такий стан.
        return not (self.level_high and not self.level_low)

    def __str__(self) -> str:
        return " ".join(f"{name}={int(getattr(self, name))}" for name in INPUT_NAMES)


@dataclass(frozen=True)
class Outputs:
    heater: bool = False
    pump: bool = False


@dataclass(frozen=True)
class Rule:
    name: str
    priority: int  # менше число — вищий пріоритет
    guard: Callable[[Inputs], bool]
    outputs: Outputs


# Порядок у кортежі важить лише для правил РІВНОГО пріоритету: перше з них
# виграє арбітраж. Різні виходи в рівних за пріоритетом правил — це дефект
# таблиці, і перебір його знаходить.
RULES: tuple[Rule, ...] = (
    Rule("PARADOX_LEVEL_FAULT", 0, lambda x: not x.physically_possible(), Outputs()),
    Rule("EMERGENCY_STOP", 0, lambda x: x.e_stop, Outputs()),
    Rule("EMPTY_TANK_SAFE_OFF", 1, lambda x: not x.level_low, Outputs()),
    Rule("PRESSURE_FAULT_HOLD", 2, lambda x: not x.pressure_ok, Outputs()),
    # Протік не з'явиться сам: якщо на брак протоку відповідати повним стопом,
    # система вже ніколи з цього стану не вийде — саме це й є взаємне блокування.
    Rule("PRIME_LOOP", 3, lambda x: not x.flow_ok, Outputs(heater=False, pump=True)),
    Rule("NORMAL_HEATING", 4, lambda x: True, Outputs(heater=True, pump=True)),
)

UNSPECIFIED = "UNSPECIFIED"


def decide(x: Inputs) -> tuple[Outputs, str, list[Rule]]:
    """Арбітраж: повертає виходи, ім'я переможця й усі правила, що спрацювали."""
    matched = [rule for rule in RULES if rule.guard(x)]
    if not matched:
        # Неврахований стан: таблиця мовчить. У прошивці це означало б, що
        # виходи лишаться такими, як були, — тобто ТЕН може лишитись увімкненим.
        return Outputs(), UNSPECIFIED, []
    winner = min(matched, key=lambda rule: rule.priority)  # min стабільний
    return winner.outputs, winner.name, matched
