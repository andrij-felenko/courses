from dataclasses import dataclass

# ── ЯДРО: чисте, нічого не читає й не пише, лише рахує ──
@dataclass(frozen=True)
class Order:
    total: float
    discounted: bool

def price_order(items: list[Item], tax_rate: float) -> Order:
    total = sum(it.price * it.qty for it in items)
    total *= 1 + tax_rate
    discounted = total > 1000
    if discounted:
        total *= 0.95
    return Order(total=total, discounted=discounted)

# ── ОБОЛОНКА: тонка, лише возить дані; жодного рішення ──
async def checkout(cart_id: str) -> None:
    cart = await db.load_cart(cart_id)              # принести
    rate = await config.tax_rate()                  # принести

    order = price_order(cart.items, rate)           # ← усе рішення тут, у ядрі

    await db.save_order(cart_id, order.total)       # винести
    await mailer.send_receipt(cart.email, order.total)  # винести
