from collections import defaultdict
from typing import Callable

class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, type_: str, handler: Callable) -> None:
        self._handlers[type_].append(handler)

    # викликає обробників ЗАРАЗ ЖЕ, у тому самому потоці
    def publish(self, type_: str, event: object) -> None:
        for handler in self._handlers[type_]:
            handler(event)
