# domain/notifications.py — усе у ВАШИХ термінах.
from dataclasses import dataclass
from typing import Literal, Protocol, Union

@dataclass(frozen=True)
class Recipient:
    email: str
    name: str
    locale: Literal["uk", "en"]      # мову листа знає домен, не вендор

# Події домену — те, ПРО ЩО сповіщаємо, мовою вашого продукту.
@dataclass(frozen=True)
class OrderShipped:
    order_id: str
    eta_minutes: int

@dataclass(frozen=True)
class CourierNear:
    order_id: str
    minutes_away: int

@dataclass(frozen=True)
class OrderDelivered:
    order_id: str

DomainEvent = Union[OrderShipped, CourierNear, OrderDelivered]

# Наслідок спроби — теж доменний: доставлено / варто повторити / марно.
@dataclass(frozen=True)
class NotifyOutcome:
    status: Literal["delivered", "retryable", "rejected"]
    reason: str = ""

    @classmethod
    def delivered(cls) -> "NotifyOutcome":
        return cls("delivered")
    @classmethod
    def retryable(cls, reason: str) -> "NotifyOutcome":
        return cls("retryable", reason)
    @classmethod
    def rejected(cls, reason: str) -> "NotifyOutcome":
        return cls("rejected", reason)

# Порт: одне гніздо, назване вашою ПОТРЕБОЮ (структурний інтерфейс).
class Notifier(Protocol):
    def notify(self, to: Recipient, event: DomainEvent) -> NotifyOutcome: ...
