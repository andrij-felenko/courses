#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми «Компас проти силового дроту».
Вивід у ./img/. Запуск: python figs.py
"""

import sys
import os

# Підключення svgkit із кореня репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import (
    render, text, mtext, rect, line, arrow, circle, textbox, fitbox,
    POS, NEG, FIELD, INK, MUTED, LINE, FILL, BG
)

def dashed_circle(cx, cy, r, fill="none", stroke=LINE, sw=1.5, dash="4,3"):
    return ('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" stroke="%s" '
            'stroke-width="%.1f" stroke-dasharray="%s"/>' % (cx, cy, r, fill, stroke, sw, dash))

def gen_biot_savart():
    """Фігура 1: biot-savart-field.svg — Порівняння полів: одиночний провідник, паралельні дроти, вита пара."""
    w, h = 840, 390
    frags = []

    # Заголовок панелей
    frags.append(text(w / 2, 28, "Магнітне поле струму: одиночний дріт, паралельна пара та вита пара", size=16, bold=True))

    # Панель 1: Одиночний дріт (B ~ 1/r)
    p1_x, p1_y, p1_w, p1_h = 20, 50, 250, 320
    frags.append(rect(p1_x, p1_y, p1_w, p1_h, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(p1_x + p1_w / 2, p1_y + 24, "Одиночний провідник", size=14, bold=True, color=POS))
    frags.append(text(p1_x + p1_w / 2, p1_y + 44, "Спадання поля: B ~ 1/r", size=12, color=MUTED))

    # Струм (червона точка в центрі, струм на нас)
    c1_x, c1_y = p1_x + p1_w / 2, p1_y + 140
    frags.append(circle(c1_x, c1_y, 16, fill="#fdecea", stroke=POS, sw=2))
    frags.append(circle(c1_x, c1_y, 4, fill=POS, stroke=POS, sw=1))
    frags.append(text(c1_x, c1_y + 32, "I = 100 A", size=12, bold=True, color=POS))

    # Концентричні кола магнітного поля
    for r_c, dash in [(38, "4,3"), (62, "4,3"), (88, "4,3")]:
        frags.append(dashed_circle(c1_x, c1_y, r_c, fill="none", stroke=FIELD, sw=1.5, dash=dash))
    # Стрілка напрямку поля (проти годинникової)
    frags.append(arrow(c1_x - 62, c1_y + 5, c1_x - 62, c1_y - 15, color=FIELD, sw=1.8))
    frags.append(arrow(c1_x + 62, c1_y - 5, c1_x + 62, c1_y + 15, color=FIELD, sw=1.8))

    tb1, _, _ = textbox(p1_x + p1_w / 2, p1_y + 270, "r = 3 см  ->  B = 667 мкТл\nr = 10 см ->  B = 200 мкТл\n(Поле Землі ~ 45 мкТл)", size=11, pad=6, fill="#ffffff", stroke="#d1d5db")
    frags.append(tb1)

    # Панель 2: Паралельні дроти (диполь B ~ 1/r^2)
    p2_x, p2_y, p2_w, p2_h = 295, 50, 250, 320
    frags.append(rect(p2_x, p2_y, p2_w, p2_h, fill="#fafbfc", stroke="#d1d5db", sw=1.2, rx=8))
    frags.append(text(p2_x + p2_w / 2, p2_y + 24, "Паралельні дроти (+ / -)", size=14, bold=True, color="#d97706"))
    frags.append(text(p2_x + p2_w / 2, p2_y + 44, "Спадання вдалині: B ~ d / r²", size=12, color=MUTED))

    # Дроти +I та -I
    c2_y = p2_y + 140
    w_plus_x = p2_x + p2_w / 2 - 28
    w_minus_x = p2_x + p2_w / 2 + 28
    frags.append(circle(w_plus_x, c2_y, 14, fill="#fdecea", stroke=POS, sw=2))
    frags.append(circle(w_plus_x, c2_y, 3.5, fill=POS, stroke=POS, sw=1))
    frags.append(text(w_plus_x, c2_y + 28, "+I", size=11, bold=True, color=POS))

    frags.append(circle(w_minus_x, c2_y, 14, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(line(w_minus_x - 5, c2_y - 5, w_minus_x + 5, c2_y + 5, color=NEG, sw=2))
    frags.append(line(w_minus_x - 5, c2_y + 5, w_minus_x + 5, c2_y - 5, color=NEG, sw=2))
    frags.append(text(w_minus_x, c2_y + 28, "−I", size=11, bold=True, color=NEG))

    # Лінія відстані між провідниками d
    frags.append(line(w_plus_x, c2_y - 24, w_minus_x, c2_y - 24, color=MUTED, sw=1, dash="2,2"))
    frags.append(text(p2_x + p2_w / 2, c2_y - 30, "зазор d = 6 мм", size=10, color=MUTED))

    # Лінії дипольного поля
    frags.append(dashed_circle(w_plus_x, c2_y, 25, fill="none", stroke=FIELD, sw=1.2, dash="3,2"))
    frags.append(dashed_circle(w_minus_x, c2_y, 25, fill="none", stroke=FIELD, sw=1.2, dash="3,2"))
    frags.append(dashed_circle(p2_x + p2_w / 2, c2_y, 75, fill="none", stroke=FIELD, sw=1.3, dash="4,3"))

    tb2, _, _ = textbox(p2_x + p2_w / 2, p2_y + 270, "r = 3 см  ->  B = 89 мкТл\nr = 10 см ->  B = 12 мкТл\n(Часткова компенсація)", size=11, pad=6, fill="#ffffff", stroke="#d1d5db")
    frags.append(tb2)

    # Панель 3: Скручена вита пара (Twisted Pair, B ~ exp(-r/L) або 1/r^3)
    p3_x, p3_y, p3_w, p3_h = 570, 50, 250, 320
    frags.append(rect(p3_x, p3_y, p3_w, p3_h, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(p3_x + p3_w / 2, p3_y + 24, "Скручена вита пара", size=14, bold=True, color=FIELD))
    frags.append(text(p3_x + p3_w / 2, p3_y + 44, "Квадруполь: B ~ 1/r³ ... 1/r⁴", size=12, color=MUTED))

    # Схематичний рисунок скрутки
    tw_y = p3_y + 135
    # Хвилі скрутки
    # Перший напіввиток
    frags.append(circle(p3_x + 55, tw_y - 20, 11, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(circle(p3_x + 55, tw_y + 20, 11, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(p3_x + 55, tw_y - 36, "+m₁", size=10, bold=True, color=POS))
    # Другий напіввиток (навпаки)
    frags.append(circle(p3_x + 125, tw_y - 20, 11, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(circle(p3_x + 125, tw_y + 20, 11, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(text(p3_x + 125, tw_y - 36, "−m₂", size=10, bold=True, color=NEG))
    # Третій напіввиток
    frags.append(circle(p3_x + 195, tw_y - 20, 11, fill="#fdecea", stroke=POS, sw=1.8))
    frags.append(circle(p3_x + 195, tw_y + 20, 11, fill="#eaf0fd", stroke=NEG, sw=1.8))
    frags.append(text(p3_x + 195, tw_y - 36, "+m₃", size=10, bold=True, color=POS))

    # З'єднувальні лінії скрутки
    frags.append(line(p3_x + 66, tw_y - 20, p3_x + 114, tw_y + 20, color=POS, sw=2.5))
    frags.append(line(p3_x + 66, tw_y + 20, p3_x + 114, tw_y - 20, color=NEG, sw=2.5))
    frags.append(line(p3_x + 136, tw_y + 20, p3_x + 184, tw_y - 20, color=POS, sw=2.5))
    frags.append(line(p3_x + 136, tw_y - 20, p3_x + 184, tw_y + 20, color=NEG, sw=2.5))

    # Крок скрутки
    frags.append(line(p3_x + 55, tw_y + 42, p3_x + 125, tw_y + 42, color=MUTED, sw=1, dash="2,2"))
    frags.append(text(p3_x + 90, tw_y + 54, "крок λ/2", size=10, color=MUTED))

    tb3, _, _ = textbox(p3_x + p3_w / 2, p3_y + 270, "r = 3 см  ->  B < 4.5 мкТл\nr = 10 см ->  B < 0.2 мкТл\n(Придушення на 98–99%)", size=11, pad=6, fill="#ffffff", stroke=FIELD)
    frags.append(tb3)

    render("img/biot-savart-field.svg", w, h, *frags)


def gen_drone_field_map():
    """Фігура 2: drone-field-map.svg — Карта завад дрона: червона зона PDB/ESC та чиста зелена зона на щоглі."""
    w, h = 840, 420
    frags = []

    frags.append(text(w / 2, 26, "Розподіл магнітних завад на рамі дрона: внутрішній компас проти виносної щогли", size=15, bold=True))

    # Нижня силова дека (карбонова рама дрона)
    frags.append(rect(140, 305, 560, 24, fill="#334155", stroke="#1e293b", sw=1.5, rx=4))
    frags.append(text(420, 321, "Нижня силова дека рами (карбон 2.5 мм)", size=11, bold=True, color="#ffffff"))

    # Промені рами ліворуч і праворуч
    frags.append(rect(15, 305, 120, 24, fill="#475569", stroke="#1e293b", sw=1.5, rx=4))
    frags.append(rect(705, 305, 120, 24, fill="#475569", stroke="#1e293b", sw=1.5, rx=4))
    frags.append(text(75, 321, "Промінь M1 / M4", size=11, bold=True, color="#ffffff"))
    frags.append(text(765, 321, "Промінь M2 / M3", size=11, bold=True, color="#ffffff"))

    # Батарея під декою
    frags.append(rect(310, 345, 220, 50, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=6))
    frags.append(text(420, 367, "LiPo акумулятор 6S 4500 мАг", size=12, bold=True, color=INK))
    frags.append(text(420, 383, "Кабелі AWG10 до PDB / XT60 (струм до 150 А)", size=10, color=MUTED))

    # Силова плата 4-in-1 ESC / PDB
    frags.append(rect(240, 245, 360, 45, fill="#fee2e2", stroke=POS, sw=2, rx=6))
    frags.append(text(420, 265, "4-in-1 ESC / PDB (струм до 180 A)", size=13, bold=True, color=POS))
    frags.append(text(420, 281, "Силові шини, ключі MOSFET, петлі струму", size=10, color=POS))

    # Силові дроти від батареї до ESC
    frags.append(line(350, 345, 350, 290, color=POS, sw=3))
    frags.append(line(490, 345, 490, 290, color=NEG, sw=3))

    # Польотний контролер (FC) прямо над ESC (зазор 15–20 мм)
    frags.append(rect(280, 175, 280, 45, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=6))
    frags.append(text(420, 193, "Польотний контролер (FC)", size=12, bold=True, color="#92400e"))
    frags.append(text(420, 209, "Вбудований давач MAG 1 (в зоні завад)", size=10, bold=True, color=POS))

    # Виносна щогла GPS / MAG (x=175)
    frags.append(line(175, 305, 175, 95, color="#0f172a", sw=4))
    frags.append(circle(175, 305, 5, fill="#0f172a", stroke="#0f172a", sw=1))

    # Модуль GPS + зовнішній компас на щоглі
    frags.append(rect(105, 50, 140, 45, fill="#dcfce7", stroke=FIELD, sw=2, rx=8))
    frags.append(text(175, 68, "Модуль GPS + MAG 2", size=12, bold=True, color=FIELD))
    frags.append(text(175, 84, "Зовнішній компас", size=10, bold=True, color=FIELD))

    # Рамка порівняння завад ліворуч (Зовнішній)
    tb_ext, _, _ = textbox(95, 125, "ЗОНА ЧИСТОГО ПОЛЯ\nЩогла: 15 см від деки\nЗавада: ΔB < 1.2 мкТл\nПохибка курсу: < 1.5°", size=11, pad=8, fill="#f0fdf4", stroke=FIELD)
    frags.append(tb_ext)

    # Рамка порівняння завад праворуч (Внутрішній)
    tb_int, _, _ = textbox(710, 175, "КРИТИЧНА ЧЕРВОНА ЗОНА\nВідстань: 1.5–2.5 см\nЗавада: ΔB = 80...250 мкТл\nПохибка курсу: 30°...75°\n(Перевищує поле Землі!)", size=11, pad=8, fill="#fef2f2", stroke=POS)
    frags.append(tb_int)
    frags.append(arrow(600, 175, 570, 195, color=POS, sw=1.5))

    render("img/drone-field-map.svg", w, h, *frags)


def gen_ekf_yaw_drift():
    """Фігура 3: ekf-yaw-drift.svg — Замкнений контур зриву курсу (Yaw divergence / Flyaway)."""
    w, h = 840, 360
    frags = []

    frags.append(text(w / 2, 26, "Ланцюг деградації EKF: від струмової завади до спірального зриву навігації", size=15, bold=True))

    # Блоки ланцюга (горизонтальний цикл)
    b1_x, b1_y = 90, 80
    b2_x, b2_y = 310, 80
    b3_x, b3_y = 530, 80
    b4_x, b4_y = 740, 80

    b5_x, b5_y = 740, 240
    b6_x, b6_y = 530, 240
    b7_x, b7_y = 310, 240
    b8_x, b8_y = 90, 240

    tb1, _, _ = textbox(b1_x, b1_y, "1. Додавання газу\nСтрум I зростає\nвід 15 А до 120 А", size=11, pad=7, fill="#fff7ed", stroke="#ea580c")
    tb2, _, _ = textbox(b2_x, b2_y, "2. Паразитне поле\nΔB ~ k · I спотворює\nвектор магнітометра", size=11, pad=7, fill="#fee2e2", stroke=POS)
    tb3, _, _ = textbox(b3_x, b3_y, "3. Хибний курс компаса\nПоворот вектора B\nна кут Δψ = 25°...50°", size=11, pad=7, fill="#fee2e2", stroke=POS)
    tb4, _, _ = textbox(b4_x, b4_y, "4. Нев'язка в EKF\nInnovation y = z − h(x)\nзміщує оцінку курсу ψ̂", size=11, pad=7, fill="#fef3c7", stroke="#d97706")

    frags.extend([tb1, tb2, tb3, tb4])

    frags.append(arrow(b1_x + 65, b1_y, b2_x - 70, b2_y, color="#ea580c", sw=2))
    frags.append(arrow(b2_x + 70, b2_y, b3_x - 75, b3_y, color=POS, sw=2))
    frags.append(arrow(b3_x + 75, b3_y, b4_x - 70, b4_y, color=POS, sw=2))

    # Спуск вниз праворуч
    frags.append(arrow(b4_x, b4_y + 35, b5_x, b5_y - 35, color="#d97706", sw=2))

    tb5, _, _ = textbox(b5_x, b5_y, "5. Реакція автопілота\nКонтролер докручує\nмотори для виправлення", size=11, pad=7, fill="#fef3c7", stroke="#d97706")
    tb6, _, _ = textbox(b6_x, b6_y, "6. Фізичний розворот\nНіс дрона відхиляється\nвід реальної траєкторії", size=11, pad=7, fill="#fee2e2", stroke=POS)
    tb7, _, _ = textbox(b7_x, b7_y, "7. Конфлікт з GPS\nВектор швидкості GPS\nсуперечить курсу ψ̂", size=11, pad=7, fill="#fee2e2", stroke=POS)
    tb8, _, _ = textbox(b8_x, b8_y, "8. Спіраль Flyaway\nEKF скидає курс або\nвходить у «унітазинг»", size=11, pad=7, fill="#450a0a", stroke="#991b1b", color="#ffffff", bold=True)

    frags.extend([tb5, tb6, tb7, tb8])

    frags.append(arrow(b5_x - 70, b5_y, b6_x + 75, b6_y, color="#d97706", sw=2))
    frags.append(arrow(b6_x - 75, b6_y, b7_x + 75, b7_y, color=POS, sw=2))
    frags.append(arrow(b7_x - 75, b7_y, b8_x + 70, b8_y, color=POS, sw=2))

    # Зворотна стрілка посилення завади
    frags.append(arrow(b8_x, b8_y - 35, b1_x, b1_y + 35, color=POS, sw=2))
    frags.append(text(b1_x - 45, 160, "Підвищення\nтяги", size=10, bold=True, color=POS))

    render("img/ekf-yaw-drift.svg", w, h, *frags)


def gen_compassmot_fitting():
    """Фігура 4: compassmot-fitting.svg — Графік струмової залежності завади та результат лінійної компенсації."""
    w, h = 840, 370
    frags = []

    frags.append(text(w / 2, 26, "Програмна компенсація Compass-Mot: калібрувальна регресія та усунення дрейфу", size=15, bold=True))

    # Графік 1 (ліворуч): Залежність B_x, B_y, B_z від струму
    g1_x, g1_y, g1_w, g1_h = 40, 60, 360, 270
    frags.append(rect(g1_x, g1_y, g1_w, g1_h, fill="#fafbfc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(g1_x + g1_w / 2, g1_y + 22, "Калібрувальний прогін (струм 0...100 А)", size=13, bold=True, color=INK))

    # Вісь X та Y
    ox1, oy1 = g1_x + 50, g1_y + g1_h - 40
    frags.append(line(ox1, oy1, ox1 + 280, oy1, color=INK, sw=1.5))
    frags.append(line(ox1, oy1, ox1, oy1 - 180, color=INK, sw=1.5))
    frags.append(text(ox1 + 270, oy1 + 22, "Струм I (А)", size=11, color=INK))
    frags.append(text(ox1 - 10, oy1 - 185, "Поле B (мкТл)", size=11, color=INK, anchor="end"))

    # Позначки струму
    for i_a, dx in [(0, 0), (25, 65), (50, 130), (75, 195), (100, 260)]:
        frags.append(line(ox1 + dx, oy1, ox1 + dx, oy1 + 4, color=INK, sw=1))
        frags.append(text(ox1 + dx, oy1 + 16, str(i_a), size=10, color=MUTED))

    # Криві завад
    # B_x (похибка вгору)
    frags.append(line(ox1, oy1 - 120, ox1 + 260, oy1 - 30, color=POS, sw=2.5))
    frags.append(text(ox1 + 270, oy1 - 25, "Bx (нахил kx)", size=10, bold=True, color=POS, anchor="start"))

    # B_y (похибка вниз)
    frags.append(line(ox1, oy1 - 90, ox1 + 260, oy1 - 165, color=NEG, sw=2.5))
    frags.append(text(ox1 + 270, oy1 - 165, "By (нахил ky)", size=10, bold=True, color=NEG, anchor="start"))

    # Точки вимірів
    for step in range(5):
        cx_pt = ox1 + step * 65
        frags.append(circle(cx_pt, oy1 - 120 + step * 22.5, 3.5, fill=POS, stroke=POS, sw=1))
        frags.append(circle(cx_pt, oy1 - 90 - step * 18.7, 3.5, fill=NEG, stroke=NEG, sw=1))

    # Графік 2 (праворуч): Похибка курсу при ривку газу: до і після компенсації
    g2_x, g2_y, g2_w, g2_h = 440, 60, 360, 270
    frags.append(rect(g2_x, g2_y, g2_w, g2_h, fill="#fafbfc", stroke="#cbd5e1", sw=1.2, rx=6))
    frags.append(text(g2_x + g2_w / 2, g2_y + 22, "Курс Yaw під час повного газу (Punch Out)", size=13, bold=True, color=INK))

    ox2, oy2 = g2_x + 50, g2_y + g1_h - 40
    frags.append(line(ox2, oy2, ox2 + 280, oy2, color=INK, sw=1.5))
    frags.append(line(ox2, oy2, ox2, oy2 - 180, color=INK, sw=1.5))
    frags.append(text(ox2 + 270, oy2 + 22, "Час t (с)", size=11, color=INK))
    frags.append(text(ox2 - 10, oy2 - 185, "Курс Yaw (°)", size=11, color=INK, anchor="end"))

    # Позначки часу
    for t_s, dx in [(0, 0), (1, 65), (2, 130), (3, 195), (4, 260)]:
        frags.append(line(ox2 + dx, oy2, ox2 + dx, oy2 + 4, color=INK, sw=1))
        frags.append(text(ox2 + dx, oy2 + 16, str(t_s), size=10, color=MUTED))

    # Істинний постійний курс (пунктир)
    frags.append(line(ox2, oy2 - 90, ox2 + 260, oy2 - 90, color=MUTED, sw=1.5, dash="4,3"))
    frags.append(text(ox2 + 20, oy2 - 75, "Істинний курс (0°)", size=10, color=MUTED))

    # Без компенсації (червона лінія з різким стрибком на газу до +35°)
    frags.append(line(ox2, oy2 - 90, ox2 + 40, oy2 - 90, color=POS, sw=2.2))
    frags.append(line(ox2 + 40, oy2 - 90, ox2 + 80, oy2 - 165, color=POS, sw=2.2))
    frags.append(line(ox2 + 80, oy2 - 165, ox2 + 180, oy2 - 155, color=POS, sw=2.2))
    frags.append(line(ox2 + 180, oy2 - 155, ox2 + 220, oy2 - 90, color=POS, sw=2.2))
    frags.append(line(ox2 + 220, oy2 - 90, ox2 + 260, oy2 - 90, color=POS, sw=2.2))
    frags.append(text(ox2 + 130, oy2 - 172, "Без компенсації: стрибок +38°", size=10, bold=True, color=POS))

    # З компенсацією Compass-Mot (зелена рівна лінія з шумом < 1°)
    frags.append(line(ox2, oy2 - 90, ox2 + 40, oy2 - 90, color=FIELD, sw=2.2))
    frags.append(line(ox2 + 40, oy2 - 90, ox2 + 80, oy2 - 93, color=FIELD, sw=2.2))
    frags.append(line(ox2 + 80, oy2 - 93, ox2 + 180, oy2 - 88, color=FIELD, sw=2.2))
    frags.append(line(ox2 + 180, oy2 - 88, ox2 + 220, oy2 - 90, color=FIELD, sw=2.2))
    frags.append(line(ox2 + 220, oy2 - 90, ox2 + 260, oy2 - 90, color=FIELD, sw=2.2))
    frags.append(text(ox2 + 130, oy2 - 102, "З Compass-Mot: похибка < 1.2°", size=10, bold=True, color=FIELD))

    render("img/compassmot-fitting.svg", w, h, *frags)


if __name__ == "__main__":
    os.makedirs("img", exist_ok=True)
    gen_biot_savart()
    gen_drone_field_map()
    gen_ekf_yaw_drift()
    gen_compassmot_fitting()
    print("Всі 4 SVG-фігури успішно згенеровано у ./img/")
