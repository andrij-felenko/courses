from fractions import Fraction

class Polynomial:
    def __init__(self, coeffs):
        # coeffs[i] відповідає степеню x^i
        self.coeffs = [Fraction(c) for c in coeffs]
        self._normalize()

    def _normalize(self):
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()
        if not self.coeffs:
            self.coeffs = [Fraction(0)]

    def deg(self):
        if len(self.coeffs) == 1 and self.coeffs[0] == 0:
            return -1
        return len(self.coeffs) - 1

    def is_zero(self):
        return self.deg() == -1

    def lead(self):
        return self.coeffs[-1]

    def __add__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        c1 = self.coeffs + [Fraction(0)] * (n - len(self.coeffs))
        c2 = other.coeffs + [Fraction(0)] * (n - len(other.coeffs))
        return Polynomial([a + b for a, b in zip(c1, c2)])

    def __sub__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        c1 = self.coeffs + [Fraction(0)] * (n - len(self.coeffs))
        c2 = other.coeffs + [Fraction(0)] * (n - len(other.coeffs))
        return Polynomial([a - b for a, b in zip(c1, c2)])

    def __mul__(self, other):
        if isinstance(other, (int, Fraction)):
            return Polynomial([c * Fraction(other) for c in self.coeffs])
        if self.is_zero() or other.is_zero():
            return Polynomial([0])
        res = [Fraction(0)] * (len(self.coeffs) + len(other.coeffs) - 1)
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                res[i + j] += a * b
        return Polynomial(res)


def div_rem(f: Polynomial, g: Polynomial):
    if g.is_zero():
        raise ZeroDivisionError("Ділення на нульовий многочлен")
    q = Polynomial([0])
    cur = Polynomial(f.coeffs)
    while not cur.is_zero() and cur.deg() >= g.deg():
        shift = cur.deg() - g.deg()
        factor = cur.lead() / g.lead()
        monom_coeffs = [Fraction(0)] * (shift + 1)
        monom_coeffs[shift] = factor
        monom = Polynomial(monom_coeffs)
        q = q + monom
        cur = cur - (monom * g)
    return q, cur


def ext_gcd(a: Polynomial, b: Polynomial):
    u0, u1 = Polynomial([1]), Polynomial([0])
    v0, v1 = Polynomial([0]), Polynomial([1])
    while not b.is_zero():
        q, r = div_rem(a, b)
        a, b = b, r
        u0, u1 = u1, u0 - (q * u1)
        v0, v1 = v1, v0 - (q * v1)

    lead_c = a.lead()
    inv_c = Fraction(1, 1) / lead_c
    return a * inv_c, u0 * inv_c, v0 * inv_c
