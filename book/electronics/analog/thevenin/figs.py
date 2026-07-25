# -*- coding: utf-8 -*-
"""Фігура до детальної статті «Теорема Тевеніна».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Генерує ОДНУ нову фігуру детальної версії:
  iv-line.svg — вольт-амперна характеристика клем як пряма V = Vth − I·Rth
                (перетин з осями = Vth та I_кз; нахил = −Rth; робоча точка з навантаженням).
Інші SVG теми (statement, vth-rth, swap-loads, worked, real-source) належать
базовій статті й тут НЕ перегенеровуються.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура: характеристика клем — пряма, задана двома числами ─────────────────
def fig_iv_line():
    W, H = 720, 440
    ox, oy = 90, 360          # початок координат (нижній лівий кут осей)
    ax_w, ax_h = 520, 290     # довжина осей
    # числова модель: Vth=6, Rth=3 → I_кз=2; робоча точка з R_нав=Rth: I=1, V=3
    Vth, Rth = 6.0, 3.0
    Isc = Vth / Rth           # = 2
    Imax, Vmax = 2.4, 7.2     # масштаб осей
    i_op = 1.0                # робочий струм (навантаження R_нав = Rth)
    v_op = Vth - i_op * Rth   # = 3

    def px(i):
        return ox + (i / Imax) * ax_w
    def py(v):
        return oy - (v / Vmax) * ax_h

    P = []
    # осі
    P.append(arrow(ox, oy, ox + ax_w + 24, oy))          # вісь I →
    P.append(arrow(ox, oy, ox, oy - ax_h - 24))          # вісь V ↑
    P.append(text(ox + ax_w + 4, oy - 14, "струм I", size=13, italic=True, anchor="end"))
    P.append(text(ox + 6, oy - ax_h - 30, "напруга V", size=13, italic=True, anchor="start"))

    # пряма джерела V = Vth − I·Rth (від холостого ходу до короткого)
    P.append(line(px(0), py(Vth), px(Isc), py(0), color=POS, sw=2.6, dash="7 4"))

    # навантажувальна пряма (лінійне навантаження крізь початок): V = I·R_нав
    P.append(line(px(0), py(0), px(1.45), py(1.45 * Rth), color=NEG, sw=2.2))

    # точка Vth на осі напруги (холостий хід)
    P.append(circle(px(0), py(Vth), 5.5, fill=POS, stroke=POS))
    P.append(text(px(0) + 14, py(Vth) - 8, "Vth — холостий хід (I = 0)",
                  size=12, color=POS, anchor="start", bold=True))

    # точка I_кз на осі струму (коротке замикання)
    P.append(circle(px(Isc), py(0), 5.5, fill=POS, stroke=POS))
    P.append(text(px(Isc), oy + 26, "I_кз = Vth/Rth", size=12, color=POS, anchor="middle", bold=True))

    # підпис нахилу вздовж прямої джерела
    P.append(text(px(1.62), py(Vth - 1.62 * Rth) - 16, "нахил = −Rth",
                  size=12, color=POS, anchor="start", bold=True))

    # робоча точка (перетин прямих) + підпис нижче, у чистій зоні
    P.append(circle(px(i_op), py(v_op), 6.5, fill=FIELD, stroke=FIELD))
    P.append(text(px(i_op), py(v_op) + 34, "робоча точка", size=12, color=FIELD, anchor="middle", bold=True))

    # підпис навантажувальної прямої (ліворуч від неї, у чистій зоні)
    P.append(text(px(0.18), py(1.7), "навантаження R_нав", size=12, color=NEG, anchor="start", bold=True))

    # довідкова рамка у вільному верхньому правому куті
    bx, by, bw, bh = 452, 70, 250, 96
    P.append(fitbox(bx, by, bw, bh,
                    "Пряма клем:  V = Vth − I·Rth\n"
                    "холостий хід (I = 0):  V = Vth\n"
                    "коротке (V = 0):  I = Vth/Rth",
                    size=13, fill=FILL, stroke=MUTED, sw=1.4, color=INK))

    render(os.path.join(IMG, "iv-line.svg"), W, H, *P,
           title="Характеристика клем — пряма, задана двома числами")


if __name__ == "__main__":
    fig_iv_line()
    print("written:", os.listdir(IMG))
