# ── 1. Об'єкти-значення: незмінні, рівність за вмістом, стережуть себе ──
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class DomainError(Exception):
    pass


@dataclass(frozen=True)                 # frozen → незмінний + рівність за вмістом задарма
class DeviceId:
    value: str
    def __post_init__(self):
        if not self.value:
            raise DomainError("порожній DeviceId — ідентифікатор мусить бути")
    def __str__(self): return self.value

@dataclass(frozen=True)
class HomeId:
    value: str

@dataclass(frozen=True)
class RoomId:
    value: str

@dataclass(frozen=True)
class UserId:
    value: str

class LockState(Enum):                  # замкнений перелік: інших станів не буває
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    JAMMED = "jammed"
    UNKNOWN = "unknown"                 # чесний «не чули від замка», не None і не діра

class HomeMode(Enum):
    HOME = "home"
    AWAY = "away"
    NIGHT = "night"

@dataclass(frozen=True)
class Threshold:
    celsius: float

@dataclass(frozen=True)
class Reading:                          # незмінний вимір — два однакові взаємозамінні
    celsius: float
    at: datetime
    def hotter_than(self, t: Threshold) -> bool:
        return self.celsius > t.celsius

@dataclass(frozen=True)
class Location:
    room_id: RoomId
    spot: str
