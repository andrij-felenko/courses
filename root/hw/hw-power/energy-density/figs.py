# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')


# ── 1. Драбина вагової щільності (Вт·год/кг) — лог-масштаб ───────────────────
def fig_ladder():
    W, H = 720, 380
    x0, y0 = 220, 60          # ліва межа смуг, верх поля
    x1 = 690                  # права межа
    row_h = 40
    # (назва, Вт·год/кг, колір)
    rows = [
        ("Суперконденсатор", 8, MUTED),
        ("Свинець-кислота", 40, NEG),
        ("Нікель-метал-гідрид", 90, NEG),
        ("LiFePO₄ (комірка)", 130, FIELD),
        ("Li-ion NMC (комірка)", 270, FIELD),
        ("Бензин (паливо)", 12000, POS),
    ]
    import math
    lo, hi = 5.0, 20000.0
    def sx(v):
        return x0 + (x1 - x0) * (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo))

    frags = []
    # осьові позначки (10, 100, 1000, 10000)
    for tick in (10, 100, 1000, 10000):
        gx = sx(tick)
        frags.append(line(gx, y0 - 8, gx, y0 + len(rows) * row_h + 4, color="#dddddd", sw=1))
        frags.append(text(gx, y0 + len(rows) * row_h + 22, str(tick), size=11, color=MUTED))
    frags.append(text((x0 + x1) / 2, H - 12, "Вт·год/кг  (логарифмічна шкала)", size=12, color=MUTED))

    for i, (name, v, col) in enumerate(rows):
        cy = y0 + i * row_h + row_h / 2
        frags.append(text(x0 - 12, cy + 4, name, size=13, color=INK, anchor="end"))
        bx = sx(v)
        frags.append(rect(x0, cy - 11, bx - x0, 22, fill=col, stroke=col, sw=1, rx=4))
        lbl = ("%d" % v) if v >= 100 else ("%d" % v)
        frags.append(text(bx + 8, cy + 4, "%s" % lbl, size=12, color=INK, anchor="start"))

    render(os.path.join(IMG, 'ladder.svg'), W, H, *frags,
           title="Скільки енергії тримає кілограм")


# ── 2. Вагова проти об'ємної: дві незалежні осі ─────────────────────────────
def fig_two_axes():
    W, H = 700, 470
    # поле графіка
    gx0, gy0 = 90, 60      # лівий-верх осей
    gx1, gy1 = 640, 380    # правий-низ
    # осі: X = Вт·год/л (0..800), Y = Вт·год/кг (0..300)
    xmax, ymax = 800.0, 300.0
    def px(v): return gx0 + (gx1 - gx0) * v / xmax
    def py(v): return gy1 - (gy1 - gy0) * v / ymax

    frags = []
    # сітка
    for xv in (200, 400, 600, 800):
        frags.append(line(px(xv), gy0, px(xv), gy1, color="#eeeeee", sw=1))
        frags.append(text(px(xv), gy1 + 20, str(xv), size=11, color=MUTED))
    for yv in (100, 200, 300):
        frags.append(line(gx0, py(yv), gx1, py(yv), color="#eeeeee", sw=1))
        frags.append(text(gx0 - 10, py(yv) + 4, str(yv), size=11, color=MUTED, anchor="end"))
    # осі
    frags.append(line(gx0, gy0, gx0, gy1, color=INK, sw=1.5))
    frags.append(line(gx0, gy1, gx1, gy1, color=INK, sw=1.5))
    frags.append(text((gx0 + gx1) / 2, H - 14, "об'ємна щільність, Вт·год/л  → менший об'єм", size=12, color=INK))
    # вертикальний підпис осі Y
    frags.append('<text x="26" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 26 %.1f)">%s</text>'
                 % ((gy0 + gy1) / 2, FONT, INK, (gy0 + gy1) / 2,
                    esc("вагова щільність, Вт·год/кг  → менша вага")))

    # точки: (назва, Вт·год/л, Вт·год/кг, колір, зсув-підпису dx, dy)
    pts = [
        ("Свинець-кислота", 90, 40, NEG, 10, -8),
        ("NiMH", 300, 90, MUTED, 8, 18),
        ("LiFePO₄", 330, 130, FIELD, -6, -14),
        ("Li-ion NMC", 620, 270, POS, -10, -14),
    ]
    for name, xv, yv, col, dx, dy in pts:
        cx, cy = px(xv), py(yv)
        frags.append(circle(cx, cy, 8, fill=col, stroke=INK, sw=1.2))
        frags.append(text(cx + dx, cy + dy, name, size=12, color=INK,
                          anchor="start" if dx >= 0 else "end", bold=True))
    # стрілка «краще»
    frags.append(text(px(700), py(285), "краще за обома", size=11, color=MUTED))

    render(os.path.join(IMG, 'two-axes.svg'), W, H, *frags,
           title="Дві щільності — дві різні осі")


# ── 3. Комірка → пакет: куди дівається щільність ─────────────────────────────
def fig_cell_to_pack():
    W, H = 700, 340
    cx = [130, 350, 570]
    cy = 150
    stages = [
        ("Комірка", 270, POS, ["гола хімія", "тільки корпус"]),
        ("Модуль", 210, FIELD, ["+ шини, зварні", "+ монітор комірок"]),
        ("Пакет", 170, NEG, ["+ корпус, BMS", "+ проводка, кріплення"]),
    ]
    frags = []
    maxv = 300.0
    box_w = 150
    for i, (name, v, col, notes) in enumerate(stages):
        # висота стовпчика пропорційна щільності
        bh = 150 * v / maxv
        bx = cx[i] - box_w / 2
        by = cy + 40 - bh
        frags.append(rect(bx, by, box_w, bh, fill=col, stroke=INK, sw=1.4, rx=6))
        frags.append(text(cx[i], by - 26, name, size=15, color=INK, bold=True))
        frags.append(text(cx[i], by - 8, "%d Вт·год/кг" % v, size=13, color=INK))
        # підписи-доважки
        ny = cy + 70
        for n in notes:
            frags.append(text(cx[i], ny, n, size=11, color=MUTED))
            ny += 17
        # стрілка й «−N %» між стадіями
        if i > 0:
            prev = stages[i - 1][1]
            drop = round(100 * (1 - v / prev))
            ax1 = cx[i - 1] + box_w / 2 + 6
            ax2 = cx[i] - box_w / 2 - 6
            frags.append(arrow(ax1, cy - 30, ax2, cy - 30, color=INK, sw=1.6))
            frags.append(text((ax1 + ax2) / 2, cy - 40, "−%d%%" % drop, size=13, color=POS, bold=True))

    render(os.path.join(IMG, 'cell-to-pack.svg'), W, H, *frags,
           title="Число з наклейки комірки — не число пакета")


if __name__ == '__main__':
    fig_ladder()
    fig_two_axes()
    fig_cell_to_pack()
    print("ok")
