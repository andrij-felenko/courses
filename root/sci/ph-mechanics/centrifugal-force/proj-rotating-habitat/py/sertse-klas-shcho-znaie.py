@dataclass
class Habitat:
    r: float                   # радіус до підлоги-обода, м
    omega: float               # кутова швидкість, рад/с

    def g_rim(self):      return self.omega**2 * self.r         # a = ω²·r, м/с²
    def g_fraction(self): return self.g_rim() / G_EARTH         # у частках земного
    def rpm(self):        return rad_to_rpm(self.omega)         # об/хв
    def period(self):     return 2.0 * math.pi / self.omega     # с на оберт
    def rim_speed(self):  return self.omega * self.r            # м/с, швидкість обода

    def gradient_frac(self, h=1.80):                            # (g_ніг − g_голови)/g_ніг
        return h / self.r                                       #  = ω²·h / (ω²·r) = h/r
    def g_head(self, h=1.80):
        return self.omega**2 * (self.r - h)                     # ноги на r, голова на r−h

    def coriolis_force(self, m=80.0, v=1.30):                   # бічний штовхан під час ходи
        return 2.0 * m * self.omega * v                         # F = 2·m·Ω·v, Н
    def coriolis_frac(self, v=1.30):                            # доля від ваги
        return 2.0 * v / self.rim_speed()                       # 2Ωv/(ω²r) = 2v/v_обода

    def verdict(self, h=1.80):
        rpm, vr, gr = self.rpm(), self.rim_speed(), self.gradient_frac(h)
        if rpm <= RPM_OK and vr >= V_RIM_MIN and gr <= GRAD_MAX:
            return "комфорт"
        if rpm <= RPM_TOL and vr >= V_RIM_MIN and gr <= GRAD_MAX:
            return "терпимо"
        return "дискомфорт"
