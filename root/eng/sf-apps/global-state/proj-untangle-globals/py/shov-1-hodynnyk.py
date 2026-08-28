from typing import Protocol

class Clock(Protocol):
    def now(self) -> datetime: ...

class SystemClock:
    def now(self) -> datetime:
        return datetime.now()

class FixedClock:
    def __init__(self, moment: datetime) -> None:
        self._moment = moment
    def now(self) -> datetime:
        return self._moment
