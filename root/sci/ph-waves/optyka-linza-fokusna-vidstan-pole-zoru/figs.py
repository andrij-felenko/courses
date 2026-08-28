# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для теми:
Оптика: лінза, фокусна відстань, поле зору.
"""

import os
import sys

# Додаємо scripts/ до шляху пошуку модулів для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_thin_lens():
    """Фігура 1: Геометрія тонкої збиральної лінзи, головні промені, формування зображення."""
    w, h = 820, 420
    frags = []

    # Головна оптична вісь
    y_axis = 210
    frags.append(line(40, y_axis, 780, y_axis, color=MUTED, sw=1.5, dash="6,4"))
    frags.append(text(760, y_axis - 12, "Оптична вісь", size=11, color=MUTED, anchor="end"))

    # Тонка збиральна лінза (вертикальна лінія зі стрілками на кінцях)
    x_lens = 380
    frags.append(line(x_lens, 45, x_lens, 375, color=NEG, sw=2.5))
    # Стрілочки збиральної лінзи (нагорі та внизу)
    frags.append(line(x_lens - 12, 60, x_lens, 45, color=NEG, sw=2.5))
    frags.append(line(x_lens + 12, 60, x_lens, 45, color=NEG, sw=2.5))
    frags.append(line(x_lens - 12, 360, x_lens, 375, color=NEG, sw=2.5))
    frags.append(line(x_lens + 12, 360, x_lens, 375, color=NEG, sw=2.5))
    frags.append(text(x_lens, 35, "Тонка лінза", size=13, color=NEG, bold=True))

    # Оптичний центр O
    frags.append(circle(x_lens, y_axis, 4, fill=LINE, stroke=LINE))
    frags.append(text(x_lens + 12, y_axis + 18, "O", size=13, color=INK, bold=True))

    # Фокуси: f = 140 px
    f_px = 140
    x_f1 = x_lens - f_px  # 240
    x_f2 = x_lens + f_px  # 520
    x_2f1 = x_lens - 2 * f_px  # 100
    x_2f2 = x_lens + 2 * f_px  # 660

    # Позначки фокусів
    for x_pt, lbl in [(x_f1, "F₁"), (x_f2, "F₂"), (x_2f1, "2F₁"), (x_2f2, "2F₂")]:
        frags.append(line(x_pt, y_axis - 6, x_pt, y_axis + 6, color=LINE, sw=1.5))
        frags.append(circle(x_pt, y_axis, 3.5, fill=LINE, stroke=LINE))
        frags.append(text(x_pt, y_axis + 22, lbl, size=12, color=INK, bold=True))

    # Предмет (стрілка вгору): d_o = 260 px -> x_obj = 120 px, h_o = 90 px
    x_obj = 120
    y_obj_top = y_axis - 90  # 120
    frags.append(line(x_obj, y_axis, x_obj, y_obj_top, color=POS, sw=3))
    frags.append(line(x_obj - 7, y_obj_top + 12, x_obj, y_obj_top, color=POS, sw=3))
    frags.append(line(x_obj + 7, y_obj_top + 12, x_obj, y_obj_top, color=POS, sw=3))
    frags.append(text(x_obj - 20, y_obj_top + 45, "h_o", size=13, color=POS, bold=True))
    frags.append(text(x_obj, y_axis + 22, "A", size=12, color=POS, bold=True))
    frags.append(text(x_obj, y_obj_top - 10, "B", size=12, color=POS, bold=True))

    # Зображення: d_i = 303.33 px -> x_img = 683.33, h_i = 105 px
    d_i = 303.33
    x_img = x_lens + d_i  # 683.33
    h_img = 105.0
    y_img_bot = y_axis + h_img  # 315

    # Стрілка зображення (перевернута вниз)
    frags.append(line(x_img, y_axis, x_img, y_img_bot, color=FIELD, sw=3))
    frags.append(line(x_img - 7, y_img_bot - 12, x_img, y_img_bot, color=FIELD, sw=3))
    frags.append(line(x_img + 7, y_img_bot - 12, x_img, y_img_bot, color=FIELD, sw=3))
    frags.append(text(x_img + 22, y_img_bot - 45, "h_i", size=13, color=FIELD, bold=True))
    frags.append(text(x_img, y_axis - 12, "A'", size=12, color=FIELD, bold=True))
    frags.append(text(x_img, y_img_bot + 20, "B'", size=12, color=FIELD, bold=True))

    # Головні промені:
    # 1. Паралельний промінь: від B(120, 120) горизонтально до лінзи (380, 120), далі через фокус F₂(520, 210) до B'(683.33, 315)
    frags.append(line(x_obj, y_obj_top, x_lens, y_obj_top, color=POS, sw=1.8))
    frags.append(line(x_lens, y_obj_top, x_img, y_img_bot, color=POS, sw=1.8))
    # Стрілочка напрямку променя 1
    frags.append(line(240, y_obj_top - 5, 250, y_obj_top, color=POS, sw=1.8))
    frags.append(line(240, y_obj_top + 5, 250, y_obj_top, color=POS, sw=1.8))
    frags.append(line(595, 260, 605, 266, color=POS, sw=1.8))
    frags.append(line(597, 270, 605, 266, color=POS, sw=1.8))

    # 2. Центральний промінь: від B(120, 120) через O(380, 210) напряму до B'(683.33, 315)
    frags.append(line(x_obj, y_obj_top, x_img, y_img_bot, color="#d97706", sw=1.8))
    # Стрілочка напрямку променя 2
    frags.append(line(250, 160, 258, 168, color="#d97706", sw=1.8))
    frags.append(line(248, 170, 258, 168, color="#d97706", sw=1.8))

    # 3. Фокальний промінь: від B(120, 120) через F₁(240, 210) до лінзи (380, 315), далі горизонтально до B'(683.33, 315)
    frags.append(line(x_obj, y_obj_top, x_lens, y_img_bot, color=NEG, sw=1.8))
    frags.append(line(x_lens, y_img_bot, x_img, y_img_bot, color=NEG, sw=1.8))
    # Стрілочка напрямку променя 3
    frags.append(line(520, y_img_bot - 5, 530, y_img_bot, color=NEG, sw=1.8))
    frags.append(line(520, y_img_bot + 5, 530, y_img_bot, color=NEG, sw=1.8))

    # Розмірні лінії знизу:
    y_dim1 = 370
    frags.append(line(x_obj, y_axis + 30, x_obj, y_dim1 + 10, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(x_lens, y_axis + 30, x_lens, y_dim1 + 10, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(x_obj, y_dim1, x_lens, y_dim1, color=INK, sw=1.2))
    frags.append(line(x_obj, y_dim1 - 4, x_obj, y_dim1 + 4, color=INK, sw=1.2))
    frags.append(line(x_lens, y_dim1 - 4, x_lens, y_dim1 + 4, color=INK, sw=1.2))
    frags.append(text((x_obj + x_lens) / 2, y_dim1 - 6, "d_o (відстань до предмета)", size=11, color=INK))

    # d_i: від x_lens(380) до x_img(683.33) на рівні y = 370
    frags.append(line(x_img, y_img_bot + 25, x_img, y_dim1 + 10, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(x_lens, y_dim1, x_img, y_dim1, color=INK, sw=1.2))
    frags.append(line(x_img, y_dim1 - 4, x_img, y_dim1 + 4, color=INK, sw=1.2))
    frags.append(text((x_lens + x_img) / 2, y_dim1 - 6, "d_i (відстань до зображення)", size=11, color=INK))

    # Фокусна відстань f (зверху): від x_lens(380) до x_f2(520) на рівні y = 80
    y_dim_f = 80
    frags.append(line(x_lens, y_dim_f, x_f2, y_dim_f, color=NEG, sw=1.2))
    frags.append(line(x_lens, y_dim_f - 4, x_lens, y_dim_f + 4, color=NEG, sw=1.2))
    frags.append(line(x_f2, y_dim_f - 4, x_f2, y_dim_f + 4, color=NEG, sw=1.2))
    frags.append(text((x_lens + x_f2) / 2, y_dim_f - 6, "f (фокусна відстань)", size=11, color=NEG, bold=True))

    return render(os.path.join(IMG_DIR, "thin-lens-geometry.svg"), w, h, *frags)


def fig_lensmaker_surfaces():
    """Фігура 2: Заломлення на двох сферичних поверхнях лінзи (формула шліфувальника)."""
    w, h = 800, 360
    frags = []

    y_axis = 180
    frags.append(line(40, y_axis, 760, y_axis, color=MUTED, sw=1.5, dash="6,4"))
    frags.append(text(740, y_axis - 12, "Оптична вісь", size=11, color=MUTED, anchor="end"))

    # Тіло лінзи
    lens_path = (
        '<path d="M 400 60 '
        'A 180 180 0 0 1 430 180 '
        'A 180 180 0 0 1 400 300 '
        'A 180 180 0 0 1 370 180 '
        'A 180 180 0 0 1 400 60 Z" '
        'fill="#e0f2fe" stroke="%s" stroke-width="2.5"/>' % NEG
    )
    frags.append(lens_path)

    # Показник заломлення всередині
    box_n = fitbox(365, 120, 70, 32, "n (скло)", size=12, color=NEG, bold=True, fill="#ffffff", stroke=NEG)
    frags.append(box_n)
    frags.append(text(200, 100, "n_med = 1 (повітря)", size=12, color=MUTED))
    frags.append(text(600, 100, "n_med = 1 (повітря)", size=12, color=MUTED))

    # Центри кривини C1 та C2
    x_c1 = 570
    x_c2 = 230
    frags.append(circle(x_c1, y_axis, 4, fill=POS, stroke=POS))
    frags.append(text(x_c1, y_axis + 22, "C₁ (для поверхні 1)", size=11, color=POS, bold=True))

    frags.append(circle(x_c2, y_axis, 4, fill=NEG, stroke=NEG))
    frags.append(text(x_c2, y_axis + 22, "C₂ (для поверхні 2)", size=11, color=NEG, bold=True))

    # Вершини поверхонь
    x_v1 = 370
    x_v2 = 430
    frags.append(circle(x_v1, y_axis, 3, fill=LINE, stroke=LINE))
    frags.append(text(x_v1 - 14, y_axis + 18, "V₁", size=11, color=INK, bold=True))
    frags.append(circle(x_v2, y_axis, 3, fill=LINE, stroke=LINE))
    frags.append(text(x_v2 + 14, y_axis + 18, "V₂", size=11, color=INK, bold=True))

    # Радіуси кривини R1 та R2 стрілками
    frags.append(arrow(x_c1, y_axis - 50, x_v1 + 10, y_axis - 50, color=POS, sw=1.5))
    frags.append(line(x_v1 + 10, y_axis - 55, x_v1 + 10, y_axis - 45, color=POS, sw=1.5))
    frags.append(line(x_c1, y_axis - 55, x_c1, y_axis - 45, color=POS, sw=1.5))
    frags.append(text((x_v1 + x_c1) / 2, y_axis - 60, "R₁ > 0 (радіус передньої поверхні)", size=11, color=POS, bold=True))

    frags.append(arrow(x_c2, y_axis + 75, x_v2 - 10, y_axis + 75, color=NEG, sw=1.5))
    frags.append(line(x_v2 - 10, y_axis + 70, x_v2 - 10, y_axis + 80, color=NEG, sw=1.5))
    frags.append(line(x_c2, y_axis + 70, x_c2, y_axis + 80, color=NEG, sw=1.5))
    frags.append(text((x_c2 + x_v2) / 2, y_axis + 95, "R₂ < 0 (радіус задньої поверхні)", size=11, color=NEG, bold=True))

    # Товщина d / t
    frags.append(line(x_v1, 305, x_v2, 305, color=LINE, sw=1.2))
    frags.append(line(x_v1, 300, x_v1, 310, color=LINE, sw=1.2))
    frags.append(line(x_v2, 300, x_v2, 310, color=LINE, sw=1.2))
    frags.append(text((x_v1 + x_v2) / 2, 325, "d (товщина)", size=11, color=LINE))

    return render(os.path.join(IMG_DIR, "lensmaker-surfaces.svg"), w, h, *frags)


def fig_sensor_fov():
    """Фігура 3: Кутове поле зору FOV, фокусна відстань, розмір сенсора та робоча дистанція."""
    w, h = 820, 380
    frags = []

    y_axis = 190

    # Оптична вісь
    frags.append(line(50, y_axis, 770, y_axis, color=MUTED, sw=1.5, dash="6,4"))

    # Об'єктив (лінза): x = 320
    x_lens = 320
    frags.append(line(x_lens, 80, x_lens, 300, color=NEG, sw=2.5))
    frags.append(line(x_lens - 10, 95, x_lens, 80, color=NEG, sw=2.5))
    frags.append(line(x_lens + 10, 95, x_lens, 80, color=NEG, sw=2.5))
    frags.append(line(x_lens - 10, 285, x_lens, 300, color=NEG, sw=2.5))
    frags.append(line(x_lens + 10, 285, x_lens, 300, color=NEG, sw=2.5))
    frags.append(text(x_lens, 65, "Об'єктив", size=13, color=NEG, bold=True))

    # Площина матриці сенсора ліворуч (у фокальній площині): x_sensor = 160, f = 160 px
    x_sensor = 160
    h_sensor = 100  # розмір d (висота/ширина)
    y_s_top = y_axis - h_sensor / 2  # 140
    y_s_bot = y_axis + h_sensor / 2  # 240

    frags.append(rect(x_sensor - 8, y_s_top, 8, h_sensor, fill="#374151", stroke="#111827", sw=1.5, rx=2))
    frags.append(text(x_sensor - 18, y_axis - 60, "Сенсор", size=12, color=INK, bold=True, anchor="end"))
    frags.append(text(x_sensor - 18, y_axis - 42, "(матриця)", size=11, color=MUTED, anchor="end"))

    # Розмір сенсора d
    frags.append(line(x_sensor - 16, y_s_top, x_sensor - 16, y_s_bot, color=POS, sw=1.5))
    frags.append(line(x_sensor - 20, y_s_top, x_sensor - 12, y_s_top, color=POS, sw=1.5))
    frags.append(line(x_sensor - 20, y_s_bot, x_sensor - 12, y_s_bot, color=POS, sw=1.5))
    frags.append(text(x_sensor - 28, y_axis + 4, "d", size=13, color=POS, bold=True, anchor="end"))

    # Фокусна відстань f
    y_dim_f = 330
    frags.append(line(x_sensor, y_axis + 60, x_sensor, y_dim_f + 10, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(x_lens, y_axis + 115, x_lens, y_dim_f + 10, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(x_sensor, y_dim_f, x_lens, y_dim_f, color=NEG, sw=1.5))
    frags.append(line(x_sensor, y_dim_f - 4, x_sensor, y_dim_f + 4, color=NEG, sw=1.5))
    frags.append(line(x_lens, y_dim_f - 4, x_lens, y_dim_f + 4, color=NEG, sw=1.5))
    frags.append(text((x_sensor + x_lens) / 2, y_dim_f - 8, "f (фокусна відстань)", size=12, color=NEG, bold=True))

    # Об'єкт / зона огляду на відстані WD (робоча відстань): x_target = 720 px
    x_target = 720
    y_t_top = y_axis - 125  # 65
    y_t_bot = y_axis + 125  # 315

    # Промені конуса зору
    frags.append(line(x_sensor, y_s_top, x_target, y_t_bot, color=POS, sw=1.8))
    frags.append(line(x_sensor, y_s_bot, x_target, y_t_top, color=POS, sw=1.8))

    # Площина об'єкта (зони огляду)
    frags.append(line(x_target, y_t_top, x_target, y_t_bot, color=FIELD, sw=3))
    frags.append(line(x_target - 8, y_t_top, x_target + 8, y_t_top, color=FIELD, sw=2))
    frags.append(line(x_target - 8, y_t_bot, x_target + 8, y_t_bot, color=FIELD, sw=2))
    frags.append(text(x_target + 14, y_axis, "Поле огляду (FOV size: W)", size=12, color=FIELD, bold=True, anchor="start"))

    # Дуги кута FOV
    fov_arc_right = '<path d="M 390 168 A 70 70 0 0 1 390 212" fill="none" stroke="%s" stroke-width="1.8"/>' % POS
    fov_arc_left = '<path d="M 250 168 A 70 70 0 0 1 250 212" fill="none" stroke="%s" stroke-width="1.8"/>' % POS
    frags.append(fov_arc_right)
    frags.append(fov_arc_left)
    frags.append(text(415, y_axis + 4, "FOV (θ)", size=12, color=POS, bold=True))

    # Робоча дистанція WD
    y_dim_wd = 330
    frags.append(line(x_target, y_t_bot + 10, x_target, y_dim_wd + 10, color=MUTED, sw=1, dash="3,3"))
    frags.append(line(x_lens, y_dim_wd, x_target, y_dim_wd, color=INK, sw=1.5))
    frags.append(line(x_target, y_dim_wd - 4, x_target, y_dim_wd + 4, color=INK, sw=1.5))
    frags.append(text((x_lens + x_target) / 2, y_dim_wd - 8, "WD (робоча відстань до об'єкта)", size=12, color=INK, bold=True))

    return render(os.path.join(IMG_DIR, "sensor-fov-geometry.svg"), w, h, *frags)


def fig_sensor_formats():
    """Фігура 4: Співвідношення типових оптичних форматів матриць сенсорів (1/4" до Full Frame)."""
    w, h = 820, 360
    frags = []

    x0, y0 = 60, 60

    formats = [
        ("Full Frame (35 мм)", 360, 240, "#1e293b", "#f8fafc", "36.0 × 24.0 мм (diag 43.3 мм, Crop 1.0×)"),
        ("APS-C (Sony/Nikon)", 235, 156, "#2563eb", "#eff6ff", "23.5 × 15.6 мм (diag 28.2 мм, Crop 1.5×)"),
        ('1" (Type 1.0)', 132, 88, "#059669", "#ecfdf5", "13.2 × 8.8 мм (diag 15.9 мм, Crop 2.7×)"),
        ('1/1.8"', 72, 53, "#d97706", "#fffbeb", "7.18 × 5.32 мм (diag 8.9 мм, Crop 4.8×)"),
        ('1/2.8"', 52, 39, "#dc2626", "#fef2f2", "5.18 × 3.89 мм (diag 6.5 мм, Crop 6.7×)"),
        ('1/4"', 32, 24, "#7c3aed", "#f5f3ff", "3.20 × 2.40 мм (diag 4.0 мм, Crop 10.8×)"),
    ]

    # Малюємо прямокутники від найбільшого до найменшого
    for name, fw, fh, stroke_col, fill_col, spec in formats:
        frags.append(rect(x0, y0, fw, fh, fill=fill_col, stroke=stroke_col, sw=1.8, rx=3))

    # Легенда / підписи праворуч
    x_leg = 450
    y_leg_start = 75
    dy_leg = 42

    for i, (name, fw, fh, stroke_col, fill_col, spec) in enumerate(formats):
        y_item = y_leg_start + i * dy_leg
        frags.append(rect(x_leg, y_item - 10, 16, 16, fill=fill_col, stroke=stroke_col, sw=1.8, rx=2))
        frags.append(text(x_leg + 26, y_item + 3, name, size=13, color=INK, bold=True, anchor="start"))
        frags.append(text(x_leg + 180, y_item + 3, spec, size=11, color=MUTED, anchor="start"))

    return render(os.path.join(IMG_DIR, "sensor-formats-comparison.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_thin_lens()
    fig_lensmaker_surfaces()
    fig_sensor_fov()
    fig_sensor_formats()
    print("Всі фігури успішно згенеровано.")
