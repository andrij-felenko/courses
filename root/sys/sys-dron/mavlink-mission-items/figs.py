# -*- coding: utf-8 -*-
"""Генератор SVG-ілюстрацій для теми mavlink-mission-items."""

import os
import sys

# Підключення svgkit із scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_mission_item_int_layout():
    """Двійкова структура кадру MISSION_ITEM_INT (#73) у пам'яті (38 байтів)."""
    dw, dh = 880, 460
    body = []
    
    # Заголовок
    body.append(text(dw / 2, 28, "Двійкова структура корисного навантаження MISSION_ITEM_INT (#73, 38 байтів)", size=16, bold=True))
    body.append(text(dw / 2, 48, "Розподіл полів за правилом вирівнювання MAVLink v2 (від 4-байтових до 1-байтових)", size=12, color=MUTED))
    
    # Сітка полів повідомлення
    # Рядок 1: param1 .. param4 (float32, 4 байти кожен = 16 байтів)
    y1 = 80
    body.append(text(60, y1 + 22, "0..15 б:", size=12, bold=True, anchor="start", color=MUTED))
    
    fields_r1 = [
        ("param1 (float)", "Параметр 1 (час / кут)", 175, POS),
        ("param2 (float)", "Параметр 2 (радіус прийому)", 175, POS),
        ("param3 (float)", "Параметр 3 (радіус прольоту)", 175, POS),
        ("param4 (float)", "Параметр 4 (курс / кут)", 175, POS),
    ]
    x_cur = 140
    for title, desc, w, col in fields_r1:
        body.append(rect(x_cur, y1, w, 44, fill="#fdf2f0", stroke=col, sw=1.5, rx=4))
        body.append(text(x_cur + w / 2, y1 + 18, title, size=13, bold=True, color=col))
        body.append(text(x_cur + w / 2, y1 + 34, desc, size=10, color=MUTED))
        x_cur += w + 6
        
    # Рядок 2: x, y, z (int32, int32, float = 12 байтів)
    y2 = 145
    body.append(text(60, y2 + 22, "16..27 б:", size=12, bold=True, anchor="start", color=MUTED))
    fields_r2 = [
        ("x / Latitude (int32)", "Широта (градуси × 10⁷) або Local X", 235, NEG),
        ("y / Longitude (int32)", "Довгота (градуси × 10⁷) або Local Y", 235, NEG),
        ("z / Altitude (float)", "Висота в метрах (AMSL / Rel / AGL)", 248, FIELD),
    ]
    x_cur = 140
    for title, desc, w, col in fields_r2:
        body.append(rect(x_cur, y2, w, 44, fill="#eff6ff" if col == NEG else "#f0fdf4", stroke=col, sw=1.5, rx=4))
        body.append(text(x_cur + w / 2, y2 + 18, title, size=13, bold=True, color=col))
        body.append(text(x_cur + w / 2, y2 + 34, desc, size=10, color=MUTED))
        x_cur += w + 6

    # Рядок 3: seq, command (uint16 = 4 байти)
    y3 = 210
    body.append(text(60, y3 + 22, "28..31 б:", size=12, bold=True, anchor="start", color=MUTED))
    fields_r3 = [
        ("seq (uint16)", "Індекс елемента в місії (0 .. 65535)", 356, INK),
        ("command (uint16)", "Код дії (перелік MAV_CMD_NAV / DO / COND)", 362, INK),
    ]
    x_cur = 140
    for title, desc, w, col in fields_r3:
        body.append(rect(x_cur, y3, w, 44, fill=FILL, stroke=col, sw=1.5, rx=4))
        body.append(text(x_cur + w / 2, y3 + 18, title, size=13, bold=True, color=col))
        body.append(text(x_cur + w / 2, y3 + 34, desc, size=10, color=MUTED))
        x_cur += w + 6

    # Рядок 4: 1-байтові поля (6 байтів = 32..37 б)
    y4 = 275
    body.append(text(60, y4 + 22, "32..37 б:", size=12, bold=True, anchor="start", color=MUTED))
    fields_r4 = [
        ("target_system", "Sys ID", 115),
        ("target_component", "Comp ID", 115),
        ("frame", "MAV_FRAME", 125),
        ("current", "1=Активний", 115),
        ("autocontinue", "1=Автоперехід", 115),
        ("mission_type", "0=Mission", 115),
    ]
    x_cur = 140
    for title, desc, w in fields_r4:
        body.append(rect(x_cur, y4, w, 44, fill=FILL, stroke=LINE, sw=1.5, rx=4))
        body.append(text(x_cur + w / 2, y4 + 18, title, size=12, bold=True, color=INK))
        body.append(text(x_cur + w / 2, y4 + 34, desc, size=10, color=MUTED))
        x_cur += w + 6

    # Пояснювальний блок унизу
    y5 = 345
    box_w = 724
    body.append(rect(140, y5, box_w, 95, fill="#f8fafc", stroke=MUTED, sw=1, rx=6))
    body.append(text(155, y5 + 20, "Ключові властивості протокольного пакування:", size=12, bold=True, anchor="start", color=INK))
    body.append(text(155, y5 + 40, "• Масштабування географічних координат: Lat/Lon множаться на 10⁷ (дискретність ≈ 1.11 см на екваторі замість ~1.7 м у float32).", size=11, anchor="start", color=INK))
    body.append(text(155, y5 + 60, "• Поле frame визначає спосіб тлумачення висоти z (AMSL / відносно точки старту / відносно рельєфу AGL / локальні метри).", size=11, anchor="start", color=INK))
    body.append(text(155, y5 + 80, "• Порядок полів у кадрі MAVLink автоматично сортується генератором за спаданням розміру типів для запобігання паддінгу.", size=11, anchor="start", color=INK))

    render(os.path.join(OUT_DIR, "mission-item-int-layout.svg"), dw, dh, "".join(body))


def fig_coordinate_frames():
    """Порівняння систем відліку висоти MAV_FRAME у MAVLink."""
    dw, dh = 860, 480
    body = []
    
    body.append(text(dw / 2, 28, "Системи відліку координат і висот у MAVLink (MAV_FRAME)", size=16, bold=True))
    body.append(text(dw / 2, 48, "Інтерпретація висоти точки z залежно від обраної системи відліку", size=12, color=MUTED))

    # Схема рельєфу та рівнів
    # 1. Рівень моря (AMSL - 0m)
    y_sea = 400
    body.append(line(80, y_sea, 780, y_sea, color=NEG, sw=2, dash="6,4"))
    body.append(text(85, y_sea - 8, "Середній рівень моря (AMSL = 0 м, геоїд EGM96 / WGS84)", size=11, color=NEG, anchor="start", bold=True))

    # 2. Рельєф (крива)
    terrain_path = "M 80,360 Q 240,340 360,260 T 560,200 T 780,290"
    body.append(f'<path d="{terrain_path}" fill="none" stroke="{LINE}" stroke-width="2.5"/>')
    # Заливка під рельєфом
    terrain_fill = f'<path d="{terrain_path} L 780,440 L 80,440 Z" fill="#f1f5f9" stroke="none"/>'
    body.insert(len(body)-1, terrain_fill)
    body.append(text(680, 260, "Рельєф місцевості", size=12, color=LINE, bold=True))

    # 3. Точка старту (Home) на рельєфі
    hx, hy = 200, 345
    body.append(circle(hx, hy, 6, fill=POS, stroke=POS))
    body.append(text(hx, hy + 22, "Точка старту (Home)", size=11, bold=True, color=POS))
    body.append(text(hx, hy + 36, "H_home = 120 м AMSL", size=10, color=MUTED))

    # Горизонтальна лінія відліку Home
    body.append(line(hx - 20, hy, 780, hy, color=POS, sw=1.5, dash="4,4"))
    body.append(text(775, hy - 6, "Рівень точки старту (Rel Alt = 0 м)", size=11, color=POS, anchor="end"))

    # 4. Дрон у точці польоту над горою
    dx, dy = 500, 110
    # Зображення дрона (квадрокоптер схематично)
    body.append(line(dx - 18, dy - 8, dx + 18, dy + 8, color=INK, sw=2))
    body.append(line(dx - 18, dy + 8, dx + 18, dy - 8, color=INK, sw=2))
    body.append(circle(dx, dy, 7, fill=FIELD, stroke=INK, sw=1.5))
    body.append(text(dx, dy - 16, "Позиція дрона в точці місії", size=12, bold=True, color=INK))

    # Точка на рельєфі прямо під дроном
    gy = 210  # висота гори під дроном
    body.append(circle(dx, gy, 4, fill=LINE, stroke=LINE))
    body.append(line(dx, dy + 8, dx, y_sea, color=MUTED, sw=1, dash="2,2"))

    # Стрілки висот:
    # А) MAV_FRAME_GLOBAL (AMSL) - від рівня моря до дрона
    ax1 = 390
    body.append(line(ax1, y_sea, ax1, dy, color=NEG, sw=1.8))
    body.append(arrow(ax1, (y_sea + dy)/2 + 20, ax1, dy, color=NEG, sw=1.8))
    body.append(arrow(ax1, (y_sea + dy)/2 - 20, ax1, y_sea, color=NEG, sw=1.8))
    body.append(rect(ax1 - 105, 230, 210, 42, fill="#eff6ff", stroke=NEG, sw=1.2, rx=4))
    body.append(text(ax1, 246, "MAV_FRAME_GLOBAL (AMSL)", size=11, bold=True, color=NEG))
    body.append(text(ax1, 262, "z = 350 м (від рівня моря)", size=10, color=NEG))

    # Б) MAV_FRAME_GLOBAL_RELATIVE_ALT - від рівня Home до дрона
    ax2 = dx + 60
    body.append(line(ax2, hy, ax2, dy, color=POS, sw=1.8))
    body.append(arrow(ax2, (hy + dy)/2 + 20, ax2, dy, color=POS, sw=1.8))
    body.append(arrow(ax2, (hy + dy)/2 - 20, ax2, hy, color=POS, sw=1.8))
    body.append(rect(ax2 + 10, 195, 240, 42, fill="#fdf2f0", stroke=POS, sw=1.2, rx=4))
    body.append(text(ax2 + 130, 211, "MAV_FRAME_GLOBAL_RELATIVE_ALT", size=11, bold=True, color=POS))
    body.append(text(ax2 + 130, 227, "z = 230 м (відносно Home)", size=10, color=POS))

    # В) MAV_FRAME_GLOBAL_TERRAIN_ALT - від поверхні гори до дрона
    ax3 = dx - 40
    body.append(line(ax3, gy, ax3, dy, color=FIELD, sw=2))
    body.append(arrow(ax3, (gy + dy)/2 + 15, ax3, dy, color=FIELD, sw=2))
    body.append(arrow(ax3, (gy + dy)/2 - 15, ax3, gy, color=FIELD, sw=2))
    body.append(rect(ax3 - 230, 130, 215, 42, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=4))
    body.append(text(ax3 - 122, 146, "MAV_FRAME_GLOBAL_TERRAIN_ALT", size=11, bold=True, color=FIELD))
    body.append(text(ax3 - 122, 162, "z = 100 м (AGL над рельєфом)", size=10, color=FIELD))

    render(os.path.join(OUT_DIR, "coordinate-frames.svg"), dw, dh, "".join(body))


def fig_mission_command_types():
    """Архітектура конвеєра виконання місії: NAV, DO та CONDITION команди."""
    dw, dh = 860, 420
    body = []
    
    body.append(text(dw / 2, 28, "Класифікація та конвеєр виконання команд місії", size=16, bold=True))
    body.append(text(dw / 2, 48, "Як автопілот обробляє навігаційні точки, паралельні дії та умовні бар'єри", size=12, color=MUTED))

    # Три колонки: NAV, DO, CONDITION
    col_w = 250
    gap = 25
    x_start = (dw - (3 * col_w + 2 * gap)) / 2

    # Колонка 1: NAV_*
    x1 = x_start
    body.append(rect(x1, 75, col_w, 315, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    body.append(rect(x1, 75, col_w, 38, fill=NEG, stroke=NEG, rx=6))
    body.append(text(x1 + col_w / 2, 99, "НАВІГАЦІЯ (MAV_CMD_NAV_*)", size=12, bold=True, color=BG))
    
    nav_items = [
        "Керують просторовим рухом",
        "Активна рівно одна команда",
        "Блокує перехід до досягнення цілі",
        "Приклади команд:",
        "• WAYPOINT (точка польоту)",
        "• TAKEOFF / LAND (зліт / посадка)",
        "• LOITER_UNLIM / TIME / TURNS",
        "• RETURN_TO_LAUNCH (повернення)",
        "• SPLINE_WAYPOINT (плавна дуга)"
    ]
    for i, item in enumerate(nav_items):
        is_bold = (i == 3)
        col = INK if not is_bold else NEG
        body.append(text(x1 + 15, 135 + i * 20, item, size=11, bold=is_bold, color=col, anchor="start"))

    # Колонка 2: DO_*
    x2 = x1 + col_w + gap
    body.append(rect(x2, 75, col_w, 315, fill="#fdf2f0", stroke=POS, sw=1.5, rx=6))
    body.append(rect(x2, 75, col_w, 38, fill=POS, stroke=POS, rx=6))
    body.append(text(x2 + col_w / 2, 99, "ДІЇ ТА НАЛАШТУВАННЯ (DO_*)", size=12, bold=True, color=BG))
    
    do_items = [
        "Виконуються миттєво / паралельно",
        "Не мають просторових цілей",
        "Не блокують навігаційний рух",
        "Приклади команд:",
        "• DO_SET_SERVO (керування серво)",
        "• DO_SET_RELAY (перемикач реле)",
        "• DO_CHANGE_SPEED (зміна швидкості)",
        "• DO_SET_CAM_TRIGG_DIST (фото)",
        "• DO_MOUNT_CONTROL (підвіс камери)",
        "• DO_JUMP (циклічний перехід)"
    ]
    for i, item in enumerate(do_items):
        is_bold = (i == 3)
        col = INK if not is_bold else POS
        body.append(text(x2 + 15, 135 + i * 20, item, size=11, bold=is_bold, color=col, anchor="start"))

    # Колонка 3: CONDITION_*
    x3 = x2 + col_w + gap
    body.append(rect(x3, 75, col_w, 315, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    body.append(rect(x3, 75, col_w, 38, fill=FIELD, stroke=FIELD, rx=6))
    body.append(text(x3 + col_w / 2, 99, "УМОВИ (CONDITION_*)", size=12, bold=True, color=BG))
    
    cond_items = [
        "Бар'єри виконання черги дій",
        "Призупиняють виклик наступних DO",
        "Чекають виконання умови",
        "Приклади команд:",
        "• CONDITION_DELAY (затримка в с)",
        "• CONDITION_DISTANCE (відстань до WPT)",
        "• CONDITION_YAW (доворот на кут)",
        "• CONDITION_GATE (прохід створу)"
    ]
    for i, item in enumerate(cond_items):
        is_bold = (i == 3)
        col = INK if not is_bold else FIELD
        body.append(text(x3 + 15, 135 + i * 20, item, size=11, bold=is_bold, color=col, anchor="start"))

    render(os.path.join(OUT_DIR, "mission-command-types.svg"), dw, dh, "".join(body))


def fig_waypoint_acceptance_radius():
    """Геометрія досягнення навігаційної точки: радіус прийому, прольоту та L1-траєкторія."""
    dw, dh = 860, 460
    body = []
    
    body.append(text(dw / 2, 28, "Геометрія проходження точки маршруту (MAV_CMD_NAV_WAYPOINT)", size=16, bold=True))
    body.append(text(dw / 2, 48, "Радіус прийому (param2), радіус зрізання кута (param3) та таймер зависання (param1)", size=12, color=MUTED))

    box_w = 370
    box_h = 370
    x_a = 45
    y_box = 70
    
    # ── Схема А: Точка з фіксацією (Hold Time > 0) ──
    body.append(rect(x_a, y_box, box_w, box_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    body.append(text(x_a + box_w / 2, y_box + 24, "А: Зупинка та зависання (param1 > 0)", size=13, bold=True, color=INK))
    
    # Координати точки WPT 1
    w1_x, w1_y = x_a + 220, y_box + 110
    r_acc = 45
    
    # Коло радіуса прийому
    body.append(f'<circle cx="{w1_x:.1f}" cy="{w1_y:.1f}" r="{r_acc:.1f}" fill="#eff6ff" stroke="{NEG}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    body.append(circle(w1_x, w1_y, 5, fill=POS, stroke=POS))
    body.append(text(w1_x + 12, w1_y - 12, "WPT 1", size=12, bold=True, color=POS, anchor="start"))
    
    # Траєкторія польоту дрона
    t_start_x, t_start_y = x_a + 40, y_box + 180
    body.append(line(t_start_x, t_start_y, w1_x, w1_y, color=INK, sw=2))
    body.append(arrow((t_start_x + w1_x)/2 - 10, (t_start_y + w1_y)/2 + 4, (t_start_x + w1_x)/2 + 10, (t_start_y + w1_y)/2 - 4, color=INK, sw=2))
    body.append(text(t_start_x, t_start_y + 16, "Старт", size=10, color=MUTED, anchor="start"))

    # Траєкторія після завершення hold time
    t_next_x, t_next_y = x_a + 330, y_box + 60
    body.append(line(w1_x, w1_y, t_next_x, t_next_y, color=INK, sw=2, dash="3,3"))
    body.append(arrow((w1_x + t_next_x)/2 - 10, (w1_y + t_next_y)/2 + 4, (w1_x + t_next_x)/2 + 10, (w1_y + t_next_y)/2 - 4, color=INK, sw=2))
    body.append(text(t_next_x - 10, t_next_y - 10, "До WPT 2", size=10, color=MUTED, anchor="end"))

    # Стрілка радіуса прийому
    body.append(line(w1_x, w1_y, w1_x - r_acc * 0.707, w1_y + r_acc * 0.707, color=NEG, sw=1.5))
    body.append(text(w1_x - 42, w1_y + 22, "R_acc", size=11, bold=True, color=NEG))
    
    # Панель опису дій
    text_y_a = y_box + 235
    body.append(rect(x_a + 15, text_y_a, box_w - 30, 115, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    body.append(text(x_a + 25, text_y_a + 22, "Послідовність автопілота:", size=11, bold=True, anchor="start", color=INK))
    body.append(text(x_a + 25, text_y_a + 44, "1. Вхід у сферу R_acc — гальмування до 0 м/с.", size=10, anchor="start", color=INK))
    body.append(text(x_a + 25, text_y_a + 66, "2. Відлік таймера зависання (Hold Time у с).", size=10, anchor="start", color=INK))
    body.append(text(x_a + 25, text_y_a + 88, "3. Розворот курсу та перехід до наступного seq.", size=10, anchor="start", color=INK))

    # ── Схема Б: Плавний проліт без зупинки (Pass-by / Fly-through, param3 > 0) ──
    x_b = x_a + box_w + 30
    body.append(rect(x_b, y_box, box_w, box_h, fill=FILL, stroke=LINE, sw=1.2, rx=6))
    body.append(text(x_b + box_w / 2, y_box + 24, "Б: Плавне зрізання кута (Fly-Through)", size=13, bold=True, color=INK))

    w2_x, w2_y = x_b + 200, y_box + 105
    body.append(f'<circle cx="{w2_x:.1f}" cy="{w2_y:.1f}" r="{r_acc:.1f}" fill="#fdf2f0" stroke="{POS}" stroke-width="1.5" stroke-dasharray="4,3"/>')
    body.append(circle(w2_x, w2_y, 5, fill=POS, stroke=POS))
    body.append(text(w2_x + 12, w2_y - 12, "WPT 1", size=12, bold=True, color=POS, anchor="start"))

    # Пунктир ідеальних відрізків
    body.append(line(x_b + 40, y_box + 180, w2_x, w2_y, color=MUTED, sw=1.2, dash="3,3"))
    body.append(line(w2_x, w2_y, x_b + 330, y_box + 60, color=MUTED, sw=1.2, dash="3,3"))

    # Плавна дуга замість ламаної лінії
    turn_arc = f"M {x_b + 40},{y_box + 180} Q {w2_x - 35},{w2_y + 35} {x_b + 330},{y_box + 60}"
    body.append(f'<path d="{turn_arc}" fill="none" stroke="{FIELD}" stroke-width="2.5"/>')
    body.append(text(x_b + 110, y_box + 90, "Траєкторія L1 (R_pass)", size=11, bold=True, color=FIELD))

    # Панель опису дій
    text_y_b = y_box + 235
    body.append(rect(x_b + 15, text_y_b, box_w - 30, 115, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
    body.append(text(x_b + 25, text_y_b + 22, "Переваги прольоту по дузі:", size=11, bold=True, anchor="start", color=INK))
    body.append(text(x_b + 25, text_y_b + 44, "1. Швидкість не падає до 0 (збереження енергії).", size=10, anchor="start", color=INK))
    body.append(text(x_b + 25, text_y_b + 66, "2. Відсутність ривків орієнтації та камери.", size=10, anchor="start", color=INK))
    body.append(text(x_b + 25, text_y_b + 88, "3. Ідеально для літаків і картографічної сітки.", size=10, anchor="start", color=INK))

    render(os.path.join(OUT_DIR, "waypoint-acceptance-radius.svg"), dw, dh, "".join(body))


def main():
    fig_mission_item_int_layout()
    fig_coordinate_frames()
    fig_mission_command_types()
    fig_waypoint_acceptance_radius()
    print("Всі SVG-фігури згенеровано успішно.")


if __name__ == '__main__':
    main()
