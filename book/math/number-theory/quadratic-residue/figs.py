# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

P = 11
QR = sorted(set((x * x) % P for x in range(1, P)))          # {1,3,4,5,9}
NR = [a for a in range(1, P) if a not in QR]                 # {2,6,7,8,10}


# ── folding: піднесення до квадрата складає лишки навпіл ─────────────────────
# Ідея: кожен квадрат приходить з пари x і 11−x, тож десять лишків сходяться
# в п'ять квадратів (зелені), а решта п'ять (сірі) не досяжні жодного разу.
def fig_folding():
    W, H = 760, 610
    p = []
    XL, XR = 235, 545
    CW, CH = 56, 30
    Y0, DY = 118, 46

    p.append(text(XL, 88, "лишок  x", size=13, color=MUTED))
    p.append(text(XR, 88, "x² mod 11", size=13, color=MUTED))

    def cell(cx, y, v, live, strong=False):
        col = FIELD if live else "#c2c7ce"
        fill = "#eafaf0" if live else BG
        p.append(rect(cx - CW / 2, y - CH / 2, CW, CH, fill=fill,
                      stroke=col, sw=1.8 if strong else 1.3))
        p.append(text(cx, y + 5, v, size=15, bold=live,
                      color=INK if live else "#aeb4bc"))

    # ліва колонка — усі ненульові лишки
    for i in range(1, P):
        cell(XL, Y0 + (i - 1) * DY, i, True)
    # права колонка — можливі значення квадрата: зелені досяжні, сірі ні
    for i in range(1, P):
        cell(XR, Y0 + (i - 1) * DY, i, i in QR, strong=True)
    # стрілки: x → x² mod 11 (сходяться попарно в зелені клітини)
    for i in range(1, P):
        y1 = Y0 + (i - 1) * DY
        y2 = Y0 + ((i * i) % P - 1) * DY
        p.append(arrow(XL + CW / 2 + 4, y1, XR - CW / 2 - 5, y2, color=FIELD, sw=1.3))

    p.append(text(W / 2, 578, "п'ять зелених квадратів, кожен по дві стрілки — "
                              "п'ять сірих нелишків без жодної", size=13,
                  color=MUTED, italic=True))
    render(os.path.join(OUT, "folding.svg"), W, H, *p,
           title="Піднесення до квадрата складає лишки навпіл")


# ── euler-criterion: той самий поділ, здобутий одним степенем ────────────────
# Ідея: a^5 mod 11 дорівнює +1 рівно для квадратів і −1 (тобто 10) рівно для
# нелишків — весь перебір квадратів заміняє одне піднесення до (p−1)/2.
def fig_euler():
    W, H = 1040, 380
    p = []
    X0, DX = 96, 94
    half = (P - 1) // 2

    p.append(text(W / 2, 62, "a⁵ mod 11  —  один степінь замість перебору квадратів",
                  size=14, color=MUTED))

    for k, a in enumerate(range(1, P)):
        cx = X0 + k * DX
        live = a in QR
        col = FIELD if live else NEG
        soft = "#eafaf0" if live else "#eaf0fd"
        # число a
        p.append(rect(cx - 30, 96, 60, 34, fill=soft, stroke=col, sw=1.8))
        p.append(text(cx, 119, a, size=17, bold=True, color=col))
        # a^5 mod 11
        val = pow(a, half, P)
        p.append(text(cx, 176, "a⁵ ≡ %d" % val, size=13, color=INK))
        # символ ±1
        p.append(rect(cx - 26, 200, 52, 30, fill=soft, stroke=col, sw=1.6))
        p.append(text(cx, 221, "+1" if live else "−1", size=15, bold=True, color=col))

    p.append(text(150, 285, "зелені: a⁵ ≡ 1  →  квадрати {1, 3, 4, 5, 9}",
                  size=13.5, color=FIELD, anchor="start", bold=True))
    p.append(text(150, 312, "сині:   a⁵ ≡ 10 ≡ −1  →  нелишки {2, 6, 7, 8, 10}",
                  size=13.5, color=NEG, anchor="start", bold=True))
    p.append(text(W / 2, 350, "поділ той самий, що дало складання лишків навпіл — "
                              "лише дістаний інакше", size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "euler-criterion.svg"), W, H, *p,
           title="Критерій Ейлера: символ Лежандра як степінь")


# ── sign-structure: лишки множаться точно як знаки ──────────────────────────
# Ідея: таблиця «лишок/нелишок» буква в букву збігається з таблицею знаків,
# тож квадрат грає роль +1, нелишок — −1, і символ Лежандра лише це й записує.
def fig_sign():
    W, H = 980, 470
    p = []

    p.append(fitbox(70, 66, 400, 50,
                    "квадрати: 1, 3, 4, 5, 9   —   роль  +1",
                    size=15, fill="#eafaf0", stroke=FIELD, sw=2.2, bold=True, color=FIELD))
    p.append(fitbox(510, 66, 400, 50,
                    "нелишки: 2, 6, 7, 8, 10   —   роль  −1",
                    size=15, fill="#eaf0fd", stroke=NEG, sw=2.2, bold=True, color=NEG))

    # дві таблиці 2×2, що збігаються візерунком
    def table(x0, y0, hdr, rows, cw=118, ch=44):
        # hdr: (кут, кол1, кол2); rows: [(мітка, e1, e2), ...] з кольорами
        def box(cx, cy, w, h, s, fill, stroke, col, bold=True, size=14):
            p.append(rect(cx, cy, w, h, fill=fill, stroke=stroke, sw=1.4))
            p.append(fitbox(cx, cy, w, h, s, size=size, fill=fill, stroke=stroke,
                            color=col, bold=bold))
        box(x0, y0, cw, ch, hdr[0], FILL, LINE, MUTED)
        box(x0 + cw, y0, cw, ch, hdr[1], "#eafaf0", FIELD, FIELD)
        box(x0 + 2 * cw, y0, cw, ch, hdr[2], "#eaf0fd", NEG, NEG)
        for r, (lab, labcol, e1, e2) in enumerate(rows):
            yy = y0 + (r + 1) * ch
            softlab = "#eafaf0" if labcol == FIELD else "#eaf0fd"
            box(x0, yy, cw, ch, lab, softlab, labcol, labcol)
            for c, (val, vcol) in enumerate(((e1), (e2))):
                soft = "#eafaf0" if vcol == FIELD else "#eaf0fd"
                box(x0 + (c + 1) * cw, yy, cw, ch, val, soft, vcol, vcol)

    table(150, 190,
          ("·", "лишок", "нелишок"),
          [("лишок", FIELD, ("лишок", FIELD), ("нелишок", NEG)),
           ("нелишок", NEG, ("нелишок", NEG), ("лишок", FIELD))])
    p.append(text(490, 258, "≡", size=30, color=MUTED))
    table(560, 190,
          ("·", "+", "−"),
          [("+", FIELD, ("+", FIELD), ("−", NEG)),
           ("−", NEG, ("−", NEG), ("+", FIELD))])

    b, _, _ = textbox(W / 2, 430,
                      "3·4 ≡ 1  (лишок)      3·2 ≡ 6  (нелишок)      2·6 ≡ 1  (лишок)",
                      size=13.5, pad=11, fill="#fbfbfc")
    p.append(b)
    render(os.path.join(OUT, "sign-structure.svg"), W, H, *p,
           title="Лишки перемножуються точно як знаки")


# ── reciprocity-ladder: (30|53) стискається до одного знака ──────────────────
# Ідея: три дії — винести двійку, перевернути за законом взаємності, звести за
# модулем — тануть число, як алгоритм Евкліда, аж до −1 (30 — нелишок).
def fig_reciprocity():
    W, H = 1000, 470
    p = []
    XL, LW = 60, 470          # ліва колонка: рівняння
    XR = 560                  # права колонка: яка дія
    Y0, DY = 96, 68

    rows = [
        ("(30|53) = (2|53) · (15|53)", "винесли двійку:  30 = 2·15", INK, FILL, LINE),
        ("(2|53) = −1",               "бо 53 ≡ 5 (mod 8)", NEG, "#eaf0fd", NEG),
        ("(15|53) = (53|15) = (8|15)", "переворот (53 ≡ 1 mod 4)  +  звели 53 mod 15 = 8",
         INK, FILL, LINE),
        ("(8|15) = (2|15)³ = +1",     "бо 15 ≡ 7 (mod 8),  тож (2|15) = +1", FIELD,
         "#eafaf0", FIELD),
        ("(30|53) = (−1)·(+1) = −1",  "30 — нелишок:  x² ≡ 30 (mod 53) без розв'язку",
         NEG, "#eaf0fd", NEG),
    ]
    for i, (eq, note, col, fill, stroke) in enumerate(rows):
        y = Y0 + i * DY
        strong = (i == len(rows) - 1)
        p.append(fitbox(XL, y, LW, 48, eq, size=15, fill=fill, stroke=stroke,
                        sw=2.2 if strong else 1.6, color=col, bold=True))
        p.append(text(XR, y + 30, note, size=13, color=MUTED, anchor="start"))
        if i < len(rows) - 1:
            p.append(arrow(XL + LW / 2, y + 48 + 2, XL + LW / 2, y + DY - 2,
                           color="#cfd4da", sw=1.6))

    p.append(text(W / 2, 448, "кілька ділень із остачею, як у пошуку НСД — "
                              "і жодного піднесення до великого степеня",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "reciprocity-ladder.svg"), W, H, *p,
           title="Обчислення символу (30|53) переворотами й зведенням")


# ── gauss-lemma: символ Лежандра як парність перескоків за p/2 ───────────────
# Ідея: кратні 3·k за модулем 11 дають лишки 3,6,9,1,4; двоє (6,9) перескочили
# за половину — їх згортають у 5 і 2. Згорнуті величини заповнюють 1…5 (пере-
# становка), а кількість перескоків μ=2 дає (3|11)=(−1)²=+1.
def fig_gauss_lemma():
    W, H = 900, 450
    a, Pp = 3, 11
    x0, span = 90, 720
    def X(v): return x0 + span * v / Pp
    yA, yB = 155, 330
    p = []
    p.append(text(W / 2, 58, "Лема Гаусса на прикладі  a = 3,  p = 11",
                  size=15, color=MUTED))

    # смуга «верхня половина» + дільник p/2
    p.append(rect(X(5.5), yA - 70, X(Pp) - X(5.5), 150, fill="#eef3fd",
                  stroke="none", rx=0))
    p.append(line(X(5.5), yA - 72, X(5.5), yB + 30, color=NEG, sw=1.4, dash="5 5"))
    p.append(text(X(5.5), yA - 80, "p/2 = 5.5", size=12, color=NEG))
    p.append(text(X(8.25), yA - 52, "верхня половина", size=11.5, color=NEG))

    # осі: повна 0…11 (лишки) і згорнута 0…5.5 (величини t)
    p.append(line(X(0), yA, X(Pp), yA, color=LINE, sw=1.6))
    p.append(line(X(0), yB, X(5.5), yB, color=LINE, sw=1.6))
    marked = {3, 6, 9, 1, 4}   # ці колонки вже мають кружечок + стрілку вниз —
                                # не дублюємо число тут, бо стрілка пройде крізь напис
    for v in range(0, Pp + 1):
        p.append(line(X(v), yA - 4, X(v), yA + 4, color=LINE, sw=1.1))
        if v not in marked:
            p.append(text(X(v), yA + 20, v, size=11, color=MUTED))
    for v in range(1, 6):
        p.append(text(X(v), yB + 22, v, size=12.5, color=INK, bold=True))

    for k, r in [(1, 3), (2, 6), (3, 9), (4, 1), (5, 4)]:
        t = min(r, Pp - r)
        folded = r > Pp / 2
        col = NEG if folded else FIELD
        soft = "#eaf0fd" if folded else "#eafaf0"
        p.append(circle(X(r), yA, 10, fill=soft, stroke=col, sw=2))
        p.append(text(X(r), yA - 20, "3·%d" % k, size=12, color=col, bold=True))
        p.append(arrow(X(r), yA + 12, X(t), yB - 12, color=col, sw=1.4))
        p.append(circle(X(t), yB, 10, fill=soft, stroke=col, sw=2))

    p.append(text(X(2.75), yB + 52, "згорнуті величини = {1, 2, 3, 4, 5} — "
                  "переставлені 1…(p−1)/2", size=12.5, color=MUTED, italic=True))
    b, _, _ = textbox(W / 2, 418, "перескочили двоє (6→5, 9→2):   μ = 2   →   "
                      "(3|11) = (−1)² = +1", size=14, pad=11,
                      fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True)
    p.append(b)
    render(os.path.join(OUT, "gauss-lemma.svg"), W, H, *p,
           title="Лема Гаусса: рахунок перескоків через половину модуля")


# ── eisenstein-lattice: закон взаємності як рахунок цілих точок ──────────────
# Ідея: прямокутник (p−1)/2 × (q−1)/2 цілих точок, розрізаний діагоналлю
# 11y=7x. Жодна точка не на лінії; нижче — N=Σ⌊qk/p⌋, вище — M=Σ⌊pj/q⌋, разом PQ.
def fig_eisenstein_lattice():
    W, H = 940, 475
    pp, qq = 11, 7
    Pn, Qn = (pp - 1) // 2, (qq - 1) // 2          # 5, 3
    OX, OY, GX, GY = 140, 330, 118, 82
    def SX(mx): return OX + GX * mx
    def SY(my): return OY - GY * my
    p = []
    p.append(text(W / 2, 60, "Ґратка Айзенштайна:  p = 11,  q = 7", size=15, color=MUTED))

    xtop = Qn * pp / qq                            # діагональ виходить крізь верх
    below = "%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        SX(0), SY(0), SX(Pn), SY(0), SX(Pn), SY(Qn), SX(xtop), SY(Qn))
    above = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        SX(0), SY(0), SX(xtop), SY(Qn), SX(0), SY(Qn))
    p.append('<polygon points="%s" fill="#eafaf0" stroke="none"/>' % below)
    p.append('<polygon points="%s" fill="#eaf0fd" stroke="none"/>' % above)

    p.append(line(SX(0), SY(0), SX(Pn + 0.45), SY(0), color=LINE, sw=1.6))
    p.append(line(SX(0), SY(0), SX(0), SY(Qn + 0.55), color=LINE, sw=1.6))
    for k in range(1, Pn + 1):
        p.append(text(SX(k), SY(0) + 22, k, size=12, color=MUTED))
    for j in range(1, Qn + 1):
        p.append(text(SX(0) - 18, SY(j) + 4, j, size=12, color=MUTED))

    xend = Pn + 0.35
    p.append(line(SX(0), SY(0), SX(xend), SY(qq * xend / pp), color=NEG, sw=2, dash="6 5"))
    p.append(text(SX(xend) + 6, SY(qq * xend / pp) - 4, "11y = 7x", size=12, color=NEG))

    for k in range(1, Pn + 1):
        for j in range(1, Qn + 1):
            bel = j < qq * k / pp
            col = FIELD if bel else NEG
            soft = "#d7f2e1" if bel else "#dbe6fb"
            p.append(circle(SX(k), SY(j), 9, fill=soft, stroke=col, sw=2))

    p.append(text(SX(Pn / 2.0), SY(0) + 44,
                  "ґратка  (p−1)/2 × (q−1)/2  =  5 × 3  =  15 точок",
                  size=12.5, color=INK))
    p.append(text(150, 407, "нижче (стовпці):  N = Σ⌊7k/11⌋ = 7    ⇒    "
                  "(7|11) = (−1)⁷ = −1", size=13, color=FIELD, anchor="start", bold=True))
    p.append(text(150, 433, "вище (рядки):     M = Σ⌊11j/7⌋ = 8    ⇒    "
                  "(11|7) = (−1)⁸ = +1", size=13, color=NEG, anchor="start", bold=True))
    p.append(text(150, 459, "N + M = 15    ⇒    (7|11)(11|7) = (−1)¹⁵ = −1",
                  size=13, color=MUTED, anchor="start", italic=True))
    render(os.path.join(OUT, "eisenstein-lattice.svg"), W, H, *p,
           title="Закон взаємності як рахунок точок під діагоналлю")


# ── golden-theorem-timeline: народження закону взаємності (для вставки hist) ──
# Ідея: закон СПЕРШУ побачили в таблицях (Ейлер), потім назвали й недодовели
# (Лежандр), і аж Гаусс зробив його неминучим — а тоді повертався ще й ще.
# Вертикальна лінія часу з паузою-провалом «пів століття без доведення».
def fig_timeline():
    W, H = 920, 700
    p = []
    AX = 250                    # вісь часу (кружечки)
    x_year = 224                # рік — ліворуч від осі, вирівняно до осі
    x_desc = 286                # опис — праворуч
    desc_w = 598

    p.append(line(AX, 96, AX, 640, color="#cfd4da", sw=2))

    rows = [
        (128, "≈1740–83", FIELD, "#eafaf0",
         ["Ейлер (Швейцарія): закон вичитано з таблиць лишків.",
          "Довести не зумів; повний виклад надруковано 1783, посмертно."], False),
        (214, "1785", NEG, "#eaf0fd",
         ["Лежандр (Франція): перше формулювання й назва «закон взаємності».",
          "Доведення з дірою — спиралось на недоведене твердження",
          "про прості в прогресіях. Символ (a|p) — у трактаті 1798."], False),
        (344, "1796", POS, "#fdecea",
         ["Гаусс (Німеччина), 18 років: ПЕРШЕ ПОВНЕ доведення.",
          "Роком раніше, 1795, за власним свідченням відкрив закон",
          "із таблиць — не знаючи ні Ейлера, ні Лежандра."], True),
        (440, "1801", POS, "#fdecea",
         ["«Арифметичні дослідження» (Disquisitiones Arithmeticae):",
          "закон надруковано. Гаусс зве його theorema fundamentale,",
          "а приватно — theorema aureum, «золота теорема»."], False),
        (524, "1801–32", POS, "#fdecea",
         ["Вісім доведень: шість за життя, ще два — у паперах.",
          "Щоразу новим методом: Гаусс шукав той, що узагальниться."], False),
        (608, "1837", MUTED, "#eef0f2",
         ["Діріхле доводить теорему про прості в прогресіях —",
          "ту саму, що бракувала Лежандрові. Діру закрито через 52 роки."], False),
    ]
    for (y, yr, col, soft, lines, emph) in rows:
        p.append(text(x_year, y + 5, yr, size=14, color=col, anchor="end", bold=True))
        h = 20 + len(lines) * 20
        p.append(fitbox(x_desc, y - h / 2, desc_w, h, "\n".join(lines),
                        size=13.5, fill=soft, stroke=col,
                        sw=2.4 if emph else 1.5, color=INK))
        if emph:
            p.append(circle(AX, y, 13, fill="#fdecea", stroke="none", sw=0))
        p.append(circle(AX, y, 7 if emph else 5.5, fill=col, stroke=BG, sw=2))

    # провал між Лежандром (1785) і Гауссом (1796): десятиліття без доведення
    # (лінія розірвана на дві частини, щоб не пролягати крізь напис у рамці)
    p.append(line(AX, 256, AX, 272, color="#cfd4da", sw=2, dash="3 6"))
    p.append(line(AX, 288, AX, 302, color="#cfd4da", sw=2, dash="3 6"))
    b, _, _ = textbox(AX, 279, "пів століття: бачать, а довести не можуть",
                      size=12.5, pad=8, fill="#fbf7e6", stroke="#d8cf9a",
                      color="#7a6f36")
    p.append(b)

    render(os.path.join(OUT, "golden-theorem-timeline.svg"), W, H, *p,
           title="Народження золотої теореми: пів століття від таблиць до доведення")


# ── jacobi-trap: +1 за складеним модулем не доводить квадрат ─────────────────
# Ідея: оборотні лишки за модулем 15 = 3·5, розкладені за поведінкою окремо за
# mod 3 і mod 5. Символ Якобі — добуток двох знаків: діагональ (однакові знаки)
# дає +1, антидіагональ −1. Та лише «лишок·лишок» — справжні квадрати; клітина
# «нелишок·нелишок» носить той самий +1, не бувши квадратом.
def fig_jacobi_trap():
    from math import gcd
    W, H = 940, 612
    p3, p5, N = 3, 5, 15

    def leg(v, pr):
        r = pow(v % pr, (pr - 1) // 2, pr)
        return -1 if r == pr - 1 else r

    G = {}
    for a in (u for u in range(1, N) if gcd(u, N) == 1):
        G.setdefault((leg(a, p3), leg(a, p5)), []).append(a)

    p = []
    HX, HW = 40, 150
    CX, CW = [200, 566], 340
    HY, HH = 62, 64
    RY, RH = [140, 350], 196

    p.append(fitbox(HX, HY, HW, HH, "(a|15) =\n(a|3)·(a|5)", size=13,
                    fill=FILL, stroke=LINE, color=MUTED, bold=True))
    p.append(fitbox(CX[0], HY, CW, HH, "лишок за mod 3     (a|3) = +1",
                    size=15, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(CX[1], HY, CW, HH, "нелишок за mod 3     (a|3) = −1",
                    size=15, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))
    p.append(fitbox(HX, RY[0], HW, RH, "лишок\nза mod 5\n(a|5) = +1",
                    size=14, fill="#eafaf0", stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(HX, RY[1], HW, RH, "нелишок\nза mod 5\n(a|5) = −1",
                    size=14, fill="#eaf0fd", stroke=NEG, color=NEG, bold=True))

    def cell(cx, cy, s3, s5):
        us = ",  ".join(map(str, G[(s3, s5)]))
        if s3 == 1 and s5 == 1:
            fill, acc, sign, verdict = "#eafaf0", FIELD, "(+1)·(+1) = +1", "справжній квадрат"
        elif s3 == -1 and s5 == -1:
            fill, acc, sign, verdict = "#fdecea", POS, "(−1)·(−1) = +1", "НЕ квадрат — символ бреше"
        else:
            g1, g2 = ("+1" if s3 == 1 else "−1"), ("+1" if s5 == 1 else "−1")
            fill, acc, sign, verdict = "#eaf0fd", NEG, "(%s)·(%s) = −1" % (g1, g2), "нелишок — символ чесний"
        p.append(rect(cx, cy, CW, RH, fill=fill, stroke=acc, sw=2.2))
        p.append(text(cx + CW / 2, cy + 66, us, size=34, bold=True, color=INK))
        p.append(text(cx + CW / 2, cy + 116, sign, size=18, bold=True, color=acc))
        p.append(text(cx + CW / 2, cy + 156, verdict, size=15, italic=True, color=acc))

    cell(CX[0], RY[0], +1, +1)   # {1,4}   зелений — справжні квадрати
    cell(CX[1], RY[0], -1, +1)   # {11,14} синій   — чесний −1
    cell(CX[0], RY[1], +1, -1)   # {7,13}  синій   — чесний −1
    cell(CX[1], RY[1], -1, -1)   # {2,8}   червоний — оманливий +1

    cap = ("Символ +1 стоїть на діагоналі — там, де знаки однакові: (+)(+) і (−)(−).\n"
           "Та лише «лишок·лишок» — квадрати; «нелишок·нелишок» носить той самий +1 дарма.")
    p.append(mtext(W / 2, 560, cap, size=13.5, color=MUTED, lh=1.35))

    render(os.path.join(OUT, "jacobi-trap.svg"), W, H, *p,
           title="+1 за складеним модулем не доводить, що число — квадрат")


# ── sqrt-branches: дві дороги до кореня за модулем p ─────────────────────────
# Ідея (для вставки proj-modular-sqrt): коли p ≡ 3 (mod 4), корінь дається одним
# піднесенням x = a^((p+1)/4), бо a^((p+1)/2) = a^((p−1)/2)·a = 1·a = a. Коли ж
# p ≡ 1 (mod 4), цей показник не цілий — і працює алгоритм Тонеллі — Шенкса.
def fig_branches():
    W, H = 1000, 500
    p = []
    b, _, _ = textbox(W / 2, 72, "дано просте p і лишок a  —  знайти x:  x² ≡ a (mod p)",
                      size=15, pad=12, fill=FILL, bold=True)
    p.append(b)
    p.append(line(W / 2, 118, W / 2, 452, color="#d8dce2", sw=1.4, dash="5 5"))

    # ── ліворуч: p ≡ 3 (mod 4) — одна формула ──
    p.append(fitbox(70, 132, 360, 40, "p ≡ 3 (mod 4)   —   одна формула",
                    size=15, fill="#eafaf0", stroke=FIELD, sw=2, color=FIELD, bold=True))
    p.append(fitbox(120, 190, 260, 48, "x = a^((p+1)/4)",
                    size=18, fill="#eafaf0", stroke=FIELD, sw=1.8, color=INK, bold=True))
    deriv = ["x² = a^((p+1)/2)",
             "     = a^((p−1)/2) · a",
             "     = 1 · a = a"]
    for i, ln in enumerate(deriv):
        p.append(text(96, 288 + i * 30, ln, size=14.5, color=INK, anchor="start"))
    p.append(text(96, 288 + 3 * 30 + 4, "бо a — лишок:  a^((p−1)/2) ≡ 1",
                  size=12.5, color=MUTED, anchor="start", italic=True))
    p.append(text(96, 288 + 4 * 30 + 8, "→ одне піднесення до степеня",
                  size=13.5, color=FIELD, anchor="start", bold=True))

    # ── праворуч: p ≡ 1 (mod 4) — треба працювати ──
    p.append(fitbox(560, 132, 380, 40, "p ≡ 1 (mod 4)   —   треба працювати",
                    size=15, fill="#eaf0fd", stroke=NEG, sw=2, color=NEG, bold=True))
    lines = ["(p+1)/4 — не ціле число",
             "p − 1 = Q · 2ˢ,   Q непарне",
             "t = a^Q  живе у 2-степеневій вежі",
             "гасити t до 1, збираючи корінь R"]
    for i, ln in enumerate(lines):
        p.append(text(584, 200 + i * 38, ln, size=14, color=INK, anchor="start"))
    p.append(fitbox(584, 200 + 4 * 38 - 2, 340, 42, "алгоритм Тонеллі — Шенкса",
                    size=15, fill="#eaf0fd", stroke=NEG, sw=1.8, color=NEG, bold=True))

    p.append(text(W / 2, 484, "увесь клопіт — лише у 2-степеневій частині p−1; "
                              "непарна частина кореня не помічає",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "sqrt-branches.svg"), W, H, *p,
           title="Квадратний корінь за модулем: дві дороги за остачею p mod 4")


# ── sqrt-cascade: Тонеллі — Шенкс гасить 2-степінь t сходинками ───────────────
# Ідея: t = a^Q лежить у циклічній 2-вежі порядку 2ˢ; кожна ітерація збиває
# порядок t удвічі (сходинка вниз), домножуючи корінь R, аж поки t = 1 і R² = a.
# Наскрізний приклад a = 5, p = 41 (p−1 = 5·2³): порядок t іде 4 → 2 → 1.
def fig_cascade():
    a, P = 5, 41
    Q, S = P - 1, 0
    while Q % 2 == 0:
        Q //= 2; S += 1
    z = 2
    while pow(z, (P - 1) // 2, P) != P - 1:
        z += 1
    # зібрати сходинки: (порядок t, t, R, b-домноження, що привело сюди)
    M, c, t, R = S, pow(z, Q, P), pow(a, Q, P), pow(a, (Q + 1) // 2, P)

    def ord2(v):
        o, x = 1, v
        while x != 1:
            x = (x * x) % P; o *= 2
        return o
    shelves = [(ord2(t), t, R, None)]
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = (tt * tt) % P; i += 1
        b = pow(c, 1 << (M - i - 1), P)
        M = i; c = (b * b) % P; t = (t * c) % P; R = (R * b) % P
        shelves.append((ord2(t) if t != 1 else 1, t, R, b))

    W, H = 1020, 560
    p = []
    p.append(text(W / 2, 56, "Тонеллі — Шенкс:  a = 5,  p = 41   "
                             "(p − 1 = 5·2³,  нелишок-затравка z = 3)",
                  size=15, color=MUTED))
    p.append(text(W / 2, 86, "старт:  t = a^Q = 5⁵ ≡ 9,   R = a^((Q+1)/2) = 5³ ≡ 2",
                  size=13.5, color=INK))

    AX = 150
    rowY = [170, 310, 450]
    tickL = ["2² = 4", "2¹ = 2", "2⁰ = 1"]
    p.append(line(AX, 138, AX, 486, color="#cfd4da", sw=2))
    p.append(text(AX, 118, "порядок t", size=12.5, color=MUTED))

    PW = 760
    for k, (order, tv, Rv, b) in enumerate(shelves):
        y = rowY[k]
        last = (k == len(shelves) - 1)
        col = FIELD if last else NEG
        soft = "#eafaf0" if last else "#eaf0fd"
        p.append(text(AX - 14, y + 5, tickL[k], size=13.5, color=col,
                      anchor="end", bold=True))
        p.append(circle(AX, y, 6, fill=col, stroke=BG, sw=2))
        p.append(rect(190, y - 37, PW, 74, fill=soft, stroke=col, sw=2.2))
        inv = "R² ≡ a·t :  %d² ≡ %d  =  5·%d" % (Rv, (Rv * Rv) % P, tv)
        p.append(text(214, y - 8, "t = %d" % tv, size=17, color=INK,
                      anchor="start", bold=True))
        p.append(text(214, y + 20, "R = %d" % Rv, size=17, color=col,
                      anchor="start", bold=True))
        p.append(text(470, y + 6, inv, size=14, color=MUTED, anchor="start"))
        if last:
            p.append(text(470, y - 14, "t = 1   ⟹   R² = a   ⟹   корінь x = %d" % Rv,
                          size=14.5, color=FIELD, anchor="start", bold=True))

    for k in range(len(shelves) - 1):
        y1, y2 = rowY[k] + 37, rowY[k + 1] - 37
        b = shelves[k + 1][3]
        p.append(arrow(AX, y1 + 2, AX, y2 - 2, color="#9aa1ab", sw=1.8))
        lab = "×b² на t,  ×b на R    (b = %d)" % b
        bx, _, _ = textbox((190 + 190 + PW) / 2, (y1 + y2) / 2, lab,
                           size=12.5, pad=8, fill="#fbfbfc", stroke="#dfe3e8",
                           color=MUTED)
        p.append(bx)

    p.append(text(W / 2, 528, "кожна сходинка вдвічі меншає порядок t; "
                              "за S кроків t доходить до 1, а R — до кореня (другий корінь = −R = %d)"
                  % (P - shelves[-1][2]),
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "sqrt-cascade.svg"), W, H, *p,
           title="Тонеллі — Шенкс: гасіння 2-степеня t сходинками до кореня")


fig_folding()
fig_euler()
fig_sign()
fig_reciprocity()
fig_gauss_lemma()
fig_eisenstein_lattice()
fig_timeline()
fig_jacobi_trap()
fig_branches()
fig_cascade()
print("ok:", sorted(os.listdir(OUT)))
