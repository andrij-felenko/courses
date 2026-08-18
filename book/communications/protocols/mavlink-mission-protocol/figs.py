# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми mavlink-mission-protocol."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT_DIR, exist_ok=True)


def fig_upload_flow():
    """Діаграма послідовності завантаження місії на дрон (Upload Transaction Flow)."""
    w, h = 840, 520
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок зверху
    b, _, _ = textbox(w / 2, 28, "ТРАНЗАКЦІЙНЕ ЗАВАНТАЖЕННЯ МІСІЇ (UPLOAD FLOW)", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    # Стовпці сутностей (GCS та Autopilot)
    x_gcs = 160
    x_drone = 680

    # Шапки сутностей
    b1, _, _ = textbox(x_gcs, 75, "Наземна станція (GCS)\n[Клієнт / Відправник даних]", size=13, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=8)
    b2, _, _ = textbox(x_drone, 75, "Польотний контролер (FCU)\n[Сервер / Керує запитами]", size=13, bold=True, fill="#fdf2e9", stroke="#d35400", pad=8)
    body += b1 + b2

    # Вертикальні лінії життя (lifelines)
    body += line(x_gcs, 105, x_gcs, 490, color="#7f8c8d", sw=1.5, dash="5,4")
    body += line(x_drone, 105, x_drone, 490, color="#7f8c8d", sw=1.5, dash="5,4")

    # Послідовність повідомлень
    # 1. MISSION_COUNT
    y1 = 140
    body += arrow(x_gcs, y1, x_drone, y1, color="#2457d6", sw=2)
    b, _, _ = textbox(420, y1 - 14, "1. MISSION_COUNT (count=3, type=MISSION)", size=12, bold=True, fill="#ffffff", stroke="#2457d6", pad=4)
    body += b

    # Блок створення тимчасового буфера на автопілоті
    b_buf, _, _ = textbox(x_drone, y1 + 35, "Виділення staging-буфера в RAM\n(старий план у Flash не чіпається)", size=10, fill="#fef9e7", stroke="#f39c12", pad=5)
    body += b_buf

    # 2. MISSION_REQUEST_INT (seq=0)
    y2 = 210
    body += arrow(x_drone, y2, x_gcs, y2, color="#d35400", sw=2)
    b, _, _ = textbox(420, y2 - 14, "2. MISSION_REQUEST_INT (seq=0)", size=12, bold=True, fill="#ffffff", stroke="#d35400", pad=4)
    body += b

    # 3. MISSION_ITEM_INT (seq=0)
    y3 = 255
    body += arrow(x_gcs, y3, x_drone, y3, color="#2457d6", sw=2)
    b, _, _ = textbox(420, y3 - 14, "3. MISSION_ITEM_INT (seq=0: TAKEOFF, 15m)", size=12, bold=True, fill="#ffffff", stroke="#2457d6", pad=4)
    body += b

    # 4. MISSION_REQUEST_INT (seq=1)
    y4 = 300
    body += arrow(x_drone, y4, x_gcs, y4, color="#d35400", sw=2)
    b, _, _ = textbox(420, y4 - 14, "4. MISSION_REQUEST_INT (seq=1)", size=12, bold=True, fill="#ffffff", stroke="#d35400", pad=4)
    body += b

    # 5. MISSION_ITEM_INT (seq=1)
    y5 = 345
    body += arrow(x_gcs, y5, x_drone, y5, color="#2457d6", sw=2)
    b, _, _ = textbox(420, y5 - 14, "5. MISSION_ITEM_INT (seq=1: WAYPOINT)", size=12, bold=True, fill="#ffffff", stroke="#2457d6", pad=4)
    body += b

    # 6. MISSION_REQUEST_INT (seq=2)
    y6 = 390
    body += arrow(x_drone, y6, x_gcs, y6, color="#d35400", sw=2)
    b, _, _ = textbox(420, y6 - 14, "6. MISSION_REQUEST_INT (seq=2)", size=12, bold=True, fill="#ffffff", stroke="#d35400", pad=4)
    body += b

    # 7. MISSION_ITEM_INT (seq=2)
    y7 = 435
    body += arrow(x_gcs, y7, x_drone, y7, color="#2457d6", sw=2)
    b, _, _ = textbox(420, y7 - 14, "7. MISSION_ITEM_INT (seq=2: RTL)", size=12, bold=True, fill="#ffffff", stroke="#2457d6", pad=4)
    body += b

    # 8. MISSION_ACK
    y8 = 475
    body += arrow(x_drone, y8, x_gcs, y8, color="#27ae60", sw=2.5)
    b, _, _ = textbox(420, y8 - 14, "8. MISSION_ACK (type=MAV_MISSION_ACCEPTED) [Атомарна фіксація у Flash]", size=12, bold=True, fill="#eafaf1", stroke="#27ae60", pad=5)
    body += b

    render(os.path.join(OUT_DIR, "mission-upload-flow.svg"), w, h, body)


def fig_download_flow():
    """Діаграма вивантаження місії на наземну станцію (Download Transaction Flow)."""
    w, h = 840, 480
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок зверху
    b, _, _ = textbox(w / 2, 28, "ВИТЯГУВАННЯ МІСІЇ НА ЗЕМЛЮ (DOWNLOAD FLOW)", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    x_gcs = 160
    x_drone = 680

    # Шапки
    b1, _, _ = textbox(x_gcs, 75, "Наземна станція (GCS)\n[Керує запитами елементів]", size=13, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=8)
    b2, _, _ = textbox(x_drone, 75, "Польотний контролер (FCU)\n[Відповідає даними з Flash]", size=13, bold=True, fill="#fdf2e9", stroke="#d35400", pad=8)
    body += b1 + b2

    # Лінії життя
    body += line(x_gcs, 105, x_gcs, 455, color="#7f8c8d", sw=1.5, dash="5,4")
    body += line(x_drone, 105, x_drone, 455, color="#7f8c8d", sw=1.5, dash="5,4")

    # 1. MISSION_REQUEST_LIST
    y1 = 140
    body += arrow(x_gcs, y1, x_drone, y1, color="#2457d6", sw=2)
    b, _, _ = textbox(420, y1 - 14, "1. MISSION_REQUEST_LIST (type=MISSION)", size=12, bold=True, fill="#ffffff", stroke="#2457d6", pad=4)
    body += b

    # 2. MISSION_COUNT
    y2 = 185
    body += arrow(x_drone, y2, x_gcs, y2, color="#d35400", sw=2)
    b, _, _ = textbox(420, y2 - 14, "2. MISSION_COUNT (count=2, type=MISSION)", size=12, bold=True, fill="#ffffff", stroke="#d35400", pad=4)
    body += b

    # 3. MISSION_REQUEST_INT (seq=0)
    y3 = 235
    body += arrow(x_gcs, y3, x_drone, y3, color="#2457d6", sw=2)
    b, _, _ = textbox(420, y3 - 14, "3. MISSION_REQUEST_INT (seq=0)", size=12, bold=True, fill="#ffffff", stroke="#2457d6", pad=4)
    body += b

    # 4. MISSION_ITEM_INT (seq=0)
    y4 = 285
    body += arrow(x_drone, y4, x_gcs, y4, color="#d35400", sw=2)
    b, _, _ = textbox(420, y4 - 14, "4. MISSION_ITEM_INT (seq=0: TAKEOFF)", size=12, bold=True, fill="#ffffff", stroke="#d35400", pad=4)
    body += b

    # 5. MISSION_REQUEST_INT (seq=1)
    y5 = 335
    body += arrow(x_gcs, y5, x_drone, y5, color="#2457d6", sw=2)
    b, _, _ = textbox(420, y5 - 14, "5. MISSION_REQUEST_INT (seq=1)", size=12, bold=True, fill="#ffffff", stroke="#2457d6", pad=4)
    body += b

    # 6. MISSION_ITEM_INT (seq=1)
    y6 = 385
    body += arrow(x_drone, y6, x_gcs, y6, color="#d35400", sw=2)
    b, _, _ = textbox(420, y6 - 14, "6. MISSION_ITEM_INT (seq=1: LAND)", size=12, bold=True, fill="#ffffff", stroke="#d35400", pad=4)
    body += b

    # 7. MISSION_ACK
    y7 = 435
    body += arrow(x_gcs, y7, x_drone, y7, color="#27ae60", sw=2.5)
    b, _, _ = textbox(420, y7 - 14, "7. MISSION_ACK (type=MAV_MISSION_ACCEPTED) [Завершення сесії]", size=12, bold=True, fill="#eafaf1", stroke="#27ae60", pad=5)
    body += b

    render(os.path.join(OUT_DIR, "mission-download-flow.svg"), w, h, body)


def fig_mission_protocol_fsm():
    """Скінченний автомат станів протоколу місій (FSM)."""
    w, h = 880, 540
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок
    b, _, _ = textbox(w / 2, 28, "СКІНЧЕННИЙ АВТОМАТ СТАНІВ ТРАНЗАКЦІЙ (GCS / AUTOPILOT FSM)", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    # Стани
    # 1. IDLE (Центральний початковий стан)
    b_idle, _, _ = textbox(440, 100, "СТАН: IDLE (ОЧІКУВАННЯ)\nТранзакція неактивна, автопілот виконує місію з Flash", size=13, bold=True, fill="#ebf5fb", stroke="#2980b9", pad=10)
    body += b_idle

    # 2. UPLOAD STAGING (Ліворуч)
    b_upl, _, _ = textbox(170, 240, "СТАН: UPLOAD_ACTIVE\n• Автопілот чекає черговий seq\n• Перевірка валідності координат\n• Запис у staging RAM-буфер", size=12, bold=True, fill="#fef9e7", stroke="#d35400", pad=8)
    body += b_upl

    # 3. DOWNLOAD STAGING (Праворуч)
    b_down, _, _ = textbox(710, 240, "СТАН: DOWNLOAD_ACTIVE\n• GCS витягує пункти [0..count-1]\n• Автопілот віддає записи\n• Очікування наступного REQUEST_INT", size=12, bold=True, fill="#eafaf1", stroke="#27ae60", pad=8)
    body += b_down

    # 4. TIMEOUT / RETRY (Внизу по центру)
    b_retry, _, _ = textbox(440, 375, "ОБРОБКА ТАЙМАУТУ (TIMEOUT / RETRY)\nТаймер > 250..1500 мс → Повторна відправка запиту\nЛічильник спроб (retries) < 5", size=12, bold=True, fill="#fdedec", stroke="#c0392b", pad=8)
    body += b_retry

    # 5. ERROR / CANCEL (В самому низу)
    b_err, _, _ = textbox(440, 485, "СКАСУВАННЯ / АВАРІЙНЕ СКИДАННЯ (ABORT)\nВідкидання staging-буфера, збереження старого плану, MISSION_ACK(ERROR)", size=11, bold=True, fill="#f2f3f4", stroke="#7f8c8d", pad=6)
    body += b_err

    # Стрілки переходів
    # IDLE -> UPLOAD (MISSION_COUNT)
    body += arrow(320, 120, 230, 185, color="#d35400", sw=2)
    b_tr1, _, _ = textbox(240, 140, "MISSION_COUNT", size=10, bold=True, fill="#ffffff", stroke="#d35400", pad=3)
    body += b_tr1

    # UPLOAD -> IDLE (MISSION_ACK ACCEPTED)
    body += arrow(170, 185, 310, 100, color="#27ae60", sw=2)
    b_tr2, _, _ = textbox(170, 110, "ACK(ACCEPTED)", size=10, bold=True, fill="#ffffff", stroke="#27ae60", pad=3)
    body += b_tr2

    # IDLE -> DOWNLOAD (MISSION_REQUEST_LIST)
    body += arrow(560, 120, 650, 185, color="#27ae60", sw=2)
    b_tr3, _, _ = textbox(640, 140, "REQUEST_LIST", size=10, bold=True, fill="#ffffff", stroke="#27ae60", pad=3)
    body += b_tr3

    # DOWNLOAD -> IDLE (MISSION_ACK)
    body += arrow(710, 185, 570, 100, color="#2980b9", sw=2)
    b_tr4, _, _ = textbox(710, 110, "MISSION_ACK", size=10, bold=True, fill="#ffffff", stroke="#2980b9", pad=3)
    body += b_tr4

    # UPLOAD -> RETRY
    body += arrow(230, 290, 330, 350, color="#c0392b", sw=1.5)
    # DOWNLOAD -> RETRY
    body += arrow(650, 290, 550, 350, color="#c0392b", sw=1.5)

    # RETRY -> UPLOAD / DOWNLOAD (повтор)
    body += arrow(350, 380, 260, 300, color="#d35400", sw=1.5)
    body += arrow(530, 380, 620, 300, color="#27ae60", sw=1.5)

    # RETRY -> ERROR (retries >= 5)
    body += arrow(440, 420, 440, 455, color="#c0392b", sw=2)
    b_tr5, _, _ = textbox(440, 438, "Retries вичерпано (5/5)", size=10, bold=True, fill="#ffffff", stroke="#c0392b", pad=3)
    body += b_tr5

    render(os.path.join(OUT_DIR, "mission-protocol-fsm.svg"), w, h, body)


def fig_mission_item_int_layout():
    """Складання байтів повідомлення MISSION_ITEM_INT (#73, 38 байтів корисного навантаження)."""
    w, h = 840, 440
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок
    b, _, _ = textbox(w / 2, 25, "РОЗКЛАДКА БАЙТІВ У КАДРІ MISSION_ITEM_INT (#73, 38 БАЙТІВ)", size=15, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    # Рядок 1: 4 float параметри (param1..param4) - по 4 байти = 16 байтів
    y_row1 = 80
    b_p1, _, _ = textbox(110, y_row1, "param1 [4 B]\nfloat32\n(затримка / кут)", size=11, bold=True, fill="#ebf5fb", stroke="#2980b9", pad=6)
    b_p2, _, _ = textbox(280, y_row1, "param2 [4 B]\nfloat32\n(радіус прийняття)", size=11, bold=True, fill="#ebf5fb", stroke="#2980b9", pad=6)
    b_p3, _, _ = textbox(450, y_row1, "param3 [4 B]\nfloat32\n(проліт / обхід)", size=11, bold=True, fill="#ebf5fb", stroke="#2980b9", pad=6)
    b_p4, _, _ = textbox(620, y_row1, "param4 [4 B]\nfloat32\n(рискання yaw / NaN)", size=11, bold=True, fill="#ebf5fb", stroke="#2980b9", pad=6)
    body += b_p1 + b_p2 + b_p3 + b_p4

    # Рядок 2: Координати x, y, z (int32, int32, float32) - 12 байтів (зсув 16..27)
    y_row2 = 175
    b_x, _, _ = textbox(160, y_row2, "x (Latitude) [4 B, int32]\nШирота в градусах × 10⁷\n(дискретність ~1.1 см)", size=11, bold=True, fill="#eafaf1", stroke="#27ae60", pad=7)
    b_y, _, _ = textbox(420, y_row2, "y (Longitude) [4 B, int32]\nДовгота в градусах × 10⁷\n(дискретність ~1.1 см)", size=11, bold=True, fill="#eafaf1", stroke="#27ae60", pad=7)
    b_z, _, _ = textbox(670, y_row2, "z (Altitude) [4 B, float32]\nВисота в метрах\n(AMSL / Relative / Terrain)", size=11, bold=True, fill="#fef9e7", stroke="#d35400", pad=7)
    body += b_x + b_y + b_z

    # Рядок 3: Службові поля (seq, command, target_system, target_component, frame, current, autocontinue, mission_type) - 10 байтів (зсув 28..37)
    y_row3 = 275
    b_seq, _, _ = textbox(110, y_row3, "seq [2 B]\nuint16\n(індекс 0..N)", size=10, bold=True, fill="#f4ecf7", stroke="#8e44ad", pad=5)
    b_cmd, _, _ = textbox(240, y_row3, "command [2 B]\nuint16\n(MAV_CMD код)", size=10, bold=True, fill="#f4ecf7", stroke="#8e44ad", pad=5)
    b_ts, _, _ = textbox(360, y_row3, "target_sys [1 B]\nuint8\n(ID апарата)", size=10, bold=True, fill="#f2f3f4", stroke="#7f8c8d", pad=5)
    b_tc, _, _ = textbox(470, y_row3, "target_comp [1 B]\nuint8\n(1 = FCU)", size=10, bold=True, fill="#f2f3f4", stroke="#7f8c8d", pad=5)
    b_frm, _, _ = textbox(575, y_row3, "frame [1 B]\nuint8\n(MAV_FRAME)", size=10, bold=True, fill="#f2f3f4", stroke="#7f8c8d", pad=5)
    b_flags, _, _ = textbox(715, y_row3, "flags: cur / auto / type [3 B]\nuint8 + uint8 + uint8\n(поточний / авто / тип місії)", size=10, bold=True, fill="#fdedec", stroke="#c0392b", pad=5)
    body += b_seq + b_cmd + b_ts + b_tc + b_frm + b_flags

    # Пояснювальний блок знизу
    b_note, _, _ = textbox(w / 2, 380, "Повідомлення впорядковане за спаданням розміру полів (MAVLink Data Alignment):\nFloat32 / Int32 (4 байти) → UInt16 (2 байти) → UInt8 (1 байт) для виключення нерівномірного padding на MCU", size=11, fill="#f8f9f9", stroke="#bdc3c7", pad=8)
    body += b_note

    render(os.path.join(OUT_DIR, "mission-item-int-layout.svg"), w, h, body)


def fig_half_duplex_collision():
    """Схема часового розділення напівдуплексного радіоканалу (TDD Half-Duplex Turnaround)."""
    w, h = 860, 460
    body = rect(0, 0, w, h, fill="#ffffff", stroke="#ffffff", sw=0)

    # Заголовок
    b, _, _ = textbox(w / 2, 25, "ПЕРЕДАЧА В НАПІВДУПЛЕКСНОМУ КАНАЛІ З ЧАСОВИМ РОЗДІЛЕННЯМ (TDD)", size=14, bold=True, fill="#eef2f7", stroke="#2c3e50")
    body += b

    # Блок 1: Потоковий Push (зверху)
    body += text(50, 65, "1. ПОТОКОВИЙ PUSH (БЕЗ STOP-AND-WAIT) — ЗУСТРІЧНА КОЛІЗІЯ", size=12, bold=True, color="#c0392b", anchor="start")
    y_t1 = 125
    body += arrow(50, y_t1, 800, y_t1, color="#2c3e50", sw=2)
    body += text(810, y_t1 + 4, "Час (t)", size=11, bold=True, anchor="start")

    # GCS пакети зверху осі
    b_gcs1, _, _ = textbox(170, 95, "GCS: ITEM_0", size=11, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=4)
    b_gcs2, _, _ = textbox(300, 95, "GCS: ITEM_1", size=11, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=4)
    b_gcs3, _, _ = textbox(430, 95, "GCS: ITEM_2", size=11, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=4)
    body += b_gcs1 + b_gcs2 + b_gcs3

    # Дрон пакети знизу осі
    b_dr1, _, _ = textbox(235, 155, "FCU: ATTITUDE (50Hz)", size=10, bold=True, fill="#fdf2e9", stroke="#d35400", pad=4)
    b_dr2, _, _ = textbox(365, 155, "FCU: GLOBAL_POS", size=10, bold=True, fill="#fdf2e9", stroke="#d35400", pad=4)
    body += b_dr1 + b_dr2

    # Зона взаємного глушіння праворуч
    b_bang, _, _ = textbox(600, 125, "КОЛІЗІЯ В ЕФІРІ\nВзаємне глушіння пакетів", size=11, bold=True, fill="#fdedec", stroke="#c0392b", pad=6)
    body += b_bang

    # Блок 2: Транзакційний Stop-and-Wait (Pull) (знизу)
    body += text(50, 220, "2. ТРАНЗАКЦІЙНИЙ STOP-AND-WAIT (PULL) — ЧЕРГУВАННЯ RX/TX БЕЗ КОЛІЗІЙ", size=12, bold=True, color="#27ae60", anchor="start")
    y_t2 = 300
    body += arrow(50, y_t2, 800, y_t2, color="#2c3e50", sw=2)
    body += text(810, y_t2 + 4, "Час (t)", size=11, bold=True, anchor="start")

    # 1. GCS -> COUNT
    b_ok1, _, _ = textbox(130, 260, "GCS → COUNT", size=10, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=4)
    # Turnaround
    b_tu1, _, _ = textbox(215, 300, "TX→RX\n10 мс", size=9, fill="#f4f6f8", stroke="#7f8c8d", pad=3)
    # 2. FCU -> REQUEST_INT(0)
    b_ok2, _, _ = textbox(300, 340, "FCU → REQ(0)", size=10, bold=True, fill="#fdf2e9", stroke="#d35400", pad=4)
    # Turnaround
    b_tu2, _, _ = textbox(385, 300, "RX→TX\n10 мс", size=9, fill="#f4f6f8", stroke="#7f8c8d", pad=3)
    # 3. GCS -> ITEM_INT(0)
    b_ok3, _, _ = textbox(470, 260, "GCS → ITEM(0)", size=10, bold=True, fill="#e8f4fd", stroke="#2457d6", pad=4)
    # Turnaround + запис у Flash
    b_tu3, _, _ = textbox(565, 300, "Flash Write\n+ REQ(1)", size=9, fill="#fef9e7", stroke="#f39c12", pad=3)
    # 4. FCU -> REQUEST_INT(1)
    b_ok4, _, _ = textbox(660, 340, "FCU → REQ(1)", size=10, bold=True, fill="#fdf2e9", stroke="#d35400", pad=4)

    body += b_ok1 + b_tu1 + b_ok2 + b_tu2 + b_ok3 + b_tu3 + b_ok4

    # Пояснення знизу
    b_bot, _, _ = textbox(w / 2, 415, "Отримувач сам запитує кожен наступний пункт лише тоді, коли готовий прийняти та записати його,\nщо гарантує відсутність колізій на фізичному рівні радіомодему SiK / ELRS / Crossfire", size=11, fill="#eafaf1", stroke="#27ae60", pad=6)
    body += b_bot

    render(os.path.join(OUT_DIR, "half-duplex-collision.svg"), w, h, body)


if __name__ == "__main__":
    fig_upload_flow()
    fig_download_flow()
    fig_mission_protocol_fsm()
    fig_mission_item_int_layout()
    fig_half_duplex_collision()
    print("Всі SVG успішно згенеровано.")
