# -*- coding: utf-8 -*-
"""Фігури до теми «Переміщення і шлях».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

DISP = FIELD        # переміщення — зелена стрілка (чистий результат)
PATH = "#8a94a6"    # шлях — сірий маршрут
ALT  = "#b07a2f"    # альтернативний маршрут — теплий коричнюватий


def dot(cx, cy, r=6, col=INK, fill=BG):
    return circle(cx, cy, r, fill=fill, stroke=col, sw=2)


# ── Фігура 1: два різні маршрути — одне переміщення ───────────────────────────
def fig_path_vs_disp():
    W, H = 880, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Хоч якою дорогою — переміщення те саме; шлях різний",
                  size=15.5, bold=True))

    ax, ay = 120, 372          # початок A
    bx, by = 726, 150          # кінець B
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux           # нормаль (перпендикуляр до A→B)

    # маршрут 1 — хвиляста прогулянка над прямою
    p1 = []
    t = 0.0
    while t <= 1.0 + 1e-9:
        amp = 62 * math.sin(3.05 * math.pi * t)
        x = ax + t * dx + amp * nx
        y = ay + t * dy + amp * ny
        p1.append("%.1f,%.1f" % (x, y))
        t += 0.01
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (" ".join(p1), PATH))

    # маршрут 2 — великий гак під прямою (пунктир)
    p2 = []
    t = 0.0
    while t <= 1.0 + 1e-9:
        amp = -104 * math.sin(1.0 * math.pi * t)
        x = ax + t * dx + amp * nx
        y = ay + t * dy + amp * ny
        p2.append("%.1f,%.1f" % (x, y))
        t += 0.01
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-dasharray="7,6"/>' % (" ".join(p2), ALT))

    # переміщення — пряма зелена стрілка A→B
    f.append(arrow(ax, ay, bx, by, color=DISP, sw=3.4))

    # точки
    f.append(dot(ax, ay, 7, col=INK))
    f.append(text(ax - 14, ay + 20, "початок A", size=13, bold=True, anchor="start"))
    f.append(dot(bx, by, 7, col=INK))
    f.append(text(bx + 12, by - 6, "кінець B", size=13, bold=True, anchor="start"))

    # підписи ліній (осторонь від самих ліній)
    f.append(text(300, 250, "маршрут 1  (шлях s₁)", size=13, color=PATH, bold=True))
    f.append(text(505, 405, "маршрут 2  (шлях s₂)", size=13, color=ALT, bold=True, anchor="middle"))
    mx, my = ax + 0.44 * dx + 20 * nx, ay + 0.44 * dy + 20 * ny
    f.append(text(mx + 20, my - 6, "переміщення  Δr", size=13.5, color=DISP,
                  bold=True, anchor="start"))

    b, bw, bh = textbox(W / 2, 447,
                        ["Шлях залежить від усього маршруту (s₁ ≠ s₂), переміщення — лише від двох кінців.",
                         "Пряма — найкоротша, тож завжди  |Δr| ≤ s."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "path-vs-displacement.svg"), W, H, *f)


# ── Фігура 2: замкнений маршрут — переміщення нуль ────────────────────────────
def fig_round_trip():
    W, H = 820, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Замкнений маршрут: шлях великий, переміщення — нуль",
                  size=15.5, bold=True))

    cx, cy = 350, 250
    R, a = 118, 30

    def rad(th):
        return R + a * math.sin(3 * th + 0.7)

    def P(th):
        r = rad(th)
        return cx + r * math.cos(th), cy + r * math.sin(th)

    # петля (замкнена крива)
    pts = []
    th = 0.0
    while th <= 2 * math.pi + 1e-9:
        x, y = P(th)
        pts.append("%.1f,%.1f" % (x, y))
        th += 0.01
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.2"/>'
             % (" ".join(pts), PATH))

    # стрілки напрямку руху по петлі
    for th0 in (0.9, 2.5, 4.1, 5.6):
        x0, y0 = P(th0)
        x1, y1 = P(th0 + 0.13)
        f.append(arrow(x0, y0, x1, y1, color=PATH, sw=3))

    # точка старт = фініш
    sx, sy = P(0.0)
    f.append(dot(sx, sy, 8, col=DISP, fill="#eafaf0"))
    f.append(text(sx + 16, sy + 5, "старт = фініш", size=13, bold=True,
                  color=DISP, anchor="start"))

    f.append(text(cx, cy + 4, "шлях  s", size=14, color=PATH, bold=True))
    f.append(text(cx, cy + 24, "= уся довжина петлі", size=12, color=PATH))

    # напис про нульове переміщення
    b, bw, bh = textbox(650, 210,
                        ["переміщення", "Δr = 0"],
                        size=15, pad=12, fill="#eafaf0", stroke=DISP, sw=1.6,
                        color=DISP, bold=True)
    f.append(b)

    b2, bw2, bh2 = textbox(W / 2, 447,
                           ["Кінець збігся з початком → переміщення нульове, хоч ти пройшов усю петлю.",
                            "Тому середня швидкість за коло — нуль, а стояти на місці ти явно не стояв."],
                           size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b2)
    return render(os.path.join(IMG, "round-trip.svg"), W, H, *f)


# ── Фігура 3: на прямій — знак замість стрілки ────────────────────────────────
def fig_one_dim():
    W, H = 860, 340
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "На прямій: переміщення — число зі знаком, шлях — сума модулів",
                  size=15.5, bold=True))

    ox = 110
    step = 108                 # px на 1 метр
    yline = 196

    def X(m): return ox + m * step

    # вісь із поділками 0..6
    f.append(arrow(ox - 20, yline, X(6) + 30, yline, color=LINE, sw=1.6))
    for m in range(0, 7):
        f.append(line(X(m), yline - 5, X(m), yline + 5, color=LINE, sw=1.4))
        f.append(text(X(m), yline + 22, str(m), size=12, color=MUTED))
    f.append(text(X(6) + 30, yline + 22, "x, м", size=12.5, color=INK, anchor="start"))

    # крок 1: +5 (над віссю, червоне)
    f.append(arrow(X(0), yline - 40, X(5), yline - 40, color=POS, sw=3))
    f.append(text((X(0) + X(5)) / 2, yline - 50, "крок 1:  +5 м", size=13, color=POS, bold=True))

    # крок 2: −3 (ще вище, синє)
    f.append(arrow(X(5), yline - 88, X(2), yline - 88, color=NEG, sw=3))
    f.append(text((X(5) + X(2)) / 2, yline - 98, "крок 2:  −3 м", size=13, color=NEG, bold=True))

    # переміщення: +2 (під віссю, зелене)
    f.append(arrow(X(0), yline + 52, X(2), yline + 52, color=DISP, sw=3.4))
    f.append(text((X(0) + X(2)) / 2, yline + 72, "переміщення  Δx = +2 м",
                  size=13, color=DISP, bold=True))

    # позначки старт / поворот / кінець
    f.append(dot(X(0), yline, 5, col=INK))
    f.append(text(X(0), yline - 12, "старт", size=11.5, color=INK))
    f.append(dot(X(5), yline, 5, col=INK))
    f.append(text(X(5), yline - 12, "поворот", size=11.5, color=INK))
    f.append(dot(X(2), yline, 5, col=DISP, fill="#eafaf0"))

    b, bw, bh = textbox(W / 2, 318,
                        ["Шлях = |+5| + |−3| = 8 м   ·   Переміщення = +5 + (−3) = +2 м"],
                        size=13, pad=10, fill=FILL, stroke=LINE, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "one-dim-sign.svg"), W, H, *f)


# ── Фігура 4 (вставка proj-odometry): шум роздуває шлях, не переміщення ────────
def fig_odo_noise():
    import random
    rnd = random.Random(9)
    W, H = 900, 440
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Шум роздуває ШЛЯХ, майже не чіпаючи ПЕРЕМІЩЕННЯ",
                  size=15.5, bold=True))

    ax, ay = 120, 232
    bx, by = 778, 232
    n = 30
    pts = []
    for i in range(n + 1):
        t = i / n
        x = ax + t * (bx - ax)
        amp = 0 if i in (0, n) else 28
        y = ay + rnd.uniform(-amp, amp)
        pts.append((x, y))

    # сірий зубчастий виміряний шлях
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
             % (" ".join("%.1f,%.1f" % (x, y) for x, y in pts), PATH))
    for x, y in pts:
        f.append(circle(x, y, 2.6, fill=PATH, stroke=PATH, sw=0))

    # зелене переміщення = справжній прямий шлях
    f.append(arrow(ax, ay, bx, by, color=DISP, sw=3.4))

    f.append(dot(ax, ay, 7, col=INK))
    f.append(text(ax - 2, ay + 30, "старт A", size=12.5, bold=True))
    f.append(dot(bx, by, 7, col=INK))
    f.append(text(bx - 2, by + 30, "фініш B", size=12.5, bold=True))

    f.append(text(W / 2, 118, "виміряний шлях — зубчастий, систематично довший",
                  size=13, color=PATH, bold=True))
    f.append(text(W / 2, 300, "переміщення  Δr  =  справжній прямий шлях",
                  size=13, color=DISP, bold=True))

    b, bw, bh = textbox(W / 2, 402,
                        ["Пряме 10 м, 100 відліків, σ = 3 см:  наївний шлях 10.96 м (+9.6 %),  переміщення 10.00 м.",
                         "Робот СТОЇТЬ, 200 відліків:  наївний шлях ≈ 10.6 м «пробігу», а переміщення ≈ 0."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "odo-noise.svg"), W, H, *f)


# ── Фігура 5 (вставка proj-odometry): поріг мінімального кроку (deadband) ──────
def fig_odo_deadband():
    import random
    rnd = random.Random(4)
    W, H = 900, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Поріг мінімального кроку: тремтіння в межах ε не рахуємо",
                  size=15.5, bold=True))

    anchors = [(190, 252), (490, 224), (760, 256)]
    eps = 66

    # зараховані кроки — суцільні зелені стрілки між якорями
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:]):
        f.append(arrow(x0, y0, x1, y1, color=DISP, sw=3))

    for k, (cx, cy) in enumerate(anchors):
        f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
                 'stroke-width="1.6" stroke-dasharray="5,5"/>' % (cx, cy, eps, MUTED))
        for _ in range(6):
            r = rnd.uniform(7, eps - 12)
            th = rnd.uniform(0, 6.283)
            jx, jy = cx + r * math.cos(th), cy + r * math.sin(th)
            f.append(line(jx - 4, jy - 4, jx + 4, jy + 4, color="#c2c8d0", sw=1.6))
            f.append(line(jx - 4, jy + 4, jx + 4, jy - 4, color="#c2c8d0", sw=1.6))
        f.append(dot(cx, cy, 7, col=DISP, fill="#eafaf0"))
        f.append(text(cx, cy - eps - 12, "якір %d" % (k + 1),
                      size=12.5, color=DISP, bold=True))

    # радіус ε — вертикальна риска вгору від першого якоря
    cx, cy = anchors[0]
    f.append(line(cx, cy, cx, cy - eps, color=MUTED, sw=1.4))
    f.append(text(cx + 13, cy - eps / 2 + 5, "ε", size=14, color=MUTED,
                  bold=True, anchor="start"))

    # легенда
    ly = 374
    f.append(line(120, ly, 152, ly, color=DISP, sw=3))
    f.append(text(160, ly + 4, "зарахований крок (вихід за ε)",
                  size=12.5, anchor="start"))
    f.append(line(432, ly - 4, 440, ly + 4, color="#c2c8d0", sw=1.6))
    f.append(line(432, ly + 4, 440, ly - 4, color="#c2c8d0", sw=1.6))
    f.append(text(450, ly + 4, "відкинуте тремтіння (крок < ε)",
                  size=12.5, anchor="start"))

    b, bw, bh = textbox(W / 2, 428,
                        ["Якір зсувається лише коли відлік ВИХОДИТЬ за коло ε від останньої збереженої точки.",
                         "Стоячи на місці, робот тремтить усередині кола — жоден зубець не додає довжини."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "odo-deadband.svg"), W, H, *f)


# ── Фігура 6 (вставка math-path-length): уписана ламана наближає дугу ──────────
def fig_arc_polygon():
    W, H = 880, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Уписана ламана наближає довжину дуги",
                  size=15.5, bold=True))

    ax, ay = 120, 372
    bx, by = 738, 150
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    nx, ny = uy, -ux                 # нормаль
    if ny > 0:                       # хай бульбашка йде вгору (менший y)
        nx, ny = -nx, -ny
    amp = 84

    def C(t):
        a = amp * math.sin(math.pi * t)
        return ax + t * dx + a * nx, ay + t * dy + a * ny

    # справжня дуга — тонкий пунктир (контекст)
    pts, t = [], 0.0
    while t <= 1.0 + 1e-9:
        x, y = C(t)
        pts.append("%.1f,%.1f" % (x, y))
        t += 0.008
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2" '
             'stroke-dasharray="2,5"/>' % (" ".join(pts), MUTED))

    # ламана — хорди з вершинами
    n = 6
    verts = [C(i / n) for i in range(n + 1)]
    poly = " ".join("%.1f,%.1f" % (x, y) for x, y in verts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (poly, PATH))
    for x, y in verts:
        f.append(dot(x, y, 5, col=PATH))

    # переміщення — пряма зелена стрілка A→B
    f.append(arrow(ax, ay, bx, by, color=DISP, sw=3.4))

    # кінці
    f.append(dot(ax, ay, 7, col=INK))
    f.append(text(ax - 12, ay + 24, "A", size=15, bold=True))
    f.append(dot(bx, by, 7, col=INK))
    f.append(text(bx + 16, by - 4, "B", size=15, bold=True, anchor="start"))

    # підпис одного кроку в лінзі між ламаною й хордою
    (x0, y0), (x1, y1) = verts[0], verts[1]
    f.append(text((x0 + x1) / 2 + 16, (y0 + y1) / 2 + 20, "Δr₁",
                  size=13, color=PATH, bold=True, anchor="start"))

    # підписи ліній — у порожніх зонах, розведені
    cx1, cy1 = C(0.34)
    f.append(text(cx1 - 24, cy1 - 20, "справжня дуга  (шлях s)",
                  size=13, color=MUTED, bold=True, anchor="middle"))
    cx2, cy2 = C(0.70)
    f.append(text(cx2 + 44, cy2 - 16, "ламана  Lₙ = Σ|Δrᵢ|",
                  size=13, color=PATH, bold=True, anchor="middle"))
    mdx, mdy = ax + 0.52 * dx, ay + 0.52 * dy
    f.append(text(mdx + 26, mdy + 30, "переміщення  Δr = Σ Δrᵢ",
                  size=13, color=DISP, bold=True, anchor="middle"))

    b, bw, bh = textbox(W / 2, 455,
                        ["Довжина ламаної Lₙ = Σ|Δrᵢ| росте до довжини дуги s, коли кроки дрібнішають.",
                         "Зелена хорда Δr — та сама сума кроків, стягнута в один відрізок:  |Δr| ≤ Lₙ ≤ s."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "arc-polygon.svg"), W, H, *f)


# ── Фігура 7 (вставка math-path-length): елемент дуги ds = √(dx²+dy²) ──────────
def fig_ds_element():
    W, H = 780, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Елемент дуги — гіпотенуза крихітного трикутника",
                  size=15.5, bold=True))

    # маленький контекст-ескіз кривої (ліворуч угорі) з позначеним елементом
    cxs, cys = 150, 92
    cpts = []
    for k in range(0, 61):
        tt = k / 60.0
        x = cxs - 70 + 150 * tt
        y = cys + 26 * math.sin(2.4 * tt + 0.3) - 8 * tt
        cpts.append("%.1f,%.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(cpts), PATH))
    hx, hy = cxs + 44, cys + 26 * math.sin(2.4 * 0.78 + 0.3) - 8 * 0.78
    f.append(circle(hx, hy, 5, fill="#eafaf0", stroke=DISP, sw=2))
    f.append(text(cxs - 78, cys - 34, "траєкторія", size=12.5, color=MUTED,
                  bold=True, anchor="start"))
    f.append(text(hx + 10, hy + 4, "цей шматочок — крупним планом", size=11.5,
                  color=MUTED, anchor="start"))

    # великий трикутник елемента
    Px, Py = 250, 340          # нижній лівий (початок елемента)
    Qx, Qy = 590, 150          # верхній правий (кінець елемента)
    Rx, Ry = Qx, Py            # прямий кут унизу праворуч

    # катети
    f.append(line(Px, Py, Rx, Ry, color=INK, sw=2.2))           # dx
    f.append(line(Rx, Ry, Qx, Qy, color=INK, sw=2.2))           # dy
    # гіпотенуза — трохи вигнута дуга (сам шматочок кривої)
    mx, my = (Px + Qx) / 2 - 26, (Py + Qy) / 2 - 26
    f.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f" fill="none" '
             'stroke="%s" stroke-width="3.4"/>' % (Px, Py, mx, my, Qx, Qy, DISP))

    # позначка прямого кута
    s = 16
    f.append(('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" fill="none" '
              'stroke="%s" stroke-width="1.6"/>')
             % (Rx - s, Ry, Rx - s, Ry - s, Rx, Ry - s, INK))

    # вершини
    f.append(dot(Px, Py, 5, col=INK))
    f.append(dot(Qx, Qy, 5, col=INK))

    # підписи катетів і гіпотенузи (осторонь ліній)
    f.append(text((Px + Rx) / 2, Py + 26, "dx", size=15, color=INK, bold=True, italic=True))
    f.append(text(Rx + 24, (Ry + Qy) / 2, "dy", size=15, color=INK, bold=True, italic=True))
    f.append(text((Px + Qx) / 2 - 48, (Py + Qy) / 2 - 30, "ds", size=16,
                  color=DISP, bold=True, italic=True))

    b, bw, bh = textbox(W / 2, 405,
                        ["Крок уздовж кривої — гіпотенуза катетів dx, dy (у просторі — ще dz):",
                         "ds = √(dx² + dy² + dz²)   ⟹   s = ∫ ds = ∫ √(dx² + dy² + dz²)"],
                        size=13, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "ds-element.svg"), W, H, *f)


# ── Фігура 8 (вставка math-path-length): проєкція кроків на напрямок Δr ────────
def fig_projection_proof():
    W, H = 900, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Тіні кроків на напрямку Δr укладають |Δr|",
                  size=15.5, bold=True))

    ax, ay = 135, 330          # A на осі
    bx = 762                   # B на осі (та сама висота — û горизонтальний)
    by = ay
    amp = 150

    def C(t):
        x = ax + t * (bx - ax)
        y = ay - amp * math.sin(math.pi * t)
        return x, y

    n = 6
    verts = [C(i / n) for i in range(n + 1)]

    # тіні на осі — світлі плитки, що впритул укладають [A,B]
    for i in range(n):
        x0 = verts[i][0]
        x1 = verts[i + 1][0]
        tint = "#eef2f7" if i % 2 == 0 else "#dfe6ee"
        f.append(rect(x0, ay + 6, x1 - x0, 16, fill=tint, stroke="none", sw=0, rx=0))

    # вертикалі-проєкції від вершин до осі
    for x, y in verts:
        f.append(line(x, y, x, ay, color=MUTED, sw=1.3, dash="3,4"))

    # ламана (кроки)
    poly = " ".join("%.1f,%.1f" % (x, y) for x, y in verts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>'
             % (poly, PATH))
    for x, y in verts:
        f.append(dot(x, y, 5, col=PATH))

    # вісь û = напрямок переміщення (зелена стрілка A→B)
    f.append(arrow(ax, ay, bx, by, color=DISP, sw=3.4))
    f.append(text(bx + 14, by + 5, "û", size=15, color=DISP, bold=True,
                  italic=True, anchor="start"))

    # кінці
    f.append(dot(ax, ay, 7, col=INK))
    f.append(text(ax - 12, ay + 22, "A", size=15, bold=True))
    f.append(dot(bx, by, 7, col=INK))
    f.append(text(bx + 2, by + 22, "B", size=15, bold=True))

    # виділити один крок і його тінь
    (x2, y2), (x3, y3) = verts[2], verts[3]
    f.append(text((x2 + x3) / 2 - 30, (y2 + y3) / 2 - 12, "крок  |Δrᵢ|",
                  size=13, color=PATH, bold=True, anchor="middle"))
    f.append(text((x2 + x3) / 2, ay + 42, "тінь  Δrᵢ·û", size=13, color=INK,
                  bold=True, anchor="middle"))
    f.append(text((x2 + x3) / 2, ay + 60, "(тінь ≤ крок)", size=11.5,
                  color=MUTED, anchor="middle"))

    # підсумок під віссю
    f.append(text((ax + bx) / 2, ay + 92, "Σ тіней = |Δr|,  а кожна тінь ≤ свій крок  ⟹  |Δr| ≤ s",
                  size=13.5, color=INK, bold=True, anchor="middle"))

    b, bw, bh = textbox(W / 2, 448,
                        ["Проєкція кроку на напрямок переміщення û — його «тінь» Δrᵢ·û; тіні впритул укладають увесь",
                         "відрізок |Δr|. Кожна тінь не довша за свій крок, тож сума кроків s не менша за |Δr|."],
                        size=12.5, pad=11, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "projection-proof.svg"), W, H, *f)


if __name__ == "__main__":
    fig_path_vs_disp()
    fig_round_trip()
    fig_one_dim()
    fig_odo_noise()
    fig_odo_deadband()
    fig_arc_polygon()
    fig_ds_element()
    fig_projection_proof()
    print("OK: 8 фігур у", IMG)
