import hmac
import hashlib
import time
from typing import Tuple, Optional

def verify_webhook_signature(
    raw_body: bytes,
    signature_header: str,
    secret: str,
    tolerance_seconds: int = 300
) -> Tuple[bool, Optional[str]]:
    timestamp: Optional[int] = None
    signatures = []

    for item in signature_header.split(','):
        if not item or '=' not in item:
            continue
        key, value = item.split('=', 1)
        if key == 't':
            try:
                timestamp = int(value)
            except ValueError:
                return False, 'INVALID_TIMESTAMP_FORMAT'
        elif key == 'v1':
            signatures.append(value)

    if timestamp is None or not signatures:
        return False, 'MISSING_SIGNATURE_OR_TIMESTAMP'

    now = int(time.time())
    if abs(now - timestamp) > tolerance_seconds:
        return False, 'TIMESTAMP_OUT_OF_TOLERANCE'

    signed_payload = f"{timestamp}.".encode('utf-8') + raw_body
    expected_sig = hmac.new(
        secret.encode('utf-8'),
        signed_payload,
        hashlib.sha256
    ).hexdigest()

    for sig in signatures:
        if hmac.compare_digest(sig, expected_sig):
            return True, None

    return False, 'INVALID_SIGNATURE'
