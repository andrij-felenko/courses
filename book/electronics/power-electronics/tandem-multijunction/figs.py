# -*- coding: utf-8 -*-
"""Фігури до теми «Багатоперехідні елементи та тандемна структура».
Фігури:
  spectrum-split.svg — сходинка «енергія фотона → скільки йде в струм»: один поріг (велика
                       термалізація) проти трьох порогів (термалізація стискається).
  stack.svg          — монолітний стос: верхній широкозонний, тунельні переходи, нижні; світло
                       різних кольорів гасне на різній глибині; струм один, напруги додаються.
  current-match.svg  — узгодження струмів: стос послідовний, тож струм = найслабший піделемент;
                       узгоджено (усе в діло) проти неузгоджено (надлишок марнується).
  ceiling.svg        — як росте стеля ККД із числом переходів: 1 → 2 → 3 → ∞.
  milestones.svg     — [hist] вертикальна стрічка віх: Джексон 1955 → Бедаїр 1979 →
                       Олсон/Курц 1988 → космос → рекорди NREL/ISE → перовскіт LONGi.
  record-climb.svg   — [hist] рекорди ККД за роками: III–V злетіли давно (концентратори,
                       47.6%), земні перовскіт-кремнієві тандеми щойно пробили стелю кремнію.
Запуск:  python figs.py   → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

HARV  = "#cdeed9"   # у струм (зібрано)
HARVE = "#2f9e63"
THERM = "#f6cba6"   # термалізація (тепло)
THERE = "#d98b4a"
TRANS = "#dfe3e8"   # пропускання (фотон надто слабкий)
TRANE = "#9aa3ad"
BLUEB = "#d7e3fa"   # синій діапазон / верхній елемент
BLUEE = "#3a5bbf"
GRNB  = "#d7f0dd"   # зелений діапазон / середній
GRNE  = "#2f9e63"
REDB  = "#fbdcd6"   # червоний/ІЧ / нижній
REDE  = "#c0392b"
TUN   = "#3a4048"   # тунельний перехід


def fillpoly(pts, fill, stroke="none", sw=0.0, op=1.0):
    d = "M" + " L".join("%.1f %.1f" % q for q in pts) + " Z"
    return ('<path d="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.1f"/>'
            % (d, fill, op, stroke, sw))


def polyline(pts, col, sw, dash=None):
    d = "M" + " L".join("%.1f %.1f" % q for q in pts)
    ex = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (d, col, sw, ex)


# ─────────────────────────────────────────────────────────────────────────────
def spectrum_split():
    W, H = 1000, 480
    p = []
    Emin, Emax, Ymax = 0.4, 3.4, 3.4

    def panel(ox, gaps, title, sub):
        pw, ph, oy = 350, 300, 396
        out = []

        def X(E):  return ox + pw * (E - Emin) / (Emax - Emin)
        def Y(en): return oy - ph * (en / Ymax)

        gaps = sorted(gaps, reverse=True)
        low = gaps[-1]

        # пропускання (сірий): уся енергія фотонів, слабших за найнижчий поріг
        out.append(fillpoly([(X(Emin), Y(0)), (X(low), Y(0)),
                             (X(low), Y(low)), (X(Emin), Y(Emin))], TRANS, op=1.0))

        # діапазони: зібране (зелений прямокутник) + термалізація (теплий трикутник)
        upper = Emax
        stair = [(X(Emax), Y(gaps[0]))]
        for g in gaps:
            out.append(rect(X(g), Y(g), X(upper) - X(g), Y(0) - Y(g),
                            fill=HARV, stroke="none", sw=0, rx=0))
            out.append(fillpoly([(X(g), Y(g)), (X(upper), Y(upper)),
                                 (X(upper), Y(g))], THERM, op=0.95))
            stair.append((X(g), Y(g)))
            stair.append((X(g), Y(gaps[gaps.index(g) + 1]) if g != low else Y(0)))
            upper = g
        stair.append((X(Emin), Y(0)))

        # діагональ «уся енергія фотона» + сходинка «у струм»
        out.append(line(X(Emin), Y(Emin), X(Emax), Y(Emax), color=INK, sw=1.6, dash="6 5"))
        out.append(polyline(stair, HARVE, 3.0))

        # осі
        out.append(line(X(Emin), Y(0), X(Emax), Y(0), color=INK, sw=1.6))
        out.append(line(X(Emin), Y(0), X(Emin), Y(Ymax), color=INK, sw=1.6))
        for E in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
            out.append(line(X(E), Y(0), X(E), Y(0) + 5, color=INK, sw=1.1))
            out.append(text(X(E), Y(0) + 20, "%.1f" % E, size=9.5, color=MUTED))
        out.append(text(ox + pw / 2, oy + 42, "енергія фотона, еВ", size=11.5, color=MUTED))

        # позначки порогів під віссю
        for g in gaps:
            out.append(line(X(g), Y(0), X(g), Y(0) - ph, color="#c2c7cf", sw=0.9, dash="2 4"))
        out.append(mtext(ox + pw / 2, 44, [title, sub], size=13.5, bold=True))

        return out, X, Y

    # ── лівий панель: один поріг ──
    L, XL, YL = panel(70, [1.1], "Один поріг (кремній)", "величезна термалізація")
    p += L
    # підписи областей (у вільних місцях)
    p.append(text(XL(2.55), YL(2.7), "уся енергія", size=11, color=INK, italic=True))
    p.append(text(XL(2.55), YL(2.48), "фотона", size=11, color=INK, italic=True))
    b, bw, bh = textbox(XL(2.35), YL(1.55), "на тепло\n(термалізація)", size=11,
                        color="#a35a1e", fill="#fdeede", stroke=THERE, pad=7)
    p.append(b)
    p.append(text(XL(2.15), YL(0.62), "у струм", size=11.5, color=HARVE, bold=True))
    b, bw, bh = textbox(XL(0.72), YL(2.05), "надто слабкі —\nпроходять намарно", size=10.5,
                        color="#5b636c", fill="#eef1f4", stroke=TRANE, pad=7)
    p.append(b)
    p.append(line(XL(0.75), YL(1.55), XL(0.78), YL(0.5), color=TRANE, sw=1, dash="3 3"))

    # ── правий панель: три пороги ──
    R, XR, YR = panel(580, [1.9, 1.2, 0.7], "Три пороги (тандем)", "термалізація стиснулась")
    p += R
    p.append(text(XR(2.62), YR(2.72), "уся енергія", size=11, color=INK, italic=True))
    p.append(text(XR(2.62), YR(2.5), "фотона", size=11, color=INK, italic=True))
    p.append(text(XR(1.35), YR(0.5), "у струм", size=11.5, color=HARVE, bold=True))
    b, bw, bh = textbox(XR(2.7), YR(1.35), "втрати на тепло\nтепер малі", size=10.5,
                        color="#a35a1e", fill="#fdeede", stroke=THERE, pad=7)
    p.append(b)

    render(os.path.join(OUT, 'spectrum-split.svg'), W, H, *p,
           title="Кілька порогів ловлять фотон ближче до його енергії — менше йде в тепло")


# ─────────────────────────────────────────────────────────────────────────────
def stack():
    W, H = 820, 500
    p = []
    cx, cw = 300, 240
    x0 = cx - cw / 2

    layers = [
        ("Верхній елемент", "широка зона  Eg₁ ≈ 1.9 еВ", "ловить синє", BLUEB, BLUEE, 82, 70),
        ("тунельний перехід", "", "", TUN, TUN, 158, 20),
        ("Середній елемент", "Eg₂ ≈ 1.4 еВ", "ловить зелене", GRNB, GRNE, 184, 70),
        ("тунельний перехід", "", "", TUN, TUN, 260, 20),
        ("Нижній елемент", "вузька зона  Eg₃ ≈ 0.7 еВ", "ловить червоне / ІЧ", REDB, REDE, 286, 70),
        ("підкладка", "", "", "#e7e2d6", "#b3a98c", 362, 40),
    ]

    for name, gap, catch, fill, edge, y, h in layers:
        thin = (h <= 20)
        p.append(rect(x0, y, cw, h, fill=fill, stroke=edge, sw=1.8, rx=(3 if thin else 7)))
        if thin:
            p.append(text(cx, y + h / 2 + 4, name, size=10.5, color="#e9ecef", bold=True))
        else:
            p.append(text(cx, y + 22, name, size=13, bold=True))
            if gap:
                p.append(text(cx, y + 42, gap, size=11, color="#3a4048"))
            if catch:
                p.append(text(cx, y + 60, catch, size=10.5, color=edge, italic=True))

    # світло згори — три кольори гаснуть на різній глибині
    # (стрічки-промені зсунуті ліворуч від центру, щоб не різати центровані підписи шарів;
    #  підпис і старт променів — нижче автозаголовка рисунка)
    sun_y = 58
    p.append(text(cx - 90, 46, "сонячне світло", size=12.5, bold=True, color="#8a6d00"))
    beams = [(-108, BLUEE, 116, "синє"), (-84, GRNE, 218, "зелене"), (-60, REDE, 320, "червоне")]
    for dx, col, stop, lbl in beams:
        xb = cx + dx
        p.append(line(xb, sun_y, xb, stop, color=col, sw=3.2))
        # наконечник-загасання
        p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f z" fill="%s"/>'
                 % (xb, stop, xb - 5, stop - 9, xb + 5, stop - 9, col))

    # права колонка: струм один, напруги додаються
    rx = cx + cw / 2 + 96
    p.append(line(x0 + cw, 117, rx, 117, color=INK, sw=1.6))
    p.append(line(x0 + cw, 219, rx, 219, color=INK, sw=1.6))
    p.append(line(x0 + cw, 321, rx, 321, color=INK, sw=1.6))
    p.append(line(rx, 117, rx, 321, color=INK, sw=2.4))
    # стрілка струму (один на весь стос)
    p.append(arrow(rx, 321, rx, 96, color=FIELD, sw=4))
    p.append(mtext(rx + 16, 205, ["той самий", "струм", "через увесь", "стос"],
                   size=11.5, color=FIELD, bold=True, anchor="start"))

    # напруги додаються — ліворуч
    lx = x0 - 40
    for (y, v, col) in [(117, "V₁", BLUEE), (219, "V₂", GRNE), (321, "V₃", REDE)]:
        p.append(text(lx, y + 4, v, size=13, bold=True, color=col, anchor="end"))
    b, bw, bh = textbox(lx - 4, 430, "V = V₁ + V₂ + V₃\nнапруги додаються", size=11.5,
                        color=INK, bold=True, fill="#eef7ff", stroke=BLUEE, pad=8)
    p.append(b)

    # клеми
    p.append(plus(rx, 88, r=8))
    p.append(minus(x0 - 40, 452, r=8))

    render(os.path.join(OUT, 'stack.svg'), W, H, *p,
           title="Монолітний тандем: пороги спадають згори вниз, з'єднані тунельними переходами")


# ─────────────────────────────────────────────────────────────────────────────
def current_match():
    W, H = 940, 470
    p = []

    def panel(ox, currents, title, ok):
        pw = 320
        oy, ph = 380, 250
        Imax = 22.0
        cols = [BLUEE, GRNE, REDE]
        labs = ["верхній", "середній", "нижній"]

        def Y(i): return oy - ph * (i / Imax)

        out = []
        # осі
        out.append(line(ox, oy, ox + pw, oy, color=INK, sw=1.6))
        out.append(line(ox, oy, ox, oy - ph, color=INK, sw=1.6))
        out.append(text(ox - 8, oy - ph - 8, "фотострум, мА/см²", size=11, color=MUTED, anchor="start"))
        for iv in (0, 5, 10, 15, 20):
            out.append(line(ox - 5, Y(iv), ox, Y(iv), color=INK, sw=1.1))
            out.append(text(ox - 9, Y(iv) + 4, str(iv), size=9.5, color=MUTED, anchor="end"))

        n = len(currents)
        bw = 56
        gap = (pw - n * bw) / (n + 1)
        Imin = min(currents)
        # лінія струму стосу = найменший
        out.append(line(ox, Y(Imin), ox + pw, Y(Imin), color=POS, sw=2.2, dash="7 5"))
        out.append(text(ox + pw - 4, Y(Imin) - 8, "струм стосу", size=10.5, color=POS,
                        bold=True, anchor="end"))

        for k, (I, col, lab) in enumerate(zip(currents, cols, labs)):
            bx = ox + gap + k * (bw + gap)
            # зібрана частина (до струму стосу)
            out.append(rect(bx, Y(Imin), bw, oy - Y(Imin), fill=HARV, stroke=col, sw=1.6, rx=3))
            # надлишок (змарновано) — заштрихована шапка
            if I > Imin + 0.05:
                out.append(rect(bx, Y(I), bw, Y(Imin) - Y(I), fill="#f2d0cb", stroke=col, sw=1.4, rx=3))
                out.append(text(bx + bw / 2, Y(I) - 6, "змарн.", size=9.5, color=POS, bold=True))
            out.append(text(bx + bw / 2, oy + 18, lab, size=10.5, color=col, bold=True))
            out.append(text(bx + bw / 2, oy + 33, "%.0f" % I, size=10, color=MUTED))

        out.append(mtext(ox + pw / 2, 46, [title], size=13.5, bold=True,
                         color=(FIELD if ok else POS)))
        return out

    p += panel(70, [15, 15, 15], "Узгоджено: усе йде в діло", True)
    p += panel(560, [15, 20, 17], "Неузгоджено: зайве марнується", False)

    render(os.path.join(OUT, 'current-match.svg'), W, H, *p,
           title="Стос послідовний: струм задає найслабший піделемент, решту зрізає")


# ─────────────────────────────────────────────────────────────────────────────
def ceiling():
    W, H = 820, 440
    p = []
    ox, oy, gw, gh = 96, 356, 620, 288
    Emax = 75.0

    def Y(e): return oy - gh * (e / Emax)

    p.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.8))
    p.append(text(ox - 8, oy - gh - 10, "стеля ККД, %", size=12, color=MUTED, anchor="start"))
    for e in (0, 20, 40, 60):
        p.append(line(ox - 5, Y(e), ox, Y(e), color=INK, sw=1.1))
        p.append(text(ox - 10, Y(e) + 4, str(e), size=10, color=MUTED, anchor="end"))

    bars = [("1 перехід", 33.7, "≈34%"), ("2 переходи", 42.0, "≈42%"),
            ("3 переходи", 49.0, "≈49%"), ("∞ переходів", 68.0, "≈68%")]
    n = len(bars)
    bw = 96
    gap = (gw - n * bw) / (n + 1)
    for k, (lab, val, tag) in enumerate(bars):
        bx = ox + gap + k * (bw + gap)
        col = [MUTED, GRNE, BLUEE, "#7d4bc0"][k]
        fll = ["#e7eaee", HARV, BLUEB, "#e7ddf5"][k]
        p.append(rect(bx, Y(val), bw, oy - Y(val), fill=fll, stroke=col, sw=1.8, rx=5))
        p.append(text(bx + bw / 2, Y(val) - 10, tag, size=13, bold=True, color=col))
        p.append(text(bx + bw / 2, oy + 20, lab, size=11.5, bold=True))

    # рекорд-лінія: 47.6% під концентрацією
    p.append(line(ox, Y(47.6), ox + gw, Y(47.6), color=POS, sw=1.8, dash="8 5"))
    b, bw2, bh2 = textbox(ox + gw - 118, Y(47.6) - 26, "рекорд ≈ 47.6%\n(4 переходи, концентр.)",
                          size=10.5, color=POS, bold=True, fill="#fdecea", stroke=POS, pad=7)
    p.append(b)

    p.append(text(ox + gw / 2, oy + 52, "один поріг проти багатьох (за одного сонця)",
                  size=11.5, color=MUTED))

    render(os.path.join(OUT, 'ceiling.svg'), W, H, *p,
           title="Що вище стос порогів, то вища стеля: від третини сонця до двох третин")


# ─────────────────────────────────────────────────────────────────────────────
def milestones():
    """[hist] Вертикальна стрічка ключових віх історії багатоперехідного елемента."""
    W, H = 812, 776
    p = []
    sx = 168                       # вертикальний хребет
    y0, step = 98, 74
    rows = [
        ("1955", "Джексон — ідея стосу порогів",
                 "стос елементів зі спадними зонами (конференція, Тусон)", MUTED),
        ("1960", "Вольф — теорія й перешкода",
                 "зустрічний p-n діод між елементами блокує струм", MUTED),
        ("1969", "Алфьоров і Кремер — гетероструктура",
                 "уможливлює тонкий якісний GaAs (Нобель, 2000)", NEG),
        ("1979", "Бедаїр — перший монолітний тандем",
                 "AlGaAs/GaAs; тунельний перехід знімає зустрічний діод", NEG),
        ("1988", "Олсон і Курц — GaInP/GaAs, 21.8%",
                 "MOCVD; широкозонний GaInP рятує верхній елемент", FIELD),
        ("~2000", "GaInP/GaAs/Ge — робочий кінь космосу",
                 "германій дарує «дармовий» третій перехід (Spectrolab)", "#7d4bc0"),
        ("2020", "NREL — 6 переходів, 47.1%",
                 "під концентрацією 143 сонця", POS),
        ("2022", "Fraunhofer ISE — 4 переходи, 47.6%",
                 "665 сонць — досі світовий рекорд ККД", POS),
        ("2026", "LONGi — перовскіт на кремнії, 35.5%",
                 "дешевий земний тандем пробиває стелю кремнію-одинака", FIELD),
    ]
    n = len(rows)
    p.append(line(sx, y0 - 20, sx, y0 + (n - 1) * step + 20, color="#c2c7cf", sw=2.6))
    bx, bw, bh = 204, 584, 58
    for i, (yr, l1, l2, col) in enumerate(rows):
        cy = y0 + i * step
        p.append(text(122, cy + 5, yr, size=15, bold=True, color=col, anchor="end"))
        p.append(line(sx + 8, cy, bx, cy, color=col, sw=1.6))
        p.append(circle(sx, cy, 8, fill=col, stroke=BG, sw=2.5))
        p.append(rect(bx, cy - bh / 2, bw, bh, fill=FILL, stroke=col, sw=1.7, rx=8))
        p.append(text(bx + 16, cy - 5, l1, size=13, bold=True, anchor="start"))
        p.append(text(bx + 16, cy + 16, l2, size=11, color=MUTED, anchor="start"))
    render(os.path.join(OUT, 'milestones.svg'), W, H, *p,
           title="Сімдесят років багатоперехідного елемента: від паперу до рекорду")


# ─────────────────────────────────────────────────────────────────────────────
def record_climb():
    """[hist] Рекорди ККД за роками: III–V-концентратори проти земних перовскіт-кремнієвих."""
    W, H = 884, 548
    p = []
    ox, oy = 92, 456
    gw, gh = 728, 376
    ytop = oy - gh
    yr0, yr1 = 1985, 2028
    emax = 52.0

    def X(yr): return ox + gw * (yr - yr0) / (yr1 - yr0)
    def Y(e):  return oy - gh * (e / emax)

    # осі й сітка
    p.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, ytop, color=INK, sw=1.8))
    p.append(text(ox - 6, ytop - 12, "ККД, %", size=12, color=MUTED, anchor="start"))
    for e in (0, 10, 20, 30, 40, 50):
        p.append(line(ox - 5, Y(e), ox, Y(e), color=INK, sw=1.1))
        p.append(text(ox - 10, Y(e) + 4, str(e), size=10, color=MUTED, anchor="end"))
    for yr in (1990, 2000, 2010, 2020):
        p.append(line(X(yr), oy, X(yr), oy + 5, color=INK, sw=1.1))
        p.append(text(X(yr), oy + 20, str(yr), size=10, color=MUTED))
    p.append(text(ox + gw / 2, oy + 40, "рік", size=11.5, color=MUTED))

    # стеля кремнію-одинака (лабораторний рекорд)
    p.append(line(ox, Y(26.6), ox + gw, Y(26.6), color=MUTED, sw=1.7, dash="7 5"))
    b, _, _ = textbox(ox + 158, Y(26.6) + 30, "кремній-одинак: лаб. рекорд ≈26.6% (2017)",
                      size=10, color="#4b5158", fill="#f0f2f5", stroke=MUTED, pad=6)
    p.append(b)

    # ── III–V-чемпіони (космос / концентратори) ──
    iiiv = [(1988, 21.8), (2006, 40.7), (2020, 47.1), (2022, 47.6)]
    p.append(polyline([(X(a), Y(b)) for a, b in iiiv], BLUEE, 2.6))
    for a, b in iiiv:
        p.append(circle(X(a), Y(b), 5.5, fill=BLUEB, stroke=BLUEE, sw=2.2))
    p.append(text(X(1988) + 9, Y(21.8) + 20, "1988 · 21.8% (2 перех.)",
                  size=10, color=BLUEE, anchor="start"))
    # підпис 2006 — праворуч-донизу від точки, осторонь висхідної лінії
    p.append(line(X(2006) + 14, Y(30) - 18, X(2006) + 5, Y(40.7) + 5, color=BLUEE, sw=1.0, dash="3 3"))
    b, _, _ = textbox(X(2009), Y(30), "2006 · 40.7%\nперший >40% (3 перех.)",
                      size=10, color=BLUEE, fill="#eaf0fd", stroke=BLUEE, pad=6)
    p.append(b)
    # кластер рекордів 2020/2022 — винесений підпис із тонкими поводками
    cb, cbw, _ = textbox(X(2004.5), Y(50.6),
                         "рекорди III–V:\n2020 · 47.1% (6 перех.)\n2022 · 47.6% (4 перех.)",
                         size=10, color=BLUEE, fill="#eaf0fd", stroke=BLUEE, pad=6)
    p.append(line(X(2004.5) + cbw / 2, Y(49.6), X(2020) - 6, Y(47.1), color=BLUEE, sw=1.0, dash="3 3"))
    p.append(line(X(2004.5) + cbw / 2, Y(51.6), X(2022) - 6, Y(47.6), color=BLUEE, sw=1.0, dash="3 3"))
    p.append(cb)

    # ── перовскіт на кремнії (земні тандеми) ──
    per = [(2023, 31.8), (2024, 34.6), (2025, 34.85), (2026, 35.5)]
    p.append(polyline([(X(a), Y(b)) for a, b in per], HARVE, 2.6))
    for a, b in per:
        p.append(circle(X(a), Y(b), 5.5, fill="#d7f0dd", stroke=HARVE, sw=2.2))
    # підпис під стелею кремнію, з поводком до останньої точки
    p.append(line(X(2025), Y(18.5) - 20, X(2026) - 4, Y(35.5) + 6, color=HARVE, sw=1.0, dash="3 3"))
    b, _, _ = textbox(X(2022.6), Y(18.5), "перовскіт на кремнії\n2026 · 35.5% — вище стелі Si",
                      size=10, color=HARVE, fill="#e7f6ec", stroke=FIELD, pad=6)
    p.append(b)

    render(os.path.join(OUT, 'record-climb.svg'), W, H, *p,
           title="Рекорди ККД: III–V злетіли давно, земні тандеми щойно пробили стелю кремнію")


# ─────────────────────────────────────────────────────────────────────────────
def sq_hump():
    """[math] Детально-балансова ефективність одного переходу η(Eg): горб із піком
    33.7% на 1.34 еВ; ліворуч термалізація, праворуч пропускання."""
    W, H = 820, 470
    p = []
    ox, oy = 96, 396
    gw, gh = 656, 316
    Emin, Emax, Nmax = 0.4, 3.2, 40.0

    def X(E): return ox + gw * (E - Emin) / (Emax - Emin)
    def Y(n): return oy - gh * (n / Nmax)

    # осі
    p.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.8))
    p.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.8))
    for n in (0, 10, 20, 30, 40):
        p.append(line(ox - 5, Y(n), ox, Y(n), color=INK, sw=1.1))
        p.append(text(ox - 10, Y(n) + 4, str(n), size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 30, oy - gh - 12, "стеля ККД, %", size=11.5, color=MUTED, anchor="start"))
    for E in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        p.append(line(X(E), oy, X(E), oy + 5, color=INK, sw=1.1))
        p.append(text(X(E), oy + 20, "%.1f" % E, size=10, color=MUTED))
    p.append(text(ox + gw / 2, oy + 42, "ширина забороненої зони Eg, еВ", size=11.5, color=MUTED))

    pts = [(0.4, 7), (0.6, 15), (0.8, 24), (1.0, 30), (1.1, 32), (1.2, 33),
           (1.34, 33.7), (1.45, 33.2), (1.6, 31.5), (1.75, 30), (1.9, 28),
           (2.1, 24.5), (2.3, 21), (2.5, 18), (2.7, 14.5), (2.9, 11.5), (3.1, 9)]
    poly = [(X(e), Y(v)) for e, v in pts]
    p.append(fillpoly(poly + [(X(3.1), Y(0)), (X(0.4), Y(0))], "#eef6f1", op=1.0))
    p.append(polyline(poly, HARVE, 3.2))

    # пік
    px, py = X(1.34), Y(33.7)
    p.append(line(px, oy, px, py, color=POS, sw=1.3, dash="4 4"))
    p.append(line(ox, py, px, py, color=POS, sw=1.3, dash="4 4"))
    p.append(circle(px, py, 5, fill=POS, stroke="#ffffff", sw=1.5))
    b, bw, bh = textbox(px + 96, py - 4, "пік 33.7%\nEg ≈ 1.34 еВ", size=12,
                        color=POS, bold=True, fill="#fdecea", stroke=POS, pad=8)
    p.append(b)

    # два режими втрат
    b, bw, bh = textbox(X(0.80), Y(10.5), "низький поріг:\nтермалізація", size=11,
                        color="#a35a1e", fill="#fdeede", stroke=THERE, pad=7)
    p.append(b)
    b, bw, bh = textbox(X(2.60), Y(28.5), "високий поріг:\nпропускання", size=11,
                        color="#5b636c", fill="#eef1f4", stroke=TRANE, pad=7)
    p.append(b)

    render(os.path.join(OUT, 'sq-hump.svg'), W, H, *p,
           title="Один перехід: детальний баланс дає горб із піком 33.7% на 1.34 еВ")


# ─────────────────────────────────────────────────────────────────────────────
def gap_partition():
    """[math] Узгодження струмів як розтин фотопотоку на рівнофотонні смуги; пороги
    рівних третин лягають на 0.70 / 1.18 / 1.81 еВ, напруги додаються."""
    W, H = 880, 470
    p = []
    ox, oy = 100, 388
    gw, gh = 700, 292
    Emin, Emax = 0.4, 3.4
    kT = 0.4998

    def phi(E): return E * E / (math.exp(E / kT) - 1.0)
    Ns = 260
    Es = [Emin + (Emax - Emin) * i / Ns for i in range(Ns + 1)]
    phis = [phi(E) for E in Es]
    pmax = max(phis)

    def X(E): return ox + gw * (E - Emin) / (Emax - Emin)
    def Y(v): return oy - gh * (v / pmax)

    Eg3, Eg2, Eg1 = 0.70, 1.18, 1.81

    def band(a, b, fill):
        inner = [(X(E), Y(v)) for E, v in zip(Es, phis) if a < E < b]
        pts = [(X(a), Y(0)), (X(a), Y(phi(a)))] + inner + [(X(b), Y(phi(b))), (X(b), Y(0))]
        return fillpoly(pts, fill, op=0.92)

    p.append(band(Emin, Eg3, TRANS))
    p.append(band(Eg3, Eg2, REDB))
    p.append(band(Eg2, Eg1, GRNB))
    p.append(band(Eg1, Emax, BLUEB))
    p.append(polyline([(X(E), Y(v)) for E, v in zip(Es, phis)], INK, 2.0))

    # пороги — пунктирні вертикалі + підписи вгорі
    for g, lab in [(Eg3, "Eg₃ ≈ 0.70"), (Eg2, "Eg₂ ≈ 1.18"), (Eg1, "Eg₁ ≈ 1.81")]:
        p.append(line(X(g), oy, X(g), Y(phi(g)), color=INK, sw=1.4, dash="5 4"))
        p.append(text(X(g), oy - gh - 8, lab, size=10.5, color=INK, bold=True))

    # осі
    p.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.8))
    for E in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
        p.append(line(X(E), oy, X(E), oy + 5, color=INK, sw=1.1))
        p.append(text(X(E), oy + 20, "%.1f" % E, size=10, color=MUTED))
    p.append(text(ox + gw / 2, oy + 42, "енергія фотона, еВ", size=11.5, color=MUTED))
    p.append(text(ox, oy - gh - 26, "фотопотік φ(E)", size=11, color=MUTED, anchor="start"))

    # підписи смуг (роль + напруга) — низько всередині смуги, під кривою
    for cx, lab, col in [(0.93, ["нижній", "V₃ ≈ 0.36 В"], REDE),
                         (1.48, ["середній", "V₂ ≈ 0.80 В"], GRNE),
                         (2.30, ["верхній", "V₁ ≈ 1.42 В"], BLUEE)]:
        p.append(mtext(X(cx), Y(0.11 * pmax), lab, size=10.5, color=col, bold=True))
    b, bw, bh = textbox(X(1.72), oy - gh + 34,
                        "кожна смуга — порівну фотонів  →  рівні струми Jsc ≈ 14.5 мА/см²",
                        size=11, color=INK, fill="#eef7ff", stroke=BLUEE, pad=7)
    p.append(b)

    render(os.path.join(OUT, 'gap-partition.svg'), W, H, *p,
           title="Узгодження струмів: рівнофотонні смуги задають пороги, напруги додаються")


# ─────────────────────────────────────────────────────────────────────────────
def thermo_walls():
    """[math] Вкладені термодинамічні стелі: 33.7 → 68 → 86 → 93.3 → 95, і яку
    ентропійну плату знімає кожна сходинка."""
    W, H = 900, 430
    p = []
    ox, oy = 250, 68
    barW = 430

    def X(pct): return ox + barW * pct / 100.0

    rows = [("1 перехід", 33.7, "термалізація + пропускання", MUTED, "#e7eaee"),
            ("∞ стос · 1 сонце", 68.0, "термалізацію знято", GRNE, HARV),
            ("∞ стос · макс. концентр.", 86.0, "ентропію розрідження знято", BLUEE, BLUEB),
            ("межа Ландсберга", 93.3, "оборотне, без нової ентропії", "#7d4bc0", "#e7ddf5"),
            ("межа Карно", 95.0, "1 − 300/6000", POS, "#fdecea")]
    rh, gp = 52, 15

    # шкала 0..100 згори
    for pct in (0, 20, 40, 60, 80, 100):
        p.append(line(X(pct), oy - 8, X(pct), oy - 3, color=MUTED, sw=1.0))
        p.append(text(X(pct), oy - 12, str(pct), size=9, color=MUTED))
    p.append(text(X(50), oy - 30, "гранична ефективність, %", size=11.5, color=MUTED))

    for k, (lab, val, note, col, fll) in enumerate(rows):
        y = oy + k * (rh + gp)
        p.append(rect(ox, y, barW, rh, fill="#f5f7f9", stroke="#e2e6ea", sw=1.0, rx=6))
        p.append(rect(ox, y, X(val) - ox, rh, fill=fll, stroke=col, sw=1.9, rx=6))
        p.append(text(ox - 12, y + rh / 2 + 5, lab, size=12, color=INK, anchor="end", bold=True))
        p.append(text(X(val) + 9, y + rh / 2 - 4, "%.1f%%" % val, size=13, color=col,
                      bold=True, anchor="start"))
        p.append(text(X(val) + 9, y + rh / 2 + 13, note, size=9.5, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'thermo-walls.svg'), W, H, *p,
           title="Термодинамічні стіни: від третини сонця до межі Ландсберга")


# ─────────────────────────────────────────────────────────────────────────────
# [proj] Дані спектра для фігур вставки proj-current-matching (той самий AM1.5G,
# що в коді): dJ/dE — доступний фотострум на еВ (мА·см⁻²·еВ⁻¹). Чистий Python.
_SE = [0.50, 0.70, 0.90, 1.10, 1.30, 1.45, 1.60, 1.75, 1.90, 2.10, 2.30, 2.60, 3.00, 3.50, 4.00]
_SD = [30,   31,   32,   36,   42,   40,   34,   29,   24,   19,   15,   10,   5.0,  2.2,  0.3]


def _dj(e):
    if e <= _SE[0] or e >= _SE[-1]:
        return 0.0
    for i in range(len(_SE) - 1):
        if _SE[i] <= e <= _SE[i + 1]:
            t = (e - _SE[i]) / (_SE[i + 1] - _SE[i])
            return _SD[i] * (1 - t) + _SD[i + 1] * t
    return 0.0


def _band(lo, hi, n=600):
    if hi <= lo:
        return 0.0
    s, step, prev = 0.0, (hi - lo) / n, _dj(lo)
    for k in range(1, n + 1):
        cur = _dj(lo + k * step)
        s += (prev + cur) * 0.5 * step
        prev = cur
    return s


def flux_bands():
    """[proj] Спектр як фотострум-на-еВ, розрізаний порогами GaInP/GaAs/Ge:
    площа кожної смуги = фотострум того піделемента; найменша задає струм стосу."""
    W, H = 960, 480
    ox, oy, gw, gh = 92, 402, 812, 322
    Emin, Emax, Ymax = 0.5, 3.5, 45.0
    p = []

    def X(e):  return ox + gw * (e - Emin) / (Emax - Emin)
    def Y(v):  return oy - gh * (v / Ymax)

    def curvepts(a, b, step=0.02):
        pts, e = [], a
        while e < b - 1e-9:
            pts.append((X(e), Y(_dj(e)))); e += step
        pts.append((X(b), Y(_dj(b))))
        return pts

    bands = [(0.50, 0.67, TRANS), (0.67, 1.42, REDB), (1.42, 1.85, GRNB), (1.85, 3.50, BLUEB)]
    for a, b, fill in bands:
        p.append(fillpoly([(X(a), Y(0))] + curvepts(a, b) + [(X(b), Y(0))], fill, op=1.0))
    p.append(polyline(curvepts(Emin, Emax), INK, 2.2))

    for g, lab in [(0.67, "0.67"), (1.42, "1.42"), (1.85, "1.85")]:
        p.append(line(X(g), Y(0), X(g), Y(0) - gh, color="#aab0b8", sw=1.1, dash="3 4"))
        p.append(text(X(g), oy + 18, lab, size=10.5, color=MUTED))

    p.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.7))
    p.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.7))
    for e in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5):
        p.append(line(X(e), oy, X(e), oy + 5, color=INK, sw=1.0))
        p.append(text(X(e), oy + 33, "%.1f" % e, size=9.5, color=MUTED))
    for v in (0, 10, 20, 30, 40):
        p.append(line(ox - 5, Y(v), ox, Y(v), color=INK, sw=1.0))
        p.append(text(ox - 9, Y(v) + 4, str(v), size=9.5, color=MUTED, anchor="end"))
    p.append(text(ox + gw / 2, oy + 52, "енергія фотона, еВ  (пороги піделементів пунктиром)",
                  size=11.5, color=MUTED))
    p.append(text(ox - 6, Y(Ymax) - 10, "dJ/dE, мА·см⁻²·еВ⁻¹  —  фотострум на одиницю енергії",
                  size=11, color=MUTED, anchor="start"))

    p.append(mtext(X(1.02), Y(6), ["нижній · Ge", "площа = 26.7 мА/см²"], size=12, color="#8f2d20", bold=True))
    p.append(mtext(X(2.35), Y(7), ["верхній · GaInP", "18.1 мА/см²"], size=12, color=BLUEE, bold=True))
    p.append(line(X(1.635), Y(_dj(1.635)), X(1.635), Y(41), color=GRNE, sw=1.0, dash="2 3"))
    p.append(mtext(X(1.635), Y(43.6), ["середній · GaAs", "14.2 — найменша"], size=12, color=GRNE, bold=True))
    b0, _, _ = textbox(X(2.95), Y(34),
                       "площа смуги = фотострум шару\nнайменша задає струм стосу,\nнадлишок решти йде в тепло",
                       size=11, color=INK, fill="#eef7ff", stroke=BLUEE, pad=9)
    p.append(b0)

    render(os.path.join(OUT, 'flux-bands.svg'), W, H, *p,
           title="Що рахує код: інтеграл спектра в кожній смузі = фотострум піделемента")


def match_sweep():
    """[proj] Двоперехідний стос на кремнієвому низі (1.11 еВ): розгортка верхнього
    порога. Струм стосу = min максимальний на перетині — це і є узгодження струмів."""
    W, H = 900, 480
    ox, oy, gw, gh = 92, 404, 764, 322
    Tmin, Tmax, Imax = 1.35, 2.05, 34.0
    BOT = 1.11
    p = []

    def X(t):  return ox + gw * (t - Tmin) / (Tmax - Tmin)
    def Y(v):  return oy - gh * (v / Imax)

    def curve(fn, step=0.01):
        pts, t = [], Tmin
        while t < Tmax - 1e-9:
            pts.append((X(t), Y(fn(t)))); t += step
        pts.append((X(Tmax), Y(fn(Tmax))))
        return pts

    jtop = lambda t: _band(t, 4.0)
    jbot = lambda t: _band(BOT, t)
    jmin = lambda t: min(jtop(t), jbot(t))

    p.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.7))
    p.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.7))
    for t in (1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0):
        p.append(line(X(t), oy, X(t), oy + 5, color=INK, sw=1.0))
        p.append(text(X(t), oy + 20, "%.1f" % t, size=9.5, color=MUTED))
    for v in (0, 5, 10, 15, 20, 25, 30):
        p.append(line(ox - 5, Y(v), ox, Y(v), color=INK, sw=1.0))
        p.append(text(ox - 9, Y(v) + 4, str(v), size=9.5, color=MUTED, anchor="end"))
    p.append(text(ox + gw / 2, oy + 40, "поріг верхнього піделемента, еВ  (низ фіксовано ≈ Si, 1.11 еВ)",
                  size=11.5, color=MUTED))
    p.append(text(ox - 6, Y(Imax) - 10, "фотострум, мА/см²", size=11, color=MUTED, anchor="start"))

    p.append(fillpoly([(X(Tmin), Y(0))] + curve(jmin) + [(X(Tmax), Y(0))], HARV, op=0.65))
    p.append(polyline(curve(jtop), BLUEE, 2.6))
    p.append(polyline(curve(jbot), REDE, 2.6))
    p.append(polyline(curve(jmin), HARVE, 3.4))

    tc = 1.70
    p.append(line(X(tc), Y(0), X(tc), Y(28), color=FIELD, sw=1.4, dash="6 5"))
    p.append(circle(X(tc), Y(jmin(tc)), 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    p.append(text(X(1.44), Y(31), "верхній  Jₜ ↓", size=12.5, color=BLUEE, bold=True, anchor="start"))
    p.append(text(X(1.92), Y(30.5), "нижній  J_б ↑", size=12.5, color=REDE, bold=True, anchor="end"))
    p.append(text(X(1.52), Y(15.5), "струм стосу = min", size=12, color=HARVE, bold=True, anchor="start"))
    b0, _, _ = textbox(X(1.70), Y(31.6), "узгодження струмів:\nтут струм стосу max —\nі потужність теж max",
                       size=11, color=INK, fill="#eafaf0", stroke=FIELD, pad=8)
    p.append(b0)
    b1, _, _ = textbox(X(1.905), Y(7), "верх ≈ 1.70 еВ на кремнієвому низі —\nсаме рецепт «перовскіт на кремнії»",
                       size=10.5, color=INK, fill="#fff6e9", stroke=THERE, pad=8)
    p.append(b1)

    render(os.path.join(OUT, 'match-sweep.svg'), W, H, *p,
           title="Чому є оптимум: струм стосу (min) максимальний на перетині — це узгодження")


if __name__ == '__main__':
    spectrum_split()
    stack()
    current_match()
    ceiling()
    milestones()
    record_climb()
    sq_hump()
    gap_partition()
    thermo_walls()
    flux_bands()
    match_sweep()
    print("OK:", os.listdir(OUT))
