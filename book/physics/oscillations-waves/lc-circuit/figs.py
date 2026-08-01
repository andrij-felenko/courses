# -*- coding: utf-8 -*-
"""Фігури до теми «LC-контур».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут).

Кольорова домовленість цих фігур:
  зелений (FIELD) — електричне: конденсатор, заряд, електрична енергія;
  червоний (POS)  — магнітне:  котушка, струм, магнітна енергія."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

ELEC = FIELD   # електричний бік (конденсатор)
MAG  = POS     # магнітний бік (котушка)


# ── деталі схеми ────────────────────────────────────────────────────────────
def coil_v(x, y1, y2, humps=5, out=1):
    """Вертикальна котушка: humps півкіл уздовж x від y1 до y2."""
    seg = (y2 - y1) / humps
    r = seg / 2
    sweep = 1 if out > 0 else 0
    d = "M %.1f %.1f" % (x, y1)
    y = y1
    for _ in range(humps):
        d += " A %.1f %.1f 0 0 %d %.1f %.1f" % (r, r, sweep, x, y + 2 * r)
        y += 2 * r
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (d, INK)


def zigzag_spring(x1, x2, y, coils=7, amp=12, lead=14):
    seg = (x2 - x1 - 2 * lead) / coils
    pts = [(x1, y), (x1 + lead, y)]
    for i in range(coils):
        pts.append((x1 + lead + seg * (i + 0.25), y - amp))
        pts.append((x1 + lead + seg * (i + 0.75), y + amp))
    pts.append((x2 - lead, y))
    pts.append((x2, y))
    d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK)


def wall(x, y1, y2, side=1):
    out = [line(x, y1, x, y2, color=INK, sw=3)]
    yy = y1 + 6
    while yy < y2:
        out.append(line(x, yy, x + 12 * side, yy - 12, color=MUTED, sw=1.3))
        yy += 14
    return "".join(out)


def ground(x1, x2, y):
    out = [line(x1, y, x2, y, color=INK, sw=3)]
    xx = x1 + 6
    while xx < x2:
        out.append(line(xx, y, xx - 12, y + 12, color=MUTED, sw=1.3))
        xx += 14
    return "".join(out)


def lc_cell(cx, top, bot, charge=0, cur=0):
    """LC-петля: конденсатор на лівому ребрі (дві горизонт. пластини), котушка — праворуч.
    charge: +1 (верхня пластина +), −1 (навпаки), 0 (розряджено).
    cur:   +1 (струм праворуч по низу), −1 (ліворуч), 0 (нема)."""
    x0, x1 = cx - 44, cx + 44
    ymid = (top + bot) / 2
    out = [line(x0, top, x1, top, color=INK, sw=2),
           line(x0, bot, x1, bot, color=INK, sw=2)]
    # конденсатор: дротини + дві пластини з проміжком
    out.append(line(x0, top, x0, ymid - 10, color=INK, sw=2))
    out.append(line(x0 - 15, ymid - 10, x0 + 15, ymid - 10, color=INK, sw=3.2))
    out.append(line(x0 - 15, ymid + 10, x0 + 15, ymid + 10, color=INK, sw=3.2))
    out.append(line(x0, ymid + 10, x0, bot, color=INK, sw=2))
    # котушка на правому ребрі
    out.append(coil_v(x1, top, bot, humps=5, out=1))
    # знаки заряду ліворуч від пластин
    if charge > 0:
        out.append(plus(x0 - 30, ymid - 10, 8)); out.append(minus(x0 - 30, ymid + 10, 8))
    elif charge < 0:
        out.append(minus(x0 - 30, ymid - 10, 8)); out.append(plus(x0 - 30, ymid + 10, 8))
    # струм — зелена/червона стрілка по нижньому дроту + буква I над ним
    if cur != 0:
        if cur > 0:
            out.append(arrow(cx - 22, bot, cx + 22, bot, color=MAG, sw=3))
        else:
            out.append(arrow(cx + 22, bot, cx - 22, bot, color=MAG, sw=3))
        out.append(text(cx, bot - 9, "I", size=14, italic=True, bold=True, color=MAG))
    return "".join(out)


def ebar(cx, top, h, frac, color, label):
    w = 24
    x = cx - w / 2
    out = [rect(x, top, w, h, fill="#eef1f4", stroke=MUTED, sw=1, rx=3)]
    if frac > 0.001:
        fh = h * frac
        out.append(rect(x, top + h - fh, w, fh, fill=color, stroke='none', sw=0, rx=3))
    out.append(text(cx, top + h + 16, label, size=12, bold=True, color=color))
    return "".join(out)


# ── Фігура 1: чотири фази коливання ─────────────────────────────────────────
def fig_cycle():
    W, H = 900, 476
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Коло «дзвенить»: енергія переливається між конденсатором і котушкою",
                  size=17, bold=True))
    f.append(text(W / 2, 51, "чотири моменти за один період T — заряд і струм по черзі проходять максимум",
                  size=12, color=MUTED))

    centers = [40 + 820 * (2 * i + 1) / 8 for i in range(4)]
    tlabels = ["t = 0", "t = T/4", "t = T/2", "t = 3·T/4"]
    charges = [+1, 0, -1, 0]
    currents = [0, +1, 0, -1]
    elec = [1, 0, 1, 0]
    states = ["заряд повний,\nструм нуль", "заряд нуль,\nструм максимум",
              "заряд повний\n(навпаки), струм нуль", "заряд нуль,\nструм максимум (назад)"]

    top, bot = 104, 196
    for i, cx in enumerate(centers):
        f.append(text(cx, 80, tlabels[i], size=14, bold=True))
        f.append(lc_cell(cx, top, bot, charge=charges[i], cur=currents[i]))
        f.append(mtext(cx, bot + 26, states[i], size=11.5, color=INK, lh=1.25))
        # смужки енергії під панеллю
        f.append(ebar(cx - 21, 300, 92, elec[i], ELEC, "поле C"))
        f.append(ebar(cx + 21, 300, 92, 1 - elec[i], MAG, "поле L"))

    # легенда
    ly = 450
    f.append(rect(228, ly - 12, 16, 16, fill=ELEC, stroke='none', sw=0, rx=3))
    f.append(text(252, ly + 1, "електричне поле конденсатора", size=12, anchor="start"))
    f.append(rect(560, ly - 12, 16, 16, fill=MAG, stroke='none', sw=0, rx=3))
    f.append(text(584, ly + 1, "магнітне поле котушки", size=12, anchor="start"))
    return render(os.path.join(IMG, "cycle.svg"), W, H, *f)


# ── Фігура 2: заряд/струм і обмін енергією в часі ───────────────────────────
def fig_energy():
    W, H = 900, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Заряд і струм зсунуті на чверть періоду; енергії гойдаються у протифазі",
                  size=16, bold=True))

    ox, rpx = 96, 812
    umax = 4 * math.pi          # два періоди
    N = 520

    def PXu(u):
        return ox + (rpx - ox) * (u / umax)

    # ── верхня панель: q(t), I(t) ──
    oy1, amp1 = 150, 62
    f.append(arrow(ox, oy1, rpx + 10, oy1, color=INK, sw=1.6))
    f.append(arrow(ox, oy1 + amp1 + 22, ox, oy1 - amp1 - 22, color=INK, sw=1.6))
    f.append(text(rpx + 8, oy1 + 22, "час t →", size=12, anchor="end"))

    def PY1(v):
        return oy1 - amp1 * v

    # чвертьперіодні вертикалі
    u = math.pi / 2
    while u < umax - 1e-6:
        f.append(line(PXu(u), oy1 - amp1 - 8, PXu(u), oy1 + amp1 + 8,
                      color="#e6e9ec", sw=1.0))
        u += math.pi / 2

    q_pts, i_pts = [], []
    for k in range(N + 1):
        u = umax * k / N
        q_pts.append((PXu(u), PY1(math.cos(u))))
        i_pts.append((PXu(u), PY1(-math.sin(u))))   # I ∝ −sin
    for pts, col in ((q_pts, ELEC), (i_pts, MAG)):
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, col))
    f.append(text(PXu(0.15), PY1(1) - 12, "заряд q ∝ cos", size=13, bold=True,
                  color=ELEC, anchor="start"))
    f.append(text(PXu(math.pi / 2 + 0.12), PY1(-1) + 20, "струм I ∝ −sin", size=13,
                  bold=True, color=MAG, anchor="start"))

    # ── нижня панель: енергії ──
    oy2, hgt = 428, 150
    f.append(arrow(ox, oy2, rpx + 10, oy2, color=INK, sw=1.6))
    f.append(arrow(ox, oy2 + 8, ox, oy2 - hgt - 24, color=INK, sw=1.6))
    f.append(text(rpx + 8, oy2 + 22, "час t →", size=12, anchor="end"))
    f.append(text(ox - 10, oy2 - hgt - 10, "енергія", size=12, anchor="end"))

    def PY2(e):
        return oy2 - hgt * e

    u = math.pi / 2
    while u < umax - 1e-6:
        f.append(line(PXu(u), oy2, PXu(u), oy2 - hgt - 6, color="#e6e9ec", sw=1.0))
        u += math.pi / 2

    # стала сума
    f.append(line(ox, PY2(1), rpx, PY2(1), color=INK, sw=1.6, dash="7,6"))
    f.append(text(rpx - 4, PY2(1) - 8, "сума стала", size=12, bold=True, anchor="end"))

    ue, um = [], []
    for k in range(N + 1):
        u = umax * k / N
        c = math.cos(u); s = math.sin(u)
        ue.append((PXu(u), PY2(c * c)))
        um.append((PXu(u), PY2(s * s)))
    for pts, col in ((ue, ELEC), (um, MAG)):
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (d, col))
    f.append(text(PXu(0.05), PY2(1) + 20, "електрична  q²/2C  ∝ cos²", size=12.5,
                  bold=True, color=ELEC, anchor="start"))
    f.append(text(PXu(math.pi / 2 + 0.05), PY2(1) - 34, "магнітна  L·I²/2  ∝ sin²",
                  size=12.5, bold=True, color=MAG, anchor="start"))
    return render(os.path.join(IMG, "energy.svg"), W, H, *f)


# ── Фігура 3: механічний осцилятор ↔ LC-контур ──────────────────────────────
def fig_analogy():
    W, H = 900, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Той самий осцилятор двома мовами: пружина з масою ↔ конденсатор із котушкою",
                  size=16, bold=True))

    # ── ліва панель: маса на пружині ──
    f.append(text(200, 66, "механіка", size=14, bold=True, color=INK))
    gy = 210
    f.append(wall(70, 108, gy))
    f.append(ground(70, 340, gy))
    mx, my, mw, mh = 250, 150, 66, 54
    f.append(zigzag_spring(70, mx, my))
    f.append(rect(mx, my - mh / 2, mw, mh, fill="#e8edf3", stroke=INK, sw=2, rx=6))
    f.append(text(mx + mw / 2, my + 9, "m", size=26, bold=True))
    f.append(text((70 + mx) / 2, my - 30, "пружина k", size=12, color=INK))
    f.append(text(mx + mw / 2, my + mh / 2 + 22, "маса m", size=12, color=INK))

    # велика стрілка відповідності
    f.append(text(W / 2, 150, "↔", size=44, bold=True, color=ELEC))

    # ── права панель: LC-контур ──
    f.append(text(700, 66, "електрика", size=14, bold=True, color=INK))
    f.append(lc_cell(700, 110, 208, charge=+1, cur=0))
    f.append(text(700 - 44 - 46, 159, "C", size=17, bold=True, color=ELEC, anchor="end"))
    f.append(text(700 + 44 + 30, 159, "L", size=17, bold=True, color=MAG, anchor="start"))
    f.append(text(700, 232, "конденсатор C · котушка L", size=12, color=INK))

    # ── таблиця відповідностей ──
    ty = 286
    f.append(line(150, ty - 20, 750, ty - 20, color="#e0e3e7", sw=1.2))
    f.append(text(330, ty - 26, "механіка", size=13, bold=True, anchor="end", color=MUTED))
    f.append(text(470, ty - 26, "електрика", size=13, bold=True, anchor="start", color=MUTED))
    rows = [
        ("зміщення  x", "заряд  q"),
        ("швидкість  v", "струм  I = dq/dt"),
        ("маса  m   (інерція)", "індуктивність  L"),
        ("жорсткість  k", "1 / C   (обернена ємність)"),
    ]
    for i, (a, b) in enumerate(rows):
        yy = ty + i * 34
        f.append(text(330, yy, a, size=14, anchor="end", color=INK))
        f.append(text(400, yy, "↔", size=16, bold=True, color=ELEC))
        f.append(text(470, yy, b, size=14, anchor="start", color=INK))
    yeq = ty + 4 * 34 + 8
    b, bw, bh = textbox(W / 2, yeq + 4,
                        "m·ẍ + k·x = 0     ↔     L·q̈ + q/C = 0",
                        size=14, pad=9, fill="#eafaf1", stroke=ELEC, sw=1.5, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "analogy.svg"), W, H, *f)


# ── фігури до історичної вставки ───────────────────────────────────────────
def _poly(pts, color, sw=2.5, dash=None):
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, color, sw, da))


def _needle(cx, cy, right=True, w=140, h=28):
    """Сталева голка з намагніченістю: стрілка від Пд до Пн."""
    x, y = cx - w / 2, cy - h / 2
    out = [rect(x, y, w, h, fill="#f4f6f8", stroke=INK, sw=1.8, rx=13)]
    lab_l, col_l = ("Пд", NEG) if right else ("Пн", POS)
    lab_r, col_r = ("Пн", POS) if right else ("Пд", NEG)
    out.append(text(x + 22, cy + 5, lab_l, size=14, bold=True, color=col_l))
    out.append(text(x + w - 22, cy + 5, lab_r, size=14, bold=True, color=col_r))
    if right:
        out.append(arrow(cx - 24, cy, cx + 26, cy, color=MUTED, sw=2.0))
    else:
        out.append(arrow(cx + 24, cy, cx - 26, cy, color=MUTED, sw=2.0))
    return "".join(out)


def fig_hist_needle():
    """Чому та сама схема лишала голку намагніченою то в один, то в інший бік."""
    W, H = 940, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Голка як детектор: полюс задає остання півхвиля, "
                             "що перевищила поріг", size=16, bold=True))

    x0, x1 = 100, 560          # поле графіка
    tmax, N = 4.5, 400         # у періодах
    tau = 1.522                # спад ≈0.72 за півперіод
    amp = 62
    thr = 0.35                 # поріг перемагнічення (частка від початкового)

    def PX(t):
        return x0 + (x1 - x0) * (t / tmax)

    def panel(base, A, head, cap, tag_label):
        g = []
        g.append(text(x0, base - amp - 16, head, size=13, bold=True, anchor="start"))
        g.append(arrow(x0 - 12, base, x1 + 18, base, color=INK, sw=1.5))
        for s in (+1, -1):
            g.append(line(x0 - 6, base - s * thr * amp, x1 + 6, base - s * thr * amp,
                          color=MUTED, sw=1.2, dash="6 5"))
        if tag_label:
            g.append(text(x1 + 18, base - thr * amp - 7, "поріг голки",
                          size=12, color=MUTED, anchor="start"))
        pts = []
        for k in range(N + 1):
            t = tmax * k / N
            v = A * math.exp(-t / tau) * math.sin(2 * math.pi * t)
            pts.append((PX(t), base - amp * v))
        g.append(_poly(pts, MAG, sw=2.6))

        last = None
        n = 0
        while True:
            t = 0.25 + 0.5 * n
            if t > tmax:
                break
            v = A * math.exp(-t / tau) * (1 if n % 2 == 0 else -1)
            if abs(v) >= thr:
                g.append(circle(PX(t), base - amp * v, 4.5, fill=MAG, stroke=MAG, sw=1))
                last = (t, v)
            n += 1

        lt, lv = last
        lx, ly = PX(lt), base - amp * lv
        g.append(circle(lx, ly, 9, fill="#eafaf1", stroke=ELEC, sw=2.6))
        cy = base + amp + 46
        g.append(line(lx, ly + (14 if lv < 0 else -14) * (-1 if lv < 0 else 1),
                      lx, cy - 14, color=ELEC, sw=1.3, dash="4 4"))
        g.append(text(lx, cy, cap, size=12, color=ELEC, bold=True))
        return "".join(g)

    baseA, baseB = 152, 344
    f.append(panel(baseA, 1.00, "сильніший розряд (більше банок)",
                   "остання сильна півхвиля — угору", True))
    f.append(panel(baseB, 0.62, "слабший розряд (менше банок)",
                   "остання сильна півхвиля — униз", False))

    # ── права колонка: результат на голці ──
    f.append(line(700, 70, 700, H - 40, color="#e6e9ec", sw=1.2))
    for base, right, cap in ((baseA, True, "намагнічена вправо"),
                             (baseB, False, "намагнічена вліво")):
        f.append(arrow(716, base, 752, base, color=INK, sw=1.8))
        f.append(_needle(838, base, right=right))
        f.append(text(838, base + 40, cap, size=12, color=INK))

    f.append(text(W / 2, H - 16,
                  "Схема та сама, полюс різний — саме ця «випадковість» і виказала, "
                  "що струм міняє напрям", size=12, color=MUTED))
    return render(os.path.join(IMG, "hist-needle.svg"), W, H, *f)


def fig_hist_regimes():
    """Дві долі розряду за Томсоном і межа між ними."""
    W, H = 940, 452
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Розв'язок 1853 року: чи дзвенить розряд — вирішує опір",
                  size=16, bold=True))

    x0, x1 = 100, 610
    base, amp = 196, 86
    tmax, N = 12.0, 500

    def PX(t):
        return x0 + (x1 - x0) * (t / tmax)

    f.append(line(x0 - 8, base, x1 + 14, base, color="#c8ccd2", sw=1.2, dash="5 5"))
    f.append(arrow(x0, base + amp + 26, x0, base - amp - 26, color=INK, sw=1.5))
    f.append(arrow(x0 - 10, base + amp + 26, x1 + 18, base + amp + 26, color=INK, sw=1.5))
    f.append(text(x0 - 10, base - amp - 32, "заряд q", size=12, anchor="start"))
    f.append(text(x1 + 14, base + amp + 44, "час", size=12, anchor="end"))

    def curve(kind, alpha, color, sw=2.6, dash=None):
        pts = []
        for k in range(N + 1):
            t = tmax * k / N
            if kind == "under":
                w = math.sqrt(1.0 - alpha * alpha)
                v = math.exp(-alpha * t) * (math.cos(w * t) + alpha / w * math.sin(w * t))
            elif kind == "crit":
                v = (1.0 + t) * math.exp(-t)
            else:
                s = math.sqrt(alpha * alpha - 1.0)
                v = math.exp(-alpha * t) * (math.cosh(s * t) + alpha / s * math.sinh(s * t))
            pts.append((PX(t), base - amp * v))
        return _poly(pts, color, sw=sw, dash=dash)

    f.append(curve("over", 2.5, NEG, sw=2.4))
    f.append(curve("crit", 1.0, MUTED, sw=2.2, dash="7 5"))
    f.append(curve("under", 0.15, MAG, sw=2.8))

    # ── легенда праворуч, три режими ──
    lx = 790
    rows = [(MAG,  ["R < 2·√(L/C)", "дзвенить"]),
            (MUTED, ["R = 2·√(L/C)", "рівно межа"]),
            (NEG,  ["R > 2·√(L/C)", "сповзає мовчки"])]
    ly = 116
    for col, lines in rows:
        b, bw, bh = textbox(lx, ly, lines, size=13, pad=12, fill="#fbfcfd",
                            stroke=col, sw=2.0, color=INK, min_w=190)
        f.append(b)
        f.append(line(lx - bw / 2 - 26, ly, lx - bw / 2 - 8, ly, color=col, sw=3.2))
        ly += 96

    # ── формула періоду ──
    b, bw, bh = textbox(355, 388, ["T = 2π / √( 1/(L·C) − R²/(4·L²) )",
                                   "при R → 0    T = 2π·√(L·C)"],
                        size=14, pad=12, fill="#eafaf1", stroke=ELEC, sw=1.6, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "hist-regimes.svg"), W, H, *f)


# ── фігури до математичної вставки ─────────────────────────────────────────
def _ellipse_svg(cx, cy, rx, ry, color=LINE, sw=2.5):
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"/>' % (cx, cy, rx, ry, color, sw))


def _arc_svg(x1, y1, x2, y2, r, color=LINE, sw=1.6, sweep=0, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="M %.1f %.1f A %.1f %.1f 0 0 %d %.1f %.1f" fill="none" '
            'stroke="%s" stroke-width="%.1f"%s/>' % (x1, y1, r, r, sweep, x2, y2, color, sw, da))


def fig_phase():
    """Фазова площина: еліпс збереження → одиничне коло → косинус як тінь."""
    W, H = 940, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Збереження енергії — це еліпс, а нормування осей робить рух рівномірним обертанням",
                  size=16, bold=True))
    f.append(text(W / 2, 52, "ліворуч — траєкторія контуру в осях (q, I); праворуч — вона ж у безрозмірних координатах",
                  size=12, color=MUTED))

    # ── ліва панель: еліпс у фізичних осях ──
    Lx, Ly, a, b = 250.0, 285.0, 120.0, 92.0
    f.append(arrow(108, Ly, 402, Ly, color=INK, sw=1.6))
    f.append(text(410, Ly + 5, "q", size=14, bold=True, italic=True, anchor="start"))
    f.append(arrow(Lx, 408, Lx, 162, color=INK, sw=1.6))
    f.append(text(Lx, 152, "I", size=14, bold=True, italic=True))
    f.append(_ellipse_svg(Lx, Ly, a, b, color=ELEC, sw=2.6))

    th = math.radians(52)
    px, py = Lx + a * math.cos(th), Ly - b * math.sin(th)
    tx, ty = -a * math.sin(th), -b * math.cos(th)
    tn = math.hypot(tx, ty)
    f.append(arrow(px, py, px + 34 * tx / tn, py + 34 * ty / tn, color=ELEC, sw=2.4))
    f.append(circle(px, py, 5.5, fill=ELEC, stroke=ELEC, sw=1))

    f.append(line(Lx + a, Ly, Lx + a, Ly + 37, color=MUTED, sw=1.2, dash="5,5"))
    f.append(text(Lx + a, Ly + 53, "q₀", size=13, color=MUTED))
    f.append(line(Lx, Ly - b, Lx - 45, Ly - b, color=MUTED, sw=1.2, dash="5,5"))
    f.append(text(Lx - 52, Ly - b + 5, "I₀", size=13, color=MUTED, anchor="end"))

    bx, _, _ = textbox(Lx, 448,
                       ["q²/(2C) + L·I²/2 = E",
                        "піввісі:  q₀ = √(2EC),   I₀ = √(2E/L)",
                        "I₀/q₀ = 1/√(L·C) = ω₀"],
                       size=13, pad=10, fill="#eafaf1", stroke=ELEC, sw=1.5)
    f.append(bx)

    # ── стрілка нормування ──
    f.append(mtext(477, 200, ["нормування", "u = q/q₀,   v = I/I₀"], size=12, color=MUTED))
    f.append(arrow(430, 250, 528, 250, color=INK, sw=2.0))

    # ── права панель: одиничне коло ──
    Rx, Ry, R = 700.0, 285.0, 105.0
    f.append(arrow(578, Ry, 838, Ry, color=INK, sw=1.6))
    f.append(text(846, Ry + 5, "u", size=14, bold=True, italic=True, anchor="start"))
    f.append(arrow(Rx, 408, Rx, 162, color=INK, sw=1.6))
    f.append(text(Rx, 152, "v", size=14, bold=True, italic=True))
    f.append(circle(Rx, Ry, R, fill="none", stroke=MAG, sw=2.6))

    qx, qy = Rx + R * math.cos(th), Ry - R * math.sin(th)
    f.append(line(Rx, Ry, qx, qy, color=INK, sw=2.0))
    f.append(circle(qx, qy, 5.5, fill=MAG, stroke=MAG, sw=1))
    f.append(_arc_svg(Rx + 40, Ry, Rx + 40 * math.cos(th), Ry - 40 * math.sin(th), 40,
                      color=INK, sw=1.6))
    f.append(text(750, 264, "θ", size=15, bold=True))
    f.append(text(719, 234, "1", size=13, bold=True))
    f.append(line(qx, qy, qx, Ry, color=MUTED, sw=1.3, dash="5,5"))
    f.append(text(qx, Ry + 21, "u = cos θ", size=12, color=MUTED))

    bx2, _, _ = textbox(Rx, 448,
                        ["u² + v² = 1,    θ = ω₀·t",
                         "кут росте рівномірно → тінь точки на вісь u є cos(ω₀·t)"],
                        size=13, pad=10, fill="#fdecea", stroke=MAG, sw=1.5)
    f.append(bx2)
    return render(os.path.join(IMG, "phase.svg"), W, H, *f)


def fig_ics():
    """Початкові умови як точка: амплітуда — відстань, фаза — кут."""
    W, H = 760, 430
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Початкові умови — точка на площині: амплітуда це відстань, фаза це кут",
                  size=15, bold=True))

    Ox, Oy = 200.0, 330.0
    Px, Py = 420.0, 210.0
    A = math.hypot(Px - Ox, Oy - Py)
    f.append(arrow(150, Oy, 620, Oy, color=INK, sw=1.6))
    f.append(text(628, Oy + 5, "q", size=14, bold=True, italic=True, anchor="start"))
    f.append(arrow(Ox, 372, Ox, 68, color=INK, sw=1.6))
    f.append(text(Ox, 58, "I / ω₀", size=13))

    f.append(_arc_svg(Ox + A, Oy, Ox, Oy - A, A, color=MUTED, sw=1.4, dash="6,6"))
    f.append(line(Ox, Oy, Px, Oy, color=MAG, sw=2.6))
    f.append(line(Px, Oy, Px, Py, color=MAG, sw=2.6, dash="6,5"))
    f.append(line(Ox, Oy, Px, Py, color=ELEC, sw=2.8))
    f.append(circle(Px, Py, 6, fill=ELEC, stroke=ELEC, sw=1))

    f.append(text(434, 205, "стан у мить t = 0", size=12, anchor="start"))
    f.append(text(310, 352, "q(0)", size=13))
    f.append(text(408, 272, "I(0)/ω₀", size=13, anchor="end"))
    f.append(text(300, 243, "A — амплітуда", size=13, anchor="end", color=ELEC))

    ph = math.atan2(Oy - Py, Px - Ox)
    f.append(_arc_svg(Ox + 52, Oy, Ox + 52 * math.cos(ph), Oy - 52 * math.sin(ph), 52,
                      color=INK, sw=1.6))
    f.append(text(268, 318, "φ", size=15, bold=True))

    f.append(mtext(480, 90, ["далі ця сама точка йде по колу радіуса A",
                             "рівномірно, з кутовою швидкістю ω₀"], size=12, color=MUTED))

    bx, _, _ = textbox(W / 2, 396,
                       "A = √( q(0)² + (I(0)/ω₀)² )         tg φ = I(0) / (ω₀·q(0))",
                       size=13, pad=10, fill="#eafaf1", stroke=ELEC, sw=1.5)
    f.append(bx)
    return render(os.path.join(IMG, "ics.svg"), W, H, *f)


# ── фігури до числової вставки (proj) ──────────────────────────────────────
def _dcircle(cx, cy, r, color=MUTED, sw=1.4, dash="6,5"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, color, sw, dash))


def _lc_steps(N):
    """Кроки інтеграторів у безрозмірних осях x = q/q₀, y = I/(q₀·ω₀); θ = ω₀·dt."""
    th = 2 * math.pi / N

    def fwd(x, y):                       # явний Ейлер: обидва — зі старого стану
        return x - th * y, y + th * x

    def bwd(x, y):                       # неявний Ейлер
        x1 = (x - th * y) / (1 + th * th)
        return x1, y + th * x1

    def sym(x, y):                       # симплектичний: спершу струм, тоді заряд
        y1 = y + th * x
        return x - th * y1, y1

    def ver(x, y):                       # Верле: пів-копняка · крок · пів-копняка
        yh = y + (th / 2) * x
        x1 = x - th * yh
        return x1, yh + (th / 2) * x1
    return fwd, bwd, sym, ver


def _orbit(stepf, N, periods, stop_r=None):
    x, y = 1.0, 0.0
    pts = [(x, y)]
    for _ in range(int(N * periods)):
        x, y = stepf(x, y)
        pts.append((x, y))
        if stop_r and math.hypot(x, y) > stop_r:
            break
    return pts


def fig_proj_phase():
    """Три інтегратори на фазовій площині: спіраль назовні, замкнений еліпс, спіраль усередину."""
    W, H = 940, 462
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Що робить із орбітою сам метод інтегрування", size=16, bold=True))
    f.append(text(W / 2, 52, "фазова площина (q, I): точна орбіта — замкнене коло, бо енергія стала",
                  size=12, color=MUTED))

    N = 24
    fwd, bwd, sym, ver = _lc_steps(N)
    cy = 238
    panels = [
        (165, "явний Ейлер", MAG, _orbit(fwd, N, 1.3, stop_r=2.5), 40.0,
         "×4.9 енергії за період", "спіраль назовні: коло розкручується"),
        (470, "симплектичний Ейлер", ELEC, _orbit(sym, N, 3), 96.0,
         "енергія стала: ±13%", "орбіта замкнена — скошений еліпс"),
        (775, "неявний Ейлер", NEG, _orbit(bwd, N, 2), 96.0,
         "×0.20 енергії за період", "спіраль усередину: фальшивий опір"),
    ]
    for cx, name, col, pts, u, cap1, cap2 in panels:
        f.append(text(cx, 96, name, size=14, bold=True))
        f.append(line(cx - 106, cy, cx + 106, cy, color="#dfe3e7", sw=1.2))
        f.append(line(cx, cy - 106, cx, cy + 106, color="#dfe3e7", sw=1.2))
        f.append(text(cx + 112, cy + 5, "q", size=12, italic=True, color=MUTED, anchor="start"))
        f.append(text(cx + 8, cy - 112, "I", size=12, italic=True, color=MUTED, anchor="start"))
        f.append(_dcircle(cx, cy, u))
        px = [(cx + u * x, cy - u * y) for (x, y) in pts]
        f.append(_poly(px, col, sw=2.4))
        f.append(circle(px[-1][0], px[-1][1], 4.5, fill=col, stroke=col, sw=1))
        f.append(text(cx, 386, cap1, size=13, bold=True, color=col))
        f.append(text(cx, 406, cap2, size=11.5, color=INK))

    f.append(text(W / 2, 434, "Штрихове коло — точна орбіта (енергія стала). "
                              "Крок навмисно грубий: 24 кроки на період.",
                  size=12, color=MUTED))
    f.append(text(W / 2, 452, "Ліва панель у власному масштабі — за один період "
                              "радіус орбіти росте в 2.2 раза.", size=12, color=MUTED))
    return render(os.path.join(IMG, "proj-phase.svg"), W, H, *f)


def fig_proj_drift():
    """Енергія в часі: явний накачує, неявний зливає, симплектичний тримає смугу."""
    W, H = 940, 420
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Куди дівається енергія ідеального контуру в числовій моделі",
                  size=16, bold=True))
    f.append(text(W / 2, 52, "той самий контур і той самий крок — 200 кроків на період",
                  size=12, color=MUTED))

    N, P = 200, 10
    fwd, bwd, sym, ver = _lc_steps(N)

    def series(stepf, periods, every=5):
        x, y = 1.0, 0.0
        out = [(0.0, 1.0)]
        for n in range(1, int(N * periods) + 1):
            x, y = stepf(x, y)
            if n % every == 0:
                out.append((n / N, x * x + y * y))
        return out

    # ── ліва панель: широкий погляд ──
    ax0, ax1, yb, yt = 104.0, 470.0, 352.0, 104.0
    EMAX = 7.6
    f.append(text(287, 82, "10 періодів: погляд згори", size=13, bold=True))

    def PXL(t):
        return ax0 + (ax1 - ax0) * (t / P)

    def PYL(e):
        return yb - (yb - yt) * (e / EMAX)

    f.append(arrow(ax0, yb + 8, ax0, yt - 12, color=INK, sw=1.5))
    f.append(arrow(ax0 - 10, yb, ax1 + 16, yb, color=INK, sw=1.5))
    for e in (1, 2, 4, 6):
        f.append(line(ax0 - 5, PYL(e), ax0, PYL(e), color=INK, sw=1.2))
        f.append(text(ax0 - 10, PYL(e) + 4, "%d" % e, size=11, color=MUTED, anchor="end"))
    f.append(text(ax0 - 10, yb + 4, "0", size=11, color=MUTED, anchor="end"))
    f.append(line(ax0, PYL(1), ax1, PYL(1), color="#c8ccd2", sw=1.2, dash="5,5"))
    for t in (2, 4, 6, 8, 10):
        f.append(text(PXL(t), yb + 18, "%d" % t, size=11, color=MUTED))
    f.append(text(ax1 + 14, yb + 32, "періоди", size=12, color=MUTED, anchor="end"))
    f.append(text(ax0 - 8, yt - 20, "E / E₀", size=12, color=MUTED, anchor="start"))

    for stepf, col in ((fwd, MAG), (bwd, NEG), (sym, ELEC)):
        pts = [(PXL(t), PYL(min(e, EMAX))) for (t, e) in series(stepf, P)]
        f.append(_poly(pts, col, sw=2.4))
    f.append(text(390, 180, "явний Ейлер  ×7.2", size=13, bold=True, color=MAG, anchor="end"))
    f.append(text(466, 300, "симплектичний і Верле", size=13, bold=True, color=ELEC, anchor="end"))
    f.append(text(466, 330, "неявний Ейлер  ×0.14", size=13, bold=True, color=NEG, anchor="end"))

    # ── права панель: збільшення смуги ──
    bx0, bx1 = 600.0, 900.0
    E_LO, E_HI, PZ = 0.980, 1.020, 3
    f.append(text(750, 82, "смуга біля 1.0, збільшена в 190 разів", size=13, bold=True))

    def PXR(t):
        return bx0 + (bx1 - bx0) * (t / PZ)

    def PYR(e):
        return yb - (yb - yt) * (e - E_LO) / (E_HI - E_LO)

    f.append(arrow(bx0, yb + 8, bx0, yt - 12, color=INK, sw=1.5))
    f.append(arrow(bx0 - 10, yb, bx1 + 16, yb, color=INK, sw=1.5))
    for e in (0.98, 0.99, 1.00, 1.01, 1.02):
        f.append(line(bx0 - 5, PYR(e), bx0, PYR(e), color=INK, sw=1.2))
        f.append(text(bx0 - 10, PYR(e) + 4, "%.2f" % e, size=11, color=MUTED, anchor="end"))
    f.append(line(bx0, PYR(1.0), bx1, PYR(1.0), color="#c8ccd2", sw=1.2, dash="5,5"))
    for t in (1, 2, 3):
        f.append(text(PXR(t), yb + 18, "%d" % t, size=11, color=MUTED))
    f.append(text(bx1 + 14, yb + 32, "періоди", size=12, color=MUTED, anchor="end"))

    for stepf, col, sw in ((sym, ELEC, 2.4), (ver, INK, 2.2)):
        pts = [(PXR(t), PYR(min(max(e, E_LO), E_HI)))
               for (t, e) in series(stepf, PZ, every=2)]
        f.append(_poly(pts, col, sw=sw))
    f.append(text(bx0 + 10, 292, "симплектичний Ейлер: ±1.6%", size=12.5, bold=True,
                  color=ELEC, anchor="start"))
    f.append(text(bx0 + 10, 316, "Верле: ±0.02% — злився з прямою", size=12.5, bold=True,
                  color=INK, anchor="start"))
    return render(os.path.join(IMG, "proj-drift.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_cycle(), fig_energy(), fig_analogy(),
          fig_hist_needle(), fig_hist_regimes(),
          fig_phase(), fig_ics(),
          fig_proj_phase(), fig_proj_drift()]
    print("written:")
    for p in ps:
        print("  ", p)
