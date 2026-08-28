import time
import json
import base64
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

def base64url_decode(payload_b64: str) -> bytes:
    """Розкодування рядка Base64URL у сирі байти з відновленням паддингу."""
    rem = len(payload_b64) % 4
    if rem > 0:
        payload_b64 += '=' * (4 - rem)
    return base64.urlsafe_b64decode(payload_b64.encode('ascii'))

def rsa_public_key_from_jwk(jwk: dict) -> RSAPublicKey:
    """Побудова об'єкта відкритого ключа RSA з параметрів JWK n та e."""
    n_bytes = base64url_decode(jwk['n'])
    e_bytes = base64url_decode(jwk['e'])
    n_int = int.from_bytes(n_bytes, byteorder='big')
    e_int = int.from_bytes(e_bytes, byteorder='big')
    public_numbers = rsa.RSAPublicNumbers(e=e_int, n=n_int)
    return public_numbers.public_key()

def verify_id_token_claims(claims: dict, expected_iss: str,
                           expected_client_id: str,
                           expected_nonce: str,
                           clock_skew_sec: int = 60) -> bool:
    """Перевірка обов'язкових тверджень ID-токена за специфікацією OIDC Core."""
    now = int(time.time())

    # 1. Перевірка видавця
    if claims.get('iss') != expected_iss:
        return False

    # 2. Перевірка аудиторії (може бути рядком або масивом)
    aud = claims.get('aud')
    if isinstance(aud, list):
        if expected_client_id not in aud:
            return False
    elif aud != expected_client_id:
        return False

    # 3. Перевірка nonce сталим часом
    token_nonce = claims.get('nonce', '')
    if not hmac.compare_digest(token_nonce, expected_nonce):
        return False

    # 4. Перевірка строку дії
    exp = claims.get('exp', 0)
    if now >= (exp + clock_skew_sec):
        return False

    # 5. Перевірка часу видачі
    iat = claims.get('iat', 0)
    if now < (iat - clock_skew_sec):
        return False

    return True

def verify_jwt_signature_rs256(raw_jwt: str, public_key: RSAPublicKey) -> bool:
    """Криптографічна перевірка підпису RS256 за відкритим ключем RSA."""
    parts = raw_jwt.split('.')
    if len(parts) != 3:
        return False

    signing_input = f"{parts[0]}.{parts[1]}".encode('ascii')
    signature = base64url_decode(parts[2])

    try:
        public_key.verify(
            signature,
            signing_input,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
