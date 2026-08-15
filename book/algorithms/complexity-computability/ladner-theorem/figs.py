# -*- coding: utf-8 -*-
"""Фігури для теми «Теорема Леднера» (book/algorithms/complexity-computability/ladner-theorem)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

COLOR_BG = "#ffffff"
COLOR_HEADER_BG = "#e2e8f0"
COLOR_P_BG = "#d1fae5"         # зелений для класу P
COLOR_P_BORDER = "#059669"
COLOR_NPC_BG = "#fee2e2"       # червоний для NP-повної зони
COLOR_NPC_BORDER = "#dc2626"
COLOR_NPI_BG = "#dbeafe"       # синій для NP-проміжної зони
COLOR_NPI_BORDER = "#2563eb"
COLOR_MUTED = "#64748b"
COLOR_LINE = "#333333"

def fig1_np_structure():
    """Фігура 1: Структура класу NP за умови P != NP (до і після теореми Леднера)."""
    W, H = 960, 520
    frags = []

    # Заголовок
    t_box, _, _ = textbox(480, 35, "Внутрішня геометрія класу NP за умови P ≠ NP",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # Ліва панель — Наївне уявлення (до Леднера)
    frags.append(rect(40, 80, 420, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(250, 110, "Рання ілюзія (до 1975 року)", size=15, bold=True, color="#475569"))
    frags.append(text(250, 132, "NP як сувора бінарна дихотомія", size=13, italic=True, color=COLOR_MUTED))

    # Зона NPC ліворуч
    tb_npc_l, _, _ = textbox(250, 200, "Клас NP-Повних задач (NPC)\n(SAT, 3-SAT, Clique, TSP)",
                             size=13, bold=True, fill=COLOR_NPC_BG, stroke=COLOR_NPC_BORDER, sw=1.5, pad=10)
    frags.append(tb_npc_l)

    frags.append(line(70, 280, 430, 280, color="#94a3b8", sw=1.5, dash="4,4"))
    frags.append(text(250, 305, "Порожнеча? (Жодних задач немає?)", size=13, italic=True, color="#dc2626"))

    # Зона P ліворуч
    tb_p_l, _, _ = textbox(250, 400, "Клас P (Поліномні задачі)\n(Сортування, Найкоротший шлях, 2-SAT)",
                           size=13, bold=True, fill=COLOR_P_BG, stroke=COLOR_P_BORDER, sw=1.5, pad=10)
    frags.append(tb_p_l)

    # Права панель — Картина Леднера (теорема Леднера)
    frags.append(rect(500, 80, 420, 400, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(710, 110, "Картина Леднера (Теорема 1975 р.)", size=15, bold=True, color="#1e3a8a"))
    frags.append(text(710, 132, "Нескінченна щільність класу NP", size=13, italic=True, color=COLOR_MUTED))

    # Зона NPC праворуч
    tb_npc_r, _, _ = textbox(710, 185, "Клас NP-Повних задач (NPC)\n(SAT, 3-SAT, Clique)",
                             size=13, bold=True, fill=COLOR_NPC_BG, stroke=COLOR_NPC_BORDER, sw=1.5, pad=8)
    frags.append(tb_npc_r)

    # Зона NP-Intermediate праворуч
    tb_npi_r, _, _ = textbox(710, 290, "Клас NP-Проміжних задач (NPI)\n(Задачі A, B, C... штучні та кандидати:\nІзоморфізм графів, Факторизація)",
                             size=13, bold=True, fill=COLOR_NPI_BG, stroke=COLOR_NPI_BORDER, sw=1.5, pad=10)
    frags.append(tb_npi_r)

    # Зона P праворуч
    tb_p_r, _, _ = textbox(710, 410, "Клас P (Поліномні задачі)\n(Порожня мова, 2-SAT, Eulerian Path)",
                           size=13, bold=True, fill=COLOR_P_BG, stroke=COLOR_P_BORDER, sw=1.5, pad=8)
    frags.append(tb_p_r)

    # Стрілки зведення <=_p
    frags.append(arrow(710, 365, 710, 340, color=COLOR_NPI_BORDER, sw=2))
    frags.append(arrow(710, 240, 710, 220, color=COLOR_NPC_BORDER, sw=2))

    render(os.path.join(IMG, "fig1-np-structure.svg"), W, H, *frags)


def fig2_delayed_simulation():
    """Фігура 2: Принцип затриманого моделювання та переключення фаз функції H(n)."""
    W, H = 940, 480
    frags = []

    # Заголовок
    t_box, _, _ = textbox(470, 35, "Динаміка затриманого моделювання: фази функції H(n)",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # Ось довжини входу n
    frags.append(line(80, 400, 880, 400, color=COLOR_LINE, sw=2))
    frags.append(arrow(850, 400, 890, 400, color=COLOR_LINE, sw=2))
    frags.append(text(880, 430, "Довжина входу n", size=13, bold=True, color=COLOR_LINE))

    # Фаза 0: H(n) = 0 (Парна) -> спростування P (A = SAT)
    frags.append(rect(80, 100, 250, 260, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(text(205, 130, "Фаза 0: H(n) = 0 (парне)", size=14, bold=True, color="#1e3a8a"))
    frags.append(line(95, 145, 315, 145, color="#93c5fd", sw=1))
    frags.append(mtext(205, 185, "Мова A(x) = SAT(x)\nСимуляція M₀(z)\nШукаємо z: M₀(z) ≠ SAT(z)\nЧасовий бюджет: n³", size=12, color="#1e3a8a"))

    # Фаза 1: H(n) = 1 (Непарна) -> спростування NP-повноти (A = порожня мова)
    frags.append(rect(355, 100, 250, 260, fill="#fef2f2", stroke="#ef4444", sw=1.5, rx=8))
    frags.append(text(480, 130, "Фаза 1: H(n) = 1 (непарне)", size=14, bold=True, color="#991b1b"))
    frags.append(line(370, 145, 590, 145, color="#fca5a5", sw=1))
    frags.append(mtext(480, 185, "Мова A(x) = ∅ (у P)\nСимуляція зведення R₀(z)\nШукаємо z ∈ SAT: R₀(z) ∉ A\nЧасовий бюджет: n³", size=12, color="#991b1b"))

    # Фаза 2: H(n) = 2 (Парна) -> спростування наступної машини M₁
    frags.append(rect(630, 100, 250, 260, fill="#eff6ff", stroke="#3b82f6", sw=1.5, rx=8))
    frags.append(text(755, 130, "Фаза 2: H(n) = 2 (парне)", size=14, bold=True, color="#1e3a8a"))
    frags.append(line(645, 145, 865, 145, color="#93c5fd", sw=1))
    frags.append(mtext(755, 185, "Мова A(x) = SAT(x)\nСимуляція M₁(z)\nШукаємо z: M₁(z) ≠ SAT(z)\nЧасовий бюджет: n³", size=12, color="#1e3a8a"))

    # Переходи між фазами
    frags.append(arrow(330, 230, 355, 230, color="#059669", sw=2))
    frags.append(text(342, 210, "Спростовано!", size=11, bold=True, color="#059669"))

    frags.append(arrow(605, 230, 630, 230, color="#059669", sw=2))
    frags.append(text(617, 210, "Спростовано!", size=11, bold=True, color="#059669"))

    # Позначки на осі n
    frags.append(line(205, 395, 205, 405, color=COLOR_LINE, sw=2))
    frags.append(text(205, 425, "n₀", size=13, bold=True))

    frags.append(line(480, 395, 480, 405, color=COLOR_LINE, sw=2))
    frags.append(text(480, 425, "n₁ (повільне зростання)", size=13, bold=True))

    frags.append(line(755, 395, 755, 405, color=COLOR_LINE, sw=2))
    frags.append(text(755, 425, "n₂", size=13, bold=True))

    render(os.path.join(IMG, "fig2-delayed-simulation.svg"), W, H, *frags)


def fig3_density_hierarchy():
    """Фігура 3: Щільність ступенів складності за теоремою Леднера між A та B."""
    W, H = 880, 440
    frags = []

    # Заголовок
    t_box, _, _ = textbox(440, 35, "Властивість щільності: вставити мову C між A та B",
                          size=17, bold=True, fill=COLOR_HEADER_BG, stroke="#94a3b8", sw=1.5, pad=10)
    frags.append(t_box)

    # Верхня мова B
    tb_b, _, _ = textbox(440, 110, "Верхня мова B ∈ NP (наприклад, SAT)", size=14, bold=True, fill=COLOR_NPC_BG, stroke=COLOR_NPC_BORDER, pad=8)
    frags.append(tb_b)

    # Проміжна мова C
    tb_c, _, _ = textbox(440, 230, "Побудована мова C ∈ NP\n(A <_p C <_p B)", size=14, bold=True, fill=COLOR_NPI_BG, stroke=COLOR_NPI_BORDER, pad=10)
    frags.append(tb_c)

    # Нижня мова A
    tb_a, _, _ = textbox(440, 350, "Нижня мова A ∈ NP (наприклад, порожня мова у P)", size=14, bold=True, fill=COLOR_P_BG, stroke=COLOR_P_BORDER, pad=8)
    frags.append(tb_a)

    # Стрілки зведень
    frags.append(arrow(440, 320, 440, 275, color=COLOR_NPI_BORDER, sw=2))
    frags.append(text(490, 300, "A ≤_p C (і C ≰_p A)", size=12, bold=True, color="#1e3a8a"))

    frags.append(arrow(440, 185, 440, 140, color=COLOR_NPC_BORDER, sw=2))
    frags.append(text(490, 160, "C ≤_p B (і B ≰_p C)", size=12, bold=True, color="#991b1b"))

    # Пояснення праворуч
    frags.append(rect(640, 150, 210, 160, fill="#f8fafc", stroke="#cbd5e1", rx=8))
    frags.append(mtext(745, 180, "Процес можна повторювати\nнескінченно:\nміж A і C → нова мова D\nміж C і B → нова мова E\nУтворюється щільне\nчастково впорядковане дерево", size=12, color=COLOR_MUTED))

    render(os.path.join(IMG, "fig3-density-hierarchy.svg"), W, H, *frags)


if __name__ == "__main__":
    fig1_np_structure()
    fig2_delayed_simulation()
    fig3_density_hierarchy()
    print("Фігури успішно згенеровано у", IMG)
