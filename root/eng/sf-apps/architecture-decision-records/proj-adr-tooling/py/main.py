# Гроші тримаємо в Decimal (не int-копійки, не float).
# Причини, відкинуті варіанти й ціна: doc/adr/0011-money-as-decimal.md
# (це рішення замінило ADR-0007 «int64 у копійках» — див. посилання там).
#
# Коротко: int-копійки не вмістили валют із трьома знаками й податкових
# правил зі складним округленням; float заборонений через похибку на дробах.

from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    amount: Decimal                       # десятковий тип, точний на дробах

    def __add__(self, o: "Money") -> "Money":
        return Money(self.amount + o.amount)

    def __mul__(self, scale: int) -> "Money":
        return Money(self.amount * scale)

# Наступний, хто захоче «повернути на int-копійки для швидкості», спершу
# прочитає ADR-0011 і побачить, ЧОМУ від них свідомо пішли — і не
# повторить уже пройдену помилку.
