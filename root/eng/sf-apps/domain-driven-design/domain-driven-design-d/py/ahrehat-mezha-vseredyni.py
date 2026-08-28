# Корінь агрегату — єдині двері; позиції змінюють ЛИШЕ через замовлення
class Order:                        # корінь
    def __init__(self):
        self._lines: list[OrderLine] = []   # внутрішні частини — закриті

    def add_line(self, product: ProductId, qty: int, price: Money) -> None:
        if self._is_placed:
            raise DomainError("не можна міняти оформлене замовлення")
        self._lines.append(OrderLine(product, qty, price))
        # інваріант «сума = сумі позицій» тримається тут і тільки тут

    def total(self) -> Money:
        return sum((l.subtotal() for l in self._lines), Money.zero())
