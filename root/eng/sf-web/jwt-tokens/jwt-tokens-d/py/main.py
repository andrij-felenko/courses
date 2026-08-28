import hmac, hashlib, base64, json, time

def b64url_decode(s: str) -> bytes:                 # доповнити паддинг і розкодувати
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def verify(token: str, secret: bytes) -> dict:
    header_b64, payload_b64, sig_b64 = token.split(".")
    header = json.loads(b64url_decode(header_b64))
    if header.get("alg") != "HS256":                # 1. прибити алгоритм цвяхом
        raise ValueError("несподіваний alg")
    msg = f"{header_b64}.{payload_b64}".encode()
    expected = base64.urlsafe_b64encode(
        hmac.new(secret, msg, hashlib.sha256).digest()).rstrip(b"=").decode()
    if not hmac.compare_digest(expected, sig_b64):  # 2. звірка сталого часу
        raise ValueError("підпис не збігається")
    payload = json.loads(b64url_decode(payload_b64))
    if payload["exp"] < time.time():                # 3. чи не протух
        raise ValueError("токен протермінований")
    return payload
