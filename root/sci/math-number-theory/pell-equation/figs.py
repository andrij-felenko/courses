import sys
import os
import math

# Add scripts directory to path (4 levels up from book/math/number-theory/pell-equation)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')))
try:
    from svgkit import render, rect, line, text, mtext, circle, textbox, fitbox, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
except ImportError:
    print("WARNING: svgkit not found.")
    sys.exit(1)

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')


def draw_hyperbola_discrete():
    """Малює гіперболу x² - 2y² = 1 та дискретні цілочисельні розв'язки на решітці."""
    width, height = 700, 450
    frags = []

    # Заливка фону
    frags.append(rect(0, 0, width, height, fill=BG))

    # Заголовок
    frags.append(text(width / 2, 22, "Дискретні розв'язки x² - 2y² = 1 на гіперболі", size=15, bold=True, color=INK))

    # Координатна сітка
    ox, oy = 70, 360
    scale_x, scale_y = 26, 24

    # Сітка та осі
    for x_val in range(0, 21):
        px = ox + x_val * scale_x
        frags.append(line(px, 50, px, oy + 15, color="#eaeaea", sw=1.0))
        if x_val % 2 == 0:
            frags.append(text(px, oy + 18, str(x_val), size=10, color=MUTED))

    for y_val in range(0, 13):
        py = oy - y_val * scale_y
        frags.append(line(ox - 10, py, ox + 580, py, color="#eaeaea", sw=1.0))
        if y_val % 2 == 0:
            frags.append(text(ox - 18, py + 4, str(y_val), size=10, color=MUTED, anchor="end"))

    # Осі X та Y
    frags.append(line(ox, oy, ox + 590, oy, color=LINE, sw=1.5))
    frags.append(line(ox, oy, ox, 45, color=LINE, sw=1.5))
    frags.append(text(ox + 600, oy + 12, "x", size=12, bold=True, color=INK))
    frags.append(text(ox - 15, 42, "y", size=12, bold=True, color=INK))

    # Асимптота y = x / √2 ≈ 0.7071 x
    asymptote_x = 20
    asymptote_y = asymptote_x / 1.41421356
    frags.append(line(ox, oy, ox + asymptote_x * scale_x, oy - asymptote_y * scale_y, color=MUTED, sw=1.2, dash="4,4"))
    frags.append(text(ox + 460, oy - 270, "Асимптота y = x / √2", size=11, italic=True, color=MUTED, anchor="start"))

    # Точки гіперболи x = √(1 + 2y²)
    hyp_points = []
    for step in range(0, 241):
        y_val = step * 0.05
        x_val = math.sqrt(1.0 + 2.0 * y_val * y_val)
        px = ox + x_val * scale_x
        py = oy - y_val * scale_y
        if px <= ox + 580 and py >= 45:
            hyp_points.append((px, py))

    for i in range(len(hyp_points) - 1):
        x1, y1 = hyp_points[i]
        x2, y2 = hyp_points[i + 1]
        frags.append(line(x1, y1, x2, y2, color=NEG, sw=2.5))

    # Цілочисельні розв'язки (1,0), (3,2), (17,12)
    solutions = [(1, 0), (3, 2), (17, 12)]

    for x_sol, y_sol in solutions:
        px = ox + x_sol * scale_x
        py = oy - y_sol * scale_y
        if px <= ox + 580 and py >= 45:
            frags.append(circle(px, py, 6, fill=POS, stroke="#ffffff", sw=1.5))
            # Пунктири до осей
            frags.append(line(px, py, px, oy, color=POS, sw=1.0, dash="2,2"))
            frags.append(line(px, py, ox, py, color=POS, sw=1.0, dash="2,2"))

    # Підписи розв'язків у textbox
    frags.append(textbox(ox + 1 * scale_x + 65, oy + 32, "x₀ = 1, y₀ = 0", size=11, color=POS, bold=True, fill=FILL, stroke=POS)[0])
    frags.append(textbox(ox + 3 * scale_x + 75, oy - 2 * scale_y - 35, "x₁ = 3, y₁ = 2", size=11, color=POS, bold=True, fill=FILL, stroke=POS)[0])
    frags.append(textbox(ox + 17 * scale_x - 90, oy - 12 * scale_y + 45, "x₂ = 17, y₂ = 12", size=11, color=POS, bold=True, fill=FILL, stroke=POS)[0])

    # Пояснювальна блок-картка
    frags.append(rect(140, 80, 240, 75, fill="#f8fafc", stroke=LINE, rx=6))
    frags.append(text(260, 100, "Властивість розв'язків", size=12, bold=True, color=INK))
    frags.append(mtext(260, 120, ["Усі розв'язки лежать на гіперболі", "й експоненціально віддаляються"], size=10, color=MUTED))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'pell-hyperbola.svg'), width, height, *frags, title="Гіпербола та цілочисельні розв'язки")


def draw_continued_fractions():
    """Малює збіжність підхідних дробів pₙ/qₙ до √3."""
    width, height = 720, 360
    frags = []

    frags.append(rect(0, 0, width, height, fill=BG))
    frags.append(text(width / 2, 24, "Збіжність підхідних дробів pₙ/qₙ до √3 ≈ 1.73205...", size=15, bold=True, color=INK))

    # Вісь значений
    y_axis = 160
    ox = 70
    length = 580
    frags.append(line(ox, y_axis, ox + length, y_axis, color=LINE, sw=2.0))

    # Справжнє значення √3
    val_sqrt3 = 1.7320508
    min_v, max_v = 0.8, 2.2
    def to_x(val):
        return ox + (val - min_v) / (max_v - min_v) * length

    x_sqrt3 = to_x(val_sqrt3)
    frags.append(line(x_sqrt3, 55, x_sqrt3, 270, color=POS, sw=2.0, dash="5,5"))
    frags.append(textbox(x_sqrt3 + 55, y_axis - 10, "√3 ≈ 1.73205", size=11, color=POS, bold=True, fill="#fef2f2", stroke=POS)[0])

    # 4 підхідні дроби з чітким рознесенням
    convergents = [
        (0, 1, 1, 1.0, "p₀/q₀ = 1/1 = 1.0", 85),
        (1, 2, 1, 2.0, "p₁/q₁ = 2/1 = 2.0", 85),
        (2, 5, 3, 5/3, "p₂/q₂ = 5/3 ≈ 1.667", 90),
        (4, 19, 11, 19/11, "p₄/q₄ = 19/11 ≈ 1.727", 235)
    ]

    for n, p, q, val, label, cy in convergents:
        cx = to_x(val)
        is_pell = (p*p - 3*q*q == 1)

        node_color = FIELD if is_pell else NEG
        frags.append(circle(cx, y_axis, 5, fill=node_color, stroke="#ffffff", sw=1.5))
        frags.append(line(cx, y_axis, cx, cy, color=node_color, sw=1.2))

        lbl_y = cy - 12 if cy < y_axis else cy + 12
        bg_fill = "#f0fdf4" if is_pell else FILL
        brd_color = FIELD if is_pell else node_color
        frags.append(textbox(cx, lbl_y, label, size=11, color=node_color, bold=is_pell, fill=bg_fill, stroke=brd_color)[0])

    # Легенда знизу
    frags.append(rect(80, 295, 560, 42, fill="#f8fafc", stroke="#e2e8f0", rx=4))
    frags.append(text(200, 321, "● Парні n: pₙ/qₙ < √3", size=11, color=NEG))
    frags.append(text(380, 321, "● Непарні n: pₙ/qₙ > √3", size=11, color=NEG))
    frags.append(text(550, 321, "★ Розв'язок x² - 3y² = 1", size=11, color=FIELD, bold=True))

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'continued-fractions-convergents.svg'), width, height, *frags, title="Підхідні дроби та збіжність")


def draw_chakravala_cycle():
    """Малює циклічний процес методу Чукравала (Brahmagupta-Bhaskara)."""
    width, height = 700, 320
    frags = []

    frags.append(rect(0, 0, width, height, fill=BG))
    frags.append(text(width / 2, 24, "Цикл методу Чукравала (Brahmagupta-Bhaskara)", size=15, bold=True, color=INK))

    # Схема з 4 блоків у циклі
    boxes = [
        (60, 80, 160, 90, "Початкова трійка", ["a² - d·b² = k", "Старт з (a₀, b₀, k₀)"], "#eff6ff", NEG),
        (255, 80, 170, 90, "Мінімізація m", ["|m² - d| → min", "при (a + b·m) ≡ 0 (mod k)"], "#fefce8", "#d97706"),
        (460, 80, 180, 90, "Нова трійка", ["a' = (a·m + d·b)/|k|", "b' = (a + b·m)/|k|", "k' = (m² - d)/k"], "#f0fdf4", FIELD),
        (255, 220, 170, 70, "Перевірка k' = 1", ["k' = 1 ⇒ СТОП (розв'язок)", "k' ≠ 1 ⇒ k := k', повтор"], "#fef2f2", POS)
    ]

    for bx, by, bw, bh, title_txt, lines_txt, bg_c, border_c in boxes:
        frags.append(rect(bx, by, bw, bh, fill=bg_c, stroke=border_c, rx=6, sw=1.5))
        frags.append(text(bx + bw / 2, by + 20, title_txt, size=12, bold=True, color=INK))
        frags.append(mtext(bx + bw / 2, by + 40, lines_txt, size=10, color=INK))

    # Стрілки переходу
    # 1 -> 2
    frags.append(line(220, 125, 255, 125, color=LINE, sw=1.5))
    frags.append(text(238, 115, "→", size=14, bold=True, color=LINE))

    # 2 -> 3
    frags.append(line(425, 125, 460, 125, color=LINE, sw=1.5))
    frags.append(text(443, 115, "→", size=14, bold=True, color=LINE))

    # 3 -> 4
    frags.append(line(550, 170, 550, 255, color=LINE, sw=1.5))
    frags.append(line(550, 255, 425, 255, color=LINE, sw=1.5))
    frags.append(text(438, 250, "←", size=14, bold=True, color=LINE))

    # 4 -> 2 (Цикл назад якщо k' != 1)
    frags.append(textbox(340, 195, "k' ≠ 1 (ітерація)", size=10, color=POS, bold=True, fill="#ffffff", stroke=POS)[0])

    os.makedirs(IMG_DIR, exist_ok=True)
    render(os.path.join(IMG_DIR, 'chakravala-cycle.svg'), width, height, *frags, title="Цикл Чукравала")


if __name__ == '__main__':
    draw_hyperbola_discrete()
    draw_continued_fractions()
    draw_chakravala_cycle()
