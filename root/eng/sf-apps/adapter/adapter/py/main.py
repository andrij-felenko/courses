from typing import Protocol

# ЦІЛЬ — інтерфейс, який очікує вся наша система
class PaymentGateway(Protocol):
    def charge(self, amount_uah: float, currency: str) -> str: ...   # повертає id платежу

# АДАПТОВАНИЙ — чужий SDK; ми його НЕ міняємо, лише використовуємо
class StripeClient:
    def create_charge(self, *, amount_in_cents: int, currency: str) -> dict:
        # ... справжній виклик до Stripe ...
        return {"id": "ch_123"}

# АДАПТЕР — реалізує ЦІЛЬ, усередині тримає АДАПТОВАНОГО і перекладає
class StripeAdapter:                                    # структурно реалізує PaymentGateway
    def __init__(self, stripe: StripeClient):
        self._stripe = stripe                           # тримаємо чужий об'єкт полем

    def charge(self, amount_uah: float, currency: str) -> str:
        res = self._stripe.create_charge(
            amount_in_cents=round(amount_uah * 100),     # гривні → центи
            currency=currency.lower(),                   # "UAH" → "uah"
        )
        return res["id"]                                 # {"id": ...} → просто id

# Клієнтський код НЕ знає про Stripe — він бачить лише PaymentGateway
def pay(gateway: PaymentGateway) -> None:
    payment_id = gateway.charge(499, "UAH")
    print("оплачено, платіж", payment_id)

pay(StripeAdapter(StripeClient()))
