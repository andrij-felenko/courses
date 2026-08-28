import urllib.parse
import urllib.request
import json
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CreatePaymentParams:
    order_id: str
    amount_cents: int
    currency: str
    payment_method_id: str
    customer_id: str

@dataclass(frozen=True)
class PaymentIntentResult:
    intent_id: str
    status: str
    client_secret: Optional[str]
    requires_action: bool

class PaymentGatewayService:
    def __init__(self, api_key: str, base_url: str = "https://api.stripe.com/v1"):
        self._api_key = api_key
        self._base_url = base_url

    def process_checkout(self, params: CreatePaymentParams) -> PaymentIntentResult:
        # Формування детермінованого ключа ідемпотентності
        idempotency_key = f"checkout_{params.order_id}_{params.amount_cents}"

        form_data = urllib.parse.urlencode({
            "amount": str(params.amount_cents),
            "currency": params.currency.lower(),
            "payment_method": params.payment_method_id,
            "confirm": "true",
            "metadata[order_id]": params.order_id,
            "metadata[customer_id]": params.customer_id,
            "capture_method": "automatic",
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self._base_url}/payment_intents",
            data=form_data,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Idempotency-Key": idempotency_key,
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                status = data.get("status", "unknown")
                return PaymentIntentResult(
                    intent_id=data["id"],
                    status=status,
                    client_secret=data.get("client_secret"),
                    requires_action=(status == "requires_action"),
                )
        except urllib.error.HTTPError as err:
            err_data = json.loads(err.read().decode("utf-8"))
            msg = err_data.get("error", {}).get("message", "Помилка платіжного шлюзу")
            raise RuntimeError(f"Платіж відхилено: {msg}") from err
