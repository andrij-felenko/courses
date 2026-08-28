import hmac
import hashlib
import struct

def generate_totp_code(
    secret_bytes: bytes,
    timestamp_seconds: int,
    time_step: int = 30,
    digits: int = 6
) -> str:
    counter = timestamp_seconds // time_step
    # 8 байтів Big-Endian: '>Q' — unsigned long long 64 біти
    counter_bytes = struct.pack(">Q", counter)

    digest = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()
    
    # Dynamic Truncation
    offset = digest[-1] & 0x0F
    binary_code = struct.unpack(">I", digest[offset:offset+4])[0] & 0x7FFFFFFF
    
    otp = binary_code % (10 ** digits)
    return str(otp).zfill(digits)
