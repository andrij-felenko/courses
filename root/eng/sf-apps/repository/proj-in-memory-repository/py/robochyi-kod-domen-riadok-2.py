from dataclasses import dataclass
from datetime import timezone


@dataclass(frozen=True)
class OrderRow:
    id: str
    customer_id: str
    total: int
    status: str
    created_at: str          # ISO-8601 у UTC — як у колонці timestamptz


# той самий мапер, яким користується SqlOrderRepository
def to_row(o: Order) -> OrderRow:
    return OrderRow(o.id, o.customer_id, o.total, o.status,
                    o.created_at.astimezone(timezone.utc).isoformat())


def to_domain(r: OrderRow) -> Order:
    return Order(r.id, r.customer_id, r.total,
                 datetime.fromisoformat(r.created_at), r.status)
