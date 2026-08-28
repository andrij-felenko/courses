class StripeError(Exception):
    def __init__(self, code: str): self.code = code

class PaymentError(Exception):                        # ТВІЙ словник помилок
    pass

# Найдрібніших одиниць в одиниці валюти — за ISO 4217. Типово 100; винятки — окремо.
MINOR = {"JPY": 1, "KRW": 1, "BHD": 1000, "KWD": 1000, "OMR": 1000}

def to_minor(amount: float, cur: str) -> int:
    return round(amount * MINOR.get(cur, 100))        # не «×100», а за валютою

class StripeAdapter:                                  # структурно реалізує PaymentGateway
    def __init__(self, stripe: "StripeClient"):
        self._stripe = stripe                         # адаптований — ПОЛЕМ (композиція)

    def charge(self, amount: float, currency: str) -> str:
        try:
            res = self._stripe.create_charge(
                amount_in_minor=to_minor(amount, currency),  # f_in: одиниці за валютою
                currency=currency.lower(),                   # f_in: "UAH" → "uah"
            )
            return res["id"]                          # f_out: {"id": ...} → id
        except StripeError as e:                      # f_out і для ПОМИЛОК:
            raise PaymentError(f"платіж відхилено: {e.code}")  # чужа помилка → наша
