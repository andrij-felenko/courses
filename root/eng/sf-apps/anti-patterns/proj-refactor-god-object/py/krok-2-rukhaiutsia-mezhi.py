class OrderManager:
    def place_order(self, cart, user):
        self._validate(cart)
        total = self._total(cart, user)
        self._save(user, total)
        self._notify(user, total)
        return total

    def _validate(self, cart):
        if not cart.items:
            raise ValueError("порожній кошик")
        for it in cart.items:
            if it.qty <= 0:
                raise ValueError("хибна кількість")

    def _total(self, cart, user):
        total = sum(it.price * it.qty for it in cart.items)
        if user.is_vip:
            total *= 0.9
        return total

    def _save(self, user, total):
        self._open_db().execute(
            "INSERT INTO orders(user_id, total) VALUES(?, ?)", user.id, total)

    def _notify(self, user, total):
        self._open_smtp().sendmail(
            "shop@x", user.email, "Замовлення на %s прийнято" % total)
