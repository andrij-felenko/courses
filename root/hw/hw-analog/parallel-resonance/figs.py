# -*- coding: utf-8 -*-
"""Фігури до статті «Паралельний резонанс» (book/electronics/analog/parallel-resonance).
Чотири фігури:
  tank.svg     — ідея «бака»: струм циркулює всередині L↔C, із джерела майже не береться
  zpeak.svg    — повний опір від частоти: ГОСТРИЙ ПІК на f₀ (дзеркало провалу послідовного)
  currents.svg — фазори: струми гілок рівні й протифазні, у Q разів більші за струм джерела
  rdyn.svg     — реальний бак (R у гілці котушки) і динамічний опір R_D = L/(C·R) = Q²·R
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


# ── Локальні символи схем ───────────────────────────────────────────────────
def cap(cx, cy, label=None, horiz=False):
    """Конденсатор — дві паралельні пластини. Повертає (svg, top, bot) або (svg, left, right)."""
    out = []
    if not horiz:
        out.append(line(cx - 14, cy - 4, cx + 14, cy - 4, color=INK, sw=2.6))
        out.append(line(cx - 14, cy + 4, cx + 14, cy + 4, color=INK, sw=2.6))
        a, b = (cx, cy - 4 - 14), (cx, cy + 4 + 14)
        out.append(line(cx, cy - 4, a[0], a[1], color=INK, sw=1.6))
        out.append(line(cx, cy + 4, b[0], b[1], color=INK, sw=1.6))
        if label:
            out.append(text(cx + 22, cy + 4, label, size=13, color=INK, bold=True, anchor="start"))
        return "".join(out), a, b
    else:
        out.append(line(cx - 4, cy - 14, cx - 4, cy + 14, color=INK, sw=2.6))
        out.append(line(cx + 4, cy - 14, cx + 4, cy + 14, color=INK, sw=2.6))
        a, b = (cx - 4 - 14, cy), (cx + 4 + 14, cy)
        out.append(line(cx - 4, cy, a[0], a[1], color=INK, sw=1.6))
        out.append(line(cx + 4, cy, b[0], b[1], color=INK, sw=1.6))
        if label:
            out.append(text(cx, cy - 22, label, size=13, color=INK, bold=True, anchor="middle"))
        return "".join(out), a, b


def coil(cx, cy, label=None, n=4, r=8):
    """Котушка — ряд напівдуг по вертикалі. Повертає (svg, top, bot)."""
    out = []
    span = n * 2 * r
    y0 = cy - span / 2
    out.append(line(cx, y0 - 14, cx, y0, color=INK, sw=1.6))
    path = 'M %.1f %.1f ' % (cx, y0)
    yy = y0
    for i in range(n):
        path += 'A %d %d 0 0 1 %.1f %.1f ' % (r, r, cx, yy + 2 * r)
        yy += 2 * r
    out.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (path, INK))
    out.append(line(cx, y0 + span, cx, y0 + span + 14, color=INK, sw=1.6))
    if label:
        out.append(text(cx + 18, cy + 4, label, size=13, color=INK, bold=True, anchor="start"))
    return "".join(out), (cx, y0 - 14), (cx, y0 + span + 14)


def resistor_h(x0, x1, y, label=None, col=INK):
    """Горизонтальний резистор-зигзаг між (x0,y) і (x1,y)."""
    out = []
    n = 6
    seg = (x1 - x0) / (n + 1)
    amp = 6
    out.append(line(x0, y, x0 + seg, y, color=col, sw=1.6))
    xx = x0 + seg
    for i in range(n):
        ny = y + (amp if i % 2 == 0 else -amp)
        out.append(line(xx, y if i == 0 else (y - amp if i % 2 == 1 else y + amp),
                        xx + seg, ny, color=col, sw=1.6))
        xx += seg
    out.append(line(xx, y + (amp if (n - 1) % 2 == 0 else -amp), x1, y, color=col, sw=1.6))
    if label:
        out.append(text((x0 + x1) / 2, y - 12, label, size=12, color=col, bold=True, anchor="middle"))
    return "".join(out)


def src_ac(cx, cy, label=None):
    """Джерело змінного струму: кружечок із синусоїдою."""
    r = 16
    out = [circle(cx, cy, r, fill="#ffffff", stroke=INK, sw=1.8)]
    out.append('<path d="M %.1f %.1f Q %.1f %.1f %.1f %.1f T %.1f %.1f" fill="none" stroke="%s" stroke-width="1.8"/>'
               % (cx - 9, cy, cx - 4.5, cy - 7, cx, cy, cx + 9, cy, INK))
    if label:
        out.append(text(cx - r - 6, cy + 4, label, size=12, color=INK, bold=True, anchor="end"))
    return "".join(out), (cx, cy - r), (cx, cy + r)


def arc_arrow(cx, cy, r, a0, a1, color=INK, sw=2.4):
    """Дуга-стрілка (для циркулюючого струму)."""
    x0 = cx + r * math.cos(math.radians(a0)); y0 = cy + r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1)); y1 = cy + r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 %d %d %.1f %.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arrow)"/>' % (x0, y0, r, r, large, sweep, x1, y1, color, sw))


# ════════════════════════════════════════════════════════════════════════════
# 1. tank.svg — ідея «бака»: великий струм гойдається в петлі L↔C, ззовні майже нуль
# ════════════════════════════════════════════════════════════════════════════
def fig_tank():
    W, H = 660, 360
    f = []
    # джерело ліворуч
    src, st, sb = src_ac(90, 180, label=None)
    f.append(src)
    f.append(text(90, 150, "джерело", size=11, color=MUTED))
    f.append(text(90, 232, "на f₀", size=11, color=MUTED))

    # контур: верхня й нижня шини
    topy, boty = 110, 250
    lx, rx = 90, 470          # ліва (джерело) і права межі петлі
    cx_c, cx_l = 330, 430     # позиції C і L у петлі
    f.append(line(lx, st[1], lx, topy, color=INK, sw=1.8))
    f.append(line(lx, sb[1], lx, boty, color=INK, sw=1.8))
    f.append(line(lx, topy, rx, topy, color=INK, sw=1.8))
    f.append(line(lx, boty, rx, boty, color=INK, sw=1.8))
    f.append(line(rx, topy, rx, boty, color=INK, sw=1.8))

    # C і L паралельно (вертикальні гілки між шинами)
    sc, _, _ = cap(cx_c, 180, label="C")
    f.append(line(cx_c, topy, cx_c, 180 - 18, color=INK, sw=1.8))
    f.append(line(cx_c, 180 + 18, cx_c, boty, color=INK, sw=1.8))
    f.append(sc)
    sl, _, _ = coil(cx_l, 180, label="L")
    f.append(line(cx_l, topy, cx_l, 180 - 32, color=INK, sw=1.8))
    f.append(line(cx_l, 180 + 32, cx_l, boty, color=INK, sw=1.8))
    f.append(sl)

    # циркулюючий струм — велика дуга-петля всередині між C і L
    f.append(arc_arrow(380, 180, 70, -60, 60, color=FIELD, sw=3))
    f.append(arc_arrow(380, 180, 70, 120, 240, color=FIELD, sw=3))
    f.append(text(380, 180, "I_цирк", size=13, color=FIELD, bold=True))
    f.append(text(380, 198, "= Q·I", size=11, color=FIELD))

    # струм із джерела — крихітна стрілка
    f.append(arrow(140, topy, 200, topy, color=POS, sw=2.2))
    f.append(text(170, topy - 8, "I (мало)", size=11, color=POS, bold=True, anchor="middle"))

    # винесений підпис
    body, w0, h0 = textbox(W / 2, 322,
                           "Енергія гойдається в петлі L↔C сама; джерело лише поповнює втрати —\nтож контур виглядає для нього як величезний опір (майже розрив)",
                           size=12, color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(body)
    render(os.path.join(IMG, "tank.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 2. zpeak.svg — повний опір від частоти: гострий ПІК на f₀
# ════════════════════════════════════════════════════════════════════════════
def fig_zpeak():
    W, H = 620, 380
    f = []
    ox, oy = 80, 300
    axw, axh = 470, 250
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.8))
    f.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.8))
    f.append(text(ox + axw - 4, oy + 24, "частота f", size=12, color=INK, anchor="end"))
    f.append(text(ox - 10, oy - axh + 8, "|Z|", size=13, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 10, oy - axh + 26, "повний", size=10, color=MUTED, anchor="end"))
    f.append(text(ox - 10, oy - axh + 40, "опір", size=10, color=MUTED, anchor="end"))

    # крива піка: низько по краях, гострий максимум на f0
    f0x = ox + axw * 0.5
    pts = []
    for i in range(0, 201):
        fr = i / 200.0
        x = ox + axw * fr
        # лоренціан, центр 0.5
        d = (fr - 0.5) * 14
        amp = 1.0 / (1.0 + d * d)
        y = oy - 6 - (axh - 40) * amp
        pts.append("%.1f %.1f" % (x, y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (" ".join(pts), POS))

    # пік
    ypk = oy - 6 - (axh - 40)
    f.append(line(f0x, oy, f0x, ypk, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(f0x, oy + 20, "f₀", size=13, color=INK, bold=True))
    f.append(circle(f0x, ypk, 4, fill=POS, stroke=POS))
    f.append(text(f0x + 12, ypk + 4, "максимум опору  Z = R_D", size=12, color=POS, bold=True, anchor="start"))

    # «нижче — ємнісне, вище — індуктивне»
    f.append(text(ox + axw * 0.22, oy - 30, "нижче f₀:", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox + axw * 0.22, oy - 16, "переважає L", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox + axw * 0.80, oy - 30, "вище f₀:", size=11, color=MUTED, anchor="middle"))
    f.append(text(ox + axw * 0.80, oy - 16, "переважає C", size=11, color=MUTED, anchor="middle"))

    f.append(text(W / 2, 350, "Паралельний контур: опір ГОСТРО зростає на f₀ — точне дзеркало провалу послідовного",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "zpeak.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 3. currents.svg — фазори: I_C і I_L рівні, протифазні, у Q разів більші за I
# ════════════════════════════════════════════════════════════════════════════
def fig_currents():
    W, H = 620, 360
    f = []
    cx, cy = 250, 185
    # осі-хрест
    f.append(line(cx - 150, cy, cx + 150, cy, color="#d7dadf", sw=1.2))
    f.append(line(cx, cy - 150, cx, cy + 140, color="#d7dadf", sw=1.2))

    # I_C — вгору (випереджає), I_L — вниз (відстає): рівні й протифазні
    f.append(arrow(cx, cy, cx, cy - 130, color=NEG, sw=3))
    f.append(text(cx + 12, cy - 120, "I_C", size=14, color=NEG, bold=True, anchor="start"))
    f.append(text(cx + 12, cy - 104, "(випереджає)", size=10, color=MUTED, anchor="start"))
    f.append(arrow(cx, cy, cx, cy + 122, color=POS, sw=3))
    f.append(text(cx + 12, cy + 116, "I_L", size=14, color=POS, bold=True, anchor="start"))
    f.append(text(cx + 12, cy + 132, "(відстає)", size=10, color=MUTED, anchor="start"))

    # струм джерела — крихітна стрілка вправо (синфазна з напругою)
    f.append(arrow(cx, cy, cx + 34, cy, color=FIELD, sw=3))
    f.append(text(cx + 40, cy - 8, "I", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(cx + 40, cy + 10, "(дрібна, у фазі)", size=10, color=MUTED, anchor="start"))

    # підпис рівності
    body, w0, h0 = textbox(490, 120,
                           "I_C = I_L\nі протифазні →\nсума майже нуль", size=12, color=INK,
                           fill="#f4f6f8", stroke=LINE)
    f.append(body)
    body, w0, h0 = textbox(490, 250,
                           "кожен у Q разів\nбільший за струм\nджерела I", size=12, color=INK,
                           fill="#eef7f0", stroke=FIELD)
    f.append(body)

    f.append(text(W / 2, 338, "Великі рівні протифазні струми гілок гасяться в зовнішньому колі — лишається крихітний I",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "currents.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 4. rdyn.svg — реальний бак (R у гілці L) і динамічний опір R_D = L/(C·R)
# ════════════════════════════════════════════════════════════════════════════
def fig_rdyn():
    W, H = 660, 360
    f = []
    topy, boty = 90, 250
    lx, rx = 110, 470
    cx_c, cx_l = 300, 430

    # шини
    f.append(line(lx, topy, rx, topy, color=INK, sw=1.8))
    f.append(line(lx, boty, rx, boty, color=INK, sw=1.8))
    f.append(line(rx, topy, rx, boty, color=INK, sw=1.8))
    f.append(line(lx, topy, lx, boty, color=INK, sw=1.8))

    # ємнісна гілка (ідеальна)
    sc, _, _ = cap(cx_c, 170, label="C")
    f.append(line(cx_c, topy, cx_c, 170 - 18, color=INK, sw=1.8))
    f.append(line(cx_c, 170 + 18, cx_c, boty, color=INK, sw=1.8))
    f.append(sc)

    # індуктивна гілка: котушка L + послідовний R (втрати обмотки)
    sl, ltop, lbot = coil(cx_l, 150, label="L")
    f.append(line(cx_l, topy, ltop[0], ltop[1], color=INK, sw=1.8))
    f.append(sl)
    # резистор від низу котушки до нижньої шини
    f.append(line(cx_l, lbot[1], cx_l, lbot[1] + 6, color=INK, sw=1.8))
    f.append(resistor_h(cx_l - 0, cx_l - 0, 0, None))  # placeholder (не малюємо горизонтальний)
    # вертикальний R: намалюємо зигзагом
    ry0, ry1 = lbot[1] + 6, boty
    n = 6; seg = (ry1 - ry0) / (n + 1); amp = 6
    f.append(line(cx_l, ry0, cx_l, ry0 + seg, color=POS, sw=1.6))
    yy = ry0 + seg
    for i in range(n):
        nx = cx_l + (amp if i % 2 == 0 else -amp)
        f.append(line(cx_l if i == 0 else (cx_l - amp if i % 2 == 1 else cx_l + amp),
                      yy, nx, yy + seg, color=POS, sw=1.6))
        yy += seg
    f.append(line(cx_l + (amp if (n - 1) % 2 == 0 else -amp), yy, cx_l, yy + seg, color=POS, sw=1.6))
    f.append(line(cx_l, yy + seg, cx_l, ry1, color=POS, sw=1.6))
    f.append(text(cx_l + 18, (ry0 + ry1) / 2, "R", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(cx_l + 18, (ry0 + ry1) / 2 + 16, "втрати", size=10, color=MUTED, anchor="start"))

    # стрілка «що бачить джерело»
    f.append(arrow(lx - 50, 170, lx - 4, 170, color=INK, sw=2.0))
    f.append(text(lx - 54, 150, "джерело", size=11, color=MUTED, anchor="middle"))
    f.append(text(lx - 54, 196, "бачить", size=11, color=MUTED, anchor="middle"))

    # формула динамічного опору
    body, w0, h0 = textbox(W / 2, 312,
                           "На f₀ контур = чистий опір R_D = L /(C·R) = Q²·R  —  тим більший, чим МЕНШІ втрати R",
                           size=13, color=INK, bold=False, fill="#fdecea", stroke=POS)
    f.append(body)
    render(os.path.join(IMG, "rdyn.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 5. susceptance.svg (math) — сприйнятливості гілок B_C і B_L vs частота;
#    їхня сума перетинає нуль ТРОХИ нижче f_ідеал → звідки зсув −R²/L²
# ════════════════════════════════════════════════════════════════════════════
def fig_susceptance():
    W, H = 660, 400
    f = []
    ox, oy = 90, 210            # початок осей (нуль по B — посередині)
    axw = 470
    half = 150                  # піврозмах по вертикалі
    # осі
    f.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.6))               # вісь частоти (B=0)
    f.append(arrow(ox + axw - 16, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(line(ox, oy - half, ox, oy + half, color=INK, sw=1.6))
    f.append(arrow(ox, oy - half + 14, ox, oy - half - 2, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 22, "частота", size=12, color=INK, anchor="end"))
    f.append(text(ox - 8, oy - half - 6, "B", size=14, color=INK, bold=True, anchor="end"))
    f.append(text(ox - 8, oy - half + 12, "сприйнятливість", size=10, color=MUTED, anchor="end"))
    f.append(text(ox + 6, oy - half + 12, "+ (ємнісна)", size=10, color=NEG, anchor="start"))
    f.append(text(ox + 6, oy + half - 4, "− (індуктивна)", size=10, color=POS, anchor="start"))

    # фізичні криві: B_C = +wC ;  B_L = -wL/(R^2+w^2 L^2)  (через гілку R+jwL)
    L = 100e-6; C = 250e-12; R = 320.0    # помітна R, щоб зсув було видно
    w_id = 1.0 / math.sqrt(L * C)
    wmin, wmax = w_id * 0.25, w_id * 1.75
    def X(w): return (w - wmin) / (wmax - wmin) * axw + ox
    # масштаб по B: нормуємо на максимум |B_C| у вікні
    Bc_max = wmax * C
    sc = (half - 18) / Bc_max
    def Yb(B): return oy - B * sc
    bc_pts, bl_pts, bsum_pts = [], [], []
    for i in range(0, 241):
        w = wmin + (wmax - wmin) * i / 240.0
        Bc = w * C
        Bl = -(w * L) / (R * R + (w * L) ** 2)
        bc_pts.append("%.1f %.1f" % (X(w), Yb(Bc)))
        bl_pts.append("%.1f %.1f" % (X(w), Yb(Bl)))
        bsum_pts.append("%.1f %.1f" % (X(w), Yb(Bc + Bl)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(bc_pts), NEG))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(bl_pts), POS))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="3.0"/>' % (" ".join(bsum_pts), FIELD))
    f.append(text(X(wmax) - 6, Yb(wmax * C) + 2, "B_C = ωC", size=12, color=NEG, bold=True, anchor="end"))
    f.append(text(X(wmax) - 6, Yb(-(wmax*L)/(R*R+(wmax*L)**2)) + 14, "B_L", size=12, color=POS, bold=True, anchor="end"))

    # ідеальна f₀ (де |B_C|=|B_L| без R) і реальна (де СУМА=0)
    w_real = math.sqrt(1.0/(L*C) - (R*R)/(L*L))
    f.append(line(X(w_id), oy - half + 20, X(w_id), oy + half - 20, color=MUTED, sw=1.2, dash="5 5"))
    f.append(text(X(w_id), oy + half - 4, "1/(2π√LC)", size=11, color=MUTED, anchor="middle"))
    # точка перетину суми з нулем
    f.append(circle(X(w_real), oy, 5, fill=FIELD, stroke=INK, sw=1.5))
    f.append(line(X(w_real), oy - 70, X(w_real), oy, color=FIELD, sw=1.2, dash="4 4"))
    bd, _, _ = textbox(X(w_real) - 4, oy - 90, "B_C + B_L = 0\nсправжня f₀", size=11,
                       color=INK, fill="#eef7f0", stroke=FIELD)
    f.append(bd)
    # стрілка зсуву
    f.append(arrow(X(w_id) - 2, oy + 44, X(w_real) + 2, oy + 44, color=INK, sw=1.6))
    f.append(text((X(w_id) + X(w_real)) / 2, oy + 60, "зсув униз", size=10, color=INK, anchor="middle"))

    f.append(text(W / 2, H - 14,
                  "Резонанс — там, де СУМА сприйнятливостей нуль; через R індуктивна крива «провисає», і нуль сповзає нижче 1/(2π√LC)",
                  size=11, italic=True, color=MUTED))
    render(os.path.join(IMG, "susceptance.svg"), W, H, *f)


# ════════════════════════════════════════════════════════════════════════════
# 6. ytriangle.svg (math) — фазор адмітансу Y = G + jB:
#    поза резонансом нахилений (є B), на f₀ лягає на вісь G → |Y| мінімум, |Z| макс
# ════════════════════════════════════════════════════════════════════════════
def fig_ytriangle():
    W, H = 660, 360
    f = []
    ox, oy = 110, 250           # початок (вузол Y-площини)
    axw, axh = 430, 200
    # осі G (вправо) та jB (вгору/вниз)
    f.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    f.append(arrow(ox, oy + 70, ox, oy - axh, color=INK, sw=1.6))
    f.append(text(ox + axw, oy + 22, "G  (провідність)", size=12, color=INK, anchor="end"))
    f.append(text(ox + 6, oy - axh + 14, "jB", size=13, color=INK, bold=True, anchor="start"))
    f.append(text(ox + 6, oy - axh + 30, "сприйнятливість", size=10, color=MUTED, anchor="start"))

    # спільна горизонталь: реальна частина G одна й та сама на всіх трьох частотах
    Gx = ox + axw * 0.62
    f.append(line(ox, oy, Gx, oy, color="#cfd3d8", sw=1.0, dash="3 3"))

    # три фазори Y: нижче f₀ (B<0), на f₀ (B=0), вище f₀ (B>0)
    # на f₀: чисто по осі G — найкоротший
    f.append(arrow(ox, oy, Gx, oy, color=FIELD, sw=3.2))
    f.append(text(Gx + 8, oy + 4, "Y = G  (на f₀)", size=12, color=FIELD, bold=True, anchor="start"))
    # нижче f₀: B<0 (індуктивне переважає) — стрілка вниз-вправо
    f.append(arrow(ox, oy, Gx, oy + 70, color=POS, sw=2.4))
    f.append(line(Gx, oy, Gx, oy + 70, color=POS, sw=1.0, dash="3 3"))
    f.append(text(Gx + 8, oy + 70, "нижче f₀", size=11, color=POS, anchor="start"))
    # вище f₀: B>0 (ємнісне) — стрілка вгору-вправо
    f.append(arrow(ox, oy, Gx, oy - 90, color=NEG, sw=2.4))
    f.append(line(Gx, oy, Gx, oy - 90, color=NEG, sw=1.0, dash="3 3"))
    f.append(text(Gx + 8, oy - 90, "вище f₀", size=11, color=NEG, anchor="start"))

    # підпис під віссю G
    f.append(text(Gx, oy + 96, "G = R/(R²+X²) ≈ R/X² = 1/R_D", size=12, color=INK, bold=True, anchor="middle"))

    # пояснювальна рамка
    bd, _, _ = textbox(ox + 150, oy - axh + 40,
                       "Поза f₀ є сприйнятливість B → |Y| більший → опір менший.\n"
                       "На f₀ сприйнятливість гілок гаситься, лишається сама G:\n"
                       "|Y| найменший → |Z| = 1/G найбільший = R_D.",
                       size=11, color=INK, fill=FILL, stroke=LINE)
    f.append(bd)

    f.append(text(W / 2, H - 14,
                  "Резонанс очима адмітансу: фазор Y лягає на вісь провідності — найкоротший Y, отже найвищий опір",
                  size=11, italic=True, color=MUTED))
    render(os.path.join(IMG, "ytriangle.svg"), W, H, *f)


# ── Фігура до вставки hist-tank-circuit ──────────────────────────────────────
def fig_hist_timeline():
    """Шлях контуру: від іскри в банці Лейдена до ручки налаштування й назви «бак»."""
    W, H = 900, 360
    f = []
    f.append(text(W / 2, 28, "Контур-бак: від лабораторної іскри до ручки налаштування",
                  size=17, bold=True))

    # вісь часу
    ax_y = 150
    x0, x1 = 70, W - 50
    f.append(line(x0, ax_y, x1, ax_y, color=INK, sw=2.2))
    f.append(arrow(x1 - 2, ax_y, x1 + 14, ax_y, color=INK, sw=2.2))

    # віхи: (рік, верх/низ, два рядки підпису)
    events = [
        (1826, "Савари: іскра з\nбанці гойдається", True),
        (1853, "Кельвін: формула\nколивань", False),
        (1888, "Герц: перший\nрезонатор", True),
        (1897, "Лодж: «синтонія»\n(налаштування)", False),
        (1900, "Марконі 7777:\n4 контури", True),
        (1920, "лампи → у книжках\nназва «tank»", False),
    ]
    n = len(events)
    for i, (yr, lbl, up) in enumerate(events):
        x = x0 + (x1 - x0 - 30) * i / (n - 1) + 16
        f.append(circle(x, ax_y, 6, fill=FIELD, stroke=INK, sw=1.8))
        f.append(text(x, ax_y + (-18 if up else 26), str(yr), size=13, bold=True, color=INK))
        # картка-підпис над/під віссю
        bw, bh = 138, 40
        by = ax_y - 18 - 14 - bh if up else ax_y + 26 + 8
        f.append(line(x, ax_y, x, by + (bh if up else 0), color=MUTED, sw=1.2, dash="3 3"))
        f.append(fitbox(x - bw / 2, by, bw, bh, lbl, size=12,
                        fill="#fff7e6" if up else FILL, stroke=MUTED))

    # підпис-висновок
    f.append(text(W / 2, H - 18,
                  "Та сама петля L↔C: спершу диво в лабораторії, далі — серце передавача, тоді — гучна назва",
                  size=12, italic=True, color=MUTED))
    render(os.path.join(IMG, "timeline.svg"), W, H, *f)


if __name__ == "__main__":
    fig_tank()
    fig_zpeak()
    fig_currents()
    fig_rdyn()
    fig_susceptance()
    fig_ytriangle()
    fig_hist_timeline()
    print("OK: 7 фігур у", IMG)
