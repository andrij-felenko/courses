import hmac
import hashlib
import time
import json
from typing import Dict, Any

class WebhookSignatureVerifier:
    def __init__(self, webhook_secret: str, tolerance_seconds: int = 300):
        self._secret = webhook_secret.encode("utf-8")
        self._tolerance = tolerance_seconds

    def verify_and_parse(self, raw_body: bytes, signature_header: str) -> Dict[str, Any]:
        parts = dict(item.strip().split("=", 1) for item in signature_header.split(","))
        timestamp = parts.get("t")
        received_sig = parts.get("v1")

        if not timestamp or not received_sig:
            raise ValueError("Некоректний заголовок Stripe-Signature")

        # 1. Перевірка мітки часу
        event_time = int(timestamp)
        now = int(time.time())
        if abs(now - event_time) > self._tolerance:
            raise ValueError("Мітка часу виходить за допустимі межі (загроза повтору)")

        # 2. Обчислення очікуваного HMAC
        signed_payload = f"{timestamp}.".encode("utf-8") + raw_body
        expected_sig = hmac.new(self._secret, signed_payload, hashlib.sha256).hexdigest()

        # 3. Порівняння за сталий час
        if not hmac.compare_digest(expected_sig, received_sig):
            raise ValueError("Підпис вебхука недійсний")

        return json.loads(raw_body.decode("utf-8"))
