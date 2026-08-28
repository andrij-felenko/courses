class Policy:
    # ...інше, як раніше...

    def __init__(self, policy_id, due_date, premium: Money):
        self._id = policy_id
        self._due_date = due_date
        self._premium = premium          # валюта поліса задана раз, тут
        self._status = PolicyStatus.DRAFT
        self._payments: list[Money] = []

    def add_payment(self, amount: Money) -> None:
        if self._status not in (PolicyStatus.ACTIVE, PolicyStatus.GRACE):
            raise DomainError("платіж приймають лише за чинним полісом")
        # «додатність» і «та сама валюта» вже гарантує сам Money — тут не дублюємо
        after_pay = self.paid_total().plus(amount)       # кине, якщо валюти різні
        if after_pay.is_greater_than(self._premium):
            raise DomainError("сума платежів не може перевищити премію")
        self._payments.append(amount)

    def paid_total(self) -> Money:
        total = Money.zero(self._premium.currency)
        for m in self._payments:
            total = total.plus(m)
        return total
