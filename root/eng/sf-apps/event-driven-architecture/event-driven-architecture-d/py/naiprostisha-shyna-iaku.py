from collections import defaultdict
from typing import Callable

class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    # підписник заявляє інтерес до типу події
    def subscribe(self, event_type: str, handler: Callable) -> None:
        self._handlers[event_type].append(handler)

    # видавець оголошує факт; шина розносить його всім підписаним
    def publish(self, event_type: str, event: object) -> None:
        for handler in self._handlers[event_type]:
            handler(event)
