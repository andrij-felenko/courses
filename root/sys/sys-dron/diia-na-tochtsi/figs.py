# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми 'Дія на точці: камера, скидання, підвіс'."""

import sys
import os
import math

# Підключаємо спільну бібліотеку svgkit з кореневої папки scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_spatial_triggering_modes():
    """Фігура 1: Просторова та часова синхронізація дій корисного навантаження."""
    w, h = 960, 490
    frags = []

    col_w = 280
    gap = 30
    x_start = 30
    y_top = 50
    panel_h = 410

    modes = [
        ("Радіус досягнення", "(Acceptance Radius)", POS, [
            "• Миттєве спрацьовування на прольоті",
            "• Умова: d_2D <= R_acc та |dz| <= z_tol",
            "• Без зависання та втрати швидкості",
            "• Застосування: скид маркерів, імпульс"
        ]),
        ("Час зависання", "(Loiter / Dwell Time)", FIELD, [
            "• Вхід у сферу зупиняє траєкторію",
            "• Таймер стартує лише при |V| <= V_max",
            "• Стабілізація коливань перед дією",
            "• Застосування: точний скид, датчики"
        ]),
        ("Інтервал шляху", "(Distance Triggering)", NEG, [
            "• Спрацьовування кожні ΔS = D_int",
            "• Фільтрація радіального шуму GNSS",
            "• Блокування на віражах (|крен| > 15°)",
            "• Застосування: ортофотозйомка, LiDAR"
        ])
    ]

    for i, (title1, title2, color, bullets) in enumerate(modes):
        px = x_start + i * (col_w + gap)
        # Рамка режиму
        frags.append(rect(px, y_top, col_w, panel_h, fill="#fdfefe", stroke=color, sw=2, rx=8))
        frags.append(text(px + col_w / 2, y_top + 24, title1, size=13, color=color, bold=True))
        frags.append(text(px + col_w / 2, y_top + 40, title2, size=11, color=MUTED))

        # Візуальна схема режиму
        cx = px + col_w / 2
        cy = y_top + 130

        if i == 0:
            # Зона радіуса
            frags.append(circle(cx, cy, 48, fill="#fdecea", stroke=POS, sw=1.5))
            frags.append(line(cx - 70, cy + 30, cx + 70, cy - 30, color=LINE, sw=2))
            frags.append(arrow(cx + 35, cy - 15, cx + 70, cy - 30, color=POS, sw=2.2))
            # Точка WP
            frags.append(circle(cx, cy, 5, fill=POS, stroke=INK, sw=1.5))
            frags.append(text(cx, cy - 12, "WP (R_acc)", size=11, color=POS, bold=True))
            # Точка тригера
            frags.append(circle(cx - 25, cy + 11, 4, fill=FIELD, stroke=INK, sw=1.2))
            frags.append(text(cx - 25, cy + 28, "ТРИГЕР", size=10, color=FIELD, bold=True))
        elif i == 1:
            # Сфера зупинки та таймер
            frags.append(circle(cx, cy, 48, fill="#eafaf1", stroke=FIELD, sw=1.5))
            frags.append(circle(cx, cy, 6, fill=FIELD, stroke=INK, sw=1.5))
            frags.append(arrow(cx - 65, cy + 18, cx - 10, cy, color=LINE, sw=1.8))
            frags.append(text(cx, cy - 14, "Стоп: V < 0.2 м/с", size=11, color=FIELD, bold=True))
            frags.append(text(cx, cy + 20, "Таймер t_dwell", size=10, color=FIELD, bold=True))
            frags.append(text(cx, cy + 34, "-> ДІЯ НАВАНТАЖЕННЯ", size=9, color=INK))
        else:
            # Лінія прольоту з імпульсами камери
            frags.append(line(cx - 80, cy, cx + 80, cy, color=LINE, sw=2))
            frags.append(arrow(cx + 45, cy, cx + 80, cy, color=NEG, sw=2))
            for k in [-55, -18, 18, 55]:
                frags.append(circle(cx + k, cy, 4, fill=NEG, stroke=INK, sw=1.2))
                frags.append(line(cx + k, cy, cx + k, cy + 24, color=NEG, sw=1.5, dash="2,2"))
                frags.append(text(cx + k, cy + 36, "Кадр", size=9, color=NEG, bold=True))
            frags.append(text(cx, cy - 14, "Крок ΔS = const", size=11, color=NEG, bold=True))

        # Описовий блок пунктів
        by = y_top + 230
        for b_idx, bullet in enumerate(bullets):
            frags.append(text(px + 14, by + b_idx * 34, bullet, size=11, color=INK, anchor="start"))

    render(os.path.join(IMG_DIR, "spatial-triggering-modes.svg"), w, h, *frags,
           title="Просторові та часові механізми синхронізації дій на точці")


def fig_gimbal_roi_geometry():
    """Фігура 2: Геометрія наведення підвісу на точку інтересу (ROI)."""
    w, h = 960, 480
    frags = []

    # Ліва частина: Просторова векторна діаграма
    frags.append(rect(30, 45, 450, 405, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(255, 74, "Векторний трикутник наведення (NED Frame)", size=13, color=INK, bold=True))

    # БПЛА позиція
    uav_x, uav_y = 120, 150
    frags.append(circle(uav_x, uav_y, 14, fill="#eaf0fd", stroke=NEG, sw=2))
    frags.append(text(uav_x, uav_y + 4, "БПЛА", size=10, color=NEG, bold=True))
    frags.append(text(uav_x, uav_y - 22, "P_uav (X_u, Y_u, Z_u)", size=11, color=INK, bold=True))

    # Точка підвісу з урахуванням lever-arm
    gimbal_x, gimbal_y = 150, 175
    frags.append(arrow(uav_x, uav_y, gimbal_x, gimbal_y, color=MUTED, sw=1.5))
    frags.append(circle(gimbal_x, gimbal_y, 6, fill=POS, stroke=INK, sw=1.5))
    frags.append(text(gimbal_x + 35, gimbal_y - 8, "r_mount", size=10, color=MUTED, italic=True))

    # Ціль на землі (ROI)
    roi_x, roi_y = 380, 360
    frags.append(circle(roi_x, roi_y, 12, fill="#fdecea", stroke=POS, sw=2))
    frags.append(text(roi_x, roi_y + 4, "ROI", size=10, color=POS, bold=True))
    frags.append(text(roi_x, roi_y + 24, "P_target (X_t, Y_t, Z_t)", size=11, color=POS, bold=True))

    # Головний вектор візування (Line of Sight)
    frags.append(arrow(gimbal_x, gimbal_y, roi_x - 10, roi_y - 10, color=POS, sw=2.5))
    frags.append(text(270, 245, "Вектор візування ΔP_ned", size=12, color=POS, bold=True))

    # Проекції на горизонталь та вертикаль
    frags.append(line(gimbal_x, gimbal_y, roi_x, gimbal_y, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(line(roi_x, gimbal_y, roi_x, roi_y, color=MUTED, sw=1.5, dash="4,4"))
    frags.append(text(280, gimbal_y - 10, "Горизонтальна дальність d_xy", size=11, color=MUTED))
    frags.append(text(roi_x + 10, (gimbal_y + roi_y) / 2, "ΔZ (Висота)", size=11, color=MUTED, anchor="start"))

    # Дуга кута тангажу (Pitch)
    frags.append(text(gimbal_x + 65, gimbal_y + 22, "Кут тангажу θ_pitch", size=11, color=POS, bold=True))

    # Права частина: Формули та розклад систем координат
    frags.append(rect(500, 45, 430, 405, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(715, 74, "Трансформація та кінематика підвісу", size=13, color=INK, bold=True))

    steps = [
        ("1. Вектор зміщення до цілі:", "ΔP = P_target - (P_uav + R_b^ned · r_mount)"),
        ("2. Кут азимуту (Yaw у системі NED):", "Ψ_target = atan2(ΔY_ned, ΔX_ned)"),
        ("3. Кут нахилу (Pitch від горизонту):", "θ_target = atan2(-ΔZ_ned, √(ΔX² + ΔY²))"),
        ("4. Компенсація крену/курсу носія:", "q_gimbal_cmd = q_uav_inv ⊗ q_target_ned"),
        ("5. Обмеження швидкості перекидання:", "dθ/dt <= SlewRate_max (захист двигунів)")
    ]

    for idx, (head, eq) in enumerate(steps):
        sy = 110 + idx * 64
        frags.append(text(520, sy, head, size=11, color=INK, anchor="start", bold=True))
        frags.append(rect(520, sy + 10, 390, 32, fill="#f4f6f8", stroke=NEG, sw=1.2, rx=4))
        frags.append(text(715, sy + 31, eq, size=11, color=INK))

    render(os.path.join(IMG_DIR, "gimbal-roi-geometry.svg"), w, h, *frags,
           title="Кінематична схема розрахунку кутів підвісу для утримання точки інтересу (ROI)")


def fig_payload_drop_mechanisms():
    """Фігура 3: Механізми скидання корисного навантаження із замкненим контуром підтвердження."""
    w, h = 960, 480
    frags = []

    # Ліва колонка: Сервопривід із кінцевиком
    frags.append(rect(30, 45, 430, 405, fill="#fdfefe", stroke=FIELD, sw=2, rx=8))
    frags.append(text(245, 74, "Сервозамок + Давач кінцевого положення", size=13, color=FIELD, bold=True))

    # Схема сервоприводу та ригеля
    frags.append(rect(60, 110, 110, 75, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(115, 142, "Сервопривід", size=11, color=INK, bold=True))
    frags.append(text(115, 158, "(PWM / CAN)", size=10, color=MUTED))
    frags.append(line(170, 148, 260, 148, color=LINE, sw=4)) # Тяга/ригель
    frags.append(text(215, 138, "Ригель замка", size=10, color=MUTED))

    # Кінцевик (Limit Switch / Hall sensor)
    frags.append(circle(275, 148, 12, fill="#fdecea", stroke=POS, sw=1.5))
    frags.append(text(275, 152, "SW", size=10, color=POS, bold=True))
    frags.append(text(275, 124, "Кінцевик відкрито", size=10, color=POS, bold=True))

    # Підвішений вантаж
    frags.append(rect(200, 175, 90, 55, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    frags.append(text(245, 198, "Вантаж", size=11, color=INK, bold=True))
    frags.append(text(245, 214, "(Вушко)", size=10, color=MUTED))
    frags.append(arrow(245, 235, 245, 268, color=POS, sw=2))
    frags.append(text(245, 284, "Гравітаційне скидання", size=10, color=POS, bold=True))

    # Блок логіки зворотного зв'язку сервозамка
    fb_lines = [
        "1. Команда відкриття PWM 1000 мкс -> 2000 мкс",
        "2. Запуск таймауту контролю руху (300 мс)",
        "3. Контакт кінцевика замикає пін GPIO на GND",
        "4. Підтвердження: статус STATUS_DROPPED",
        "5. Якщо кінцевик не спрацював -> RETRY / ALARM"
    ]
    for idx, l in enumerate(fb_lines):
        frags.append(text(45, 312 + idx * 24, l, size=11, color=INK, anchor="start"))

    # Права колонка: Соленоїдний замок із контролем струму шунта
    frags.append(rect(500, 45, 430, 405, fill="#fdfefe", stroke=POS, sw=2, rx=8))
    frags.append(text(715, 74, "Соленоїдний скидач + Давач струму шунта", size=13, color=POS, bold=True))

    # Схема котушки соленоїда та польового транзистора
    frags.append(rect(530, 110, 110, 75, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    frags.append(text(585, 142, "Котушка", size=11, color=INK, bold=True))
    frags.append(text(585, 158, "Соленоїда", size=10, color=MUTED))
    frags.append(line(640, 148, 710, 148, color=POS, sw=5)) # Сердечник
    frags.append(text(675, 138, "Сердечник", size=10, color=POS))

    # Ключ MOSFET та шунт
    frags.append(rect(730, 120, 80, 40, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    frags.append(text(770, 145, "MOSFET", size=10, color=NEG, bold=True))
    frags.append(rect(830, 120, 70, 40, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=4))
    frags.append(text(865, 145, "Шунт R_s", size=10, color=INK, bold=True))

    # Графік імпульсу струму
    frags.append(rect(530, 205, 370, 80, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    frags.append(text(545, 224, "Профіль струму I(t):", size=10, color=MUTED, anchor="start"))
    # Крива струму: стрибок -> втягування сердечника -> спад
    frags.append(line(550, 268, 590, 268, color=LINE, sw=1.5))
    frags.append(line(590, 268, 610, 230, color=POS, sw=2)) # Наростання
    frags.append(line(610, 230, 650, 240, color=POS, sw=2)) # Рух сердечника (провал індуктивності)
    frags.append(line(650, 240, 680, 226, color=POS, sw=2)) # Упор
    frags.append(line(680, 226, 690, 268, color=LINE, sw=1.5)) # Відсічка імпульсу
    frags.append(text(640, 263, "Втягування (ΔI)", size=9, color=POS, bold=True))
    frags.append(text(780, 240, "I_peak: 4..8 А", size=10, color=INK))
    frags.append(text(780, 256, "Час: 40..80 мс", size=10, color=MUTED))

    # Пояснення логіки соленоїда
    sol_lines = [
        "1. Короткий імпульс на затвор MOSFET (50 мс)",
        "2. АЦП вимірює напругу падіння на шунті R_s",
        "3. Відсутність струму -> обрив ланцюга / запобіжник",
        "4. Відсутність провалу індуктивності -> клин сердечника",
        "5. Захист від перегріву: апаратне обмеження тривалості"
    ]
    for idx, l in enumerate(sol_lines):
        frags.append(text(515, 312 + idx * 24, l, size=11, color=INK, anchor="start"))

    render(os.path.join(IMG_DIR, "payload-drop-mechanisms.svg"), w, h, *frags,
           title="Електромеханічні механізми скидання та контури апаратного підтвердження")


def fig_payload_subsystem_architecture():
    """Фігура 4: Архітектура підсистеми керування корисним навантаженням."""
    w, h = 960, 480
    frags = []

    # Ліва колонка: Джерела команд місії (Mission Execution Layer)
    frags.append(rect(30, 45, 230, 405, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(145, 70, "Планувальник місії", size=12, color=INK, bold=True))
    frags.append(text(145, 86, "(Mission Planner)", size=10, color=MUTED))

    m_items = [
        ("NAV_WAYPOINT", "(+ Дія на точці)", POS),
        ("DO_SET_ROI_LOCATION", "(Координати цілі)", NEG),
        ("DO_SET_CAM_TRIGG_DIST", "(Інтервал зйомки)", FIELD),
        ("DO_GRIPPER / DROP", "(Команда скидання)", POS)
    ]
    for idx, (name1, name2, col) in enumerate(m_items):
        box_y = 115 + idx * 76
        frags.append(rect(45, box_y, 200, 52, fill="#f4f6f8", stroke=col, sw=1.5, rx=6))
        frags.append(text(145, box_y + 22, name1, size=10, color=col, bold=True))
        frags.append(text(145, box_y + 38, name2, size=9, color=MUTED))

    # Середня колонка: Підсистема корисного навантаження (Payload Executive Manager)
    frags.append(rect(290, 45, 380, 405, fill="#fdfefe", stroke=NEG, sw=2, rx=8))
    frags.append(text(480, 70, "Менеджер корисного навантаження", size=13, color=NEG, bold=True))
    frags.append(text(480, 86, "(Payload Manager)", size=10, color=MUTED))

    exec_blocks = [
        ("Синхронізатор положення (Spatial Trigger Engine)", "Облік d_2D, dz, швидкості V та кутів крену"),
        ("Контролер наведення підвісу (ROI Pointing Controller)", "Перетворення NED -> Body -> Gimbal, фільтрація кутів"),
        ("Автомат скидання вантажу (Payload Drop State Machine)", "Керування імпульсом, моніторинг струму та кінцевика"),
        ("Формувач зворотного зв'язку (Feedback Event Dispatcher)", "Часові мітки затвора, геоприв'язка, MAVLink ACK")
    ]
    for idx, (title, desc) in enumerate(exec_blocks):
        frags.append(rect(305, 115 + idx * 76, 350, 56, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
        frags.append(text(480, 137 + idx * 76, title, size=11, color=NEG, bold=True))
        frags.append(text(480, 155 + idx * 76, desc, size=9, color=MUTED))

    # Права колонка: Апаратні виконавчі модулі та лог
    frags.append(rect(700, 45, 230, 405, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(815, 70, "Апаратний рівень", size=12, color=INK, bold=True))
    frags.append(text(815, 86, "та Реєстрація", size=10, color=MUTED))

    hw_items = [
        ("Стабілізований підвіс", "(CAN / UART Gimbal)", NEG),
        ("Затвор камери", "(HotShoe Sync)", FIELD),
        ("Серво/Соленоїд", "(Power Switch / Shunt)", POS),
        ("Бортовий лог", "(ULog / MAVLink)", LINE)
    ]
    for idx, (name1, name2, col) in enumerate(hw_items):
        box_y = 115 + idx * 76
        frags.append(rect(715, box_y, 200, 52, fill="#f4f6f8", stroke=col, sw=1.5, rx=6))
        frags.append(text(815, box_y + 22, name1, size=10, color=col, bold=True))
        frags.append(text(815, box_y + 38, name2, size=9, color=MUTED))

    # Сполучні стрілки між шарами
    for idx in range(4):
        y_pos = 141 + idx * 76
        frags.append(arrow(248, y_pos, 288, y_pos, color=LINE, sw=1.5))
        frags.append(arrow(658, y_pos, 698, y_pos, color=LINE, sw=1.5))

    render(os.path.join(IMG_DIR, "payload-subsystem-architecture.svg"), w, h, *frags,
           title="Архітектура підсистеми корисного навантаження у складі автопілота")


if __name__ == "__main__":
    fig_spatial_triggering_modes()
    fig_gimbal_roi_geometry()
    fig_payload_drop_mechanisms()
    fig_payload_subsystem_architecture()
    print("Всі 4 фігури успішно згенеровано у %s" % IMG_DIR)
