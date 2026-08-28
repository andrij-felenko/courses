# Крок рефакторингу: та сама поведінка, зрозуміліша будова.
# Магічні числа стали іменами, гілки — окремими функціями.
VIP_THRESHOLD = 1000.0
VIP_RATE      = 0.15

def compute_discount(cart: Cart, vip: bool) -> float:
    subtotal = cart.subtotal()
    if vip and subtotal >= VIP_THRESHOLD:
        return subtotal * VIP_RATE           # 1200 · 0.15 = 180 — тест досі зелений
    return regular_discount(subtotal)
