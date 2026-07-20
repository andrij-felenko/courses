# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

INLIER = "#16a34a"   # згодна точка (inlier)
OUTL   = "#c0392b"   # викид (outlier)
LSCOL  = "#c0392b"   # лінія найменших квадратів (потягнута)
RSCOL  = "#16a34a"   # лінія RANSAC
BAND   = "#16a34a"   # смуга допуску
SAMPLE = "#7c3aed"   # взяті у вибірку точки


# ── спільні дані: хмара точок уздовж прямої + кілька викидів унизу-праворуч ─────
# координати локальні до панелі (x праворуч, y донизу — прямий SVG)
INLIERS = [(50, 152), (80, 134), (110, 126), (140, 108), (170, 100),
           (200, 84), (230, 74), (258, 60), (288, 50)]
OUTLIERS = [(228, 196), (256, 190), (284, 182)]


def fit_line(pts):
    """Пряма y = k·x + b за найменшими квадратами. Повертає (k, b)."""
    n = len(pts)
    sx = sum(p[0] for p in pts); sy = sum(p[1] for p in pts)
    sxx = sum(p[0] * p[0] for p in pts); sxy = sum(p[0] * p[1] for p in pts)
    den = n * sxx - sx * sx
    k = (n * sxy - sx * sy) / den
    b = (sy - k * sx) / n
    return k, b


def line_through(p, q):
    """Пряма через дві точки як (a,b,c): a·x+b·y+c=0, нормована (a²+b²=1)."""
    a = q[1] - p[1]
    b = p[0] - q[0]
    c = -(a * p[0] + b * p[1])
    m = math.hypot(a, b) or 1.0
    return a / m, b / m, c / m


def dist(abc, pt):
    a, b, c = abc
    return abs(a * pt[0] + b * pt[1] + c)


def points_word(n):
    """Правильна форма слова «точка» для числа n (укр.)."""
    d100 = n % 100
    d10 = n % 10
    if 11 <= d100 <= 14:
        return "точок"
    if d10 == 1:
        return "точка"
    if 2 <= d10 <= 4:
        return "точки"
    return "точок"


def _dot(cx, cy, col, r=5.5, ring=False):
    out = circle(cx, cy, r, fill=col, stroke="#ffffff", sw=1.2)
    if ring:
        out += circle(cx, cy, r + 4, fill="none", stroke=SAMPLE, sw=2.2)
    return out


def _panel(x, y, w, h, title, tcol):
    out = rect(x, y, w, h, fill="#fbfbfd", stroke=tcol, sw=1.8, rx=12)
    out += text(x + w / 2, y + 24, title, size=13, color=tcol, bold=True)
    return out


# ── ФІГУРА 1: найменші квадрати тягне до викидів — RANSAC їх ігнорує ────────────
def fig_ls_vs_ransac():
    W, H = 820, 384
    p = []
    pw, ph = 344, 250
    ys = 60
    xs = [40, W - 40 - pw]
    px0, py0 = 30, 44          # відступ області побудови всередині панелі
    xr = (40, 300)             # діапазон x для малювання лінії

    # ── ліва панель: LS по ВСІХ точках (тягнеться вниз до викидів) ──
    p.append(_panel(xs[0], ys, pw, ph, "Найменші квадрати — по всіх точках", LSCOL))
    kx, bx = fit_line(INLIERS + OUTLIERS)
    y1 = kx * xr[0] + bx; y2 = kx * xr[1] + bx
    p.append(line(xs[0] + xr[0], ys + y1, xs[0] + xr[1], ys + y2, color=LSCOL, sw=3))
    for (lx, ly) in INLIERS:
        p.append(_dot(xs[0] + lx, ys + ly, INK, r=5))      # LS не знає, хто викид
    for (lx, ly) in OUTLIERS:
        p.append(_dot(xs[0] + lx, ys + ly, INK, r=5))
    p.append(text(xs[0] + pw / 2, ys + ph - 16,
                  "три викиди внизу тягнуть пряму — вона не лягла ні на кого",
                  size=9.5, color=MUTED))

    # ── права панель: RANSAC — пряма по чесних, викиди відсіяні ──
    p.append(_panel(xs[1], ys, pw, ph, "RANSAC — тільки по згодних точках", RSCOL))
    kr, br = fit_line(INLIERS)
    y1 = kr * xr[0] + br; y2 = kr * xr[1] + br
    p.append(line(xs[1] + xr[0], ys + y1, xs[1] + xr[1], ys + y2, color=RSCOL, sw=3))
    for (lx, ly) in INLIERS:
        p.append(_dot(xs[1] + lx, ys + ly, INLIER, r=5))
    for (lx, ly) in OUTLIERS:
        c = xs[1] + lx; cc = ys + ly
        p.append(circle(c, cc, 6.5, fill="none", stroke=OUTL, sw=2))
        p.append(line(c - 4, cc - 4, c + 4, cc + 4, color=OUTL, sw=2))
        p.append(line(c - 4, cc + 4, c + 4, cc - 4, color=OUTL, sw=2))
    p.append(text(xs[1] + pw / 2, ys + ph - 16,
                  "викиди (×) відкинуто — пряма лягла на чесну хмару",
                  size=9.5, color=MUTED))

    render(os.path.join(OUT, "ls-vs-ransac.svg"), W, H, *p,
           title="Один викид псує найменші квадрати; RANSAC його не пускає")


# ── ФІГУРА 2: цикл RANSAC — вибірка → модель → згода → рекорд, і знову ──────────
def fig_ransac_loop():
    W, H = 820, 366
    p = []
    cx, cy = W / 2, 180
    bw, bh = 208, 66
    # чотири вузли по колу
    nodes = [
        (cx,        70,  "1. ВИБІРКА",  "взяти навмання мінімум точок\n(для прямої — лише 2)"),
        (cx + 250, 180,  "2. МОДЕЛЬ",   "побудувати модель\nрівно по цій вибірці"),
        (cx,       290,  "3. ЗГОДА",    "полічити точки в межах ±t\nвід моделі — це «свої»"),
        (cx - 250, 180,  "4. РЕКОРД",   "згоди більше, ніж досі?\nзапам'ятати цю модель"),
    ]
    cols = [SAMPLE, NEG, INLIER, "#d98a00"]
    for i, (nx, ny, head, body) in enumerate(nodes):
        p.append(rect(nx - bw / 2, ny - bh / 2, bw, bh, fill="#fbfbfd",
                      stroke=cols[i], sw=1.8, rx=10))
        p.append(text(nx, ny - 12, head, size=12, color=cols[i], bold=True))
        for j, ln in enumerate(body.split("\n")):
            p.append(text(nx, ny + 6 + j * 15, ln, size=9.5, color=INK))

    # стрілки по колу (за годинниковою)
    p.append(arrow(cx + bw / 2 - 16, 92, cx + 250 - bw / 2, 158, color=INK, sw=1.8))
    p.append(arrow(cx + 250 - 4, 180 + bh / 2, cx + 8, 290 - bh / 2 + 2, color=INK, sw=1.8))
    p.append(arrow(cx - bw / 2 + 16, 268, cx - 250 + bw / 2, 202, color=INK, sw=1.8))
    p.append(arrow(cx - 250 + 4, 180 - bh / 2, cx - 8, 70 + bh / 2 - 2, color=INK, sw=1.8))

    # підпис у центрі — «повторити k разів»
    p.append(text(cx, 172, "повторити", size=13, color=MUTED, bold=True))
    p.append(text(cx, 192, "k разів", size=13, color=MUTED, bold=True))

    # вихід із «рекорду» вниз — переможець
    p.append(arrow(cx - 250, 180 + bh / 2, cx - 250, 322, color=RSCOL, sw=2))
    p.append(fitbox(cx - 250 - 155, 326, 310, 40,
                    "переможець = модель із найбільшою згодою;\n"
                    "наприкінці уточнити її по всіх згодних точках", size=10,
                    fill="#eaf7ee", stroke=RSCOL, sw=1.4, color=INK))

    render(os.path.join(OUT, "ransac-loop.svg"), W, H, *p,
           title="RANSAC: вгадай по дрібці — хай решта проголосує — лиши найкраще")


# ── ФІГУРА 3: чому згода відбирає правильну модель (вдала vs невдала спроба) ────
def fig_good_vs_bad_trial():
    W, H = 820, 392
    p = []
    pw, ph = 344, 258
    ys = 60
    xs = [40, W - 40 - pw]
    t = 20.0        # напів-ширина смуги допуску, px
    xr = (36, 306)

    def band_and_count(x, sample_pts, head, hcol):
        p.append(_panel(x, ys, pw, ph, head, hcol))
        abc = line_through(sample_pts[0], sample_pts[1])
        a, b, c = abc
        # намалювати центральну пряму й дві межі смуги ±t (зсув уздовж нормалі)
        def seg(cshift, col, sw, dash=None):
            cc = c + cshift
            # y для двох x: b·y = -(a·x + cc) → y = -(a·x+cc)/b
            if abs(b) < 1e-6:
                return ""
            yA = -(a * xr[0] + cc) / b
            yB = -(a * xr[1] + cc) / b
            return line(x + xr[0], ys + yA, x + xr[1], ys + yB, color=col, sw=sw, dash=dash)
        p.append(seg(-t, BAND, 1.2, "5,4"))
        p.append(seg(+t, BAND, 1.2, "5,4"))
        p.append(seg(0, hcol, 2.6))
        # точки: зелені якщо в смузі, сірі якщо ні; вибіркові — фіолетове кільце
        cnt = 0
        for (lx, ly) in INLIERS + OUTLIERS:
            inb = dist(abc, (lx, ly)) <= t
            if inb:
                cnt += 1
            col = INLIER if inb else "#9aa4b2"
            ring = (lx, ly) in sample_pts
            p.append(_dot(x + lx, ys + ly, col, r=5, ring=ring))
        return cnt

    # ── ліва: невдала — у вибірці є викид, пряма косо, згоди мало ──
    bad_sample = [INLIERS[0], OUTLIERS[2]]
    cb = band_and_count(xs[0], bad_sample, "Невдала спроба", OUTL)
    p.append(text(xs[0] + pw / 2, ys + ph - 34,
                  "вибірка зачепила викид → пряма косо", size=10, color=MUTED))
    p.append(text(xs[0] + pw / 2, ys + ph - 15,
                  "згода: %d %s" % (cb, points_word(cb)), size=13, color=OUTL, bold=True))

    # ── права: вдала — вибірка з чесних, згоди багато ──
    good_sample = [INLIERS[2], INLIERS[7]]
    cg = band_and_count(xs[1], good_sample, "Вдала спроба", INLIER)
    p.append(text(xs[1] + pw / 2, ys + ph - 34,
                  "вибірка з чесних точок → пряма лягла", size=10, color=MUTED))
    p.append(text(xs[1] + pw / 2, ys + ph - 15,
                  "згода: %d %s" % (cg, points_word(cg)), size=13, color=INLIER, bold=True))

    # легенда — фіолетове кільце = взяте у вибірку
    p.append(circle(xs[0] + 20, ys - 2, 5.5, fill=INK, stroke="#fff", sw=1.2))
    p.append(circle(xs[0] + 20, ys - 2, 9.5, fill="none", stroke=SAMPLE, sw=2.2))
    p.append(text(xs[0] + 34, ys + 2, "— точки вибірки", size=9.5, color=INK, anchor="start"))

    render(os.path.join(OUT, "good-vs-bad-trial.svg"), W, H, *p,
           title="Згода відбирає модель: чиста вибірка збирає більше голосів")


# ═══════════════════════════════════════════════════════════════════════════════
# Фігури вставки math-iterations.md
# ═══════════════════════════════════════════════════════════════════════════════

CURVE = ["#2457d6", "#16a34a", "#d98a00", "#c0392b"]   # n = 2, 3, 4, 8


def k_req(w, n, p=0.99):
    """Потрібне число спроб k = log(1−p)/log(1−wⁿ)."""
    return math.log(1 - p) / math.log(1 - w ** n)


# ── ФІГУРА 4: вибух числа спроб за n і w ───────────────────────────────────────
def fig_k_explosion():
    W, H = 860, 470
    X0, X1 = 96, 632          # область побудови по x
    Y0, Y1 = 66, 384          # по y (Y0 — верх)
    WMIN, WMAX = 0.2, 0.9
    DEC = 7                    # декад по y: 10⁰ … 10⁷
    p = []

    def px(w):
        return X0 + (w - WMIN) / (WMAX - WMIN) * (X1 - X0)

    def py(k):
        return Y1 - min(math.log10(max(k, 1.0)), DEC) / DEC * (Y1 - Y0)

    # сітка по y (декади) + підписи
    ylab = ["1", "10", "100", "1 тис.", "10 тис.", "100 тис.", "1 млн", "10 млн"]
    for d in range(DEC + 1):
        yy = Y1 - d / DEC * (Y1 - Y0)
        p.append(line(X0, yy, X1, yy, color="#e3e6ea", sw=1))
        p.append(text(X0 - 12, yy + 4, ylab[d], size=10, color=MUTED, anchor="end"))

    # сітка по x + підписи
    for wv in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        xx = px(wv)
        p.append(line(xx, Y0, xx, Y1, color="#eef0f3", sw=1))
        p.append(text(xx, Y1 + 20, "%.1f" % wv, size=10, color=MUTED))

    # осі
    p.append(line(X0, Y0, X0, Y1, color=INK, sw=1.6))
    p.append(line(X0, Y1, X1, Y1, color=INK, sw=1.6))
    p.append(text((X0 + X1) / 2, Y1 + 44, "частка чесних точок w", size=12, color=INK))
    p.append(text(X0 - 62, Y0 - 26, "спроб k", size=12, color=INK, anchor="start"))
    p.append(text(X0 - 62, Y0 - 12, "(на 99% певності)", size=9.5, color=MUTED, anchor="start"))

    # криві для n = 2, 3, 4, 8
    ns = [2, 3, 4, 8]
    for i, n in enumerate(ns):
        pts = []
        wv = WMIN
        while wv <= WMAX + 1e-9:
            pts.append((px(wv), py(k_req(wv, n))))
            wv += 0.005
        d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % q for q in pts[1:])
        p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, CURVE[i]))

    # легенда — праворуч від області побудови, з великим кроком
    LX, LY = X1 + 34, Y0 + 16
    names = ["пряма", "коло, площина", "гомографія", "фунд. матриця"]
    p.append(text(LX, LY - 24, "мінімальна вибірка", size=11, color=INK,
                  anchor="start", bold=True))
    for i, n in enumerate(ns):
        yy = LY + i * 42
        p.append(line(LX, yy, LX + 30, yy, color=CURVE[i], sw=3))
        p.append(text(LX + 38, yy + 4, "n = %d" % n, size=11.5, color=INK,
                      anchor="start", bold=True))
        p.append(text(LX, yy + 20, names[i], size=10, color=MUTED, anchor="start"))

    # зріз при w = 0,5 — пунктир через усю область побудови, два маркери на кривих
    p.append(line(px(0.5), Y0, px(0.5), Y1, color="#9aa4b2", sw=1.4, dash="5,4"))
    p.append(circle(px(0.5), py(17), 5.5, fill="#ffffff", stroke=CURVE[0], sw=2.6))
    p.append(circle(px(0.5), py(1177), 5.5, fill="#ffffff", stroke=CURVE[3], sw=2.6))

    p.append(text((X0 + X1) / 2, H - 14,
                  "зріз по пунктиру w = 0.5 (половина точок — сміття): "
                  "пряма — 17 спроб, фундаментальна матриця — 1177",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "k-explosion.svg"), W, H, *p,
           title="Ціна однієї зайвої точки у вибірці — вертикаль на логарифмічній шкалі")


# ── ФІГУРА 5: середнє оманливе — хвіст геометричного розподілу ─────────────────
def fig_geometric_tail():
    W, H = 860, 440
    X0, X1 = 92, 626
    Y0, Y1 = 92, 344
    KMAX = 20
    q = 0.25
    p = []

    def px(k):
        return X0 + k / KMAX * (X1 - X0)

    def py(v):
        return Y1 - v * (Y1 - Y0)

    # сітка по y
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        yy = py(v)
        p.append(line(X0, yy, X1, yy, color="#e3e6ea", sw=1))
        p.append(text(X0 - 12, yy + 4, "%d%%" % round(v * 100), size=10,
                      color=MUTED, anchor="end"))

    # осі
    p.append(line(X0, Y0 - 10, X0, Y1, color=INK, sw=1.6))
    p.append(line(X0, Y1, X1 + 10, Y1, color=INK, sw=1.6))
    for k in range(0, KMAX + 1, 2):
        p.append(text(px(k), Y1 + 20, str(k), size=10, color=MUTED))
    p.append(text((X0 + X1) / 2, Y1 + 44, "зроблено спроб k", size=12, color=INK))
    p.append(text(X0 - 58, Y0 - 34, "певність", size=12, color=INK, anchor="start"))
    p.append(text(X0 - 58, Y0 - 20, "хоч раз ухопити", size=9.5, color=MUTED, anchor="start"))
    p.append(text(X0 - 58, Y0 - 8, "чисту вибірку", size=9.5, color=MUTED, anchor="start"))

    # крива 1 − (1 − q)^k
    pts = [(px(k / 4.0), py(1 - (1 - q) ** (k / 4.0))) for k in range(0, KMAX * 4 + 1)]
    d = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % t for t in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, NEG))

    # три віхи на кривій: медіана 3, середнє 4, 99% на 17 — самі маркери в полі
    marks = [
        (3,  1 - 0.75 ** 3,  FIELD),
        (4,  1 - 0.75 ** 4,  "#d98a00"),
        (17, 1 - 0.75 ** 17, POS),
    ]
    for k, v, col in marks:
        xx, yy = px(k), py(v)
        p.append(line(xx, yy + 6, xx, Y1, color=col, sw=1.3, dash="4,3"))
        p.append(circle(xx, yy, 5.5, fill="#ffffff", stroke=col, sw=2.4))

    # ── підписи — окремим стовпчиком ПОЗА сіткою, щоб лінії не різали написи ──
    AX = X1 + 26
    notes = [
        ("медіана: 3 спроби\nвже 58% — але це\nкидок монети", FIELD, "#eaf7ee"),
        ("середнє E(k) = 4\nспроби — а певності\nлише 68%", "#d98a00", "#fff6e6"),
        ("99% певності —\nаж на 17-й спробі:\nучетверо за середнє", POS, "#fdecea"),
    ]
    for i, (lab, col, bg) in enumerate(notes):
        yy = Y0 + i * 86
        p.append(fitbox(AX, yy, 190, 62, lab, size=10,
                        fill=bg, stroke=col, sw=1.3, color=INK))

    p.append(text((X0 + X1) / 2, H - 14,
                  "w = 0.5 · n = 2 · шанс чистої вибірки wⁿ = 0.25",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "geometric-tail.svg"), W, H, *p,
           title="Чому середнього замало: 4 спроби дають 68%, а 99% коштують 17")


# ── ФІГУРА 6: адаптивне k — перегони бюджету, що тане, і лічильника, що росте ──
def fig_adaptive_k():
    W, H = 860, 450
    X0, X1 = 96, 640
    Y0, Y1 = 74, 356
    KMAX = 15
    DEC = 4                     # 10⁰ … 10⁴
    p = []

    def px(t):
        return X0 + t / KMAX * (X1 - X0)

    def py(v):
        return Y1 - min(math.log10(max(v, 1.0)), DEC) / DEC * (Y1 - Y0)

    # сітка
    ylab = ["1", "10", "100", "1 тис.", "10 тис."]
    for d in range(DEC + 1):
        yy = Y1 - d / DEC * (Y1 - Y0)
        p.append(line(X0, yy, X1, yy, color="#e3e6ea", sw=1))
        p.append(text(X0 - 12, yy + 4, ylab[d], size=10, color=MUTED, anchor="end"))
    p.append(line(X0, Y0 - 8, X0, Y1, color=INK, sw=1.6))
    p.append(line(X0, Y1, X1 + 8, Y1, color=INK, sw=1.6))
    for t in range(0, KMAX + 1, 1):
        p.append(text(px(t), Y1 + 20, str(t), size=10, color=MUTED))
    p.append(text((X0 + X1) / 2, Y1 + 44, "зроблено спроб", size=12, color=INK))
    p.append(text(X0 - 64, Y0 - 30, "спроб", size=12, color=INK, anchor="start"))
    p.append(text(X0 - 64, Y0 - 16, "(лог. шкала)", size=9.5, color=MUTED, anchor="start"))

    # бюджет k, що тане: сходинки за найкращою згодою (N = 100, n = 2, p = 0.99)
    steps = [(0, 2876), (1, 2876), (5, 49), (9, 13), (13, 13)]
    path = []
    for i in range(len(steps) - 1):
        t0, v0 = steps[i]
        t1, v1 = steps[i + 1]
        path.append((px(t0), py(v0)))
        path.append((px(t1), py(v0)))
        path.append((px(t1), py(v1)))
    d = "M %.1f %.1f " % path[0] + " ".join("L %.1f %.1f" % t for t in path[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d, POS))

    # лічильник спроб, що росте: пряма y = x
    pts = [(px(t), py(max(t, 1))) for t in range(1, 14)]
    d2 = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % t for t in pts[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (d2, NEG))

    # точка зустрічі
    mx, my = px(13), py(13)
    p.append(circle(mx, my, 7, fill="#ffffff", stroke=FIELD, sw=3))
    p.append(line(mx, my - 10, mx, Y0 + 6, color=FIELD, sw=1.3, dash="4,3"))
    p.append(fitbox(mx - 92, Y0 - 34, 184, 34,
                    "лічильник наздогнав бюджет\n→ СТОП на 13-й спробі", size=10,
                    fill="#eaf7ee", stroke=FIELD, sw=1.4, color=INK))

    # підписи згод, що зростають (рознесені по вертикалі, щоб не чіпати криву)
    notes = [
        (1, 2876, "згода 4/100 → ŵ = 0.04\nбюджет 2876", 22),
        (5, 49,   "згода 30/100 → ŵ = 0.30\nбюджет 49", -46),
        (9, 13,   "згода 55/100 → ŵ = 0.55\nбюджет 13", -46),
    ]
    for t, v, lab, dy in notes:
        xx, yy = px(t), py(v)
        p.append(circle(xx, yy, 4.5, fill=POS, stroke="#ffffff", sw=1.4))
        p.append(fitbox(xx + 14, yy + dy, 164, 34, lab, size=9.5,
                        fill="#fdecea", stroke=POS, sw=1.2, color=INK))

    # легенда — під областю побудови, двома далеко рознесеними стовпчиками
    p.append(line(X0 + 8, H - 30, X0 + 40, H - 30, color=POS, sw=3))
    p.append(text(X0 + 48, H - 26, "потрібно спроб k — перераховують за ŵ = згода/N",
                  size=10, color=INK, anchor="start"))
    p.append(line(X0 + 8, H - 12, X0 + 40, H - 12, color=NEG, sw=3))
    p.append(text(X0 + 48, H - 8, "зроблено спроб — росте на одиницю за крок",
                  size=10, color=INK, anchor="start"))

    # праворуч — пояснення, чому це працює
    p.append(fitbox(X1 + 26, Y0 + 40, 184, 96,
                    "w наперед невідоме,\nтож беремо ŵ = згода/N\nз найкращої моделі досі.\n"
                    "Згода лише росте →\nбюджет лише тане.", size=10,
                    fill="#f4f6f8", stroke=MUTED, sw=1.2, color=INK))

    render(os.path.join(OUT, "adaptive-k.svg"), W, H, *p,
           title="Адаптивне k: бюджет тане назустріч лічильнику — зустрілись, спиняємось")


# ── ФІГУРА 7: звідки беруться 1,96σ і 2.45σ ───────────────────────────────────
def fig_threshold_sigma():
    W, H = 860, 410
    p = []
    pw, ph = 372, 254
    ys = 62
    xs = [40, W - 40 - pw]

    def axis(x, lo, hi, mid_lab):
        """Вісь у пікселях для панелі, що починається на x."""
        ax0, ax1 = x + 40, x + pw - 30
        base = ys + ph - 78          # лишаємо місце під два підписи ВСЕРЕДИНІ панелі
        return ax0, ax1, base, (lambda v: ax0 + (v - lo) / (hi - lo) * (ax1 - ax0))

    # ── ліва панель: відхилення точки від прямої, codim 1 → гаусів дзвін ──
    p.append(_panel(xs[0], ys, pw, ph, "Відстань до прямої: одна вісь (codim 1)", NEG))
    ax0, ax1, base, X = axis(xs[0], -3.6, 3.6, "0")
    top = ys + 52
    HGT = base - top

    def gauss(v):
        return math.exp(-v * v / 2)

    # заливка ±1.96σ
    fill_pts = [(X(-1.96), base)]
    v = -1.96
    while v <= 1.96:
        fill_pts.append((X(v), base - gauss(v) * HGT))
        v += 0.04
    fill_pts.append((X(1.96), base))
    d = "M %.1f %.1f " % fill_pts[0] + " ".join("L %.1f %.1f" % t for t in fill_pts[1:]) + " Z"
    p.append('<path d="%s" fill="#dbe4fb" stroke="none"/>' % d)

    # сама крива
    cur = []
    v = -3.6
    while v <= 3.6:
        cur.append((X(v), base - gauss(v) * HGT))
        v += 0.04
    d = "M %.1f %.1f " % cur[0] + " ".join("L %.1f %.1f" % t for t in cur[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, NEG))
    p.append(line(ax0, base, ax1, base, color=INK, sw=1.5))

    for v, lab in ((-1.96, "−1.96σ"), (1.96, "+1.96σ")):
        p.append(line(X(v), base, X(v), base - gauss(v) * HGT - 6, color=POS, sw=1.6, dash="4,3"))
        p.append(text(X(v), base + 18, lab, size=10, color=POS, bold=True))
    p.append(text(X(0), base - HGT * 0.42, "95%", size=15, color=NEG, bold=True))
    p.append(text(xs[0] + pw / 2, base + 42, "поріг t = 1.96σ", size=12, color=INK, bold=True))
    p.append(text(xs[0] + pw / 2, base + 60, "t² = 3.84σ²", size=10.5, color=MUTED))

    # ── права панель: відстань між двома точками, codim 2 → релей ──
    p.append(_panel(xs[1], ys, pw, ph, "Відстань між точками: дві осі (codim 2)", FIELD))
    ax0, ax1, base, X = axis(xs[1], 0, 4.6, "0")
    top = ys + 52
    HGT = base - top

    def rayl(v):
        return v * math.exp(-v * v / 2) / 0.6065      # нормуємо до піка = 1

    fill_pts = [(X(0), base)]
    v = 0.0
    while v <= 2.4477:
        fill_pts.append((X(v), base - rayl(v) * HGT))
        v += 0.03
    fill_pts.append((X(2.4477), base))
    d = "M %.1f %.1f " % fill_pts[0] + " ".join("L %.1f %.1f" % t for t in fill_pts[1:]) + " Z"
    p.append('<path d="%s" fill="#d8f0e0" stroke="none"/>' % d)

    cur = []
    v = 0.0
    while v <= 4.6:
        cur.append((X(v), base - rayl(v) * HGT))
        v += 0.03
    d = "M %.1f %.1f " % cur[0] + " ".join("L %.1f %.1f" % t for t in cur[1:])
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (d, FIELD))
    p.append(line(ax0, base, ax1, base, color=INK, sw=1.5))

    p.append(line(X(2.4477), base, X(2.4477), base - rayl(2.4477) * HGT - 30,
                  color=POS, sw=1.6, dash="4,3"))
    p.append(text(X(2.4477), base + 18, "2.45σ", size=10, color=POS, bold=True))
    p.append(text(X(0.95), base - HGT * 0.40, "95%", size=15, color=FIELD, bold=True))
    p.append(text(xs[1] + pw / 2, base + 42, "поріг t = 2.45σ", size=12, color=INK, bold=True))
    p.append(text(xs[1] + pw / 2, base + 60, "t² = 5.99σ²", size=10.5, color=MUTED))

    p.append(text(W / 2, H - 14,
                  "поріг — це квантиль 95% розподілу відстані чесної точки; "
                  "скільки осей у відстані, стільки й ступенів вільності",
                  size=10.5, color=MUTED))

    render(os.path.join(OUT, "threshold-sigma.svg"), W, H, *p,
           title="Поріг t не вгадують — його читають зі шуму чесних точок")


# ══════════════════════════════════════════════════════════════════════════════
#  ФІГУРИ ДО ВСТАВКИ proj-ransac-linefit.md
#  Дані ТІ САМІ, що в прогоні вставки: 9 чесних уздовж y = 0.5x + 1, 3 викиди.
# ══════════════════════════════════════════════════════════════════════════════

D_HONEST = [(0.0, 1.05), (1.0, 1.42), (2.0, 2.10), (3.0, 2.42), (4.0, 3.08),
            (5.0, 3.44), (6.0, 4.13), (7.0, 4.39), (8.0, 5.06)]
D_OUTL = [(2.0, 5.60), (5.0, 0.40), (7.0, 1.20)]
D_T = 0.25
PXU = 30.0                  # пікселів на одиницю даних — ОДНАКОВО по обох осях,
                            # інакше перпендикулярні відстані брехали б на око
GREY = "#9aa4b2"


def _mk(px, py):
    """Перетворювачі даних (x праворуч, y вгору) у піксели панелі."""
    def fx(x):
        return px + 34 + (x + 0.6) * PXU

    def fy(y):
        return py + 48 + (5.9 - y) * PXU
    return fx, fy


def _band(fx, fy, abc, t, col, xr=(-0.6, 8.6)):
    """Центральна пряма + дві межі смуги ±t (зсув уздовж нормалі = зсув c)."""
    a, b, c = abc
    out = ""
    if abs(b) < 1e-9:
        return out
    for cc, sw, dash in ((c, 2.6, None), (c - t, 1.2, "5,4"), (c + t, 1.2, "5,4")):
        yA = -(a * xr[0] + cc) / b
        yB = -(a * xr[1] + cc) / b
        out += line(fx(xr[0]), fy(yA), fx(xr[1]), fy(yB), color=col, sw=sw, dash=dash)
    return out


def _cross(cx, cy, col):
    return (circle(cx, cy, 6.0, fill="none", stroke=col, sw=1.8)
            + line(cx - 3.6, cy - 3.6, cx + 3.6, cy + 3.6, color=col, sw=1.8)
            + line(cx - 3.6, cy + 3.6, cx + 3.6, cy - 3.6, color=col, sw=1.8))


# ── ФІГУРА: обидві точки вибірки чесні — а коротка база все одно губить згоду ───
def fig_sample_baseline():
    W, H = 820, 400
    pw, ph = 344, 300
    ys = 64
    p = []

    def panel(x, i, j, head, hcol, note):
        fx, fy = _mk(x, ys)
        p.append(_panel(x, ys, pw, ph, head, hcol))
        abc = line_through(D_HONEST[i], D_HONEST[j])
        p.append(_band(fx, fy, abc, D_T, hcol))
        cnt = 0
        for pt in D_HONEST:
            inb = dist(abc, pt) <= D_T
            cnt += inb
            ring = pt in (D_HONEST[i], D_HONEST[j])
            p.append(_dot(fx(pt[0]), fy(pt[1]), INLIER if inb else GREY, r=5, ring=ring))
        for pt in D_OUTL:
            p.append(_cross(fx(pt[0]), fy(pt[1]), OUTL))
        base = math.dist(D_HONEST[i], D_HONEST[j])
        p.append(text(x + pw / 2, ys + ph - 64, note, size=10, color=MUTED))
        p.append(text(x + pw / 2, ys + ph - 42, "база вибірки: %.2f" % base,
                      size=11, color=INK))
        p.append(text(x + pw / 2, ys + ph - 16,
                      "згода: %d %s із 9" % (cnt, points_word(cnt)),
                      size=14, color=hcol, bold=True))

    panel(40, 8, 6, "Коротка база", "#d98a00",
          "пряму хитнуло на 1.6° — і далекі чесні точки випали")
    panel(W - 40 - pw, 8, 1, "Довга база", INLIER,
          "той самий шум, але важіль довгий — пряма лягла")

    p.append(text(W / 2, 50, "обидві вибірки — З ДВОХ ЧЕСНИХ ТОЧОК; різниця лише в базі",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "sample-baseline.svg"), W, H, *p,
           title="Чиста вибірка ще не означає добру модель: усе вирішує база")


# ── ФІГУРА: пастка y = k·x + b — поріг по вертикалі душить круті прямі ──────────
def fig_vertical_vs_perp():
    W, H = 820, 398
    pw, ph = 344, 290
    ys = 64
    p = []
    # ті самі перпендикулярні відхилення, що й у чесних точок прогону
    DEV = [+0.045, -0.072, +0.089, -0.072, +0.072, -0.054, +0.116, -0.098, +0.054]

    def wedge(cx, cy, ux, uy, nx, ny, half, hw, fill):
        """Смуга завширшки ±hw уздовж напрямку (ux,uy) — заливка чотирикутником."""
        pts = [(cx - ux * half + nx * hw * s, cy - uy * half + ny * hw * s)
               for s in (-1, 1)]
        pts += [(cx + ux * half + nx * hw * s, cy + uy * half + ny * hw * s)
                for s in (1, -1)]
        d = "M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f Z" % (
            pts[0][0], pts[0][1], pts[1][0], pts[1][1],
            pts[2][0], pts[2][1], pts[3][0], pts[3][1])
        return '<path d="%s" fill="%s" stroke="none"/>' % (d, fill)

    def panel(x, k, head, hcol):
        p.append(_panel(x, ys, pw, ph, head, hcol))
        cx, cy = x + pw / 2, ys + 128
        th = math.atan(k)
        ux, uy = math.cos(th), -math.sin(th)        # уздовж прямої (y вгору)
        nx, ny = math.sin(th), math.cos(th)         # нормаль до неї
        half = min(122.0, 76.0 / max(abs(uy), 0.02))   # не даємо вилізти по вертикалі
        tp = D_T * PXU                                  # чесна ±t по перпендикуляру
        tv = D_T * PXU * math.cos(th)                   # те, що лишає поріг «по y»
        p.append(wedge(cx, cy, ux, uy, nx, ny, half, tp, "#eaf7ee"))
        p.append(wedge(cx, cy, ux, uy, nx, ny, half, tv, "#f7dcd8"))
        for s in (-1, 1):
            p.append(line(cx - ux * half + nx * tp * s, cy - uy * half + ny * tp * s,
                          cx + ux * half + nx * tp * s, cy + uy * half + ny * tp * s,
                          color=INLIER, sw=1.3, dash="6,4"))
            p.append(line(cx - ux * half + nx * tv * s, cy - uy * half + ny * tv * s,
                          cx + ux * half + nx * tv * s, cy + uy * half + ny * tv * s,
                          color=OUTL, sw=1.3))
        p.append(line(cx - ux * half, cy - uy * half,
                      cx + ux * half, cy + uy * half, color=hcol, sw=1.4))
        cnt = 0
        for i, d in enumerate(DEV):
            t_along = (i - 4) * (half * 2 / 11.0)
            ok = abs(d) <= D_T * math.cos(th)       # чи проходить ВЕРТИКАЛЬНИЙ поріг
            cnt += ok
            p.append(_dot(cx + ux * t_along + nx * d * PXU,
                          cy + uy * t_along + ny * d * PXU,
                          INLIER if ok else GREY, r=4.4))
        p.append(text(x + pw / 2, ys + ph - 62,
                      "нахил k = %.1f  →  t/√(1+k²) = %.3f" % (k, D_T / math.hypot(1, k)),
                      size=10.5, color=MUTED))
        p.append(text(x + pw / 2, ys + ph - 40,
                      "той самий поріг t = 0.25, той самий шум", size=10, color=MUTED))
        p.append(text(x + pw / 2, ys + ph - 16, "пройшло: %d із 9" % cnt,
                      size=14, color=hcol, bold=True))

    panel(40, 0.5, "Полога пряма", INLIER)
    panel(W - 40 - pw, 5.0, "Крута пряма", OUTL)

    p.append(text(W / 2, 50, "поріг на |y − k·x − b| міряє відстань ПО ВЕРТИКАЛІ —"
                             " і тим більше душить смугу, чим крутіша пряма",
                  size=11.5, color=MUTED))
    p.append(line(78, 378, 114, 378, color=INLIER, sw=1.3, dash="6,4"))
    p.append(text(122, 382, "— чесна смуга ±t по перпендикуляру", size=9.5,
                  color=INK, anchor="start"))
    p.append(line(452, 378, 488, 378, color=OUTL, sw=1.3))
    p.append(text(496, 382, "— що з неї лишає поріг по вертикалі", size=9.5,
                  color=INK, anchor="start"))
    render(os.path.join(OUT, "vertical-vs-perp.svg"), W, H, *p,
           title="Чому пряму беруть як a·x + b·y + c = 0, а не як y = k·x + b")


# ═══ ФІГУРИ ДО ВСТАВКИ hist-ransac.md ══════════════════════════════════════════

# Сім точок із Figure 1 статті Фішлера й Боллса (CACM 24(6), 1981, с. 382).
# Шість чесних лежать уздовж прямої; точка 7 — груба похибка далеко по x.
F1_PTS = {1: (0.0, 0.0), 2: (1.0, 1.0), 3: (2.0, 2.0), 4: (3.0, 2.0),
          5: (3.0, 3.0), 6: (4.0, 4.0), 7: (10.0, 2.0)}
F1_TOL = 0.8          # допуск, заданий в умові задачі статті
F1_GROSS = 7          # номер грубої похибки
F1_VALID = [1, 2, 3, 4, 5, 6]

DEAD = "#9aa1ac"      # точка, яку евристика вже викинула


def _f1_ls(ids):
    """Пряма y = b + k·x найменшими квадратами по підмножині точок Figure 1."""
    return fit_line([F1_PTS[i] for i in ids])


def _f1_prune():
    """Евристика «викинь найдальшого» крок за кроком.
    Повертає список кроків (набір_живих, k, b, кого_викинуто|None)."""
    alive = sorted(F1_PTS)
    steps = []
    while True:
        k, b = _f1_ls(alive)
        res = {i: F1_PTS[i][1] - (b + k * F1_PTS[i][0]) for i in alive}
        worst = max(alive, key=lambda i: abs(res[i]))
        if abs(res[worst]) <= F1_TOL:
            steps.append((list(alive), k, b, None))
            return steps
        steps.append((list(alive), k, b, worst))
        alive = [i for i in alive if i != worst]


# ── ФІГУРА: сім точок 1981 року — латка виїдає чесних, а похибку лишає ─────────
def fig_hist_pruning_fails():
    W, H = 930, 430
    p = []

    # ── ліва панель: власне графік Figure 1 ──
    px, py, pw, ph = 36, 58, 390, 330
    p.append(_panel(px, py, pw, ph, "Сім точок із задачі 1981 року", INK))

    ox, oy = 78.0, 298.0        # екранні координати точки (0, 0)
    sx, sy = 30.0, 44.0         # px на одиницю даних

    def X(dx):
        return ox + dx * sx

    def Y(dy):
        return oy - dy * sy

    # осі з підписами поділок (написи — ПОЗА лініями осей)
    p.append(line(ox, Y(4.6), ox, oy, color=MUTED, sw=1.2))
    p.append(line(ox, oy, X(10.6), oy, color=MUTED, sw=1.2))
    for dx in (0, 2, 4, 6, 8, 10):
        p.append(text(X(dx), oy + 16, str(dx), size=10, color=MUTED))
    for dy in (1, 2, 3, 4):
        p.append(text(ox - 10, Y(dy) + 4, str(dy), size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 10, oy + 4, "0", size=10, color=MUTED, anchor="end"))

    # ідеальна пряма по шести чесних точках (обрізана по верху поля)
    ki, bi = _f1_ls(F1_VALID)
    xi_top = (4.4 - bi) / ki
    p.append(line(X(0), Y(bi), X(xi_top), Y(4.4), color=INLIER, sw=2.6))

    # пряма, якою скінчила евристика «викинь найдальшого»
    steps = _f1_prune()
    kf, bf = steps[-1][1], steps[-1][2]
    p.append(line(X(0), Y(bf), X(10.6), Y(bf + kf * 10.6), color=OUTL, sw=2.4, dash="7,5"))

    # точки: чесні — зелені; груба похибка — червоне коло з ×
    lab = {1: (-14, -8), 2: (0, -15), 3: (0, -15), 4: (0, -15),
           5: (0, -15), 6: (0, -15), 7: (0, -16)}
    for i, (dx, dy) in F1_PTS.items():
        cx, cy = X(dx), Y(dy)
        if i == F1_GROSS:
            p.append(circle(cx, cy, 7, fill="none", stroke=OUTL, sw=2.4))
            p.append(line(cx - 4.4, cy - 4.4, cx + 4.4, cy + 4.4, color=OUTL, sw=2.4))
            p.append(line(cx - 4.4, cy + 4.4, cx + 4.4, cy - 4.4, color=OUTL, sw=2.4))
        else:
            p.append(_dot(cx, cy, INLIER, r=5.5))
        lx, ly = lab[i]
        p.append(text(cx + lx, cy + ly, str(i), size=11,
                      color=OUTL if i == F1_GROSS else INK, bold=True))
    p.append(text(X(10.0), Y(2.0) - 34, "груба похибка", size=10, color=OUTL, bold=True))

    # легенда — свічки-відрізки ліворуч, написи праворуч, без перетинів
    p.append(line(px + 18, 348, px + 54, 348, color=INLIER, sw=2.6))
    p.append(text(px + 62, 352, "— пряма по шести чесних точках", size=10,
                  color=INK, anchor="start"))
    p.append(line(px + 18, 370, px + 54, 370, color=OUTL, sw=2.4, dash="7,5"))
    p.append(text(px + 62, 374, "— чим скінчила латка «викинь найдальшого»", size=10,
                  color=INK, anchor="start"))

    # ── права панель: драбина відсіву ──
    qx, qy, qw, qh = 446, 58, 452, 330
    p.append(_panel(qx, qy, qw, qh, "Латка крок за кроком: кого вона викидає", OUTL))

    d0, dstep = 492.0, 26.0
    rows_y = [146, 190, 234, 278]
    for i in range(7):
        p.append(text(d0 + i * dstep, 120, str(i + 1), size=10, color=MUTED, bold=True))

    for r, (alive, k, b, worst) in enumerate(steps[:4]):
        ry = rows_y[r]
        p.append(text(qx + 26, ry + 4, str(r + 1), size=11, color=MUTED, bold=True))
        for i in range(1, 8):
            cx = d0 + (i - 1) * dstep
            if i not in alive:
                p.append(circle(cx, ry, 5.5, fill="none", stroke=DEAD, sw=1.6))
            elif i == F1_GROSS:
                p.append(_dot(cx, ry, OUTL, r=6))
            else:
                p.append(_dot(cx, ry, INLIER, r=6))
        if worst is None:
            note, col = "усі в межах 0.8 → стоп", INK
        else:
            note, col = "найдалі — точка %d (чесна) → геть" % worst, OUTL
        p.append(text(d0 + 6 * dstep + 22, ry + 4, note, size=10, color=col,
                      anchor="start", bold=(worst is None)))

    p.append(fitbox(qx + 22, 314, qw - 44, 52,
                    "Лишилися точки 2, 3, 4, 7 — а 7 і є груба похибка.\n"
                    "Три викинуті (6, 5, 1) були чесні. Латка з'їла здорових.",
                    size=11, fill="#fdecea", stroke=OUTL, sw=1.4, color=INK))

    render(os.path.join(OUT, "hist-pruning-fails.svg"), W, H, *p,
           title="Чому Фішлер і Боллс не полагодили стару латку, а викинули її")


# ── ФІГУРА: ланцюг першостей — кого забули на кожній ланці ─────────────────────
def fig_hist_attribution_chain():
    W, H = 900, 596
    p = []
    spine = 132.0
    rows = [
        ("≈1615 · 1617", ["Віллеброрд Снелліус розв'язує зворотну засічку",
                          "й друкує її в «Eratosthenes Batavus»"], None),
        ("1692", ["Лоран Потено переказує той самий розв'язок —",
                  "і задача назавжди дістає ЙОГО ім'я"], OUTL),
        ("1805 · 1809", ["Лежандр друкує найменші квадрати; Гаусс заявляє,",
                         "що мав їх від 1795 — суперечка про першість"], None),
        ("1841", ["Йоганн Ґрунерт зводить P3P до рівняння 4-го степеня",
                  "(≤ 4 розв'язки) — у статті «Потенотова задача»"], FIELD),
        ("1945", ["Ерл Черч дає ітеративний метод — саме він стає каноном",
                  "американської фотограмметрії"], None),
        ("1978", ["SRI Road Expert: знімок проти бази даних —",
                  "і перші грубі похибки просто від корелятора"], None),
        ("1981", ["Фішлер і Боллс: RANSAC. «Чинна фотограмметрична",
                  "література не дає аналітичного розв'язку, крім методу Черча»"], SAMPLE),
        ("1994", ["Гаралік зі співавторами зшивають нитку назад:",
                  "перший розв'язок P3P — Ґрунертів, 1841"], FIELD),
        ("2006", ["CVPR: воркшоп «25 років RANSAC» —", "у методу день народження"], None),
    ]
    y0, step = 84, 52
    p.append(line(spine, y0 - 16, spine, y0 + (len(rows) - 1) * step + 16,
                  color=MUTED, sw=1.6))
    for i, (year, lines, col) in enumerate(rows):
        ry = y0 + i * step
        p.append(text(spine - 20, ry + 4, year, size=11, color=INK,
                      anchor="end", bold=True))
        p.append(circle(spine, ry, 6.5, fill=col or "#ffffff",
                        stroke=col or MUTED, sw=2.2))
        p.append(mtext(spine + 26, ry - 4, lines, size=11, color=INK, anchor="start"))
    p.append(fitbox(40, y0 + (len(rows) - 1) * step + 34, W - 80, 44,
                    "Забуття тут — не збіг, а норма: результат живий, поки його несе якийсь"
                    " живий канон,\nа канони обмежені мовою, фахом і десятиліттям.",
                    size=11, fill="#f2f6ff", stroke=NEG, sw=1.4, color=INK))
    render(os.path.join(OUT, "hist-attribution-chain.svg"), W, H, *p,
           title="Ланцюг першостей навколо RANSAC: на кожній ланці когось забули")


if __name__ == "__main__":
    fig_ls_vs_ransac()
    fig_ransac_loop()
    fig_good_vs_bad_trial()
    fig_k_explosion()
    fig_geometric_tail()
    fig_adaptive_k()
    fig_threshold_sigma()
    fig_sample_baseline()
    fig_vertical_vs_perp()
    fig_hist_pruning_fails()
    fig_hist_attribution_chain()
    print("OK: figures written to", OUT)
