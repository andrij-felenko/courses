# -*- coding: utf-8 -*-
"""Фігури до статті «Коди Голея». Запуск із теки теми:  python figs.py
Виводить SVG у ./img/. Стиль — через svgkit (не копіювати, а імпортувати)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def hexagon(cx, cy, R, fill=FILL, stroke=LINE, sw=1.5):
    pts = []
    for a in (0, 60, 120, 180, 240, 300):
        rad = math.radians(a)
        pts.append((cx + R * math.cos(rad), cy + R * math.sin(rad)))
    d = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.1f"/>'
            % (d, fill, stroke, sw))


# ── Фігура 1: досконале укладання (стільники без зазору) ─────────────────────
def fig_packing():
    W, H = 780, 470
    frags = []

    R = 30
    dx = 1.5 * R              # крок між стовпцями (flat-top)
    dy = R * math.sqrt(3)     # крок між рядками
    x0, y0 = 80, 100
    cols, rows = 6, 5
    hi_c, hi_r = 5, 0         # підсвічений осередок (правий верхній — leader вправо чистий)

    hx = hy = 0
    for c in range(cols):
        for r in range(rows):
            cx = x0 + c * dx
            cy = y0 + r * dy + (dy / 2 if c % 2 else 0)
            hi = (c == hi_c and r == hi_r)
            frags.append(hexagon(cx, cy, R,
                                 fill="#e9f7ef" if hi else FILL,
                                 stroke=FIELD if hi else LINE,
                                 sw=2.8 if hi else 1.3))
            frags.append(circle(cx, cy, 3.0, fill=INK, stroke=INK, sw=1))
            if hi:
                hx, hy = cx, cy

    # leader від підсвіченого осередку до пояснення праворуч
    frags.append(line(hx + R, hy, 470, 150, color=FIELD, sw=1.6))

    # пояснення праворуч
    expl = ["Кожен осередок —", "одне кодове слово (·)",
            "разом з усіма словами,", "куди не більш як три",
            "помилки могли б його", "зсунути: куля з 2048 слів."]
    ty = 150
    for i, ln in enumerate(expl):
        frags.append(text(478, ty + i * 26, ln, size=16, anchor="start", color=INK))

    # нижня смуга-висновок
    frags.append(rect(48, 388, W - 96, 62, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=8))
    frags.append(text(W / 2, 412,
                      "Осередки не налазять один на одного й не лишають зазору:",
                      size=16, color=INK))
    frags.append(text(W / 2, 436,
                      "4096 кодових слів × 2048 слів у кулі  =  2²³  —  увесь простір, без залишку.",
                      size=16, color=INK, bold=True))

    render(os.path.join(OUT, "perfect-packing.svg"), W, H, *frags,
           title="Досконале укладання: код Голея заповнює простір слів без зазору")


# ── Фігура 2: родина кодів Голея ────────────────────────────────────────────
def fig_family():
    W, H = 780, 470
    frags = []

    def card(y, tag, lines, badge, badge_fill, badge_stroke):
        frags.append(rect(40, y, 700, 112, fill=BG, stroke=LINE, sw=1.6, rx=10))
        # ярлик [n, k, d]
        frags.append(text(60, y + 66, tag, size=26, anchor="start", color=INK, bold=True))
        # опис посередині
        y_text = y + 56 - (len(lines) - 1) * 22 / 2
        frags.append(mtext(272, y_text, lines, size=16, color=INK, anchor="start", lh=1.4))
        # значок праворуч
        bf, bw, bh = textbox(648, y + 56, badge, size=15, pad=12,
                             fill=badge_fill, stroke=badge_stroke, bold=True)
        frags.append(bf)

    card(56, "[23, 12, 7]",
         ["12 бітів даних + 11 перевірних = 23", "виправляє 3 помилки"],
         "ДОСКОНАЛИЙ\n2¹²·2¹¹ = 2²³", "#e9f7ef", FIELD)

    card(180, "[24, 12, 8]",
         ["+1 біт парності до 23  →  24", "навпіл: 12 даних, 12 захисту",
          "виправляє 3, виявляє 4"],
         "код «Вояджерів»\nЮпітер і Сатурн", "#eaf0fd", NEG)

    card(304, "[11, 6, 5]",
         ["трійковий: над 3 символами (1 / X / 2)", "виправляє 2 помилки"],
         "ДОСКОНАЛИЙ\n3⁶·3⁵ = 3¹¹", "#e9f7ef", FIELD)

    render(os.path.join(OUT, "golay-family.svg"), W, H, *frags,
           title="Три коди Голея")


# ── Верифікована матриця A [24,12,8] (облямований циклант QR mod 11) ─────────
A_GOLAY = [
    "011111111111",
    "110100011101",
    "111010001110",
    "101101000111",
    "110110100011",
    "111011010001",
    "111101101000",
    "101110110100",
    "100111011010",
    "100011101101",
    "110001110110",
    "101000111011",
]


# ── Фігура 3: твірна матриця [I₁₂ | A] ───────────────────────────────────────
def fig_generator():
    cell = 22
    x0, y0 = 96, 84
    ncol, nrow = 24, 12
    W = x0 + ncol * cell + 44
    H = y0 + nrow * cell + 140
    frags = []

    for r in range(nrow):
        for c in range(ncol):
            v = (1 if c == r else 0) if c < 12 else int(A_GOLAY[r][c - 12])
            x, y = x0 + c * cell, y0 + r * cell
            frags.append(rect(x, y, cell, cell,
                              fill=INK if v else BG, stroke=MUTED, sw=0.7, rx=0))
        frags.append(text(x0 - 12, y0 + r * cell + cell * 0.68, str(r),
                          size=12, anchor="end", color=MUTED))

    # межа між блоком-одиницею і блоком перевірок
    xd = x0 + 12 * cell
    frags.append(line(xd, y0 - 8, xd, y0 + 12 * cell + 8, color=INK, sw=2.6))

    # облямівка A (рядок 0 і стовпець 0) — зелена рамка
    frags.append(rect(xd, y0, 12 * cell, cell, fill="none", stroke=FIELD, sw=2.4, rx=0))
    frags.append(rect(xd, y0, cell, 12 * cell, fill="none", stroke=FIELD, sw=2.4, rx=0))

    frags.append(text(x0 + 6 * cell, y0 - 18, "I₁₂  —  дані (12 біт)",
                      size=15, color=NEG, bold=True))
    frags.append(text(xd + 6 * cell, y0 - 18, "A  —  перевірка (12 біт)",
                      size=15, color=FIELD, bold=True))

    cap = ["Ліва половина слова — самі дані, права — їхня згортка матрицею A.",
           "Зелена облямівка (рядок 0 і стовпець 0) — суцільні одиниці;",
           "решта 11×11 — циклічна таблиця: клітину (i, j) зафарбовано,",
           "коли i = j або i − j — квадратичний лишок mod 11."]
    cy = y0 + 12 * cell + 28
    for i, ln in enumerate(cap):
        frags.append(text(W / 2, cy + i * 22, ln, size=13, color=INK))

    render(os.path.join(OUT, "generator-matrix.svg"), W, H, *frags,
           title="Твірна матриця [I₁₂ | A] розширеного коду Голея [24, 12, 8]")


# ── Фігура 4: циклічна побудова — квадратичні лишки mod 23 ───────────────────
def fig_qr23():
    W, H = 540, 520
    cx, cy = 270, 232
    R = 158
    QR = {1, 2, 3, 4, 6, 8, 9, 12, 13, 16, 18}
    frags = []

    frags.append(circle(cx, cy, R, fill="none", stroke=MUTED, sw=1.2))
    for i in range(23):
        ang = math.radians(-90 + i * 360.0 / 23)
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        if i == 0:
            frags.append(circle(x, y, 14, fill="#f4f6f8", stroke=INK, sw=2.4))
            frags.append(text(x, y + 5, "0", size=14, bold=True, color=INK))
        elif i in QR:
            frags.append(circle(x, y, 14, fill=FIELD, stroke=FIELD, sw=1))
            frags.append(text(x, y + 5, str(i), size=13, bold=True, color=BG))
        else:
            frags.append(circle(x, y, 14, fill=BG, stroke=MUTED, sw=1.6))
            frags.append(text(x, y + 5, str(i), size=13, color=MUTED))

    frags.append(mtext(cx, cy - 14, ["зсув на 1 позицію", "= знову кодове слово", "(код циклічний)"],
                       size=13, color=INK))

    # легенда
    ly = cy + R + 44
    frags.append(circle(60, ly, 11, fill=FIELD, stroke=FIELD, sw=1))
    frags.append(text(80, ly + 5, "11 квадратичних лишків — корені g(x), твірного полінома",
                      size=13, anchor="start", color=INK))
    frags.append(circle(60, ly + 30, 11, fill=BG, stroke=MUTED, sw=1.6))
    frags.append(text(80, ly + 35, "11 нелишків — корені h(x), перевірного полінома",
                      size=13, anchor="start", color=INK))
    frags.append(circle(60, ly + 60, 11, fill="#f4f6f8", stroke=INK, sw=2.2))
    frags.append(text(80, ly + 65, "позиція 0 — множник (x − 1)",
                      size=13, anchor="start", color=INK))

    render(os.path.join(OUT, "qr23-circle.svg"), W, H, *frags,
           title="Циклічна дорога: корені g(x) — на лишках mod 23")


# ── Фігура 5: багато доріг — один код ────────────────────────────────────────
def fig_convergence():
    W, H = 780, 470
    frags = []
    sources = [
        "Циклічна\nкв. лишки mod 23",
        "Облямована\nкв. лишки mod 11",
        "Ікосаедр\nдоповнення суміжності",
        "Склеювання |a|a+b|\nз Геммінга [8,4,4]",
        "Гексакод / MOG\nсітка 4×6 над GF(4)",
    ]
    lx = 150
    ys = [70, 148, 226, 304, 382]
    cxn, cyn = 585, 226
    for s, y in zip(sources, ys):
        bf, bw, bh = textbox(lx, y, s, size=13, pad=10,
                             fill=BG, stroke=LINE, sw=1.5)
        frags.append(bf)
        frags.append(arrow(lx + bw / 2 + 4, y, cxn - 118, cyn, color=MUTED, sw=1.7))

    # центральний вузол
    frags.append(rect(cxn - 112, cyn - 44, 224, 88, fill="#e9f7ef", stroke=FIELD, sw=2.4, rx=12))
    frags.append(text(cxn, cyn - 12, "ЄДИНИЙ код", size=20, bold=True, color=INK))
    frags.append(text(cxn, cyn + 14, "[24, 12, 8]", size=20, bold=True, color=FIELD))
    frags.append(mtext(cxn, cyn + 74,
                       ["самодвоїстий · Aut = M₂₄",
                        "октади = S(5, 8, 24) · ґратка Ліча"],
                       size=13, color=INK, lh=1.4))

    render(os.path.join(OUT, "many-roads.svg"), W, H, *frags,
           title="Багато побудов — один код (єдиність з точністю до перестановки)")


# ── Фігура: розкладка кодового слова (кодек) ─────────────────────────────────
def fig_encode():
    W, H = 860, 252
    frags = []
    n, cw, x0, ytop, ch = 24, 30, 40, 96, 46

    frags.append(text(W / 2, 54,
                      "24 біти — в одному uint32:  низькі 12 = дані,  високі 12 = перевірка",
                      size=14, color=MUTED))

    for k in range(n):
        x = x0 + k * cw
        data = k < 12
        frags.append(rect(x, ytop, cw, ch,
                          fill="#e9f7ef" if data else "#eaf0fd",
                          stroke=LINE, sw=1.2, rx=3))
    xd = x0 + 12 * cw
    frags.append(line(xd, ytop - 10, xd, ytop + ch + 10, color=INK, sw=2.4))

    frags.append(text(x0 + 0.5 * cw, ytop - 8, "0", size=13, color=MUTED))
    frags.append(text(x0 + 23.5 * cw, ytop - 8, "23", size=13, color=MUTED))

    yb = ytop + ch + 16
    frags.append(line(x0, yb, xd, yb, color=FIELD, sw=2.6))
    frags.append(text(x0 + 6 * cw, yb + 24, "12 бітів даних", size=15, bold=True))
    frags.append(text(x0 + 6 * cw, yb + 43, "просто копія повідомлення m", size=13, color=MUTED))
    frags.append(line(xd, yb, x0 + 24 * cw, yb, color=NEG, sw=2.6))
    frags.append(text(x0 + 18 * cw, yb + 24, "12 перевірних", size=15, bold=True))
    frags.append(text(x0 + 18 * cw, yb + 43, "= m · B  (XOR рядків B)", size=13, color=MUTED))

    render(os.path.join(OUT, "codeword-layout.svg"), W, H, *frags,
           title="Кодування: [ дані | дані · B ]")


# ── Фігура: каскад декодування (два синдроми, рядки B як таблиця) ─────────────
def fig_decode():
    W, H = 900, 700
    frags = []
    LX, LW = 60, 350
    RX, RW = 540, 330
    BH = 60
    rows = [48, 140, 232, 324, 416, 508, 600]
    lcx = LX + LW / 2
    rcx = RX + RW / 2

    AMB_F, AMB_S = "#fff3e0", "#e08a00"
    GRY_F, GRY_S = "#eef1f4", MUTED

    frags.append(fitbox(LX, rows[0], LW, BH, "s = B·x ⊕ y   (12-бітний синдром)",
                        size=15, fill=GRY_F, stroke=GRY_S, sw=1.6))
    frags.append(fitbox(LX, rows[1], LW, BH, "вага(s) ≤ 3 ?",
                        size=17, fill=AMB_F, stroke=AMB_S, sw=1.8, bold=True))
    frags.append(fitbox(LX, rows[2], LW, BH, "є рядок i:  вага(s ⊕ Bᵢ) ≤ 2 ?",
                        size=15, fill=AMB_F, stroke=AMB_S, sw=1.8, bold=True))
    frags.append(fitbox(LX, rows[3], LW, BH, "s₂ = B·s   (другий синдром)",
                        size=15, fill=GRY_F, stroke=GRY_S, sw=1.6))
    frags.append(fitbox(LX, rows[4], LW, BH, "вага(s₂) ≤ 3 ?",
                        size=17, fill=AMB_F, stroke=AMB_S, sw=1.8, bold=True))
    frags.append(fitbox(LX, rows[5], LW, BH, "є рядок i:  вага(s₂ ⊕ Bᵢ) ≤ 2 ?",
                        size=15, fill=AMB_F, stroke=AMB_S, sw=1.8, bold=True))
    frags.append(fitbox(LX, rows[6], LW, BH, "НЕВИПРАВНО:  4+ помилки — чесне «ні»",
                        size=15, fill="#fdecea", stroke=POS, sw=1.9, bold=True))

    outs = {
        1: ("e = [ 0 | s ]", "усі помилки — в перевірній половині"),
        2: ("e = [ eᵢ | s ⊕ Bᵢ ]", "один зіпсований біт даних"),
        4: ("e = [ s₂ | 0 ]", "усі помилки — в половині даних"),
        5: ("e = [ s₂ ⊕ Bᵢ | eᵢ ]", "один зіпсований перевірний біт"),
    }
    for r, (a, b) in outs.items():
        y = rows[r]
        frags.append(rect(RX, y, RW, BH, fill="#e9f7ef", stroke=FIELD, sw=1.7, rx=8))
        frags.append(text(rcx, y + 26, a, size=16, bold=True))
        frags.append(text(rcx, y + 46, b, size=12, color=MUTED))

    for i in range(6):
        frags.append(arrow(lcx, rows[i] + BH, lcx, rows[i + 1], color=INK, sw=1.8))
    for r in (1, 2, 4, 5):
        frags.append(text(lcx + 10, rows[r] + BH + 18, "ні", size=12,
                          color=MUTED, anchor="start"))
        y = rows[r] + BH / 2
        frags.append(arrow(LX + LW, y, RX, y, color=FIELD, sw=2))
        frags.append(text((LX + LW + RX) / 2, y - 8, "так", size=13,
                          color=FIELD, bold=True))

    render(os.path.join(OUT, "decode-flow.svg"), W, H, *frags,
           title="Декодування: синдром → рядки B → до 3 виправлень, 4-та відхилена")


if __name__ == "__main__":
    fig_packing()
    fig_family()
    fig_generator()
    fig_qr23()
    fig_convergence()
    fig_encode()
    fig_decode()
    print("OK: perfect-packing.svg, golay-family.svg, generator-matrix.svg, "
          "qr23-circle.svg, many-roads.svg, codeword-layout.svg, decode-flow.svg")
