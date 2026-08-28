class Pricer:
    def total(self, cart, user):
        total = sum(it.price * it.qty for it in cart.items)
        if user.is_vip:
            total *= 0.9
        return total

class OrderManager:
    def __init__(self):
        self._pricer = Pricer()          # поки що створює сам — це тимчасово

    def _total(self, cart, user):
        return self._pricer.total(cart, user)   # старе ім'я лишилось, тіло переїхало
