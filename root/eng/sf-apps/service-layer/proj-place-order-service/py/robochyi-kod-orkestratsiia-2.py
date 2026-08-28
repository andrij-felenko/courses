class OrderService:
    def __init__(self, orders, payments, mailer, idempotency, tx):
        self._orders = orders
        self._payments = payments
        self._mailer = mailer
        self._idempotency = idempotency
        self._tx = tx

    def place_order(self, cmd: PlaceOrderCommand) -> OrderDto:
        # 0. Захист від подвійного кліку: уже робили цей ключ? Віддай старе.
        seen = self._idempotency.find(cmd.idempotency_key)
        if seen is not None:
            return seen                        # ← нічого не виконуємо вдруге

        # 1..4 — усе, що має закріпитися РАЗОМ, усередині однієї транзакції
        with self._tx.begin():
            cart = self._orders.load_cart(cmd.cart_id)

            # логіка ПРЕДМЕТА: рішення ухвалює домен, не сервіс
            order = cart.checkout()            # кине, якщо кошик порожній

            # оплата — зі своїм ключем: якщо шлюз уже бачив ключ, не спише вдруге
            self._payments.charge(order.total(), cmd.card, cmd.idempotency_key)

            self._orders.save(order)           # запис у сховище
            dto = OrderDto.from_order(order)   # назовні — DTO, не домен
            self._idempotency.remember(cmd.idempotency_key, dto)
        # ↑ вихід із with без винятку = COMMIT. Будь-який виняток усередині →
        #   __exit__ робить ROLLBACK і проштовхує виняток далі — рядки нижче
        #   у цьому разі не виконуються.

        # 5. Лист — ПІСЛЯ коміту й ПОЗА транзакцією: його не можна відкотити.
        #    Впаде пошта — замовлення вже надійно збережене, лист дошлемо окремо.
        self._mailer.send_confirmation(dto.order)
        return dto
