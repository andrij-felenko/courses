# -*- coding: utf-8 -*-
"""Фігури до теми «Течія Пуазейля».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WALL = "#3a4149"
FLUID = "#cfe8f5"
FLUIDD = "#8fc7e6"
SHADE = "#f6d3ce"
ORANGE = "#e08e0b"
GREEN = FIELD


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=SHADE, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


# ── Фігура 1: параболічний профіль швидкості в трубі ─────────────────────────
def fig_velocity_profile():
    W, H = 900, 470
    F = []
    xL, xR = 150, 770
    yTop, yBot = 128, 348           # внутрішні грані стінок
    yc = (yTop + yBot) / 2
    Rpx = (yBot - yTop) / 2
    xbase = 300                     # база профілю (де швидкість «починається»)
    Umax = 250                      # довжина стрілки в центрі

    def prof(r_frac):               # r_frac ∈ [-1,1]; парабола 1-r²
        return Umax * (1.0 - r_frac * r_frac)

    # градієнт тиску над трубою
    F.append(text(xL + 4, 74, "вищий тиск", size=13, color=POS, bold=True, anchor="start"))
    F.append(text(xR - 4, 74, "нижчий тиск", size=13, color=NEG, bold=True, anchor="end"))
    F.append(arrow(xL + 20, 92, xR - 20, 92, color=MUTED, sw=2.2))
    F.append(text((xL + xR) / 2, 112, "тиск жене рідину злива направо", size=12.5, color=MUTED))

    # стінки труби
    F.append(rect(xL, yTop - 20, xR - xL, 20, fill=WALL, stroke=INK, sw=1.4, rx=3))
    F.append(rect(xL, yBot, xR - xL, 20, fill=WALL, stroke=INK, sw=1.4, rx=3))
    # смуга рідини
    F.append(rect(xL, yTop, xR - xL, yBot - yTop, fill=FLUID, stroke=FLUIDD, sw=1.2))

    # заливка-профіль (площа = витрата) + обвідна парабола
    env = [(xbase, yTop)]
    for f in frange(-1.0, 1.0, 60):
        env.append((xbase + prof(f), yc + f * Rpx))
    env.append((xbase, yBot))
    F.append(polygon(env, fill=SHADE))
    F.append(polyline(env[1:-1], color=POS, sw=2.8))
    F.append(line(xbase, yTop, xbase, yBot, color=MUTED, sw=1.4))

    # стрілки швидкості
    for f in [-0.9, -0.72, -0.52, -0.3, 0.0, 0.3, 0.52, 0.72, 0.9]:
        y = yc + f * Rpx
        F.append(arrow(xbase, y, xbase + prof(f), y, color=NEG, sw=2.1))

    # мітки прилипання
    F.append(text(xbase + 8, yTop + 15, "u = 0  (прилипання)", size=11.5, color=INK, anchor="start"))
    F.append(text(xbase + 8, yBot - 7, "u = 0  (прилипання)", size=11.5, color=INK, anchor="start"))
    # мітка максимуму в центрі
    F.append(text(xbase + Umax + 14, yc + 4, "u_max у центрі", size=13, color=POS, bold=True, anchor="start"))

    # радіус R
    F.append(arrow(xL + 40, yc, xL + 40, yTop, color=INK, sw=1.6))
    F.append(arrow(xL + 40, yc, xL + 40, yBot, color=INK, sw=1.6))
    F.append(text(xL + 28, yc + 5, "R", size=16, color=INK, bold=True, italic=True, anchor="end"))
    F.append(line(xL + 55, yc, xbase - 10, yc, color=MUTED, sw=1.0, dash="6 6"))

    render(os.path.join(IMG, "velocity-profile.svg"), W, H, *F,
           title="Профіль швидкості в трубі — парабола: нуль на стінках, максимум у центрі")


# ── Фігура 2: баланс сил на циліндричному осерді ─────────────────────────────
def fig_force_balance():
    W, H = 900, 500
    F = []
    xL, xR = 190, 700
    yTop, yBot = 150, 330           # стінки труби
    yc = (yTop + yBot) / 2
    # осердя радіуса r (горизонтальна смуга завтовшки 2r у центрі)
    cr = 44
    yCoreT, yCoreB = yc - cr, yc + cr

    # стінки труби
    F.append(rect(xL, yTop - 16, xR - xL, 16, fill=WALL, stroke=INK, sw=1.3, rx=3))
    F.append(rect(xL, yBot, xR - xL, 16, fill=WALL, stroke=INK, sw=1.3, rx=3))
    # рідина
    F.append(rect(xL, yTop, xR - xL, yBot - yTop, fill=FLUID, stroke=FLUIDD, sw=1.1))
    # осердя
    F.append(rect(xL, yCoreT, xR - xL, 2 * cr, fill="#dff0d8", stroke=GREEN, sw=1.8, rx=3))
    F.append(text((xL + xR) / 2, yc + 5, "осердя радіуса r, довжина L", size=13, color="#2f7d32", bold=True))

    # тиск на торці — штовхає вперед
    F.append(text(xL - 12, yc - 34, "Δp", size=15, color=POS, bold=True, anchor="end"))
    for dy in (-22, 0, 22):
        F.append(arrow(xL - 42, yc + dy, xL - 6, yc + dy, color=POS, sw=2.6))
    F.append(text(xL - 24, yCoreB + 36, "сила тиску", size=11.5, color=POS, anchor="middle"))
    F.append(text(xL - 24, yCoreB + 54, "Δp · π r²", size=12.5, color=POS, bold=True, anchor="middle"))

    # в'язке тертя на бічних гранях осердя — тримає назад
    for x in [xL + 120, xL + 250, xL + 380]:
        F.append(arrow(x + 30, yCoreT, x - 30, yCoreT, color=NEG, sw=2.3))
        F.append(arrow(x + 30, yCoreB, x - 30, yCoreB, color=NEG, sw=2.3))
    F.append(text((xL + xR) / 2 + 40, yCoreT - 12, "в'язке тертя  τ · 2π r L  (тримає назад)",
                  size=12, color=NEG, bold=True))

    # права стрілка — напрям руху
    F.append(arrow(xR + 6, yc, xR + 44, yc, color=MUTED, sw=2.4))
    F.append(text(xR + 50, yc + 4, "рух", size=12, color=MUTED, anchor="start"))

    # блок рівноваги
    F.append(fitbox(20, 388, 860, 88,
                    "рівновага (течія стала, без прискорення):   Δp · π r²  =  τ · 2π r L\n"
                    "⇒   τ = (Δp / 2L) · r      — зсув росте ЛІНІЙНО від центра до стінки\n"
                    "а τ = μ · (швидкість зміни u) ⇒ інтегруємо ⇒ u(r) — ПАРАБОЛА",
                    size=13.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=11))

    render(os.path.join(IMG, "force-balance.svg"), W, H, *F,
           title="Баланс сил на осерді: штовхання тиску проти в'язкого тертя")


# ── Фігура 3: закон четвертого степеня Q ∝ R⁴ ────────────────────────────────
def fig_r4_law():
    W, H = 880, 540
    F = []
    x0, x1 = 130, 740
    yt, yb = 92, 430
    rmax = 1.5
    qmax = rmax ** 4                # ~5.06

    def X(r):
        return x0 + r / rmax * (x1 - x0)

    def Y(q):
        return yb - q / qmax * (yb - yt)

    # осі: мітки
    for r in [0, 0.5, 0.8, 1.0, 1.25, 1.5]:
        F.append(line(X(r), yb, X(r), yb + 6, color=MUTED, sw=1.1))
        F.append(text(X(r), yb + 24, ("%g" % r), size=12, color=MUTED))
    for q in [0, 1, 2, 3, 4, 5]:
        F.append(line(x0 - 6, Y(q), x0, Y(q), color=MUTED, sw=1.1))
        F.append(text(x0 - 12, Y(q) + 4, ("%g" % q), size=12, color=MUTED, anchor="end"))

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 52, "відносний радіус  R / R₀  →", size=14, color=INK))
    F.append(text(x0 - 6, yt - 16, "відносна витрата  Q / Q₀", size=12.5, color=MUTED, anchor="start"))

    # крива Q = (R/R0)^4
    pts = [(X(r), Y(r ** 4)) for r in frange(0.0, rmax, 200)]
    F.append(polyline(pts, color=GREEN, sw=3.4))

    # опорна лінія Q = 1 при R/R0 = 1
    F.append(line(x0, Y(1.0), X(1.0), Y(1.0), color=MUTED, sw=1.0, dash="5 5"))
    F.append(line(X(1.0), yb, X(1.0), Y(1.0), color=MUTED, sw=1.0, dash="5 5"))

    # точки на кривій
    F.append(circle(X(1.0), Y(1.0), 5.5, fill=GREEN, stroke=INK, sw=1.5))
    F.append(circle(X(0.5), Y(0.5 ** 4), 5.5, fill=POS, stroke=INK, sw=1.5))
    F.append(circle(X(0.8), Y(0.8 ** 4), 5.5, fill=ORANGE, stroke=INK, sw=1.5))

    # анотація у верхньому лівому просторі (там крива лежить низько — порожньо)
    F.append(fitbox(x0 + 20, yt + 4, 296, 64,
                    "Q ∝ R⁴\nодне R² — від площі перерізу,\nще R² — бо ширша труба жене рідину швидше",
                    size=12.5, bold=True, fill="#eafaf0", stroke=GREEN, pad=9))

    # виноски до точок — над кожною точкою, у порожню смугу, вертикальні лідери
    # (крива тут лежить низько, тож написи стоять високо й не торкаються її)
    # ½ радіус
    F.append(line(X(0.5), Y(0.5 ** 4) - 6, X(0.5), 250, color=POS, sw=1.2, dash="4 4"))
    F.append(text(X(0.5), 240, "½ радіус  →  Q = 1/16", size=12.5, color=POS, bold=True))
    # −20% радіус
    F.append(line(X(0.8), Y(0.8 ** 4) - 6, X(0.8), 302, color=ORANGE, sw=1.2, dash="4 4"))
    F.append(text(X(0.8), 292, "−20%  →  Q ≈ 0.41", size=12.5, color=ORANGE, bold=True))
    # вихідна труба
    F.append(line(X(1.0), Y(1.0) - 6, X(1.0), 328, color="#2f7d32", sw=1.2, dash="4 4"))
    F.append(text(X(1.0), 318, "вихідна  Q₀", size=12, color="#2f7d32", bold=True))

    render(os.path.join(IMG, "r4-law.svg"), W, H, *F,
           title="Закон четвертого степеня: витрата шалено чутлива до радіуса")


# ── Фігура 4: гідравлічний опір ↔ закон Ома ──────────────────────────────────
def fig_hydraulic_analogy():
    W, H = 940, 500
    F = []

    # ── ліва панель: труба ──
    F.append(text(240, 66, "рідина в трубі", size=15, bold=True))
    yp = 150
    xpL, xpR = 96, 400
    # труба
    F.append(rect(xpL, yp, xpR - xpL, 46, fill=FLUID, stroke=FLUIDD, sw=1.4, rx=4))
    F.append(rect(xpL, yp - 6, xpR - xpL, 6, fill=WALL, stroke="none", sw=0, rx=2))
    F.append(rect(xpL, yp + 46, xpR - xpL, 6, fill=WALL, stroke="none", sw=0, rx=2))
    # тиск обабіч
    F.append(text(xpL - 6, yp + 28, "p₁", size=14, color=POS, bold=True, anchor="end"))
    F.append(text(xpR + 8, yp + 28, "p₂", size=14, color=NEG, bold=True, anchor="start"))
    # потік
    F.append(arrow(xpL + 40, yp + 23, xpR - 40, yp + 23, color=INK, sw=2.6))
    F.append(text((xpL + xpR) / 2, yp + 18, "Q", size=15, color=INK, bold=True, italic=True))
    # опис опору
    F.append(textbox(240, yp + 100, "R_гідр = 8 μ L / (π R⁴)", size=13.5, bold=True,
                     fill="#fdf2ef", stroke=POS)[0])
    F.append(textbox(240, yp + 150, "Q = Δp / R_гідр", size=15, bold=True,
                     fill="#eafaf0", stroke=GREEN)[0])

    # ── права панель: коло ──
    F.append(text(700, 66, "струм у колі", size=15, bold=True))
    # батарея
    bx = 620
    by0, by1 = 150, 300
    F.append(line(bx, by0, bx, by1, color=INK, sw=2.2))
    # довга/коротка риски батареї
    F.append(line(bx - 16, by1, bx + 16, by1, color=INK, sw=3.4))
    F.append(line(bx - 9, by1 + 10, bx + 9, by1 + 10, color=INK, sw=1.8))
    F.append(text(bx - 24, (by0 + by1) / 2, "U", size=15, color=NEG, bold=True, italic=True, anchor="end"))
    # провід верх
    F.append(line(bx, by0, 790, by0, color=INK, sw=2.2))
    # резистор (зигзаг)
    rx0, rx1 = 790, 790
    ry0, ry1 = by0, by0 + 90
    zz = [(790, by0)]
    for i in range(6):
        zz.append((790 + (18 if i % 2 == 0 else -18), by0 + 12 + i * 12))
    zz.append((790, by0 + 90))
    F.append(polyline(zz, color=INK, sw=2.4))
    F.append(text(824, by0 + 46, "R", size=15, color=POS, bold=True, italic=True, anchor="start"))
    # провід низ
    F.append(line(790, by0 + 90, 790, by1 + 10, color=INK, sw=2.2))
    F.append(line(bx, by1 + 10, 790, by1 + 10, color=INK, sw=2.2))
    # струм
    F.append(arrow(686, by0, 742, by0, color=INK, sw=2.4))
    F.append(text(714, by0 - 10, "I", size=15, color=INK, bold=True, italic=True))
    F.append(textbox(700, 372, "I = U / R", size=15, bold=True,
                     fill="#eaf0fd", stroke=NEG)[0])

    # ── таблиця відповідності знизу ──
    F.append(fitbox(96, 430, 748, 54,
                    "різниця тисків Δp ↔ напруга U      витрата Q ↔ струм I      "
                    "гідравлічний опір R_гідр ↔ електричний опір R",
                    size=13, bold=True, fill="#f4f6f8", stroke=LINE, pad=9))

    render(os.path.join(IMG, "hydraulic-analogy.svg"), W, H, *F,
           title="Труба — резистор для рідини: закон Пуазейля повторює закон Ома")


# ── Фігура 5: історична доріжка — дослід випередив теорію ────────────────────
def fig_history_timeline():
    W, H = 1060, 560
    F = []
    axis_y = 300
    x0, x1 = 70, 1000

    BLUEF, GREENF, ORANGEF = "#eaf0fd", "#eafaf0", "#fdf3e6"

    # часова вісь
    F.append(arrow(x0, axis_y, x1 + 6, axis_y, color=INK, sw=2.2))
    F.append(text(x1 + 34, axis_y + 5, "час", size=13, color=MUTED))

    def ev(x, ytext, lines, color, fill):
        F.append(line(x, axis_y, x, ytext, color=color, sw=1.4, dash="3 4"))
        F.append(circle(x, axis_y, 6, fill=color, stroke=INK, sw=1.5))
        F.append(textbox(x, ytext, lines, size=12.5, bold=True,
                         fill=fill, stroke=color, pad=8)[0])

    # заголовки доріжок
    F.append(text(x0 + 2, 70, "ДОСЛІД · ВИМІР", size=13, color=NEG, bold=True, anchor="start"))
    F.append(text(x0 + 2, 532, "ТЕОРІЯ · НАЗВА · ОДИНИЦЯ", size=13, color=FIELD, bold=True, anchor="start"))

    # ── дослід (над віссю) ──
    ev(120, 150, "1828\nПуазейль:\nманометр, мм рт.ст.", NEG, BLUEF)
    ev(250, 222, "1838\nПуазейль:\nпочаток дослідів", NEG, BLUEF)
    ev(360, 150, "1839\nГаген:\nлатунні труби, друк", NEG, BLUEF)
    ev(475, 222, "1840–41\nПуазейль:\nзаписки в Академію", NEG, BLUEF)
    ev(610, 150, "1846\nПуазейль:\nвелика праця", NEG, BLUEF)

    # ── теорія · назва · одиниця (під віссю) ──
    ev(545, 388, "1845\nСтокс:\nрівняння руху", FIELD, GREENF)
    ev(700, 388, "1856\nВідеман:\nвиведення", FIELD, GREENF)
    ev(820, 462, "1860\nНейман і Гагенбах:\nчисте виведення +\nназва «закон Пуазейля»", FIELD, GREENF)
    ev(955, 388, "≈1900\nодиниця «пуаз» (P)", ORANGE, ORANGEF)

    # ── виноска про розрив: емпірика ↔ теорія (порожній нижній-лівий кут) ──
    F.append(textbox(255, 452,
                     "Емпірика випередила теорію\n"
                     "≈ 20 років закон ЗНАЛИ як факт (Q ∝ R⁴) —\n"
                     "доки Стокс, Нейман і Гагенбах пояснили,\n"
                     "ЧОМУ: в'язкість μ і прилипання до стінок",
                     size=12, fill=FILL, stroke=MUTED, pad=10)[0])

    render(os.path.join(IMG, "history-timeline.svg"), W, H, *F,
           title="Дві доріжки до одного закону: дослід випередив теорію")


# ── Фігура 6: розв'язана мережа труб — тиски у вузлах і розподіл витрат ───────
def fig_pipe_network():
    W, H = 940, 610
    F = []
    A = (150, 300); B = (470, 150); C = (470, 450); D = (790, 300)

    def edge(p1, p2, Q, label, lx, ly):
        x1, y1 = p1; x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        Ln = math.hypot(dx, dy)
        ux, uy = dx / Ln, dy / Ln
        ax1, ay1 = x1 + ux * 30, y1 + uy * 30
        ax2, ay2 = x2 - ux * 30, y2 - uy * 30
        F.append(line(ax1, ay1, ax2, ay2, color=FLUIDD, sw=11))   # обичайка труби
        F.append(line(ax1, ay1, ax2, ay2, color=FLUID, sw=7))
        F.append(arrow(ax1, ay1, ax2, ay2, color=NEG, sw=1.6 + Q * 3.4))  # струмінь ∝ Q
        F.append(text(lx, ly, label, size=12.5, color=NEG, bold=True))

    # труби (Q у ×10⁻⁶ м³/с) — товщина стрілки ∝ витраті
    edge(A, B, 1.27, "Q ≈ 1.27", 250, 196)
    edge(A, C, 1.09, "Q ≈ 1.09", 250, 408)
    edge(B, D, 1.09, "Q ≈ 1.09", 692, 196)
    edge(C, D, 1.27, "Q ≈ 1.27", 692, 408)
    edge(B, C, 0.18, "Q ≈ 0.18", 556, 296)
    F.append(text(556, 314, "місток", size=11.5, color=MUTED, bold=True))

    # вузли
    def node(pt, letter, ring):
        x, y = pt
        F.append(circle(x, y, 27, fill="#eef3f7", stroke=ring, sw=2.6))
        F.append(text(x, y + 7, letter, size=22, color=INK, bold=True))

    node(A, "A", POS); node(D, "D", NEG); node(B, "B", INK); node(C, "C", INK)

    # мітки тиску у вузлах
    F.append(textbox(150, 244, "джерело\np = 1000 Па", size=12.5, bold=True,
                     fill="#fdecea", stroke=POS)[0])
    F.append(textbox(790, 244, "стік\np = 0", size=12.5, bold=True,
                     fill="#eaf0fd", stroke=NEG)[0])
    F.append(textbox(470, 96, "p ≈ 677 Па", size=12.5, bold=True,
                     fill=FILL, stroke=MUTED)[0])
    F.append(textbox(470, 504, "p ≈ 323 Па", size=12.5, bold=True,
                     fill=FILL, stroke=MUTED)[0])

    # смуга аналогії знизу
    F.append(fitbox(150, 548, 640, 46,
                    "труба ↔ резистор      Δp ↔ напруга U      "
                    "Q ↔ струм I      R_гідр = 8μL/(πR⁴) ↔ опір R",
                    size=13, bold=True, fill="#f4f6f8", stroke=LINE, pad=9))

    render(os.path.join(IMG, "pipe-network.svg"), W, H, *F,
           title="Розв'язана мережа-місток: тиски у вузлах і розподіл витрат")


# ── Фігура (вставка math): зсув → швидкість, серце інтегрування ───────────────
def fig_shear_to_velocity():
    W, H = 940, 470
    F = []
    base = 392
    top_val = 150
    amp = base - top_val - 18                # ~224
    Lx0, Lxc, Lx1 = 96, 246, 396
    Rx0, Rxc, Rx1 = 560, 710, 860

    def panel(x0, xc, x1, ttl):
        f = []
        f.append(line(x0 - 10, base, x1 + 10, base, color=INK, sw=1.8))
        f.append(line(xc, base, xc, top_val, color=MUTED, sw=1.0, dash="5 5"))
        f.append(text((x0 + x1) / 2, top_val - 22, ttl, size=15, bold=True))
        f.append(text(x0, base + 20, "стінка", size=11, color=MUTED))
        f.append(text(x1, base + 20, "стінка", size=11, color=MUTED))
        f.append(text(xc, base + 20, "вісь (r = 0)", size=11, color=MUTED))
        return f

    # ліва панель: |τ| — «галочка» (0 у центрі, максимум на стінках)
    F += panel(Lx0, Lxc, Lx1, "зсувне напруження τ(r)")
    F.append(polyline([(Lx0, base - amp), (Lxc, base), (Lx1, base - amp)], color=POS, sw=3.4))
    F.append(text(Lx0, base - amp - 8, "τ_w", size=12.5, color=POS, bold=True))
    F.append(text(Lx1, base - amp - 8, "τ_w", size=12.5, color=POS, bold=True))
    F.append(text(Lxc, base - 10, "0", size=11.5, color=MUTED))
    F.append(text(Lxc, base + 44, "τ = (Δp/2L)·r  — лінійне", size=12.5, color=POS, bold=True))

    # права панель: u — парабола (максимум у центрі, 0 на стінках)
    F += panel(Rx0, Rxc, Rx1, "швидкість u(r)")
    par = [(Rxc + ff * (Rx1 - Rxc), base - amp * (1 - ff * ff)) for ff in frange(-1.0, 1.0, 45)]
    F.append(polyline(par, color="#1f7a33", sw=3.4))
    F.append(text(Rxc, base - amp - 8, "u_max", size=12.5, color="#1f7a33", bold=True))
    F.append(text(Rxc, base + 44, "u = (Δp/4μL)(R²−r²)  — парабола", size=12.5, color="#1f7a33", bold=True))

    # місток інтегрування
    F.append(arrow(Lx1 + 16, 206, Rx0 - 16, 206, color=INK, sw=2.4))
    tb = textbox((Lx1 + Rx0) / 2, 268, "τ = −μ·du/dr\n⇓  інтегруємо\nз умовою u(R) = 0",
                 size=12, bold=True, fill="#eef3ee", stroke=GREEN, pad=8)
    F.append(tb[0])

    render(os.path.join(IMG, "shear-to-velocity.svg"), W, H, *F,
           title="Лінійний зсув інтегрується у параболу швидкості")


# ── Фігура (вставка math): розвиток профілю на вході в трубу ──────────────────
def fig_entrance_length():
    W, H = 990, 470
    F = []
    xin, xout = 120, 910
    yTop, yBot = 150, 330
    yc = (yTop + yBot) / 2
    halfg = (yBot - yTop) / 2
    xmerge = 600

    # стінки й рідина
    F.append(rect(xin, yTop - 16, xout - xin, 16, fill=WALL, stroke=INK, sw=1.2, rx=3))
    F.append(rect(xin, yBot, xout - xin, 16, fill=WALL, stroke=INK, sw=1.2, rx=3))
    F.append(rect(xin, yTop, xout - xin, yBot - yTop, fill=FLUID, stroke=FLUIDD, sw=1.0))

    # незбурене ядро (світле) + межові шари (тінь)
    F.append(polygon([(xin, yTop), (xin, yBot), (xmerge, yc)], fill="#eaf6fc"))
    F.append(polygon([(xin, yTop), (xmerge, yTop), (xmerge, yc)], fill=SHADE))
    F.append(polygon([(xin, yBot), (xmerge, yBot), (xmerge, yc)], fill=SHADE))
    F.append(line(xin, yTop, xmerge, yc, color=ORANGE, sw=2.0))
    F.append(line(xin, yBot, xmerge, yc, color=ORANGE, sw=2.0))
    F.append(text((xin + xmerge) / 2 + 40, yTop + 20, "межові шари ростуть", size=11.5,
                  color="#a85a06", bold=True, anchor="middle"))
    F.append(text(xin + 66, yc + 4, "ядро ще пласке", size=11, color=NEG))

    # профілі на станціях
    def profile(xs, shape, maxlen, color):
        f = []
        for ff in [-0.85, -0.6, -0.35, -0.12, 0.12, 0.35, 0.6, 0.85, 0.0]:
            y = yc + ff * halfg
            ln = maxlen * shape(ff)
            if ln > 3:
                f.append(arrow(xs, y, xs + ln, y, color=color, sw=1.7))
        f.append(line(xs, yTop, xs, yBot, color=color, sw=1.0, dash="3 3"))
        return f

    flat = lambda f: 1.0
    para = lambda f: (1.0 - f * f)

    def developing(f):
        a = 0.5
        return 1.0 if abs(f) < a else max(0.0, (1 - abs(f)) / (1 - a))

    F += profile(xin + 14, flat, 44, NEG)
    F += profile(310, developing, 60, NEG)
    F += profile(xmerge + 44, para, 64, NEG)
    F += profile(792, para, 70, NEG)

    F.append(text(xin + 30, yTop - 26, "плаский", size=11, color=NEG, anchor="middle"))
    F.append(text(310, yTop - 26, "розвивається", size=11, color=NEG))
    F.append(text(792, yTop - 26, "парабола", size=11, color=NEG))

    # розмірна лінія L_e
    ydim = yBot + 44
    F.append(line(xin, yBot + 22, xin, ydim + 6, color=INK, sw=1.0))
    F.append(line(xmerge, yBot + 22, xmerge, ydim + 6, color=INK, sw=1.0))
    F.append(arrow(xin, ydim, xmerge, ydim, color=INK, sw=1.5))
    F.append(arrow(xmerge, ydim, xin, ydim, color=INK, sw=1.5))
    F.append(text((xin + xmerge) / 2, ydim - 8, "вхідна довжина  L_e ≈ 0.06·Re·D", size=13, bold=True))
    F.append(text((xmerge + xout) / 2, ydim - 8, "розвинена течія — закон Пуазейля",
                  size=12.5, color="#1f7a33", bold=True))

    render(os.path.join(IMG, "entrance-length.svg"), W, H, *F,
           title="Розвиток профілю на вході: від плаского до параболи")


# ── Фігура (вставка math): коефіцієнт тертя f = 64/Re і перехід ───────────────
def fig_friction_factor():
    W, H = 900, 560
    F = []
    x0, x1 = 132, 830
    yt, yb = 96, 470
    lreMin, lreMax = 2.0, 5.0
    lfMin, lfMax = math.log10(8e-3), 0.0

    def X(re):
        return x0 + (math.log10(re) - lreMin) / (lreMax - lreMin) * (x1 - x0)

    def Y(f):
        return yb - (math.log10(f) - lfMin) / (lfMax - lfMin) * (yb - yt)

    labE = ("10²", "10³", "10⁴", "10⁵")
    for e in (2, 3, 4, 5):
        xx = X(10 ** e)
        F.append(line(xx, yt, xx, yb, color="#e3e6ea", sw=1.0))
        F.append(text(xx, yb + 22, labE[e - 2], size=12, color=MUTED))
    for fv in (0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0):
        yy = Y(fv)
        F.append(line(x0, yy, x1, yy, color="#eef0f3", sw=1.0))
        F.append(text(x0 - 10, yy + 4, ("%g" % fv), size=11, color=MUTED, anchor="end"))

    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 48, "число Рейнольдса  Re →", size=14))
    F.append(text(x0 - 4, yt - 14, "f — коефіцієнт тертя Дарсі", size=12.5, color=MUTED, anchor="start"))

    # смуга переходу
    xa, xbnd = X(2300), X(4000)
    F.append(rect(xa, yt, xbnd - xa, yb - yt, fill="#f4ecdc", stroke="none", sw=0, rx=0))
    F.append(text((xa + xbnd) / 2, yt + 16, "перехід", size=11, color="#9a6b1a"))
    F.append(text((xa + xbnd) / 2, yt + 32, "Re≈2300", size=11, color="#9a6b1a"))

    # ламінарна пряма f = 64/Re
    lam = [(X(re), Y(64.0 / re)) for re in frange(100, 2300, 50)]
    F.append(polyline(lam, color=FIELD, sw=3.8))
    # турбулентна (гладка): Блазіус 0.316·Re^−¼
    tb = [(X(re), Y(0.316 * re ** -0.25)) for re in (4000, 6000, 1e4, 2e4, 4e4, 7e4, 1e5)]
    F.append(polyline(tb, color=NEG, sw=2.6))
    # родина шорстких труб (майже горизонтальні)
    for fr in (0.043, 0.030):
        F.append(line(X(4000), Y(fr), X(1e5), Y(fr), color=MUTED, sw=1.6, dash="6 4"))

    F.append(text(X(300), Y(0.42), "f = 64/Re", size=15, color=FIELD, bold=True))
    F.append(text(X(300), Y(0.30), "ламінарна — закон Пуазейля", size=12, color=FIELD, bold=True))
    F.append(text(X(2.6e4), Y(0.052), "турбулентна, гладка (Блазіус)", size=11.5, color=NEG))
    F.append(text(X(5.5e4), Y(0.061), "шорсткі труби", size=11, color=MUTED))

    render(os.path.join(IMG, "friction-factor.svg"), W, H, *F,
           title="Коефіцієнт тертя: ламінарна пряма f = 64/Re, далі перехід і турбулентність")


# ── Фігура (вставка math): неколовий переріз і гідравлічний діаметр ───────────
def fig_cross_sections():
    W, H = 1000, 430
    F = []
    cx = [120, 306, 496, 692, 882]
    ys = 148
    F.append(text(W / 2, 58, "гідравлічний діаметр  D_h = 4A / P     ·     f = C / Re",
                  size=15, bold=True))

    F.append(circle(cx[0], ys, 44, fill=FLUID, stroke=FLUIDD, sw=2))
    F.append(rect(cx[1] - 44, ys - 44, 88, 88, fill=FLUID, stroke=FLUIDD, sw=2, rx=2))
    F.append(rect(cx[2] - 58, ys - 29, 116, 58, fill=FLUID, stroke=FLUIDD, sw=2, rx=2))
    F.append(rect(cx[3] - 58, ys - 40, 116, 12, fill=WALL, stroke=INK, sw=1, rx=2))
    F.append(rect(cx[3] - 58, ys + 28, 116, 12, fill=WALL, stroke=INK, sw=1, rx=2))
    F.append(rect(cx[3] - 58, ys - 28, 116, 56, fill=FLUID, stroke=FLUIDD, sw=1))
    F.append(arrow(cx[3], ys - 26, cx[3], ys + 26, color=INK, sw=1.4))
    F.append(arrow(cx[3], ys + 26, cx[3], ys - 26, color=INK, sw=1.4))
    F.append(circle(cx[4], ys, 44, fill=FLUID, stroke=FLUIDD, sw=2))
    F.append(circle(cx[4], ys, 18, fill=BG, stroke=WALL, sw=2))

    names = ["коло", "квадрат", "прямокутник 2:1", "пластини (∞)", "кільце"]
    dh = ["D_h = 2R", "D_h = a", "D_h = 4b/3", "D_h = 2·зазор", "D_h = 2(R−r_i)"]
    cc = ["C = 64", "C ≈ 56.9", "C ≈ 62.2", "C = 96", "C: 64 → 96"]
    exact = [True, False, False, True, True]
    for i, x in enumerate(cx):
        F.append(text(x, 232, names[i], size=12.5, bold=True))
        F.append(text(x, 254, dh[i], size=11.5, color=MUTED))
        F.append(text(x, 278, cc[i], size=13, color=(FIELD if exact[i] else POS), bold=True))

    F.append(fitbox(96, 322, 808, 62,
                    "коло і пластини — точні; квадрат/прямокутник — числові (Шах–Лондон); кільце — точна формула витрати.\n"
                    "наївне C = 64 з D_h завищує Δp для квадрата на ~12 %, бо насправді C ≈ 56.9.",
                    size=12.5, fill=FILL, stroke=LINE, pad=9))

    render(os.path.join(IMG, "cross-sections.svg"), W, H, *F,
           title="Неколовий переріз: D_h вирівнює масштаб, але стала C залежить від форми")


if __name__ == "__main__":
    fig_velocity_profile()
    fig_force_balance()
    fig_r4_law()
    fig_hydraulic_analogy()
    fig_history_timeline()
    fig_pipe_network()
    fig_shear_to_velocity()
    fig_entrance_length()
    fig_friction_factor()
    fig_cross_sections()
    print("OK: 6 SVG ->", IMG)
