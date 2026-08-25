# -*- coding: utf-8 -*-
"""Фігури для теми «Ейлерів цикл» (book/algorithms/complexity-computability/eulerian-cycle)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def svg_path(d, fill="none", stroke=LINE, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def fig_konigsberg_bridges():
    """fig1-konigsberg-bridges.svg: Модель семи мостів Кенігсберга та відповідний мультиграф з непарними степенями."""
    W, H = 880, 450
    frags = []

    frags.append(rect(10, 10, 860, 430, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Задача про сім мостів Кенігсберга (Леонард Ейлер, 1736)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Географічна схема (4 сухопутні області та 7 мостів через річку Преголя)
    frags.append(rect(30, 65, 390, 360, fill="#e0f2fe", stroke="#0284c7", sw=1.5, rx=8))
    frags.append(text(225, 90, "Карта суші та річки Преголя", size=14, bold=True, color="#0369a1"))

    # Острів Кнайпгоф (A) посередині
    frags.append(rect(140, 205, 145, 50, fill="#fef3c7", stroke="#d97706", sw=2, rx=25))
    frags.append(text(212, 235, "Острів A", size=13, bold=True, color="#b45309"))

    # Північний берег (B)
    frags.append(rect(60, 110, 330, 40, fill="#dcfce7", stroke="#15803d", sw=2, rx=6))
    frags.append(text(225, 133, "Північний берег B", size=13, bold=True, color="#15803d"))

    # Південний берег (C)
    frags.append(rect(60, 320, 330, 40, fill="#dcfce7", stroke="#15803d", sw=2, rx=6))
    frags.append(text(225, 343, "Південний берег C", size=13, bold=True, color="#15803d"))

    # Східний берег / Ломсе (D)
    frags.append(rect(335, 185, 60, 90, fill="#fef3c7", stroke="#d97706", sw=2, rx=25))
    frags.append(text(365, 235, "Схід D", size=12, bold=True, color="#b45309"))

    # 7 мостів (коричневі прямокутники)
    # 2 мости між B та A
    frags.append(rect(160, 150, 20, 55, fill="#78350f", stroke="#451a03", rx=3))
    frags.append(rect(220, 150, 20, 55, fill="#78350f", stroke="#451a03", rx=3))

    # 2 мости між C та A
    frags.append(rect(160, 255, 20, 65, fill="#78350f", stroke="#451a03", rx=3))
    frags.append(rect(220, 255, 20, 65, fill="#78350f", stroke="#451a03", rx=3))

    # 1 міст між A та D
    frags.append(rect(290, 220, 40, 20, fill="#78350f", stroke="#451a03", rx=3))

    # 1 міст між B та D
    frags.append(svg_path("M 330,145 L 360,185", fill="none", stroke="#78350f", sw=8))

    # 1 міст між C та D
    frags.append(svg_path("M 330,315 L 360,275", fill="none", stroke="#78350f", sw=8))

    # Права частина: Абстракція у вигляді мультиграфа
    frags.append(rect(460, 65, 390, 360, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(655, 90, "Мультиграф задачі (Вершини = Суша, Ребра = Мости)", size=13, bold=True, color="#334155"))

    # Вершини мультиграфа
    # A (центр)
    b_va, _, _ = textbox(655, 220, "A (deg = 5)", size=13, bold=True, fill=RED_F, stroke=RED_S)
    # B (верх)
    b_vb, _, _ = textbox(655, 130, "B (deg = 3)", size=13, bold=True, fill=RED_F, stroke=RED_S)
    # C (низ)
    b_vc, _, _ = textbox(655, 310, "C (deg = 3)", size=13, bold=True, fill=RED_F, stroke=RED_S)
    # D (право)
    b_vd, _, _ = textbox(790, 220, "D (deg = 3)", size=13, bold=True, fill=RED_F, stroke=RED_S)

    frags.append(b_va)
    frags.append(b_vb)
    frags.append(b_vc)
    frags.append(b_vd)

    # Подвійні ребра B-A
    frags.append(svg_path("M 635,150 Q 610,185 635,210", fill="none", stroke=AMBER_S, sw=2.5))
    frags.append(svg_path("M 675,150 Q 700,185 675,210", fill="none", stroke=AMBER_S, sw=2.5))

    # Подвійні ребра C-A
    frags.append(svg_path("M 635,290 Q 610,255 635,230", fill="none", stroke=AMBER_S, sw=2.5))
    frags.append(svg_path("M 675,290 Q 700,255 675,230", fill="none", stroke=AMBER_S, sw=2.5))

    # Одинарне ребро A-D
    frags.append(line(710, 220, 740, 220, color=AMBER_S, sw=2.5))

    # Одинарне ребро B-D
    frags.append(line(700, 140, 770, 200, color=AMBER_S, sw=2.5))

    # Одинарне ребро C-D
    frags.append(line(700, 300, 770, 240, color=AMBER_S, sw=2.5))

    # Підсумок у виклику (підігнаний розмір шрифту 10.5, щоб влізом у прямокутник шириною 350)
    b_reason, _, _ = textbox(655, 380, "Усі 4 вершини мають непарні степені (5, 3, 3, 3)\nотже Ейлерів цикл у даній системі не існує!", size=10, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_reason)

    render(os.path.join(IMG, "fig1-konigsberg-bridges.svg"), W, H, *frags)


def fig_hierholzer_splicing():
    """fig2-hierholzer-splicing.svg: Алгоритм Гіргольцера — декомпозиція графа на прості цикли та їх зрощування."""
    W, H = 880, 460
    frags = []

    frags.append(rect(10, 10, 860, 440, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Алгоритм Гіргольцера: Побудова та зрощування суб-циклів", size=16, bold=True, color="#1e293b"))

    # Етап 1: Первинний цикл C1
    frags.append(rect(30, 65, 390, 175, fill="#ffffff", stroke=BLUE_S, sw=1.5, rx=8))
    frags.append(text(225, 88, "Етап 1: Знаходження первинного циклу C₁", size=13, bold=True, color=BLUE_S))

    # Трикутник A-B-C-A
    b_a1, _, _ = textbox(100, 180, "A", size=13, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_b1, _, _ = textbox(225, 120, "B", size=13, bold=True, fill=BLUE_F, stroke=BLUE_S)
    b_c1, _, _ = textbox(350, 180, "C", size=13, bold=True, fill=BLUE_F, stroke=BLUE_S)
    frags.append(b_a1)
    frags.append(b_b1)
    frags.append(b_c1)

    frags.append(arrow(120, 170, 205, 130, color=BLUE_S, sw=2))
    frags.append(arrow(245, 130, 330, 170, color=BLUE_S, sw=2))
    frags.append(arrow(330, 180, 120, 180, color=BLUE_S, sw=2))
    frags.append(text(225, 215, "Цикл C₁: (A → B → C → A)", size=11, bold=True, color=BLUE_S))

    # Етап 2: Вторинний цикл C2 від вершини B
    frags.append(rect(460, 65, 390, 175, fill="#ffffff", stroke=TEAL_S, sw=1.5, rx=8))
    frags.append(text(655, 88, "Етап 2: Пошук циклу C₂ у невідвіданих ребрах від B", size=13, bold=True, color=TEAL_S))

    b_b2, _, _ = textbox(655, 120, "B (спільна)", size=12, bold=True, fill=PURPLE_F, stroke=PURPLE_S)
    b_d2, _, _ = textbox(570, 180, "D", size=13, bold=True, fill=TEAL_F, stroke=TEAL_S)
    b_e2, _, _ = textbox(740, 180, "E", size=13, bold=True, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b_b2)
    frags.append(b_d2)
    frags.append(b_e2)

    frags.append(arrow(630, 135, 585, 165, color=TEAL_S, sw=2))
    frags.append(arrow(590, 180, 720, 180, color=TEAL_S, sw=2))
    frags.append(arrow(725, 165, 680, 135, color=TEAL_S, sw=2))
    frags.append(text(655, 215, "Додатковий цикл C₂: (B → D → E → B)", size=11, bold=True, color=TEAL_S))

    # Стрілка вниз: Зрощування циклів
    frags.append(arrow(440, 250, 440, 280, color="#475569", sw=2.5))
    frags.append(text(440, 265, "Вставка (Splicing) циклу C₂ у точку B циклу C₁", size=12, bold=True, color="#475569"))

    # Етап 3: Об'єднаний Ейлерів цикл
    frags.append(rect(30, 290, 820, 145, fill=GREEN_F, stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(440, 315, "Фінальний зрощений Ейлерів цикл C = C₁ ⋈ C₂", size=14, bold=True, color=GREEN_S))

    # Послідовність вершин зрощеного циклу
    seq_nodes = ["A", "B", "D", "E", "B", "C", "A"]
    xs = [80, 200, 320, 440, 560, 680, 800]
    colors = [BLUE_F, PURPLE_F, TEAL_F, TEAL_F, PURPLE_F, BLUE_F, BLUE_F]
    strokes = [BLUE_S, PURPLE_S, TEAL_S, TEAL_S, PURPLE_S, BLUE_S, BLUE_S]

    for i in range(len(seq_nodes)):
        b_node, _, _ = textbox(xs[i], 360, seq_nodes[i], size=14, bold=True, fill=colors[i], stroke=strokes[i])
        frags.append(b_node)
        if i < len(seq_nodes) - 1:
            edge_color = TEAL_S if (i in [1, 2, 3]) else BLUE_S
            frags.append(arrow(xs[i] + 25, 360, xs[i+1] - 25, 360, color=edge_color, sw=2.5))

    frags.append(text(440, 410, "Послідовність проходження: A → (Вхід у C₂: B → D → E → B) → Повернення в C₁: C → A", size=12, bold=True, color="#166534"))

    render(os.path.join(IMG, "fig2-hierholzer-splicing.svg"), W, H, *frags)


def fig_directed_euler_degree():
    """fig3-directed-euler-degree.svg: Баланс степеней вершин у орієнтованому графі (Ейлерів vs Не-Ейлерів)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Критерій Ейлерового циклу в орієнтованому графі: deg⁺(v) = deg⁻(v)", size=16, bold=True, color="#1e293b"))

    # Ліва частина: Ейлерів орієнтований граф (баланс витримано)
    frags.append(rect(30, 65, 390, 325, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(225, 90, "Збалансований орієнтований граф (Ейлерів)", size=13, bold=True, color=GREEN_S))

    # Вершини V1, V2, V3
    b_v1, _, _ = textbox(130, 160, "V₁\n(in=2, out=2)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_v2, _, _ = textbox(320, 160, "V₂\n(in=1, out=1)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_v3, _, _ = textbox(225, 280, "V₃\n(in=1, out=1)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_v1)
    frags.append(b_v2)
    frags.append(b_v3)

    # Направлені ребра
    frags.append(arrow(165, 150, 275, 150, color=GREEN_S, sw=2))
    frags.append(arrow(320, 195, 260, 265, color=GREEN_S, sw=2))
    frags.append(arrow(190, 265, 140, 195, color=GREEN_S, sw=2))
    # Петля на V1
    frags.append(svg_path("M 105,145 C 60,110 60,200 102,165", fill="none", stroke=GREEN_S, sw=2))

    b_valid, _, _ = textbox(225, 355, "Для всіх v ∈ V: in-degree(v) == out-degree(v)\nі граф сильно зв'язний ⇒ Є Ейлерів цикл", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_valid)

    # Права частина: Незбалансований орієнтований граф (НЕ-Ейлерів)
    frags.append(rect(460, 65, 390, 325, fill="#ffffff", stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(655, 90, "Незбалансований граф (Дисбаланс степеней)", size=13, bold=True, color=RED_S))

    b_u1, _, _ = textbox(560, 160, "U₁\nin=1, out=2 ✖", size=11, bold=True, fill=RED_F, stroke=RED_S)
    b_u2, _, _ = textbox(750, 160, "U₂\nin=2, out=1 ✖", size=11, bold=True, fill=RED_F, stroke=RED_S)
    b_u3, _, _ = textbox(655, 280, "U₃\nin=1, out=1 ✓", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_u1)
    frags.append(b_u2)
    frags.append(b_u3)

    # Направлені ребра з надлишком
    frags.append(svg_path("M 595,145 Q 655,120 715,145", fill="none", stroke=RED_S, sw=2))
    frags.append(svg_path("M 595,175 Q 655,200 715,175", fill="none", stroke=RED_S, sw=2))
    frags.append(arrow(750, 195, 690, 265, color=GREEN_S, sw=2))
    frags.append(arrow(620, 265, 570, 195, color=GREEN_S, sw=2))

    b_invalid, _, _ = textbox(655, 355, "Дисбаланс: out(U₁) - in(U₁) = +1 (Джерело)\nin(U₂) - out(U₂) = +1 (Сток) ⇒ Цикл відсутній!", size=11, fill=RED_F, stroke=RED_S)
    frags.append(b_invalid)

    render(os.path.join(IMG, "fig3-directed-euler-degree.svg"), W, H, *frags)


def fig_chinese_postman_matching():
    """fig4-chinese-postman-matching.svg: Задача китайського листоноші — дублювання ребер через паросполучення."""
    W, H = 880, 440
    frags = []

    frags.append(rect(10, 10, 860, 420, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 36, "Задача китайського листоноші (CPP): Перетворення на Ейлерів граф", size=16, bold=True, color="#1e293b"))

    # Етап 1: Вхідний граф з непарними вершинами
    frags.append(rect(30, 65, 390, 345, fill="#ffffff", stroke=AMBER_S, sw=1.5, rx=8))
    frags.append(text(225, 90, "1. Початковий граф із непарними вершинами", size=13, bold=True, color=AMBER_S))

    b_p1, _, _ = textbox(110, 150, "V₁ (deg=3)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    b_p2, _, _ = textbox(340, 150, "V₂ (deg=3)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    b_p3, _, _ = textbox(110, 290, "V₃ (deg=3)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    b_p4, _, _ = textbox(340, 290, "V₄ (deg=3)", size=11, bold=True, fill=RED_F, stroke=RED_S)
    frags.append(b_p1)
    frags.append(b_p2)
    frags.append(b_p3)
    frags.append(b_p4)

    frags.append(line(145, 150, 305, 150, color=GRAY_S, sw=2))
    frags.append(text(225, 135, "w = 4", size=11, color="#475569"))

    frags.append(line(110, 175, 110, 265, color=GRAY_S, sw=2))
    frags.append(text(90, 220, "w = 2", size=11, color="#475569"))

    frags.append(line(340, 175, 340, 265, color=GRAY_S, sw=2))
    frags.append(text(360, 220, "w = 5", size=11, color="#475569"))

    frags.append(line(145, 290, 305, 290, color=GRAY_S, sw=2))
    frags.append(text(225, 305, "w = 3", size=11, color="#475569"))

    frags.append(line(140, 170, 310, 270, color=GRAY_S, sw=2))
    frags.append(text(240, 210, "w = 6", size=11, color="#475569"))

    b_note1, _, _ = textbox(225, 370, "Непарні вершини: V₁, V₂, V₃, V₄ (усього 4)\nПотрібно продублювати шляхи між ними!", size=11, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b_note1)

    # Етап 2: Побудова Ейлерового мультиграфа
    frags.append(rect(460, 65, 390, 345, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=8))
    frags.append(text(655, 90, "2. Продубльовані ребра (Мін. паросполучення)", size=13, bold=True, color=GREEN_S))

    b_q1, _, _ = textbox(540, 150, "V₁ (deg=4)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_q2, _, _ = textbox(770, 150, "V₂ (deg=4)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_q3, _, _ = textbox(540, 290, "V₃ (deg=4)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    b_q4, _, _ = textbox(770, 290, "V₄ (deg=4)", size=11, bold=True, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_q1)
    frags.append(b_q2)
    frags.append(b_q3)
    frags.append(b_q4)

    # Базові ребра
    frags.append(line(575, 150, 735, 150, color=GRAY_S, sw=2))
    frags.append(line(770, 175, 770, 265, color=GRAY_S, sw=2))
    frags.append(line(575, 290, 735, 290, color=GRAY_S, sw=2))
    frags.append(line(570, 170, 740, 270, color=GRAY_S, sw=2))

    # Продубльовані ребра (червоні/пунктирні з мінімальною вагою)
    # Пара (V1, V3) з вагою 2 та пара (V2, V4) з вагою 5
    frags.append(svg_path("M 510,175 Q 490,220 510,265", fill="none", stroke=PURPLE_S, sw=2.5))
    frags.append(text(475, 220, "+V₁-V₃ (w=2)", size=11, bold=True, color=PURPLE_S))

    frags.append(svg_path("M 800,175 Q 820,220 800,265", fill="none", stroke=PURPLE_S, sw=2.5))
    frags.append(text(835, 220, "+V₂-V₄ (w=5)", size=11, bold=True, color=PURPLE_S))

    # Початковий V1-V3
    frags.append(line(540, 175, 540, 265, color=GRAY_S, sw=2))

    b_note2, _, _ = textbox(655, 370, "Додано повторні ребра: (V₁,V₃) та (V₂,V₄)\nМін. додаткова вага = 2 + 5 = 7\nТепер усі степені парні (4) ⇒ Побудовано Ейлерів цикл!", size=11, fill=GREEN_F, stroke=GREEN_S)
    frags.append(b_note2)

    render(os.path.join(IMG, "fig4-chinese-postman-matching.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_konigsberg_bridges()
    fig_hierholzer_splicing()
    fig_directed_euler_degree()
    fig_chinese_postman_matching()
    print("Усі 4 фігури для Ейлерового циклу згенеровано в ./img/")
