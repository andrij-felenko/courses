import secrets
import base64
import urllib.parse

def generate_base32_secret(byte_length: int = 20) -> str:
    raw_bytes = secrets.token_bytes(byte_length)
    return base64.b32encode(raw_bytes).decode("ascii").rstrip("=")

def decode_base32(secret: str) -> bytes:
    clean = secret.replace(" ", "").replace("-", "").upper()
    padding = (8 - len(clean) % 8) % 8
    clean += "=" * padding
    return base64.b32decode(clean, casefold=True)

def build_totp_uri(issuer: str, account_name: str, secret_base32: str) -> str:
    label = f"{issuer}:{account_name}"
    params = {
        "secret": secret_base32,
        "issuer": issuer,
        "algorithm": "SHA1",
        "digits": 6,
        "period": 30,
    }
    return f"otpauth://totp/{urllib.parse.quote(label)}?{urllib.parse.urlencode(params)}"
