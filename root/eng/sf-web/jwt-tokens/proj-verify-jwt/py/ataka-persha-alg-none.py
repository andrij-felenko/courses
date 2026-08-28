def verify_naive(token: str, secret: bytes) -> dict:
    header_b64, payload_b64, sig_b64 = token.split(".")
    alg = json.loads(b64url_decode(header_b64)).get("alg")   # ← вірить токену
    if alg == "none":
        return json.loads(b64url_decode(payload_b64))        # ← ЖОДНОЇ перевірки
    if alg == "HS256":
        expected = hs256((header_b64 + "." + payload_b64).encode(), secret)
        if not hmac.compare_digest(expected, b64url_decode(sig_b64)):
            raise InvalidToken("підпис не збігається")
        return json.loads(b64url_decode(payload_b64))
    raise InvalidToken("невідомий alg")
