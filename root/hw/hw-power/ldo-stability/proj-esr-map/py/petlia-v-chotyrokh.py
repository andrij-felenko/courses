import math

TWO_PI = 2.0 * math.pi


class Loop:
    """Петля LDO: підсилення на постійному струмі, два сталі полюси
    (підсилювача похибки й прохідного транзистора) плюс вузол виходу,
    який дає рухомий полюс навантаження й нуль ESR."""

    def __init__(self, a0_db, f_ea, f_pass, r_out):
        self.a0 = 10.0 ** (a0_db / 20.0)   # підсилення петлі, у разах
        self.f_ea = f_ea                   # полюс підсилювача похибки, Гц
        self.f_pass = f_pass               # полюс прохідного транзистора, Гц
        self.r_out = r_out                 # вихідний опір ≈ Vвих/Iнав, Ом

    def features(self, cout, esr):
        """Полюс навантаження й нуль ESR для цієї пари (Cвих, ESR), Гц."""
        f_load = 1.0 / (TWO_PI * cout * (self.r_out + esr))
        f_zero = 1.0 / (TWO_PI * cout * esr)
        return f_load, f_zero

    def gain(self, f, cout, esr):
        """|L| на частоті f. s/ω = j·f/f_x — множники 2π скоротилися."""
        f_load, f_zero = self.features(cout, esr)
        s = 1j * f
        return abs(self.a0 * (1 + s / f_zero)
                   / ((1 + s / f_load) * (1 + s / self.f_ea) * (1 + s / self.f_pass)))

    def phase(self, f, cout, esr):
        """Фаза петлі, градуси. Сума арктангенсів, а НЕ кут комплексного
        добутку: за −180° кут згортається в +180°, і мертва петля
        прикидається бездоганною."""
        f_load, f_zero = self.features(cout, esr)
        deg = math.degrees(math.atan(f / f_zero))          # нуль тягне вгору
        for f_pole in (f_load, self.f_ea, self.f_pass):
            deg -= math.degrees(math.atan(f / f_pole))     # кожен полюс — униз
        return deg
