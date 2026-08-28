# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_handshake_fsm():
    W, H = 940, 480
    p = []

    stages = [
        ("1. Виявлення серцебиття", "HEARTBEAT (#0)\nsysid, compid, MAV_TYPE,\nMAV_AUTOPILOT, base_mode", FIELD, "#eef8f2"),
        ("2. Вичитка параметрів", "PARAM_REQUEST_LIST (#21)\nпотік PARAM_VALUE (#22)\nдозапит пропущених індексів", NEG, "#eaf0fd"),
        ("3. Налаштування потоків", "MAV_CMD_SET_MESSAGE_INTERVAL\nATTITUDE (20 Гц), POS (5 Гц),\nSYS_STATUS (1 Гц), BATTERY (1 Гц)", "#8e44ad", "#f5eef8"),
        ("4. Синхронізація місії", "MISSION_REQUEST_LIST (#43)\nMISSION_COUNT (#44) → ITEMS (#73)\nфінал: MISSION_ACK (#47)", "#d35400", "#fef5ec"),
        ("5. Робочий стан (READY)", "Фоновий HEARTBEAT (1 Гц)\nконтроль таймаутів лінка (3 с)\nвідображення телеметрії", POS, "#fdecea"),
    ]

    bw, bh = 164, 210
    start_x = 32
    spacing = 182
    y_box = 100

    for i, (title, desc, color, fill) in enumerate(stages):
        x = start_x + i * spacing
        p.append(rect(x, y_box, bw, bh, fill=fill, stroke=color, sw=2, rx=8))
        p.append(text(x + bw / 2, y_box + 28, title, size=11, color=color, bold=True))
        p.append(line(x + 10, y_box + 40, x + bw - 10, y_box + 40, color=color, sw=1, dash="2,2"))
        p.append(mtext(x + bw / 2, y_box + 68, desc, size=10, color=INK, lh=1.35))

        if i < len(stages) - 1:
            ax1 = x + bw + 2
            ax2 = x + spacing - 2
            ay = y_box + bh / 2
            p.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=2))

    # Нижній блок: контроль таймаутів і відкат станів
    ny = 350
    p.append(rect(start_x, ny, W - 2 * start_x, 90, fill="#fafbfc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(W / 2, ny + 24, "Захисні механізми кожного ступеня конвеєра", size=12, color=INK, bold=True))
    bullets = (
        "• Немає HEARTBEAT > 3.5 с → перехід у LINK_LOST, скидання готовності оператора\n"
        "• Втрата окремих пакетів параметрів/місії → виявлення дірок у бітовій масці та дозапит за індексом\n"
        "• Перевищення ліміту повторів (5 спроб) → сповіщення про помилку ініціалізації без блокування UI"
    )
    p.append(mtext(W / 2, ny + 46, bullets, size=10, color=MUTED, lh=1.35))

    render(os.path.join(OUT, "handshake-fsm.svg"), W, H, *p,
           title="Поетапний конвеєр первинного рукостискання GCS та автопілота")


def fig_param_sync_recovery():
    W, H = 940, 460
    p = []

    # Верхній пояс: відправка запиту
    p.append(rect(40, 60, 240, 50, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(160, 82, "Наземна станція (GCS)", size=11, color=NEG, bold=True))
    p.append(text(160, 98, "Шле PARAM_REQUEST_LIST (#21)", size=9, color=INK))

    p.append(arrow(280, 85, 620, 85, color=NEG, sw=1.8))
    p.append(text(450, 75, "PARAM_REQUEST_LIST (sys=1, comp=1)", size=9, color=NEG, bold=True))

    p.append(rect(620, 60, 280, 50, fill="#eef8f2", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(760, 82, "Автопілот (Pixhawk / ArduPilot)", size=11, color=FIELD, bold=True))
    p.append(text(760, 98, "Відповідає потоком: param_count = 8", size=9, color=INK))

    # Середній пояс: потік пакетів та втрати
    sy = 150
    p.append(text(W / 2, sy, "Потік відповідей PARAM_VALUE (індекси 0 .. 7)", size=11, color=INK, bold=True))

    indices = [
        (0, True, "IDX 0: RC1_MIN"),
        (1, True, "IDX 1: RC1_MAX"),
        (2, False, "IDX 2: WPNAV_SPEED (ВТРАЧЕНО)"),
        (3, True, "IDX 3: BATT_CAPACITY"),
        (4, True, "IDX 4: RTL_ALT"),
        (5, False, "IDX 5: FS_THR_VALUE (ВТРАЧЕНО)"),
        (6, True, "IDX 6: MOT_SPIN_ARM"),
        (7, True, "IDX 7: INS_GYR_CAL"),
    ]

    bx_start = 30
    bx_w = 102
    bx_gap = 9

    for i, (idx, ok, label) in enumerate(indices):
        bx = bx_start + i * (bx_w + bx_gap)
        by = sy + 20
        if ok:
            p.append(rect(bx, by, bx_w, 65, fill="#eef8f2", stroke=FIELD, sw=1.5, rx=4))
            p.append(text(bx + bx_w / 2, by + 20, "PARAM_VALUE", size=9, color=FIELD, bold=True))
            p.append(text(bx + bx_w / 2, by + 36, "idx = %d (OK)" % idx, size=9, color=INK))
            p.append(text(bx + bx_w / 2, by + 52, label.split(": ")[1], size=9, color=MUTED))
        else:
            p.append(rect(bx, by, bx_w, 65, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
            p.append(text(bx + bx_w / 2, by + 20, "ЗАВАДА", size=9, color=POS, bold=True))
            p.append(text(bx + bx_w / 2, by + 36, "idx = %d (CRC)" % idx, size=9, color=POS))
            p.append(text(bx + bx_w / 2, by + 52, "Втрачено", size=9, color=POS, italic=True))

    # Нижній пояс: бітова маска та дозапит
    my = 280
    p.append(rect(30, my, W - 60, 50, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=6))
    p.append(text(140, my + 28, "Бітова маска в GCS:", size=11, color=INK, bold=True))
    mask_str = "[ 1 | 1 | 0 | 1 | 1 | 0 | 1 | 1 ]  →  Дірки на позиціях 2 та 5 (отримано 6/8)"
    p.append(text(540, my + 28, mask_str, size=11, color=POS, bold=True))

    # Адресні дозапити
    ry = 355
    p.append(rect(30, ry, 420, 80, fill="#fef5ec", stroke="#d35400", sw=1.5, rx=6))
    p.append(text(240, ry + 22, "1. Адресний дозапит пропущеного індексу 2", size=10, color="#d35400", bold=True))
    p.append(text(240, ry + 42, "GCS → PARAM_REQUEST_READ (param_index=2)", size=9, color=INK))
    p.append(text(240, ry + 62, "Автопілот → PARAM_VALUE (WPNAV_SPEED, idx=2)", size=9, color=FIELD))

    p.append(rect(490, ry, 420, 80, fill="#fef5ec", stroke="#d35400", sw=1.5, rx=6))
    p.append(text(700, ry + 22, "2. Адресний дозапит пропущеного індексу 5", size=10, color="#d35400", bold=True))
    p.append(text(700, ry + 42, "GCS → PARAM_REQUEST_READ (param_index=5)", size=9, color=INK))
    p.append(text(700, ry + 62, "Автопілот → PARAM_VALUE (FS_THR_VALUE, idx=5)", size=9, color=FIELD))

    render(os.path.join(OUT, "param-sync-recovery.svg"), W, H, *p,
           title="Відновлення пропущених параметрів за бітовою маскою індексів")


def fig_mission_fsm_flow():
    W, H = 940, 520
    p = []

    # Дві лінії учасників (GCS та Autopilot)
    gcs_x = 180
    ap_x = 760
    top_y = 65
    bot_y = 485

    p.append(rect(gcs_x - 100, top_y, 200, 36, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    p.append(text(gcs_x, top_y + 23, "Наземна станція (GCS)", size=12, color=NEG, bold=True))
    p.append(line(gcs_x, top_y + 36, gcs_x, bot_y, color=MUTED, sw=1.5, dash="4,4"))

    p.append(rect(ap_x - 100, top_y, 200, 36, fill="#eef8f2", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(ap_x, top_y + 23, "Автопілот (Борт)", size=12, color=FIELD, bold=True))
    p.append(line(ap_x, top_y + 36, ap_x, bot_y, color=MUTED, sw=1.5, dash="4,4"))

    # Крок 1: Запит кількості
    y1 = 130
    p.append(arrow(gcs_x, y1, ap_x, y1, color=NEG, sw=1.8))
    p.append(text((gcs_x + ap_x) / 2, y1 - 8, "1. MISSION_REQUEST_LIST (#43) [mission_type = MAV_MISSION_TYPE_MISSION]", size=10, color=NEG, bold=True))

    # Крок 2: Відповідь кількості
    y2 = 175
    p.append(arrow(ap_x, y2, gcs_x, y2, color=FIELD, sw=1.8))
    p.append(text((gcs_x + ap_x) / 2, y2 - 8, "2. MISSION_COUNT (#44) [count = N, наприклад 3 елементи]", size=10, color=FIELD, bold=True))

    # Рамка циклу вичитки
    cy_top = 205
    cy_h = 195
    p.append(rect(gcs_x - 40, cy_top, ap_x - gcs_x + 80, cy_h, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(gcs_x - 30, cy_top + 18, "ТРАНЗАКЦІЙНИЙ ЦИКЛ (покрокова вичитка точок i = 0 .. N-1)", size=9, color=MUTED, anchor="start", bold=True))

    # Точка 0
    y3 = 245
    p.append(arrow(gcs_x, y3, ap_x, y3, color=INK, sw=1.5))
    p.append(text((gcs_x + ap_x) / 2, y3 - 6, "MISSION_REQUEST_INT (#51) [seq = 0]", size=9, color=INK))

    y4 = 280
    p.append(arrow(ap_x, y4, gcs_x, y4, color=FIELD, sw=1.5))
    p.append(text((gcs_x + ap_x) / 2, y4 - 6, "MISSION_ITEM_INT (#73) [seq = 0, TAKEOFF, lat/lon/alt]", size=9, color=FIELD))

    # Точка 1 (із затримкою / таймаутом)
    y5 = 325
    p.append(arrow(gcs_x, y5, ap_x, y5, color=INK, sw=1.5))
    p.append(text((gcs_x + ap_x) / 2, y5 - 6, "MISSION_REQUEST_INT (#51) [seq = 1]", size=9, color=INK))

    y6 = 360
    p.append(arrow(ap_x, y6, gcs_x, y6, color=FIELD, sw=1.5))
    p.append(text((gcs_x + ap_x) / 2, y6 - 6, "MISSION_ITEM_INT (#73) [seq = 1, WAYPOINT, lat/lon/alt]", size=9, color=FIELD))

    # Крок фіналу: підтвердження всієї місії
    y7 = 430
    p.append(arrow(gcs_x, y7, ap_x, y7, color=POS, sw=2))
    p.append(text((gcs_x + ap_x) / 2, y7 - 8, "3. MISSION_ACK (#47) [type = MAV_MISSION_ACCEPTED (0)]", size=10, color=POS, bold=True))

    p.append(rect(gcs_x + 40, 455, ap_x - gcs_x - 80, 32, fill="#fdecea", stroke=POS, sw=1.2, rx=4))
    p.append(text((gcs_x + ap_x) / 2, 475, "Транзакцію успішно закрито: план завантажено повністю й узгоджено", size=9, color=POS, bold=True))

    render(os.path.join(OUT, "mission-fsm-flow.svg"), W, H, *p,
           title="Транзакційний протокол обміну місією з гарантованим підтвердженням")


if __name__ == "__main__":
    fig_handshake_fsm()
    fig_param_sync_recovery()
    fig_mission_fsm_flow()
    print("OK: all figures rendered ->", OUT)
