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


if __name__ == "__main__":
    fig_disagree()
    fig_weighted_blend()
    fig_gain()
    fig_shrink()
    print("OK: figures written to", OUT)
