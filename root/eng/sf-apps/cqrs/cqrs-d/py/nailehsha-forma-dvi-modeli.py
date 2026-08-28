from dataclasses import dataclass

# КОМАНДА — намір змінити стан. Проста структура: що зробити й з чим.
@dataclass
class PlaceOrder:
    user_id: str
    items: list[LineItem]

class PlaceOrderHandler:
    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders

    def handle(self, cmd: PlaceOrder) -> None:
        # доменна модель із правилами: конструктор боронить інваріанти
        order = Order.create(cmd.user_id, cmd.items)
        order.reserve_stock()       # кине помилку, якщо товару бракує
        self._orders.save(order)    # зберігаємо нормалізовано
