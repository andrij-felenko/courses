from fractions import Fraction
from math import floor

def best_rational(x, Q):
    """Найближчий до x дріб p/q зі знаменником 1 ≤ q ≤ Q (Q ≥ 1).
    x — int, float або Fraction; повертає Fraction.
    Те саме, що stdlib Fraction(x).limit_denominator(Q), лише з відкритим нутром."""
    target = x if isinstance(x, Fraction) else Fraction(x)
    a = floor(target)
    pp, qq = 1, 0                    # підхідний «−1»:  1/0
    p,  q  = a, 1                    # підхідний [a₀]:  a/1
    frac = target - a

    while frac != 0:
        y = 1 / frac                 # перевертаємо хвіст — це крок Евкліда
        a = floor(y)
        p2, q2 = a*p + pp, a*q + qq  # наступний підхідний за рекурентою
        if q2 > Q:                   # він вискочить за стелю — спиняємось
            break
        pp, qq, p, q = p, q, p2, q2  # зсуваємо вікно
        frac = y - a

    best = Fraction(p, q)            # остання підхідна, що влізла
    if frac != 0:                    # ланцюг не скінчився → є напівпідхідні
        t = (Q - qq) // q            # найвищий щабель: qq + t·q ≤ Q
        if t > 0:
            semi = Fraction(pp + t*p, qq + t*q)
            if abs(target - semi) < abs(target - best):
                best = semi          # напівпідхідний виявився ближчим
    return best
