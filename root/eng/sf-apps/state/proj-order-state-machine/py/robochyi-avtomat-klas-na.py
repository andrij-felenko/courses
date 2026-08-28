from __future__ import annotations


# ── Спільний інтерфейс стану ──────────────────────────────────────────────
# Кожен стан мусить уміти відповісти на кожну з чотирьох подій.
# База дає безпечні типові відповіді, а конкретні стани перекривають лише те,
# що для них має сенс — так «забута клітина» стає явним рішенням, а не дірою.
class IllegalTransition(Exception):
    pass


class OrderState:
    name: str = "?"

    # Типова відповідь на подію, яку стан не описав, — заборона.
    def pay(self, order: "Order") -> None:    self._reject("оплатити")
    def ship(self, order: "Order") -> None:   self._reject("відправити")
    def cancel(self, order: "Order") -> None: self._reject("скасувати")
    def refund(self, order: "Order") -> None: self._reject("повернути гроші")

    def _reject(self, action: str) -> None:
        raise IllegalTransition(
            f"не можна {action}: замовлення у стані «{self.name}»")

    # Тихий ігнор — окремий, СВІДОМИЙ вихід, а не мовчазне «нічого не сталось».
    def _ignore(self, order: "Order", note: str) -> None:
        order.log(f"ігнор: {note} (стан «{self.name}»)")


# ── Контекст: тримає поточний стан і делегує йому все ──────────────────────
class Order:
    def __init__(self, id: str) -> None:
        self.id = id
        self._state: OrderState = States.NEW    # спільний екземпляр, див. нижче
        self.logbook: list[str] = []

    # Публічний API — жодного if за станом, самі делегації:
    def pay(self) -> None:    self._state.pay(self)
    def ship(self) -> None:   self._state.ship(self)
    def cancel(self) -> None: self._state.cancel(self)
    def refund(self) -> None: self._state.refund(self)

    # Перехід — єдина точка, де стан змінюється; звідси зручно логувати маршрут.
    def transition_to(self, nxt: OrderState) -> None:
        self.log(f"{self._state.name} → {nxt.name}")
        self._state = nxt

    @property
    def state_name(self) -> str:
        return self._state.name

    def log(self, msg: str) -> None:
        self.logbook.append(msg)


# ── Конкретні стани: кожен — один рядок таблиці ───────────────────────────
class NewState(OrderState):
    name = "New"
    def pay(self, order: "Order") -> None:    # провести оплату
        order.transition_to(States.PAID)
    def cancel(self, order: "Order") -> None:
        order.transition_to(States.CANCELLED)
    # ship, refund не описані → база кине заборону. Клітини (New,ship)/(New,refund).


class PaidState(OrderState):
    name = "Paid"
    def ship(self, order: "Order") -> None:   # відвантажити
        order.transition_to(States.SHIPPED)
    def cancel(self, order: "Order") -> None:  # скасування після оплати = повернення
        order.transition_to(States.REFUNDED)
    def refund(self, order: "Order") -> None:
        order.transition_to(States.REFUNDED)


class ShippedState(OrderState):
    name = "Shipped"
    def ship(self, order: "Order") -> None:    # (Shipped,ship) = ігнор
        self._ignore(order, "повторне відправлення")
    def refund(self, order: "Order") -> None:
        order.transition_to(States.REFUNDED)
    # pay, cancel → база кине заборону: платити й скасовувати відправлене вже пізно.


# Кінцеві стани: будь-яка дія або заборонена, або ігнорується — шляху далі немає.
class CancelledState(OrderState):
    name = "Cancelled"
    def cancel(self, order: "Order") -> None:  # (Cancelled,cancel) = ігнор
        self._ignore(order, "повторне скасування")


class RefundedState(OrderState):
    name = "Refunded"
    def refund(self, order: "Order") -> None:  # (Refunded,refund) = ігнор
        self._ignore(order, "повторне повернення")


# ── Пул спільних екземплярів: по ОДНОМУ на стан на всю програму ───────────
class States:
    NEW = NewState()
    PAID = PaidState()
    SHIPPED = ShippedState()
    CANCELLED = CancelledState()
    REFUNDED = RefundedState()
