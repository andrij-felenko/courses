# -*- coding: utf-8 -*-
"""Фігури для теми «Класи складності логарифмічної пам'яті L та NL» (book/algorithms/complexity-computability/l-nl-logspace)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

# Кольорова палітра для схем складності
AMBER_F, AMBER_S = "#fff6e5", "#e08a1e"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
BLUE_F, BLUE_S = "#eef2ff", "#3b82f6"
GREEN_F, GREEN_S = "#f0fdf4", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"


def fig_logspace_machine():
    """logspace-machine.svg: Стрічкова модель машини Тюринга з логарифмічною пам'яттю."""
    W, H = 840, 420
    frags = []

    # Головний контейнер
    frags.append(rect(10, 10, 820, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # 1. Вхідна стрічка (Read-Only)
    frags.append(rect(40, 30, 760, 90, fill=BLUE_F, stroke=BLUE_S, sw=2, rx=8))
    frags.append(text(250, 52, "Вхідна стрічка (Тільки для читання, довжина n бітів)", size=13, bold=True, color=BLUE_S))
    
    # Комірки вхідної стрічки
    cell_w = 40
    start_x = 180
    cells = ["1", "0", "1", "1", "0", "1", "0", "0", "1", "1", "0", "1"]
    for i, char in enumerate(cells):
        x = start_x + i * cell_w
        is_read = (i == 4)
        bg = AMBER_F if is_read else "#ffffff"
        st = AMBER_S if is_read else "#94a3b8"
        frags.append(rect(x, 62, cell_w, 40, fill=bg, stroke=st, sw=1.5 if not is_read else 2))
        frags.append(text(x + 20, 87, char, size=15, bold=True, color=AMBER_S if is_read else INK))

    # 2. Скінченний контроль (State Control)
    frags.append(rect(320, 160, 200, 80, fill=PURPLE_F, stroke=PURPLE_S, sw=2.5, rx=10))
    frags.append(text(420, 192, "Скінченний контроль", size=14, bold=True, color=PURPLE_S))
    frags.append(text(420, 218, "Стан q ∈ Q", size=13, bold=True, color=INK))

    # Стрілка зчитування входу
    frags.append(arrow(420, 160, start_x + 4 * cell_w + 20, 104, color=AMBER_S, sw=2))
    frags.append(text(285, 140, "Головка читання входу (Вказівник i ∈ [1..n])", size=11, bold=True, color=AMBER_S))

    # 3. Робоча стрічка (Read-Write, обмежена c·log₂ n бітами)
    frags.append(rect(40, 280, 420, 110, fill=GREEN_F, stroke=GREEN_S, sw=2, rx=8))
    frags.append(text(230, 302, "Робоча стрічка (Запис/Читання, O(log n) бітів)", size=13, bold=True, color=GREEN_S))
    
    # Робочі комірки
    w_cells = ["i=4", "cnt=2", "st=1", "0", "1"]
    for i, label in enumerate(w_cells):
        x = 60 + i * 75
        frags.append(rect(x, 315, 70, 40, fill="#ffffff", stroke=GREEN_S, sw=1.5))
        frags.append(text(x + 35, 340, label, size=12, bold=True, color=GREEN_S))
    
    frags.append(text(250, 377, "Зберігає лише лічену кількість вказівників!", size=11, italic=True, color=GREEN_S))

    # Стрілка до робочої стрічки
    frags.append(arrow(370, 240, 270, 280, color=GREEN_S, sw=2))

    # 4. Вихідна стрічка (Write-Only Transducer output)
    frags.append(rect(500, 280, 300, 110, fill=GRAY_F, stroke=GRAY_S, sw=2, rx=8))
    frags.append(text(650, 302, "Вихідна стрічка (Тільки для запису)", size=13, bold=True, color=GRAY_S))
    
    out_cells = ["y₁", "y₂", "y₃", "..."]
    for i, label in enumerate(out_cells):
        x = 520 + i * 55
        frags.append(rect(x, 315, 50, 40, fill="#ffffff", stroke=GRAY_S, sw=1.5))
        frags.append(text(x + 25, 340, label, size=13, bold=True, color=INK))

    frags.append(text(650, 377, "Рух головки тільки вправо (без перечитання)", size=10, italic=True, color=GRAY_S))
    frags.append(arrow(470, 240, 580, 280, color=GRAY_S, sw=2))

    render(os.path.join(IMG, "logspace-machine.svg"), W, H, *frags)


def fig_logspace_hierarchy():
    """logspace-hierarchy.svg: Вкладеність класів складності L ⊆ NL = coNL ⊆ L² ⊆ P ⊆ PSPACE."""
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, 820, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # PSPACE
    frags.append(rect(30, 30, 780, 400, fill=PURPLE_F, stroke=PURPLE_S, sw=2, rx=12))
    frags.append(text(420, 55, "PSPACE — Поліноміальна пам'ять (TQBF)", size=15, bold=True, color=PURPLE_S))

    # P
    frags.append(rect(55, 75, 730, 340, fill=BLUE_F, stroke=BLUE_S, sw=2, rx=10))
    frags.append(text(420, 98, "P — Поліноміальний час (Складеність чисел, Знаходження лінійних шляхів)", size=14, bold=True, color=BLUE_S))

    # L² (DSPACE(log² n)) — Межа Савича
    frags.append(rect(80, 120, 680, 280, fill=GRAY_F, stroke=GRAY_S, sw=2, rx=8))
    frags.append(text(420, 142, "L² = DSPACE(log² n) — Полілогарифмічна пам'ять (Теорема Савича)", size=13, bold=True, color=GRAY_S))

    # NL = coNL
    frags.append(rect(105, 165, 630, 220, fill=AMBER_F, stroke=AMBER_S, sw=2.5, rx=8))
    frags.append(text(420, 188, "NL = coNL — Недетермінований Logspace (Теорема Іммермана-Сделепченей)", size=14, bold=True, color=AMBER_S))
    frags.append(text(620, 212, "NL-повні: ST-CONN, 2SAT", size=12, bold=True, color=AMBER_S))

    # L (Детермінований Logspace)
    frags.append(rect(130, 230, 420, 135, fill=GREEN_F, stroke=GREEN_S, sw=2.5, rx=8))
    frags.append(text(340, 255, "L (LOGSPACE) — Детермінована O(log n)", size=14, bold=True, color=GREEN_S))
    frags.append(text(340, 285, "Регулярні мови, Паліндроми", size=12, color=INK))
    frags.append(text(340, 312, "USTCONN ∈ L (Теорема Рейнгольда, 2004)", size=12, bold=True, color=GREEN_S))

    # L-повнота примітка
    frags.append(rect(570, 240, 150, 110, fill="#ffffff", stroke="#94a3b8", sw=1.5, rx=6))
    frags.append(text(645, 265, "Зведення ≤_L", size=12, bold=True, color=INK))
    frags.append(text(645, 290, "Логарифмічний", size=11, color=INK))
    frags.append(text(645, 308, "трансд'юсер", size=11, color=INK))
    frags.append(text(645, 330, "використовує O(log n)", size=10, italic=True, color=GRAY_S))

    render(os.path.join(IMG, "logspace-hierarchy.svg"), W, H, *frags)


def fig_inductive_counting():
    """inductive-counting.svg: Алгоритм індуктивного підрахунку Іммермана-Сделепченей."""
    W, H = 840, 420
    frags = []

    frags.append(rect(10, 10, 820, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # База індукції
    frags.append(rect(30, 30, 220, 360, fill=GREEN_F, stroke=GREEN_S, sw=2, rx=8))
    frags.append(text(140, 58, "1. База (k = 0)", size=14, bold=True, color=GREEN_S))
    frags.append(rect(50, 85, 180, 60, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(140, 110, "R₀ = {s}", size=13, bold=True, color=INK))
    frags.append(text(140, 130, "|R₀| = 1", size=13, bold=True, color=GREEN_S))
    frags.append(text(140, 175, "Початкова вершина s", size=11, color=INK))
    frags.append(text(140, 195, "досяжна за 0 кроків.", size=11, color=INK))

    # Крок індукції
    frags.append(rect(280, 30, 280, 360, fill=AMBER_F, stroke=AMBER_S, sw=2, rx=8))
    frags.append(text(420, 58, "2. Перехід k ──> k+1", size=14, bold=True, color=AMBER_S))
    
    frags.append(rect(295, 85, 250, 120, fill="#ffffff", stroke=AMBER_S, sw=1.5, rx=6))
    frags.append(text(420, 108, "Для кожної вершини v ∈ V:", size=12, bold=True, color=INK))
    frags.append(text(420, 130, "Вгадуємо |Rₖ| вершин u,", size=11, color=INK))
    frags.append(text(420, 148, "перевіряємо досяжність за k кроків", size=11, color=INK))
    frags.append(text(420, 166, "та наявність ребра (u, v).", size=11, color=INK))
    frags.append(text(420, 188, "Якщо так ──> |Rₖ₊₁|++", size=12, bold=True, color=AMBER_S))

    frags.append(rect(295, 220, 250, 150, fill="#ffffff", stroke=AMBER_S, sw=1.5, rx=6))
    frags.append(text(420, 245, "Параметри в пам'яті:", size=12, bold=True, color=INK))
    frags.append(text(420, 270, "• Лічильник k ∈ [0..n]", size=11, color=INK))
    frags.append(text(420, 290, "• Розмір |Rₖ| ∈ [1..n]", size=11, color=INK))
    frags.append(text(420, 310, "• Поточна вершина v ∈ V", size=11, color=INK))
    frags.append(text(420, 335, "Разом: 4-5 лічильників = O(log n)", size=11, bold=True, color=AMBER_S))

    # Стрілки між етапами
    frags.append(arrow(250, 210, 280, 210, color=GRAY_S, sw=2))
    frags.append(arrow(560, 210, 590, 210, color=GRAY_S, sw=2))

    # Перевірка недеосяжності
    frags.append(rect(590, 30, 220, 360, fill=PURPLE_F, stroke=PURPLE_S, sw=2, rx=8))
    frags.append(text(700, 58, "3. Фінал (k = n)", size=14, bold=True, color=PURPLE_S))
    frags.append(rect(605, 85, 190, 140, fill="#ffffff", stroke=PURPLE_S, sw=1.5, rx=6))
    frags.append(text(700, 110, "Маємо точне |Rₙ|", size=13, bold=True, color=PURPLE_S))
    frags.append(text(700, 138, "Вгадуємо |Rₙ| вершин,", size=11, color=INK))
    frags.append(text(700, 158, "перевіряємо їх досяжність", size=11, color=INK))
    frags.append(text(700, 178, "і що жодна z ≠ t.", size=11, color=INK))
    frags.append(text(700, 205, "Якщо усе вірно ──> t ∉ Rₙ!", size=12, bold=True, color=PURPLE_S))

    render(os.path.join(IMG, "inductive-counting.svg"), W, H, *frags)


def fig_transducer_composition():
    """transducer-composition.svg: Віртуальна композиція логарифмічних трансд'юсерів g(f(x))."""
    W, H = 840, 380
    frags = []

    frags.append(rect(10, 10, 820, 360, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))

    # Верхній розділ: Проблема прямого збереження
    frags.append(rect(30, 25, 780, 120, fill=RED_F, stroke=RED_S, sw=1.5, rx=8))
    frags.append(text(420, 48, "Прямий підхід (Помилковий): Збереження проміжного результату f(x)", size=13, bold=True, color=RED_S))
    frags.append(rect(60, 65, 160, 45, fill="#ffffff", stroke=RED_S, sw=1))
    frags.append(text(140, 92, "Вхід x (n бітів)", size=12, color=INK))
    frags.append(arrow(220, 87, 280, 87, color=RED_S, sw=2))
    
    frags.append(rect(280, 65, 140, 45, fill="#ffffff", stroke=RED_S, sw=1.5))
    frags.append(text(350, 92, "Трансд'юсер f", size=12, bold=True, color=RED_S))
    frags.append(arrow(420, 87, 480, 87, color=RED_S, sw=2))

    frags.append(rect(480, 65, 150, 45, fill=RED_F, stroke=RED_S, sw=2))
    frags.append(text(555, 85, "Стрічка f(x)", size=12, bold=True, color=RED_S))
    frags.append(text(555, 102, "O(n^k) бітів! ✖", size=11, bold=True, color=RED_S))

    frags.append(arrow(630, 87, 680, 87, color=RED_S, sw=2))
    frags.append(rect(680, 65, 110, 45, fill="#ffffff", stroke=RED_S, sw=1))
    frags.append(text(735, 92, "Трансд me g", size=12, color=INK))
    frags.append(text(420, 132, "Порушення обмеження O(log n): проміжний вихід не вміщується у пам'ять!", size=11, italic=True, color=RED_S))

    # Нижній розділ: Лінива обчислювальна композиція
    frags.append(rect(30, 165, 780, 190, fill=GREEN_F, stroke=GREEN_S, sw=2, rx=8))
    frags.append(text(420, 190, "Коректний підхід: Віртуальний запит біта за вимогою (On-Demand Bit Query)", size=14, bold=True, color=GREEN_S))

    frags.append(rect(60, 210, 220, 120, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(170, 235, "Трансд'юсер g", size=13, bold=True, color=GREEN_S))
    frags.append(text(170, 260, "Потребує i-й біт", size=12, color=INK))
    frags.append(text(170, 280, "проміжного входу f(x)", size=12, color=INK))
    frags.append(text(170, 310, "Зберігає лише індекс i ∈ O(log n)", size=10, bold=True, color=GREEN_S))

    # Запит біта
    frags.append(arrow(280, 250, 440, 250, color=BLUE_S, sw=2))
    frags.append(text(360, 242, "1. Запит: «Дай i-й біт!»", size=11, bold=True, color=BLUE_S))

    # Відповідь з бітом
    frags.append(arrow(440, 290, 280, 290, color=GREEN_S, sw=2))
    frags.append(text(360, 308, "2. Повернення: 0 або 1", size=11, bold=True, color=GREEN_S))

    frags.append(rect(440, 210, 340, 120, fill="#ffffff", stroke=GREEN_S, sw=1.5, rx=6))
    frags.append(text(610, 235, "Симулятор f на вході x", size=13, bold=True, color=GREEN_S))
    frags.append(text(610, 260, "Перезапускає f(x) від початку,", size=11, color=INK))
    frags.append(text(610, 280, "відраховує i виведених бітів,", size=11, color=INK))
    frags.append(text(610, 300, "повертає i-й біт і скидає стан", size=11, color=INK))
    frags.append(text(610, 320, "Пам'ять: O(log n) для f + O(log n) для g", size=10, bold=True, color=GREEN_S))

    render(os.path.join(IMG, "transducer-composition.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_logspace_machine()
    fig_logspace_hierarchy()
    fig_inductive_counting()
    fig_transducer_composition()
    print("Всі фігури успішно згенеровані у теці img/")
