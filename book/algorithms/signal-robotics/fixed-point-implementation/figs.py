# -*- coding: utf-8 -*-
"""Фігури до теми «Реалізація fixed-point».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

import math

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── float-fixed: чому ціла арифметика ─────────────────────────────────────────
# Ідея: на чипі без FPU одна операція з комою емулюється довгою підпрограмою
# (десятки тактів), а ціла виконується нативно за такт-два. Два стовпчики
# наочно показують прірву у вартості.

def fig_float_fixed():
    W, H = 720, 250
    p = []
    base = 200                       # лінія, від якої ростуть стовпчики
    # float — високий стовпчик (дорого)
    p.append(rect(150, 50, 120, base - 50, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(210, 42, "~60 тактів", size=10, color=INK, bold=True))
    p.append(text(210, base + 18, "float (емуляція)", size=10.5, color=POS, bold=True))
    # ціле — майже пласка смужка (дешево)
    p.append(rect(450, base - 5, 120, 5, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=2))
    p.append(text(510, base - 12, "~2 такти", size=10, color=INK, bold=True))
    p.append(text(510, base + 18, "ціле (нативно)", size=10.5, color=FIELD, bold=True))

    p.append(text(W / 2, 234,
                  "на чипі без апаратного float кожна операція з комою емулюється — дорого",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "float-fixed.svg"), W, H, *p,
           title="Без FPU ціла арифметика в десятки разів швидша за float")


# ── qformat: дріб як масштабоване ціле ────────────────────────────────────────
# Ідея: дріб множать на 2¹⁵ і зберігають як ціле; при множенні двох Q15 масштаб
# подвоюється (Q30), тож результат зсувають праворуч на 15 назад у Q15.

def fig_qformat():
    W, H = 740, 240
    p = []
    # дріб → ціле
    p.append(rect(40, 70, 150, 50, fill="#eef3fb", stroke=NEG, sw=1.6, rx=8))
    p.append(text(115, 100, "0.5  (дріб)", size=12, color=NEG, bold=True))
    p.append(arrow(192, 95, 250, 95, color=INK, sw=1.8))
    p.append(text(221, 86, "×32768", size=9, color=MUTED, italic=True))
    p.append(rect(254, 70, 170, 50, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(339, 100, "16384  (Q15 ціле)", size=11, color=FIELD, bold=True))
    p.append(text(560, 92, "кома «зашита»", size=9, color=MUTED, italic=True))
    p.append(text(560, 106, "в масштабі 2¹⁵", size=9, color=MUTED, italic=True))

    # множення зі зсувом
    p.append(text(60, 162, "множення:", size=11, color=INK, anchor="start", bold=True))
    p.append(text(60, 188, "Q15 × Q15  →  Q30   (добуток у ширшому регістрі)",
                  size=11.5, color=INK, anchor="start"))
    p.append(text(60, 214, "Q30  >> 15  →  Q15   (зсув коми назад у масштаб)",
                  size=11.5, color=INK, anchor="start"))
    render(os.path.join(IMG, "qformat.svg"), W, H, *p,
           title="Формат Q15: дроби як масштабовані цілі")


# ── accumulator: акумулятор ширший за відліки ─────────────────────────────────
# Ідея: відлік 16 біт × коеф. 16 біт = добуток 32 біт; сума багатьох добутків
# потребує ще більше — тож суму коплять у широкому (64-біт) акумуляторі.

def fig_accumulator():
    W, H = 720, 240
    p = []
    bx, bw = 60, 256                 # повна ширина «шкали бітів»
    rows = [
        ("відлік 16 біт", 64, NEG),
        ("× коеф. 16 біт", 64, FIELD),
        ("= добуток 32 біт", 128, "#caa24a"),
        ("Σ акумулятор 64 біт (із запасом)", 256, "#9a4ea8"),
    ]
    y = 66
    for lab, fillw, col in rows:
        p.append(rect(bx, y, bw, 26, fill=BG, stroke=INK, sw=1.0, rx=3))
        p.append(rect(bx, y, fillw, 26, fill=col, stroke="none", sw=0, rx=0))
        p.append(text(bx + bw + 8, y + 18, lab, size=10, color=INK, anchor="start", bold=True))
        y += 34

    p.append(text(bx, 212, "вузький акумулятор переповнюється на сумі — бери 32/64-бітний",
                  size=9.5, color=MUTED, anchor="start", italic=True))
    render(os.path.join(IMG, "accumulator.svg"), W, H, *p,
           title="Акумулятор має бути ширший за відліки")


# ── overflow-sat: загортання проти насичення ─────────────────────────────────
# Ідея: коли значення лізе за межу, наївне загортання перекидає його з +макс на
# −макс (дикий стрибок); насичення впирається в межу й лишається там.

def fig_overflow_sat():
    W, H = 720, 260
    p = []
    x0, x1 = 70, 650
    ymid, ytop, ybot = 140, 80, 200          # 0, +макс, −макс

    p.append(line(x0, ymid, x1, ymid, color="#e4e4e4", sw=1.0))
    p.append(line(x0, ytop, x1, ytop, color="#e4e4e4", sw=1.0, dash="4 3"))
    p.append(text(x0 - 4, ytop, "+макс", size=9, color=MUTED, anchor="end"))
    p.append(line(x0, ybot, x1, ybot, color="#e4e4e4", sw=1.0, dash="4 3"))
    p.append(text(x0 - 4, ybot + 4, "−макс", size=9, color=MUTED, anchor="end"))

    N = 301
    # «справжній» сигнал лінійно повзе вгору, двічі перетинаючи +макс
    def ideal(i):
        t = i / (N - 1)
        return ytop - (t - 0.5) * 260        # px; вище ytop = за межею

    wrap_pts, sat_pts = [], []
    for i in range(N):
        x = x0 + (x1 - x0) * i / (N - 1)
        v = ideal(i)
        # насичення: затиск у смугу [ytop..ybot]
        sv = max(ytop, min(ybot, v))
        sat_pts.append((x, sv))
        # загортання: за +макс перекидає на −макс і знову повзе вгору
        span = ybot - ytop
        wv = v
        while wv < ytop:
            wv += span
        while wv > ybot:
            wv -= span
        wrap_pts.append((x, wv))

    def poly(pts, color, sw, dash=None):
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        s = " ".join("%.1f,%.1f" % q for q in pts)
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round" stroke-linecap="round"%s/>' % (s, color, sw, d))

    p.append(poly(wrap_pts, POS, 2.0))
    p.append(poly(sat_pts, FIELD, 2.6))

    p.append(text(x1 - 220, 48, "загортання (wrap): дикий стрибок",
                  size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(x0 + 30, 235, "насичення (sat): впирається в межу",
                  size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(W / 2, 250, "ніколи не давай сумі тихо «загорнутися» — затискай (saturate) на межі",
                  size=9.5, color=MUTED, italic=True))
    render(os.path.join(IMG, "overflow-sat.svg"), W, H, *p,
           title="Переповнення: згубне загортання vs безпечне насичення")


# ── coef-quant: квантування коефіцієнтів зсуває характеристику ───────────────
# Ідея: ідеальна АЧХ і та сама після грубого округлення коефіцієнтів — затримання
# спливає вгору, перехід пливе.

def fig_coef_quant():
    W, H = 720, 270
    p = []
    ox, oy = 70, 220
    top = 60
    p.append(arrow(ox, oy, ox, top - 12, color=INK, sw=1.6))
    p.append(arrow(ox, oy, 660, oy, color=INK, sw=1.6))
    p.append(text(652, oy + 16, "частота →", size=9, color=INK, bold=True))

    span = 580.0
    def fr(i, n):
        return i / (n - 1)

    # ідеальна: низькочастотна полиця → плавний спад у глибоке затримання
    def ideal(t):
        # т у [0..1]; повертає висоту над віссю (px)
        cut = 0.42
        if t < cut:
            return top + (oy - top) * 0.0           # пропускання ≈ верх
        # спад до дна, далі дрібні брижі біля дна
        d = (t - cut) / (1 - cut)
        floor = oy - 4
        depth = (oy - top) * (1 - math.exp(-3.4 * d))
        ripple = 4 * math.exp(-2.0 * d) * math.cos(11 * d)
        return top + depth + ripple - 0 if False else min(floor, top + depth - ripple)

    # квантована: затримання гірше (полиця «спливла» вгору від дна), перехід пливе
    def quant(t):
        base = ideal(t)
        cut = 0.42
        if t < cut:
            return base
        d = (t - cut) / (1 - cut)
        lift = (oy - top) * 0.18 * (1 - math.exp(-2.2 * d))   # дно вище
        return base - lift

    n = 301
    def curve(fn, color, sw, dash=None):
        pts = []
        for i in range(n):
            t = fr(i, n)
            x = ox + span * t
            pts.append("%.1f,%.1f" % (x, fn(t)))
        d = ' stroke-dasharray="%s"' % dash if dash else ''
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round" stroke-linecap="round"%s/>' % (" ".join(pts), color, sw, d))

    p.append(curve(ideal, FIELD, 2.4))
    p.append(curve(quant, POS, 2.0, dash="5 3"))

    p.append(text(360, 108, "ідеальні коеф.", size=9.5, color=FIELD, anchor="start", bold=True))
    p.append(text(330, 168, "грубо квантовані", size=9.5, color=POS, anchor="start", bold=True))
    p.append(text(W / 2, 256,
                  "округлення коеф. псує характеристику; для БІХ може й дестабілізувати",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "coef-quant.svg"), W, H, *p,
           title="Квантування коефіцієнтів трохи зсуває характеристику")


# ── budget: бюджет реального часу ─────────────────────────────────────────────
# Ідея: смуга періоду T = 1/fs; фільтр займає лише частину, решта — запас.

def fig_budget():
    W, H = 720, 220
    p = []
    bx, by, bw, bh = 70, 110, 560, 40
    p.append(rect(bx, by, bw, bh, fill=BG, stroke=INK, sw=1.5, rx=4))
    p.append(text(bx + bw / 2, by - 10, "період відліку  T = 1/fs", size=10, color=INK, bold=True))
    fw = int(bw * 0.35)
    p.append(rect(bx, by, fw, bh, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(bx + fw / 2, by + 25, "фільтр", size=10, color=FIELD, bold=True))
    p.append(text(bx + fw + (bw - fw) / 2, by + 25, "запас на решту", size=10, color=MUTED, italic=True))
    p.append(text(W / 2, 182,
                  "усі MAC-и фільтра + інше мусять укластися в T; не влізли — нижчий fs або легший фільтр",
                  size=9, color=MUTED, italic=True))
    render(os.path.join(IMG, "budget.svg"), W, H, *p,
           title="Бюджет реального часу: фільтр має влізти в період відліку")


if __name__ == "__main__":
    fig_float_fixed()
    fig_qformat()
    fig_accumulator()
    fig_overflow_sat()
    fig_coef_quant()
    fig_budget()
    print("OK: 6 figures ->", IMG)
