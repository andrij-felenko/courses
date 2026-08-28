from dataclasses import dataclass
import time

# подія — плоский факт про те, що вже сталося на боці запису
@dataclass
class OrderPlaced:
    order_id: str
    user_id: str
    total: float

@dataclass
class OrderCancelled:
    order_id: str

class OrderProjection:
    def __init__(self, read: OrderReadStore, users: UserLookup) -> None:
        self._read = read
        self._users = users

    # на КОЖНУ подію оновлюємо denormalized-знімок
    def on(self, ev) -> None:
        if isinstance(ev, OrderPlaced):
            # ім'я клієнта склеюємо ТУТ, ОДИН раз, а не на кожному читанні
            name = self._users.name_of(ev.user_id)
            self._read.upsert(OrderReadModel(
                id=ev.order_id, user_id=ev.user_id, customer_name=name,
                total=ev.total, status="placed", updated_at=time.time()))
        elif isinstance(ev, OrderCancelled):
            cur = self._read.by_id(ev.order_id)
            if cur:
                cur.status = "cancelled"
                cur.updated_at = time.time()
                self._read.upsert(cur)

# команда тепер, окрім запису, оголошує факт — його підхопить проєкція
class PlaceOrderHandler:
    def __init__(self, orders: OrderRepository, bus: EventBus) -> None:
        self._orders = orders
        self._bus = bus
    def handle(self, cmd: PlaceOrder) -> str:
        order = Order.create(cmd.user_id, cmd.items)
        order.reserve_stock()
        self._orders.save(order)
        self._bus.publish(OrderPlaced(order_id=order.id,
                                      user_id=cmd.user_id, total=order.total()))
        return order.id
