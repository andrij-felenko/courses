# ids/types.py — спільний словник: окремі типи поверх str, щоб не сплутати ідентифікатори
from typing import NewType
DeviceId = NewType("DeviceId", str)
HomeId   = NewType("HomeId", str)

# ids/events.py — ДРОТОВИЙ факт: ані живих агрегатів, ані вендорських типів
from dataclasses import dataclass
from typing import Literal
from .types import DeviceId, HomeId

@dataclass(frozen=True)
class DeviceEvent:
    kind: Literal["state", "added", "removed"]
    device_id: DeviceId
    home_id: HomeId
    at: int            # epoch-мілісекунди — примітив, не datetime якоїсь бібліотеки
    value: float

# ids/bus.py — внутрішньопроцесна шина: СИНХРОННА диспетчеризація в тій самій транзакції
from typing import Callable
Subscriber = Callable[[DeviceEvent], None]

class Bus:
    def __init__(self) -> None:
        self._subs: list[Subscriber] = []
    def subscribe(self, handler: Subscriber) -> None:
        self._subs.append(handler)
    def publish(self, event: DeviceEvent) -> None:
        for handler in self._subs:      # по черзі, ТУТ-ТАКИ, у tx продюсера
            handler(event)              # виняток підписника ЛЕТИТЬ УГОРУ

# ids/__init__.py — БАР'ЄР спільного ядра
from .types import DeviceId, HomeId
from .events import DeviceEvent
from .bus import Bus, Subscriber
__all__ = ["DeviceId", "HomeId", "DeviceEvent", "Bus", "Subscriber"]
