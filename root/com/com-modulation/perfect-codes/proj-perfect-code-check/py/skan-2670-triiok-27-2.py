def is_prime_power(q):
    """Чи існує поле з q символів: q = pᵐ для простого p.
    Без поля немає ні лінійного коду, ні побудови Геммінга."""
    p = 2
    while p * p <= q:
        if q % p == 0:
            while q % p == 0:
                q //= p
            return q == 1
        p += 1
    return q >= 2                       # q лишилося простим


def classify(q, n, t, M):
    """Чи це відома родина — чи безіменний кандидат?"""
    names = []
    if M == 2 and q == 2 and n == 2 * t + 1:
        names.append("повторення")
    if t == 1:
        m, unit = 1, 0
        while unit < n:
            unit = (q ** m - 1) // (q - 1)
            m += 1
        if unit == n:
            # довжина Геммінга — але код існує, лише якщо є поле GF(q)
            names.append("Геммінг" if is_prime_power(q)
                         else "довжина Геммінга, але GF(%d) НЕ ІСНУЄ" % q)
    if (q, n, t) == (2, 23, 3):
        names.append("Голей двійковий")
    if (q, n, t) == (3, 11, 2):
        names.append("Голей трійковий")
    return " = ".join(names) if names else "??? БЕЗІМЕННИЙ КАНДИДАТ"
