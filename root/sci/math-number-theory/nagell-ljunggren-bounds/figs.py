import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, circle, arrow, POS, NEG
except ImportError:
    print("ERROR: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def draw_solutions_overview():
    frags = []
    
    # Title box
    frags.append(rect(220, 15, 360, 40, rx=6, fill="#f8f9fa", stroke="#343a40", sw=1.5))
    frags.append(text(400, 40, "Три єдині відомі розв'язки рівняння Нагеля–Люнггрена", size=13, bold=True, color="#212529", anchor="middle"))

    # Connectors
    frags.append(arrow(280, 55, 140, 95, color="#6c757d", sw=1.5))
    frags.append(arrow(400, 55, 400, 95, color="#6c757d", sw=1.5))
    frags.append(arrow(520, 55, 660, 95, color="#6c757d", sw=1.5))

    # Solution 1: x=3, n=5
    frags.append(rect(30, 95, 220, 145, rx=8, fill="#e7f5ff", stroke="#1c7ed6", sw=1.8))
    frags.append(text(140, 122, "Розв'язок 1: x = 3, n = 5", size=13, bold=True, color="#1864ab", anchor="middle"))
    frags.append(rect(45, 135, 190, 30, rx=4, fill="#ffffff", stroke="#74c0fc", sw=1.0))
    frags.append(text(140, 155, "(3⁵ - 1) / (3 - 1) = 242 / 2 = 121", size=11, color="#1c7ed6", anchor="middle"))
    frags.append(text(140, 182, "Форма степеня: 121 = 11²", size=12, bold=True, color="#0b7285", anchor="middle"))
    frags.append(text(140, 205, "Основа y = 11, показник q = 2 (квадрат)", size=10, color="#495057", anchor="middle"))
    frags.append(text(140, 222, "Реп'юніт у трійковій системі: 11111₃", size=10, color="#495057", anchor="middle"))

    # Solution 2: x=7, n=4
    frags.append(rect(290, 95, 220, 145, rx=8, fill="#ebfbee", stroke="#2b8a3e", sw=1.8))
    frags.append(text(400, 122, "Розв'язок 2: x = 7, n = 4", size=13, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(rect(305, 135, 190, 30, rx=4, fill="#ffffff", stroke="#8ce99a", sw=1.0))
    frags.append(text(400, 155, "(7⁴ - 1) / (7 - 1) = 2400 / 6 = 400", size=11, color="#2b8a3e", anchor="middle"))
    frags.append(text(400, 182, "Форма степеня: 400 = 20²", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(400, 205, "Основа y = 20, показник q = 2 (квадрат)", size=10, color="#495057", anchor="middle"))
    frags.append(text(400, 222, "Реп'юніт у сімковій системі: 1111₇", size=10, color="#495057", anchor="middle"))

    # Solution 3: x=18, n=3
    frags.append(rect(550, 95, 220, 145, rx=8, fill="#fff9db", stroke="#f59f00", sw=1.8))
    frags.append(text(660, 122, "Розв'язок 3: x = 18, n = 3", size=13, bold=True, color="#e67700", anchor="middle"))
    frags.append(rect(565, 135, 190, 30, rx=4, fill="#ffffff", stroke="#ffe066", sw=1.0))
    frags.append(text(660, 155, "(18³ - 1) / (18 - 1) = 5831 / 17 = 343", size=11, color="#d9480f", anchor="middle"))
    frags.append(text(660, 182, "Форма степеня: 343 = 7³", size=12, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(660, 205, "Основа y = 7, показник q = 3 (куб)", size=10, color="#495057", anchor="middle"))
    frags.append(text(660, 222, "Реп'юніт у 18-річній системі: 111₁₈", size=10, color="#495057", anchor="middle"))

    # Bottom summary box
    frags.append(rect(100, 260, 600, 45, rx=6, fill="#f1f3f5", stroke="#adb5bd", sw=1.2))
    frags.append(text(400, 287, "Гіпотеза Нагеля–Люнггрена: інших розв'язків у цілих числах не існує", size=12, bold=True, color="#343a40", anchor="middle"))

    render(os.path.join(IMG_DIR, 'fig-solutions-overview.svg'), 800, 320, *frags, title="Огляд трьох відомих розв'язків рівняння Нагеля-Люнггрена")

def draw_cyclotomic_decomposition():
    frags = []

    # Top Box: Repunit N_n(x)
    frags.append(rect(230, 15, 340, 50, rx=6, fill="#f3f0ff", stroke="#7950f2", sw=1.8))
    frags.append(text(400, 36, "Реп'юніт N_n(x) = (xⁿ - 1) / (x - 1)", size=14, bold=True, color="#5f3dc4", anchor="middle"))
    frags.append(text(400, 55, "Сума степеней: 1 + x + x² + ... + xⁿ⁻¹", size=11, color="#7950f2", anchor="middle"))

    # Arrows to factorization components
    frags.append(arrow(320, 65, 180, 110, color="#7950f2", sw=1.5))
    frags.append(arrow(400, 65, 400, 110, color="#7950f2", sw=1.5))
    frags.append(arrow(480, 65, 620, 110, color="#7950f2", sw=1.5))

    # Factor 1: Cyclotomic polynomials
    frags.append(rect(50, 110, 260, 95, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(180, 133, "Кругові многочлени Φ_d(x)", size=13, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(180, 155, "N_n(x) = ∏_{d|n, d>1} Φ_d(x)", size=12, bold=True, color="#1c7ed6", anchor="middle"))
    frags.append(text(180, 175, "Розклад на взаємно прості або", size=10, color="#495057", anchor="middle"))
    frags.append(text(180, 192, "слабко пов'язані множники", size=10, color="#495057", anchor="middle"))

    # Factor 2: Primitive prime divisors (Zsigmondy)
    frags.append(rect(330, 110, 140, 95, rx=6, fill="#fff4e6", stroke="#fd7e14", sw=1.5))
    frags.append(text(400, 133, "Теорема Зігмонді", size=13, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(400, 155, "Примітивний дільник p", size=11, bold=True, color="#e8590c", anchor="middle"))
    frags.append(text(400, 175, "p | (xⁿ - 1), p ∤ (xᵏ - 1)", size=10, color="#495057", anchor="middle"))
    frags.append(text(400, 192, "p ≡ 1 (mod n)", size=10, bold=True, color="#d9480f", anchor="middle"))

    # Factor 3: Target pure power y^q
    frags.append(rect(490, 110, 260, 95, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.5))
    frags.append(text(620, 133, "Вимога точного степеня y^q", size=13, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(620, 155, "Кожен простий множник p | N_n(x)", size=10, color="#495057", anchor="middle"))
    frags.append(text(620, 175, "входить з показником, кратним q", size=10, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(620, 192, "НСД(Φ_d, Φ_k) ділить n", size=10, color="#495057", anchor="middle"))

    # Structural constraint banner at bottom
    frags.append(rect(80, 225, 640, 50, rx=6, fill="#fff0f6", stroke="#e64980", sw=1.5))
    frags.append(text(400, 246, "Жорстке арифметичне обмеження:", size=12, bold=True, color="#c2255c", anchor="middle"))
    frags.append(text(400, 265, "Множники Φ_d(x) повинні бути майже точними q-ми степенями, що неможливо при n ≥ 3", size=11, color="#a61e4d", anchor="middle"))

    render(os.path.join(IMG_DIR, 'fig-cyclotomic-decomposition.svg'), 800, 290, *frags, title="Розклад реп'юніта на кругові многочлени та примітивні прості дільники")

def draw_baker_bounds_map():
    frags = []

    # Title box
    frags.append(rect(200, 15, 400, 45, rx=6, fill="#f8f9fa", stroke="#343a40", sw=1.5))
    frags.append(text(400, 42, "Структура аналітичних та ефективних меж", size=14, bold=True, color="#212529", anchor="middle"))

    # Branch 1: Ljunggren exact result (q=2)
    frags.append(rect(30, 80, 230, 120, rx=6, fill="#e7f5ff", stroke="#1c7ed6", sw=1.5))
    frags.append(text(145, 105, "Результат Люнггрена (1943)", size=12, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(145, 128, "Випадок q = 2 (квадрати)", size=11, bold=True, color="#1c7ed6", anchor="middle"))
    frags.append(text(145, 150, "Повне розв'язання:", size=10, color="#495057", anchor="middle"))
    frags.append(text(145, 168, "лише (3, 5, 11) та (7, 4, 20)", size=10, bold=True, color="#1864ab", anchor="middle"))
    frags.append(text(145, 186, "інших точних квадратів немає", size=10, color="#495057", anchor="middle"))

    # Branch 2: Baker's logarithmic forms
    frags.append(rect(285, 80, 230, 120, rx=6, fill="#fff9db", stroke="#f59f00", sw=1.5))
    frags.append(text(400, 105, "Метод Бейкера (1966+)", size=12, bold=True, color="#e67700", anchor="middle"))
    frags.append(text(400, 128, "Лінійні форми логарифмів", size=11, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(400, 150, "Верхні межі: q < C₁(x), n < C₂", size=10, color="#495057", anchor="middle"))
    frags.append(text(400, 168, "Скінченність кількості", size=10, bold=True, color="#d9480f", anchor="middle"))
    frags.append(text(400, 186, "розв'язків для фіксованого x", size=10, color="#495057", anchor="middle"))

    # Branch 3: Modern Galois & Modular Methods
    frags.append(rect(540, 80, 230, 120, rx=6, fill="#ebfbee", stroke="#2b8a3e", sw=1.5))
    frags.append(text(655, 105, "Бюжо, Міньотт, Анро (2001+)", size=12, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(655, 128, "Модулярні методи та Галуа", size=11, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(655, 150, "Явні числові межі для q", size=10, color="#495057", anchor="middle"))
    frags.append(text(655, 168, "Доведення відсутності розв'язків", size=10, bold=True, color="#2b8a3e", anchor="middle"))
    frags.append(text(655, 186, "при x ≡ 1 (mod q) та n ≡ 1", size=10, color="#495057", anchor="middle"))

    # Bottom summary box
    frags.append(rect(120, 220, 560, 50, rx=6, fill="#f1f3f5", stroke="#adb5bd", sw=1.2))
    frags.append(text(400, 242, "Сучасний статус: гіпотеза доведена для багатьох класів (q=2, фіксовані x, n),", size=11, bold=True, color="#343a40", anchor="middle"))
    frags.append(text(400, 260, "але загальний випадок досі чекає повного аналітичного доведення", size=11, color="#495057", anchor="middle"))

    render(os.path.join(IMG_DIR, 'fig-baker-bounds-map.svg'), 800, 285, *frags, title="Карта аналітичних меж та результатів для рівняння Нагеля-Люнггрена")

if __name__ == '__main__':
    draw_solutions_overview()
    draw_cyclotomic_decomposition()
    draw_baker_bounds_map()
    print("Figures generated successfully.")
