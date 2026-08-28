import urllib.parse
import urllib.request
import json
from typing import Optional, Dict

class PaymentRefundService:
    def __init__(self, api_key: str, base_url: str = "https://api.stripe.com/v1"):
        self._api_key = api_key
        self._base_url = base_url

    def process_refund(self, payment_intent_id: str, amount_cents: Optional[int] = None) -> Dict[str, str]:
        payload_dict = {"payment_intent": payment_intent_id}
        if amount_cents:
            payload_dict["amount"] = str(amount_cents)

        payload = urllib.parse.urlencode(payload_dict).encode("utf-8")
        idempotency_key = f"refund_{payment_intent_id}_{amount_cents or 'full'}"

        req = urllib.request.Request(
            f"{self._base_url}/refunds",
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Idempotency-Key": idempotency_key,
            },
            method="POST",
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "refund_id": data["id"],
                "status": data["status"]
            }
