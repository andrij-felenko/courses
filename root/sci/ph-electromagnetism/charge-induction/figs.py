# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми «Електростатична індукція» (charge-induction)."""

import os
import sys
import math

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, rect, circle, line, arrow, text, mtext, textbox, fitbox,
    plus, minus, POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)

def fig_induction_mechanism():
    """Фігура 1: Механізм електростатичної індукції у провіднику."""
    w, h = 760, 360
    frags = []

    # Заголовок / підзаголовки панелей
    frags.append(text(200, 30, "А. Нейтральний провідник у полі", size=15, bold=True))
    frags.append(text(560, 30, "Б. Електростатична рівновага", size=15, bold=True))

    # Ліва панель (А)
    # Ззовні заряджена куля (+)
    frags.append(circle(60, 180, 28, fill="#fdecea", stroke=POS, sw=2))
    for dx, dy in [(-12, -12), (12, -12), (-12, 12), (12, 12), (0, 0)]:
        frags.append(text(60 + dx, 180 + dy + 4, "+", size=14, color=POS, bold=True))
    frags.append(text(60, 225, "Заряд +Q", size=12, color=POS, bold=True))

    # Провідник (нейтральний)
    frags.append(rect(140, 110, 180, 140, fill="#f4f6f8", stroke=LINE, sw=2, rx=12))
    frags.append(text(230, 132, "Металевий провідник", size=13, bold=True))

    # Хаотичні електрони всередині
    e_coords = [(165, 160), (200, 190), (270, 165), (220, 225), (285, 215), (175, 215)]
    for ex, ey in e_coords:
        frags.append(minus(ex, ey, r=8))

    # Зовнішнє поле E_ext
    for y in [140, 180, 220]:
        frags.append(arrow(100, y, 135, y, color=FIELD, sw=2))
    frags.append(text(118, 125, "E₀", size=14, color=FIELD, bold=True, italic=True))

    # Розділювальна лінія між панелями
    frags.append(line(380, 20, 380, 340, color=MUTED, sw=1, dash="4,4"))

    # Права панель (Б)
    # Ззовні заряджена куля (+)
    frags.append(circle(420, 180, 28, fill="#fdecea", stroke=POS, sw=2))
    for dx, dy in [(-12, -12), (12, -12), (-12, 12), (12, 12), (0, 0)]:
        frags.append(text(420 + dx, 180 + dy + 4, "+", size=14, color=POS, bold=True))
    frags.append(text(420, 225, "Заряд +Q", size=12, color=POS, bold=True))

    # Провідник з наведеними зарядами
    frags.append(rect(500, 110, 180, 140, fill="#f4f6f8", stroke=LINE, sw=2, rx=12))
    frags.append(text(590, 132, "E_всередині = 0", size=13, bold=True, color=FIELD))

    # Індуктивні заряди на гранях: ліва грань -, права грань +
    for y in [155, 180, 205, 230]:
        frags.append(minus(512, y, r=7))
        frags.append(plus(668, y, r=7))

    # Вектори полів: E_0 праворуч, E_ind ліворуч
    frags.append(arrow(530, 175, 650, 175, color=FIELD, sw=2))
    frags.append(text(590, 163, "E₀ (зовнішнє)", size=12, color=FIELD, bold=True))

    frags.append(arrow(650, 210, 530, 210, color=POS, sw=2))
    frags.append(text(590, 228, "E_індук (внутрішнє)", size=12, color=POS, bold=True))

    # Підписи під фігурою
    frags.append(textbox(230, 290, "Вільні електрони вільні\nрухатися під дією E₀", size=12, pad=6)[0])
    frags.append(textbox(590, 290, "E_індук компенсує E₀:\nE_заг = E₀ − E_індук = 0", size=12, pad=6)[0])

    render(os.path.join(OUT_DIR, "induction-mechanism.svg"), w, h, *frags)

def fig_charging_by_induction():
    """Фігура 2: Чотири етапи заряджання провідника через індукцію."""
    w, h = 800, 360
    frags = []

    steps = [
        ("1. Піднесення", "Піднесення +палички:\nподіл зарядів"),
        ("2. Заземлення", "Заземлення далекого боку:\nстек позитиву з Землі"),
        ("3. Від'єднання", "Зняття заземлення:\nнадлишок − зафіксовано"),
        ("4. Готовий заряд", "Віддалення палички:\nнабуто негативний заряд")
    ]

    for i, (title_str, desc_str) in enumerate(steps):
        cx = 100 + i * 200
        frags.append(text(cx, 25, title_str, size=13, bold=True))

        # Заряджена паличка (для 1, 2, 3)
        if i < 3:
            frags.append(rect(cx - 85, 95, 20, 90, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
            for py in [110, 130, 150, 170]:
                frags.append(text(cx - 75, py + 4, "+", size=12, color=POS, bold=True))

        # Провідна куля на ізольованій ніжці
        frags.append(circle(cx, 140, 35, fill="#f4f6f8", stroke=LINE, sw=2))
        # Ніжка
        frags.append(rect(cx - 5, 175, 10, 50, fill="#e5e7eb", stroke=LINE, sw=1.5))
        frags.append(rect(cx - 25, 225, 50, 8, fill="#d1d5db", stroke=LINE, sw=1.5))

        # Заряди на кулі залежно від етапу
        if i == 0:
            # Поділ
            for cy_off in [-15, 0, 15]:
                frags.append(minus(cx - 20, 140 + cy_off, r=6))
                frags.append(plus(cx + 20, 140 + cy_off, r=6))
        elif i == 1:
            # Заземлення: ліворуч мінуси, праворуч зв'язок із землею
            for cy_off in [-18, -6, 6, 18]:
                frags.append(minus(cx - 20, 140 + cy_off, r=6))
            # Дріт заземлення
            frags.append(line(cx + 35, 140, cx + 60, 140, color=LINE, sw=2))
            frags.append(line(cx + 60, 140, cx + 60, 180, color=LINE, sw=2))
            # Знак землі
            frags.append(line(cx + 48, 180, cx + 72, 180, color=LINE, sw=2))
            frags.append(line(cx + 52, 185, cx + 68, 185, color=LINE, sw=1.5))
            frags.append(line(cx + 56, 190, cx + 64, 190, color=LINE, sw=1))
            # Стрілка руху електронів із землі
            frags.append(arrow(cx + 60, 175, cx + 60, 145, color=NEG, sw=1.8))
            frags.append(text(cx + 70, 160, "e⁻", size=11, color=NEG, bold=True))
        elif i == 2:
            # Від'єднано заземлення, паличка ще поруч
            for cy_off in [-18, -6, 6, 18]:
                frags.append(minus(cx - 20, 140 + cy_off, r=6))
        elif i == 3:
            # Паличка прибрана, мінуси розподілилися по всій кулі
            angles = [0, 60, 120, 180, 240, 300]
            for a in angles:
                rad = math.radians(a)
                mx = cx + 22 * math.cos(rad)
                my = 140 + 22 * math.sin(rad)
                frags.append(minus(mx, my, r=6))

        # Опис під етапом
        frags.append(fitbox(cx - 85, 245, 170, 95, desc_str, size=11, pad=6))

    render(os.path.join(OUT_DIR, "charging-by-induction.svg"), w, h, *frags)

def fig_method_of_images():
    """Фігура 3: Метод дзеркальних зарядів для точкового заряду біля заземленого екрана."""
    w, h = 720, 380
    frags = []

    frags.append(text(360, 25, "Метод дзеркальних зображень (точковий заряд біля плоскої межі)", size=15, bold=True))

    # Площина x = 0 (заземлений провідник)
    px = 360
    frags.append(rect(px - 6, 55, 12, 270, fill="#d1d5db", stroke=LINE, sw=2))
    frags.append(text(px, 345, "Заземлена металева площина (V = 0)", size=12, bold=True))

    # Знак заземлення на площині
    frags.append(line(px, 315, px + 35, 315, color=LINE, sw=1.5))
    frags.append(line(px + 35, 315, px + 35, 330, color=LINE, sw=1.5))
    frags.append(line(px + 23, 330, px + 47, 330, color=LINE, sw=2))
    frags.append(line(px + 27, 334, px + 43, 334, color=LINE, sw=1.5))
    frags.append(line(px + 31, 338, px + 39, 338, color=LINE, sw=1))

    # Реальний заряд +q праворуч
    qx = px + 180
    qy = 185
    frags.append(circle(qx, qy, 16, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(qx, qy + 5, "+q", size=14, color=POS, bold=True))
    frags.append(text(qx, qy - 24, "Реальний заряд", size=12, color=POS, bold=True))

    # Фіктивний дзеркальний заряд -q ліворуч
    ix = px - 180
    iy = 185
    frags.append(circle(ix, iy, 16, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(ix, iy + 4, "−q", size=14, color=NEG, bold=True))
    frags.append(text(ix, iy - 24, "Дзеркальний заряд (фіктивний)", size=12, color=NEG, bold=True))

    # Осі відстаней
    frags.append(line(ix, qy, qx, qy, color=MUTED, sw=1, dash="3,3"))
    frags.append(arrow(px, qy + 40, qx, qy + 40, color=INK, sw=1.5))
    frags.append(arrow(qx, qy + 40, px, qy + 40, color=INK, sw=1.5))
    frags.append(text(px + 90, qy + 34, "d", size=13, bold=True, italic=True))

    frags.append(arrow(ix, qy + 40, px, qy + 40, color=INK, sw=1.5))
    frags.append(arrow(px, qy + 40, ix, qy + 40, color=INK, sw=1.5))
    frags.append(text(px - 90, qy + 34, "d", size=13, bold=True, italic=True))

    # Силові лінії поля (праворуч від площини)
    for target_y in [75, 115, 150, 185, 220, 255, 295]:
        frags.append(line(qx, qy, px + 2, target_y, color=FIELD, sw=1.5))
        mx = (qx + px) / 2
        my = (qy + target_y) / 2
        frags.append(arrow(mx + (qx - px) * 0.1, my + (qy - target_y) * 0.1,
                           mx - (qx - px) * 0.1, my - (qy - target_y) * 0.1, color=FIELD, sw=1.5))
        frags.append(minus(px + 10, target_y, r=5))

    frags.append(text(px + 40, 200, "σ(y)", size=12, color=NEG, bold=True, italic=True))
    frags.append(textbox(540, 330, "Густина наведеного заряду:\nσ(y) = −q·d / [2π(d² + y²)³/²]", size=11, pad=6)[0])

    render(os.path.join(OUT_DIR, "method-of-images.svg"), w, h, *frags)

def fig_faraday_ice_pail():
    """Фігура 4: Дослід Фарадея з льодовим відром (Faraday's ice pail experiment)."""
    w, h = 760, 360
    frags = []

    frags.append(text(380, 25, "Експеримент Фарадея з металевим відром (індукція у замкненій порожнині)", size=15, bold=True))

    panels = [
        ("А. Внесення +q всередину", 140),
        ("Б. Заземлення ззовні", 380),
        ("В. Лишається тільки −q на стінці", 620)
    ]

    for title_str, cx in panels:
        frags.append(text(cx, 55, title_str, size=13, bold=True))

        # Металеве відро (U-подібний провідник)
        frags.append(rect(cx - 45, 100, 10, 120, fill="#d1d5db", stroke=LINE, sw=1.5))
        frags.append(rect(cx + 35, 100, 10, 120, fill="#d1d5db", stroke=LINE, sw=1.5))
        frags.append(rect(cx - 45, 210, 90, 10, fill="#d1d5db", stroke=LINE, sw=1.5))

        if title_str.startswith("А"):
            # Зарядщена кулька +q всередині
            frags.append(line(cx, 75, cx, 145, color=MUTED, sw=1.5))
            frags.append(circle(cx, 150, 14, fill="#fdecea", stroke=POS, sw=2))
            frags.append(text(cx, 154, "+q", size=12, color=POS, bold=True))

            # Індукований -q всередині відра
            for y in [120, 150, 180]:
                frags.append(minus(cx - 30, y, r=5))
                frags.append(minus(cx + 30, y, r=5))

            # Індукований +q ззовні відра
            for y in [120, 150, 180]:
                frags.append(plus(cx - 52, y, r=5))
                frags.append(plus(cx + 52, y, r=5))

            frags.append(fitbox(cx - 90, 240, 180, 85, "Внутрішня стінка: −q\nЗовнішня стінка: +q\nПоле ззовні присутнє", size=11, pad=5))

        elif title_str.startswith("Б"):
            # Зарядщена кулька +q всередині
            frags.append(line(cx, 75, cx, 145, color=MUTED, sw=1.5))
            frags.append(circle(cx, 150, 14, fill="#fdecea", stroke=POS, sw=2))
            frags.append(text(cx, 154, "+q", size=12, color=POS, bold=True))

            # Індукований -q всередині
            for y in [120, 150, 180]:
                frags.append(minus(cx - 30, y, r=5))
                frags.append(minus(cx + 30, y, r=5))

            # Дріт заземлення ззовні
            frags.append(line(cx + 45, 160, cx + 75, 160, color=LINE, sw=2))
            frags.append(line(cx + 75, 160, cx + 75, 190, color=LINE, sw=2))
            frags.append(line(cx + 63, 190, cx + 87, 190, color=LINE, sw=2))
            frags.append(line(cx + 67, 194, cx + 83, 194, color=LINE, sw=1.5))
            frags.append(line(cx + 71, 198, cx + 79, 198, color=LINE, sw=1))

            frags.append(fitbox(cx - 90, 240, 180, 85, "Зовнішній +q іде в Землю\nПоле ззовні зникає!\nV_відра = 0", size=11, pad=5))

        elif title_str.startswith("В"):
            # Заряджена кулька торкається внутрішньої стінки -> скасування зарядів
            frags.append(line(cx, 75, cx, 150, color=MUTED, sw=1.5))
            frags.append(circle(cx - 28, 150, 12, fill="#e5e7eb", stroke=LINE, sw=1.5))
            frags.append(text(cx - 28, 154, "0", size=11, color=MUTED, bold=True))
            frags.append(fitbox(cx - 85, 240, 170, 85, "При торканні стінки:\n+q кульки нейтралізує −q\nвідра. Заряд кульки = 0!\nЗзовні заряд не з'являється", size=11, pad=5))

    render(os.path.join(OUT_DIR, "faraday-ice-pail.svg"), w, h, *frags)

def fig_charge_concentration_tips():
    """Фігура 5: Концентрація наведеного заряду та напруженості поля на вістрях."""
    w, h = 720, 320
    frags = []

    frags.append(text(360, 25, "Концентрація наведеного заряду на вістрях провідника", size=15, bold=True))

    path_d = "M 180,160 C 180,90 280,100 480,150 C 510,155 520,160 510,165 C 480,170 280,220 180,160 Z"
    frags.append('<path d="%s" fill="#f4f6f8" stroke="%s" stroke-width="2"/>' % (path_d, LINE))

    frags.append(circle(210, 155, 3, fill=MUTED, stroke=MUTED, sw=1))
    frags.append(arrow(210, 155, 180, 155, color=MUTED, sw=1.5))
    frags.append(text(225, 150, "Великий радіус R₁", size=12, color=MUTED, bold=True))

    frags.append(circle(500, 160, 2, fill=MUTED, stroke=MUTED, sw=1))
    frags.append(arrow(500, 160, 515, 160, color=MUTED, sw=1.5))
    frags.append(text(430, 140, "Малий радіус R₂ (вістря)", size=12, color=POS, bold=True))

    for y in [130, 160, 190]:
        frags.append(plus(170, y, r=6))

    for dx, dy in [(470, 142), (485, 148), (498, 154), (508, 160), (498, 166), (485, 172), (470, 178)]:
        frags.append(plus(dx, dy, r=5))

    frags.append(arrow(160, 160, 110, 160, color=FIELD, sw=2))
    frags.append(text(125, 148, "E₁ (слабке)", size=12, color=FIELD, bold=True))

    frags.append(arrow(515, 160, 620, 160, color=FIELD, sw=2.5))
    frags.append(text(570, 148, "E₂ ∝ 1/R₂ (сильне!)", size=13, color=FIELD, bold=True))

    frags.append(textbox(360, 265, "Потенціал однаковий: V₁ = V₂  ⇒  q₁/R₁ = q₂/R₂  ⇒  σ₂/σ₁ = R₁/R₂\nНа гострих ділянках (малий R) густина заряду σ та напруженість E_n = σ/ε₀ максимальні!", size=12, pad=8)[0])

    render(os.path.join(OUT_DIR, "charge-concentration-tips.svg"), w, h, *frags)

def main():
    fig_induction_mechanism()
    fig_charging_by_induction()
    fig_method_of_images()
    fig_faraday_ice_pail()
    fig_charge_concentration_tips()
    print("Всі SVG-фігури для charge-induction успішно згенеровано.")

if __name__ == "__main__":
    main()
