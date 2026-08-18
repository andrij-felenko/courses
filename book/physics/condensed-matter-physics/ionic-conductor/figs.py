# -*- coding: utf-8 -*-
"""Генератор фігур для теми 'Іонний провідник' (ionic-conductor)."""

import os
import sys

# Додаємо шлях до scripts/ для імпорту svgkit
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def make_frenkel_schottky():
    """Фігура 1: Порівняння дефектів Френкеля та Шотткі у ґратці."""
    w, h = 760, 360
    elements = []

    # Заголовок панелі Френкеля
    elements.append(rect(20, 20, 350, 320, fill=FILL, stroke=LINE, sw=1, rx=8))
    elements.append(text(195, 45, "Дефект Френкеля (міжвузловий іон)", size=14, bold=True, color=INK))
    elements.append(text(195, 65, "Катіон залишає вузол і іде в міжвузля", size=11, color=MUTED))

    # Заголовок панелі Шотткі
    elements.append(rect(390, 20, 350, 320, fill=FILL, stroke=LINE, sw=1, rx=8))
    elements.append(text(565, 45, "Дефект Шотткі (пара вакансій)", size=14, bold=True, color=INK))
    elements.append(text(565, 65, "Пара іонів виходить на поверхню кристала", size=11, color=MUTED))

    # Спрощена сітка ґратки Френкеля (5x4)
    start_x, start_y = 60, 110
    step_x, step_y = 65, 55

    for row in range(4):
        for col in range(5):
            cx = start_x + col * step_x
            cy = start_y + row * step_y
            is_cation = (row + col) % 2 == 0

            # На позиції (row=1, col=2) створюємо вакансію катіона
            if row == 1 and col == 2:
                elements.append(circle(cx, cy, 14, fill="#ffffff", stroke=POS, sw=1.5))
                elements.append(line(cx - 8, cy - 8, cx + 8, cy + 8, color=POS, sw=1.5, dash="2,2"))
                elements.append(line(cx - 8, cy + 8, cx + 8, cy - 8, color=POS, sw=1.5, dash="2,2"))
                elements.append(text(cx, cy + 26, "v_M'", size=10, color=POS, bold=True))
            else:
                if is_cation:
                    elements.append(plus(cx, cy, r=12))
                else:
                    elements.append(minus(cx, cy, r=12))

    # Міжвузловий іон для Френкеля
    inter_x = start_x + 2 * step_x + 32
    inter_y = start_y + 1 * step_y + 28
    elements.append(plus(inter_x, inter_y, r=10))
    elements.append(text(inter_x + 30, inter_y + 4, "M_i°", size=10, color=POS, bold=True))

    # Стрілка переходу для Френкеля
    from_x = start_x + 2 * step_x
    from_y = start_y + 1 * step_y
    elements.append(arrow(from_x + 10, from_y + 10, inter_x - 8, inter_y - 8, color=POS, sw=2))

    # Сітка ґратки Шотткі (5x4)
    start_x2 = 430
    for row in range(4):
        for col in range(5):
            cx = start_x2 + col * step_x
            cy = start_y + row * step_y
            is_cation = (row + col) % 2 == 0

            # Катіонна вакансія (row=1, col=1)
            if row == 1 and col == 1:
                elements.append(circle(cx, cy, 14, fill="#ffffff", stroke=POS, sw=1.5))
                elements.append(line(cx - 8, cy - 8, cx + 8, cy + 8, color=POS, sw=1.5, dash="2,2"))
                elements.append(text(cx - 15, cy + 26, "v_M'", size=10, color=POS, bold=True))
            # Аніонна вакансія (row=2, col=3)
            elif row == 2 and col == 3:
                elements.append(circle(cx, cy, 14, fill="#ffffff", stroke=NEG, sw=1.5))
                elements.append(line(cx - 8, cy - 8, cx + 8, cy + 8, color=NEG, sw=1.5, dash="2,2"))
                elements.append(text(cx + 15, cy + 26, "v_X°", size=10, color=NEG, bold=True))
            else:
                if is_cation:
                    elements.append(plus(cx, cy, r=12))
                else:
                    elements.append(minus(cx, cy, r=12))

    # Іони, що вийшли на поверхню (зверху панелі Шотткі)
    surf_y = 90
    elements.append(plus(start_x2 + 1 * step_x, surf_y, r=10))
    elements.append(minus(start_x2 + 3 * step_x, surf_y, r=10))
    elements.append(arrow(start_x2 + 1 * step_x, start_y + 1 * step_y - 12, start_x2 + 1 * step_x, surf_y + 12, color=POS, sw=1.5))
    elements.append(arrow(start_x2 + 3 * step_x, start_y + 2 * step_y - 12, start_x2 + 3 * step_x, surf_y + 12, color=NEG, sw=1.5))

    elements.append(text(565, 310, "Збереження електронетральності кристала", size=11, italic=True, color=INK))

    render(os.path.join(OUT_DIR, "frenkel-schottky-defects.svg"), w, h, "".join(elements))


def make_hopping_potential():
    """Фігура 2: Енергетичний потенціальний рельєф і зміщення під дією поля."""
    w, h = 720, 360
    elements = []

    # Заголовок
    elements.append(text(360, 30, "Потенціальний рельєф ґратки та вплив зовнішнього поля E", size=15, bold=True))

    # Осі
    ox, oy = 60, 300
    elements.append(arrow(ox, oy, ox + 620, oy, color=LINE, sw=1.5))
    elements.append(text(ox + 630, oy + 4, "Координати x", size=12, color=INK))

    elements.append(arrow(ox, oy, ox, 60, color=LINE, sw=1.5))
    elements.append(text(ox - 10, 50, "Енергія U(x)", size=12, color=INK))

    # Симетрична потенціальна крива (E = 0) - пунктир
    min_y = 240
    max_y = 120

    pts_e0 = []
    import math
    for x in range(100, 570):
        val = math.sin((x - 120) * math.pi / 140)
        y = min_y - (min_y - max_y) * (val ** 2)
        pts_e0.append((x, y))

    d_e0 = "M " + " L ".join("%.1f,%.1f" % pt for pt in pts_e0)
    elements.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="4,4"/>' % (d_e0, MUTED))

    # Потенціальна крива під дією поля E > 0 (нахил)
    pts_e = []
    slope = 0.12
    for x, y in pts_e0:
        y_tilted = y - (x - 120) * slope
        pts_e.append((x, y_tilted))

    d_e = "M " + " L ".join("%.1f,%.1f" % pt for pt in pts_e)
    elements.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (d_e, POS))

    # Позначення іона в мінімумі x=260
    ion_x = 260
    ion_y = min_y - (260 - 120) * slope
    elements.append(plus(ion_x, ion_y - 10, r=11))

    # Стрілка можливого стрибка вправо
    elements.append(arrow(ion_x + 12, ion_y - 10, ion_x + 100, ion_y - 25, color=FIELD, sw=2.5))
    elements.append(text(ion_x + 60, ion_y - 35, "Стрибок по полю (E_a - q·a·E/2)", size=11, color=FIELD, bold=True))

    # Бар'єр E_a для E=0
    elements.append(line(190, 120, 260, 120, color=LINE, sw=1, dash="2,2"))
    elements.append(line(260, 240, 260, 120, color=LINE, sw=1, dash="2,2"))
    elements.append(arrow(225, 240, 225, 120, color=INK, sw=1.5))
    elements.append(text(225 - 25, 180, "E_a", size=13, bold=True, color=INK))

    # Позначення поля E
    elements.append(arrow(480, 70, 580, 70, color=POS, sw=2))
    elements.append(text(530, 55, "Поле E →", size=13, color=POS, bold=True))

    # Пояснення легенди
    elements.append(line(80, 325, 120, 325, color=MUTED, sw=1.8, dash="4,4"))
    elements.append(text(185, 329, "Без поля (E = 0, симетричні бар'єри)", size=11, color=MUTED))

    elements.append(line(310, 325, 350, 325, color=POS, sw=2.2))
    elements.append(text(465, 329, "З полем E > 0 (знижений бар'єр для стрибка вперед)", size=11, color=POS, bold=True))

    render(os.path.join(OUT_DIR, "hopping-potential-barrier.svg"), w, h, "".join(elements))


def make_arrhenius_plot():
    """Фігура 3: Графік Арреніуса ln(σ·T) від 1/T."""
    w, h = 680, 380
    elements = []

    elements.append(text(340, 30, "Графік Арреніуса іонної провідності ln(σ·T) від 10³/T", size=15, bold=True))

    ox, oy = 70, 320
    elements.append(arrow(ox, oy, ox + 570, oy, color=LINE, sw=1.5))
    elements.append(text(ox + 580, oy + 4, "10³/T (K⁻¹)", size=12, color=INK))

    elements.append(arrow(ox, oy, ox, 60, color=LINE, sw=1.5))
    elements.append(text(ox - 10, 50, "ln(σ·T)", size=12, color=INK))

    x_break = 300
    y_break = 140

    # Високотемпературна область
    x1, y1 = 120, 70
    elements.append(line(x1, y1, x_break, y_break, color=NEG, sw=2.5))
    elements.append(text(180, 85, "Власна область (E_a = E_m + E_f/2)", size=11, color=NEG, bold=True))

    # Низькотемпературна область
    x2, y2 = 520, 270
    elements.append(line(x_break, y_break, x2, y2, color=NEG, sw=2.5))
    elements.append(text(430, 220, "Домішкова область (E_a = E_m)", size=11, color=NEG, bold=True))

    # Точка зламу T_c
    elements.append(circle(x_break, y_break, 5, fill=NEG, stroke=LINE, sw=1))
    elements.append(line(x_break, y_break, x_break, oy, color=MUTED, sw=1, dash="2,2"))
    elements.append(text(x_break, oy + 18, "10³/T_c", size=11, color=INK))

    # Крива суперіонного провідника (фазовий перехід α-AgI)
    x_tr = 240
    elements.append(line(100, 60, x_tr - 20, 60, color=POS, sw=2.5))
    elements.append(line(x_tr - 20, 60, x_tr + 20, 230, color=POS, sw=2, dash="3,3"))
    elements.append(line(x_tr + 20, 230, 480, 300, color=POS, sw=2.5))

    elements.append(text(140, 45, "Суперіонна α-фаза (підґраткове плавлення)", size=11, color=POS, bold=True))
    elements.append(text(x_tr + 35, 140, "Фазовий перехід (напр. AgI при 147°C)", size=10, color=POS, italic=True))

    # Легенда
    elements.append(rect(430, 60, 220, 75, fill=FILL, stroke=LINE, sw=1, rx=6))
    elements.append(line(445, 80, 475, 80, color=NEG, sw=2.5))
    elements.append(text(560, 84, "Ззвичайний твердий провідник", size=11, color=INK))
    elements.append(line(445, 110, 475, 110, color=POS, sw=2.5))
    elements.append(text(560, 114, "Суперіонний провідник", size=11, color=POS, bold=True))

    render(os.path.join(OUT_DIR, "arrhenius-conductivity.svg"), w, h, "".join(elements))


def make_superionic_channel():
    """Фігура 4: Схема каналів 3D/2D транспорту у суперіонній структурі (NASICON / β-alumina)."""
    w, h = 740, 340
    elements = []

    elements.append(rect(20, 20, 340, 300, fill=FILL, stroke=LINE, sw=1, rx=8))
    elements.append(text(190, 45, "2D проводильні шари (β-глинозем)", size=13, bold=True))

    # Жорсткі шпінельні блоки
    elements.append(rect(40, 70, 300, 60, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    elements.append(text(190, 105, "Жорсткий блок Al₂O₃ (шпінель)", size=12, color="#334155"))

    elements.append(rect(40, 210, 300, 60, fill="#e2e8f0", stroke="#64748b", sw=1.5, rx=4))
    elements.append(text(190, 245, "Жорсткий блок Al₂O₃ (шпінель)", size=12, color="#334155"))

    # Провідний шар
    elements.append(rect(40, 135, 300, 70, fill="#fef3c7", stroke="#f59e0b", sw=1.5, rx=4))
    elements.append(text(190, 155, "Провідний шар Na-O", size=11, color="#b45309", bold=True))

    # Стрілки руху іонів Na+
    for nx in [70, 130, 190, 250]:
        elements.append(plus(nx, 180, r=9))
        elements.append(arrow(nx + 10, 180, nx + 42, 180, color=POS, sw=2))

    # 3D канальна структура
    elements.append(rect(380, 20, 340, 300, fill=FILL, stroke=LINE, sw=1, rx=8))
    elements.append(text(550, 45, "3D сітка каналів (NASICON / LLZO)", size=13, bold=True))

    nodes = [(430, 100), (550, 90), (660, 110),
             (450, 190), (560, 210), (650, 180),
             (480, 270), (590, 260)]

    edges = [(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5), (3, 6), (4, 7), (6, 7)]

    for i, j in edges:
        x1, y1 = nodes[i]
        x2, y2 = nodes[j]
        elements.append(line(x1, y1, x2, y2, color="#94a3b8", sw=4))
        elements.append(line(x1, y1, x2, y2, color="#f1f5f9", sw=1.5, dash="3,3"))

    for i, (nx, ny) in enumerate(nodes):
        elements.append(plus(nx, ny, r=10))

    elements.append(arrow(nodes[0][0] + 8, nodes[0][1] + 8, nodes[3][0] - 8, nodes[3][1] - 8, color=POS, sw=2.5))
    elements.append(arrow(nodes[3][0] + 8, nodes[3][1] + 8, nodes[4][0] - 8, nodes[4][1] - 8, color=POS, sw=2.5))

    elements.append(text(550, 305, "Тривимірна сітка перехресних каналів", size=11, italic=True, color=INK))

    render(os.path.join(OUT_DIR, "superionic-channel.svg"), w, h, "".join(elements))


if __name__ == "__main__":
    make_frenkel_schottky()
    make_hopping_potential()
    make_arrhenius_plot()
    make_superionic_channel()
    print("Генерацію SVG фігур для ionic-conductor успішно завершено.")
