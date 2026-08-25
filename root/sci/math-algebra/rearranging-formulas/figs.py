# -*- coding: utf-8 -*-
"""Фігури до статті «Перестановка формул»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def step_row(cx, cy, s, size=15, green=False, min_w=0):
    """Рядок-рівність у рамці. Повертає (фрагмент, верх, низ)."""
    frag, w, h = textbox(cx, cy, s, size=size, pad=12, min_w=min_w,
                         stroke=FIELD if green else LINE,
                         fill="#eef8f1" if green else FILL,
                         sw=2.2 if green else 1.5)
    return frag, cy - h / 2, cy + h / 2


def op_arrow(x, y_from, y_to, label, lx, size=13):
    """Вертикальна стрілка ліворуч + підпис дії праворуч від неї (без накладань)."""
    return (arrow(x, y_from, x, y_to)
            + text(lx, (y_from + y_to) / 2 + size * 0.35, label,
                   size=size, color=MUTED, anchor="start"))


# ─────────────────────────────────────────────────────────────────────────────
# 1. Той самий рух: шукане над рискою (один крок) і під рискою (два кроки)
# ─────────────────────────────────────────────────────────────────────────────
def fig_same_move():
    W, H = 1000, 400
    LX, RX = 250, 730          # центри колонок
    frags = []

    # заголовки колонок
    frags.append(text(LX, 76, "шукане НАД рискою — один крок", size=15, bold=True))
    frags.append(text(RX, 76, "шукане ПІД рискою — два кроки", size=15, bold=True))

    # роздільник колонок (у порожньому коридорі між колонками)
    frags.append(line(494, 96, 494, 360, color="#c9ced6", sw=1.2, dash="6 6"))

    # ── ліва колонка ────────────────────────────────────────────────────────
    f, _, b1 = step_row(LX, 130, "ω = m(солі) / m(розчину)")
    frags.append(f)
    f, t2, b2 = step_row(LX, 250, "m(солі) = ω · m(розчину)", green=True)
    frags.append(op_arrow(150, b1 + 12, t2 - 12, "× m(розчину)  —  обидва боки", 172))
    frags.append(f)
    frags.append(text(LX, 320, "ділення прибрали множенням", size=13, color=MUTED))

    # ── права колонка ───────────────────────────────────────────────────────
    f, _, b1 = step_row(RX, 118, "n = m / M", min_w=230)
    frags.append(f)
    f, t2, b2 = step_row(RX, 214, "n · M = m", min_w=230)
    frags.append(op_arrow(636, b1 + 10, t2 - 10, "× M  —  обидва боки", 658))
    frags.append(f)
    f, t3, b3 = step_row(RX, 310, "M = m / n", green=True, min_w=230)
    frags.append(op_arrow(636, b2 + 10, t3 - 10, "÷ n  —  обидва боки", 658))
    frags.append(f)
    frags.append(text(RX, 366, "той самий рух, застосований двічі", size=13, color=MUTED))

    render(os.path.join(OUT, 'same-move.svg'), W, H, *frags,
           title="Дію виконують з обома боками рівності")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Одна рівність — три запитання
# ─────────────────────────────────────────────────────────────────────────────
def fig_three_formulas():
    W, H = 940, 380
    frags = []

    top, w0, h0 = textbox(470, 90, "m(солі) = ω · m(розчину)", size=17, pad=14,
                          fill="#eef8f1", stroke=FIELD, sw=2.2)
    frags.append(top)
    frags.append(text(470, 90 + h0 / 2 + 22, "один зв'язок між трьома величинами",
                      size=13, color=MUTED))

    cols = [
        (160, "шукаю ω", "ω = m(солі) / m(розчину)", "відомі обидві маси"),
        (470, "шукаю m(солі)", "m(солі) = ω · m(розчину)", "відомі частка й розчин"),
        (780, "шукаю m(розчину)", "m(розчину) = m(солі) / ω", "відомі частка й сіль"),
    ]
    for cx, ask, formula, note in cols:
        box, w, h = textbox(cx, 265, [ask, formula], size=13, pad=12, min_w=250)
        frags.append(arrow(470, 90 + h0 / 2 + 40, cx, 265 - h / 2 - 10))
        frags.append(box)
        frags.append(text(cx, 265 + h / 2 + 24, note, size=12, color=MUTED))

    render(os.path.join(OUT, 'three-formulas.svg'), W, H, *frags,
           title="Одна рівність — три запитання")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Пари обернених дій (до вставки math-worked-rearrangements)
# ─────────────────────────────────────────────────────────────────────────────
def fig_inverse_pairs():
    W, H = 1000, 470
    C1, C2, C3 = 170, 420, 748
    frags = []

    frags.append(text(C1, 84, "що тримає шукане", size=15, bold=True))
    frags.append(text(C2, 84, "чим знімають", size=15, bold=True))
    frags.append(text(C3, 84, "формула з розбору", size=15, bold=True))

    rows = [
        ("множення на c", "ділення на c", ["U = I · R", "⟹  R = U / I"]),
        ("ділення на c", "множення на c", ["ρ = m / V", "⟹  m = ρ · V"]),
        ("додавання s₀", "віднімання s₀", ["s = s₀ + v · t", "⟹  s − s₀ = v · t"]),
        ("квадрат", "квадратний корінь", ["E = m · v² / 2", "⟹  v = √(2E / m)"]),
        ("степінь основи e", "натуральний логарифм",
         ["u = U₀ · e^(−t / RC)", "⟹  t = R · C · ln(U₀ / u)"]),
    ]

    y = 128
    for hold, undo, ex in rows:
        b1, _, _ = textbox(C1, y, hold, size=13, pad=11, min_w=190)
        b2, _, _ = textbox(C2, y, undo, size=13, pad=11, min_w=190)
        b3, _, _ = textbox(C3, y, ex, size=13, pad=12, min_w=420,
                           stroke=FIELD, fill="#eef8f1", sw=2.0)
        frags += [b1, arrow(280, y, 320, y), b2, b3]
        y += 72

    render(os.path.join(OUT, 'inverse-pairs.svg'), W, H, *frags,
           title="Обернена дія залежить лише від того, що тримає шукане")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Порядок зняття шарів: s = s₀ + v·t
# ─────────────────────────────────────────────────────────────────────────────
def fig_peel_order():
    W, H = 1000, 410
    frags = []

    # ── ліворуч: t під двома шарами ─────────────────────────────────────────
    frags.append(text(250, 84, "s = s₀ + v · t", size=16, bold=True))
    frags.append(rect(120, 138, 260, 204, fill="#ffffff"))
    frags.append(text(250, 164, "+ s₀   — зовнішній шар", size=13, color=MUTED))
    frags.append(rect(160, 180, 180, 124, fill="#fbfcfd"))
    frags.append(text(250, 204, "· v   — внутрішній", size=13, color=MUTED))
    frags.append(textbox(250, 246, "t", size=20, pad=12, min_w=100,
                         stroke=FIELD, fill="#eef8f1", sw=2.2)[0])
    frags.append(text(250, 372, "шукане — у самій серцевині", size=13, color=MUTED))

    frags.append(line(470, 104, 470, 380, color="#c9ced6", sw=1.2, dash="6 6"))

    # ── праворуч: порядок зняття ────────────────────────────────────────────
    frags.append(text(742, 84, "знімати — зовнішній шар першим", size=16, bold=True))

    b1, _, h1 = textbox(742, 168, ["1.  − s₀  з обох боків", "s − s₀ = v · t"],
                        size=14, pad=13, min_w=400)
    frags.append(b1)
    b2, _, h2 = textbox(742, 282, ["2.  ÷ v  з обох боків", "(s − s₀) / v = t"],
                        size=14, pad=13, min_w=400,
                        stroke=FIELD, fill="#eef8f1", sw=2.2)
    frags.append(arrow(742, 168 + h1 / 2 + 10, 742, 282 - h2 / 2 - 10))
    frags.append(b2)
    frags.append(text(742, 372, "почати з ÷ v не можна — воно зачепить і s₀",
                      size=13, color=POS))

    render(os.path.join(OUT, 'peel-order.svg'), W, H, *frags,
           title="Шари знімають у зворотному порядку до того, як їх наклали")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Дві дії з багдадського трактату — і те саме сучасними словами (hist-al-jabr)
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_ops():
    W, H = 1150, 440
    C1, C2, C3 = 160, 520, 930
    frags = []

    frags.append(text(C1, 72, "як звалося", size=13, bold=True, color=MUTED))
    frags.append(text(C2, 72, "приклад просто з трактату", size=13, bold=True, color=MUTED))
    frags.append(text(C3, 72, "те саме сучасними словами", size=13, bold=True, color=MUTED))

    rows = [
        (155, ["al-jabr", "«відновлення»"],
         "x² = 40x − 4x²   →   5x² = 40x",
         "додати 4x² до обох боків"),
        (265, ["al-muqābala", "«зіставлення»"],
         "x² + 5 = 40x + 4x²   →   5 = 40x + 3x²",
         "відняти x² від обох боків"),
    ]
    for cy, name, sample, modern in rows:
        frags.append(textbox(C1, cy, name, size=14, pad=10, min_w=200, bold=True)[0])
        frags.append(textbox(C2, cy, sample, size=15, pad=12, min_w=420)[0])
        frags.append(textbox(C3, cy, modern, size=13, pad=12, min_w=320,
                             fill="#eef8f1", stroke=FIELD, sw=2.0)[0])

    frags.append(textbox(575, 370,
                         "Два імені — одна дія: зробити те саме з обома боками рівності",
                         size=16, pad=14, fill="#eef8f1", stroke=FIELD, sw=2.4)[0])
    frags.append(text(575, 418,
                      "окремі імена були потрібні, доки не було від'ємних чисел",
                      size=13, color=MUTED))

    render(os.path.join(OUT, 'two-operations.svg'), W, H, *frags,
           title="al-jabr і al-muqābala — очима свого часу й нашого")


# ─────────────────────────────────────────────────────────────────────────────
# 6. Дорога слова: Багдад → Сеговія → Англія, і дві бічні гілки (hist-al-jabr)
# ─────────────────────────────────────────────────────────────────────────────
def fig_word_journey():
    W, H = 1160, 430
    AXIS_Y = 210
    frags = []

    stops = [
        (172, ["бл. 820 · Багдад", "«al-jabr wa-l-muqābala»", "назва двох дій над рівністю"]),
        (467, ["1145 · Сеговія", "Liber algebrae et almucabola", "перший латинський переклад"]),
        (751, ["1551 · Англія", "«the rule of Algeber»", "перша згадка англійською"]),
        (1010, ["сьогодні", "«алгебра»", "у більшості мов світу"]),
    ]

    frags.append(line(60, AXIS_Y, 1100, AXIS_Y, color="#c9ced6", sw=2.5))

    for cx, lines in stops:
        b, _, h = textbox(cx, 115, lines, size=13, pad=12)
        frags.append(b)
        frags.append(line(cx, 115 + h / 2, cx, AXIS_Y - 6, color="#c9ced6", sw=1.4))
        frags.append(circle(cx, AXIS_Y, 6, fill=BG, stroke=LINE, sw=2.2))

    # бічна гілка 1: ім'я автора → «алгоритм»
    frags.append(arrow(172, AXIS_Y + 8, 172, 266, color=MUTED, sw=1.6))
    frags.append(textbox(172, 295, ["ім'я автора → лат. Algoritmi", "→ «алгоритм»"],
                         size=12, pad=12, fill="#fdf6ec", stroke="#c98a2b", sw=1.6)[0])

    # бічна гілка 2: al-jabr в іспанській → костоправ
    frags.append(arrow(467, AXIS_Y + 8, 467, 346, color=MUTED, sw=1.6))
    frags.append(textbox(467, 375, ["ісп. algebrista", "костоправ, що вправляє кістки"],
                         size=12, pad=12, fill="#fdf6ec", stroke="#c98a2b", sw=1.6)[0])

    render(os.path.join(OUT, 'word-journey.svg'), W, H, *frags,
           title="Дорога слова від назви книжки до назви галузі")


if __name__ == '__main__':
    fig_same_move()
    fig_three_formulas()
    fig_inverse_pairs()
    fig_peel_order()
    fig_two_ops()
    fig_word_journey()
    print("ok:", os.listdir(OUT))
