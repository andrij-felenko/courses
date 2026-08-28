# ── Підсистема: чотири служби, кожна робить одне й нічого не знає про сусідів ──
from dataclasses import dataclass


@dataclass
class CartItem:
    sku: str
    qty: int
    price: float

@dataclass
class Cart:
    items: list[CartItem]
    total: float
    email: str

@dataclass
class Card:
    token: str


class OutOfStockError(Exception): ...
class PaymentDeclinedError(Exception): ...


# 1. Склад: резервує товар і вміє резерв ЗНЯТИ (це стане ключем до відкоту)
class InventoryService:
    def reserve(self, items: list[CartItem]) -> str:
        for it in items:
            if not self._has_stock(it.sku, it.qty):
                raise OutOfStockError(f"Немає {it.qty}× {it.sku}")
        return self._hold(items)          # повертає розписку про резерв

    def release(self, reservation_id: str) -> None:
        ...                               # повертає товар на полицю

    def _has_stock(self, sku: str, qty: int) -> bool: ...
    def _hold(self, items: list[CartItem]) -> str: return "res_1"


# 2. Платіж: списує гроші; може відхилити картку
class PaymentGateway:
    def charge(self, card: Card, amount: float) -> "Charge":
        ok = self._call_provider(card.token, amount)     # зовнішній API банку
        if not ok:
            raise PaymentDeclinedError("Картку відхилено")
        return Charge(id="chg_...", amount=amount)

    def refund(self, charge_id: str) -> None:
        ...                               # повертає гроші, теж компенсація

    def _call_provider(self, token: str, amount: float) -> bool: return True


# 3. Сховище замовлень: створює й зберігає запис замовлення
class OrderRepository:
    def create(self, cart: Cart, charge_id: str) -> "Order":
        return Order(id="ord_...", cart=cart, charge_id=charge_id, status="paid")


# 4. Пошта: шле листи; НЕ критична — її збій не має валити замовлення
class EmailService:
    def send_confirmation(self, order: "Order") -> None:
        ...                               # SMTP, може бути недоступний


@dataclass
class Charge:
    id: str
    amount: float

@dataclass
class Order:
    id: str
    cart: Cart
    charge_id: str
    status: str
