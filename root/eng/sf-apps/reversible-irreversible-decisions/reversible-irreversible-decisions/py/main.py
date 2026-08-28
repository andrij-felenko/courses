# ЗІ ШВОМ: логіка знає тільки інтерфейс, база — за адаптером
from abc import ABC, abstractmethod

class OrderRepo(ABC):                     # порт: контракт без бази
    @abstractmethod
    def total(self, order_id: int) -> float: ...

def order_total(repo: OrderRepo, order_id: int) -> float:
    return repo.total(order_id)           # жодного сліду конкретної бази

# Конкретна база живе в ОДНОМУ місці — в адаптері:
class PgOrderRepo(OrderRepo):             # сьогодні PostgreSQL...
    def total(self, order_id: int) -> float: ...  # psycopg2-запит саме тут
# Завтра інша база — новий адаптер, а order_total і виклики не міняються.
