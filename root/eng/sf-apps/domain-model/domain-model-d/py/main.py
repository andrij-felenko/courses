class Order:
    def __init__(self):
        self._status: Status = "new"
        self._lines: list[OrderLine] = []

    # операція — це розмова, а не процедура: Order нічого не рахує сам,
    # він лише збирає відповіді від тих, хто володіє потрібними даними
    def place(self, customer: "Customer") -> None:
        if not self._lines:
            raise DomainError("порожнє замовлення оформити не можна")
        for line in self._lines:
            line.product.reserve(line.qty)       # товар сам стереже свій залишок
        tier = customer.tier()                   # клієнт сам знає свій рівень
        self._total = sum(
            (l.subtotal().with_discount(tier) for l in self._lines),
            Money.zero())                        # гроші самі знають, як додаватись
        self._status = "placed"                  # інваріант циклу — під замком самого Order
