def place_order(self, cart: Cart, card: Card) -> "OrderResult":
    # ✗ рахує знижку — це БІЗНЕС-рішення, а не виклик підсистеми
    if cart.total > 1000:
        cart.total *= 0.9

    # ✗ вирішує, чи давати клієнтові кредит — знову бізнес-правило
    if self._is_vip(cart.email) and cart.total < self._credit_limit(cart.email):
        ...

    # ✗ сам рахує податок за таблицею регіонів — предметна логіка
    tax = cart.total * self._tax_rate_for(cart.region)

    # ✗ веде власний стан — лічильник, кеш, історія
    self._orders_today += 1
    self._recent_carts.append(cart)

    # ...і десь тут, поміж усім цим, ще й ті чотири виклики служб
