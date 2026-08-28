# Сервісний шар: одна операція = один сценарій. Сам НЕ рахує правил —
# відкриває транзакцію, дістає домен, делегує йому, зберігає, сповіщає.
class OrderService:
    def __init__(self, orders, payments, mailer, tx):
        self._orders = orders        # сховище (інтерфейс, не база)
        self._payments = payments    # платіжний шлюз (інтерфейс)
        self._mailer = mailer        # пошта (інтерфейс)
        self._tx = tx

    def place_order(self, cmd: PlaceOrderCommand) -> OrderDto:
        with self._tx.begin():
            cart = self._orders.load_cart(cmd.cart_id)

            # ↓ логіка ПРЕДМЕТА — рішення ухвалює домен, не сервіс
            order = cart.checkout()               # кине помилку, якщо кошик порожній

            self._payments.charge(order.total(), cmd.card)  # domain дав суму
            self._orders.save(order)
            self._mailer.send_confirmation(order)           # логіка ЗАСТОСУНКУ
            return OrderDto.from_order(order)     # назовні — DTO, не голий домен
