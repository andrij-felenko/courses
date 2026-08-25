#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генератор ілюстрацій до теми 'Діофантові множини та теорема ДПРМ'."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_dprm_equivalence():
    """Діаграма концептуального мосту між теорією обчислюваності та діофантовими рівняннями."""
    w, h = 860, 430
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 30, "Концептуальний міст теореми ДПРМ (RE ≡ Діофантові множини)", size=18, bold=True))

    # Ліва колонка: Теорія обчислюваності
    col1_x, col1_w = 30, 240
    frags.append(rect(col1_x, 60, col1_w, 340, fill="none", stroke=NEG, sw=1.8, rx=8))
    frags.append(text(col1_x + col1_w / 2, 90, "Теорія обчислюваності", size=15, bold=True, color=NEG))
    frags.append(text(col1_x + col1_w / 2, 112, "Світ машин та алгоритмів", size=12, color=MUTED, italic=True))

    b1, _, _ = textbox(col1_x + col1_w / 2, 160, "Машина Тюрінга\nПроблема зупинки K", size=13, pad=8, fill="#f0f4fc", stroke=LINE)
    b2, _, _ = textbox(col1_x + col1_w / 2, 235, "Рекурсивно перелічні\nмножини (клас RE / Σ₁⁰)", size=13, pad=8, fill="#f0f4fc", stroke=LINE)
    b3, _, _ = textbox(col1_x + col1_w / 2, 320, "Напіввирішуваність:\n∃ t (Крок t дає Halt)", size=13, pad=8, fill="#f0f4fc", stroke=LINE)
    frags.extend([b1, b2, b3])
    frags.append(arrow(col1_x + col1_w / 2, 190, col1_x + col1_w / 2, 210, sw=1.5))
    frags.append(arrow(col1_x + col1_w / 2, 265, col1_x + col1_w / 2, 290, sw=1.5))

    # Центральна колонка: 4 етапи доведення
    col2_x, col2_w = 300, 260
    frags.append(rect(col2_x, 60, col2_w, 340, fill="none", stroke="#d97706", sw=1.8, rx=8))
    frags.append(text(col2_x + col2_w / 2, 90, "Еволюція редукції", size=15, bold=True, color="#b45309"))
    frags.append(text(col2_x + col2_w / 2, 112, "1950 — 1970 роки", size=12, color=MUTED, italic=True))

    m1, _, _ = textbox(col2_x + col2_w / 2, 155, "Нормальна форма Девіса (1950)\n∀ z ≤ y ∃ w (P = 0)", size=12, pad=6, fill="#fdfbf7", stroke=LINE)
    m2, _, _ = textbox(col2_x + col2_w / 2, 235, "Теорема DPR (1961)\nЕкспоненційно діофантові (aᵇ = c)", size=12, pad=6, fill="#fdfbf7", stroke=LINE)
    m3, _, _ = textbox(col2_x + col2_w / 2, 320, "Прорив Матіясевича (1970)\nРівняння Пелля: aᵇ суто в ℤ[X]", size=12, pad=6, fill="#fdfbf7", stroke=LINE)
    frags.extend([m1, m2, m3])
    frags.append(arrow(col2_x + col2_w / 2, 185, col2_x + col2_w / 2, 210, color="#d97706", sw=1.5))
    frags.append(arrow(col2_x + col2_w / 2, 265, col2_x + col2_w / 2, 290, color="#d97706", sw=1.5))

    # Права колонка: Теорія чисел
    col3_x, col3_w = 590, 240
    frags.append(rect(col3_x, 60, col3_w, 340, fill="none", stroke=FIELD, sw=1.8, rx=8))
    frags.append(text(col3_x + col3_w / 2, 90, "Теорія чисел та алгебра", size=15, bold=True, color=FIELD))
    frags.append(text(col3_x + col3_w / 2, 112, "Світ многочленів у цілих числах", size=12, color=MUTED, italic=True))

    r1, _, _ = textbox(col3_x + col3_w / 2, 160, "Многочлен P(a, x₁, ..., xₘ) = 0\nЦілі коефіцієнти", size=13, pad=8, fill="#f0faf4", stroke=LINE)
    r2, _, _ = textbox(col3_x + col3_w / 2, 235, "Діофантова множина:\na ∈ S ⇔ ∃ x ∈ ℕᵐ (P(a,x) = 0)", size=13, pad=8, fill="#f0faf4", stroke=LINE)
    r3, _, _ = textbox(col3_x + col3_w / 2, 320, "10-та проблема Гільберта:\nАлгоритму пошуку НЕ існує", size=13, pad=8, fill="#f0faf4", stroke=POS)
    frags.extend([r1, r2, r3])
    frags.append(arrow(col3_x + col3_w / 2, 190, col3_x + col3_w / 2, 210, sw=1.5))
    frags.append(arrow(col3_x + col3_w / 2, 265, col3_x + col3_w / 2, 290, sw=1.5))

    # Великі зв'язувальні стрілки між колонками
    frags.append(arrow(col1_x + col1_w, 235, col2_x, 235, color="#d97706", sw=2.5))
    frags.append(arrow(col2_x + col2_w, 235, col3_x, 235, color=FIELD, sw=2.5))

    render(os.path.join(IMG_DIR, "dprm-equivalence.svg"), w, h, *frags)


def fig_pell_growth():
    """Ілюстрація експоненційного розльоту розв'язків рівняння Пелля та рекурентного зростання."""
    w, h = 860, 420
    frags = []

    frags.append(text(w / 2, 28, "Рівняння Пелля x² − (d² − 1)y² = 1 як генератор експоненти", size=17, bold=True))

    # Ліва частина: Графік гіперболи та дискретні точки-розв'язки
    ox, oy = 80, 350
    frags.append(rect(ox - 30, 55, 390, 335, fill="none", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(ox + 165, 80, "Гілка гіперболи та цілочисельні точки (d = 2)", size=13, bold=True, color=INK))

    # Осі
    frags.append(arrow(ox, oy, ox + 330, oy, color=LINE, sw=1.5))
    frags.append(text(ox + 340, oy + 4, "x", size=13, bold=True))
    frags.append(arrow(ox, oy, ox, oy - 260, color=LINE, sw=1.5))
    frags.append(text(ox, oy - 270, "y", size=13, bold=True))

    # Сітка та мітки
    for i in range(1, 6):
        gx = ox + i * 55
        frags.append(line(gx, oy - 5, gx, oy + 5, color=MUTED, sw=1))
        frags.append(line(gx, oy, gx, oy - 240, color="#e5e7eb", sw=1, dash="3,3"))
    for j in range(1, 5):
        gy = oy - j * 55
        frags.append(line(ox - 5, gy, ox + 5, gy, color=MUTED, sw=1))
        frags.append(line(ox, gy, ox + 300, gy, color="#e5e7eb", sw=1, dash="3,3"))

    # Крива гіперболи x² - 3y² = 1 => x = √(1 + 3y²)
    # Масштаб: x_scale = 10 px per unit, y_scale = 18 px per unit
    pts = []
    for step in range(0, 130):
        y_val = step / 10.0
        x_val = (1.0 + 3.0 * y_val * y_val) ** 0.5
        px = ox + x_val * 10.5
        py = oy - y_val * 18.5
        if px <= ox + 310 and py >= oy - 250:
            pts.append((px, py))

    path_d = ["M %.1f %.1f" % pts[0]]
    for p in pts[1:]:
        path_d.append("L %.1f %.1f" % p)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (" ".join(path_d), NEG))

    # Точки розв'язків:
    # n=0: (1, 0)
    # n=1: (2, 1) -> x=2, y=1
    # n=2: (7, 4) -> x=7, y=4
    # n=3: (26, 15) -> x=26, y=15
    sol_pts = [
        (0, 1, 0, ox + 1 * 10.5, oy - 0 * 18.5, "(x₀, y₀) = (1, 0)"),
        (1, 2, 1, ox + 2 * 10.5, oy - 1 * 18.5, "(x₁, y₁) = (2, 1)"),
        (2, 7, 4, ox + 7 * 10.5, oy - 4 * 18.5, "(x₂, y₂) = (7, 4)"),
        (3, 26, 15, ox + 26 * 10.5, oy - 15 * 18.5, "(x₃, y₃) = (26, 15)"),
    ]
    for n, x_v, y_v, px, py, lbl in sol_pts:
        frags.append(circle(px, py, 4.5, fill=POS, stroke="#991b1b", sw=1.5))
        # Зміщення підпису для уникнення накладання
        lx = px + 12 if n < 2 else px - 65
        ly = py - 8 if n < 3 else py - 12
        frags.append(text(lx, ly, lbl, size=11, bold=True, color=INK, anchor="start" if n < 2 else "end"))

    # Права частина: Алгебраїчна структура та властивості експоненційного росту
    rx = 490
    frags.append(rect(rx, 55, 340, 335, fill="none", stroke="#d97706", sw=1.2, rx=6))
    frags.append(text(rx + 170, 80, "Рекурентність та оцінка зростання", size=13, bold=True, color="#b45309"))

    t1, _, _ = textbox(rx + 170, 130, "Характеристичний корінь:\nα = d + √(d² − 1) > 1", size=12, pad=6, fill="#ffffff", stroke=LINE)
    t2, _, _ = textbox(rx + 170, 205, "Формула Біне для Пелля:\nyₙ(d) = (αⁿ − α⁻ⁿ) / (2√(d² − 1))", size=12, pad=6, fill="#ffffff", stroke=LINE)
    t3, _, _ = textbox(rx + 170, 285, "Асимптотичне зростання:\n(2d − 1)ⁿ ≤ yₙ₊₁(d) ≤ (2d)ⁿ", size=12, pad=6, fill="#ffffff", stroke=FIELD)
    t4, _, _ = textbox(rx + 170, 350, "Конгруенція порядку степеня:\nyₙ(d) ≡ n (mod d − 1)", size=12, pad=6, fill="#ffffff", stroke=POS)
    frags.extend([t1, t2, t3, t4])

    render(os.path.join(IMG_DIR, "pell-growth-lattice.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_dprm_equivalence()
    fig_pell_growth()
    print("Фігури успішно згенеровано.")
