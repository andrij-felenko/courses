# -*- coding: utf-8 -*-
"""Фігури для вставки comp-sync-vs-async (synchronous vs asynchronous buck).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_loss_crossover():
    """Втрата на нижньому елементі vs струм навантаження: діод (∝I, лінія) проти
    MOSFET (∝I², парабола). Перетин — рідкісна точка, де діод усе ще не гірший."""
    W, H = 760, 470
    # поле графіка
    L, R = 90, 600          # ліва/права межа осей
    T, B = 70, 380          # верх/низ
    Imax = 12.0             # А по осі x
    Pmax = 4.0              # Вт по осі y
    Vf = 0.4                # падіння Шотткі, В
    Rds = 0.005            # Rds(on), Ом
    dty = 0.9               # частка циклу, коли нижній елемент проводить (1−D при D≈0.1)

    def px(i):  return L + (i / Imax) * (R - L)
    def py(p):  return B - (p / Pmax) * (B - T)

    frags = []
    # осі
    frags.append(line(L, T, L, B, color=INK, sw=2))
    frags.append(line(L, B, R, B, color=INK, sw=2))
    # сітка + підписи осі x (струм)
    for i in range(0, int(Imax) + 1, 2):
        x = px(i)
        frags.append(line(x, B, x, B + 5, color=INK, sw=1.2))
        frags.append(text(x, B + 22, "%d" % i, size=12, color=MUTED))
    # підписи осі y (потужність)
    for p in range(0, int(Pmax) + 1):
        y = py(p)
        frags.append(line(L - 5, y, L, y, color=INK, sw=1.2))
        frags.append(text(L - 14, y + 4, "%d" % p, size=12, color=MUTED, anchor="end"))
    frags.append(text((L + R) / 2, B + 44, "струм навантаження I, А", size=13, color=INK))
    frags.append(text(L - 50, (T + B) / 2, "втрата, Вт", size=13, color=INK))

    # крива діода: P = Vf · I · dty (пряма)
    d_pts = []
    n = 80
    for k in range(n + 1):
        i = Imax * k / n
        p = Vf * i * dty
        d_pts.append("%.1f,%.1f" % (px(i), py(min(p, Pmax))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(d_pts), POS))

    # крива MOSFET: P = I² · Rds · dty (парабола)
    m_pts = []
    for k in range(n + 1):
        i = Imax * k / n
        p = i * i * Rds * dty
        m_pts.append("%.1f,%.1f" % (px(i), py(min(p, Pmax))))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(m_pts), NEG))

    # точка перетину: Vf·I·dty = I²·Rds·dty → I = Vf/Rds
    icr = Vf / Rds            # = 80 А — поза полем; перетин фактично аж за межею
    # Реально в межах поля парабола нижча скрізь; познач це стрілкою-виноскою.
    ix = px(10); iy_d = py(Vf * 10 * dty); iy_m = py(10 * 10 * Rds * dty)
    frags.append(line(ix, iy_d, ix, iy_m, color=FIELD, sw=1.6, dash="4,3"))
    frags.append(circle(ix, iy_d, 4, fill=POS, stroke=POS))
    frags.append(circle(ix, iy_m, 4, fill=NEG, stroke=NEG))

    # підписи кривих
    frags.append(text(px(9.6), py(Vf * 9.6 * dty) - 12, "діод  Vf·I", size=13, color=POS, bold=True, anchor="end"))
    frags.append(text(px(10.4), py(10.4 * 10.4 * Rds * dty) + 20, "MOSFET  I²·Rds", size=13, color=NEG, bold=True, anchor="start"))

    # виноска про розрив при I=10 А
    box, bw, bh = textbox(px(4.0), py(3.1),
                          ["при 10 А:", "діод 3.6 Вт", "MOSFET 0.45 Вт", "розрив ×8"],
                          size=12, fill="#eef7f0", stroke=FIELD)
    frags.append(box)

    # ліворуч — зона дуже малого струму
    frags.append(line(px(0.6), T + 6, px(0.6), B, color=MUTED, sw=1.2, dash="3,4"))
    frags.append(text(px(0.7), T + 18, "← мікроструми: розрив зникає", size=11,
                      color=MUTED, anchor="start"))

    render(os.path.join(OUT, "loss-vs-current.svg"), W, H, *frags,
           title="Втрата нижнього елемента: діод (∝I) проти MOSFET (∝I²)")


if __name__ == "__main__":
    fig_loss_crossover()
    print("ok figs")
