# БЕЗ фасаду: контролер сам знає всі 4 служби, порядок і відкіт
class CheckoutController:
    def __init__(self, inventory, payments, orders, mailer):
        self._inventory = inventory       # залежність 1
        self._payments = payments         # залежність 2
        self._orders = orders             # залежність 3
        self._mailer = mailer             # залежність 4

    def handle_post(self, cart: Cart, card: Card) -> "Response":
        reservation = None
        try:
            reservation = self._inventory.reserve(cart.items)         # крок 1
            charge = self._payments.charge(card, cart.total)          # крок 2
            order = self._orders.create(cart, charge.id)              # крок 3
            try:
                self._mailer.send_confirmation(order)                 # крок 4
            except Exception:
                pass                        # лист не критичний — ковтаємо
            return Response.ok(order.id)
        except OutOfStockError:
            if reservation:
                self._inventory.release(reservation)                  # відкіт!
            return Response.conflict("Розкупили")
        except PaymentDeclinedError:
            if reservation:
                self._inventory.release(reservation)                  # відкіт!
            return Response.payment_required("Відхилено")
