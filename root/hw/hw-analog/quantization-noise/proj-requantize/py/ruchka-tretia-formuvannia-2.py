_MASK32 = 0xFFFFFFFF
_rng_state = 0x1234567
ns_err = 0

def xorshift32() -> int:
    global _rng_state
    s = _rng_state
    s ^= (s << 13) & _MASK32; s ^= s >> 17; s ^= (s << 5) & _MASK32
    _rng_state = s
    return s

# Повний перекодувач: округлення + TPDF-дизер + формування шуму 1-го порядку.
def requantize_full(x24: int, S: int) -> int:
    global ns_err
    q    = 1 << S
    half = 1 << (S - 1)

    # TPDF-дизер розмахом ±q (сума двох рівномірних)
    d = (xorshift32() % q) + (xorshift32() % q) - q

    # формування: додаємо і дизер, і накопичену похибку
    u = x24 + d + ns_err
    y = (u + half) >> S

    # похибку рахуємо БЕЗ дизера — переносити треба лише похибку округлення,
    # не наш власний доданий шум (інакше формувач боровся б із дизером)
    u_clean = x24 + ns_err
    ns_err = u_clean - (y << S)
    return y
