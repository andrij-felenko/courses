# -*- coding: utf-8 -*-
"""Фігури до теми «В'язкість».
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

FLU = "#cfe8f5"     # рідина/газ — світлий прошарок
FLUD = "#8fc7e6"
SHADE = "#fbe4c4"   # заливка профілю швидкості
ORANGE = "#e08e0b"
GREEN = FIELD


def frange(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def logsp(a, b, n):
    return [a * (b / a) ** (i / (n - 1)) for i in range(n)]


def polyline(pts, color=INK, sw=2.6, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" '
            'stroke-width="%.1f"%s/>' % (p, color, sw, d))


def polygon(pts, fill=SHADE, stroke="none", sw=0):
    p = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" '
            'stroke-width="%.1f"/>' % (p, fill, stroke, sw))


def ground(x1, x2, y, color=INK, sw=2):
    out = [line(x1, y, x2, y, color=color, sw=sw)]
    n = 15
    for i in range(n):
        xx = x1 + (x2 - x1) * i / (n - 1)
        out.append(line(xx, y, xx - 11, y + 12, color=color, sw=1.2))
    return "".join(out)


# ── Фігура 1: означення — профіль швидкості між пластинами (течія Куетта) ─────
def fig_couette():
    W, H = 940, 560
    F = []
    xL, xR = 150, 560
    yTop, yBot = 158, 396          # низ верхньої / верх нижньої пластини
    hpx = yBot - yTop

    # верхня рухома пластина
    F.append(rect(xL, yTop - 24, xR - xL, 24, fill="#3a4149", stroke=INK, sw=1.5, rx=3))
    F.append(text((xL + xR) / 2, yTop - 8, "рухома пластина", size=13, color="#ffffff", bold=True))
    # стрілка швидкості U
    F.append(arrow(xR - 150, yTop - 40, xR - 10, yTop - 40, color=POS, sw=3.2))
    F.append(text(xR - 80, yTop - 48, "швидкість U", size=13.5, color=POS, bold=True))

    # рідина
    F.append(rect(xL, yTop, xR - xL, hpx, fill=FLU, stroke=FLUD, sw=1.3))

    # профіль швидкості: u=0 внизу (прилипання), u=U угорі
    xb = xL + 88
    Umax = 258
    tri = [(xb, yBot), (xb + Umax, yTop), (xb, yTop)]
    F.append(polygon(tri, fill=SHADE))
    F.append(line(xb, yBot, xb + Umax, yTop, color=POS, sw=2.8))     # обвідна профілю
    F.append(line(xb, yTop, xb, yBot, color=MUTED, sw=1.4))          # база
    for f in [0.14, 0.3, 0.46, 0.62, 0.78, 0.94]:
        y = yBot - f * hpx
        F.append(arrow(xb, y, xb + Umax * f, y, color=NEG, sw=2.2))
    F.append(text(xb + 4, yTop + 14, "u = U", size=12, color=POS, bold=True, anchor="start"))
    F.append(text(xb + 4, yBot - 8, "u = 0  (прилипання)", size=11.5, color=MUTED, anchor="start"))
    F.append(text(xb + Umax + 12, yTop + 30, "профіль u(y)", size=13, color=POS, bold=True, anchor="start"))

    # нижня нерухома пластина
    F.append(rect(xL, yBot, xR - xL, 24, fill="#3a4149", stroke=INK, sw=1.5, rx=3))
    F.append(text((xL + xR) / 2, yBot + 16, "нерухома пластина", size=13, color="#ffffff", bold=True))
    F.append(ground(xL, xR, yBot + 24))

    # розмір h
    F.append(arrow(xL + 36, yTop, xL + 36, yBot, color=INK, sw=1.7))
    F.append(arrow(xL + 36, yBot, xL + 36, yTop, color=INK, sw=1.7))
    F.append(text(xL + 24, (yTop + yBot) / 2 + 5, "h", size=16, color=INK, bold=True, italic=True, anchor="end"))

    # права колонка — зсунутий елемент рідини + формула
    bx = 640
    F.append(text(bx + 118, 96, "рідину безперервно зсуває", size=13, bold=True))
    # квадрат → паралелограм
    sq_y0, sq_h = 128, 92
    F.append(polygon([(bx, sq_y0 + sq_h), (bx + 120, sq_y0 + sq_h), (bx + 120, sq_y0), (bx, sq_y0)],
                     fill="none", stroke=MUTED, sw=1.4))
    F.append(polygon([(bx + 150, sq_y0 + sq_h), (bx + 270, sq_y0 + sq_h),
                      (bx + 270 + 46, sq_y0), (bx + 150 + 46, sq_y0)],
                     fill=FLU, stroke=FLUD, sw=1.6))
    F.append(arrow(bx + 128, sq_y0 + sq_h / 2, bx + 148, sq_y0 + sq_h / 2, color=INK, sw=2.0))
    F.append(text(bx + 60, sq_y0 - 8, "спокій", size=11.5, color=MUTED))
    F.append(text(bx + 236, sq_y0 - 8, "зсув γ", size=11.5, color=NEG, bold=True))

    F.append(fitbox(bx, 250, 264, 96,
                    "дотичне напруження\n"
                    "τ = μ · (U / h)\n"
                    "μ — коефіцієнт в'язкості (Па·с)",
                    size=14, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))

    F.append(fitbox(150, 470, 754, 54,
                    "тонший шар або швидша пластина → крутіший перепад швидкості U/h "
                    "→ більше тертя;  сила F = τ·A = μ·A·U/h",
                    size=13.5, bold=True, fill="#f4f6f8", stroke=LINE, pad=10))

    render(os.path.join(IMG, "couette-definition.svg"), W, H, *F,
           title="В'язкість = тертя між шарами: напруження ∝ перепаду швидкості U/h")


# ── Фігура 2: протилежна температурна залежність рідини й газу ────────────────
def fig_temperature():
    W, H = 960, 540
    F = []
    x0, x1 = 108, 606
    yt, yb = 96, 430

    def X(t):    # t у [0,1] — відносна температура
        return x0 + t * (x1 - x0)

    def Y(v):    # v у [0,1]
        return yb - v * (yb - yt) * 0.92

    # осі
    F.append(line(x0, yt, x0, yb, color=INK, sw=1.8))
    F.append(line(x0, yb, x1, yb, color=INK, sw=1.8))
    F.append(arrow(x1 - 2, yb, x1 + 24, yb, color=INK, sw=1.8))
    F.append(text((x0 + x1) / 2, yb + 40, "температура  T  →", size=14, color=INK))
    F.append(text(x0 - 6, yt - 16, "в'язкість  μ", size=13, color=MUTED, anchor="start"))

    # крива рідини — круто спадає
    liq = [(X(t), Y(0.95 * math.exp(-2.6 * t) + 0.03)) for t in frange(0.02, 1.0, 160)]
    F.append(polyline(liq, color=ORANGE, sw=3.4))
    F.append(text(X(0.30), Y(0.95 * math.exp(-2.6 * 0.30) + 0.03) - 16,
                  "РІДИНА:  μ ПАДАЄ", size=14, color=ORANGE, bold=True, anchor="start"))

    # крива газу — полого росте (∝ √T)
    gas = [(X(t), Y(0.16 + 0.5 * math.sqrt(t))) for t in frange(0.02, 1.0, 160)]
    F.append(polyline(gas, color=GREEN, sw=3.4))
    F.append(text(X(0.52), Y(0.16 + 0.5 * math.sqrt(0.52)) + 26,
                  "ГАЗ:  μ РОСТЕ  (∝ √T)", size=14, color=GREEN, bold=True, anchor="start"))

    # права колонка — два механізми
    bx, bw = 648, 292
    # газ (згори)
    F.append(fitbox(bx, 84, bw, 150,
                    "ГАЗ — молекули вільно літають.\n"
                    "Тертя = обмін імпульсом:\n"
                    "молекула з швидшого шару\n"
                    "перескакує в повільніший.\n"
                    "Гарячіше → жвавіший обмін\n"
                    "→ тертя росте.",
                    size=12.5, fill="#eafaf0", stroke=GREEN, pad=10))
    # маленька схема перескоку
    ly, lyd = 250, 40
    F.append(line(bx + 20, ly, bx + bw - 20, ly, color=NEG, sw=1.4, dash="5 5"))
    F.append(line(bx + 20, ly + lyd, bx + bw - 20, ly + lyd, color=MUTED, sw=1.4, dash="5 5"))
    F.append(text(bx + bw - 16, ly - 8, "швидкий шар", size=10.5, color=NEG, anchor="end"))
    F.append(text(bx + bw - 16, ly + lyd + 16, "повільний шар", size=10.5, color=MUTED, anchor="end"))
    F.append(arrow(bx + 90, ly, bx + 150, ly + lyd, color=POS, sw=2.2))
    F.append(circle(bx + 90, ly, 6, fill="#fdecea", stroke=POS, sw=1.6))
    F.append(text(bx + 60, ly + lyd + 16, "переносить\nімпульс".split("\n")[0], size=10.5, color=POS, anchor="start"))

    # рідина (знизу)
    F.append(fitbox(bx, 330, bw, 120,
                    "РІДИНА — молекули зчеплені.\n"
                    "Тертя = розрив зчеплень при\n"
                    "ковзанні шарів.\n"
                    "Гарячіше → зчеплення слабшають\n"
                    "→ тертя падає.",
                    size=12.5, fill="#fdf2ef", stroke=ORANGE, pad=10))

    F.append(fitbox(x0, yb + 58, 532, 40,
                    "мед у теплі тече, застигши — ні; а от повітря гарячим тече «густіше»,\n"
                    "ніж холодним — бо в газі за в'язкість відповідає геть інший механізм",
                    size=12, bold=True, fill="#f4f6f8", stroke=LINE, pad=8))

    render(os.path.join(IMG, "temperature-dependence.svg"), W, H, *F,
           title="Дві різні природи: з нагрівом рідина рідшає, а газ — «густішає»")


# ── Фігура 3: динамічна проти кінематичної — ролі води й повітря міняються ────
def fig_dynamic_kinematic():
    W, H = 940, 520
    F = []

    def group(cx, title, unit, wname, wval, aname, aval, wtxt, atxt, note):
        out = []
        gw = 300
        x0 = cx - gw / 2
        yb = 380
        yt = 150
        # log-шкала висоти стовпців
        vals = [wval, aval]
        lo = min(vals) / 3.0
        hi = max(vals) * 1.4

        def Hbar(v):
            return (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (yb - yt)

        F_bw = 78
        wx = cx - 84
        ax = cx + 84
        # база
        out.append(line(x0, yb, x0 + gw, yb, color=INK, sw=1.8))
        out.append(text(cx, 108, title, size=15, bold=True))
        out.append(text(cx, 128, unit, size=12, color=MUTED))
        # стовпці
        out.append(rect(wx - F_bw / 2, yb - Hbar(wval), F_bw, Hbar(wval), fill=NEG, stroke=INK, sw=1.3, rx=3))
        out.append(rect(ax - F_bw / 2, yb - Hbar(aval), F_bw, Hbar(aval), fill=FLUD, stroke=INK, sw=1.3, rx=3))
        out.append(text(wx, yb - Hbar(wval) - 10, wtxt, size=12, color=NEG, bold=True))
        out.append(text(ax, yb - Hbar(aval) - 10, atxt, size=12, color="#2a6f97", bold=True))
        out.append(text(wx, yb + 20, wname, size=12.5, bold=True))
        out.append(text(ax, yb + 20, aname, size=12.5, bold=True))
        out.append(text(cx, yb + 44, note, size=12, color=POS, italic=True, bold=True))
        return out

    F += group(255, "динамічна  μ", "(Па·с — «липкість» на дотик)",
               "вода", 1.0e-3, "повітря", 1.8e-5,
               "1.0 мПа·с", "0.018 мПа·с", "вода ~55× «густіша»")
    F += group(690, "кінематична  ν = μ/ρ", "(мм²/с — як розповзається рух)",
               "вода", 1.0, "повітря", 15.0,
               "1.0 мм²/с", "15 мм²/с", "повітря ~15× «швидше»")

    # стрілка-переворот
    F.append(text(472, 190, "але", size=13, color=INK, bold=True))
    F.append(arrow(430, 220, 512, 220, color=INK, sw=2.6))
    F.append(text(472, 246, "ролі\nміняються".split("\n")[0], size=12.5, color=POS, bold=True))
    F.append(text(472, 262, "місцями", size=12.5, color=POS, bold=True))

    F.append(fitbox(120, 430, 700, 56,
                    "повітря на дотик у 55 разів «рідше» за воду (мала μ),\n"
                    "але вділивши на його крихітну густину — рух розповзається в ньому в 15 разів ШВИДШЕ",
                    size=13, bold=True, fill="#f4f6f8", stroke=LINE, pad=10))

    render(os.path.join(IMG, "dynamic-vs-kinematic.svg"), W, H, *F,
           title="Дві в'язкості: поділивши μ на густину, вода й повітря міняються місцями")


# ── Фігура 4: драбина в'язкостей — 13 порядків величини ──────────────────────
def fig_ladder():
    W, H = 980, 470
    F = []
    x0, x1 = 96, 900
    ax = 322         # рівень осі (унизу, щоб над нею стало місце на дві полиці міток)
    vmin, vmax = 1e-5, 1e9
    lmin, lmax = math.log10(vmin), math.log10(vmax)

    def X(v):
        return x0 + (math.log10(v) - lmin) / (lmax - lmin) * (x1 - x0)

    # вісь
    F.append(line(x0, ax, x1, ax, color=INK, sw=2.2))
    F.append(arrow(x1 - 2, ax, x1 + 24, ax, color=INK, sw=2.2))
    # мітки степенів (Unicode) — стоять ПІД віссю
    ticks = [(-5, "10⁻⁵"), (-3, "10⁻³"), (-1, "10⁻¹"), (1, "10¹"),
             (3, "10³"), (5, "10⁵"), (7, "10⁷"), (9, "10⁹")]
    for e, lb in ticks:
        v = 10.0 ** e
        F.append(line(X(v), ax - 6, X(v), ax + 6, color=MUTED, sw=1.2))
        F.append(text(X(v), ax + 26, lb, size=12, color=MUTED))
    F.append(text((x0 + x1) / 2, ax + 50, "в'язкість  μ,  Па·с   (логарифмічна шкала)", size=13.5, color=INK))

    # елементи — усі підписи ВГОРІ (під віссю лише мітки степенів), дві полиці,
    # щоб виноски не лягали одна на одну й не чіпали міток осі
    items = [
        (1.8e-5, "повітря", 0),
        (1.0e-3, "вода", 1),
        (8.0e-2, "оливкова олія", 0),
        (1.0e1,  "мед", 1),
        (1.0e8,  "бітум (смола)", 0),
    ]
    shelf = {0: ax - 62, 1: ax - 118}   # центр напису на полиці
    for v, name, s in items:
        x = X(v)
        cy = shelf[s]
        # виноска доходить ДО центру напису (кінець усередині рамки — рамка накриває хвіст),
        # тож лінія не «протикає» напис наскрізь
        F.append(line(x, ax - 7, x, cy, color=MUTED, sw=1.2))
        F.append(circle(x, ax, 6.5, fill=GREEN, stroke=INK, sw=1.5))
        F.append(textbox(x, cy, name, size=12.5, bold=True,
                         fill="#eafaf0", stroke=GREEN, pad=7)[0])

    F.append(fitbox(x0, 402, x1 - x0, 46,
                    "від повітря до смоли — понад 13 порядків величини:  "
                    "смола тече в мільярди разів «важче» за воду, але тече",
                    size=13, bold=True, fill="#fff6e8", stroke=ORANGE, pad=9))

    render(os.path.join(IMG, "viscosity-ladder.svg"), W, H, *F,
           title="Драбина в'язкостей: одне явище на 13 порядків величини")


# ── Фігура 5 (hist): 180-річна дорога від слова до числа ─────────────────────
def fig_history():
    W, H = 1180, 470
    F = []
    x0, x1 = 95, 1085
    ly = 235                       # рівень осі часу
    usable = x1 - x0

    # горизонтальна вісь-стрічка часу
    F.append(line(x0, ly, x1, ly, color=INK, sw=2.4))
    F.append(arrow(x1 - 2, ly, x1 + 26, ly, color=INK, sw=2.4))
    F.append(text(x1 + 20, ly + 28, "час", size=13, color=MUTED, anchor="end"))

    # ноти: 6 станцій, рівномірно; підписи через одну — вгору/вниз
    BLUE_F, ORA_F, GRN_F = "#eaf0fd", "#fff2e2", "#eafaf0"
    nodes = [
        ("1687 · Ньютон\nгіпотеза словами\n(Principia, кн. II)",      INK,   FILL),
        ("1822 · Навʼє\nвʼязкість — у рівняння\nруху рідини",          NEG,   BLUE_F),
        ("1838–46 · Пуазейль\nзакон тонких трубок\n(∝ r⁴); з крові",   ORANGE, ORA_F),
        ("1845 · Стокс\nстрога суцільна\n3-D форма",                   NEG,   BLUE_F),
        ("1860 · Максвелл\nкінетична теорія:\nμ газу не від тиску",    GREEN, GRN_F),
        ("1866 · Максвелл і Кетрін\nвимір біля каміна:\nμ росте з T",  GREEN, GRN_F),
    ]
    for i, (label, col, fillc) in enumerate(nodes):
        cx = x0 + usable * (i + 0.5) / len(nodes)
        up = (i % 2 == 0)
        boxcy = 112 if up else 358
        # конектор від точки до рамки
        F.append(line(cx, ly + (-8 if up else 8), cx, boxcy + (30 if up else -30),
                      color=MUTED, sw=1.3))
        F.append(circle(cx, ly, 7.5, fill=fillc, stroke=col, sw=2.4))
        F.append(textbox(cx, boxcy, label, size=13, bold=True,
                         fill=fillc, stroke=col, pad=9)[0])

    # позначка «довгої тиші» між Ньютоном і Навʼє
    xm = (x0 + usable * 0.5 / 6 + x0 + usable * 1.5 / 6) / 2
    F.append(text(xm, ly - 16, "≈130 років майже тиші", size=12.5,
                  color=MUTED, italic=True))
    F.append(line(x0 + usable * 0.5 / 6 + 40, ly - 30,
                  x0 + usable * 1.5 / 6 - 40, ly - 30, color=MUTED, sw=1.2, dash="4 5"))

    F.append(fitbox(x0, 418, x1 - x0, 40,
                    "від слова в трактаті про вихори — через рівняння руху — "
                    "до коефіцієнта, який виміряли власноруч і пояснили молекулами",
                    size=13, bold=True, fill="#f4f6f8", stroke=LINE, pad=9))

    render(os.path.join(IMG, "history-timeline.svg"), W, H, *F,
           title="Як в'язкість стала числом: від Ньютона (1687) до Максвелла (1866)")


# ── Фігура 6 (math): Стоксова перша задача — профіль erfc проникає як √(νt) ────
def fig_stokes():
    W, H = 1000, 560
    F = []
    xAx = 214                 # вертикальна вісь: u/U = 0 (далеке поле)
    S = 250                   # ширина під u/U ∈ [0,1]
    yWall, yTop = 452, 96
    span = yWall - yTop

    # легка сітка по u/U
    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = xAx + f * S
        F.append(line(x, yTop, x, yWall, color="#e6e9ec", sw=1))

    # осі
    F.append(line(xAx, yTop, xAx, yWall, color=INK, sw=1.8))
    F.append(arrow(xAx, yTop + 4, xAx, yTop - 26, color=INK, sw=1.8))
    F.append(text(xAx + 8, yTop - 14, "y — вглиб рідини", size=12.5, color=MUTED, anchor="start"))
    F.append(line(xAx, yWall, xAx + S, yWall, color=INK, sw=1.8))
    F.append(text(xAx + S + 10, yWall - 2, "u / U →", size=12.5, color=INK, anchor="start"))

    # три «моменти часу»: масштаб a ∝ √t,  a₁:a₂:a₃ = 1:2:3 → t₂=4t₁, t₃=9t₁
    curves = [
        (1 / 6.0, ORANGE, "t₁"),
        (1 / 3.0, GREEN,  "t₂ = 4·t₁"),
        (1 / 2.0, NEG,    "t₃ = 9·t₁"),
    ]
    for a, col, lab in curves:
        pts = []
        n = 90
        for i in range(n):
            yv = i / (n - 1)                     # нормована відстань 0..1
            uu = math.erfc(yv / a)               # u/U = erfc(y / a)
            pts.append((xAx + uu * S, yWall - yv * span))
        F.append(polyline(pts, color=col, sw=3.2))
        yl = 1.12 * a                            # мітка там, де u/U≈0.12
        F.append(text(xAx + 0.12 * S + 8, yWall - yl * span + 4, lab,
                      size=12.5, color=col, bold=True, anchor="start"))

    F.append(text(xAx + 14, yTop + 24, "u → 0  (спокій угорі)", size=11.5, color=MUTED, anchor="start"))

    # рухома стінка (u = U) знизу
    F.append(rect(xAx - 54, yWall, S + 58, 22, fill="#3a4149", stroke=INK, sw=1.5, rx=3))
    F.append(text(xAx + S / 2 - 8, yWall + 15, "рухома стінка ·  u = U", size=12.5, color="#ffffff", bold=True))
    F.append(arrow(xAx + S - 116, yWall + 42, xAx + S + 4, yWall + 42, color=POS, sw=3))
    F.append(text(xAx + S + 14, yWall + 46, "U", size=14, color=POS, bold=True, anchor="start"))
    F.append(text(xAx - 20, (yTop + yWall) / 2, "t₁ < t₂ < t₃", size=12, color=MUTED,
                  anchor="middle", italic=True))

    # права колонка — суть і числа
    bx, bw = 566, 404
    F.append(fitbox(bx, 92, bw, 60,
                    "u(y, t) = U · erfc( y / (2·√(ν·t)) )",
                    size=17, bold=True, fill="#eafaf0", stroke=GREEN, pad=12))
    F.append(fitbox(bx, 168, bw, 104,
                    "Єдиний масштаб довжини в задачі — √(ν·t).\n"
                    "Тому профіль із часом лише РОЗТЯГУЄТЬСЯ,\n"
                    "не міняючи форми: рух проникає вглиб на\n"
                    "глибину  δ ~ √(ν·t).  Учетверо довше чекаєш —\n"
                    "лише вдвічі глибше проникло (t₂=4t₁ → δ₂=2δ₁).",
                    size=13, fill=FILL, stroke=LINE, pad=10))
    F.append(fitbox(bx, 288, bw, 96,
                    "за t = 1 с  (край δ ≈ 4·√(ν·t)):\n"
                    "• вода    ν = 1.0·10⁻⁶ м²/с  → δ ≈ 4 мм\n"
                    "• повітря  ν = 1.5·10⁻⁵ м²/с  → δ ≈ 1.6 см\n"
                    "• мед     ν ≈ 7·10⁻³ м²/с    → δ ≈ 0.3 м",
                    size=13, fill="#fff6e8", stroke=ORANGE, pad=10))
    F.append(fitbox(bx, 400, bw, 72,
                    "erfc спадає круто: при  y = 4·√(ν·t)  швидкість\n"
                    "уже < 1 % від U — практичний край розігнаного\n"
                    "шару (у сталій течії це майбутній межовий шар).",
                    size=12.5, fill="#f0f4ff", stroke=NEG, pad=10))

    render(os.path.join(IMG, "stokes-first-problem.svg"), W, H, *F,
           title="Стоксова перша задача: раптово зрушена стінка — рух дифундує як √(νt)")


# ── Фігура 7 (math): один закон дифузії — імпульс, тепло, маса ────────────────
def fig_three_diffusivities():
    W, H = 1000, 560
    F = []
    panels = [
        ("ІМПУЛЬС",  "швидкість u",    "∂u/∂t = ν·∂²u/∂y²",
         "ν — кінематична в'язкість\n(дифузія імпульсу)", NEG,    "#e8f0ff"),
        ("ТЕПЛО",    "температура T",  "∂T/∂t = α·∂²T/∂y²",
         "α — температуропровідність\n(дифузія тепла)",   ORANGE, "#fff0e2"),
        ("РЕЧОВИНА", "концентрація c", "∂c/∂t = D·∂²c/∂y²",
         "D — коефіцієнт дифузії\n(дифузія маси)",             GREEN,  "#e9faf0"),
    ]
    pw, gap, x0 = 290, 20, 48
    pyT, pyB = 108, 300
    axis_w = pw - 76
    for k, (tag, qty, pde, coefname, col, fillc) in enumerate(panels):
        px = x0 + k * (pw + gap)
        ax = px + 40
        cx = px + pw / 2
        mid = (pyT + pyB) / 2
        amp = (pyB - pyT) * 0.19
        F.append(rect(px, pyT, pw, pyB - pyT, fill="#ffffff", stroke=col, sw=2, rx=8))
        F.append(text(cx, pyT - 14, tag, size=15, bold=True, color=col))
        F.append(line(ax, pyT + 12, ax, pyB - 12, color=INK, sw=1.5))     # вісь величини
        # початковий різкий стрибок (пунктир): угорі велика, унизу мала
        F.append(line(ax + axis_w, pyT + 12, ax + axis_w, mid, color=MUTED, sw=1.5, dash="5 5"))
        F.append(line(ax, mid, ax + axis_w, mid, color=MUTED, sw=1.5, dash="5 5"))
        F.append(line(ax, mid, ax, pyB - 12, color=MUTED, sw=1.5, dash="5 5"))
        # згладжений erf-профіль (те, у що стрибок перетворює дифузія)
        prof = []
        n = 80
        for i in range(n):
            yy = pyT + 12 + (pyB - pyT - 24) * i / (n - 1)
            phi = 0.5 * math.erfc((yy - mid) / amp)          # →1 угорі, →0 унизу
            prof.append((ax + phi * axis_w, yy))
        F.append(polyline(prof, color=col, sw=3.2))
        F.append(text(ax + axis_w, pyT + 4, "велика", size=10, color=col))
        F.append(text(ax, pyB - 2, "мала", size=10, color=MUTED))
        F.append(text(cx, pyB + 22, qty, size=12.5, bold=True))
        F.append(fitbox(px + 8, pyB + 34, pw - 16, 34, pde, size=15, bold=True, fill=fillc, stroke=col, pad=6))
        F.append(textbox(cx, pyB + 100, coefname, size=11.5, fill=fillc, stroke=col, pad=8)[0])

    # нижня стрічка — безрозмірні відношення й числа
    by = 452
    F.append(fitbox(48, by, 424, 92,
                    "ОДНАКОВА математика — різні коефіцієнти.\n"
                    "Їхні відношення безрозмірні:\n"
                    "Pr = ν / α   (імпульс ÷ тепло) — число Прандтля\n"
                    "Sc = ν / D   (імпульс ÷ маса)  — число Шмідта",
                    size=13, bold=True, fill="#f4f6f8", stroke=LINE, pad=10))
    F.append(fitbox(492, by, 460, 92,
                    "повітря (газ):  Pr≈0.71,  Sc≈0.7 — усі три близькі: один\n"
                    "     механізм (перельоти молекул) несе і імпульс, і тепло, і масу\n"
                    "вода:  Pr≈7 (тепло відстає),  Sc≈10³ (розчин повзе — тому\n"
                    "     цукор РОЗМІШУЮТЬ, а не чекають, поки сам розійдеться)\n"
                    "ртуть:  Pr≈0.02 — тепло (електрони) біжить швидше за імпульс",
                    size=11.5, fill="#eef4ff", stroke=NEG, pad=9))

    render(os.path.join(IMG, "momentum-diffusivity-analogy.svg"), W, H, *F,
           title="Кінематична в'язкість ν — коефіцієнт дифузії імпульсу (поряд із тепловою α та масовою D)")


# ── Фігура 8 (math): кінетика газу — μ = ⅓ρv̄λ і незалежність від тиску ────────
def fig_kinetic_transport():
    W, H = 980, 640
    F = []
    # ── верх: перенос імпульсу перельотом на ~λ ──
    F.append(text(300, 54, "ГАЗ: тертя = перенос імпульсу перельотами молекул", size=15, bold=True))
    xL, xR = 96, 556
    yFast, ySlow = 128, 250
    F.append(line(xL, yFast, xR, yFast, color=NEG, sw=1.6, dash="6 5"))
    F.append(line(xL, ySlow, xR, ySlow, color=MUTED, sw=1.6, dash="6 5"))
    F.append(text(xR - 4, yFast - 10, "швидкий шар (u+)", size=12, color=NEG, anchor="end"))
    F.append(text(xR - 4, ySlow + 22, "повільний шар (u−)", size=12, color=MUTED, anchor="end"))
    F.append(arrow(xR - 150, yFast, xR - 8, yFast, color=NEG, sw=2.6))
    F.append(arrow(xR - 84, ySlow, xR - 8, ySlow, color=MUTED, sw=2.6))
    # молекула згори вниз — несе +імпульс у повільний шар
    mx = 250
    F.append(arrow(mx, yFast + 6, mx + 40, ySlow - 6, color=POS, sw=2.4))
    F.append(circle(mx, yFast, 7, fill="#fdecea", stroke=POS, sw=1.8))
    F.append(text(mx + 52, (yFast + ySlow) / 2 - 4, "несе +імпульс", size=11.5, color=POS, anchor="start"))
    F.append(text(mx + 52, (yFast + ySlow) / 2 + 12, "у повільний шар", size=11.5, color=POS, anchor="start"))
    # молекула знизу вгору
    mx2 = 168
    F.append(arrow(mx2, ySlow - 6, mx2 - 34, yFast + 6, color=NEG, sw=2.4))
    F.append(circle(mx2, ySlow, 7, fill="#eaf0fd", stroke=NEG, sw=1.8))
    # відстань між шарами ≈ λ
    F.append(arrow(xL + 20, yFast, xL + 20, ySlow, color=INK, sw=1.5))
    F.append(arrow(xL + 20, ySlow, xL + 20, yFast, color=INK, sw=1.5))
    F.append(text(xL + 28, (yFast + ySlow) / 2 + 4, "≈ λ", size=14, color=INK, bold=True, italic=True, anchor="start"))
    # формула праворуч
    F.append(fitbox(600, 96, 352, 96,
                    "потік імпульсу через площину:\n"
                    "τ = ⅓·ρ·v̄·λ · (du/dy)\n"
                    "⇒  μ = ⅓·ρ·v̄·λ\n"
                    "(строга кінетика: коеф. ≈ 0.49)",
                    size=14, bold=True, fill="#eafaf0", stroke=GREEN, pad=10))
    F.append(fitbox(600, 204, 352, 46,
                    "v̄ — середня теплова швидкість\nλ — довжина вільного пробігу",
                    size=12, fill=FILL, stroke=LINE, pad=8))

    # ── низ: незалежність від тиску (n·λ = const) ──
    F.append(line(64, 300, 916, 300, color=LINE, sw=1))
    F.append(text(300, 338, "Чому μ газу майже не залежить від тиску", size=15, bold=True))

    def gas_box(x0, dots, plen, title):
        by0, bw, bh = 366, 300, 150
        F.append(rect(x0, by0, bw, bh, fill="#f7fbff", stroke=NEG, sw=1.6, rx=8))
        F.append(text(x0 + bw / 2, by0 - 8, title, size=12.5, bold=True, color=NEG))
        for (dx, dy) in dots:
            F.append(circle(x0 + dx, by0 + dy, 5, fill="#dfeaff", stroke=NEG, sw=1.3))
        # репрезентативний вільний пробіг
        F.append(arrow(x0 + 40, by0 + 118, x0 + 40 + plen, by0 + 118, color=INK, sw=2))
        return by0, bh

    d1 = [(60, 46), (150, 96), (240, 40), (110, 78), (200, 108), (250, 84)]
    gas_box(110, d1, 200, "звичайний тиск:  n переносників")
    F.append(text(110 + 150, 366 + 138, "довгий пробіг  λ", size=11.5, color=INK))
    F.append(text(110 + 150, 366 + 172, "n · λ", size=15, bold=True, color=NEG))

    d2 = [(40, 44), (95, 100), (140, 40), (75, 74), (170, 104), (210, 60),
          (250, 96), (120, 112), (200, 42), (60, 116), (235, 44), (160, 78)]
    gas_box(560, d2, 100, "стиснули вдвічі:  2n переносників")
    F.append(text(560 + 150, 366 + 138, "короткий пробіг  λ/2", size=11.5, color=INK))
    F.append(text(560 + 150, 366 + 172, "2n · (λ/2)", size=15, bold=True, color=NEG))

    F.append(text(487, 366 + 84, "=", size=30, bold=True, color=POS))

    F.append(fitbox(64, 566, 852, 54,
                    "переносників стало вдвічі більше — зате кожен долітає вдвічі ближче:  добуток  n·λ = const\n"
                    "⇒  μ не залежить від тиску;   а v̄ ∝ √T  ⇒  μ ∝ √T  (з нагрівом газ «густішає»)",
                    size=13, bold=True, fill="#fff6e8", stroke=ORANGE, pad=10))

    render(os.path.join(IMG, "kinetic-momentum-transport.svg"), W, H, *F,
           title="Кінетична оцінка: μ = ⅓·ρ·v̄·λ, і чому вона не залежить від тиску")


# ── Unicode-надрядкові для степенів на осі ───────────────────────────────────
_SUP = {'-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
def sup(n):
    return ''.join(_SUP[c] for c in str(n))


# ── proj-фігура 1: баланс сил на кульці й вихід на усталену швидкість ─────────
def fig_ball_balance():
    W, H = 980, 600
    F = []
    # трубка з рідиною
    tx, tw, tyt, tyb = 96, 104, 78, 470
    F.append(rect(tx, tyt, tw, tyb - tyt, fill=FLU, stroke=FLUD, sw=1.6))
    F.append(text(tx + tw / 2, tyt - 12, "трубка з рідиною", size=12, color=MUTED))
    cx, cy, br = tx + tw / 2, 252, 21
    # сили: вага вниз (довга) = виштовхування + опір угору (дві коротші)
    F.append(arrow(cx, cy + br + 3, cx, cy + br + 92, color=POS, sw=3.6))
    F.append(arrow(cx - 24, cy - br - 3, cx - 24, cy - br - 50, color=NEG, sw=3.0))
    F.append(arrow(cx + 24, cy - br - 3, cx + 24, cy - br - 50, color=GREEN, sw=3.0))
    F.append(circle(cx, cy, br, fill="#9aa4ad", stroke=INK, sw=1.7))
    F.append(text(cx, cy + br + 112, "вниз", size=11, color=POS, bold=True))
    F.append(text(cx, cy - br - 60, "вгору", size=11, color=MUTED))

    # легенда трьох сил
    lx, ly, lw = 244, 150, 258
    rows = [(POS,   "вага   ρ_s · V · g"),
            (NEG,   "виштовхування   ρ_f · V · g"),
            (GREEN, "Стоксів опір   6π μ r v")]
    F.append(text(lx, ly - 18, "три сили на кульці:", size=13, bold=True, anchor="start"))
    for i, (col, lab) in enumerate(rows):
        yy = ly + i * 30
        F.append(rect(lx, yy - 12, 16, 16, fill=col, stroke=INK, sw=1.2, rx=3))
        F.append(text(lx + 24, yy + 1, lab, size=12.5, anchor="start"))
    F.append(fitbox(lx, ly + 92, lw, 44,
                    "на терміналі прискорення = 0:\nвгору (виштовх. + опір) = вниз (вага)",
                    size=12, bold=True, fill="#f4f6f8", stroke=LINE, pad=8))

    # крива v(t) → v_т
    ax0, ax1, ayb, ayt = 566, 936, 372, 152
    F.append(line(ax0, ayt - 6, ax0, ayb, color=INK, sw=1.7))
    F.append(arrow(ax0, ayt - 6, ax0, ayt - 30, color=INK, sw=1.7))
    F.append(line(ax0, ayb, ax1, ayb, color=INK, sw=1.7))
    F.append(arrow(ax1, ayb, ax1 + 22, ayb, color=INK, sw=1.7))
    F.append(text(ax0 - 8, ayt - 18, "v", size=14, color=INK, bold=True, italic=True, anchor="end"))
    F.append(text((ax0 + ax1) / 2, ayb + 34, "час  t  →", size=13, color=INK))

    def X(t): return ax0 + t * (ax1 - ax0)
    def Y(v): return ayb - v * (ayb - ayt)
    curve = [(X(t), Y(1 - math.exp(-t / 0.17))) for t in frange(0.0, 1.0, 72)]
    F.append(polyline(curve, color=POS, sw=3.4))
    F.append(line(ax0, Y(1.0), ax1, Y(1.0), color=MUTED, sw=1.4, dash="6 5"))
    F.append(text(ax1 - 6, Y(1.0) - 10, "v_т  (усталена)", size=12.5, color=MUTED, bold=True, anchor="end"))
    F.append(line(X(0.17), ayb, X(0.17), Y(1 - math.exp(-1.0)), color=NEG, sw=1.3, dash="4 4"))
    F.append(text(X(0.17), ayb + 18, "τ", size=13, color=NEG, bold=True, italic=True))
    F.append(mtext(X(0.60), Y(0.46), ["кулька розганяється,", "поки опір не зрівняє вагу"],
                   size=11.5, color=MUTED, anchor="middle"))

    # формула
    F.append(fitbox(96, 508, 840, 74,
                    "рівновага на терміналі:    (4/3)π r³ (ρ_s − ρ_f) g   =   6π μ r v_т\n"
                    "звідси міряємо в'язкість:    μ = 2 r² (ρ_s − ρ_f) g / (9 v_т)",
                    size=15, bold=True, fill="#eafaf0", stroke=GREEN, pad=12))

    render(os.path.join(IMG, "proj-ball-balance.svg"), W, H, *F,
           title="Кульковий в'язкозиметр: баланс трьох сил дає μ з усталеної швидкості")


# ── proj-фігура 2: вікно застосовності за числом Рейнольдса ───────────────────
def fig_reynolds_window():
    W, H = 1000, 440
    F = []
    x0, x1 = 96, 912
    axy = 250
    emin, emax = -3, 5

    def X(e): return x0 + (e - emin) / (emax - emin) * (x1 - x0)

    zt, zb = 150, 330
    zones = [(-3, -1, "#eafaf0", GREEN,  "повзка течія\nСтокс точний"),
             (-1,  0, "#fff6e8", ORANGE, "Стокс ±10 %"),
             ( 0,  3, "#fdece0", ORANGE, "інерція (Осін),\nзрив вихорів"),
             ( 3,  5, "#fdecea", POS,    "турбулентний слід\nметод НЕ діє")]
    for a, b, fillc, col, lab in zones:
        F.append(rect(X(a), zt, X(b) - X(a), zb - zt, fill=fillc, stroke="none", sw=0, rx=0))
        F.append(mtext((X(a) + X(b)) / 2, zt + 32, lab.split("\n"), size=12, color=col, bold=True))

    F.append(line(x0, axy, x1, axy, color=INK, sw=2.2))
    F.append(arrow(x1, axy, x1 + 22, axy, color=INK, sw=2.2))
    for e in range(emin, emax + 1):
        F.append(line(X(e), axy - 6, X(e), axy + 6, color=MUTED, sw=1.2))
        F.append(text(X(e), axy + 26, "10" + sup(e), size=11.5, color=MUTED))
    F.append(text((x0 + x1) / 2, axy + 52,
                  "число Рейнольдса   Re = ρ_f · v · d / μ    (логарифмічна шкала)", size=13, color=INK))

    def marker(e, col, lab, up=True):
        x = X(e)
        yy = zt - 26 if up else zb + 26
        F.append(circle(x, axy, 7, fill=col, stroke=INK, sw=1.6))
        F.append(line(x, axy, x, yy + (16 if up else -16), color=col, sw=1.4, dash="3 3"))
        F.append(textbox(x, yy, lab, size=11.5, bold=True, fill="#ffffff", stroke=col, pad=6)[0])

    marker(math.log10(0.031), GREEN, "сталь у гліцерині\nRe ≈ 0.03", up=True)
    marker(math.log10(3e4),   POS,   "сталь у воді\nRe ≈ 3·10⁴", up=False)

    F.append(fitbox(x0, 372, x1 - x0, 46,
                    "той самий прилад чинний, лише поки кулька повзе:  у гліцерині Re крихітне й Стокс точний,\n"
                    "а сталева кулька у воді «летіла б» 15 м/с — Re ~ 10⁴, вихори, і формула завищує μ у рази",
                    size=12, bold=True, fill="#f4f6f8", stroke=LINE, pad=9))

    render(os.path.join(IMG, "proj-reynolds-window.svg"), W, H, *F,
           title="Кульковий в'язкозиметр працює лише в повзкій течії (мале Re)")


# ── proj-фігура 3: пристінкова поправка — Ладенбург проти повного ряду Факсена ─
def fig_wall_correction():
    W, H = 980, 540
    F = []
    x0, x1 = 114, 612
    yb, yt = 430, 94
    xmax, Lmin, Lmax = 0.26, 1.0, 2.0

    def X(x): return x0 + x / xmax * (x1 - x0)
    def Y(L): return yb - (L - Lmin) / (Lmax - Lmin) * (yb - yt)

    def Kfax(x):
        return 1.0 / (1 - 2.10444 * x + 2.08877 * x**3 - 0.94813 * x**5)

    # осі
    F.append(line(x0, yt - 6, x0, yb, color=INK, sw=1.7))
    F.append(arrow(x0, yt - 6, x0, yt - 28, color=INK, sw=1.7))
    F.append(line(x0, yb, x1 + 8, yb, color=INK, sw=1.7))
    F.append(arrow(x1 + 8, yb, x1 + 30, yb, color=INK, sw=1.7))
    F.append(text(x0 - 8, yt - 18, "L", size=15, bold=True, italic=True, anchor="end"))
    F.append(text((x0 + x1) / 2, yb + 44, "відношення радіусів   r / R   →", size=13))
    for xv in (0.0, 0.05, 0.10, 0.15, 0.20, 0.25):
        F.append(line(X(xv), yb, X(xv), yb + 5, color=MUTED, sw=1.1))
        F.append(text(X(xv), yb + 20, "%.2f" % xv, size=10.5, color=MUTED))
    for Lv in (1.0, 1.2, 1.4, 1.6, 1.8, 2.0):
        F.append(line(x0 - 5, Y(Lv), x0, Y(Lv), color=MUTED, sw=1.1))
        F.append(text(x0 - 10, Y(Lv) + 4, "%.1f" % Lv, size=10.5, color=MUTED, anchor="end"))

    xs = frange(0.001, xmax, 90)
    lin = [(X(x), Y(1 + 2.104 * x)) for x in xs]
    fax = [(X(x), Y(Kfax(x))) for x in xs]
    F.append(polyline(lin, color=NEG, sw=3.0))
    F.append(polyline(fax, color=GREEN, sw=3.0))

    # межа лінійної форми
    F.append(line(X(0.10), yt, X(0.10), yb, color=MUTED, sw=1.3, dash="5 5"))
    F.append(text(X(0.10) + 6, yt + 12, "лінійна чинна до  r/R ≈ 0.1", size=10.5, color=MUTED, anchor="start"))

    # приклад r/R = 0.08
    F.append(circle(X(0.08), Y(1 + 2.104 * 0.08), 6, fill=ORANGE, stroke=INK, sw=1.5))
    F.append(text(X(0.08), Y(1 + 2.104 * 0.08) + 22, "наш приклад  L ≈ 1.17",
                  size=10.5, color=ORANGE, bold=True, anchor="middle"))

    # підписи кривих
    F.append(mtext(X(0.150), Y(1 + 2.104 * 0.150) + 42, ["Ладенбург (лінійна)", "1 + 2.1 · r/R"],
                   size=11.5, color=NEG, bold=True))
    F.append(text(X(0.118), Y(Kfax(0.235)) - 6, "Факсен (повний ряд)", size=11.5, color=GREEN, bold=True))

    # інсет: чому виникає гальмо
    ix = 700
    F.append(text(ix + 96, 116, "звідки гальмо", size=12.5, bold=True))
    itx, itw, ityt, ityb = ix + 66, 62, 142, 360
    F.append(rect(itx, ityt, itw, ityb - ityt, fill=FLU, stroke=FLUD, sw=1.5))
    bcx, bcy, bbr = itx + itw / 2, 252, 25
    F.append(circle(bcx, bcy, bbr, fill="#9aa4ad", stroke=INK, sw=1.6))
    F.append(arrow(itx + 3, bcy, bcx - bbr - 2, bcy, color=POS, sw=1.8))
    F.append(arrow(itx + itw - 3, bcy, bcx + bbr + 2, bcy, color=POS, sw=1.8))
    F.append(text(bcx, ityt - 8, "стінка близько", size=10.5, color=MUTED))
    F.append(fitbox(ix + 4, 374, 262, 92,
                    "рідина протискається у вузький\nзазор між кулькою й стінкою —\n"
                    "це додає опору: кулька гальмує,\nуявна μ завищена. правимо, ділячи на L.",
                    size=11, fill="#fff6e8", stroke=ORANGE, pad=9))

    F.append(fitbox(114, 488, x1 - x0, 42,
                    "у трубці кулька повзе повільніше, ніж у безмежжі:  реальну μ дістаємо, "
                    "поділивши уявну на L(r/R)",
                    size=12, bold=True, fill="#f4f6f8", stroke=LINE, pad=9))

    render(os.path.join(IMG, "proj-wall-correction.svg"), W, H, *F,
           title="Пристінкова поправка: за r/R > 0.1 лінійна форма вже занижує гальмо")


if __name__ == "__main__":
    fig_couette()
    fig_temperature()
    fig_dynamic_kinematic()
    fig_ladder()
    fig_history()
    fig_stokes()
    fig_three_diffusivities()
    fig_kinetic_transport()
    fig_ball_balance()
    fig_reynolds_window()
    fig_wall_correction()
    print("OK: 11 SVG ->", IMG)
