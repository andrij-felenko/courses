import hmac, hashlib, time

# Перевіряємо ДО розбору тіла. raw_body — точні отримані байти, не переупакований JSON.
def verify(raw_body: bytes, header: str, secret: str) -> bool:
    parts = dict(kv.split("=", 1) for kv in header.split(","))
    t = int(parts.get("t", 0))
    if not t or abs(time.time() - t) > 300:           # застарілий підпис → повтор, геть
        return False
    signed = f"{t}.".encode() + raw_body
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, parts.get("v1", ""))    # звірка за СТАЛИЙ час
