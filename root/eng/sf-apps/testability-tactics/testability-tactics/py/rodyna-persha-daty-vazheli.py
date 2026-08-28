# Джерела стали параметрами через інтерфейси — тест підставить свої.
class RateSource(Protocol):
    def rate(self) -> float: ...

class Clock(Protocol):
    def is_weekend(self) -> bool: ...

def order_total(order, rates: RateSource, clock: Clock) -> float:
    total = order.amount * rates.rate()
    if clock.is_weekend():
        total *= 1.05
    return total
