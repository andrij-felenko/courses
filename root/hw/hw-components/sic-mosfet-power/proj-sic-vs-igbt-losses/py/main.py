from dataclasses import dataclass


@dataclass(frozen=True)
class Switch:
    """Ключ у двох рисах: як він падає напругу і чого коштує один перемик."""
    name:  str
    v0:    float   # В   — поріг ВАХ; у польового ключа його немає
    r:     float   # Ом  — нахил ВАХ (rce) або Rds(on) — обов'язково ГАРЯЧИЙ
    e_ref: float   # Дж  — Eon+Eoff у даташитній точці
    v_ref: float   # В   — напруга тієї точки
    i_ref: float   # А   — струм тієї точки
    price: float   # $

    def p_cond(self, i, duty):
        """Провідні втрати: поріг бере струм, опір бере квадрат струму."""
        return duty * (self.v0 * i + self.r * i * i)

    def e_sw(self, v, i):
        """Даташитна енергія, перерахована на наш режим: лінійно по V і по I."""
        return self.e_ref * (v / self.v_ref) * (i / self.i_ref)

    def p_total(self, v, i, duty, fsw):
        return self.p_cond(i, duty) + self.e_sw(v, i) * fsw


SIC = Switch("SiC C2M0080120D @150 °C", v0=0.0, r=0.144,
             e_ref=684e-6, v_ref=800.0, i_ref=20.0, price=25.0)
IGBT = Switch("Si IKW40N120H3 @175 °C", v0=0.8, r=0.0375,
              e_ref=7.0e-3, v_ref=600.0, i_ref=40.0, price=8.0)


def f_crossover(mos, igbt, v, i, duty):
    """Частота, вище якої польовий ключ холодніший. None — перетину не існує."""
    cond_gap = mos.p_cond(i, duty) - igbt.p_cond(i, duty)
    sw_gain = igbt.e_sw(v, i) - mos.e_sw(v, i)
    if sw_gain <= 0:
        return None          # відігравати нічим
    if cond_gap <= 0:
        return 0.0           # MOSFET кращий і провідністю — виграє на будь-якій частоті
    return cond_gap / sw_gain


def breakeven_current(mos, igbt):
    """Струм, нижче якого MOSFET кращий і в провідності теж."""
    dr = mos.r - igbt.r
    return igbt.v0 / dr if dr > 0 else None


V_DC, I_SW, DUTY = 800.0, 20.0, 0.5

print("струм-беззбитковість : %.1f А" % breakeven_current(SIC, IGBT))
print("частота-перетин @%.0f А: %.2f кГц"
      % (I_SW, f_crossover(SIC, IGBT, V_DC, I_SW, DUTY) / 1e3))
print()
print("f, кГц    SiC, Вт   IGBT, Вт    виграш")
for f_khz in (2, 5, 10, 20, 50):
    ps = SIC.p_total(V_DC, I_SW, DUTY, f_khz * 1e3)
    pi = IGBT.p_total(V_DC, I_SW, DUTY, f_khz * 1e3)
    print("%6d   %8.1f   %8.1f   %+7.1f" % (f_khz, ps, pi, pi - ps))
