# -*- coding: utf-8 -*-
"""Фігури до статті «VTOL-гібриди».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

import math


# ── Фігура 1: піднімальна сила крила ∝ V² проти спадної тяги висіння ──────────
def fig_lift_vs_speed():
    W, H = 820, 520
    f = [text(W / 2, 30, "Дві сили проти ваги: висіння слабшає, крило (∝ V²) наростає",
              size=15, bold=True)]

    ox, oy = 90, 420          # початок осей (низ-ліво)
    top = 80                  # верх графіка
    right = ox + 640          # права межа осі швидкості
    Wy = 210                  # рівень ваги на екрані (менше — вище)

    # осі
    f.append(line(ox, oy, right, oy, color=MUTED, sw=1.5))
    f.append(line(ox, oy, ox, top, color=MUTED, sw=1.5))
    f.append(text(right, oy + 28, "швидкість польоту V →", size=12, color=MUTED, anchor="end"))
    f.append(text(ox - 12, top + 6, "сила вгору", size=12, color=MUTED, anchor="end", italic=True))
    f.append(text(ox - 10, oy + 5, "0", size=11, color=MUTED, anchor="end"))

    # лінія ваги (горизонтальна)
    f.append(line(ox, Wy, right, Wy, color=INK, sw=1.6, dash="7 5"))
    f.append(text(right - 4, Wy - 9, "вага апарата W", size=12, color=INK, anchor="end", bold=True))

    span = right - ox
    # V_stall — де крило доростає до ваги
    x_stall = ox + span * 0.62
    # V_trans — безпечний поріг (крило несе з запасом)
    x_trans = ox + span * 0.74

    # крива крила: L ∝ V² (парабола від 0), доростає до ваги в x_stall
    # масштаб: у x_stall піднімальна = W (тобто y = Wy)
    def wing_y(x):
        t = (x - ox) / (x_stall - ox)          # 0..1 у точці звалювання
        val = t * t                             # ∝ V²
        return oy - (oy - Wy) * val
    pts = []
    x = ox
    while x <= right:
        pts.append("%.1f,%.1f" % (x, max(top, wing_y(x))))
        x += 6
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
             % (" ".join(pts), FIELD))
    # підпис крила — біля точки, де крива ще в межах графіка (трохи вище рівня ваги)
    x_wl = x_stall + span * 0.06
    f.append(text(x_wl + 8, max(top + 12, wing_y(x_wl)) - 8, "крило  L = ½ρV²·S·C_L",
                  size=12, color=FIELD, anchor="start", bold=True))

    # крива висіння: повна на нулі (трохи вище ваги), спадає з розгоном
    y_hover0 = Wy - 70        # висіння на нулі трохи потужніше за вагу (є запас)
    def hover_y(x):
        t = (x - ox) / (right - ox)             # 0..1
        val = 1.0 - 0.85 * t * t                 # спад, прискорений із швидкістю
        if val < 0: val = 0
        return oy - (oy - y_hover0) * val
    pts2 = []
    x = ox
    while x <= right:
        pts2.append("%.1f,%.1f" % (x, hover_y(x)))
        x += 6
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
             % (" ".join(pts2), POS))
    f.append(text(ox + 24, y_hover0 - 12, "висіння  T = ṁ·v", size=12, color=POS,
                  anchor="start", bold=True))

    # вертикалі V_stall та V_trans
    f.append(line(x_stall, oy, x_stall, wing_y(x_stall) - 4, color=MUTED, sw=1.0, dash="3 4"))
    f.append(line(x_trans, oy, x_trans, top + 30, color=MUTED, sw=1.0, dash="3 4"))
    f.append(text(x_stall, oy + 18, "V_stall", size=11, color=MUTED, anchor="middle"))
    f.append(text(x_trans, oy + 18, "V_перех", size=11, color=MUTED, anchor="middle"))

    # «діра»: смуга, де жодна крива не дотягує до ваги
    # знайдемо ліву межу — де висіння спадає нижче ваги
    xL = ox
    x = ox
    while x <= right:
        if hover_y(x) > Wy:      # висіння вже нижче ваги (y більше = нижче)
            xL = x
            break
        x += 2
    xR = x_stall
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" '
             'opacity="0.55"/>' % (xL, top + 46, xR - xL, oy - top - 46))
    bx, bw, bh = textbox((xL + xR) / 2, top + 20, "НЕБЕЗПЕЧНА ДІРА",
                         size=12, bold=True, color=POS, fill="#fdecea", stroke=POS)
    f.append(bx)
    f.append(text((xL + xR) / 2, top + 66, "жодна сила сама", size=10.5, color=POS))
    f.append(text((xL + xR) / 2, top + 82, "не тримає вагу", size=10.5, color=POS))

    render(os.path.join(IMG, "lift-vs-speed.svg"), W, H, *f)


# ── Фігура 2: три школи VTOL — куди перенаправити тягу ────────────────────────
def fig_vtol_types():
    W, H = 840, 430
    f = [text(W / 2, 30, "Три способи перекласти тягу з висіння у політ",
              size=15, bold=True)]

    colw = W / 3
    cx = [colw * 0.5, colw * 1.5, colw * 2.5]
    y_hover = 150          # ряд «висіння»
    y_cruise = 300         # ряд «крейсер»

    # підписи рядів зліва
    f.append(text(14, y_hover, "висіння", size=11, color=MUTED, anchor="start", italic=True))
    f.append(text(14, y_cruise, "політ", size=11, color=MUTED, anchor="start", italic=True))
    f.append(line(0, (y_hover + y_cruise) / 2 - 2, W, (y_hover + y_cruise) / 2 - 2,
                  color="#e5e7eb", sw=1.0))

    def up_arrow(x, y, ln=26, col=POS):
        return arrow(x, y + ln, x, y - ln, color=col, sw=2.4)

    def fwd_arrow(x, y, ln=30, col=FIELD):
        return arrow(x - ln, y, x + ln, y, color=FIELD, sw=2.4)

    # фюзеляж-капсула з центром (x,y); vertical=True → носом угору (для хвостосідача).
    # Малюємо в АБСОЛЮТНИХ координатах (без transform), щоб перевірка меж бачила справжні краї.
    def body(x, y, w=54, h=14, vertical=False):
        bw, bh = (h, w) if vertical else (w, h)
        return rect(x - bw / 2, y - bh / 2, bw, bh, fill="#eef2f7", stroke=LINE, sw=1.5, rx=7)

    def wing(x, y, span=70, vertical=False):
        if vertical:
            return rect(x - 3, y - span / 2, 6, span, fill="#d7dee7", stroke=LINE, sw=1.2, rx=3)
        return rect(x - span / 2, y - 3, span, 6, fill="#d7dee7", stroke=LINE, sw=1.2, rx=3)

    # ── стовпець 1: КОНВЕРТОПЛАН (нахил гвинтів) ──
    x = cx[0]
    f.append(text(x, 64, "Конвертоплан", size=13, bold=True))
    f.append(text(x, 82, "повертає гвинти", size=10.5, color=MUTED))
    # висіння: крило горизонтальне, гвинти вгору
    f.append(wing(x, y_hover))
    f.append(body(x, y_hover))
    f.append(up_arrow(x - 30, y_hover - 6))
    f.append(up_arrow(x + 30, y_hover - 6))
    f.append(text(x, y_hover + 40, "гондоли вгору", size=10, color=POS))
    # крейсер: те саме крило, гвинти вперед
    f.append(wing(x, y_cruise))
    f.append(body(x, y_cruise))
    f.append(fwd_arrow(x - 30, y_cruise - 2, ln=22))
    f.append(fwd_arrow(x + 30, y_cruise - 2, ln=22))
    f.append(text(x, y_cruise + 40, "гондоли вперед", size=10, color=FIELD))

    # ── стовпець 2: ХВОСТОСІДАЧ (нахил корпусу) ──
    x = cx[1]
    f.append(text(x, 64, "Хвостосідач", size=13, bold=True))
    f.append(text(x, 82, "нахиляє весь корпус", size=10.5, color=MUTED))
    # висіння: весь апарат носом угору (вертикально)
    f.append(body(x, y_hover, vertical=True))
    f.append(wing(x, y_hover, span=44, vertical=True))
    f.append(up_arrow(x, y_hover - 22))
    f.append(text(x, y_hover + 44, "стоїть на хвості", size=10, color=POS))
    # крейсер: ліг горизонтально, крило несе
    f.append(body(x, y_cruise))
    f.append(wing(x, y_cruise, span=64))
    f.append(fwd_arrow(x, y_cruise - 2, ln=30))
    f.append(text(x, y_cruise + 40, "ліг на крило", size=10, color=FIELD))

    # ── стовпець 3: КВАДРОПЛАН (окремі мотори) ──
    x = cx[2]
    f.append(text(x, 64, "Квадроплан", size=13, bold=True))
    f.append(text(x, 82, "окремі гвинти висіння", size=10.5, color=MUTED))
    # висіння: крило + 4 гвинти вгору активні, тягнучий вимкнено
    f.append(wing(x, y_hover, span=78))
    f.append(body(x, y_hover))
    f.append(up_arrow(x - 34, y_hover - 6))
    f.append(up_arrow(x + 34, y_hover - 6))
    f.append(text(x, y_hover + 40, "верхні гвинти", size=10, color=POS))
    # крейсер: верхні зупинені (сірі × ), тягнучий уперед
    f.append(wing(x, y_cruise, span=78))
    f.append(body(x, y_cruise))
    f.append(text(x - 34, y_cruise - 24, "×", size=17, color=MUTED, bold=True))
    f.append(text(x + 34, y_cruise - 24, "×", size=17, color=MUTED, bold=True))
    f.append(fwd_arrow(x, y_cruise + 26, ln=30))
    f.append(text(x, y_cruise + 52, "тягнучий гвинт", size=10, color=FIELD))

    # вертикальні розділювачі стовпців
    f.append(line(colw, 50, colw, H - 12, color="#e5e7eb", sw=1.0))
    f.append(line(2 * colw, 50, 2 * colw, H - 12, color="#e5e7eb", sw=1.0))

    render(os.path.join(IMG, "vtol-types.svg"), W, H, *f)


if __name__ == "__main__":
    fig_lift_vs_speed()
    fig_vtol_types()
    print("OK: lift-vs-speed.svg, vtol-types.svg")
