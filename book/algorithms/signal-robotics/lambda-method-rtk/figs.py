# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: Геометрія декореляції: перетворення Z та стиснення еліпса ────────
def fig_decorrelation():
    W, H = 760, 360
    frags = []

    # Ліва панель (x: 20..365, ширина 345)
    frags.append(rect(20, 45, 345, 295, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(192, 70, "Вихідний простір a (корельований)", size=13, bold=True, color=INK))

    # Оси координат a1, a2
    ax0, ay0 = 192, 185
    frags.append(line(45, ay0, 340, ay0, color="#b0b8c4", sw=1.2))
    frags.append(line(ax0, 280, ax0, 85, color="#b0b8c4", sw=1.2))
    frags.append(text(345, ay0 + 4, "a₁", size=12, color=MUTED, anchor="start"))
    frags.append(text(ax0, 80, "a₂", size=12, color=MUTED))

    # Ціла ґратка точок для лівої панелі
    step = 30
    for ix in range(-4, 5):
        for iy in range(-3, 4):
            gx, gy = ax0 + ix * step, ay0 - iy * step
            frags.append(circle(gx, gy, 2, fill="#8c9ba5", stroke="#8c9ba5", sw=0.5))

    # Похилий витягнутий еліпс під кутом ~42 градусів
    c_ax, c_ay = ax0 + 8, ay0 - 10
    import math
    pts_left = []
    theta_rad = math.radians(42)
    cos_t, sin_t = math.cos(theta_rad), math.sin(theta_rad)
    for deg in range(0, 361, 10):
        rad = math.radians(deg)
        ex = 90 * math.cos(rad)
        ey = 16 * math.sin(rad)
        rx = c_ax + ex * cos_t - ey * sin_t
        ry = c_ay - (ex * sin_t + ey * cos_t)
        pts_left.append((rx, ry))
    
    path_d = "M " + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts_left) + " Z"
    frags.append(f'<path d="{path_d}" fill="#fee2e2" fill-opacity="0.55" stroke="{POS}" stroke-width="2"/>')

    # Точка float оцінки a_hat
    frags.append(circle(c_ax, c_ay, 4.5, fill=POS, stroke=POS, sw=1.5))
    frags.append(text(c_ax + 8, c_ay + 14, "â (float)", size=11, bold=True, color=POS, anchor="start"))

    # Найближчий за Евклідом вузол ґратки (наївне округлення)
    naiv_x, naiv_y = ax0, ay0
    frags.append(circle(naiv_x, naiv_y, 4, fill=NEG, stroke=NEG, sw=1.5))
    frags.append(text(naiv_x - 6, naiv_y + 14, "[â] (хибний)", size=10, bold=True, color=NEG, anchor="end"))

    # Справжній оптимальний цілий вузол всередині еліпса вздовж головної осі
    true_x, true_y = ax0 + step * 2, ay0 - step * 2
    frags.append(circle(true_x, true_y, 5, fill=FIELD, stroke=FIELD, sw=1.8))
    frags.append(text(true_x + 8, true_y - 8, "ǎ (істинний fix)", size=10, bold=True, color=FIELD, anchor="start"))

    b_left = fitbox(35, 290, 315, 40, "Еліпс стиснутий у голку:\nнаївне округлення [â] дає похибку", size=11, pad=5, fill="#fff8e1", stroke=INK)
    frags.append(b_left)

    # Стрілка перетворення між панелями
    frags.append(arrow(368, 185, 392, 185, color=INK, sw=1.8))
    frags.append(text(380, 168, "z = Zᵀa", size=11, bold=True, color=INK))

    # Права панель (x: 395..740, ширина 345)
    frags.append(rect(395, 45, 345, 295, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=8))
    frags.append(text(567, 70, "Декорельований простір z", size=13, bold=True, color=INK))

    # Оси координат z1, z2
    zx0, zy0 = 567, 185
    frags.append(line(420, zy0, 715, zy0, color="#b0b8c4", sw=1.2))
    frags.append(line(zx0, 280, zx0, 85, color="#b0b8c4", sw=1.2))
    frags.append(text(720, zy0 + 4, "z₁", size=12, color=MUTED, anchor="start"))
    frags.append(text(zx0, 80, "z₂", size=12, color=MUTED))

    # Ціла ґратка для правої панелі
    for ix in range(-4, 5):
        for iy in range(-3, 4):
            gx, gy = zx0 + ix * step, zy0 - iy * step
            frags.append(circle(gx, gy, 2, fill="#8c9ba5", stroke="#8c9ba5", sw=0.5))

    # Майже круглий еліпс у просторі z
    c_zx, c_zy = zx0 + 6, zy0 - 8
    pts_right = []
    for deg in range(0, 361, 10):
        rad = math.radians(deg)
        rx = c_zx + 44 * math.cos(rad)
        ry = c_zy - 38 * math.sin(rad)
        pts_right.append((rx, ry))
    path_right = "M " + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts_right) + " Z"
    frags.append(f'<path d="{path_right}" fill="#dcfce7" fill-opacity="0.55" stroke="{FIELD}" stroke-width="2"/>')

    # Точка float z_hat
    frags.append(circle(c_zx, c_zy, 4.5, fill=POS, stroke=POS, sw=1.5))
    frags.append(text(c_zx + 8, c_zy + 14, "ẑ (float)", size=11, bold=True, color=POS, anchor="start"))

    # Найближчий вузол у просторі z — це і є правильний вузол!
    opt_zx, opt_zy = zx0, zy0
    frags.append(circle(opt_zx, opt_zy, 5, fill=FIELD, stroke=FIELD, sw=1.8))
    frags.append(text(opt_zx - 8, opt_zy - 8, "ž (найближчий)", size=10, bold=True, color=FIELD, anchor="end"))

    b_right = fitbox(410, 290, 315, 40, "Еліпс майже круглий:\nнайближчий вузол ž є оптимальним", size=11, pad=5, color=FIELD, fill="#eafaf1", stroke=FIELD)
    frags.append(b_right)

    render(os.path.join(OUT, 'decorrelation-geometry.svg'), W, H,
           *frags,
           title="Геометрія LAMBDA: унімодулярна декореляція вирівнює еліпс пошуку")


# ── Фігура 2: Конвеєр обчислень LAMBDA в RTK-рушії ────────────────────────────
def fig_pipeline():
    W, H = 760, 370
    frags = []

    # 4 етапи горизонтального конвеєра
    b1 = fitbox(20, 60, 160, 110,
                "1. Плаваючий розв'язок\nâ (дійсний вектор)\nQ_â (коваріація)\nз EKF або МНК",
                size=12, pad=6, fill="#f4f6f8", stroke=INK)
    frags.append(b1)

    frags.append(arrow(180, 115, 210, 115, color=INK, sw=2))

    b2 = fitbox(210, 60, 170, 110,
                "2. Z-перетворення\nQ_â = L·D·Lᵀ\nГауссові зсуви + swap\nматриця Z (det = ±1)",
                size=12, pad=6, fill="#eff6ff", stroke=NEG)
    frags.append(b2)

    frags.append(arrow(380, 115, 410, 115, color=INK, sw=2))

    b3 = fitbox(410, 60, 165, 110,
                "3. Дерево пошуку\nẑ = Zᵀâ, Q_ẑ = ZᵀQ_âZ\nПошук у гіперсфері\nКандидати ž₁ та ž₂",
                size=12, pad=6, fill="#fef3c7", stroke="#d97706")
    frags.append(b3)

    frags.append(arrow(575, 115, 605, 115, color=INK, sw=2))

    b4 = fitbox(605, 60, 135, 110,
                "4. Відновлення\nǎ₁ = Z⁻ᵀ ž₁\nǎ₂ = Z⁻ᵀ ž₂\n(цілі вектори)",
                size=12, pad=6, fill="#eafaf1", stroke=FIELD)
    frags.append(b4)

    # Стрілка вниз від блоку 4 до Ратіо-тесту
    frags.append(arrow(672, 170, 672, 210, color=INK, sw=2))

    # Блок Ратіо-тесту
    b_val = fitbox(540, 210, 200, 75,
                   "Валідація: Ratio-Test\nR = F(ǎ₂) / F(ǎ₁) ≥ μ\n(зазвичай μ = 2.0...3.0)",
                   size=12, pad=6, fill="#fdf2f8", stroke="#db2777", bold=True)
    frags.append(b_val)

    # Розгалуження після Ratio: Fix або Float
    frags.append(arrow(540, 247, 430, 247, color=FIELD, sw=2))
    b_fix = fitbox(250, 225, 180, 45,
                   "Успіх (R ≥ μ) → RTK FIXED\nКоординати з точністю 1-2 см",
                   size=11, pad=5, fill="#dcfce7", stroke=FIELD, bold=True, color=FIELD)
    frags.append(b_fix)

    frags.append(arrow(640, 285, 640, 315, color=POS, sw=1.8))
    b_flt = fitbox(540, 315, 200, 40,
                   "Невдача (R < μ) → Тримати FLOAT\nОчікування нових вимірів",
                   size=11, pad=5, fill="#fee2e2", stroke=POS, color=POS)
    frags.append(b_flt)

    # Зв'язок оновлення baseline координат
    frags.append(line(250, 247, 100, 247, color=FIELD, sw=1.5, dash="3,3"))
    frags.append(arrow(100, 247, 100, 170, color=FIELD, sw=1.5))
    frags.append(text(175, 235, "b̌ = b̂ − Q_bâ Q_â⁻¹(â − ǎ)", size=11, color=FIELD))

    render(os.path.join(OUT, 'lambda-pipeline.svg'), W, H,
           *frags,
           title="Повний конвеєр алгоритму LAMBDA у структурі RTK-приймача")


# ── Фігура 3: Деревоподібний пошук у декорельованому просторі ──────────────────
def fig_search_tree():
    W, H = 760, 350
    frags = []

    root_x, root_y = 380, 50
    frags.append(circle(root_x, root_y, 6, fill=INK, stroke=INK))
    frags.append(text(root_x, root_y - 12, "Початок пошуку (χ² = радіус еліпсоїда)", size=12, bold=True))

    # Рівень n: 3 гілки
    n_nodes = [220, 380, 540]
    for x in n_nodes:
        frags.append(line(root_x, root_y, x, 100, color=LINE, sw=1.5))
        frags.append(circle(x, 100, 5, fill=NEG, stroke=NEG))

    frags.append(text(n_nodes[0], 90, "zₙ = k − 1", size=10, color=NEG))
    frags.append(text(n_nodes[1], 90, "zₙ = k", size=10, bold=True, color=NEG))
    frags.append(text(n_nodes[2], 90, "zₙ = k + 1", size=10, color=NEG))

    # Рівень n-1: розгалуження від центрального вузла
    mid_n = n_nodes[1]
    nm1_nodes = [310, 380, 450]
    for x in nm1_nodes:
        frags.append(line(mid_n, 100, x, 180, color=LINE, sw=1.5))
        frags.append(circle(x, 180, 4.5, fill="#d97706", stroke="#d97706"))

    frags.append(text(nm1_nodes[0], 170, "відсікання (>χ²)", size=9, color=POS))
    frags.append(cross(nm1_nodes[0], 180, 6))

    frags.append(text(nm1_nodes[1], 170, "z_{n-1} допустиме", size=10, color="#d97706"))
    frags.append(text(nm1_nodes[2], 170, "z_{n-1} допустиме", size=10, color="#d97706"))

    # Обрізка лівої гілки з рівня n
    frags.append(line(n_nodes[0], 100, 220, 150, color=MUTED, sw=1.2, dash="2,3"))
    frags.append(cross(220, 150, 6))
    frags.append(text(220, 165, "часткова сума > χ²", size=9, color=POS))

    # Рівень 1 (листки)
    frags.append(line(nm1_nodes[1], 180, 350, 260, color=FIELD, sw=2))
    frags.append(circle(350, 260, 6, fill=FIELD, stroke=FIELD))
    frags.append(text(350, 280, "ž₁ (найкращий розв'язок F₁)", size=11, bold=True, color=FIELD))

    frags.append(line(nm1_nodes[2], 180, 450, 260, color="#2563eb", sw=1.5))
    frags.append(circle(450, 260, 5, fill="#2563eb", stroke="#2563eb"))
    frags.append(text(450, 280, "ž₂ (другий кандидат F₂)", size=11, color="#2563eb"))

    # Пояснення праворуч
    b_desc = fitbox(550, 130, 195, 140,
                    "Динамічне звуження χ²:\nЩойно знайдено повний\nлисток ž, радіус χ²\nзменшується до його\nвідстані F(ž). Це миттєво\nвідсікає всі гірші гілки.",
                    size=11, pad=6, fill="#fff8e1", stroke="#d97706")
    frags.append(b_desc)

    # Підпис знизу
    b_bot = fitbox(180, 305, 400, 35,
                   "Пошук у глибину (depth-first search) з умовними межами",
                   size=12, pad=6, fill="#f4f6f8", stroke=INK, bold=True)
    frags.append(b_bot)

    render(os.path.join(OUT, 'search-tree.svg'), W, H,
           *frags,
           title="Пошук у глибину впорядкованого дерева цілочислових кандидатів")


def cross(cx, cy, r=6):
    return (line(cx - r, cy - r, cx + r, cy + r, color=POS, sw=2) +
            line(cx - r, cy + r, cx + r, cy - r, color=POS, sw=2))


if __name__ == "__main__":
    fig_decorrelation()
    fig_pipeline()
    fig_search_tree()
    print("Фігури успішно згенеровано.")
