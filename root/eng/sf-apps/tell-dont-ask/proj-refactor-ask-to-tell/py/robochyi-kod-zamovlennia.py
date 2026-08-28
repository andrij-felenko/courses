from enum import Enum


class Status(Enum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


class OrderError(Exception):
    """Недозволений перехід стану замовлення."""


class Order:
    def __init__(self, order_id):
        self._id = order_id
        self._status = Status.NEW

    # --- КОМАНДИ: кожна стереже свій інваріант ---

    def pay(self):
        self._require(self._status is Status.NEW, "оплатити можна лише нове")
        self._status = Status.PAID

    def ship(self):
        self._require(self._status is Status.PAID, "відвантажити можна лише оплачене")
        self._status = Status.SHIPPED

    def cancel(self):
        self._require(self._status not in (Status.SHIPPED, Status.CANCELLED),
                      "скасувати вже не можна")
        self._status = Status.CANCELLED

    # --- ЗАПИТ: лише читає, нічого не міняє ---
    @property
    def status(self):
        return self._status

    @property
    def id(self):
        return self._id

    # спільний вартовий: не виконуй перехід, якщо умова хибна
    def _require(self, ok, why):
        if not ok:
            raise OrderError(f"{why} (зараз {self._status.value})")
