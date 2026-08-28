from dataclasses import dataclass

@dataclass(frozen=True)
class Item:  price: int; qty: int          # ціна в копійках

@dataclass(frozen=True)
class Order: pre_discount: float; total: float; discounted: bool

def price_order(items: list[Item], tax_rate: float) -> Order:
    subtotal = sum(it.price * it.qty for it in items)
    pre_discount = subtotal * (1 + tax_rate)           # сума з податком, ДО знижки
    discounted = pre_discount > 1000                   # знижка за великий чек
    total = pre_discount * 0.95 if discounted else pre_discount
    return Order(pre_discount=pre_discount, total=total, discounted=discounted)
