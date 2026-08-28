#!/usr/bin/env python3
"""ocvgen.py — з виміряної кривої OCV(SoC) робить масив вузлів для прошивки."""

V_UNIT  = 10000   # 1 В = 10000 одиниць по 0.1 мВ
SIGMA_V = 50      # похибка вольтметра, тих самих одиниць (5 мВ)


def enforce_monotone(pts, min_step=1, noise=20):
    """Напруга мусить СТРОГО зростати: інакше зворотний пошук неоднозначний,
       а різниця сусідніх вузлів може стати нулем. Дрібні брижі виміру
       підправляємо, справжній провал — це зіпсутий вимір, і ми кричимо."""
    out = [pts[0]]
    for soc, v in pts[1:]:
        need = out[-1][1] + min_step
        if v < need - noise:                       # провал понад 2 мВ — не шум
            raise ValueError("немонотонність при SoC = %.1f %%" % (soc / 10.0))
        out.append((soc, max(v, need)))
    return out


def interp_soc(knots, v):
    """Рівно те саме, що робитиме прошивка, — щоб похибку рахувати чесно."""
    if v <= knots[0][1]:  return knots[0][0]
    if v >= knots[-1][1]: return knots[-1][0]
    lo, hi = 0, len(knots) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if knots[mid][1] <= v: lo = mid
        else:                  hi = mid
    (s0, v0), (s1, v1) = knots[lo], knots[lo + 1]
    return s0 + ((v - v0) * (s1 - s0) + (v1 - v0) // 2) // (v1 - v0)


def build(pts, tol_pm=5, max_knots=32):
    """Жадібно вставляти найгіршу точку, доки похибка В ЗАРЯДІ не влізе в допуск."""
    knots = [pts[0], pts[-1]]
    while True:
        worst, werr = None, 0
        for soc, v in pts:
            err = abs(interp_soc(knots, v) - soc)   # похибка міряється в заряді!
            if err > werr:
                worst, werr = (soc, v), err
        if werr <= tol_pm or len(knots) >= max_knots:
            return knots, werr
        knots.append(worst)
        knots.sort(key=lambda p: p[1])


def emit_c(knots, name, t_c):
    print("static const knot_t %s[] = {   // %d °C" % (name, t_c))
    for soc, v in knots:
        print("    { %5d, %4d },   // %5.3f В → %5.1f %%" % (v, soc, v / V_UNIT, soc / 10.0))
    print("};")


def report(knots):
    """Головний звіт: де таблиця бачить, а де сліпа."""
    for (s0, v0), (s1, v1) in zip(knots, knots[1:]):
        k   = (v1 - v0) / (s1 - s0)                 # одразу мВ на 1 % заряду
        sig = SIGMA_V * (s1 - s0) / (v1 - v0)       # похибка заряду, проміле
        print("%5.1f–%5.1f %%   нахил %7.2f мВ/%%   σ = %5.1f %% %s"
              % (s0 / 10, s1 / 10, k, sig / 10, "  ← сліпо" if sig > 150 else ""))
