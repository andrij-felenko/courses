from dataclasses import dataclass


@dataclass(frozen=True)   # frozen -> незмінний і порівнюється за значенням "з коробки"
class Money:
    cents: int            # тримаємо в копійках — жодних дробових гривень
    currency: str

    @staticmethod
    def of(amount: int, currency: str) -> "Money":
        if not isinstance(amount, int) or amount < 0:
            raise DomainError("сума має бути невід'ємним цілим числом копійок")
        return Money(amount, currency)

    @staticmethod
    def zero(currency: str) -> "Money":
        return Money(0, currency)

    def plus(self, other: "Money") -> "Money":
        self._same_currency(other)
        return Money(self.cents + other.cents, self.currency)

    def is_greater_than(self, other: "Money") -> bool:
        self._same_currency(other)
        return self.cents > other.cents

    def _same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise DomainError(f"не складаються різні валюти: {self.currency} і {other.currency}")
