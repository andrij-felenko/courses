# -*- coding: utf-8 -*-
"""Фігури до теми «HEARTBEAT: як апарат оголошує себе».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори
COL_CUSTOM   = "#2457d6"  # синій (режими автопілота)
COL_TYPE     = "#8e44ad"  # фіолетовий (тип платформи)
COL_AUTO     = "#2980b9"  # блакитний (стек автопілота)
COL_BASE     = "#d35400"  # помаранчевий (базовий прапорець)
COL_STATE    = "#27ae60"  # зелений (стан системи)
COL_VER      = "#7f8c8d"  # сірий (версія)
COL_ALERT    = "#c0392b"  # червоний (аварія, армінг)
COL_WARN     = "#f39c12"  # жовтий/бурштиновий (деградація, тайм-аут)


# ── 1. Анатомія корисного навантаження HEARTBEAT (9 байтів) ─────────────────
def fig_payload():
    W, H = 840, 310
    f = [text(W / 2, 28, "Корисне навантаження повідомлення HEARTBEAT (MSG ID 0, 9 байтів)", size=15, bold=True)]

    y = 80
    bh = 58
    cells = [
        ("custom_mode", 4, COL_CUSTOM, "uint32 (4 Б)", "байт 0..3: режим польоту прошивки"),
        ("type",        1, COL_TYPE,   "uint8 (1 Б)",  "байт 4: тип апарата"),
        ("autopilot",   1, COL_AUTO,   "uint8 (1 Б)",  "байт 5: стек прошивки"),
        ("base_mode",   1, COL_BASE,   "uint8 (1 Б)",  "байт 6: маска стану й армінгу"),
        ("system_status", 1, COL_STATE,"uint8 (1 Б)",  "байт 7: життєвий стан"),
        ("mavlink_version", 1, COL_VER,"uint8 (1 Б)",  "байт 8: версія MAVLink"),
    ]
    total_bytes = 9
    x = 35
    span = W - 70

    for name, b_len, col, type_str, desc in cells:
        w = span * b_len / total_bytes
        f.append(rect(x, y, w, bh, fill=BG, stroke=col, sw=2.2))
        f.append(text(x + w / 2, y + 23, name, size=12.5 if b_len == 1 else 13.5, color=col, bold=True))
        f.append(text(x + w / 2, y + 43, type_str, size=10.5, color=MUTED, italic=True))
        x += w

    # Описи під полями
    yo = y + bh + 22
    row_h = 24
    f.append(rect(35, yo - 8, span, 120, fill=FILL, stroke=LINE, sw=1.0, rx=4))

    details = [
        ("custom_mode (4 Б):", "Власний режим польоту конкретного автопілота (PX4 / ArduPilot: MANUAL, POSHOLD, AUTO, RTL)", COL_CUSTOM),
        ("type (1 Б):", "Фізична конфігурація апарата за MAV_TYPE (квадрокоптер, літак, вертоліт, ровер, GCS)", COL_TYPE),
        ("autopilot (1 Б):", "Тип системи керування за MAV_AUTOPILOT (PX4, ArduPilot, Generic, Betaflight)", COL_AUTO),
        ("base_mode (1 Б):", "Стандартизовані прапорці MAV_MODE_FLAG: статус безпеки (ARMED), стабілізація, автономність", COL_BASE),
        ("system_status (1 Б):", "Поточний стан за MAV_STATE (BOOT, CALIBRATING, STANDBY, ACTIVE, CRITICAL, EMERGENCY)", COL_STATE),
    ]

    for i, (lbl, desc, col) in enumerate(details):
        ly = yo + 14 + i * row_h
        f.append(text(45, ly, lbl, size=11, color=col, anchor="start", bold=True))
        f.append(text(190, ly, desc, size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "heartbeat-payload.svg"), W, H, *f)


# ── 2. Бітова маска base_mode (MAV_MODE_FLAG) ────────────────────────────────
def fig_base_mode():
    W, H = 840, 360
    f = [text(W / 2, 28, "Структура бітової маски base_mode (uint8, MAV_MODE_FLAG)", size=15, bold=True)]

    bits = [
        ("7", "0x80", "SAFETY_ARMED",         COL_ALERT, "Мотори розблоковані й отримують живлення (1 = небезпечно, 0 = вимкнено)"),
        ("6", "0x40", "MANUAL_INPUT_ENABLED", COL_BASE,  "Увімкнено пряме ручне керування від пульта радіокерування або джойстика"),
        ("5", "0x20", "HIL_ENABLED",           COL_VER,   "Апарат працює в режимі апаратно-програмної симуляції (Hardware-in-the-Loop)"),
        ("4", "0x10", "STABILIZE_ENABLED",     COL_CUSTOM,"Активний контур кутової стабілізації за гіроскопами й акселерометрами"),
        ("3", "0x08", "GUIDED_ENABLED",        COL_AUTO,  "Автопілот слідує за зовнішніми цільовими векторами від GCS або супутнього комп'ютера"),
        ("2", "0x04", "AUTO_ENABLED",          COL_STATE, "Повністю автономна навігація за точками маршруту завантаженої місії"),
        ("1", "0x02", "TEST_ENABLED",          COL_VER,   "Апарат перебуває в інженерному або тестовому режимі заводської перевірки"),
        ("0", "0x01", "CUSTOM_MODE_ENABLED",   COL_CUSTOM,"Поле custom_mode активне: розшифровка режиму за правилами конкретної прошивки"),
    ]

    y_start = 65
    row_h = 33
    col_bit_x = 40
    col_hex_x = 95
    col_name_x = 170
    col_desc_x = 385

    # Заголовок таблиці
    f.append(rect(30, y_start - 8, W - 60, 26, fill=FILL, stroke=LINE, sw=1.2, rx=4))
    f.append(text(col_bit_x + 12, y_start + 9, "Біт", size=11, color=MUTED, bold=True))
    f.append(text(col_hex_x + 18, y_start + 9, "Маска", size=11, color=MUTED, bold=True))
    f.append(text(col_name_x, y_start + 9, "Ім'я прапорця MAV_MODE_FLAG", size=11, color=MUTED, anchor="start", bold=True))
    f.append(text(col_desc_x, y_start + 9, "Функціональне призначення", size=11, color=MUTED, anchor="start", bold=True))

    y = y_start + 24
    for bit_num, hex_val, name, col, desc in bits:
        f.append(rect(30, y - 2, W - 60, row_h - 4, fill=BG, stroke=MUTED, sw=0.7, rx=3))
        # Біт
        f.append(rect(col_bit_x, y + 2, 28, 20, fill=FILL, stroke=col, sw=1.2, rx=3))
        f.append(text(col_bit_x + 14, y + 16, bit_num, size=11.5, color=col, bold=True))
        # Шістнадцяткова маска
        f.append(text(col_hex_x + 18, y + 16, hex_val, size=11.5, color=INK, bold=True))
        # Назва
        f.append(text(col_name_x, y + 16, name, size=11.5, color=col, anchor="start", bold=True))
        # Опис
        f.append(text(col_desc_x, y + 16, desc, size=10.5, color=INK, anchor="start"))
        y += row_h

    render(os.path.join(IMG, "base-mode-mask.svg"), W, H, *f)


# ── 3. Машина станів життєвого циклу (MAV_STATE) ────────────────────────────
def fig_state_machine():
    W, H = 840, 370
    f = [text(W / 2, 28, "Життєвий цикл системи: машина станів MAV_STATE (system_status)", size=15, bold=True)]

    # Основний ланцюг: UNINIT (0) -> BOOT (1) -> CALIBRATING (2) -> STANDBY (3) -> ACTIVE (4)
    box_w = 125
    box_h = 52
    y_main = 85

    states = [
        ("UNINIT (0)",     "Неініціалізовано", COL_VER,   65),
        ("BOOT (1)",       "Завантаження ОС",  COL_AUTO,  220),
        ("CALIBRATING (2)","Калібрування IMU", COL_CUSTOM,375),
        ("STANDBY (3)",    "Очікування (готов)",COL_BASE, 530),
        ("ACTIVE (4)",     "У польоті (ARMED)",COL_STATE, 685),
    ]

    for name, sub, col, cx in states:
        f.append(rect(cx - box_w/2, y_main, box_w, box_h, fill=BG, stroke=col, sw=2.0, rx=5))
        f.append(text(cx, y_main + 22, name, size=11.5, color=col, bold=True))
        f.append(text(cx, y_main + 40, sub, size=10, color=MUTED, italic=True))

    # Стрілки основного ланцюга
    for i in range(len(states) - 1):
        x1 = states[i][3] + box_w/2
        x2 = states[i+1][3] - box_w/2
        f.append(arrow(x1, y_main + box_h/2, x2, y_main + box_h/2, color=INK, sw=1.6))

    # Підписи під стрілками основного ланцюга
    f.append(text((states[0][3] + states[1][3])/2, y_main + box_h/2 - 8, "живлення", size=9.5, color=MUTED))
    f.append(text((states[1][3] + states[2][3])/2, y_main + box_h/2 - 8, "сенсори", size=9.5, color=MUTED))
    f.append(text((states[2][3] + states[3][3])/2, y_main + box_h/2 - 8, "нулі знайдено", size=9.5, color=MUTED))
    f.append(text((states[3][3] + states[4][3])/2, y_main + box_h/2 - 8, "ARM команди", size=9.5, color=MUTED))

    # Нижні аварійні стани: CRITICAL (5), EMERGENCY (6), POWEROFF (7)
    y_sub = 230

    sub_states = [
        ("POWEROFF (7)",  "Знеструмлення",    COL_VER,   220),
        ("CRITICAL (5)",  "Відмова вузла / RTL", COL_WARN, 530),
        ("EMERGENCY (6)", "Падіння / Kill",  COL_ALERT, 685),
    ]

    for name, sub, col, cx in sub_states:
        f.append(rect(cx - box_w/2, y_sub, box_w, box_h, fill=BG, stroke=col, sw=2.0, rx=5))
        f.append(text(cx, y_sub + 22, name, size=11.5, color=col, bold=True))
        f.append(text(cx, y_sub + 40, sub, size=10, color=MUTED, italic=True))

    # Стрілка ACTIVE -> CRITICAL (збій, просідання батареї, втрата GPS)
    f.append(arrow(states[4][3] - 20, y_main + box_h, sub_states[1][3] + 20, y_sub, color=COL_WARN, sw=1.6))
    f.append(text(620, 175, "відмова сенсора / втрата лінку", size=9.5, color=COL_WARN, bold=True))

    # Стрілка ACTIVE -> EMERGENCY (втрата керування, руйнування)
    f.append(arrow(states[4][3], y_main + box_h, sub_states[2][3], y_sub, color=COL_ALERT, sw=1.6))
    f.append(text(725, 175, "катастрофа", size=9.5, color=COL_ALERT, bold=True))

    # Стрілка CRITICAL -> EMERGENCY (деградація аварії)
    f.append(arrow(sub_states[1][3] + box_w/2, y_sub + box_h/2, sub_states[2][3] - box_w/2, y_sub + box_h/2, color=COL_ALERT, sw=1.6))

    # Стрілка STANDBY -> POWEROFF
    f.append(arrow(states[3][3] - 30, y_main + box_h, sub_states[0][3] + 30, y_sub, color=COL_VER, sw=1.6))
    f.append(text(360, 175, "команда вимкнення", size=9.5, color=MUTED))

    # Стрілка повернення ACTIVE -> STANDBY (посадка, Disarm)
    f.append(arrow(states[4][3] - 30, y_main - 4, states[3][3] + 30, y_main - 4, color=COL_BASE, sw=1.4))
    f.append(text((states[3][3] + states[4][3])/2, y_main - 12, "посадка / DISARM", size=9.5, color=COL_BASE))

    # Пояснення знизу
    f.append(rect(30, 310, W - 60, 45, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    f.append(text(W / 2, 336,
                  "GCS аналізує поле system_status: блокує зліт у CALIBRATING/CRITICAL, активує аварійні таймери в EMERGENCY.",
                  size=11, color=INK, italic=True))

    render(os.path.join(IMG, "system-state-machine.svg"), W, H, *f)


# ── 4. Розпізнавання топології мережі MAVLink (SYS / COMP) ───────────────────
def fig_network_topology():
    W, H = 840, 370
    f = [text(W / 2, 28, "Топологія мережі MAVLink: вузли оголошують себе через (sysid, compid)", size=15, bold=True)]

    # Центральна шина зв'язку (радіоканал телеметрії / UDP)
    bus_y = 175
    f.append(line(40, bus_y, W - 40, bus_y, color=INK, sw=3.0))
    f.append(rect(W / 2 - 130, bus_y - 12, 260, 24, fill=FILL, stroke=INK, sw=1.2, rx=4))
    f.append(text(W / 2, bus_y + 4, "Спільний радіоканал телеметрії / UDP-мережа", size=11, color=INK, bold=True))

    # 1. Наземна станція керування (GCS)
    gcs_x, gcs_y = 130, 75
    f.append(rect(gcs_x - 85, gcs_y - 35, 170, 70, fill=BG, stroke=COL_AUTO, sw=2.0, rx=5))
    f.append(text(gcs_x, gcs_y - 14, "Наземна станція (GCS)", size=12, color=COL_AUTO, bold=True))
    f.append(text(gcs_x, gcs_y + 6, "SYS 255 · COMP 0/190", size=10.5, color=INK, bold=True))
    f.append(text(gcs_x, gcs_y + 24, "type: MAV_TYPE_GCS", size=9.5, color=MUTED, italic=True))
    f.append(arrow(gcs_x, gcs_y + 35, gcs_x, bus_y - 14, color=COL_AUTO, sw=1.5))
    f.append(text(gcs_x + 8, 135, "HEARTBEAT 1 Гц", size=9, color=COL_AUTO, anchor="start"))

    # 2. Антенний трекер
    trk_x, trk_y = 330, 75
    f.append(rect(trk_x - 80, trk_y - 35, 160, 70, fill=BG, stroke=COL_CUSTOM, sw=2.0, rx=5))
    f.append(text(trk_x, trk_y - 14, "Антенний трекер", size=12, color=COL_CUSTOM, bold=True))
    f.append(text(trk_x, trk_y + 6, "SYS 254 · COMP 1", size=10.5, color=INK, bold=True))
    f.append(text(trk_x, trk_y + 24, "type: MAV_TYPE_TRACKER", size=9.5, color=MUTED, italic=True))
    f.append(arrow(trk_x, trk_y + 35, trk_x, bus_y - 14, color=COL_CUSTOM, sw=1.5))
    f.append(text(trk_x + 8, 135, "HEARTBEAT 1 Гц", size=9, color=COL_CUSTOM, anchor="start"))

    # 3. Дрон №1 (SYS 1) — містить 3 компоненти
    d1_x, d1_y = 610, 80
    f.append(rect(d1_x - 170, d1_y - 45, 340, 88, fill=FILL, stroke=COL_STATE, sw=2.2, rx=6))
    f.append(text(d1_x, d1_y - 25, "Борт Дрона №1 (SYS 1 · MAV_TYPE_QUADROTOR)", size=12, color=COL_STATE, bold=True))

    # Три компоненти дрона 1
    c1_x = d1_x - 110
    f.append(rect(c1_x - 50, d1_y - 10, 100, 44, fill=BG, stroke=COL_STATE, sw=1.2, rx=3))
    f.append(text(c1_x, d1_y + 7, "Автопілот", size=10.5, color=COL_STATE, bold=True))
    f.append(text(c1_x, d1_y + 23, "COMP 1", size=9.5, color=INK))

    c2_x = d1_x
    f.append(rect(c2_x - 50, d1_y - 10, 100, 44, fill=BG, stroke=COL_CUSTOM, sw=1.2, rx=3))
    f.append(text(c2_x, d1_y + 7, "Комп'ютер", size=10.5, color=COL_CUSTOM, bold=True))
    f.append(text(c2_x, d1_y + 23, "COMP 191", size=9.5, color=INK))

    c3_x = d1_x + 110
    f.append(rect(c3_x - 50, d1_y - 10, 100, 44, fill=BG, stroke=COL_BASE, sw=1.2, rx=3))
    f.append(text(c3_x, d1_y + 7, "Підвіс камери", size=10.5, color=COL_BASE, bold=True))
    f.append(text(c3_x, d1_y + 23, "COMP 154", size=9.5, color=INK))

    f.append(arrow(d1_x, d1_y + 43, d1_x, bus_y - 14, color=COL_STATE, sw=1.8))
    f.append(text(d1_x + 8, 145, "3 незалежні HEARTBEAT по 1 Гц", size=9, color=COL_STATE, anchor="start"))

    # Нижня частина: Дрон №2 (SYS 2) та ровер (SYS 3)
    d2_x, d2_y = 250, 275
    f.append(rect(d2_x - 110, d2_y - 35, 220, 70, fill=BG, stroke=COL_STATE, sw=1.8, rx=5))
    f.append(text(d2_x, d2_y - 14, "Дрон №2 (SYS 2 · COMP 1)", size=11.5, color=COL_STATE, bold=True))
    f.append(text(d2_x, d2_y + 6, "type: MAV_TYPE_FIXED_WING", size=10, color=INK))
    f.append(text(d2_x, d2_y + 24, "autopilot: MAV_AUTOPILOT_PX4", size=9.5, color=MUTED, italic=True))
    f.append(arrow(d2_x, d2_y - 35, d2_x, bus_y + 14, color=COL_STATE, sw=1.5))

    d3_x, d3_y = 610, 275
    f.append(rect(d3_x - 110, d3_y - 35, 220, 70, fill=BG, stroke=COL_BASE, sw=1.8, rx=5))
    f.append(text(d3_x, d3_y - 14, "Ровер (SYS 3 · COMP 1)", size=11.5, color=COL_BASE, bold=True))
    f.append(text(d3_x, d3_y + 6, "type: MAV_TYPE_GROUND_ROVER", size=10, color=INK))
    f.append(text(d3_x, d3_y + 24, "autopilot: MAV_AUTOPILOT_ARDUPILOTMEGA", size=9.5, color=MUTED, italic=True))
    f.append(arrow(d3_x, d3_y - 35, d3_x, bus_y + 14, color=COL_BASE, sw=1.5))

    render(os.path.join(IMG, "network-topology.svg"), W, H, *f)


# ── 5. Сторожовий таймер і розпізнавання втрати лінку (Watchdog) ──────────────
def fig_watchdog():
    W, H = 840, 320
    f = [text(W / 2, 28, "Сторожовий таймер серцебиття: часова шкала виявлення втрати лінку", size=15, bold=True)]

    # Часова шкала (вісь t)
    ax_y = 120
    x_start = 60
    x_end = W - 60
    f.append(arrow(x_start, ax_y, x_end, ax_y, color=INK, sw=2.0))
    f.append(text(x_end - 10, ax_y - 12, "Час (секунди)", size=11, color=INK, anchor="end", bold=True))

    # Позначки часу
    p1_x = 110
    f.append(circle(p1_x, ax_y, 6, fill=COL_STATE, stroke=COL_STATE, sw=1.5))
    f.append(text(p1_x, ax_y + 22, "t = 0.0 с", size=10.5, color=INK))
    f.append(text(p1_x, ax_y - 18, "HEARTBEAT #1", size=10, color=COL_STATE, bold=True))
    f.append(line(p1_x, ax_y - 35, p1_x, ax_y - 8, color=COL_STATE, sw=1.5))

    p2_x = 230
    f.append(circle(p2_x, ax_y, 6, fill=COL_STATE, stroke=COL_STATE, sw=1.5))
    f.append(text(p2_x, ax_y + 22, "t = 1.0 с", size=10.5, color=INK))
    f.append(text(p2_x, ax_y - 18, "HEARTBEAT #2", size=10, color=COL_STATE, bold=True))
    f.append(line(p2_x, ax_y - 35, p2_x, ax_y - 8, color=COL_STATE, sw=1.5))

    # Знак аварійного обриву зв'язку
    jam_x = 290
    f.append(line(jam_x - 12, ax_y - 25, jam_x + 12, ax_y + 25, color=COL_ALERT, sw=3.0))
    f.append(line(jam_x - 12, ax_y + 25, jam_x + 12, ax_y - 25, color=COL_ALERT, sw=3.0))
    f.append(text(jam_x, ax_y - 35, "Обрив зв'язку / завада", size=10.5, color=COL_ALERT, bold=True))

    # Зона 1: Очікування наступного пульсу (до 2.0 с)
    f.append(rect(230, ax_y + 40, 140, 32, fill=FILL, stroke=COL_STATE, sw=1.2, rx=4))
    f.append(text(300, ax_y + 60, "Норма (джиттер)", size=10.5, color=COL_STATE, bold=True))

    # Зона 2: Попередження (2.5 - 4.5 с)
    warn_x = 440
    f.append(circle(warn_x, ax_y, 6, fill=COL_WARN, stroke=COL_WARN, sw=1.5))
    f.append(text(warn_x, ax_y + 22, "t = 3.0 с", size=10.5, color=INK))
    f.append(rect(380, ax_y + 40, 170, 32, fill=FILL, stroke=COL_WARN, sw=1.2, rx=4))
    f.append(text(465, ax_y + 60, "Деградація лінку (Warning)", size=10.5, color=COL_WARN, bold=True))

    # Зона 3: Спрацьовування сторожового таймера (4.5 - 5.0 с)
    to_x = 620
    f.append(circle(to_x, ax_y, 7, fill=COL_ALERT, stroke=COL_ALERT, sw=2.0))
    f.append(text(to_x, ax_y + 22, "t = 4.5 с (Поріг)", size=11, color=COL_ALERT, bold=True))
    f.append(line(to_x, ax_y - 50, to_x, ax_y - 10, color=COL_ALERT, sw=2.0, dash="3,3"))

    # Блок аварійного захисту Failsafe
    f.append(rect(to_x - 80, ax_y - 95, 180, 44, fill=BG, stroke=COL_ALERT, sw=2.2, rx=5))
    f.append(text(to_x + 10, ax_y - 78, "FAILSAFE АКТИВОВАНО", size=11, color=COL_ALERT, bold=True))
    f.append(text(to_x + 10, ax_y - 62, "RTL / Land / Loiter", size=10, color=INK, italic=True))

    # Пояснювальний текст унизу
    f.append(rect(60, 235, W - 120, 60, fill=FILL, stroke=LINE, sw=1.0, rx=4))
    f.append(text(W / 2, 260,
                  "Сторожовий таймер (Watchdog) відлічує: Δt = t_поточний - t_останнього_HEARTBEAT.",
                  size=11, color=INK, bold=True))
    f.append(text(W / 2, 280,
                  "Якщо Δt > 4.5 с: станція позначає зв'язок втраченим, автопілот переходить у режим захисту (GCS Failsafe).",
                  size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "heartbeat-watchdog.svg"), W, H, *f)


if __name__ == "__main__":
    fig_payload()
    fig_base_mode()
    fig_state_machine()
    fig_network_topology()
    fig_watchdog()
    print("All figures generated successfully.")
