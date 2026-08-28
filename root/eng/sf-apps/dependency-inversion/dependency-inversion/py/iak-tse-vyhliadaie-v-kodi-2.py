from abc import ABC, abstractmethod

# Абстракція говорить БІЗНЕС-мовою: «списати кошти», а не «зробити POST»
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: Money, card: Card) -> ChargeResult: ...

# Ядро залежить ЛИШЕ від обіцянки — і не знає, хто її виконає
class PaymentService:
    def __init__(self, gateway: PaymentGateway):
        self._gateway = gateway         # посилання на абстракцію

    def charge(self, order):
        r = self._gateway.charge(order.total(), order.card())
        if not r.ok:
            raise PaymentFailed(r.reason)
