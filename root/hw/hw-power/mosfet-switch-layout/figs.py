# -*- coding: utf-8 -*-
"""Фігури для теми mosfet-switch-layout (розводка плати для MOSFET-ключа).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COPPER = "#b5763a"


def cap_v(x, ytop, ybot, ymid, plate=17, gap=6, color=INK, sw=3.2):
    """Вертикальний конденсатор між шинами: дроти + дві горизонтальні пластини."""
    return (line(x, ytop, x, ymid - gap, color=INK, sw=1.8) +
            line(x, ymid + gap, x, ybot, color=INK, sw=1.8) +
            line(x - plate, ymid - gap, x + plate, ymid - gap, color=color, sw=sw) +
            line(x - plate, ymid + gap, x + plate, ymid + gap, color=color, sw=sw))


def mosfet(cx, cy, w=64, h=64, stroke=NEG):
    """Простий блок-ключ із мітками D (зверху), S (знизу), G (зліва)."""
    x, y = cx - w / 2, cy - h / 2
    b = rect(x, y, w, h, fill="#eaf0fd", stroke=stroke, sw=2)
    b += text(cx, cy + 5, "MOSFET", size=11, color=stroke, bold=True)
    return b


# ── 1. Дві петлі: силова й затворна ─────────────────────────────────────────
def fig_two_loops():
    W, H = 820, 480
    f = []
    xv = 150      # ліва вертикаль звідки йдуть шини
    yV, yG = 100, 400          # +V та GND рівні
    xcap = 360                 # локальний конденсатор
    xm = 560                   # колонка стік-витік
    cy = 250                   # центр MOSFET

    # шини
    f.append(line(xcap, yV, xm, yV, color=POS, sw=3))
    f.append(text(xcap - 24, yV + 4, "+V", size=13, color=POS, bold=True, anchor="end"))
    f.append(line(xcap, yG, xm, yG, color=INK, sw=3))
    f.append(text(xcap - 24, yG + 4, "GND", size=13, color=INK, bold=True, anchor="end"))

    # локальний конденсатор
    f.append(cap_v(xcap, yV, yG, 250, color=COPPER))
    f.append(text(xcap, yV - 12, "Cлок", size=12, color=COPPER, bold=True))

    # навантаження (від +V до стоку)
    f.append(line(xm, yV, xm, 150, color=POS, sw=3))
    f.append(rect(xm - 20, 150, 40, 46, fill="#f7faf8", stroke=INK, sw=1.8))
    f.append(text(xm + 30, 175, "навантаження", size=11, color=INK, anchor="start"))
    f.append(line(xm, 196, xm, cy - 32, color=POS, sw=3))   # до стоку

    # MOSFET
    f.append(mosfet(xm, cy))
    f.append(text(xm + 40, cy - 30, "D", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(xm + 40, cy + 40, "S", size=12, color=INK, bold=True, anchor="start"))
    f.append(text(xm - 38, cy - 6, "G", size=12, color=INK, bold=True, anchor="end"))

    # витік → GND
    f.append(line(xm, cy + 32, xm, yG, color=POS, sw=3))
    ysrc = cy + 32
    f.append(circle(xm, ysrc + 60, 4.5, fill=INK, stroke=INK))   # вузол витоку на шляху

    # драйвер (внизу зліва)
    dx, dy = 250, 300
    f.append(rect(dx - 55, dy - 30, 110, 60, fill="#eef7f0", stroke=FIELD, sw=2))
    f.append(mtext(dx, dy - 4, ["драйвер", "затвора"], size=12, color=FIELD, bold=True))
    # вихід драйвера → затвор
    f.append(line(dx + 55, dy - 12, 430, dy - 12, color=NEG, sw=2.4))
    f.append(line(430, dy - 12, 430, cy, color=NEG, sw=2.4))
    f.append(line(430, cy, xm - 32, cy, color=NEG, sw=2.4))
    f.append(rect(452, cy - 10, 22, 20, fill="#fff", stroke=INK, sw=1.4))  # Rg
    f.append(text(463, cy - 16, "Rg", size=10, color=INK))
    # земля драйвера → витік
    f.append(line(dx + 55, dy + 14, xm, dy + 14, color=NEG, sw=2.4))
    f.append(line(xm, dy + 14, xm, ysrc + 60, color=NEG, sw=2.4))

    # підсвітка силової петлі (права, висока)
    f.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" '
             'fill-opacity="0.07"/>' % (xcap - 6, yV - 6, (xm) - xcap + 12, yG - yV + 12, POS))
    f.append(text(455, 130, "СИЛОВА ПЕТЛЯ", size=13, color=POS, bold=True))
    f.append(text(455, 360, "різаний струм навантаження", size=11, color=POS))

    # підсвітка затворної петлі (ліва, низька) — контур без заливки
    f.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" fill="%s" '
             'fill-opacity="0.09"/>' % (dx - 62, dy - 34, (xm) - (dx - 62) + 6, 82, FIELD))
    f.append(text(dx, dy - 48, "ЗАТВОРНА ПЕТЛЯ", size=13, color=FIELD, bold=True))
    f.append(text(dx + 30, dy + 58, "заряд у затвор і назад", size=11, color=FIELD))

    # спільний вузол
    f.append(text(xm + 16, ysrc + 64, "← спільний вузол: витік", size=11, color=INK,
                  anchor="start", bold=True))

    render(os.path.join(OUT, "two-loops.svg"), W, H, *f,
           title="Дві петлі ключа: силова й затворна діляться витоком")


# ── 2. Спільна індуктивність витоку і Kelvin-джерело ────────────────────────
def fig_kelvin():
    W, H = 840, 440
    f = []

    def block(x0, good, head, hc):
        f.append(text(x0 + 150, 66, head, size=14, color=hc, bold=True))
        cy = 200
        xm = x0 + 150
        f.append(mosfet(xm, cy, w=58, h=58))
        # стік угору
        f.append(line(xm, cy - 29, xm, 110, color=POS, sw=3))
        f.append(text(xm, 100, "стік → +V", size=10, color=POS))
        # драйвер зліва
        f.append(rect(x0 + 20, cy - 22, 74, 44, fill="#eef7f0", stroke=FIELD, sw=1.8))
        f.append(text(x0 + 57, cy + 4, "драйвер", size=11, color=FIELD, bold=True))
        f.append(line(x0 + 94, cy - 10, xm - 29, cy - 10, color=NEG, sw=2.2))  # → затвор

        if not good:
            # один вивід витоку: силовий струм І зворот затвора йдуть спільним шматком
            f.append(line(xm, cy + 29, xm, 330, color=POS, sw=6))     # товста силова мідь
            # позначка індуктивності на спільному шматку
            f.append(text(xm + 14, 300, "Lспільна", size=11, color=POS, bold=True, anchor="start"))
            f.append(text(xm + 14, 316, "V = L·di/dt", size=10, color=POS, anchor="start"))
            f.append(line(xm, 330, xm, 360, color=INK, sw=6))
            f.append(text(xm, 380, "GND", size=11, color=INK, bold=True))
            # зворот драйвера чіпляється на ту саму силову мідь
            f.append(line(x0 + 57, cy + 22, x0 + 57, 300, color=NEG, sw=2.2))
            f.append(line(x0 + 57, 300, xm, 300, color=NEG, sw=2.2))
            f.append(circle(xm, 300, 4.5, fill=INK, stroke=INK))
            f.append(text(x0 + 40, 288, "зворот затвора на силовій міді", size=9.5,
                          color=POS, anchor="start"))
            f.append(text(x0 + 150, 410, "силовий струм бореться з драйвером",
                          size=11, color=POS, bold=True))
        else:
            # два виводи: силовий витік окремо, Kelvin окремо
            f.append(line(xm - 8, cy + 29, xm - 8, 360, color=POS, sw=6))   # силовий витік
            f.append(text(xm - 40, 350, "силовий", size=9.5, color=POS, anchor="end"))
            f.append(text(xm - 8, 380, "GND", size=11, color=INK, bold=True))
            f.append(line(xm + 12, cy + 24, xm + 12, 300, color=FIELD, sw=2.2))  # Kelvin
            f.append(text(xm + 20, 250, "Kelvin-витік", size=10, color=FIELD,
                          bold=True, anchor="start"))
            # зворот драйвера на Kelvin
            f.append(line(x0 + 57, cy + 22, x0 + 57, 300, color=FIELD, sw=2.2))
            f.append(line(x0 + 57, 300, xm + 12, 300, color=FIELD, sw=2.2))
            f.append(circle(xm + 12, 300, 4.5, fill=FIELD, stroke=FIELD))
            f.append(text(x0 + 150, 410, "затвор не бачить силового di/dt",
                          size=11, color=FIELD, bold=True))

    block(20, False, "БЕЗ Kelvin — погано", POS)
    f.append(line(420, 60, 420, 420, color=MUTED, sw=1, dash="5,5"))
    block(440, True, "З Kelvin-витоком — добре", FIELD)

    render(os.path.join(OUT, "kelvin-source.svg"), W, H, *f,
           title="Спільна індуктивність витоку і як її прибирає Kelvin-вивід")


# ── 3. Викид і дзвін на стоку: мала проти великої петлі ─────────────────────
def fig_overshoot():
    W, H = 855, 430
    f = []
    x0, x1 = 95, 750
    ybase, ytop = 370, 90
    Vmax = 45.0

    def vy(v):
        return ybase - (v / Vmax) * (ybase - ytop)

    def tx(frac):
        return x0 + frac * (x1 - x0)

    # осі
    f.append(line(x0, ytop, x0, ybase, color=INK, sw=1.6))
    f.append(line(x0, ybase, x1, ybase, color=INK, sw=1.6))
    f.append(text(x0 - 10, ytop + 2, "Vси", size=12, color=INK, anchor="end", bold=True))
    f.append(text(x1, ybase + 20, "час", size=12, color=INK, anchor="end"))

    # опорні рівні
    for v, lab, col in [(24, "Vшини = 24 В", NEG), (30, "межа ключа = 30 В", POS)]:
        f.append(line(x0, vy(v), x1, vy(v), color=col, sw=1.3, dash="6,4"))
        f.append(text(x1 + 4, vy(v) + 4, lab, size=10, color=col, anchor="start"))

    # криві: до t0 ≈ 0 (ключ відкритий), після — викид + згасний дзвін навколо 24
    t0 = 0.28

    def curve(A, decay, cycles, col, sw):
        pts = []
        N = 260
        for i in range(N + 1):
            fr = i / N
            if fr < t0:
                v = 1.0
            else:
                u = (fr - t0) / (1 - t0)
                if u < 0.05:                       # швидкий фронт до піка
                    v = 1.0 + (24 + A - 1.0) * (u / 0.05)
                else:
                    env = math.exp(-decay * u)
                    v = 24 + A * env * math.cos(2 * math.pi * cycles * (u - 0.05))
            pts.append("%.1f,%.1f" % (tx(fr), vy(max(0, v))))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (" ".join(pts), col, sw))

    # велика петля — високий викид за межу, довгий дзвін
    f.append(curve(15.0, 2.2, 5.5, POS, 2.4))
    # мала петля — низький викид, швидко тихне
    f.append(curve(5.0, 6.0, 3.0, FIELD, 2.6))

    f.append(line(tx(t0), ybase, tx(t0), ytop, color=MUTED, sw=1, dash="3,3"))
    f.append(text(tx(t0), ybase + 20, "вимкнення", size=10, color=MUTED))

    # підписи кривих
    f.append(text(tx(0.52), vy(41), "велика петля: викид +15 В → пробій",
                  size=11, color=POS, bold=True, anchor="start"))
    f.append(text(tx(0.52), vy(30.5) - 4, "мала петля: викид +5 В, швидко тихне",
                  size=11, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "overshoot-ring.svg"), W, H, *f,
           title="Напруга на стоку при вимкненні: площа петлі задає викид")


# ── 4. Тепловий шлях: стокова мідь як радіатор ──────────────────────────────
def fig_thermal():
    W, H = 820, 440
    f = []

    # ── переріз плати (ліворуч) ──
    bx = 70
    board_w = 300
    ytopcu = 250
    f.append(text(bx + board_w / 2, 66, "переріз: куди йде тепло", size=13, color=INK, bold=True))
    # тіло FR4
    f.append(rect(bx, ytopcu, board_w, 60, fill="#efe6d6", stroke=MUTED, sw=1.4))
    f.append(text(bx + board_w - 6, ytopcu + 35, "FR4", size=10, color=MUTED, anchor="end"))
    # верхня мідь (полігон стоку)
    f.append(rect(bx, ytopcu - 12, board_w, 12, fill=COPPER, stroke="none"))
    f.append(text(bx + 4, ytopcu - 16, "полігон стоку", size=10, color=COPPER,
                  anchor="start", bold=True))
    # нижня мідь
    f.append(rect(bx, ytopcu + 60, board_w, 12, fill=COPPER, stroke="none"))
    f.append(text(bx + 4, ytopcu + 50, "мідь звороту", size=10, color=COPPER,
                  anchor="start", bold=True))
    # MOSFET на верхній міді
    mx = bx + 90
    f.append(rect(mx, ytopcu - 44, 90, 32, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(mx + 45, ytopcu - 24, "MOSFET", size=11, color=NEG, bold=True))
    f.append(text(mx + 45, ytopcu - 50, "кристал гріється: P = I²·Ron", size=10, color=POS))
    # теплові via
    for k in range(5):
        vx = mx + 12 + k * 17
        f.append(line(vx, ytopcu, vx, ytopcu + 60, color=INK, sw=3))
    f.append(text(mx - 8, ytopcu + 40, "теплові via", size=10, color=INK, anchor="end"))
    # стрілки тепла вниз і в повітря
    for k in range(3):
        ax = bx + 60 + k * 90
        f.append(arrow(ax, ytopcu + 82, ax, ytopcu + 106, color=POS, sw=2))
    f.append(text(bx + board_w / 2, ytopcu + 124, "тепло в повітря / корпус",
                  size=10, color=POS))

    # ── ланцюжок теплових опорів (праворуч) ──
    rx = 470
    f.append(text(rx + 130, 66, "тепловий опір → температура", size=13, color=INK, bold=True))
    steps = [("кристал", "P = 0.8 Вт", POS),
             ("θ мала мідь", "≈ 62 °C/Вт → +50 °C", POS),
             ("θ полігон + via", "≈ 30 °C/Вт → +24 °C", FIELD),
             ("повітря", "оточення", INK)]
    y = 110
    for i, (a, b, col) in enumerate(steps):
        f.append(fitbox(rx, y, 260, 44, a + "\n" + b, size=12, fill="#f7faf8",
                        stroke=col, color=INK))
        if i < len(steps) - 1:
            f.append(arrow(rx + 130, y + 44, rx + 130, y + 62, color=INK, sw=2))
        y += 62

    render(os.path.join(OUT, "thermal-copper.svg"), W, H, *f,
           title="Стокова мідь — радіатор: полігон і via ведуть тепло з кристала")


# ── 5. Стендовий прийом: зсув частоти дзвону від доданої ємності ─────────────
def fig_ring_shift():
    W, H = 880, 440
    f = []

    def panel(x0, w, cycles, decay, flab, sub, subcol, cx_note=None):
        yb, yt = 350, 110
        yrail = (yb + yt) / 2 + 20
        f.append(rect(x0, yt - 10, w, yb - yt + 30, fill="#fbfcfe", stroke=MUTED, sw=1.2))
        f.append(line(x0 + 12, yrail, x0 + w - 12, yrail, color=MUTED, sw=1, dash="5,4"))
        f.append(text(x0 + w - 14, yrail - 6, "Vшини", size=10, color=MUTED, anchor="end"))
        xa, xb = x0 + 30, x0 + w - 20
        amp = 74
        pts = []
        N = 300
        for i in range(N + 1):
            fr = i / N
            env = math.exp(-decay * fr)
            v = -amp * env * math.cos(2 * math.pi * cycles * fr)
            pts.append("%.1f,%.1f" % (xa + fr * (xb - xa), yrail + v))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(pts), POS))
        # позначка одного періоду (перші два піки: fr=0 і fr=1/cycles)
        xp0 = xa
        xp1 = xa + (1.0 / cycles) * (xb - xa)
        ytk = yt + 8
        f.append(line(xp0, ytk, xp1, ytk, color=INK, sw=1.4))
        f.append(line(xp0, ytk - 5, xp0, ytk + 5, color=INK, sw=1.4))
        f.append(line(xp1, ytk - 5, xp1, ytk + 5, color=INK, sw=1.4))
        f.append(text((xp0 + xp1) / 2, ytk - 7, "T = 1/f", size=11, color=INK, bold=True))
        f.append(text(x0 + w / 2, yb + 36, flab, size=15, color=subcol, bold=True))
        f.append(text(x0 + w / 2, yb + 56, sub, size=11, color=subcol))
        if cx_note:
            f.append(text(x0 + w / 2, yt - 20, cx_note, size=12, color=FIELD, bold=True))

    panel(30, 380, 4.6, 1.15, "f₁ ≈ 112 МГц", "як є: L і Coss разом", POS)
    f.append(arrow(420, 240, 470, 240, color=INK, sw=2.4))
    f.append(text(445, 224, "+ Cx", size=13, color=FIELD, bold=True))
    panel(470, 380, 2.5, 0.75, "f₂ ≈ 61 МГц", "додали відому ємність Cx", FIELD,
          cx_note="Cx на стік–витік")

    render(os.path.join(OUT, "ring-shift.svg"), W, H, *f,
           title="Дзвін звучить нижче, коли додати відому ємність")


# ── 6. Частота дзвону vs повна ємність вузла: два виміри пришпилюють криву ────
def fig_freq_vs_cap():
    W, H = 820, 480
    f = []
    L = 10e-9
    Cmin, Cmax = 120e-12, 900e-12
    fmax = 130.0
    x0, x1 = 110, 720
    yb, yt = 380, 90

    def fx(C):
        return x0 + (C - Cmin) / (Cmax - Cmin) * (x1 - x0)

    def fy(fMHz):
        return yb - (fMHz / fmax) * (yb - yt)

    def fofC(C):
        return 1.0 / (2 * math.pi * math.sqrt(L * C)) / 1e6

    # осі
    f.append(line(x0, yt, x0, yb, color=INK, sw=1.6))
    f.append(line(x0, yb, x1, yb, color=INK, sw=1.6))
    f.append(text(x0 - 8, yt - 2, "f, МГц", size=12, color=INK, anchor="end", bold=True))

    # сітка по f
    for fv in (50, 100):
        f.append(line(x0, fy(fv), x1, fy(fv), color="#e6e8ec", sw=1))
        f.append(text(x0 - 8, fy(fv) + 4, str(fv), size=10, color=MUTED, anchor="end"))
    # сітка по C
    for Cv in (400, 600, 800):
        f.append(text(fx(Cv * 1e-12), yb + 16, str(Cv), size=10, color=MUTED))
    # Coss-позначка замість «200»
    f.append(text(fx(200e-12) - 4, yb + 16, "200", size=10, color=POS, bold=True, anchor="end"))
    f.append(text(fx(200e-12) + 14, yb + 16, "= Coss", size=10, color=POS, bold=True, anchor="start"))

    # крива f(C)
    pts = []
    N = 220
    for i in range(N + 1):
        C = Cmin + (Cmax - Cmin) * i / N
        pts.append("%.1f,%.1f" % (fx(C), fy(fofC(C))))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), NEG))
    f.append(text(fx(300e-12), fy(fofC(300e-12)) - 34, "f = 1/(2π√(LC))",
                  size=12, color=NEG, bold=True, anchor="start"))

    # точки вимірів
    C0, Cx = 200e-12, 470e-12
    A = (C0, fofC(C0))
    B = (C0 + Cx, fofC(C0 + Cx))
    for (C, fv, lab, col) in ((A[0], A[1], "f₁", POS), (B[0], B[1], "f₂", FIELD)):
        f.append(line(x0, fy(fv), fx(C), fy(fv), color=col, sw=1.2, dash="5,4"))
        f.append(line(fx(C), fy(fv), fx(C), yb, color=col, sw=1.2, dash="5,4"))
        f.append(circle(fx(C), fy(fv), 5, fill=col, stroke=col))
        f.append(text(x0 + 8, fy(fv) - 6, lab, size=13, color=col, bold=True, anchor="start"))

    # крок Cx між x(A) і x(B)
    ybr = yb + 40
    f.append(line(fx(A[0]), ybr, fx(B[0]), ybr, color=FIELD, sw=1.6))
    f.append(line(fx(A[0]), ybr - 5, fx(A[0]), ybr + 5, color=FIELD, sw=1.6))
    f.append(line(fx(B[0]), ybr - 5, fx(B[0]), ybr + 5, color=FIELD, sw=1.6))
    f.append(text((fx(A[0]) + fx(B[0])) / 2, ybr + 18, "Cx (відоме)", size=11,
                  color=FIELD, bold=True))

    # вісь C — підпис
    f.append(text((x0 + x1) / 2, 462, "повна ємність вузла  C = Coss + Cx,  пФ",
                  size=12, color=INK))

    # результат-бокси
    f.append(fitbox(560, 118, 232, 40, "Coss = Cx / [(f₁/f₂)² − 1]",
                    size=12, stroke=POS, color=INK))
    f.append(fitbox(560, 166, 232, 40, "L = 1 / [(2π·f₁)²·Coss]",
                    size=12, stroke=NEG, color=INK))

    render(os.path.join(OUT, "freq-vs-cap.svg"), W, H, *f,
           title="Дві виміряні частоти пришпилюють криву — і дають L та Coss")


# ── 7. Спад віддачі від міді: θ_JA vs площа полігону (вставка proj) ──────────
def _theta_ja(A, N):
    """Насичувальна модель θ_JA(площа см², via) — та сама, що в калькуляторі."""
    floor = 40.0 - (40.0 - 22.0) * N / (N + 10.0)
    board = floor + (60.0 - floor) * 1.0 / (A + 1.0)
    return 1.5 + board


def fig_copper_returns():
    W, H = 880, 500
    f = []
    x0, x1 = 120, 700
    ybase, ytop = 420, 100
    Amax = 10.5
    th_lo, th_hi = 20.0, 65.0

    def vx(a):
        return x0 + (a / Amax) * (x1 - x0)

    def vy(th):
        return ybase - (th - th_lo) / (th_hi - th_lo) * (ybase - ytop)

    # затінена «зона коліна» — де живе весь виграш (0..2 см²)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
             'fill-opacity="0.07"/>' % (vx(0), ytop, vx(2) - vx(0), ybase - ytop, FIELD))
    f.append(text((vx(0) + vx(2)) / 2, ytop - 8, "зона коліна", size=11,
                  color=FIELD, bold=True))

    # осі
    f.append(line(x0, ytop, x0, ybase, color=INK, sw=1.6))
    f.append(line(x0, ybase, x1, ybase, color=INK, sw=1.6))
    f.append(text(x0 - 12, ytop + 4, "θ_JA", size=12, color=INK, anchor="end", bold=True))
    f.append(text(x0 - 12, ytop + 20, "К/Вт", size=10, color=MUTED, anchor="end"))

    # сітка по θ
    for tv in (30, 40, 50, 60):
        f.append(line(x0, vy(tv), x1, vy(tv), color="#e6e8ec", sw=1))
        f.append(text(x0 - 10, vy(tv) + 4, str(tv), size=10, color=MUTED, anchor="end"))
    # позначки по площі
    for av in (0, 2, 4, 6, 8, 10):
        f.append(line(vx(av), ybase, vx(av), ybase + 5, color=INK, sw=1.2))
        f.append(text(vx(av), ybase + 20, str(av), size=10, color=MUTED))
    f.append(text((x0 + x1) / 2, ybase + 42, "площа полігону стоку, см²",
                  size=12, color=INK))

    # дві криві
    def curve(N, col):
        pts = []
        M = 240
        for i in range(M + 1):
            a = 0.02 + (Amax - 0.02) * i / M
            pts.append("%.1f,%.1f" % (vx(a), vy(_theta_ja(a, N))))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
                % (" ".join(pts), col))

    f.append(curve(0, POS))
    f.append(curve(20, FIELD))
    # підписи кривих біля правих кінців
    f.append(text(x1 + 8, vy(_theta_ja(Amax, 0)) + 4, "без via", size=11,
                  color=POS, bold=True, anchor="start"))
    f.append(text(x1 + 8, vy(_theta_ja(Amax, 20)) + 4, "20 via", size=11,
                  color=FIELD, bold=True, anchor="start"))

    # гола площадка (A→0): обидві криві стартують ~61.5
    f.append(circle(vx(0.02), vy(61.5), 4.5, fill=INK, stroke=INK))
    f.append(text(vx(0.4), vy(61.5) - 10, "гола площадка ≈ 62 К/Вт", size=11,
                  color=INK, anchor="start", bold=True))

    # маржинальний виграш за кожен доданий см² — окремим акуратним боксом
    lines = ["Δθ за кожен +1 см² (без via):",
             "0 → 1 см² :  −10.0 К/Вт",
             "1 → 2 см² :   −3.3",
             "2 → 3 см² :   −1.7",
             "3 → 4 см² :   −1.0"]
    f.append(fitbox(vx(4.4), vy(64), 250, 96, "\n".join(lines), size=11,
                    fill="#fbfcfe", stroke=MUTED, color=INK))

    render(os.path.join(OUT, "copper-returns.svg"), W, H, *f,
           title="Мідь наситься: перший см² — майже весь виграш")


# ── 8. Важелі індуктивності: лінійний проти логарифмічних (вставка proj) ─────
def fig_l_levers():
    W, H = 820, 360
    f = []
    x0, xmax = 340, 770
    Lmax = 30.0
    per = (xmax - x0) / Lmax

    rows = [("базова петля", "30 / 2.0 / 0.8 мм", 28.5, POS,
             "з чого починаємо"),
            ("довжина 30 → 10 мм", "лінійно ↓", 9.5, FIELD,
             "утричі коротше — утричі менше L"),
            ("просвіт 2.0 → 0.5 мм", "логарифм", 11.8, MUTED,
             "учетверо тісніше — лише третину"),
            ("ширина 0.8 → 3 мм", "логарифм", 13.0, MUTED,
             "учетверо ширше — теж кволо")]

    y = 78
    dy = 66
    f.append(line(x0, 60, x0, y + 3 * dy + 30, color=MUTED, sw=1, dash="4,4"))
    for name, how, L, col, note in rows:
        bw = L * per
        f.append(text(x0 - 14, y + 6, name, size=12.5, color=INK, anchor="end", bold=True))
        f.append(text(x0 - 14, y + 23, how, size=10, color=MUTED, anchor="end"))
        f.append(rect(x0, y - 12, bw, 34, fill=col, stroke="none", rx=4))
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="34" rx="4" '
                 'fill="%s" fill-opacity="0.16"/>' % (x0, y - 12, bw, col))
        f.append(text(x0 + bw + 12, y + 9, "%.1f нГн" % L, size=13, color=col,
                      anchor="start", bold=True))
        y += dy

    f.append(text((x0 + xmax) / 2, y + 6,
                  "тільки довжина — поза логарифмом; за неї й тягнути першою",
                  size=12, color=INK))

    render(os.path.join(OUT, "l-levers.svg"), W, H, *f,
           title="Три важелі проти L петлі: один лінійний, два кволі")


if __name__ == "__main__":
    fig_two_loops()
    fig_kelvin()
    fig_overshoot()
    fig_thermal()
    fig_ring_shift()
    fig_freq_vs_cap()
    fig_copper_returns()
    fig_l_levers()
    print("ok figs")
