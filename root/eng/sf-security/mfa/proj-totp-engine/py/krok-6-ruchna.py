def resynchronize_clock(
    secret_base32: str,
    code1: str,
    code2: str,
    current_timestamp: int,
    max_drift_steps: int = 50,
    time_step: int = 30
) -> tuple[bool, int | None]:
    secret_bytes = decode_base32(secret_base32)
    current_step = current_timestamp // time_step
    c1, c2 = code1.strip(), code2.strip()

    for drift in range(-max_drift_steps, max_drift_steps + 1):
        exp1 = generate_totp_code(secret_bytes, (current_step + drift) * time_step, time_step)
        exp2 = generate_totp_code(secret_bytes, (current_step + drift + 1) * time_step, time_step)

        if hmac.compare_digest(c1, exp1) and hmac.compare_digest(c2, exp2):
            return True, drift

    return False, None
