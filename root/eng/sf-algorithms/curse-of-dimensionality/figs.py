# -*- coding: utf-8 -*-
"""Фігури до теми «Прокляття розмірності»."""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)


def rnd(seed):
    """Детермінований генератор — щоб фігури не мінялися між запусками.
    Беремо старші біти 64-бітного конгруентного кроку: молодші в такій схемі надто регулярні,
    а нам потрібні пари координат без прихованої ґратки."""
    x = seed & ((1 << 64) - 1)
    while True:
        x = (6364136223846793005 * x + 1442695040888963407) % (1 << 64)
        yield (x >> 33) / float(1 << 31)


def tb(cx, cy, s, **kw):
    body, _w, _h = textbox(cx, cy, s, **kw)
    return body


def dot(x, y, r=3.0, color=INK):
    return circle(x, y, r, fill=color, stroke=color, sw=0.6)


def polyline(pts, color=POS, sw=2.6):
    d = " ".join("%.1f,%.1f" % p for p in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"/>' % (d, color, sw))


# ── 1. Об'єм тікає до межі ──────────────────────────────────────────────────
def fig_volume():
    W, H = 860, 430
    out = []

    # ліва панель: квадрат і його серцевина
    X0, Y0, S = 60, 110, 220
    k = 0.9
    inner = S * k
    off = (S - inner) / 2.0
    out.append(rect(X0, Y0, S, S, fill="#fdecea", stroke=POS, sw=2.0, rx=0))
    out.append(rect(X0 + off, Y0 + off, inner, inner, fill=BG, stroke=LINE, sw=1.6, rx=0))
    out.append(text(X0 + S / 2, Y0 + S / 2, "81%", size=22, bold=True))
    out.append(text(X0 + S / 2, Y0 - 24, "два виміри: серцевина ще майже все", size=13))
    out.append(text(X0 + S / 2, Y0 + S + 34, "кожна сторона вкорочена на десяту", size=13, color=MUTED))
    out.append(text(X0 + S / 2, Y0 + S + 56, "частину — шкаралупа забрала 19%", size=13, color=MUTED))

    # права панель: крива 0.9^d
    PX, PY, PW, PH = 400, 110, 400, 200
    out.append(line(PX, PY + PH, PX + PW, PY + PH, color=INK, sw=1.6))
    out.append(line(PX, PY, PX, PY + PH, color=INK, sw=1.6))
    pts = []
    for i in range(0, 101):
        x = PX + PW * i / 100.0
        y = PY + PH - PH * (k ** i)
        pts.append((x, y))
    out.append(polyline(pts, color=POS, sw=2.6))
    for i in (0, 20, 40, 60, 80, 100):
        x = PX + PW * i / 100.0
        out.append(line(x, PY + PH, x, PY + PH + 6, color=INK, sw=1.2))
        out.append(text(x, PY + PH + 24, str(i), size=12, color=MUTED))
    out.append(text(PX + PW / 2, PY + PH + 50, "кількість вимірів", size=13))
    out.append(text(PX, PY - 40, "частка об'єму, що лишилась у серцевині", size=13, anchor="start"))

    for i, lab in ((10, "10 вимірів — 35%"), (20, "20 вимірів — 12%")):
        x = PX + PW * i / 100.0
        y = PY + PH - PH * (k ** i)
        out.append(dot(x, y, 4.0, POS))
        out.append(text(x + 14, y - 12, lab, size=12, anchor="start"))
    out.append(tb(PX + PW - 110, PY + 46,
                  "50 вимірів — 0.5%\n100 вимірів — 0.003%", size=12, pad=10))

    return render(os.path.join(OUT, 'volume-to-shell.svg'), W, H, *out,
                  title="Куди дівається об'єм, коли додати вимірів")


# ── 2. Гістограми відстаней звужуються ──────────────────────────────────────
def _hist(d, m=1600, nb=34, seed=20260808):
    g = rnd(seed + d)
    ds = []
    for _ in range(m):
        s = 0.0
        for _ in range(d):
            t = next(g) - next(g)
            s += t * t
        ds.append(math.sqrt(s))
    mu = sum(ds) / len(ds)
    var = sum((x - mu) ** 2 for x in ds) / len(ds)
    rel = math.sqrt(var) / mu
    bins = [0] * nb
    for x in ds:
        i = int(x / mu / 2.0 * nb)
        if 0 <= i < nb:
            bins[i] += 1
    return bins, rel


def fig_contrast():
    W, H = 880, 430
    out = []
    panels = [(2, 60), (10, 350), (200, 640)]
    PW, PY, PH = 200, 120, 180
    for d, PX in panels:
        bins, rel = _hist(d)
        top = float(max(bins)) or 1.0
        nb = len(bins)
        bw = PW / float(nb)
        for i, v in enumerate(bins):
            if v == 0:
                continue
            h = PH * v / top
            out.append(rect(PX + i * bw + 0.6, PY + PH - h, bw - 1.2, h,
                            fill="#f6c7c0", stroke=POS, sw=0.7, rx=0))
        out.append(line(PX, PY + PH, PX + PW, PY + PH, color=INK, sw=1.6))
        out.append(line(PX + PW / 2, PY - 6, PX + PW / 2, PY + PH, color=NEG, sw=1.4, dash="5 4"))
        for frac, lab in ((0.0, "0"), (0.5, "1"), (1.0, "2")):
            x = PX + PW * frac
            out.append(line(x, PY + PH, x, PY + PH + 6, color=INK, sw=1.2))
            out.append(text(x, PY + PH + 24, lab, size=12, color=MUTED))
        out.append(text(PX + PW / 2, PY - 30, "%d вимір%s" % (d, "и" if d == 2 else "ів"),
                        size=15, bold=True))
        out.append(text(PX + PW / 2, PY + PH + 52, "розкид %d%%" % round(rel * 100), size=13))

    out.append(text(W / 2, H - 46, "по горизонталі — відстань між двома випадковими точками,", size=13, color=MUTED))
    out.append(text(W / 2, H - 26, "поділена на середню відстань цього ж простору", size=13, color=MUTED))
    return render(os.path.join(OUT, 'distance-histograms.svg'), W, H, *out,
                  title="Що більше вимірів, то тісніше всі відстані туляться до однієї")


# ── 3. Чому дерево перестає різати простір ──────────────────────────────────
def fig_search():
    W, H = 880, 430
    out = []
    X0, Y0, S = 60, 100, 240

    g = rnd(4242)
    pts = [(next(g), next(g)) for _ in range(16)]

    cuts = []

    def split(items, x0, y0, x1, y1, axis, depth):
        if len(items) <= 1 or depth >= 4:
            return
        items = sorted(items, key=lambda p: p[axis])
        mid = len(items) // 2
        v = (items[mid - 1][axis] + items[mid][axis]) / 2.0
        if axis == 0:
            cx = x0 + (x1 - x0) * v
            cuts.append((cx, y0, cx, y1, depth))
            split(items[:mid], x0, y0, cx, y1, 1, depth + 1)
            split(items[mid:], cx, y0, x1, y1, 1, depth + 1)
        else:
            cy = y1 - (y1 - y0) * v
            cuts.append((x0, cy, x1, cy, depth))
            split(items[:mid], x0, cy, x1, y1, 0, depth + 1)
            split(items[mid:], x0, y0, x1, cy, 0, depth + 1)

    split(pts, X0, Y0, X0 + S, Y0 + S, 0, 0)

    out.append(rect(X0, Y0, S, S, fill=BG, stroke=INK, sw=2.0, rx=0))
    for (a, b, c, e, depth) in cuts:
        out.append(line(a, b, c, e, color=MUTED, sw=1.6 - 0.25 * depth))
    for (px, py) in pts:
        out.append(dot(X0 + S * px, Y0 + S * (1 - py), 3.2))
    qx, qy = X0 + S * 0.42, Y0 + S * 0.46
    out.append(circle(qx, qy, 26, fill="none", stroke=NEG, sw=2.2))
    out.append(dot(qx, qy, 4.5, NEG))
    out.append(text(X0 + S / 2, Y0 + S + 32,
                    "два виміри: куля запиту зачіпає", size=13))
    out.append(text(X0 + S / 2, Y0 + S + 54,
                    "лише дві комірки з шістнадцяти", size=13))

    CX = 620
    steps = [
        "мільйон точок — дерево встигає\nзробити лише 20 розрізів",
        "зі ста координат розрізано двадцять,\nуздовж решти комірка на всю ширину",
        "радіус пошуку майже дорівнює середній\nвідстані — куля накриває всі комірки",
        "обхід дерева вироджується\nу повний перебір",
    ]
    ys = [110, 190, 270, 350]
    for i, (s, y) in enumerate(zip(steps, ys)):
        out.append(tb(CX, y, s, size=12, pad=11))
        if i < len(steps) - 1:
            out.append(arrow(CX, y + 26, CX, ys[i + 1] - 26, color=LINE, sw=1.8))

    return render(os.path.join(OUT, 'kdtree-degrades.svg'), W, H, *out,
                  title="Чому просторове дерево перестає допомагати")


# ── 4. Виміряна частка відвіданих листків ───────────────────────────────────
# Числа — вихід програми зі вставки proj-contrast-measure.md (kd-дерево з лічильником,
# кошик 16, точний пошук найближчого, середнє по запитах). Тут вони вписані сталими:
# перераховувати дерево на ста тисячах точок усередині figs.py надто повільно.
VISITED = {
    20000:  [(2, 0.001), (3, 0.002), (5, 0.008), (8, 0.058), (10, 0.161),
             (12, 0.653), (13, 0.926), (15, 0.975), (20, 1.000), (30, 1.000)],
    100000: [(2, 0.000), (3, 0.000), (5, 0.002), (8, 0.021), (10, 0.048),
             (12, 0.216), (13, 0.592), (15, 0.928), (20, 1.000)],
}


def fig_visited():
    W, H = 860, 470
    out = []
    PX, PY, PW, PH = 90, 90, 560, 250
    DMAX = 30.0

    def sx(d):
        return PX + PW * (d - 2.0) / (DMAX - 2.0)

    def sy(f):
        return PY + PH - PH * f

    # смуга, де перебір уже дешевший
    out.append(rect(PX, PY, PW, PH * 0.8, fill="#fdecea", stroke="none", sw=0, rx=0))

    out.append(line(PX, PY + PH, PX + PW, PY + PH, color=INK, sw=1.6))
    out.append(line(PX, PY, PX, PY + PH, color=INK, sw=1.6))
    for f in (0.0, 0.2, 0.5, 1.0):
        y = sy(f)
        out.append(line(PX - 6, y, PX, y, color=INK, sw=1.2))
        out.append(text(PX - 14, y + 5, "%d%%" % round(f * 100), size=12,
                        color=MUTED, anchor="end"))
    for d in (2, 5, 10, 15, 20, 25, 30):
        x = sx(d)
        out.append(line(x, PY + PH, x, PY + PH + 6, color=INK, sw=1.2))
        out.append(text(x, PY + PH + 24, str(d), size=12, color=MUTED))
    out.append(text(PX + PW / 2, PY + PH + 50, "кількість вимірів", size=13))
    out.append(text(PX - 60, PY - 30, "частка листків дерева, у які довелося зазирнути",
                    size=13, anchor="start"))

    for n, color in ((20000, POS), (100000, NEG)):
        pts = [(sx(d), sy(f)) for d, f in VISITED[n] if d <= DMAX]
        out.append(polyline(pts, color=color, sw=2.6))
        for x, y in pts:
            out.append(dot(x, y, 3.6, color))

    out.append(text(sx(16.6), sy(0.99) - 16, "20 000 точок", size=13, color=POS, anchor="start"))
    out.append(text(sx(20.8), sy(0.60), "100 000 точок", size=13, color=NEG, anchor="start"))
    out.append(tb(PX + 150, PY + PH + 104,
                  "рожеве — дерево торкається понад п'ятої частини бази:\n"
                  "суцільний перебір дешевший навіть за тієї самої роботи",
                  size=12, pad=11))
    out.append(tb(PX + PW - 40, PY + PH + 104,
                  "уп'ятеро більше точок — це\nдва зайві розрізи: половину\n"
                  "листків обходимо на 12.8\nвиміру замість 11.5",
                  size=12, pad=11))

    return render(os.path.join(OUT, 'visited-fraction.svg'), W, H, *out,
                  title="Скільки дерева доводиться обійти заради одного найближчого сусіда")


# ── 5. Об'єм кулі: пік на d=5 і падіння швидше за експоненту ────────────────
def _vball(d, r=1.0):
    return math.pi ** (d / 2.0) * r ** d / math.gamma(d / 2.0 + 1.0)


def fig_ball_volume():
    W, H = 900, 430
    out = []
    PY, PH = 120, 230

    # ── ліва панель: V_d(1) з максимумом на d = 5 ──
    X0, LW = 70, 310
    out.append(text(X0, 96, "об'єм кулі радіуса 1", size=13, anchor="start"))
    ymax, nb = 6.0, 14
    bw = LW / float(nb)
    for i in range(nb):
        d = i + 1
        h = PH * _vball(d) / ymax
        out.append(rect(X0 + i * bw + 2.5, PY + PH - h, bw - 5, h,
                        fill=(POS if d == 5 else "#f6c7c0"), stroke=POS, sw=1.0, rx=0))
    out.append(line(X0, PY + PH, X0 + LW, PY + PH, color=INK, sw=1.6))
    out.append(line(X0, PY, X0, PY + PH, color=INK, sw=1.6))
    for v in (0, 2, 4, 6):
        y = PY + PH - PH * v / ymax
        out.append(line(X0 - 6, y, X0, y, color=INK, sw=1.2))
        out.append(text(X0 - 12, y + 4, str(v), size=11, color=MUTED, anchor="end"))
    for d in (1, 5, 10, 14):
        out.append(text(X0 + (d - 0.5) * bw, PY + PH + 22, str(d), size=11, color=MUTED))
    out.append(text(X0 + LW / 2, PY + PH + 48, "вимір d", size=13))
    out.append(tb(X0 + 230, 162, "максимум на d = 5,\nдалі об'єм тане", size=12, pad=10))

    # ── права панель: частка куба, яку займає вписана куля (log₁₀) ──
    PX, PW = 490, 350
    out.append(text(PX, 96, "яку частку куба займає вписана куля (log₁₀)",
                    size=13, anchor="start"))
    span = 72.0
    out.append(line(PX, PY + PH, PX + PW, PY + PH, color=INK, sw=1.6))
    out.append(line(PX, PY, PX, PY + PH, color=INK, sw=1.6))
    for lg in (0, 20, 40, 60):
        y = PY + PH * lg / span
        out.append(line(PX - 6, y, PX, y, color=INK, sw=1.2))
        out.append(text(PX - 12, y + 4, "10⁰" if lg == 0 else "10⁻%d" % lg,
                        size=11, color=MUTED, anchor="end"))
    for d in (0, 25, 50, 75, 100):
        x = PX + PW * d / 100.0
        out.append(line(x, PY + PH, x, PY + PH + 6, color=INK, sw=1.2))
        out.append(text(x, PY + PH + 22, str(d), size=11, color=MUTED))
    out.append(text(PX + PW / 2, PY + PH + 48, "вимір d", size=13))

    # пунктир — чиста експонента 0.5^d: на логарифмічній шкалі це пряма
    out.append(line(PX, PY, PX + PW, PY + PH * (-math.log10(0.5) * 100) / span,
                    color=NEG, sw=2.0, dash="6 5"))
    out.append(polyline([(PX + PW * d / 100.0,
                          PY + PH * (-math.log10(_vball(d, 0.5))) / span)
                         for d in range(1, 101)], color=POS, sw=2.6))
    out.append(mtext(PX + PW - 10, 143, ["для порівняння —", "чиста експонента 0.5ᵈ"],
                     size=12, color=NEG, anchor="end"))
    out.append(tb(PX + 130, 300, "0.25% на d = 10\n2.5·10⁻⁸ на d = 20\n1.9·10⁻⁷⁰ на d = 100",
                  size=12, pad=10))

    return render(os.path.join(OUT, 'ball-volume-collapse.svg'), W, H, *out,
                  title="Об'єм кулі тане швидше за будь-яку експоненту")


# ── 6. Густина різниці двох рівномірних координат ───────────────────────────
def fig_difference_density():
    W, H = 880, 420
    out = []

    # ── ліва панель: перекриття двох відрізків ──
    out.append(text(60, 96, "перекриття двох відрізків дає густину", size=13, anchor="start"))
    U = 160.0                       # одиниця довжини в пікселях
    XA, w = 70.0, 0.35
    XB = XA + U * w
    ov0, ov1 = XB, XA + U           # спільна частина — відрізок [w, 1]
    out.append(rect(XA, 140, U, 22, fill="#f6c7c0", stroke=POS, sw=1.4, rx=0))
    out.append(rect(XB, 185, U, 22, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=0))
    out.append(rect(ov0, 230, ov1 - ov0, 22, fill="#e8f6ed", stroke=FIELD, sw=1.6, rx=0))
    out.append(text(XA, 132, "x = t: t ∈ [0, 1]", size=12, color=POS, anchor="start"))
    out.append(text(XB, 177, "y = t − w: t ∈ [w, 1+w]", size=12, color=NEG, anchor="start"))
    out.append(text(ov0, 222, "спільна частина: 1 − |w|", size=12, color=FIELD, anchor="start"))
    out.append(line(55, 272, 310, 272, color=INK, sw=1.6))
    for xv, lab in ((XA, "0"), (XB, "w"), (XA + U, "1"), (XB + U, "1+w")):
        out.append(line(xv, 272, xv, 278, color=INK, sw=1.2))
        out.append(text(xv, 294, lab, size=12, color=MUTED))
    out.append(text(185, 320, "f(w) = довжина спільної частини", size=13))

    # ── права панель: сама густина ──
    PX, PW, PY, PH = 430, 340, 110, 180
    out.append(text(PX, 96, "густина різниці W = x − y", size=13, anchor="start"))
    cx, base = PX + PW / 2, PY + PH
    out.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#f6c7c0" '
               'stroke="%s" stroke-width="2.2"/>'
               % (PX, base, cx, PY, PX + PW, base, POS))
    out.append(line(PX - 14, base, PX + PW + 14, base, color=INK, sw=1.6))
    for xv, lab in ((PX, "−1"), (cx, "0"), (PX + PW, "1")):
        out.append(line(xv, base, xv, base + 6, color=INK, sw=1.2))
        out.append(text(xv, base + 24, lab, size=12, color=MUTED))
    out.append(text(PX + PW - 40, 150, "f(u) = 1 − |u|", size=13, anchor="end"))
    out.append(tb(cx, 358, "площа під кривою = 1\nE[W²] = 1/6\nVar[W²] = 7/180",
                  size=12, pad=11))

    return render(os.path.join(OUT, 'difference-density.svg'), W, H, *out,
                  title="Густина різниці двох рівномірних координат")


if __name__ == '__main__':
    fig_volume()
    fig_contrast()
    fig_search()
    fig_visited()
    fig_ball_volume()
    fig_difference_density()
    print("ok")
