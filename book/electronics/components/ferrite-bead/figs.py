# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Феритова намистина».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: будова намистини — один виток крізь втратний ферит ──────────────
# Головна ідея: намистина — це НЕ котушка із запасанням, а провідник у втратному
# фериті. Зліва SMD-цеглинка (один виток крізь керамічний брусок), справа —
# «дротяна» рідня (кільце на кабелі). Підпис: котушка запасає, намистина палить.
def fig_anatomy():
    W, H = 960, 430
    p = []

    # ── ЛІВОРУЧ: SMD-намистина в розрізі ─────────────────────────────────────
    cx = 250
    p.append(text(cx, 60, "SMD-намистина в розрізі", size=15, bold=True))

    # феритовий брусок
    bx, by, bw, bh = cx - 130, 110, 260, 120
    p.append(rect(bx, by, bw, bh, fill="#3a3a42", stroke=INK, sw=2, rx=10))
    p.append(text(cx, by + bh / 2 - 16, "втратний", size=13, color="#e8e8ec"))
    p.append(text(cx, by + bh / 2 + 4, "NiZn-ферит", size=13, color="#e8e8ec", bold=True))

    # провідник наскрізь (один виток) + контактні шапочки
    wy = by + bh / 2 + 34
    p.append(line(bx - 46, wy, bx + bw + 46, wy, color="#c9a227", sw=8))
    p.append(rect(bx - 22, by, 22, bh, fill="#c9c9cf", stroke=INK, sw=1.5, rx=3))
    p.append(rect(bx + bw, by, 22, bh, fill="#c9c9cf", stroke=INK, sw=1.5, rx=3))
    p.append(text(bx - 60, wy + 26, "вивід", size=12, color=MUTED, anchor="middle"))
    p.append(text(cx, by + bh + 40, "провідник = ОДИН виток", size=12.5, color=POS, bold=True))

    # ── ПРАВОРУЧ: феритове кільце на кабелі ──────────────────────────────────
    dx = 710
    p.append(text(dx, 60, "феритове кільце на кабелі", size=15, bold=True))
    # кабель
    p.append(line(dx - 150, 170, dx + 150, 170, color="#444", sw=10))
    # кільце (тор у розрізі — два кільця)
    p.append(circle(dx, 170, 62, fill="none", stroke="#3a3a42", sw=22))
    p.append(circle(dx, 170, 62, fill="none", stroke=INK, sw=2))
    p.append(circle(dx, 170, 40, fill="none", stroke=INK, sw=1.2))
    p.append(text(dx, 170 + 100, "ферит охоплює дріт —", size=12.5, color=MUTED))
    p.append(text(dx, 170 + 118, "виткa немає взагалі", size=12.5, color=MUTED))

    # ── НИЗ: контраст із котушкою ────────────────────────────────────────────
    b1, w1, h1 = textbox(cx, 360, ["котушка: запасає поле", "й ПОВЕРТАЄ енергію"],
                         size=13.5, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    p.append(b1)
    b2, w2, h2 = textbox(dx, 360, ["намистина: перемелює", "заваду в ТЕПЛО"],
                         size=13.5, fill="#fdecea", stroke=POS, color=POS, bold=True)
    p.append(b2)

    render("img/anatomy.svg", W, H, *p)


# ── Фігура 2: паспортна крива Z(f) — індуктивна частина і втратна ─────────────
# Намистину описують не генрі, а «омами на контрольній частоті». Крива Z(f)
# росте (індуктивна область — ще «котушка»), виходить на горб (втратна область —
# уже «резистор»), і саме горб роблять робочим. Контрольна точка 100 МГц.
def fig_impedance():
    W, H = 920, 470
    p = []
    p.append(text(W / 2, 34, "Паспортна крива намистини: де вона котушка, а де резистор",
                  size=15, bold=True))

    # осі (лог-частота умовно — рівномірна шкала з підписами декад)
    ox, oy = 110, 380          # початок осей
    ax, ay = 840, 70           # кінець осей
    p.append(arrow(ox, oy, ax, oy, color=INK))      # X
    p.append(arrow(ox, oy, ox, ay, color=INK))      # Y
    p.append(text((ox + ax) / 2, oy + 46, "частота  (МГц, логарифм)", size=13, color=MUTED))
    p.append(text(ox - 70, (oy + ay) / 2, "опір заваді  Z", size=13, color=MUTED))

    decades = [("1", 0.0), ("10", 0.33), ("100", 0.66), ("1000", 1.0)]
    for lab, fr in decades:
        x = ox + fr * (ax - ox)
        p.append(line(x, oy, x, oy + 6, color=INK))
        p.append(text(x, oy + 24, lab, size=12, color=MUTED))

    # крива Z(f): росте лінійно (індуктивна), горб, легкий спад (втратна)
    def zx(fr):
        return ox + fr * (ax - ox)
    def zy(val):                # val 0..1 (частка від максимуму)
        return oy - val * (oy - ay - 20)
    pts = [(0.0, 0.03), (0.20, 0.10), (0.40, 0.28), (0.55, 0.50),
           (0.66, 0.72), (0.78, 0.93), (0.86, 1.0), (0.95, 0.95), (1.0, 0.88)]
    d = "M " + " L ".join("%.1f %.1f" % (zx(f), zy(v)) for f, v in pts)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.5"/>' % (d, INK))

    # межа двох областей (вертикаль під горбом)
    xb = zx(0.62)
    p.append(line(xb, oy, xb, ay + 30, color=MUTED, sw=1.4, dash="6 5"))

    # підписи двох областей
    p.append(text(zx(0.30), zy(0.92), "індуктивна", size=13, color=NEG, bold=True))
    p.append(text(zx(0.30), zy(0.92) + 18, "(запасає — ще «котушка»)", size=11.5, color=NEG))
    p.append(text(zx(0.86), zy(0.30), "втратна", size=13, color=POS, bold=True))
    p.append(text(zx(0.86), zy(0.30) + 18, "(гріє ферит — «резистор»)", size=11.5, color=POS))

    # контрольна точка «Z @ 100 МГц»
    xp, yp = zx(0.66), zy(0.72)
    p.append(circle(xp, yp, 6, fill=FIELD, stroke=INK, sw=2))
    b, bw, bh = textbox(xp + 96, yp - 30, "«600 Ом @ 100 МГц»",
                        size=12.5, fill="#eafaf0", stroke=FIELD, bold=True)
    p.append(b)
    p.append(line(xp + 6, yp, xp + 96 - bw / 2, yp - 24, color=FIELD, sw=1.4))

    render("img/impedance.svg", W, H, *p)


# ── Фігура 3: постійний струм «здуває» опір намистини ────────────────────────
# Ахіллесова п'ята: робочий постійний струм підмагнічує ферит, домени вже
# вишикувані — і «опір для шуму» тане. Дві криві Z(f): без струму й на половині
# номіналу (100 Ом → 10 Ом — реальна цифра з даташита TDK).
def fig_dc_bias():
    W, H = 900, 460
    p = []
    p.append(text(W / 2, 34, "Постійний струм «здуває» опір намистини", size=15, bold=True))

    ox, oy = 110, 380
    ax, ay = 820, 70
    p.append(arrow(ox, oy, ax, oy, color=INK))
    p.append(arrow(ox, oy, ox, ay, color=INK))
    p.append(text((ox + ax) / 2, oy + 46, "частота", size=13, color=MUTED))
    p.append(text(ox - 58, (oy + ay) / 2, "опір  Z", size=13, color=MUTED))

    def zx(fr):
        return ox + fr * (ax - ox)
    def zy(val):
        return oy - val * (oy - ay - 20)

    # крива без струму (повна)
    hi = [(0.0, 0.03), (0.25, 0.18), (0.45, 0.42), (0.62, 0.74),
          (0.74, 0.95), (0.82, 1.0), (0.93, 0.95), (1.0, 0.9)]
    d_hi = "M " + " L ".join("%.1f %.1f" % (zx(f), zy(v)) for f, v in hi)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (d_hi, NEG))

    # крива на половині номіналу (придушена ~у 10 разів)
    lo = [(0.0, 0.02), (0.25, 0.04), (0.45, 0.07), (0.62, 0.10),
          (0.74, 0.12), (0.82, 0.13), (0.93, 0.12), (1.0, 0.11)]
    d_lo = "M " + " L ".join("%.1f %.1f" % (zx(f), zy(v)) for f, v in lo)
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2" stroke-dasharray="7 5"/>' % (d_lo, POS))

    # підписи кривих
    b1, w1, h1 = textbox(zx(0.70), zy(1.0) - 4, "I = 0:  100 Ом",
                         size=12.5, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    p.append(b1)
    b2, w2, h2 = textbox(zx(0.74), zy(0.13) + 40, ["I = ½ номіналу:", "лишилось ~10 Ом"],
                         size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    p.append(b2)

    # стрілка «обвал»
    p.append(arrow(zx(0.55), zy(0.70), zx(0.55), zy(0.12), color=MUTED, sw=1.8))
    p.append(text(zx(0.46), zy(0.40), "обвал", size=12, color=MUTED, anchor="end"))
    p.append(text(zx(0.46), zy(0.40) + 16, "у ~10×", size=12, color=MUTED, anchor="end"))

    render("img/dc-bias.svg", W, H, *p)


if __name__ == "__main__":
    fig_anatomy()
    fig_impedance()
    fig_dc_bias()
    print("figs.py: згенеровано anatomy.svg, impedance.svg, dc-bias.svg")
