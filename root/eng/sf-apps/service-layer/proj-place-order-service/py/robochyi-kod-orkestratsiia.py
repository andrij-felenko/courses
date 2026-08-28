from typing import Protocol, Optional

# Порти — усе, з чим сервіс говорить, є абстракцією (DIP).
# Реалізації (Postgres, Stripe, SMTP) живуть деінде й підставляються ззовні.
class OrderRepository(Protocol):
    def load_cart(self, cart_id: CartId) -> "Cart": ...
    def save(self, order: "Order") -> None: ...

class PaymentGateway(Protocol):
    # key — ключ ідемпотентності: шлюз сам не спише двічі за тим самим ключем
    def charge(self, amount: Money, card: CardToken, key: str) -> PaymentId: ...

class Mailer(Protocol):
    def send_confirmation(self, order: "Order") -> None: ...

# Журнал уже виконаних операцій — серце захисту від подвійного кліку
class IdempotencyStore(Protocol):
    def find(self, key: str) -> Optional["OrderDto"]: ...   # уже робили цей ключ?
    def remember(self, key: str, result: "OrderDto") -> None: ...

class TransactionManager(Protocol):
    def begin(self): ...        # контекст-менеджер: BEGIN … COMMIT / ROLLBACK


# Вхідний намір і вихідна виписка — плаский DTO на межі, не голий домен
@dataclass(frozen=True)
class PlaceOrderCommand:
    cart_id: CartId
    card: CardToken
    idempotency_key: str        # згенерований КЛІЄНТОМ, не сервером
