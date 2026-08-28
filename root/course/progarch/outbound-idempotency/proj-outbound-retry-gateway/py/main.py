# Python: Надійний вихідний HTTP-клієнт з детермінованим Idempotency-Key
import time
import hashlib
import requests

class OutboundGateway:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def make_deterministic_key(self, entity_id: str, action: str) -> str:
        raw = f"{entity_id}:{action}".encode("utf-8")
        return f"idemp_{hashlib.sha256(raw).hexdigest()[:24]}"

    def post_charge(self, order_id: str, amount: float, max_retries: int = 3) -> dict:
        key = self.make_deterministic_key(order_id, "charge")
        payload = {"order_id": order_id, "amount": amount}
        headers = {"Idempotency-Key": key, "Content-Type": "application/json"}

        backoff = 1.0
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/v1/charges",
                    json=payload,
                    headers=headers,
                    timeout=5.0
                )
                if response.status_code in (200, 201):
                    return response.json()
                elif response.status_code in (409, 502, 503, 504):
                    time.sleep(backoff)
                    backoff *= 2.0
                    continue
                else:
                    response.raise_for_status()
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                if attempt == max_retries:
                    raise
                time.sleep(backoff)
                backoff *= 2.0

        raise TimeoutError(f"Exhausted retries for order {order_id}")
