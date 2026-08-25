# -*- coding: utf-8 -*-
"""Фігури для теми «NP-важкість задачі розміщення» (book/algorithms/data-structures)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

WIRE = "#7a869a"
BLOCKFILL = "#eaf0fd"

SUP = {"-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
       "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}


def sup(n):
    return "".join(SUP[c] for c in str(n))


def fmt_p(p):
    """Імовірність: звичайним записом, а зовсім малу — науковим."""
    if p >= 0.001:
        return "%.3f" % p
    e = int(math.floor(math.log10(p)))
    m = p / (10.0 ** e)
    if round(m) >= 10:          # 9.6·10⁻⁵ → 1·10⁻⁴
        m, e = m / 10.0, e + 1
    return "%.0f·10%s" % (m, sup(e))


def grid_placement(ox, oy, cell, placement, nets, label, hpwl):
    """3×3 сітка слотів, сполуки-лінії, блоки-кружки, підпис і HPWL під сіткою."""
    frags = []
    n = 3
    for c in range(n):
        for r in range(n):
            cx = ox + c * cell
            cy = oy + r * cell
            frags.append(rect(cx - cell * 0.44, cy - cell * 0.44,
                              cell * 0.88, cell * 0.88,
                              fill=BG, stroke="#d0d5dd", sw=1.2, rx=6))

    def cen(b):
        c, r = placement[b]
        return ox + c * cell, oy + r * cell

    for a, b in nets:
        ax, ay = cen(a); bx, by = cen(b)
        frags.append(line(ax, ay, bx, by, color=WIRE, sw=2.4))
    for b, (c, r) in placement.items():
        cx = ox + c * cell; cy = oy + r * cell
        frags.append(circle(cx, cy, cell * 0.28, fill=BLOCKFILL, stroke=NEG, sw=2))
        frags.append(text(cx, cy + 6, b, size=18, color=INK, bold=True))

    mid = ox + (n - 1) * cell / 2
    by = oy + (n - 1) * cell + cell * 0.44 + 34
    frags.append(text(mid, by, label, size=16, bold=True))
    frags.append(text(mid, by + 24, "HPWL = %d" % hpwl, size=15, color=MUTED))
    return "".join(frags)


def fig_two_placements():
    W, H = 940, 500
    cell = 66
    bad = {"A": (0, 0), "B": (2, 2), "C": (2, 0), "D": (0, 2)}
    good = {"A": (0, 0), "B": (1, 0), "C": (0, 1), "D": (1, 1)}
    nets = [("A", "B"), ("B", "D"), ("D", "C"), ("C", "A")]
    left = grid_placement(150, 120, cell, bad, nets, "Погане розміщення", 12)
    right = grid_placement(620, 120, cell, good, nets, "Добре розміщення", 4)
    render(os.path.join(IMG, "two-placements.svg"), W, H, left, right,
           title="Ті самі блоки, різні слоти — різна ціна дроту")


def fig_factorial_wall():
    W, H = 900, 400
    header = ("блоків n", "розкладок n!", "час повного перебору (10⁹/с)")
    rows = [
        ("10", "3.6·10⁶", "0.004 секунди"),
        ("15", "1.3·10¹²", "22 хвилини"),
        ("20", "2.4·10¹⁸", "77 років"),
        ("25", "1.6·10²⁵", "490 мільйонів років"),
        ("60", "8·10⁸¹", "більше за число атомів у Всесвіті"),
    ]
    cols = [(50, 120), (180, 250), (440, 410)]  # (x, width)
    y0, rh = 64, 52
    frags = []
    for (cx, cw), h in zip(cols, header):
        frags.append(fitbox(cx, y0, cw, rh, h, size=15, bold=True,
                            fill="#eef2f7", stroke="#c7ced6"))
    for i, row in enumerate(rows):
        y = y0 + rh * (i + 1)
        fill = BG if i % 2 == 0 else "#f7f9fb"
        for (cx, cw), val in zip(cols, row):
            frags.append(fitbox(cx, y, cw, rh, val, size=15, fill=fill, stroke="#e2e6ea"))
    render(os.path.join(IMG, "factorial-wall.svg"), W, H, *frags,
           title="Скільки коштує знайти найкраще перебором")


def fig_reduction_chain():
    W, H = 860, 430
    frags = []
    b1, _, _ = textbox(430, 78,
                       "Мінімальне лінійне впорядкування\n(розкласти блоки в ОДИН ряд —\nдоведено NP-повна)",
                       size=15, fill="#fdecea", stroke=POS, sw=2, pad=14)
    frags.append(b1)
    frags.append(arrow(430, 134, 430, 182, color=INK, sw=2))
    frags.append(text(470, 154, "1-D — лише окремий випадок", size=13,
                      color=MUTED, italic=True, anchor="start"))

    b2, _, _ = textbox(430, 220, "Задача розміщення\n(блоки по всій тканині)",
                       size=15, fill=FILL, stroke=LINE, pad=14)
    frags.append(b2)
    frags.append(arrow(430, 262, 430, 310, color=INK, sw=2))
    frags.append(text(470, 282, "швидка загальна ⇒ швидка NP-повна", size=13,
                      color=MUTED, italic=True, anchor="start"))

    b3, _, _ = textbox(430, 356, "Отже, розміщення — NP-важке",
                       size=17, fill="#e9f7ef", stroke=FIELD, sw=2.5, bold=True, pad=16)
    frags.append(b3)
    render(os.path.join(IMG, "reduction-chain.svg"), W, H, *frags,
           title="Чому розміщення важке: воно містить відому важку задачу")


def fig_frustration_twins():
    """Фрустрація: трикутник спінів і трикутник сполук — одна й та сама біда."""
    W, H = 1040, 560
    frags = []

    # ── ліворуч: трикутник спінів ─────────────────────────────────────────
    frags.append(text(290, 112, "Скло зі спінів: трикутник зв'язків", size=16, bold=True))
    T, L, R = (290, 165), (215, 299), (365, 299)
    frags.append(line(T[0], T[1], L[0], L[1], color=FIELD, sw=3))
    frags.append(line(L[0], L[1], R[0], R[1], color=FIELD, sw=3))
    frags.append(line(T[0], T[1], R[0], R[1], color=POS, sw=3, dash="7 5"))
    for p in (T, L, R):
        frags.append(circle(p[0], p[1], 24, fill="#eaf0fd", stroke=NEG, sw=2))
        frags.append(text(p[0], p[1] + 9, "↑", size=24, color=NEG, bold=True))
    frags.append(text(166, 212, "хоче однаково ✓", size=14, color=FIELD,
                      bold=True, anchor="end"))
    frags.append(text(414, 212, "хоче навпаки ✗", size=14, color=POS,
                      bold=True, anchor="start"))
    frags.append(text(290, 355, "хоче однаково ✓", size=14, color=FIELD, bold=True))
    frags.append(text(290, 406, "Вдовольнити можна лише два зв'язки з трьох",
                      size=15, color=MUTED, italic=True))

    # ── праворуч: трикутник сполук на сітці ───────────────────────────────
    frags.append(text(760, 112, "Розміщення: трикутник сполук", size=16, bold=True))
    ox, oy, cell = 720, 229, 80
    for c in (0, 1):
        for r in (0, 1):
            frags.append(rect(ox + c * cell - cell * 0.44, oy + r * cell - cell * 0.44,
                              cell * 0.88, cell * 0.88, fill=BG, stroke="#d0d5dd",
                              sw=1.2, rx=6))
    A, B, C = (ox, oy), (ox + cell, oy), (ox, oy + cell)
    frags.append(line(A[0], A[1], B[0], B[1], color=FIELD, sw=3))
    frags.append(line(A[0], A[1], C[0], C[1], color=FIELD, sw=3))
    frags.append(line(B[0], B[1], C[0], C[1], color=POS, sw=3, dash="7 5"))
    for p, nm in ((A, "A"), (B, "B"), (C, "C")):
        frags.append(circle(p[0], p[1], 24, fill=BLOCKFILL, stroke=NEG, sw=2))
        frags.append(text(p[0], p[1] + 7, nm, size=19, color=INK, bold=True))
    frags.append(text(665, 372, "A–B = 1 ✓", size=14, color=FIELD, bold=True))
    frags.append(text(760, 372, "A–C = 1 ✓", size=14, color=FIELD, bold=True))
    frags.append(text(857, 372, "B–C = 2 ✗", size=14, color=POS, bold=True))
    frags.append(text(760, 406, "Короткими будуть лише дві сполуки з трьох",
                      size=15, color=MUTED, italic=True))

    bar, _, _ = textbox(520, 492,
                        "Спільна причина: ціна залежить від ПАР — а пари не дають догодити всім одразу",
                        size=16, bold=True, fill="#eef2f7", stroke="#c7ced6", sw=2, pad=14)
    frags.append(bar)
    render(os.path.join(IMG, "frustration-twins.svg"), W, H, *frags,
           title="Одна й та сама фрустрація у двох світах")


def _flush_box(x_edge, cy, s, side, **kw):
    """textbox, притиснутий лівим ('right') або правим ('left') краєм до x_edge."""
    lines = s.split("\n") if isinstance(s, str) else list(s)
    size = kw.get("size", 13)
    bold = kw.get("bold", False)
    pad = kw.get("pad", 10)
    w = max(text_width(ln, size, bold) for ln in lines) + 2 * pad
    cx = (x_edge - w / 2) if side == "left" else (x_edge + w / 2)
    body, _, _ = textbox(cx, cy, s, **kw)
    return body


def fig_two_threads():
    """Дві нитки — задача з економіки й ліки з фізики — сходяться 1983-го."""
    W, H = 1000, 800
    AX = 500
    E_FILL, E_STROKE = "#eaf0fd", NEG      # нитка задачі
    P_FILL, P_STROKE = "#fdecea", POS      # нитка ліків
    frags = []

    hdr_l, _, _ = textbox(310, 64, "ЗАДАЧА — економіка й математика", size=14,
                          bold=True, fill=E_FILL, stroke=E_STROKE, sw=2, pad=10)
    hdr_r, _, _ = textbox(690, 64, "ЛІКИ — фізика й термодинаміка", size=14,
                          bold=True, fill=P_FILL, stroke=P_STROKE, sw=2, pad=10)
    frags += [hdr_l, hdr_r]

    rows = [
        ("1939", "E", "Канторович: лінійна оптимізація\nв плануванні виробництва"),
        ("1945", "E", "Купманс: маршрути суден,\n«аналіз діяльності»"),
        ("1953", "P", "Метрополіс і Розенблути:\nправило прийняття на MANIAC"),
        ("1955", "E", "Купманс і Бекман: дискусійна\nпраця Фонду Коулза №4"),
        ("1957", "E", "Econometrica 25(1): ціни більше\nне втримують оптимум"),
        ("1963", "E", "Лоулер: загальна форма\nй ім'я «квадратична задача»"),
        ("1975", "P", "Шеррінгтон і Кіркпатрик:\nмодель скла зі спінів"),
        ("1976", "E", "Сахні й Гонсалес: немає\nнавіть дешевого наближення"),
        ("1982", "P", "IBM RC 9355 · звіт Черни\nв Братиславі"),
        ("1983", "M", "1983 · Science 220: «імітація відпалу» розкладає елементи комп'ютера"),
        ("1985", "P", "Черни: JOTA 45 — незалежне\nвідкриття нарешті друком"),
    ]
    y0, step = 120, 62
    ys = [y0 + i * step for i in range(len(rows))]

    for (year, lane, txt), y in zip(rows, ys):
        if lane == "M":
            box, _, _ = textbox(AX, y, txt, size=14, bold=True, fill="#e9f7ef",
                                stroke=FIELD, sw=2.5, pad=13)
            frags.append(box)
            continue
        fill, stroke = (E_FILL, E_STROKE) if lane == "E" else (P_FILL, P_STROKE)
        side, edge = ("left", 440) if lane == "E" else ("right", 560)
        frags.append(_flush_box(edge, y, txt, side, size=13, fill=fill,
                                stroke=stroke, sw=1.8, pad=10))
        frags.append(text(AX, y + 5, year, size=15, bold=True, color=INK))

    # з'єднувачі осі — короткі відтинки МІЖ мітками, щоб текст не лягав на лінію
    m_i = [i for i, r in enumerate(rows) if r[1] == "M"][0]
    m_half = 14 * 1.3 / 2 + 13 + 4          # півheight рамки-«зустрічі»
    for i in range(len(ys) - 1):
        top = ys[i] + (m_half + 6 if i == m_i else 16)
        bot = ys[i + 1] - (m_half + 6 if i + 1 == m_i else 16)
        frags.append(line(AX, top, AX, bot, color="#b8c0cc", sw=2.5))

    render(os.path.join(IMG, "two-threads.svg"), W, H, *frags,
           title="Дві нитки, що зійшлися на кремнії")


def fig_delta_nets():
    """Серце інкрементного відпалу: хід чіпає лише сполуки двох блоків."""
    W, H = 1020, 390
    cell = 92
    ox, oy = 110, 115
    GW, GH = 5, 3

    blocks = {"A": (0, 0), "D": (2, 0), "H": (4, 0),
              "B": (1, 1), "E": (3, 1),
              "C": (0, 2), "G": (2, 2), "F": (4, 2)}
    hot = [("A", "B"), ("B", "C"), ("B", "G"), ("D", "E"), ("E", "F"), ("E", "H")]
    cold = [("A", "D"), ("C", "G"), ("F", "H")]
    swapped = ("B", "E")

    def cen(b):
        c, r = blocks[b]
        return ox + c * cell, oy + r * cell

    frags = []
    for c in range(GW):
        for r in range(GH):
            frags.append(rect(ox + c * cell - cell * 0.44, oy + r * cell - cell * 0.44,
                              cell * 0.88, cell * 0.88, fill=BG, stroke="#d0d5dd",
                              sw=1.2, rx=6))
    for a, b in cold:
        ax, ay = cen(a); bx, by = cen(b)
        frags.append(line(ax, ay, bx, by, color="#c3cad3", sw=2.0))
    for a, b in hot:
        ax, ay = cen(a); bx, by = cen(b)
        frags.append(line(ax, ay, bx, by, color=POS, sw=3.6))

    mx, my = ox + 2 * cell, oy + cell          # порожній слот між B і E
    frags.append(arrow(mx, my, mx + cell * 0.70, my, color=INK, sw=2.2))
    frags.append(arrow(mx, my, mx - cell * 0.70, my, color=INK, sw=2.2))
    frags.append(text(mx, my - 20, "обмін", size=13, color=MUTED, italic=True))

    for b in blocks:
        x, y = cen(b)
        sw_ = b in swapped
        frags.append(circle(x, y, cell * 0.27, fill=BLOCKFILL if sw_ else FILL,
                            stroke=NEG if sw_ else "#9aa4b2", sw=3.5 if sw_ else 1.8))
        frags.append(text(x, y + 6, b, size=17, color=INK, bold=True))

    frags.append(rect(590, 115, 410, 160, fill="#fbfcfd", stroke="#dfe4ea", sw=1.2, rx=8))
    frags.append(line(610, 155, 655, 155, color=POS, sw=3.6))
    frags.append(text(670, 160, "зачеплені сполуки — 6, перерахувати",
                      size=13, anchor="start"))
    frags.append(line(610, 200, 655, 200, color="#c3cad3", sw=2.0))
    frags.append(text(670, 205, "решта — 3, НЕ чіпаємо", size=13, anchor="start"))
    frags.append(circle(632, 245, 13, fill=BLOCKFILL, stroke=NEG, sw=3))
    frags.append(text(670, 250, "блоки B і E міняються місцями",
                      size=13, anchor="start"))

    render(os.path.join(IMG, "delta-nets.svg"), W, H, *frags,
           title="Хід чіпає лише сполуки двох блоків — решту рахувати нема чого")


def fig_metropolis():
    """Точна арифметика правила прийняття: exp(−Δ/T) на різних температурах."""
    W, H = 940, 430
    temps = [50.0, 10.0, 2.0, 0.5, 0.145]
    labels = ["50 — розплав", "10", "2", "0.5", "0.145 — вихід"]
    deltas = [1, 5, 20]
    x0, y0, cw0, cw, rh = 60, 74, 200, 220, 52

    frags = [fitbox(x0, y0, cw0, rh, "температура T", size=15, bold=True,
                    fill="#eef2f7", stroke="#c7ced6")]
    for j, d in enumerate(deltas):
        frags.append(fitbox(x0 + cw0 + j * cw, y0, cw, rh, "Δ = +%d" % d,
                            size=15, bold=True, fill="#eef2f7", stroke="#c7ced6"))
    for i, T in enumerate(temps):
        y = y0 + rh * (i + 1)
        frags.append(fitbox(x0, y, cw0, rh, labels[i], size=14,
                            fill="#f7f9fb", stroke="#e2e6ea"))
        for j, d in enumerate(deltas):
            p = math.exp(-d / T)
            fill = "#fdecea" if p > 0.5 else ("#fff6e5" if p > 0.05 else "#f2f4f6")
            frags.append(fitbox(x0 + cw0 + j * cw, y, cw, rh, fmt_p(p),
                                size=15, fill=fill, stroke="#e2e6ea"))
    frags.append(text(W / 2, y0 + rh * 6 + 26,
                      "Що холодніше, то раніше вмирають великі стрибки — останнім гасне Δ = +1.",
                      size=13, color=MUTED, italic=True))
    render(os.path.join(IMG, "metropolis-table.svg"), W, H, *frags,
           title="Імовірність прийняти гірший хід: exp(−Δ/T)")


def fig_cooling_schedules():
    """Той самий старт і поріг — але α вирішує, скільки пакетів ходів буде."""
    W, H = 1120, 500
    x0, y0, pw, ph = 130, 90, 590, 320
    T0, TEXIT, KMAX = 50.0, 0.145, 130
    ytop, ybot = math.log10(80.0), math.log10(0.08)

    def px(k):
        return x0 + pw * k / KMAX

    def py(T):
        return y0 + ph * (ytop - math.log10(T)) / (ytop - ybot)

    frags = [rect(x0, y0, pw, ph, fill="#fcfdfe", stroke="#dfe4ea", sw=1.2, rx=4)]
    for T in (50, 10, 1):
        y = py(T)
        frags.append(line(x0, y, x0 + pw, y, color="#eceff2", sw=1.2))
        frags.append(text(x0 - 14, y + 5, "T = %g" % T, size=13,
                          color=MUTED, anchor="end"))
    ye = py(TEXIT)
    frags.append(line(x0, ye, x0 + pw, ye, color=NEG, sw=1.8, dash="7 5"))
    frags.append(text(x0 - 14, ye + 5, "0.145", size=13, color=NEG,
                      anchor="end", bold=True))
    for k in (0, 25, 50, 75, 100, 125):
        frags.append(line(px(k), y0 + ph, px(k), y0 + ph + 6, color=MUTED, sw=1.2))
        frags.append(text(px(k), y0 + ph + 26, str(k), size=13, color=MUTED))
    frags.append(text(x0 + pw / 2, y0 + ph + 54,
                      "крок температури k — на кожному свій пакет ходів",
                      size=14, color=INK))

    lanes = [(0.50, POS, "9", "гартування"),
             (0.80, "#e08a1e", "27", ""),
             (0.95, FIELD, "114", "відпал")]
    for a, color, _, _ in lanes:
        kx = math.log(TEXIT / T0) / math.log(a)
        frags.append(line(px(0), py(T0), px(kx), py(TEXIT), color=color, sw=3.2))
        frags.append(circle(px(kx), py(TEXIT), 5.5, fill=BG, stroke=color, sw=3))

    frags.append(rect(750, 110, 350, 150, fill="#fbfcfd", stroke="#dfe4ea", sw=1.2, rx=8))
    ly = 148
    for a, color, steps, name in lanes:
        frags.append(line(768, ly, 806, ly, color=color, sw=3.2))
        lab = "α = %.2f — %s кроків" % (a, steps)
        if name:
            lab += " (%s)" % name
        frags.append(text(818, ly + 5, lab, size=13, anchor="start"))
        ly += 44

    render(os.path.join(IMG, "cooling-schedules.svg"), W, H, *frags,
           title="Однакова дорога, різна швидкість: T ← α·T від 50 до порога виходу")


def fig_hpwl_truth():
    """Півпериметр: до трьох виводів модель точна, з чотирьох — занижує."""
    W, H = 1200, 540
    cell, oy = 50, 290
    frags = []

    def panel(ox, title, pins, route, hp, real, verdict, ok):
        out = []
        for c in range(5):
            out.append(line(ox + c * cell, oy, ox + c * cell, oy - 3 * cell,
                            color="#e9edf2", sw=1))
        for r in range(4):
            out.append(line(ox, oy - r * cell, ox + 4 * cell, oy - r * cell,
                            color="#e9edf2", sw=1))
        xs = [p[0] for p in pins]
        ys = [p[1] for p in pins]
        bx0 = ox + min(xs) * cell - 9
        by0 = oy - max(ys) * cell - 9
        bw = (max(xs) - min(xs)) * cell + 18
        bh = (max(ys) - min(ys)) * cell + 18
        out.append(rect(bx0, by0, bw, bh, fill="#eaf1ff", stroke="none", sw=0, rx=0))
        for a, b in ((( bx0, by0), (bx0 + bw, by0)), ((bx0 + bw, by0), (bx0 + bw, by0 + bh)),
                     ((bx0 + bw, by0 + bh), (bx0, by0 + bh)), ((bx0, by0 + bh), (bx0, by0))):
            out.append(line(a[0], a[1], b[0], b[1], color=NEG, sw=2, dash="6 4"))
        for (ax, ay), (bx, by) in route:
            out.append(line(ox + ax * cell, oy - ay * cell,
                            ox + bx * cell, oy - by * cell, color=POS, sw=4))
        for (pxx, pyy) in pins:
            out.append(circle(ox + pxx * cell, oy - pyy * cell, 8.5,
                              fill=BG, stroke=INK, sw=2.4))
        cx = ox + 2 * cell
        out.append(text(cx, by0 - 26, title, size=17, bold=True))
        out.append(text(cx, oy + 42, "HPWL = 4 + 3 = %d" % hp, size=15,
                        color=NEG, bold=True))
        out.append(text(cx, oy + 68, "справжня траса = %d" % real, size=15,
                        color=POS, bold=True))
        box, _, _ = textbox(cx, oy + 110, verdict, size=14, bold=True,
                            fill="#e9f7ef" if ok else "#fdecea",
                            stroke=FIELD if ok else POS, sw=2, pad=11)
        out.append(box)
        return "".join(out)

    frags.append(panel(90, "2 виводи",
                       [(0, 0), (4, 3)],
                       [((0, 0), (4, 0)), ((4, 0), (4, 3))],
                       7, 7, "модель ТОЧНА", True))
    frags.append(panel(500, "3 виводи",
                       [(0, 0), (4, 0), (2, 3)],
                       [((0, 0), (4, 0)), ((2, 0), (2, 3))],
                       7, 7, "модель ТОЧНА", True))
    frags.append(panel(910, "4 виводи",
                       [(0, 0), (4, 0), (0, 3), (4, 3)],
                       [((0, 0), (0, 3)), ((4, 0), (4, 3)), ((0, 1.5), (4, 1.5))],
                       7, 10, "ЗАНИЖУЄ на 3", False))

    bar, _, _ = textbox(600, 480,
                        "Півпериметр бачить лише РАМКУ, а не те, що всередині: до трьох виводів цього досить, з чотирьох — уже ні",
                        size=15, bold=True, fill="#eef2f7", stroke="#c7ced6", sw=2, pad=14)
    frags.append(bar)
    render(os.path.join(IMG, "hpwl-truth.svg"), W, H, *frags,
           title="Та сама рамка 4×3, той самий HPWL = 7 — а траса різна")


def fig_two_cuts():
    """Два інгредієнти важкості: зв'язок пар × дискретність області."""
    W, H = 1140, 660
    frags = []
    HX, HW = 40, 250
    C1, C2, CW = 310, 720, 390
    HY, HH = 76, 64
    R1, R2, RH = 156, 368, 196

    for x, s in ((C1, "ОБЛАСТЬ НЕПЕРЕРВНА\nкоординати — дійсні числа"),
                 (C2, "ОБЛАСТЬ ДИСКРЕТНА\nперестановка по слотах")):
        frags.append(fitbox(x, HY, CW, HH, s, size=15, bold=True,
                            fill="#eef2f7", stroke="#c7ced6", sw=2))
    for y, s in ((R1, "ЦІНА ЛІНІЙНА\n\nблок коштує\nсам по собі\n\nΣ c(i, π(i))"),
                 (R2, "ЦІНА КВАДРАТИЧНА\n\nкоштує ПАРА блоків\n\nΣ f(i,j)·d(π(i),π(j))")):
        frags.append(fitbox(HX, y, HW, RH, s, size=14, bold=True,
                            fill="#eef2f7", stroke="#c7ced6", sw=2))

    easy = dict(fill="#e9f7ef", stroke=FIELD, sw=2.4)
    cells = [
        (C1, R1, "Лінійне програмування\n\nмінімум — у вершині\nмногогранника\n\nсимплекс — ЛЕГКО", easy),
        (C2, R1, "Лінійна задача про призначення\n\nвершини Біркгофа = перестановки,\nтож ЛП сама дає цілу відповідь\n\nугорський метод O(n³) — ЛЕГКО", easy),
        (C1, R2, "Аналітичне розміщення\n\nградієнт = 0 → L·x = b\nрозріджений лапласіан\n\nмайже лінійний час — ЛЕГКО", easy),
        (C2, R2, "РОЗМІЩЕННЯ = QAP\n\nNP-ВАЖКЕ\n\nні швидкого точного,\nні дешевої гарантії", dict(fill="#fdecea", stroke=POS, sw=3.4)),
    ]
    for x, y, s, kw in cells:
        frags.append(fitbox(x, y, CW, RH, s, size=14, bold=True, **kw))

    bar, _, _ = textbox(570, 610,
                        "Жоден інгредієнт сам по собі не важкий — важкий їхній ДОБУТОК: зв'язані пари НА перестановці",
                        size=15, bold=True, fill="#eef2f7", stroke="#c7ced6", sw=2, pad=14)
    frags.append(bar)
    render(os.path.join(IMG, "two-cuts.svg"), W, H, *frags,
           title="Де саме ховається важкість: розріжемо задачу двома ножами")


def fig_relaxation_gap():
    """Многогранник Біркгофа: неперервний мінімум дешевший за всі справжні розкладки."""
    W, H = 1080, 660
    X0, X1, YB, YSC = 260, 760, 500, 300
    fx = lambda t: X0 + t * (X1 - X0)
    fy = lambda c: YB - c * YSC
    cost = lambda t: t * t + (1 - t) * (1 - t)
    frags = []

    frags.append(line(X0, YB, 800, YB, color=INK, sw=2))
    frags.append(line(X0, 170, X0, 520, color=INK, sw=2))
    frags.append(text(X0, 158, "ціна", size=14, color=MUTED))
    for t, lab in ((0, "0"), (0.5, "½"), (1, "1")):
        frags.append(line(fx(t), YB, fx(t), YB + 6, color=INK, sw=2))
        frags.append(text(fx(t), YB + 26, lab, size=14))
    for c, lab in ((0, "0"), (0.5, "½"), (1, "1")):
        frags.append(line(X0 - 6, fy(c), X0, fy(c), color=INK, sw=2))
        frags.append(text(X0 - 18, fy(c) + 5, lab, size=14, anchor="end"))
    frags.append(text(530, YB + 54, "t — частка блока A у слоті s₁",
                      size=14, color=MUTED, italic=True))

    frags.append(line(X0, fy(1), X1, fy(1), color="#b8c0cc", sw=2, dash="7 5"))
    pts = [(fx(i / 60.0), fy(cost(i / 60.0))) for i in range(61)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        frags.append(line(ax, ay, bx, by, color=NEG, sw=3.5))

    frags.append(circle(fx(0), fy(1), 8, fill=BG, stroke=POS, sw=3))
    frags.append(circle(fx(1), fy(1), 8, fill=BG, stroke=POS, sw=3))
    frags.append(circle(fx(0.5), fy(0.5), 8, fill="#e9f7ef", stroke=FIELD, sw=3))

    frags.append(arrow(fx(0.5), fy(0.5) - 9, fx(0.5), fy(1) + 6, color=INK, sw=2))
    frags.append(text(fx(0.5) - 14, 292, "розрив ×2", size=14, bold=True, anchor="end"))

    l1, _, _ = textbox(168, 116, "t = 0\nA→s₂, B→s₁\nсправжня, ціна 1",
                       size=13, fill="#fdecea", stroke=POS, sw=2, pad=10)
    frags.append(l1)
    frags.append(arrow(200, 151, 252, 194, color=MUTED, sw=1.8))
    r1, _, _ = textbox(890, 116, "t = 1\nA→s₁, B→s₂\nсправжня, ціна 1",
                       size=13, fill="#fdecea", stroke=POS, sw=2, pad=10)
    frags.append(r1)
    frags.append(arrow(858, 151, 770, 194, color=MUTED, sw=1.8))

    m, _, _ = textbox(510, 432,
                      "t = ½ — дробовий «оптимум»\nціна ½: дешевше за БУДЬ-ЯКУ\nсправжню розкладку",
                      size=14, fill="#e9f7ef", stroke=FIELD, sw=2, pad=12)
    frags.append(m)
    frags.append(arrow(510, 393, 510, 361, color=MUTED, sw=1.8))

    bar, _, _ = textbox(540, 600,
                        "Опуклість тягне мінімум УСЕРЕДИНУ многогранника — туди, де справжніх розкладок немає",
                        size=15, bold=True, fill="#eef2f7", stroke="#c7ced6", sw=2, pad=14)
    frags.append(bar)
    render(os.path.join(IMG, "relaxation-gap.svg"), W, H, *frags,
           title="Два блоки, два слоти: релаксація купує фікцію й бреше вдвічі")


if __name__ == "__main__":
    fig_two_placements()
    fig_factorial_wall()
    fig_reduction_chain()
    fig_frustration_twins()
    fig_two_threads()
    fig_delta_nets()
    fig_metropolis()
    fig_cooling_schedules()
    fig_hpwl_truth()
    fig_two_cuts()
    fig_relaxation_gap()
    print("OK:", sorted(os.listdir(IMG)))
