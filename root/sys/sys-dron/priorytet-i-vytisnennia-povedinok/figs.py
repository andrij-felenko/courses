# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Пріоритет і витіснення поведінок».
Генерує SVG у ./img/ за допомогою svgkit.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


def fig_subsumption_hierarchy():
    """Фігура 1: Ієрархія шарів витіснення (Subsumption Architecture) в автопілоті."""
    w, h = 1040, 600
    p = []

    # Заголовок
    p.append(text(w / 2, 28, "Ієрархія шарів витіснення (Subsumption) та арбітраж поведінок", size=16, bold=True))

    col_sensor_x = 135
    col_layer_x = 440
    col_bus_x = 730
    col_out_x = 925

    # Заголовки стовпчиків
    p.append(text(col_sensor_x, 60, "СЕНСОРНІ ПОТОКИ", size=11, bold=True, color=MUTED))
    p.append(text(col_layer_x, 60, "РІВНІ ПОВЕДІНОК (ПРОЦЕСИ)", size=11, bold=True, color=MUTED))
    p.append(text(col_bus_x, 60, "АРБІТРАЖ І ШИНА ВИТІСНЕННЯ", size=11, bold=True, color=MUTED))
    p.append(text(col_out_x, 60, "УСТАВКИ Й АКТУАТОРИ", size=11, bold=True, color=MUTED))

    # Розділювальна лінія під заголовками
    p.append(line(40, 72, w - 40, 72, color="#e5e7eb", sw=1.2))

    layers = [
        {
            "lvl": "Рівень 4 (Prio 100 — Найвищий)",
            "name": "Аварійний захист (Failsafe)\nMotor fail, Low battery, Loss of link",
            "sensor": "Напруга батареї, Watchdog, RC Link",
            "fill": "#fdecea", "stroke": POS, "color": POS
        },
        {
            "lvl": "Рівень 3 (Prio 80)",
            "name": "Реактивне уникнення (Avoidance)\nEmergency climb, Geofence breach",
            "sensor": "LIDAR, Радар, ESDF карта, GNSS",
            "fill": "#fef3c7", "stroke": "#d97706", "color": "#b45309"
        },
        {
            "lvl": "Рівень 2 (Prio 60)",
            "name": "Локальне перепланування (Local Plan)\nDWA / TEB обхід, Terrain follow",
            "sensor": "Локальна сітка зайнятості, Далекомір",
            "fill": "#fef9c3", "stroke": "#ca8a04", "color": "#854d0e"
        },
        {
            "lvl": "Рівень 1 (Prio 40)",
            "name": "Місія та навігація (Mission)\nWaypoint cruise, Survey grid, Orbit",
            "sensor": "План місії, GNSS траєкторія",
            "fill": "#eaf0fd", "stroke": NEG, "color": NEG
        },
        {
            "lvl": "Рівень 0 (Prio 10 — Базовий)",
            "name": "Базове утримання (Loiter / Idle)\nPosition hold, Manual assist",
            "sensor": "Поточний стан EKF [p, v, q]",
            "fill": "#e9f7ef", "stroke": FIELD, "color": FIELD
        }
    ]

    y_start = 115
    dy = 88

    for i, lyr in enumerate(layers):
        cy = y_start + i * dy

        # 1. Сенсорний блок
        fr_s, ws, hs = textbox(col_sensor_x, cy, lyr["sensor"], size=10, pad=8, fill="#f8fafc", stroke="#cbd5e1", color=INK, min_w=200)
        p.append(fr_s)

        # Стрілка сенсор -> рівень поведінки
        p.append(arrow(col_sensor_x + ws / 2, cy, col_layer_x - 150, cy, color=MUTED, sw=1.3))

        # 2. Блок поведінки
        p.append(rect(col_layer_x - 150, cy - 34, 300, 68, fill=lyr["fill"], stroke=lyr["stroke"], sw=1.5, rx=5))
        p.append(text(col_layer_x - 138, cy - 16, lyr["lvl"], size=10, bold=True, color=lyr["color"], anchor="start"))
        lines = lyr["name"].split("\n")
        p.append(text(col_layer_x - 138, cy + 2, lines[0], size=11, bold=True, color=INK, anchor="start"))
        p.append(text(col_layer_x - 138, cy + 19, lines[1], size=10, color=MUTED, anchor="start"))

        # Стрілка рівень поведінки -> шина арбітражу
        p.append(arrow(col_layer_x + 150, cy, col_bus_x - 70, cy, color=lyr["stroke"], sw=1.5))

    # Вертикальний блок арбітражу
    arb_top = 85
    arb_h = 445
    p.append(rect(col_bus_x - 70, arb_top, 140, arb_h, fill="#f1f5f9", stroke="#475569", sw=1.8, rx=6))
    p.append(text(col_bus_x, arb_top + 28, "АРБІТР", size=12, bold=True, color=INK))
    p.append(text(col_bus_x, arb_top + 45, "ВИТІСНЕННЯ", size=11, bold=True, color=INK))

    p.append(line(col_bus_x - 55, arb_top + 62, col_bus_x + 55, arb_top + 62, color="#94a3b8", sw=1))

    p.append(text(col_bus_x, arb_top + 85, "Перевірка пріоритету", size=9.5, bold=True, color="#334155"))
    p.append(text(col_bus_x, arb_top + 104, "Виклик halt()", size=10, color=POS, bold=True))
    p.append(text(col_bus_x, arb_top + 122, "Збереження стану", size=9.5, color=MUTED))

    p.append(line(col_bus_x - 55, arb_top + 140, col_bus_x + 55, arb_top + 140, color="#94a3b8", sw=1))

    p.append(text(col_bus_x, arb_top + 166, "БЕЗПОШТОВХОВИЙ", size=10, bold=True, color=NEG))
    p.append(text(col_bus_x, arb_top + 184, "ЗГЛАДЖУВАЧ", size=10, bold=True, color=NEG))
    p.append(text(col_bus_x, arb_top + 206, "Фільтр стрибків уставки", size=9.5, color=MUTED))
    p.append(text(col_bus_x, arb_top + 224, "Обмеження ривка j_max", size=9.5, color=MUTED))
    p.append(text(col_bus_x, arb_top + 242, "Неперервність [p, v, a]", size=9.5, color=MUTED))

    p.append(line(col_bus_x - 55, arb_top + 260, col_bus_x + 55, arb_top + 260, color="#94a3b8", sw=1))
    p.append(text(col_bus_x, arb_top + 288, "Шина придушення:", size=9.5, bold=True, color=INK))
    p.append(text(col_bus_x, arb_top + 308, "Inhibition Bus", size=9.5, color=POS, bold=True))
    p.append(text(col_bus_x, arb_top + 328, "Перехоплення каналів", size=9.5, color=MUTED))
    p.append(text(col_bus_x, arb_top + 348, "Roll / Pitch / Thrust", size=9.5, color=MUTED))

    # Стрілки з арбітра до вихідних блоків
    out_y1 = 200
    out_y2 = 380
    p.append(arrow(col_bus_x + 70, out_y1, col_out_x - 70, out_y1, color=INK, sw=1.8))
    p.append(arrow(col_bus_x + 70, out_y2, col_out_x - 70, out_y2, color=INK, sw=1.8))

    fr_o1, wo1, ho1 = textbox(col_out_x, out_y1, "Неперервні уставки\n[p_sp, v_sp, a_sp, yaw_sp]", size=10, pad=8, fill="#eef2f7", stroke=NEG, color=INK, min_w=150)
    p.append(fr_o1)

    fr_o2, wo2, ho2 = textbox(col_out_x, out_y2, "Контури кутів і тяги\nAttitude Rate / Mixer", size=10, pad=8, fill="#eef2f7", stroke=FIELD, color=INK, min_w=150)
    p.append(fr_o2)

    p.append(arrow(col_out_x, out_y1 + ho1 / 2, col_out_x, out_y2 - ho2 / 2, color=MUTED, sw=1.4))

    # Нижній рядок
    bot_y = 565
    fr_b, wb, hb = textbox(w / 2, bot_y, "Вищий рівень миттєво перериває нижчий через halt(), але уставки передаються через безпоштовховий фільтр", size=11, pad=8, fill="#f8fafc", stroke="#94a3b8", color=INK, bold=True)
    p.append(fr_b)

    render("img/behavior-subsumption-hierarchy.svg", w, h, *p)


def fig_bumpless_takeover():
    """Фігура 2: Часова діаграма витіснення та безпоштовхового перехоплення (Bumpless Takeover)."""
    w, h = 1000, 560
    p = []

    p.append(text(w / 2, 28, "Часова діаграма витіснення місії та безпоштовхового перехоплення (Bumpless Takeover)", size=16, bold=True))

    ox = 140
    oy_b1 = 120   # Доріжка місії
    oy_b2 = 180   # Доріжка уникнення
    oy_v = 320    # Графік швидкості
    oy_a = 465    # Графік прискорення
    ax_w = 800
    ax_end = ox + ax_w

    # Вертикальні мітки часу
    t_ev = ox + 220   # t1: Obstacle detected
    t_clr = ox + 540  # t2: Obstacle cleared
    t_res = ox + 700  # t3: Mission resume finished

    # Пунктирні лінії розділу фаз по всій висоті
    p.append(line(t_ev, 55, t_ev, 505, color="#f87171", sw=1.5, dash="4,4"))
    p.append(line(t_clr, 55, t_clr, 505, color="#facc15", sw=1.5, dash="4,4"))
    p.append(line(t_res, 55, t_res, 505, color="#4ade80", sw=1.5, dash="4,4"))

    # Написи фаз угорі
    p.append(text((ox + t_ev) / 2, 70, "Фаза 1: Cruise місія", size=10.5, bold=True, color=NEG))
    p.append(text((t_ev + t_clr) / 2, 70, "Фаза 2: Collision Avoidance (Витіснення)", size=10.5, bold=True, color=POS))
    p.append(text((t_clr + t_res) / 2, 70, "Фаза 3: Плавне повернення", size=10.5, bold=True, color="#b45309"))
    p.append(text((t_res + ax_end) / 2, 70, "Фаза 4: Відновлена місія", size=10.5, bold=True, color=NEG))

    # 1. Доріжка 1: Поведінка місії (Waypoint Cruise)
    p.append(text(ox - 15, oy_b1, "Waypoint Cruise", size=10.5, bold=True, anchor="end"))

    # Активний стан місії до t_ev
    p.append(rect(ox + 5, oy_b1 - 14, t_ev - ox - 10, 28, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
    p.append(text((ox + t_ev) / 2, oy_b1 + 4, "RUNNING (v = 15 м/с)", size=10, bold=True, color=NEG))

    # Призупинений стан місії (SUSPENDED) від t_ev до t_clr
    p.append(rect(t_ev + 5, oy_b1 - 14, t_clr - t_ev - 10, 28, fill="#f1f5f9", stroke=MUTED, sw=1.2, rx=4))
    p.append(text((t_ev + t_clr) / 2, oy_b1 + 4, "SUSPENDED (Збережено чекпоінт)", size=9.5, italic=True, color=MUTED))

    # Відновлений стан місії від t_clr
    p.append(rect(t_clr + 5, oy_b1 - 14, ax_end - t_clr - 10, 28, fill="#dbeafe", stroke=NEG, sw=1.5, rx=4))
    p.append(text((t_clr + ax_end) / 2, oy_b1 + 4, "RESUMED (Продовження місії)", size=10, bold=True, color=NEG))

    # 2. Доріжка 2: Поведінка безпеки (Collision Avoidance)
    p.append(text(ox - 15, oy_b2, "Collision Avoid", size=10.5, bold=True, anchor="end"))

    # Неактивний стан
    p.append(text((ox + t_ev) / 2, oy_b2 + 4, "INACTIVE", size=9.5, color=MUTED))
    p.append(text((t_clr + ax_end) / 2, oy_b2 + 4, "INACTIVE", size=9.5, color=MUTED))

    # Активний стан витіснення
    p.append(rect(t_ev + 5, oy_b2 - 14, t_clr - t_ev - 10, 28, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    p.append(text((t_ev + t_clr) / 2, oy_b2 + 4, "ACTIVE (Гальмування та обхід)", size=10, bold=True, color=POS))

    # 3. Графік швидкості v_x (м/с)
    p.append(text(ox - 15, oy_v - 15, "Уставка", size=11, bold=True, anchor="end"))
    p.append(text(ox - 15, oy_v + 1, "швидкості v_x", size=11, bold=True, anchor="end"))
    p.append(arrow(ox, oy_v + 45, ox, oy_v - 65, color=INK, sw=1.5))
    p.append(arrow(ox, oy_v + 25, ax_end, oy_v + 25, color=INK, sw=1.5))
    p.append(text(ox - 8, oy_v - 45, "+15 м/с", size=9.5, color=MUTED, anchor="end"))
    p.append(text(ox - 8, oy_v + 25, "0", size=9.5, color=MUTED, anchor="end"))

    # Стрибок (пунктир)
    p.append(line(ox, oy_v - 45, t_ev, oy_v - 45, color=MUTED, sw=1.2))
    p.append(line(t_ev, oy_v - 45, t_ev, oy_v + 18, color="#f87171", sw=1.5, dash="3,3"))
    p.append(line(t_ev, oy_v + 18, t_clr, oy_v + 18, color="#f87171", sw=1.5, dash="3,3"))
    p.append(text(t_ev + 75, oy_v + 38, "Ступінчастий стрибок (небезпечно)", size=9.5, color=POS))

    # Плавний перехід (Bumpless)
    p.append(line(ox, oy_v - 45, t_ev, oy_v - 45, color=NEG, sw=2.5))
    p.append(line(t_ev, oy_v - 45, t_ev + 80, oy_v + 15, color=POS, sw=2.5))
    p.append(line(t_ev + 80, oy_v + 15, t_clr, oy_v + 15, color=POS, sw=2.5))
    p.append(line(t_clr, oy_v + 15, t_res, oy_v - 45, color=FIELD, sw=2.5))
    p.append(line(t_res, oy_v - 45, ax_end, oy_v - 45, color=NEG, sw=2.5))

    # 4. Графік прискорення a_x
    p.append(text(ox - 15, oy_a - 10, "Прискорення a_x", size=10.5, bold=True, anchor="end"))
    p.append(text(ox - 15, oy_a + 6, "(тяга моторів)", size=10.5, bold=True, anchor="end"))
    p.append(arrow(ox, oy_a + 35, ox, oy_a - 45, color=INK, sw=1.5))
    p.append(arrow(ox, oy_a, ax_end, oy_a, color=INK, sw=1.5))
    p.append(text(ox - 8, oy_a - 28, "+a_max", size=9.5, color=MUTED, anchor="end"))
    p.append(text(ox - 8, oy_a + 28, "-a_max", size=9.5, color=MUTED, anchor="end"))

    # Межі насичення
    p.append(line(ox, oy_a - 28, ax_end, oy_a - 28, color="#fca5a5", sw=1, dash="4,4"))
    p.append(line(ox, oy_a + 28, ax_end, oy_a + 28, color="#fca5a5", sw=1, dash="4,4"))
    p.append(text(ax_end - 8, oy_a - 32, "Поріг насичення актуаторів", size=9.5, color=POS, anchor="end"))

    # Хвиля прискорення
    p.append(line(ox, oy_a, t_ev, oy_a, color=MUTED, sw=1.5))
    p.append(line(t_ev, oy_a, t_ev + 40, oy_a + 22, color=POS, sw=2))
    p.append(line(t_ev + 40, oy_a + 22, t_ev + 80, oy_a, color=POS, sw=2))
    p.append(line(t_ev + 80, oy_a, t_clr, oy_a, color=MUTED, sw=1.5))
    p.append(line(t_clr, oy_a, t_clr + 80, oy_a - 22, color=FIELD, sw=2))
    p.append(line(t_clr + 80, oy_a - 22, t_res, oy_a, color=FIELD, sw=2))
    p.append(line(t_res, oy_a, ax_end, oy_a, color=MUTED, sw=1.5))

    # Підписи подій
    p.append(text(t_ev, oy_a + 46, "t1: Виявлено перешкоду", size=10, bold=True, color=POS))
    p.append(text(t_clr, oy_a + 46, "t2: Загрозу усунено", size=10, bold=True, color="#b45309"))
    p.append(text(t_res, oy_a + 46, "t3: Відновлено курс", size=10, bold=True, color=FIELD))

    render("img/preemption-bumpless-takeover.svg", w, h, *p)


if __name__ == "__main__":
    fig_subsumption_hierarchy()
    fig_bumpless_takeover()
    print("OK: generated 2 figures in img/")
