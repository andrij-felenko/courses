import urllib.parse
import urllib.request
import json
from typing import Dict

class SubscriptionSetupService:
    def __init__(self, api_key: str, base_url: str = "https://api.stripe.com/v1"):
        self._api_key = api_key
        self._base_url = base_url

    def attach_payment_method(self, customer_id: str, payment_method_id: str) -> Dict[str, str]:
        payload = urllib.parse.urlencode({
            "customer": customer_id,
            "payment_method": payment_method_id,
            "usage": "off_session",
            "confirm": "true"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self._base_url}/setup_intents",
            data=payload,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
                "Idempotency-Key": f"setup_{customer_id}_{payment_method_id}"
            },
            method="POST"
        )

        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "setup_intent_id": data["id"],
                "status": data["status"]
            }
