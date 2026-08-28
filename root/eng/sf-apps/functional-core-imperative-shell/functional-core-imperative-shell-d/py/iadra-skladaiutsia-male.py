# Кожен крок — чиста функція від значення до значення.
def subtotal(items: list[Item]) -> float:
    return sum(i.price * i.qty for i in items)
def with_tax(rate: float):
    return lambda t: t * (1 + rate)
def with_vol(t: float) -> float:
    return t * 0.95 if t > 1000 else t

# Велике рішення — композиція малих. Ціле лишається чистим.
def price(items: list[Item], rate: float) -> float:
    return with_vol(with_tax(rate)(subtotal(items)))
