# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Орієнтована площа многокутника (формула шнурівки)».
Вивід у ./img/ за допомогою спільного модуля scripts/svgkit.py."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: Декомпозиція на орієнтовані трикутники та скасування площ ────────
def fig_shoelace_triangles():
    W, H = 860, 440
    P = []

    P.append(text(W / 2, 28, "Декомпозиція на трикутники від початку координат: скасування зовнішньої площі",
                  size=16, bold=True))

    # Початок координат O(0,0)
    ox, oy = 90, 360
    P.append(circle(ox, oy, 5.5, fill=INK, stroke=INK, sw=1.5))
    P.append(text(ox - 14, oy + 18, "O (0,0)", size=13, color=INK, bold=True, anchor="middle"))

    # Осі координат
    P.append(arrow(ox, oy, ox + 680, oy, color=MUTED, sw=1.2))
    P.append(text(ox + 695, oy + 4, "x", size=13, color=MUTED, bold=True, anchor="start"))
    P.append(arrow(ox, oy, ox, 60, color=MUTED, sw=1.2))
    P.append(text(ox, 50, "y", size=13, color=MUTED, bold=True, anchor="middle"))

    # Вершини многокутника (простий 4-кутник)
    v0 = (310, 240)
    v1 = (590, 270)
    v2 = (650, 110)
    v3 = (260, 130)

    # Заливка додатної площі
    poly_pos = f"{ox},{oy} {v3[0]},{v3[1]} {v2[0]},{v2[1]}"
    P.append(f'<polygon points="{poly_pos}" fill="#eaf7ed" stroke="{FIELD}" stroke-width="1.6" stroke-dasharray="4 3"/>')

    # Трикутник віднімання площі
    poly_neg = f"{ox},{oy} {v1[0]},{v1[1]} {v0[0]},{v0[1]}"
    P.append(f'<polygon points="{poly_neg}" fill="#fdecea" stroke="{POS}" stroke-width="1.6" stroke-dasharray="4 3"/>')

    # Сам многокутник
    poly_pts = f"{v0[0]},{v0[1]} {v1[0]},{v1[1]} {v2[0]},{v2[1]} {v3[0]},{v3[1]}"
    P.append(f'<polygon points="{poly_pts}" fill="#c3e6cb" fill-opacity="0.85" stroke="{INK}" stroke-width="2.5"/>')

    # Промені від O до вершин
    for v in (v0, v1, v2, v3):
        P.append(line(ox, oy, v[0], v[1], color=MUTED, sw=1.1, dash="3 3"))

    # Орієнтовані ребра полігона
    P.append(arrow(v0[0], v0[1], v1[0], v1[1], color=INK, sw=2.2))
    P.append(arrow(v1[0], v1[1], v2[0], v2[1], color=FIELD, sw=2.5))
    P.append(arrow(v2[0], v2[1], v3[0], v3[1], color=FIELD, sw=2.5))
    P.append(arrow(v3[0], v3[1], v0[0], v0[1], color=POS, sw=2.5))

    # Підписи вершин
    P.append(circle(v0[0], v0[1], 4.5, fill=BG, stroke=INK, sw=2))
    P.append(text(v0[0] - 12, v0[1] + 16, "V₀", size=13, color=INK, bold=True))

    P.append(circle(v1[0], v1[1], 4.5, fill=BG, stroke=INK, sw=2))
    P.append(text(v1[0] + 16, v1[1] + 16, "V₁", size=13, color=INK, bold=True))

    P.append(circle(v2[0], v2[1], 4.5, fill=BG, stroke=INK, sw=2))
    P.append(text(v2[0] + 16, v2[1] - 8, "V₂", size=13, color=INK, bold=True))

    P.append(circle(v3[0], v3[1], 4.5, fill=BG, stroke=INK, sw=2))
    P.append(text(v3[0] - 14, v3[1] - 8, "V₃", size=13, color=INK, bold=True))

    # Пояснювальні плашки збоку
    tb1, _, _ = textbox(690, 200, "+ Ребра V₁→V₂ та V₂→V₃\nдодають додатну площу\nΔ(O, V_i, V_{i+1}) > 0",
                        size=12, pad=8, fill="#eaf7ed", stroke=FIELD, color=FIELD, bold=True)
    P.append(tb1)

    tb2, _, _ = textbox(690, 310, "− Ребро V₃→V₀ та V₀→V₁\nвіднімають зайву площу\nΔ(O, V_i, V_{i+1}) < 0",
                        size=12, pad=8, fill="#fdecea", stroke=POS, color=POS, bold=True)
    P.append(tb2)

    # Центральний напис у полігоні
    P.append(text(440, 185, "Результуюча площа S", size=14, color="#155724", bold=True))
    P.append(text(440, 205, "(зовнішні сектори взаємно скоротилися)", size=11, color="#155724", italic=True))

    render("img/shoelace-triangles.svg", W, H, *P)


# ── Фігура 2: Схема шнурівки (перехресне множення матриці координат) ───────────
def fig_shoelace_matrix():
    W, H = 840, 420
    P = []

    P.append(text(W / 2, 26, "Схема діагонального перемноження координат («шнурівка»)",
                  size=16, bold=True))

    # Ліва частина — таблиця стовпчиків координат
    cx = 240
    rows = [
        ("x₀", "y₀"),
        ("x₁", "y₁"),
        ("x₂", "y₂"),
        ("x₃", "y₃"),
        ("x₀", "y₀")
    ]
    y_start = 80
    row_h = 55

    P.append(text(cx - 50, y_start - 10, "X", size=15, color=INK, bold=True))
    P.append(text(cx + 50, y_start - 10, "Y", size=15, color=INK, bold=True))

    for i, (rx, ry) in enumerate(rows):
        cy = y_start + i * row_h
        b1, _, _ = textbox(cx - 50, cy, rx, size=14, pad=6, fill=FILL, stroke=MUTED, min_w=44)
        b2, _, _ = textbox(cx + 50, cy, ry, size=14, pad=6, fill=FILL, stroke=MUTED, min_w=44)
        P.append(b1)
        P.append(b2)

    # Стрілки шнурівки між рядками
    for i in range(len(rows) - 1):
        cy1 = y_start + i * row_h
        cy2 = y_start + (i + 1) * row_h

        # Стрілка вниз-вправо: + x_i * y_{i+1} (зелена)
        P.append(arrow(cx - 25, cy1 + 8, cx + 25, cy2 - 8, color=FIELD, sw=2.2))

        # Стрілка вниз-вліво: - y_i * x_{i+1} (червона)
        P.append(arrow(cx + 25, cy1 + 8, cx - 25, cy2 - 8, color=POS, sw=2.2))

    # Легенда стрілок
    P.append(arrow(cx - 130, 360, cx - 70, 395, color=FIELD, sw=2.2))
    P.append(text(cx - 60, 395, "+ x[i] · y[i+1]", size=12, color=FIELD, bold=True, anchor="start"))

    P.append(arrow(cx + 130, 360, cx + 70, 395, color=POS, sw=2.2))
    P.append(text(cx + 80, 395, "− x[i+1] · y[i]", size=12, color=POS, bold=True, anchor="start"))

    # Права частина — формула та підсумок
    fx = 590
    tb_formula, _, _ = textbox(fx, 150,
                               "2 · S = (x₀ y₁ + x₁ y₂ + x₂ y₃ + x₃ y₀)\n"
                               "      − (y₀ x₁ + y₁ x₂ + y₂ x₃ + y₃ x₀)",
                               size=13, pad=12, fill="#f8f9fa", stroke=LINE, color=INK, bold=True)
    P.append(tb_formula)

    tb_det, _, _ = textbox(fx, 255,
                           "Еквівалентний вигляд через 2D детермінанти:\n"
                           "2 · S = ∑  det | x[i]    y[i]   |\n"
                           "               | x[i+1]  y[i+1] |",
                           size=12.5, pad=10, fill="#eef2f7", stroke=NEG, color=INK, bold=False)
    P.append(tb_det)

    tb_note, _, _ = textbox(fx, 345,
                            "Замикання контуру: останній рядок\nповторює першу вершину (x₀, y₀)",
                            size=12, pad=8, fill="#fff9db", stroke="#f59f00", color="#854d0e", bold=True)
    P.append(tb_note)

    render("img/shoelace-matrix.svg", W, H, *P)


# ── Фігура 3: Знак орієнтованої площі та напрямок обходу (CCW vs CW) ───────────
def fig_polygon_winding():
    W, H = 860, 380
    P = []

    P.append(text(W / 2, 26, "Орієнтація вершин: знак площі визначає напрямок обходу",
                  size=16, bold=True))

    # Лівий багатокутник — CCW (додатна площа)
    cx1 = 230
    p1 = [(cx1 - 100, 240), (cx1 + 80, 250), (cx1 + 110, 130), (cx1 - 60, 100)]
    pts1 = " ".join(f"{x},{y}" for x, y in p1)
    P.append(f'<polygon points="{pts1}" fill="#eaf7ed" stroke="{FIELD}" stroke-width="2.5"/>')

    # Стрілки обходу проти годинникової стрілки
    for i in range(len(p1)):
        x1, y1 = p1[i]
        x2, y2 = p1[(i + 1) % len(p1)]
        P.append(arrow(x1, y1, x2, y2, color=FIELD, sw=2.2))
        P.append(circle(x1, y1, 4.5, fill=BG, stroke=FIELD, sw=2))
        P.append(text(x1 + (-12 if i in (0, 3) else 14), y1 + (14 if i in (0, 1) else -10),
                      f"V{i}", size=12, color=FIELD, bold=True))

    # Кругова стрілка/підпис у центрі CCW
    P.append(text(cx1, 175, "Обхід CCW", size=15, color=FIELD, bold=True))
    P.append(text(cx1, 198, "проти годинникової стрілки", size=11.5, color=FIELD, italic=True))
    tb_sign1, _, _ = textbox(cx1, 310, "S > 0  (додатна площа)\nСтандартний зовнішній контур",
                             size=12.5, pad=8, fill="#eaf7ed", stroke=FIELD, color="#155724", bold=True)
    P.append(tb_sign1)

    # Правий багатокутник — CW (від'ємна площа)
    cx2 = 630
    p2 = [(cx2 - 100, 240), (cx2 - 60, 100), (cx2 + 110, 130), (cx2 + 80, 250)]
    pts2 = " ".join(f"{x},{y}" for x, y in p2)
    P.append(f'<polygon points="{pts2}" fill="#fdecea" stroke="{POS}" stroke-width="2.5"/>')

    # Стрілки обходу за годинниковою стрілкою
    for i in range(len(p2)):
        x1, y1 = p2[i]
        x2, y2 = p2[(i + 1) % len(p2)]
        P.append(arrow(x1, y1, x2, y2, color=POS, sw=2.2))
        P.append(circle(x1, y1, 4.5, fill=BG, stroke=POS, sw=2))
        P.append(text(x1 + (-12 if i in (0, 1) else 14), y1 + (14 if i in (0, 3) else -10),
                      f"V{i}", size=12, color=POS, bold=True))

    # Підпис у центрі CW
    P.append(text(cx2, 175, "Обхід CW", size=15, color=POS, bold=True))
    P.append(text(cx2, 198, "за годинниковою стрілкою", size=11.5, color=POS, italic=True))
    tb_sign2, _, _ = textbox(cx2, 310, "S < 0  (від'ємна площа)\nКонтур отвору / внутрішній виріз",
                             size=12.5, pad=8, fill="#fdecea", stroke=POS, color="#721c24", bold=True)
    P.append(tb_sign2)

    render("img/polygon-winding.svg", W, H, *P)


if __name__ == "__main__":
    fig_shoelace_triangles()
    fig_shoelace_matrix()
    fig_polygon_winding()
    print("OK: 3 figures generated in img/")
