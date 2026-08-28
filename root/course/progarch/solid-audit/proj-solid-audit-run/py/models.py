# models.py — дані, якими обмінюються шари (не types.py: так зветься модуль стандартної бібліотеки)
from dataclasses import dataclass

@dataclass(frozen=True)
class SensorEvent:
    type: str
    zone: str

@dataclass(frozen=True)
class Message:
    to: str
    body: str

# ports.py — вузькі абстракції, які визначає ЯДРО
from typing import Protocol
from datetime import datetime
from models import Message

class Notifier(Protocol):                       # рівно одна дія
    async def send(self, msg: Message) -> None: ...

class Clock(Protocol):
    def now(self) -> datetime: ...
