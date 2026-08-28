from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

# Якісні атрибути, про які дбають стейкхолдери.
class Attr(Enum):
    AVAIL = "доступність"
    MODIF = "змінюваність"
    PERF  = "швидкодія"
    SEC   = "безпека"
    COST  = "вартість"

# Стейкхолдер = ім'я + три булеві осі вагомості + інтерес + його турбота.
@dataclass(frozen=True)
class Stakeholder:
    name: str
    power: bool        # чи може ЗМУСИТИ?
    legitimacy: bool   # чи МАЄ ПРАВО вимагати?
    urgency: bool      # чи мусить бути ЗАРАЗ?
    interest: bool     # чи не байдуже, що буде із системою?
    concern: Attr      # головна турбота
    hard: bool = False # турбота — твердий поріг (закон), а не м'яке вподобання

# Архітектурне рішення свідомо закриває один атрибут.
@dataclass(frozen=True)
class Decision:
    name: str
    closes: Attr

# Параметр устрою тягне атрибути в той чи інший бік: +1 краще, −1 гірше.
@dataclass(frozen=True)
class Push:
    attr: Attr
    dir: int

@dataclass(frozen=True)
class Parameter:
    name: str
    pushes: tuple[Push, ...]

# В'ю обрамлює (показує) певні турботи-атрибути.
@dataclass(frozen=True)
class View:
    name: str
    frames: frozenset[Attr]
