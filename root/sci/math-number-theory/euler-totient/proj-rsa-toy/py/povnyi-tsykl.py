from math import gcd

def keygen(bits: int = 1024):
    """Повертає ((n, e), (n, d)) — відкритий і таємний ключі."""
    e = 65537
    while True:
        p, q = gen_prime(bits), gen_prime(bits)
        if p == q:                     # астрономічно малоймовірно, та перевірмо
            continue
        phi = (p - 1) * (q - 1)
        if gcd(e, phi) != 1:           # без цього оберненого не існує
            continue                   # рідко, але буває — тоді інша пара
        return (p * q, e), (p * q, inverse(e, phi))
        # p, q і phi більше не потрібні — і саме тому їх тут не повертають

def encrypt(m: int, pub) -> int:
    n, e = pub
    if not 0 <= m < n:
        raise ValueError("повідомлення мусить бути числом від 0 до n−1")
    return powmod(m, e, n)

def decrypt(c: int, priv) -> int:
    n, d = priv
    return powmod(c, d, n)
