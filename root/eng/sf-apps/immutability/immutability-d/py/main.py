from dataclasses import dataclass, replace

@dataclass(frozen=True)          # frozen дає незмінність + __eq__ + __hash__ за вмістом
class Money:
    amount: int
    currency: str

    def add(self, o: "Money") -> "Money":
        if o.currency != self.currency:
            raise ValueError("різні валюти")
        return replace(self, amount=self.amount + o.amount)   # новий примірник

a = Money(100, "UAH")
b = Money(100, "UAH")
a is b       # False — різні примірники (ідентичність)
a == b       # True  — рівні за значенням
