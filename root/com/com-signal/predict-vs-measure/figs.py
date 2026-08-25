# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори ролей (єдині для всіх фігур теми):
PRED = NEG          # передбачення — холодне синє
MEAS = FIELD        # вимір давача — зелене
BLEND = POS         # сплав/оцінка — гаряче червоне


def gauss_path(ox, oy, axw, mu, sigma, peak, color, sw=2.4, dash=None,
               x0=0.0, x1=1.0, n=160, fill=None):
    """Дзвоноподібна крива на осі положення [x0..x1] (нормовані одиниці).
    ox,oy — початок осі (низ-зліва); axw — піксельна ширина осі; peak — піксельна
    висота для піку sigma-кривої з амплітудою 1. Повертає <polyline> (та опційно
    напівпрозору заливку під кривою)."""
    pts = []
    for i in range(n + 1):
        xu = x0 + (x1 - x0) * i / n
        y = math.exp(-0.5 * ((xu - mu) / sigma) ** 2)
        px = ox + (xu - x0) / (x1 - x0) * axw
        py = oy - y * peak
        pts.append((px, py))
    poly = ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round"%s/>'
            % (" ".join("%.1f,%.1f" % p for p in pts), color, sw,
               (' stroke-dasharray="%s"' % dash) if dash else ''))
    if fill:
        area = "%.1f,%.1f " % (pts[0][0], oy) + " ".join("%.1f,%.1f" % p for p in pts) + " %.1f,%.1f" % (pts[-1][0], oy)
        return ('<polygon points="%s" fill="%s" fill-opacity="0.12" stroke="none"/>' % (area, color)) + poly
    return poly


def axis(ox, oy, axw, label="положення"):
    return [arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6),
            text(ox + axw, oy + 20, label, size=12, color=INK, italic=True, anchor="end")]


# ── 1. disagree: дві хмари розходяться, між ними «?» ──────────────────────────
def fig_disagree():
    W, H = 700, 320
    ox, oy = 70, 250
    axw = 560
    peak = 168
    p = list(axis(ox, oy, axw))

    p.append(gauss_path(ox, oy, axw, mu=0.34, sigma=0.085, peak=peak, color=PRED, fill=True))
    p.append(gauss_path(ox, oy, axw, mu=0.66, sigma=0.085, peak=peak, color=MEAS, fill=True))

    # центри-позначки
    for mu, col, lab, dy in ((0.34, PRED, "передбачення", -8), (0.66, MEAS, "вимір", -8)):
        cx = ox + mu * axw
        p.append(line(cx, oy, cx, oy - peak, color=col, sw=1.0, dash="3 3"))
        p.append(text(cx, oy - peak + dy, lab, size=12, color=col, bold=True))

    # знак питання посередині
    midx = ox + 0.5 * axw
    p.append(text(midx, oy - peak * 0.5, "?", size=34, color=INK, bold=True))

    # підписи «що значить хмара»
    p.append(text(ox + 6, oy - peak - 4, "центр — найімовірніше · ширина — невпевненість",
                  size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "disagree.svg"), W, H, *p,
           title="Двоє свідків розходяться: кому й наскільки вірити?")


# ── 2. weighted-blend: сплав тягнеться до певнішого (дві панелі) ──────────────
def fig_weighted_blend():
    W, H = 700, 360
    p = []
    axw = 250
    peak = 118

    def panel(ox, oy, sig_meas, title, note):
        out = list(axis(ox, oy, axw, label="положення"))
        out.append(text(ox + axw / 2, oy - peak - 30, title, size=12, color=INK, bold=True))
        mu_p, sig_p = 0.30, 0.10
        mu_m = 0.72
        # сплав: обернено-дисперсійне зважування центрів і звуження ширини
        wp, wm = 1.0 / sig_p ** 2, 1.0 / sig_meas ** 2
        mu_b = (wp * mu_p + wm * mu_m) / (wp + wm)
        sig_b = math.sqrt(1.0 / (wp + wm))
        out.append(gauss_path(ox, oy, axw, mu_p, sig_p, peak, PRED, sw=2.0))
        out.append(gauss_path(ox, oy, axw, mu_m, sig_meas, peak, MEAS, sw=2.0))
        out.append(gauss_path(ox, oy, axw, mu_b, sig_b, peak, BLEND, sw=2.8, fill=True))
        out.append(line(ox + mu_b * axw, oy, ox + mu_b * axw, oy - peak, color=BLEND, sw=1.0, dash="3 3"))
        out.append(text(ox + axw / 2, oy + 38, note, size=10, color=MUTED))
        return out

    p += panel(60, 150, 0.05, "вимір точний (вузька зелена)", "сплав лягає близько до виміру")
    p += panel(390, 150, 0.18, "вимір шумний (широка зелена)", "сплав майже не зрушується з передбачення")

    # легенда
    ly = H - 22
    p.append(line(70, ly, 96, ly, color=PRED, sw=2.4)); p.append(text(102, ly + 4, "передбачення", size=10, color=PRED, anchor="start", bold=True))
    p.append(line(250, ly, 276, ly, color=MEAS, sw=2.4)); p.append(text(282, ly + 4, "вимір", size=10, color=MEAS, anchor="start", bold=True))
    p.append(line(360, ly, 386, ly, color=BLEND, sw=2.8)); p.append(text(392, ly + 4, "сплав (вужчий за обидва)", size=10, color=BLEND, anchor="start", bold=True))

    render(os.path.join(OUT, "weighted-blend.svg"), W, H, *p,
           title="Сплав тягнеться до певнішого — і виходить вужчим за обидва")


# ── 3. gain: підсилення K як регулятор довіри ────────────────────────────────
def fig_gain():
    W, H = 700, 300
    p = []
    bx, by, bw = 90, 150, 520           # шкала K
    # шкала-смуга 0..1
    p.append(line(bx, by, bx + bw, by, color=INK, sw=2.2))
    for frac, lab in ((0.0, "0"), (0.5, "0.5"), (1.0, "1")):
        x = bx + frac * bw
        p.append(line(x, by - 7, x, by + 7, color=INK, sw=1.8))
        p.append(text(x, by + 24, lab, size=11, color=INK))
    p.append(text(bx, by - 22, "вірю передбаченню", size=11, color=PRED, anchor="start", bold=True))
    p.append(text(bx + bw, by - 22, "вірю виміру", size=11, color=MEAS, anchor="end", bold=True))

    # повзунок K у проміжному положенні
    kx = bx + 0.62 * bw
    p.append(circle(kx, by, 9, fill="#fdecea", stroke=BLEND, sw=2.4))
    p.append(text(kx, by - 30, "K", size=15, color=BLEND, bold=True))

    # стрілки «куди тягне K»
    p.append(arrow(bx + 0.30 * bw, by + 52, bx + 0.06 * bw, by + 52, color=PRED, sw=1.7))
    p.append(text(bx + 0.32 * bw, by + 56, "шумний вимір тягне K → 0", size=10, color=PRED, anchor="start"))
    p.append(arrow(bx + 0.70 * bw, by + 78, bx + 0.96 * bw, by + 78, color=MEAS, sw=1.7))
    p.append(text(bx + 0.68 * bw, by + 82, "точний вимір тягне K → 1", size=10, color=MEAS, anchor="end"))

    # формула
    f, fw, fh = textbox(W / 2, H - 26, "K = σ²передб / (σ²передб + σ²вим)",
                        size=13, bold=True, fill="#f6f4ec", stroke=INK, sw=1.6, pad=10)
    p.append(f)

    render(os.path.join(OUT, "gain.svg"), W, H, *p,
           title="Підсилення K — самоналаштовний регулятор довіри")


# ── 4. shrink: цикл «передбач → виправ» звужує хмару ──────────────────────────
def fig_shrink():
    W, H = 700, 340
    p = []
    # ліворуч: дві широкі хмари → вузька
    ox, oy = 60, 210
    axw = 330
    peak = 120
    p += axis(ox, oy, axw)
    p.append(gauss_path(ox, oy, axw, 0.34, 0.11, peak, PRED, sw=2.0))
    p.append(gauss_path(ox, oy, axw, 0.62, 0.10, peak, MEAS, sw=2.0))
    p.append(gauss_path(ox, oy, axw, 0.49, 0.062, peak, BLEND, sw=2.8, fill=True))
    p.append(text(ox + axw / 2, oy - peak - 10, "після корекції хмара вужча — певність зросла",
                  size=11, color=BLEND, bold=True))
    p.append(text(ox + 0.20 * axw, oy - 0.30 * peak, "передбачення", size=10, color=PRED))
    p.append(text(ox + 0.80 * axw, oy - 0.30 * peak, "вимір", size=10, color=MEAS, anchor="end"))

    # праворуч: петля передбач → виправ
    cx, cy = 540, 150
    b1, w1, h1 = textbox(cx, cy - 56, "передбач\n(хмара ширшає)", size=11, bold=True,
                         fill="#eaf0fd", stroke=PRED, sw=1.8, color=PRED)
    b2, w2, h2 = textbox(cx, cy + 56, "виправ виміром\n(хмара вужчає)", size=11, bold=True,
                         fill="#eafaf0", stroke=MEAS, sw=1.8, color=MEAS)
    # дуги-стрілки по колу
    p.append(arrow(cx + w1 / 2, cy - 56, cx + w2 / 2 + 8, cy + 40, color=INK, sw=1.7))
    p.append(arrow(cx - w2 / 2, cy + 56, cx - w1 / 2 - 8, cy - 40, color=INK, sw=1.7))
    p.append(b1)
    p.append(b2)
    p.append(text(cx, H - 26, "сотні обертів на секунду", size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "shrink.svg"), W, H, *p,
           title="Цикл замикається: тісніша оцінка живить наступне передбачення")


# ── 5. precision-add: точність (1/σ²) додається — сплав вужчий і вищий ─────────
def fig_precision_add():
    W, H = 720, 440
    p = []

    # --- Панель А: нормовані густини (вужча крива — вища) ---
    ox, oy = 90, 210
    axw = 500
    base = 86            # піксельна висота найширшої (передбачення) кривої
    sig_p, mu_p = 0.130, 0.36
    sig_m, mu_m = 0.100, 0.60
    # обернено-дисперсійне зважування центрів і додавання точностей
    prec_p, prec_m = 1.0 / sig_p ** 2, 1.0 / sig_m ** 2
    prec_f = prec_p + prec_m
    sig_f = math.sqrt(1.0 / prec_f)
    mu_f = (prec_p * mu_p + prec_m * mu_m) / prec_f
    # висота кожної кривої ∝ 1/σ (нормована густина: вужча — вища)
    peak_p = base
    peak_m = base * sig_p / sig_m
    peak_f = base * sig_p / sig_f

    p += axis(ox, oy, axw, label="положення")
    p.append(gauss_path(ox, oy, axw, mu_p, sig_p, peak_p, PRED, sw=2.0))
    p.append(gauss_path(ox, oy, axw, mu_m, sig_m, peak_m, MEAS, sw=2.0))
    p.append(gauss_path(ox, oy, axw, mu_f, sig_f, peak_f, BLEND, sw=2.8, fill=True))
    # тонка вертикаль до піка сплаву + підпис збоку, щоб не накладати на криві
    p.append(line(ox + mu_f * axw, oy, ox + mu_f * axw, oy - peak_f, color=BLEND, sw=1.0, dash="3 3"))
    p.append(text(ox + mu_f * axw + 8, oy - peak_f + 4,
                  "сплав: вищий і вужчий за обидва", size=11, color=BLEND, anchor="start", bold=True))
    p.append(text(ox + mu_p * axw - 10, oy - peak_p - 8, "передбачення", size=10, color=PRED, anchor="end"))
    p.append(text(ox + mu_m * axw + 40, oy - peak_m - 6, "вимір", size=10, color=MEAS, anchor="start"))

    # --- Панель Б: смуги точності (1/σ²) додаються ---
    p.append(text(ox, 268, "точність (обернена дисперсія 1/σ²) свідчень ДОДАЄТЬСЯ:",
                  size=12, color=INK, anchor="start", bold=True))
    bx = 300                       # ліва межа смуг
    scale = 380.0 / prec_f         # px на одиницю точности
    bh = 20
    lp, lm = prec_p * scale, prec_m * scale
    rows = [
        (300, "1/σ²передбачення", [(PRED, lp)]),
        (338, "1/σ²виміру",       [(MEAS, lm)]),
        (376, "1/σ²оцінки (сума)", [(PRED, lp), (MEAS, lm)]),
    ]
    for ry, lab, segs in rows:
        p.append(text(bx - 12, ry + bh * 0.72, lab, size=11, color=INK, anchor="end"))
        cx = bx
        for col, wseg in segs:
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" '
                     'fill-opacity="0.85" stroke="%s" stroke-width="1.2"/>' % (cx, ry, wseg, bh, col, col))
            cx += wseg
        if len(segs) > 1:   # рамка навколо суми
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="none" '
                     'stroke="%s" stroke-width="2.4"/>' % (bx, ry, cx - bx, bh, BLEND))

    render(os.path.join(OUT, "precision-add.svg"), W, H, *p,
           title="Незалежні свідчення додають точність — сплав певніший за обидва")


# ── 6. sawtooth: невпевненість у часі — росте на передбаченні, падає на вимірі ──
def fig_sawtooth():
    W, H = 720, 360
    p = []
    ox, oy = 80, 292           # початок осей (низ-зліва)
    axw, axh = 570, 214
    T, SMAX = 10.5, 1.5

    def X(t): return ox + t / T * axw
    def Y(s): return oy - s / SMAX * axh

    # осі
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    p.append(text(ox + axw, oy + 22, "час →", size=12, color=INK, anchor="end", italic=True))
    p.append(text(ox - 8, oy - axh + 4, "невпевненість σ", size=12, color=INK, anchor="end", italic=True))

    # штрихова «самий лише прогноз — дрейф без меж»
    p.append(line(X(0), Y(0.30), X(10.5), Y(1.42), color=MUTED, sw=1.8, dash="6 5"))
    p.append(text(X(7.4), Y(1.18), "самий прогноз — дрейф без меж",
                  size=11, color=MUTED, anchor="middle", italic=True))

    # пилка: підйоми (передбачення, синє) і падіння (корекція, зелене)
    peaks = [0.72, 0.68, 0.66, 0.65]
    corrs = [0.33, 0.31, 0.30, 0.30]
    s0 = 0.30
    t = 0.0
    cur = s0
    events = []
    for i in range(4):
        t2 = t + 2.0
        p.append(line(X(t), Y(cur), X(t2), Y(peaks[i]), color=PRED, sw=2.6))   # підйом
        p.append(line(X(t2), Y(peaks[i]), X(t2), Y(corrs[i]), color=MEAS, sw=2.6))  # падіння
        events.append(t2)
        cur = corrs[i]
        t = t2
    # хвіст останнього підйому
    p.append(line(X(t), Y(cur), X(10.5), Y(0.56), color=PRED, sw=2.6))

    # позначки вимірів на осі часу
    for te in events:
        p.append(line(X(te), oy - 4, X(te), oy + 4, color=MEAS, sw=1.6))
    # підписи ролей (осторонь ліній)
    p.append(text(X(1.0), Y(0.86), "передбач: хмара ширшає", size=11, color=PRED, anchor="middle", bold=True))
    p.append(text(X(2.05), Y(0.20), "вимір:", size=11, color=MEAS, anchor="middle", bold=True))
    p.append(text(X(2.05), Y(0.09), "хмара вужчає", size=11, color=MEAS, anchor="middle", bold=True))
    p.append(text(X(6.6), Y(0.15), "корекції тримають σ обмеженою", size=11, color=INK, anchor="middle"))

    render(os.path.join(OUT, "sawtooth.svg"), W, H, *p,
           title="Невпевненість у часі: передбачення її роздуває, вимір — стискає")


# ── 7. variance-parabola: σ²(w) — опукла парабола з дном у w* ─────────────────
def fig_variance_parabola():
    W, H = 700, 400
    p = []
    ox, oy = 100, 322          # початок осей (низ-зліва)
    axw, axh = 500, 250
    VA, VB = 4.0, 1.0          # σ²_пер, σ²_вим (числа наскрізного прикладу)
    VMAX = 4.6
    wstar = VB / (VA + VB)             # 0.2
    vopt = VA * VB / (VA + VB)         # 0.8

    def X(w): return ox + w * axw
    def Y(v): return oy - v / VMAX * axh
    def sig2(w): return w * w * VA + (1 - w) * (1 - w) * VB

    # осі
    p.append(arrow(ox, oy, ox + axw + 18, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - axh - 18, color=INK, sw=1.6))
    p.append(text(ox + axw + 16, oy + 24, "w — вага передбачення", size=12, color=INK, anchor="end", italic=True))
    p.append(text(ox - 6, oy - axh - 6, "σ² оцінки", size=12, color=INK, anchor="end", italic=True))

    # позначки w на осі
    for wv, lab, col, bold in ((0.0, "0", INK, False), (wstar, "w*", BLEND, True), (1.0, "1", INK, False)):
        p.append(line(X(wv), oy - 4, X(wv), oy + 4, color=INK, sw=1.4))
        p.append(text(X(wv), oy + 22, lab, size=12, color=col, bold=bold))
    p.append(text(X(wstar), oy + 42, "w* = σ²_вим/(σ²_пер+σ²_вим) = 0.2", size=10, color=BLEND))

    # крива параболи
    pts = [(X(i / 120.0), Y(sig2(i / 120.0))) for i in range(121)]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round"/>' % (" ".join("%.1f,%.1f" % q for q in pts), INK))

    # кінці параболи: чистий вимір і чисте передбачення
    p.append(circle(X(0.0), Y(VB), 4.5, fill=MEAS, stroke=MEAS, sw=1.5))
    p.append(text(X(0.0) + 10, Y(VB) - 12, "лише вимір: σ²=σ²_вим=1.0", size=10, color=MEAS, anchor="start"))
    p.append(circle(X(1.0), Y(VA), 4.5, fill=PRED, stroke=PRED, sw=1.5))
    p.append(text(X(1.0) - 10, Y(VA) - 12, "лише передбачення: σ²=σ²_пер=4.0", size=10, color=PRED, anchor="end"))

    # дно параболи
    p.append(line(X(wstar), oy, X(wstar), Y(vopt), color=BLEND, sw=1.2, dash="4 3"))
    p.append(line(ox, Y(vopt), X(wstar), Y(vopt), color=BLEND, sw=1.2, dash="4 3"))
    p.append(line(X(wstar) - 48, Y(vopt), X(wstar) + 48, Y(vopt), color=BLEND, sw=1.8))  # дотична: нахил=0
    p.append(circle(X(wstar), Y(vopt), 6, fill="#fdecea", stroke=BLEND, sw=2.4))
    p.append(text(X(wstar) + 56, Y(vopt) + 4, "нахил = 0  →  дно (мінімум)", size=10, color=BLEND, anchor="start", bold=True))
    p.append(text(ox - 8, Y(vopt) + 4, "σ²_опт", size=11, color=BLEND, anchor="end", bold=True))

    # формула-підпис у вільному верхньому куті
    f, _, _ = textbox(ox + axw * 0.70, oy - axh * 0.80,
                      "σ²(w) = w²·σ²_пер + (1−w)²·σ²_вим", size=12, bold=True,
                      fill="#f6f4ec", stroke=INK, sw=1.4, pad=9)
    p.append(f)

    render(os.path.join(OUT, "variance-parabola.svg"), W, H, *p,
           title="Дисперсія сплаву — опукла парабола від ваги; дно = оптимум")


# ── 8. precision-lever: оцінка = точка рівноваги мас-точностей ────────────────
def fig_precision_lever():
    W, H = 700, 400
    p = []
    ox, axw = 100, 500
    lo, hi = 8.0, 18.0
    beamY = 148

    def X(pos): return ox + (pos - lo) / (hi - lo) * axw

    a, VA = 10.0, 4.0          # передбачення, σ²_пер
    b, VB = 16.0, 1.0          # вимір, σ²_вим
    ma, mb = 1.0 / VA, 1.0 / VB        # маси = точності: 0.25 і 1.0
    m = (ma * a + mb * b) / (ma + mb)  # 14.8 — точка рівноваги

    # вісь положення (внизу)
    ay = 262
    p.append(line(ox - 10, ay, ox + axw + 10, ay, color=MUTED, sw=1.2))
    for pos in range(8, 19, 2):
        p.append(line(X(pos), ay - 4, X(pos), ay + 4, color=MUTED, sw=1.0))
        p.append(text(X(pos), ay + 18, str(pos), size=9, color=MUTED))
    p.append(text(ox + axw + 10, ay + 34, "положення", size=10, color=MUTED, anchor="end", italic=True))

    # балка-важіль
    p.append(line(X(a) - 26, beamY, X(b) + 26, beamY, color=INK, sw=4))

    # маси-точності (площа кружка ∝ маса: r ∝ √маса, тож r_вим = 2·r_пер)
    def mass_circle(pos, r, col):
        cx = X(pos)
        cy = beamY + 20 + r
        p.append(line(cx, beamY, cx, cy - r, color=col, sw=1.4))
        p.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.28" '
                 'stroke="%s" stroke-width="1.8"/>' % (cx, cy, r, col, col))
        return cx, cy

    cxa, cya = mass_circle(a, 15, PRED)
    cxb, cyb = mass_circle(b, 30, MEAS)

    # опора-трикутник під точкою рівноваги
    fx = X(m)
    p.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>'
             % (fx, beamY + 2, fx - 15, beamY + 30, fx + 15, beamY + 30, BLEND))

    # верхні підписи (над балкою, лише над масами — далеко від опори)
    p.append(text(X(a), beamY - 38, "передбачення", size=11, color=PRED, bold=True))
    p.append(text(X(a), beamY - 24, "a = 10", size=11, color=PRED))
    p.append(text(X(b), beamY - 38, "вимір", size=11, color=MEAS, bold=True))
    p.append(text(X(b), beamY - 24, "b = 16", size=11, color=MEAS))

    # значення мас усередині кружків + підписи знизу
    p.append(text(cxa, cya + 4, "0.25", size=11, color=PRED, bold=True))
    p.append(text(cxb, cyb + 5, "1.0", size=14, color=MEAS, bold=True))
    p.append(text(cxa, cya + 30, "маса = 1/σ²_пер", size=10, color=PRED))
    p.append(text(cxb, cyb + 46, "маса = 1/σ²_вим", size=10, color=MEAS))

    # анотація опори — виноскою у вільну зону між масами
    p.append(line(fx, beamY + 30, 372, 216, color=BLEND, sw=1.0))
    p.append(text(332, 224, "опора: оцінка m = 14.8", size=11, color=BLEND, bold=True))
    p.append(text(332, 238, "(точка рівноваги важеля)", size=10, color=BLEND))

    # формула центру мас
    f, _, _ = textbox(W / 2, H - 34,
                      "m = (a·1/σ²_пер + b·1/σ²_вим) / (1/σ²_пер + 1/σ²_вим)   — центр мас точностей",
                      size=12, bold=True, fill="#f6f4ec", stroke=INK, sw=1.4, pad=9)
    p.append(f)

    render(os.path.join(OUT, "precision-lever.svg"), W, H, *p,
           title="Оптимальна оцінка = точка рівноваги мас-точностей")


# ── Спільна симуляція трекера (детермінований ГВЧ, як у C-демо) ───────────────
def _sim(N=48, seed=0x2545F4914F6CDD1D):
    dt, v, q, r = 1.0, 1.0, 0.25, 9.0
    sp, sm = 0.5, 3.0
    st = [seed]
    def urand():
        s = st[0]
        s ^= (s << 13) & 0xFFFFFFFFFFFFFFFF
        s ^= (s >> 7)
        s ^= (s << 17) & 0xFFFFFFFFFFFFFFFF
        st[0] = s
        return ((s >> 11) + 1.0) * (1.0 / 9007199254740992.0)
    def gauss(sig):
        u1, u2 = urand(), urand()
        return sig * math.sqrt(-2.0 * math.log(u1)) * math.cos(6.283185307179586 * u2)
    xt, x, p, xd = 0.0, -20.0, 100.0, -20.0
    T, Z, X, D, K, Ppre, Ppost = [], [], [], [], [], [], []
    se_t = se_r = se_d = 0.0
    for _ in range(N):
        xt += v * dt + gauss(sp)
        z = xt + gauss(sm)
        x += v * dt; p += q; Ppre.append(p)          # передбачення роздуло p
        k = p / (p + r); x += k * (z - x); p = (1.0 - k) * p
        xd += v * dt
        T.append(xt); Z.append(z); X.append(x); D.append(xd)
        K.append(k); Ppost.append(p)
        se_t += (x - xt) ** 2; se_r += (z - xt) ** 2; se_d += (xd - xt) ** 2
    rms = (math.sqrt(se_t / N), math.sqrt(se_r / N), math.sqrt(se_d / N))
    return dict(T=T, Z=Z, X=X, D=D, K=K, Ppre=Ppre, Ppost=Ppost, rms=rms, N=N)


# ── tracker-run: істина, зашумлені виміри, трекер, самий прогноз ──────────────
def fig_tracker_run():
    W, H = 760, 430
    s = _sim(N=48)
    N = s["N"]
    ox, oy, axw, axh = 74, 356, 620, 300
    ymin, ymax = -26.0, 52.0

    def X(k): return ox + k / (N - 1) * axw
    def Y(val): return oy - (val - ymin) / (ymax - ymin) * axh

    p = []
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.6))
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.6))
    p.append(text(ox + axw, oy + 24, "такт →", size=12, color=INK, anchor="end", italic=True))
    p.append(text(ox - 8, oy - axh + 2, "положення, м", size=12, color=INK, anchor="end", italic=True))
    p.append(line(ox, Y(0), ox + axw, Y(0), color=MUTED, sw=0.8, dash="2 4"))
    p.append(text(ox - 8, Y(0) + 4, "0", size=10, color=MUTED, anchor="end"))

    def poly(vals, col, sw, dash=None):
        pts = " ".join("%.1f,%.1f" % (X(k), Y(vals[k])) for k in range(N))
        return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f" '
                'stroke-linejoin="round"%s/>'
                % (pts, col, sw, (' stroke-dasharray="%s"' % dash) if dash else ''))

    p.append(poly(s["T"], INK, 2.2))
    p.append(poly(s["D"], PRED, 2.0, dash="7 5"))
    for k in range(N):
        p.append(circle(X(k), Y(s["Z"][k]), 2.6, fill=MEAS, stroke=MEAS, sw=0.6))
    p.append(poly(s["X"], BLEND, 2.8))

    p.append(text(X(1) + 4, Y(-20) + 4, "хибний старт (−20 м)", size=10, color=MUTED, anchor="start"))
    p.append(arrow(X(2.2), Y(-16), X(3.2), Y(-3), color=BLEND, sw=1.6))
    p.append(text(X(4.2), Y(-9), "трекер стрибає на виміри й наздоганяє", size=10, color=BLEND, anchor="start"))
    p.append(text(X(46), Y(s["D"][46]) - 8, "самий прогноз лишився з похибкою старту", size=10, color=PRED, anchor="end"))

    lx, ly = ox + 6, oy - axh + 18
    for col, lab, dx in [(INK, "істина", 0), (MEAS, "зашумлений вимір", 128), (BLEND, "трекер", 300), (PRED, "самий прогноз", 384)]:
        p.append(line(lx + dx, ly, lx + dx + 22, ly, color=col, sw=2.6))
        p.append(text(lx + dx + 27, ly + 4, lab, size=10, color=col, anchor="start", bold=True))

    render(os.path.join(OUT, "tracker-run.svg"), W, H, *p,
           title="Трекер приборкує шум: гладка оцінка тримається істини, самий прогноз дрейфує")


# ── kp-flow: K сам перетікає (верх) · p дихає пилкою (низ) ─────────────────────
def fig_kp_flow():
    W, H = 760, 470
    s = _sim(N=48)
    K, Ppre, Ppost = s["K"], s["Ppre"], s["Ppost"]
    p = []

    ox, oy, axw, axh = 78, 210, 610, 150
    Nk = 24
    def XA(k): return ox + k / (Nk - 1) * axw
    def YA(v): return oy - v / 1.0 * axh
    p.append(arrow(ox, oy, ox + axw, oy, color=INK, sw=1.5))
    p.append(arrow(ox, oy, ox, oy - axh, color=INK, sw=1.5))
    p.append(text(ox + axw, oy + 22, "такт →", size=11, color=INK, anchor="end", italic=True))
    for gv in (0.0, 0.5, 1.0):
        p.append(line(ox - 4, YA(gv), ox, YA(gv), color=INK, sw=1.2))
        p.append(text(ox - 8, YA(gv) + 4, "%.1f" % gv, size=10, color=INK, anchor="end"))
    p.append(text(ox + axw / 2, oy - axh - 10, "підсилення K", size=12, color=BLEND, bold=True))
    pts = " ".join("%.1f,%.1f" % (XA(k), YA(K[k])) for k in range(Nk))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts, BLEND))
    for k in range(Nk):
        p.append(circle(XA(k), YA(K[k]), 2.4, fill=BLEND, stroke=BLEND, sw=0.5))
    p.append(text(XA(0) + 6, YA(K[0]) - 8, "K≈0.92: хапає виміри, щоб виправити старт", size=10, color=MUTED, anchor="start"))
    p.append(text(XA(Nk - 1), YA(K[Nk - 1]) - 12, "K→0.15: модель певна, шум відкидають", size=10, color=MUTED, anchor="end"))

    ox2, oy2, axw2, axh2 = 78, 430, 610, 130
    k0, k1 = 18, 30
    lo, hi = 1.30, 1.72
    def XB(k): return ox2 + (k - k0) / (k1 - k0) * axw2
    def YB(v): return oy2 - (v - lo) / (hi - lo) * axh2
    p.append(arrow(ox2, oy2, ox2 + axw2, oy2, color=INK, sw=1.5))
    p.append(arrow(ox2, oy2, ox2, oy2 - axh2, color=INK, sw=1.5))
    p.append(text(ox2 + axw2, oy2 + 22, "такт →", size=11, color=INK, anchor="end", italic=True))
    for gv in (1.38, 1.63):
        p.append(line(ox2 - 4, YB(gv), ox2, YB(gv), color=INK, sw=1.2))
        p.append(text(ox2 - 8, YB(gv) + 4, "%.2f" % gv, size=10, color=INK, anchor="end"))
    p.append(text(ox2 + axw2 / 2, oy2 - axh2 - 10, "дисперсія оцінки p (масштаб зближено)", size=12, color=INK, bold=True))
    for k in range(k0, k1):
        p.append(line(XB(k), YB(Ppost[k - 1]), XB(k), YB(Ppre[k]), color=PRED, sw=2.4))
        p.append(line(XB(k), YB(Ppre[k]), XB(k + 1), YB(Ppost[k]), color=MEAS, sw=2.4))
    p.append(text(XB(k0 + 1.2), YB(1.70), "передбач роздуває (+q)", size=10, color=PRED, anchor="start"))
    p.append(text(XB(k0 + 1.2), YB(1.335), "вимір стискає ×(1−K)", size=10, color=MEAS, anchor="start"))

    render(os.path.join(OUT, "kp-flow.svg"), W, H, *p,
           title="K сам перетікає з певністю · p дихає пилкою: роздув на такті, стиск на вимірі")


# ── rms-bars: похибка трекера проти сирого виміру й самого прогнозу ────────────
def fig_rms_bars():
    W, H = 748, 300
    s = _sim(N=100)
    trk, raw, dead = s["rms"]
    p = []
    bx, by, bw = 250, 70, 380
    rowh, gap = 46, 26
    vmax = dead * 1.08
    for i, (col, lab, val) in enumerate([(BLEND, "трекер", trk), (MEAS, "сирий вимір", raw), (PRED, "самий прогноз", dead)]):
        ry = by + i * (rowh + gap)
        wpx = val / vmax * bw
        p.append(text(bx - 14, ry + rowh * 0.62, lab, size=13, color=col, anchor="end", bold=True))
        p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" fill="%s" '
                 'fill-opacity="0.85" stroke="%s" stroke-width="1.4"/>' % (bx, ry, wpx, rowh, col, col))
        p.append(text(bx + wpx + 10, ry + rowh * 0.62, "%.2f м" % val, size=13, color=col, anchor="start", bold=True))
    p.append(text(bx + bw / 2, by + 3 * (rowh + gap) + 6,
                  "середньоквадратична похибка за 100 тактів (менше — краще)",
                  size=11, color=MUTED))
    render(os.path.join(OUT, "rms-bars.svg"), W, H, *p,
           title="Хто ближчий до істини: трекер удвічі точніший за сирий вимір, прогноз — геть мимо")


# ── estimation-timeline (hist): від пакета Гаусса до рекурсивної петлі ─────────
def fig_estimation_timeline():
    W, H = 960, 380
    sy = 200                       # рівень смуги часу
    p = []

    # дві доби: тло-смуги (пакетна ліворуч, рекурсивна праворуч)
    split = 279.0
    p.append('<rect x="40" y="66" width="%.1f" height="252" rx="10" fill="%s" fill-opacity="0.10"/>'
             % (split - 40, PRED))
    p.append('<rect x="%.1f" y="66" width="%.1f" height="252" rx="10" fill="%s" fill-opacity="0.10"/>'
             % (split, 916 - split, BLEND))
    p.append(line(split, 74, split, 312, color=MUTED, sw=1.2, dash="5 5"))

    # заголовки діб
    p.append(text(160, 40, "ПАКЕТНА ДОБА", size=14, color=PRED, bold=True))
    p.append(text(160, 58, "увесь ряд разом", size=11, color=MUTED, italic=True))
    p.append(text(600, 40, "РЕКУРСИВНИЙ ПОВОРОТ", size=14, color=BLEND, bold=True))
    p.append(text(600, 58, "стан уперед — стала робота на такт", size=11, color=MUTED, italic=True))

    # смуга часу
    p.append(arrow(52, sy, 928, sy, color=INK, sw=1.8))
    p.append(text(926, sy - 12, "час →", size=12, color=INK, anchor="end", italic=True))

    # вузли: (year, name, role, side, color, r)
    nodes = [
        ("1801", "Гаусс", "орбіта Церери", "up", INK, 7),
        ("1805", "Лежандр", "друк МНК", "dn", MUTED, 6),
        ("1880", "Тіле", "рекурсія — забута", "up", MUTED, 6),
        ("1941–42", "Колмогоров·Вінер", "оптимальна, частотна", "dn", PRED, 7),
        ("1958", "Сверлінг", "майже рекурсія", "up", PRED, 7),
        ("1960", "Калман", "простір станів", "dn", BLEND, 11),
        ("1969", "Аполлон", "фільтр на борту", "up", MEAS, 8),
    ]
    xl, xr = 90.0, 900.0
    n = len(nodes)
    for i, (yr, nm, role, side, col, r) in enumerate(nodes):
        x = xl + (xr - xl) * i / (n - 1)
        if side == "up":
            p.append(line(x, sy - r, x, sy - 30, color=col, sw=1.3))
            p.append(text(x, sy - 40, yr, size=13, color=col, bold=True))
            p.append(text(x, sy - 57, nm, size=12, color=col, bold=True))
            p.append(text(x, sy - 73, role, size=10, color=MUTED, italic=True))
        else:
            p.append(line(x, sy + r, x, sy + 30, color=col, sw=1.3))
            p.append(text(x, sy + 46, yr, size=13, color=col, bold=True))
            p.append(text(x, sy + 63, nm, size=12, color=col, bold=True))
            p.append(text(x, sy + 79, role, size=10, color=MUTED, italic=True))
        p.append(circle(x, sy, r, fill="#ffffff", stroke=col, sw=2.6))
        if r >= 11:                # злам — заповнений вузол
            p.append(circle(x, sy, r - 4, fill=col, stroke="none"))

    # підпис зламу
    xk = xl + (xr - xl) * 5 / (n - 1)
    p.append(text(xk, sy + 98, "злам: два числа замість усієї історії", size=10, color=BLEND, bold=True))

    render(os.path.join(OUT, "estimation-timeline.svg"), W, H, *p,
           title="Від пакета Гаусса до рекурсивної петлі Калмана — сто шістдесят років дороги")


if __name__ == "__main__":
    fig_disagree()
    fig_weighted_blend()
    fig_gain()
    fig_shrink()
    fig_precision_add()
    fig_sawtooth()
    fig_variance_parabola()
    fig_precision_lever()
    fig_tracker_run()
    fig_kp_flow()
    fig_rms_bars()
    fig_estimation_timeline()
    print("OK: figures written to", OUT)
    print("RMS (trk, raw, dead) over 100 ticks:", _sim(N=100)["rms"])
