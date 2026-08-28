from fractions import Fraction

class Monomial:
    def __init__(self, a, b):
        self.a = a  # степінь x
        self.b = b  # степінь y

    def total_deg(self):
        return self.a + self.b

    def __lt__(self, other):
        if self.total_deg() != other.total_deg():
            return self.total_deg() < other.total_deg()
        if self.b != other.b:
            return self.b > other.b  # grevlex order
        return self.a < other.a

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b


def lcm(m1: Monomial, m2: Monomial):
    return Monomial(max(m1.a, m2.a), max(m1.b, m2.b))


def divides(div: Monomial, target: Monomial):
    return div.a <= target.a and div.b <= target.b


class Poly2D:
    def __init__(self, terms=None):
        # terms: list of (Fraction, Monomial)
        self.terms = terms or []
        self.cleanup()

    def cleanup(self):
        d = {}
        for coeff, monom in self.terms:
            c = Fraction(coeff)
            key = (monom.a, monom.b)
            d[key] = d.get(key, Fraction(0)) + c
        clean = []
        for (a, b), c in d.items():
            if c != 0:
                clean.append((c, Monomial(a, b)))
        clean.sort(key=lambda t: t[1], reverse=True)
        self.terms = clean

    def is_zero(self):
        return len(self.terms) == 0

    def lt(self):
        return self.terms[0] if self.terms else (Fraction(0), Monomial(0, 0))


def reduce_poly(f: Poly2D, g_list: list):
    f_cur = Poly2D(list(f.terms))
    rem_terms = []
    while not f_cur.is_zero():
        c_f, m_f = f_cur.lt()
        reduced = False
        for g in g_list:
            c_g, m_g = g.lt()
            if divides(m_g, m_f):
                factor = c_f / c_g
                shift = Monomial(m_f.a - m_g.a, m_f.b - m_g.b)
                new_terms = list(f_cur.terms)
                for cg, mg in g.terms:
                    new_terms.append((-factor * cg, Monomial(mg.a + shift.a, mg.b + shift.b)))
                f_cur = Poly2D(new_terms)
                reduced = True
                break
        if not reduced:
            rem_terms.append((c_f, m_f))
            f_cur.terms.pop(0)
    return Poly2D(rem_terms)


def s_polynomial(g1: Poly2D, g2: Poly2D):
    c1, m1 = g1.lt()
    c2, m2 = g2.lt()
    L = lcm(m1, m2)
    s1 = Monomial(L.a - m1.a, L.b - m1.b)
    s2 = Monomial(L.a - m2.a, L.b - m2.b)

    terms = []
    for c, m in g1.terms:
        terms.append((c / c1, Monomial(m.a + s1.a, m.b + s1.b)))
    for c, m in g2.terms:
        terms.append((-c / c2, Monomial(m.a + s2.a, m.b + s2.b)))
    return Poly2D(terms)


def buchberger(G: list):
    G = [Poly2D(g.terms) for g in G]
    pairs = [(i, j) for i in range(len(G)) for j in range(i + 1, len(G))]
    while pairs:
        i, j = pairs.pop()
        S = s_polynomial(G[i], G[j])
        rem = reduce_poly(S, G)
        if not rem.is_zero():
            new_idx = len(G)
            for k in range(len(G)):
                pairs.append((k, new_idx))
            G.append(rem)
    return G
