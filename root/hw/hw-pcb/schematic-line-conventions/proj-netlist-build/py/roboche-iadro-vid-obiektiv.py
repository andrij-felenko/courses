from dataclasses import dataclass
from enum import Enum

# Точка на аркуші — у КРОКАХ СІТКИ (цілі!), щоб «дотик» був точним ==, а не «майже».
# frozen=True робить точку незмінною й хешованою — тож вона годиться в ключ dict/set,
# а рівність двох точок — це збіг обох координат (Python дає __eq__/__hash__ даром).
@dataclass(frozen=True)
class Point:
    x: int
    y: int

@dataclass
class Wire:                              # відрізок дроту: два кінці
    a: Point
    b: Point

@dataclass
class Pin:                               # вивід деталі
    at: Point
    part: int
    num: int
    name: str

# Мітка ланцюга. scope розрізняє радіус дії: локальна діє в межах аркуша,
# глобальна — по всьому проєкту. Тому ключ збігу — ПАРА (ім'я, область).
class Scope(Enum):
    LOCAL = 0
    GLOBAL = 1

@dataclass
class Label:
    at: Point
    name: str
    scope: Scope
    sheet: int
