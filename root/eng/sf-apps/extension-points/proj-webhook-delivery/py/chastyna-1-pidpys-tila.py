import hmac, hashlib, json, time
from dataclasses import dataclass

@dataclass
class SignedDelivery:
    body: str                       # ті САМІ байти, що підуть по дроту
    headers: dict[str, str]

def sign_webhook(payload: dict, secret: str) -> SignedDelivery:
    body = json.dumps(payload, separators=(",", ":"))   # серіалізуємо РАЗ
    timestamp = int(time.time())
    signed_string = f"{timestamp}.{body}"               # час . тіло

    signature = hmac.new(
        secret.encode(), signed_string.encode(), hashlib.sha256
    ).hexdigest()                                        # підписуємо саме цей рядок

    return SignedDelivery(
        body=body,                                       # і надсилаємо ЙОГО, не пере-серіалізуємо
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Timestamp": str(timestamp),
            "X-Webhook-Signature": f"v1={signature}",    # версіонуємо схему підпису
        },
    )

# Бік ОДЕРЖУВАЧА: сталим-у-часі порівнянням + відкидаємо стару мітку.
def verify_webhook(body: str, header_ts: str, header_sig: str,
                   secret: str, tolerance_sec: int = 300) -> bool:
    if abs(time.time() - int(header_ts)) > tolerance_sec:
        return False                                     # задавнена звістка — геть

    expected = hmac.new(
        secret.encode(), f"{header_ts}.{body}".encode(), hashlib.sha256
    ).hexdigest()
    got = header_sig.removeprefix("v1=")
    return hmac.compare_digest(expected, got)            # час порівняння НЕ видає підпис
