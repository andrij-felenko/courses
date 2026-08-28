import base64, hashlib, hmac, json, time

# ── base64url без службових '=' (JWT їх не тримає) ────────────────────────
def b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

def b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)          # добити довжину до кратної чотирьом
    return base64.urlsafe_b64decode(s + pad)

def hs256(msg: bytes, secret: bytes) -> bytes:
    return hmac.new(secret, msg, hashlib.sha256).digest()

class InvalidToken(Exception):
    pass

# ── ВИДАЧА ────────────────────────────────────────────────────────────────
def issue(claims: dict, secret: bytes, ttl: int = 900) -> str:
    now = int(time.time())
    header  = {"alg": "HS256", "typ": "JWT"}
    payload = {**claims, "iat": now, "nbf": now, "exp": now + ttl}
    signing_input = (
        b64url_encode(json.dumps(header,  separators=(",", ":")).encode())
        + "." +
        b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    )
    sig = b64url_encode(hs256(signing_input.encode(), secret))
    return signing_input + "." + sig

# ── ПЕРЕВІРКА ──────────────────────────────────────────────────────────────
def verify(token: str, secret: bytes, leeway: int = 30) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise InvalidToken("не три частини")
    header_b64, payload_b64, sig_b64 = parts

    # (1) АЛГОРИТМ ПРИБИТО: очікуваний — НАШ, а не той, що в токені
    if json.loads(b64url_decode(header_b64)).get("alg") != "HS256":
        raise InvalidToken("несподіваний alg")

    # (2) ПОРІВНЯННЯ СТАЛОГО ЧАСУ на сирих байтах підпису
    expected = hs256((header_b64 + "." + payload_b64).encode(), secret)
    if not hmac.compare_digest(expected, b64url_decode(sig_b64)):
        raise InvalidToken("підпис не збігається")

    # (3) ЧАСОВІ ТВЕРДЖЕННЯ (з невеликим допуском на розбіжність годинників)
    payload = json.loads(b64url_decode(payload_b64))
    now = int(time.time())
    if "exp" in payload and now > payload["exp"] + leeway:
        raise InvalidToken("протермінований")
    if "nbf" in payload and now + leeway < payload["nbf"]:
        raise InvalidToken("ще не набув чинності")
    if "iat" in payload and now + leeway < payload["iat"]:
        raise InvalidToken("виданий у майбутньому")
    return payload
