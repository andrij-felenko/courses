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


# ── Фігури до вставки proj-fft-spectrum ──────────────────────────────────────
def bar(x, y0, h, color=INK, dot=NEG, sw=2.6, r=3.4):
    """Тонкий стовпчик спектра з кружечком-вершиною (для щільних сіток бінів)."""
    return (line(x, y0, x, y0 - h, color, sw)
            + circle(x, y0 - h, r, fill=dot, stroke=dot))


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
    # значення пораховані numpy-кодом зі статті (біни 93…108 при fs = 1000, N = 1000)
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
    fig_fft_pipeline()
    fig_fft_leak()
    fig_fft_resolution()
    fig_analysis_synthesis()
    fig_tone_dispute_timeline()
    print("OK: 8 SVG у", IMG)
