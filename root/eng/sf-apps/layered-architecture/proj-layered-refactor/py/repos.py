# domain/repos.py — обіцянки, які домен вимагає від світу (ще не реалізація)
from typing import Protocol
from domain.order import Order, Line

class ProductRepo(Protocol):
    def find(self, sku: str) -> tuple[float, int] | None:
        """Повернути (ціна, залишок) або None, якщо товару немає."""
        ...

class OrderRepo(Protocol):
    def add(self, order: Order) -> int:
        """Зберегти замовлення, повернути його id."""
        ...
    def reduce_stock(self, sku: str, qty: int) -> None:
        ...
