def verify_naive_multi(token: str, key: bytes) -> dict:
    """key — це те, що сервіс тримає для перевірки. Для RS256 — ВІДКРИТИЙ ключ (PEM)."""
    header_b64, payload_b64, sig_b64 = token.split(".")
    alg = json.loads(b64url_decode(header_b64)).get("alg")   # ← знову вірить токену
    signing_input = (header_b64 + "." + payload_b64).encode()
    sig = b64url_decode(sig_b64)
    if alg == "RS256":
        rsa_verify(signing_input, sig, key)                  # key як ВІДКРИТИЙ ключ
    elif alg == "HS256":
        if not hmac.compare_digest(hs256(signing_input, key), sig):
            raise InvalidToken("підпис не збігається")       # key як HMAC-СЕКРЕТ (!)
    else:
        raise InvalidToken("невідомий alg")
    return json.loads(b64url_decode(payload_b64))
