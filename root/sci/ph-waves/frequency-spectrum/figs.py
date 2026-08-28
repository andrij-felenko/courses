# -*- coding: utf-8 -*-
"""Фігури до статті «Частотний спектр». Запуск із теки теми:  python figs.py
Виводить SVG у ./img/. svgkit береться зі scripts/ у корені репо."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def curve(x0, W, fn, color, sw=1.6, n=720, dash=None):
    """Полілінія y=fn(t), t∈[0,1], x=x0+t·W. fn повертає піксельний y."""
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append("%.1f,%.1f" % (x0 + t * W, fn(t)))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline fill="none" stroke="%s" stroke-width="%.1f"%s points="%s"/>'
            % (color, sw, d, " ".join(pts)))


def stem(x, y0, h, color=INK, dot=NEG, sw=3.2, r=5):
    """Спектральна лінія: стовпчик угору на h від осі y0 + кружечок зверху."""
    return (line(x, y0, x, y0 - h, color, sw)
            + circle(x, y0 - h, r, fill=dot, stroke=dot))


def bar(x, y0, h, color=INK, dot=NEG, sw=2.6, r=3.4):
    """Тонкий стовпчик спектра з кружечком-вершиною (для щільних сіток бінів)."""
    return (line(x, y0, x, y0 - h, color, sw)
            + circle(x, y0 - h, r, fill=dot, stroke=dot))


# ── Фігура 1: та сама хвиля — форма в часі ↔ спектр у частоті ─────────────────
def fig_time_vs_freq():
    W, H = 940, 430
    # ── ліва панель: форма в часі ──
    x0, wide, yc, sc = 72, 320, 155, 44
    sig = lambda t: (math.sin(2 * math.pi * 2 * t)
                     + 0.5 * math.sin(2 * math.pi * 4 * t)
                     + 0.3 * math.sin(2 * math.pi * 6 * t))
    t_axis = arrow(x0 - 12, yc, x0 + wide + 6, yc, INK, 1.6)
    a_axis = arrow(x0 - 12, yc + 96, x0 - 12, yc - 96, INK, 1.6)
    wave = curve(x0, wide, lambda t: yc - sc * sig(t), INK, 1.9)
    t_cap = text(x0 - 6, 58, "у часі: форма хвилі", size=15, color=INK, anchor="start", bold=True)
    t_lbl = text(x0 + wide + 2, yc + 20, "час", size=13, color=MUTED, anchor="end")
    a_lbl = text(x0 - 6, yc - 84, "зміщення", size=12, color=MUTED, anchor="start")

    # ── місток: та сама інформація ──
    xm = 470
    eq = text(xm, yc + 8, "⇄", size=40, color=MUTED, bold=True)
    eq_lbl = mtext(xm, yc + 46, ["та сама", "інформація"], size=12, color=MUTED)

    # ── права панель: спектр у частоті ──
    fx0, fy = 560, 258
    fw = 340
    f_axis = arrow(fx0 - 12, fy, fx0 + fw, fy, INK, 1.6)
    fa_axis = arrow(fx0 - 12, fy, fx0 - 12, fy - 168, INK, 1.6)
    f_cap = text(fx0 - 6, 58, "у частоті: спектр", size=15, color=INK, anchor="start", bold=True)
    f_lbl = text(fx0 + fw - 4, fy + 20, "частота", size=13, color=MUTED, anchor="end")
    fa_lbl = text(fx0 - 6, fy - 158, "амплітуда", size=12, color=MUTED, anchor="start")

    bars, blab, hlab = [], [], []
    for k, (nm, a) in enumerate([("f", 1.0), ("2f", 0.5), ("3f", 0.3)]):
        bx = fx0 + 60 + k * 96
        h = a * 140
        bars.append(stem(bx, fy, h))
        blab.append(text(bx, fy + 22, nm, size=15, color=INK, bold=True))
        hlab.append(text(bx + 12, fy - h + 4, "%.1f" % a, size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "time-vs-freq.svg"), W, H,
           t_axis, a_axis, wave, t_cap, t_lbl, a_lbl,
           eq, eq_lbl,
           f_axis, fa_axis, f_cap, f_lbl, fa_lbl, *bars, *blab, *hlab,
           title="Той самий сигнал двома мовами")


# ── Фігура 2: та сама нота, різний тембр — різниця у спектрі ──────────────────
def fig_timbre():
    W, H = 900, 480
    x_l, x_r = 92, 840
    step = 70
    x_first = 132
    sc = 128

    guide = line(x_first, 74, x_first, 452, MUTED, 1.2, dash="4,6")
    gnote = text(x_first + 8, 70, "основна частота — та сама в обох", size=12,
                 color=MUTED, anchor="start")

    def panel(axis_y, amps, cap):
        p = [arrow(x_l - 6, axis_y, x_r, axis_y, INK, 1.6)]
        for k, a in enumerate(amps):
            bx = x_first + k * step
            p.append(stem(bx, axis_y, a * sc))
        p.append(text((x_l + x_r) / 2, axis_y - sc - 24, cap, size=15, color=INK, bold=True))
        p.append(text(x_r - 4, axis_y + 20, "частота", size=12, color=MUTED, anchor="end"))
        return p

    flute = panel(210, [1.0, 0.14, 0.08, 0.05], "Флейта — тон майже чистий")
    violin = panel(440, [1.0, 0.75, 0.6, 0.65, 0.45, 0.4, 0.3, 0.22],
                   "Скрипка — гармоніки сильні й численні")

    foot = text(W / 2, 474,
                "перша лінія (основна) в обох на тому самому місці — висота однакова; різняться лише гармоніки над нею",
                size=12, color=MUTED)

    render(os.path.join(IMG, "timbre.svg"), W, H,
           guide, gnote, *flute, *violin, foot,
           title="Та сама нота, різний тембр")


# ── Фігура 3: три почерки спектра — лінія, набір ліній, суцільна смуга ────────
def fig_signatures():
    W, H = 980, 340
    ay = 262

    def frame(x0, x1, ttl, sub):
        p = [arrow(x0 - 4, ay, x1, ay, INK, 1.6),
             text((x0 + x1) / 2, 62, ttl, size=15, color=INK, bold=True),
             text((x0 + x1) / 2, 300, sub, size=13, color=MUTED),
             text(x1 - 4, ay + 20, "частота", size=11, color=MUTED, anchor="end")]
        return p

    # A: чистий тон — одна лінія
    a = frame(60, 300, "Чистий тон", "одна лінія")
    a.append(stem(180, ay, 158))

    # B: акорд — кілька ліній
    b = frame(360, 620, "Акорд", "кілька ліній")
    for bx, h in [(430, 158), (476, 120), (540, 138)]:
        b.append(stem(bx, ay, h))

    # C: шум/клац — суцільна смуга
    c = frame(680, 940, "Шум, клац", "суцільна смуга")
    xl, xr, mid, amp = 694, 930, 812, 132
    pts = ["%.1f,%.1f" % (xl, ay)]
    n = 90
    for i in range(n + 1):
        x = xl + (xr - xl) * i / n
        env = math.exp(-((x - mid) / 90.0) ** 2)
        rip = 0.12 * math.sin(x * 0.9) * env
        y = ay - amp * max(0.0, env + rip)
        pts.append("%.1f,%.1f" % (x, y))
    pts.append("%.1f,%.1f" % (xr, ay))
    hump = ('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="1.8"/>'
            % (" ".join(pts), POS))

    seps = (line(330, 72, 330, 292, MUTED, 1.0, dash="2,6")
            + line(650, 72, 650, 292, MUTED, 1.0, dash="2,6"))

    render(os.path.join(IMG, "signatures.svg"), W, H,
           seps, *a, *b, *c, hump,
           title="Три почерки спектра")


# ── Фігура 4: Синтез Фур'є та ефект Гіббса ───────────────────────────────────
def fig_fourier_synthesis():
    W, H = 960, 480
    pw = 190
    sc = 40.0
    yc = 200

    def sq_harmonics(t, n_terms):
        val = 0.0
        for k in range(n_terms):
            n = 2 * k + 1
            val += (4.0 / (math.pi * n)) * math.sin(2 * math.pi * n * t)
        return val

    panels = [
        (60, 1, "N = 1 (основна)", ["тільки sin(ωt)", "гладенька хвиля"]),
        (280, 2, "N = 2 (1-ша + 3-тя)", ["додано 1/3·sin(3ωt)", "вершина приплюснута"]),
        (500, 4, "N = 4 (до 7-ї)", ["до 1/7·sin(7ωt)", "круті фронти, пульсація"]),
        (720, 15, "N = 15 (до 29-ї)", ["майже прямокутник,", "викид Гіббса ≈ 8.95%"])
    ]

    elements = []
    for x0, n_t, ttl, note in panels:
        ax = arrow(x0 - 8, yc, x0 + pw + 8, yc, INK, 1.4)
        ay = line(x0, yc + 65, x0, yc - 65, INK, 1.4)
        sq_ideal = (line(x0, yc - sc, x0 + pw / 2, yc - sc, MUTED, 1.0, dash="3,3")
                    + line(x0 + pw / 2, yc - sc, x0 + pw / 2, yc + sc, MUTED, 1.0, dash="3,3")
                    + line(x0 + pw / 2, yc + sc, x0 + pw, yc + sc, MUTED, 1.0, dash="3,3"))
        wv = curve(x0, pw, lambda t, nt=n_t: yc - sc * sq_harmonics(t, nt), NEG if n_t < 15 else POS, 2.0)
        tbox = text(x0 + pw / 2, 75, ttl, size=14, color=INK, bold=True)
        nbox = mtext(x0 + pw / 2, 305, note, size=12, color=MUTED, lh=1.35)
        elements.extend([ax, ay, sq_ideal, wv, tbox, nbox])

    # Позначення викиду Гіббса на 4-й панелі
    x_gibbs = 720 + pw * 0.04
    y_gibbs = yc - sc * 1.18
    g_arr = arrow(x_gibbs + 35, y_gibbs - 20, x_gibbs + 4, y_gibbs + 4, POS, 1.4)
    g_lbl = text(x_gibbs + 45, y_gibbs - 26, "викид +8.95%", size=11, color=POS, bold=True, anchor="start")
    elements.extend([g_arr, g_lbl])

    div1 = line(260, 60, 260, 360, MUTED, 1.0, dash="2,4")
    div2 = line(480, 60, 480, 360, MUTED, 1.0, dash="2,4")
    div3 = line(700, 60, 700, 360, MUTED, 1.0, dash="2,4")
    elements.extend([div1, div2, div3])

    foot = text(W / 2, 420,
                "Послідовне додавання непарних гармонік формує прямокутний фронт; біля розриву лишається пульсація Гіббса",
                size=13, color=MUTED)
    elements.append(foot)

    render(os.path.join(IMG, "fourier-synthesis.svg"), W, H, *elements,
           title="Синтез меандру з гармонік та ефект Гіббса")


# ── Фігура 5: Дискретний спектр проти неперервного ────────────────────────────
def fig_discrete_vs_continuous():
    W, H = 960, 480
    mid_x = 480

    # ── Ліва панель: Періодична послідовність імпульсів (дискретний спектр) ──
    l_ttl = text(240, 60, "Періодичний сигнал: лінійчастий спектр", size=15, color=INK, bold=True)
    l_t_ax = arrow(50, 160, 430, 160, INK, 1.4)
    l_t_lbl = text(430, 180, "t", size=13, color=MUTED, anchor="end")
    l_t_sig_lbl = text(50, 95, "період T₀, тривалість τ", size=12, color=MUTED, anchor="start")

    # Малюємо 3 періодичні імпульси
    pulses = []
    for cx in (120, 240, 360):
        pulses.append(rect(cx - 20, 115, 40, 45, fill="#dbe4fb", stroke=NEG, sw=1.6, rx=2))
    t0_dim = (line(120, 190, 240, 190, MUTED, 1.2)
              + line(120, 182, 120, 198, MUTED, 1.2)
              + line(240, 182, 240, 198, MUTED, 1.2)
              + text(180, 212, "T₀", size=13, color=INK, bold=True))

    l_f_ax = arrow(50, 360, 430, 360, INK, 1.4)
    l_f_lbl = text(430, 380, "f", size=13, color=MUTED, anchor="end")
    l_f_amp = text(50, 248, "амплітуда Aₙ", size=12, color=MUTED, anchor="start")

    # Огинаюча sinc
    sinc_env_l = []
    for i in range(120):
        freq = i * 0.05
        arg = math.pi * freq * 0.8
        val = abs(math.sin(arg) / arg) if arg > 1e-4 else 1.0
        sinc_env_l.append((60 + i * 3.0, 360 - val * 95))
    pts_l = " ".join("%.1f,%.1f" % p for p in sinc_env_l)
    env_line_l = '<polyline fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="3,4" points="%s"/>' % (MUTED, pts_l)

    # Дискретні стовпчики
    stems_l = []
    for k in range(1, 14):
        bx = 60 + k * 26
        freq = k * 0.43
        arg = math.pi * freq * 0.8
        val = abs(math.sin(arg) / arg) if arg > 1e-4 else 1.0
        stems_l.append(bar(bx, 360, val * 95, color=NEG, dot=NEG, sw=2.4, r=3.0))

    df_note = text(240, 420, "дискретний крок ліній: Δf = 1/T₀", size=13, color=NEG, bold=True)

    # ── Права панель: Одиночний імпульс (T -> ∞, неперервний спектр) ──
    r_ttl = text(720, 60, "Одиночний імпульс: неперервний спектр", size=15, color=INK, bold=True)
    r_t_ax = arrow(530, 160, 910, 160, INK, 1.4)
    r_t_lbl = text(910, 180, "t", size=13, color=MUTED, anchor="end")
    r_t_sig_lbl = text(530, 95, "один імпульс (T₀ → ∞)", size=12, color=MUTED, anchor="start")

    # Один імпульс у центрі
    single_pulse = (rect(700, 115, 40, 45, fill="#fdecea", stroke=POS, sw=1.6, rx=2)
                    + line(700, 190, 740, 190, MUTED, 1.2)
                    + line(700, 182, 700, 198, MUTED, 1.2)
                    + line(740, 182, 740, 198, MUTED, 1.2)
                    + text(720, 212, "тривалість τ", size=12, color=MUTED))

    r_f_ax = arrow(530, 360, 910, 360, INK, 1.4)
    r_f_lbl = text(910, 380, "f", size=13, color=MUTED, anchor="end")
    r_f_amp = text(530, 248, "густина |X(f)|", size=12, color=MUTED, anchor="start")

    # Неперервна крива sinc
    sinc_env_r = []
    poly_pts = ["%.1f,%.1f" % (540, 360)]
    for i in range(120):
        freq = i * 0.05
        arg = math.pi * freq * 0.8
        val = abs(math.sin(arg) / arg) if arg > 1e-4 else 1.0
        px, py = 540 + i * 3.0, 360 - val * 95
        sinc_env_r.append((px, py))
        poly_pts.append("%.1f,%.1f" % (px, py))
    poly_pts.append("%.1f,%.1f" % (540 + 119 * 3.0, 360))

    sinc_poly = ('<polygon points="%s" fill="#fdecea" stroke="%s" stroke-width="1.8"/>'
                 % (" ".join(poly_pts), POS))
    zero_mark = (line(690, 355, 690, 365, INK, 1.4)
                 + text(690, 382, "1/τ", size=13, color=INK, bold=True)
                 + text(690, 420, "перший нуль спектра: f₀ = 1/τ", size=12, color=POS, bold=True))

    sep = line(mid_x, 60, mid_x, 440, MUTED, 1.0, dash="3,5")

    render(os.path.join(IMG, "discrete-vs-continuous.svg"), W, H,
           l_ttl, l_t_ax, l_t_lbl, l_t_sig_lbl, *pulses, t0_dim,
           l_f_ax, l_f_lbl, l_f_amp, env_line_l, *stems_l, df_note,
           sep,
           r_ttl, r_t_ax, r_t_lbl, r_t_sig_lbl, single_pulse,
           r_f_ax, r_f_lbl, r_f_amp, sinc_poly, zero_mark,
           title="Дискретний спектр періодичного сигналу та неперервний спектр імпульсу")


# ── Фігура 6: Зв'язок форми в часі та спадання спектра ────────────────────────
def fig_shapes_spectra_comparison():
    W, H = 980, 480
    cw = 280

    def col(x0, ttl, sub, t_shape_fn, decay_fn, decay_lbl, color):
        p = [text(x0 + cw / 2, 60, ttl, size=15, color=INK, bold=True),
             text(x0 + cw / 2, 82, sub, size=12, color=MUTED)]

        # Часова вісь
        ay_t = 165
        p.append(arrow(x0 + 10, ay_t, x0 + cw - 10, ay_t, INK, 1.4))
        p.append(text(x0 + cw - 10, ay_t + 16, "t", size=11, color=MUTED, anchor="end"))
        p.append(t_shape_fn(x0 + 20, ay_t, cw - 40))

        # Частотна вісь
        ay_f = 370
        p.append(arrow(x0 + 10, ay_f, x0 + cw - 10, ay_f, INK, 1.4))
        p.append(text(x0 + cw - 10, ay_f + 16, "f", size=11, color=MUTED, anchor="end"))
        p.append(decay_fn(x0 + 20, ay_f, cw - 40, color))
        p.append(text(x0 + cw / 2, 420, decay_lbl, size=13, color=color, bold=True))
        return p

    # 1. Меандр
    def draw_sq(x, y, w):
        pts = [(x, y + 25), (x + w * 0.25, y + 25), (x + w * 0.25, y - 25),
               (x + w * 0.75, y - 25), (x + w * 0.75, y + 25), (x + w, y + 25)]
        return '<polyline fill="none" stroke="%s" stroke-width="2.0" points="%s"/>' % (
            NEG, " ".join("%.1f,%.1f" % pt for pt in pts))

    def decay_sq(x, y, w, colr):
        stms = []
        for k, n in enumerate([1, 3, 5, 7, 9, 11]):
            bx = x + 15 + k * 35
            h = (1.0 / n) * 90
            stms.append(bar(bx, y, h, color=colr, dot=colr, sw=2.6, r=3.2))
        return "".join(stms)

    # 2. Трикутник
    def draw_tri(x, y, w):
        pts = [(x, y), (x + w * 0.25, y - 28), (x + w * 0.75, y + 28), (x + w, y)]
        return '<polyline fill="none" stroke="%s" stroke-width="2.0" points="%s"/>' % (
            FIELD, " ".join("%.1f,%.1f" % pt for pt in pts))

    def decay_tri(x, y, w, colr):
        stms = []
        for k, n in enumerate([1, 3, 5, 7, 9, 11]):
            bx = x + 15 + k * 35
            h = (1.0 / (n * n)) * 95
            stms.append(bar(bx, y, h, color=colr, dot=colr, sw=2.6, r=3.2))
        return "".join(stms)

    # 3. Дельта-імпульс
    def draw_delta(x, y, w):
        cx = x + w * 0.5
        arr = arrow(cx, y, cx, y - 45, POS, 2.4)
        lbl = text(cx + 8, y - 35, "δ(t)", size=13, color=POS, bold=True, anchor="start")
        return arr + lbl

    def decay_delta(x, y, w, colr):
        ln = line(x + 10, y - 60, x + w - 10, y - 60, colr, 2.2)
        poly_pts = ["%.1f,%.1f" % (x + 10, y), "%.1f,%.1f" % (x + 10, y - 60),
                    "%.1f,%.1f" % (x + w - 10, y - 60), "%.1f,%.1f" % (x + w - 10, y)]
        poly = ('<polygon points="%s" fill="#fdecea" stroke="none"/>' % " ".join(poly_pts))
        return poly + ln

    c1 = col(40, "Меандр", "розрив функції (ступінь)", draw_sq, decay_sq, "Спадання: 1/n (-6 дБ/окт)", NEG)
    c2 = col(350, "Трикутна хвиля", "неперервна, злам похідної", draw_tri, decay_tri, "Спадання: 1/n² (-12 дБ/окт)", FIELD)
    c3 = col(660, "Дельта-імпульс", "нескінченно короткий сплеск", draw_delta, decay_delta, "Рівномірний білий спектр", POS)

    div1 = line(335, 60, 335, 430, MUTED, 1.0, dash="2,5")
    div2 = line(645, 60, 645, 430, MUTED, 1.0, dash="2,5")

    render(os.path.join(IMG, "shapes-spectra-comparison.svg"), W, H,
           div1, div2, *c1, *c2, *c3,
           title="Гладкість сигналу в часі та швидкість спадання спектра")


# ── Фігура 7: Лінійна фільтрація та гармонічні спотворення (THD) ─────────────
def fig_filtering_and_thd():
    W, H = 980, 460
    mid_x = 490

    # ── Ліва панель: Лінійна фільтрація (ФНЧ) ──
    l_ttl = text(245, 60, "Лінійна система: фільтрація", size=15, color=INK, bold=True)
    l_sub = text(245, 82, "Y(f) = H(f) · X(f) — нові частоти не з'являються", size=12, color=MUTED)

    # Вхідний спектр
    ax_in = arrow(40, 200, 210, 200, INK, 1.4)
    lbl_in = text(125, 120, "Вхід X(f)", size=13, color=INK, bold=True)
    b_in1 = bar(75, 200, 65, color=NEG, dot=NEG)
    b_in2 = bar(115, 200, 50, color=MUTED, dot=MUTED)
    b_in3 = bar(155, 200, 55, color=MUTED, dot=MUTED)
    b_in4 = bar(185, 200, 45, color=MUTED, dot=MUTED)

    # Передавальна характеристика фільтра |H(f)|
    ax_h = arrow(270, 200, 440, 200, INK, 1.4)
    lbl_h = text(355, 120, "Фільтр |H(f)|", size=13, color=FIELD, bold=True)
    h_curve = (curve(275, 80, lambda t: 135, FIELD, 2.0)
               + curve(355, 45, lambda t: 135 + t * 65, FIELD, 2.0)
               + curve(400, 35, lambda t: 200, FIELD, 2.0))
    h_cutoff = text(355, 220, "зріз f_c", size=11, color=FIELD)

    # Стрілка операції множення
    arr_filter = arrow(218, 160, 262, 160, INK, 1.6)
    arr_res = arrow(448, 160, 475, 160, INK, 1.6)

    # Вихідний спектр
    ax_out = arrow(140, 360, 350, 360, INK, 1.4)
    lbl_out = text(245, 275, "Вихід Y(f) = H(f)·X(f)", size=13, color=INK, bold=True)
    b_out1 = bar(175, 360, 65, color=NEG, dot=NEG)
    b_out2 = bar(215, 360, 40, color=MUTED, dot=MUTED)
    b_out3 = bar(255, 360, 8, color=MUTED, dot=MUTED)
    b_out4 = bar(285, 360, 0, color=MUTED, dot=MUTED)
    filt_note = text(245, 420, "Фільтр послаблює верхні гармоніки", size=12, color=FIELD, bold=True)

    # ── Права панель: Нелінійні спотворення (THD) ──
    r_ttl = text(735, 60, "Нелінійна система: поява гармонік (THD)", size=15, color=INK, bold=True)
    r_sub = text(735, 82, "Чистий синус f₁ породжує вищі гармоніки 2f₁, 3f₁...", size=12, color=MUTED)

    # Спектр спотвореного сигналу
    ax_thd = arrow(530, 260, 930, 260, INK, 1.4)
    lbl_thd_f = text(930, 280, "частота", size=11, color=MUTED, anchor="end")

    # Стовпчик основної частоти f1
    h_f1 = bar(600, 260, 140, color=NEG, dot=NEG, sw=3.4, r=5.0)
    lbl_f1 = text(600, 282, "f₁ (основна)", size=13, color=NEG, bold=True)
    amp_f1 = text(600, 105, "A₁ = 1.0", size=12, color=INK, bold=True)

    # Гармоніки
    h_f2 = bar(680, 260, 28, color=POS, dot=POS, sw=2.6, r=4.0)
    lbl_f2 = text(680, 282, "2f₁", size=12, color=POS, bold=True)
    amp_f2 = text(680, 222, "A₂=0.20", size=11, color=POS)

    h_f3 = bar(760, 260, 15, color=POS, dot=POS, sw=2.6, r=4.0)
    lbl_f3 = text(760, 282, "3f₁", size=12, color=POS, bold=True)
    amp_f3 = text(760, 235, "A₃=0.10", size=11, color=POS)

    h_f4 = bar(840, 260, 7, color=POS, dot=POS, sw=2.6, r=4.0)
    lbl_f4 = text(840, 282, "4f₁", size=12, color=POS, bold=True)
    amp_f4 = text(840, 245, "A₄=0.05", size=11, color=POS)

    # Формула THD
    thd_box, _, _ = textbox(735, 365, "THD = √(A₂² + A₃² + A₄² + ...) / A₁ ≈ 22.9 %",
                            size=13, color=POS, bold=True, pad=10, fill="#fdecea", stroke=POS)
    thd_note = text(735, 420, "Нелінійність середовища чи підсилювача створює паразитичні гармоніки",
                    size=12, color=MUTED)

    sep = line(mid_x, 60, mid_x, 430, MUTED, 1.0, dash="3,5")

    render(os.path.join(IMG, "filtering-and-thd.svg"), W, H,
           l_ttl, l_sub, ax_in, lbl_in, b_in1, b_in2, b_in3, b_in4,
           ax_h, lbl_h, h_curve, h_cutoff, arr_filter,
           ax_out, lbl_out, b_out1, b_out2, b_out3, b_out4, filt_note,
           sep,
           r_ttl, r_sub, ax_thd, lbl_thd_f,
           h_f1, lbl_f1, amp_f1, h_f2, lbl_f2, amp_f2, h_f3, lbl_f3, amp_f3, h_f4, lbl_f4, amp_f4,
           thd_box, thd_note,
           title="Лінійна фільтрація та нелінійні гармонічні спотворення")


# ── Фігури до вставки proj-fft-spectrum ──────────────────────────────────────
# Фігура A: конвеєр «масив відліків → гребінець»
def fig_fft_pipeline():
    W, H = 1020, 470
    ys = 104
    boxes, arrows, notes = [], [], []
    spec = [(155, "x[n]: N відліків", ["крок 1/fs,", "тривалість T = N/fs"]),
            (400, "×  вікно w[n]", ["прибирає стрибок", "на стику блока"]),
            (640, "FFT → X[k]", ["N·log₂N дій", "замість N² у лоб"]),
            (875, "2·|X[k]| / Σw", ["амплітуда в", "одиницях сигналу"])]
    edges = []
    for cx, label, note in spec:
        body, w, h = textbox(cx, ys, label, size=15, bold=True, pad=11)
        boxes.append(body)
        edges.append((cx - w / 2, cx + w / 2))
        notes.append(mtext(cx, 162, note, size=12, color=MUTED, lh=1.45))
    for i in range(len(edges) - 1):
        arrows.append(arrow(edges[i][1] + 8, ys, edges[i + 1][0] - 8, ys, INK, 1.8))

    ay = 372
    cap = text(W / 2, 250, "Результат: висота стовпчика в біні k — амплітуда на частоті k·Δf",
               size=13, color=INK, bold=True)
    axis = arrow(92, ay, 968, ay, INK, 1.6)
    amps = [0.05, 0.18, 1.0, 0.22, 0.6, 0.12, 0.38, 0.09, 0.15, 0.06]
    comb, klab = [], []
    for k, a in enumerate(amps):
        bx = 118 + k * 88
        comb.append(bar(bx, ay, a * 96))
        klab.append(text(bx, 392, str(k), size=12, color=MUTED))
    x5, x6 = 118 + 5 * 88, 118 + 6 * 88
    dim = (line(x5, 414, x6, 414, MUTED, 1.4)
           + line(x5, 405, x5, 423, MUTED, 1.2) + line(x6, 405, x6, 423, MUTED, 1.2))
    dlab = text((x5 + x6) / 2, 440, "Δf = fs/N = 1/T", size=13, color=INK, bold=True)
    tail = text(968, 330, "правий край гребінця — бін N/2, тобто fs/2",
                size=12, color=MUTED, anchor="end")

    render(os.path.join(IMG, "fft-pipeline.svg"), W, H,
           *boxes, *arrows, *notes, cap, axis, *comb, *klab, dim, dlab, tail,
           title="Від масиву відліків до гребінця")


# Фігура B: витік — тон на вузлі, тон між вузлами, вікно Ганна
def fig_fft_leak():
    W, H = 940, 620
    SC = 110.0
    rect_on = [0.0] * 7 + [1.0] + [0.0] * 8
    rect_off = [0.0439, 0.0504, 0.0593, 0.0721, 0.0923, 0.1287, 0.2136, 0.6380,
                0.6353, 0.2109, 0.1260, 0.0896, 0.0694, 0.0565, 0.0477, 0.0411]
    hann_off = [0.0008, 0.0012, 0.0020, 0.0037, 0.0081, 0.0243, 0.1705, 0.8491,
                0.8491, 0.1705, 0.0243, 0.0081, 0.0037, 0.0020, 0.0012, 0.0008]

    def panel(ay, amps, ttl, note):
        p = [arrow(100, ay, 890, ay, INK, 1.6),
             text(100, ay - 128, ttl, size=15, color=INK, anchor="start", bold=True),
             text(890, ay - 128, note, size=12, color=MUTED, anchor="end")]
        for i, a in enumerate(amps):
            p.append(bar(118 + i * 50, ay, a * SC))
        return p

    a = panel(175, rect_on, "Тон точно на вузлі сітки — 100.0 Гц", "прямокутне вікно")
    a.append(text(478, 69, "1.00", size=12, color=INK, anchor="start", bold=True))
    b = panel(355, rect_off, "Тон між вузлами — 100.5 Гц", "прямокутне вікно")
    b.append(text(478, 289, "0.64", size=12, color=INK, anchor="start", bold=True))
    b.append(text(868, 325, "хвости тягнуться на весь спектр",
                  size=12, color=POS, anchor="end"))
    c = panel(535, hann_off, "Той самий тон — 100.5 Гц", "вікно Ганна")
    c.append(text(478, 446, "0.85", size=12, color=INK, anchor="start", bold=True))
    c.append(text(868, 505, "сусіди гаснуть за два біни",
                  size=12, color=FIELD, anchor="end"))

    xlab = [text(118 + i * 50, 555, s, size=12, color=MUTED)
            for i, s in ((2, "95"), (7, "100"), (12, "105"))]
    fl = text(500, 585, "частота, Гц", size=12, color=MUTED)

    render(os.path.join(IMG, "fft-leak.svg"), W, H, *a, *b, *c, *xlab, fl,
           title="Витік: та сама лінія на сітці й між вузлами")


# Фігура C: роздільність купується тільки тривалістю блока
def fig_fft_resolution():
    W, H = 940, 480
    SC = 69.0

    def xf(f):
        return 110 + (f - 422) * (780.0 / 36)

    short = [(424, 0.0266), (432, 0.6336), (440, 1.5917), (448, 1.0698), (456, 0.1111)]
    long_ = {439: 0.5001, 440: 1.0, 441: 0.5001, 442: 0.5001, 443: 1.0, 444: 0.5001}

    guides = [line(xf(f), 62, xf(f), 420, MUTED, 1.2, dash="5,6") for f in (440, 443)]
    top = text(W / 2, 48, "штрихові лінії — справжні тони 440 і 443 Гц",
               size=12, color=MUTED)

    def panel(ay, ttl, note):
        return [arrow(100, ay, 890, ay, INK, 1.6),
                text(100, ay - 114, ttl, size=15, color=INK, anchor="start", bold=True),
                text(890, ay - 114, note, size=12, color=MUTED, anchor="end")]

    p1 = panel(210, "Блок 0.125 с → крок сітки 8 Гц", "один горб, 443 Гц ніде не видно")
    for f, a in short:
        p1.append(bar(xf(f), 210, a * SC))
    p2 = panel(420, "Блок 1 с → крок сітки 1 Гц", "дві лінії рівно там, де треба")
    for f in range(430, 453):
        p2.append(bar(xf(f), 420, long_.get(f, 0.0) * SC))

    xlab = [text(xf(f), 440, str(f), size=12, color=MUTED)
            for f in (425, 430, 435, 440, 445, 450)]
    fl = text(W / 2, 466, "частота, Гц", size=12, color=MUTED)

    render(os.path.join(IMG, "fft-resolution.svg"), W, H,
           *guides, top, *p1, *p2, *xlab, fl,
           title="Роздільність купується тільки часом")


# ── Фігури до вставки hist-helmholtz ─────────────────────────────────────────
# Фігура D: два прилади Гельмгольца — аналіз і синтез
def fig_analysis_synthesis():
    W, H = 1000, 430
    ys = [126, 186, 246, 306]
    names = ["f", "2f", "3f", "4f"]

    # ── ліва панель: аналіз ──
    left = [text(265, 66, "Аналіз: розібрати звук", size=15, color=INK, bold=True),
            text(270, 92, "резонатори", size=12, color=MUTED),
            text(392, 92, "сила складової", size=12, color=MUTED),
            fitbox(60, 183, 118, 66, "складний\nзвук", size=13)]
    for y, nm, a in zip(ys, names, [1.0, 0.55, 0.30, 0.15]):
        bw = 110 * a
        left += [arrow(182, 216, 242, y, MUTED, 1.4),
                 circle(270, y, 25, fill=FILL, stroke=INK, sw=1.6),
                 text(270, y + 5, nm, size=14, color=INK, bold=True),
                 rect(304, y - 8, bw, 16, fill="#dbe4fb", stroke=NEG, sw=1.4, rx=3),
                 text(304 + bw + 8, y + 5, "%.2f" % a, size=12, color=MUTED, anchor="start")]
    left.append(mtext(265, 352,
                      ["куля відгукується лише на свою частоту:",
                       "у вухо йде тільки вона — і видно, яка сильна"],
                      size=12, color=MUTED))

    # ── права панель: синтез ──
    right = [text(740, 66, "Синтез: скласти звук назад", size=15, color=INK, bold=True),
             text(600, 92, "камертони", size=12, color=MUTED),
             text(726, 92, "задана сила", size=12, color=MUTED),
             fitbox(872, 186, 92, 60, "звучить\n«А»", size=13)]
    for y, nm, a in zip(ys, names, [1.0, 0.85, 0.45, 0.25]):
        bw = 90 * a
        right += [fitbox(546, y - 21, 108, 42, "камертон " + nm, size=12),
                  rect(668, y - 8, bw, 16, fill="#e2f4e8", stroke=FIELD, sw=1.4, rx=3),
                  text(668 + bw + 8, y + 5, "%.2f" % a, size=12, color=MUTED, anchor="start"),
                  arrow(804, y, 866, 216, MUTED, 1.4)]
    right.append(mtext(740, 352,
                       ["міняєш лише пропорції — і замість «А»",
                        "чується «О»; частоти при цьому ті самі"],
                       size=12, color=MUTED))

    divider = line(500, 84, 500, 372, MUTED, 1.0, dash="3,7")
    foot = text(500, 406,
                "доводить не кожен прилад окремо, а обидва разом: розібрати — і зібрати назад",
                size=13, color=MUTED)

    render(os.path.join(IMG, "analysis-synthesis.svg"), W, H,
           divider, *left, *right, foot,
           title="Два прилади Гельмгольца")


# Фігура E: хроніка суперечки про тон
def fig_tone_dispute_timeline():
    W, H = 1240, 380
    ax_y = 212
    xs = [92 + i * 151 for i in range(8)]

    events = [
        ("1841", ["Зеєбек: сирена", "з нерівними отворами", "— тон без основної"]),
        ("1843", ["Ом: слух — це", "розклад Фур'є,", "висота = найнижчий тон"]),
        ("1844", ["остання відповідь;", "Ом іде з акустики"]),
        ("1851", ["Корті описує", "устрій завитки"]),
        ("1859", ["резонатори", "Гельмгольца;", "тембр голосних"]),
        ("1863", ["«Вчення про слухові", "відчуття»: тембр —", "це набір обертонів"]),
        ("1940", ["Схаутен: висота є", "й без основного тону"]),
        ("1961·1978", ["Бекеші: біжуча", "хвиля в завитці;", "Кемп: вухо саме", "випромінює звук"]),
    ]

    parts = [line(50, ax_y, 912, ax_y, INK, 1.8),
             line(932, ax_y, 1200, ax_y, INK, 1.8),
             line(914, ax_y + 12, 924, ax_y - 12, MUTED, 1.6),
             line(922, ax_y + 12, 932, ax_y - 12, MUTED, 1.6)]

    for i, (yr, rows) in enumerate(events):
        x = xs[i]
        parts.append(circle(x, ax_y, 6, fill=NEG, stroke=NEG, sw=1.2))
        if i % 2 == 0:                      # опис угорі, рік унизу
            parts += [mtext(x, 160 - (len(rows) - 1) * 12 * 1.3, rows, size=12, color=INK),
                      line(x, 172, x, 202, MUTED, 1.0, dash="3,4"),
                      text(x, 238, yr, size=14, color=NEG, bold=True)]
        else:                               # опис унизу, рік угорі
            parts += [mtext(x, 264, rows, size=12, color=INK),
                      line(x, 222, x, 250, MUTED, 1.0, dash="3,4"),
                      text(x, 200, yr, size=14, color=NEG, bold=True)]

    foot = text(W / 2, 352,
                "злам на осі — сімдесят сім років, за які з'явилася апаратура, здатна перевірити спірне",
                size=13, color=MUTED)

    render(os.path.join(IMG, "tone-dispute-timeline.svg"), W, H,
           *parts, foot, title="Від сирени Зеєбека до звуку, що йде з вуха назовні")


if __name__ == "__main__":
    fig_time_vs_freq()
    fig_timbre()
    fig_signatures()
    fig_fourier_synthesis()
    fig_discrete_vs_continuous()
    fig_shapes_spectra_comparison()
    fig_filtering_and_thd()
    fig_fft_pipeline()
    fig_fft_leak()
    fig_fft_resolution()
    fig_analysis_synthesis()
    fig_tone_dispute_timeline()
    print("OK: 12 SVG у", IMG)
