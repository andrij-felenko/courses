from dataclasses import dataclass

# --- БІК КОМАНД: сама поведінка, жодного коду під екран ---
@dataclass
class PlaceOrder:
    user_id: str
    items: list[LineItem]

@dataclass
class CancelOrder:
    order_id: str

class PlaceOrderHandler:
    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders
    def handle(self, cmd: PlaceOrder) -> str:
        order = Order.create(cmd.user_id, cmd.items)
        order.reserve_stock()
        self._orders.save(order)       # репозиторій пише нормалізовано
        return order.id

class CancelOrderHandler:
    def __init__(self, orders: OrderRepository) -> None:
        self._orders = orders
    def handle(self, cmd: CancelOrder) -> None:
        order = self._orders.by_id(cmd.order_id)  # агрегат вантажимо, бо ТУТ це правда:
        order.cancel()                            # правило справді читає стан замовлення
        self._orders.save(order)
