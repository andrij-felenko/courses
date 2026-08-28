from dataclasses import dataclass

# Багатий домен: поведінка, приховані поля, інваріанти під замком
class Order:
    def __init__(self, id, cost, lines, status):
        self._id = id              # внутрішній ключ бази
        self._cost = cost          # собівартість — назовні не їде
        self._lines = lines        # рядки замовлення (товар, кількість, ціна)
        self._status = status      # New / Paid / Shipped / Cancelled

    def total(self) -> Money:      # правило: сума з урахуванням знижок
        ...
    def can_cancel(self) -> bool:  # правило: коли скасування дозволене
        ...
    def cancel(self) -> None:      # міняє статус, боронячи інваріант
        ...
    # ... конструктор, що НЕ дає створити некоректне замовлення

@dataclass(frozen=True)
class Line:                        # рядок домену теж багатий: valid-об'єкти
    sku: Sku                       # код товару (не голий рядок — тип із перевіркою)
    qty: int                       # кількість > 0 (гарантує конструктор)
    unit_price: Money
