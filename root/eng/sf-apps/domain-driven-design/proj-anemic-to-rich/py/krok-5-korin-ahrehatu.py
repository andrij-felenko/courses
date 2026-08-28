@dataclass(frozen=True)
class Payment:                        # внутрішня частина агрегату — теж незмінна
    amount: Money
    at: object                        # дата платежу


class Policy:                         # ← корінь агрегату
    # ...стан, премія, переходи — як раніше...

    # єдині двері: платіж додають ЛИШЕ через корінь, і тут тримається інваріант
    def add_payment(self, amount: Money, at) -> None:
        if self._status not in (PolicyStatus.ACTIVE, PolicyStatus.GRACE):
            raise DomainError("платіж приймають лише за чинним полісом")
        if self.paid_total().plus(amount).is_greater_than(self._premium):
            raise DomainError("сума платежів не може перевищити премію")
        self._payments.append(Payment(amount, at))

    def paid_total(self) -> Money:
        total = Money.zero(self._premium.currency)
        for p in self._payments:
            total = total.plus(p.amount)
        return total

    # назовні — незмінний знімок, а не жива внутрішня колекція
    @property
    def payments(self) -> tuple:
        return tuple(self._payments)
