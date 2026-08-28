#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми «Калібрування компаса на зібраному апараті».
Вивід у ./img/. Запуск: python figs.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

def dashed_circle(cx, cy, r, fill="none", stroke=LINE, sw=1.5, dash="4,3"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))

def dashed_ellipse(cx, cy, rx, ry, angle=0, fill="none", stroke=LINE, sw=1.5, dash="4,3"):
    transform = f' transform="rotate({angle} {cx} {cy})"' if angle != 0 else ''
    return ('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"%s/>' % (cx, cy, rx, ry, fill, stroke, sw, dash, transform))

def gen_hard_soft_iron(fpath):
    """Фігура 1: hard-soft-iron-geometry.svg — Геометрія спотворень: ідеальна сфера, зсунутий еліпсоїд та відновлення сфери."""
    w, h = 880, 420
    frags = []

    # Головний заголовок
    frags.append(text(w / 2, 26, "Геометрія калібрування магнітометра: сфера, еліпсоїд і відновлення поля", size=16, bold=True))

    # Панель 1: Ідеальний сенсор
    p1_x, p1_y, p1_w, p1_h = 20, 48, 265, 352
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(p1_x + p1_w / 2, p1_y + 24, "1. Ідеальний магнітометр", size=13, bold=True, color="#0f172a"))
    frags.append(text(p1_x + p1_w / 2, p1_y + 42, "Поза металом: чиста сфера", size=11, color=MUTED))

    # Вісь і сфера
    c1_x, c1_y = p1_x + p1_w / 2, p1_y + 155
    r_sphere = 65
    frags.append(line(c1_x - 90, c1_y, c1_x + 90, c1_y, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(c1_x, c1_y - 90, c1_x, c1_y + 90, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(circle(c1_x, c1_y, r_sphere, fill="#f0fdf4", stroke=FIELD, sw=2.0))
    frags.append(circle(c1_x, c1_y, 3.5, fill=INK, stroke=INK, sw=1.0))
    frags.append(text(c1_x + 8, c1_y + 14, "(0,0)", size=10, color=MUTED, anchor="start"))

    # Вектор B_earth
    frags.append(arrow(c1_x, c1_y, c1_x + 46, c1_y - 46, color=FIELD, sw=2.0))
    frags.append(text(c1_x + 28, c1_y - 32, "‖B‖ = B_earth", size=11, bold=True, color=FIELD, anchor="start"))

    tb1, _, _ = textbox(p1_x + p1_w / 2, p1_y + 285, "Центр у нулі (0, 0, 0)\nУсі радіуси однакові\n‖B_raw‖ = const ≈ 45 мкТл", size=11, pad=6, fill="#ffffff", stroke="#cbd5e1")
    frags.append(tb1)

    # Панель 2: Спотворення на зібраному апараті
    p2_x, p2_y, p2_w, p2_h = 305, 48, 270, 352
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fff7ed", stroke="#fdba74", sw=1.2, rx=8))
    frags.append(text(p2_x + p2_w / 2, p2_y + 24, "2. На зібраному дроні", size=13, bold=True, color="#9a3412"))
    frags.append(text(p2_x + p2_w / 2, p2_y + 42, "Hard + Soft Iron спотворення", size=11, color=MUTED))

    # Вісь і зсунутий еліпсоїд
    c2_x, c2_y = p2_x + p2_w / 2, p2_y + 155
    frags.append(line(c2_x - 95, c2_y, c2_x + 95, c2_y, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(c2_x, c2_y - 90, c2_x, c2_y + 90, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(circle(c2_x, c2_y, 3.0, fill="#64748b", stroke="#64748b", sw=1.0))
    frags.append(text(c2_x + 6, c2_y + 13, "(0,0)", size=10, color=MUTED, anchor="start"))

    # Зсув Hard Iron
    v0_x, v0_y = c2_x + 28, c2_y - 20
    frags.append(arrow(c2_x, c2_y, v0_x, v0_y, color=POS, sw=2.0))
    frags.append(text(c2_x + 14, c2_y - 18, "V₀", size=11, bold=True, color=POS, anchor="end"))
    frags.append(circle(v0_x, v0_y, 3.5, fill=POS, stroke=POS, sw=1.0))

    # Еліпсоїд Soft Iron
    frags.append(dashed_ellipse(v0_x, v0_y, 75, 48, angle=-25, fill="#ffedd5", stroke=POS, sw=2.0, dash="none"))
    frags.append(text(v0_x + 40, v0_y - 30, "Еліпсоїд", size=11, bold=True, color=POS))

    tb2, _, _ = textbox(p2_x + p2_w / 2, p2_y + 285, "Зсув центру: Hard Iron V₀\nСтиснення й поворот осей:\nSoft Iron матриця A_soft", size=11, pad=6, fill="#ffffff", stroke="#fdba74")
    frags.append(tb2)

    # Панель 3: Відновлення калібруванням
    p3_x, p3_y, p3_w, p3_h = 595, 48, 265, 352
    frags.append(rect(p3_x, p3_y, p3_w, p3_h, fill="#eff6ff", stroke="#93c5fd", sw=1.2, rx=8))
    frags.append(text(p3_x + p3_w / 2, p3_y + 24, "3. Після калібрування", size=13, bold=True, color="#1e40af"))
    frags.append(text(p3_x + p3_w / 2, p3_y + 42, "B_cal = W · (B_raw − V₀)", size=11, color=MUTED))

    # Вісь і відкалібрована сфера
    c3_x, c3_y = p3_x + p3_w / 2, p3_y + 155
    frags.append(line(c3_x - 90, c3_y, c3_x + 90, c3_y, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(line(c3_x, c3_y - 90, c3_x, c3_y + 90, color="#94a3b8", sw=1.0, dash="3,3"))
    frags.append(circle(c3_x, c3_y, r_sphere, fill="#dbeafe", stroke=NEG, sw=2.0))
    frags.append(circle(c3_x, c3_y, 3.5, fill=NEG, stroke=NEG, sw=1.0))
    frags.append(text(c3_x + 8, c3_y + 14, "(0,0)", size=10, color=MUTED, anchor="start"))

    frags.append(arrow(c3_x, c3_y, c3_x + 46, c3_y + 46, color=NEG, sw=2.0))
    frags.append(text(c3_x + 24, c3_y + 40, "‖B_cal‖ = B_earth", size=11, bold=True, color=NEG, anchor="start"))

    tb3, _, _ = textbox(p3_x + p3_w / 2, p3_y + 285, "1. Зсув повернено в нуль\n2. Осі вирівняно й масштабовано\nПовна сфера без азимутальних похибок", size=11, pad=6, fill="#ffffff", stroke="#93c5fd")
    frags.append(tb3)

    return render(fpath, w, h, *frags)

def gen_rotation_coverage(fpath):
    """Фігура 2: drone-dance-rotation-coverage.svg — 6-осьове обертання та просторове покриття сфери вимірів."""
    w, h = 860, 430
    frags = []

    frags.append(text(w / 2, 26, "Процедура 6-осьового обертання та просторове покриття сфери (Spatial Binning)", size=16, bold=True))

    # Ліва панель: 6 базових орієнтацій
    p1_x, p1_y, p1_w, p1_h = 20, 50, 400, 360
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fafbfc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(p1_x + p1_w / 2, p1_y + 24, "6 базових орієнтацій («танець із дроном»)", size=13, bold=True, color="#0f172a"))
    frags.append(text(p1_x + p1_w / 2, p1_y + 42, "Плавне обертання навколо кожної осі (ω < 60°/с)", size=11, color=MUTED))

    # 6 комірок рухів
    poses = [
        ("1. Горизонт (Up)", "Обертання за/проти курсу", p1_x + 20, p1_y + 60, 170, 75),
        ("2. Ніс униз (Nose Down)", "Обертання навколо осі X", p1_x + 210, p1_y + 60, 170, 75),
        ("3. Ніс угору (Nose Up)", "Обертання для нижньої півсфери", p1_x + 20, p1_y + 150, 170, 75),
        ("4. Лівий борт (Left Side)", "Обертання навколо осі Y", p1_x + 210, p1_y + 150, 170, 75),
        ("5. Правий борт (Right Side)", "Покриття бічних секторів", p1_x + 20, p1_y + 240, 170, 75),
        ("6. Догори дном (Inverted)", "Замикання верхнього купола", p1_x + 210, p1_y + 240, 170, 75),
    ]

    for title_txt, sub_txt, px, py, pw, ph in poses:
        frags.append(rect(px, py, pw, ph, fill="#ffffff", stroke="#e2e8f0", sw=1.0, rx=6))
        frags.append(circle(px + 18, py + 22, 6, fill=FIELD, stroke=FIELD, sw=1.0))
        frags.append(text(px + 32, py + 26, title_txt, size=11, bold=True, color="#1e293b", anchor="start"))
        frags.append(text(px + 32, py + 48, sub_txt, size=10, color=MUTED, anchor="start"))

    tb_rule, _, _ = textbox(p1_x + p1_w / 2, p1_y + 338, "Критерій: рівномірна кутова швидкість без ривків\nВиконувати просто неба далеко від залізобетону й авто", size=10, pad=5, fill="#f1f5f9", stroke="#cbd5e1")
    frags.append(tb_rule)

    # Права панель: Просторове розбиття (Spatial Binning)
    p2_x, p2_y, p2_w, p2_h = 440, 50, 400, 360
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fafbfc", stroke="#cbd5e1", sw=1.2, rx=8))
    frags.append(text(p2_x + p2_w / 2, p2_y + 24, "Просторове розбиття сфери (72 сектори)", size=13, bold=True, color="#0f172a"))
    frags.append(text(p2_x + p2_w / 2, p2_y + 42, "Контроль повноти зібраної хмари точок", size=11, color=MUTED))

    # Сферична сітка (аксонометрія)
    sc_x, sc_y = p2_x + p2_w / 2, p2_y + 165
    sr = 75
    frags.append(circle(sc_x, sc_y, sr, fill="#f8fafc", stroke="#94a3b8", sw=1.5))
    frags.append(dashed_ellipse(sc_x, sc_y, sr, 26, fill="none", stroke="#cbd5e1", sw=1.0, dash="3,3"))
    frags.append(dashed_ellipse(sc_x, sc_y, 26, sr, fill="none", stroke="#cbd5e1", sw=1.0, dash="3,3"))
    frags.append(line(sc_x - sr - 15, sc_y, sc_x + sr + 15, sc_y, color="#94a3b8", sw=1.0, dash="2,2"))
    frags.append(line(sc_x, sc_y - sr - 15, sc_x, sc_y + sr + 15, color="#94a3b8", sw=1.0, dash="2,2"))

    # Точки хмари вимірів
    points = [
        (-45, -30), (-25, -50), (20, -55), (45, -25), (60, 10), (35, 40),
        (-20, 55), (-55, 30), (-10, -15), (25, 10), (-35, 15), (10, -40),
        (50, 45), (-40, -45), (15, 50), (-60, -5), (40, -45), (0, 0)
    ]
    for dx, dy in points:
        frags.append(circle(sc_x + dx, sc_y + dy, 3.0, fill=POS, stroke=POS, sw=0.8))

    frags.append(text(sc_x + 55, sc_y - 65, "Покриття > 85%", size=11, bold=True, color=FIELD))

    tb_bin, _, _ = textbox(p2_x + p2_w / 2, p2_y + 300, "1. Сфера розбивається на N рівновеликих комірок\n2. У кожну комірку приймається обмежена кількість точок\n3. Захист від зміщення ваги у бік однієї площини", size=10.5, pad=6, fill="#ffffff", stroke="#cbd5e1")
    frags.append(tb_bin)

    return render(fpath, w, h, *frags)

def gen_calibration_pipeline(fpath):
    """Фігура 3: compass-calibration-pipeline.svg — Повний конвеєр калібрування та оцінки придатності."""
    w, h = 860, 360
    frags = []

    frags.append(text(w / 2, 26, "Конвеєр цифрової обробки та валідації калібрування магнітометра", size=16, bold=True))

    blocks = [
        ("1. Сирі виміри", "I2C/SPI @ 50–100 Гц\nB_raw = [x, y, z]ᵀ\nТемпературний дрейф", 90, 110, 140, 95, "#f1f5f9", "#cbd5e1", INK),
        ("2. Просторова фільтрація", "Spatial Binning (72 комірки)\nВідсіювання викидів (3σ)\nДетектор руху (ω < limit)", 265, 110, 175, 95, "#e0f2fe", "#7dd3fc", "#0369a1"),
        ("3. Оптимізація", "Алгебраїчний старт (Ферше)\n+ Нелінійний LM-спуск\nМінімізація нев'язки радіуса", 475, 110, 185, 95, "#fef3c7", "#fcd34d", "#b45309"),
        ("4. Валідація", "RMS похибка < 2.5 мкТл\nЗумовленість cond(W) < 2.5\nЗвірка з моделлю WMM", 700, 110, 180, 95, "#dcfce7", "#86efac", "#15803d"),
    ]

    for b_title, b_desc, cx, cy, bw, bh, bfill, bstroke, bcolor in blocks:
        frags.append(rect(cx - bw/2, cy - bh/2, bw, bh, fill=bfill, stroke=bstroke, sw=1.5, rx=6))
        frags.append(text(cx, cy - bh/2 + 20, b_title, size=12, bold=True, color=bcolor))
        lines = b_desc.split("\n")
        for idx, ln in enumerate(lines):
            frags.append(text(cx, cy - bh/2 + 42 + idx * 17, ln, size=10.5, color=INK))

    # Стрілки між блоками
    frags.append(arrow(160, 110, 177, 110, color="#64748b", sw=2.0))
    frags.append(arrow(352, 110, 382, 110, color="#64748b", sw=2.0))
    frags.append(arrow(567, 110, 610, 110, color="#64748b", sw=2.0))

    # Нижні гілки: Успіх / Відхилення
    # Успіх -> EEPROM
    frags.append(arrow(700, 157, 700, 220, color=FIELD, sw=2.0))
    tb_ok, _, _ = textbox(700, 265, "Калібрування УСПІШНЕ\nЗапис V₀ та W у Flash/EEPROM\nГотовність до Arming (EKF OK)", size=11, pad=6, fill="#f0fdf4", stroke=FIELD, bold=True, color=FIELD)
    frags.append(tb_ok)

    # Помилка -> Повтор
    frags.append(arrow(700, 157, 700, 195, color=POS, sw=1.5))
    frags.append(line(700, 195, 475, 195, color=POS, sw=1.5, dash="3,3"))
    frags.append(arrow(475, 195, 475, 157, color=POS, sw=1.5))
    frags.append(text(585, 210, "RMS > 3.0 мкТл (повторити обертання)", size=10, bold=True, color=POS))

    # Реальний час польоту
    tb_rt, _, _ = textbox(270, 265, "Під час польоту (In-Flight EKF):\nКорекція заліза за супутниковим вектором GNSS\nКомпенсація тяги: B_mot = K_curr · I_batt", size=10.5, pad=6, fill="#f8fafc", stroke="#cbd5e1")
    frags.append(tb_rt)
    frags.append(arrow(270, 215, 270, 157, color="#64748b", sw=1.5))

    return render(fpath, w, h, *frags)

def main():
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)

    figs = [
        ("hard-soft-iron-geometry.svg", gen_hard_soft_iron),
        ("drone-dance-rotation-coverage.svg", gen_rotation_coverage),
        ("compass-calibration-pipeline.svg", gen_calibration_pipeline),
    ]

    for fname, generator in figs:
        fpath = os.path.join(img_dir, fname)
        generator(fpath)
        print(f"Згенеровано: {fpath}")

if __name__ == "__main__":
    main()
