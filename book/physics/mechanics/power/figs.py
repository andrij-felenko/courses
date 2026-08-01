# -*- coding: utf-8 -*-
"""Фігури до статті «Потужність» (book/physics/mechanics/power)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_power_is_rate():
    """Однакова робота, різний час → різна потужність."""
    W, H = 760, 440
    top_y, ground_y = 150, 350
    xL, xR = 210, 550
    bw, bh = 64, 46
    f = []
    # рівні висоти
    f.append(line(100, top_y, 660, top_y, color=MUTED, sw=1.2, dash="6 5"))
    f.append(line(100, ground_y, 660, ground_y, color=INK, sw=2))
    # розмір h
    f.append(line(125, top_y, 125, ground_y, color=INK, sw=1.5))
    f.append(line(119, top_y, 131, top_y, color=INK, sw=1.5))
    f.append(line(119, ground_y, 131, ground_y, color=INK, sw=1.5))
    f.append(text(110, (top_y + ground_y) / 2 + 5, "h", size=15, bold=True, anchor="end"))
    # дві колони: швидко / повільно
    for cx, tlabel in [(xL, "за t = 2 с"), (xR, "за t = 60 с")]:
        f.append(rect(cx - bw / 2, ground_y - bh, bw, bh, fill="none", stroke=MUTED, sw=1.4, rx=4))
        f.append(text(cx, ground_y - bh / 2 + 5, "старт", size=12, color=MUTED))
        f.append(arrow(cx, ground_y - bh - 4, cx, top_y + bh + 6, color=INK, sw=2.2))
        f.append(rect(cx - bw / 2, top_y, bw, bh, fill=FILL, stroke=INK, sw=1.8))
        f.append(text(cx, top_y + bh / 2 + 6, "m", size=17, bold=True))
        f.append(text(cx, ground_y + 30, tlabel, size=15, bold=True))
    # ярлики потужності
    tagL, _, _ = textbox(340, 92, "P = W / 2 с\nбільша", size=14,
                         fill="#fdecea", stroke=POS, color=POS, bold=True)
    tagR, _, _ = textbox(660, 92, "P = W / 60 с\nменша", size=14,
                         fill="#eaf0fd", stroke=NEG, color=NEG, bold=True)
    f.append(tagL)
    f.append(tagR)
    # нижня смуга з формулами
    f.append(text(W / 2, 420, "однакова робота  W = m·g·h        потужність  P = W / t", size=15))
    render(os.path.join(OUT, "power-is-rate.svg"), W, H, *f,
           title="Однакова робота — різна потужність")


def fig_constant_power():
    """Гіпербола сталої потужності: розмін сили на швидкість."""
    W, H = 720, 480
    X0, X1 = 90, 660
    Y0, Y1 = 400, 70
    P = 6.0
    vmax, Fmax = 5.5, 7.0
    sx = lambda v: X0 + v / vmax * (X1 - X0)
    sy = lambda Fv: Y0 + Fv / Fmax * (Y1 - Y0)
    f = []
    # осі
    f.append(arrow(X0, Y0, X0, 58, color=INK, sw=2))
    f.append(arrow(X0, Y0, 672, Y0, color=INK, sw=2))
    f.append(text(X0 - 8, 66, "сила F", size=14, bold=True, anchor="end"))
    f.append(text(672, Y0 + 26, "швидкість v", size=14, bold=True, anchor="end"))
    # гіпербола F = P / v
    pts = []
    v = 0.95
    while v <= 5.25:
        pts.append("%.1f,%.1f" % (sx(v), sy(P / v)))
        v += 0.05
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (" ".join(pts), POS))
    # точки A (низька передача) та B (висока передача)
    for vv, dx in [(1.2, -14), (4.0, 14)]:
        x, y = sx(vv), sy(P / vv)
        f.append(line(x, y, x, Y0, color=MUTED, sw=1.3, dash="5 4"))
        f.append(line(x, y, X0, y, color=MUTED, sw=1.3, dash="5 4"))
        f.append(circle(x, y, 5.5, fill=INK, stroke=INK, sw=1))
    f.append(text(sx(1.2) - 14, sy(P / 1.2) - 8, "A", size=16, bold=True))
    f.append(text(sx(4.0) + 14, sy(P / 4.0) - 8, "B", size=16, bold=True))
    # легенда у вільному верхньо-правому куті
    lg, _, _ = textbox(478, 132,
        "Крива сталої потужності:  F · v = P\n"
        "A — велика сила, мала швидкість\n"
        "B — мала сила, велика швидкість\n"
        "уздовж кривої потужність незмінна",
        size=13, fill=FILL, stroke=LINE, color=INK)
    f.append(lg)
    render(os.path.join(OUT, "constant-power-hyperbola.svg"), W, H, *f,
           title="Та сама потужність: сила проти швидкості")


def fig_horse_gin():
    """Кінний коловорот, за яким Ватт полічив «одного коня» (вставка hist)."""
    W, H = 760, 490
    cx, cy, R = 380, 210, 110
    f = []
    # коло — шлях, яким ходить кінь
    f.append(circle(cx, cy, R, fill="none", stroke=MUTED, sw=1.6))
    # вал і важіль (радіус)
    f.append(line(cx, cy, cx + R, cy, color=INK, sw=1.8))
    f.append(circle(cx, cy, 5, fill=INK, stroke=INK, sw=1))
    f.append(text(cx, cy + 24, "вал млина", size=12, color=MUTED))
    f.append(text(cx + 55, cy - 10, "R = 12 футів", size=13))
    # кінь на колі
    f.append(circle(cx + R, cy, 6, fill=INK, stroke=INK, sw=1))
    horse, hw, hh = textbox(560, cy, "кінь", size=13, fill=FILL, stroke=INK, bold=True)
    f.append(line(cx + R + 8, cy, 560 - hw / 2 - 2, cy, color=MUTED, sw=1.2))
    f.append(horse)
    # сила, з якою кінь тягне важіль (дотична, рух за годинниковою)
    f.append(arrow(cx + R, cy + 12, cx + R, cy + 90, color=POS, sw=2.4))
    f.append(text(500, cy + 58, "F = 180 фунтів-сили", size=13, color=POS, anchor="start"))
    # дуга напрямку обертання (ліворуч, за годинниковою стрілкою)
    f.append('<path d="M 252.0 232.6 A 130 130 0 0 1 267.4 145.0" fill="none" '
             'stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>' % INK)
    f.append(mtext(140, 184, "2.4 оберти\nза хвилину", size=13, bold=True))
    # підсумкова арифметика
    calc, _, _ = textbox(380, 425,
        "шлях коня за хвилину:  s = 2.4 · 2π · 12 ≈ 181 фут\n"
        "робота за хвилину:  180 · 181 ≈ 32 572 фут·фунта\n"
        "Ватт округлив: 33 000 фут·фунтів/хв = 550 фут·фунтів/с",
        size=13, fill=FILL, stroke=LINE, color=INK)
    f.append(calc)
    render(os.path.join(OUT, "horse-gin.svg"), W, H, *f,
           title="Кінний коловорот, за яким Ватт полічив «одного коня»")


def fig_hp_family():
    """Скільки ватів у «кінській силі»: метрична, механічна, електрична."""
    W, H = 760, 400
    AX = 230
    x0, x1 = 110.0, 690.0
    w0, w1 = 733.0, 748.0
    sx = lambda w: x0 + (w - w0) / (w1 - w0) * (x1 - x0)
    f = []
    # вісь у ватах
    f.append(line(x0, AX, x1, AX, color=INK, sw=2))
    f.append(text(700, AX + 5, "Вт", size=13, anchor="start"))
    for w in (735, 740, 745):
        f.append(line(sx(w), AX, sx(w), AX + 8, color=INK, sw=1.4))
        f.append(text(sx(w), AX + 26, str(w), size=12, color=MUTED))
    # метрична кінська сила
    xps = sx(735.49875)
    f.append(line(xps, AX, xps, 199, color=NEG, sw=1.6))
    f.append(circle(xps, AX, 4.5, fill=NEG, stroke=NEG, sw=1))
    bps, _, _ = textbox(206, 172,
        "метрична к.с.  (PS, ch, cv, к.с.)\n75 кгс·м/с = 735.49875 Вт",
        size=13, fill="#eaf0fd", stroke=NEG, color=INK)
    f.append(bps)
    # механічна (imperial) horsepower
    xhp = sx(745.69987)
    f.append(line(xhp, AX, xhp, 199, color=POS, sw=1.6))
    f.append(circle(xhp, AX, 4.5, fill=POS, stroke=POS, sw=1))
    bhp, _, _ = textbox(560, 172,
        "механічна hp (imperial)\n550 фут·фунтів/с = 745.69987 Вт",
        size=13, fill="#fdecea", stroke=POS, color=INK)
    f.append(bhp)
    # електрична кінська сила
    xeh = sx(746.0)
    f.append(line(xeh, AX, xeh, 273, color=MUTED, sw=1.6))
    f.append(circle(xeh, AX, 4.5, fill=MUTED, stroke=MUTED, sw=1))
    beh, _, _ = textbox(600, 300,
        "електрична hp (США)\nрівно 746 Вт",
        size=13, fill=FILL, stroke=MUTED, color=INK)
    f.append(beh)
    # проміжок між двома «кінськими силами»
    f.append(line(xps, 208, xps, 220, color=MUTED, sw=1.4))
    f.append(line(xhp, 208, xhp, 220, color=MUTED, sw=1.4))
    f.append(line(xps, 214, 350, 214, color=MUTED, sw=1.4))
    f.append(line(458, 214, xhp, 214, color=MUTED, sw=1.4))
    f.append(text(404, 219, "різниця 1.4 %", size=12, color=MUTED, bold=True))
    # котлова — зовсім не з цієї шкали
    note, _, _ = textbox(380, 358,
        "котлова к.с. (boiler hp) — зовсім інша величина: 9809.5 Вт ≈ 13.2 механічних",
        size=12, fill=FILL, stroke=LINE, color=MUTED)
    f.append(note)
    render(os.path.join(OUT, "hp-family.svg"), W, H, *f,
           title="Скільки ватів у «кінській силі»")


# ── Фігури до вставки proj-cycling-power ───────────────────────────────────
GRAV = 9.80665


def _pedal_power(v, mass=78.0, cda=0.30, crr=0.005, rho=1.225, eta=0.97, grade=0.0):
    """Та сама модель, що у вставці: ватти на педалях за швидкості v (м/с)."""
    th = math.atan(grade)
    f = (mass * GRAV * math.sin(th) + crr * mass * GRAV * math.cos(th)
         + 0.5 * rho * cda * v * v)
    return (f * v + v * (91.0 + 8.7 * v) * 1e-3) / eta


def fig_power_vs_speed():
    """Рівнина: кочення росте як v, повітря — як v³; де вони міняються місцями."""
    W, H = 800, 500
    X0, X1 = 100, 720
    Y0, Y1 = 415, 80
    VMAX, PMAX = 50.0, 600.0          # км/год і Вт
    MASS, CDA, CRR, RHO, ETA = 78.0, 0.30, 0.005, 1.225, 0.97
    sx = lambda kmh: X0 + kmh / VMAX * (X1 - X0)
    sy = lambda p: Y0 - p / PMAX * (Y0 - Y1)
    f = []
    # осі
    f.append(arrow(X0, Y0, X0, Y1 - 18, color=INK, sw=2))
    f.append(arrow(X0, Y0, X1 + 30, Y0, color=INK, sw=2))
    f.append(text(X0 + 6, Y1 - 32, "потужність на педалях, Вт", size=14, bold=True, anchor="start"))
    f.append(text(X1 + 28, Y0 + 40, "швидкість, км/год", size=14, bold=True, anchor="end"))
    for p in range(100, 601, 100):
        f.append(line(X0 - 6, sy(p), X0, sy(p), color=INK, sw=1.4))
        f.append(text(X0 - 12, sy(p) + 5, str(p), size=12, color=MUTED, anchor="end"))
    for kmh in range(10, 51, 10):
        f.append(line(sx(kmh), Y0, sx(kmh), Y0 + 6, color=INK, sw=1.4))
        f.append(text(sx(kmh), Y0 + 24, str(kmh), size=12, color=MUTED))
    # три криві
    def poly(fn, color, sw):
        pts = []
        for i in range(0, 201):
            kmh = VMAX * i / 200.0
            v = kmh / 3.6
            pts.append("%.1f,%.1f" % (sx(kmh), sy(fn(v))))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round"/>' % (" ".join(pts), color, sw))
    p_roll = lambda v: CRR * MASS * GRAV * v
    p_air = lambda v: 0.5 * RHO * CDA * v ** 3
    p_all = lambda v: _pedal_power(v, MASS, CDA, CRR, RHO, ETA, 0.0)
    f.append(poly(p_roll, NEG, 2.4))
    f.append(poly(p_air, POS, 2.4))
    f.append(poly(p_all, INK, 3.0))
    # легенда у порожньому лівому верху
    lx, ly = 140, 88
    f.append(rect(lx, ly, 300, 96, fill=BG, stroke=MUTED, sw=1.3))
    rows = [("разом на педалях (з ККД 0.97)", INK, 3.0),
            ("опір повітря  ∝ v³", POS, 2.4),
            ("тертя кочення  ∝ v", NEG, 2.4)]
    for i, (lab, col, sw) in enumerate(rows):
        ry = ly + 26 + i * 26
        f.append(line(lx + 16, ry, lx + 46, ry, color=col, sw=sw))
        f.append(text(lx + 58, ry + 5, lab, size=13, anchor="start"))
    # точка перетину: кочення = повітря
    v_cross = math.sqrt(CRR * MASS * GRAV / (0.5 * RHO * CDA))
    kmh_cross = v_cross * 3.6
    f.append(line(sx(kmh_cross), Y0, sx(kmh_cross), 258, color=MUTED, sw=1.4, dash="6 5"))
    note, _, _ = textbox(sx(kmh_cross), 228,
                         "≈%.0f км/год\nвище повітря дорожче за кочення" % kmh_cross,
                         size=12, fill=BG, stroke=MUTED, color=MUTED)
    f.append(note)
    # робоча точка 36 км/год
    v36 = 10.0
    p36 = p_all(v36)
    f.append(line(sx(36), Y0, sx(36), sy(p36), color=MUTED, sw=1.3, dash="5 4"))
    f.append(circle(sx(36), sy(p36), 6, fill=INK, stroke=INK, sw=1))
    f.append(text(sx(36) - 16, sy(p36) - 14, "36 км/год → %.0f Вт" % p36,
                  size=13, bold=True, anchor="end"))
    render(os.path.join(OUT, "cycling-power-vs-speed.svg"), W, H, *f,
           title="Рівнина: куди зростають ватти зі швидкістю")


def fig_watts_path():
    """Шлях ватів від педалей до дороги: де сидить ККД і де міряють вимірювачі."""
    W, H = 860, 440
    f = []
    yc = 200
    boxA, wA, hA = textbox(120, yc, "ноги на педалях\n299 Вт", size=14, bold=True)
    boxB, wB, hB = textbox(310, yc, "трансмісія\nη = 0.97", size=14)
    boxC, wC, hC = textbox(490, yc, "на колесі\n290 Вт", size=14, bold=True)
    f += [boxA, boxB, boxC]
    f.append(arrow(120 + wA / 2 + 6, yc, 310 - wB / 2 - 6, yc, color=INK, sw=2.2))
    f.append(arrow(310 + wB / 2 + 6, yc, 490 - wC / 2 - 6, yc, color=INK, sw=2.2))
    # чотири статті витрат
    outs = [(95, "тяжіння  259 Вт"), (160, "кочення  16 Вт"),
            (230, "повітря  14.5 Вт"), (300, "підшипники  0.5 Вт")]
    for oy, lab in outs:
        f.append(arrow(490 + wC / 2 + 6, yc, 631, oy, color=MUTED, sw=1.8))
        bx, _, _ = textbox(720, oy, lab, size=13, min_w=170)
        f.append(bx)
    # втрата в трансмісії — вниз, у тепло
    f.append(arrow(310, yc + hB / 2 + 6, 310, 274, color=POS, sw=2.2))
    lossbox, _, _ = textbox(310, 300, "−9 Вт у нагрів ланцюга", size=13,
                            fill="#fdecea", stroke=POS, color=POS, bold=True)
    f.append(lossbox)
    # де стоять вимірювачі
    m1, _, hm1 = textbox(120, 105, "вимірювач у шатунах\nчи педалях міряє тут",
                         size=13, fill="#eaf0fd", stroke=NEG, color=NEG)
    f.append(m1)
    f.append(arrow(120, 105 + hm1 / 2 + 4, 120, yc - hA / 2 - 6, color=NEG, sw=1.8))
    m2, _, hm2 = textbox(500, 332, "вимірювач у втулці\nміряє тут",
                         size=13, fill="#eaf0fd", stroke=NEG, color=NEG)
    f.append(m2)
    f.append(arrow(500, 332 - hm2 / 2 - 4, 500, yc + hC / 2 + 6, color=NEG, sw=1.8))
    f.append(text(430, 418, "299 Вт на педалях = 290 Вт на колесі + 9 Вт у трансмісії",
                  size=13, color=MUTED))
    render(os.path.join(OUT, "cycling-watts-path.svg"), W, H, *f,
           title="Шлях 299 ватів: підйом 8.1 %, 15 км/год")


if __name__ == "__main__":
    fig_power_is_rate()
    fig_constant_power()
    fig_horse_gin()
    fig_hp_family()
    fig_power_vs_speed()
    fig_watts_path()
    print("OK: power figures ->", OUT)
