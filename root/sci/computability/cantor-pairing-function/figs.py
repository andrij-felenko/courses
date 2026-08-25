# -*- coding: utf-8 -*-
"""Фігури для теми «Парна функція Кантора» (book/algorithms/complexity-computability/cantor-pairing-function)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE_F, BLUE_S = "#eaf0fd", "#2563eb"
PURPLE_F, PURPLE_S = "#f3e8ff", "#7e22ce"
TEAL_F, TEAL_S = "#e6fffa", "#0d9488"
AMBER_F, AMBER_S = "#fff6e5", "#d97706"
GREEN_F, GREEN_S = "#e9f7ef", "#16a34a"
RED_F, RED_S = "#fef2f2", "#dc2626"
GRAY_F, GRAY_S = "#f8fafc", "#64748b"

def fig_cantor_diagonal_grid():
    """fig1-cantor-diagonal-grid.svg: 2D-сітка з діагональним обходом Кантора."""
    W, H = 880, 500
    frags = []

    frags.append(rect(10, 10, 860, 480, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Діагональний обхід Кантора: бієкція ℕ₀ × ℕ₀ → ℕ₀", size=16, bold=True, color="#0f172a"))

    # Сітка координат
    ox, oy = 90, 410
    step = 70
    grid_n = 5

    # Осі
    frags.append(arrow(ox - 10, oy, ox + grid_n * step + 40, oy, color="#334155", sw=2))
    frags.append(arrow(ox, oy + 10, ox, oy - grid_n * step - 40, color="#334155", sw=2))
    frags.append(text(ox + grid_n * step + 45, oy + 20, "x", size=15, bold=True, color="#0f172a"))
    frags.append(text(ox - 20, oy - grid_n * step - 35, "y", size=15, bold=True, color="#0f172a"))

    # Сітка допоміжних ліній
    for i in range(grid_n + 1):
        # Позначки осі x
        frags.append(line(ox + i * step, oy - 4, ox + i * step, oy + 4, color="#64748b", sw=1.5))
        frags.append(text(ox + i * step, oy + 22, str(i), size=13, color="#334155", bold=True))
        # Позначки осі y
        frags.append(line(ox - 4, oy - i * step, ox + 4, oy - i * step, color="#64748b", sw=1.5))
        if i > 0:
            frags.append(text(ox - 22, oy - i * step + 4, str(i), size=13, color="#334155", bold=True))

    # Діагоналі w = x + y
    diag_colors = [BLUE_S, GREEN_S, AMBER_S, PURPLE_S, RED_S, "#0284c7"]
    diag_fills  = [BLUE_F, GREEN_F, AMBER_F, PURPLE_F, RED_F, "#e0f2fe"]

    # Значення функції π(x, y) = ((x+y)(x+y+1))/2 + y
    nodes = {}
    for w in range(grid_n + 1):
        for y in range(w + 1):
            x = w - y
            if x <= grid_n and y <= grid_n:
                val = (w * (w + 1)) // 2 + y
                nodes[(x, y)] = (val, w)

    # Малювання діагональних ліній обходу
    for w in range(grid_n + 1):
        col = diag_colors[w % len(diag_colors)]
        pts = [(ox + (w - y) * step, oy - y * step) for y in range(w + 1) if (w - y) <= grid_n and y <= grid_n]
        if len(pts) > 1:
            for k in range(len(pts) - 1):
                frags.append(line(pts[k][0], pts[k][1], pts[k+1][0], pts[k+1][1], color=col, sw=2.5, dash="4,3"))
                # стрілка напрямку
                mx = (pts[k][0] + pts[k+1][0]) / 2
                my = (pts[k][1] + pts[k+1][1]) / 2
                frags.append(circle(mx, my, 3, fill=col, stroke=col))

        # Перехідна стрілка від кінця діагоналі w до початку діагоналі w+1
        if w < grid_n:
            end_pt = (ox + 0 * step, oy - w * step)
            start_next = (ox + (w + 1) * step, oy - 0 * step)
            if w <= 3:
                # дуга-стрілка переходу
                frags.append(line(end_pt[0], end_pt[1], start_next[0], start_next[1], color="#94a3b8", sw=1.2, dash="2,2"))

    # Вузли
    for (x, y), (val, w) in nodes.items():
        cx = ox + x * step
        cy = oy - y * step
        col = diag_colors[w % len(diag_colors)]
        fill_col = diag_fills[w % len(diag_fills)]
        frags.append(circle(cx, cy, 17, fill=fill_col, stroke=col, sw=2))
        frags.append(text(cx, cy + 5, str(val), size=12, bold=True, color=col))

    # Права панель з формулами та поясненням
    px, py = 520, 60
    pw, ph = 330, 410
    frags.append(rect(px, py, pw, ph, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(px + pw/2, py + 26, "Алгебра діагонального обходу", size=14, bold=True, color="#0f172a"))

    f1, _, _ = textbox(px + pw/2, py + 75, "1. Номер діагоналі:  w = x + y\nВсі пари (x, y) на одній лінії мають сталу суму w", size=11, pad=8, fill="#ffffff", stroke=BLUE_S)
    frags.append(f1)

    f2, _, _ = textbox(px + pw/2, py + 155, "2. База діагоналі (трикутне число):\nT(w) = w·(w + 1) / 2\nКількість точок у попередніх w діагоналях", size=11, pad=8, fill="#ffffff", stroke=GREEN_S)
    frags.append(f2)

    f3, _, _ = textbox(px + pw/2, py + 245, "3. Зсув всередині діагоналі:  y\nРух від (w, 0) вгору-вліво до (0, w)\nπ(x, y) = T(x + y) + y", size=11, pad=8, fill="#ffffff", stroke=AMBER_S)
    frags.append(f3)

    f4, _, _ = textbox(px + pw/2, py + 345, "Повна формула Кантора:\nπ(x, y) = ((x + y)·(x + y + 1)) / 2 + y\nБієкція без пропусків і дублікатів", size=11, pad=8, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(f4)

    render(os.path.join(IMG, "fig1-cantor-diagonal-grid.svg"), W, H, *frags)

def fig_cantor_inversion_pipeline():
    """fig2-cantor-inversion-pipeline.svg: Алгоритмічний конвеєр декодування z -> (x, y)."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Конвеєр аналітичного декодування Кантора: z ↦ (x, y)", size=16, bold=True, color="#0f172a"))

    # Блоки конвеєра
    # 1. Вхід z
    b1, _, _ = textbox(110, 100, "Вхідний номер\nz ∈ ℕ₀", size=13, pad=10, fill=BLUE_F, stroke=BLUE_S, bold=True)
    frags.append(b1)

    frags.append(arrow(180, 100, 230, 100, color=BLUE_S, sw=2))

    # 2. Обчислення w (дискримінант)
    b2, _, _ = textbox(360, 100, "Крок 1: Знаходження діагоналі w\nw² + w - 2z ≤ 0\nw = ⌊ (√(8z + 1) - 1) / 2 ⌋", size=12, pad=10, fill=PURPLE_F, stroke=PURPLE_S)
    frags.append(b2)

    frags.append(arrow(490, 100, 540, 100, color=PURPLE_S, sw=2))

    # 3. Трикутна база t
    b3, _, _ = textbox(680, 100, "Крок 2: Трикутна база t\nt = w·(w + 1) / 2\nПочаток діагоналі w у просторі ℕ₀", size=12, pad=10, fill=TEAL_F, stroke=TEAL_S)
    frags.append(b3)

    # Стрілка вниз до кроку 3
    frags.append(arrow(680, 150, 680, 190, color="#475569", sw=2))

    # 4. Обчислення координат
    b4, _, _ = textbox(680, 250, "Крок 3: Виділення координат\ny = z - t  (зсув по вертикалі)\nx = w - y  (горизонтальна позиція)", size=12, pad=10, fill=AMBER_F, stroke=AMBER_S)
    frags.append(b4)

    frags.append(arrow(540, 250, 480, 250, color=AMBER_S, sw=2))

    # 5. Результат (x, y)
    b5, _, _ = textbox(340, 250, "Вихідна пара координат\n(x, y) = (w - y, z - t)", size=13, pad=10, fill=GREEN_F, stroke=GREEN_S, bold=True)
    frags.append(b5)

    # Числовий приклад у нижній панелі
    frags.append(rect(30, 310, 820, 85, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(440, 332, "Числовий приклад декодування: z = 13", size=13, bold=True, color="#0f172a"))
    ex_text = "1. 8z + 1 = 105 → √105 ≈ 10.246 → w = ⌊(10.246 - 1)/2⌋ = ⌊4.623⌋ = 4   |   2. t = 4·5/2 = 10   |   3. y = 13 - 10 = 3,  x = 4 - 3 = 1 → (1, 3)"
    frags.append(text(440, 362, ex_text, size=11, color="#1e293b", bold=True))

    render(os.path.join(IMG, "fig2-cantor-inversion-pipeline.svg"), W, H, *frags)

def fig_pairing_functions_comparison():
    """fig3-pairing-functions-comparison.svg: Порівняння структур спарювання (Cantor vs Szudzik vs Morton vs Godel)."""
    W, H = 880, 460
    frags = []

    frags.append(rect(10, 10, 860, 440, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Порівняльний аналіз архітектур парного кодування ℕ₀² ↔ ℕ₀", size=16, bold=True, color="#0f172a"))

    cards = [
        ("Спарювання Кантора (1877)", BLUE_F, BLUE_S, 30, 60, 395, 175,
         "Геометрія: трикутні діагоналі (x + y = const)\nФормула: π(x, y) = ((x+y)(x+y+1))/2 + y\nВластивість: компактна бієкція, плавне зростання\nЦіна: обчислення цілочисельного кореня isqrt"),

        ("Спарювання Шудзіка (Елегантне)", GREEN_F, GREEN_S, 455, 60, 395, 175,
         "Геометрія: вкладені квадрати (max(x, y) = const)\nФормула: x < y ? y² + x : x² + x + y\nВластивість: бієкція, відсутність ділення на 2\nПеревага: локальність у прямокутних областях"),

        ("Кодування Мортона (Z-крива)", PURPLE_F, PURPLE_S, 30, 255, 395, 175,
         "Геометрія: бітове чергування (Z-order curve)\nФормула: рознесення бітів x та y через маски\nВластивість: апаратна швидкість, квадродерева\nОбмеження: фіксована розрядність, нерівномірні стрибки"),

        ("Кодування Ґеделя (Степені простих)", AMBER_F, AMBER_S, 455, 255, 395, 175,
         "Геометрія: мультиплікативне просте розкладання\nФормула: g(x, y) = 2ˣ · 3ʸ\nВластивість: ін'єктивне, але не сюр'єктивне (дірки)\nНедолік: експоненційне зростання чисел, факторизація")
    ]

    for title, fill, stroke, cx, cy, cw, ch, desc in cards:
        frags.append(rect(cx, cy, cw, ch, fill=fill, stroke=stroke, sw=1.5, rx=8))
        frags.append(text(cx + cw/2, cy + 24, title, size=13, bold=True, color=stroke))
        lines = desc.split("\n")
        ly = cy + 52
        for ln in lines:
            frags.append(text(cx + 15, ly, ln, size=11, color="#1e293b", anchor="start"))
            ly += 26

    render(os.path.join(IMG, "fig3-pairing-functions-comparison.svg"), W, H, *frags)

def fig_computability_applications():
    """fig4-computability-applications.svg: Застосування спарювання в теорії обчислюваності."""
    W, H = 880, 420
    frags = []

    frags.append(rect(10, 10, 860, 400, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=10))
    frags.append(text(440, 34, "Функція спарювання як універсальний міст у теорії обчислюваності", size=16, bold=True, color="#0f172a"))

    apps = [
        ("1. Згортання кванторів", BLUE_F, BLUE_S, 30, 70, 260, 310,
         "Арифметична ієрархія\n\n∃x ∃y P(x, y) ≡ ∃z P(π₁(z), π₂(z))\n∀x ∀y P(x, y) ≡ ∀z P(π₁(z), π₂(z))\n\nДозволяє звести будь-який блок\nоднотипних кванторів до одного,\nфіксуючи рівні Σₙ та Πₙ."),

        ("2. Арифметизація машин", TEAL_F, TEAL_S, 310, 70, 260, 310,
         "Конфігурація Тюринга\n\nK = ⟨q, pos, tape⟩\nK = π(q, π(pos, tape))\n\nКодування багатовимірного\nстану пам'яті, стрічки та головки\nв єдиний натуральний індекс\nбез втрати інформації."),

        ("3. Нумерація Кліні", PURPLE_F, PURPLE_S, 590, 70, 260, 310,
         "Універсальні функції\n\nU(e, x) = Ψ(π(e, x))\n\nЗведення функцій k змінних\nдо одномісних: f(x₁, ..., xₖ) ↦ g(z).\nТеорема про нормальну форму\nта перелік обчислюваних програм.")
    ]

    for title, fill, stroke, cx, cy, cw, ch, desc in apps:
        frags.append(rect(cx, cy, cw, ch, fill=fill, stroke=stroke, sw=1.5, rx=8))
        frags.append(text(cx + cw/2, cy + 26, title, size=13, bold=True, color=stroke))
        lines = desc.split("\n")
        ly = cy + 60
        for ln in lines:
            if ln.startswith("∃") or ln.startswith("∀") or ln.startswith("K =") or ln.startswith("U("):
                frags.append(text(cx + cw/2, ly, ln, size=11, color=stroke, bold=True))
            elif ln.startswith("Арифметична") or ln.startswith("Конфігурація") or ln.startswith("Універсальні"):
                frags.append(text(cx + cw/2, ly, ln, size=12, color="#0f172a", bold=True))
            else:
                frags.append(text(cx + 15, ly, ln, size=11, color="#334155", anchor="start"))
            ly += 22

    render(os.path.join(IMG, "fig4-computability-applications.svg"), W, H, *frags)

if __name__ == "__main__":
    fig_cantor_diagonal_grid()
    fig_cantor_inversion_pipeline()
    fig_pairing_functions_comparison()
    fig_computability_applications()
    print("All figures generated successfully.")
