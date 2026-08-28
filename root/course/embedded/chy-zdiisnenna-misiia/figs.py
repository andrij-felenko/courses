# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'Чи здійсненна місія: час, енергія, вітер, висота'."""

import sys
import os
import math

# Підключаємо svgkit з scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts")))
from svgkit import *

os.makedirs("img", exist_ok=True)


def fig_validation_pipeline():
    """Етапи передпольотної валідації місії."""
    w, h = 960, 360
    frags = []

    # Заголовок
    frags.append(text(480, 24, "Конвеєр передпольотної валідації місії (Pre-Flight Validation)", size=16, bold=True))

    # Вхідний блок (x: 15..140)
    in_box = fitbox(15, 60, 125, 260, "Вхідні дані\n\n• План місії (WP)\n• Модель БПЛА\n• Вітер (прогноз)\n• Рельєф (DEM)\n• Батарея (SoC)", size=11, fill="#eef2f7", stroke="#4a5568")
    frags.append(in_box)

    # 5 етапів перевірки (ширина 110, відступи між блоками 20px)
    steps = [
        ("1. Геометрія\nй геозона", "Координати,\nрадіуси точок,\nмежі Geofence", 220),
        ("2. Вітрове\nвікно", "Трикутник v,\nзнос, шляхова\nv_g > v_min", 350),
        ("3. Кліренс\nрельєфу", "Профіль DEM,\nзапас h_safe,\nкути набору γ", 480),
        ("4. Енергетичний\nбюджет", "Інтеграл P(t),\nрезерв 25%,\nточка неповерн.", 610),
        ("5. Часові\nвікна", "Тривалість,\nзахід сонця,\nкут для оптики", 740),
    ]

    # Стрілка від входу до першого етапу
    frags.append(arrow(140, 190, 163, 190, color=LINE, sw=1.8))

    for i, (title, desc, cx) in enumerate(steps):
        # Рамка етапу (w=110, h=180, x: cx-55 .. cx+55)
        box = fitbox(cx - 55, 100, 110, 180, f"{title}\n\n{desc}", size=11, fill="#f8fafc", stroke="#2563eb", sw=1.8)
        frags.append(box)

        # Стрілка до наступного
        if i < len(steps) - 1:
            next_cx = steps[i+1][2]
            frags.append(arrow(cx + 55, 190, next_cx - 57, 190, color=LINE, sw=1.8))

    # Вихідні результати: GO / NO-GO (x: 840..930)
    frags.append(arrow(795, 150, 835, 115, color=FIELD, sw=2))
    frags.append(arrow(795, 230, 835, 265, color=POS, sw=2))

    go_box = fitbox(840, 85, 95, 55, "ГОТОВИЙ\n(GO)", size=11, bold=True, fill="#e8f8f0", stroke=FIELD, sw=2)
    nogo_box = fitbox(840, 240, 95, 60, "ВІДХИЛЕНО\n(NO-GO)\n+ звіт", size=10, bold=True, fill="#fdecea", stroke=POS, sw=2)
    frags.append(go_box)
    frags.append(nogo_box)

    render("img/validation-pipeline.svg", w, h, *frags)


def fig_wind_triangle():
    """Трикутник швидкостей та вітрове вікно здійсненності."""
    w, h = 880, 420
    frags = []

    frags.append(text(440, 24, "Трикутник швидкостей та кут зносу (Crab Angle)", size=16, bold=True))

    # Ліва частина: Векторна діаграма
    frags.append(rect(30, 50, 400, 345, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(230, 75, "Векторний трикутник навігації", size=13, bold=True))

    ox, oy = 80, 320
    ax, ay = 200, 120
    bx, by = 360, 200

    # Шляхова траєкторія (пунктир)
    frags.append(line(ox, oy, bx, by, color=FIELD, sw=2.5))
    frags.append(arrow(ox, oy, bx, by, color=FIELD, sw=2.5))

    # Повітряна швидкість (куда дивиться ніс)
    frags.append(line(ox, oy, ax, ay, color=NEG, sw=2.5))
    frags.append(arrow(ox, oy, ax, ay, color=NEG, sw=2.5))

    # Вітер (знос)
    frags.append(line(ax, ay, bx, by, color=POS, sw=2.5))
    frags.append(arrow(ax, ay, bx, by, color=POS, sw=2.5))

    # Підписи векторів
    frags.append(text(120, 200, "v_air (повітряна)", size=12, color=NEG, bold=True))
    frags.append(text(285, 145, "w (вітер)", size=12, color=POS, bold=True))
    frags.append(text(250, 295, "v_ground (шляхова)", size=12, color=FIELD, bold=True))

    # Кут зносу beta
    frags.append(text(125, 290, "β (знос)", size=11, color="#7c3aed", bold=True))

    # Права частина: Графік v_ground проти зустрічного вітру
    frags.append(rect(450, 50, 400, 345, fill="#fafbfc", stroke="#cbd5e1", sw=1.5, rx=8))
    frags.append(text(650, 75, "Шляхова швидкість vs Зустрічний вітер", size=13, bold=True))

    # Осі графіка
    gx0, gy0 = 500, 340
    gx_max, gy_max = 810, 120
    frags.append(line(gx0, gy0, gx_max + 20, gy0, color=LINE, sw=1.5))
    frags.append(line(gx0, gy0, gx0, gy_max - 20, color=LINE, sw=1.5))
    frags.append(text(gx_max + 15, gy0 + 20, "w (м/с)", size=11))
    frags.append(text(gx0 - 15, gy_max - 15, "v_g", size=11))

    # Лінія v_ground = v_air - w
    frags.append(line(500, 140, 760, 340, color=POS, sw=2.5))

    # Безпечна зона v_g >= 5 м/с
    frags.append(line(500, 273, 760, 273, color="#d97706", sw=1.5, dash="4,4"))
    frags.append(text(575, 265, "Поріг v_min = 5 м/с", size=10, color="#d97706"))

    # Заборонена зона (w >= v_air)
    frags.append(rect(760, gy_max - 10, 60, gy0 - gy_max + 10, fill="#fee2e2", stroke="none"))
    frags.append(text(790, 220, "Неповер-\nнення\nw ≥ v_air", size=10, color=POS, bold=True))

    # Позначки
    frags.append(text(500, gy0 + 15, "0", size=10))
    frags.append(text(630, gy0 + 15, "w = 10", size=10))
    frags.append(text(760, gy0 + 15, "w = v_air", size=10))

    render("img/wind-triangle-envelope.svg", w, h, *frags)


def fig_terrain_clearance():
    """Профіль висоти польоту та кліренс над моделлю рельєфу (DEM)."""
    w, h = 880, 400
    frags = []

    frags.append(text(440, 24, "Профіль кліренсу рельєфу (Terrain Clearance) за даними DEM", size=16, bold=True))

    # Полотно графіка
    x0, y0 = 60, 340
    w_graph, h_graph = 760, 270

    # Сітка та вісі
    frags.append(line(x0, y0, x0 + w_graph, y0, color=LINE, sw=1.5))
    frags.append(line(x0, y0, x0, y0 - h_graph, color=LINE, sw=1.5))
    frags.append(text(x0 + w_graph, y0 + 20, "Дистанція маршруту s (км)", size=11, anchor="end"))
    frags.append(text(x0 - 10, y0 - h_graph, "Висота h (м)", size=11, anchor="end"))

    # Позначки висоти
    for alt, py in [(0, y0), (100, y0 - 70), (200, y0 - 140), (300, y0 - 210), (400, y0 - 270)]:
        frags.append(line(x0 - 4, py, x0, py, color=LINE, sw=1))
        frags.append(text(x0 - 8, py + 4, str(alt), size=10, anchor="end"))
        if alt > 0:
            frags.append(line(x0, py, x0 + w_graph, py, color="#e2e8f0", sw=1, dash="3,3"))

    # Точки рельєфу (DEM профіль)
    dem_pts = [
        (60, 340 - 30),
        (160, 340 - 50),
        (260, 340 - 160),  # Пагорб 1
        (380, 340 - 90),
        (520, 340 - 240),  # Висока гора
        (650, 340 - 120),
        (760, 340 - 60),
        (820, 340 - 40)
    ]

    # Заливка рельєфу
    path_d = f"M {dem_pts[0][0]} {y0} " + " ".join(f"L {px} {py}" for px, py in dem_pts) + f" L {dem_pts[-1][0]} {y0} Z"
    frags.append(f'<path d="{path_d}" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>')

    # Буфер безпеки (DEM + h_clearance = 50м, тобто py - 35px)
    clearance_pts = [(px, py - 35) for px, py in dem_pts]
    c_path = " ".join(f"{'M' if i==0 else 'L'} {px} {py}" for i, (px, py) in enumerate(clearance_pts))
    frags.append(f'<path d="{c_path}" fill="none" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="5,4"/>')
    frags.append(text(280, 130, "Буфер безпеки (h_safe = 50 м)", size=10, color="#b45309"))

    # Траєкторія 1: Небезпечна (пряма між WP1 і WP2 через пік)
    frags.append(line(160, 190, 650, 190, color=POS, sw=2, dash="4,4"))
    frags.append(circle(520, 190, 6, fill="#fee2e2", stroke=POS, sw=2))
    frags.append(text(520, 175, "Колізія з рельєфом!", size=11, color=POS, bold=True))

    # Траєкторія 2: Валідована безпечна з огинанням
    safe_traj = [(160, 190), (450, 50), (580, 50), (650, 190)]
    s_path = " ".join(f"{'M' if i==0 else 'L'} {px} {py}" for i, (px, py) in enumerate(safe_traj))
    frags.append(f'<path d="{s_path}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')

    # Вейпойнти
    for px, py, name in [(160, 190, "WP1"), (450, 50, "WP2 (Climb)"), (580, 50, "WP3"), (650, 190, "WP4")]:
        frags.append(circle(px, py, 4, fill=FIELD, stroke=INK, sw=1.5))
        frags.append(text(px, py - 10, name, size=10, bold=True))

    render("img/terrain-clearance-profile.svg", w, h, *frags)


def fig_energy_budget():
    """Енергетичний бюджет місії та точка неповернення (Point of Safe Return)."""
    w, h = 880, 400
    frags = []

    frags.append(text(440, 24, "Енергетичний баланс місії та точка неповернення (PSR)", size=16, bold=True))

    x0, y0 = 70, 330
    gw, gh = 740, 250

    # Осі
    frags.append(line(x0, y0, x0 + gw, y0, color=LINE, sw=1.5))
    frags.append(line(x0, y0, x0, y0 - gh, color=LINE, sw=1.5))
    frags.append(text(x0 + gw, y0 + 20, "Час місії t (хв)", size=11, anchor="end"))
    frags.append(text(x0 - 10, y0 - gh, "Енергія (Вт·год)", size=11, anchor="end"))

    # Позначки осі Y (Батарея = 200 Вт*год)
    frags.append(text(x0 - 8, y0 + 4, "0", size=10, anchor="end"))
    frags.append(text(x0 - 8, 134, "200 Wh (E_bat)", size=10, anchor="end"))
    frags.append(text(x0 - 8, 184, "150 Wh (E_usable)", size=10, anchor="end"))

    # Лінія повної ємності батареї (200 Wh)
    frags.append(line(x0, 130, x0 + gw, 130, color=LINE, sw=1.5, dash="4,4"))

    # Лінія доступної ємності (150 Wh = 75%, 25% резерв)
    frags.append(line(x0, 180, x0 + gw, 180, color="#dc2626", sw=1.8, dash="5,4"))

    # Заливка 25% аварійного резерву
    frags.append(rect(x0, 130, gw, 50, fill="#fee2e2", stroke="none"))
    frags.append(text(x0 + gw - 80, 155, "Аварійний резерв 25%", size=11, color=POS, bold=True))

    # Крива витрати енергії: Штиль (Calm)
    frags.append(line(x0, y0, x0 + 600, 200, color=FIELD, sw=2.5))
    frags.append(text(x0 + 605, 200, "У штиль (успіх: 130 Wh)", size=11, color=FIELD, bold=True, anchor="start"))

    # Крива витрати енергії: Зустрічний вітер на зворотному шляху (Wind)
    pts_wind = [(x0, y0), (x0 + 220, 275), (x0 + 480, 130)]
    w_path = f"M {pts_wind[0][0]} {pts_wind[0][1]} L {pts_wind[1][0]} {pts_wind[1][1]} L {pts_wind[2][0]} {pts_wind[2][1]}"
    frags.append(f'<path d="{w_path}" fill="none" stroke="{POS}" stroke-width="2.5"/>')
    frags.append(text(x0 + 490, 125, "Зустрічний вітер (дефіцит!)", size=11, color=POS, bold=True, anchor="start"))

    # Точка неповернення (PSR / Bingo Point)
    psr_x, psr_y = x0 + 220, 275
    frags.append(circle(psr_x, psr_y, 6, fill="#fef08a", stroke="#ca8a04", sw=2))
    frags.append(line(psr_x, psr_y, psr_x, y0, color="#ca8a04", sw=1.5, dash="3,3"))
    frags.append(text(psr_x, y0 + 15, "t_PSR (Точка розвороту)", size=10, color="#854d0e", bold=True))

    render("img/energy-wind-budget.svg", w, h, *frags)


if __name__ == "__main__":
    fig_validation_pipeline()
    fig_wind_triangle()
    fig_terrain_clearance()
    fig_energy_budget()
    print("All figures generated successfully.")
