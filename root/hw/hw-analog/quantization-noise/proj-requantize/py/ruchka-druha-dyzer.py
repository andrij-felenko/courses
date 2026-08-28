# Дешевий швидкий генератор псевдовипадкових (xorshift32).
# Тримає власний стан; на кожен виклик — новий 32-розрядний кидок.
_MASK32 = 0xFFFFFFFF
_rng_state = 0x1234567

def xorshift32() -> int:
    global _rng_state
    s = _rng_state
    s ^= (s << 13) & _MASK32
    s ^= s >> 17
    s ^= (s << 5) & _MASK32
    _rng_state = s
    return s

# TPDF-дизер розмахом ±q (тобто повний розмах 2q) для скорочення на S розрядів.
# q = 1<<S — крок нової сітки в одиницях старого слова.
def tpdf_dither(S: int) -> int:
    q = 1 << S
    # два незалежні рівномірні на [0, q) — їхня сума трикутна на [0, 2q)
    r1 = xorshift32() % q
    r2 = xorshift32() % q
    # зсунути так, щоб центр був у нулі: розмах стає [−q, +q)
    return r1 + r2 - q

def requantize_dither(x24: int, S: int) -> int:
    d = tpdf_dither(S)          # ±q, трикутний
    half = 1 << (S - 1)         # пів-кроку для округлення
    return (x24 + d + half) >> S   # сигнал + дизер + ½q, тоді зсув
