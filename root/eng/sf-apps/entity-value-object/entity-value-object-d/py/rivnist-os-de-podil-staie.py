from dataclasses import dataclass

# frozen=True робить об'єкт незмінним І дає рівність за полями «безкоштовно»:
# dataclass сам згенерує __eq__, що порівнює всі поля, і __hash__.
@dataclass(frozen=True)
class Money:
    amount: int          # у копійках
    currency: str

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("не можна додавати різні валюти")
        return Money(self.amount + other.amount, self.currency)  # НОВИЙ об'єкт

a = Money(30000, "UAH")
b = Money(30000, "UAH")
a == b            # True — рівність за вмістом, як і має бути для значення
a is b            # False — різні об'єкти в пам'яті, але нам байдуже
