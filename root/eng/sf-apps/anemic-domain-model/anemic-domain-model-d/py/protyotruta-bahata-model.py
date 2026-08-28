class Order:
    def __init__(self):
        self._status = "new"
        self._discount = 0
        self._items = []

    # правило знижки тепер ТУТ, разом зі своїм вартовим
    def apply_discount(self, percent):
        if self._status != "new":
            raise DomainError("знижку міняють лише до оплати")
        if percent < 0 or percent > 100:
            raise DomainError("знижка поза межами 0..100")
        self._discount = percent

    def ship(self):
        if self._status != "paid":           # перевірка, якої бракувало
            raise DomainError("відвантажують лише оплачене")
        self._status = "shipped"
