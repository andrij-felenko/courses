# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_two_slopes():
    """Нелінійна ВАХ: статичний опір = нахил січної до 0; диференційний = нахил дотичної."""
    W, H = 720, 470
    # осі
    ox, oy = 90, 400      # початок координат
    ax2, ay2 = 660, 70    # кінці осей
    frags = []
    frags.append(line(ox, oy, ax2, oy, color=INK, sw=2))           # вісь U
    frags.append(line(ox, oy, ox, ay2, color=INK, sw=2))           # вісь I
    frags.append(text(ax2 + 4, oy + 5, "U", size=16, bold=True, anchor="start"))
    frags.append(text(ox - 8, ay2 - 4, "I", size=16, bold=True, anchor="end"))

    # крива ВАХ (експонента діода), точки рахуємо у px
    import math
    def curve_y(px):
        # px у [ox..ax2]; нормуємо в [0..1] і беремо опуклу криву вгору
        t = (px - ox) / (ax2 - ox)
        v = t ** 0.5                       # опукла: швидко росте на старті
        return oy - v * (oy - ay2) * 0.92
    pts = []
    px = ox
    while px <= ax2:
        pts.append((px, curve_y(px)))
        px += 4
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # робоча точка Q
    qx = ox + (ax2 - ox) * 0.52
    qy = curve_y(qx)
    # січна з 0 (статичний опір) — пунктир від (ox,oy) до Q, трохи продовжена,
    # але обрізана по верхньому краю поля, щоб не вилазила за viewBox
    k_sec = (qy - oy) / (qx - ox)
    sy2 = ay2 + 10
    sx2 = ox + (sy2 - oy) / k_sec
    frags.append(line(ox, oy, sx2, sy2, color=MUTED, sw=2, dash="7 5"))

    # дотична в Q (диференційний опір) — нахил похідної кривої в Q
    h = 1.0
    k_tan = (curve_y(qx + h) - curve_y(qx - h)) / (2 * h)
    tx1, tx2 = qx - 120, qx + 120
    ty1 = qy + k_tan * (tx1 - qx)
    ty2 = qy + k_tan * (tx2 - qx)
    frags.append(line(tx1, ty1, tx2, ty2, color=NEG, sw=2.5))

    # маленький трикутник приростів ΔU, ΔI біля Q (на дотичній)
    dux = 70
    p1x, p1y = qx, qy
    p2x = qx + dux
    p2y = qy + k_tan * dux
    frags.append(line(p1x, p1y, p2x, p1y, color=NEG, sw=1.5))      # ΔU горизонталь
    frags.append(line(p2x, p1y, p2x, p2y, color=NEG, sw=1.5))      # ΔI вертикаль
    frags.append(text((p1x + p2x) / 2, p1y + 16, "ΔU", size=13, color=NEG))
    frags.append(text(p2x + 18, (p1y + p2y) / 2, "ΔI", size=13, color=NEG, anchor="start"))

    # точка Q
    frags.append(circle(qx, qy, 5, fill=INK, stroke=INK, sw=1))
    frags.append(text(qx + 10, qy - 8, "Q", size=15, bold=True, anchor="start"))

    # підписи-рамки
    b1, _, _ = textbox(190, 360, "січна 0→Q\nR = U/I\n(статичний)", size=12,
                       color=MUTED, stroke=MUTED)
    frags.append(b1)
    b2, _, _ = textbox(560, 150, "дотична в Q\nr = ΔU/ΔI\n(диференційний)", size=12,
                       color=NEG, stroke=NEG)
    frags.append(b2)

    render(os.path.join(IMG, 'two-slopes.svg'), W, H, *frags)


def fig_negative():
    """N-подібна ВАХ із ділянкою спаду: там diff-опір від'ємний."""
    W, H = 720, 460
    ox, oy = 80, 390
    ax2, ay2 = 660, 70
    frags = []
    frags.append(line(ox, oy, ax2, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, ay2, color=INK, sw=2))
    frags.append(text(ax2 + 4, oy + 5, "U", size=16, bold=True, anchor="start"))
    frags.append(text(ox - 8, ay2 - 4, "I", size=16, bold=True, anchor="end"))

    # N-крива: вгору → вниз (горб) → знову вгору. Будуємо кусково по px.
    def curve_y(px):
        t = (px - ox) / (ax2 - ox)        # 0..1
        # горб біля t≈0.25, провал, далі ріст
        import math
        base = 0.20 + 0.95 * t            # повільний загальний ріст
        bump = 0.55 * math.exp(-((t - 0.28) / 0.12) ** 2)   # пік
        dip = 0.45 * math.exp(-((t - 0.60) / 0.13) ** 2)    # провал
        v = base + bump - dip
        v = max(0.02, min(1.0, v))
        return oy - v * (oy - ay2)
    pts = []
    px = ox
    while px <= ax2:
        pts.append((px, curve_y(px)))
        px += 3
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # знайти ділянку спаду (de I/dU < 0) і виділити її зеленим
    seg = [p for i, p in enumerate(pts) if i > 0 and pts[i][1] > pts[i - 1][1]]
    if len(seg) >= 2:
        d2 = "M %.1f %.1f " % seg[0] + " ".join("L %.1f %.1f" % p for p in seg[1:])
        frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="5"/>' % (d2, FIELD))
        midx = seg[len(seg) // 2][0]
        midy = seg[len(seg) // 2][1]
        frags.append(line(midx, midy, midx + 90, midy - 70, color=FIELD, sw=1.5))
        bx, _, _ = textbox(midx + 150, midy - 95, "r = ΔU/ΔI < 0\nспад струму", size=12,
                           color=FIELD, stroke=FIELD)
        frags.append(bx)

    # підписати дві позитивні гілки
    frags.append(text(ox + 70, oy - 18, "r > 0", size=12, color=MUTED, anchor="middle"))
    frags.append(text(ax2 - 70, ay2 + 60, "r > 0", size=12, color=MUTED, anchor="middle"))

    render(os.path.join(IMG, 'negative-region.svg'), W, H, *frags)


def fig_diode_slope():
    """Експонента діода: дотична в малому струмі полога (r велике),
    у великому — крута (r мале). r = U_T/I видно як обернений нахил."""
    W, H = 720, 470
    ox, oy = 95, 405
    ax2, ay2 = 660, 70
    frags = []
    frags.append(line(ox, oy, ax2, oy, color=INK, sw=2))           # вісь U
    frags.append(line(ox, oy, ox, ay2, color=INK, sw=2))           # вісь I
    frags.append(text(ax2 + 4, oy + 5, "U", size=16, bold=True, anchor="start"))
    frags.append(text(ox - 8, ay2 - 4, "I", size=16, bold=True, anchor="end"))

    import math
    # експонента: I(t) = exp(a·t)-1, нормуємо у px. t — частка осі U.
    a = 3.4
    Imax = math.exp(a) - 1.0
    def curve_xy(t):
        px = ox + t * (ax2 - ox)
        iv = (math.exp(a * t) - 1.0) / Imax
        py = oy - iv * (oy - ay2) * 0.93
        return px, py
    pts = []
    t = 0.0
    while t <= 1.0001:
        pts.append(curve_xy(t))
        t += 0.01
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="3"/>' % (d, POS))

    # дві робочі точки: малий струм (t1) і вдесятеро більший (t2 далі праворуч)
    def tangent_at(t):
        h = 0.004
        x0, y0 = curve_xy(t)
        x1, y1 = curve_xy(t - h)
        x2, y2 = curve_xy(t + h)
        k = (y2 - y1) / (x2 - x1)
        return x0, y0, k

    for t, lab, col, L in [(0.50, "I₁  (мало)", NEG, 95), (0.86, "10·I₁", "#8e44ad", 58)]:
        x0, y0, k = tangent_at(t)
        # вкоротити дотичну, щоб не вилазила за поле осей
        x_a, x_b = x0 - L, x0 + L
        y_a = y0 + k * (x_a - x0)
        y_b = y0 + k * (x_b - x0)
        frags.append(line(x_a, y_a, x_b, y_b, color=col, sw=2.4))
        frags.append(circle(x0, y0, 5, fill=INK, stroke=INK, sw=1))
        frags.append(text(x0 - 8, y0 + 20, lab, size=12, color=col, anchor="end"))

    # пояснення: полога дотична → r велике; крута → r мале
    b1, _, _ = textbox(255, 175, "полога дотична\nr = U_T/I — велике", size=12,
                       color=NEG, stroke=NEG)
    frags.append(b1)
    b2, _, _ = textbox(560, 360, "крута дотична\nr = U_T/I — мале", size=12,
                       color="#8e44ad", stroke="#8e44ad")
    frags.append(b2)

    render(os.path.join(IMG, 'diode-slope.svg'), W, H, *frags)


def fig_ut_temp():
    """Теплова напруга U_T = kT/q росте з температурою лінійно (~0.086 мВ/К).
    Позначено робочу точку 300 K → 25.85 мВ."""
    W, H = 700, 430
    ox, oy = 95, 360
    ax2, ay2 = 640, 70
    frags = []
    frags.append(line(ox, oy, ax2, oy, color=INK, sw=2))
    frags.append(line(ox, oy, ox, ay2, color=INK, sw=2))
    frags.append(text(ax2 + 6, oy + 5, "T, K", size=14, bold=True, anchor="start"))
    frags.append(text(ox - 10, ay2 - 6, "U_T, мВ", size=14, bold=True, anchor="end"))

    # діапазон T: 200..400 K; U_T = 0.08617·T мВ
    Tmin, Tmax = 200.0, 400.0
    Umin, Umax = 0.08617 * Tmin, 0.08617 * Tmax   # ~17.2 .. ~34.5 мВ
    def XY(T):
        px = ox + (T - Tmin) / (Tmax - Tmin) * (ax2 - ox)
        U = 0.08617 * T
        py = oy - (U - 0) / (Umax * 1.05) * (oy - ay2)
        return px, py
    p0 = XY(Tmin)
    p1 = XY(Tmax)
    frags.append(line(p0[0], p0[1], p1[0], p1[1], color=POS, sw=3))

    # сітка по T
    for T in (200, 250, 300, 350, 400):
        px, _ = XY(T)
        frags.append(line(px, oy, px, oy + 5, color=INK, sw=1.5))
        frags.append(text(px, oy + 20, str(T), size=11, color=MUTED))

    # робоча точка 300 K → 25.85 мВ
    qx, qy = XY(300.0)
    frags.append(line(ox, qy, qx, qy, color=MUTED, sw=1.2, dash="5 4"))
    frags.append(line(qx, oy, qx, qy, color=MUTED, sw=1.2, dash="5 4"))
    frags.append(circle(qx, qy, 5, fill=INK, stroke=INK, sw=1))
    frags.append(text(ox - 8, qy + 4, "25.85", size=11, color=MUTED, anchor="end"))

    b1, _, _ = textbox(qx + 95, qy - 55, "300 K → 25.85 мВ\n(≈26 мВ «кімнатні»)",
                       size=12, color=INK)
    frags.append(b1)
    frags.append(text(ax2 - 30, ay2 + 30, "нахил k/q ≈ 0.086 мВ/К",
                      size=12, color=POS, anchor="end"))

    render(os.path.join(IMG, 'ut-temp.svg'), W, H, *frags)


def fig_history_timeline():
    """Стрічка часу приручення від'ємного диф-опору: Лосєв (1922) майже на
    покоління раніше за Есакі (1957) і Ґанна (1963); провал-забуття між ними."""
    W, H = 760, 360
    x0, x1 = 70, 690          # межі осі часу в px
    yax = 150                 # рівень осі
    t0, t1 = 1918.0, 1968.0   # межі в роках
    frags = []

    def X(year):
        return x0 + (year - t0) / (t1 - t0) * (x1 - x0)

    # вісь часу
    frags.append(line(x0, yax, x1 + 8, yax, color=INK, sw=2))
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
                 % (x1 + 18, yax, x1 + 8, yax - 5, x1 + 8, yax + 5, INK))
    # десятиліття-засічки
    for yr in (1920, 1930, 1940, 1950, 1960):
        px = X(yr)
        frags.append(line(px, yax - 5, px, yax + 5, color=MUTED, sw=1.5))
        frags.append(text(px, yax + 22, str(yr), size=12, color=MUTED))

    # тінь-провал «забуто» між 1933 і 1957
    gx0, gx1 = X(1933), X(1957)
    frags.append(rect(gx0, yax - 60, gx1 - gx0, 120, fill="#f1f1f2",
                      stroke="none", sw=0, rx=8))
    frags.append(text((gx0 + gx1) / 2, yax - 40, "забуто", size=12,
                      color=MUTED, italic=True))
    frags.append(text((gx0 + gx1) / 2, yax - 24, "(тріумф ламп)", size=11,
                      color=MUTED, italic=True))

    # три віхи: рік, колір, підпис над/під, бік підпису
    marks = [
        (1922, NEG,   "above", "Лосєв\nцинкіт\n(кристадин)"),
        (1957, POS,   "below", "Есакі\nтунельний\nдіод"),
        (1963, FIELD, "above", "Ґанн\nефект на\nGaAs"),
    ]
    for yr, col, side, lab in marks:
        px = X(yr)
        frags.append(circle(px, yax, 7, fill=col, stroke=INK, sw=1.5))
        if side == "above":
            frags.append(line(px, yax - 7, px, yax - 34, color=col, sw=1.5))
            b, _, _ = textbox(px, yax - 64, lab, size=12, color=col, stroke=col)
            frags.append(b)
        else:
            frags.append(line(px, yax + 7, px, yax + 40, color=col, sw=1.5))
            b, _, _ = textbox(px, yax + 70, lab, size=12, color=col, stroke=col)
            frags.append(b)

    # дужка-проміжок «~35 років» від Лосєва до Есакі
    ay = yax - 118
    frags.append(line(X(1922), ay, X(1957), ay, color=INK, sw=1.2))
    frags.append(line(X(1922), ay, X(1922), ay + 8, color=INK, sw=1.2))
    frags.append(line(X(1957), ay, X(1957), ay + 8, color=INK, sw=1.2))
    frags.append(text((X(1922) + X(1957)) / 2, ay - 8,
                      "≈ 35 років", size=13, color=INK, bold=True))

    render(os.path.join(IMG, 'history-timeline.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_two_slopes()
    fig_negative()
    fig_diode_slope()
    fig_ut_temp()
    fig_history_timeline()
    print("figures written to", IMG)
