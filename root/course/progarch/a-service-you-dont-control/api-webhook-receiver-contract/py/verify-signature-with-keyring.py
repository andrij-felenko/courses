import hmac
import hashlib
from typing import List, Optional, Tuple, Dict

def verify_signature_with_keyring(
    raw_body: bytes,
    timestamp: int,
    signatures: List[str],
    keyring: Dict[str, Optional[str]]
) -> Tuple[bool, str]:
    """
    Верифікує підпис вебхука з підтримкою безшовної ротації через кільце ключів.
    Повертає кортеж (is_valid, matched_key).
    """
    signed_payload = f"{timestamp}.".encode('utf-8') + raw_body

    def check_secret(secret: str) -> bool:
        expected_sig = hmac.new(
            secret.encode('utf-8'),
            signed_payload,
            hashlib.sha256
        ).hexdigest()
        for sig in signatures:
            if hmac.compare_digest(sig, expected_sig):
                return True
        return False

    # Перевірка основним ключем
    primary_secret = keyring.get("primary")
    if primary_secret and check_secret(primary_secret):
        return True, "primary"

    # Перевірка вторинним ключем
    secondary_secret = keyring.get("secondary")
    if secondary_secret and check_secret(secondary_secret):
        return True, "secondary"

    return False, "none"
