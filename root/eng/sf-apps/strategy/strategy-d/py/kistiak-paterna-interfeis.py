from abc import ABC, abstractmethod

class DiscountPolicy(ABC):                        # інтерфейс стратегії: одна операція
    @abstractmethod
    def discount(self, order: "Order") -> float: ...

class NoDiscount(DiscountPolicy):
    def discount(self, order): return 0.0

class VipDiscount(DiscountPolicy):
    def discount(self, order): return order.total * 0.20

class SeasonalDiscount(DiscountPolicy):
    def __init__(self, rate: float):              # стратегія може мати власний стан
        self.rate = rate
    def discount(self, order): return order.total * self.rate
