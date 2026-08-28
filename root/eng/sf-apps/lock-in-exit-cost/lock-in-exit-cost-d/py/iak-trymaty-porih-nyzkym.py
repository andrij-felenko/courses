from abc import ABC, abstractmethod

# Свій контракт: рівно те, що потрібно системі.
# Жодних типів вендора тут немає — це і є шов.
class MessageQueue(ABC):
    @abstractmethod
    def publish(self, topic: str, payload: str) -> None:
        ...

    # повертає None, якщо за timeout нічого не прийшло
    @abstractmethod
    def consume(self, timeout_ms: int) -> str | None:
        ...
