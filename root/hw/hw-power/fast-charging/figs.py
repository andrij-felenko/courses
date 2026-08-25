# -*- coding: utf-8 -*-
"""Фігури до теми «Прискорений заряд літію» (fast-charging).
Чистий Python + svgkit, вивід у ./img. Запуск: python figs.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: «обрив» потенціалу анода → зона осадження літію ────────────────
def fig_plating():
    W, H = 720, 400
    x0, y0, x1, y1 = 70, 60, 660, 320        # поле графіка
    # осі
    frags = [
        text(W / 2, 30, "Потенціал графітового анода під час заряду", size=17, bold=True),
        line(x0, y1, x1, y1, color=INK, sw=2),          # вісь X (струм/наповнення)
        line(x0, y0, x0, y1, color=INK, sw=2),          # вісь Y (потенціал)
        text(x1, y1 + 24, "струм заряду · наповнення · холод →", size=13, color=MUTED, anchor="end"),
        text(x0 - 8, y0 - 8, "потенціал анода (В vs Li/Li⁺)", size=13, color=MUTED, anchor="start"),
    ]
    # лінія 0 В — поріг осадження
    y_zero = y0 + (y1 - y0) * 0.62
    frags.append(line(x0, y_zero, x1, y_zero, color=POS, sw=1.6, dash="7 5"))
    frags.append(text(x1 - 6, y_zero - 8, "0 В — поріг осадження літію", size=12.5, color=POS, anchor="end", bold=True))
    # зона під нулем — небезпечна
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" opacity="0.7"/>'
                 % (x0 + 1, y_zero, x1 - x0 - 2, y1 - y_zero - 1))
    # робочий рівень ~0.1 В (де інтеркаляція здорова)
    y_safe = y0 + (y1 - y0) * 0.30
    frags.append(text(x0 + 8, y_safe - 8, "≈0.1 В — здорова інтеркаляція", size=12.5, color=FIELD, anchor="start", bold=True))
    # крива потенціалу: спадає з ростом струму/наповнення, «падає з обриву» під нуль
    import math
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        # плавно вниз, тоді різкий обрив після ~0.7
        base = 0.30 + 0.10 * t
        cliff = 0.55 * (1 / (1 + math.exp(-(t - 0.78) * 22)))
        frac = base + cliff                     # 0.30 → ~0.95 у частках поля
        px = x0 + (x1 - x0) * t
        py = y0 + (y1 - y0) * frac
        pts.append("%.1f,%.1f" % (px, py))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), NEG))
    # позначка точки обриву
    xb = x0 + (x1 - x0) * 0.82
    frags.append(circle(xb, y_zero, 5, fill=POS, stroke=POS))
    b, w, h = textbox(xb + 4, y0 + 34, "тут потенціал\nпробиває 0 В →\nметал осідає\nна аноді", size=12, fill="#fff6f5", stroke=POS)
    frags.append(b)
    # підпис зон (тримаємо всередині поля графіка)
    b2, _, _ = textbox(x0 + 176, y1 - 26, "здоровий заряд: іони входять у ґрати графіту", size=12, fill="#eafaf0", stroke=FIELD)
    frags.append(b2)
    render(os.path.join(IMG, "plating-cliff.svg"), W, H, *frags)


# ── Фігура 2: одноступеневий CC проти багатоступеневого (boost / step) ───────
def fig_step():
    W, H = 720, 430
    x0, y0, x1, y1 = 70, 92, 660, 330
    frags = [
        text(W / 2, 30, "Один великий струм проти сходинок (step / boost charging)", size=16, bold=True),
        line(x0, y1, x1, y1, color=INK, sw=2),
        line(x0, y0, x0, y1, color=INK, sw=2),
        text(x1, y1 + 24, "наповнення (SOC) →", size=13, color=MUTED, anchor="end"),
        text(x0 - 8, y0 - 12, "струм заряду", size=13, color=MUTED, anchor="start"),
    ]
    def yfrac(f):   # f=0 верх поля (великий струм), f=1 низ (малий струм)
        return y0 + (y1 - y0) * f
    # межа безпечного струму: спадає з ростом SOC (що повніше — то менший струм без осадження)
    def ylim(t):
        return yfrac(0.20 + 0.66 * t)
    limpts = ["%.1f,%.1f" % (x0 + (x1 - x0) * (i / 100.0), ylim(i / 100.0)) for i in range(0, 101)]
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="7 5"/>'
                 % (" ".join(limpts), POS))
    frags.append(text(x1 - 6, ylim(1.0) + 20, "межа без осадження (падає з наповненням)", size=12, color=POS, anchor="end", bold=True))

    # наївний один великий струм — горизонталь угорі, що ПЕРЕТИНАЄ межу
    yhi = yfrac(0.10)
    tcross = 0.62
    xcross = x0 + (x1 - x0) * tcross
    frags.append(line(x0, yhi, xcross, yhi, color=NEG, sw=3))
    frags.append(line(xcross, yhi, x1, yhi, color=NEG, sw=3, dash="4 4"))
    frags.append(circle(xcross, ylim(tcross), 5.5, fill=POS, stroke=POS))
    frags.append(text(x0 + 6, yhi - 9, "наївно: один великий струм до кінця", size=12, color=NEG, anchor="start", bold=True))
    b, w, h = textbox(xcross + 108, yfrac(0.30),
                      "за цією точкою наївний струм\nуже над межею → осадження",
                      size=11.5, fill="#eaf0fd", stroke=NEG)
    frags.append(b)

    # сходинки — тримаються ПІД межею (кожна сходинка нижча за межу у своєму вікні)
    steps = [(0.00, 0.30), (0.34, 0.46), (0.58, 0.62), (0.80, 0.78)]  # (SOC-старт, рівень частки)
    prev = None
    for k, (s, lvl) in enumerate(steps):
        xa = x0 + (x1 - x0) * s
        xb = x0 + (x1 - x0) * (steps[k + 1][0] if k + 1 < len(steps) else 1.0)
        ys = yfrac(lvl)
        frags.append(line(xa, ys, xb, ys, color=FIELD, sw=3.5))
        if prev is not None:
            frags.append(line(xa, prev, xa, ys, color=FIELD, sw=3.5))   # вертикальний спад між сходинками
        prev = ys
    frags.append(text(x0 + 8, yfrac(0.30) + 20, "сходинки: струм падає з наповненням, тримаючись під межею",
                      size=12, color=FIELD, bold=True, anchor="start"))
    render(os.path.join(IMG, "step-charge.svg"), W, H, *frags)


# ── Фігура 3: трилема швидкість — ресурс — тепло ─────────────────────────────
def fig_trilemma():
    W, H = 640, 400
    cx, cy, R = 320, 232, 132
    import math
    # вершини трикутника
    ang = [-90, 150, 30]
    labels = ["ШВИДКІСТЬ\n(великий струм)", "РЕСУРС\n(без осадження,\nмале старіння)", "ТЕПЛО\n(P = I²·R,\nвідведення)"]
    cols = [NEG, FIELD, POS]
    pts = []
    for a in ang:
        pts.append((cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))))
    frags = [text(W / 2, 34, "Трилема прискореного заряду", size=17, bold=True)]
    # сторони
    tri = " ".join("%.1f,%.1f" % p for p in pts)
    frags.append('<polygon points="%s" fill="#f4f6f8" stroke="%s" stroke-width="2"/>' % (tri, MUTED))
    # центр — компроміс
    b, w, h = textbox(cx, cy + 6, "натягни один кут —\nдва інші напнуться", size=12.5, fill=BG, stroke=INK, bold=True)
    frags.append(b)
    # вершини-рамки
    for (px, py), lab, col in zip(pts, labels, cols):
        # трохи винести рамку за вершину
        ox = px + (px - cx) * 0.16
        oy = py + (py - cy) * 0.16
        bb, ww, hh = textbox(ox, oy, lab, size=12.5, fill="#ffffff", stroke=col, color=col, bold=True)
        frags.append(bb)
    render(os.path.join(IMG, "trilemma.svg"), W, H, *frags)


# ── Фігура 4 (math-вставка): бюджет потенціалу анода — з чого лишається зазор ─
def fig_budget():
    W, H = 720, 430
    x0, y0, x1, y1 = 90, 70, 470, 360      # поле стовпчиків
    frags = [
        text(W / 2, 30, "Бюджет потенціалу анода: що з'їдає зазор до 0 В", size=16, bold=True),
        line(x0, y1, x1, y1, color=INK, sw=2),
        line(x0, y0, x0, y1, color=INK, sw=2),
        text(x0 - 8, y0 - 10, "потенціал анода (мВ vs Li/Li⁺)", size=12.5, color=MUTED, anchor="start"),
    ]
    # шкала: 0..200 мВ по висоті поля (y1 = 0 мВ, y0 = 200 мВ)
    def yv(mv):
        return y1 - (y1 - y0) * (mv / 200.0)
    # сітка 0/50/100/150/200
    for mv in (0, 50, 100, 150, 200):
        yy = yv(mv)
        frags.append(line(x0 - 4, yy, x1, yy, color="#e5e7eb", sw=1))
        frags.append(text(x0 - 8, yy + 4, "%d" % mv, size=11, color=MUTED, anchor="end"))
    # лінія 0 В — поріг осадження (жирна червона по осі X)
    frags.append(line(x0, yv(0), x1, yv(0), color=POS, sw=2.2))
    frags.append(text(x1 + 6, yv(0) + 4, "0 В — поріг", size=11.5, color=POS, anchor="start", bold=True))

    # стовпчик-водоспад: Uрівн(SOC) → −η → −I·Rвн → лишок Uанод
    bx = x0 + 60
    bw = 120
    Ueq = 120.0     # рівноважний при цьому SOC, мВ
    eta = 55.0      # перенапруга
    iR  = 40.0      # омічне падіння
    rest = Ueq - eta - iR   # 25 мВ зазор
    # 1) повний рівноважний
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eafaf0" stroke="%s" stroke-width="1.6"/>'
                 % (bx, yv(Ueq), bw, yv(0) - yv(Ueq), FIELD))
    frags.append(text(bx + bw / 2, yv(Ueq) - 8, "Uрівн(SOC)", size=12, color=FIELD, bold=True))
    frags.append(text(bx + bw / 2, yv(Ueq) + 18, "≈120 мВ", size=11.5, color=FIELD))
    # 2) відняти η (від верху вниз)
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.4"/>'
                 % (bx, yv(Ueq), bw, yv(Ueq - eta) - yv(Ueq), POS))
    frags.append(text(bx + bw + 8, (yv(Ueq) + yv(Ueq - eta)) / 2 + 4, "− η(I) ≈ 55", size=11.5, color=POS, anchor="start"))
    # 3) відняти I·Rвн
    frags.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.4"/>'
                 % (bx, yv(Ueq - eta), bw, yv(rest) - yv(Ueq - eta), POS))
    frags.append(text(bx + bw + 8, (yv(Ueq - eta) + yv(rest)) / 2 + 4, "− I·Rвн ≈ 40", size=11.5, color=POS, anchor="start"))
    # лишок — зелена риска на рівні rest
    frags.append(line(bx - 6, yv(rest), bx + bw + 6, yv(rest), color=INK, sw=2, dash="5 4"))
    b, w, h = textbox(x1 + 118, yv(rest) + 2, "лишок Uанод\n≈ 25 мВ > 0\n(поки безпечно)",
                      size=11.5, fill="#ffffff", stroke=INK, bold=True)
    frags.append(b)
    # підпис-стрілка «більший струм тисне η та I·R вниз»
    frags.append(text(x0 + 100, y1 + 26, "більший струм / вищий SOC / холод → η та I·R ростуть, лишок → 0",
                      size=12, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "potential-budget.svg"), W, H, *frags)


# ── Фігура 5 (math-вставка): стеля струму Imax(SOC), виведена з бюджету ───────
def fig_imax():
    import math
    W, H = 720, 400
    x0, y0, x1, y1 = 80, 66, 660, 320
    frags = [
        text(W / 2, 30, "Стеля струму Imax(SOC): зазор ділимо на опір кінетики", size=15.5, bold=True),
        line(x0, y1, x1, y1, color=INK, sw=2),
        line(x0, y0, x0, y1, color=INK, sw=2),
        text(x1, y1 + 24, "наповнення SOC →", size=13, color=MUTED, anchor="end"),
        text(x0 - 8, y0 - 10, "Imax (C)", size=13, color=MUTED, anchor="start"),
    ]
    # Imax(SOC) ∝ (Uрівн(SOC) − 0) / (dη/dI + Rвн); і чисельник падає, і знаменник росте з SOC
    def imax(t):        # t = SOC 0..1, повертає C-rate
        Ueq = 0.16 - 0.11 * t          # рівноважний потенціал падає ~160→50 мВ
        slope = 0.020 + 0.055 * t      # ефективний опір кінетики росте з SOC (В на C)
        return Ueq / slope
    # крива (тепла — 25 °C)
    pts, pts_cold = [], []
    for i in range(0, 101):
        t = i / 100.0
        c = imax(t)
        pc = x0 + (x1 - x0) * t
        # шкала Y: 0..3C
        py = y1 - (y1 - y0) * min(c, 3.0) / 3.0
        pts.append("%.1f,%.1f" % (pc, py))
        # холод: рівноважний той самий, але опір кінетики ~вдвічі більший
        cc = (0.16 - 0.11 * t) / (0.045 + 0.11 * t)
        pyc = y1 - (y1 - y0) * min(cc, 3.0) / 3.0
        pts_cold.append("%.1f,%.1f" % (pc, pyc))
    # осі-риски по Y (0..3C)
    for cc in (0, 1, 2, 3):
        yy = y1 - (y1 - y0) * cc / 3.0
        frags.append(line(x0 - 4, yy, x1, yy, color="#eef0f2", sw=1))
        frags.append(text(x0 - 8, yy + 4, "%dC" % cc, size=11, color=MUTED, anchor="end"))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3"/>' % (" ".join(pts), FIELD))
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="7 5"/>' % (" ".join(pts_cold), NEG))
    # підпис теплої кривої — на спадній ділянці (SOC≈0.62), трохи над кривою, гарантовано в полі
    yt = y1 - (y1 - y0) * min(imax(0.62), 3.0) / 3.0
    frags.append(text(x0 + (x1 - x0) * 0.63, yt - 12, "25 °C: межа падає з SOC", size=12, color=FIELD, bold=True, anchor="middle"))
    frags.append(text(x0 + (x1 - x0) * 0.30, y1 - (y1 - y0) * 0.72 / 3.0 + 20, "холод: та сама межа, нижча (опір ×2)", size=11.5, color=NEG, bold=True, anchor="start"))
    # заливка «безпечно/осадження»
    frags.append(text(x1 - 6, y0 + 16, "над кривою — осадження", size=11.5, color=POS, anchor="end", bold=True))
    render(os.path.join(IMG, "imax-soc.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_plating()
    fig_step()
    fig_trilemma()
    fig_budget()
    fig_imax()
    print("OK: 5 figures ->", IMG)
