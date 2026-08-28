from datetime import timedelta

T0 = datetime(2026, 3, 1, 10, 0, tzinfo=timezone.utc)


def day(n: int) -> datetime:
    return T0 + timedelta(days=n)


def paid_order(id: str, customer_id: str, total: int, d: int) -> Order:
    o = Order(id, customer_id, total, day(d))
    o.mark_paid()
    return o
