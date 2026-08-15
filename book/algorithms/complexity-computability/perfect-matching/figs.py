# -*- coding: utf-8 -*-
"""Фігури для теми «Досконале паросполучення» (book/algorithms/complexity-computability/perfect-matching)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
RED_F, RED_S = "#fef2f2", "#dc2626"

def fig_bipartite_vs_general():
    """fig1-bipartite-vs-general-matching.svg: Порівняння паросполучень у двочасткових та загальних графах."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Паросполучення: двочасткові графи проти загальних графів", size=16, bold=True, color="#1e293b"))

    # Ліва панель: Двочастковий граф (L та R)
    frags.append(rect(25, 60, 405, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(225, 85, "Двочастковий граф G = (L ∪ R, E)", size=13, bold=True, color=BLUE_S))

    # Вершини L
    l_xs = [75] * 4
    l_ys = [125, 185, 245, 305]
    l_names = ["u₁", "u₂", "u₃", "u₄"]
    for x, y, name in zip(l_xs, l_ys, l_names):
        b, _, _ = textbox(x, y, name, size=11, bold=True, fill="#ffffff", stroke=BLUE_S)
        frags.append(b)

    # Вершини R
    r_xs = [175] * 4
    r_ys = [125, 185, 245, 305]
    r_names = ["v₁", "v₂", "v₃", "v₄"]
    for x, y, name in zip(r_xs, r_ys, r_names):
        b, _, _ = textbox(x, y, name, size=11, bold=True, fill="#ffffff", stroke=BLUE_S)
        frags.append(b)

    # Ребра досконалого паросполучення (жирні зелені)
    frags.append(line(95, 125, 155, 125, color=GREEN_S, sw=3.0))
    frags.append(line(95, 185, 155, 245, color=GREEN_S, sw=3.0))
    frags.append(line(95, 245, 155, 185, color=GREEN_S, sw=3.0))
    frags.append(line(95, 305, 155, 305, color=GREEN_S, sw=3.0))

    # Звичайні ребра графа (пунктирні сірі)
    frags.append(line(95, 125, 155, 185, color="#94a3b8", sw=1.2, dash="4 3"))
    frags.append(line(95, 305, 155, 245, color="#94a3b8", sw=1.2, dash="4 3"))

    txt_bip = "• Немає непарних циклів\n• Прості чергувальні шляхи\n• Теорема Голла: |N(S)| ≥ |S|\n• Складність: O(E √V)"
    b_bip_t, _, _ = textbox(315, 215, txt_bip, size=10, fill="#ffffff", stroke=BLUE_S, pad=6)
    frags.append(b_bip_t)

    # Права панель: Загальний граф з непарним циклом (квіткою)
    frags.append(rect(450, 60, 405, 330, fill=AMBER_F, stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(652, 85, "Загальний граф (з непарним циклом C₅)", size=13, bold=True, color=AMBER_S))

    # Вершини непарного циклу C5
    c_coords = [(475, 140, "w₁"), (535, 115, "w₂"), (595, 145, "w₃"), (575, 235, "w₄"), (485, 235, "w₅")]
    for x, y, name in c_coords:
        b, _, _ = textbox(x, y, name, size=11, bold=True, fill=RED_F, stroke=RED_S)
        frags.append(b)

    # Ребра циклу C5
    frags.append(line(493, 140, 517, 115, color=RED_S, sw=2.0))
    frags.append(line(553, 115, 577, 145, color=RED_S, sw=2.0))
    frags.append(line(595, 163, 575, 217, color=RED_S, sw=2.0))
    frags.append(line(557, 235, 503, 235, color=RED_S, sw=2.0))
    frags.append(line(485, 217, 475, 158, color=RED_S, sw=2.0))

    # Зовнішня вершина
    b_ext, _, _ = textbox(530, 320, "v_ext", size=11, bold=True, fill="#ffffff", stroke=AMBER_S)
    frags.append(b_ext)
    frags.append(line(530, 302, 530, 253, color=GREEN_S, sw=3.0))

    txt_gen = "• Наявність непарних циклів (квіток)\n• Зациклення чергувальних шляхів\n• Теорема Тутте: q(G \\ S) ≤ |S|\n• Стискання квіток [Едмондс]"
    b_gen_t, _, _ = textbox(735, 200, txt_gen, size=10, fill="#ffffff", stroke=AMBER_S, pad=6)
    frags.append(b_gen_t)

    render(os.path.join(IMG, "fig1-bipartite-vs-general-matching.svg"), W, H, *frags)


def fig_edmonds_blossom_shrink():
    """fig2-edmonds-blossom-shrink.svg: Процес стискання непарного циклу (квітки) у супервершину."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Алгоритм Едмондса: стискання квітки (Blossom Contraction)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Граф з квіткою C3
    frags.append(rect(25, 60, 395, 340, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(222, 85, "1. Виявлення непарного циклу (квітка B)", size=13, bold=True, color=RED_S))

    # Вершини квітки C3: x, y, z
    b_r, _, _ = textbox(75, 170, "r (корінь)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_x, _, _ = textbox(175, 170, "x (база)", size=11, bold=True, fill=AMBER_F, stroke=AMBER_S)
    b_y, _, _ = textbox(285, 125, "y", size=11, bold=True, fill=RED_F, stroke=RED_S)
    b_z, _, _ = textbox(285, 215, "z", size=11, bold=True, fill=RED_F, stroke=RED_S)

    frags += [b_r, b_x, b_y, b_z]

    # Ребра
    frags.append(line(115, 170, 135, 170, color=GREEN_S, sw=3.0)) # M-ребро
    frags.append(line(215, 170, 270, 125, color=RED_S, sw=2.0))
    frags.append(line(215, 170, 270, 215, color=RED_S, sw=2.0))
    frags.append(line(285, 143, 285, 197, color=GREEN_S, sw=3.0)) # M-ребро в квітці

    txt_l = "• Непарний цикл (довжина 3)\n• Дві парні дуги збігаються у базальній вершині x\n• Необхідно стиснути цикл в одну супервершину"
    b_tl, _, _ = textbox(222, 335, txt_l, size=10, fill="#ffffff", stroke=RED_S, pad=6)
    frags.append(b_tl)

    # Стрілка переходу посередині
    frags.append(arrow(430, 210, 450, 210, color=PURPLE_S, sw=2.5))
    frags.append(text(440, 185, "G ↦ G/B", size=11, bold=True, color=PURPLE_S))

    # Права частина: Фактор-граф G/B з супервершиною B
    frags.append(rect(460, 60, 395, 340, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(657, 85, "2. Фактор-граф G/B із супервершиною B", size=13, bold=True, color=GREEN_S))

    b_r2, _, _ = textbox(520, 170, "r (корінь)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_super, _, _ = textbox(700, 170, "Супервершина B\n(містить x, y, z)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S)

    frags += [b_r2, b_super]

    frags.append(line(560, 170, 630, 170, color=GREEN_S, sw=3.0))

    txt_r = "• Чергувальний шлях будується в G/B\n• Після знайдення шляху B розгортається назад\n• Зберігається коректна парність усередині квітки"
    b_tr, _, _ = textbox(657, 335, txt_r, size=10, fill="#ffffff", stroke=GREEN_S, pad=6)
    frags.append(b_tr)

    render(os.path.join(IMG, "fig2-edmonds-blossom-shrink.svg"), W, H, *frags)


def fig_tutte_matrix_pfaffian():
    """fig3-tutte-matrix-pfaffian.svg: Структура матриці Тутте та детермінантний аналіз."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Алгебраїчна теорія: Матриця Тутте T(G) та фафіан Pf(T)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Кососиметрична матриця Тутте
    frags.append(rect(25, 60, 405, 330, fill=PURPLE_F, stroke=PURPLE_S, sw=1.5, rx=8))
    frags.append(text(227, 85, "Символьна матриця Тутте T(G)", size=13, bold=True, color=PURPLE_S))

    matrix_text = (
        "┌                                   ┐\n"
        "│    0     x₁₂    -x₃₁    0    │\n"
        "│  -x₁₂     0      x₂₃   x₂₄   │\n"
        "│   x₃₁   -x₂₃      0     0    │\n"
        "│    0    -x₂₄      0     0    │\n"
        "└                                   ┘"
    )
    frags.append(text(227, 175, matrix_text, size=13, bold=True, color="#1e293b"))

    txt_tm = "• T[i,j] =  x[i,j]  якщо i < j та (i,j) ∈ E\n• T[i,j] = -x[j,i]  якщо i > j та (i,j) ∈ E\n• T[i,j] =  0       в інших випадках\n• Кососиметрія: Tᵀ = -T"
    b_tm_t, _, _ = textbox(227, 325, txt_tm, size=10, fill="#ffffff", stroke=PURPLE_S, pad=6)
    frags.append(b_tm_t)

    # Права частина: Детермінант та Лема Шварца-Ціппеля
    frags.append(rect(450, 60, 405, 330, fill=BLUE_F, stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(652, 85, "Алгебраїчні властивості та рандомізація", size=13, bold=True, color=BLUE_S))

    b_det, _, _ = textbox(652, 130, "det(T(G)) = (Pf(T(G)))²", size=13, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_det)

    txt_alg = (
        "1. det(T(G)) ≢ 0  ⇔  G має досконале паросполучення\n\n"
        "2. Тест Ловаса (1979):\n"
        "   Замість символів x[i,j] підставляємо випадкові\n"
        "   значення з скінченного поля F_q.\n\n"
        "3. Обчислення det(T) за O(nʷ) через Гаусса.\n\n"
        "4. За лемою Шварца-Ціппеля:\n"
        "   P(помилки) ≤ n / q  (зменшується ростом q)"
    )
    b_alg_t, _, _ = textbox(652, 275, txt_alg, size=10, fill="#ffffff", stroke=BLUE_S, pad=6)
    frags.append(b_alg_t)

    render(os.path.join(IMG, "fig3-tutte-matrix-pfaffian.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_bipartite_vs_general()
    fig_edmonds_blossom_shrink()
    fig_tutte_matrix_pfaffian()
    print("Perfect matching figures generated successfully.")
