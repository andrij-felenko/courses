from typing import Callable

# стратегія — це просто тип функції: Order -> float
DiscountPolicy = Callable[["Order"], float]

def vip(o: "Order") -> float: return o.total * 0.20
def seasonal(rate: float) -> DiscountPolicy:
    return lambda o: o.total * rate

class Order:
    def __init__(self, total: float, policy: DiscountPolicy):
        self.total = total
        self._policy = policy
    def final_price(self) -> float:
        return self.total - self._policy(self)   # кличемо функцію напряму

order = Order(1000, vip)              # передаємо функцію, не об'єкт
order.final_price()                   # 800
Order(1000, seasonal(0.30)).final_price()   # 700
