from dataclasses import dataclass, replace
from typing import Protocol

Money = int  # копійки

class PriceCatalog(Protocol):
    def price_of(self, sku: str) -> Money: ...

class OrderRepository(Protocol):
    def save(self, order: "Order") -> None: ...
    def find(self, order_id: str) -> "Order | None": ...

class Notifier(Protocol):
    def send_confirmation(self, email: str, total: Money) -> None: ...

class AuditLog(Protocol):
    def record(self, event: str, order_id: str) -> None: ...

@dataclass
class Line:
    sku: str
    qty: int

@dataclass
class Order:
    id: str
    email: str
    total: Money
    status: str  # "placed"

@dataclass
class PlaceOrderCmd:
    order_id: str
    email: str
    items: list[Line]

@dataclass
class Deps:
    catalog: PriceCatalog
    repo: OrderRepository
    notifier: Notifier
    audit: AuditLog

def place_order(cmd: PlaceOrderCmd, deps: Deps) -> Order:
    total = sum(deps.catalog.price_of(line.sku) * line.qty for line in cmd.items)
    order = Order(id=cmd.order_id, email=cmd.email, total=total, status="placed")
    deps.repo.save(order)
    deps.notifier.send_confirmation(order.email, total)
    deps.audit.record("order_placed", order.id)
    return order
