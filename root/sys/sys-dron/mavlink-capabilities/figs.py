# -*- coding: utf-8 -*-
"""Фігури до теми «Можливості апарата: бітова маска AUTOPILOT_VERSION».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольори
COL_GCS   = "#2457d6"   # НСКУ (синій)
COL_AP    = "#c0392b"   # Автопілот (червоний)
COL_CAP   = "#27ae60"   # Можливості / маска (зелений)
COL_VER   = "#8e44ad"   # Версії (фіолетовий)
COL_UID   = "#d35400"   # UID / залізо (помаранчевий)
COL_ACK   = "#16a085"   # Підтвердження / ACK (бірюзовий)


# ── 1. Послідовність узгодження можливостей (Handshake Sequence) ─────────────
def fig_negotiation_sequence():
    W, H = 840, 520
    f = [text(W / 2, 28, "Процедура запиту та узгодження можливостей (Capability Handshake)", size=15, bold=True)]

    x_gcs = 160
    x_ap  = 680
    y_top = 70
    y_bot = 480

    # Заголовки ліній життя
    b_gcs, _, _ = textbox(x_gcs, y_top, "Наземна станція (GCS)\nQGroundControl / Mission Planner", size=11, bold=True, stroke=COL_GCS)
    b_ap, _, _  = textbox(x_ap, y_top, "Польотний контролер (Autopilot)\nPX4 / ArduPilot", size=11, bold=True, stroke=COL_AP)
    f.append(b_gcs)
    f.append(b_ap)

    # Вертикальні лінії життя (розриваємо навколо блоку стану, щоб не перетинати написи)
    f.append(line(x_gcs, y_top + 28, x_gcs, 360, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(x_gcs, 445, x_gcs, y_bot, color=MUTED, sw=1.5, dash="4,4"))
    f.append(line(x_ap, y_top + 28, x_ap, y_bot, color=MUTED, sw=1.5, dash="4,4"))

    # Повідомлення
    # 1. HEARTBEAT від автопілота
    y1 = 140
    f.append(arrow(x_ap, y1, x_gcs, y1, color=COL_AP, sw=1.8))
    f.append(text((x_gcs + x_ap) / 2, y1 - 10, "1. HEARTBEAT (#0) — тип апарата, автопілот, стан готовності", size=11, color=COL_AP, bold=True))

    # 2. GCS шле MAV_CMD_REQUEST_MESSAGE
    y2 = 205
    f.append(arrow(x_gcs, y2, x_ap, y2, color=COL_GCS, sw=1.8))
    f.append(text((x_gcs + x_ap) / 2, y2 - 10, "2. COMMAND_LONG: MAV_CMD_REQUEST_MESSAGE (#512) [param1 = 148]", size=11, color=COL_GCS, bold=True))

    # 3. Автопілот відповідає AUTOPILOT_VERSION
    y3 = 270
    f.append(arrow(x_ap, y3, x_gcs, y3, color=COL_CAP, sw=2.0))
    f.append(text((x_gcs + x_ap) / 2, y3 - 10, "3. AUTOPILOT_VERSION (#148) — маска capabilities, версії SemVer, UID2", size=11, color=COL_CAP, bold=True))

    # 4. Автопілот шле COMMAND_ACK
    y4 = 330
    f.append(arrow(x_ap, y4, x_gcs, y4, color=COL_ACK, sw=1.6))
    f.append(text((x_gcs + x_ap) / 2, y4 - 10, "4. COMMAND_ACK (#77) — command=512, result=MAV_RESULT_ACCEPTED", size=10.5, color=COL_ACK))

    # 5. Внутрішній стан GCS (блок розбору маски)
    y5 = 400
    b_dec, w_dec, h_dec = textbox(x_gcs, y5, "Розбір маски capabilities:\n✓ MISSION_INT (int32 координати)\n✓ PARAM_UNION / FTP (швидкі параметри)\n✓ PROTOCOL_V2 (MAVLink 2.0)", size=9.5, pad=8, fill="#e8f8f5", stroke=COL_CAP)
    f.append(b_dec)

    # 6. Активація протоколів
    y6 = 460
    f.append(arrow(x_gcs, y6, x_ap, y6, color=COL_GCS, sw=1.8))
    f.append(text((x_gcs + x_ap) / 2, y6 - 10, "5. Активація протоколів: завантаження місії через MISSION_INT / FTP", size=11, color=INK, bold=True))

    render(os.path.join(IMG, "negotiation-sequence.svg"), W, H, *f)


# ── 2. Структура корисного навантаження AUTOPILOT_VERSION (#148) ─────────────
def fig_autopilot_version_packet():
    W, H = 840, 380
    f = [text(W / 2, 26, "Структура корисного навантаження AUTOPILOT_VERSION (#148, 78 байтів)", size=15, bold=True)]

    x0 = 30
    span = W - 60

    # Рядок 1: capabilities (8B), uid (8B)
    y1 = 65
    h1 = 52
    w_cap = span * 0.5
    w_uid = span * 0.5
    f.append(rect(x0, y1, w_cap, h1, fill="#eafaf1", stroke=COL_CAP, sw=2))
    f.append(text(x0 + w_cap / 2, y1 + 22, "capabilities (uint64_t, 8 байтів)", size=12, color=COL_CAP, bold=True))
    f.append(text(x0 + w_cap / 2, y1 + 40, "Бітова маска підтримуваних протоколів та команд MAVLink", size=10, color=MUTED))

    f.append(rect(x0 + w_cap, y1, w_uid, h1, fill="#fef5e7", stroke=COL_UID, sw=2))
    f.append(text(x0 + w_cap + w_uid / 2, y1 + 22, "uid (uint64_t, 8 байтів)", size=12, color=COL_UID, bold=True))
    f.append(text(x0 + w_cap + w_uid / 2, y1 + 40, "Застарілий 64-бітний апаратний ідентифікатор CPU", size=10, color=MUTED))

    # Рядок 2: 4 версії по 4 байти (flight_sw, middleware_sw, os_sw, board_version)
    y2 = 130
    h2 = 52
    w_v = span / 4
    v_fields = [
        ("flight_sw_version", "SemVer прошивки"),
        ("middleware_sw_version", "Версія middleware"),
        ("os_sw_version", "Версія RTOS (NuttX)"),
        ("board_version", "Ревізія друкованої плати"),
    ]
    for i, (name, desc) in enumerate(v_fields):
        xi = x0 + i * w_v
        f.append(rect(xi, y2, w_v, h2, fill="#f4ecf7", stroke=COL_VER, sw=1.8))
        f.append(text(xi + w_v / 2, y2 + 22, name, size=10.5, color=COL_VER, bold=True))
        f.append(text(xi + w_v / 2, y2 + 40, desc, size=10, color=MUTED))

    # Рядок 3: custom version hashes (8B + 8B + 8B) + vendor_id (2B) + product_id (2B)
    y3 = 195
    h3 = 54
    w_cust = span * 0.23
    w_ids  = (span - 3 * w_cust) / 2
    c_fields = [
        ("flight_custom_version", "Git SHA прошивки (8Б)", w_cust, "#fef9e7", COL_VER),
        ("middleware_custom_version", "Git SHA middleware (8Б)", w_cust, "#fef9e7", COL_VER),
        ("os_custom_version", "Git SHA RTOS (8Б)", w_cust, "#fef9e7", COL_VER),
        ("vendor_id", "ID вендора (2Б)", w_ids, "#ebf5fb", COL_GCS),
        ("product_id", "ID продукту (2Б)", w_ids, "#ebf5fb", COL_GCS),
    ]
    cur_x = x0
    for name, desc, w_box, bg_c, strk_c in c_fields:
        f.append(rect(cur_x, y3, w_box, h3, fill=bg_c, stroke=strk_c, sw=1.6))
        f.append(text(cur_x + w_box / 2, y3 + 22, name, size=9.5, color=strk_c, bold=True))
        f.append(text(cur_x + w_box / 2, y3 + 41, desc, size=9.5, color=MUTED))
        cur_x += w_box

    # Рядок 4: uid2 (uint8_t[18], 18 байтів)
    y4 = 262
    h4 = 52
    f.append(rect(x0, y4, span, h4, fill="#fbeee6", stroke=COL_UID, sw=2))
    f.append(text(x0 + span / 2, y4 + 22, "uid2 (uint8_t[18], 18 байтів)", size=12, color=COL_UID, bold=True))
    f.append(text(x0 + span / 2, y4 + 40, "128-бітний апаратний серійний номер чіпа (UUID) або розширений UID з байтом формату", size=10.5, color=INK))

    f.append(text(W / 2, 345, "Усі багатобайтові поля впорядковано за спаданням розміру (uint64 -> uint32 -> uint16 -> uint8) для сумісності з MAVLink v2 x255", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "autopilot-version-packet.svg"), W, H, *f)


# ── 3. Кодування SemVer у flight_sw_version ──────────────────────────────────
def fig_semver_bitfield():
    W, H = 800, 260
    f = [text(W / 2, 26, "Кодування семантичної версії в 32-бітному полі flight_sw_version", size=15, bold=True)]

    x0 = 40
    y0 = 65
    span = W - 80
    w_byte = span / 4
    h_box = 60

    bytes_info = [
        ("Біти 31..24 [Байт 3 / MSB]", "Major (головна версія)", "1 (0x01)", COL_AP),
        ("Біти 23..16 [Байт 2]", "Minor (додаткова версія)", "14 (0x0E)", COL_VER),
        ("Біти 15..8 [Байт 1]", "Patch (патч/виправлення)", "0 (0x00)", COL_CAP),
        ("Біти 7..0 [Байт 0 / LSB]", "Release Type (тип релізу)", "192 (0xC0 = RC)", COL_GCS),
    ]

    for i, (bits, name, val, col) in enumerate(bytes_info):
        xi = x0 + i * w_byte
        f.append(rect(xi, y0, w_byte, h_box, fill=BG, stroke=col, sw=2))
        f.append(text(xi + w_byte / 2, y0 + 20, bits, size=10, color=MUTED))
        f.append(text(xi + w_byte / 2, y0 + 38, name, size=11, color=col, bold=True))
        f.append(text(xi + w_byte / 2, y0 + 52, f"Приклад: {val}", size=10, color=INK, italic=True))

    # Типи релізів (FIRMWARE_VERSION_TYPE)
    y_enum = 145
    f.append(rect(x0, y_enum, span, 80, fill="#f8f9fa", stroke=LINE, sw=1.2))
    f.append(text(W / 2, y_enum + 20, "Шкала FIRMWARE_VERSION_TYPE (значення байта 0):", size=11, bold=True))

    types = [
        ("0x00 (0)", "DEV (розробка)"),
        ("0x40 (64)", "ALPHA"),
        ("0x80 (128)", "BETA"),
        ("0xC0 (192)", "RC (кандидат)"),
        ("0xFF (255)", "OFFICIAL (стабільний)"),
    ]
    w_t = span / 5
    for i, (code, t_name) in enumerate(types):
        xt = x0 + i * w_t + w_t / 2
        f.append(text(xt, y_enum + 44, code, size=11, color=COL_GCS, bold=True))
        f.append(text(xt, y_enum + 62, t_name, size=10, color=INK))

    f.append(text(W / 2, 245, "Число 0x010E00C0 розпаковується як v1.14.0-rc", size=11.5, color=COL_AP, bold=True))

    render(os.path.join(IMG, "semver-bitfield.svg"), W, H, *f)


# ── 4. Бітова маска можливостей capabilities ────────────────────────────────
def fig_capabilities_mask():
    W, H = 820, 390
    f = [text(W / 2, 26, "64-бітна маска capabilities: ключові прапорці протоколу MAVLink", size=15, bold=True)]

    # Список ключових прапорців
    flags = [
        ("Бит 0 (0x0001)", "MISSION_FLOAT", "Застарілі float-координати місії (точність ~1.1 м на екваторі)", False),
        ("Бит 2 (0x0004)", "MISSION_INT", "Цілочисельні int32 координати (1e7 град, точність ~1 см)", True),
        ("Бит 1 (0x0002)", "PARAM_FLOAT", "Базовий протокол параметрів (одинарна точність float32)", False),
        ("Бит 4 (0x0010)", "PARAM_UNION", "Розширений протокол параметрів PARAM_EXT_* (типізовані поля int/float)", True),
        ("Бит 5 (0x0020)", "FTP", "Протокол MAVLink FTP (пакетний обмін файлами та логами через burst-пакети)", True),
        ("Бит 6 (0x0040)", "SET_ATTITUDE_TARGET", "Пряме керування орієнтацією та тягою (offboard attitude setpoints)", True),
        ("Бит 7 (0x0080)", "SET_POS_TARGET_LOCAL_NED", "Керування положенням/швидкістю в локальній системі NED", True),
        ("Бит 11 (0x0800)", "COMPASS_CALIBRATION", "Бортове калібрування компаса (автопілот сам обчислює матрицю корекції)", True),
        ("Бит 12 (0x1000)", "MAVLINK2 / PROTOCOL_V2", "Повна підтримка кадрів MAVLink 2.0 (пакетні розширення та підпис)", True),
        ("Бит 15 (0x8000)", "FLIGHT_INFORMATION", "Повідомлення FLIGHT_INFORMATION (час озброєння, час польоту)", True),
    ]

    y0 = 60
    rh = 28
    w_box = W - 60
    x0 = 30

    for i, (bit_lbl, name, desc, is_modern) in enumerate(flags):
        yi = y0 + i * rh
        col_stroke = COL_CAP if is_modern else MUTED
        fill_bg = "#eafaf1" if is_modern else "#f8f9fa"

        f.append(rect(x0, yi, 140, rh - 4, fill=fill_bg, stroke=col_stroke, sw=1.4))
        f.append(text(x0 + 70, yi + 16, bit_lbl, size=10, color=col_stroke, bold=True))

        f.append(rect(x0 + 145, yi, 200, rh - 4, fill=fill_bg, stroke=col_stroke, sw=1.4))
        f.append(text(x0 + 245, yi + 16, name, size=10, color=INK, bold=True))

        f.append(rect(x0 + 350, yi, w_box - 350, rh - 4, fill=BG, stroke=LINE, sw=1.0))
        f.append(text(x0 + 360, yi + 16, desc, size=10, color=INK, anchor="start"))

    f.append(text(W / 2, y0 + len(flags) * rh + 20, "GCS формує внутрішню таблицю можливостей апарата під час підключення і блокує несумісні команди", size=10.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "capabilities-mask.svg"), W, H, *f)


if __name__ == "__main__":
    fig_negotiation_sequence()
    fig_autopilot_version_packet()
    fig_semver_bitfield()
    fig_capabilities_mask()
    print("Всі фігури згенеровано успішно.")
