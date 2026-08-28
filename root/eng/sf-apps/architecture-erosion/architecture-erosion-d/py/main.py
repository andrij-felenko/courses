# ЗАДУМАНО: логіка залежить від порту, не від бази.
from abc import ABC, abstractmethod

class OrderRepository(ABC):                  # порт: контракт без бази
    @abstractmethod
    def load(self, order_id: int) -> Order: ...

def order_total(repo: OrderRepository, order_id: int) -> int:
    order = repo.load(order_id)              # жодного сліду бази
    return order.total()
