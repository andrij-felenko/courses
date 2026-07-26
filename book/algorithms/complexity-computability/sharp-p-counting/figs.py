# -*- coding: utf-8 -*-
"""Фігури для теми «Клас #P: складність підрахунку розв'язків»
(book/algorithms/complexity-computability/sharp-p-counting)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"


def fig_det_vs_perm():
    """Визначник і перманента: та сама сума по n! перестановках, різниця — лише sgn(σ)."""
    W, H = 1140, 470
    frags = []
    lx, rx = 300, 840          # центри лівої (det) і правої (perm) панелей
    frags.append(line(570, 60, 570, 330, color="#d5dbe2", sw=2, dash="7 7"))

    # ── заголовки ────────────────────────────────────────────────────────────
    frags.append(textbox(lx, 82, "Визначник   det A", size=16, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=2.4, pad=13)[0])
    frags.append(textbox(rx, 82, "Перманента   perm A", size=16, bold=True,
                         fill="#fdecea", stroke=POS, sw=2.4, pad=13)[0])

    # ── формули (та сама сума, різниться лише множник sgn) ────────────────────
    frags.append(textbox(lx, 158, "det A  =  Σσ  sgn(σ) · ∏ᵢ a[i, σ(i)]",
                         size=15, bold=True, fill=BG, stroke="#c7ced6", sw=1.6, pad=13)[0])
    frags.append(textbox(rx, 158, "perm A  =  Σσ  ∏ᵢ a[i, σ(i)]",
                         size=15, bold=True, fill=BG, stroke="#c7ced6", sw=1.6, pad=13)[0])

    # ── анотації під формулами ───────────────────────────────────────────────
    frags.append(mtext(lx, 214, ["є множник знаку sgn(σ) = ±1 —",
                                 "він дає структуру для методу Гаусса"],
                       size=13, color=NEG, bold=True))
    frags.append(mtext(rx, 214, ["того самого множника вже немає —",
                                 "жодної структури, лишається сума по n!"],
                       size=13, color=POS, bold=True))

    # ── наслідки (чипи) ──────────────────────────────────────────────────────
    frags.append(textbox(lx, 300, "O(n³) — легко (клас P)", size=15, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=2.4, pad=13)[0])
    frags.append(textbox(rx, 300, "#P-повна (Валіант, 1979)", size=15, bold=True,
                         fill="#fdecea", stroke=POS, sw=2.4, pad=13)[0])

    # ── нижня смуга-висновок ─────────────────────────────────────────────────
    band, _, _ = textbox(W / 2, 405,
                         "Та сама сума по всіх n! перестановках σ. Прибрали єдиний множник — знак sgn(σ) — і O(n³)-задача обернулася на #P-повну.",
                         size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=14)
    frags.append(band)

    render(os.path.join(IMG, "det-vs-perm.svg"), W, H, *frags,
           title="Визначник і перманента: уся різниця — знак sgn(σ)")


def fig_decide_vs_count():
    """Той самий двочастковий граф: «чи існує?» полін., «скільки?» — #P-повна."""
    W, H = 1160, 560
    frags = []

    # ── двочастковий граф угорі по центру ────────────────────────────────────
    frags.append(text(W / 2, 62, "той самий вхід — двочастковий граф G", size=14,
                      color=MUTED, bold=True))
    Lx, Rx = 500, 660
    ys = [96, 150, 204]
    Lp = [(Lx, y) for y in ys]
    Rp = [(Rx, y) for y in ys]
    edges = [(0, 0), (0, 1), (1, 1), (1, 2), (2, 0), (2, 2)]
    match = {(0, 1), (1, 2), (2, 0)}           # одне досконале паросполучення — зелене
    for (u, v) in edges:
        he = (u, v) in match
        frags.append(line(Lp[u][0] + 15, Lp[u][1], Rp[v][0] - 15, Rp[v][1],
                          color=(FIELD if he else "#9aa4b2"), sw=(3.4 if he else 1.8)))
    for i, (x, y) in enumerate(Lp):
        frags.append(circle(x, y, 15, fill="#eef2f7", stroke=INK, sw=1.8))
        frags.append(text(x, y + 5, "u%d" % (i + 1), size=13, bold=True))
    for i, (x, y) in enumerate(Rp):
        frags.append(circle(x, y, 15, fill="#eef2f7", stroke=INK, sw=1.8))
        frags.append(text(x, y + 5, "v%d" % (i + 1), size=13, bold=True))

    # стрілки від графа до двох панелей
    frags.append(arrow(490, 230, 300, 300, color=INK, sw=2))
    frags.append(arrow(670, 230, 860, 300, color=INK, sw=2))

    # ── ліва панель: існування ───────────────────────────────────────────────
    lx = 290
    frags.append(textbox(lx, 322, "Питання ІСНУВАННЯ", size=15, bold=True,
                         fill="#eaf0fd", stroke=NEG, sw=2.2, pad=12)[0])
    frags.append(mtext(lx, 384, ["Чи Є хоч одне", "досконале паросполучення?"],
                       size=15, bold=True, color=INK))
    frags.append(textbox(lx, 452, "P — поліном. час\n(Гопкрофт–Карп)", size=15, bold=True,
                         fill="#e9f7ef", stroke=FIELD, sw=2.4, pad=13)[0])

    # ── права панель: підрахунок ─────────────────────────────────────────────
    rx = 870
    frags.append(textbox(rx, 322, "Питання ПІДРАХУНКУ", size=15, bold=True,
                         fill="#fdecea", stroke=POS, sw=2.2, pad=12)[0])
    frags.append(mtext(rx, 384, ["СКІЛЬКИ", "досконалих паросполучень?"],
                       size=15, bold=True, color=INK))
    frags.append(textbox(rx, 452, "#P-повна\n= перманента 0/1-матриці", size=15, bold=True,
                         fill="#fdecea", stroke=POS, sw=2.4, pad=13)[0])

    # ── нижня смуга ──────────────────────────────────────────────────────────
    band, _, _ = textbox(W / 2, 522,
                         "Змінили одне слово — «чи є» на «скільки» — і поліномна задача стала однією з найважчих відомих.",
                         size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=13)
    frags.append(band)

    render(os.path.join(IMG, "decide-vs-count.svg"), W, H, *frags,
           title="«Чи існує?» проти «Скільки?» — той самий граф, різна прірва")


def fig_class_map():
    """Де живе #P: концентричні класи P ⊂ NP ⊂ PH ⊂ P^#P ⊂ PSPACE; теорема Тоди."""
    W, H = 1000, 580
    cxc = W / 2
    frags = []

    # п'ять вкладених рамок (зовнішня PSPACE → внутрішня P)
    frags.append(rect(40, 60, 920, 388, fill="#fbfcfd", stroke=MUTED, sw=2, rx=18))
    frags.append(rect(104, 114, 792, 300, fill="#f0f3f8", stroke="#7a63c0", sw=2.4, rx=16))
    frags.append(rect(176, 168, 648, 208, fill="#eef2f7", stroke="#8a93a0", sw=2, rx=14))
    frags.append(rect(268, 220, 464, 114, fill="#eaf0fd", stroke=NEG, sw=2.2, rx=12))
    frags.append(rect(384, 264, 232, 58, fill="#e9f7ef", stroke=FIELD, sw=2.4, rx=10))

    # заголовки в верхній смузі кожної рамки
    frags.append(text(cxc, 88, "PSPACE — поліномна пам'ять", size=15, bold=True, color=MUTED))
    frags.append(text(cxc, 140, "P^#P = P^PP  —  поліном. час з оракулом «скільки?»",
                      size=15, bold=True, color="#5b4aa0"))
    frags.append(text(cxc, 194, "PH — поліноміальна ієрархія  (NP ⊆ Σ₂ᵖ ⊆ Σ₃ᵖ ⊆ ⋯)",
                      size=14, bold=True, color="#5a6472"))
    frags.append(text(cxc, 246, "NP — існування свідка", size=14, bold=True, color=NEG))
    frags.append(text(cxc, 298, "P", size=17, bold=True, color=FIELD))

    # приписка про функційний бік підрахунку
    frags.append(text(cxc, 432, "#P — це функції-лічильники:   FP ⊆ #P ⊆ FPSPACE",
                      size=13, bold=True, color="#5b4aa0"))

    # каптіон-смуга: теорема Тоди
    cap, _, _ = textbox(cxc, 512,
                        "Тода (1991): вся вежа PH вкладається в P^#P — один-єдиний оракул «скільки?»\nприборкує цілу ієрархію кванторів над NP.",
                        size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=13)
    frags.append(cap)

    render(os.path.join(IMG, "class-map.svg"), W, H, *frags,
           title="Де живе #P: P ⊆ NP ⊆ PH ⊆ P^#P ⊆ PSPACE")


def fig_birth_timeline():
    """Часоплин народження #P: від складности РІШЕННЯ (Кук, Карп) через
    поворот Валіанта 1979 до складности ПІДРАХУНКУ та її спадку."""
    W, H = 1220, 560
    PURP = "#5b4aa0"
    axis_y = 292
    frags = []

    # ── дві ери — фонові смуги ────────────────────────────────────────────────
    frags.append(rect(70, 96, 530, 368, fill="#eef2fb", stroke="#c7d2ea", sw=1.6, rx=16))
    frags.append(rect(600, 96, 560, 368, fill=AMBER_F, stroke=AMBER_S, sw=1.6, rx=16))
    frags.append(line(600, 96, 600, 464, color="#b9a26a", sw=2, dash="6 6"))
    frags.append(text(335, 82, "ДО 1979 · складність РІШЕННЯ «чи існує?»",
                      size=14, bold=True, color="#3a56a0"))
    frags.append(text(880, 82, "ВІД 1979 · складність ПІДРАХУНКУ «скільки?» — клас #P",
                      size=14, bold=True, color="#9a6a12"))

    # ── вісь часу ─────────────────────────────────────────────────────────────
    frags.append(line(100, axis_y, 1120, axis_y, color=INK, sw=2.5))

    # x, рік, рядки, above?, колір, hero?
    nodes = [
        (175, "1963", ["Райзер (Ryser):", "перманента за O(2ⁿ·n) —", "межа, та все ще експонента"],
         False, MUTED, False),
        (360, "1971", ["Кук (Cook):", "SAT — перша", "NP-повна задача"], True, NEG, False),
        (540, "1972", ["Карп (Karp):", "21 NP-повна задача —", "карта рішеневої важкости"],
         False, NEG, False),
        (735, "1979", ["ВАЛІАНТ — дві роботи:", "народжується клас #P;", "перманента 0/1 і надійність",
                       "мереж, #2SAT — #P-повні"], True, AMBER_S, True),
        (920, "1991", ["Тода (Toda):", "PH ⊆ P^#P — підрахунок", "вінчає всю ієрархію"],
         False, PURP, False),
        (1060, "2010", ["Валіант —", "премія Тюрінга за", "складність перелічування"], True, PURP, False),
    ]
    for (x, year, lines, above, color, hero) in nodes:
        r = 13 if hero else 8
        node_fill = "#ffe4bd" if hero else BG
        frags.append(circle(x, axis_y, r, fill=node_fill, stroke=color, sw=(3.6 if hero else 2.6)))
        # рік — на «порожньому» боці осі від коробки
        frags.append(text(x, (axis_y + 31) if above else (axis_y - 20), year,
                          size=15, bold=True, color=color))
        # коробка-опис
        yc = (150 if hero else 170) if above else 402
        box_fill = "#ffe4bd" if hero else BG
        body, bw, bh = textbox(x, yc, "\n".join(lines), size=13, bold=hero,
                               fill=box_fill, stroke=color, sw=(2.6 if hero else 1.8), pad=11)
        if above:
            frags.append(line(x, yc + bh / 2, x, axis_y - r, color=color, sw=1.6,
                              dash=(None if hero else "4 4")))
        else:
            frags.append(line(x, axis_y + r, x, yc - bh / 2, color=color, sw=1.6, dash="4 4"))
        frags.append(body)

    render(os.path.join(IMG, "birth-timeline.svg"), W, H, *frags,
           title="Народження класу #P: 1979 рік у часоплині складности")


def fig_count_tree():
    """Дерево лічильника #SAT: розгалузитися за змінною й СКЛАСТИ числа гілок."""
    W, H = 1240, 690
    frags = []
    BLU_F, GRN_F, RED_F = "#eaf0fd", "#e9f7ef", "#fdecea"

    # ── формула й корінь ─────────────────────────────────────────────────────
    frags.append(textbox(620, 66,
                         "F = (x₁∨x₂∨¬x₃) · (¬x₁∨x₃) · (x₂∨x₃)      [x₄ — вільна]",
                         size=15, bold=True, fill=BG, stroke=MUTED, sw=1.8, pad=13)[0])
    frags.append(textbox(620, 122, "count(F) — 4 змінні", size=15, bold=True,
                         fill="#f0f3f8", stroke=INK, sw=2.2, pad=12)[0])

    # ── перша розвилка за x₁ ──────────────────────────────────────────────────
    frags.append(arrow(560, 140, 340, 214, color=NEG, sw=2))
    frags.append(arrow(690, 140, 900, 214, color=NEG, sw=2))
    frags.append(text(620, 196, "склади гілки:  4 + 4 = 8", size=14, bold=True, color=FIELD))

    frags.append(textbox(330, 236, "x₁ = 1", size=15, bold=True,
                         fill=BLU_F, stroke=NEG, sw=2.2, pad=11)[0])
    frags.append(textbox(900, 236, "x₁ = 0  ⇒  (x₂∨¬x₃) · (x₂∨x₃)", size=14, bold=True,
                         fill=BLU_F, stroke=NEG, sw=2.2, pad=11)[0])

    # ── ліва гілка: одиничний диз'юнкт форсує, далі вільні змінні ─────────────
    frags.append(arrow(330, 258, 330, 320, color=INK, sw=1.8))
    frags.append(textbox(330, 372, "одиничний (x₃) ⇒ x₃=1\nусі клаузи зняті\n2² = 4",
                         size=14, bold=True, fill=GRN_F, stroke=FIELD, sw=2.4, pad=12)[0])
    frags.append(text(330, 452, "(x₂, x₄ — вільні)", size=12, color=MUTED, italic=True))

    # ── права гілка: друга розвилка за x₂ ────────────────────────────────────
    frags.append(text(900, 320, "4 + 0 = 4", size=14, bold=True, color=FIELD))
    frags.append(arrow(840, 258, 780, 336, color=NEG, sw=2))
    frags.append(arrow(960, 258, 1050, 336, color=NEG, sw=2))
    frags.append(textbox(770, 360, "x₂ = 1", size=15, bold=True,
                         fill=BLU_F, stroke=NEG, sw=2.2, pad=11)[0])
    frags.append(textbox(1050, 360, "x₂ = 0", size=15, bold=True,
                         fill=BLU_F, stroke=NEG, sw=2.2, pad=11)[0])

    frags.append(arrow(770, 382, 770, 452, color=INK, sw=1.8))
    frags.append(textbox(770, 500, "усі клаузи зняті\n2² = 4", size=14, bold=True,
                         fill=GRN_F, stroke=FIELD, sw=2.4, pad=12)[0])
    frags.append(text(770, 556, "(x₃, x₄ — вільні)", size=12, color=MUTED, italic=True))

    frags.append(arrow(1050, 382, 1050, 452, color=INK, sw=1.8))
    frags.append(textbox(1050, 496, "(¬x₃) · (x₃)\nсуперечність", size=14, bold=True,
                         fill=RED_F, stroke=POS, sw=2.4, pad=12)[0])
    frags.append(arrow(1050, 540, 1050, 590, color=POS, sw=2))
    frags.append(textbox(1050, 622, "0 моделей", size=15, bold=True,
                         fill=RED_F, stroke=POS, sw=2.4, pad=11)[0])

    # ── нижня смуга-висновок ─────────────────────────────────────────────────
    band, _, _ = textbox(430, 648,
                        "Не перебір 2⁴ = 16 наборів, а пошук: розгалузити за змінною й СКЛАСТИ числа обох гілок.",
                        size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=13)
    frags.append(band)

    render(os.path.join(IMG, "count-tree.svg"), W, H, *frags,
           title="Лічильник #SAT: розгалузитися за змінною й скласти гілки")


def fig_components():
    """Незалежні компоненти множаться; однакову підформулу кешуємо."""
    W, H = 1160, 560
    frags = []
    BLU_F, GRN_F = "#eaf0fd", "#e9f7ef"

    frags.append(textbox(580, 66, "G = (x₁∨x₂) · (¬x₁∨¬x₂) · (x₃∨x₄)",
                         size=16, bold=True, fill=BG, stroke=MUTED, sw=1.8, pad=13)[0])

    # роздільник «немає спільних змінних»
    frags.append(text(580, 128, "жодної спільної змінної", size=13, color=MUTED, bold=True))
    frags.append(line(580, 146, 580, 300, color="#c7ced6", sw=2, dash="6 6"))

    # дві компоненти
    frags.append(textbox(300, 210,
                         "Компонента A · {x₁, x₂}\n(x₁∨x₂) · (¬x₁∨¬x₂)\nрівно одне істинне → 2 моделі",
                         size=14, bold=True, fill=BLU_F, stroke=NEG, sw=2.2, pad=13)[0])
    frags.append(textbox(860, 210,
                         "Компонента B · {x₃, x₄}\n(x₃∨x₄)\n→ 3 моделі",
                         size=14, bold=True, fill=BLU_F, stroke=NEG, sw=2.2, pad=13)[0])

    # вузол множення
    frags.append(arrow(300, 262, 505, 344, color=INK, sw=2))
    frags.append(arrow(860, 262, 655, 344, color=INK, sw=2))
    frags.append(textbox(580, 366, "2 × 3 = 6 моделей", size=17, bold=True,
                         fill=GRN_F, stroke=FIELD, sw=2.6, pad=14)[0])

    # кеш
    frags.append(textbox(580, 436,
                         "кеш: канонічна форма компоненти → її число моделей\nта сама підформула в іншій гілці — готове число, без нового дерева",
                         size=13, bold=True, fill="#fbfcfd", stroke="#8a93a0", sw=1.8, pad=12)[0])

    band, _, _ = textbox(580, 510,
                        "Незалежні компоненти МНОЖАТЬСЯ (не додаються); однакову підформулу лічимо раз і кладемо в кеш.",
                        size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=13)
    frags.append(band)

    render(os.path.join(IMG, "components-cache.svg"), W, H, *frags,
           title="Незалежні компоненти множаться, повтори — з кешу")


def fig_ryser_gray():
    """Кодом Ґрея сусідні підмножини стовпців різняться одним стовпцем —
    рядкові суми оновлюються за O(n), а не перераховуються за O(n²)."""
    W, H = 1200, 560
    frags = []
    BLU_F, GRN_F = "#eaf0fd", "#e9f7ef"
    CELL_ON = "#dcefe1"

    # ── заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 60,
                      "обхід підмножин стовпців у порядку коду Ґрея — між сусідами перемикається рівно один стовпець",
                      size=14, bold=True, color=MUTED))

    # ── один перехід крупним планом ────────────────────────────────────────────
    frags.append(textbox(300, 152,
                         "S = {c₀, c₂}\nмаска [1 0 1]\nrowsumᵢ = A[i,0] + A[i,2]",
                         size=14, bold=True, fill=BLU_F, stroke=NEG, sw=2.2, pad=13)[0])
    frags.append(arrow(415, 152, 805, 152, color=INK, sw=2.2))
    frags.append(text(610, 132, "код Ґрея → перемкнути стовпець c₁", size=13, bold=True, color=FIELD))
    frags.append(textbox(900, 152,
                         "S = {c₀, c₁, c₂}\nмаска [1 1 1]\nrowsumᵢ += A[i,1]",
                         size=14, bold=True, fill=GRN_F, stroke=FIELD, sw=2.4, pad=13)[0])
    frags.append(text(W / 2, 232,
                      "один стовпець змінився → оновити n сум за O(n), а не перераховувати всі за O(n²)",
                      size=14, bold=True, color=INK))

    # ── сходинка Ґрея: усі 2³ = 8 масок, кожна — на один стовпець від сусідньої ──
    frags.append(text(W / 2, 290,
                      "усі 2³ = 8 підмножин стовпців {c₀, c₁, c₂}, кожна — на один стовпець від сусідньої",
                      size=13, bold=True, color=MUTED))
    order = [0, 1, 3, 2, 6, 7, 5, 4]          # gray(0..7): сусіди різняться одним бітом
    cs = 22
    y0 = 324
    xs = [72 + i * 140 for i in range(8)]
    prev = None
    for idx, m in enumerate(order):
        x = xs[idx]
        changed = None if prev is None else ((m ^ prev).bit_length() - 1)
        for b in range(3):                     # c0, c1, c2 зліва направо
            on = (m >> b) & 1
            hot = (b == changed)
            frags.append(rect(x + b * cs, y0, cs - 3, cs - 3,
                              fill=(CELL_ON if on else BG),
                              stroke=(POS if hot else "#9aa4b2"),
                              sw=(3.0 if hot else 1.6), rx=3))
        prev = m
        if idx < 7:
            frags.append(arrow(x + 3 * cs - 3, y0 + (cs - 3) / 2, xs[idx + 1], y0 + (cs - 3) / 2,
                              color=INK, sw=1.6))
    frags.append(text(72 + cs * 1.5 - 1.5, y0 + cs + 15, "c₀ c₁ c₂", size=11, color=MUTED))

    # ── нижня смуга: складності ─────────────────────────────────────────────────
    band, _, _ = textbox(W / 2, 472,
                        "Райзер кодом Ґрея: 2ⁿ кроків × O(n) = O(2ⁿ·n).    Перерахунок сум з нуля — O(2ⁿ·n²).    Сліпий перебір перестановок — O(n·n!).",
                        size=14, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=13)
    frags.append(band)

    render(os.path.join(IMG, "ryser-gray.svg"), W, H, *frags,
           title="Код Ґрея: інкрементне оновлення рядкових сум у формулі Райзера")


if __name__ == "__main__":
    fig_det_vs_perm()
    fig_decide_vs_count()
    fig_class_map()
    fig_birth_timeline()
    fig_count_tree()
    fig_components()
    fig_ryser_gray()
    print("OK:", sorted(os.listdir(IMG)))
