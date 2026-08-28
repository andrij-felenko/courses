# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_shortest_vs_costmap():
    W, H = 880, 480
    p = []

    # Рамка робочого поля
    p.append(rect(20, 20, W - 40, H - 40, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))

    # Перешкода 1: Кут будівлі ліворуч зверху
    # Зовнішній шар інфляції (Inflation Radius r_inf = 70px)
    p.append(rect(110, 90, 200, 160, fill="#fef3c7", stroke="#fde68a", sw=1.2, rx=24))
    # Внутрішній шар вписування (Inscribed Radius r_insc = 35px)
    p.append(rect(125, 105, 170, 130, fill="#fee2e2", stroke="#fca5a5", sw=1.2, rx=12))
    # Тверда статична перешкода (Lethal Obstacle)
    p.append(rect(140, 120, 140, 100, fill="#475569", stroke="#1e293b", sw=2.0, rx=4))
    p.append(text(210, 175, "Будівля A (Lethal = 254)", size=12, color="#ffffff", anchor="middle", bold=True))

    # Перешкода 2: Споруда праворуч знизу
    p.append(rect(510, 230, 220, 170, fill="#fef3c7", stroke="#fde68a", sw=1.2, rx=24))
    p.append(rect(525, 245, 190, 140, fill="#fee2e2", stroke="#fca5a5", sw=1.2, rx=12))
    p.append(rect(540, 260, 160, 110, fill="#475569", stroke="#1e293b", sw=2.0, rx=4))
    p.append(text(620, 320, "Будівля B (Lethal = 254)", size=12, color="#ffffff", anchor="middle", bold=True))

    # Зона вітрової турбулентності за будівлею A (зрив потоку)
    poly_turb = [(280, 120), (410, 100), (440, 190), (280, 220)]
    pts_turb = " ".join("%.1f,%.1f" % pt for pt in poly_turb)
    p.append('<polygon points="%s" fill="#f3e8ff" stroke="#c084fc" stroke-width="1.5" stroke-dasharray="4,3"/>' % pts_turb)
    p.append(text(360, 150, "Зона зриву потоку", size=11, color="#7e22ce", anchor="middle", bold=True))
    p.append(text(360, 168, "(аеродинамічна турбулентність)", size=9, color="#9333ea", anchor="middle", italic=True))

    # Точки старту і фінішу
    start_pt = (70, 390)
    goal_pt = (810, 80)

    # Позначення старту
    p.append(circle(start_pt[0], start_pt[1], 8, fill="#10b981", stroke="#047857", sw=2.0))
    p.append(text(start_pt[0], start_pt[1] + 24, "Старт", size=12, color="#047857", anchor="middle", bold=True))

    # Позначення фінішу
    p.append(circle(goal_pt[0], goal_pt[1], 8, fill="#3b82f6", stroke="#1d4ed8", sw=2.0))
    p.append(text(goal_pt[0], goal_pt[1] - 14, "Ціль", size=12, color="#1d4ed8", anchor="middle", bold=True))

    # 1. Траєкторія Евклідового найкоротшого шляху (Red dashed)
    euc_path = "M 70,390 L 280,220 L 540,260 L 810,80"
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,4"/>' % (euc_path, POS))

    # Червоні контрольні маркери колізійного ризику
    p.append(circle(280, 220, 5, fill=POS, stroke="#ffffff", sw=1.5))
    p.append(circle(540, 260, 5, fill=POS, stroke="#ffffff", sw=1.5))

    # 2. Траєкторія на карті вартості з інфляцією (Green solid)
    cost_path = "M 70,390 C 140,380 250,370 360,350 C 440,335 465,250 485,170 C 505,90 640,65 810,80"
    p.append('<path d="%s" fill="none" stroke="%s" stroke-width="3.2"/>' % (cost_path, FIELD))

    # Зелений контрольний маркер безпеки
    p.append(circle(360, 350, 5, fill=FIELD, stroke="#ffffff", sw=1.5))

    # Пояснювальні плашки збоку
    tb_risk, _, _ = textbox(210, 435, "Зрізання кута: нульовий кліренс, зрив потоку, ризик зіткнення", size=10, bold=True, fill="#fff1f2", stroke=POS)
    p.append(tb_risk)

    tb_safe, _, _ = textbox(620, 435, "Шлях на карті вартості: рух безпечним коридором із запасом дистанції", size=10, bold=True, fill="#f0fdf4", stroke=FIELD)
    p.append(tb_safe)

    # Легенда у верхньому лівому кутку
    p.append(rect(35, 35, 340, 46, fill="#ffffff", stroke="#94a3b8", sw=1.0, rx=4))
    p.append(line(50, 48, 85, 48, color=POS, sw=2.5, dash="6,4"))
    p.append(text(95, 52, "Евклідовий найкоротший шлях (небезпечний)", size=10, color=INK, anchor="start"))
    p.append(line(50, 68, 85, 68, color=FIELD, sw=3.0))
    p.append(text(95, 72, "Шлях за картою вартості (оптимальний)", size=10, color=INK, anchor="start", bold=True))

    render(os.path.join(OUT, "shortest-vs-costmap-path.svg"), W, H, *p)


def fig_costmap_layers():
    W, H = 880, 490
    p = []

    # Заголовок зверху
    p.append(text(W / 2, 26, "Архітектура шарів карти вартості (Layered Costmap)", size=15, color=INK, anchor="middle", bold=True))

    layers = [
        {
            "x": 35, "y": 55, "w": 185, "h": 370,
            "title": "1. Статичний шар", "sub": "Static Layer",
            "bg": "#f8fafc", "border": "#64748b", "header_bg": "#e2e8f0",
            "desc": [
                "• Тверді стіни та споруди",
                "• Двійкова сітка зайнятості",
                "• LETHAL_OBSTACLE = 254",
                "• FREE_SPACE = 0",
                "• Джерело: стаціонарна карта,",
                "  план приміщення, висотна сітка"
            ]
        },
        {
            "x": 245, "y": 55, "w": 185, "h": 370,
            "title": "2. Шар інфляції", "sub": "Inflation Layer",
            "bg": "#fefce8", "border": "#ca8a04", "header_bg": "#fef08a",
            "desc": [
                "• Вписаний радіус r_insc",
                "  INSCRIBED_COST = 253",
                "• Експоненційний спад:",
                "  cost(d) = exp(-α·Δd)·252",
                "• Радіус інфляції r_inf",
                "• Створює градієнт відштовхування",
                "  від кутів та ребер стін"
            ]
        },
        {
            "x": 455, "y": 55, "w": 185, "h": 370,
            "title": "3. Динамічний шар", "sub": "Hazard / Sensor Layer",
            "bg": "#faf5ff", "border": "#9333ea", "header_bg": "#f3e8ff",
            "desc": [
                "• Зони вітрової турбулентності",
                "• Сліпі зони сенсорів (FOV)",
                "• Зони завад GNSS / зв'язку",
                "• Тимчасові заборонені геозони",
                "• Штраф: додаткова вартість",
                "  cost_hazard ∈ [20..180]"
            ]
        },
        {
            "x": 665, "y": 55, "w": 180, "h": 370,
            "title": "4. Master Costmap", "sub": "Зведена карта вартості",
            "bg": "#f0fdf4", "border": "#16a34a", "header_bg": "#dcfce7",
            "desc": [
                "• Пошарова суперпозиція:",
                "  C_total = max(L_stat, L_inf)",
                "            + L_hazard",
                "• Вхідні дані для A* / Dijkstra",
                "• Шлях проходить долинами",
                "  мінімального інтегралу вартості"
            ]
        }
    ]

    for lay in layers:
        # Каркас
        p.append(rect(lay["x"], lay["y"], lay["w"], lay["h"], fill=lay["bg"], stroke=lay["border"], sw=1.8, rx=6))
        # Шапка
        p.append(rect(lay["x"], lay["y"], lay["w"], 46, fill=lay["header_bg"], stroke=lay["border"], sw=1.2, rx=6))
        p.append(text(lay["x"] + lay["w"] / 2, lay["y"] + 19, lay["title"], size=12, color=INK, anchor="middle", bold=True))
        p.append(text(lay["x"] + lay["w"] / 2, lay["y"] + 36, lay["sub"], size=10, color=MUTED, anchor="middle", italic=True))

        # Тіло
        ty = lay["y"] + 68
        for line_str in lay["desc"]:
            p.append(text(lay["x"] + 10, ty, line_str, size=10, color=INK, anchor="start"))
            ty += 22

    # Стрілки злиття між шарами
    p.append(line(220, 240, 245, 240, color="#64748b", sw=2.0))
    p.append(circle(245, 240, 3, fill="#64748b", stroke="none"))

    p.append(line(430, 240, 455, 240, color="#64748b", sw=2.0))
    p.append(circle(455, 240, 3, fill="#64748b", stroke="none"))

    p.append(line(640, 240, 665, 240, color="#16a34a", sw=2.5))
    p.append(circle(665, 240, 4, fill="#16a34a", stroke="none"))

    # Підсумковий блок знизу
    tb_foot, _, _ = textbox(W / 2, 455, "Планувальник оптимізує інтегральну функцію вартості вздовж траєкторії", size=11, bold=True, fill="#f8fafc", stroke="#0284c7")
    p.append(tb_foot)

    render(os.path.join(OUT, "costmap-layers-stack.svg"), W, H, *p)


if __name__ == "__main__":
    fig_shortest_vs_costmap()
    fig_costmap_layers()
    print("SVGs generated successfully.")
