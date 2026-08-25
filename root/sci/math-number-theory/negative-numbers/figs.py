# -*- coding: utf-8 -*-
"""Фігури до статті «Від'ємні числа»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_number_line_direction():
    """Фігура 1: Числова вісь із орієнтацією та додаванням векторів."""
    W, H = 900, 260
    frags = []

    # Заголовок
    frags.append(text(W / 2, 30, "Числова вісь як орієнтований простір: векторний зсув 3 + (-5) = -2", size=16, bold=True))

    # Головна числова вісь
    y_axis = 160
    x_min, x_max = 80, 820
    frags.append(line(x_min, y_axis, x_max, y_axis, color="#2c3e50", sw=2))
    # Стрілка на правому кінці
    frags.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="#2c3e50"/>' %
                 (x_max, y_axis - 5, x_max + 12, y_axis, x_max, y_axis + 5))

    # Поділки на осі (від -4 до +4)
    ticks = [
        (-4, 130, "-4"),
        (-3, 210, "-3"),
        (-2, 290, "-2"),
        (-1, 370, "-1"),
        (0,  450, "0"),
        (1,  530, "+1"),
        (2,  610, "+2"),
        (3,  690, "+3"),
        (4,  770, "+4"),
    ]

    for val, x, label in ticks:
        is_zero = (val == 0)
        t_h = 14 if is_zero else 8
        sw_t = 2.5 if is_zero else 1.5
        col = "#d9534f" if val < 0 else ("#27ae60" if val > 0 else "#2c3e50")

        frags.append(line(x, y_axis - t_h, x, y_axis + t_h, color=col if not is_zero else "#2c3e50", sw=sw_t))
        frags.append(text(x, y_axis + 28, label, size=14, bold=is_zero, color=col if not is_zero else "#2c3e50"))

    # Вектор +3 від 0 до 3
    frags.append('<path d="M 450 145 Q 570 95 685 142" stroke="#27ae60" fill="none" stroke-width="2.2" stroke-dasharray="4 2"/>')
    frags.append('<polygon points="685,142 690,148 678,148" fill="#27ae60"/>')
    frags.append(text(570, 105, "зсув +3 (праворуч)", size=13, color="#27ae60", bold=True))

    # Вектор -5 від 3 до -2
    frags.append('<path d="M 690 145 Q 490 55 295 142" stroke="#d9534f" fill="none" stroke-width="2.5"/>')
    frags.append('<polygon points="295,142 302,148 302,138" fill="#d9534f"/>')
    frags.append(text(490, 75, "зсув -5 (ліворуч)", size=13, color="#d9534f", bold=True))

    # Підпис під кінцевою точкою
    frags.append(rect(240, 210, 100, 32, fill="#fdf2f2", stroke="#d9534f", rx=4, sw=1.5))
    frags.append(text(290, 231, "Результат: -2", size=13, bold=True, color="#d9534f"))

    render(os.path.join(OUT, "number-line-direction.svg"), W, H, *frags)


def fig_grothendieck_pairs():
    """Фігура 2: Класи еквівалентності пар (a,b) у конструкції Гротендіка."""
    W, H = 850, 440
    frags = []

    frags.append(text(W / 2, 28, "Побудова цілих чисел Z як класів еквівалентності пар (a, b) ∈ N₀ × N₀", size=15, bold=True))

    ox, oy = 120, 360
    step = 70

    frags.append(line(ox - 20, oy, ox + 4 * step + 40, oy, color="#7f8c8d", sw=2))
    frags.append(text(ox + 4 * step + 55, oy + 5, "a (додатний компонент)", size=13, color="#2c3e50", anchor="start"))

    frags.append(line(ox, oy + 20, ox, oy - 4 * step - 30, color="#7f8c8d", sw=2))
    frags.append(text(ox, oy - 4 * step - 42, "b (від'ємний компонент)", size=13, color="#2c3e50", anchor="middle"))

    classes = [
        (2, "#27ae60", "Клас [(2,0)] = +2"),
        (0, "#2c3e50", "Клас [(0,0)] = 0"),
        (-2, "#d9534f", "Клас [(0,2)] = -2"),
    ]

    for diff, col, name in classes:
        pts = []
        for a in range(5):
            b = a - diff
            if 0 <= b <= 4:
                pts.append((ox + a * step, oy - b * step))
        if len(pts) >= 2:
            x1, y1 = pts[0]
            x2, y2 = pts[-1]
            dx = (x2 - x1) / (len(pts) - 1)
            dy = (y2 - y1) / (len(pts) - 1)
            lx1, ly1 = x1 - 0.4 * dx, y1 - 0.4 * dy
            lx2, ly2 = x2 + 0.4 * dx, y2 + 0.4 * dy
            frags.append(line(lx1, ly1, lx2, ly2, color=col, sw=2, dash="5 3"))
            frags.append(text(lx2 + 15, ly2 + 4, name, size=12, color=col, bold=True, anchor="start"))

    for a in range(5):
        for b in range(5):
            px = ox + a * step
            py = oy - b * step
            diff = a - b
            col = "#27ae60" if diff > 0 else ("#d9534f" if diff < 0 else "#2c3e50")

            frags.append(circle(px, py, 6, fill=col, stroke="#ffffff", sw=1.5))
            frags.append(text(px + 12, py - 8, f"({a},{b})", size=11, color="#555555", anchor="start"))

    bx, by = 540, 240
    frags.append(rect(bx, by, 280, 140, fill="#f8f9fa", stroke="#bdc3c7", rx=6, sw=1.5))
    frags.append(text(bx + 140, by + 24, "Умова еквівалентності:", size=13, bold=True, color="#2c3e50"))
    frags.append(text(bx + 140, by + 52, "(a, b) ~ (c, d) ⇔ a + d = b + c", size=13, color="#2c3e50"))
    frags.append(text(bx + 140, by + 80, "Пара (a, b) уособлює різницю a - b.", size=12, color="#7f8c8d"))
    frags.append(text(bx + 140, by + 105, "Пари на одній паралелі", size=12, color="#7f8c8d"))
    frags.append(text(bx + 140, by + 124, "позначають одне й те саме ціле число.", size=12, color="#7f8c8d"))

    render(os.path.join(OUT, "grothendieck-pairs.svg"), W, H, *frags)


def fig_multiplication_signs():
    """Фігура 3: Симетрія квадрантів та множення знаків."""
    W, H = 850, 420
    frags = []

    frags.append(text(W / 2, 28, "Геометрична інтуїція правила знаків: множення на мінус як поворот на 180°", size=15, bold=True))

    cx, cy = 425, 230
    qw, qh = 360, 160

    quads = [
        (cx + 10, cy - qh - 10, "#eef8f1", "#27ae60", "(+a) · (+b) = +(a · b)", "Перший квадрант: збереження напрямку", "Прямий масштаб без зміни орієнтації"),
        (cx - qw - 10, cy - qh - 10, "#fdf2f2", "#d9534f", "(-a) · (+b) = -(a · b)", "Другий квадрант: один поворот", "Один від'ємний множник повертає вектор на 180°"),
        (cx - qw - 10, cy + 10, "#eef8f1", "#27ae60", "(-a) · (-b) = +(a · b)", "Третій квадрант: подвійний поворот", "180° + 180° = 360° (відновлення початкового знаку!)"),
        (cx + 10, cy + 10, "#fdf2f2", "#d9534f", "(+a) · (-b) = -(a · b)", "Четвертий квадрант: один поворот", "Один від'ємний множник міняє орієнтацію на протилежну"),
    ]

    for qx, qy, bg, border, formula, title, desc in quads:
        frags.append(rect(qx, qy, qw, qh, fill=bg, stroke=border, rx=6, sw=1.8))
        frags.append(text(qx + qw / 2, qy + 30, formula, size=16, bold=True, color=border))
        frags.append(text(qx + qw / 2, qy + 65, title, size=13, bold=True, color="#2c3e50"))
        frags.append(text(qx + qw / 2, qy + 105, desc, size=12, color="#555555"))

    frags.append(line(cx - qw - 20, cy, cx + qw + 20, cy, color="#bdc3c7", sw=1.5, dash="4 4"))
    frags.append(line(cx, cy - qh - 20, cx, cy + qh + 20, color="#bdc3c7", sw=1.5, dash="4 4"))

    render(os.path.join(OUT, "multiplication-signs-symmetry.svg"), W, H, *frags)


def fig_division_remainder():
    """Фігура 4: Порівняння евклідового ділення та truncation division."""
    W, H = 900, 320
    frags = []

    frags.append(text(W / 2, 28, "Порівняння ділення з остачею для -13 ÷ 5: Евклідове (math) vs Усічене (C/C++)", size=15, bold=True))

    y1 = 120
    frags.append(rect(40, 60, 820, 110, fill="#f8f9fa", stroke="#27ae60", rx=6, sw=1.5))
    frags.append(text(60, 85, "1. Евклідове ділення (Математичний стандарт: остача 0 ≤ r < 5):", size=14, bold=True, color="#27ae60", anchor="start"))
    frags.append(text(60, 115, "Рівність: -13 = (-3) · 5 + 2   ⇒   частка q = -3, остача r = +2", size=14, color="#2c3e50", anchor="start"))

    frags.append(line(450, y1 + 25, 830, y1 + 25, color="#7f8c8d", sw=1.5))
    frags.append(circle(500, y1 + 25, 5, fill="#27ae60"))
    frags.append(text(500, y1 + 42, "-15 = (-3)·5", size=11, color="#27ae60"))

    frags.append(circle(700, y1 + 25, 5, fill="#2c3e50"))
    frags.append(text(700, y1 + 42, "-10 = (-2)·5", size=11, color="#2c3e50"))

    frags.append(circle(580, y1 + 25, 6, fill="#d9534f"))
    frags.append(text(580, y1 + 42, "-13", size=12, bold=True, color="#d9534f"))

    frags.append('<path d="M 500 115 Q 540 100 575 120" stroke="#27ae60" fill="none" stroke-width="2"/>')
    frags.append(text(540, 102, "остача r = +2", size=11, color="#27ae60", bold=True))

    y2 = 250
    frags.append(rect(40, 190, 820, 110, fill="#fdf2f2", stroke="#d9534f", rx=6, sw=1.5))
    frags.append(text(60, 215, "2. Усічене ділення (Truncation division у C/C++/Java: остача бере знак діленого):", size=14, bold=True, color="#d9534f", anchor="start"))
    frags.append(text(60, 245, "Рівність: -13 = (-2) · 5 + (-3)   ⇒   частка q = -2, остача r = -3", size=14, color="#2c3e50", anchor="start"))

    frags.append(line(450, y2 + 25, 830, y2 + 25, color="#7f8c8d", sw=1.5))
    frags.append(circle(700, y2 + 25, 5, fill="#2c3e50"))
    frags.append(text(700, y2 + 42, "-10 = (-2)·5", size=11, color="#2c3e50"))

    frags.append(circle(580, y2 + 25, 6, fill="#d9534f"))
    frags.append(text(580, y2 + 42, "-13", size=12, bold=True, color="#d9534f"))

    frags.append('<path d="M 700 245 Q 640 230 585 250" stroke="#d9534f" fill="none" stroke-width="2"/>')
    frags.append(text(640, 232, "остача r = -3", size=11, color="#d9534f", bold=True))

    render(os.path.join(OUT, "division-remainder-comparison.svg"), W, H, *frags)


if __name__ == '__main__':
    fig_number_line_direction()
    fig_grothendieck_pairs()
    fig_multiplication_signs()
    fig_division_remainder()
    print("Всі фігури згенеровано успішно.")
