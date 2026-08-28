# Фасад над підсистемою оформлення: складає крихкий порядок в один метод
class CheckoutFacade:
    def __init__(self, inventory, payments, orders, mailer):
        self._inventory = inventory
        self._payments = payments
        self._orders = orders
        self._mailer = mailer

    def place_order(self, cart: "Cart", card: "Card") -> "OrderId":
        # порядок кроків — крихкий, і він захований ТУТ, а не в клієнті
        self._inventory.reserve(cart.items)                 # 1. спершу резерв
        charge = self._payments.charge(card, cart.total)    # 2. тоді гроші
        order = self._orders.create(cart, charge.id)        # 3. запис
        self._mailer.send_confirmation(order)               # 4. і лише тепер лист
        return order.id


# Клієнт (веб-контролер) не знає ні кроків, ні їхнього порядку:
id = checkout.place_order(cart, card)
