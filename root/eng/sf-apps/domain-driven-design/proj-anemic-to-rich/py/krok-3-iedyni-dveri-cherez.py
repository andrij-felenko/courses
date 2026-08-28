class Policy:
    # ...конструктор і переходи стану, як у кроці 2...

    # ЄДИНІ ДВЕРІ для платежу: сюди зайти можна лише правильним значенням
    def add_payment(self, amount: int) -> None:
        if self._status not in (PolicyStatus.ACTIVE, PolicyStatus.GRACE):
            raise DomainError("платіж приймають лише за чинним полісом")
        if amount <= 0:
            raise DomainError("платіж має бути додатним")
        if self.paid_total() + amount > self._premium:
            raise DomainError("сума платежів не може перевищити премію")
        self._payments.append(amount)

    def paid_total(self) -> int:
        return sum(self._payments)

    # назовні — КОПІЯ, а не сам список: читач не дотягнеться до нутрощів
    @property
    def payments(self) -> tuple:
        return tuple(self._payments)
