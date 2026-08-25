# -*- coding: utf-8 -*-
"""Генерація SVG-фігур для теми 'Демон Максвелла й ціна інформації'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def build_fig1_maxwell_box():
    """Фігура 1: Класична схема демона Максвелла з розподілом молекул за швидкостями."""
    w, h = 800, 420
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Класичний мисленнєвий експеримент: сортування молекул демоном", size=16, bold=True))

    # Основна судина
    box_x, box_y, box_w, box_h = 50, 60, 700, 280
    frags.append(rect(box_x, box_y, box_w, box_h, fill="#f8fafc", stroke=LINE, sw=2, rx=6))

    # Розділювальна перегородка
    mid_x = box_x + box_w / 2
    door_top = box_y + 110
    door_bottom = box_y + 170
    frags.append(line(mid_x, box_y, mid_x, door_top, color=LINE, sw=3))
    frags.append(line(mid_x, door_bottom, mid_x, box_y + box_h, color=LINE, sw=3))

    # Дверцята (підняті / відкриті)
    frags.append(line(mid_x, door_top, mid_x + 18, door_top - 25, color=NEG, sw=3))
    frags.append(circle(mid_x + 18, door_top - 25, 4, fill=NEG, stroke="none"))
    frags.append(text(mid_x + 28, door_top - 28, "дверцята", size=11, color=NEG, bold=True))

    # Демон над дверцятами
    dem_x, dem_y = mid_x - 35, door_top - 55
    frags.append(rect(dem_x, dem_y, 70, 32, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    frags.append(text(dem_x + 35, dem_y + 20, "Демон", size=13, color="#b45309", bold=True))

    # Підписи відсіків A і B
    frags.append(text(box_x + 175, box_y + 35, "Відсік А (нагрівається)", size=14, bold=True, color=POS))
    frags.append(text(box_x + 525, box_y + 35, "Відсік Б (охолоджується)", size=14, bold=True, color=FIELD))

    # Молекули у відсіку А (гарячі: червоні, довгі стрілки)
    fast_mols = [
        (100, 120, 25, -10), (160, 180, 20, 15), (220, 100, 30, 5),
        (120, 240, 22, -15), (250, 220, 28, -8), (290, 150, 35, -5)
    ]
    for mx, my, vx, vy in fast_mols:
        frags.append(circle(mx, my, 8, fill="#fee2e2", stroke=POS, sw=2))
        frags.append(arrow(mx, my, mx + vx, my + vy, color=POS, sw=2))

    # Повільна молекула у відсіку А (синя), що летить ліворуч
    frags.append(circle(200, 270, 8, fill="#dbeafe", stroke=FIELD, sw=2))
    frags.append(arrow(200, 270, 190, 270, color=FIELD, sw=1.5))

    # Молекули у відсіку Б (повільні: сині, короткі стрілки)
    slow_mols = [
        (450, 110, 8, 5), (520, 190, -10, 6), (600, 120, 6, -8),
        (480, 260, 5, 10), (580, 240, -8, -5), (640, 210, 7, 7)
    ]
    for mx, my, vx, vy in slow_mols:
        frags.append(circle(mx, my, 8, fill="#dbeafe", stroke=FIELD, sw=2))
        frags.append(arrow(mx, my, mx + vx, my + vy, color=FIELD, sw=1.5))

    # Швидка молекула, що проходить крізь дверцята з Б до А
    frags.append(circle(mid_x + 10, door_top + 30, 8, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(arrow(mid_x + 10, door_top + 30, mid_x - 30, door_top + 30, color=POS, sw=2.5))
    frags.append(text(mid_x - 5, door_top + 50, "v > v_сер", size=11, color=POS, bold=True))

    # Нижня інформаційна плашка
    frags.append(textbox(w / 2, 380, "Результат: Т_А зростає, Т_Б спадає без зовнішньої роботи ⇒ ΔS_газу < 0", size=13, bold=True, fill="#fff7ed", stroke="#f97316", sw=1.5)[0])

    render(os.path.join(IMG_DIR, "maxwell-box.svg"), w, h, *frags)


def build_fig2_szilard_engine():
    """Фігура 2: Чотириетапний цикл одномолекулярного двигуна Сіларда."""
    w, h = 820, 440
    frags = []

    frags.append(text(w / 2, 26, "Чотириетапний термодинамічний цикл двигуна Сіларда (1929)", size=15, bold=True))

    col_w = 180
    gap = 15
    start_x = 25

    steps = [
        ("1. Вставляння", "Перегородка ділить\nоб'єм V навпіл.\nМолекула з одного боку.", "#f1f5f9", LINE),
        ("2. Вимірювання", "Демон реєструє:\nмолекула Ліворуч (L).\nПам'ять = 1 біт.", "#fef3c7", "#d97706"),
        ("3. Розширення", "Газ розширюється,\nвиконує роботу W = kT ln 2,\nпоглинає Q з теплостата.", "#dcfce7", POS),
        ("4. Стирання", "Стирання 1 біта\nпам'яті демона (0).\nQ_стирання = kT ln 2.", "#fee2e2", NEG)
    ]

    for i, (title, desc, bg_color, border_color) in enumerate(steps):
        cx = start_x + i * (col_w + gap)
        cy = 55
        ch = 330

        # Рамка етапу
        frags.append(rect(cx, cy, col_w, ch, fill="none", stroke=border_color, sw=1.5, rx=8))
        frags.append(rect(cx, cy, col_w, 35, fill=bg_color, stroke="none", rx=8))
        frags.append(rect(cx, cy + 20, col_w, 15, fill=bg_color, stroke="none"))
        frags.append(text(cx + col_w / 2, cy + 22, title, size=13, bold=True, color=border_color))
        frags.append(line(cx + 10, cy + 35, cx + col_w - 10, cy + 35, color=border_color, sw=1))

        # Малюнок циліндра на етапі
        cyl_x = cx + 20
        cyl_y = cy + 50
        cyl_w = col_w - 40
        cyl_h = 100
        frags.append(rect(cyl_x, cyl_y, cyl_w, cyl_h, fill="#ffffff", stroke=LINE, sw=1.5))

        if i == 0: # Вставляння
            frags.append(line(cyl_x + cyl_w / 2, cyl_y, cyl_x + cyl_w / 2, cyl_y + cyl_h, color=LINE, sw=2, dash="3,3"))
            frags.append(circle(cyl_x + 25, cyl_y + 50, 7, fill="#fee2e2", stroke=POS, sw=1.5))
        elif i == 1: # Вимірювання
            frags.append(line(cyl_x + cyl_w / 2, cyl_y, cyl_x + cyl_w / 2, cyl_y + cyl_h, color=LINE, sw=2))
            frags.append(circle(cyl_x + 25, cyl_y + 50, 7, fill="#fee2e2", stroke=POS, sw=1.5))
            frags.append(text(cyl_x + cyl_w / 2, cyl_y + 120, "Пам'ять: [ L ]", size=11, bold=True, color="#b45309"))
        elif i == 2: # Розширення
            frags.append(line(cyl_x + cyl_w - 20, cyl_y, cyl_x + cyl_w - 20, cyl_y + cyl_h, color=POS, sw=2.5))
            frags.append(arrow(cyl_x + 40, cyl_y + 50, cyl_x + cyl_w - 25, cyl_y + 50, color=POS, sw=2))
            frags.append(circle(cyl_x + 35, cyl_y + 50, 7, fill="#fee2e2", stroke=POS, sw=1.5))
            frags.append(text(cyl_x + cyl_w / 2, cyl_y + 120, "W = k_B T ln 2", size=11, bold=True, color=POS))
        elif i == 3: # Стирання
            frags.append(circle(cyl_x + cyl_w / 2, cyl_y + 50, 7, fill="#fee2e2", stroke=POS, sw=1.5))
            frags.append(arrow(cyl_x + cyl_w / 2, cyl_y + 115, cyl_x + cyl_w / 2, cyl_y + 135, color=NEG, sw=2))
            frags.append(text(cyl_x + cyl_w / 2, cyl_y + 145, "Q_виділ ≥ k_B T ln 2", size=10, bold=True, color=NEG))

        # Опис під циліндром
        frags.append(textbox(cx + col_w / 2, cy + 240, desc, size=11, fill="#ffffff", stroke=border_color, sw=1)[0])

    # Нижній висновок
    frags.append(textbox(w / 2, 410, "Сумарний баланс ентропії за весь цикл: ΔS_сумарна = ΔS_теплостата + ΔS_стирання = -k_B ln 2 + k_B ln 2 = 0", size=12, bold=True, fill="#f8fafc", stroke=LINE, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "szilard-engine.svg"), w, h, *frags)


def build_fig3_landauer_erasure():
    """Фігура 3: Потенціальний рельєф двоямної лунки та стирання інформації за Ландауером."""
    w, h = 780, 400
    frags = []

    frags.append(text(w / 2, 26, "Термодинаміка стирання 1 біта: стиснення фазового простору", size=15, bold=True))

    # Ліва частина: Стан пам'яті до стирання (дві рівноправні лунки 0 та 1)
    l_x, l_y, l_w, l_h = 40, 60, 330, 280
    frags.append(rect(l_x, l_y, l_w, l_h, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(l_x + l_w / 2, l_y + 25, "1. До стирання: 1 біт пам'яті (стан 0 або 1)", size=13, bold=True, color=LINE))
    
    pts_left = []
    for px in range(50):
        x_norm = (px - 25) / 12.0
        val = 0.25 * (x_norm ** 4) - 1.2 * (x_norm ** 2)
        py = l_y + 170 + val * 25
        pts_left.append((l_x + 40 + px * 5, py))
    
    for i in range(len(pts_left) - 1):
        frags.append(line(pts_left[i][0], pts_left[i][1], pts_left[i+1][0], pts_left[i+1][1], color=LINE, sw=2.5))

    frags.append(circle(l_x + 95, l_y + 140, 9, fill="#fef08a", stroke="#ca8a04", sw=2))
    frags.append(circle(l_x + 235, l_y + 140, 9, fill="#fef08a", stroke="#ca8a04", sw=2))
    frags.append(text(l_x + 95, l_y + 205, "Стан '0'", size=12, bold=True, color=LINE))
    frags.append(text(l_x + 235, l_y + 205, "Стан '1'", size=12, bold=True, color=LINE))
    frags.append(textbox(l_x + l_w / 2, l_y + 245, "Невизначеність: 2 мікростани (Ω = 2)\nЕнтропія пам'яті S_поч = k_B ln 2", size=11, fill="#fef3c7", stroke="#d97706", sw=1)[0])

    # Стрілка переходу посередині
    frags.append(arrow(l_x + l_w + 10, l_y + l_h / 2, l_x + l_w + 60, l_y + l_h / 2, color=NEG, sw=3))
    frags.append(text(l_x + l_w + 35, l_y + l_h / 2 - 15, "Стирання", size=12, bold=True, color=NEG))

    # Права частина: Стан після стирання
    r_x = l_x + l_w + 70
    r_y, r_w, r_h = l_y, l_w, l_h
    frags.append(rect(r_x, r_y, r_w, r_h, fill="#ffffff", stroke=NEG, sw=1.5, rx=8))
    frags.append(text(r_x + r_w / 2, r_y + 25, "2. Після стирання: фіксований стан '0'", size=13, bold=True, color=NEG))

    pts_right = []
    for px in range(50):
        x_norm = (px - 15) / 15.0
        val = 0.4 * (x_norm ** 2) + 0.3 * x_norm
        py = r_y + 140 + val * 30
        pts_right.append((r_x + 40 + px * 5, py))

    for i in range(len(pts_right) - 1):
        frags.append(line(pts_right[i][0], pts_right[i][1], pts_right[i+1][0], pts_right[i+1][1], color=NEG, sw=2.5))

    frags.append(circle(r_x + 85, r_y + 148, 9, fill="#fee2e2", stroke=NEG, sw=2))
    frags.append(text(r_x + 85, r_y + 205, "Фіксовано '0'", size=12, bold=True, color=NEG))
    frags.append(arrow(r_x + 235, r_y + 140, r_x + 105, r_y + 150, color=NEG, sw=2))
    frags.append(text(r_x + 210, r_y + 125, "стиснення фазового об'єму", size=11, color=NEG))

    frags.append(textbox(r_x + r_w / 2, r_y + 245, "Фіксований стан: 1 мікростан (Ω = 1)\nΔS_пам'яті = -k_B ln 2 ⇒ Q_тепло ≥ k_B T ln 2", size=11, fill="#fee2e2", stroke=NEG, sw=1)[0])

    # Загальний підпис знизу
    frags.append(textbox(w / 2, 375, "Принцип Ландауера (1961): стирання 1 біта зменшує ентропію носія на k_B ln 2 і скидає відповідне тепло в середовище.", size=12, bold=True, fill="#f8fafc", stroke=LINE, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "landauer-erasure.svg"), w, h, *frags)


def build_fig4_information_cycle():
    """Фігура 4: Схема потоків енергії та інформації в замкненій системі."""
    w, h = 800, 410
    frags = []

    frags.append(text(w / 2, 26, "Баланс потоків роботи, тепла та інформації між компонентами", size=15, bold=True))

    # Три головні блоки: Робоче тіло (Газ), Носій пам'яті (Демон), Тепловий резервуар (Термостат)
    gas_x, gas_y, gas_w, gas_h = 60, 70, 200, 130
    frags.append(rect(gas_x, gas_y, gas_w, gas_h, fill="#dcfce7", stroke=POS, sw=2, rx=8))
    frags.append(text(gas_x + gas_w / 2, gas_y + 30, "Робоче тіло (Газ)", size=14, bold=True, color=POS))
    frags.append(text(gas_x + gas_w / 2, gas_y + 65, "Вилучення роботи:\nW = k_B T ln 2", size=12, color=POS))
    frags.append(text(gas_x + gas_w / 2, gas_y + 100, "ΔS_газу = 0 (за цикл)", size=11, color=MUTED))

    mem_x, mem_y, mem_w, mem_h = 540, 70, 200, 130
    frags.append(rect(mem_x, mem_y, mem_w, mem_h, fill="#fef3c7", stroke="#d97706", sw=2, rx=8))
    frags.append(text(mem_x + mem_w / 2, mem_y + 30, "Пам'ять Демона", size=14, bold=True, color="#b45309"))
    frags.append(text(mem_x + mem_w / 2, mem_y + 65, "Накопичення: I = 1 біт\nСтирання: ΔS = -k_B ln 2", size=12, color="#b45309"))
    frags.append(text(mem_x + mem_w / 2, mem_y + 100, "ΔS_пам'яті = 0 (за цикл)", size=11, color=MUTED))

    bath_x, bath_y, bath_w, bath_h = 300, 240, 200, 110
    frags.append(rect(bath_x, bath_y, bath_w, bath_h, fill="#f1f5f9", stroke=LINE, sw=2, rx=8))
    frags.append(text(bath_x + bath_w / 2, bath_y + 30, "Тепловий резервуар (T)", size=14, bold=True, color=LINE))
    frags.append(text(bath_x + bath_w / 2, bath_y + 65, "Поглинає тепло Ландауера:\nQ_стирання ≥ k_B T ln 2", size=12, color=LINE))

    # Стрілка вимірювання (Інформаційний потік між Газом і Демоном)
    frags.append(arrow(gas_x + gas_w, gas_y + 40, mem_x, mem_y + 40, color="#b45309", sw=2.5))
    frags.append(text(gas_x + gas_w + 70, gas_y + 28, "1. Вимірювання (I = 1 біт)", size=11, bold=True, color="#b45309"))

    # Стрілка тепла від Термостата до Газу (для розширення)
    frags.append(arrow(bath_x + 30, bath_y, gas_x + gas_w / 2, gas_y + gas_h, color=POS, sw=2.5))
    frags.append(text(bath_x - 70, bath_y - 20, "2. Q_поглинуте = k_B T ln 2", size=11, bold=True, color=POS))

    # Стрілка розсіювання тепла Ландауера від Демона до Термостата
    frags.append(arrow(mem_x + mem_w / 2, mem_y + mem_h, bath_x + bath_w - 30, bath_y, color=NEG, sw=2.5))
    frags.append(text(bath_x + bath_w + 10, bath_y - 20, "3. Q_стирання ≥ k_B T ln 2", size=11, bold=True, color=NEG))

    # Загальний висновок
    frags.append(textbox(w / 2, 385, "Нерівність Сагави-Уеди: ⟨W⟩ ≤ -ΔF + k_B T · I. Інформація перетворюється на роботу, але її стирання компенсує ентропію.", size=12, bold=True, fill="#f8fafc", stroke=LINE, sw=1.5)[0])

    render(os.path.join(IMG_DIR, "information-cycle.svg"), w, h, *frags)


if __name__ == '__main__':
    build_fig1_maxwell_box()
    build_fig2_szilard_engine()
    build_fig3_landauer_erasure()
    build_fig4_information_cycle()
    print("Всі SVG-фігури успішно згенеровано у теку img/")
