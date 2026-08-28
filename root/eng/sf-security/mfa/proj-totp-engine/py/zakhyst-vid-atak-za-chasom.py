import hmac

def verify_totp_code(
    secret_base32: str,
    user_input_code: str,
    current_timestamp: int,
    last_verified_step: int = 0,
    window: int = 1,
    time_step: int = 30
) -> tuple[bool, int | None]:
    clean_code = user_input_code.strip()
    if len(clean_code) != 6 or not clean_code.isdigit():
        return False, None

    secret_bytes = decode_base32(secret_base32)
    current_step = current_timestamp // time_step

    for offset in range(-window, window + 1):
        step = current_step + offset
        
        # Anti-Replay захист
        if step <= last_verified_step:
            continue

        expected = generate_totp_code(secret_bytes, step * time_step, time_step)
        
        # hmac.compare_digest захищає від Timing Attack
        if hmac.compare_digest(clean_code, expected):
            return True, step

    return False, None
