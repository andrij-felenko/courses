# Фасад: тримає підсистему, порядок і відкіт. Клієнт не знає нічого з цього.
class CheckoutFacade:
    def __init__(self, inventory, payments, orders, mailer):
        self._inventory = inventory
        self._payments = payments
        self._orders = orders
        self._mailer = mailer

    def place_order(self, cart: Cart, card: Card) -> "OrderResult":
        # Крок 1: резерв. Якщо тут упало — відкочувати ще нічого, просто виходимо.
        try:
            reservation = self._inventory.reserve(cart.items)
        except OutOfStockError:
            return OrderResult(ok=False, reason="out_of_stock")

        # Крок 2: платіж. Якщо ВІН упав — резерв уже висить: ЗНІМАЄМО (компенсація).
        try:
            charge = self._payments.charge(card, cart.total)
        except PaymentDeclinedError:
            self._inventory.release(reservation)          # ← відкіт кроку 1
            return OrderResult(ok=False, reason="declined")

        # Крок 3: запис замовлення. Якщо впав — знімаємо І резерв, І платіж.
        try:
            order = self._orders.create(cart, charge.id)
        except Exception:
            self._payments.refund(charge.id)              # ← відкіт кроку 2
            self._inventory.release(reservation)          # ← відкіт кроку 1
            raise                                         # це вже наша вина, не клієнтова

        # Крок 4: лист. НЕ критичний — його збій не валить замовлення й не відкочує.
        try:
            self._mailer.send_confirmation(order)
        except Exception:
            pass          # залогувати й забути: гроші взято, товар є, запис є

        return OrderResult(ok=True, order_id=order.id)


@dataclass
class OrderResult:
    ok: bool
    order_id: str | None = None
    reason: str | None = None
