# -*- coding: utf-8 -*-
"""Фігури до статті «Розділення секрету Шаміра»."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 1: Геометрична інтуїція — поліном степеня k-1 визначений k точками
# ─────────────────────────────────────────────────────────────────────────────
def fig_geom_threshold():
    W, H = 820, 420
    frby = []

    # Панель 1 (Ліва): k=2 (ступінь 1)
    bx1, by1, bw, bh = 30, 50, 360, 320
    frby.append(rect(bx1, by1, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frby.append(text(bx1 + bw / 2, by1 + 26, "Поріг k = 2 (поліном степеня 1: пряма)", size=14, bold=True, color=INK))

    ox1, oy1 = bx1 + 50, by1 + bh - 55
    frby.append(line(ox1 - 10, oy1, ox1 + 280, oy1, color=MUTED, sw=1.5))
    frby.append(line(ox1, oy1 + 10, ox1, oy1 - 220, color=MUTED, sw=1.5))
    frby.append(text(ox1 + 290, oy1 + 4, "x", size=13, bold=True, color=MUTED))
    frby.append(text(ox1 - 4, oy1 - 230, "y", size=13, bold=True, color=MUTED))

    px1, py1 = ox1 + 120, oy1 - 100
    frby.append(line(ox1 - 20, oy1 - 30, ox1 + 240, oy1 - 160, color="#cbd5e1", sw=1.8, dash="4 4"))
    frby.append(line(ox1 - 20, oy1 - 100, ox1 + 240, oy1 - 100, color=POS, sw=2.2))
    frby.append(line(ox1 - 20, oy1 - 170, ox1 + 240, oy1 - 40, color="#cbd5e1", sw=1.8, dash="4 4"))

    frby.append(circle(ox1, oy1 - 30, 4, fill=NEG, stroke=NEG))
    frby.append(text(ox1 - 16, oy1 - 26, "S'", size=12, color=NEG))
    frby.append(circle(ox1, oy1 - 100, 5, fill=POS, stroke=INK, sw=1.5))
    frby.append(text(ox1 - 16, oy1 - 96, "S", size=13, bold=True, color=POS))
    frby.append(circle(ox1, oy1 - 170, 4, fill=NEG, stroke=NEG))
    frby.append(text(ox1 - 16, oy1 - 166, "S''", size=12, color=NEG))

    frby.append(circle(px1, py1, 6, fill=FIELD, stroke=INK, sw=1.5))
    frby.append(text(px1, py1 - 14, "(x₁, y₁)", size=12, bold=True, color=FIELD))

    frby.append(text(bx1 + bw / 2, by1 + bh - 24, "1 точка (k-1) ⟹ безліч прямих", size=12, color=MUTED))
    frby.append(text(bx1 + bw / 2, by1 + bh - 6, "Секрет S = f(0) невідомий", size=12, color=MUTED))

    # Панель 2 (Права): k=3 (ступінь 2: парабола)
    bx2, by2 = 430, 50
    frby.append(rect(bx2, by2, bw, bh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frby.append(text(bx2 + bw / 2, by2 + 26, "Поріг k = 3 (поліном степеня 2: парабола)", size=14, bold=True, color=INK))

    ox2, oy2 = bx2 + 50, by2 + bh - 55
    frby.append(line(ox2 - 10, oy2, ox2 + 280, oy2, color=MUTED, sw=1.5))
    frby.append(line(ox2, oy2 + 10, ox2, oy2 - 220, color=MUTED, sw=1.5))
    frby.append(text(ox2 + 290, oy2 + 4, "x", size=13, bold=True, color=MUTED))
    frby.append(text(ox2 - 4, oy2 - 230, "y", size=13, bold=True, color=MUTED))

    p1 = (ox2 + 60, oy2 - 70)
    p2 = (ox2 + 140, oy2 - 150)
    p3 = (ox2 + 220, oy2 - 110)

    curve_d = f"M {ox2} {oy2 - 50} Q {ox2 + 100} {oy2 - 220} {ox2 + 250} {oy2 - 80}"
    frby.append(f'<path d="{curve_d}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    curve_alt1 = f"M {ox2} {oy2 - 130} Q {ox2 + 100} {oy2 - 180} {ox2 + 250} {oy2 - 20}"
    frby.append(f'<path d="{curve_alt1}" fill="none" stroke="#cbd5e1" stroke-width="1.8" stroke-dasharray="4 4"/>')

    frby.append(circle(ox2, oy2 - 50, 6, fill=POS, stroke=INK, sw=1.5))
    frby.append(text(ox2 - 16, oy2 - 46, "S", size=13, bold=True, color=POS))
    frby.append(circle(ox2, oy2 - 130, 4, fill=NEG, stroke=NEG))
    frby.append(text(ox2 - 16, oy2 - 126, "S'", size=12, color=NEG))

    frby.append(circle(p1[0], p1[1], 5, fill=FIELD, stroke=INK, sw=1.5))
    frby.append(text(p1[0], p1[1] + 18, "(x₁, y₁)", size=11, bold=True, color=FIELD))

    frby.append(circle(p2[0], p2[1], 5, fill=FIELD, stroke=INK, sw=1.5))
    frby.append(text(p2[0] - 12, p2[1] - 12, "(x₂, y₂)", size=11, bold=True, color=FIELD))

    frby.append(circle(p3[0], p3[1], 5, fill=FIELD, stroke=INK, sw=1.5))
    frby.append(text(p3[0] + 12, p3[1] + 18, "(x₃, y₃)", size=11, bold=True, color=FIELD))

    frby.append(text(bx2 + bw / 2, by2 + bh - 24, "3 точки (k) ⟹ єдина крива f(x)", size=12, color=MUTED))
    frby.append(text(bx2 + bw / 2, by2 + bh - 6, "Точно визначає S = f(0)", size=12, color=MUTED))

    render(os.path.join(OUT, "geom-threshold.svg"), W, H, *frby,
           title="Геометрична інтуїція порогової схеми: поліном степеня k-1 визначений k точками")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 2: Архітектура порогового розділення секрету Шаміра (k, n)
# ─────────────────────────────────────────────────────────────────────────────
def fig_shamir_architecture():
    W, H = 840, 480
    frby = []

    # 1. Дилєр
    frby.append(rect(40, 160, 210, 150, fill="#eef2f7", stroke=INK, sw=2, rx=8))
    frby.append(text(145, 185, "Дилер (Dealer)", size=15, bold=True, color=INK))
    frby.append(line(50, 198, 240, 198, color=LINE, sw=1))
    frby.append(text(145, 222, "Секрет S = f(0)", size=13, bold=True, color=POS))
    frby.append(text(145, 248, "f(x) = S + a₁x + ... mod p", size=12, color=INK))
    frby.append(text(145, 276, "a₁, ..., aₖ₋₁ ~ CSPRNG", size=11, color=MUTED))

    # Стрілки роздачі часток до n учасників
    parts = [
        (370, 50, "Учасник 1", "(1, y₁)", True),
        (370, 135, "Учасник 2", "(2, y₂)", True),
        (370, 220, "Учасник 3", "(3, y₃)", False),
        (370, 335, "Учасник n", "(n, yₙ)", True),
    ]

    frby.append(text(370, 276, "•  •  •", size=16, bold=True, color=MUTED))

    for x, y, name, share, active in parts:
        col_fill = "#e7f7ee" if active else "#f8fafc"
        col_st = FIELD if active else LINE
        frby.append(rect(x - 65, y - 20, 130, 40, fill=col_fill, stroke=col_st, sw=1.6, rx=6))
        frby.append(text(x, y - 4, name, size=12, bold=True, color=INK))
        frby.append(text(x, y + 12, share, size=11, color=FIELD if active else MUTED))

        frby.append(arrow(250, 235, x - 65, y, color=LINE, sw=1.5))

    # Блок відновлення секрету (збирає k часток)
    frby.append(rect(590, 160, 210, 150, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    frby.append(text(695, 185, "Відновлення", size=15, bold=True, color=FIELD))
    frby.append(line(600, 198, 790, 198, color=FIELD, sw=1))
    frby.append(text(695, 222, "Інтерполяція Лагранжа", size=12, bold=True, color=INK))
    frby.append(text(695, 248, "S = ∑ yᵢ · ℓᵢ(0) mod p", size=12, bold=True, color=POS))
    frby.append(text(695, 276, "Потрібно k із n часток", size=11, color=MUTED))

    for x, y, name, share, active in parts:
        if active:
            frby.append(arrow(x + 65, y, 590, 235, color=FIELD, sw=1.8))

    frby.append(text(W / 2, 415, "Будь-які k активних учасників відновлюють секрет S.", size=12, color=MUTED))
    frby.append(text(W / 2, 442, "Менше ніж k учасників знають про S не більше, ніж сторонній спостерігач.", size=12, color=MUTED))

    render(os.path.join(OUT, "shamir-architecture.svg"), W, H, *frby,
           title="Порогова схема розділення секрету Шаміра (k, n)")


# ─────────────────────────────────────────────────────────────────────────────
# Фігура 3: Досконала таємність у скінченному полі GF(p)
# ─────────────────────────────────────────────────────────────────────────────
def fig_finite_field_secrecy():
    W, H = 800, 440
    frby = []

    # Сітка поля GF(p), p = 7
    bx, by, bw, bh = 140, 60, 360, 320
    frby.append(rect(bx, by, bw, bh, fill="#ffffff", stroke=INK, sw=2, rx=4))

    p_val = 7
    cell_w = bw / p_val
    cell_h = bh / p_val

    for i in range(1, p_val):
        frby.append(line(bx + i * cell_w, by, bx + i * cell_w, by + bh, color="#e2e8f0", sw=1))
        frby.append(line(bx, by + i * cell_h, bx + bw, by + i * cell_h, color="#e2e8f0", sw=1))

    for i in range(p_val):
        frby.append(text(bx + (i + 0.5) * cell_w, by + bh + 16, str(i), size=12, color=INK))
        frby.append(text(bx - 16, by + bh - (i + 0.5) * cell_h + 4, str(i), size=12, color=INK))

    frby.append(text(bx + bw / 2, by + bh + 36, "Аргумент x ∈ GF(7)", size=13, bold=True, color=INK))
    frby.append(text(bx - 45, by + bh / 2, "y = f(x)", size=13, bold=True, color=INK))

    pt1_x, pt1_y = 2, 4
    pt2_x, pt2_y = 5, 1

    cx1 = bx + (pt1_x + 0.5) * cell_w
    cy1 = by + bh - (pt1_y + 0.5) * cell_h

    cx2 = bx + (pt2_x + 0.5) * cell_w
    cy2 = by + bh - (pt2_y + 0.5) * cell_h

    colors = ["#e11d48", "#ea580c", "#d97706", "#16a34a", "#0284c7", "#4f46e5", "#9333ea"]

    for S_cand in range(p_val):
        cy_s = by + bh - (S_cand + 0.5) * cell_h
        frby.append(circle(bx + 0.5 * cell_w, cy_s, 4, fill=colors[S_cand], stroke=INK, sw=1))

    frby.append(circle(cx1, cy1, 8, fill=FIELD, stroke=INK, sw=2))
    frby.append(text(cx1 + 25, cy1 - 10, "Частка 1: (2, 4)", size=12, bold=True, color=FIELD))

    frby.append(circle(cx2, cy2, 8, fill=FIELD, stroke=INK, sw=2))
    frby.append(text(cx2 + 25, cy2 - 10, "Частка 2: (5, 1)", size=12, bold=True, color=FIELD))

    rx, ry, rw, rh = 530, 60, 240, 320
    frby.append(rect(rx, ry, rw, rh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=6))
    frby.append(text(rx + rw / 2, ry + 24, "Рівноймовірність S", size=14, bold=True, color=INK))
    frby.append(line(rx + 10, ry + 36, rx + rw - 10, ry + 36, color=LINE, sw=1))

    frby.append(text(rx + rw / 2, ry + 56, "Для БУДЬ-ЯКОГО S' ∈ GF(7)", size=12, color=INK))
    frby.append(text(rx + rw / 2, ry + 76, "існує РІВНО ОДИН поліном", size=12, color=INK))
    frby.append(text(rx + rw / 2, ry + 96, "степеня 2, що проходить", size=12, color=INK))
    frby.append(text(rx + rw / 2, ry + 116, "через (0, S') та 2 точки.", size=12, color=INK))

    frby.append(rect(rx + 15, ry + 150, rw - 30, 65, fill="#eaf7ed", stroke=FIELD, sw=1.5, rx=6))
    frby.append(text(rx + rw / 2, ry + 174, "P(S = S' | 2 частки) = 1/7", size=13, bold=True, color=POS))
    frby.append(text(rx + rw / 2, ry + 196, "Нуль витоку інформації!", size=12, bold=True, color=FIELD))

    frby.append(text(rx + rw / 2, ry + 250, "Усі 7 кандидатів секрету", size=11, color=MUTED))
    frby.append(text(rx + rw / 2, ry + 270, "абсолютно рівноймовірні.", size=11, color=MUTED))

    render(os.path.join(OUT, "finite-field-secrecy.svg"), W, H, *frby,
           title="Досконала таємність Шеннона в полі GF(7)")


if __name__ == "__main__":
    fig_geom_threshold()
    fig_shamir_architecture()
    fig_finite_field_secrecy()
    print("OK: 3 фігури згенеровано в", OUT)
