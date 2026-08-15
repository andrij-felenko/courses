# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def path_elem(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    stroke_dash = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{stroke_dash}/>'


def fig_cycle_grid():
    """
    cycle-grid.svg: Схема кільця остач за модулем 4
    Показує 6 станів (пар сусідніх остач) і замкнений цикл повернення до (0, 1).
    """
    W, H = 880, 400
    p = []

    p.append(text(W / 2, 45, "Остачі чисел Фібоначчі за модулем 4: кільце з 6 станів", size=16, bold=True))

    # 6 станів циклу mod 4: (0,1) -> (1,1) -> (1,2) -> (2,3) -> (3,1) -> (1,0)
    states = [
        (0, "(0, 1)", "n=0, 6, 12…", True),
        (1, "(1, 1)", "n=1, 7…", False),
        (2, "(1, 2)", "n=2, 8…", False),
        (3, "(2, 3)", "n=3, 9…", False),
        (4, "(3, 1)", "n=4, 10…", False),
        (5, "(1, 0)", "n=5, 11…", False),
    ]

    cx, cy, rx, ry = W / 2, 220, 280, 110
    import math

    nodes_coords = []
    for i, pair_str, sub_str, is_start in states:
        angle = math.pi / 2 - i * (2 * math.pi / 6)
        x = cx + rx * math.cos(angle)
        y = cy - ry * math.sin(angle)
        nodes_coords.append((x, y, pair_str, sub_str, is_start))

    # Стрілки між сусідніми вузлами
    for i in range(6):
        x1, y1, _, _, _ = nodes_coords[i]
        x2, y2, _, _, _ = nodes_coords[(i + 1) % 6]
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        ux, uy = dx / dist, dy / dist
        sx, sy = x1 + ux * 45, y1 + uy * 45
        ex, ey = x2 - ux * 45, y2 - uy * 45
        p.append(arrow(sx, sy, ex, ey, color=FIELD if i == 5 else LINE, sw=2.0 if i == 5 else 1.5))

    # Малювання самих вузлів
    for x, y, pair_str, sub_str, is_start in nodes_coords:
        bw, bh = 88, 54
        fill_col = "#eafaf0" if is_start else "#fbfbfc"
        stroke_col = FIELD if is_start else LINE
        p.append(rect(x - bw / 2, y - bh / 2, bw, bh, fill=fill_col, stroke=stroke_col, sw=2.0 if is_start else 1.2, rx=8))
        p.append(text(x, y - 4, pair_str, size=15, bold=True, color=FIELD if is_start else INK))
        p.append(text(x, y + 15, sub_str, size=11, color=MUTED))

    # Пояснювальний бокс знизу
    b, _, _ = textbox(W / 2, 365, "Період Пізано π(4) = 6  —  після 6 кроків пара (0, 1) відновлюється повністю",
                      size=13.5, pad=10, fill="#fbfbfc", bold=True)
    p.append(b)

    render(os.path.join(OUT, "cycle-grid.svg"), W, H, *p, title="Кільце остач за модулем 4")


def fig_prime_split():
    """
    prime-split.svg: Класифікація простих чисел за квадратичним лишком 5 mod p
    Показує розгалуження для p mod 5 і відповідні межі періоду Пізано π(p).
    """
    W, H = 940, 420
    p = []

    p.append(text(W / 2, 42, "Структура періоду Пізано π(p) залежно від квадратичного лишку (5 / p)", size=16, bold=True))

    # Корінь: Просте число p
    p.append(rect(W / 2 - 110, 75, 220, 48, fill="#fbfbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(W / 2, 104, "Просте число p", size=15, bold=True))

    x1, x2, x3 = 180, 500, 800
    y_branch = 180
    y_box = 240

    # Лінії розгалуження
    p.append(arrow(W / 2 - 50, 123, x1, y_branch - 15, color=LINE, sw=1.4))
    p.append(arrow(W / 2, 123, x2, y_branch - 15, color=LINE, sw=1.4))
    p.append(arrow(W / 2 + 50, 123, x3, y_branch - 15, color=LINE, sw=1.4))

    # Вузли умов
    p.append(rect(x1 - 110, y_branch - 15, 220, 36, fill="#eef6ff", stroke="#93c5fd", sw=1.2, rx=6))
    p.append(text(x1, y_branch + 8, "p ≡ 1, 4 (mod 5)", size=13.5, bold=True, color="#1e40af"))

    p.append(rect(x2 - 110, y_branch - 15, 220, 36, fill="#fff7ed", stroke="#fdba74", sw=1.2, rx=6))
    p.append(text(x2, y_branch + 8, "p ≡ 2, 3 (mod 5)", size=13.5, bold=True, color="#c2410c"))

    p.append(rect(x3 - 70, y_branch - 15, 140, 36, fill="#f3e8ff", stroke="#c084fc", sw=1.2, rx=6))
    p.append(text(x3, y_branch + 8, "p = 5", size=13.5, bold=True, color="#6b21a8"))

    # Стрілки від умов до результатів
    p.append(arrow(x1, y_branch + 21, x1, y_box - 15, color=LINE, sw=1.3))
    p.append(arrow(x2, y_branch + 21, x2, y_box - 15, color=LINE, sw=1.3))
    p.append(arrow(x3, y_branch + 21, x3, y_box - 15, color=LINE, sw=1.3))

    # Результативні бокси
    p.append(rect(x1 - 135, y_box - 15, 270, 125, fill="#eafaf0", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(x1, y_box + 12, "5 є квадратичним лишком", size=13, bold=True, color=FIELD))
    p.append(text(x1, y_box + 34, "√5 існує в полі F_p", size=12.5, color=INK))
    p.append(text(x1, y_box + 58, "Власні значення φ, ψ ∈ F_p", size=12, color=MUTED))
    p.append(text(x1, y_box + 88, "π(p) ділить (p − 1)", size=14, bold=True, color=FIELD))

    p.append(rect(x2 - 135, y_box - 15, 270, 125, fill="#fefce8", stroke="#eab308", sw=1.6, rx=8))
    p.append(text(x2, y_box + 12, "5 не є квадратичним лишком", size=13, bold=True, color="#a16207"))
    p.append(text(x2, y_box + 34, "√5 належить розширенню F_p²", size=12.5, color=INK))
    p.append(text(x2, y_box + 58, "Фробеніус: φ^p ≡ ψ (mod p)", size=12, color=MUTED))
    p.append(text(x2, y_box + 88, "π(p) ділить 2(p + 1)", size=14, bold=True, color="#a16207"))

    p.append(rect(x3 - 85, y_box - 15, 170, 125, fill="#fcfcfc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(x3, y_box + 18, "Вироджений випадок", size=12.5, bold=True, color=MUTED))
    p.append(text(x3, y_box + 44, "φ ≡ ψ ≡ 3 (mod 5)", size=12, color=INK))
    p.append(text(x3, y_box + 88, "π(5) = 20", size=14, bold=True, color=INK))

    render(os.path.join(OUT, "prime-split.svg"), W, H, *p, title="Класифікація періоду Пізано за модулем простого p")


def fig_matrix_orbit():
    """
    matrix-orbit.svg: Орбіта степеної матриці Q^k mod m
    Показує степені матриці Q, що повертаються до одиничної матриці I на кроці π(m).
    """
    W, H = 900, 360
    p = []

    p.append(text(W / 2, 45, "Період Пізано як мультиплікативний порядок матриці Q у GL₂(ℤ/mℤ)", size=16, bold=True))

    steps_data = [
        (120, "k = 0", "I = [[1, 0],\n [0, 1]]", True),
        (300, "k = 1", "Q = [[1, 1],\n [1, 0]]", False),
        (480, "k = 2", "Q² = [[2, 1],\n [1, 1]]", False),
        (660, "k = …", "Q^k (mod m)", False),
        (800, "k = π(m)", "Q^π(m) ≡ I\n(mod m)", True),
    ]

    for x, title_str, mat_str, is_id in steps_data:
        bw, bh = 120, 75
        fill_col = "#eafaf0" if is_id else "#fbfbfc"
        stroke_col = FIELD if is_id else LINE
        p.append(rect(x - bw / 2, 125, bw, bh, fill=fill_col, stroke=stroke_col, sw=1.8 if is_id else 1.2, rx=8))
        p.append(text(x, 110, title_str, size=13, bold=True, color=FIELD if is_id else INK))

        lines = mat_str.split("\n")
        if len(lines) == 1:
            p.append(text(x, 165, lines[0], size=12, bold=is_id, color=FIELD if is_id else INK))
        else:
            p.append(text(x, 153, lines[0], size=11.5, bold=is_id, color=FIELD if is_id else INK))
            p.append(text(x, 173, lines[1], size=11.5, bold=is_id, color=FIELD if is_id else INK))

    # Стрілки між матрицями
    p.append(arrow(180, 162, 240, 162, color=LINE, sw=1.5))
    p.append(arrow(360, 162, 420, 162, color=LINE, sw=1.5))
    p.append(arrow(540, 162, 600, 162, color=LINE, sw=1.5))
    p.append(arrow(720, 162, 740, 162, color=LINE, sw=1.5))

    # Велика зворотна дуга від k=π(m) до k=0
    p.append(path_elem("M 800 200 C 800 300, 120 300, 120 200", fill="none", stroke=FIELD, sw=2.0, dash="6,4"))
    p.append(arrow(125, 205, 120, 200, color=FIELD, sw=2.0))
    p.append(text(W / 2, 280, "Поневоле зациклення: Q^π(m) ≡ I (mod m)", size=14, bold=True, color=FIELD))

    render(os.path.join(OUT, "matrix-orbit.svg"), W, H, *p, title="Орбіта степенів матриці Q в GL2(Z/mZ)")


if __name__ == "__main__":
    fig_cycle_grid()
    fig_prime_split()
    fig_matrix_orbit()
    print("All figures generated successfully.")
