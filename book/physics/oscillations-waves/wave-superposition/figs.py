# -*- coding: utf-8 -*-
"""Фігури до теми «Суперпозиція хвиль».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

W1 = "#c0392b"   # хвиля 1 — гаряче червоне
W2 = "#2457d6"   # хвиля 2 — холодне синє
SUM = "#1a1a1a"  # сума — чорне, товсте
ENV = "#c0392b"  # обвідна — червоне пунктиром
GRID = "#e6e9ee"


def poly(pts, color=INK, sw=2.0, dash=None, fill="none"):
    d = "M " + " L ".join("%.1f %.1f" % (x, y) for x, y in pts)
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>' % (d, fill, color, sw, da)


def sine_pts(xa, xb, yb, amp, cycles, phase=0.0, n=240, sign=-1):
    """Синусоїда над базовою лінією yb: y = yb + sign*amp*sin(2π·cycles·u + phase)."""
    pts = []
    for i in range(n + 1):
        u = i / n
        x = xa + u * (xb - xa)
        y = yb + sign * amp * math.sin(2 * math.pi * cycles * u + phase)
        pts.append((x, y))
    return pts


# ── Фігура 1: два імпульси проходять крізь себе — ядро суперпозиції ───────────
def fig_pulses_pass():
    W, H = 1000, 600
    f = [text(W / 2, 30, "Суперпозиція: хвилі складаються — і проходять крізь себе незмінними", size=16, bold=True)]
    xa, xb = 150, 900
    sig = 36
    hA, hB = 48, 34

    def bump(x, c, h):
        return h * math.exp(-((x - c) / sig) ** 2)

    def rope(yb, cA, cB):
        return [(x, yb - bump(x, cA, hA) - bump(x, cB, hB)) for x in range(int(xa), int(xb) + 1, 3)]

    def half(yb, c, h):
        return [(x, yb - bump(x, c, h)) for x in range(int(xa), int(xb) + 1, 3)]

    rows = [
        (170, 300, 700, "1 · до зустрічі", "дві окремі опуклості біжать назустріч"),
        (335, 500, 500, "2 · мить накладання", "збігаються — висоти додаються"),
        (500, 700, 300, "3 · після зустрічі", "розійшлися, кожна тієї самої висоти"),
    ]
    for yb, cA, cB, name, note in rows:
        f.append(line(xa, yb, xb, yb, color=GRID, sw=1.4))
        if cA == cB:  # рядок накладання — показати складові пунктиром
            f.append(poly(half(yb, cA, hA), color=W1, sw=1.6, dash="5,5"))
            f.append(poly(half(yb, cB, hB), color=W2, sw=1.6, dash="5,5"))
        f.append(poly(rope(yb, cA, cB), color=SUM, sw=3.0))
        f.append(text(28, yb - 6, name, size=13.5, bold=True, anchor="start"))
        f.append(text(W / 2, yb + 66, note, size=12.5, color=MUTED))
        # стрілки напряму й теги над опуклостями
        f.append(arrow(cA - 24, yb - hA - 16, cA + 24, yb - hA - 16, color=W1, sw=2.2))
        f.append(arrow(cB + 24, yb - hB - 16, cB - 24, yb - hB - 16, color=W2, sw=2.2))
        if name.startswith("1"):
            f.append(text(cA, yb - hA - 26, "хвиля A", size=12, color=W1))
            f.append(text(cB, yb - hB - 26, "хвиля B", size=12, color=W2))
        if cA == cB:
            f.append(text(cA + 150, yb - 60, "48 + 34 = 82", size=13, bold=True, color=SUM, anchor="start"))
            f.append(line(cA + 46, yb - hA - hB, cA + 145, yb - 62, color=MUTED, sw=1.2))
    render(os.path.join(IMG, "pulses-pass.svg"), W, H, *f)


# ── Фігура 2: складання залежить від фази — підсилення й гасіння ──────────────
def fig_interference():
    W, H = 1000, 480
    f = [text(W / 2, 30, "Однакова частота: результат вирішує різниця фаз", size=16, bold=True)]
    f.append(line(W / 2, 58, W / 2, 372, color=GRID, sw=1.4))
    pw = 380
    yc1, yc2, ysum = 120, 190, 300
    amp = 24
    cyc = 2.0

    def panel(ox, sub, ph2, sub_col):
        fr = [text(ox + pw / 2, 62, sub, size=14, bold=True, color=sub_col)]
        # базові лінії
        for yy, lab, col in [(yc1, "хвиля 1", W1), (yc2, "хвиля 2", W2), (ysum, "сума", SUM)]:
            fr.append(line(ox, yy, ox + pw, yy, color=GRID, sw=1.2))
            fr.append(text(ox - 8, yy - 30, lab, size=11.5, color=col, anchor="start"))
        fr.append(poly(sine_pts(ox, ox + pw, yc1, amp, cyc, 0.0), color=W1, sw=2.4))
        fr.append(poly(sine_pts(ox, ox + pw, yc2, amp, cyc, ph2), color=W2, sw=2.4))
        # сума
        summ = []
        for i in range(241):
            u = i / 240.0
            x = ox + u * pw
            y = ysum - amp * (math.sin(2 * math.pi * cyc * u) + math.sin(2 * math.pi * cyc * u + ph2))
            summ.append((x, y))
        fr.append(poly(summ, color=SUM, sw=3.2))
        return fr

    f += panel(70, "у фазі  (Δφ = 0)", 0.0, W1)
    f.append(text(70 + pw / 2, 356, "гребінь на гребінь → амплітуда 2A (підсилення)", size=12.5, color=INK))
    f += panel(540, "у протифазі  (Δφ = 180°)", math.pi, NEG)
    f.append(text(540 + pw / 2, 356, "гребінь на западину → рівно нуль (гасіння)", size=12.5, color=INK))

    box, bw, bh = textbox(W / 2, 438,
                          "амплітуда суми:   A = √( A₁² + A₂² + 2·A₁·A₂·cos Δφ )",
                          size=14.5, pad=12, fill="#f4f6f8", stroke=INK, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "interference.svg"), W, H, *f)


# ── Фігура 3: дві зустрічні хвилі дають стоячу ───────────────────────────────
def fig_standing_wave():
    W, H = 1000, 560
    f = [text(W / 2, 30, "Дві однакові хвилі назустріч дають стоячу хвилю", size=16, bold=True)]
    xa, xb = 130, 880

    # верх — дві біжучі хвилі
    f.append(line(xa, 110, xb, 110, color=GRID, sw=1.2))
    f.append(poly(sine_pts(xa, xb, 110, 22, 3.0, 0.0), color=W1, sw=2.4))
    f.append(arrow(xb + 10, 110, xb + 46, 110, color=W1, sw=2.4))
    f.append(text(xa - 8, 84, "біжить праворуч →", size=12, color=W1, anchor="start"))

    f.append(line(xa, 175, xb, 175, color=GRID, sw=1.2))
    f.append(poly(sine_pts(xa, xb, 175, 22, 3.0, 0.0), color=W2, sw=2.4))
    f.append(arrow(xa - 10, 175, xa - 46, 175, color=W2, sw=2.4))
    f.append(text(xa - 8, 208, "← біжить ліворуч", size=12, color=W2, anchor="start"))

    f.append(text(W / 2, 250, "сума в кожній точці:", size=13, bold=True))

    # низ — стояча хвиля
    yc = 400
    amp = 74
    n = 300
    # знімки різних миттєвостей (сірі), спільні вузли
    for fac in (1.0, 0.7, 0.4, -0.4, -0.7, -1.0):
        pts = [(xa + i / n * (xb - xa),
                yc - fac * amp * math.sin(2 * math.pi * 1.5 * (i / n))) for i in range(n + 1)]
        f.append(poly(pts, color="#b9c0ca", sw=1.4))
    # обвідна ±
    envp = [(xa + i / n * (xb - xa), yc - amp * abs(math.sin(2 * math.pi * 1.5 * (i / n)))) for i in range(n + 1)]
    envm = [(xa + i / n * (xb - xa), yc + amp * abs(math.sin(2 * math.pi * 1.5 * (i / n)))) for i in range(n + 1)]
    f.append(poly(envp, color=ENV, sw=1.8, dash="6,5"))
    f.append(poly(envm, color=ENV, sw=1.8, dash="6,5"))
    f.append(line(xa, yc, xb, yc, color=GRID, sw=1.2))

    # вузли (нулі sin) і пучності
    span = xb - xa
    for k in range(4):
        xn = xa + k / 3.0 * span
        f.append(circle(xn, yc, 5.5, fill=SUM, stroke=SUM, sw=1))
    f.append(text(xa, yc + 40, "вузол", size=12.5, bold=True, color=SUM, anchor="start"))
    f.append(line(xa + 18, yc + 30, xa + 4, yc + 8, color=MUTED, sw=1.2))
    xanti = xa + 0.5 / 3.0 * span
    f.append(text(xanti, yc - amp - 12, "пучність", size=12.5, bold=True, color=ENV))

    f.append(text(W / 2, 520, "вузли стоять нерухомо, пучності гойдаються між пунктирними обвідними — візерунок не біжить",
                  size=12.5, color=MUTED))
    render(os.path.join(IMG, "standing-wave.svg"), W, H, *f)


# ── Фігура 4: биття — дві близькі частоти пульсують гучністю ──────────────────
def fig_beats():
    W, H = 1020, 420
    f = [text(W / 2, 30, "Биття: дві близькі частоти то підсилюються, то гасяться", size=16, bold=True)]
    xa, xb = 90, 960
    yc = 210
    A = 78
    carrier = 21.0     # швидка несуча
    Bn = 1.0           # обвідна: 2 повні періоди биття у вікні
    n = 900

    # обвідна ±A·cos(2π·Bn·u)
    envp = [(xa + i / n * (xb - xa), yc - A * math.cos(2 * math.pi * Bn * (i / n))) for i in range(n + 1)]
    envm = [(xa + i / n * (xb - xa), yc + A * math.cos(2 * math.pi * Bn * (i / n))) for i in range(n + 1)]
    f.append(poly(envp, color=ENV, sw=1.6, dash="6,5"))
    f.append(poly(envm, color=ENV, sw=1.6, dash="6,5"))

    # сумарний сигнал
    sig = []
    for i in range(n + 1):
        u = i / n
        x = xa + u * (xb - xa)
        y = yc - A * math.cos(2 * math.pi * Bn * u) * math.sin(2 * math.pi * carrier * u)
        sig.append((x, y))
    f.append(poly(sig, color=SUM, sw=2.0))
    f.append(line(xa, yc, xb, yc, color=GRID, sw=1.2))

    # позначки гучно / тихо
    for uu, lab, col in [(0.0, "гучно", INK), (0.25, "тихо", MUTED), (0.5, "гучно", INK),
                         (0.75, "тихо", MUTED), (1.0, "гучно", INK)]:
        xx = xa + uu * (xb - xa)
        if lab == "тихо":
            f.append(circle(xx, yc, 4.5, fill=MUTED, stroke=MUTED, sw=1))
            f.append(text(xx, yc + 38, lab, size=12, color=col))
        else:
            f.append(text(xx, yc - A - 12, lab, size=12.5, bold=True, color=col))

    # період биття (гучно → гучно)
    x0 = xa + 0.0 * (xb - xa)
    x1 = xa + 0.5 * (xb - xa)
    ybr = yc + A + 44
    f.append(line(x0, ybr, x1, ybr, color=INK, sw=1.6))
    f.append(line(x0, ybr - 6, x0, ybr + 6, color=INK, sw=1.6))
    f.append(line(x1, ybr - 6, x1, ybr + 6, color=INK, sw=1.6))
    f.append(text((x0 + x1) / 2, ybr - 10, "період биття  T = 1/|f₁ − f₂|", size=12.5, bold=True))

    box, bw, bh = textbox(W / 2, 396, "частота биття:   f_биття = | f₁ − f₂ |",
                          size=14, pad=10, fill="#f4f6f8", stroke=INK, sw=1.3)
    f.append(box)
    render(os.path.join(IMG, "beats.svg"), W, H, *f)


# ── Фігура 5: защипнута струна як сума обертонів — крок до кута ───────────────
def fig_pluck_harmonics():
    W, H = 1060, 400
    f = [text(W / 2, 30, "Защипнута струна — сума синусів-обертонів: гострий кут виникає в границі", size=16, bold=True)]

    def tri(u):                     # трикутник із вершиною 1 при u = 0.5
        return 2 * u if u <= 0.5 else 2 * (1 - u)

    def psum(u, K):                 # часткова сума за непарними k = 1,3,…,K
        s = 0.0
        k = 1
        while k <= K:
            sign = 1 if ((k - 1) // 2) % 2 == 0 else -1
            s += sign * math.sin(k * math.pi * u) / (k * k)
            k += 2
        return (8 / math.pi ** 2) * s

    pw, gap, ox0 = 232, 20, 30
    yb, amp = 300, 150              # база й масштаб висоти (вершина → yb−amp)
    panels = [(1, "лише основний тон", "1 синус"),
              (3, "додали 3-й обертон", "1 + 3"),
              (7, "додали 5-й і 7-й", "1 + 3 + 5 + 7"),
              (31, "багато обертонів", "1 + 3 + … + 31")]
    N = 240
    for j, (K, capt, tag) in enumerate(panels):
        ox = ox0 + j * (pw + gap)
        x0, x1 = ox + 14, ox + pw - 14
        pwid = x1 - x0
        f.append(text(ox + pw / 2, 66, tag, size=13.5, bold=True, color=SUM))
        f.append(line(x0, yb, x1, yb, color=GRID, sw=1.3))
        # ціль — трикутник защипу (світло-сірий пунктир)
        tgt = [(x0 + i / N * pwid, yb - tri(i / N) * amp) for i in range(N + 1)]
        f.append(poly(tgt, color="#b9c0ca", sw=1.6, dash="5,5"))
        # часткова сума (кольорова, товста)
        col = [W2, "#8e44ad", "#c0392b", "#1a1a1a"][j]
        cur = [(x0 + i / N * pwid, yb - psum(i / N, K) * amp) for i in range(N + 1)]
        f.append(poly(cur, color=col, sw=2.8))
        f.append(text(ox + pw / 2, yb + 30, capt, size=12, color=MUTED))
    # легенда
    f.append(line(ox0, 356, ox0 + 34, 356, color="#b9c0ca", sw=1.8, dash="5,5"))
    f.append(text(ox0 + 42, 360, "ціль — форма защипнутої струни (кут)", size=12, color=MUTED, anchor="start"))
    f.append(text(W - 30, 360, "що більше синусів — то ближче гладка сума до зламу", size=12.5, color=INK, anchor="end"))
    render(os.path.join(IMG, "pluck-harmonics.svg"), W, H, *f)


# ── Фігура 6: хроніка суперечки про струну ───────────────────────────────────
def fig_controversy_timeline():
    W, H = 1080, 760
    f = [text(W / 2, 32, "Суперечка про струну: хто, коли, що заявив", size=17, bold=True)]
    xline = 168
    f.append(line(xline, 92, xline, 712, color=GRID, sw=2.4))

    rows = [
        (120, "1713", "Brook Taylor — англієць", MUTED,
         "форма струни — синусоїда; висота тону ∝ √(натяг / маса на довжину)"),
        (210, "1747", "Jean d'Alembert — француз", NEG,
         "хвильове рівняння та його загальний розв'язок — дві біжучі хвилі; але форма мусить бути «однією формулою»"),
        (300, "1748", "Leonhard Euler — швейцарець", "#8e44ad",
         "початкова форма — будь-яка накреслена від руки крива, навіть зі зламом (защип)"),
        (390, "1753", "Daniel Bernoulli — швейцарець", "#c0392b",
         "будь-яке коливання струни — сума основного тону й обертонів, тобто сума синусів"),
        (480, "1777", "Euler — знову", "#8e44ad",
         "виводить формулу коефіцієнтів (раніше й Clairaut, 1754) — та не вірить, що ряд дає геть довільну форму"),
        (570, "1807 / 1822", "Joseph Fourier — француз", FIELD,
         "довільну функцію справді складає ряд синусів — і ось інтеграл, що знаходить кожен коефіцієнт"),
        (660, "1829", "P. G. L. Dirichlet — німець", INK,
         "строгі умови, за яких ряд Фур'є збігається саме до заданої функції"),
    ]
    for yr, year, who, col, claim in rows:
        f.append(circle(xline, yr, 7.5, fill=col, stroke=col, sw=1))
        f.append(text(xline - 18, yr + 4, year, size=13.5, bold=True, anchor="end"))
        f.append(text(xline + 22, yr - 7, who, size=14, bold=True, color=col, anchor="start"))
        f.append(text(xline + 22, yr + 15, claim, size=12.5, color=MUTED, anchor="start"))

    # смуги «суперечка» / «розв'язка»
    f.append(line(W - 30, 190, W - 30, 410, color=NEG, sw=3))
    f.append(text(W - 40, 300, "с у п е р е ч к а", size=12.5, bold=True, color=NEG, anchor="end"))
    f.append(line(W - 30, 548, W - 30, 682, color=FIELD, sw=3))
    f.append(text(W - 40, 615, "р о з в ' я з к а", size=12.5, bold=True, color=FIELD, anchor="end"))
    render(os.path.join(IMG, "controversy-timeline.svg"), W, H, *f)


# ── Фігура 7 (math-вставка): одна крива амплітуди керує і гасінням, і биттям ──
def fig_phase_amplitude():
    W, H = 1000, 540
    f = [text(W / 2, 30, "Амплітуда суми двох рівних хвиль = 2A·|cos(Δφ/2)| — одна крива на всі випадки",
              size=15.5, bold=True)]
    x0, x1 = 130, 900          # вісь Δφ: 0 … 360°
    yb, yt = 400, 120          # yb — амплітуда 0; yt — амплітуда 2A
    span = x1 - x0
    hpx = yb - yt

    def X(deg):
        return x0 + deg / 360.0 * span

    def Y(deg):
        return yb - hpx * abs(math.cos(math.radians(deg) / 2.0))

    # осі
    f.append(line(x0, yb, x1 + 24, yb, color=INK, sw=1.6))
    f.append(line(x0, yt - 12, x0, yb, color=INK, sw=1.6))
    f.append(text(x1 + 30, yb + 4, "Δφ", size=13, anchor="start", bold=True))
    f.append(text(x0 - 12, yt + 4, "2A", size=12.5, color=MUTED, anchor="end"))
    yA2 = yb - hpx * (2 ** 0.5 / 2)
    f.append(line(x0, yA2, x1, yA2, color=GRID, sw=1.1, dash="4,5"))
    f.append(text(x0 - 12, yA2 + 4, "A√2", size=12, color=MUTED, anchor="end"))
    f.append(text(x0 - 12, yb + 4, "0", size=12.5, color=MUTED, anchor="end"))

    # вертикальні позначки фаз
    for deg in (0, 90, 180, 270, 360):
        f.append(line(X(deg), yt, X(deg), yb, color=GRID, sw=1.0))
        f.append(line(X(deg), yb, X(deg), yb + 6, color=INK, sw=1.4))
        f.append(text(X(deg), yb + 22, "%d°" % deg, size=12, color=MUTED))

    # крива 2A|cos(Δφ/2)|
    curve = [(X(d), Y(d)) for d in range(0, 361)]
    f.append(poly(curve, color=SUM, sw=3.0))

    # особливі точки
    f.append(circle(X(0), Y(0), 5.5, fill=W1, stroke=W1, sw=1))
    f.append(text(X(0) + 8, Y(0) - 12, "2A — у фазі: підсилення (гучно)", size=12, color=W1, anchor="start"))
    f.append(circle(X(360), Y(360), 5.5, fill=W1, stroke=W1, sw=1))
    f.append(circle(X(180), Y(180), 6.0, fill=W2, stroke=W2, sw=1))
    f.append(text(X(180), Y(180) - 16, "0 — у протифазі: гасіння (тиша)", size=12.5, color=W2, bold=True))
    f.append(circle(X(90), Y(90), 4.5, fill=MUTED, stroke=MUTED, sw=1))
    f.append(circle(X(270), Y(270), 4.5, fill=MUTED, stroke=MUTED, sw=1))

    # два способи читати ту саму криву
    f.append(fitbox(120, 452, 385, 74,
                    "ЗАМОРОЗЬ Δφ (стала в часі)\n→ інтерференція: у кожній точці\nсвоя незмінна гучність",
                    size=12, fill="#fdf0ee", stroke=W1, sw=1.4, color=INK))
    f.append(fitbox(512, 452, 385, 74,
                    "ХАЙ Δφ ПЛИВЕ:  Δφ = (ω₁−ω₂)·t\n→ биття: амплітуда сама котиться\nкривою  гучно → тиша → гучно",
                    size=12, fill="#eef2fd", stroke=W2, sw=1.4, color=INK))
    render(os.path.join(IMG, "phase-amplitude.svg"), W, H, *f)


# ── Фігура 8 (math-вставка): чому f_биття = |f₁−f₂|, а не половина ─────────────
def fig_beats_doubling():
    W, H = 1020, 470
    f = [text(W / 2, 30, "Гучність |cos| пульсує вдвічі частіше за саму обвідну cos → f_биття = |f₁−f₂|",
              size=15, bold=True)]
    xa, xb = 110, 910
    yc = 195
    A = 82
    carrier = 15.0
    n = 900
    span = xb - xa

    # сигнал 2A·cos(2π·u)·sin(2π·carrier·u): вікно = рівно один період cos-обвідної
    sig = []
    for i in range(n + 1):
        u = i / n
        x = xa + u * span
        y = yc - A * math.cos(2 * math.pi * u) * math.sin(2 * math.pi * carrier * u)
        sig.append((x, y))
    f.append(poly(sig, color=SUM, sw=1.6))

    # cos-обвідна ± (червоний пунктир) — один повний період: +1 → −1 → +1
    envp = [(xa + i / n * span, yc - A * math.cos(2 * math.pi * (i / n))) for i in range(n + 1)]
    envm = [(xa + i / n * span, yc + A * math.cos(2 * math.pi * (i / n))) for i in range(n + 1)]
    f.append(poly(envp, color=ENV, sw=1.6, dash="6,5"))
    f.append(poly(envm, color=ENV, sw=1.6, dash="6,5"))

    # |cos|-гучність (зелені горби) — ДВА горби на один період cos
    loud = [(xa + i / n * span, yc - A * abs(math.cos(2 * math.pi * (i / n)))) for i in range(n + 1)]
    f.append(poly(loud, color=FIELD, sw=2.6))
    f.append(line(xa, yc, xb, yc, color=GRID, sw=1.2))

    # гучно при u=0, 0.5, 1;  тихо при u=0.25, 0.75
    for u in (0.0, 0.5, 1.0):
        f.append(text(xa + u * span, yc - A - 12, "гучно", size=12, bold=True, color=FIELD))
    for u in (0.25, 0.75):
        xx = xa + u * span
        f.append(circle(xx, yc, 4.5, fill=MUTED, stroke=MUTED, sw=1))
        f.append(text(xx, yc + 40, "тихо", size=12, color=MUTED))

    # дужка зверху: один період cos-обвідної (u=0..1)
    ytop = yc - A - 42
    f.append(line(xa, ytop, xb, ytop, color=W2, sw=1.6))
    f.append(line(xa, ytop, xa, ytop + 8, color=W2, sw=1.6))
    f.append(line(xb, ytop, xb, ytop + 8, color=W2, sw=1.6))
    f.append(text((xa + xb) / 2, ytop - 8, "один період обвідної cos:  T_cos = 2 / |f₁−f₂|",
                  size=12.5, bold=True, color=W2))

    # дужка знизу: один цикл биття (u=0..0.5)
    ybot = yc + A + 60
    xm = xa + 0.5 * span
    f.append(line(xa, ybot, xm, ybot, color=FIELD, sw=1.8))
    f.append(line(xa, ybot, xa, ybot - 8, color=FIELD, sw=1.8))
    f.append(line(xm, ybot, xm, ybot - 8, color=FIELD, sw=1.8))
    f.append(text((xa + xm) / 2, ybot + 16, "чутне биття (гучно→тихо→гучно):  T_биття = 1 / |f₁−f₂|",
                  size=12.5, bold=True, color=FIELD))
    render(os.path.join(IMG, "beats-doubling.svg"), W, H, *f)


# ── Фігура (proj): складання відлік за відліком — стеми трьох масивів ─────────
def fig_samples_sum():
    W, H = 1000, 560
    f = [text(W / 2, 30, "Складання відлік за відліком:  y[n] = y₁[n] + y₂[n]", size=16, bold=True)]
    xa, xb = 120, 900
    N = 24
    SCALE = 68.0
    a1, c1, ph1 = 0.50, 1.5, 0.0
    a2, c2, ph2 = 0.34, 3.0, 0.6

    def v1(nn):
        u = nn / (N - 1)
        return a1 * math.sin(2 * math.pi * c1 * u + ph1)

    def v2(nn):
        u = nn / (N - 1)
        return a2 * math.sin(2 * math.pi * c2 * u + ph2)

    def xof(nn):
        return xa + nn / (N - 1) * (xb - xa)

    panels = [
        (130, v1, W1, "y₁[n]   (нижчий тон)"),
        (285, v2, W2, "y₂[n]   (вищий тон)"),
        (460, lambda nn: v1(nn) + v2(nn), SUM, "y[n] = y₁[n] + y₂[n]   (сума)"),
    ]
    hi = 5
    for yb, fn, col, lab in panels:
        f.append(line(xa - 14, yb, xb + 14, yb, color=GRID, sw=1.4))
        f.append(text(xa - 14, yb - 64, lab, size=13.5, bold=True, color=col, anchor="start"))
        for nn in range(N):
            x = xof(nn)
            y = yb - fn(nn) * SCALE
            f.append(line(x, yb, x, y, color=col, sw=2.4))
            f.append(circle(x, y, 3.4, fill=col, stroke=col, sw=1))
    xh = xof(hi)
    f.append(line(xh, 78, xh, 520, color=FIELD, sw=1.5, dash="5,5"))
    f.append(text(xh, 74, "n = %d" % hi, size=12, bold=True, color=FIELD))

    def fmt(v):
        return ("%.2f" % v) if v >= 0 else ("(−%.2f)" % (-v))
    val = "%.2f + %s = %.2f" % (v1(hi), fmt(v2(hi)), v1(hi) + v2(hi))
    f.append(fitbox(W / 2 - 175, 526, 350, 28, "у відліку n = %d:   %s" % (hi, val),
                    size=13.5, fill="#eefaf1", stroke=FIELD))
    render(os.path.join(IMG, "samples-sum.svg"), W, H, *f)


# ── Фігура (proj): синтез квадрата із синусів і викид Ґіббса ──────────────────
def fig_gibbs():
    W, H = 1000, 470
    f = [text(W / 2, 30, "Синтез квадрата із синусів: більше гармонік — гостріше, але викид лишається",
              size=15.5, bold=True)]
    xa, xb = 80, 930
    yc = 250
    A = 120
    n = 900
    periods = 2.0

    def partial(u, Nh):
        s = 0.0
        for k in range(1, 2 * Nh, 2):
            s += math.sin(2 * math.pi * k * u) / k
        return (4 / math.pi) * s

    def ideal(u):
        return 1.0 if (u % 1.0) < 0.5 else -1.0

    f.append(line(xa, yc, xb, yc, color=GRID, sw=1.2))
    sq = [(xa + i / n * (xb - xa), yc - A * ideal(periods * i / n)) for i in range(n + 1)]
    f.append(poly(sq, color="#c3c9d2", sw=2.0))

    curves = [(1, "#f0b3ab", "1"), (3, "#e07f72", "3"),
              (11, "#cf4a39", "11"), (63, "#7a1d12", "63")]
    for Nh, col, lab in curves:
        pts = [(xa + i / n * (xb - xa), yc - A * partial(periods * i / n, Nh)) for i in range(n + 1)]
        f.append(poly(pts, color=col, sw=2.4 if Nh == 63 else 1.9))

    # позначити викид біля стрибка (u ≈ 0.5) для щільної суми
    umax, vmax = 0.0, -9.0
    for i in range(135, 225):
        u = periods * i / n
        v = partial(u, 63)
        if v > vmax:
            vmax, umax = v, u
    xo = xa + (umax / periods) * (xb - xa)
    yo = yc - A * vmax
    f.append(circle(xo, yo, 4, fill=POS, stroke=POS, sw=1))
    f.append(line(xo, yo - 6, xo + 60, yo - 34, color=MUTED, sw=1.2))
    f.append(text(xo + 64, yo - 36, "≈ 9% викид (Ґіббс)", size=12.5, bold=True, color=POS, anchor="start"))

    # легенда
    lx, ly = xa, H - 22
    f.append(text(lx, ly, "гармонік у сумі:", size=12, color=MUTED, anchor="start"))
    xoff = lx + text_width("гармонік у сумі:", 12) + 16
    f.append(line(xoff, ly - 4, xoff + 22, ly - 4, color="#c3c9d2", sw=3))
    f.append(text(xoff + 27, ly, "ідеал", size=12, color=INK, anchor="start"))
    xoff += 27 + text_width("ідеал", 12) + 26
    for Nh, col, lab in curves:
        f.append(line(xoff, ly - 4, xoff + 22, ly - 4, color=col, sw=3))
        f.append(text(xoff + 27, ly, lab, size=12, color=INK, anchor="start"))
        xoff += 27 + text_width(lab, 12) + 26
    render(os.path.join(IMG, "gibbs.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pulses_pass()
    fig_interference()
    fig_standing_wave()
    fig_beats()
    fig_pluck_harmonics()
    fig_controversy_timeline()
    fig_phase_amplitude()
    fig_beats_doubling()
    fig_samples_sum()
    fig_gibbs()
    print("OK: figs written to", IMG)
