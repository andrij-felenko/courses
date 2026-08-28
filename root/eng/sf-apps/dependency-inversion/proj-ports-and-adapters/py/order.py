# domain/order.py ── СУТНІСТЬ і правила. Не імпортує нічого зовнішнього.
from dataclasses import dataclass


class DomainError(Exception):
    pass


@dataclass(frozen=True)
class Line:
    sku: str
    price: int
    qty: int


@dataclass(frozen=True)
class Order:
    id: str
    email: str
    lines: tuple[Line, ...]

    @staticmethod
    def place(id: str, email: str, lines: list[Line]) -> "Order":
        if not lines:
            raise DomainError("порожнє замовлення")          # ПРАВИЛО
        if "@" not in email:
            raise DomainError("недійсна пошта")              # ПРАВИЛО
        return Order(id, email, tuple(lines))

    def total(self) -> int:
        return sum(l.price * l.qty for l in self.lines)      # ПРАВИЛО
