from dataclasses import dataclass

@dataclass
class Priced:
    total: float
    discount: float

# чиста функція: жодної бази, лише правило ціни в одному місці
def price_order(unit_price: float, qty: int, discount: float, region: str) -> Priced:
    subtotal = unit_price * qty
    net = subtotal * (1 - discount)
    floor = region_floor(region)
    if net < floor:                         # поріг тепер існує РІВНО ТУТ
        net = floor
        discount = 1 - floor / subtotal if subtotal > 0 else 0.0  # підрізана знижка
    total = net * (1 + region_tax(region))
    return Priced(total=total, discount=discount)

# усі три сценарії тепер кличуть одне:
priced = price_order(product.price, qty, loyalty_discount(tx, customer_id), region)
