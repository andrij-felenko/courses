# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_occupancy_grid_raycast_logodds():
    W, H = 880, 430
    p = []

    # Розділювач панелей
    p.append(line(440, 20, 440, 410, color="#e2e8f0", sw=1.5, dash="4,4"))

    # ── ЛІВА ПАНЕЛЬ: Растеризація променя далекоміра ──
    tb_l, _, _ = textbox(220, 32, "Растеризація променя в сітці зайнятості", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_l)

    # Область сітки (10x7 клітинок, крок 32px)
    grid_ox, grid_oy = 50, 75
    cs = 34
    cols, rows = 10, 7

    # Малюємо фонову сітку
    for r in range(rows):
        for c in range(cols):
            x = grid_ox + c * cs
            y = grid_oy + r * cs
            # Кольори клітинок за станом
            # Промінь іде від (1,3) до (7,2)
            # Трасування Брезенгема: (1,3) -> (2,3) -> (3,3) -> (4,2) -> (5,2) -> (6,2) -> [7,2]
            if c == 1 and r == 3:
                # Сенсор
                p.append(rect(x, y, cs, cs, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=2))
            elif (c == 2 and r == 3) or (c == 3 and r == 3) or (c == 4 and r == 2) or (c == 5 and r == 2) or (c == 6 and r == 2):
                # Вільні клітинки
                p.append(rect(x, y, cs, cs, fill="#e0f2fe", stroke="#38bdf8", sw=1.2, rx=2))
            elif c == 7 and r == 2:
                # Зайнята клітинка (відбиття)
                p.append(rect(x, y, cs, cs, fill="#fecaca", stroke=POS, sw=1.8, rx=2))
            elif (c == 7 and r == 1) or (c == 7 and r == 3) or (c == 8 and r == 2):
                # Тіло перешкоди
                p.append(rect(x, y, cs, cs, fill="#e2e8f0", stroke="#94a3b8", sw=1.0, rx=2))
            else:
                # Невідомі клітинки
                p.append(rect(x, y, cs, cs, fill="#f8fafc", stroke="#cbd5e1", sw=0.8, rx=2))

    # Лінія променя через центри
    sensor_cx = grid_ox + 1 * cs + cs / 2
    sensor_cy = grid_oy + 3 * cs + cs / 2
    hit_cx = grid_ox + 7 * cs + cs / 2
    hit_cy = grid_oy + 2 * cs + cs / 2
    p.append(line(sensor_cx, sensor_cy, hit_cx, hit_cy, color="#ef4444", sw=2.0, dash="3,3"))
    p.append(circle(sensor_cx, sensor_cy, 4.0, fill="#ea580c", stroke="#ffffff", sw=1.5))
    p.append(circle(hit_cx, hit_cy, 4.5, fill=POS, stroke="#ffffff", sw=1.5))

    # Пояснення клітинок
    fb_free = fitbox(50, 325, 175, 80, "Вільний простір (l_free):\nl(m) ← l(m) + l_free\nЙмовірність P ↓ (< 0.5)", size=10, fill="#f0f9ff", stroke="#7dd3fc")
    p.append(fb_free)

    fb_occ = fitbox(235, 325, 175, 80, "Точка відбиття (l_occ):\nl(m) ← l(m) + l_occ\nЙмовірність P ↑ (> 0.5)", size=10, fill="#fef2f2", stroke="#fca5a5")
    p.append(fb_occ)

    # ── ПРАВА ПАНЕЛЬ: Шкала логарифмічних шансів та насичення ──
    tb_r, _, _ = textbox(660, 32, "Шкала Log-Odds та насичення ймовірності", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_r)

    # Вісь Log-Odds
    axis_x = 480
    axis_y = 170
    axis_w = 350
    p.append(line(axis_x, axis_y, axis_x + axis_w, axis_y, color=LINE, sw=2.0))
    p.append(arrow(axis_x + axis_w - 20, axis_y, axis_x + axis_w + 10, axis_y, color=LINE, sw=2.0))

    # Засічки на осі
    ticks = [
        (axis_x + 30, "-4.0 (l_min)", "P ≈ 0.02", POS),
        (axis_x + 100, "-1.0 (l_free_th)", "Вільна", NEG),
        (axis_x + 175, "0.0 (l₀)", "P = 0.50 (Невідомо)", MUTED),
        (axis_x + 250, "+1.0 (l_occ_th)", "Зайнята", FIELD),
        (axis_x + 320, "+4.0 (l_max)", "P ≈ 0.98", POS),
    ]

    for tx, lbl_top, lbl_bot, col in ticks:
        p.append(line(tx, axis_y - 8, tx, axis_y + 8, color=LINE, sw=1.5))
        p.append(text(tx, axis_y - 14, lbl_top, size=10, color=col, anchor="middle", bold=True))
        p.append(text(tx, axis_y + 22, lbl_bot, size=9, color=INK, anchor="middle"))

    # Пояснення кліпінгу та порогів
    p.append(rect(480, 220, 350, 65, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(655, 240, "Формула переходу: l = ln( P / (1 - P) )", size=11, color=INK, anchor="middle", bold=True))
    p.append(text(655, 260, "Насичення [l_min, l_max] запобігає «зацементовуванню» карти", size=10, color=MUTED, anchor="middle"))
    p.append(text(655, 274, "Динамічні об'єкти зникають після серії вільних променів", size=10, color=MUTED, anchor="middle"))

    # Блок ковзного вікна
    fb_rw = fitbox(480, 305, 350, 100, "Кільцевий буфер локальної сітки (Rolling Grid):\n• Центр сітки прив'язаний до поточної позиції дрона\n• Зсув індексів за модулем N без копіювання масиву в RAM\n• Очищення старих шарів під час переміщення", size=10, fill="#f0fdf4", stroke="#86efac")
    p.append(fb_rw)

    render(os.path.join(OUT, "occupancy-grid-raycast-logodds.svg"), W, H, *p)


def fig_reactive_avoidance_tactics():
    W, H = 900, 440
    p = []

    # Заголовок
    tb_main, _, _ = textbox(450, 28, "Три тактичні реакції автопілота на виявлену перешкоду", size=13, bold=True, fill="#f8fafc", stroke=LINE)
    p.append(tb_main)

    # 3 стовпці: 1 - Stop/Hold, 2 - Horizontal VFH Bypass, 3 - Vertical Climb
    col_w = 265
    col_h = 360
    top_y = 60

    # ── КОЛОНКА 1: Екстрене гальмування (Stop / Hold) ──
    x1 = 25
    p.append(rect(x1, top_y, col_w, col_h, fill="#ffffff", stroke="#cbd5e1", rx=6))
    p.append(rect(x1, top_y, col_w, 36, fill="#fee2e2", stroke="#fca5a5", rx=6))
    p.append(text(x1 + col_w/2, top_y + 23, "1. Екстрений стоп (Braking)", size=12, color=POS, anchor="middle", bold=True))

    # Схема дрона та перешкоди
    p.append(circle(x1 + 60, top_y + 100, 14, fill="#fed7aa", stroke="#ea580c", sw=2))
    p.append(text(x1 + 60, top_y + 104, "БПЛА", size=9, color="#ea580c", anchor="middle", bold=True))
    p.append(arrow(x1 + 76, top_y + 100, x1 + 130, top_y + 100, color=POS, sw=2.5))
    p.append(text(x1 + 105, top_y + 90, "v_x", size=10, color=POS, anchor="middle", bold=True))

    # Перешкода
    p.append(rect(x1 + 190, top_y + 70, 45, 60, fill="#fecaca", stroke=POS, sw=1.5, rx=3))
    p.append(text(x1 + 212, top_y + 104, "Стіна", size=10, color=POS, anchor="middle", bold=True))

    # Дистанція гальмування
    p.append(line(x1 + 74, top_y + 125, x1 + 190, top_y + 125, color=LINE, sw=1.2))
    p.append(line(x1 + 74, top_y + 120, x1 + 74, top_y + 130, color=LINE, sw=1.2))
    p.append(line(x1 + 190, top_y + 120, x1 + 190, top_y + 130, color=LINE, sw=1.2))
    p.append(text(x1 + 132, top_y + 140, "d_dist < d_stop", size=10, color=POS, anchor="middle", bold=True))

    fb_c1 = fitbox(x1 + 12, top_y + 160, col_w - 24, 185, "Критерій спрацювання:\n• Немає вільного коридору для маневру\n• d < v² / (2 · a_max) + v · t_react + d_safe\n\nДія регулятора:\n• Миттєве скидання уставки швидкості до 0\n• Перехід у режим Loiter / Position Hold\n• Утримання координат проти зносу вітром", size=10, fill="#fef2f2", stroke="#fecaca")
    p.append(fb_c1)

    # ── КОЛОНКА 2: Горизонтальний об'їзд (VFH) ──
    x2 = 315
    p.append(rect(x2, top_y, col_w, col_h, fill="#ffffff", stroke="#cbd5e1", rx=6))
    p.append(rect(x2, top_y, col_w, 36, fill="#e0f2fe", stroke="#7dd3fc", rx=6))
    p.append(text(x2 + col_w/2, top_y + 23, "2. Горизонтальний об'їзд (VFH)", size=12, color=NEG, anchor="middle", bold=True))

    # Міні-полярна гістограма секторів
    vfh_cx = x2 + col_w / 2
    vfh_cy = top_y + 98
    p.append(circle(vfh_cx, vfh_cy, 35, fill="#f8fafc", stroke="#94a3b8", sw=1.0))
    p.append(circle(vfh_cx, vfh_cy, 6, fill="#ea580c", stroke="#ffffff", sw=1.2))

    # Сектори гістограми
    # Сектор прямо - заблокований (червоний сектор)
    p.append('<path d="M %d %d L %d %d A 35 35 0 0 1 %d %d Z" fill="#fecaca" stroke="%s" stroke-width="1.2"/>' % (
        vfh_cx, vfh_cy, vfh_cx - 15, vfh_cy - 32, vfh_cx + 15, vfh_cy - 32, POS))
    # Сектор праворуч - вільна долина (зелений сектор)
    p.append('<path d="M %d %d L %d %d A 35 35 0 0 1 %d %d Z" fill="#dcfce7" stroke="%s" stroke-width="1.2"/>' % (
        vfh_cx, vfh_cy, vfh_cx + 15, vfh_cy - 32, vfh_cx + 34, vfh_cy - 10, FIELD))

    # Вектор цілі та обраний вектор
    p.append(arrow(vfh_cx, vfh_cy, vfh_cx, vfh_cy - 48, color=MUTED, sw=1.5))
    p.append(text(vfh_cx - 20, vfh_cy - 42, "Ціль", size=9, color=MUTED, anchor="middle"))

    p.append(arrow(vfh_cx, vfh_cy, vfh_cx + 38, vfh_cy - 28, color=FIELD, sw=2.2))
    p.append(text(vfh_cx + 52, vfh_cy - 32, "θ_cmd", size=10, color=FIELD, anchor="middle", bold=True))

    fb_c2 = fitbox(x2 + 12, top_y + 160, col_w - 24, 185, "Критерій спрацювання:\n• Прямий промінь перекрито\n• Виявлено вільний сектор (долину H_k < τ)\n\nДія регулятора:\n• Мінімізація функції вартості:\n  J(θ) = c₁·|θ - θ_target| + c₂·|θ - θ_current|\n• Плавний поворот вектора швидкості\n• Збереження крейсерської швидкості", size=10, fill="#f0f9ff", stroke="#bae6fd")
    p.append(fb_c2)

    # ── КОЛОНКА 3: Набір висоти (Climb over obstacle) ──
    x3 = 605
    p.append(rect(x3, top_y, col_w, col_h, fill="#ffffff", stroke="#cbd5e1", rx=6))
    p.append(rect(x3, top_y, col_w, 36, fill="#f0fdf4", stroke="#86efac", rx=6))
    p.append(text(x3 + col_w/2, top_y + 23, "3. Набір висоти (Climb over)", size=12, color=FIELD, anchor="middle", bold=True))

    # Схема перельоту через низьку перешкоду
    c3_ox = x3 + 30
    c3_oy = top_y + 130
    # Перешкода з відомою верхньою гранню
    p.append(rect(c3_ox + 90, c3_oy - 45, 60, 45, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=2))
    p.append(text(c3_ox + 120, c3_oy - 20, "Огорожа", size=9, color="#ea580c", anchor="middle", bold=True))

    # Дрон і траєкторія вгору
    p.append(circle(c3_ox + 30, c3_oy - 10, 10, fill="#dcfce7", stroke=FIELD, sw=1.5))
    # Траєкторія набору висоти дугою
    p.append('<path d="M %d %d Q %d %d %d %d" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="3,3"/>' % (
        c3_ox + 40, c3_oy - 10, c3_ox + 90, c3_oy - 65, c3_ox + 175, c3_oy - 60, FIELD))
    p.append(arrow(c3_ox + 155, c3_oy - 61, c3_ox + 185, c3_oy - 59, color=FIELD, sw=2.2))
    p.append(text(c3_ox + 115, c3_oy - 72, "h_clearance", size=9, color=FIELD, anchor="middle", bold=True))

    fb_c3 = fitbox(x3 + 12, top_y + 160, col_w - 24, 185, "Критерій спрацювання:\n• Горизонтальний об'їзд заблокований\n• Висота перешкоди < допустимої стелі\n• Вільний простір над об'єктом за 3D-сіткою\n\nДія регулятора:\n• Уставка вертикальної швидкості v_z > 0\n• Формування кліренсу h_obs + h_margin\n• Переліт та повернення на робочий ешелон", size=10, fill="#f0fdf4", stroke="#bbf7d0")
    p.append(fb_c3)

    render(os.path.join(OUT, "reactive-avoidance-tactics.svg"), W, H, *p)


if __name__ == "__main__":
    fig_occupancy_grid_raycast_logodds()
    fig_reactive_avoidance_tactics()
    print("OK: generated figures for karta-zainiatosti-z-dalekomira")
