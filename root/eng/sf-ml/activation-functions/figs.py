# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Помічник: намалювати осі + криву y=f(x) у заданому «вікні» графіка ─────────
def _panel(px, py, pw, ph, xr, yr, f, col, sw=2.4, dash=None, samples=120):
    """Повертає (список фрагментів осей+сітки, функція->точки).
    px,py — лівий-верхній кут панелі; pw,ph — розміри; xr=(xmin,xmax); yr=(ymin,ymax)."""
    xmin, xmax = xr
    ymin, ymax = yr

    def X(x):
        return px + (x - xmin) / (xmax - xmin) * pw

    def Y(y):
        return py + ph - (y - ymin) / (ymax - ymin) * ph

    frags = []
    # рамка панелі
    frags.append(rect(px, py, pw, ph, fill=BG, stroke="#c9d2dc", sw=1.2, rx=6))
    # осі (x=0, y=0), якщо в межах
    if xmin <= 0 <= xmax:
        frags.append(line(X(0), py, X(0), py + ph, color="#b0b8c2", sw=1.2))
    if ymin <= 0 <= ymax:
        frags.append(line(px, Y(0), px + pw, Y(0), color="#b0b8c2", sw=1.2))

    # сама крива як polyline
    pts = []
    for i in range(samples + 1):
        x = xmin + (xmax - xmin) * i / samples
        y = f(x)
        y = max(ymin, min(ymax, y))
        pts.append("%.1f,%.1f" % (X(x), Y(y)))
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
                 % (" ".join(pts), col, sw, d))
    return frags, X, Y


# ── shapes: чотири базові активації поряд (сходинка, сигмоїда, tanh, ReLU) ─────
# Ідея: показати «форму» кожної відповіді й межі виходу — читач бачить, чим вони
# різняться геометрично: різкий поріг → плавний 0…1 → плавний −1…1 → злам у нулі.
def fig_shapes():
    W, H = 840, 320
    p = []
    pw, ph = 176, 176
    gap = 30
    top = 62
    xr = (-4, 4)

    def sig(x):
        return 1.0 / (1.0 + math.exp(-x))

    panels = [
        ("сходинка", "0 або 1", lambda x: 0.0 if x < 0 else 1.0, (-0.15, 1.15), POS),
        ("сигмоїда", "σ(x) → 0…1", sig, (-0.15, 1.15), NEG),
        ("tanh", "→ −1…1", math.tanh, (-1.2, 1.2), FIELD),
        ("ReLU", "max(0, x)", lambda x: max(0.0, x), (-0.6, 4.0), "#8e44ad"),
    ]
    x0 = 26
    for i, (name, sub, f, yr, col) in enumerate(panels):
        px = x0 + i * (pw + gap)
        frags, X, Y = _panel(px, top, pw, ph, xr, yr, f, col)
        p += frags
        p.append(text(px + pw / 2, top - 30, name, size=13, color=col, bold=True))
        p.append(text(px + pw / 2, top - 14, sub, size=10.5, color=MUTED))

    # підпис-висновок унизу (два рядки → більший шрифт)
    p.append(fitbox(x0, top + ph + 16, W - 2 * x0, 46,
                    "Сходинка — різкий поріг (недиференційовна). Сигмоїда й tanh — плавні S-криві, але «насичуються» на краях.\n"
                    "ReLU — злам у нулі: наліво рівний нуль, направо пряма (найдешевша й найпоширеніша нині).",
                    size=11, fill=FILL, stroke="#c9d2dc", sw=1.2, color=INK))

    render(os.path.join(OUT, "shapes.svg"), W, H, *p,
           title="Форми чотирьох активацій: поріг, сигмоїда, tanh, ReLU")


# ── saturation: чому сигмоїда «гасить» градієнт — похідна-дзвін тисне до 0 ─────
# Ідея: ліворуч сама σ і її похідна (дзвін, макс 0.25); праворуч — як добуток
# малих похідних крізь шари гасне: 0.2·0.2·0.2·… → майже нуль на вході.
def fig_saturation():
    W, H = 840, 344
    p = []

    def sig(x):
        return 1.0 / (1.0 + math.exp(-x))

    def dsig(x):
        s = sig(x)
        return s * (1 - s)

    # ── ЛІВА панель: σ (синя) і σ' (помаранч, дзвін) ──
    px, py, pw, ph = 40, 66, 320, 200
    xr, yr = (-6, 6), (-0.05, 1.05)
    frags, X, Y = _panel(px, py, pw, ph, xr, yr, sig, NEG, sw=2.4)
    p += frags
    # похідна поверх (масштаб той самий, макс 0.25)
    dfrags, _, _ = _panel(px, py, pw, ph, xr, yr, dsig, "#e67e22", sw=2.2, dash="6 4")
    # беремо лише криву-polyline (останній елемент), без повторної рамки/осей
    p.append(dfrags[-1])
    p.append(text(px + pw - 6, Y(sig(5)) - 8, "σ(x)", size=11, color=NEG, bold=True, anchor="end"))
    p.append(text(X(0) + 6, Y(0.25) - 6, "σ′(x) ≤ 0.25", size=11, color="#b5651d", bold=True, anchor="start"))
    # зони насичення
    p.append(rect(px, py, X(-2.6) - px, ph, fill="#25467010", stroke="none", sw=0))
    p.append(rect(X(2.6), py, px + pw - X(2.6), ph, fill="#25467010", stroke="none", sw=0))
    p.append(text(px + 40, py + 18, "насичення", size=9.5, color=NEG))
    p.append(text(px + pw - 40, py + 18, "насичення", size=9.5, color=NEG))
    p.append(text(px + pw / 2, py + ph + 20, "де σ плоска — нахил ≈ 0", size=10, color=MUTED))

    # ── ПРАВА панель: множення похідних крізь шари → затухання ──
    rx, ry = 440, 82
    p.append(text(rx + 170, ry - 20, "градієнт назад = добуток нахилів", size=12, color=INK, bold=True))
    # ланцюг шарів із множниками
    vals = [0.20, 0.20, 0.20, 0.20]
    bw, bh = 58, 42
    x = rx
    y = ry + 20
    prev = None
    for i, v in enumerate(vals):
        p.append(rect(x, y, bw, bh, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
        p.append(text(x + bw / 2, y + 17, "шар %d" % (len(vals) - i), size=9.5, color=NEG, bold=True))
        p.append(text(x + bw / 2, y + 33, "×%.2f" % v, size=10, color="#b5651d", bold=True))
        if prev is not None:
            p.append(arrow(prev + bw + 2, y + bh / 2, x - 2, y + bh / 2, color=INK, sw=1.6))
        prev = x
        x += bw + 26
    p.append(text(rx + 3 * (bw + 26) + bw + 8, y + bh / 2 + 4, "→ вхід", size=10, color=MUTED, anchor="start"))

    # добуток
    prod = 1.0
    for v in vals:
        prod *= v
    p.append(fitbox(rx, y + bh + 26, 360, 92,
                    "0.20 · 0.20 · 0.20 · 0.20 ≈ %.4f\n"
                    "Кожен насичений шар домножує градієнт на ≤ 0.25.\n"
                    "Через десяток шарів він гасне до нуля — глибокі шари\n"
                    "майже не вчаться. Це «затухання градієнта»." % prod,
                    size=10.5, fill=FILL, stroke=POS, sw=1.4, color=INK))

    render(os.path.join(OUT, "saturation.svg"), W, H, *p,
           title="Насичення сигмоїди й затухання градієнта крізь шари")


# ── relu-family: ReLU і його полагоджені родичі (Leaky, плавний Swish/GELU) ────
# Ідея: показати ваду ReLU (мертвий нейрон — плоский нуль наліво, нахил 0) і як
# її лікують: Leaky дає малий нахил наліво; Swish/GELU — плавний провал і нахил.
def fig_relu_family():
    W, H = 840, 320
    p = []
    pw, ph = 236, 200
    gap = 40
    top = 62
    xr, yr = (-4, 4), (-1.0, 4.0)

    def relu(x):
        return max(0.0, x)

    def leaky(x):
        return x if x > 0 else 0.1 * x

    def sig(x):
        return 1.0 / (1.0 + math.exp(-x))

    def swish(x):
        return x * sig(x)

    panels = [
        ("ReLU", "max(0, x)", relu, "#8e44ad",
         "наліво рівний нуль → нахил 0:\nнейрон може «померти»"),
        ("Leaky ReLU", "малий нахил наліво", leaky, "#16a085",
         "наліво не нуль, а 0.1·x →\nградієнт завжди тече"),
        ("Swish / GELU", "плавний згин", swish, "#c0392b",
         "гладко, з легким провалом:\nнахил ніде не зникає різко"),
    ]
    x0 = 24
    for i, (name, sub, f, col, note) in enumerate(panels):
        px = x0 + i * (pw + gap)
        frags, X, Y = _panel(px, top, pw, ph, xr, yr, f, col, sw=2.6)
        p += frags
        p.append(text(px + pw / 2, top - 30, name, size=13, color=col, bold=True))
        p.append(text(px + pw / 2, top - 14, sub, size=10.5, color=MUTED))
        p.append(fitbox(px, top + ph + 12, pw, 42, note, size=10, fill=FILL,
                        stroke="#c9d2dc", sw=1.1, color=INK))

    render(os.path.join(OUT, "relu-family.svg"), W, H, *p,
           title="ReLU і його полагоджені родичі: Leaky, Swish/GELU")


# ── lineage: дві родові лінії активацій, ноди рівним кроком (не в справжньому
# масштабі часу — інакше все злиплося б у 2010-х). Верхня нитка — «плавний поріг»
# (логістична крива Верхюльста → у мережу через backprop → буксування). Нижня —
# «випрямляч» (Фукусіма → Наір-Гінтон → глибокі rectifier → AlexNet → Swish).
# Обидві сходяться до 2012 — де випрямляч переміг поріг.
def fig_lineage():
    W, H = 980, 430
    p = []
    x0, x1 = 92, W - 92

    def node(cx, cy, year, lab, col, fill, w=150, h=52):
        """Ромб-віха з роком + рамка-підпис під/над ним."""
        s = []
        s.append(fitbox(cx - w / 2, cy - h / 2, w, h, lab, size=9.5,
                        fill=fill, stroke=col, sw=1.3, color=INK))
        s.append(circle(cx, cy + h / 2 + 13, 12, fill=BG, stroke=col, sw=1.4))
        s.append(text(cx, cy + h / 2 + 16.5, str(year)[2:], size=10, color=col, bold=True))
        return s, cx, cy + h / 2 + 13

    def spread(n):
        return [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]

    # ── ВЕРХНЯ нитка: плавний поріг ──
    yU = 92
    p.append(text(x0 - 8, 52, "лінія «плавного порога» (сигмоїда)", size=12, color=NEG, bold=True, anchor="start"))
    up = [
        (1838, "логістична крива\nросту населення\n(Верхюльст)"),
        (1986, "входить у мережу\nчерез backprop\n(Румельгарт, Гінтон,\nВільямс)"),
        (2012, "у глибині буксує:\nзатухаючий\nградієнт"),
    ]
    ux = [x0 + 40, (x0 + x1) / 2, x1 - 40]
    prev = None
    for (yr, lab), cx in zip(up, ux):
        frs, nx, ny = node(cx, yU, yr, lab, NEG, "#eaf0fd", w=158, h=58)
        p += frs
        if prev is not None:
            p.append(arrow(prev[0] + 12, prev[1], nx - 12, ny, color=NEG, sw=1.6))
        prev = (nx, ny)

    # ── НИЖНЯ нитка: випрямляч ──
    yD = 300
    p.append(text(x0 - 8, H - 20, "лінія «випрямляча» (ReLU)", size=12, color="#8e44ad", bold=True, anchor="start"))
    down = [
        (1969, "аналоговий поріг\nmax(0,x) у мережі\n(Фукусіма)"),
        (2010, "ReLU оживляє\nмашину Больцмана\n(Наір, Гінтон)"),
        (2011, "глибокі rectifier-\nмережі без\nпідготовки\n(Глоро, Борде,\nБенжіо)"),
        (2012, "AlexNet: ~6×\nшвидше за tanh\n(Крижевський,\nСуцкевер, Гінтон)"),
        (2017, "Swish x·σ(x)\nзнайдено\nавтопошуком\n(Google Brain)"),
    ]
    dx = spread(len(down))
    prev = None
    for (yr, lab), cx in zip(down, dx):
        frs, nx, ny = node(cx, yD, yr, lab, "#8e44ad", "#f3e8fb", w=158, h=64)
        p += frs
        if prev is not None:
            p.append(arrow(prev[0] + 12, prev[1], nx - 12, ny, color="#8e44ad", sw=1.6))
        prev = (nx, ny)

    # вертикаль-перелом 2012: обидві нитки сходяться
    conv_x = x1 - 40  # ≈ де стоїть «AlexNet» унизу і «буксує» вгорі
    p.append(line(ux[-1], yU + 42, dx[-2], yD - 42, color="#c0392b", sw=1.2, dash="4 4"))
    p.append(text((ux[-1] + dx[-2]) / 2 + 24, (yU + yD) / 2, "2012:", size=11, color="#c0392b", bold=True, anchor="start"))
    p.append(text((ux[-1] + dx[-2]) / 2 + 24, (yU + yD) / 2 + 15, "випрямляч", size=10, color="#c0392b", anchor="start"))
    p.append(text((ux[-1] + dx[-2]) / 2 + 24, (yU + yD) / 2 + 29, "переміг поріг", size=10, color="#c0392b", anchor="start"))

    # висновок унизу
    p.append(fitbox(x0, H - 52, 470, 34,
                    "Дві нитки століттями йшли нарізно — крива росту населення й випрямляч —\n"
                    "і перетнулися аж у глибокому навчанні.",
                    size=10, fill=FILL, stroke="#c9d2dc", sw=1.2, color=INK))

    render(os.path.join(OUT, "lineage.svg"), W, H, *p,
           title="Дві родові лінії активацій: плавний поріг і випрямляч")


# ── softmax-pipeline: логіти → експонента → нормування (три кроки) ─────────────
# Ідея: показати механіку softmax як конвеєр. Ліворуч сирі логіти (є від'ємні),
# посередині після exp — усі додатні й розрив підкреслено, праворуч після ділення
# на суму — три ймовірності, що складаються в 1. Приклад (2.0, 1.0, 0.1).
def fig_softmax_pipeline():
    W, H = 860, 340
    p = []

    logits = [2.0, 1.0, 0.1]
    exps = [math.exp(z) for z in logits]
    s = sum(exps)
    probs = [e / s for e in exps]
    labels = ["клас 1", "клас 2", "клас 3"]

    pw, ph = 210, 190           # панель графіка стовпчиків
    top = 74
    gap = 100                   # проміжок під стрілку між панелями
    x0 = 26

    def _bars(px, vals, ymax, col, fmt, negmin=0.0):
        """Стовпчикова панель: рамка + осьова лінія нуля + стовпчики з підписами."""
        frags = [rect(px, top, pw, ph, fill=BG, stroke="#c9d2dc", sw=1.2, rx=6)]
        yr0, yr1 = (negmin, ymax)
        span = yr1 - yr0

        def Y(v):
            return top + ph - (v - yr0) / span * ph

        if yr0 < 0 <= yr1:
            frags.append(line(px, Y(0), px + pw, Y(0), color="#b0b8c2", sw=1.2))
        n = len(vals)
        slot = pw / n
        bw = slot * 0.5
        for i, v in enumerate(vals):
            cx = px + slot * (i + 0.5)
            y_top = Y(max(v, 0))
            y_bot = Y(min(v, 0))
            h = max(2.0, y_bot - y_top)
            frags.append(rect(cx - bw / 2, y_top, bw, h, fill=col, stroke="none", sw=0, rx=3))
            ty = y_top - 7 if v >= 0 else y_bot + 14
            frags.append(text(cx, ty, fmt % v, size=11, color=INK, bold=True))
            frags.append(text(cx, top + ph + 16, labels[i], size=10, color=MUTED))
        return frags

    px1 = x0
    px2 = x0 + pw + gap
    px3 = x0 + 2 * (pw + gap)

    p += _bars(px1, logits, 2.4, NEG, "%.1f", negmin=-0.4)
    p += _bars(px2, exps, 8.2, "#8e44ad", "%.2f", negmin=0.0)
    p += _bars(px3, probs, 1.0, FIELD, "%.2f", negmin=0.0)

    p.append(text(px1 + pw / 2, top - 34, "логіти z", size=13, color=NEG, bold=True))
    p.append(text(px1 + pw / 2, top - 18, "сирі оцінки (є від'ємні)", size=10, color=MUTED))
    p.append(text(px2 + pw / 2, top - 34, "e^z", size=13, color="#8e44ad", bold=True))
    p.append(text(px2 + pw / 2, top - 18, "усі додатні, розрив підкреслено", size=10, color=MUTED))
    p.append(text(px3 + pw / 2, top - 34, "e^z / Σ", size=13, color=FIELD, bold=True))
    p.append(text(px3 + pw / 2, top - 18, "ймовірності, Σ = 1", size=10, color=MUTED))

    ay = top + ph / 2
    p.append(arrow(px1 + pw + 8, ay, px2 - 8, ay, color=INK, sw=2.0))
    p.append(text((px1 + pw + px2) / 2, ay - 12, "exp", size=11, color=INK, bold=True))
    p.append(arrow(px2 + pw + 8, ay, px3 - 8, ay, color=INK, sw=2.0))
    p.append(text((px2 + pw + px3) / 2, ay - 12, "÷ Σ", size=11, color=INK, bold=True))

    p.append(fitbox(x0, top + ph + 30, W - 2 * x0, 40,
                    "Два кроки: експонента робить оцінки додатними й розтягує розрив між ними; "
                    "ділення на суму зводить їх у чесний розподіл (0.66, 0.24, 0.10), що дає рівно 1.",
                    size=11, fill=FILL, stroke="#c9d2dc", sw=1.2, color=INK))

    render(os.path.join(OUT, "softmax-pipeline.svg"), W, H, *p,
           title="softmax як конвеєр: логіти -> експонента -> нормування")


# ── softmax-temperature: та сама трійка логітів за трьох температур ───────────
# Ідея: показати, що «м'якість» регульована. Низька T → гостро (майже argmax),
# T=1 → штатно, висока T → пласко (майже рівномірно). Логіти (2.0, 1.0, 0.1).
def fig_softmax_temperature():
    W, H = 840, 320
    p = []

    logits = [2.0, 1.0, 0.1]
    labels = ["к1", "к2", "к3"]

    def softmax_T(z, T):
        e = [math.exp(v / T) for v in z]
        s = sum(e)
        return [v / s for v in e]

    pw, ph = 216, 188
    gap = 42
    top = 70
    x0 = 24

    panels = [
        (0.5, "гостро", POS, "лідер забирає майже все"),
        (1.0, "штатно (T=1)", NEG, "звичайний softmax"),
        (5.0, "розмито", FIELD, "класи майже зрівнялись"),
    ]

    for i, (T, name, col, note) in enumerate(panels):
        px = x0 + i * (pw + gap)
        probs = softmax_T(logits, T)
        p.append(rect(px, top, pw, ph, fill=BG, stroke="#c9d2dc", sw=1.2, rx=6))

        def Y(v):
            return top + ph - v * ph

        for gv in (0.5, 1.0):
            p.append(line(px, Y(gv), px + pw, Y(gv), color="#e2e7ee", sw=1.0))
        n = len(probs)
        slot = pw / n
        bw = slot * 0.5
        for j, v in enumerate(probs):
            cx = px + slot * (j + 0.5)
            yt = Y(v)
            p.append(rect(cx - bw / 2, yt, bw, top + ph - yt, fill=col, stroke="none", sw=0, rx=3))
            p.append(text(cx, yt - 7, "%.2f" % v, size=10.5, color=INK, bold=True))
            p.append(text(cx, top + ph + 15, labels[j], size=9.5, color=MUTED))
        p.append(text(px + pw / 2, top - 32, "T = %.1f" % T, size=13, color=col, bold=True))
        p.append(text(px + pw / 2, top - 16, name, size=10.5, color=MUTED))
        p.append(fitbox(px, top + ph + 26, pw, 30, note, size=10, fill=FILL,
                        stroke="#c9d2dc", sw=1.1, color=INK))

    render(os.path.join(OUT, "softmax-temperature.svg"), W, H, *p,
           title="Температура softmax: ті самі логіти, різна різкість")


if __name__ == "__main__":
    fig_shapes()
    fig_saturation()
    fig_relu_family()
    fig_lineage()
    fig_softmax_pipeline()
    fig_softmax_temperature()
    print("OK: figures written to", OUT)
