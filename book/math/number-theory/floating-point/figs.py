# -*- coding: utf-8 -*-
"""Фігури до статті «Числа з рухомою комою» (book/math/number-theory/floating-point).
Запуск із теки теми:  python figs.py   → SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── Фігура A: куди поставити мітки — рівні кроки проти геометричних ──────────
def fig_placement():
    W, H = 880, 380
    xs = [70 + i * 90 for i in range(9)]          # 9 міток, однакові позиції
    f = []

    # верхній рядок — рівні кроки (+1)
    f.append(text(W / 2, 78, "Рівні кроки (+1): вистачає лише до 8", size=15, bold=True))
    f.append(arrow(70, 130, 822, 130, sw=1.8))
    top = ['0', '1', '2', '3', '4', '5', '6', '7', '8']
    for x, lab in zip(xs, top):
        f.append(line(x, 124, x, 136, sw=1.6))
        f.append(text(x, 159, lab, size=14))

    # нижній рядок — геометричні кроки (×2)
    f.append(text(W / 2, 252, "Кроки ×2: ті самі мітки дотягуються до 256 — у 32 рази далі",
                  size=15, bold=True))
    f.append(arrow(70, 302, 822, 302, sw=1.8))
    bot = ['1', '2', '4', '8', '16', '32', '64', '128', '256']
    for x, lab in zip(xs, bot):
        f.append(line(x, 296, x, 308, sw=1.6))
        f.append(text(x, 331, lab, size=14))
    for i in range(8):                             # позначки ×2 між сусідами
        mx = (xs[i] + xs[i + 1]) / 2
        f.append(text(mx, 289, "×2", size=11, color=POS))

    f.append(text(W / 2, 363, "проміжки між сусідніми значеннями ростуть разом із числом",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "placement.svg"), W, H, *f,
           title="Куди поставити мітки на числовій осі")


# ── Фігура B: три октави — однаково чисел, проміжок подвоюється ──────────────
def fig_binades():
    W, H = 900, 300
    x0, x1 = 80.0, 820.0                            # осі відповідають значенням 1 … 8

    def X(v):
        return x0 + (v - 1.0) / 7.0 * (x1 - x0)

    f = []
    f.append(arrow(70, 210, 838, 210, sw=1.8))

    pts = ([1, 1.25, 1.5, 1.75], [2, 2.5, 3, 3.5], [4, 5, 6, 7])
    for group in pts:
        for v in group:
            f.append(circle(X(v), 210, 4.2, fill=INK, stroke=INK, sw=1))

    for b in (1, 2, 4, 8):                          # межі октав
        f.append(line(X(b), 199, X(b), 221, sw=2.2))
        f.append(text(X(b), 245, str(b), size=13, bold=True))

    # крок усередині кожної октави (над віссю, по центру діапазону)
    steps = [((1, 2), "крок ¼"), ((2, 4), "крок ½"), ((4, 8), "крок 1")]
    for (a, b), lab in steps:
        f.append(text((X(a) + X(b)) / 2, 150, lab, size=15, bold=True, color=NEG))

    for b in (2, 4):                                # подвоєння на межах
        f.append(text(X(b), 120, "×2", size=13, bold=True, color=POS))

    f.append(text(W / 2, 279,
                  "кількість значень у кожній октаві однакова — росте лише абсолютний крок",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "binades.svg"), W, H, *f,
           title="Октави: однаково чисел, проміжок подвоюється")


# ── Фігура C: бюджет бітів — діапазон проти точності ────────────────────────
def fig_budget():
    W, H = 880, 360
    f = []
    y, hh = 80, 56

    # три поля слова
    f.append(rect(90, y, 44, hh, fill=FILL, stroke=LINE))
    f.append(rect(134, y, 236, hh, fill="#eaf0fd", stroke=NEG))
    f.append(rect(370, y, 420, hh, fill="#eafaf1", stroke=FIELD))
    f.append(text(112, y + 34, "знак", size=12))
    f.append(text(252, y + 34, "порядок (8 біт)", size=14, bold=True, color=NEG))
    f.append(text(580, y + 34, "мантиса (23 біти)", size=14, bold=True, color=FIELD))

    # з'єднувачі до пояснень
    f.append(line(252, y + hh, 252, 196, color=NEG, sw=1.6))
    f.append(line(580, y + hh, 580, 196, color=FIELD, sw=1.6))

    b1, _, _ = textbox(252, 232, "ДІАПАЗОН\nкуди пливе кома\n10⁻³⁸ … 10³⁸",
                       size=13, fill="#eaf0fd", stroke=NEG)
    b2, _, _ = textbox(580, 232, "ТОЧНІСТЬ\nскільки значущих цифр\n~7 десяткових",
                       size=13, fill="#eafaf1", stroke=FIELD)
    f.append(b1)
    f.append(b2)

    f.append(mtext(W / 2, 312,
                   ["Сума бітів стала: більше під порядок — ширший діапазон, але грубіша точність.",
                    "Віддаси під мантису — навпаки: тонша сітка, зате вужчий діапазон."],
                   size=12.5, color=MUTED))
    render(os.path.join(IMG, "budget.svg"), W, H, *f,
           title="Ті самі біти: діапазон проти точності")


# ── Фігура D: заокруглення до найближчого — межа ½ ULP ──────────────────────
def fig_rounding():
    W, H = 860, 340
    f = []
    ax = 175
    xm, xp, mid = 210, 650, 430

    # смуги «куди заокруглюється» (ліворуч — до x⁻, праворуч — до x⁺)
    f.append(rect(xm, ax - 40, mid - xm, 80, fill="#eef3fd", stroke="none", sw=0, rx=0))
    f.append(rect(mid, ax - 40, xp - mid, 80, fill="#fdeeec", stroke="none", sw=0, rx=0))

    # вісь із продовженням в обидва боки
    f.append(arrow(90, ax, 800, ax, sw=1.8))
    f.append(text(122, ax - 12, "⋯", size=20, color=MUTED))
    f.append(text(762, ax - 12, "⋯", size=20, color=MUTED))

    # два сусідні представні числа
    f.append(circle(xm, ax, 5.5, fill=INK, stroke=INK, sw=1))
    f.append(circle(xp, ax, 5.5, fill=INK, stroke=INK, sw=1))
    f.append(text(xm, ax + 30, "x⁻", size=15, bold=True))
    f.append(text(xp, ax + 30, "x⁺", size=15, bold=True))
    f.append(text(xm, ax + 48, "представне", size=11, color=MUTED))
    f.append(text(xp, ax + 48, "представне", size=11, color=MUTED))

    # середина — вододіл заокруглення
    f.append(line(mid, ax - 66, mid, ax + 14, color=MUTED, sw=1.4, dash="5 4"))
    f.append(text(mid, ax - 74, "середина — вододіл", size=12, color=MUTED))

    # довільне дійсне x у лівій смузі
    xr = 335
    f.append(line(xr, ax - 40, xr, ax - 2, color=POS, sw=1.7, dash="4 3"))
    f.append(text(xr, ax - 48, "x", size=16, bold=True, color=POS))

    # присуди в смугах
    f.append(text((xm + mid) / 2, ax - 24, "→ x⁻", size=13, bold=True, color=NEG))
    f.append(text((mid + xp) / 2, ax - 24, "x⁺ ←", size=13, bold=True, color=POS))

    # брекет ULP під віссю
    yb = ax + 70
    f.append(line(xm, yb, xp, yb, sw=1.6))
    f.append(line(xm, yb - 6, xm, yb + 6, sw=1.6))
    f.append(line(xp, yb - 6, xp, yb + 6, sw=1.6))
    f.append(line(mid, yb - 6, mid, yb + 6, sw=1.2, color=MUTED))
    f.append(text((xm + mid) / 2, yb + 18, "½ ULP", size=12, color=MUTED))
    f.append(text((mid + xp) / 2, yb + 18, "½ ULP", size=12, color=MUTED))
    f.append(text(mid, yb - 12, "ULP", size=13, bold=True))

    f.append(mtext(W / 2, ax + 118,
                   ["Хоч де впаде x усередині інтервалу завдовжки ULP, найближче представне — не далі ½ ULP.",
                    "Ліворуч від середини заокруглюємо вниз, до x⁻; праворуч — угору, до x⁺."],
                   size=12.5, color=MUTED))
    render(os.path.join(IMG, "rounding.svg"), W, H, *f,
           title="Заокруглення до найближчого: похибка ≤ ½ ULP")


# ── Фігура E: денормалі рівномірно заповнюють проміжок до нуля ───────────────
def fig_subnormals():
    W, H = 920, 300
    f = []
    ax = 165

    # позиції: денормалі [0 … 2^emin] рівним кроком s; далі октави з кроком ×2
    sub = [100, 140, 180, 220, 260]                 # 0 … 2^emin (крок s)
    nb1 = [260, 300, 340, 380, 420]                 # [2^emin, 2^(emin+1))  крок s
    nb2 = [420, 500, 580, 660, 740]                 # [2^(emin+1), 2^(emin+2))  крок 2s
    bounds = {100: "0", 260: "2^e min", 420: "2^(e min+1)", 740: "2^(e min+2)"}

    # кольорові підкреслення діапазонів (просто під віссю)
    f.append(line(100, ax + 8, 260, ax + 8, color=FIELD, sw=3.2))
    f.append(line(260, ax + 8, 420, ax + 8, color=NEG, sw=3.2))
    f.append(line(420, ax + 8, 740, ax + 8, color=MUTED, sw=3.2))

    f.append(arrow(90, ax, 880, ax, sw=1.8))
    f.append(text(800, ax - 12, "⋯", size=20, color=MUTED))

    for group, r in ((sub, 3.6), (nb1, 3.6), (nb2, 3.6)):
        for x in group:
            f.append(circle(x, ax, r, fill=INK, stroke=INK, sw=1))

    for x, lab in bounds.items():                    # межі — вищі риски й підписи
        f.append(line(x, ax - 11, x, ax + 11, sw=2.2))
        f.append(text(x, ax + 34, lab, size=12, bold=True))

    # кроки над віссю: s = s (той самий), далі 2s
    f.append(text(180, ax - 22, "крок s", size=13, bold=True, color=FIELD))
    f.append(text(340, ax - 22, "крок s", size=13, bold=True, color=NEG))
    f.append(text(580, ax - 22, "крок 2s", size=13, bold=True))
    f.append(text(420, ax - 40, "×2", size=13, bold=True, color=POS))
    f.append(text(740, ax - 40, "×2", size=13, bold=True, color=POS))

    f.append(text(180, ax + 56, "денормалі", size=11.5, color=FIELD))
    f.append(text(340, ax + 56, "1-ша нормальна октава", size=11.5, color=NEG))

    f.append(mtext(W / 2, ax + 92,
                   ["Найменше нормальне число (2^e min) не обривається проваллям у нуль: денормалі підхоплюють",
                    "ту саму сітку з кроком s і рівномірно доводять її аж до 0 — точність спадає плавно, а не стрибком."],
                   size=12.5, color=MUTED))
    render(os.path.join(IMG, "subnormals.svg"), W, H, *f,
           title="Денормалі: рівний крок до самого нуля (поступове заникання)")


# ── Фігура F (вставка hist): дуга від ідеї до стандарту ─────────────────────
def fig_timeline():
    W, H = 1040, 470
    yax = 235
    f = []
    f.append(arrow(80, yax, 980, yax, sw=2))
    f.append(text(974, yax - 12, "час", size=12, color=MUTED, anchor="end"))

    xs = [120 + i * 164 for i in range(6)]
    data = [
        (["1914", "Торрес-і-Кеведо", "ідея на папері"],  NEG,   "up"),
        (["1938", "Z1 — механічна,", "ненадійна"],       INK,   "down"),
        (["1941", "Z3 — перша робоча", "двійкова РК"],    INK,   "up"),
        (["1954", "IBM 704 —", "РК у залізі, масово"],    INK,   "down"),
        (["1964", "System/360 —", "хитлива точність"],    POS,   "up"),
        (["1985", "IEEE 754 —", "єдиний стандарт"],       FIELD, "down"),
    ]
    for x, (lines, col, side) in zip(xs, data):
        f.append(circle(x, yax, 6, fill=col, stroke=col, sw=1.5))
        cy = 118 if side == "up" else 352
        box, w, h = textbox(x, cy, "\n".join(lines), size=13, stroke=col, color=INK)
        if side == "up":
            f.append(line(x, cy + h / 2, x, yax - 6, color=col, sw=1.5))
        else:
            f.append(line(x, yax + 6, x, cy - h / 2, color=col, sw=1.5))
        f.append(box)

    f.append(text(W / 2, 452,
                  "ідея (1914) → перші робочі машини (1938–41) → десятиліття несумісних форматів → єдиний стандарт (1985)",
                  size=12.5, color=MUTED))
    render(os.path.join(IMG, "timeline.svg"), W, H, *f,
           title="Народження рухомої коми: від ідеї на папері до єдиного стандарту")


# ── Фігура G (вставка hist): слово Z3 — перша двійкова РК у залізі ───────────
def fig_z3word():
    W, H = 940, 380
    f = []
    x0, ybar, hh = 150, 112, 58

    # три поля 22-бітового слова
    f.append(rect(x0, ybar, 56, hh, fill=FILL, stroke=LINE))
    f.append(rect(x0 + 56, ybar, 180, hh, fill="#eaf0fd", stroke=NEG))
    f.append(rect(x0 + 236, ybar, 336, hh, fill="#eafaf1", stroke=FIELD))
    f.append(fitbox(x0, ybar, 56, hh, "знак\n1 біт", size=12))
    f.append(fitbox(x0 + 56, ybar, 180, hh, "порядок\n7 біт", size=13,
                    stroke=NEG, fill="#eaf0fd", color=NEG, bold=True))
    f.append(fitbox(x0 + 236, ybar, 336, hh, "мантиса\n14 біт (збережених)", size=13,
                    stroke=FIELD, fill="#eafaf1", color=FIELD, bold=True))

    # прихована провідна одиниця над лівим краєм мантиси
    hx = x0 + 236
    f.append(rect(hx, 62, 34, 34, fill="#fff8e6", stroke=POS, sw=1.6, rx=5))
    f.append(text(hx + 17, 85, "1.", size=15, bold=True, color=POS))
    f.append(arrow(hx + 17, 98, hx + 17, ybar - 2, color=POS, sw=1.6))
    f.append(mtext(hx + 46, 74,
                   ["провідна 1 нормалізованої мантиси —",
                    "завжди 1, тому її не зберігають (фактично 15 біт)"],
                   size=12.5, color=INK, anchor="start"))

    # формула значення
    f.append(mtext(W / 2, 210,
                   ["значення  =  ± 1.m₁m₂ … m₁₄ × 2ᵉ",
                    "нормалізовано: 1 ≤ 1.m < 2 ;  порядок e від −64 до +63"],
                   size=14, color=INK))

    # дві виноски-суті
    b1, _, _ = textbox(278, 302, "напівлогарифмічна форма\n(Zuse: «halblogarithmische Form»)",
                       size=12.5, stroke=FIELD, color=INK)
    b2, _, _ = textbox(668, 302, "окремі значення для ±∞ та невизначеності —\nвинятки, що повернуться в IEEE 754",
                       size=12.5, stroke=NEG, color=INK)
    f.append(b1)
    f.append(b2)

    f.append(text(W / 2, 360,
                  "Прихована одиниця й особливі значення були вже тут — стандарт закріпить їх лише за 44 роки.",
                  size=12, color=MUTED))
    render(os.path.join(IMG, "z3word.svg"), W, H, *f,
           title="Слово Z3 (1941): перша двійкова рухома кома в залізі")


if __name__ == "__main__":
    fig_placement()
    fig_binades()
    fig_budget()
    fig_rounding()
    fig_subnormals()
    fig_timeline()
    fig_z3word()
    print("OK: placement.svg, binades.svg, budget.svg, rounding.svg, subnormals.svg, timeline.svg, z3word.svg")
