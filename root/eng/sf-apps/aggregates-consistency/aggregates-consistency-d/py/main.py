class Order:
    def __init__(self) -> None:
        # Внутрішні частини — приватні. Ззовні до них не дотягтися.
        self._lines: list[OrderLine] = []
        self._discount = Money.ZERO

    def add_line(self, product: ProductId, qty: int, price: Money) -> None:
        if qty <= 0:
            raise ValueError("кількість має бути додатною")
        self._lines.append(OrderLine(product, qty, price))
        # правило перевіряти не треба: додавання рядка лише збільшує суму

    def apply_discount(self, amount: Money) -> None:
        if amount.is_negative():
            raise ValueError("знижка не буває від'ємною")
        if amount > self.subtotal():                     # ← спільне правило
            raise ValueError("знижка не може перевищити суму рядків")
        self._discount = amount

    def remove_line(self, product: ProductId) -> None:
        self._lines = [l for l in self._lines if l.product != product]
        # прибрали рядок → сума впала → знижка могла стати завеликою:
        if self._discount > self.subtotal():
            self._discount = self.subtotal()             # тримаємо правило

    def subtotal(self) -> Money:
        return sum((l.total() for l in self._lines), Money.ZERO)

    def total(self) -> Money:
        return self.subtotal() - self._discount
