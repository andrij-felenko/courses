import hmac
import hashlib
import time
from typing import Optional, List
from flask import Flask, request, jsonify, abort

class WebhookSecurity:
    def __init__(self, primary_secret: str, secondary_secret: Optional[str] = None, tolerance: int = 300):
        self.primary_secret = primary_secret.encode('utf-8')
        self.secondary_secret = secondary_secret.encode('utf-8') if secondary_secret else None
        self.tolerance = tolerance

    def verify(self, raw_body: bytes, signature_header: Optional[str]) -> bool:
        if not raw_body or not signature_header:
            return False

        # Парсинг заголовка: t=1719580800,v1=5257a869e7ec...
        timestamp: int = -1
        signatures: List[str] = []

        for item in signature_header.split(','):
            parts = item.strip().split('=', 1)
            if len(parts) != 2:
                continue
            k, v = parts[0].strip(), parts[1].strip()
            if k == 't':
                try:
                    timestamp = int(v)
                except ValueError:
                    return False
            elif k == 'v1':
                signatures.append(v)

        if timestamp == -1 or not signatures:
            return False

        # 1. Перевірка часового вікна (Time-Window)
        now = int(time.time())
        if abs(now - timestamp) > self.tolerance:
            return False

        # 2. Підготовка підписуваного рядка: timestamp.raw_body
        payload_to_sign = f"{timestamp}.".encode('utf-8') + raw_body

        active_secrets = [self.primary_secret]
        if self.secondary_secret:
            active_secrets.append(self.secondary_secret)

        # 3. Перевірка проти активних секретів (Zero-Downtime Rotation)
        for secret in active_secrets:
            expected_sig = hmac.new(
                secret,
                payload_to_sign,
                hashlib.sha256
            ).hexdigest()

            for sig in signatures:
                # 4. Порівняння сталого часу (Constant-Time Comparison)
                if hmac.compare_digest(sig, expected_sig):
                    return True

        return False

app = Flask(__name__)
verifier = WebhookSecurity(
    primary_secret="whsec_primary_abc123",
    secondary_secret=None,
    tolerance=300
)

@app.route('/api/webhooks', methods=['POST'])
def handle_webhook():
    # Отримання сирих байтів запиту
    raw_body = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    if not verifier.verify(raw_body, sig_header):
        abort(401, description="Invalid signature or expired timestamp")

    # Розбір JSON лише після повної верифікації
    event = request.get_json(force=True)

    # Дедуплікація за event['id'] виконується тут...
    return jsonify({"received": True}), 200
