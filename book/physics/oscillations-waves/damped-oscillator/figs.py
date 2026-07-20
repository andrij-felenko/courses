# -*- coding: utf-8 -*-
"""Фігури до теми «Загасний осцилятор».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── допоміжні деталі схеми (пружина, демпфер, стіна, підлога) ────────────────
def spring(x1, x2, y, coils=7, amp=13, lead=16):
    seg = (x2 - x1 - 2 * lead) / coils
    pts = [(x1, y), (x1 + lead, y)]
    for i in range(coils):
        pts.append((x1 + lead + seg * (i + 0.25), y - amp))
        pts.append((x1 + lead + seg * (i + 0.75), y + amp))
    pts.append((x2 - lead, y))
    pts.append((x2, y))
    d = "M " + " L ".join("%.1f %.1f" % (px, py) for px, py in pts)
    return '<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, INK)


def dashpot(x1, x2, y):
    out = []
    cyl_x, cyl_w, cyl_h = x1 + 14, 42, 30
    out.append(line(x1, y, cyl_x, y, color=INK, sw=2.2))
    out.append(line(cyl_x, y - cyl_h / 2, cyl_x + cyl_w, y - cyl_h / 2, color=INK, sw=2.2))
    out.append(line(cyl_x, y + cyl_h / 2, cyl_x + cyl_w, y + cyl_h / 2, color=INK, sw=2.2))
    out.append(line(cyl_x, y - cyl_h / 2, cyl_x, y + cyl_h / 2, color=INK, sw=2.2))
    px = cyl_x + cyl_w - 12
    out.append(line(px, y - cyl_h / 2 + 4, px, y + cyl_h / 2 - 4, color=INK, sw=3.4))
    out.append(line(px, y, x2, y, color=INK, sw=2.2))
    return "".join(out)


def wall(x, y1, y2, side=1):
    out = [line(x, y1, x, y2, color=INK, sw=3)]
    step = 14
    yy = y1 + 6
    while yy < y2:
        out.append(line(x, yy, x + 12 * side, yy - 12, color=MUTED, sw=1.4))
        yy += step
    return "".join(out)


def ground(x1, x2, y):
    out = [line(x1, y, x2, y, color=INK, sw=3)]
    xx = x1 + 6
    while xx < x2:
        out.append(line(xx, y, xx - 12, y + 12, color=MUTED, sw=1.4))
        xx += 14
    return "".join(out)


# ── розв'язки загасного осцилятора (ω₀ = 1) ─────────────────────────────────
def x_under(t, zeta, w0=1.0):
    """Відпуск зі спокою: x(0)=1, v(0)=0, ζ<1."""
    g = zeta * w0
    wd = w0 * math.sqrt(1 - zeta * zeta)
    return math.exp(-g * t) * (math.cos(wd * t) + (g / wd) * math.sin(wd * t))


def x_crit(t, w0=1.0):
    """Критичне загасання ζ=1: x(0)=1, v(0)=0."""
    return (1 + w0 * t) * math.exp(-w0 * t)


def x_over(t, zeta, w0=1.0):
    """Перезагасання ζ>1: x(0)=1, v(0)=0."""
    g = zeta * w0
    b = w0 * math.sqrt(zeta * zeta - 1)
    return math.exp(-g * t) * (math.cosh(b * t) + (g / b) * math.sinh(b * t))


def ring(t, zeta, w0=1.0):
    """Чистий дзвін від піка: A·e^(−γt)·cos(ω_d t)."""
    g = zeta * w0
    wd = w0 * math.sqrt(1 - zeta * zeta)
    return math.exp(-g * t) * math.cos(wd * t)


# ── Фігура 1: модель — маса, пружина, демпфер (без зовнішньої сили) ──────────
def fig_model():
    W, H = 780, 350
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Загасний осцилятор: пружина повертає, демпфер з'їдає рух",
                  size=16, bold=True))

    wx = 70
    gy = 268
    f.append(wall(wx, 92, gy))
    f.append(ground(wx, W - 40, gy))

    # рівновага (пунктирна вертикаль) і зміщена маса праворуч
    eqx = 430
    mx, my, mw, mh = 480, 188, 118, 92
    f.append(line(eqx, 108, eqx, gy, color=MUTED, sw=1.3, dash="4,6"))
    f.append(text(eqx, 100, "рівновага", size=12, color=MUTED))

    f.append(rect(mx, my - mh / 2, mw, mh, fill="#e8edf3", stroke=INK, sw=2, rx=6))
    f.append(text(mx + mw / 2, my + 8, "m", size=26, bold=True))

    # пружина зверху, демпфер знизу
    f.append(spring(wx, mx, my - 26))
    f.append(text((wx + mx) / 2, my - 26 - 24, "пружина k  —  повертає до рівноваги",
                  size=13, color=INK))
    f.append(dashpot(wx, mx, my + 28))
    f.append(text((wx + mx) / 2 + 4, my + 28 + 34, "демпфер c  —  сила ∝ швидкості, гасить",
                  size=13, color=INK))

    # зміщення x від рівноваги до центру маси
    cxm = mx + mw / 2
    f.append(arrow(eqx, gy - 8, cxm, gy - 8, color=INK, sw=1.6))
    f.append(text((eqx + cxm) / 2, gy - 15, "x", size=14, italic=True))

    # швидкість маси і демпферна сила проти неї (над масою, у вільному місці)
    vy = my - mh / 2 - 16
    f.append(arrow(cxm + 6, vy, cxm + 66, vy, color=FIELD, sw=2.6))
    f.append(text(cxm + 72, vy + 4, "v", size=14, italic=True, color=FIELD, anchor="start"))
    f.append(arrow(cxm - 6, vy, cxm - 66, vy, color=NEG, sw=2.6))
    f.append(text(cxm - 72, vy + 4, "−c·v", size=13, bold=True, color=NEG, anchor="end"))

    # рівняння руху
    b, bw, bh = textbox(200, 322, "рівняння руху:   m·ẍ + c·ẋ + k·x = 0",
                        size=14, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.5, bold=True)
    f.append(b)
    return render(os.path.join(IMG, "model.svg"), W, H, *f)


# ── Фігура 2: дзвін із загасанням — синус під спадною обвідною ───────────────
def fig_ringdown():
    W, H = 840, 380
    zeta = 0.12
    tmax = 33.0
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Загасне коливання: синусоїда під спадною обвідною e^(−γt)",
                  size=16, bold=True))

    ox, oy = 84, 205
    rx = 792
    amp = 128

    def PX(t):
        return ox + (rx - ox) * (t / tmax)

    def PY(x):
        return oy - amp * x

    # осі
    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.7))
    f.append(arrow(ox, oy + amp + 22, ox, oy - amp - 22, color=INK, sw=1.7))
    f.append(text(rx + 2, oy + 24, "час  t →", size=13, anchor="end"))
    f.append(text(ox - 10, oy - amp - 24, "x", size=14, italic=True, anchor="end"))

    # обвідні ±A·e^(−γt)
    g = zeta
    N = 700
    et, eb, cv = [], [], []
    for i in range(N + 1):
        t = tmax * i / N
        env = math.exp(-g * t)
        et.append((PX(t), PY(env)))
        eb.append((PX(t), PY(-env)))
        cv.append((PX(t), PY(ring(t, zeta))))
    for env in (et, eb):
        de = "M %.1f %.1f " % env[0] + " ".join("L %.1f %.1f" % p for p in env[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.7" '
                 'stroke-dasharray="7,6"/>' % (de, MUTED))
    d = "M %.1f %.1f " % cv[0] + " ".join("L %.1f %.1f" % p for p in cv[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.3"/>' % (d, POS))

    # підпис обвідної (над верхньою кривою, ліворуч, де є місце)
    f.append(text(PX(5.4), PY(math.exp(-g * 5.4)) - 18,
                  "обвідна  A·e^(−γt)", size=13, bold=True, color=MUTED))

    # позначити спадні піки (кожен ≈ у e^(−γT_d) раза менший)
    wd = math.sqrt(1 - zeta * zeta)
    Td = 2 * math.pi / wd
    for n in range(5):
        tp = n * Td
        if tp > tmax:
            break
        f.append(circle(PX(tp), PY(math.exp(-g * tp)), 3.6, fill=POS, stroke=POS, sw=1))

    # позначка одного періоду T_d унизу (у вільному місці між першими піками)
    ybar = oy + amp + 6
    f.append(arrow(PX(0), ybar, PX(Td), ybar, color=INK, sw=1.5))
    f.append(arrow(PX(Td), ybar, PX(0), ybar, color=INK, sw=1.5))
    f.append(text(PX(Td / 2), ybar + 18, "період T_d = 2π/ω_d", size=12, bold=True))

    # плашка з висновком
    b, bw, bh = textbox(W - 232, 92,
                        "частота ω_d ледь нижча за ω₀;\nкожен розмах менший у стале число раз",
                        size=12, pad=9, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "ringdown.svg"), W, H, *f)


# ── Фігура 3: три режими — недо-, критичне, пере-загасання ───────────────────
def fig_regimes():
    W, H = 880, 430
    tmax = 12.0
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Три долі осцилятора: ζ вирішує, як він повертається до спокою",
                  size=16, bold=True))
    f.append(text(W / 2, 50, "усі відпущені з того самого відхилення x₀ у стані спокою",
                  size=12, color=MUTED))

    ox, oy = 80, 300
    rx, top = 596, 84
    xmin = -0.42

    def PX(t):
        return ox + (rx - ox) * (t / tmax)

    def PYv(x):
        # x=1 → верхня зона; x=0 → вісь (oy); x<0 → нижче осі
        return oy - (oy - top) * x

    # осі
    f.append(arrow(ox, oy, rx + 6, oy, color=INK, sw=1.7))
    f.append(arrow(ox, PYv(xmin) + 20, ox, PYv(1) - 18, color=INK, sw=1.7))
    f.append(text(rx + 2, oy + 24, "час  t →", size=13, anchor="end"))
    f.append(text(ox - 12, PYv(1) - 20, "x / x₀", size=13, bold=True, anchor="start"))

    # риски по x
    for xv in (0.0, 0.5, 1.0):
        f.append(line(ox - 6, PYv(xv), ox, PYv(xv), color=INK, sw=1.3))
        f.append(text(ox - 12, PYv(xv) + 4, "%.1f" % xv, size=11, color=MUTED, anchor="end"))
    f.append(line(ox, oy, rx, oy, color="#e6e9ec", sw=1.0))  # нульова лінія

    curves = [
        ("недозагашений", "ζ = 0.22", "гойдається й стихає", FIELD,
         lambda t: x_under(t, 0.22)),
        ("критичне", "ζ = 1", "найшвидше, без перельоту", NEG,
         lambda t: x_crit(t)),
        ("перезагашений", "ζ = 2.5", "мляве повзуче повернення", POS,
         lambda t: x_over(t, 2.5)),
    ]
    N = 600
    for name, zt, desc, col, fn in curves:
        pts = []
        for i in range(N + 1):
            t = tmax * i / N
            pts.append((PX(t), PYv(max(xmin, fn(t)))))
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, col))

    # легенда праворуч, широкий вільний стовпець (не на кривих)
    lx, ly = rx + 30, 118
    for i, (name, zt, desc, col, fn) in enumerate(curves):
        yy = ly + i * 92
        f.append(line(lx, yy, lx + 30, yy, color=col, sw=3.4))
        f.append(text(lx + 40, yy + 5, zt, size=13, bold=True, color=col, anchor="start"))
        f.append(text(lx, yy + 26, name, size=13, bold=True, color=INK, anchor="start"))
        f.append(text(lx, yy + 46, desc, size=12, color=MUTED, anchor="start"))

    # підказка про переліт нижче нуля — у вільному місці біля осі часу
    f.append(text(PX(8.6), PYv(-0.34), "переліт нижче нуля = «дзвін»", size=11,
                  color=FIELD))
    return render(os.path.join(IMG, "regimes.svg"), W, H, *f)


# ── Фігура 4 (історична вставка): три нитки, що зійшлися в добротності ────────
def fig_timeline():
    W, H = 1180, 500
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Три нитки, що зійшлися в понятті загасання й буквi Q",
                  size=17, bold=True))
    f.append(text(W / 2, 52, "відстані між подіями НЕ в масштабі часу — це порядок, а не шкала",
                  size=12, color=MUTED))

    ox, rx = 90, 1090
    axis_y = 258
    # кольори за ниткою
    C = {"math": INK, "instr": NEG, "theory": FIELD, "radio": POS}
    events = [
        (1739, "Ейлер",       "e^(λt), три корені",   "math",   "up"),
        (1833, "Ґаус–Вебер",  "загасна стрілка",       "instr",  "down"),
        (1858, "Кельвін",     "чутливий гальванометр", "instr",  "up"),
        (1873, "Релей",       "дисипативна функція",   "theory", "down"),
        (1914, "Джонсон",     "K = ωL/R",              "radio",  "up"),
        (1920, "Джонсон",     "K → Q",                 "radio",  "down"),
        (1925, "Легг",        "«quality factor»",      "radio",  "up"),
    ]
    n = len(events)

    # головна вісь-стрілка часу
    f.append(arrow(ox - 14, axis_y, rx + 18, axis_y, color=INK, sw=2.0))
    f.append(text(rx + 20, axis_y + 24, "час →", size=13, anchor="end", color=INK))

    for i, (yr, name, phrase, stream, side) in enumerate(events):
        x = ox + (rx - ox) * i / (n - 1)
        col = C[stream]
        f.append(circle(x, axis_y, 6.5, fill=col, stroke=col, sw=1.5))
        if side == "up":
            # короткий стояк угору, текст ще вище — лінія не перетинає напис
            f.append(line(x, axis_y - 8, x, 184, color=MUTED, sw=1.2))
            f.append(text(x, 128, str(yr), size=15, bold=True, color=col))
            f.append(text(x, 150, name, size=13, bold=True, color=INK))
            f.append(text(x, 170, phrase, size=12, color=MUTED))
        else:
            f.append(line(x, axis_y + 8, x, 332, color=MUTED, sw=1.2))
            f.append(text(x, 352, str(yr), size=15, bold=True, color=col))
            f.append(text(x, 374, name, size=13, bold=True, color=INK))
            f.append(text(x, 394, phrase, size=12, color=MUTED))

    # легенда ниток унизу
    ly = 452
    legend = [("матем. підґрунтя", INK), ("прилади", NEG),
              ("теорія втрат", FIELD), ("радіо / Q", POS)]
    # рахуємо ширини, щоб рівно розкласти по центру
    seg_w = 260
    total = seg_w * len(legend)
    lx0 = (W - total) / 2 + 20
    for i, (lab, col) in enumerate(legend):
        lx = lx0 + i * seg_w
        f.append(circle(lx, ly, 6.5, fill=col, stroke=col, sw=1.5))
        f.append(text(lx + 16, ly + 5, lab, size=13, color=INK, anchor="start"))
    return render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f)


# ── Фігура: корені характеристичного рівняння на комплексній λ-площині ────────
def fig_roots():
    W, H = 880, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Корені λ на комплексній площині: знак ζ²−1 розводить три режими",
                  size=16, bold=True))
    f.append(text(W / 2, 50, "λ = −γ ± ω₀·√(ζ²−1),   |λ| = ω₀,   cos φ = ζ",
                  size=13, color=MUTED))

    S = 96.0
    Ox, Oy = 574, 270

    def P(re, im):
        return (Ox + re * S, Oy - im * S)

    # осі Re λ (горизонт) та Im λ (вертикаль)
    f.append(arrow(300, Oy, 742, Oy, color=INK, sw=1.6))
    f.append(text(738, Oy - 12, "Re λ", size=13, italic=True, anchor="end"))
    f.append(arrow(Ox, Oy + 1.55 * S, Ox, Oy - 1.55 * S, color=INK, sw=1.6))
    f.append(text(Ox + 12, Oy - 1.55 * S + 6, "Im λ", size=13, italic=True, anchor="start"))
    f.append(text(Ox + 9, Oy + 18, "0", size=12, color=MUTED, anchor="start"))

    # межа стабільності — уявна вісь; ліворуч усе згасає
    f.append(line(Ox, Oy - 1.55 * S, Ox, Oy + 1.55 * S, color=MUTED, sw=1.1, dash="3,5"))
    f.append(text(Ox - 8, Oy - 1.42 * S, "Re λ < 0  →  рух згасає", size=12,
                  color=MUTED, anchor="end"))

    import math as _m
    # локус комплексних коренів — ліва півкруглість кола |λ|=ω₀
    arc = []
    steps = 90
    for i in range(steps + 1):
        a = _m.pi / 2 + _m.pi * i / steps          # від (0,+1) через (−1,0) до (0,−1)
        arc.append(P(_m.cos(a), _m.sin(a)))
    da = "M %.1f %.1f " % arc[0] + " ".join("L %.1f %.1f" % p for p in arc[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-dasharray="7,6"/>' % (da, FIELD))
    # праву (нефізичну) половину кола — ледь-ледь, як довідку радіуса
    arc2 = []
    for i in range(steps + 1):
        a = -_m.pi / 2 + _m.pi * i / steps
        arc2.append(P(_m.cos(a), _m.sin(a)))
    da2 = "M %.1f %.1f " % arc2[0] + " ".join("L %.1f %.1f" % p for p in arc2[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.0" '
             'stroke-dasharray="3,7"/>' % (da2, "#d7dbe0"))
    f.append(text(*P(-0.70, 0.88), s="локус при 0<ζ<1", size=12, color=FIELD))

    # локус перезагасання — обидві гілки вздовж дійсної осі від −ω₀
    px1, _ = P(-1.0, 0)
    px2, _ = P(-2.55, 0)
    px0, _ = P(-0.02, 0)
    f.append(line(px1, Oy, px2, Oy, color=POS, sw=2.2, dash="7,6"))
    f.append(line(px1, Oy, px0, Oy, color=POS, sw=2.2, dash="7,6"))

    # дійсні корені перезагасання (ζ = 1.4): −ζ ± √(ζ²−1)
    z = 1.4
    r_slow = -(z - _m.sqrt(z * z - 1))
    r_fast = -(z + _m.sqrt(z * z - 1))
    for rr in (r_slow, r_fast):
        f.append(circle(*P(rr, 0), r=6.2, fill=POS, stroke=POS, sw=1))
    f.append(text(*P(r_slow, 0.40), s="повільний", size=11, color=POS))
    f.append(text(*P(r_fast, 0.40), s="швидкий", size=11, color=POS))
    f.append(text(*P((r_slow + r_fast) / 2, -0.36), s="ζ>1: два дійсні корені",
                  size=12, bold=True, color=POS))

    # подвійний корінь при ζ=1 у точці −ω₀
    f.append(circle(*P(-1.0, 0), r=7.6, fill="#fff", stroke=NEG, sw=2.6))
    f.append(circle(*P(-1.0, 0), r=3.0, fill=NEG, stroke=NEG, sw=1))
    f.append(text(*P(-1.02, -0.28), s="ζ=1: подвійний −ω₀", size=12, bold=True,
                  color=NEG, anchor="middle"))

    # комплексна пара при ζ=0.5
    zc = 0.5
    reu, imu = -zc, _m.sqrt(1 - zc * zc)
    for sg in (1, -1):
        f.append(circle(*P(reu, sg * imu), r=6.2, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(*P(reu - 0.08, imu + 0.18), s="−γ + iω_d", size=12, bold=True,
                  color=FIELD, anchor="end"))
    f.append(text(*P(reu - 0.08, -imu - 0.02), s="−γ − iω_d", size=12, bold=True,
                  color=FIELD, anchor="end"))
    # радіус до верхнього кореня + кут φ від від'ємної дійсної осі
    f.append(line(Ox, Oy, *P(reu, imu), color=MUTED, sw=1.3))
    ar = []
    for i in range(31):
        a = _m.pi - (_m.pi - _m.atan2(imu, reu)) * i / 30   # від осі −Re до радіуса
        ar.append((Ox + 0.36 * S * _m.cos(a), Oy - 0.36 * S * _m.sin(a)))
    dar = "M %.1f %.1f " % ar[0] + " ".join("L %.1f %.1f" % p for p in ar[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (dar, INK))
    f.append(text(Ox - 0.54 * S, Oy - 0.20 * S, "φ", size=14, bold=True, italic=True))

    # межові точки ζ=0 — чисте гойдання на уявній осі
    for sg in (1, -1):
        f.append(circle(*P(0, sg * 1.0), r=5.0, fill="#fff", stroke=MUTED, sw=2))
    f.append(text(*P(0.06, 1.02), s="ζ=0: ±iω₀ (не згасає)", size=11, color=MUTED, anchor="start"))

    # стрілка «ζ зростає» вниз по локусу
    a1 = _m.pi / 2 + _m.pi * 0.28
    a2 = _m.pi / 2 + _m.pi * 0.34
    p1 = P(_m.cos(a1), _m.sin(a1))
    p2 = P(_m.cos(a2), _m.sin(a2))
    f.append(arrow(p1[0], p1[1], p2[0], p2[1], color=FIELD, sw=2.2))
    f.append(text(*P(-0.34, 1.06), s="ζ ↑", size=12, bold=True, color=FIELD))

    b, bw, bh = textbox(196, 456,
                        "усі корені у лівій півплощині\n→ будь-який рух згасає до нуля",
                        size=12, pad=9, fill=FILL, stroke=LINE, sw=1.3)
    f.append(b)
    return render(os.path.join(IMG, "roots.svg"), W, H, *f)


# ── Фігура: фазовий портрет — траєкторії у площині (x, v) ─────────────────────
def fig_phase():
    W, H = 860, 470
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Фазовий портрет: стан (x, v) — одна точка, рух — крива до рівноваги",
                  size=16, bold=True))

    Ox, Oy = 305, 258
    S = 150.0

    def P(x, v):
        return (Ox + x * S, Oy - v * S)

    # осі x (горизонт) і v/ω₀ (вертикаль)
    f.append(arrow(Ox - 1.35 * S, Oy, Ox + 1.35 * S, Oy, color=INK, sw=1.6))
    f.append(text(Ox + 1.35 * S, Oy + 20, "x", size=14, italic=True, anchor="end"))
    f.append(arrow(Ox, Oy + 1.30 * S, Ox, Oy - 1.30 * S, color=INK, sw=1.6))
    f.append(text(Ox + 10, Oy - 1.30 * S + 6, "v / ω₀", size=13, italic=True, anchor="start"))

    # довідкове коло — незгасний рух (стала енергія)
    f.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="none" stroke="%s" '
             'stroke-width="1.4" stroke-dasharray="6,6"/>' % (Ox, Oy, S, MUTED))
    f.append(text(*P(0.74, 0.82), s="ζ=0: замкнене коло", size=12, color=MUTED))

    def traj(xfn, tmax, n=1600):
        pts = []
        h = 1e-4
        for i in range(n + 1):
            t = tmax * i / n
            x = xfn(t)
            v = (xfn(t + h) - xfn(t - h)) / (2 * h)
            pts.append(P(x, v))
        return pts

    def draw(pts, col, sw=2.5):
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (d, col, sw))

    under = traj(lambda t: x_under(t, 0.15), 27.0)
    crit = traj(lambda t: x_crit(t), 8.5)
    over = traj(lambda t: x_over(t, 2.5), 15.0)
    draw(under, FIELD)
    draw(crit, NEG)
    draw(over, POS)

    # стрілки напрямку руху (за годинниковою) на кожній кривій
    for pts, col in ((under, FIELD), (crit, NEG), (over, POS)):
        k = 70
        f.append(arrow(pts[k][0], pts[k][1], pts[k + 6][0], pts[k + 6][1], color=col, sw=2.2))

    # спільний старт і рівновага-атрактор
    f.append(circle(*P(1.0, 0.0), r=4.6, fill="#fff", stroke=INK, sw=2))
    f.append(text(*P(1.0, -0.18), s="старт (x₀, 0)", size=11, color=INK))
    f.append(circle(Ox, Oy, 5.0, fill=INK, stroke=INK, sw=1))
    f.append(text(Ox - 8, Oy - 12, "рівновага", size=11, color=INK, anchor="end"))

    # легенда праворуч
    lx, ly = Ox + 1.5 * S + 24, 150
    rows = [
        ("ζ = 0.15  недозагашений", "спіраль — виток за витком", FIELD),
        ("ζ = 1  критичне", "прямо в центр, без обертів", NEG),
        ("ζ = 2.5  перезагашений", "мляве повзуче наближення", POS),
    ]
    for i, (a, b2, col) in enumerate(rows):
        yy = ly + i * 78
        f.append(line(lx, yy, lx + 30, yy, color=col, sw=3.4))
        f.append(text(lx + 40, yy + 5, a, size=13, bold=True, color=col, anchor="start"))
        f.append(text(lx, yy + 26, b2, size=12, color=MUTED, anchor="start"))
    f.append(text(lx, ly + 3 * 78 + 2, "оберт навколо 0 = гойдання;",
                  size=12, color=INK, anchor="start"))
    f.append(text(lx, ly + 3 * 78 + 22, "стягування в 0 = загасання",
                  size=12, color=INK, anchor="start"))
    return render(os.path.join(IMG, "phase.svg"), W, H, *f)


# ── Фігура (вставка proj-ringdown): як алгоритм читає дзвін ──────────────────
def fig_ringdown_fit():
    """Вершини дзвону → пряма в логарифмі амплітуд (нахил −γ, крок δ)."""
    W, H = 900, 610
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30,
                  "Вимірювання загасання: вершини дзвону лягають на пряму в логарифмі",
                  size=16, bold=True))

    zeta, w0 = 0.08, 1.0
    g = zeta * w0
    wd = w0 * math.sqrt(1 - zeta * zeta)
    Td = 2 * math.pi / wd
    tmax = 6.4 * Td

    ox, rxp = 92, 592

    # ── панель 1: сам запис дзвону ──
    oy1, amp = 165, 92

    def PX(t):
        return ox + (rxp - ox) * (t / tmax)

    def PY1(x):
        return oy1 - amp * x

    f.append(arrow(ox, oy1, rxp + 8, oy1, color=INK, sw=1.6))
    f.append(arrow(ox, oy1 + amp + 18, ox, oy1 - amp - 20, color=INK, sw=1.6))
    f.append(text(rxp + 6, oy1 + 22, "t →", size=12, anchor="end"))
    f.append(text(ox - 10, oy1 - amp - 16, "a(t)", size=13, italic=True, anchor="end"))

    N = 640
    cv, et, eb = [], [], []
    for i in range(N + 1):
        t = tmax * i / N
        env = math.exp(-g * t)
        cv.append((PX(t), PY1(env * math.cos(wd * t))))
        et.append((PX(t), PY1(env)))
        eb.append((PX(t), PY1(-env)))
    for e2 in (et, eb):
        de = "M %.1f %.1f " % e2[0] + " ".join("L %.1f %.1f" % p for p in e2[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.5" '
                 'stroke-dasharray="6,6"/>' % (de, MUTED))
    d = "M %.1f %.1f " % cv[0] + " ".join("L %.1f %.1f" % p for p in cv[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d, POS))

    peaks_t = []
    n = 0
    while n * Td <= tmax + 1e-9:
        tp = n * Td
        peaks_t.append(tp)
        f.append(circle(PX(tp), PY1(math.exp(-g * tp)), 4.2, fill=BG, stroke=INK, sw=2))
        n += 1

    ybar = oy1 - amp - 4
    f.append(arrow(PX(0), ybar, PX(Td), ybar, color=INK, sw=1.3))
    f.append(arrow(PX(Td), ybar, PX(0), ybar, color=INK, sw=1.3))
    f.append(text(PX(Td / 2), ybar - 7, "T_d", size=12, bold=True))
    f.append(text((ox + rxp) / 2, 300,
                  "кружечки — вхід алгоритму: час і висота кожної вершини",
                  size=12, color=MUTED))

    # ── панель 2: логарифм висоти вершин — пряма ──
    oy2top, oy2bot = 360, 548
    lnmin = -g * tmax * 1.04

    def PY2(L):
        return oy2top + (oy2bot - oy2top) * (L / lnmin)

    f.append(arrow(ox, oy2bot, rxp + 8, oy2bot, color=INK, sw=1.6))
    f.append(arrow(ox, oy2bot + 8, ox, oy2top - 20, color=INK, sw=1.6))
    f.append(text(rxp + 6, oy2bot + 22, "t →", size=12, anchor="end"))
    f.append(text(ox - 10, oy2top - 8, "ln(висота вершини)", size=12, anchor="end"))

    la = [(PX(t), PY2(-g * t)) for t in peaks_t]
    d2 = "M %.1f %.1f " % la[0] + " ".join("L %.1f %.1f" % p for p in la[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d2, NEG))
    for (px, py) in la:
        f.append(circle(px, py, 4.2, fill=BG, stroke=INK, sw=2))

    x0p, y0p = la[1]
    x1p, y1p = la[2]
    f.append(line(x0p, y0p, x1p, y0p, color=FIELD, sw=1.7))
    f.append(line(x1p, y0p, x1p, y1p, color=FIELD, sw=1.7))
    f.append(text((x0p + x1p) / 2, y0p - 7, "T_d", size=11, bold=True, color=FIELD))
    f.append(text(x1p + 9, (y0p + y1p) / 2 + 4, "δ", size=14, bold=True,
                  italic=True, color=FIELD, anchor="start"))

    b, bw, bh = textbox(452, 400,
                        "нахил = −γ  (темп загасання)\nкрок вниз δ = γ·T_d  →  ζ, Q",
                        size=12, pad=9, fill="#eafaf1", stroke=FIELD, sw=1.4)
    f.append(b)
    return render(os.path.join(IMG, "ringdown-fit.svg"), W, H, *f)


# ── Фігура (вставка proj-ringdown): форма обвідної викриває тертя ────────────
def fig_damping_signatures():
    """Три природи втрат — три форми спадної обвідної."""
    W, H = 920, 400
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Форма спадної обвідної викриває природу втрат",
                  size=16, bold=True))

    panels = [
        ("В'ЯЗКЕ  −c·v", FIELD, lambda t: math.exp(-1.15 * t),
         "розмах × стале число щоцикла;\nу логарифмі — пряма"),
        ("СУХЕ  (Кулон)", NEG, lambda t: max(0.0, 1 - 0.34 * t),
         "розмах − стала щоцикла; обвідна\nпряма до нуля, тоді стоп"),
        ("ОПІР ∝ v²", POS, lambda t: 1.0 / (1 + 2.3 * t),
         "крутий спад на великих амплітудах,\nдалі довгий хвіст"),
    ]
    pw = 280
    gap = (W - 3 * pw) / 4.0
    tmax, oy, amp = 3.0, 210, 74

    for j, (name, col, env, cap) in enumerate(panels):
        px0 = gap + j * (pw + gap)
        left, right = px0 + 22, px0 + pw - 14

        def PX(t, left=left, right=right):
            return left + (right - left) * (t / tmax)

        def PY(x):
            return oy - amp * x

        f.append(text(px0 + pw / 2, 66, name, size=13, bold=True, color=col))
        f.append(arrow(left, oy, right + 6, oy, color=INK, sw=1.4))
        f.append(arrow(left, oy + 16, left, oy - amp - 22, color=INK, sw=1.4))

        M = 400
        cv, et, eb = [], [], []
        for i in range(M + 1):
            t = tmax * i / M
            e = env(t)
            cv.append((PX(t), PY(e * math.cos(9.0 * t))))
            et.append((PX(t), PY(e)))
            eb.append((PX(t), PY(-e)))
        for e2 in (et, eb):
            de = "M %.1f %.1f " % e2[0] + " ".join("L %.1f %.1f" % p for p in e2[1:])
            f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.9" '
                     'stroke-dasharray="5,5"/>' % (de, col))
        d = "M %.1f %.1f " % cv[0] + " ".join("L %.1f %.1f" % p for p in cv[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.4"/>' % (d, MUTED))

        f.append(fitbox(px0 + 6, 300, pw - 12, 74, cap, size=12, pad=8,
                        fill=FILL, stroke=LINE, sw=1.2))
    return render(os.path.join(IMG, "damping-signatures.svg"), W, H, *f)


if __name__ == "__main__":
    ps = [fig_model(), fig_ringdown(), fig_regimes(), fig_timeline(), fig_roots(), fig_phase(),
          fig_ringdown_fit(), fig_damping_signatures()]
    print("written:")
    for p in ps:
        print("  ", p)
