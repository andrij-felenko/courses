# -*- coding: utf-8 -*-
"""Фігури до статті «Інтегратор і диференціатор на ОП»
(book/electronics/analog/integrator-differentiator).

Кут статті — операція, що дала операційному підсилювачу його ім'я:
інтегрування й диференціювання як арифметика аналогової обчислювальної машини,
що фізично кориться диференціальному рівнянню.

Фігури:
  ops.svg     — дві дзеркальні операції: накопичення (площа) ↔ нахил (швидкість зміни)
  swap.svg    — одна схема, два прочитання: де стоїть C — там і операція
  summing.svg — підсумовуючий інтегратор: кілька входів течуть в один конденсатор
  solver.svg  — петля з інтеграторів, що розв'язує рівняння руху (ẍ = −k·x)
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи ────────────────────────────────────────────────────────
def opamp(cx, cy, w=70, h=70, label=None):
    """Трикутник-ОП вершиною вправо. Повертає (svg, dict вузлів)."""
    x0 = cx - w / 2
    top, bot = cy - h / 2, cy + h / 2
    tipx = cx + w / 2
    out = ['<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#ffffff" '
           'stroke="%s" stroke-width="1.8"/>' % (x0, top, x0, bot, tipx, cy, INK)]
    yin_m = cy - h * 0.22      # «−» згори (інвертуючий)
    yin_p = cy + h * 0.22      # «+» знизу
    out.append(text(x0 + 12, yin_m + 4, "−", size=15, color=NEG, bold=True))
    out.append(text(x0 + 12, yin_p + 5, "+", size=14, color=POS, bold=True))
    if label:
        out.append(text(cx + 2, cy + 5, label, size=11, color=MUTED))
    nodes = {"in_m": (x0, yin_m), "in_p": (x0, yin_p), "out": (tipx, cy)}
    return "".join(out), nodes


def cap(x1, y1, x2, y2, label=None, vertical=False):
    """Конденсатор — дві паралельні пластини посередині відрізка."""
    out = []
    if x1 == x2:  # вертикальний
        ym = (y1 + y2) / 2
        out.append(line(x1, y1, x1, ym - 5, color=INK, sw=1.6))
        out.append(line(x1 - 11, ym - 5, x1 + 11, ym - 5, color=INK, sw=2.2))
        out.append(line(x1 - 11, ym + 5, x1 + 11, ym + 5, color=INK, sw=2.2))
        out.append(line(x1, ym + 5, x1, y2, color=INK, sw=1.6))
        if label:
            out.append(text(x1 + 18, ym + 4, label, size=12, color=INK, bold=True, anchor="start"))
    else:        # горизонтальний
        xm = (x1 + x2) / 2
        out.append(line(x1, y1, xm - 5, y1, color=INK, sw=1.6))
        out.append(line(xm - 5, y1 - 11, xm - 5, y1 + 11, color=INK, sw=2.2))
        out.append(line(xm + 5, y1 - 11, xm + 5, y1 + 11, color=INK, sw=2.2))
        out.append(line(xm + 5, y1, x2, y1, color=INK, sw=1.6))
        if label:
            out.append(text(xm, y1 - 16, label, size=12, color=INK, bold=True))
    return "".join(out)


def res(x1, y1, x2, y2, label=None):
    """Резистор-зигзаг між двома точками (горизонтальний або вертикальний)."""
    out = []
    n = 6
    if y1 == y2:  # горизонтальний
        L = x2 - x1
        seg = L / (n + 2)
        out.append(line(x1, y1, x1 + seg, y1, color=INK, sw=1.6))
        amp = 6
        xx = x1 + seg
        for i in range(n):
            ny = y1 + (amp if i % 2 == 0 else -amp)
            out.append(line(xx, y1 if i == 0 else (y1 - amp if i % 2 == 1 else y1 + amp),
                            xx + seg, ny, color=INK, sw=1.6))
            xx += seg
        out.append(line(xx, y1 + (amp if (n - 1) % 2 == 0 else -amp), xx + seg, y1, color=INK, sw=1.6))
        out.append(line(xx + seg, y1, x2, y1, color=INK, sw=1.6))
        if label:
            out.append(text((x1 + x2) / 2, y1 - 14, label, size=12, color=POS, bold=True))
    else:
        L = y2 - y1
        seg = L / (n + 2)
        out.append(line(x1, y1, x1, y1 + seg, color=INK, sw=1.6))
        amp = 6
        yy = y1 + seg
        for i in range(n):
            nx = x1 + (amp if i % 2 == 0 else -amp)
            out.append(line(x1 if i == 0 else (x1 - amp if i % 2 == 1 else x1 + amp),
                            yy, nx, yy + seg, color=INK, sw=1.6))
            yy += seg
        out.append(line(x1 + (amp if (n - 1) % 2 == 0 else -amp), yy, x1, yy + seg, color=INK, sw=1.6))
        out.append(line(x1, yy + seg, x1, y2, color=INK, sw=1.6))
        if label:
            out.append(text(x1 + 16, (y1 + y2) / 2 + 4, label, size=12, color=POS, bold=True, anchor="start"))
    return "".join(out)


def gnd(cx, y):
    return "".join([line(cx, y, cx, y + 6, color=INK, sw=1.6),
                    line(cx - 11, y + 6, cx + 11, y + 6, color=INK, sw=2.2),
                    line(cx - 7, y + 10, cx + 7, y + 10, color=INK, sw=1.8),
                    line(cx - 3, y + 14, cx + 3, y + 14, color=INK, sw=1.6)])


def block(cx, cy, w, h, top, mid, col):
    """Прямокутний блок-операція з підписом-формулою."""
    out = [rect(cx - w / 2, cy - h / 2, w, h, fill="#ffffff", stroke=col, sw=2, rx=8)]
    out.append(text(cx, cy - 4, top, size=15, color=col, bold=True))
    out.append(text(cx, cy + 16, mid, size=11, color=MUTED))
    return "".join(out)


# ════════════════════════════════════════════════════════════════════════════
# 1. ops.svg — дві дзеркальні операції: площа під кривою ↔ нахил кривої
# ════════════════════════════════════════════════════════════════════════════
def fig_ops():
    W, H = 680, 320
    f = []

    # ── ліва панель: інтеграл = накопичена площа ──
    ax, ay = 70, 200
    aw, ah = 200, 140
    f.append(arrow(ax, ay, ax + aw, ay, color=INK, sw=1.6))
    f.append(arrow(ax, ay, ax, ay - ah, color=INK, sw=1.6))
    # сигнал — горб
    pts = []
    for i in range(0, 161, 4):
        t = i / 160.0
        y = math.sin(t * math.pi)
        px = ax + 10 + t * (aw - 24)
        py = ay - 8 - y * (ah - 36)
        pts.append((px, py))
    # заливка площі
    poly = "M %.1f %.1f " % (pts[0][0], ay) + " ".join("L %.1f %.1f" % p for p in pts) + " L %.1f %.1f Z" % (pts[-1][0], ay)
    f.append('<path d="%s" fill="#27ae60" fill-opacity="0.16" stroke="none"/>' % poly)
    f.append('<path d="M ' + " L ".join("%.1f %.1f" % p for p in pts) + '" fill="none" stroke="%s" stroke-width="2.4"/>' % INK)
    f.append(text(ax + aw / 2, ay - ah / 2 + 10, "площа", size=13, color=FIELD, bold=True))
    f.append(text(ax + aw / 2 + 70, 40, "ІНТЕГРАЛ", size=15, color=FIELD, bold=True, anchor="middle"))
    f.append(text(ax + aw / 2 + 70, 58, "скільки набралося", size=11, color=MUTED, anchor="middle"))
    f.append(text(ax + aw / 2, ay + 22, "∫ V dt", size=14, color=FIELD, bold=True))

    # ── права панель: похідна = нахил у точці ──
    bx, by = 410, 200
    bw, bh = 200, 140
    f.append(arrow(bx, by, bx + bw, by, color=INK, sw=1.6))
    f.append(arrow(bx, by, bx, by - bh, color=INK, sw=1.6))
    pts2 = []
    for i in range(0, 161, 4):
        t = i / 160.0
        y = t * t                      # крива, що крутішає
        px = bx + 10 + t * (bw - 24)
        py = by - 8 - y * (bh - 40)
        pts2.append((px, py, t))
    f.append('<path d="M ' + " L ".join("%.1f %.1f" % (p[0], p[1]) for p in pts2) + '" fill="none" stroke="%s" stroke-width="2.4"/>' % INK)
    # дотична в точці t≈0.7
    tt = pts2[int(len(pts2) * 0.7)]
    slope_dx = 46
    # нахил ~ 2t у наших координатах; намалюємо просто похилий відрізок
    f.append(line(tt[0] - slope_dx, tt[1] + slope_dx * 0.95, tt[0] + slope_dx, tt[1] - slope_dx * 0.95,
                  color=POS, sw=2.4))
    f.append(circle(tt[0], tt[1], 3.4, fill=POS, stroke=POS))
    f.append(text(tt[0] + 8, tt[1] - 26, "нахил", size=12, color=POS, bold=True, anchor="start"))
    f.append(text(bx + bw / 2 + 70, 40, "ПОХІДНА", size=15, color=POS, bold=True, anchor="middle"))
    f.append(text(bx + bw / 2 + 70, 58, "як швидко змінюється", size=11, color=MUTED, anchor="middle"))
    f.append(text(bx + bw / 2, by + 22, "dV/dt", size=14, color=POS, bold=True))

    # ↔ між панелями
    f.append(text(W / 2, 200, "↔", size=30, color=MUTED))
    f.append(text(W / 2, 232, "дзеркальні", size=11, color=MUTED))
    render(os.path.join(IMG, "ops.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. swap.svg — одна схема, два прочитання: переставив R і C — змінив операцію
# ════════════════════════════════════════════════════════════════════════════
def fig_swap():
    W, H = 700, 400
    f = []

    def stage(ox, oy, title, in_elem, fb_elem, formula, col):
        # in_elem, fb_elem ∈ {"R","C"}
        sub = []
        s, n = opamp(ox + 150, oy, w=64, h=64)
        node = (n["in_m"][0] - 36, n["in_m"][1])   # вузол «−» (віртуальна земля)
        # вхід зліва → елемент → вузол
        if in_elem == "R":
            sub.append(res(ox + 14, node[1], node[0], node[1], label="R"))
        else:
            sub.append(cap(ox + 14, node[1], node[0], node[1], label="C"))
        sub.append(line(node[0], node[1], n["in_m"][0], n["in_m"][1], color=INK, sw=1.6))
        sub.append(circle(node[0], node[1], 2.4, fill=INK, stroke=INK))
        sub.append(text(ox - 6, node[1] + 4, "вхід", size=11, color=MUTED, anchor="end"))
        # «+» на землю
        sub.append(line(n["in_p"][0], n["in_p"][1], n["in_p"][0] - 14, n["in_p"][1], color=INK, sw=1.6))
        sub.append(line(n["in_p"][0] - 14, n["in_p"][1], n["in_p"][0] - 14, n["in_p"][1] + 22, color=INK, sw=1.6))
        sub.append(gnd(n["in_p"][0] - 14, n["in_p"][1] + 22))
        sub.append(s)
        # зворотний зв'язок: вузол → елемент → вихід
        fbY = oy - 56
        sub.append(line(node[0], node[1], node[0], fbY, color=INK, sw=1.6))
        sub.append(line(n["out"][0], n["out"][1], n["out"][0] + 18, n["out"][1], color=INK, sw=1.6))
        sub.append(line(n["out"][0] + 18, n["out"][1], n["out"][0] + 18, fbY, color=INK, sw=1.6))
        if fb_elem == "R":
            sub.append(res(node[0], fbY, n["out"][0] + 18, fbY, label="R"))
        else:
            sub.append(cap(node[0], fbY, n["out"][0] + 18, fbY, label="C"))
        # вихід
        sub.append(line(n["out"][0] + 18, n["out"][1], ox + 290, n["out"][1], color=INK, sw=1.6))
        sub.append(arrow(ox + 270, n["out"][1], ox + 292, n["out"][1], color=col, sw=2.4))
        sub.append(text(ox + 150, oy + 78, title, size=14, color=col, bold=True))
        sub.append(text(ox + 150, oy + 96, formula, size=12, color=INK))
        return "".join(sub)

    # верх: R на вході, C у ЗЗ → інтегратор
    f.append(stage(40, 110, "ІНТЕГРАТОР", "R", "C", "V_вих = −(1/RC)·∫ V_вх dt", FIELD))
    # низ: C на вході, R у ЗЗ → диференціатор
    f.append(stage(40, 280, "ДИФЕРЕНЦІАТОР", "C", "R", "V_вих = −RC·dV_вх/dt", POS))

    # стрілка-натяк «переставили місцями»
    f.append(line(388, 150, 388, 246, color=MUTED, sw=1.4, dash="5 5"))
    bb, _, _ = textbox(520, 200, "та сама пара R і C —\nпереставлена місцями", size=11,
                       color=INK, fill=FILL, stroke=MUTED)
    f.append(bb)
    render(os.path.join(IMG, "swap.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. summing.svg — підсумовуючий інтегратор: кілька входів в один конденсатор
# ════════════════════════════════════════════════════════════════════════════
def fig_summing():
    W, H = 660, 320
    f = []
    s, n = opamp(430, 170, w=70, h=78)
    node = (n["in_m"][0] - 50, n["in_m"][1])

    ins = [(70, "V₁", "R₁"), (70, "V₂", "R₂"), (70, "V₃", "R₃")]
    ys = [110, 170, 230]
    for (x0, vlab, rlab), yy in zip(ins, ys):
        f.append(text(x0 - 8, yy + 4, vlab, size=13, color=NEG, bold=True, anchor="end"))
        f.append(res(x0, yy, node[0], yy, label=rlab))
        f.append(line(node[0], yy, node[0], n["in_m"][1], color=INK, sw=1.6))
    f.append(circle(node[0], n["in_m"][1], 2.6, fill=INK, stroke=INK))
    f.append(line(node[0], n["in_m"][1], n["in_m"][0], n["in_m"][1], color=INK, sw=1.6))
    f.append(text(node[0] - 4, n["in_m"][1] - 12, "сума струмів", size=11, color=FIELD, bold=True, anchor="middle"))

    # «+» на землю
    f.append(line(n["in_p"][0], n["in_p"][1], n["in_p"][0] - 16, n["in_p"][1], color=INK, sw=1.6))
    f.append(line(n["in_p"][0] - 16, n["in_p"][1], n["in_p"][0] - 16, n["in_p"][1] + 22, color=INK, sw=1.6))
    f.append(gnd(n["in_p"][0] - 16, n["in_p"][1] + 22))
    f.append(s)

    # конденсатор у ЗЗ
    fbY = 90
    f.append(line(node[0], n["in_m"][1], node[0], fbY, color=INK, sw=1.6))
    f.append(line(n["out"][0], n["out"][1], n["out"][0] + 20, n["out"][1], color=INK, sw=1.6))
    f.append(line(n["out"][0] + 20, n["out"][1], n["out"][0] + 20, fbY, color=INK, sw=1.6))
    f.append(cap(node[0], fbY, n["out"][0] + 20, fbY, label="C"))

    # вихід
    f.append(line(n["out"][0] + 20, n["out"][1], 600, n["out"][1], color=INK, sw=1.6))
    f.append(arrow(580, n["out"][1], 602, n["out"][1], color=FIELD, sw=2.6))
    f.append(text(600, n["out"][1] - 12, "V_вих", size=13, color=FIELD, bold=True, anchor="end"))

    bb, _, _ = textbox(W / 2, 290,
                       "V_вих = −(1/C)·∫ (V₁/R₁ + V₂/R₂ + V₃/R₃) dt   — інтегрує зважену суму входів",
                       size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(bb)
    render(os.path.join(IMG, "summing.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. solver.svg — петля інтеграторів розв'язує ẍ = −k·x (коливання)
# ════════════════════════════════════════════════════════════════════════════
def fig_solver():
    W, H = 700, 340
    f = []
    yb = 150

    f.append(text(W / 2, 34, "Машина, що сама розв'язує рівняння руху", size=15, bold=True))
    f.append(text(W / 2, 56, "ẍ = −k·x   (тягни назад пропорційно зміщенню — вийде синусоїда)", size=11, color=MUTED))

    # три блоки в ряд: ẍ → [∫] → ẋ → [∫] → x
    b1 = block(150, yb, 96, 64, "∫", "інтегруй", FIELD)
    b2 = block(420, yb, 96, 64, "∫", "інтегруй", FIELD)
    f.append(b1); f.append(b2)
    f.append(text(60, yb - 14, "ẍ", size=15, color=INK, bold=True))
    f.append(text(60, yb + 6, "приск.", size=10, color=MUTED))
    f.append(line(78, yb, 102, yb, color=INK, sw=1.8))
    f.append(arrow(96, yb, 102, yb, color=INK, sw=1.8))

    f.append(text(290, yb - 14, "ẋ", size=15, color=INK, bold=True))
    f.append(text(290, yb + 6, "швидк.", size=10, color=MUTED))
    f.append(line(198, yb, 372, yb, color=INK, sw=1.8))
    f.append(arrow(366, yb, 372, yb, color=INK, sw=1.8))

    f.append(text(560, yb - 14, "x", size=15, color=INK, bold=True))
    f.append(text(560, yb + 6, "зміщення", size=10, color=MUTED))
    f.append(line(468, yb, 600, yb, color=INK, sw=1.8))
    f.append(arrow(594, yb, 600, yb, color=INK, sw=1.8))

    # зворотний зв'язок: x помножене на −k повертається на вхід (ẍ)
    fbY = yb + 110
    f.append(circle(600, yb, 2.6, fill=INK, stroke=INK))
    f.append(line(600, yb, 600, fbY, color=POS, sw=2.0))
    f.append(block(420, fbY, 120, 50, "× (−k)", "", POS))
    f.append(line(600, fbY, 480, fbY, color=POS, sw=2.0))
    f.append(line(360, fbY, 60, fbY, color=POS, sw=2.0))
    f.append(line(60, fbY, 60, yb + 14, color=POS, sw=2.0))
    f.append(arrow(60, yb + 20, 60, yb + 14, color=POS, sw=2.0))
    f.append(text(230, fbY - 10, "поверни −k·x назад на вхід", size=11, color=POS, bold=True))

    # маленька синусоїда-результат
    sx, sy, sw_, sh = 470, 250, 150, 36
    pts = []
    for i in range(0, 151, 3):
        t = i / 150.0
        px = sx + t * sw_
        py = sy - math.sin(t * 2 * math.pi * 1.4) * sh / 2
        pts.append((px, py))
    f.append('<path d="M ' + " L ".join("%.1f %.1f" % p for p in pts) + '" fill="none" stroke="%s" stroke-width="2"/>' % FIELD)
    f.append(text(545, sy + 36, "x(t) — синусоїда", size=10, color=FIELD, anchor="middle"))
    render(os.path.join(IMG, "solver.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. wheel-disc.svg — механічний інтегратор: колесо на диску (Кельвін/Буш)
#    колесо на відстані y від осі за один оберт диска проходить шлях ∝ y —
#    сумуючи оберти, воно фізично рахує ∫ y dx
# ════════════════════════════════════════════════════════════════════════════
def fig_wheel_disc():
    W, H = 680, 360
    f = []
    f.append(text(W / 2, 30, "Механічний інтегратор: колесо на диску", size=15, bold=True))
    f.append(text(W / 2, 50, "де сидить колесо (y) — так швидко крутиться лічильник (∫ y dx)", size=11, color=MUTED))

    # ── диск, що обертається (вид згори) ──
    dcx, dcy, dR = 230, 210, 108
    f.append(circle(dcx, dcy, dR, fill="#eef2f6", stroke=INK, sw=2))
    f.append(circle(dcx, dcy, 3, fill=INK, stroke=INK))
    # напрям обертання диска
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (dcx - 40, dcy + dR + 14, 40, 40, dcx + 40, dcy + dR + 14, MUTED))
    f.append(text(dcx, dcy + dR + 38, "диск крутиться рівномірно (це вхід x)", size=10, color=MUTED))
    f.append(text(dcx, dcy - dR - 12, "ДИСК", size=11, color=INK, bold=True))

    # колесо-«ролик», що стоїть на радіусі y від центра
    y_off = 62
    wx = dcx + y_off
    f.append(line(dcx, dcy, wx, dcy, color=FIELD, sw=1.6, dash="4 4"))
    f.append(text(dcx + y_off / 2, dcy - 8, "y", size=13, color=FIELD, bold=True))
    # колесо (маленький кружок-ребро) + вісь
    f.append('<ellipse cx="%.1f" cy="%.1f" rx="7" ry="20" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (wx, dcy, POS))
    f.append(line(wx, dcy - 20, wx + 70, dcy - 20, color=INK, sw=1.6))   # вісь колеса до лічильника
    f.append(text(wx, dcy + 40, "колесо", size=10, color=POS, bold=True))

    # ── права частина: що це рахує ──
    lx = wx + 78
    f.append(circle(lx + 20, dcy - 20, 22, fill="#fff", stroke=INK, sw=1.8))
    f.append(circle(lx + 20, dcy - 20, 3, fill=INK, stroke=INK))
    f.append(arrow(lx + 20 - 10, dcy - 20 - 16, lx + 20 + 12, dcy - 20 - 12, color=INK, sw=1.6))
    f.append(text(lx + 20, dcy + 14, "лічильник", size=10, color=INK))
    f.append(text(lx + 20, dcy + 28, "обертів", size=10, color=INK))

    # пояснювальна рамка
    bb, _, _ = textbox(W / 2, 322,
                       "далеко від центра (велике y) — колесо мчить швидко; біля центра (мале y) — ледь повзе;\n"
                       "рухай колесо по радіусу за законом y(x) — і лічильник сам набирає ∫ y dx",
                       size=11, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(bb)
    render(os.path.join(IMG, "wheel-disc.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. lineage.svg — естафета від механіки до електроніки: інтегратор дозріває
# ════════════════════════════════════════════════════════════════════════════
def fig_lineage():
    W, H = 700, 470
    f = []
    f.append(text(W / 2, 30, "Естафета інтегратора: пів століття до першого ОП", size=15, bold=True))

    # вертикальна вісь-час
    ax = 150
    f.append(line(ax, 60, ax, 430, color=MUTED, sw=2))

    rows = [
        ("1876", "колесо на диску", "Джеймс Томсон описав механічний інтегратор", INK),
        ("1880-ті", "ідея є, сили нема", "Кельвін хоче з'єднати інтегратори — та їхній вихід заслабкий", MUTED),
        ("1925", "підсилювач моменту", "Німен дає інтеграторам силу крутити наступний", FIELD),
        ("1931", "диференціальний аналізатор", "Буш (MIT): шість колес-на-диску розв'язують рівняння", INK),
        ("1941", "уже без шестерень", "Гельцер (V-2) і M9 (Bell): інтегратор став електронним", POS),
        ("1947", "здобув ім'я", "Раґаззіні, Рендолл, Расселл: «операційний підсилювач»", NEG),
        ("1953", "у продажу", "Філбрик K2-W: ОП-цеглинка за 22 долари", FIELD),
    ]
    y = 78
    dy = (430 - 78) / (len(rows) - 1)
    for (yr, head, sub, col) in rows:
        f.append(circle(ax, y, 6, fill=col, stroke=col))
        f.append(text(ax - 16, y + 4, yr, size=12, color=INK, bold=True, anchor="end"))
        f.append(text(ax + 18, y - 3, head, size=12.5, color=col, bold=True, anchor="start"))
        f.append(text(ax + 18, y + 14, sub, size=10.5, color=MUTED, anchor="start"))
        y += dy

    # смуга-межа: механіка (до Буша) / електроніка (від Гельцера) — між 1931 і 1941
    ymid = 78 + 3.5 * dy
    f.append(line(ax - 74, ymid, ax + 500, ymid, color=POS, sw=1.2, dash="6 5"))
    f.append(text(ax + 486, ymid - 12, "механіка", size=10, color=MUTED, anchor="end", italic=True))
    f.append(text(ax + 486, ymid + 20, "електроніка", size=10, color=POS, anchor="end", italic=True))
    render(os.path.join(IMG, "lineage.svg"), W, H, *f)


if __name__ == "__main__":
    fig_ops()
    fig_swap()
    fig_summing()
    fig_solver()
    fig_wheel_disc()
    fig_lineage()
    print("OK: 6 фігур у", IMG)
