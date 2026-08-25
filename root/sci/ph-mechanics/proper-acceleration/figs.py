# -*- coding: utf-8 -*-
"""Фігури до теми «Власне прискорення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def vec(x0, y0, x1, y1, color=INK, sw=3.0, head=12, dash=None):
    """Пряма стрілка-вектор із наконечником У КОЛІР лінії (marker svgkit завжди темний)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    body = ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (x0, y0, x1, y1, color, sw, d))
    px, py = x1 - ux * head, y1 - uy * head
    nx, ny = -uy, ux
    b = head / 2.3
    h = ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
         % (x1, y1, px + nx * b, py + ny * b, px - nx * b, py - ny * b, color))
    return body + h


def spring(cx, y0, y1, coils=5, w=13, color=INK, sw=2.0):
    """Вертикальна пружина-зигзаг від y0 до y1."""
    pts = [(cx, y0)]
    n = coils * 2
    seg = (y1 - y0) / n
    for i in range(1, n):
        x = cx + (w if i % 2 else -w)
        pts.append((x, y0 + seg * i))
    pts.append((cx, y1))
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
            % (d, color, sw))


def hatch_ground(x0, x1, y, n=9, color=MUTED):
    """Горизонтальна опора з косими штрихами знизу."""
    out = [line(x0, y, x1, y, color=color, sw=2.0)]
    step = (x1 - x0) / n
    for i in range(n):
        gx = x0 + step * (i + 0.5)
        out.append(line(gx, y, gx - 9, y + 10, color=color, sw=1.3))
    return "".join(out)


# ── Фігура 1: хто на опорі — прискорюється; хто падає — ні ────────────────────
def fig_sit_vs_fall():
    W, H = 760, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Хто нерухомий на опорі — прискорюється; хто падає — ні",
                  size=16, bold=True))

    # дві панелі
    f.append(rect(24, 52, 348, 348, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=10))
    f.append(rect(388, 52, 348, 348, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=10))

    # ── ЛІВА: спочиває на опорі ──
    cxL = 198
    f.append(text(cxL, 82, "спочиває на опорі", size=14, bold=True))
    # опора + тіло
    f.append(hatch_ground(108, 288, 214))
    f.append(rect(cxL - 30, 168, 60, 46, fill=FILL, stroke=INK, sw=2, rx=6))
    f.append(text(cxL, 196, "тіло", size=13))
    # велика зелена стрілка вгору — власне 1g
    f.append(vec(cxL, 164, cxL, 104, color=FIELD, sw=4.0, head=15))
    f.append(text(cxL + 16, 128, "власне", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(cxL + 16, 145, "a = 1g ↑", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(cxL, 236, "опора штовхає вгору", size=11, color=MUTED))
    # readout
    f.append(rect(78, 262, 240, 78, fill=BG, stroke=MUTED, sw=1.3, rx=8))
    f.append(text(cxL, 290, "координатне  a = 0", size=13, color=NEG))
    f.append(text(cxL, 316, "власне  a = 1g ↑", size=14, bold=True, color=FIELD))

    # ── ПРАВА: вільно падає ──
    cxR = 562
    f.append(text(cxR, 82, "вільно падає", size=14, bold=True))
    f.append(rect(cxR - 30, 122, 60, 46, fill=FILL, stroke=INK, sw=2, rx=6))
    f.append(text(cxR, 150, "тіло", size=13))
    # велика синя стрілка вниз — координатне g
    f.append(vec(cxR, 168, cxR, 232, color=NEG, sw=4.0, head=15))
    f.append(text(cxR + 16, 196, "координатне", size=13, bold=True, color=NEG, anchor="start"))
    f.append(text(cxR + 16, 213, "a = g ↓", size=13, bold=True, color=NEG, anchor="start"))
    f.append(text(cxR, 254, "опори немає — сама гравітація", size=11, color=MUTED))
    # readout
    f.append(rect(442, 262, 240, 78, fill=BG, stroke=MUTED, sw=1.3, rx=8))
    f.append(text(cxR, 290, "координатне  a = g ↓", size=13, color=NEG))
    f.append(text(cxR, 316, "власне  a = 0  (невагомість)", size=14, bold=True, color=FIELD))

    b, w, h = textbox(W / 2, 380,
                      "різниця між ними — гравітація, якої акселерометр не чує",
                      size=12, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "sit-vs-fall.svg"), W, H, *f)


# ── Фігура 2: чому пружина не чує гравітації ─────────────────────────────────
def fig_accelerometer_blind():
    W, H = 760, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Акселерометр глухий до гравітації, чутливий до опори",
                  size=16, bold=True))

    f.append(rect(24, 52, 348, 358, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=10))
    f.append(rect(388, 52, 348, 358, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=10))

    def sensor(cx, mass_y, spring_top=140, spring_coils=5):
        """Корпус приладу + пружина + тягарець на висоті mass_y."""
        out = []
        # корпус
        out.append(rect(cx - 52, 118, 104, 150, fill=BG, stroke=INK, sw=2.2, rx=10))
        # верхнє кріплення пружини
        out.append(line(cx - 22, spring_top, cx + 22, spring_top, color=INK, sw=2.6))
        out.append(spring(cx, spring_top, mass_y - 12, coils=spring_coils, w=12,
                          color=MUTED, sw=2.2))
        # тягарець
        out.append(rect(cx - 20, mass_y - 12, 40, 26, fill=FILL, stroke=INK, sw=2, rx=4))
        out.append(text(cx, mass_y + 5, "m", size=13, bold=True))
        return "".join(out)

    # ── ЛІВА: сама гравітація ──
    cxL = 198
    f.append(text(cxL, 82, "сама гравітація", size=14, bold=True))
    f.append(sensor(cxL, mass_y=214, spring_coils=5))
    # дві однакові стрілки g — на корпус (ліворуч) і на тягарець
    f.append(vec(cxL - 78, 150, cxL - 78, 210, color=MUTED, sw=3.0, head=12))
    f.append(text(cxL - 78, 138, "g на корпус", size=10, color=MUTED))
    f.append(vec(cxL, 226, cxL, 250, color=MUTED, sw=3.0, head=11))
    f.append(text(cxL + 40, 244, "g на m", size=10, color=MUTED, anchor="start"))
    f.append(text(cxL, 300, "тягне обох однаково →", size=11, color=INK))
    f.append(text(cxL, 318, "тягарець НЕ відстає, пружина рівна", size=11, color=INK))
    b, w, h = textbox(cxL, 356, "показ:  0", size=14, pad=8,
                      fill="#eaf0fd", stroke=NEG, sw=1.4, bold=True)
    f.append(b)
    f.append(text(cxL, 392, "гравітації не чути", size=11, color=MUTED))

    # ── ПРАВА: опора штовхає корпус ──
    cxR = 562
    f.append(text(cxR, 82, "опора штовхає корпус", size=14, bold=True))
    # тягарець НИЖЧЕ (відстав), пружина розтягнута (більше витків/довша)
    f.append(sensor(cxR, mass_y=236, spring_coils=7))
    # велика стрілка знизу — опора/тяга штовхає корпус угору
    f.append(vec(cxR, 300, cxR, 272, color=FIELD, sw=4.0, head=15))
    f.append(text(cxR, 320, "опора / тяга штовхає корпус угору", size=11, color=FIELD))
    f.append(text(cxR, 100, "корпус розганяється вгору,", size=11, color=INK))
    f.append(text(cxR, 116, "тягарець відстає → пружина тягнеться", size=11, color=INK))
    b, w, h = textbox(cxR, 356, "показ:  власне прискорення", size=13, pad=8,
                      fill="#eef6ef", stroke=FIELD, sw=1.4, bold=True)
    f.append(b)
    f.append(text(cxR, 392, "міряє все, крім гравітації", size=11, color=MUTED))
    return render(os.path.join(IMG, "accelerometer-blind.svg"), W, H, *f)


# ── Фігура 3: векторна різниця a_власне = a_коорд − g ────────────────────────
def fig_vector_subtraction():
    W, H = 760, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Власне прискорення = координатне − g   (векторна різниця)",
                  size=16, bold=True))

    G = 44  # 1g у пікселях

    # рамки чотирьох клітин
    cells = [(20, 46), (388, 46), (20, 268), (388, 268)]
    CW, CH = 352, 214
    for (x0, y0) in cells:
        f.append(rect(x0, y0, CW, CH, fill="#fbfcfe", stroke=MUTED, sw=1.3, rx=10))

    def title(i, s, color=INK):
        x0, y0 = cells[i]
        f.append(text(x0 + CW / 2, y0 + 26, s, size=14, bold=True, color=color))

    def legend(i, s):
        x0, y0 = cells[i]
        f.append(text(x0 + CW / 2, y0 + CH - 14, s, size=11, color=MUTED))

    # helper: намалювати −g (сірий, вгору) від точки p як довжину G
    def minus_g(px, py, dash="4,3"):
        return vec(px, py, px, py - G, color=MUTED, sw=2.6, head=10, dash=dash)

    # 1) у СПОКОЇ: a_коорд = 0 → власне = −g (1g угору)
    title(0, "у спокої")
    x0, y0 = cells[0]
    ox, oy = x0 + CW / 2 - 30, y0 + 150
    f.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(ox - 8, oy + 20, "a_коорд = 0", size=12, color=NEG, anchor="end"))
    f.append(minus_g(ox, oy))
    f.append(text(ox - 8, oy - G / 2, "−g", size=12, color=MUTED, anchor="end"))
    f.append(vec(ox + 26, oy, ox + 26, oy - G, color=FIELD, sw=3.4, head=13))
    f.append(text(ox + 34, oy - G / 2, "власне = 1g ↑", size=12, bold=True,
                  color=FIELD, anchor="start"))
    legend(0, "рухатись нікуди — лишається сам −g")

    # 2) ВІЛЬНЕ ПАДІННЯ: a_коорд = g вниз, −g угору → власне = 0
    title(1, "вільне падіння", color=FIELD)
    x0, y0 = cells[1]
    ox, oy = x0 + CW / 2 - 40, y0 + 74
    f.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=1))
    # a_коорд вниз
    f.append(vec(ox, oy, ox, oy + G, color=NEG, sw=3.4, head=13))
    f.append(text(ox - 8, oy + G / 2, "a_коорд = g ↓", size=12, color=NEG, anchor="end"))
    # −g від кінця a_коорд назад угору
    f.append(minus_g(ox + 30, oy + G))
    f.append(text(ox + 38, oy + G / 2, "−g", size=12, color=MUTED, anchor="start"))
    # результат: 0
    b, w, h = textbox(ox + 30, oy + G + 44, "власне = 0", size=13, pad=7,
                      fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    legend(1, "координатне точно гасить гравітацію")

    # 3) ЛІФТ УГОРУ: a_коорд = 0.5g вгору, −g угору → власне = 1.5g
    title(2, "ліфт рушає вгору")
    x0, y0 = cells[2]
    ox, oy = x0 + CW / 2 - 40, y0 + 176
    f.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=1))
    # a_коорд вгору 0.5g
    f.append(vec(ox, oy, ox, oy - G * 0.5, color=NEG, sw=3.4, head=12))
    f.append(text(ox - 8, oy - G * 0.25, "a_коорд", size=12, color=NEG, anchor="end"))
    # −g далі вгору від кінця
    f.append(minus_g(ox, oy - G * 0.5))
    f.append(text(ox - 8, oy - G * 0.5 - G / 2, "−g", size=12, color=MUTED, anchor="end"))
    # результат зелений від O угору на 1.5g (трохи праворуч)
    f.append(vec(ox + 34, oy, ox + 34, oy - G * 1.5, color=FIELD, sw=3.4, head=13))
    f.append(text(ox + 42, oy - G * 0.75, "власне", size=12, bold=True,
                  color=FIELD, anchor="start"))
    f.append(text(ox + 42, oy - G * 0.75 + 16, "= 1.5g ↑", size=12, bold=True,
                  color=FIELD, anchor="start"))
    legend(2, "вектори додаються — важчаєш")

    # 4) ГОРИЗОНТАЛЬНИЙ РОЗГІН: a_коорд убік, −g угору → власне нахилене
    title(3, "горизонтальний розгін")
    x0, y0 = cells[3]
    ox, oy = x0 + CW / 2 - 30, y0 + 150
    f.append(circle(ox, oy, 4, fill=INK, stroke=INK, sw=1))
    ax = G * 0.9
    # a_коорд праворуч
    f.append(vec(ox, oy, ox + ax, oy, color=NEG, sw=3.4, head=12))
    f.append(text(ox + ax / 2, oy + 18, "a_коорд", size=12, color=NEG))
    # −g угору від кінця a_коорд
    f.append(minus_g(ox + ax, oy))
    f.append(text(ox + ax + 8, oy - G / 2, "−g", size=12, color=MUTED, anchor="start"))
    # результат від O до кінця −g (діагональ)
    f.append(vec(ox, oy, ox + ax, oy - G, color=FIELD, sw=3.4, head=13))
    f.append(text(ox - 6, oy - G * 0.6, "власне", size=12, bold=True,
                  color=FIELD, anchor="end"))
    legend(3, "нахилене — нитка з тягарцем відхиляється")

    return render(os.path.join(IMG, "vector-subtraction.svg"), W, H, *f)


# ── Фігура 4 (вставка proj): чому наївне інтегрування зносить оцінку ─────────
def fig_naive_drift():
    W, H = 840, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Подвійний інтеграл множить будь-який залишок на час у квадраті",
                  size=16, bold=True))

    def panel(px, py, pw, ph, title_s):
        return [rect(px, py, pw, ph, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=10),
                text(px + pw / 2, py + 24, title_s, size=13, bold=True)]

    def axes(P, ymax, yticks, xmax=10.0):
        ax = P['px'] + 46
        ay = P['py'] + P['ph'] - 30
        top = P['py'] + 40
        right = P['px'] + P['pw'] - 16
        out = [line(ax, top, ax, ay, color=INK, sw=1.6),
               line(ax, ay, right, ay, color=INK, sw=1.6)]
        for val, lab in yticks:
            yy = ay - (ay - top) * (val / ymax)
            out += [line(ax - 5, yy, ax, yy, color=INK, sw=1.4),
                    text(ax - 9, yy + 4, lab, size=11, color=MUTED, anchor="end")]
        for tv in (0, 5, 10):
            xx = ax + (right - ax) * (tv / xmax)
            out += [line(xx, ay, xx, ay + 5, color=INK, sw=1.4),
                    text(xx, ay + 19, str(tv), size=11, color=MUTED)]
        out.append(text(right, ay + 19, "час, с", size=11, color=MUTED, anchor="end"))
        return out, ax, ay, top, right

    def curve(ax, ay, top, right, a_coef, ymax, color, sw=3.2, xmax=10.0, n=48):
        pts = []
        for i in range(n + 1):
            t = xmax * i / n
            val = 0.5 * a_coef * t * t
            if val > ymax:
                val = ymax
            xx = ax + (right - ax) * (t / xmax)
            yy = ay - (ay - top) * (val / ymax)
            pts.append((xx, yy))
        d = " ".join("%.1f,%.1f" % p for p in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>'
                % (d, color, sw))

    L = {'px': 70, 'py': 92, 'pw': 310, 'ph': 300}
    R = {'px': 458, 'py': 92, 'pw': 310, 'ph': 300}

    # ── ЛІВА: сирий показ (g не віднято), ymax = 500 м ──
    f += panel(**L, title_s="сирий показ — g не віднято")
    aL, axL, ayL, topL, rightL = axes(L, 500, [(0, "0"), (250, "250"), (500, "500")])
    f += aL
    f.append(curve(axL, ayL, topL, rightL, 9.81, 500, POS))
    b, _, _ = textbox(210, 168, "фантомне a = 9.81 м/с²", size=11, pad=6,
                      fill="#fdecea", stroke=POS, sw=1.2)
    f.append(b)
    f.append(text(250, 210, "→  ≈ 490 м за 10 с", size=12, bold=True, color=POS))

    # ── ПРАВА: g віднято, але нахил 0.5°, ymax = 10 м ──
    f += panel(**R, title_s="g віднято, похибка нахилу 0.5°")
    aR, axR, ayR, topR, rightR = axes(R, 10, [(0, "0"), (5, "5"), (10, "10")])
    f += aR
    f.append(curve(axR, ayR, topR, rightR, 0.0856, 10, "#e08a1e"))          # 9.81·sin(0.5°)
    f.append(line(axR, ayR - 1.5, rightR, ayR - 1.5, color=FIELD, sw=3.0))  # точна орієнтація ≈ 0
    f.append(text(616, 172, "≈ 4.3 м за 10 с", size=12, bold=True, color="#e08a1e"))
    f.append(text(rightR - 6, ayR - 8, "точна орієнтація ≈ 0", size=11, bold=True,
                  color=FIELD, anchor="end"))

    b, w, h = textbox(W / 2, 448,
                      "навіть пів градуса похибки орієнтації дає метри вигаданого шляху; "
                      "сирий показ — сотні метрів",
                      size=12, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "naive-drift.svg"), W, H, *f)


# ── Фігура 5 (вставка proj): детекція вільного падіння за |a| ≈ 0 ────────────
def fig_free_fall_detect():
    W, H = 840, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Вільне падіння видно за тим, що ВЕСЬ показ падає до нуля",
                  size=16, bold=True))

    px, py, pw, ph = 64, 74, 700, 236
    ax = px + 44
    ay = py + ph - 30
    top = py + 16
    right = px + pw - 12
    T, AMAX = 2.0, 30.0

    def X(t):
        return ax + (right - ax) * (t / T)

    def Y(v):
        return ay - (ay - top) * (v / AMAX)

    f.append(rect(px, py, pw, ph, fill="#fbfcfe", stroke=MUTED, sw=1.4, rx=10))

    # зелена смуга «вільне падіння виявлено»
    fx0, fx1 = X(0.75), X(1.30)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e7f6ec" stroke="none"/>'
             % (fx0, top, fx1 - fx0, ay - top))

    f.append(line(ax, top, ax, ay, color=INK, sw=1.6))
    f.append(line(ax, ay, right, ay, color=INK, sw=1.6))

    y1g = Y(9.81)
    f.append(line(ax, y1g, right, y1g, color=NEG, sw=1.4, dash="6,4"))
    yth = Y(1.0)
    f.append(line(ax, yth, right, yth, color=FIELD, sw=1.5, dash="5,4"))

    for val, lab in [(0, "0"), (9.81, "g"), (20, "20"), (30, "30")]:
        yy = Y(val)
        f.append(line(ax - 5, yy, ax, yy, color=INK, sw=1.3))
        f.append(text(ax - 9, yy + 4, lab, size=11, color=MUTED, anchor="end"))

    # мітки ліній праворуч, поза кривою
    f.append(text(right + 6, y1g + 4, "1g", size=12, bold=True, color=NEG, anchor="start"))
    f.append(text(right + 6, yth + 4, "поріг", size=11, bold=True, color=FIELD, anchor="start"))
    f.append(text(right + 6, yth + 19, "≈0.1g", size=10, color=FIELD, anchor="start"))

    pts_a = [(0.0, 9.8), (0.1, 10.4), (0.2, 9.3), (0.3, 10.1), (0.4, 9.5), (0.5, 10.2),
             (0.6, 9.6), (0.68, 9.9),
             (0.72, 4.2), (0.75, 0.7), (0.82, 0.3), (0.92, 0.5), (1.02, 0.2), (1.12, 0.5),
             (1.22, 0.3), (1.28, 0.8),
             (1.33, 13.0), (1.37, 28.0), (1.41, 21.0), (1.45, 7.0),
             (1.52, 12.8), (1.61, 8.4), (1.70, 10.7), (1.80, 9.3), (1.90, 9.9), (2.0, 9.8)]
    d = " ".join("%.1f,%.1f" % (X(t), Y(v)) for t, v in pts_a)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (d, INK))

    f.append(text((fx0 + fx1) / 2, top + 20, "|a| ≈ 0  →  вільне падіння",
                  size=12, bold=True, color=FIELD))
    f.append(text(fx0 + 4, ay + 17, "витримка ~30 мс", size=10, color=MUTED, anchor="start"))

    # фази під віссю
    f.append(text(X(0.34), ay + 34, "на опорі / рух", size=11, color=MUTED))
    f.append(text(X(1.02), ay + 34, "падіння", size=11, bold=True, color=FIELD))
    f.append(text(X(1.38), ay + 52, "удар", size=11, bold=True, color=POS))
    f.append(text(X(1.76), ay + 34, "спокій", size=11, color=MUTED))
    return render(os.path.join(IMG, "free-fall-detect.svg"), W, H, *f)


# ── Фігура 6 (вставка proj): конвеєр обробки IMU ─────────────────────────────
def fig_gravity_pipeline():
    W, H = 840, 300
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26,
                  "Конвеєр: прибрати g → інтегрувати; окрема гілка ловить вільне падіння",
                  size=15, bold=True))

    def box(cx, cy, w, h, s, fill=FILL, stroke=INK, sw=1.8, tc=INK, size=12, bold=False):
        return fitbox(cx - w / 2, cy - h / 2, w, h, s, size=size,
                      fill=fill, stroke=stroke, sw=sw, color=tc, bold=bold)

    IN = "#eef3fb"   # входи
    GR = "#e7f6ec"   # чистий результат / вільне падіння

    # верхній ряд — джерело орієнтації
    f.append(box(60, 70, 92, 44, "орієнтація q", fill=IN, size=11))
    f.append(box(206, 70, 176, 44, "g_body = q⁻¹·(g↑)", fill=FILL, size=12))
    # головний ряд
    f.append(box(92, 150, 130, 52, "акселерометр\na_b (корпус)", fill=IN))
    f.append(circle(206, 150, 16, fill=BG, stroke=INK, sw=2.0))
    f.append(text(206, 157, "−", size=24, bold=True, color=NEG))
    f.append(box(320, 150, 136, 52, "лінійне\na_рух", fill=GR))
    f.append(box(496, 150, 150, 52, "у світ q·a\n+ ∫∫ dt", fill=FILL))
    f.append(box(676, 150, 140, 52, "швидкість v\nшлях p", fill=FILL))
    # гілка вільного падіння
    f.append(box(92, 250, 150, 46, "|a_b| ≈ 0 ?", fill=FILL))
    f.append(box(300, 250, 150, 46, "вільне падіння", fill=GR, bold=True, tc=FIELD))

    # межа систем координат
    f.append(line(405, 116, 405, 184, color=MUTED, sw=1.0, dash="4,4"))

    # стрілки головного ряду
    f.append(vec(157, 150, 189, 150, color=INK, sw=2.2, head=10))
    f.append(vec(223, 150, 252, 150, color=INK, sw=2.2, head=10))
    f.append(vec(388, 150, 421, 150, color=INK, sw=2.2, head=10))
    f.append(vec(571, 150, 606, 150, color=INK, sw=2.2, head=10))
    # стрілки джерела орієнтації
    f.append(vec(106, 70, 118, 70, color=INK, sw=2.0, head=9))
    f.append(vec(206, 92, 206, 132, color=INK, sw=2.2, head=10))
    # стрілки гілки падіння
    f.append(vec(92, 176, 92, 227, color=MUTED, sw=2.0, head=10))
    f.append(vec(167, 250, 225, 250, color=INK, sw=2.2, head=10))

    # підписи систем координат
    f.append(text(240, 200, "осі корпусу (body)", size=11, italic=True, color=MUTED))
    f.append(text(585, 200, "світові осі (world)", size=11, italic=True, color=MUTED))
    return render(os.path.join(IMG, "gravity-removal-pipeline.svg"), W, H, *f)


def _polyline(pts, color=INK, sw=3.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (s, color, sw, d))


# ── Фігура (вставка math): гіперболічний рух у просторі-часі ──────────────────
def fig_hyperbolic_motion():
    W, H = 720, 560
    px, py, s = 160.0, 300.0, 76.0      # півот (перетин асимптот), масштаб px/св.рік
    R = s                                # c²/α = 1 св. рік → R = s пікселів
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Сталий власний прискорений рух — гіпербола в просторі-часі",
                  size=16, bold=True))

    # осі
    f.append(vec(px, 505, px, 86, color=INK, sw=1.7, head=10))       # ct угору
    f.append(text(px + 10, 100, "ct — час", size=12, color=INK, anchor="start"))
    f.append(vec(102, py, 690, py, color=INK, sw=1.7, head=10))      # x праворуч
    f.append(text(668, py + 22, "x — простір", size=12, color=INK, anchor="middle"))

    # світлові промені (асимптоти), під 45°
    f.append(line(px, py, 378, 82, color=MUTED, sw=1.8, dash="6,5"))    # угору-праворуч
    f.append(line(px, py, 300, 440, color=MUTED, sw=1.8, dash="6,5"))   # униз-праворуч

    # гіпербола (нижнє плече коротше — вхідний етап гальмування)
    pts = []
    n = 80
    lo, hi = -1.15, 1.62
    for i in range(n + 1):
        phi = lo + (hi - lo) * i / n
        pts.append((px + s * math.cosh(phi), py - s * math.sinh(phi)))
    f.append(_polyline(pts, color=FIELD, sw=3.6))

    # вершина: миттєвий спокій, U ⟂ A
    vx, vy = px + R, py
    f.append(vec(vx, vy, vx, vy - 78, color=NEG, sw=3.4, head=13))   # U угору (час)
    f.append(vec(vx, vy, vx + 78, vy, color=POS, sw=3.4, head=13))   # A праворуч (простір)
    f.append(line(vx, vy - 13, vx + 13, vy - 13, color=MUTED, sw=1.2))   # прямий кут
    f.append(line(vx + 13, vy - 13, vx + 13, vy, color=MUTED, sw=1.2))
    f.append(circle(vx, vy, 3.6, fill=INK, stroke=INK, sw=1))
    f.append(text(vx - 12, vy - 40, "U", size=15, bold=True, color=NEG, anchor="end"))
    f.append(text(vx + 44, vy - 10, "A", size=15, bold=True, color=POS, anchor="start"))
    f.append(text(vx + 18, vy - 44, "τ = 0", size=12, bold=True, color=INK, anchor="start"))
    f.append(text(vx + 18, vy - 28, "миттєвий спокій", size=10, color=MUTED, anchor="start"))

    # плече c²/α між півотом і вершиною
    f.append(line(px, py + 12, px, py + 20, color=MUTED, sw=1.2))
    f.append(line(vx, py + 12, vx, py + 20, color=MUTED, sw=1.2))
    f.append(line(px, py + 16, vx, py + 16, color=MUTED, sw=1.2))
    f.append(text((px + vx) / 2, py + 34, "c²/α ≈ 1 св. рік", size=11, color=MUTED))

    # рухома точка вище по лінії: тулиться до променя, v → c
    mphi = 1.2
    mx, my = px + s * math.cosh(mphi), py - s * math.sinh(mphi)
    f.append(circle(mx, my, 3.4, fill=INK, stroke=INK, sw=1))
    Ln = math.hypot(math.sinh(mphi), math.cosh(mphi))
    ex = mx + (math.sinh(mphi) / Ln) * 52
    ey = my - (math.cosh(mphi) / Ln) * 52
    f.append(vec(mx, my, ex, ey, color=MUTED, sw=2.5, head=10))
    f.append(text(ex + 8, ey + 8, "v → c", size=11, color=MUTED, anchor="start"))

    # нотатка згори-праворуч
    b, w, h = textbox(560, 150, "чим вище по лінії —\nтим ближче до 45°,\nдотику немає ніколи",
                      size=11, pad=8, fill="#fbfcfe", stroke=MUTED, sw=1.2)
    f.append(b)

    # легенда знизу-ліворуч (нижнє плече вище за y≈410, тут вільно)
    lx, ly = 18, 466
    f.append(rect(lx, ly, 336, 86, fill="#fbfcfe", stroke=MUTED, sw=1.2, rx=8))
    rows = [
        (FIELD, 3.8, None, "світова лінія (гіпербола)"),
        (NEG, 3.4, None, "U — 4-швидкість  (|U| = c)"),
        (POS, 3.4, None, "A — 4-прискорення  (|A| = α)"),
        (MUTED, 1.8, "6,5", "світлові промені — асимптоти (v = c)"),
    ]
    for i, (col, sw, dash, s_) in enumerate(rows):
        ry = ly + 20 + i * 19
        f.append(line(lx + 14, ry, lx + 44, ry, color=col, sw=sw, dash=dash))
        f.append(text(lx + 54, ry + 4, s_, size=11, color=INK, anchor="start"))

    return render(os.path.join(IMG, "hyperbolic-motion.svg"), W, H, *f)


# ── Фігура (вставка math): прудкість росте лінійно, швидкість насичується ─────
def fig_rapidity_vs_velocity():
    W, H = 720, 480
    L, Rr, T, B = 110.0, 650.0, 80.0, 400.0
    tmax = 3.8
    kk = 1.03
    xof = lambda t: L + t * (Rr - L) / tmax
    yphi = lambda p: B - p * 80.0        # φ: 0..4 → B..T
    yv = lambda v: B - v * 320.0         # v/c: 0..1 → B..T

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Прудкість росте лінійно й без межі — швидкість лише насичується до c",
                  size=15, bold=True))

    # осі
    f.append(vec(105, B, 662, B, color=INK, sw=1.7, head=10))
    f.append(text((L + Rr) / 2, B + 38, "власний час τ (роки корабля)", size=12, color=INK))
    f.append(vec(L, B + 5, L, 70, color=INK, sw=1.7, head=10))
    f.append(vec(Rr, B + 5, Rr, 70, color=INK, sw=1.7, head=10))
    f.append(text(72, 62, "прудкість φ", size=12, bold=True, color=POS, anchor="start"))
    f.append(text(636, 62, "v / c", size=12, bold=True, color=NEG, anchor="start"))

    # мітки осей
    for p in range(5):
        f.append(line(104, yphi(p), L, yphi(p), color=INK, sw=1.4))
        f.append(text(99, yphi(p) + 4, str(p), size=11, color=POS, anchor="end"))
    for v in [0, 0.25, 0.5, 0.75, 1.0]:
        f.append(line(Rr, yv(v), 656, yv(v), color=INK, sw=1.4))
        f.append(text(661, yv(v) + 4, "%.2f" % v, size=11, color=NEG, anchor="start"))
    for t in range(4):
        f.append(line(xof(t), B, xof(t), B + 6, color=INK, sw=1.4))
        f.append(text(xof(t), B + 20, str(t), size=11, color=INK))

    # стеля c
    f.append(line(L, T, Rr, T, color=MUTED, sw=1.6, dash="6,5"))
    f.append(text(548, T - 8, "c — недосяжна межа", size=11, color=MUTED))

    # прудкість — пряма зі стрілкою (без стелі)
    f.append(vec(xof(0), yphi(0), xof(tmax), yphi(kk * tmax), color=POS, sw=3.4, head=12))
    f.append(text(300, 206, "прудкість φ = 1.03·τ", size=12, bold=True, color=POS))

    # швидкість — насичувана крива
    vpts = []
    n = 90
    for i in range(n + 1):
        t = tmax * i / n
        vpts.append((xof(t), yv(math.tanh(kk * t))))
    f.append(_polyline(vpts, color=NEG, sw=3.4))
    f.append(text(330, 384, "v = c · th(1.03·τ)  →  c", size=12, bold=True, color=NEG))

    # точки на кривій швидкості
    for t, lab, tx, ty, anc in [(1, "0.77c", xof(1), yv(math.tanh(kk)) - 12, "middle"),
                                (2, "0.97c", xof(2) + 8, yv(math.tanh(2 * kk)) + 18, "start"),
                                (3, "0.995c", xof(3) + 12, yv(math.tanh(3 * kk)) + 26, "start")]:
        cy = yv(math.tanh(kk * t))
        f.append(circle(xof(t), cy, 3.6, fill=NEG, stroke=NEG, sw=1))
        f.append(text(tx, ty, lab, size=11, color=NEG, anchor=anc))

    return render(os.path.join(IMG, "rapidity-vs-velocity.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_sit_vs_fall(), fig_accelerometer_blind(), fig_vector_subtraction(),
          fig_naive_drift(), fig_free_fall_detect(), fig_gravity_pipeline(),
          fig_hyperbolic_motion(), fig_rapidity_vs_velocity()]
    print("written:")
    for p in ps:
        print("  ", p)
