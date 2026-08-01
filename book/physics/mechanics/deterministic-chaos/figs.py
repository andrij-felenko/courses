# -*- coding: utf-8 -*-
"""Фігури до статті «Детермінований хаос».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

C1 = INK          # перша траєкторія
C2 = POS          # друга траєкторія (майже той самий старт) — червона
GAP = NEG         # відстань між ними — синя


# ── Fig 1: чутливість до початкових умов (система Лоренца) ────────────────────
def fig_sensitive_dependence():
    sigma, rho, beta = 10.0, 28.0, 8.0 / 3.0

    def deriv(s):
        x, y, z = s
        return (sigma * (y - x), x * (rho - z) - y, x * y - beta * z)

    def rk4(s, h):
        k1 = deriv(s)
        k2 = deriv(tuple(s[i] + 0.5 * h * k1[i] for i in range(3)))
        k3 = deriv(tuple(s[i] + 0.5 * h * k2[i] for i in range(3)))
        k4 = deriv(tuple(s[i] + h * k3[i] for i in range(3)))
        return tuple(s[i] + h / 6.0 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(3))

    h, T = 0.005, 16.0
    # спершу вивести траєкторію на атрактор (відкинути перехідний процес),
    # аж тоді збурити старт — щоб розбіжність була експоненційною від t=0
    s = (1.0, 1.0, 1.0)
    for _ in range(4000):
        s = rk4(s, h)
    s1 = s
    s2 = (s[0] + 1e-3, s[1], s[2])
    n = int(T / h)
    ts, x1s, x2s, dist = [], [], [], []
    for i in range(n):
        s1 = rk4(s1, h)
        s2 = rk4(s2, h)
        t = i * h
        ts.append(t)
        x1s.append(s1[0]); x2s.append(s2[0])
        d = math.sqrt(sum((s1[k] - s2[k]) ** 2 for k in range(3)))
        dist.append(max(d, 1e-12))

    # момент зриву прогнозу: перше t, де відстань перевищує 4
    tdiv = ts[-1]
    for t, d in zip(ts, dist):
        if d > 4.0:
            tdiv = t
            break

    W, H = 800, 632
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Чутливість до початкових умов: два майже однакові старти", size=17, bold=True))

    PL, PW = 84, 636
    # верхня панель: координата x(t) обох копій
    PT, PH = 66, 214
    f.append(rect(PL, PT, PW, PH, fill="#fcfcfd", stroke="#e4e7eb", sw=1.2, rx=4))
    xmin, xmax = -21.0, 21.0

    def Tx(t):
        return PL + t / T * PW

    def Yx(x):
        return PT + PH - (x - xmin) / (xmax - xmin) * PH

    f.append(line(PL, Yx(0), PL + PW, Yx(0), color="#d7dbe0", sw=1.0))
    p1 = " ".join("%.1f,%.1f" % (Tx(t), Yx(x)) for t, x in zip(ts, x1s))
    p2 = " ".join("%.1f,%.1f" % (Tx(t), Yx(x)) for t, x in zip(ts, x2s))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" opacity="0.9"/>' % (p1, C1))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" opacity="0.85"/>' % (p2, C2))
    f.append(text(PL - 14, PT + 14, "x", size=14, italic=True, color=MUTED, anchor="end"))
    # маркер зриву
    f.append(line(Tx(tdiv), PT, Tx(tdiv), PT + PH, color=FIELD, sw=1.6, dash="5,5"))
    lb = textbox(Tx(tdiv), PT - 18, "тут прогноз ломиться", size=11, pad=6,
                 fill="#eafaf0", stroke=FIELD, sw=1.2, color="#1c7a43", bold=True)[0]
    f.append(lb)
    # легенда
    lx = PL + 16
    f.append(line(lx, PT + 20, lx + 26, PT + 20, color=C1, sw=2.4))
    f.append(text(lx + 32, PT + 24, "старт A", size=12, color=C1, anchor="start", bold=True))
    f.append(line(lx + 118, PT + 20, lx + 144, PT + 20, color=C2, sw=2.4))
    f.append(text(lx + 150, PT + 24, "старт A + 0.001", size=12, color=C2, anchor="start", bold=True))

    # нижня панель: відстань між копіями в лог-шкалі
    PT2, PH2 = 330, 150
    f.append(rect(PL, PT2, PW, PH2, fill="#fcfcfd", stroke="#e4e7eb", sw=1.2, rx=4))
    lo, hi = -3.3, 1.9   # log10 відстані

    def Yd(d):
        v = math.log10(d)
        v = max(lo, min(hi, v))
        return PT2 + PH2 - (v - lo) / (hi - lo) * PH2

    # горизонталь «розмір системи»
    f.append(line(PL, Yd(30), PL + PW, Yd(30), color=C2, sw=1.3, dash="6,5"))
    f.append(text(PL + PW - 8, Yd(30) - 8, "розмір системи", size=11, color=C2, anchor="end"))
    for gy in (-3, -2, -1, 0, 1):
        yy = PT2 + PH2 - (gy - lo) / (hi - lo) * PH2
        f.append(line(PL, yy, PL + 5, yy, color=MUTED, sw=1.0))
        f.append(text(PL - 9, yy + 4, "10%s" % _sup(gy), size=10.5, color=MUTED, anchor="end"))
    pd = " ".join("%.1f,%.1f" % (Tx(t), Yd(d)) for t, d in zip(ts, dist))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.8"/>' % (pd, GAP))
    f.append(line(Tx(tdiv), PT2, Tx(tdiv), PT2 + PH2, color=FIELD, sw=1.6, dash="5,5"))
    f.append(text(PL - 14, PT2 + PH2 / 2, "відстань", size=12, italic=True, color=MUTED, anchor="end"))
    f.append(text(PL + PW / 2, PT2 + PH2 + 26, "час  t  →", size=12.5, italic=True, color=MUTED))
    # пояснення нахилу (у порожньому верхньо-лівому куті, над кривою)
    f.append(text(Tx(0.7), PT2 + 24, "росте по прямій — множиться щокроку",
                  size=11.5, color=GAP, anchor="start"))

    cap = textbox(W / 2, 566,
                  "Згори — координата двох копій: криві злиті, аж поки за мить не розбігаються.\n"
                  "Знизу — відстань між ними (лог-шкала): вона росте прямою (експоненційно) від самого\n"
                  "початку й виходить на стелю, коли копії стають чужі. Зелена риска — межа прогнозу.",
                  size=11.5, pad=11, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(cap)
    return render(os.path.join(IMG, "sensitive-dependence.svg"), W, H, *f)


def _sup(n):
    m = {'-': '⁻', '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
         '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'}
    return "".join(m[c] for c in str(n))


# ── Fig 2: стіна прогнозу (стократ точніший старт → лише +Δt) ─────────────────
def fig_prediction_horizon():
    W, H = 780, 486
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 30, "Стіна прогнозу: у сто разів точніший старт купує лише сталу добавку часу", size=15.5, bold=True))

    PL, PT, PW, PH = 96, 58, 596, 300
    f.append(rect(PL, PT, PW, PH, fill="#fcfcfd", stroke="#e4e7eb", sw=1.2, rx=4))
    lam = 1.0
    tmax = 15.5
    lo, hi = -6.4, 0.7   # log10 похибки

    def Tx(t):
        return PL + t / tmax * PW

    def Yy(logv):
        logv = max(lo, min(hi, logv))
        return PT + PH - (logv - lo) / (hi - lo) * PH

    # стеля
    f.append(line(PL, Yy(0.0), PL + PW, Yy(0.0), color=C2, sw=2.0, dash="7,5"))
    f.append(text(PL + 10, Yy(0.0) - 9, "похибка = масштаб системи → прогноз даремний",
                  size=11.5, color=C2, anchor="start", bold=True))

    # осі-підписи по y
    for gy in (-6, -4, -2, 0):
        yy = Yy(gy)
        f.append(line(PL, yy, PL + 5, yy, color=MUTED, sw=1.0))
        f.append(text(PL - 10, yy + 4, "10%s" % _sup(gy), size=10.5, color=MUTED, anchor="end"))

    shades = ["#8aa0c8", "#3f63b0", "#12306e"]
    eps_log = [-2.0, -4.0, -6.0]
    labels = ["старт ε", "×100 точніший", "×10000 точніший"]
    tcross = []
    for k, e0 in enumerate(eps_log):
        # log10(err) = e0 + lam*t/ln10
        tc = (0.0 - e0) * math.log(10) / lam
        tcross.append(tc)
        pts = []
        tt = 0.0
        while tt <= tc + 1e-9:
            pts.append("%.1f,%.1f" % (Tx(tt), Yy(e0 + lam * tt / math.log(10))))
            tt += 0.1
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(pts), shades[k]))
        # позначка старту
        f.append(circle(Tx(0.0), Yy(e0), 3.2, fill=shades[k], stroke=shades[k], sw=1))
        f.append(text(Tx(0.0) + 8, Yy(e0) + 4, labels[k], size=11.5, color=shades[k], anchor="start", bold=True))
        # вертикаль до стелі
        f.append(line(Tx(tc), Yy(0.0), Tx(tc), PT + PH, color=shades[k], sw=1.2, dash="3,4"))

    # рівні проміжки Δt між перетинами
    ybr = PT + PH + 20
    for k in range(len(tcross) - 1):
        a, b = Tx(tcross[k]), Tx(tcross[k + 1])
        f.append(line(a, ybr, b, ybr, color=INK, sw=1.4))
        f.append(line(a, ybr - 4, a, ybr + 4, color=INK, sw=1.4))
        f.append(line(b, ybr - 4, b, ybr + 4, color=INK, sw=1.4))
        f.append(text((a + b) / 2, ybr + 16, "Δt", size=12, color=INK, bold=True))
    f.append(text(PL + PW / 2, PT + PH + 54, "час  t  →   (проміжки Δt однакові)", size=12, italic=True, color=MUTED))

    cap = textbox(W / 2, 448,
                  "Кожна лінія — розростання похибки від у сто разів точнішого старту, ніж сусідня "
                  "(шкала лог, тож\nекспонента — пряма). До стелі всі доходять через РІВНІ проміжки Δt: "
                  "тисячократна точність\nсунула стіну лише на два кроки Δt праворуч.",
                  size=11.5, pad=11, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(cap)
    return render(os.path.join(IMG, "prediction-horizon.svg"), W, H, *f)


# ── Fig 3: механізм «розтягнути й скласти» ───────────────────────────────────
def fig_stretch_and_fold():
    W, H = 890, 384

    def dot(cx, cy, col):
        # тачка-трасер із білим ореолом — видно на будь-якому тлі
        return circle(cx, cy, 5.4, fill=col, stroke="#ffffff", sw=2.0)

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 32, "Механізм хаосу: розтягнути й скласти (замішування тіста)", size=16.5, bold=True))

    side = 120
    ytop = 92
    cyc = ytop + side / 2

    def dashed_square(x0):
        return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="none" '
                'stroke="#b9c0c9" stroke-width="1.3" stroke-dasharray="5,5"/>' % (x0, ytop, side, side))

    # Крок 0 — вихідний клаптик, дві близькі точки
    x0 = 60
    f.append(rect(x0, ytop, side, side, fill="#eef4ff", stroke=NEG, sw=1.6, rx=4))
    f.append(dot(x0 + 52, cyc, C1))
    f.append(dot(x0 + 66, cyc, C2))
    f.append(text(x0 + side / 2, ytop + side + 26, "клаптик близьких", size=12, color=INK))
    f.append(text(x0 + side / 2, ytop + side + 42, "станів", size=12, color=INK))

    # стрілка «розтягнути»
    ax = x0 + side + 20
    f.append(arrow(ax, cyc, ax + 62, cyc, color=INK, sw=2.2))
    f.append(text(ax + 31, cyc - 14, "розтягнути", size=12.5, color=INK, bold=True))
    f.append(text(ax + 31, cyc + 26, "×2", size=12, color=MUTED))

    # Крок 1 — витягнута смуга (вдвічі довша, вдвічі тонша), вилазить за межі
    x1 = ax + 84
    f.append(dashed_square(x1))
    strip_w, strip_h = side * 2, side / 2
    sy = cyc - strip_h / 2
    f.append(rect(x1, sy, strip_w, strip_h, fill="#fdecea", stroke=C2, sw=1.6, rx=6))
    # точки роз'їхались по x
    f.append(dot(x1 + 104, cyc, C1))
    f.append(dot(x1 + 132, cyc, C2))
    f.append(text(x1 + strip_w / 2, ytop + side + 26, "смуга вийшла", size=12, color=INK))
    f.append(text(x1 + strip_w / 2, ytop + side + 42, "за межі області", size=12, color=INK))

    # стрілка «скласти»
    ax2 = x1 + strip_w + 22
    f.append(arrow(ax2, cyc, ax2 + 62, cyc, color=INK, sw=2.2))
    f.append(text(ax2 + 31, cyc - 14, "скласти", size=12.5, color=INK, bold=True))

    # Крок 2 — складена підкова назад в область, точки на різних плечах
    x2 = ax2 + 84
    f.append(dashed_square(x2))
    # підкова U: дві горизонтальні смуги, з'єднані дугою праворуч
    uw = side - 16
    uy1 = cyc - 26
    uy2 = cyc + 26
    lx = x2 + 10
    rx = x2 + 10 + uw
    path = ('<path d="M %.1f %.1f L %.1f %.1f Q %.1f %.1f %.1f %.1f L %.1f %.1f" '
            'fill="none" stroke="%s" stroke-width="12" stroke-linecap="round" '
            'stroke-linejoin="round" opacity="0.9"/>'
            % (lx, uy1, rx, uy1, rx + 30, cyc, rx, uy2, lx, uy2, C2))
    f.append(path)
    # дві точки на різних плечах — тепер далеко
    f.append(dot(lx + 34, uy1, C1))
    f.append(dot(lx + 34, uy2, C2))
    f.append(text(x2 + side / 2, ytop + side + 26, "згорнута назад —", size=12, color=INK))
    f.append(text(x2 + side / 2, ytop + side + 42, "точки вже далеко", size=12, color=INK))

    # петля «повторити»
    ax3 = x2 + side + 16
    f.append(text(ax3 + 10, cyc - 6, "…", size=22, color=MUTED, anchor="start", bold=True))
    f.append(text(ax3 + 10, cyc + 22, "повторити", size=11.5, color=MUTED, anchor="start"))

    return render(os.path.join(IMG, "stretch-and-fold.svg"), W, H, *f)


# ── Fig 4: як народжувалося поняття (до вставки hist-chaos-birth) ────────────
def fig_chaos_birth_timeline():
    rows = [
        ("1873", "Джеймс Клерк Максвелл",
         "нестійкі точки: приблизне знання старту вбиває передбачення", False),
        ("1889", "Анрі Пуанкаре",
         "ловить помилку у власній праці — і бачить плутанину траєкторій", False),
        ("1892", "Олександр Ляпунов, Харків",
         "показник, яким міряють швидкість розбігання", False),
        ("1898", "Жак Адамар",
         "перший чистий приклад: геодезичні на сідлоподібній поверхні", False),
        ("1945", "Мері Картрайт і Джон Літлвуд",
         "безлад у рівняннях радарних схем — не шум, а сам розв'язок", False),
        ("", "72 роки думка не ставала наукою",
         "порахувати довгу траєкторію просто не було на чому", True),
        ("1961", "Едвард Лоренц · Йосісуке Уеда",
         "машина крутить рівняння тисячі разів — розбіжність видно на око", False),
        ("1963", "«Deterministic Nonperiodic Flow»",
         "три рівняння Лоренца: у прогнозу погоди є горизонт", False),
        ("1964 · 1975", "Олександр Шарковський, Київ · Лі й Йорк",
         "порядок періодів; слово «хаос» входить у математику", False),
        ("1971–78", "Рюель і Такенс · Мей · Фейгенбаум",
         "«дивний атрактор», логістичне відображення, універсальність", False),
    ]

    NAME_S, DESC_S, YEAR_S = 13.5, 12.5, 13.0
    PAD = 13
    SPINE = 186
    BOX_L = 218
    STEP = 68
    TOP = 88

    W = 880
    H = TOP + STEP * len(rows) + 26

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 34, "Як народжувалося поняття детермінованого хаосу", size=17, bold=True))
    f.append(text(W / 2, 58, "думку висловлювали шість разів — наукою вона стала аж із машиною",
                  size=12.5, italic=True, color=MUTED))

    y_first = TOP + STEP / 2
    y_last = TOP + STEP * (len(rows) - 1) + STEP / 2
    f.append(line(SPINE, y_first - 18, SPINE, y_last + 18, color="#d7dbe0", sw=2.4))

    for i, (year, name, desc, accent) in enumerate(rows):
        cy = TOP + STEP * i + STEP / 2
        bw = max(text_width(name, NAME_S, True), text_width(desc, DESC_S)) + 2 * PAD
        bh = 50
        by = cy - bh / 2
        if accent:
            f.append(rect(BOX_L, by, bw, bh, fill="#fdecea", stroke=C2, sw=1.6, rx=6))
            f.append(circle(SPINE, cy, 6.0, fill=C2, stroke="#ffffff", sw=2.0))
            f.append(line(SPINE + 7, cy, BOX_L, cy, color=C2, sw=1.6, dash="4,4"))
            ncol, dcol = C2, "#8c4a42"
        else:
            f.append(rect(BOX_L, by, bw, bh, fill="#fcfcfd", stroke="#e4e7eb", sw=1.3, rx=6))
            f.append(circle(SPINE, cy, 5.4, fill=NEG, stroke="#ffffff", sw=2.0))
            f.append(line(SPINE + 7, cy, BOX_L, cy, color="#c9ced6", sw=1.4))
            ncol, dcol = INK, MUTED
        f.append(text(BOX_L + PAD, cy - 4, name, size=NAME_S, color=ncol, anchor="start", bold=True))
        f.append(text(BOX_L + PAD, cy + 15, desc, size=DESC_S, color=dcol, anchor="start"))
        if year:
            f.append(text(SPINE - 16, cy + 5, year, size=YEAR_S, color=MUTED, anchor="end", bold=True))

    return render(os.path.join(IMG, "chaos-birth-timeline.svg"), W, H, *f)


# ══ Фігури до вставки «Логістичне відображення» ══════════════════════════════

def _logi(r, x0, n):
    """Орбіта логістичного відображення: [x0, f(x0), …] довжиною n+1."""
    out = [x0]
    x = x0
    for _ in range(n):
        x = r * x * (1.0 - x)
        out.append(x)
    return out


# ── Fig L1: ручка r — те саме рівняння з трьома різними r ────────────────────
def fig_logistic_r_knob():
    W, H = 840, 352
    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 28, "Одне рівняння, три режими: усе вирішує ручка r", size=16.5, bold=True))

    NSTEP = 40
    panels = [
        (62,  2.8, "r = 2.8: одна точка",   INK),
        (322, 3.2, "r = 3.2: два значення", NEG),
        (582, 4.0, "r = 4.0: без повторів", POS),
    ]
    PW, PT, PH = 228, 74, 168

    for PL, r, head, col in panels:
        f.append(text(PL + PW / 2, 60, head, size=12.5, bold=True, color=col))
        f.append(rect(PL, PT, PW, PH, fill="#fcfcfd", stroke="#e4e7eb", sw=1.2, rx=4))

        def Tx(n, PL=PL):
            return PL + 8 + n / float(NSTEP) * (PW - 16)

        def Yy(v):
            return PT + PH - 8 - v * (PH - 16)

        orb = _logi(r, 0.4, NSTEP)
        pts = " ".join("%.1f,%.1f" % (Tx(n), Yy(v)) for n, v in enumerate(orb))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.2" opacity="0.55"/>'
                 % (pts, col))
        for n, v in enumerate(orb):
            f.append(circle(Tx(n), Yy(v), 2.4, fill=col, stroke=col, sw=0.8))

    # підписи осі y — лише в лівої панелі
    PL0 = panels[0][0]
    for v, lab in ((0.0, "0"), (1.0, "1")):
        yy = PT + PH - 8 - v * (PH - 16)
        f.append(line(PL0, yy, PL0 + 5, yy, color=MUTED, sw=1.0))
        f.append(text(PL0 - 10, yy + 4, lab, size=11, color=MUTED, anchor="end"))
    f.append(text(PL0 - 10, PT + PH / 2, "x", size=12, italic=True, color=MUTED, anchor="end"))

    f.append(text(W / 2, PT + PH + 26, "крок  n  →   (той самий старт x₀ = 0.4 в усіх трьох)",
                  size=12, italic=True, color=MUTED))

    cap = textbox(W / 2, 316,
                  "Ті самі два множення, лише інше r. До r = 3 популяція осідає в нерухому точку "
                  "1 − 1/r (тут 0.642857).\nЗа r = 3 точка втрачає стійкість, рух розпадається "
                  "надвоє, тоді начетверо; коли подвоєння вичерпуються\n(r ≈ 3.5699), повторення "
                  "зникає. r = 4 — край: парабола рівно накриває весь відрізок [0, 1].",
                  size=11.5, pad=11, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(cap)
    return render(os.path.join(IMG, "logistic-r-knob.svg"), W, H, *f)


# ── Fig L2: два старти, що різняться в дев'ятому знаку ────────────────────────
def fig_logistic_divergence():
    W, H = 820, 630
    NSTEP = 45
    a = _logi(4.0, 0.400000000, NSTEP)
    b = _logi(4.0, 0.400000001, NSTEP)
    d = [max(abs(a[i] - b[i]), 1e-12) for i in range(NSTEP + 1)]
    nbreak = next(i for i, v in enumerate(d) if v > 0.1)

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Різниця 10⁻⁹ на старті з'їдає всю систему за тридцять кроків",
                  size=16.5, bold=True))

    PL, PW = 82, 648

    def Tx(n):
        return PL + n / float(NSTEP) * PW

    # легенда над верхньою панеллю
    f.append(line(112, 52, 138, 52, color=C1, sw=2.6))
    f.append(text(144, 56, "старт A: x₀ = 0.400000000", size=11.5, color=C1, anchor="start", bold=True))
    f.append(line(452, 52, 478, 52, color=C2, sw=2.6))
    f.append(text(484, 56, "старт B: x₀ = 0.400000001", size=11.5, color=C2, anchor="start", bold=True))

    # верхня панель: обидві орбіти
    PT, PH = 66, 208
    f.append(rect(PL, PT, PW, PH, fill="#fcfcfd", stroke="#e4e7eb", sw=1.2, rx=4))

    def Yx(v):
        return PT + PH - 8 - v * (PH - 16)

    for orb, col in ((a, C1), (b, C2)):
        pts = " ".join("%.1f,%.1f" % (Tx(n), Yx(v)) for n, v in enumerate(orb))
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.3" opacity="0.75"/>'
                 % (pts, col))
        for n, v in enumerate(orb):
            f.append(circle(Tx(n), Yx(v), 2.3, fill=col, stroke=col, sw=0.8))
    for v, lab in ((0.0, "0"), (0.5, "0.5"), (1.0, "1")):
        yy = Yx(v)
        f.append(line(PL, yy, PL + 5, yy, color=MUTED, sw=1.0))
        f.append(text(PL - 10, yy + 4, lab, size=11, color=MUTED, anchor="end"))
    f.append(line(Tx(nbreak), PT, Tx(nbreak), PT + PH, color=FIELD, sw=1.6, dash="5,5"))
    f.append(text(Tx(nbreak) - 10, 292, "крок %d: копії вже чужі одна одній" % nbreak,
                  size=11.5, color="#1c7a43", anchor="end", bold=True))

    # нижня панель: |A − B| у лог-шкалі
    PT2, PH2 = 328, 186
    lo, hi = -9.6, 0.9
    f.append(rect(PL, PT2, PW, PH2, fill="#fcfcfd", stroke="#e4e7eb", sw=1.2, rx=4))

    def Yd(logv):
        logv = max(lo, min(hi, logv))
        return PT2 + PH2 - (logv - lo) / (hi - lo) * PH2

    # стеля: далі розходитися нікуди
    f.append(line(PL, Yd(0.0), PL + PW, Yd(0.0), color=C2, sw=1.4, dash="6,5"))
    f.append(text(PL + PW - 10, Yd(0.0) - 9, "уся система завширшки 1", size=11,
                  color=C2, anchor="end"))
    for gy in (-9, -6, -3, 0):
        yy = Yd(gy)
        f.append(line(PL, yy, PL + 5, yy, color=MUTED, sw=1.0))
        f.append(text(PL - 10, yy + 4, "10%s" % _sup(gy), size=11, color=MUTED, anchor="end"))
    # опорна пряма «×2 за крок»
    nref = 30.0
    f.append(line(Tx(0), Yd(-9.0), Tx(nref), Yd(-9.0 + nref * math.log10(2.0)),
                  color=MUTED, sw=1.4, dash="4,4"))
    pts = " ".join("%.1f,%.1f" % (Tx(n), Yd(math.log10(v))) for n, v in enumerate(d))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (pts, GAP))
    for n, v in enumerate(d):
        f.append(circle(Tx(n), Yd(math.log10(v)), 2.3, fill=GAP, stroke=GAP, sw=0.8))
    f.append(line(Tx(nbreak), PT2, Tx(nbreak), PT2 + PH2, color=FIELD, sw=1.6, dash="5,5"))
    f.append(text(Tx(13), PT2 + PH2 - 22, "сіра пряма — рівно ×2 за крок", size=11.5,
                  color=MUTED, anchor="start"))
    f.append(text(PL - 10, PT2 + PH2 / 2, "|A − B|", size=12, italic=True, color=MUTED, anchor="end"))
    f.append(text(PL + PW / 2, PT2 + PH2 + 26, "крок  n  →", size=12, italic=True, color=MUTED))

    cap = textbox(W / 2, 584,
                  "Угорі — обидві орбіти: майже тридцять кроків точки лягають одна на одну, "
                  "тоді розлітаються.\nВнизу — відстань між ними в лог-шкалі: вона йде вздовж сірої "
                  "прямої «×2 за крок» (окремі кроки\nстискають розрив, середнє — ні) і впирається "
                  "в стелю, бо далі розходитися просто нікуди.",
                  size=11.5, pad=11, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(cap)
    return render(os.path.join(IMG, "logistic-divergence.svg"), W, H, *f)


# ── Fig L3: закон читає двійковий запис старту, по біту за крок ───────────────
def fig_logistic_bitshift():
    W, H = 880, 440
    NB = 40

    def bits(x0):
        th = math.asin(math.sqrt(x0)) / math.pi
        out, v = [], th
        for _ in range(NB):
            v *= 2.0
            if v >= 1.0:
                out.append("1"); v -= 1.0
            else:
                out.append("0")
        return out

    bA, bB = bits(0.400000000), bits(0.400000001)
    same = next(i for i in range(NB) if bA[i] != bB[i])     # перший різний біт (0-базовий)

    f = [rect(0, 0, W, H, fill=BG, stroke='none', sw=0, rx=0)]
    f.append(text(W / 2, 26, "Чому саме тридцять: закон читає двійковий запис старту по біту за крок",
                  size=16.5, bold=True))

    # ланцюжок заміни змінної
    b1, w1, _ = textbox(146, 88, "xₙ₊₁ = 4·xₙ·(1 − xₙ)", size=13.5, pad=11)
    b2, w2, _ = textbox(438, 88, "θₙ₊₁ = 2·θₙ (mod 1)", size=13.5, pad=11)
    b3, w3, _ = textbox(742, 88, "зсув запису θ\nна біт ліворуч", size=13.5, pad=11)
    f += [b1, b2, b3]
    f.append(arrow(146 + w1 / 2 + 10, 88, 438 - w2 / 2 - 10, 88, color=LINE, sw=2.0))
    f.append(arrow(438 + w2 / 2 + 10, 88, 742 - w3 / 2 - 10, 88, color=LINE, sw=2.0))
    f.append(text((146 + w1 / 2 + 438 - w2 / 2) / 2, 60, "x = sin²(π·θ)", size=12, color=NEG, bold=True))
    f.append(text((438 + w2 / 2 + 742 - w3 / 2) / 2, 60, "×2 у двійковому", size=12, color=NEG, bold=True))

    # стрічка бітів
    X0, PITCH = 158, 17.0

    def bx(i):
        return X0 + i * PITCH

    yA, yB = 200, 232
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" fill="#eafaf0" '
             'stroke="%s" stroke-width="1.2"/>'
             % (bx(0) - 8.5, 180, same * PITCH, 74, FIELD))
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5" fill="#fdecea" '
             'stroke="%s" stroke-width="1.2"/>'
             % (bx(same) - 8.5, 180, (NB - same) * PITCH, 74, POS))
    f.append(text(bx(0) - 8.5 + same * PITCH / 2, 168,
                  "перші %d бітів однакові" % same, size=11.5, color="#1c7a43", bold=True))
    f.append(text(bx(same) - 8.5 + (NB - same) * PITCH / 2, 168,
                  "з %d-го — різні" % (same + 1), size=11.5, color=POS, bold=True))

    f.append(text(bx(0) - 20, yA + 4, "θ₀ старту A", size=12, color=C1, anchor="end", bold=True))
    f.append(text(bx(0) - 20, yB + 4, "θ₀ старту B", size=12, color=C2, anchor="end", bold=True))
    for i in range(NB):
        cA = C1 if i < same else "#8a1f14"
        cB = C2 if i < same else "#8a1f14"
        f.append(text(bx(i), yA + 4, bA[i], size=13, color=cA, bold=(i >= same)))
        f.append(text(bx(i), yB + 4, bB[i], size=13, color=cB, bold=(i >= same)))

    # головка, що читає стрічку
    for i, lab, anch, dx in ((0, "крок 0: головка тут", "start", -8),
                             (15, "крок 15", "middle", 0),
                             (same, "крок %d: головний біт уже інший" % same, "end", 8)):
        f.append(arrow(bx(i), 292, bx(i), 262, color=FIELD, sw=2.2))
        f.append(text(bx(i) + dx, 310, lab, size=11.5, color="#1c7a43", anchor=anch, bold=True))

    cap = textbox(W / 2, 378,
                  "Заміна x = sin²(π·θ) перетворює логістичне відображення на подвоєння числа θ, "
                  "а подвоєння\nу двійковому записі — це просто зсув: щокроку старший біт вилітає, "
                  "а на його місце виходить\nнаступний. Різниця 10⁻⁹ між стартами сидить аж у 31-му "
                  "біті — тож тридцять кроків обидві\nорбіти читають ту саму стрічку, цифра в цифру.",
                  size=11.5, pad=11, fill=FILL, stroke=LINE, sw=1.2)[0]
    f.append(cap)
    return render(os.path.join(IMG, "logistic-bitshift.svg"), W, H, *f)


if __name__ == "__main__":
    fig_sensitive_dependence()
    fig_prediction_horizon()
    fig_stretch_and_fold()
    fig_chaos_birth_timeline()
    fig_logistic_r_knob()
    fig_logistic_divergence()
    fig_logistic_bitshift()
    print("OK: фігури у", IMG)
