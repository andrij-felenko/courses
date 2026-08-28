# -*- coding: utf-8 -*-
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. architecture-split: Поділ обов'язків між SBC та FCU ────────────────────
def fig_architecture_split():
    W, H = 940, 480
    p = []

    # Лівий блок: Бортовий комп'ютер (SBC)
    p.append(rect(30, 40, 390, 400, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(225, 70, "Бортовий комп'ютер (Linux SBC)", size=15, color=INK, bold=True))
    p.append(text(225, 92, "Raspberry Pi 5 / Jetson Orin / Radxa", size=11, color=MUTED))

    b_sbc_type, _, _ = textbox(225, 130, "М'який реальний час (Soft RT)\nПотужні CPU/GPU обчислення",
                               size=11, fill="#ffffff", stroke=MUTED)
    p.append(b_sbc_type)

    # Задачі SBC
    p.append(rect(50, 175, 350, 245, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(225, 200, "Високорівневі задачі (5–20 Гц)", size=12, color=INK, bold=True))

    tasks_sbc = [
        "• Комп'ютерний зір і розпізнавання цілей (YOLO)",
        "• Візуальна одометрія та картографування (VIO / SLAM)",
        "• Планування траєкторій та обхід перешкод",
        "• Автомат місії та поведінкові дерева (BehaviorTree)",
        "• Зв'язок із хмарою, базою та LTE-модемом"
    ]
    for i, t_str in enumerate(tasks_sbc):
        p.append(text(65, 230 + i * 28, t_str, size=11, color=INK, anchor="start"))

    p.append(text(225, 395, "Генерація уставок: позиція, швидкість, курс", size=11, color=POS, bold=True))

    # Середній блок: Фізичний інтерфейс
    p.append(rect(435, 140, 70, 200, fill="#eef2f6", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(470, 165, "Канал", size=11, color=MUTED, bold=True))
    p.append(text(470, 185, "UART /", size=10, color=MUTED))
    p.append(text(470, 200, "USB /", size=10, color=MUTED))
    p.append(text(470, 215, "Ethernet", size=10, color=MUTED))

    # Стрілки обміну
    p.append(arrow(400, 255, 520, 255, color=POS, sw=2.2))
    p.append(text(470, 245, "Уставки", size=10, color=POS, bold=True))
    p.append(text(470, 270, "10–50 Гц", size=9, color=POS))

    p.append(arrow(540, 305, 420, 305, color=NEG, sw=2.2))
    p.append(text(470, 295, "Телеметрія", size=10, color=NEG, bold=True))
    p.append(text(470, 320, "20–100 Гц", size=9, color=NEG))

    # Правий блок: Польотний контролер (FCU)
    p.append(rect(520, 40, 390, 400, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(715, 70, "Польотний контролер (FCU / MCU)", size=15, color=INK, bold=True))
    p.append(text(715, 92, "STM32F7 / STM32H7 (PX4 / ArduPilot)", size=11, color=MUTED))

    b_fcu_type, _, _ = textbox(715, 130, "Жорсткий реальний час (Hard RT)\nДжиттер такту < 50 мкс",
                               size=11, fill="#ffffff", stroke=MUTED)
    p.append(b_fcu_type)

    # Задачі FCU
    p.append(rect(540, 175, 350, 245, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(715, 200, "Низькорівневе керування (100–1000 Гц)", size=12, color=INK, bold=True))

    tasks_fcu = [
        "• Опитування IMU / барометра / магнітометра (1 кГц)",
        "• Оцінювач орієнтації та позиції (EKF2, 100–250 Гц)",
        "• Каскад ПІД: кутові швидкості (1 кГц), кути (400 Гц)",
        "• Контур позиції та швидкості (50–100 Гц)",
        "• Мікшер моторів, виходи DShot / PWM, Failsafe"
    ]
    for i, t_str in enumerate(tasks_fcu):
        p.append(text(555, 230 + i * 28, t_str, size=11, color=INK, anchor="start"))

    p.append(text(715, 395, "Виконання уставок та безпека платформи", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "architecture-split.svg"), W, H, *p)

# ── 2. offboard-handshake-failsafe: Рукостискання, потік та відкат Failsafe ───
def fig_offboard_handshake_failsafe():
    W, H = 940, 460
    p = []

    # Часова вісь
    p.append(line(60, 400, 880, 400, color=LINE, sw=2.0))
    p.append(arrow(850, 400, 890, 400, color=LINE, sw=2.0))
    p.append(text(890, 420, "Час t", size=12, color=INK, bold=True, anchor="end"))

    # Смуги етапів
    stages = [
        (80, 240, "#eff6ff", "1. Передстартовий потік", "SBC шле уставки (f ≥ 2 Гц)\nТривалість > 500 мс\nКонтролер у стані Hold/Manual"),
        (260, 440, "#f0fdf4", "2. Запит і перехід", "SBC шле MAV_CMD_SET_MODE\nFCU перевіряє потік та EKF\nРежим переходить в OFFBOARD"),
        (460, 680, "#faf5ff", "3. Штатне ведення", "Безперервний потік 20–50 Гц\nПозиція / швидкість / кути\nРегулятори тримають уставку"),
        (700, 880, "#fef2f2", "4. Обрив і Failsafe", "Потік перервано на > 500 мс\nFCU спрацьовує таймаут\nАвтоматичний відкат у Hold/Land")
    ]

    for x1, x2, bg, title_s, desc_s in stages:
        w_box = x2 - x1
        p.append(rect(x1, 60, w_box, 300, fill=bg, stroke=MUTED, sw=1.2, rx=6))
        p.append(text(x1 + w_box / 2, 85, title_s, size=12, color=INK, bold=True))
        lines_d = desc_s.split("\n")
        for j, ln in enumerate(lines_d):
            p.append(text(x1 + w_box / 2, 115 + j * 20, ln, size=10.5, color=MUTED))

    # Стрілки та події на діаграмі
    # Етап 1: потік уставок
    for sx in [100, 130, 160, 190, 220]:
        p.append(arrow(sx, 220, sx, 270, color=POS, sw=1.5))
    p.append(text(160, 205, "Потік уставок (2–10 Гц)", size=10, color=POS, bold=True))
    p.append(text(160, 290, "Offboard НЕ активний", size=10, color=MUTED))

    # Етап 2: Запит
    p.append(arrow(310, 200, 390, 200, color=INK, sw=2.0))
    p.append(text(350, 190, "DO_SET_MODE(OFFBOARD)", size=10, color=INK, bold=True))
    p.append(circle(390, 250, 16, fill="#dcfce7", stroke=FIELD, sw=1.8))
    p.append(text(390, 255, "OK", size=11, color=FIELD, bold=True))
    p.append(text(350, 280, "Підтвердження переходу", size=10, color=FIELD))

    # Етап 3: Штатний потік
    for sx in [480, 510, 540, 570, 600, 630, 660]:
        p.append(arrow(sx, 210, sx, 260, color=FIELD, sw=1.5))
    p.append(text(570, 195, "Стабільний потік уставок 20–50 Гц", size=10.5, color=FIELD, bold=True))
    p.append(text(570, 285, "FCU слідує за командами SBC", size=10, color=INK))

    # Етап 4: Обрив і аварія
    p.append(line(710, 210, 750, 250, color=POS, sw=2.5))
    p.append(line(710, 250, 750, 210, color=POS, sw=2.5))
    p.append(text(790, 215, "Обрив потоку!", size=11, color=POS, bold=True))
    p.append(text(790, 235, "Δt > COM_OF_LOSS_T (0.5 с)", size=10, color=POS))

    b_fs, _, _ = textbox(790, 285, "АВАРІЙНИЙ ВІДСПАТ\nРежим AUTO_HOLD / LAND",
                         size=10.5, fill="#fee2e2", stroke=POS)
    p.append(b_fs)

    # Позначки на осі часу
    p.append(circle(80, 400, 4, fill=INK, stroke=INK))
    p.append(text(80, 420, "t = 0", size=10, color=MUTED))

    p.append(circle(260, 400, 4, fill=INK, stroke=INK))
    p.append(text(260, 420, "t = 0.5 с", size=10, color=MUTED))

    p.append(circle(700, 400, 4, fill=POS, stroke=POS))
    p.append(text(700, 420, "Збій SBC", size=10, color=POS, bold=True))

    p.append(circle(760, 400, 4, fill=POS, stroke=POS))
    p.append(text(760, 420, "+0.5 с", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "offboard-handshake-failsafe.svg"), W, H, *p)

# ── 3. frames-ned-enu: Системи координат NED vs ENU та FRD vs FLU ─────────────
def fig_frames_ned_enu():
    W, H = 940, 450
    p = []

    # Ліва половина: Світові системи (World Frames)
    p.append(rect(30, 35, 420, 385, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(240, 65, "Світові системи координат (World)", size=14, color=INK, bold=True))

    # Блок NED (Авіація / PX4 / ArduPilot)
    p.append(rect(50, 85, 180, 220, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(140, 110, "NED (Автопілоти)", size=12, color=INK, bold=True))
    p.append(text(140, 128, "North - East - Down", size=10, color=MUTED))

    # Осі NED
    ox, oy = 140, 190
    p.append(arrow(ox, oy, ox, oy - 45, color=POS, sw=2.0))
    p.append(text(ox + 12, oy - 40, "+X (North)", size=10, color=POS, bold=True))

    p.append(arrow(ox, oy, ox + 45, oy, color=FIELD, sw=2.0))
    p.append(text(ox + 48, oy + 12, "+Y (East)", size=10, color=FIELD, bold=True))

    p.append(arrow(ox, oy, ox - 30, oy + 30, color=NEG, sw=2.0))
    p.append(text(ox - 35, oy + 42, "+Z (Down / глибина)", size=9.5, color=NEG, bold=True))

    p.append(text(140, 280, "Yaw: ↻ за годинниковою\nвід Півночі до Сходу", size=10, color=INK))

    # Блок ENU (Робототехніка / ROS REP-103)
    p.append(rect(250, 85, 180, 220, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(340, 110, "ENU (ROS 2)", size=12, color=INK, bold=True))
    p.append(text(340, 128, "East - North - Up", size=10, color=MUTED))

    # Осі ENU
    ox2, oy2 = 340, 190
    p.append(arrow(ox2, oy2, ox2 + 45, oy2, color=FIELD, sw=2.0))
    p.append(text(ox2 + 48, oy2 + 12, "+X (East)", size=10, color=FIELD, bold=True))

    p.append(arrow(ox2, oy2, ox2, oy2 - 45, color=POS, sw=2.0))
    p.append(text(ox2 + 12, oy2 - 40, "+Y (North)", size=10, color=POS, bold=True))

    p.append(arrow(ox2, oy2, ox2 - 30, oy2 - 30, color=NEG, sw=2.0))
    p.append(text(ox2 - 35, oy2 - 35, "+Z (Up / висота)", size=9.5, color=NEG, bold=True))

    p.append(text(340, 280, "Yaw: ↺ проти годинникової\nвід Сходу до Півночі", size=10, color=INK))

    # Формули перетворення внизу лівого блоку
    p.append(rect(50, 315, 380, 90, fill="#eef2f6", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(240, 335, "Перетворення координат (World Conversion):", size=11, color=INK, bold=True))
    p.append(text(240, 355, "x_ned = y_enu  |  y_ned = x_enu  |  z_ned = −z_enu", size=10.5, color=POS, bold=True))
    p.append(text(240, 380, "yaw_ned = π/2 − yaw_enu  (зміна напрямку обертання)", size=10, color=MUTED))

    # Права половина: Зв'язані системи апарата (Body Frames)
    p.append(rect(490, 35, 420, 385, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(700, 65, "Зв'язані системи апарата (Body)", size=14, color=INK, bold=True))

    # Блок FRD (Автопілоти)
    p.append(rect(510, 85, 180, 220, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(600, 110, "FRD (Автопілоти)", size=12, color=INK, bold=True))
    p.append(text(600, 128, "Forward - Right - Down", size=10, color=MUTED))

    # Осі FRD
    ox3, oy3 = 600, 190
    p.append(arrow(ox3, oy3, ox3, oy3 - 45, color=POS, sw=2.0))
    p.append(text(ox3 + 12, oy3 - 40, "+X (Forward / ніс)", size=9.5, color=POS, bold=True))

    p.append(arrow(ox3, oy3, ox3 + 45, oy3, color=FIELD, sw=2.0))
    p.append(text(ox3 + 48, oy3 + 12, "+Y (Right / борт)", size=9.5, color=FIELD, bold=True))

    p.append(arrow(ox3, oy3, ox3 - 30, oy3 + 30, color=NEG, sw=2.0))
    p.append(text(ox3 - 35, oy3 + 42, "+Z (Down / днище)", size=9.5, color=NEG, bold=True))

    p.append(text(600, 280, "Крен (Roll): правий борт вниз\nТангаж (Pitch): ніс угору", size=9.5, color=INK))

    # Блок FLU (ROS 2 REP-103)
    p.append(rect(710, 85, 180, 220, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(800, 110, "FLU (ROS 2)", size=12, color=INK, bold=True))
    p.append(text(800, 128, "Forward - Left - Up", size=10, color=MUTED))

    # Осі FLU
    ox4, oy4 = 800, 190
    p.append(arrow(ox4, oy4, ox4, oy4 - 45, color=POS, sw=2.0))
    p.append(text(ox4 + 12, oy4 - 40, "+X (Forward / ніс)", size=9.5, color=POS, bold=True))

    p.append(arrow(ox4, oy4, ox4 - 45, oy4, color=FIELD, sw=2.0))
    p.append(text(ox4 - 48, oy4 + 12, "+Y (Left / лівий)", size=9.5, color=FIELD, bold=True))

    p.append(arrow(ox4, oy4, ox4 + 30, oy4 - 30, color=NEG, sw=2.0))
    p.append(text(ox4 + 35, oy4 - 35, "+Z (Up / дах)", size=9.5, color=NEG, bold=True))

    p.append(text(800, 280, "Крен (Roll): лівий борт вниз\nТангаж (Pitch): ніс униз", size=9.5, color=INK))

    # Формули перетворення Body
    p.append(rect(510, 315, 380, 90, fill="#eef2f6", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(700, 335, "Перетворення зв'язаних осей (Body Conversion):", size=11, color=INK, bold=True))
    p.append(text(700, 355, "x_frd = x_flu  |  y_frd = −y_flu  |  z_frd = −z_flu", size=10.5, color=POS, bold=True))
    p.append(text(700, 380, "roll_frd = roll_flu  |  pitch_frd = −pitch_flu  |  yaw_frd = −yaw_flu", size=9.5, color=MUTED))

    render(os.path.join(OUT, "frames-ned-enu.svg"), W, H, *p)

# ── 4. software-stacks: Порівняння MAVLink/MAVROS та micro-XRCE-DDS ───────────
def fig_software_stacks():
    W, H = 940, 470
    p = []

    # Ліва колонка: Класичний MAVLink стек
    p.append(rect(30, 40, 420, 400, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(240, 70, "Класичний міст: MAVSDK / MAVROS", size=14, color=INK, bold=True))
    p.append(text(240, 92, "Широкий стандарт для ArduPilot та PX4", size=11, color=MUTED))

    # Шари MAVLink
    layers_m = [
        (120, "Користувацька програма (C++ / Python)", "#ffffff"),
        (175, "MAVSDK / MAVROS (Трансляція топіків)", "#ffffff"),
        (230, "Серіалізація MAVLink (msg #84 / #83)", "#eef2f6"),
        (285, "UART / USB потік байтів (Serial Driver)", "#ffffff"),
        (340, "Автопілот: MAVLink парсер → uORB топіки", "#dcfce7")
    ]
    for y_pos, title_l, bg_l in layers_m:
        p.append(rect(50, y_pos, 380, 42, fill=bg_l, stroke=LINE, sw=1.1, rx=5))
        p.append(text(240, y_pos + 26, title_l, size=11, color=INK))

    for y_arr in [162, 217, 272, 327]:
        p.append(arrow(240, y_arr, 240, y_arr + 12, color=POS, sw=1.8))

    p.append(text(240, 400, "Плюси: універсальність, сумісність з ArduPilot/PX4", size=10, color=MUTED))
    p.append(text(240, 418, "Мінуси: подвійна серіалізація, оверхед MAVLink", size=10, color=MUTED))

    # Права колонка: Прямий micro-XRCE-DDS / micro-ROS
    p.append(rect(490, 40, 420, 400, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=8))
    p.append(text(700, 70, "Пряма шина: micro-XRCE-DDS (PX4 v1.14+)", size=14, color=INK, bold=True))
    p.append(text(700, 92, "Пряма інтеграція ROS 2 без посередників", size=11, color=MUTED))

    # Шари micro-DDS
    layers_d = [
        (120, "Вузол ROS 2 (Nav2 / Autonomy Node)", "#ffffff"),
        (175, "Топік ROS 2: /fmu/in/trajectory_setpoint", "#ffffff"),
        (230, "micro-XRCE-DDS Agent (Linux daemon)", "#eef2f6"),
        (285, "UART / UDP транспорт (DDS кадр CDR)", "#ffffff"),
        (340, "PX4 uORB: пряме відображення структури", "#dcfce7")
    ]
    for y_pos, title_l, bg_l in layers_d:
        p.append(rect(510, y_pos, 380, 42, fill=bg_l, stroke=LINE, sw=1.1, rx=5))
        p.append(text(700, y_pos + 26, title_l, size=11, color=INK))

    for y_arr in [162, 217, 272, 327]:
        p.append(arrow(700, y_arr, 700, y_arr + 12, color=FIELD, sw=1.8))

    p.append(text(700, 400, "Плюси: нульовий оверхед, нативний ROS 2 тип uORB", size=10, color=MUTED))
    p.append(text(700, 418, "Мінуси: прив'язка до версії PX4, складніший bringup", size=10, color=MUTED))

    render(os.path.join(OUT, "software-stacks.svg"), W, H, *p)

if __name__ == "__main__":
    fig_architecture_split()
    fig_offboard_handshake_failsafe()
    fig_frames_ned_enu()
    fig_software_stacks()
    print("All figures generated successfully.")
