# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_F  = "#e8eefc"
RED_F   = "#fdecea"
GREEN_F = "#e6f7ee"
QUAD_F  = "#eef4ff"


# ── lattice-line: цілий розв'язок = вузол сітки на прямій ─────────────────────
# Ідея: рівняння a·x + b·y = c — пряма; цілий розв'язок — точка, де вона
# простромлює вузол сітки. Дві паралельні прямі: одна нанизує вузли, друга
# з тим самим нахилом ковзає між ними, бо c не кратне НСД.
def fig_lattice_line():
    W, H = 1060, 600
    p = []
    cell = 50
    ox, oy = 130, 430
    xmin, xmax, ymin, ymax = -1, 7, -1, 5

    def Px(x): return ox + x * cell
    def Py(y): return oy - y * cell

    p.append(text(300, 42, "Цілий розв'язок — це вузол сітки, що лежить на прямій",
                  size=16, color=INK, bold=True))

    for xi in range(xmin, xmax + 1):
        for yi in range(ymin, ymax + 1):
            p.append(circle(Px(xi), Py(yi), 2.4, fill=MUTED, stroke=MUTED, sw=0))

    p.append(line(Px(xmin) - 10, Py(0), Px(xmax) + 12, Py(0), color=MUTED, sw=1.3))
    p.append(line(Px(0), Py(ymax) - 12, Px(0), Py(ymin) + 12, color=MUTED, sw=1.3))
    p.append(text(Px(xmax) + 22, Py(0) + 5, "x", size=13, color=MUTED, italic=True))
    p.append(text(Px(0) - 6, Py(ymax) - 20, "y", size=13, color=MUTED, italic=True))

    # line 1: 2x + 3y = 12 — нанизує вузли
    p.append(line(Px(-1), Py(14 / 3), Px(7), Py(-2 / 3), color=FIELD, sw=2.6))
    for nx, ny in [(0, 4), (3, 2), (6, 0)]:
        p.append(circle(Px(nx), Py(ny), 8, fill=GREEN_F, stroke=FIELD, sw=2.6))
    p.append(text(Px(0) - 34, Py(4) - 8, "(0, 4)", size=12.5, color=FIELD, bold=True))
    p.append(text(Px(3) + 38, Py(2) - 8, "(3, 2)", size=12.5, color=FIELD, bold=True))
    p.append(text(Px(6) + 38, Py(0) - 8, "(6, 0)", size=12.5, color=FIELD, bold=True))
    p.append(text(Px(-1) + 6, Py(14 / 3) - 18, "2x + 3y = 12", size=13.5,
                  color=FIELD, bold=True, anchor="start"))

    # line 2: 4x + 6y = 9  (=2x+3y=4.5) — той самий нахил, ковзає між вузлами
    p.append(line(Px(-1), Py(6.5 / 3), Px(4.5), Py(-1.5), color=POS, sw=2.2, dash="7,5"))
    for mx in [0, 1, 2, 3]:
        my = (4.5 - 2 * mx) / 3.0
        p.append(circle(Px(mx), Py(my), 4.5, fill=BG, stroke=POS, sw=1.8))
    p.append(text(Px(4.75), Py(-0.55), "4x + 6y = 9", size=13.5,
                  color=POS, bold=True, anchor="start"))

    # праворуч — розбір
    xR = 600
    p.append(text(xR, 108, "Чи проходить пряма через вузол?", size=15.5,
                  color=INK, anchor="start", bold=True))
    p.append(mtext(xR, 146, ["Зелена  2x + 3y = 12  нанизує вузли",
                             "(0, 4), (3, 2), (6, 0) — рівним кроком (3, −2)."],
                   size=13.5, color=FIELD, anchor="start", lh=1.5))
    p.append(mtext(xR, 210, ["Червона  4x + 6y = 9  має ТОЙ САМИЙ нахил,",
                             "але зсунута: 4x + 6y завжди парне, а 9 —",
                             "непарне, тож вона ковзає між рядами вузлів."],
                   size=13.5, color=POS, anchor="start", lh=1.5))
    p.append(fitbox(xR, 300, 410, 64, "Цілі розв'язки є  ⟺  НСД(a, b) ділить c",
                    size=17, fill=GREEN_F, stroke=FIELD, sw=2.4, bold=True, color=INK))
    p.append(mtext(xR, 410, ["Для 2, 3: НСД = 1 ділить 12 → вузли є.",
                             "Для 4, 6: НСД = 2 не ділить 9 → жодного."],
                   size=13, color=MUTED, anchor="start", lh=1.55))

    return render(os.path.join(OUT, "lattice-line.svg"), W, H, *p)


# ── general-solution: один розв'язок → уся родина ────────────────────────────
# Ідея: різниця двох розв'язків задовольняє a·Δx + b·Δy = 0; найдрібніший
# такий цілий крок — (b/d, −a/d). Додаючи його з параметром t, дістаємо ВСІ
# розв'язки. Праворуч — родина для 5x + 8y = 43, крок (8, −5).
def fig_general_solution():
    W, H = 1080, 530
    p = []

    # ЛІВА панель — схема нульового кроку
    p.append(text(70, 58, "Один розв'язок породжує всю родину", size=15.5,
                  color=INK, anchor="start", bold=True))

    p.append(line(120, 432, 500, 160, color=INK, sw=1.6))
    A, B, C = (200, 375), (340, 275), (480, 175)
    for pt in (A, B, C):
        p.append(circle(pt[0], pt[1], 7, fill=GREEN_F, stroke=FIELD, sw=2.4))

    for (sx, sy), (ex, ey) in ((A, B), (B, C)):
        dx, dy = ex - sx, ey - sy
        L = math.hypot(dx, dy)
        k = 13 / L
        p.append(arrow(sx + dx * k, sy + dy * k, ex - dx * k, ey - dy * k, color=NEG, sw=2.2))

    p.append(text(150, 250, "крок  (b/d, −a/d)", size=13.5, color=NEG, anchor="start", bold=True))
    p.append(text(A[0] - 78, A[1] + 6, "(x₁, y₁)", size=12.5, color=FIELD, anchor="start", bold=True))
    p.append(text(C[0] + 14, C[1] + 4, "…", size=15, color=FIELD, anchor="start", bold=True))

    p.append(fitbox(70, 452, 470, 52,
                    "різниця двох розв'язків:  a·Δx + b·Δy = 0",
                    size=15, fill=FILL, stroke=NEG, sw=1.8))

    # ПРАВА панель — таблиця родини 5x + 8y = 43
    xT = 640
    p.append(text(xT, 58, "Родина розв'язків  5x + 8y = 43", size=15.5,
                  color=INK, anchor="start", bold=True))
    p.append(text(xT, 84, "x = −129 + 8t        y = 86 − 5t", size=13,
                  color=MUTED, anchor="start"))

    cols = [("t", xT + 30), ("x", xT + 150), ("y", xT + 260)]
    for h, cx in cols:
        p.append(text(cx, 124, h, size=13.5, color=MUTED, bold=True))
    p.append(line(xT, 134, xT + 320, 134, color=MUTED, sw=1.2))

    rows = [("15", "−9", "11"), ("16", "−1", "6"), ("17", "7", "1"),
            ("18", "15", "−4"), ("19", "23", "−9")]
    y = 164
    for tt, xx, yy in rows:
        hit = (tt == "17")
        if hit:
            p.append(rect(xT, y - 20, 320, 31, fill=GREEN_F, stroke=FIELD, sw=1.6, rx=4))
        for (h, cx), val in zip(cols, (tt, xx, yy)):
            p.append(text(cx, y, val, size=13.5, color=(FIELD if hit else INK), bold=hit))
        y += 37

    p.append(text(xT, y + 14, "сусідні рядки різняться на (8, −5) = (b, −a)",
                  size=12.5, color=MUTED, anchor="start"))
    p.append(text(xT, y + 38, "єдиний невід'ємний розв'язок — (7, 1) при t = 17",
                  size=12.5, color=FIELD, anchor="start", bold=True))

    return render(os.path.join(OUT, "general-solution.svg"), W, H, *p)


# ── nonneg-window: невід'ємність → скінченний відрізок прямої ────────────────
# Ідея: цілих розв'язків нескінченно багато вздовж усієї прямої, але умова
# x, y ≥ 0 лишає тільки відрізок у першому квадранті. Скільки вузлів на ньому —
# стільки й розв'язків: тут один проти двох.
def fig_nonneg_window():
    W, H = 1080, 590
    p = []
    p.append(text(W / 2, 40, "Невід'ємність відрізає від прямої скінченний відрізок",
                  size=16, color=INK, bold=True))

    def panel(ox, title, line_ends, hit_nodes, out_nodes):
        out = []
        cell = 40
        oy = 452
        xmin, xmax, ymin, ymax = -1, 9, -1, 6

        def Px(x): return ox + x * cell
        def Py(y): return oy - y * cell

        out.append(text(ox + 4 * cell, 84, title, size=14.5, color=INK, bold=True))
        # затінений перший квадрант
        out.append(rect(Px(0), Py(ymax), cell * xmax, cell * ymax,
                        fill=QUAD_F, stroke="none", sw=0, rx=0))
        for xi in range(xmin, xmax + 1):
            for yi in range(ymin, ymax + 1):
                out.append(circle(Px(xi), Py(yi), 2.2, fill=MUTED, stroke=MUTED, sw=0))
        out.append(line(Px(xmin) - 6, Py(0), Px(xmax) + 8, Py(0), color=MUTED, sw=1.2))
        out.append(line(Px(0), Py(ymax) + 8, Px(0), Py(ymin) + 6, color=MUTED, sw=1.2))
        out.append(text(Px(xmax) + 16, Py(0) + 5, "x", size=12, color=MUTED, italic=True))
        out.append(text(Px(0) - 6, Py(ymax) - 4, "y", size=12, color=MUTED, italic=True))

        (xa, ya), (xb, yb) = line_ends
        out.append(line(Px(xa), Py(ya), Px(xb), Py(yb), color=NEG, sw=2.4))

        for nx, ny in out_nodes:
            out.append(circle(Px(nx), Py(ny), 5, fill=BG, stroke=MUTED, sw=1.6))
        for nx, ny in hit_nodes:
            out.append(circle(Px(nx), Py(ny), 8, fill=GREEN_F, stroke=FIELD, sw=2.6))
            out.append(text(Px(nx) + 14, Py(ny) - 10, "(%d, %d)" % (nx, ny),
                            size=12.5, color=FIELD, bold=True, anchor="start"))
        return out

    p += panel(96, "5x + 8y = 43  →  один спосіб",
               ((-1, 6), (8.6, 0)), [(7, 1)], [(-1, 6)])
    p += panel(628, "5x + 8y = 40  →  два способи",
               ((0, 5), (8, 0)), [(0, 5), (8, 0)], [])

    p.append(text(96 + 60, 108, "порожній вузол — розв'язок є, але з x < 0",
                  size=11.5, color=MUTED, anchor="start", italic=True))

    p.append(fitbox(90, 508, 900, 60,
                    "Скільки вузлів попаде на відрізок — стільки й невід'ємних розв'язків: нуль, один чи кілька.\n"
                    "А яких сум не скласти зовсім, коли повертати нічого не можна, — це вже задача про число Фробеніуса.",
                    size=13.5, fill=FILL, stroke=NEG, sw=2))

    return render(os.path.join(OUT, "nonneg-window.svg"), W, H, *p)


# ── history-timeline: метод (Індія) і ім'я (Діофант) розійшлися в часі ────────
# Ідея вставки-історії: рівняння зветься «діофантовим», але систематичний
# цілочисельний метод дала індійська школа (Аріабгата 499 → Брахмагупта 628),
# а в Європу його — уже під іменем Діофанта — повернув Баше (1621/1624),
# сам того не знаючи, перевідкривши алгоритм Евкліда. Часова вісь із розривом
# показує тисячолітню прогалину між методом і його перевідкриттям.
def fig_history_timeline():
    W, H = 1180, 610
    p = []
    p.append(text(W / 2, 40, "Метод і ім'я розійшлися: хто що зробив насправді",
                  size=17, color=INK, bold=True))

    axy = 300
    # дві половини осі часу з розривом «≈ 1000 років» між Індією і Європою
    p.append(line(95, axy, 646, axy, color=MUTED, sw=2))
    p.append(line(714, axy, 1085, axy, color=MUTED, sw=2))
    for gx in (662, 682):                      # символ розриву осі
        p.append(line(gx, axy - 12, gx - 9, axy + 12, color=MUTED, sw=2))
    p.append(text(680, 250, "≈ 1000 років", size=12.5, color=MUTED, italic=True))
    p.append(text(680, 268, "Європа без методу", size=11.5, color=MUTED, italic=True))

    # вузол: кружок на осі + стеблина + підпис (ім'я жирним, під ним рік і роль)
    def node(x, color, up, name, year, roles):
        out = [circle(x, axy, 8, fill=color, stroke=BG, sw=2)]
        if up:
            out.append(line(x, axy - 10, x, 214, color=color, sw=1.4))
            out.append(text(x, 132, name, size=14, color=color, bold=True))
            out.append(mtext(x, 152, [year] + roles, size=12.5, color=MUTED, lh=1.45))
        else:
            out.append(line(x, axy + 10, x, 418, color=color, sw=1.4))
            out.append(text(x, 432, name, size=14, color=color, bold=True))
            out.append(mtext(x, 452, [year] + roles, size=12.5, color=MUTED, lh=1.45))
        return out

    p += node(150, NEG,   True,  "Діофант",       "III ст. н.е.",
              ["Александрія:", "приклади + символіка"])
    p += node(305, MUTED, False, "Чжан Цюцзянь",  "≈ V ст., Китай",
              ["«сто птахів»:", "7x + 4y = 100"])
    p += node(460, FIELD, True,  "Аріабгата",     "499, Індія",
              ["перший загальний", "метод «кут-така»"])
    p += node(600, FIELD, False, "Брахмагупта",   "628, Індія",
              ["розвинув", "і узагальнив"])
    p += node(815, POS,   True,  "Баше де Мезіріак", "1621 / 1624, Європа",
              ["переклав Діофанта;", "метод ax − by = 1"])
    p += node(985, INK,   False, "П'єр Ферма",    "≈ 1637",
              ["нотатки на полях", "«Арифметики»"])

    p.append(fitbox(150, 548, 880, 44,
                    "Зелене — справжній загальний метод (Індія).   "
                    "Синє — окремі приклади й символіка (Діофант).   "
                    "Червоне — незалежне перевідкриття в Європі (Баше).",
                    size=13, fill=FILL, stroke=MUTED, sw=1.6))

    return render(os.path.join(OUT, "history-timeline.svg"), W, H, *p)


# ── t-window: невід'ємність двома нерівностями стягує t у відрізок ────────────
# Ідея math-вставки: підставивши родину в x ≥ 0 та y ≥ 0, дістаємо L ≤ t ≤ R;
# кількість невід'ємних розв'язків = число цілих у [L, R] = ⌊R⌋ − ⌈L⌉ + 1.
# Дві панелі: 43 → одне ціле t у вікні (1 спосіб); 40 → два (кінці самі цілі).
def fig_t_window():
    W, H = 1060, 380
    p = []
    p.append(text(W / 2, 40, "Дві нерівності стягують t у відрізок — рахуємо цілі поділки",
                  size=16, color=INK, bold=True))

    def panel(ox, oy, eqn, fam, tmin, tmax, L, R, Llab, Rlab, hits, formula, verdict):
        out = []
        plotw = 400
        def Pt(t): return ox + (t - tmin) / (tmax - tmin) * plotw

        out.append(text(ox + plotw / 2, oy - 78, eqn, size=14.5, color=INK, bold=True))
        out.append(text(ox + plotw / 2, oy - 58, fam, size=12.5, color=MUTED))

        # відрізок [L, R] на осі параметра
        out.append(rect(Pt(L), oy - 15, Pt(R) - Pt(L), 30,
                        fill=QUAD_F, stroke=FIELD, sw=2, rx=4))
        out.append(text(Pt(L), oy - 26, Llab, size=12, color=FIELD, bold=True, anchor="end"))
        out.append(text(Pt(R), oy - 26, Rlab, size=12, color=FIELD, bold=True, anchor="start"))

        # вісь t
        out.append(line(ox - 16, oy, ox + plotw + 20, oy, color=MUTED, sw=1.6))
        out.append(text(ox + plotw + 32, oy + 5, "t", size=13, color=MUTED, italic=True))

        # цілі поділки; ті, що в [L, R], — зелені вузли-розв'язки
        for t in range(math.ceil(tmin), math.floor(tmax) + 1):
            x = Pt(t)
            out.append(line(x, oy - 7, x, oy + 7, color=MUTED, sw=1.3))
            out.append(text(x, oy + 26, str(t), size=12.5, color=MUTED))
            if L - 1e-9 <= t <= R + 1e-9:
                out.append(circle(x, oy, 8, fill=GREEN_F, stroke=FIELD, sw=2.6))

        for t, lab in hits:
            out.append(text(Pt(t), oy + 52, lab, size=12.5, color=FIELD, bold=True))

        out.append(text(ox + plotw / 2, oy + 84, formula, size=12.5, color=INK))
        out.append(text(ox + plotw / 2, oy + 108, verdict, size=13.5, color=FIELD, bold=True))
        return out

    p += panel(70, 205, "5x + 8y = 43", "x = 7 + 8t,   y = 1 − 5t",
               -2, 2, -0.875, 0.2, "L = −7⁄8", "R = 1⁄5",
               [(0, "t = 0  →  (7, 1)")],
               "⌊0.2⌋ − ⌈−0.875⌉ + 1 = 0 − 0 + 1",
               "один спосіб")

    p += panel(560, 205, "5x + 8y = 40", "x = 8t,   y = 5 − 5t",
               -1, 2, 0.0, 1.0, "L = 0", "R = 1",
               [(0, "(0, 5)"), (1, "(8, 0)")],
               "⌊1⌋ − ⌈0⌉ + 1 = 1 − 0 + 1",
               "два способи")

    return render(os.path.join(OUT, "t-window.svg"), W, H, *p)


# ── solver-flow: керуюча логіка розв'язника (для вставки proj) ────────────────
# Ідея: вертикальний потік від входу (a,b,c) через перевірку a=b=0, НСД і
# критерій d|c до масштабування, зведення параметром t і переліку невід'ємних.
# Гілки праворуч — три виходи «немає / уся площина / нескінченно».
def fig_solver_flow():
    W, H = 880, 690
    p = []
    p.append(text(W / 2, 32, "Розв'язник  a·x + b·y = c:  від входу до переліку",
                  size=16.5, color=INK, bold=True))

    MX, MW = 60, 380            # головна колона
    EX, EW = 530, 330           # виходи праворуч
    cxm = MX + MW / 2

    def box(y, h, s, fill=FILL, stroke=MUTED, x=MX, w=MW, bold=False, size=13.5):
        p.append(fitbox(x, y, w, h, s, size=size, fill=fill, stroke=stroke,
                        sw=1.8, bold=bold, color=INK))

    def down(y1, y2):
        p.append(arrow(cxm, y1, cxm, y2, color=INK, sw=1.9))

    def right(ymid, label):
        p.append(arrow(MX + MW, ymid, EX, ymid, color=MUTED, sw=1.8))
        p.append(text((MX + MW + EX) / 2, ymid - 8, label, size=12, color=MUTED, italic=True))

    # головна колона
    box(62, 44, "вхід:  цілі  a, b, c")
    box(128, 44, "a = 0  і  b = 0 ?", fill=BLUE_F, stroke=NEG, bold=True)
    box(196, 52, "d = НСД(a, b),  розшир. Евклід:\nx₀, y₀ :  a·x₀ + b·y₀ = d")
    box(284, 44, "d  ділить  c ?", fill=BLUE_F, stroke=NEG, bold=True)
    box(356, 52, "один розв'язок:\nx₁ = x₀·(c/d),   y₁ = y₀·(c/d)")
    box(444, 52, "уся родина:\nx = x₁ + (b/d)·t,   y = y₁ − (a/d)·t")
    box(530, 44, "зведення:   t  →  найменший  | x |")
    box(598, 52, "вікно t:  x ≥ 0  і  y ≥ 0\n→  перелік невід'ємних",
        fill=GREEN_F, stroke=FIELD, bold=True)

    # виходи праворуч
    box(124, 52, "так, c = 0  →  уся площина\nтак, c ≠ 0  →  немає розв'язку",
        x=EX, w=EW, fill=FILL, stroke=MUTED, size=12.5)
    box(284, 44, "ні   →   немає розв'язку",
        x=EX, w=EW, fill=RED_F, stroke=POS, bold=True)
    box(598, 52, "a чи b = 0, або різні знаки\n→  нескінченно багато",
        x=EX, w=EW, fill=FILL, stroke=MUTED, size=12.5)

    # стрілки вниз по колоні
    for y1, y2 in ((106, 128), (172, 196), (248, 284), (328, 356),
                   (408, 444), (496, 530), (574, 598)):
        down(y1, y2)

    # гілки праворуч
    right(150, "так")
    right(306, "ні")
    right(624, "інакше")

    return render(os.path.join(OUT, "solver-flow.svg"), W, H, *p)


for f in (fig_lattice_line, fig_general_solution, fig_nonneg_window,
          fig_history_timeline, fig_t_window, fig_solver_flow):
    print("написано:", f())
