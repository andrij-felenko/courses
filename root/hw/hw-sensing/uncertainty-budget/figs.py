# -*- coding: utf-8 -*-
"""Фігури до теми «Бюджет невизначеності».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── дрібні помічники ────────────────────────────────────────────────────────
def polyline(pts, color=INK, sw=2.4, dash=None, fill="none"):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (p, fill, color, sw, d))


def polygon(pts, fill=FILL, stroke=LINE, sw=2.0):
    p = " ".join("%.1f,%.1f" % (x, y) for (x, y) in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (p, fill, stroke, sw))


def head_at(x, y, dx, dy, color=INK, size=10):
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    bx, by = x - ux * size, y - uy * size
    nx, ny = -uy, ux
    return ('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f z" fill="%s"/>'
            % (x, y, bx + nx * size * 0.5, by + ny * size * 0.5,
               bx - nx * size * 0.5, by - ny * size * 0.5, color))


def varrow(x1, y1, x2, y2, color=LINE, sw=2.4, head=11):
    return line(x1, y1, x2, y2, color=color, sw=sw) + head_at(x2, y2, x2 - x1, y2 - y1, color, head)


def tick(x, y, h=7, color=INK, sw=1.6):
    return line(x, y - h, x, y + h, color=color, sw=sw)


def arc_between(cx, cy, r, a0deg, a1deg, color=MUTED, sw=1.6):
    a0, a1 = math.radians(a0deg), math.radians(a1deg)
    x0, y0 = cx + r * math.cos(a0), cy - r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy - r * math.sin(a1)
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 0 0 %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"/>' % (x0, y0, r, r, x1, y1, color, sw))


# ── Фігура 1: зведення будь-якого «±» до стандартного відхилення σ ────────────
def fig_distributions():
    W, H = 860, 384
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Спільна валюта: будь-яке «±» зводимо до одного σ", size=17, bold=True))
    f.append(text(W / 2, 52, "стандартна невизначеність u = 1σ", size=13, color=MUTED))

    base = 252              # рівень базової лінії
    a = 66                  # піврозмах ±a у пікселях
    top = base - 96         # верх фігури
    cols = [160, 430, 700]

    def baseline(cx, la, lb):
        out = line(cx - a - 26, base, cx + a + 26, base, color=MUTED, sw=1.5)
        out += tick(cx - a, base) + tick(cx + a, base) + tick(cx, base, h=5, color=MUTED)
        out += text(cx - a, base + 22, la, size=12, color=INK)
        out += text(cx + a, base + 22, lb, size=12, color=INK)
        return out

    # (1) рівномірний
    cx = cols[0]
    f.append(rect(cx - a, top, 2 * a, base - top, fill="#eef1fb", stroke=NEG, sw=2.2, rx=0))
    f.append(baseline(cx, "−a", "+a"))
    f.append(text(cx, top - 12, "рівномірний", size=13, bold=True, color=NEG))
    f.append(fitbox(cx - 96, 300, 192, 54, "знаєте лише межі ±a\nσ = a / √3",
                    size=13, pad=8, fill=FILL, stroke=NEG, sw=1.4, bold=True))

    # (2) трикутний
    cx = cols[1]
    f.append(polygon([(cx - a, base), (cx, top), (cx + a, base)],
                     fill="#eef6ef", stroke=FIELD, sw=2.2))
    f.append(baseline(cx, "−a", "+a"))
    f.append(text(cx, top - 12, "трикутний", size=13, bold=True, color=FIELD))
    f.append(fitbox(cx - 96, 300, 192, 54, "центр імовірніший\nσ = a / √6",
                    size=13, pad=8, fill=FILL, stroke=FIELD, sw=1.4, bold=True))

    # (3) нормальний — дано вже як 95%-й інтервал ±U
    cx = cols[2]
    sig = a / 2.0                         # ±2σ = ±a (=±U)
    pts = []
    for i in range(81):
        xx = cx - a - 8 + (2 * a + 16) * i / 80.0
        z = (xx - cx) / sig
        yy = base - 96 * math.exp(-0.5 * z * z)
        pts.append((xx, yy))
    # затінити смугу ±2σ
    band = [(cx - a, base)] + [(x, y) for (x, y) in pts if cx - a <= x <= cx + a] + [(cx + a, base)]
    f.append(polygon(band, fill="#fdecea", stroke='none', sw=0))
    f.append(polyline(pts, color=POS, sw=2.6))
    f.append(baseline(cx, "−U", "+U"))
    f.append(text(cx, top - 12, "нормальний", size=13, bold=True, color=POS))
    f.append(text(cx, top + 30, "±U = ±2σ", size=11, color=POS))
    f.append(fitbox(cx - 96, 300, 192, 54, "дано як 95%: ±U\nσ = U / 2",
                    size=13, pad=8, fill=FILL, stroke=POS, sw=1.4, bold=True))

    return render(os.path.join(IMG, "distributions-to-sigma.svg"), W, H, *f)


# ── Фігура 2: квадратне складання — гіпотенуза з катетів ──────────────────────
def fig_quadrature():
    W, H = 860, 432
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Незалежні невизначеності складаються по квадрату — як катети в гіпотенузу",
                  size=16, bold=True))

    def right_square(x, y, s, dirx, diry):
        # маленький квадратик — позначка прямого кута у вершині (x,y)
        return polyline([(x + dirx * s, y), (x + dirx * s, y + diry * s), (x, y + diry * s)],
                        color=MUTED, sw=1.4)

    # ── ЛІВОРУЧ: співмірні внески ──
    Ox, Oy = 150, 330
    u1 = 190; u2 = 150
    A = (Ox + u1, Oy)          # прямий кут тут
    B = (Ox + u1, Oy - u2)
    f.append(polygon([(Ox, Oy), A, B], fill="#f7f9fb", stroke=INK, sw=1.6))
    f.append(right_square(A[0], A[1], -14, 1, -1))       # кут при A
    f.append(varrow(Ox, Oy, A[0], A[1], color=NEG, sw=3, head=11))    # катет u1
    f.append(varrow(A[0], A[1], B[0], B[1], color=FIELD, sw=3, head=11))  # катет u2
    f.append(varrow(Ox, Oy, B[0], B[1], color=POS, sw=3.2, head=12))  # гіпотенуза u_c
    f.append(text((Ox + A[0]) / 2, Oy + 24, "u₁", size=15, bold=True, italic=True, color=NEG))
    f.append(text(A[0] + 16, (A[1] + B[1]) / 2 + 4, "u₂", size=15, bold=True, italic=True, color=FIELD, anchor="start"))
    f.append(text((Ox + B[0]) / 2 - 22, (Oy + B[1]) / 2 - 8, "u_c", size=15, bold=True, italic=True, color=POS, anchor="end"))
    f.append(fitbox(Ox - 4, 350, 200, 40, "співмірні внески", size=12, pad=7,
                    fill=FILL, stroke=INK, sw=1.3, bold=True))

    # ── ПРАВОРУЧ: дрібний другий внесок майже зникає ──
    Ox2, Oy2 = 520, 330
    v1 = 220; v2 = 30
    A2 = (Ox2 + v1, Oy2)
    B2 = (Ox2 + v1, Oy2 - v2)
    f.append(polygon([(Ox2, Oy2), A2, B2], fill="#f7f9fb", stroke=INK, sw=1.6))
    f.append(varrow(Ox2, Oy2, A2[0], A2[1], color=NEG, sw=3, head=11))
    f.append(varrow(A2[0], A2[1], B2[0], B2[1], color=FIELD, sw=3, head=10))
    f.append(varrow(Ox2, Oy2, B2[0], B2[1], color=POS, sw=3.2, head=12))
    f.append(text((Ox2 + A2[0]) / 2, Oy2 + 24, "u₁", size=15, bold=True, italic=True, color=NEG))
    f.append(text(A2[0] + 14, A2[1] - 20, "u₂ (мале)", size=12, bold=True, italic=True, color=FIELD, anchor="start"))
    f.append(fitbox(Ox2 - 4, 350, 250, 40, "u₂ ≪ u₁   →   u_c ≈ u₁", size=12, pad=7,
                    fill="#fdecea", stroke=POS, sw=1.3, bold=True))

    b, w, h = textbox(W / 2, H - 22,
                      "у лоб u₁ + u₂ — це найгірший випадок (усі похибки змовились), майже неможливий",
                      size=13, pad=9, fill="#fff6e9", stroke=MUTED, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "quadrature-triangle.svg"), W, H, *f)


# ── Фігура 3: бюджет маятника — котрий рядок переважає ────────────────────────
def fig_budget():
    W, H = 880, 404
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Бюджет невизначеності для  g = 4π²L / T²", size=17, bold=True))

    x0 = 250                          # початок смуг (вісь)
    maxbar = 470                      # найдовша смуга у пікселях
    per = maxbar / 0.0502             # пікселів на (м/с²)

    # вісь
    f.append(line(x0, 84, x0, 250, color=MUTED, sw=1.6))
    f.append(text(x0 + maxbar / 2, 274, "внесок у u(g),  м/с²", size=12, color=MUTED))

    def bar_row(yc, name, subtype, val, share, color):
        out = rect(x0, yc - 22, val * per, 44, fill=color, stroke=color, sw=1, rx=4)
        out += text(x0 - 12, yc - 4, name, size=14, bold=True, anchor="end")
        out += text(x0 - 12, yc + 15, subtype, size=11, color=MUTED, anchor="end")
        out += text(x0 + val * per + 10, yc + 5,
                    "%.4f  (%s)" % (val, share), size=13, bold=True, color=color, anchor="start")
        return out

    f.append(bar_row(120, "час T", "тип A (розкид повторів)", 0.0502, "98.5%", POS))
    f.append(bar_row(200, "довжина L", "тип B (поділка рулетки)", 0.0062, "1.5%", NEG))

    # підсумок складання
    f.append(fitbox(x0 - 2, 296, 560, 44,
                    "u_c = √(0.0502² + 0.0062²) = 0.0505 м/с²   →   U = 2·u_c = 0.10 м/с²",
                    size=13, pad=8, fill=FILL, stroke=INK, sw=1.4, bold=True))

    b, w, h = textbox(W / 2, H - 22,
                      "g = (9.81 ± 0.10) м/с² — час дає 98.5% розкиду, отже покращувати треба його, не довжину",
                      size=13, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "pendulum-budget.svg"), W, H, *f)


# ── Фігура 4: лінеаризація — дотична переносить смугу входу в смугу виходу ─────
def fig_linearize():
    W, H = 880, 476
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Коефіцієнт чутливості — це нахил дотичної:  c = ∂f/∂xᵢ",
                  size=17, bold=True))
    f.append(text(W / 2, 50, "смугу входу ±u(xᵢ) дотична переносить у смугу виходу ±c·u(xᵢ)",
                  size=13, color=MUTED))

    xL, xR, yT, yB = 150, 720, 100, 372
    YMAX = 120.0

    def PX(x):
        return xL + (x / 10.0) * (xR - xL)

    def PY(y):
        return yB - (y / YMAX) * (yB - yT)

    def fdata(x):
        return 10 + 2.4 * (x ** 1.6)

    def slope(x):
        return 3.84 * (x ** 0.6)        # аналітична похідна 2.4·1.6·x^0.6

    xs, us = 5.0, 1.35
    ys, c = fdata(xs), slope(xs)
    xlo, xhi = xs - us, xs + us
    ylo, yhi = ys - c * us, ys + c * us          # смуга виходу через дотичну

    # шаровані смуги (малюємо першими, під кривою)
    f.append(rect(PX(xlo), yT, PX(xhi) - PX(xlo), yB - yT, fill="#eef1fb", stroke='none', sw=0, rx=0))
    f.append(rect(xL, PY(yhi), PX(xhi) - xL, PY(ylo) - PY(yhi), fill="#fdecea", stroke='none', sw=0, rx=0))

    # осі
    f.append(varrow(xL, yB, xR + 16, yB, color=INK, sw=1.8, head=10))
    f.append(varrow(xL, yB, xL, yT - 16, color=INK, sw=1.8, head=10))
    f.append(text(xR + 14, yB + 24, "xᵢ (вхід)", size=13, color=INK, anchor="end"))
    f.append(text(xL + 4, yT - 20, "y = f(x)", size=13, color=INK, anchor="start"))

    # крива моделі
    pts = [(PX(x), PY(fdata(x))) for x in [i * 0.2 for i in range(0, 51)]]
    f.append(polyline(pts, color=FIELD, sw=3.0))
    f.append(text(PX(9.4), PY(fdata(9.1)), "y = f(x)", size=12, color=FIELD, anchor="start"))

    # дотична (пунктир) через точку оцінки
    tx0, tx1 = xs - 2.4, xs + 2.4
    f.append(line(PX(tx0), PY(ys + c * (tx0 - xs)), PX(tx1), PY(ys + c * (tx1 - xs)),
                  color=POS, sw=2.4, dash="8 5"))
    f.append(text(PX(tx1) + 6, PY(ys + c * (tx1 - xs)) + 4, "дотична", size=12, color=POS, anchor="start"))

    # проєкція країв смуги входу вгору до дотичної, тоді до осі y
    for xb, yb_ in [(xlo, ylo), (xhi, yhi)]:
        f.append(line(PX(xb), yB, PX(xb), PY(yb_), color=MUTED, sw=1.4, dash="4 4"))
        f.append(line(PX(xb), PY(yb_), xL, PY(yb_), color=MUTED, sw=1.4, dash="4 4"))
    f.append(line(PX(xs), yB, PX(xs), PY(ys), color=MUTED, sw=1.2, dash="2 4"))
    f.append(circle(PX(xs), PY(ys), 4.5, fill=INK, stroke=INK, sw=1))

    # позначки смуги входу
    f.append(tick(PX(xlo), yB, h=6))
    f.append(tick(PX(xhi), yB, h=6))
    f.append(tick(PX(xs), yB, h=6))
    f.append(text(PX(xs), yB + 24, "оцінка xᵢ", size=12, color=INK))
    f.append(varrow(PX(xlo), yB + 40, PX(xhi), yB + 40, color=NEG, sw=1.6, head=7))
    f.append(varrow(PX(xhi), yB + 40, PX(xlo), yB + 40, color=NEG, sw=1.6, head=7))
    f.append(text(PX(xs), yB + 58, "2·u(xᵢ)", size=13, bold=True, color=NEG))

    # позначки смуги виходу
    f.append(varrow(xL - 34, PY(ylo), xL - 34, PY(yhi), color=POS, sw=1.6, head=7))
    f.append(varrow(xL - 34, PY(yhi), xL - 34, PY(ylo), color=POS, sw=1.6, head=7))
    f.append(text(xL - 44, PY(ys) + 4, "2·c·u(xᵢ)", size=13, bold=True, color=POS, anchor="end"))

    # трикутник нахилу на дотичній
    hx0, hx1 = xs + 0.6, xs + 1.8
    yhoriz = ys + c * (hx0 - xs)
    f.append(line(PX(hx0), PY(yhoriz), PX(hx1), PY(yhoriz), color=INK, sw=1.4))
    f.append(line(PX(hx1), PY(yhoriz), PX(hx1), PY(ys + c * (hx1 - xs)), color=INK, sw=1.4))
    f.append(text(PX((hx0 + hx1) / 2), PY(yhoriz) + 16, "Δx", size=12, color=MUTED))
    f.append(text(PX(hx1) + 8, PY(ys + c * ((hx0 + hx1) / 2 - xs)), "c·Δx", size=12, color=MUTED, anchor="start"))

    b, w, h = textbox(566, 156, "де крива відходить від дотичної,\nлінеаризація вже бреше",
                      size=12, pad=8, fill="#fff6e9", stroke=MUTED, sw=1.2)
    f.append(b)
    return render(os.path.join(IMG, "propagation-linearize.svg"), W, H, *f)


# ── Фігура 5: загальний закон = теорема косинусів, кут = кореляція ─────────────
def fig_correlation_cosine():
    W, H = 900, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Загальний закон — це теорема косинусів: кут між внесками є кореляцією",
                  size=16, bold=True))
    f.append(text(W / 2, 52, "u_c² = (c₁u₁)² + (c₂u₂)² + 2·(c₁u₁)(c₂u₂)·r,      r = cos θ",
                  size=14, color=MUTED))

    L1, L2 = 118.0, 84.0
    Oy = 306
    cols = [(178, "θ = 45°", "r = +0.71", "корелюють →\nсмуга ширша", 45, POS),
            (458, "θ = 90°", "r = 0", "незалежні →\nПіфагор (RSS)", 90, INK),
            (738, "θ = 135°", "r = −0.71", "антикорелюють →\nчастково гасяться", 135, NEG)]
    for (cx, ttl, rr, note, thdeg, col) in cols:
        Ox = cx - 58
        th = math.radians(thdeg)
        t1 = (Ox + L1, Oy)
        t2 = (t1[0] + L2 * math.cos(th), t1[1] - L2 * math.sin(th))
        # внески «голова-до-хвоста» і рівнодійна
        f.append(varrow(Ox, Oy, t1[0], t1[1], color=NEG, sw=2.6, head=10))
        f.append(varrow(t1[0], t1[1], t2[0], t2[1], color=FIELD, sw=2.6, head=10))
        f.append(varrow(Ox, Oy, t2[0], t2[1], color=col, sw=3.4, head=12))
        # кут θ у спільному початку: копія C₂ пунктиром + дуга
        f.append(line(Ox, Oy, Ox + 46 * math.cos(th), Oy - 46 * math.sin(th),
                      color=MUTED, sw=1.2, dash="3 3"))
        f.append(arc_between(Ox, Oy, 30, 0, thdeg))
        lab = math.radians(thdeg / 2.0)
        f.append(text(Ox + 44 * math.cos(lab), Oy - 44 * math.sin(lab) + 4, "θ",
                      size=13, bold=True, italic=True, color=MUTED, anchor="middle"))
        # підписи катетів
        f.append(text((Ox + t1[0]) / 2, Oy + 20, "c₁u₁", size=12, bold=True, italic=True, color=NEG))
        f.append(text(t1[0] + 8, (t1[1] + t2[1]) / 2, "c₂u₂", size=12, bold=True, italic=True,
                      color=FIELD, anchor="start"))
        # шапка колонки і підсумок
        f.append(text(cx, 92, ttl, size=15, bold=True))
        f.append(text(cx, 114, rr, size=14, bold=True, color=col))
        f.append(fitbox(cx - 92, 356, 184, 54, note, size=12, pad=7, fill=FILL, stroke=col, sw=1.3, bold=True))
    return render(os.path.join(IMG, "correlation-cosine.svg"), W, H, *f)


# ── Фігура 6: історична вісь — народження спільної мови невизначеності ─────────
def fig_gum_timeline():
    W, H = 980, 492
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Народження спільної мови невизначеності", size=18, bold=True))

    # верхня смуга: зсув парадигми «похибки → невизначеність»
    f.append(fitbox(64, 58, 268, 56,
                    "ДО: «похибки»\nкожна лабораторія по-своєму, ± означає різне",
                    size=12, pad=7, fill="#fdecea", stroke=POS, sw=1.3, bold=True))
    f.append(varrow(352, 86, 632, 86, color=MUTED, sw=2.6, head=13))
    f.append(fitbox(648, 58, 268, 56,
                    "ПІСЛЯ: «оцінка невизначеності»\nспільна мова: тип A/B, u_c, U = k·u_c",
                    size=12, pad=7, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True))

    axisY = 300
    f.append(varrow(60, axisY, 918, axisY, color=MUTED, sw=2.0, head=12))
    f.append(text(926, axisY + 4, "час", size=12, color=MUTED, anchor="start"))

    nodes = [
        (120, "1977", "CIPM просить BIPM дати раду виразу невизначеності", "up", NEG),
        (268, "1980", "Робоча група, 11 лабораторій; Р. Каарлс — доповідач. INC-1: поділ на тип A / тип B", "down", POS),
        (416, "1981", "CIPM ухвалює INC-1 (Реком. 1, CI-1981); підтверджено 1986", "up", NEG),
        (564, "1993", "Виходить GUM (ISO/IEC Guide 98) — від імені семи організацій", "down", FIELD),
        (712, "1995", "Виправлене перевидання — канонічний текст", "up", NEG),
        (860, "2008", "JCGM 100: вільний доступ, супровід JCGM", "down", FIELD),
    ]
    wbox, hbox = 220, 86
    for (nx, yr, desc, side, col) in nodes:
        bx = max(10, min(nx - wbox / 2, W - 10 - wbox))
        if side == "up":
            by = axisY - 26 - hbox
            f.append(line(nx, axisY - 9, nx, by + hbox, color=MUTED, sw=1.4, dash="3 3"))
            f.append(text(nx, axisY + 24, yr, size=15, bold=True, color=col))
        else:
            by = axisY + 26
            f.append(line(nx, axisY + 9, nx, by, color=MUTED, sw=1.4, dash="3 3"))
            f.append(text(nx, axisY - 14, yr, size=15, bold=True, color=col))
        f.append(fitbox(bx, by, wbox, hbox, desc, size=12, pad=8, fill=FILL, stroke=col, sw=1.4))
        f.append(circle(nx, axisY, 8, fill=col, stroke=col, sw=1))
    return render(os.path.join(IMG, "gum-timeline.svg"), W, H, *f)


# ── Фігура: поширення РОЗПОДІЛІВ — входи за формою, вихід за формою ────────────
def _bell_pts(cx, base, halfw, height, n=64):
    pts = []
    sig = halfw / 2.4
    for i in range(n + 1):
        xx = cx - halfw + 2 * halfw * i / n
        z = (xx - cx) / sig
        pts.append((xx, base - height * math.exp(-0.5 * z * z)))
    return pts


def fig_mc_propagation():
    W, H = 960, 480
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Монте-Карло: розкидати ВХОДИ за їхніми розподілами, дивитися на розкид ВИХОДУ",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "замість похідних-коефіцієнтів у гру йде вся форма кожного входу", size=13, color=MUTED))

    # ── вхід L: рівномірний (синій) ──
    cx = 150
    yL = 186
    f.append(text(cx, 92, "вхід  L", size=13, bold=True, color=NEG))
    f.append(rect(cx - 52, 142, 104, yL - 142, fill="#eef1fb", stroke=NEG, sw=2.2, rx=0))
    f.append(line(cx - 74, yL, cx + 74, yL, color=MUTED, sw=1.5))
    f.append(text(cx, 208, "рівномірний  ±1 мм", size=12, color=MUTED))

    # ── вхід T: нормальний (червоний) ──
    yT = 330
    f.append(text(cx, 250, "вхід  T", size=13, bold=True, color=POS))
    band = _bell_pts(cx, yT, 60, 70)
    f.append(polygon([(cx - 60, yT)] + band + [(cx + 60, yT)], fill="#fdecea", stroke=POS, sw=2.4))
    f.append(line(cx - 78, yT, cx + 78, yT, color=MUTED, sw=1.5))
    f.append(text(cx, 352, "нормальний,  σ = 0.25 с", size=12, color=MUTED))

    # ── модель ──
    b, w, h = textbox(476, 210, "g = 4π²L / T²", size=18, pad=16, fill=FILL, stroke=INK, sw=1.8, bold=True)
    f.append(b)
    f.append(text(476, 252, "кожну з  M  вибірок — крізь модель", size=12, color=MUTED))

    # стрілки входів у модель
    f.append(varrow(212, 168, 476 - w / 2 - 8, 200, color=NEG, sw=2.4, head=10))
    f.append(varrow(212, 300, 476 - w / 2 - 8, 224, color=POS, sw=2.4, head=10))
    # стрілка з моделі у вихід
    f.append(varrow(476 + w / 2 + 8, 212, 648, 212, color=INK, sw=2.4, head=11))

    # ── вихід: розподіл g ──
    ox = 792
    yO = 300
    f.append(text(ox, 92, "розподіл  g  (вихід)", size=13, bold=True, color=INK))
    obell = _bell_pts(ox, yO, 92, 150)
    q = 75.0
    inband = [(x, y) for (x, y) in obell if ox - q <= x <= ox + q]
    f.append(polygon([(ox - q, yO)] + inband + [(ox + q, yO)], fill="#eef6ef", stroke='none', sw=0))
    f.append(polyline(obell, color=FIELD, sw=2.8))
    f.append(line(ox - 104, yO, ox + 104, yO, color=MUTED, sw=1.5))
    # бракет σ
    f.append(varrow(ox - 38, yO + 24, ox + 38, yO + 24, color=INK, sw=1.6, head=7))
    f.append(varrow(ox + 38, yO + 24, ox - 38, yO + 24, color=INK, sw=1.6, head=7))
    f.append(text(ox, yO + 44, "σ виходу  =  u_c", size=12, bold=True, color=INK))
    # бракет перцентилів
    f.append(varrow(ox - q, yO + 66, ox + q, yO + 66, color=FIELD, sw=1.8, head=8))
    f.append(varrow(ox + q, yO + 66, ox - q, yO + 66, color=FIELD, sw=1.8, head=8))
    f.append(text(ox, yO + 86, "2.5 %  …  97.5 %  =  інтервал охоплення", size=12, bold=True, color=FIELD))

    b2, w2, h2 = textbox(W / 2, H - 24,
                         "Похідних не рахуємо: уся форма входу → уся форма виходу; σ дає u_c, перцентилі — інтервал",
                         size=13, pad=9, fill="#fff6e9", stroke=MUTED, sw=1.3, bold=True)
    f.append(b2)
    return render(os.path.join(IMG, "mc-propagation.svg"), W, H, *f)


# ── Фігура: асиметричний вихід — симетричне ± промахується, перцентилі ні ──────
def fig_mc_skew():
    W, H = 960, 492
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Коли вихід асиметричний, симетричне ±U лінеаризації сидить криво",
                  size=16, bold=True))
    f.append(text(W / 2, 54, "Монте-Карло бере перцентилі й тримається форми; лінеаризація малює симетрію, якої нема",
                  size=12.5, color=MUTED))

    xL, xR, yB, yT = 120, 858, 316, 96
    X0, X1 = -0.45, 3.65

    def PX(x):
        return xL + (x - X0) / (X1 - X0) * (xR - xL)

    s = 0.55
    mean = math.exp(s * s / 2.0)
    std = mean * math.sqrt(math.exp(s * s) - 1.0)
    mode = math.exp(-s * s)
    z = 1.96
    q_lo, q_hi = math.exp(-z * s), math.exp(z * s)
    lin_lo, lin_hi = mean - z * std, mean + z * std

    def dens(x):
        if x <= 0:
            return 0.0
        return math.exp(-(math.log(x)) ** 2 / (2 * s * s)) / (x * s * math.sqrt(2 * math.pi))

    ymax = max(dens(x / 200.0) for x in range(1, 720))
    Hpx = yB - yT

    nb = 46
    for i in range(nb):
        x0 = 3.5 * i / nb
        x1 = 3.5 * (i + 1) / nb
        d = dens((x0 + x1) / 2.0)
        hh = d / ymax * Hpx
        if hh < 0.5:
            continue
        f.append(rect(PX(x0), yB - hh, PX(x1) - PX(x0) - 1.5, hh, fill="#fdecea", stroke=POS, sw=1.0, rx=0))

    f.append(varrow(xL - 6, yB, xR + 14, yB, color=INK, sw=1.8, head=10))
    for xv in (0, 1, 2, 3):
        f.append(tick(PX(xv), yB, h=6))
        f.append(text(PX(xv), yB + 20, str(xv), size=12, color=MUTED))

    # межа 0 — фізичний бар'єр
    f.append(line(PX(0), yT - 4, PX(0), yB, color=NEG, sw=1.6, dash="5 4"))
    f.append(text(PX(0), yT - 12, "0 — фізична межа (x<0 неможливо)", size=11.5, color=NEG))

    # мода й середнє
    f.append(line(PX(mode), yB, PX(mode), yB - dens(mode) / ymax * Hpx, color=FIELD, sw=1.6, dash="4 4"))
    f.append(text(PX(mode) - 6, yB - dens(mode) / ymax * Hpx - 8, "мода", size=12, color=FIELD, anchor="end"))
    f.append(line(PX(mean), yB, PX(mean), yT + 8, color=INK, sw=1.4))
    f.append(text(PX(mean) + 6, yT + 18, "середнє", size=12, color=INK, anchor="start"))

    # бракет лінеаризації (симетричний, синій)
    yl = yB + 44
    f.append(varrow(PX(lin_lo), yl, PX(lin_hi), yl, color=NEG, sw=2.4, head=9))
    f.append(varrow(PX(lin_hi), yl, PX(lin_lo), yl, color=NEG, sw=2.4, head=9))
    f.append(text((PX(lin_lo) + PX(lin_hi)) / 2, yl - 10, "лінеаризація:  середнє ± U  (симетрично)",
                  size=12, bold=True, color=NEG))
    f.append(text(PX(lin_lo), yl + 20, "%.2f" % lin_lo, size=11.5, color=NEG))
    f.append(text(PX(lin_hi), yl + 20, "%.2f" % lin_hi, size=11.5, color=NEG))

    # бракет Монте-Карло (перцентилі, зелений)
    ym = yB + 96
    f.append(varrow(PX(q_lo), ym, PX(q_hi), ym, color=FIELD, sw=2.6, head=10))
    f.append(varrow(PX(q_hi), ym, PX(q_lo), ym, color=FIELD, sw=2.6, head=10))
    f.append(text((PX(q_lo) + PX(q_hi)) / 2, ym - 10, "Монте-Карло:  перцентилі 2.5 – 97.5 %",
                  size=12, bold=True, color=FIELD))
    f.append(text(PX(q_lo), ym + 20, "%.2f" % q_lo, size=11.5, color=FIELD))
    f.append(text(PX(q_hi), ym + 20, "%.2f" % q_hi, size=11.5, color=FIELD))

    b, w, h = textbox(W / 2, H - 22,
                      "Симетричний інтервал вивалюється в неможливе (x<0) і зрізає правий хвіст; перцентилі тримаються форми",
                      size=12.5, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.3, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "mc-skew.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_distributions(), fig_quadrature(), fig_budget(),
          fig_linearize(), fig_correlation_cosine(), fig_gum_timeline(),
          fig_mc_propagation(), fig_mc_skew()]
    print("written:")
    for p in ps:
        print("  ", p)
