# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# локальні кольори для шести кривих (крім палітри svgkit)
C_ONE   = FIELD          # O(1)      — зелений, найкращий
C_LOG   = "#2457d6"      # O(log n)  — синій
C_LIN   = "#0e9aa7"      # O(n)      — бірюзовий
C_NLOGN = "#8e44ad"      # O(n log n)— фіолетовий
C_SQ    = "#e08a1e"      # O(n²)     — помаранчевий
C_EXP   = POS            # O(2ⁿ)     — червоний, найгірший


# ── Фіг. 1: криві зростання — як розходяться класи ────────────────────────────
# Ідея: поставити O(1), O(log n), O(n), O(n log n), O(n²), O(2ⁿ) на одні осі.
# Логарифм майже стелеться; квадрат і особливо експонента пробивають стелю
# графіка вже на маленькому n. Ця прірва й робить клас важливішим за множник.
def fig_growth_curves():
    W, H = 920, 500
    p = []
    ox, oy = 90.0, 430.0
    pw, ph = 560.0, 350.0
    N = 20
    ycap = 100.0

    def X(n):
        return ox + pw * (n - 1) / (N - 1)

    def Y(v):
        return oy - ph * min(v, ycap) / ycap

    # осі
    p.append(line(ox, oy, ox + pw + 8, oy, color=INK, sw=1.4))
    p.append(line(ox, oy, ox, oy - ph - 6, color=INK, sw=1.4))
    p.append(text(ox + pw / 2, oy + 40, "розмір входу  n  →", size=12.5, color=INK))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="12.5" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 52, oy - ph / 2, FONT, INK, esc("кількість кроків  T(n)  →")))

    # стеля графіка
    p.append(line(ox, Y(ycap), ox + pw, Y(ycap), color=MUTED, sw=1.2, dash="6 5"))
    p.append(text(ox + pw - 6, Y(ycap) - 8, "стеля графіка — далі не влазить",
                  size=11, color=MUTED, anchor="end"))

    def curve(f, color, clip_label=None):
        pts = []
        prev = None
        clip_x = None
        nx = 1.0
        while nx <= N + 1e-9:
            v = f(nx)
            if v <= ycap:
                pts.append((X(nx), Y(v)))
                prev = (nx, v)
            else:
                if prev is not None:
                    n0, v0 = prev
                    t = (ycap - v0) / (v - v0)
                    ns = n0 + t * (nx - n0)
                    pts.append((X(ns), Y(ycap)))
                    clip_x = X(ns)
                break
            nx += 0.25
        poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (poly, color))
        if clip_x is not None and clip_label is not None:
            p.append(arrow(clip_x, Y(ycap), clip_x, Y(ycap) - 18, color=color, sw=2.0))
            p.append(text(clip_x, Y(ycap) - 24, clip_label, size=12.5, color=color, bold=True))

    curve(lambda n: 1.0, C_ONE)
    curve(lambda n: math.log(n, 2), C_LOG)
    curve(lambda n: n, C_LIN)
    curve(lambda n: n * math.log(n, 2), C_NLOGN)
    curve(lambda n: n * n, C_SQ, clip_label="n²")
    curve(lambda n: 2.0 ** n, C_EXP, clip_label="2ⁿ")

    # легенда — окрема панель праворуч (не перетинає криві)
    lx, ly, lw, lh = 668.0, 92.0, 234.0, 300.0
    p.append(rect(lx, ly, lw, lh, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
    p.append(text(lx + lw / 2, ly + 26, "класи зростання", size=13, color=INK, bold=True))
    rows = [
        (C_ONE,   "O(1)",       "стала"),
        (C_LOG,   "O(log n)",   "логарифм"),
        (C_LIN,   "O(n)",       "лінійна"),
        (C_NLOGN, "O(n log n)", "майже лінійна"),
        (C_SQ,    "O(n²)",      "квадратична"),
        (C_EXP,   "O(2ⁿ)",      "експонента"),
    ]
    ry = ly + 58
    for col, name, note in rows:
        p.append(line(lx + 18, ry, lx + 52, ry, color=col, sw=3.4))
        p.append(text(lx + 62, ry - 6, name, size=13, color=INK, bold=True, anchor="start"))
        p.append(text(lx + 62, ry + 12, note, size=11, color=MUTED, anchor="start"))
        ry += 40

    render(os.path.join(OUT, "growth-curves.svg"), W, H, *p,
           title="Класи зростання на одних осях: прірва між ними колосальна")


# ── Фіг. 2: що означає O — стеля з точністю до сталого множника ───────────────
# Ідея: реальне число кроків 3n²+5n+7 на малих n навіть перевищує обрану стелю
# c·g(n)=4n², але від порога n₀ стеля лягає зверху назавжди. Тому нижчі доданки
# й сталий множник відкидають: на великих n вони не міняють, під якою стелею
# живе функція. Це наочне «∃c, n₀: f(n) ≤ c·g(n) для всіх n ≥ n₀».
def fig_big_o_envelope():
    W, H = 800, 470
    p = []
    ox, oy = 92.0, 410.0
    pw, ph = 588.0, 320.0
    NM = 13.0
    ymax = 680.0
    n0 = (5 + math.sqrt(53)) / 2   # 3n²+5n+7 = 4n²  →  n²−5n−7 = 0

    def X(n):
        return ox + pw * n / NM

    def Y(v):
        return oy - ph * v / ymax

    # затінення області n ≥ n₀ (стеля зверху) — під кривими
    p.append(rect(X(n0), Y(ymax), (ox + pw) - X(n0), oy - Y(ymax),
                  fill="#eef7f0", stroke="none", sw=0, rx=0))

    # осі
    p.append(line(ox, oy, ox + pw + 8, oy, color=INK, sw=1.4))
    p.append(line(ox, oy, ox, oy - ph - 6, color=INK, sw=1.4))
    p.append(text(ox + pw / 2, oy + 40, "розмір входу  n  →", size=12.5, color=INK))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="12.5" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 54, oy - ph / 2, FONT, INK, esc("кількість кроків  →")))

    def plot(f, color, sw=2.6):
        pts = []
        n = 0.0
        while n <= NM + 1e-9:
            pts.append((X(n), Y(f(n))))
            n += 0.25
        poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (poly, color, sw))

    plot(lambda n: 4 * n * n, C_ONE)                 # стеля c·g(n)
    plot(lambda n: 3 * n * n + 5 * n + 7, C_LOG)     # справжня f(n)

    # вертикаль порога n₀
    p.append(line(X(n0), oy, X(n0), Y(ymax) + 4, color=MUTED, sw=1.4, dash="6 5"))
    p.append(text(X(n0), oy + 20, "n₀", size=13, color=INK, bold=True))

    # підписи кривих (права частина, зелена вище синьої)
    p.append(text(X(12.6), Y(4 * 12.6 ** 2) - 10, "c·g(n) = 4n²  — стеля",
                  size=12.5, color=C_ONE, bold=True, anchor="end"))
    p.append(text(X(13), Y(3 * 13 ** 2 + 5 * 13 + 7) + 20, "f(n) = 3n²+5n+7",
                  size=12.5, color=C_LOG, bold=True, anchor="end"))

    # пояснювальна рамка — верхній лівий кут (там обидві криві низько)
    b, bw, bh = textbox(ox + 168, Y(ymax) + 52,
                        "від n₀ і далі:  f(n) ≤ c·g(n)\nстеля зверху назавжди  ⟹  f = O(n²)",
                        size=12.5, bold=True, fill="#fff6e6", stroke="#e08a1e")
    p.append(b)

    render(os.path.join(OUT, "big-o-envelope.svg"), W, H, *p,
           title="O велике: стеля зростання з точністю до сталого множника")


# ── Фіг. 3: реакція класів на подвоєння входу + практичний присуд ─────────────
# Ідея: найгостріше клас відчувається у відповіді на «вхід подвоївся — що з
# роботою?». Від «без змін» для сталої до «підноситься у квадрат» для експоненти.
# Праворуч — практичний присуд, кольором від зеленого (масштабується) до
# червоного (нежиттєздатно).
def fig_doubling_response():
    W, H = 906, 524
    p = []
    x0 = 30.0
    w1, w2, w3 = 180.0, 348.0, 300.0
    gap = 8.0
    cx1 = x0
    cx2 = cx1 + w1 + gap
    cx3 = cx2 + w2 + gap
    y0, rowh = 70.0, 54.0

    # заголовок таблиці
    def hcell(x, w, s):
        p.append(rect(x, y0, w, rowh, fill="#eef2f8", stroke="#c2cad4", sw=1.3, rx=6))
        p.append(text(x + w / 2, y0 + rowh / 2 + 5, s, size=12.5, color=INK, bold=True))
    hcell(cx1, w1, "клас")
    hcell(cx2, w2, "вхід подвоюється  →  робота")
    hcell(cx3, w3, "практичний присуд")

    G, Nn, Or, Rd = "#eef7f0", "#eef2f8", "#fdf2e6", "#fdecea"
    Gs, Ns, Ors, Rds = FIELD, "#aab4c0", "#e08a1e", POS
    rows = [
        ("O(1)",       "без змін  (×1)",                 "миттєво, байдуже до n",        G,  Gs,  C_ONE),
        ("O(log n)",   "+1 крок",                        "ідеально масштабується",       G,  Gs,  C_LOG),
        ("O(n)",       "×2",                             "чесно, лінійно",               Nn, Ns,  C_LIN),
        ("O(n log n)", "трохи більше за ×2",             "майже лінійно — дуже добре",   Nn, Ns,  C_NLOGN),
        ("O(n²)",      "×4",                             "боляче на великих n",          Or, Ors, C_SQ),
        ("O(2ⁿ)",      "підноситься у квадрат  (T→T²)",  "нежиттєздатно поза малими n",  Rd, Rds, C_EXP),
    ]
    for i, (cls, react, verdict, fill, stroke, ccol) in enumerate(rows):
        ry = y0 + (i + 1) * rowh
        # клітина класу — колір мітки за кривою
        p.append(rect(cx1, ry, w1, rowh, fill=BG, stroke="#dfe4ea", sw=1.2, rx=6))
        p.append(line(cx1 + 14, ry + rowh / 2, cx1 + 40, ry + rowh / 2, color=ccol, sw=3.4))
        p.append(text(cx1 + 50, ry + rowh / 2 + 5, cls, size=13, color=INK, bold=True, anchor="start"))
        # клітина реакції
        p.append(fitbox(cx2, ry, w2, rowh, react, size=13, pad=10,
                        fill=fill, stroke=stroke, color=INK, bold=True))
        # клітина присуду
        p.append(fitbox(cx3, ry, w3, rowh, verdict, size=12.5, pad=10,
                        fill=fill, stroke=stroke, color=INK))

    yb = y0 + 7 * rowh + 10
    p.append(fitbox(x0, yb, cx3 + w3 - x0, 40,
                    "той самий клас — та сама реакція на будь-якому залізі: "
                    "подвоєння входу не питає, який у тебе процесор",
                    size=13, bold=True, fill="#fff6e6", stroke="#e08a1e", color=INK))

    render(os.path.join(OUT, "doubling-response.svg"), W, H, *p,
           title="Вхід подвоївся — що робить робота?")


# ── Фіг. (proj): декодер подвоєння — відношення часів → показник → клас ───────
# Ідея: серце методу подвоєння. Для степеневого закону T(n)=a·nᵇ відношення
# сусідніх часів T(2n)/T(n) = 2ᵇ, тож показник читається просто: b = log₂(відн.).
# Таблиця перекладає відношення (1, 2, 3, 4, 8, вибух) на клас і присуд.
def fig_doubling_decoder():
    W, H = 960, 566
    p = []
    bhead, bw, bh = textbox(W / 2, 60, "b = log₂( T(2n) / T(n) )", size=19, bold=True,
                            fill="#eef2f8", stroke="#c2cad4")
    p.append(bhead)
    p.append(text(W / 2, 96, "заміряй час на n, 2n, 4n…  —  і читай клас із відношення сусідніх часів",
                  size=12.5, color=MUTED))

    x0 = 34.0
    w1, w2, w3, w4 = 118.0, 96.0, 176.0, 472.0
    gap = 8.0
    cx1 = x0
    cx2 = cx1 + w1 + gap
    cx3 = cx2 + w2 + gap
    cx4 = cx3 + w3 + gap
    y0, rowh = 122.0, 58.0

    p.append(fitbox(cx1, y0, w1, rowh, "T(2n)/T(n)", size=12.5, pad=6,
                    fill="#eef2f8", stroke="#c2cad4", bold=True))
    p.append(fitbox(cx2, y0, w2, rowh, "b", size=13, pad=6,
                    fill="#eef2f8", stroke="#c2cad4", bold=True))
    p.append(fitbox(cx3, y0, w3, rowh, "клас", size=12.5, pad=6,
                    fill="#eef2f8", stroke="#c2cad4", bold=True))
    p.append(fitbox(cx4, y0, w4, rowh, "як це читати", size=12.5, pad=6,
                    fill="#eef2f8", stroke="#c2cad4", bold=True))

    G, Nn, Or, Rd = "#eef7f0", "#eef2f8", "#fdf2e6", "#fdecea"
    Gs, Ns, Ors, Rds = FIELD, "#aab4c0", "#e08a1e", POS
    rows = [
        ("≈ 1",     "0",      "O(1) або O(log n)",
         "стала не росте зовсім;\nлогарифм додає лише крихту", G,  Gs,  C_LOG),
        ("≈ 2",     "1",      "O(n)",
         "лінійний прохід —\nчас масштабується чесно",         Nn, Ns,  C_LIN),
        ("≈ 3",     "≈ 1.58", "між O(n) і O(n²)",
         "поділяй-і-володарюй нижче квадрата\n(множення Карацуби)", Nn, Ns, C_NLOGN),
        ("≈ 4",     "2",      "O(n²)",
         "вкладений цикл: кожне\nподвоєння вчетверо дорожче",   Or, Ors, C_SQ),
        ("≈ 8",     "3",      "O(n³)",
         "три вкладені цикли (ThreeSum):\nподвоєння — увосьмеро", Or, Ors, C_SQ),
        ("вибухає", "—",      "не степінь",
         "відношення не стоїть на місці —\nце вже експонента O(2ⁿ)", Rd, Rds, C_EXP),
    ]
    for i, (r, bb, cls, note, fill, stroke, ccol) in enumerate(rows):
        ry = y0 + (i + 1) * rowh
        p.append(fitbox(cx1, ry, w1, rowh, r, size=14, pad=6,
                        fill=BG, stroke="#dfe4ea", bold=True))
        p.append(fitbox(cx2, ry, w2, rowh, bb, size=14, pad=6,
                        fill=BG, stroke="#dfe4ea", bold=True))
        p.append(rect(cx3, ry, w3, rowh, fill=BG, stroke="#dfe4ea", sw=1.2, rx=6))
        p.append(line(cx3 + 12, ry + rowh / 2, cx3 + 34, ry + rowh / 2, color=ccol, sw=3.4))
        fs = fit_font(cls, w3 - 52, 13, True)
        p.append(text(cx3 + 44, ry + rowh / 2 + 5, cls, size=fs, color=INK, bold=True, anchor="start"))
        p.append(fitbox(cx4, ry, w4, rowh, note, size=12.5, pad=10,
                        fill=fill, stroke=stroke, color=INK, bold=True))

    render(os.path.join(OUT, "doubling-decoder.svg"), W, H, *p,
           title="Метод подвоєння: відношення часів прямо називає клас")


# ── Фіг. (proj): чому подвоєння міряє нахил на лог-лог осях ───────────────────
# Ідея: на осях (log₂ n, log₂ T) степеневий закон T=a·nᵇ — це ПРЯМА з нахилом b.
# Один крок подвоєння входу — це +1 по горизонталі; висота, на яку піднялася
# крива, і є b. Тобто відношення T(2n)/T(n) — це двоточкова оцінка нахилу.
def fig_loglog_slope():
    W, H = 840, 540
    p = []
    ox, oy = 104.0, 440.0
    pw, ph = 566.0, 356.0
    XN, YT = 5.0, 11.0

    def X(lx):
        return ox + pw * lx / XN

    def Y(ly):
        return oy - ph * ly / YT

    p.append(line(ox, oy, ox + pw + 8, oy, color=INK, sw=1.4))
    p.append(line(ox, oy, ox, oy - ph - 6, color=INK, sw=1.4))
    p.append(text(ox + pw / 2, oy + 44, "log₂ n   —   крок праворуч = подвоєння входу",
                  size=12.5, color=INK))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="12.5" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 60, oy - ph / 2, FONT, INK, esc("log₂ T   —   подвоєний час = +1 угору")))

    labels = ["n", "2n", "4n", "8n", "16n", "32n"]
    for i, lab in enumerate(labels):
        p.append(line(X(i), oy, X(i), oy + 6, color=INK, sw=1.2))
        p.append(text(X(i), oy + 22, lab, size=11.5, color=MUTED))

    def plot(f, color):
        pts = " ".join("%.1f,%.1f" % (X(lx), Y(f(lx))) for lx in [0, 1, 2, 3, 4, 5])
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>' % (pts, color))

    lin = lambda lx: 1 + 1 * lx     # нахил 1 → O(n)
    sq = lambda lx: 1 + 2 * lx      # нахил 2 → O(n²)
    plot(lin, C_LIN)
    plot(sq, C_SQ)

    # трикутник нахилу для квадрата між lx=2 і lx=3
    p.append(line(X(2), Y(sq(2)), X(3), Y(sq(2)), color=MUTED, sw=1.4, dash="5 4"))
    p.append(line(X(3), Y(sq(2)), X(3), Y(sq(3)), color=MUTED, sw=1.4, dash="5 4"))
    p.append(text(X(3) + 10, (Y(sq(2)) + Y(sq(3))) / 2 + 4, "b = 2", size=13, color=C_SQ, bold=True, anchor="start"))
    # трикутник нахилу для лінії між lx=2 і lx=3
    p.append(line(X(2), Y(lin(2)), X(3), Y(lin(2)), color=MUTED, sw=1.4, dash="5 4"))
    p.append(line(X(3), Y(lin(2)), X(3), Y(lin(3)), color=MUTED, sw=1.4, dash="5 4"))
    p.append(text(X(3) + 10, (Y(lin(2)) + Y(lin(3))) / 2 + 4, "b = 1", size=13, color=C_LIN, bold=True, anchor="start"))
    p.append(text(X(2.5), Y(lin(2)) + 20, "крок = 1", size=11, color=MUTED))

    # підписи кривих
    p.append(text(X(4.05), Y(sq(4)) - 12, "нахил 2  →  O(n²)", size=12.5, color=C_SQ, bold=True, anchor="end"))
    p.append(text(X(5), Y(lin(5)) - 12, "нахил 1  →  O(n)", size=12.5, color=C_LIN, bold=True, anchor="end"))

    # пояснення — верхній лівий кут (там порожньо)
    bx, bxw, bxh = textbox(X(1.35), Y(9.4),
                           "один крок подвоєння підіймає\nlog₂T рівно на b\n⟹  b = log₂( T(2n)/T(n) )",
                           size=12.5, bold=True, fill="#eef7f0", stroke=FIELD)
    p.append(bx)

    render(os.path.join(OUT, "loglog-slope.svg"), W, H, *p,
           title="Подвоєння — це вимір нахилу на лог-лог осях")


# ── Фіг. (proj): збіжність відношення й шум (реальні заміри) ──────────────────
# Ідея: виміряні відношення — не ідеальні числа. Квадратичний код виходить на 4
# ЗНИЗУ (на малих n сталі ще важать), а шумний прогін стрибає навколо 2 (один
# замір бреше — тому медіана/повтори). Дані — справжні заміри з тексту.
def fig_ratio_convergence():
    W, H = 880, 500
    p = []
    ox, oy = 92.0, 408.0
    pw, ph = 610.0, 328.0
    xmax, ymax = 6.0, 5.2

    def X(s):
        return ox + pw * s / xmax

    def Y(v):
        return oy - ph * v / ymax

    p.append(line(ox, oy, ox + pw + 8, oy, color=INK, sw=1.4))
    p.append(line(ox, oy, ox, oy - ph - 6, color=INK, sw=1.4))
    p.append(text(ox + pw / 2, oy + 42, "крок подвоєння   (n, 2n, 4n, …)", size=12.5, color=INK))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="12.5" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 56, oy - ph / 2, FONT, INK, esc("виміряне T(2n)/T(n)")))

    for v in range(1, 6):
        p.append(line(ox, Y(v), ox - 6, Y(v), color=INK, sw=1.2))
        p.append(text(ox - 16, Y(v) + 4, str(v), size=11.5, color=MUTED, anchor="end"))

    # цільові межі
    p.append(line(X(0.4), Y(4), X(5.5), Y(4), color=C_SQ, sw=1.3, dash="6 5"))
    p.append(text(X(5.5), Y(4) - 8, "межа O(n²) = 4", size=11.5, color=C_SQ, bold=True, anchor="end"))
    p.append(line(X(0.4), Y(2), X(5.5), Y(2), color=C_LIN, sw=1.3, dash="6 5"))
    p.append(text(X(5.5), Y(2) - 8, "межа O(n) = 2", size=11.5, color=C_LIN, bold=True, anchor="end"))

    def series(pts, color):
        poly = " ".join("%.1f,%.1f" % (X(s), Y(v)) for s, v in pts)
        p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (poly, color))
        for s, v in pts:
            p.append(circle(X(s), Y(v), 4.2, fill=color, stroke=BG, sw=1.4))

    sq = [(1, 2.65), (2, 4.24), (3, 4.32), (4, 4.51), (5, 4.60)]   # count_pairs — реальні заміри
    bs = [(1, 1.98), (2, 2.02), (3, 1.56), (4, 2.84), (5, 2.16)]   # багато двійкових пошуків — реальні
    series(sq, C_SQ)
    series(bs, C_LIN)

    # анотації
    a1, aw, ah = textbox(X(1.4), Y(1.3),
                         "малі n занижують:\nсталі ще важать",
                         size=11.5, bold=True, fill="#fdf2e6", stroke="#e08a1e")
    p.append(a1)
    p.append(arrow(X(1.2), Y(1.75), X(1.03), Y(2.5), color="#e08a1e", sw=1.8))
    a2, aw2, ah2 = textbox(X(4.15), Y(3.75),
                           "шум ОС/GC: один прогін бреше\n→ бери медіану кількох",
                           size=11.5, bold=True, fill="#eef2f8", stroke="#aab4c0")
    p.append(a2)
    p.append(arrow(X(3.4), Y(3.12), X(3.05), Y(1.72), color="#0e9aa7", sw=1.8))

    render(os.path.join(OUT, "ratio-convergence.svg"), W, H, *p,
           title="Виміряні відношення: збіжність знизу й шум прогону")


# ── Фіг. 4: O vs Ω vs Θ — стеля, підлога, коридор ─────────────────────────────
# Ідея: три означення поруч. O — крива під стелею c·g; Ω — над підлогою c·g;
# Θ — затиснута між двома прямими c₁·g і c₂·g. В усіх трьох панелях відношення
# набуває чинності від того самого порога n₀ — це наочне «для всіх n ≥ n₀».
def fig_theta_sandwich():
    W, H = 900, 322
    p = []
    C_F = "#1a1a1a"          # сама f — чорна
    C_UP = C_ONE             # стеля — зелена
    C_LO = NEG               # підлога — синя
    dom = (0.0, 8.0)
    ymax = 15.0
    n0 = 3.0

    def panel(px, title, curves, corridor=None, cap=""):
        pw, ph = 268.0, 232.0
        py = 46.0
        p.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
        p.append(text(px + pw / 2, py + 26, title, size=14.5, color=INK, bold=True))
        ax, ay = px + 30, py + ph - 34
        aw, ah = pw - 52, ph - 88
        nlo, nhi = dom

        def X(n):
            return ax + aw * (n - nlo) / (nhi - nlo)

        def Y(v):
            return ay - ah * min(v, ymax) / ymax

        # коридор (для Θ) — заливка між двома прямими
        if corridor:
            lof, upf = corridor
            up = [(X(n), Y(upf(n))) for n in [nlo + 0.2 * i for i in range(int((nhi - nlo) / 0.2) + 1)]]
            lo = [(X(n), Y(lof(n))) for n in [nlo + 0.2 * i for i in range(int((nhi - nlo) / 0.2) + 1)]][::-1]
            poly = " ".join("%.1f,%.1f" % (x, y) for x, y in up + lo)
            p.append('<polygon points="%s" fill="#eef7f0" stroke="none"/>' % poly)

        # осі
        p.append(line(ax, ay, ax + aw + 6, ay, color=INK, sw=1.2))
        p.append(line(ax, ay, ax, ay - ah - 4, color=INK, sw=1.2))
        p.append(text(ax + aw - 2, ay + 18, "n", size=11.5, color=INK, anchor="end", italic=True))
        # поріг n₀
        p.append(line(X(n0), ay, X(n0), Y(ymax) + 2, color=MUTED, sw=1.2, dash="5 4"))
        p.append(text(X(n0), ay + 18, "n₀", size=12, color=INK, bold=True))

        for f, color, sw, lab, ly in curves:
            pts = [(X(n), Y(f(n))) for n in [nlo + 0.2 * i for i in range(int((nhi - nlo) / 0.2) + 1)] if 0.0 <= f(n) <= ymax + 1e-9]
            poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
            p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (poly, color, sw))
            p.append(text(X(7.9), Y(f(7.9)) + ly, lab, size=12, color=color, bold=True, anchor="end"))

        p.append(text(px + pw / 2, py + ph - 8, cap, size=11.5, color=MUTED))

    panel(20,
          "O — стеля",
          [(lambda n: 1.3 * n, C_UP, 2.4, "c·g", -6),
           (lambda n: 0.6 * n + 2.1, C_F, 2.6, "f", 16)],
          cap="f(n) ≤ c·g(n)")
    panel(316,
          "Ω — підлога",
          [(lambda n: 1.3 * n, C_LO, 2.4, "c·g", 16),
           (lambda n: 2.0 * n - 2.1, C_F, 2.6, "f", -6)],
          cap="f(n) ≥ c·g(n)")
    panel(612,
          "Θ — коридор",
          [(lambda n: 1.3 * n, C_UP, 2.2, "c₂·g", -6),
           (lambda n: 1.0 * n, C_LO, 2.2, "c₁·g", 15),
           (lambda n: 1.1 * n + 0.6, C_F, 2.6, "f", -6)],
          corridor=(lambda n: 1.0 * n, lambda n: 1.3 * n),
          cap="c₁·g(n) ≤ f(n) ≤ c₂·g(n)")

    render(os.path.join(OUT, "theta-sandwich.svg"), W, H, *p,
           title="Одна функція g — три різні твердження про f")


# ── Фіг. 5: границя відношення f/g як «диск налаштування» родини ──────────────
# Ідея: куди прямує f(n)/g(n) — і однозначно диктує символ. Нуль → o (строго
# менший); скінченне додатне → Θ (той самий порядок); нескінченність → ω
# (строго більший). O і Ω — «слабші» сусіди, що включають межу.
def fig_limit_dial():
    W, H = 900, 340
    p = []
    # шкала-диск угорі
    ax0, ax1, ay = 78.0, 822.0, 74.0
    p.append(line(ax0, ay, ax1, ay, color=INK, sw=1.6))
    p.append(arrow(ax1 - 28, ay, ax1 + 6, ay, color=INK, sw=1.6))
    p.append(text(ax0 - 14, ay + 5, "0", size=14, color=INK, bold=True, anchor="end"))
    p.append(text(ax1 + 12, ay + 5, "∞", size=15, color=INK, bold=True, anchor="start"))
    p.append(text((ax0 + ax1) / 2, ay - 16, "границя відношення   f(n) / g(n)   при  n → ∞",
                  size=12.5, color=MUTED))
    for xd in (326.0, 574.0):
        p.append(line(xd, ay - 7, xd, ay + 7, color=INK, sw=1.5))
    # три вузли на шкалі
    for xn, col in ((ax0, C_LOG), ((326 + 574) / 2, C_ONE), (ax1, C_EXP)):
        p.append(circle(xn, ay, 5.5, fill=col, stroke=BG, sw=1.6))

    def col_panel(px, head, rel, relcol, sub, also, ex):
        pw, ph = 250.0, 208.0
        py = 108.0
        p.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.3, rx=10))
        p.append(text(px + pw / 2, py + 30, head, size=14, color=INK, bold=True))
        p.append(text(px + pw / 2, py + 66, rel, size=21, color=relcol, bold=True))
        p.append(text(px + pw / 2, py + 90, sub, size=12, color=MUTED))
        p.append(fitbox(px + 18, py + 104, pw - 36, 44, also, size=12, pad=7,
                        fill="#f4f6f8", stroke="#dfe4ea", color=INK))
        p.append(text(px + pw / 2, py + ph - 14, ex, size=12.5, color=INK, bold=True))

    col_panel(40, "lim  =  0", "f = o(g)", C_LOG, "строго менший порядок",
              "звідси й f = O(g)\nале не Θ, не Ω", "n = o(n²)")
    col_panel(325, "0  <  lim  <  ∞", "f = Θ(g)", C_ONE, "той самий порядок",
              "звідси й O(g), і Ω(g)\nточна двобічна межа", "3n²+5n+7 = Θ(n²)")
    col_panel(610, "lim  =  ∞", "f = ω(g)", C_EXP, "строго більший порядок",
              "звідси й f = Ω(g)\nале не Θ, не O", "2ⁿ = ω(nᵏ)")

    render(os.path.join(OUT, "limit-dial.svg"), W, H, *p,
           title="Куди прямує f/g — той символ і чинний")


# ── Фіг. 6 (hist): часова смуга нотації порядку ──────────────────────────────
# Ідея: показати сторічну мандрівку одного знаку п'ятьма віхами (рівні колонки,
# роки як мітки, а не пропорційна вісь — інакше 1909 і 1914 злипаються). Тло
# внизу міняє колір: синє — теорія чисел, зелене — інформатика; знак перетнув
# межу полів аж у Кнута (1976).
def fig_notation_timeline():
    W, H = 1000, 470
    p = []
    yline = 214.0
    xl, xr = 96.0, 904.0
    cxs = [132.0, 316.0, 500.0, 684.0, 868.0]
    C_NT = "#2457d6"   # теорія чисел
    C_CS = FIELD       # інформатика

    milestones = [
        ("1871", "дю Буа-Реймон",   "відносні знаки ≺:\nсама ідея порядку",  C_NT),
        ("1894", "Бахман",          "знак O (Ordnung)\nу теорії чисел",       C_NT),
        ("1909", "Ландау",          "«мале o»;\nсимволи Ландау",              C_NT),
        ("1914", "Гарді й Літлвуд",  "Ω: «нескінченно\nчасто» (інший зміст)", C_NT),
        ("1976", "Кнут",            "O, Ω, Θ —\nлад для інформатики",         C_CS),
    ]

    # тло-смуги полів (низько, під нотатками)
    yb, hb = 356.0, 40.0
    xbnd = (cxs[3] + cxs[4]) / 2.0
    p.append(rect(xl, yb, xbnd - xl, hb, fill="#eaf0fd", stroke="#c7d6f5", sw=1.2, rx=8))
    p.append(rect(xbnd, yb, xr - xbnd, hb, fill="#eef7f0", stroke="#bfe6cd", sw=1.2, rx=8))
    p.append(text((xl + xbnd) / 2, yb + hb / 2 + 5, "аналітична теорія чисел",
                  size=13, color=C_NT, bold=True))
    p.append(text((xbnd + xr) / 2, yb + hb / 2 + 5, "інформатика",
                  size=13, color=C_CS, bold=True))

    # головна лінія часу
    p.append(line(xl, yline, xr, yline, color=INK, sw=2.2))
    p.append(arrow(xr - 2, yline, xr + 14, yline, color=INK, sw=2.2))
    p.append(text(xr + 20, yline + 5, "час", size=12.5, color=INK, anchor="start"))

    for cx, (year, name, note, col) in zip(cxs, milestones):
        # вузол на лінії
        p.append(circle(cx, yline, 8.0, fill=col, stroke=BG, sw=2.4))
        # рік + ім'я — рамка над лінією
        b, bw, bh = textbox(cx, 150.0, year + "\n" + name, size=14, bold=True,
                            fill="#ffffff", stroke=col, sw=1.6, min_w=150)
        p.append(b)
        # коротка нотатка — під лінією
        p.append(fitbox(cx - 86, 250.0, 172.0, 66.0, note, size=12.5, pad=9,
                        fill="#fbfdff", stroke="#dfe4ea", color=INK))

    p.append(text(W / 2, 420,
                  "ідея старша за знак на два десятиліття; у код нотація перейшла аж наприкінці шляху",
                  size=12.5, color=MUTED))

    render(os.path.join(OUT, "notation-timeline.svg"), W, H, *p,
           title="Століття мандрів однієї нотації: від лічби простих до алгоритмів")


# ── Фіг. 7 (hist): дві несумісні Ω на одній функції ──────────────────────────
# Ідея: осцилятор f(n) раз по раз вистрілює над планку C·g(n), а між сплесками
# падає під неї. Для Гарді–Літлвуда це Ω (перевищено нескінченно часто); для
# Кнута — не Ω (не тримається над планкою для всіх великих n). Той самий знак —
# дві відповіді: ось чому Кнутові довелося переозначувати.
def fig_two_omegas():
    W, H = 880, 470
    p = []
    ox, oy = 92.0, 384.0
    pw, ph = 556.0, 300.0
    N = 12.0
    ymax = 120.0

    def X(n): return ox + pw * n / N
    def Y(v): return oy - ph * v / ymax

    def L(n):  return 40.0 + 4.0 * n            # планка C·g(n) — пряма, що росте
    def F(n):  return L(n) + 24.0 * math.sin(2.0 * math.pi * n / 3.0)

    # осі
    p.append(line(ox, oy, ox + pw + 8, oy, color=INK, sw=1.4))
    p.append(line(ox, oy, ox, oy - ph - 6, color=INK, sw=1.4))
    p.append(text(ox + pw / 2, oy + 38, "розмір входу  n  →", size=12.5, color=INK))
    p.append('<text transform="translate(%.1f,%.1f) rotate(-90)" font-family="%s" '
             'font-size="12.5" fill="%s" text-anchor="middle">%s</text>'
             % (ox - 54, oy - ph / 2, FONT, INK, esc("значення  f(n)  →")))

    # планка C·g(n)
    p.append(line(X(0), Y(L(0)), X(N), Y(L(N)), color=FIELD, sw=2.2, dash="7 5"))
    p.append(text(X(N) - 4, Y(L(N)) - 12, "планка  C·g(n)", size=12.5, color=FIELD,
                  bold=True, anchor="end"))

    # крива f(n)
    pts = []
    n = 0.0
    while n <= N + 1e-9:
        pts.append((X(n), Y(F(n))))
        n += 0.1
    poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (poly, INK))
    p.append(text(X(0.5), Y(F(0.5)) - 14, "f(n)", size=13, color=INK, bold=True, anchor="start"))

    # позначити один пік (над) і один провал (під)
    npk = 3.75   # sin = +1
    ntr = 5.25   # sin = −1
    p.append(circle(X(npk), Y(F(npk)), 4.2, fill=POS, stroke=BG, sw=1.6))
    p.append(text(X(npk), Y(F(npk)) - 12, "над планкою", size=12, color=POS, bold=True))
    p.append(circle(X(ntr), Y(F(ntr)), 4.2, fill=NEG, stroke=BG, sw=1.6))
    p.append(text(X(ntr), Y(F(ntr)) + 22, "під планкою", size=12, color=NEG, bold=True))

    # два присуди — панель праворуч
    b1, w1, h1 = textbox(748.0, 150.0,
                         "Гарді–Літлвуд\nнад планкою\nнескінченно часто\n✓  Ω — ТАК",
                         size=12.5, bold=True, fill="#eef7f0", stroke=FIELD, sw=1.6, min_w=196)
    p.append(b1)
    b2, w2, h2 = textbox(748.0, 300.0,
                         "Кнут\nне над планкою\nдля всіх великих n\n✗  Ω — НІ",
                         size=12.5, bold=True, fill="#fdecea", stroke=POS, sw=1.6, min_w=196)
    p.append(b2)

    render(os.path.join(OUT, "two-omegas.svg"), W, H, *p,
           title="Одна функція — дві Ω: чому Кнут переозначив знак")


if __name__ == "__main__":
    fig_growth_curves()
    fig_big_o_envelope()
    fig_doubling_response()
    fig_theta_sandwich()
    fig_limit_dial()
    fig_notation_timeline()
    fig_two_omegas()
    fig_doubling_decoder()
    fig_loglog_slope()
    fig_ratio_convergence()
    print("OK figs")
