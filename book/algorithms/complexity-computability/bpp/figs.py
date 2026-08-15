# -*- coding: utf-8 -*-
"""Фігури для теми «Клас BPP: ймовірнісні поліноміальні обчислення»
(book/algorithms/complexity-computability/bpp)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

FIELD_F, FIELD_S = "#e9f7ef", "#27ae60"
POS_F, POS_S = "#fdecea", "#e74c3c"
BLUE_F, BLUE_S = "#ebf5fb", "#2980b9"
PURPLE_F, PURPLE_S = "#f5eeef", "#8e44ad"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"


def fig_bpp_acceptance_gap():
    """Візуалізація порогових інтервалів прийняття для BPP, RP та ZPP."""
    W, H = 1080, 520
    frags = []

    # Секція BPP (верхня вісь)
    frags.append(textbox(150, 130, "Клас BPP", size=15, bold=True, fill=BLUE_F, stroke=BLUE_S, sw=2, pad=10)[0])
    frags.append(line(270, 130, 1010, 130, color="#2c3e50", sw=2))

    # Засічки BPP
    frags.append(line(270, 120, 270, 140, color="#2c3e50", sw=2))
    frags.append(mtext(270, 160, ["0"], size=12, bold=True))

    frags.append(rect(270, 115, 200, 30, rx=4, fill=POS_F, stroke=POS_S, sw=1.5))
    frags.append(mtext(370, 135, ["x ∉ L: ≤ 1/3"], size=12, bold=True, color=POS_S))

    frags.append(line(470, 120, 470, 140, color=POS_S, sw=2, dash="3 3"))
    frags.append(mtext(470, 160, ["1/3"], size=12, bold=True, color=POS_S))

    # Порожній нейтральний зазор
    frags.append(rect(470, 115, 200, 30, rx=4, fill="#f2f4f4", stroke="#bdc3c7", sw=1.5))
    frags.append(mtext(570, 135, ["зазор ε ≥ 1/poly(n)"], size=12, bold=True, color="#7f8c8d"))

    frags.append(line(670, 120, 670, 140, color=FIELD_S, sw=2, dash="3 3"))
    frags.append(mtext(670, 160, ["2/3"], size=12, bold=True, color=FIELD_S))

    frags.append(rect(670, 115, 340, 30, rx=4, fill=FIELD_F, stroke=FIELD_S, sw=1.5))
    frags.append(mtext(840, 135, ["x ∈ L: ≥ 2/3"], size=12, bold=True, color=FIELD_S))

    frags.append(line(1010, 120, 1010, 140, color="#2c3e50", sw=2))
    frags.append(mtext(1010, 160, ["1"], size=12, bold=True))

    # Секція RP (середня вісь)
    frags.append(textbox(150, 260, "Клас RP", size=15, bold=True, fill=AMBER_F, stroke=AMBER_S, sw=2, pad=10)[0])
    frags.append(line(270, 260, 1010, 260, color="#2c3e50", sw=2))

    frags.append(line(270, 250, 270, 270, color="#2c3e50", sw=2))
    frags.append(mtext(270, 290, ["0"], size=12, bold=True))

    # P(accept | x ∉ L) = 0
    frags.append(textbox(340, 260, "x ∉ L: P=0 (одностороння хиба)", size=12, bold=True,
                         fill=POS_F, stroke=POS_S, sw=1.5, pad=8)[0])

    frags.append(line(670, 250, 670, 270, color=FIELD_S, sw=2, dash="3 3"))
    frags.append(mtext(670, 290, ["1/2"], size=12, bold=True, color=FIELD_S))

    frags.append(rect(670, 245, 340, 30, rx=4, fill=FIELD_F, stroke=FIELD_S, sw=1.5))
    frags.append(mtext(840, 265, ["x ∈ L: ≥ 1/2"], size=12, bold=True, color=FIELD_S))

    frags.append(line(1010, 250, 1010, 270, color="#2c3e50", sw=2))
    frags.append(mtext(1010, 290, ["1"], size=12, bold=True))

    # Секція ZPP (нижня вісь)
    frags.append(textbox(150, 390, "Клас ZPP", size=15, bold=True, fill=PURPLE_F, stroke=PURPLE_S, sw=2, pad=10)[0])
    frags.append(rect(270, 370, 740, 40, rx=6, fill="#f4ecf7", stroke=PURPLE_S, sw=1.5))
    frags.append(mtext(640, 395, ["Нульова хиба: повертає точний результат або '?' з імовірністю ≤ 1/2"],
                       size=13, bold=True, color=PURPLE_S))

    # Пояснювальний блок знизу
    frags.append(textbox(540, 470, "BPP дозволяє двосторонній ризик помилки, але зазор 1/3 дозволяє мажоритарне підсилення",
                         size=13, fill="#ffffff", stroke="#7f8c8d", sw=1.2, pad=8)[0])

    render(os.path.join(IMG, "bpp-acceptance-gap.svg"), W, H, *frags,
           title="Порівняння порогових зазорів у ймовірнісних класах")


def fig_error_amplification_chernoff():
    """Графік ампліфікації помилки від кількості запусків k."""
    W, H = 1000, 500
    frags = []

    # Осі координат
    ox, oy = 140, 400
    w_axis, h_axis = 760, 310

    frags.append(arrow(ox, oy, ox + w_axis, oy, color="#2c3e50", sw=2))  # X: k (число випробувань)
    frags.append(arrow(ox, oy, ox, oy - h_axis, color="#2c3e50", sw=2))  # Y: Prob(Error)

    frags.append(mtext(ox + w_axis - 20, oy + 30, ["k (повторення)"], size=13, bold=True))
    frags.append(mtext(ox - 70, oy - h_axis + 10, ["Імовірність", "помилки"], size=12, bold=True))

    # Позначки Y
    y_marks = [(400, "1/3 ≈ 0.333"), (310, "1/10 = 0.100"), (220, "1/100 = 0.010"), (130, "2⁻¹⁰ ≈ 0.001")]
    for y_pos, label in y_marks:
        frags.append(line(ox - 5, y_pos, ox + 5, y_pos, color="#2c3e50", sw=1.5))
        frags.append(line(ox, y_pos, ox + w_axis - 40, y_pos, color="#eaeded", sw=1, dash="3 3"))
        frags.append(mtext(ox - 60, y_pos + 5, [label], size=11, anchor="end"))

    # Позначки X
    x_marks = [(140, "k=1"), (270, "k=5"), (400, "k=10"), (530, "k=20"), (660, "k=50"), (790, "k=100")]
    for x_pos, label in x_marks:
        frags.append(line(x_pos, oy - 5, x_pos, oy + 5, color="#2c3e50", sw=1.5))
        frags.append(line(x_pos, oy, x_pos, oy - h_axis + 40, color="#eaeded", sw=1, dash="3 3"))
        frags.append(mtext(x_pos, oy + 25, [label], size=12, bold=True))

    # Крива експоненційного спадання (по точках)
    pts = [(140, 400), (270, 310), (400, 220), (530, 160), (660, 120), (790, 105)]
    path_d = f"M {pts[0][0]} {pts[0][1]} C 210 340, 310 240, {pts[2][0]} {pts[2][1]} S 600 130, {pts[5][0]} {pts[5][1]}"
    frags.append(f'<path d="{path_d}" fill="none" stroke="#e74c3c" stroke-width="3.5" />')

    # Точки на кривій
    for px, py in pts:
        frags.append(circle(px, py, 5, fill="#e74c3c", stroke="#ffffff", sw=2))

    # Анотація формули Чернова вгорі праворуч (поза кривою)
    frags.append(textbox(750, 180, "P(Error) ≤ exp(-2 · k · ε²)", size=13, bold=True,
                         fill=POS_F, stroke=POS_S, sw=2, pad=10)[0])
    frags.append(textbox(750, 235, "При ε = 1/6 та k = 100:\nпомилка < 10⁻¹⁰", size=12,
                         fill="#ffffff", stroke="#bdc3c7", sw=1.2, pad=8)[0])

    render(os.path.join(IMG, "error-amplification-chernoff.svg"), W, H, *frags,
           title="Експоненційне згасання імовірності помилки (Межа Чернова)")


def fig_complexity_hierarchy_bpp():
    """Вкладення класу BPP у складнісну ієрархію."""
    W, H = 1000, 540
    frags = []

    # PSPACE (зовнішній контур)
    frags.append(rect(60, 80, 880, 420, rx=16, fill="#f4f6f7", stroke="#7f8c8d", sw=2))
    frags.append(mtext(130, 110, ["PSPACE"], size=16, bold=True, color="#7f8c8d"))

    # PH (Поліноміальна ієрархія)
    frags.append(rect(100, 130, 800, 350, rx=14, fill="#ebf5fb", stroke="#2980b9", sw=2))
    frags.append(mtext(180, 155, ["PH (Поліноміальна ієрархія)"], size=15, bold=True, color="#2980b9"))

    # Σ₂ᵖ ∩ Π₂ᵖ (Рівень 2 PH)
    frags.append(rect(140, 175, 720, 285, rx=12, fill="#e8f8f5", stroke="#16a085", sw=2))
    frags.append(mtext(260, 200, ["Σ₂ᵖ ∩ Π₂ᵖ (Теорема Зіпсера — Ґачса — Лотемана)"], size=14, bold=True, color="#16a085"))

    # BPP (ймовірнісний поліноміальний час)
    frags.append(rect(180, 220, 640, 220, rx=10, fill=AMBER_F, stroke=AMBER_S, sw=2.5))
    frags.append(mtext(230, 245, ["BPP"], size=16, bold=True, color=AMBER_S))

    # RP (ліворуч)
    frags.append(rect(200, 260, 180, 160, rx=8, fill=FIELD_F, stroke=FIELD_S, sw=2))
    frags.append(mtext(290, 285, ["RP (Одностороння)"], size=12, bold=True, color=FIELD_S))

    # coRP (праворуч)
    frags.append(rect(620, 260, 180, 160, rx=8, fill=POS_F, stroke=POS_S, sw=2))
    frags.append(mtext(710, 285, ["coRP (Обернений)"], size=12, bold=True, color=POS_S))

    # ZPP (посередині, між RP та coRP)
    frags.append(rect(395, 260, 210, 160, rx=8, fill=PURPLE_F, stroke=PURPLE_S, sw=2))
    frags.append(mtext(500, 285, ["ZPP = RP ∩ coRP"], size=12, bold=True, color=PURPLE_S))

    # P всередині ZPP
    frags.append(rect(435, 330, 130, 65, rx=6, fill="#ffffff", stroke="#2c3e50", sw=2))
    frags.append(mtext(500, 368, ["P"], size=15, bold=True, color="#2c3e50"))

    # Текст про P/poly
    frags.append(textbox(750, 105, "Теорема Адлемана:\nBPP ⊆ P/poly", size=12, bold=True,
                         fill="#fef9e7", stroke="#f1c40f", sw=1.8, pad=8)[0])

    render(os.path.join(IMG, "complexity-hierarchy-bpp.svg"), W, H, *frags,
           title="Місце BPP у загальній ієрархії складністей")


if __name__ == "__main__":
    fig_bpp_acceptance_gap()
    fig_error_amplification_chernoff()
    fig_complexity_hierarchy_bpp()
    print("Всі фігури для BPP згенеровано успішно.")
