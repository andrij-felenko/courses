# Ядро прибите до конкретного HTTP-клієнта: стрілка «важливе → дрібне»
from stripe_http_client import StripeHttpClient  # деталь протекла у модуль із логікою

class PaymentService:
    def __init__(self):
        self._http = StripeHttpClient()           # ядро ТРИМАЄ конкретну деталь

    def charge(self, order):
        body = build_stripe_json(order)           # логіка знає формат саме Stripe
        self._http.post("https://api.stripe.com/charges", body)
