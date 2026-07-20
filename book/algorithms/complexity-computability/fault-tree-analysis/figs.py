# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

BLUE_R = "#2457d6"
GREEN  = "#27ae60"
RED    = "#c0392b"
GREY   = "#9aa3af"
TINT = {BLUE_R: "#eaf0fd", GREEN: "#eaf7ee", RED: "#fdecea", GREY: "#eef1f4", INK: "#eef2f7"}


# ── елементи мови дерева відмов ────────────────────────────────────────────────
def gate_and(cx, cy, w=60, h=52, fill=TINT[INK], stroke=LINE, label="І"):
    """Вентиль І: пласке дно (входи), напівкругла баня (вихід угору)."""
    hw = w / 2.0
    top, bot = cy - h / 2.0, cy + h / 2.0
    spring = top + hw
    if spring > bot - 4:
        spring = bot - 6
    d = ("M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f L %.1f %.1f Z"
         % (cx - hw, bot, cx - hw, spring, hw, hw, cx + hw, spring, cx + hw, bot))
    out = '<path d="%s" fill="%s" stroke="%s" stroke-width="2.2"/>' % (d, fill, stroke)
    out += text(cx, cy + 16, label, size=14, color=INK, bold=True)
    return out


def gate_or(cx, cy, w=64, h=54, fill=TINT[INK], stroke=LINE, label="АБО"):
    """Вентиль АБО: увігнуте дно, вигнуті боки, гострий верх."""
    hw = w / 2.0
    top, bot = cy - h / 2.0, cy + h / 2.0
    conc = 13.0
    d = ("M %.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f Q %.1f %.1f %.1f %.1f Z"
         % (cx - hw, bot,
            cx, bot - conc, cx + hw, bot,
            cx + hw + 7, cy - 3, cx, top,
            cx - hw - 7, cy - 3, cx - hw, bot))
    out = '<path d="%s" fill="%s" stroke="%s" stroke-width="2.2"/>' % (d, fill, stroke)
    out += text(cx, cy + 12, label, size=12, color=INK, bold=True)
    return out


def basic_event(cx, cy, label, r=27, color=BLUE_R):
    """Базова подія — кружечок; підпис ПІД ним, щоб не тіснити текст."""
    out = circle(cx, cy, r, fill=TINT[color], stroke=color, sw=2.2)
    lines = label.split("\n")
    out += mtext(cx, cy + r + 18, lines, size=12, color=INK, lh=1.25)
    return out


def event_box(cx, cy, s, color=INK, fill="#fbfcfd"):
    body, w, h = textbox(cx, cy, s, size=13, pad=12, fill=fill, stroke=color, sw=2.0, bold=True)
    return body, w, h


# ── ФІГ.1  Мова дерева: вершинна подія, вентилі І/АБО, базові події ─────────────
def fig_fault_tree():
    W, H = 820, 600
    p = []

    yTE, yOR, yPow, yMid, yAND, yPump = 60, 152, 300, 288, 388, 512
    xL, xR = 220, 600
    xPA, xPB = 505, 695

    # вершинна подія
    te, teW, teH = event_box(410, yTE, "Втрата\nохолодження", color=RED, fill=TINT[RED])
    p.append(te)
    # вентиль АБО під нею
    p.append(gate_or(410, yOR))
    # з'єднання: вершина → АБО
    p.append(line(410, yTE + teH / 2, 410, yOR - 27, color=LINE, sw=1.6))

    # шина під АБО до двох дітей
    yBus = 226
    p.append(line(410, yOR + 27, 410, yBus, color=LINE, sw=1.6))
    p.append(line(xL, yBus, xR, yBus, color=LINE, sw=1.6))
    p.append(line(xL, yBus, xL, yPow - 27, color=LINE, sw=1.6))

    # ліва дитина — базова подія «живлення»
    p.append(basic_event(xL, yPow, "Відмова\nживлення", color=BLUE_R))

    # права дитина — проміжна подія + вентиль І
    mid, midW, midH = event_box(xR, yMid, "Стали обидва\nнасоси")
    p.append(line(xR, yBus, xR, yMid - midH / 2, color=LINE, sw=1.6))
    p.append(mid)
    p.append(line(xR, yMid + midH / 2, xR, yAND - 26, color=LINE, sw=1.6))
    p.append(gate_and(xR, yAND))

    # шина під І до двох насосів
    yBus2 = 456
    p.append(line(xR, yAND + 26, xR, yBus2, color=LINE, sw=1.6))
    p.append(line(xPA, yBus2, xPB, yBus2, color=LINE, sw=1.6))
    p.append(line(xPA, yBus2, xPA, yPump - 27, color=LINE, sw=1.6))
    p.append(line(xPB, yBus2, xPB, yPump - 27, color=LINE, sw=1.6))
    p.append(basic_event(xPA, yPump, "Насос A", color=BLUE_R))
    p.append(basic_event(xPB, yPump, "Насос B", color=BLUE_R))

    # легенда праворуч угорі
    lx = 640
    p.append(rect(lx, 44, 158, 96, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(lx + 79, 66, "позначення", size=12, color=MUTED, bold=True))
    p.append(gate_or(lx + 26, 92, w=30, h=26, label=""))
    p.append(text(lx + 50, 96, "вентиль АБО", size=11, color=INK, anchor="start"))
    p.append(gate_and(lx + 26, 122, w=28, h=24, label=""))
    p.append(text(lx + 50, 124, "вентиль І", size=11, color=INK, anchor="start"))

    render(os.path.join(OUT, "fault-tree.svg"), W, H, *p)


# ── ФІГ.2  Мінімальні перерізи: одноелементний (єдина точка) vs двоелементний ──
def fig_cut_sets():
    W, H = 820, 396
    p = []

    def chip(cx, cy, s, color):
        w = text_width(s, 13, True) + 26
        out = rect(cx - w / 2, cy - 17, w, 34, fill="#ffffff", stroke=color, sw=1.9, rx=9)
        out += text(cx, cy + 5, s, size=13, color=INK, bold=True)
        return out, w

    # булева функція дерева вгорі
    b, bw, bh = textbox(410, 52, "ВТРАТА = ЖИВЛЕННЯ  ∨  (НАСОС A  ∧  НАСОС B)",
                        size=14, pad=12, fill="#fbfcfd", stroke=MUTED, sw=1.3, bold=True)
    p.append(b)
    p.append(text(410, 92, "найменші набори відмов, що валять систему:", size=12, color=MUTED))

    # картка 1 — переріз розміру 1 (небезпека)
    p.append(rect(70, 120, 300, 196, fill=TINT[RED], stroke=RED, sw=2.2, rx=12))
    p.append(text(220, 150, "Переріз 1", size=15, color=INK, bold=True))
    c1, _ = chip(220, 196, "ЖИВЛЕННЯ", RED)
    p.append(c1)
    p.append(mtext(220, 244, ["порядок 1 — валить САМ", "єдина точка відмови"],
                   size=13, color=RED, bold=True))
    p.append(text(220, 296, "одна поломка = кінець", size=11, color=MUTED))

    # картка 2 — переріз розміру 2 (безпечніше)
    p.append(rect(450, 120, 300, 196, fill=TINT[BLUE_R], stroke=BLUE_R, sw=2.2, rx=12))
    p.append(text(600, 150, "Переріз 2", size=15, color=INK, bold=True))
    c2a, w2a = chip(556, 196, "НАСОС A", BLUE_R)
    c2b, w2b = chip(646, 196, "НАСОС B", BLUE_R)
    p.append(c2a)
    p.append(c2b)
    p.append(mtext(600, 244, ["порядок 2 — потрібні", "ОБИДВІ поломки разом"],
                   size=13, color=BLUE_R, bold=True))
    p.append(text(600, 296, "переживе будь-яку одну", size=11, color=MUTED))

    p.append(text(410, 356, "перерізи = прості імпліканти булевої функції; порядок найменшого — це міра крихкості",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "cut-sets.svg"), W, H, *p)


# ── ФІГ.3  Стіна складності: незалежні гілки (легко) vs спільна подія (#P) ──────
def fig_complexity_wall():
    W, H = 1000, 556
    p = []
    xWall = 372

    # ── ЛІВА панель: без спільних подій ──
    p.append(text(196, 66, "БЕЗ спільних подій", size=14, color=GREEN, bold=True))
    p.append(text(196, 88, "кожна подія — раз у дереві", size=11, color=MUTED))

    # дві базові події → вентиль → вершина
    p.append(basic_event(120, 250, "", r=17, color=GREEN))
    p.append(basic_event(272, 250, "", r=17, color=GREEN))
    p.append(gate_and(196, 190, w=44, h=38, label=""))
    p.append(line(120, 233, 150, 208, color=LINE, sw=1.5))
    p.append(line(272, 233, 242, 208, color=LINE, sw=1.5))
    p.append(rect(160, 120, 72, 34, fill="#fbfcfd", stroke=GREEN, sw=2.0, rx=7))
    p.append(text(196, 142, "вершина", size=11, color=INK, bold=True))
    p.append(line(196, 164, 196, 120 + 34, color=LINE, sw=1.5))

    # велика стрілка «знизу вгору»
    p.append(arrow(320, 250, 320, 140, color=GREEN, sw=2.6))
    p.append(mtext(340, 210, ["знизу", "вгору"], size=11, color=GREEN, anchor="start", bold=True))

    box, _, _ = textbox(196, 330, "×  та  1 − ∏(1−pᵢ)", size=13, pad=10,
                        fill="#ffffff", stroke=GREEN, sw=1.8, color=INK, bold=True)
    p.append(box)
    stamp, _, _ = textbox(196, 400, "O(n) — лінійно, легко", size=14, pad=12,
                          fill=TINT[GREEN], stroke=GREEN, sw=2.2, color=INK, bold=True)
    p.append(stamp)

    # ── СТІНА ──
    p.append(line(xWall, 52, xWall, 470, color=MUTED, sw=1.4, dash="6 5"))
    p.append(mtext(xWall, 30, ["межа обчислюваного"], size=12, color=MUTED, bold=True))

    # ── ПРАВА панель: зі спільною подією ──
    xr = 690
    p.append(text(xr, 66, "ЗІ спільною подією", size=14, color=RED, bold=True))
    p.append(text(xr, 88, "одна деталь живить дві гілки", size=11, color=MUTED))

    # два вентилі, у які веде та сама подія X
    p.append(gate_or(xr - 120, 168, w=48, h=42, label=""))
    p.append(gate_or(xr + 120, 168, w=48, h=42, label=""))
    p.append(text(xr - 120, 138, "гілка 1", size=11, color=MUTED))
    p.append(text(xr + 120, 138, "гілка 2", size=11, color=MUTED))
    p.append(basic_event(xr, 268, "", r=22, color=RED))
    p.append(text(xr, 274, "X", size=16, color=INK, bold=True))
    p.append(text(xr, 316, "спільна подія", size=11, color=RED, bold=True))
    p.append(arrow(xr - 16, 250, xr - 120, 192, color=RED, sw=2.0))
    p.append(arrow(xr + 16, 250, xr + 120, 192, color=RED, sw=2.0))

    warn, _, _ = textbox(xr, 384, "гілки НЕ незалежні — множити не можна", size=12, pad=11,
                         fill="#ffffff", stroke=RED, sw=1.8, color=INK, bold=True)
    p.append(warn)
    hard, _, _ = textbox(xr, 438, "точний розрахунок #P-складний · включення-виключення: 2ᵐ доданків",
                         size=12, pad=11, fill=TINT[RED], stroke=RED, sw=2.2, color=INK, bold=True)
    p.append(hard)

    # ── нижня смуга: обхідні шляхи ──
    p.append(line(40, 486, W - 40, 486, color=MUTED, sw=1.0))
    p.append(text(58, 531, "обхід:", size=12, color=INK, bold=True, anchor="start"))
    esc = [(300, "сума перерізів — оцінка зверху", GREEN),
           (598, "BDD — точно, поки компактний", BLUE_R),
           (852, "Монте-Карло — наближено", MUTED)]
    for cx, s, col in esc:
        w = text_width(s, 11) + 22
        p.append(rect(cx - w / 2, 512, w, 30, fill=TINT.get(col, "#fbfcfd"), stroke=col, sw=1.6, rx=8))
        p.append(text(cx, 531, s, size=11, color=INK))

    render(os.path.join(OUT, "complexity-wall.svg"), W, H, *p)


# ── ФІГ.4 (hist)  Дві ери народження методу: зброя → ядро ───────────────────────
def fig_history_timeline():
    W, H = 1130, 560
    p = []

    bY0, bY1 = 70, 500
    b1x0, b1x1 = 60, 565
    b2x0, b2x1 = 600, 1070
    axisY = 285
    TR, TB = "#fdecea", "#eaf0fd"

    # смуги двох ер (позаду всього)
    p.append(rect(b1x0, bY0, b1x1 - b1x0, bY1 - bY0, fill=TR, stroke=RED, sw=1.6, rx=14))
    p.append(rect(b2x0, bY0, b2x1 - b2x0, bY1 - bY0, fill=TB, stroke=BLUE_R, sw=1.6, rx=14))

    # заголовки ер + пауза між ними
    p.append(text((b1x0 + b1x1) / 2, 52, "ЕРА ЗБРОЇ — ракетний щит", size=14, color=RED, bold=True))
    p.append(text((b2x0 + b2x1) / 2, 52, "ЕРА ЯДРА — безпека АЕС", size=14, color=BLUE_R, bold=True))
    p.append(line(582, bY0, 582, bY1, color=GREY, sw=1.2, dash="5 5"))
    p.append(text(582, 52, "пауза ≈10 років", size=11, color=MUTED))

    # вісь часу
    p.append(arrow(96, axisY, 1058, axisY, color=INK, sw=2.4))
    p.append(text(1040, axisY - 12, "час", size=11, color=MUTED))

    def milestone(cx, year, lines, color, above):
        out = circle(cx, axisY, 6, fill=color, stroke=color, sw=1.5)
        if above:
            out += line(cx, axisY - 6, cx, 214, color=color, sw=1.6)
            out += text(cx, 202, year, size=15, color=color, bold=True)
            box, _, _ = textbox(cx, 148, "\n".join(lines), size=12, pad=11,
                                fill="#ffffff", stroke=color, sw=1.9, color=INK, bold=True, rx=9)
            out += box
        else:
            out += line(cx, axisY + 6, cx, 366, color=color, sw=1.6)
            out += text(cx, 384, year, size=15, color=color, bold=True)
            box, _, _ = textbox(cx, 432, "\n".join(lines), size=12, pad=11,
                                fill="#ffffff", stroke=color, sw=1.9, color=INK, bold=True, rx=9)
            out += box
        return out

    p.append(milestone(172, "1962", ["Вотсон і Мірнз", "(Bell Labs)", "«Мінітмен I»"], RED, True))
    p.append(milestone(330, "1963–64", ["Boeing підхоплює", "весь «Мінітмен II»"], RED, False))
    p.append(milestone(485, "1965", ["1-й симпозіум", "системної безпеки", "Сіетл"], RED, True))
    p.append(milestone(690, "1975", ["WASH-1400", "Расмуссен, Левін", "ризик цілої АЕС"], BLUE_R, False))
    p.append(milestone(855, "1977–78", ["Комітет Льюїса:", "«непевність", "дуже занижено»"], BLUE_R, True))
    p.append(milestone(985, "1981", ["NUREG-0492", "Fault Tree Handbook", "метод у каноні"], BLUE_R, False))

    # підсумкова смуга
    p.append(line(60, 515, 1070, 515, color=MUTED, sw=1.0))
    p.append(text(565, 537,
                  "Двічі викуваний там, де помилка означала ядерну катастрофу, — звідси сувора формальність методу.",
                  size=12, color=INK))

    render(os.path.join(OUT, "history-timeline.svg"), W, H, *p)


# ── ФІГ.5 (math)  Зважений підрахунок моделей: таблиця всіх 2ⁿ станів ────────────
def fig_weighted_count():
    W, H = 940, 600
    p = []
    p.append(text(400, 40, "Ймовірність вершини — зважений підрахунок моделей", size=16, color=INK, bold=True))
    p.append(text(400, 64, "система «2 з 3», p = 0.1  ·  біт: 0 — ціла, 1 — відмовила", size=12, color=MUTED))

    x0, tW = 70, 630
    cA, cB, cC, cSys, cW = 150, 205, 260, 410, 600
    yHead = 100
    rowH = 48
    yTop = yHead + 20

    p.append(rect(x0, yHead - 22, tW, 42, fill=TINT[INK], stroke=MUTED, sw=1.2, rx=8))
    for cx, s in [(cA, "A"), (cB, "B"), (cC, "C"), (cSys, "стан системи"), (cW, "вага w(x)")]:
        p.append(text(cx, yHead + 5, s, size=13, color=INK, bold=True))

    rows = [
        ("0", "0", "0", "жива",  "0.729", False),
        ("0", "0", "1", "жива",  "0.081", False),
        ("0", "1", "0", "жива",  "0.081", False),
        ("1", "0", "0", "жива",  "0.081", False),
        ("0", "1", "1", "ВПАЛА", "0.009", True),
        ("1", "0", "1", "ВПАЛА", "0.009", True),
        ("1", "1", "0", "ВПАЛА", "0.009", True),
        ("1", "1", "1", "ВПАЛА", "0.001", True),
    ]
    for i, (a, b, c, st, wv, fail) in enumerate(rows):
        ry = yTop + i * rowH
        if fail:
            p.append(rect(x0, ry, tW, rowH, fill=TINT[RED], stroke="none", sw=0, rx=0))
        cy = ry + rowH / 2 + 5
        col = RED if fail else GREEN
        p.append(text(cA, cy, a, size=13, color=INK))
        p.append(text(cB, cy, b, size=13, color=INK))
        p.append(text(cC, cy, c, size=13, color=INK))
        p.append(text(cSys, cy, st, size=12, color=col, bold=fail))
        p.append(text(cW, cy, wv, size=13, color=(RED if fail else INK), bold=fail))

    p.append(rect(x0, yTop, tW, 8 * rowH, fill="none", stroke=MUTED, sw=1.2, rx=8))
    for xsep in [285, 520]:
        p.append(line(xsep, yTop, xsep, yTop + 8 * rowH, color=GREY, sw=1.0))

    res, _, _ = textbox(400, 560,
                        "P(вершина) = сума ваг рядків «ВПАЛА» = 0.009+0.009+0.009+0.001 = 0.028",
                        size=13, pad=11, fill=TINT[GREEN], stroke=GREEN, sw=2.0, color=INK, bold=True)
    p.append(res)

    n1, w1, _ = textbox(830, 235, "перевірити\nОДИН рядок:\nпідстав біти,\nпройди дерево\n— O(n)",
                        size=12, pad=11, fill=TINT[GREEN], stroke=GREEN, sw=1.8, color=INK)
    p.append(line(x0 + tW, yTop + rowH * 1.5, 830 - w1 / 2, 235, color=GREEN, sw=1.3))
    p.append(n1)
    n2, w2, _ = textbox(830, 430, "просумувати\nВСІ 2ⁿ рядків\n— ось де\nекспонента",
                        size=12, pad=11, fill=TINT[RED], stroke=RED, sw=1.8, color=INK)
    p.append(line(x0 + tW, yTop + rowH * 6, 830 - w2 / 2, 430, color=RED, sw=1.3))
    p.append(n2)

    render(os.path.join(OUT, "weighted-count.svg"), W, H, *p)


# ── ФІГ.6 (math)  Включення-виключення: перекриття перерізів і 2ᵐ−1 доданків ─────
def fig_inclusion_exclusion():
    W, H = 900, 520
    p = []
    p.append(text(250, 34, "Перекровні перерізи → експонента доданків", size=15, color=INK, bold=True))

    def vc(cx, cy, r, color):
        return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.26" '
                'stroke="%s" stroke-width="2.2"/>' % (cx, cy, r, color, color))

    R = 92
    p.append(vc(235, 210, R, RED))
    p.append(vc(360, 210, R, BLUE_R))
    p.append(vc(297, 298, R, GREEN))
    p.append(text(185, 168, "C₁", size=16, color=RED, bold=True))
    p.append(text(410, 168, "C₂", size=16, color=BLUE_R, bold=True))
    p.append(text(297, 376, "C₃", size=16, color=GREEN, bold=True))
    p.append(arrow(150, 452, 285, 250, color=MUTED, sw=1.6))
    note, _, _ = textbox(150, 468, "спільні базові події → перетин ≠ 0", size=11, pad=9,
                         fill="#ffffff", stroke=MUTED, sw=1.3, color=INK)
    p.append(note)

    xs, xt, xn = 505, 545, 762
    p.append(text(505, 96, "P(C₁ ∨ C₂ ∨ C₃) =", size=15, color=INK, bold=True, anchor="start"))
    rows_ie = [
        (150, "+", GREEN,  "(P₁ + P₂ + P₃)",    "3 одинарні"),
        (196, "−", BLUE_R, "(P₁₂ + P₁₃ + P₂₃)", "3 парні"),
        (242, "+", GREEN,  "P₁₂₃",              "1 потрійний"),
    ]
    for y, sg, col, term, nt in rows_ie:
        p.append(text(xs, y, sg, size=18, color=col, bold=True, anchor="start"))
        p.append(text(xt, y, term, size=15, color=INK, anchor="start"))
        p.append(text(xn, y, "← " + nt, size=12, color=MUTED, anchor="start"))

    s1, _, _ = textbox(690, 305, "3 + 3 + 1 = 7 = 2³ − 1 доданків", size=13, pad=10,
                       fill=TINT[INK], stroke=MUTED, sw=1.4, color=INK, bold=True)
    p.append(s1)
    p.append(text(690, 362, "для m перерізів:", size=13, color=MUTED))
    big, _, _ = textbox(690, 415, "2ᵐ − 1 доданків  →  експонента", size=15, pad=13,
                        fill=TINT[RED], stroke=RED, sw=2.4, color=INK, bold=True)
    p.append(big)
    render(os.path.join(OUT, "inclusion-exclusion.svg"), W, H, *p)


# ── ФІГ.7 (math)  Межі Бонферроні: частинні суми затискають істинне P ────────────
def fig_bonferroni():
    W, H = 860, 470
    p = []
    p.append(text(360, 32, "Частинні суми затискають істинне P — межі Бонферроні", size=15, color=INK, bold=True))

    xL, xR = 150, 600
    yT, yB = 90, 360
    vmin, vmax = 0.0258, 0.0312

    def yv(v):
        return yB - (v - vmin) / (vmax - vmin) * (yB - yT)

    p.append(line(xL, yT - 6, xL, yB, color=MUTED, sw=1.2))
    p.append(line(xL, yB, xR, yB, color=MUTED, sw=1.2))

    yP = yv(0.028)
    p.append(line(xL, yP, xR, yP, color=GREEN, sw=1.6, dash="7 5"))
    p.append(text(xR + 12, yP + 5, "істинне P = 0.028", size=12, color=GREEN, bold=True, anchor="start"))

    p.append(text(xL - 10, yv(0.030) + 4, "0.030", size=11, color=MUTED, anchor="end"))
    p.append(text(xL - 10, yv(0.027) + 4, "0.027", size=11, color=MUTED, anchor="end"))

    xs = [230, 370, 510]
    vs = [0.030, 0.027, 0.028]
    cols = [RED, BLUE_R, GREEN]
    pts = [(xs[i], yv(vs[i])) for i in range(3)]
    p.append(line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], color=GREY, sw=1.8))
    p.append(line(pts[1][0], pts[1][1], pts[2][0], pts[2][1], color=GREY, sw=1.8))
    for (px, py), col in zip(pts, cols):
        p.append(circle(px, py, 7, fill=col, stroke="#ffffff", sw=1.6))

    p.append(text(230, yv(0.030) - 14, "S₁ = 0.030", size=13, color=RED, bold=True))
    p.append(text(370, yv(0.027) + 24, "S₂ = 0.027", size=13, color=BLUE_R, bold=True))
    p.append(text(510, yv(0.028) - 14, "S₃ = 0.028", size=13, color=GREEN, bold=True))

    p.append(mtext(230, yB + 26, ["одинарні перерізи", "(межа зверху)"], size=11, color=MUTED))
    p.append(mtext(370, yB + 26, ["− парні перетини", "(межа знизу)"], size=11, color=MUTED))
    p.append(mtext(510, yB + 26, ["+ потрійний", "(точно)"], size=11, color=MUTED))

    note, _, _ = textbox(725, 150, "рідкісні події:\nперекриття мізерні →\nS₁ ≈ P, безпечна\nоцінка зверху",
                         size=12, pad=11, fill=TINT[GREEN], stroke=GREEN, sw=1.8, color=INK)
    p.append(note)

    p.append(text(430, 440,
                  "непарні члени — зверху, парні — знизу; більше членів → тісніше кільце  ·  нерівності Бонферроні, 1936",
                  size=12, color=MUTED))
    render(os.path.join(OUT, "bonferroni.svg"), W, H, *p)


# ── ФІГ.6 (proj)  MOCUS: розгортання дерева в матрицю перерізів ──────────────────
def fig_mocus_expansion():
    W, H = 1080, 660
    p = []
    p.append(text(W / 2, 40, "MOCUS: розгортання дерева в матрицю перерізів", size=16, color=INK, bold=True))
    p.append(text(W / 2, 64, "рядок матриці — набір відмов, що разом валять систему; згори вниз розкриваємо вентилі",
                  size=12, color=MUTED))

    RH, GAP = 44, 18

    def chip(cx, cy, s, kind):
        col = RED if kind == "gate" else BLUE_R
        fill = TINT[RED] if kind == "gate" else TINT[BLUE_R]
        w = max(128, text_width(s, 14, True) + 36)
        out = rect(cx - w / 2, cy - RH / 2, w, RH, fill=fill, stroke=col, sw=2.0, rx=10)
        out += text(cx, cy + 5, s, size=14, color=INK, bold=True)
        return out

    def stage(cx, ytop, title, rows):
        out = text(cx, ytop, title, size=13, color=INK, bold=True)
        y = ytop + 34 + RH / 2
        for s, kind in rows:
            out += chip(cx, y, s, kind)
            y += RH + GAP
        return out

    yT = 150
    p.append(stage(160, yT, "старт: вершина", [("TOP", "gate")]))
    p.append(stage(535, yT, "АБО → 2 рядки", [("POWER", "basic"), ("PUMPS", "gate")]))
    p.append(stage(910, yT, "І → ширший рядок", [("POWER", "basic"), ("A · B", "basic")]))

    yA = yT + 52
    p.append(arrow(255, yA, 430, yA, color=INK, sw=2.4))
    p.append(mtext(342, yA - 22, ["вентиль АБО", "МНОЖИТЬ рядки"], size=12, color=RED, bold=True))
    p.append(text(342, yA + 34, "TOP = POWER ∨ PUMPS", size=11, color=MUTED))
    p.append(arrow(632, yA, 805, yA, color=INK, sw=2.4))
    p.append(mtext(718, yA - 22, ["вентиль І", "ДОПИСУЄ стовпці"], size=12, color=BLUE_R, bold=True))
    p.append(text(718, yA + 34, "PUMPS = A ∧ B", size=11, color=MUTED))

    # поглинання
    ab, _, _ = textbox(W / 2, 356, "усі елементи базові → перерізи знайдено.  Поглинання прибирає надмножинні:  {A} ⊂ {A, B}  ⟹  {A, B} геть",
                       size=12, pad=12, fill=TINT[GREEN], stroke=GREEN, sw=1.8, color=INK, bold=True)
    p.append(ab)

    # ── смуга вибуху ──
    p.append(line(50, 404, W - 50, 404, color=MUTED, sw=1.0))
    p.append(text(W / 2, 434, "Чому число перерізів вибухає", size=14, color=RED, bold=True))
    p.append(mtext(270, 476,
                   ["добуток сум — n резервованих пар:",
                    "TOP = (a₁∨b₁) ∧ (a₂∨b₂) ∧ … ∧ (aₙ∨bₙ)",
                    "",
                    "кожна пара незалежно дає a або b —",
                    "тож рядків 2·2·…·2 = 2ⁿ, по одному",
                    "на кожен вибір гілок."],
                   size=12, color=INK, lh=1.45))

    # драбина подвоєння
    bx0, base = 600, 596
    labels = [("1", 2), ("2", 4), ("3", 8), ("4", 16), ("5", 32), ("6", 64)]
    for i, (nlab, cnt) in enumerate(labels):
        cx = bx0 + i * 72
        h = 7 * (2 ** i)
        col = GREEN if i < 2 else (BLUE_R if i < 4 else RED)
        p.append(rect(cx - 24, base - h, 48, h, fill=TINT[col], stroke=col, sw=1.8, rx=4))
        p.append(text(cx, base - h - 8, "2%s" % "⁰¹²³⁴⁵⁶⁷⁸⁹"[i + 1], size=12, color=col, bold=True))
        p.append(text(cx, base + 18, "n=%s" % nlab, size=11, color=MUTED))
    p.append(text(bx0 + 3 * 72 - 36, 452, "рядків = 2ⁿ", size=12, color=RED, bold=True))

    render(os.path.join(OUT, "mocus-expansion.svg"), W, H, *p)


# ── ФІГ.7 (proj)  BDD: точна ймовірність одним проходом + ціна порядку ───────────
def fig_bdd_eval():
    W, H = 1120, 640
    p = []
    p.append(text(W / 2, 38, "BDD: точна ймовірність одним проходом знизу вгору", size=16, color=INK, bold=True))
    p.append(text(W / 2, 62, "у кожному вузлі — розклад Шеннона по змінній; гілки «ціла» і «відмовила» взаємовиключні → ймовірності складаються",
                  size=12, color=MUTED))

    def bnode(cx, cy, label, r=27):
        out = circle(cx, cy, r, fill=TINT[INK], stroke=INK, sw=2.3)
        out += text(cx, cy + 5, label, size=12, color=INK, bold=True)
        return out

    def terminal(cx, cy, val):
        col = RED if val == 1 else GREY
        out = rect(cx - 22, cy - 20, 44, 40, fill=TINT[col], stroke=col, sw=2.3, rx=6)
        out += text(cx, cy + 6, str(val), size=17, color=INK, bold=True)
        return out

    P0 = (250, 140)   # POWER
    PA = (185, 285)   # PUMP_A
    PB = (330, 420)   # PUMP_B
    T0 = (185, 545)   # FALSE
    T1 = (455, 545)   # TRUE

    # ребра: суцільне червоне = відмовила (1, hi), пунктир сірий = ціла (0, lo)
    p.append(line(P0[0], P0[1], PA[0], PA[1], color=GREY, sw=1.9, dash="6 4"))
    p.append(line(P0[0], P0[1], T1[0], T1[1], color=RED, sw=2.1))
    p.append(line(PA[0], PA[1], T0[0], T0[1], color=GREY, sw=1.9, dash="6 4"))
    p.append(line(PA[0], PA[1], PB[0], PB[1], color=RED, sw=2.1))
    p.append(line(PB[0], PB[1], T0[0], T0[1], color=GREY, sw=1.9, dash="6 4"))
    p.append(line(PB[0], PB[1], T1[0], T1[1], color=RED, sw=2.1))

    # мітки гілок 0/1 біля виходів
    p.append(text(205, 205, "0", size=12, color=GREY, bold=True))
    p.append(text(360, 300, "1", size=12, color=RED, bold=True))
    p.append(text(168, 415, "0", size=12, color=GREY, bold=True))
    p.append(text(268, 345, "1", size=12, color=RED, bold=True))
    p.append(text(240, 495, "0", size=12, color=GREY, bold=True))
    p.append(text(408, 490, "1", size=12, color=RED, bold=True))

    p.append(bnode(*P0, "POWER"))
    p.append(bnode(*PA, "PUMP_A"))
    p.append(bnode(*PB, "PUMP_B"))
    p.append(terminal(*T0, 0))
    p.append(terminal(*T1, 1))
    p.append(text(T0[0], T0[1] + 38, "система ціла", size=10, color=MUTED))
    p.append(text(T1[0], T1[1] + 38, "відмова", size=10, color=MUTED))

    # ймовірності, що спливають угору
    p.append(text(P0[0] + 74, P0[1] - 2, "P = 0.0011", size=12, color=INK, bold=True, anchor="start"))
    p.append(text(PA[0] - 78, PA[1] + 2, "P = 0.0001", size=12, color=INK, bold=True, anchor="end"))
    p.append(text(PB[0] + 44, PB[1] + 2, "P = 0.01", size=12, color=INK, bold=True, anchor="start"))

    # формула проходу
    fb, _, _ = textbox(300, 118, "P(вузол) = (1−p)·P(0-гілка) + p·P(1-гілка)", size=12, pad=10,
                       fill="#ffffff", stroke=INK, sw=1.6, color=INK, bold=True)
    p.append(fb)

    # легенда ребер
    lx, ly = 60, 470
    p.append(line(lx, ly, lx + 34, ly, color=RED, sw=2.1))
    p.append(text(lx + 42, ly + 4, "відмовила (1)", size=10, color=INK, anchor="start"))
    p.append(line(lx, ly + 22, lx + 34, ly + 22, color=GREY, sw=1.9, dash="6 4"))
    p.append(text(lx + 42, ly + 26, "ціла (0)", size=10, color=INK, anchor="start"))

    # ── ПРАВА панель: ціна порядку змінних ──
    p.append(line(560, 92, 560, 600, color=MUTED, sw=1.2, dash="5 5"))
    xr = 840
    p.append(text(xr, 118, "Ціна порядку змінних", size=15, color=INK, bold=True))
    p.append(text(xr, 140, "n резервованих пар: (a₁∧b₁) ∨ … ∨ (aₙ∧bₙ)", size=11, color=MUTED))

    good, _, _ = textbox(xr, 196, "добрий порядок: переплести пари\na₁ b₁ a₂ b₂ … aₙ bₙ", size=12, pad=12,
                         fill=TINT[GREEN], stroke=GREEN, sw=2.0, color=INK, bold=True)
    p.append(good)
    bad, _, _ = textbox(xr, 280, "поганий порядок: усі a, потім усі b\na₁ a₂ … aₙ b₁ b₂ … bₙ", size=12, pad=12,
                        fill=TINT[RED], stroke=RED, sw=2.0, color=INK, bold=True)
    p.append(bad)

    # стовпчики розміру діаграми (n=10)
    p.append(text(xr, 348, "розмір діаграми, n = 10 пар", size=12, color=INK, bold=True))
    base2 = 560
    gx = 720
    p.append(rect(gx - 34, base2 - 30, 68, 30, fill=TINT[GREEN], stroke=GREEN, sw=2.0, rx=5))
    p.append(text(gx, base2 - 10, "120", size=13, color=INK, bold=True))
    p.append(text(gx, base2 + 20, "добрий → полиноміально", size=10, color=GREEN, bold=True))
    bx = 960
    p.append(rect(bx - 40, base2 - 170, 80, 170, fill=TINT[RED], stroke=RED, sw=2.0, rx=5))
    p.append(text(bx, base2 - 178, "3069", size=13, color=INK, bold=True))
    p.append(text(bx, base2 + 20, "поганий → ≈ 3·2ⁿ", size=10, color=RED, bold=True))

    p.append(mtext(xr, 592, ["та сама функція, той самий результат — інший лише РОЗМІР;",
                             "поганий порядок оживляє #P-стіну зсередини діаграми"],
                   size=11, color=MUTED, lh=1.4))

    render(os.path.join(OUT, "bdd-eval.svg"), W, H, *p)


if __name__ == "__main__":
    fig_fault_tree()
    fig_cut_sets()
    fig_complexity_wall()
    fig_history_timeline()
    fig_weighted_count()
    fig_inclusion_exclusion()
    fig_bonferroni()
    fig_mocus_expansion()
    fig_bdd_eval()
    print("figs OK:", os.listdir(OUT))
