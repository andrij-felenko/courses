# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def poly(points, color=INK, sw=2.0, fill="none"):
    pts = " ".join("%.1f,%.1f" % (x, y) for (x, y) in points)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f" '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, fill, color, sw))


def square_wave(x0, y_hi, y_lo, period_px, duty, n_periods):
    """Точки прямокутної ШІМ: high частку duty, далі low."""
    pts = [(x0, y_lo)]
    x = x0
    for _ in range(n_periods):
        on = period_px * duty
        pts.append((x, y_hi))
        pts.append((x + on, y_hi))
        pts.append((x + on, y_lo))
        pts.append((x + period_px, y_lo))
        x += period_px
    return pts


def hbrace(x1, x2, y, color=MUTED, sw=1.4, drop=6):
    """Горизонтальна дужка [ x1..x2 ] на рівні y з засічками вниз."""
    return (line(x1, y, x2, y, color=color, sw=sw)
            + line(x1, y, x1, y + drop, color=color, sw=sw)
            + line(x2, y, x2, y + drop, color=color, sw=sw))


# ── 1. Чому перемикати вигідніше, ніж гальмувати ────────────────────────────
def fig_switch_vs_linear():
    W, H = 860, 470
    frags = []

    def panel(px, title, elem_kind, load_frac, heat_frac, caption):
        pw, ph = 380, 372
        out = [rect(px, 60, pw, ph, fill=BG, stroke=LINE, sw=1.6, rx=10)]
        cx = px + 118
        out.append(fitbox(px + 16, 76, pw - 32, 30, title, size=15, bold=True,
                          fill=FILL, stroke=LINE))
        # вертикальний ланцюг: джерело -> елемент -> навантаження -> земля
        y_src, y_el, y_ld = 138, 210, 300
        out.append(fitbox(cx - 54, y_src, 108, 34, "джерело\nVdd", size=12,
                         fill="#eef2f7", stroke=LINE))
        out.append(line(cx, y_src + 34, cx, y_el, color=LINE, sw=2))
        if elem_kind == "linear":
            out.append(fitbox(cx - 60, y_el, 120, 44, "гальмівний\nелемент", size=12,
                             fill="#fdecea", stroke=POS, color=POS, bold=True))
        else:
            # ключ: два вузли й похилий контакт
            out.append(rect(cx - 60, y_el, 120, 44, fill="#eaf7ef", stroke=FIELD, sw=1.6, rx=6))
            n1x, n2x, ny = cx - 30, cx + 30, y_el + 22
            out.append(circle(n1x, ny, 3.5, fill=INK, stroke=INK))
            out.append(circle(n2x, ny, 3.5, fill=INK, stroke=INK))
            out.append(line(n1x, ny, n2x - 4, ny - 18, color=INK, sw=3))
            out.append(text(cx, y_el + 40, "ключ", size=12, color=FIELD, bold=True))
        out.append(line(cx, y_el + 44, cx, y_ld, color=LINE, sw=2))
        out.append(fitbox(cx - 54, y_ld, 108, 34, "навантаження", size=12,
                         fill="#eef2f7", stroke=LINE))
        gy = y_ld + 34 + 16
        out.append(line(cx, y_ld + 34, cx, gy, color=LINE, sw=2))
        for j, ww in enumerate((20, 13, 6)):
            out.append(line(cx - ww, gy + j * 5, cx + ww, gy + j * 5, color=LINE, sw=2))
        # анотація праворуч від елемента
        ax = px + 190
        if elem_kind == "linear":
            out.append(fitbox(ax, y_el - 6, 176, 56,
                             "спад Vdd−Vн\nпри струмі I\n→ (Vdd−Vн)·I у тепло",
                             size=11, fill="#fdecea", stroke=POS, color=POS))
        else:
            out.append(fitbox(ax, y_el - 6, 176, 56,
                             "ON: Vкл≈0 ⇒ P≈0\nOFF: I≈0 ⇒ P≈0\n→ елемент не гріється",
                             size=11, fill="#eaf7ef", stroke=FIELD, color="#1e7d44"))
        # смуга розподілу енергії
        by, bx, bw, bh = 400, px + 40, 300, 24
        wl = bw * load_frac
        out.append(rect(bx, by, wl, bh, fill=FIELD, stroke="none", rx=0))
        out.append(rect(bx + wl, by, bw - wl, bh, fill=POS, stroke="none", rx=0))
        out.append(rect(bx, by, bw, bh, fill="none", stroke=LINE, sw=1.4, rx=0))
        out.append(text(bx + wl / 2, by + 16, "у навантаження", size=10, color="#ffffff", bold=True))
        if heat_frac > 0.12:
            out.append(text(bx + wl + (bw - wl) / 2, by + 16, "у тепло", size=10, color="#ffffff", bold=True))
        out.append(text(px + pw / 2, by + 46, caption, size=12, color=INK, bold=True))
        return "".join(out)

    frags.append(panel(20, "Лінійне керування", "linear", 0.5, 0.5,
                        "≈ половина енергії — у тепло"))
    frags.append(panel(460, "Керування ШІМ (ключ)", "switch", 0.94, 0.06,
                        "майже вся енергія — у навантаження"))
    return render(os.path.join(IMG, "switch-vs-linear.svg"), W, H, *frags,
                  title="Чому ШІМ ефективна: ідеальний ключ не гріється")


# ── 2. Шпаруватість задає середнє ───────────────────────────────────────────
def fig_duty_average():
    W, H = 840, 360
    frags = []
    x0, plot_w = 120, 560
    hiY, baseY = 118, 250
    duty = 0.6
    period = plot_w / 3.0
    # рівні
    frags.append(line(x0, hiY, x0 + plot_w, hiY, color=MUTED, sw=1, dash="3,4"))
    frags.append(line(x0, baseY, x0 + plot_w, baseY, color=LINE, sw=1.5))
    frags.append(text(x0 - 12, hiY + 5, "Vdd", size=13, color=MUTED, anchor="end"))
    frags.append(text(x0 - 12, baseY + 5, "0", size=13, color=MUTED, anchor="end"))
    # сигнал
    frags.append(poly(square_wave(x0, hiY, baseY, period, duty, 3), color=NEG, sw=2.6))
    # середнє
    avgY = baseY - (baseY - hiY) * duty
    frags.append(line(x0, avgY, x0 + plot_w, avgY, color=POS, sw=2.2, dash="7,5"))
    frags.append(text(x0 + plot_w + 8, avgY + 5, "середнє = D·Vdd", size=12, color=POS, anchor="start", bold=True))
    # дужки T і t_on під першим періодом
    frags.append(hbrace(x0, x0 + period, baseY + 16, color=MUTED))
    frags.append(text(x0 + period / 2, baseY + 40, "T  (період)", size=12, color=MUTED))
    frags.append(hbrace(x0, x0 + period * duty, baseY + 62, color=FIELD))
    frags.append(text(x0 + period * duty / 2, baseY + 86, "tₒₙ", size=12, color=FIELD, bold=True))
    # виноска-формула
    frags.append(fitbox(x0 + plot_w - 500, 62, 500, 32,
                        "площа за період = Vdd·tₒₙ  →  середнє = Vdd·tₒₙ/T = Vdd·D",
                        size=13, fill=FILL, stroke=LINE, bold=True))
    return render(os.path.join(IMG, "duty-average.svg"), W, H, *frags,
                  title="Шпаруватість D = tₒₙ/T керує середнім рівнем")


# ── 3. Аналогова ШІМ: компаратор + пиляк ─────────────────────────────────────
def fig_comparator_pwm():
    import math
    W, H = 1000, 470
    frags = []
    x0, plot_w = 290, 520
    n = 6
    period = plot_w / n
    topHi, topLo = 90, 210          # рівні верхньої панелі: 1 і 0
    outHi, outLo = 320, 390

    def sig(u):
        """Повільний вхідний сигнал, нормований 0..1; u — частка вздовж вікна."""
        return 0.5 + 0.34 * math.sin(2 * math.pi * (u - 0.25))

    def yv(v):
        return topLo - (topLo - topHi) * v

    # осі верхньої панелі
    frags.append(line(x0, topHi, x0 + plot_w, topHi, color=MUTED, sw=1, dash="3,4"))
    frags.append(line(x0, topLo, x0 + plot_w, topLo, color=LINE, sw=1.4))
    frags.append(text(x0 - 14, topHi + 5, "max", size=12, color=MUTED, anchor="end"))
    frags.append(text(x0 - 14, topLo + 5, "0", size=12, color=MUTED, anchor="end"))

    # пиляк-несуча: щоперіоду лінійно 0 → 1, тоді обрив
    ramp = []
    for k in range(n):
        x = x0 + k * period
        ramp.append((x, topLo))
        ramp.append((x + period, topHi))
        ramp.append((x + period, topLo))
    frags.append(poly(ramp, color=NEG, sw=2.2))

    # вхідний сигнал
    sigpts = [(x0 + plot_w * i / 200.0, yv(sig(i / 200.0))) for i in range(201)]
    frags.append(poly(sigpts, color=POS, sw=2.6))

    # перетини «пиляк = сигнал» → фронти виходу (природна вибірка)
    out_pts = [(x0, outLo)]
    for k in range(n):
        xk = x0 + k * period
        xc = xk + period            # запобіжник, якщо перетину нема
        steps = 240
        for i in range(steps + 1):
            x = xk + period * i / steps
            if (x - xk) / period >= sig((x - x0) / plot_w):
                xc = x
                break
        frags.append(line(xc, yv((xc - xk) / period), xc, outLo, color="#c9ced6", sw=1, dash="4,4"))
        out_pts += [(xk, outHi), (xc, outHi), (xc, outLo), (xk + period, outLo)]

    # осі й сигнал нижньої панелі
    frags.append(line(x0, outHi, x0 + plot_w, outHi, color=MUTED, sw=1, dash="3,4"))
    frags.append(line(x0, outLo, x0 + plot_w, outLo, color=LINE, sw=1.4))
    frags.append(poly(out_pts, color=NEG, sw=2.6))

    # підписи праворуч, поза полем графіка
    lx = x0 + plot_w + 12
    frags.append(text(lx, topHi + 5, "пиляк (несуча)", size=12, color=NEG, anchor="start"))
    frags.append(text(lx, yv(sig(1.0)) + 5, "вхідний сигнал", size=12, color=POS, anchor="start", bold=True))
    frags.append(text(lx, (outHi + outLo) / 2 + 5, "вихід ШІМ", size=12, color=INK, anchor="start", bold=True))

    # компаратор ліворуч
    ctx, cty = 130, 250
    tri = [(ctx, cty - 34), (ctx, cty + 34), (ctx + 66, cty)]
    frags.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (" ".join("%.1f,%.1f" % p for p in tri), FILL, LINE))
    frags.append(line(46, cty - 18, ctx, cty - 18, color=POS, sw=1.8))
    frags.append(line(46, cty + 18, ctx, cty + 18, color=NEG, sw=1.8))
    frags.append(text(48, cty - 26, "вхідний сигнал", size=11, color=POS, anchor="start"))
    frags.append(text(48, cty + 34, "пиляк", size=11, color=NEG, anchor="start"))
    frags.append(text(ctx + 10, cty - 8, "+", size=17, color=POS, bold=True, anchor="start"))
    frags.append(text(ctx + 10, cty + 24, "−", size=17, color=NEG, bold=True, anchor="start"))
    frags.append(arrow(ctx + 66, cty, x0 - 16, (outHi + outLo) / 2, color=LINE, sw=1.8))
    frags.append(fitbox(24, 336, 216, 58,
                        "доки пиляк нижчий\nза сигнал — вихід угорі",
                        size=11, fill=FILL, stroke=LINE))

    # анотація до найширшого імпульсу (сигнал у максимумі)
    xw = x0 + plot_w * 0.5
    frags.append(arrow(xw, 424, xw, 396, color=FIELD, sw=1.8))
    frags.append(fitbox(xw - 150, 428, 300, 28,
                        "вищий сигнал → ширший імпульс", size=12,
                        fill="#eaf7ef", stroke=FIELD, color="#1e7d44", bold=True))
    return render(os.path.join(IMG, "comparator-pwm.svg"), W, H, *frags,
                  title="Компаратор і пиляк: рівень сигналу стає шириною імпульсу")


# ── 4. Навантаження саме усереднює (інерція) ─────────────────────────────────
def fig_load_averages():
    W, H = 820, 330
    frags = []
    midY = 190
    # ліворуч: рвана потужність
    ix, iw = 60, 190
    hiY, loY = midY - 46, midY + 20
    frags.append(text(ix + iw / 2, 74, "потужність до навантаження", size=13, bold=True))
    frags.append(poly(square_wave(ix, hiY, loY, iw / 4.0, 0.55, 4), color=NEG, sw=2.4))
    frags.append(line(ix, loY + 22, ix + iw, loY + 22, color=MUTED, sw=1, dash="3,4"))
    frags.append(text(ix + iw / 2, loY + 42, "вмик / вимик", size=11, color=MUTED))
    frags.append(arrow(ix + iw + 6, midY - 12, ix + iw + 58, midY - 12, color=LINE, sw=2))
    # посередині: інерція
    bxc = ix + iw + 64
    frags.append(fitbox(bxc, midY - 52, 150, 78,
                        "інерція\nнавантаження\n(маса ротора ·\nтепло · око)",
                        size=12, fill="#eef2f7", stroke=LINE, bold=True))
    frags.append(arrow(bxc + 150 + 6, midY - 12, bxc + 150 + 58, midY - 12, color=LINE, sw=2))
    # праворуч: гладкий ефект
    ox = bxc + 150 + 66
    ow = 190
    frags.append(text(ox + ow / 2, 74, "ефект: стала величина", size=13, bold=True))
    avgY = midY - 14
    frags.append(line(ox, avgY, ox + ow, avgY, color=POS, sw=1.8, dash="6,5"))
    # плавна крива: наростання й вихід на полицю з дрібним тремтінням
    import math
    smooth = []
    for i in range(0, 121):
        t = i / 120.0
        v = 1 - math.exp(-3.2 * t)
        y = midY + 34 - v * 48 + 2.0 * math.sin(t * 34)
        smooth.append((ox + ow * t, y))
    frags.append(poly(smooth, color=NEG, sw=2.6))
    frags.append(text(ox + ow + 8, avgY + 4, "= середнє", size=12, color=POS, anchor="start", bold=True))
    frags.append(text(ox + ow / 2, midY + 52, "швидкість · яскравість · температура", size=10, color=MUTED))
    return render(os.path.join(IMG, "load-averages.svg"), W, H, *frags,
                  title="Часто фільтр не потрібен — навантаження саме усереднює")

# ═══════════════════════════════════════════════════════════════════════════
#  Фігури до вставки math-natural-sampling.md
# ═══════════════════════════════════════════════════════════════════════════
import math as _m


def polygon(points, fill, opacity=1.0):
    pts = " ".join("%.2f,%.2f" % (x, y) for (x, y) in points)
    return ('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="none"/>'
            % (pts, fill, opacity))


def _uniform_edge(y, M, q):
    """Розв'язок x = πM·cos(y − (x+π)/q) ітерацією (відображення стискне)."""
    x = _m.pi * M * _m.cos(y)
    for _ in range(120):
        x = _m.pi * M * _m.cos(y - (x + _m.pi) / q)
    return x


# ── 5. Одиничний осередок: межа «ввімкнено» — це графік самого сигналу ──────
def fig_natural_cell():
    W, H = 1000, 580
    frags = []
    M, Q = 0.85, 5.0
    cw, ch = 300, 340
    top = 116
    ys = [-_m.pi + i * (2 * _m.pi) / 260 for i in range(261)]

    def panel(px, head, boundary, ghost, tint, note, note_color):
        out = []
        X = lambda xv: px + (xv + _m.pi) / (2 * _m.pi) * cw
        Y = lambda yv: top + ch - (yv + _m.pi) / (2 * _m.pi) * ch
        out.append(fitbox(px - 10, 62, cw + 20, 32, head, size=14, bold=True,
                          fill=FILL, stroke=LINE))
        pts = [(X(-_m.pi), Y(-_m.pi))]
        pts += [(X(boundary(y)), Y(y)) for y in ys]
        pts += [(X(-_m.pi), Y(_m.pi))]
        out.append(polygon(pts, fill=tint, opacity=0.55))
        out.append(rect(px, top, cw, ch, fill="none", stroke=LINE, sw=1.6, rx=4))
        if ghost:
            out.append(poly([(X(ghost(y)), Y(y)) for y in ys], color=MUTED, sw=1.6))
        out.append(poly([(X(boundary(y)), Y(y)) for y in ys], color=POS, sw=2.8))
        for yv in (-2.05, 0.3, 2.35):
            xb = boundary(yv)
            out.append(line(X(-_m.pi), Y(yv), X(xb), Y(yv), color=NEG, sw=2.2))
            out.append(line(X(xb), Y(yv) - 6, X(xb), Y(yv) + 6, color=NEG, sw=2.2))
            out.append(text(X(-_m.pi) + 9, Y(yv) - 9, "L(y)", size=12, color=NEG,
                            anchor="start", bold=True))
        out.append(text(px - 6, top + ch + 24, "−π", size=12, color=MUTED, anchor="end"))
        out.append(text(px + cw + 6, top + ch + 24, "+π", size=12, color=MUTED, anchor="start"))
        out.append(text(px + cw / 2, top + ch + 24, "фаза несучої  x = ω_c·t", size=12,
                        color=MUTED))
        out.append(text(px + cw / 2, top + ch + 58, note, size=13, color=note_color, bold=True))
        return out

    frags += panel(112, "природна вибірка: живе порівняння",
                   lambda y: _m.pi * M * _m.cos(y), None, "#eaf7ef",
                   "L(y) = π(1 + M·cos y) — ТОЧНО", FIELD)
    frags += panel(576, "рівномірна вибірка (q = 5, перебільшено)",
                   lambda y: _uniform_edge(y, M, Q),
                   lambda y: _m.pi * M * _m.cos(y), "#fdecea",
                   "межу покривлено — L(y) уже не косинус", POS)
    frags.append(arrow(66, top + ch - 20, 66, top + 14, color=MUTED, sw=1.6))
    frags.append(text(66, top + ch / 2 - 16, "фаза", size=12, color=MUTED))
    frags.append(text(66, top + ch / 2 + 1, "сигналу", size=12, color=MUTED))
    frags.append(text(66, top + ch / 2 + 18, "y = ω₀·t", size=12, color=MUTED))
    frags.append(text(W / 2, 32, "Одиничний осередок: смуга «ввімкнено» на кожній висоті y",
                      size=15, bold=True))
    frags.append(text(W / 2, H - 20, "сіре — точний графік сигналу для порівняння · "
                                     "база = L(y) / 2π",
                      size=12, color=MUTED))
    return render(os.path.join(IMG, "natural-cell.svg"), W, H, *frags)


# ── 6. Витримка відліку: чому один край бреше, а два — ні ───────────────────
def fig_stale_edges():
    W, H = 1000, 500
    frags = []
    gw, gh = 336, 208
    top = 100
    Yg = lambda v: top + gh - (v + 1.25) / 2.5 * gh
    slope, s0 = 0.55, 0.15
    sig = lambda u: s0 + slope * u

    def head(px, t):
        return [fitbox(px - 8, 58, gw + 16, 30, t, size=13.5, bold=True,
                       fill=FILL, stroke=LINE),
                rect(px, top, gw, gh, fill="none", stroke="#d5d9de", sw=1.2, rx=3)]

    # ── ЛІВОРУЧ: пилка, один рухомий край
    px = 96
    Xg = lambda u: px + u * gw
    frags += head(px, "пилка: рухається ОДИН край")
    frags.append(poly([(Xg(0), Yg(-1)), (Xg(1), Yg(1))], color=MUTED, sw=2.0))
    frags.append(poly([(Xg(0), Yg(sig(0))), (Xg(1), Yg(sig(1)))], color=NEG, sw=2.4))
    frags.append(line(Xg(0), Yg(s0), Xg(1), Yg(s0), color=POS, sw=2.0, dash="7,5"))
    ue = (1 + s0) / 2
    frags.append(line(Xg(ue), Yg(s0), Xg(ue), top + gh, color=POS, sw=1.6, dash="4,4"))
    frags.append(circle(Xg(ue), Yg(s0), 5, fill=POS, stroke=POS, sw=1.5))
    frags.append(line(Xg(0), top, Xg(0), top + gh + 34, color=MUTED, sw=1.4, dash="4,4"))
    ya = top + gh + 28
    frags.append(arrow(Xg(0), ya, Xg(ue), ya, color=POS, sw=1.8))
    frags.append(text(Xg(ue / 2), ya + 22, "витримка (π + x_e)/q", size=12.5, color=POS, bold=True))
    frags.append(text(Xg(ue / 2), ya + 40, "сама залежить від сигналу", size=12.5, color=POS, bold=True))
    frags.append(text(Xg(0) + 8, Yg(s0) - 10, "заморожений відлік", size=11.5, color=POS, anchor="start"))
    frags.append(text(Xg(1) - 6, Yg(sig(1)) - 11, "живий сигнал", size=11.5, color=NEG, anchor="end"))
    frags.append(text(Xg(0) + 8, top + 15, "мить відліку", size=11.5, color=MUTED, anchor="start"))

    # ── ПРАВОРУЧ: трикутник, два рухомі краї
    px = 568
    Xg = lambda u: px + u * gw
    frags += head(px, "трикутник: рухаються ДВА краї")
    frags.append(poly([(Xg(0), Yg(1)), (Xg(0.5), Yg(-1)), (Xg(1), Yg(1))], color=MUTED, sw=2.0))
    frags.append(poly([(Xg(0), Yg(sig(0))), (Xg(1), Yg(sig(1)))], color=NEG, sw=2.4))
    frags.append(line(Xg(0), Yg(s0), Xg(1), Yg(s0), color=POS, sw=2.0, dash="7,5"))
    u1, u2 = (1 - s0) / 4, (3 + s0) / 4
    for uu in (u1, u2):
        frags.append(line(Xg(uu), Yg(s0), Xg(uu), top + gh, color=POS, sw=1.6, dash="4,4"))
        frags.append(circle(Xg(uu), Yg(s0), 5, fill=POS, stroke=POS, sw=1.5))
    frags.append(line(Xg(0), top, Xg(0), top + gh + 58, color=MUTED, sw=1.4, dash="4,4"))
    ya = top + gh + 28
    frags.append(arrow(Xg(0), ya, Xg(u1), ya, color=POS, sw=1.8))
    frags.append(text(Xg(u1) + 10, ya + 4, "(π − a)/q", size=12.5, color=POS, anchor="start", bold=True))
    frags.append(arrow(Xg(0), ya + 26, Xg(u2), ya + 26, color=POS, sw=1.8))
    frags.append(text(Xg(u2) + 10, ya + 30, "(π + a)/q", size=12.5, color=POS, anchor="start", bold=True))
    frags.append(text(Xg(0.5), ya + 62, "сума = 2π/q — СТАЛА: сигнал у ній скоротився",
                      size=13, color=FIELD, bold=True))
    frags.append(text(Xg(0) + 8, top + 15, "мить відліку", size=11.5, color=MUTED, anchor="start"))

    frags.append(text(W / 2, 32, "Наскільки застарів відлік, коли нарешті спрацьовує край",
                      size=15, bold=True))
    return render(os.path.join(IMG, "stale-edges.svg"), W, H, *frags)


# ── 7. Скільки коштує цифрова вибірка ──────────────────────────────────────
def fig_hd2_vs_ratio():
    W, H = 900, 540
    frags = []
    gx, gy, gw, gh = 132, 92, 630, 328
    q_lo, q_hi, h_lo, h_hi, M = 16.0, 1024.0, 1e-6, 1e-1, 0.9
    X = lambda q: gx + (_m.log10(q) - _m.log10(q_lo)) / (_m.log10(q_hi) - _m.log10(q_lo)) * gw
    Y = lambda h: gy + gh - (_m.log10(h) - _m.log10(h_lo)) / (_m.log10(h_hi) - _m.log10(h_lo)) * gh

    frags.append(rect(gx, gy, gw, gh, fill="#fbfcfd", stroke=LINE, sw=1.5, rx=4))
    for e in range(-6, 0):
        yv = Y(10.0 ** e)
        frags.append(line(gx, yv, gx + gw, yv, color="#e3e6ea", sw=1.0))
        frags.append(text(gx - 12, yv + 4, "%g%%" % (10.0 ** e * 100), size=11.5,
                          color=MUTED, anchor="end"))
    for q in (16, 32, 64, 128, 256, 512, 1024):
        frags.append(line(X(q), gy, X(q), gy + gh, color="#e3e6ea", sw=1.0))
        frags.append(text(X(q), gy + gh + 22, str(q), size=11.5, color=MUTED))

    qs = [q_lo * (q_hi / q_lo) ** (i / 200.0) for i in range(201)]
    frags.append(poly([(X(q), Y(_m.pi * M / (2 * q))) for q in qs], color=POS, sw=2.8))
    frags.append(poly([(X(q), Y(_m.pi ** 2 * M / 4 / q ** 2)) for q in qs
                       if _m.pi ** 2 * M / 4 / q ** 2 > h_lo], color="#b8860b", sw=2.8))
    frags.append(line(gx, gy + gh - 7, gx + gw, gy + gh - 7, color=FIELD, sw=3.2))

    frags.append(text(X(19), Y(_m.pi * M / (2 * 19)) - 15, "один край:  HD₂ = πM / 2q",
                      size=13, color=POS, bold=True, anchor="start"))
    frags.append(text(X(46), Y(_m.pi ** 2 * M / 4 / 30 ** 2) - 12, "два краї:  HD₂ = π²M / 4q²",
                      size=13, color="#b8860b", bold=True, anchor="start"))
    frags.append(text(X(50), gy + gh - 17, "природна вибірка: рівно 0 — на будь-якому q",
                      size=13, color=FIELD, bold=True, anchor="start"))

    qd = 384.0
    frags.append(line(X(qd), gy, X(qd), gy + gh, color=INK, sw=1.4, dash="5,5"))
    frags.append(circle(X(qd), Y(_m.pi * M / (2 * qd)), 5, fill=BG, stroke=POS, sw=2.2))
    frags.append(circle(X(qd), Y(_m.pi ** 2 * M / 4 / qd ** 2), 5, fill=BG, stroke="#b8860b", sw=2.2))
    frags.append(text(X(qd), gy - 12, "клас D: 384 кГц несуча, 1 кГц тон", size=12,
                      color=INK, bold=True))
    frags.append(text(X(qd) + 13, Y(_m.pi * M / (2 * qd)) - 8, "0.37 %", size=12.5,
                      color=POS, anchor="start", bold=True))
    frags.append(text(X(qd) + 13, Y(_m.pi ** 2 * M / 4 / qd ** 2) + 5, "0.0015 %", size=12.5,
                      color="#b8860b", anchor="start", bold=True))

    frags.append(text(gx + gw / 2, gy + gh + 50,
                      "q = f_c / f₀    (скільки періодів несучої припадає на період сигналу)",
                      size=13, color=MUTED))
    frags.append(text(58, gy + gh / 2 - 8, "HD₂", size=13.5, color=MUTED, bold=True))
    frags.append(text(58, gy + gh / 2 + 11, "M = 0.9", size=11.5, color=MUTED))
    frags.append(text(W / 2, 36, "Друга гармоніка: що модулятор додає від себе", size=15, bold=True))
    frags.append(text(W / 2, H - 20, "нахил −1 проти −2: удвічі вища несуча ріже один край "
                                     "удвічі, а два краї — вчетверо", size=12, color=MUTED))
    return render(os.path.join(IMG, "hd2-vs-ratio.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_switch_vs_linear()
    fig_duty_average()
    fig_comparator_pwm()
    fig_load_averages()
    fig_natural_cell()
    fig_stale_edges()
    fig_hd2_vs_ratio()
    print("figs done:", sorted(os.listdir(IMG)))
