# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

GOLD = "#d98a00"
PURPLE = "#8a5fb0"


def log2(x):
    return math.log(x, 2)


# ══════════════════════════════════════════════════════════════════════════════
# Базова стаття (kl-divergence.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── extra-bits: ціна хибної моделі по символах ────────────────────────────────
# Ідея: ГОЛОВНА фігура теми. Джерело p, кодуємо оптимальним кодом для НЕправильної
# моделі q. На кожному символі правильна ціна log2(1/p), а ми платимо log2(1/q).
# Різниця, зважена частотою p, додається в D(p‖q) — зайві біти.
def fig_extra_bits():
    W, H = 760, 360
    p = []
    # p — справжній розподіл, q — модель кодека
    syms = [("A", 0.50, 0.25, FIELD, "#eafaf0"),
            ("B", 0.25, 0.25, NEG, "#eef4ff"),
            ("C", 0.125, 0.25, GOLD, "#fdf6e3"),
            ("D", 0.125, 0.25, POS, "#fdecea")]
    x0, y0 = 56, 78
    rowh = 50
    cols = [(0, "символ"), (92, "p (правда)"), (196, "q (модель)"),
            (312, "правильно\nlog₂(1/p)"), (432, "платимо\nlog₂(1/q)"),
            (556, "зайве\n×p")]
    for cx, lab in cols:
        for j, ln in enumerate(lab.split("\n")):
            p.append(text(x0 + cx, y0 - 30 + j * 12, ln, size=10, color=MUTED,
                          anchor="middle", bold=True))
    total = 0.0
    for i, (s, pr, qr, col, fill) in enumerate(syms):
        y = y0 + i * rowh
        cp = log2(1 / pr)
        cq = log2(1 / qr)
        extra = pr * (cq - cp)
        total += extra
        p.append(rect(x0 - 14, y, 28, 28, fill=fill, stroke=col, sw=1.6))
        p.append(text(x0, y + 19, s, size=14, color=col, bold=True))
        p.append(text(x0 + 92, y + 18, "%.3f" % pr, size=11, color=INK))
        p.append(text(x0 + 196, y + 18, "%.2f" % qr, size=11, color=INK))
        p.append(text(x0 + 312, y + 18, "%.0f біт" % cp, size=11, color=FIELD, bold=True))
        p.append(text(x0 + 432, y + 18, "%.0f біт" % cq, size=11, color=POS, bold=True))
        sign = "+" if extra >= 0 else "−"
        p.append(text(x0 + 556, y + 18, "%s%.3f" % (sign, abs(extra)), size=11,
                      color=col, bold=True))
    yb = y0 + len(syms) * rowh + 4
    p.append(line(x0 + 470, yb, x0 + 596, yb, color=INK, sw=1.2))
    b, _, _ = textbox(x0 + 540, yb + 26, "D(p‖q) = 0.25 біта / символ", size=12,
                      bold=True, color=GOLD, fill="#fdf6e3", stroke=GOLD, sw=1.8)
    p.append(b)
    p.append(text(x0 + 130, yb + 26, "сума зайвих бітів =", size=11, color=MUTED, anchor="start"))
    render(os.path.join(OUT, "extra-bits.svg"), W, H, *p,
           title="Розбіжність — зайві біти за хибної моделі q")


# ── asymmetry: D(p‖q) ≠ D(q‖p) ────────────────────────────────────────────────
# Ідея: показати наочно, що міняючи ролі p і q, дістаємо РІЗНІ числа. Дві колонки
# з тими самими двома розподілами, але різним порядком, і два різні підсумки.
def fig_asymmetry():
    W, H = 720, 330
    p = []

    def kl(P, Q):
        return sum(pi * log2(pi / qi) for pi, qi in zip(P, Q) if pi > 0)

    P = [0.9, 0.1]
    Q = [0.5, 0.5]
    dpq = kl(P, Q)
    dqp = kl(Q, P)

    def mini_dist(cx, top, dist, lab, col, fill):
        bw, gap = 30, 14
        x0 = cx - (2 * bw + gap) / 2
        base = top + 90
        for i, pr in enumerate(dist):
            h = pr * 90
            p.append(rect(x0 + i * (bw + gap), base - h, bw, h, fill=fill, stroke=col, sw=1.5))
            p.append(text(x0 + i * (bw + gap) + bw / 2, base + 14,
                          ["x₁", "x₂"][i], size=9, color=MUTED))
        p.append(line(x0 - 6, base, x0 + 2 * bw + gap + 4, base, color=INK, sw=1.2))
        p.append(text(cx, top, lab, size=12, color=col, bold=True))

    # лівий блок: D(p‖q)
    mini_dist(140, 64, P, "p = (0.9, 0.1)", POS, "#fdecea")
    mini_dist(280, 64, Q, "q = (0.5, 0.5)", NEG, "#eef4ff")
    b1, _, _ = textbox(210, 240, "D(p‖q) = %.2f біта" % dpq, size=13, bold=True,
                       color=POS, fill="#fdecea", stroke=POS, sw=1.8)
    p.append(b1)
    p.append(text(210, 50, "штрафуємо за кодом для q", size=10, color=MUTED, italic=True))

    # роздільник
    p.append(line(W / 2, 56, W / 2, 270, color=MUTED, sw=1, dash="4 4"))

    # правий блок: D(q‖p)
    mini_dist(440, 64, Q, "q = (0.5, 0.5)", NEG, "#eef4ff")
    mini_dist(580, 64, P, "p = (0.9, 0.1)", POS, "#fdecea")
    b2, _, _ = textbox(510, 240, "D(q‖p) = %.2f біта" % dqp, size=13, bold=True,
                       color=NEG, fill="#eef4ff", stroke=NEG, sw=1.8)
    p.append(b2)
    p.append(text(510, 50, "ролі p і q помінялись", size=10, color=MUTED, italic=True))

    p.append(text(W / 2, 300, "ті самі два розподіли, інший порядок — інше число: D несиметрична, це не відстань",
                  size=11, color=GOLD, bold=True))
    render(os.path.join(OUT, "asymmetry.svg"), W, H, *p,
           title="Несиметрія: D(p‖q) ≠ D(q‖p)")


# ── cross-entropy: H(p,q) = H(p) + D(p‖q) ─────────────────────────────────────
# Ідея: вісь біт/символ. Перехресна ентропія = справжнє дно H(p) ПЛЮС надбавка
# розбіжності. Розбіжність — це рівно той надлишок над дном.
def fig_cross_entropy():
    W, H = 720, 290
    p = []
    ax0, ay = 80, 210
    p.append(arrow(ax0, ay, 660, ay, color=INK, sw=1.6))
    p.append(text(660, ay + 22, "біт на символ", size=11, color=INK, italic=True, anchor="end"))
    p.append(line(ax0, ay - 4, ax0, ay + 4, color=INK, sw=1.2))
    p.append(text(ax0, ay + 18, "0", size=9, color=MUTED))

    Hx = ax0 + 230
    Cx = ax0 + 380
    # зона змісту = H(p)
    p.append(rect(ax0, 110, Hx - ax0, ay - 110, fill="#eafaf0", stroke="none", sw=0))
    p.append(text((ax0 + Hx) / 2, 142, "H(p)", size=13, color=FIELD, bold=True))
    p.append(text((ax0 + Hx) / 2, 162, "справжнє дно", size=10, color=FIELD))
    # зона надбавки = D
    p.append(rect(Hx, 110, Cx - Hx, ay - 110, fill="#fdf6e3", stroke="none", sw=0))
    p.append(text((Hx + Cx) / 2, 142, "D(p‖q)", size=13, color=GOLD, bold=True))
    p.append(text((Hx + Cx) / 2, 162, "зайве", size=10, color=GOLD))
    # межі
    p.append(line(Hx, 96, Hx, ay + 6, color=FIELD, sw=2.2, dash="5 4"))
    p.append(line(Cx, 96, Cx, ay + 6, color=POS, sw=2.2, dash="5 4"))
    p.append(text(Hx, 86, "H(p)", size=10, color=FIELD, bold=True))
    p.append(text(Cx, 86, "H(p,q) — перехресна", size=10, color=POS, bold=True, anchor="middle"))

    b, _, _ = textbox(W / 2, ay + 58, "H(p, q) = H(p) + D(p‖q)", size=14, bold=True,
                      color=INK, fill="#f4f6f8", stroke=INK, sw=1.6)
    p.append(b)
    render(os.path.join(OUT, "cross-entropy.svg"), W, H, *p,
           title="Перехресна ентропія = дно H(p) + розбіжність D(p‖q)")


# ── gibbs: D ≥ 0, нуль лише за p=q ────────────────────────────────────────────
# Ідея: проста ілюстрація нерівності Гіббса. Що ближче q до p, то менша
# розбіжність; у точці збігу — рівно нуль; розійшлись — додатна.
def fig_gibbs():
    W, H = 700, 320
    ox, oy = 90, 250
    aw, ah = 540, 196
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw - 6, oy + 22, "q₁ — частка першого символу в моделі q",
                  size=11, color=INK, italic=True, anchor="end"))
    p.append(text(ox - 12, oy - ah - 2, "D(p‖q), біт", size=11, color=INK, bold=True, anchor="end"))

    # фіксуємо p = (0.7, 0.3), варіюємо q = (t, 1-t)
    p1 = 0.7
    dmax = 3.2

    def D(t):
        if t <= 0 or t >= 1:
            return dmax
        return p1 * log2(p1 / t) + (1 - p1) * log2((1 - p1) / (1 - t))

    pts = []
    n = 260
    for i in range(n + 1):
        t = 0.012 + (1 - 0.024) * i / n
        x = ox + t * aw
        yv = oy - min(D(t), dmax) / dmax * ah
        pts.append("%.1f,%.1f" % (x, yv))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(pts), GOLD))

    # мінімум у q = p
    xt = ox + p1 * aw
    p.append(circle(xt, oy, 4.5, fill=FIELD, stroke=FIELD, sw=1))
    p.append(line(xt, oy - 4, xt, oy + 4, color=INK, sw=1.1))
    p.append(text(xt, oy + 18, "q₁=0.7", size=9, color=MUTED))
    p.append(text(xt, oy - 14, "q = p → D = 0", size=11, color=FIELD, bold=True))

    for lbl, t in (("0", 0.0), ("1", 1.0)):
        x = ox + t * aw
        p.append(line(x, oy - 4, x, oy + 4, color=INK, sw=1.1))
        p.append(text(x, oy + 18, lbl, size=9, color=MUTED))

    p.append(text(ox + aw * 0.18, oy - ah + 30, "будь-яке q ≠ p → D > 0",
                  size=11, color=POS, bold=True, anchor="start"))
    render(os.path.join(OUT, "gibbs.svg"), W, H, *p,
           title="Нерівність Гіббса: D(p‖q) ≥ 0, нуль лише за q = p (тут p = (0.7, 0.3))")


# ══════════════════════════════════════════════════════════════════════════════
# Детальна версія (kl-divergence-d.md)
# ══════════════════════════════════════════════════════════════════════════════

# ── jensen: опуклість −log і нерівність Єнсена ────────────────────────────────
# Ідея: доведення D≥0 спирається на опуклість. Для опуклої −log хорда ЛЕЖИТЬ ВИЩЕ
# за криву, тож середнє від функції ≥ функція від середнього — звідки й D≥0.
def fig_jensen():
    W, H = 700, 340
    ox, oy = 80, 280
    aw, ah = 560, 230
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw - 6, oy + 22, "x", size=12, color=INK, italic=True, anchor="end"))
    p.append(text(ox + 8, oy - ah - 2, "−log x  (опукла)", size=11, color=INK, bold=True, anchor="start"))

    xa, xb = 0.18, 3.4

    def fx(x):
        return -log2(x)

    ya = fx(xa)
    yb = fx(xb)
    ymin, ymax = -2.6, 2.6

    def sx(x):
        return ox + (x - xa) / (xb - xa) * aw

    def sy(y):
        return oy - (y - ymin) / (ymax - ymin) * ah

    pts = []
    n = 200
    for i in range(n + 1):
        x = xa + (xb - xa) * i / n
        pts.append("%.1f,%.1f" % (sx(x), sy(fx(x))))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(pts), NEG))

    # хорда між двома точками
    p.append(line(sx(xa), sy(ya), sx(xb), sy(yb), color=POS, sw=2.2))
    p.append(circle(sx(xa), sy(ya), 4, fill=POS, stroke=POS, sw=1))
    p.append(circle(sx(xb), sy(yb), 4, fill=POS, stroke=POS, sw=1))
    p.append(text(sx(xa) - 6, sy(ya) - 8, "a", size=11, color=POS, bold=True, anchor="end"))
    p.append(text(sx(xb) + 6, sy(yb) - 8, "b", size=11, color=POS, bold=True, anchor="start"))

    # середня точка: хорда вище за криву
    xm = (xa + xb) / 2
    ychord = (ya + yb) / 2
    ycurve = fx(xm)
    p.append(line(sx(xm), sy(ycurve), sx(xm), sy(ychord), color=FIELD, sw=2, dash="4 3"))
    p.append(circle(sx(xm), sy(ychord), 3.5, fill=POS, stroke=POS, sw=1))
    p.append(circle(sx(xm), sy(ycurve), 3.5, fill=NEG, stroke=NEG, sw=1))
    p.append(text(sx(xm) + 8, sy((ychord + ycurve) / 2) + 4,
                  "розрив ≥ 0", size=10, color=FIELD, bold=True, anchor="start"))
    p.append(text(sx(xm), sy(ychord) - 8, "середнє від f", size=9, color=POS, anchor="middle"))
    p.append(text(sx(xm), sy(ycurve) + 16, "f від середнього", size=9, color=NEG, anchor="middle"))

    p.append(text(W / 2, oy + 50,
                  "хорда опуклої −log лежить вище за криву: E[−log] ≥ −log E[·] — саме це дає D ≥ 0",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "jensen.svg"), W, H, *p,
           title="Нерівність Єнсена для опуклої −log")


# ── forward-reverse: mode-covering vs mode-seeking ────────────────────────────
# Ідея: справжнє p — двогорба суміш. Forward KL D(p‖q) тягне ОДНОГОРБУ q накрити
# обидва горби (розмазує, mode-covering). Reverse D(q‖p) тягне q залізти в ОДИН
# горб (mode-seeking). Той самий p, та сама q-сім'я — різний вибір.
def fig_forward_reverse():
    W, H = 720, 360
    p = []

    def bump(x, mu, s, a):
        return a * math.exp(-((x - mu) ** 2) / (2 * s * s))

    def ptrue(x):
        return bump(x, 1.4, 0.45, 1.0) + bump(x, 4.0, 0.5, 0.85)

    def panel(x0, y0, w, h, qmu, qs, title, sub, col):
        # осі
        p.append(line(x0, y0 + h, x0 + w, y0 + h, color=INK, sw=1.4))
        # справжнє p — сіра заливка
        n = 120
        xa, xb = -0.4, 5.8
        scale = 78
        polyp = []
        for i in range(n + 1):
            xx = xa + (xb - xa) * i / n
            polyp.append("%.1f,%.1f" % (x0 + (xx - xa) / (xb - xa) * w,
                                        y0 + h - ptrue(xx) * scale))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>'
                 % (" ".join(polyp), MUTED))
        p.append(text(x0 + w - 4, y0 + 12, "p (правда)", size=10, color=MUTED, anchor="end"))
        # модель q — одногорба
        polyq = []
        for i in range(n + 1):
            xx = xa + (xb - xa) * i / n
            polyq.append("%.1f,%.1f" % (x0 + (xx - xa) / (xb - xa) * w,
                                        y0 + h - bump(xx, qmu, qs, 1.0) * scale))
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
                 'stroke-linejoin="round"/>' % (" ".join(polyq), col))
        p.append(text(x0 + w / 2, y0 - 16, title, size=13, color=col, bold=True))
        p.append(text(x0 + w / 2, y0 - 1, sub, size=10, color=MUTED))

    panel(60, 70, 280, 200, 2.7, 1.7, "forward  D(p‖q)", "накриває обидва горби (розмазує)", NEG)
    panel(390, 70, 280, 200, 4.0, 0.5, "reverse  D(q‖p)", "залазить в один горб (загострює)", POS)

    p.append(text(W / 2, 322,
                  "та сама двогорба p і та сама одногорба сім'я q — напрям KL диктує різний компроміс",
                  size=11, color=GOLD, bold=True))
    render(os.path.join(OUT, "forward-reverse.svg"), W, H, *p,
           title="Forward vs reverse KL: накрити все чи вибрати один режим")


# ── mle: мінімум KL = максимум правдоподібності ───────────────────────────────
# Ідея: емпіричний розподіл даних p̂ фіксований. Підбір параметрів θ моделі q_θ
# так, щоб D(p̂‖q_θ)→min, — це РІВНО максимізація правдоподібності (бо H(p̂) стала).
def fig_mle():
    W, H = 720, 320
    ox, oy = 90, 240
    aw, ah = 540, 180
    p = []
    p.append(arrow(ox, oy, ox, oy - ah - 12, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox + aw, oy, color=INK, sw=1.6))
    p.append(text(ox + aw - 6, oy + 22, "θ — параметр моделі q_θ", size=11, color=INK,
                  italic=True, anchor="end"))

    # дві криві спільного мінімуму: D(p̂‖q_θ) і −logL/N зсунуті на H(p̂)
    def U(t):  # параболічна «яма»
        return (t - 0.58) ** 2

    cmax = 0.62
    shift = 0.30  # = H(p̂), стала
    # D — від нуля
    ptsD = []
    ptsL = []
    n = 200
    for i in range(n + 1):
        t = i / n
        d = U(t) * 1.7
        ptsD.append("%.1f,%.1f" % (ox + t * aw, oy - min(d, cmax) / cmax * ah))
        ptsL.append("%.1f,%.1f" % (ox + t * aw, oy - min(d + shift, cmax) / cmax * ah))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8" '
             'stroke-linejoin="round"/>' % (" ".join(ptsD), GOLD))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round" stroke-dasharray="6 4"/>' % (" ".join(ptsL), NEG))

    # спільний мінімум
    tm = 0.58
    p.append(line(ox + tm * aw, oy - ah - 6, ox + tm * aw, oy, color=FIELD, sw=1.6, dash="4 4"))
    p.append(circle(ox + tm * aw, oy - U(tm) * 1.7 / cmax * ah, 4, fill=GOLD, stroke=GOLD, sw=1))
    p.append(text(ox + tm * aw, oy + 16, "θ*", size=11, color=FIELD, bold=True))
    p.append(text(ox + tm * aw + 8, oy - ah + 14, "спільний мінімум", size=10,
                  color=FIELD, bold=True, anchor="start"))

    p.append(text(ox + 14, oy - U(0.05) * 1.7 / cmax * ah - 6, "D(p̂ ‖ q_θ)",
                  size=11, color=GOLD, bold=True, anchor="start"))
    p.append(text(ox + 14, oy - (U(0.05) * 1.7 + shift) / cmax * ah - 6,
                  "−(1/N)·log L(θ)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(text(W / 2, oy + 52,
                  "криві різняться лише сталою H(p̂) — мінімум той самий: мінімізувати KL = максимізувати правдоподібність",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "mle.svg"), W, H, *p,
           title="Мінімум розбіжності = максимум правдоподібності")


if __name__ == "__main__":
    # базова
    fig_extra_bits()
    fig_asymmetry()
    fig_cross_entropy()
    fig_gibbs()
    # детальна
    fig_jensen()
    fig_forward_reverse()
    fig_mle()
    print("OK: figures written to", OUT)
