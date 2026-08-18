# -*- coding: utf-8 -*-
"""Фігури до теми «Словник MAVLink».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки
C_CORE   = "#2457d6"   # базові визначення (синій)
C_COMMON = "#1e824c"   # спільні повідомлення (зелений)
C_DIAL   = "#d35400"   # діалекти вендорів (помаранчевий)
C_WARN   = "#c0392b"   # розширення / особливості (червоний)
C_V1     = "#8e44ad"   # v1 простір (фіолетовий)
C_V2     = "#2980b9"   # v2 простір (блакитний)
C_ALIGN  = "#27ae60"   # вирівнювання (зелений)


# ── 1. Ієрархія XML-дефініцій та успадкування через <include> ────────────────
def fig_xml_hierarchy():
    W, H = 840, 430
    f = [text(W / 2, 28, "Ієрархія XML-визначень MAVLink та успадкування через include", size=15, bold=True)]

    # Рівень 1: minimal.xml
    x1, y1, w1, h1 = 50, 60, 740, 62
    f.append(rect(x1, y1, w1, h1, fill="#edf2fa", stroke=C_CORE, sw=2, rx=8))
    f.append(text(x1 + 16, y1 + 24, "minimal.xml", size=13, color=C_CORE, bold=True, anchor="start"))
    f.append(text(x1 + 16, y1 + 46, "Ядро протоколу: HEARTBEAT (#0), PROTOCOL_VERSION (#300). Не залежить від інших файлів.", size=11.5, color=INK, anchor="start"))

    # Стрілка включення до standard.xml
    f.append(arrow(W / 2, y1 + h1, W / 2, y1 + h1 + 24, color=C_CORE, sw=1.6))
    f.append(text(W / 2 + 55, y1 + h1 + 16, "<include>", size=10.5, color=MUTED, italic=True))

    # Рівень 2: standard.xml
    y2, h2 = y1 + h1 + 28, 62
    f.append(rect(x1, y2, w1, h2, fill="#eafaf1", stroke=C_COMMON, sw=2, rx=8))
    f.append(text(x1 + 16, y2 + 24, "standard.xml", size=13, color=C_COMMON, bold=True, anchor="start"))
    f.append(text(x1 + 16, y2 + 46, "Базовий стандарт керування: AUTOPILOT_VERSION (#148), SYSTEM_TIME (#2), PING (#4), PARAM-протокол.", size=11.5, color=INK, anchor="start"))

    # Стрілка включення до common.xml
    f.append(arrow(W / 2, y2 + h2, W / 2, y2 + h2 + 24, color=C_COMMON, sw=1.6))
    f.append(text(W / 2 + 55, y2 + h2 + 16, "<include>", size=10.5, color=MUTED, italic=True))

    # Рівень 3: common.xml
    y3, h3 = y2 + h2 + 28, 70
    f.append(rect(x1, y3, w1, h3, fill="#fef9e7", stroke="#b7950b", sw=2, rx=8))
    f.append(text(x1 + 16, y3 + 24, "common.xml", size=13, color="#b7950b", bold=True, anchor="start"))
    f.append(text(x1 + 16, y3 + 44, "Загальний словник БПЛА: ATTITUDE (#30), GLOBAL_POSITION_INT (#33), SYS_STATUS (#1), GPS_RAW_INT (#24),", size=11, color=INK, anchor="start"))
    f.append(text(x1 + 16, y3 + 60, "COMMAND_LONG (#76), COMMAND_INT (#75), STATUSTEXT (#253), HIGHRES_IMU (#105), VFR_HUD (#74).", size=11, color=INK, anchor="start"))

    # Стрілки розгалуження до діалектів
    y4 = y3 + h3 + 32
    f.append(arrow(220, y3 + h3, 160, y4, color=C_DIAL, sw=1.6))
    f.append(arrow(420, y3 + h3, 420, y4, color=C_DIAL, sw=1.6))
    f.append(arrow(620, y3 + h3, 680, y4, color=C_DIAL, sw=1.6))

    # Рівень 4: Діалекти вендорів
    dial_w, dial_h = 220, 68
    # ArduPilotMega
    f.append(rect(50, y4, dial_w, dial_h, fill="#fbeee6", stroke=C_DIAL, sw=1.8, rx=6))
    f.append(text(50 + dial_w / 2, y4 + 22, "ardupilotmega.xml", size=12, color=C_DIAL, bold=True))
    f.append(text(50 + dial_w / 2, y4 + 40, "Специфіка ArduPilot:", size=10.5, color=MUTED))
    f.append(text(50 + dial_w / 2, y4 + 56, "AHRS, EKF, MOUNT, RALLY", size=10.5, color=INK))

    # PX4
    f.append(rect(310, y4, dial_w, dial_h, fill="#fbeee6", stroke=C_DIAL, sw=1.8, rx=6))
    f.append(text(310 + dial_w / 2, y4 + 22, "development.xml / px4.xml", size=12, color=C_DIAL, bold=True))
    f.append(text(310 + dial_w / 2, y4 + 40, "Специфіка PX4 та розширення:", size=10.5, color=MUTED))
    f.append(text(310 + dial_w / 2, y4 + 56, "ACTUATOR_OUTPUT_STATUS тощо", size=10.5, color=INK))

    # Custom / ASLUAV
    f.append(rect(570, y4, dial_w, dial_h, fill="#fbeee6", stroke=C_DIAL, sw=1.8, rx=6))
    f.append(text(570 + dial_w / 2, y4 + 22, "asluav.xml / custom.xml", size=12, color=C_DIAL, bold=True))
    f.append(text(570 + dial_w / 2, y4 + 40, "Власні діалекти:", size=10.5, color=MUTED))
    f.append(text(570 + dial_w / 2, y4 + 56, "Користувацьке навантаження", size=10.5, color=INK))

    render(os.path.join(IMG, "xml-hierarchy.svg"), W, H, *f)


# ── 2. Простір ідентифікаторів повідомлень (Message ID space) ─────────────────
def fig_message_id_space():
    W, H = 840, 360
    f = [text(W / 2, 28, "Простір ідентифікаторів повідомлень: 8-бітний MAVLink v1 проти 24-бітного v2", size=15, bold=True)]

    # Блок 1: MAVLink v1 (0..255)
    y_v1 = 70
    f.append(rect(40, y_v1, 760, 95, fill="#f5eef8", stroke=C_V1, sw=1.8, rx=8))
    f.append(text(55, y_v1 + 24, "MAVLink v1 (1 байт MSG ID, діапазон 0 – 255)", size=12.5, color=C_V1, bold=True, anchor="start"))

    # Секції v1
    cells_v1 = [
        ("0 – 149 (150 ID)", 150, "#d2b4de", "Стандартні та спільні (minimal, standard, common)"),
        ("150 – 240 (91 ID)", 91, "#ebdef0", "Діалекти вендорів (ArduPilot, PX4 тощо)"),
        ("241 – 255 (15 ID)", 15, "#fadbd8", "Тести / налагодження"),
    ]
    x_cur = 55
    tot_w = 730
    for title, span_val, fill_c, desc in cells_v1:
        cw = tot_w * (span_val / 256.0)
        f.append(rect(x_cur, y_v1 + 35, cw, 48, fill=fill_c, stroke=C_V1, sw=1.2, rx=4))
        f.append(text(x_cur + cw / 2, y_v1 + 54, title, size=11, color=INK, bold=True))
        f.append(text(x_cur + cw / 2, y_v1 + 72, desc, size=9.5, color=MUTED))
        x_cur += cw

    # Блок 2: MAVLink v2 (0..16777215)
    y_v2 = 190
    f.append(rect(40, y_v2, 760, 140, fill="#ebf5fb", stroke=C_V2, sw=1.8, rx=8))
    f.append(text(55, y_v2 + 24, "MAVLink v2 (3 байти MSG ID, діапазон 0 – 16 777 215)", size=12.5, color=C_V2, bold=True, anchor="start"))

    # Секції v2
    cells_v2 = [
        ("0 – 255", 80, "#d4e6f1", "Спадщина v1", "Зворотна сумісність"),
        ("256 – 9 999", 150, "#aed6f1", "Нові спільні v2", "Розширення common.xml"),
        ("10 000 – 12 999", 140, "#f9e79f", "ArduPilot v2", "Діалектний простір APM"),
        ("13 000 – 13 999", 100, "#f5cba7", "PX4 v2", "Діалектний простір PX4"),
        ("14 000 – 16 777 215", 260, "#d5f5e3", "Користувацькі та майбутні", "Величезний резерв"),
    ]
    x_cur2 = 55
    for title, cw, fill_c, l1, l2 in cells_v2:
        f.append(rect(x_cur2, y_v2 + 35, cw, 80, fill=fill_c, stroke=C_V2, sw=1.2, rx=4))
        f.append(text(x_cur2 + cw / 2, y_v2 + 56, title, size=11, color=INK, bold=True))
        f.append(text(x_cur2 + cw / 2, y_v2 + 76, l1, size=10, color=INK))
        f.append(text(x_cur2 + cw / 2, y_v2 + 96, l2, size=9.5, color=MUTED, italic=True))
        x_cur2 += cw

    render(os.path.join(IMG, "message-id-space.svg"), W, H, *f)


# ── 3. Серіалізація: сортування полів за спаданням розміру типу ──────────────
def fig_wire_reordering():
    W, H = 840, 420
    f = [text(W / 2, 28, "Перевпорядкування полів: сортування за спаданням розміру для природного вирівнювання", size=15, bold=True)]

    # Ліва колонка: Порядок в XML
    xl, y0, wl = 40, 65, 340
    f.append(rect(xl, y0, wl, 315, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(xl + wl / 2, y0 + 26, "Оголошення в XML (логічний порядок)", size=13, color=INK, bold=True))

    xml_fields = [
        ("uint8_t target_system", "1 байт", "#fadbd8"),
        ("uint64_t time_usec", "8 байтів", "#d4efdf"),
        ("float param1", "4 байти", "#d6eaf8"),
        ("uint16_t command", "2 байти", "#fcf3cf"),
        ("uint32_t custom_mode", "4 байти", "#d6eaf8"),
        ("char text[10]", "10 × 1 Б (масив)", "#fadbd8"),
    ]
    yf = y0 + 44
    for name, sz, col in xml_fields:
        f.append(rect(xl + 16, yf, wl - 32, 36, fill=col, stroke=LINE, sw=1, rx=4))
        f.append(text(xl + 26, yf + 22, name, size=11.5, color=INK, bold=True, anchor="start"))
        f.append(text(xl + wl - 26, yf + 22, sz, size=10.5, color=MUTED, anchor="end"))
        yf += 43

    # Центральна стрілка перетворення
    f.append(arrow(395, y0 + 150, 435, y0 + 150, color=C_CORE, sw=2.5))
    f.append(text(415, y0 + 130, "mavgen", size=11, color=C_CORE, bold=True))
    f.append(text(415, y0 + 175, "сортування", size=10, color=MUTED))
    f.append(text(415, y0 + 190, "8 → 4 → 2 → 1", size=10, color=MUTED, italic=True))

    # Права колонка: Порядок у корисних даних на дроті
    xr, wr = 450, 350
    f.append(rect(xr, y0, wr, 315, fill="#f4fbf7", stroke=C_ALIGN, sw=1.8, rx=8))
    f.append(text(xr + wr / 2, y0 + 26, "Розкладка на дроті (дротовий порядок)", size=13, color=C_ALIGN, bold=True))

    wire_fields = [
        ("time_usec", "uint64_t", "зміщення 0", "8 Б", "#d4efdf", "вирівняно по 8 ✓"),
        ("param1", "float", "зміщення 8", "4 Б", "#d6eaf8", "вирівняно по 4 ✓"),
        ("custom_mode", "uint32_t", "зміщення 12", "4 Б", "#d6eaf8", "вирівняно по 4 ✓"),
        ("command", "uint16_t", "зміщення 16", "2 Б", "#fcf3cf", "вирівняно по 2 ✓"),
        ("target_system", "uint8_t", "зміщення 18", "1 Б", "#fadbd8", "вирівняно по 1 ✓"),
        ("text[10]", "char[10]", "зміщення 19..28", "10 Б", "#fadbd8", "вирівняно по 1 ✓"),
    ]
    yw = y0 + 44
    for name, typ, off, sz, col, align in wire_fields:
        f.append(rect(xr + 14, yw, wr - 28, 36, fill=col, stroke=C_ALIGN, sw=1, rx=4))
        f.append(text(xr + 22, yw + 22, f"{name} ({typ})", size=11, color=INK, bold=True, anchor="start"))
        f.append(text(xr + wr - 22, yw + 16, f"{off} ({sz})", size=10, color=INK, anchor="end"))
        f.append(text(xr + wr - 22, yw + 30, align, size=9, color=C_ALIGN, bold=True, anchor="end"))
        yw += 43

    # Підсумок унизу
    f.append(text(W / 2, H - 16, "Сума розмірів усіх попередніх полів завжди кратна розміру поточного поля — нуль байтів паддінгу!", size=11.5, color=INK, bold=True))

    render(os.path.join(IMG, "wire-reordering-alignment.svg"), W, H, *f)


# ── 4. Поля розширення MAVLink 2 та відкидання при v1-трансляції ──────────────
def fig_v2_extensions():
    W, H = 840, 370
    f = [text(W / 2, 28, "MAVLink 2: розширення extensions, Zero-Byte Truncation та трансляція у v1", size=15, bold=True)]

    # Стрічка корисного навантаження MAVLink 2
    y_p = 65
    f.append(text(40, y_p + 16, "Структура корисного навантаження (Payload) повідомлення MAVLink 2:", size=12, color=INK, bold=True, anchor="start"))

    # Базова частина (Base fields)
    bx, by, bw, bh = 40, y_p + 28, 420, 75
    f.append(rect(bx, by, bw, bh, fill="#d4efdf", stroke=C_ALIGN, sw=1.8, rx=6))
    f.append(text(bx + bw / 2, by + 24, "Базові поля (Base Fields, v1-сумісні)", size=12.5, color=C_ALIGN, bold=True))
    f.append(text(bx + bw / 2, by + 44, "Сортовані за розміром (8 → 4 → 2 → 1).", size=11, color=INK))
    f.append(text(bx + bw / 2, by + 62, "Беруть участь у розрахунку CRC_EXTRA!", size=10.5, color=C_WARN, bold=True))

    # Розширення (Extension fields)
    ex, ey, ew, eh = bx + bw + 10, by, 330, bh
    f.append(rect(ex, ey, ew, eh, fill="#fdebd0", stroke=C_WARN, sw=1.8, rx=6))
    f.append(text(ex + ew / 2, by + 24, "Поля розширення (<extensions/>)", size=12.5, color=C_WARN, bold=True))
    f.append(text(ex + ew / 2, by + 44, "Додаються після базових у порядку оголошення.", size=11, color=INK))
    f.append(text(ex + ew / 2, by + 62, "НЕ змінюють CRC_EXTRA! (сумісність)", size=10.5, color=C_WARN, italic=True))

    # Схема Zero-byte truncation
    y_z = by + bh + 30
    f.append(rect(40, y_z, 760, 68, fill="#ebf5fb", stroke=C_V2, sw=1.5, rx=6))
    f.append(text(55, y_z + 22, "Zero-Byte Truncation (економія байтів у MAVLink 2):", size=11.5, color=C_V2, bold=True, anchor="start"))
    f.append(text(55, y_z + 42, "Якщо наприкінці корисних даних стоять байти 0x00 (наприклад, нульові прапорці чи невикористані поля розширення),", size=11, color=INK, anchor="start"))
    f.append(text(55, y_z + 58, "вони обрізаються перед відправкою (LEN зменшується). Приймач автоматично заповнює відсутні байти нулями.", size=11, color=INK, anchor="start"))

    # Схема трансляції у v1
    y_t = y_z + 82
    f.append(rect(40, y_t, 760, 68, fill="#fdf2e9", stroke=C_DIAL, sw=1.5, rx=6))
    f.append(text(55, y_t + 22, "Правила шлюзування / трансляції з MAVLink 2 у MAVLink 1:", size=11.5, color=C_DIAL, bold=True, anchor="start"))
    f.append(text(55, y_t + 42, "• Поля розширення відкидаються (Payload обрізається до розміру базової частини).", size=11, color=INK, anchor="start"))
    f.append(text(55, y_t + 58, "• Якщо MSG ID > 255, повідомлення не транслюється у v1 (drop), бо v1 підтримує лише 8-бітні ID.", size=11, color=INK, anchor="start"))

    render(os.path.join(IMG, "v2-extensions-truncation.svg"), W, H, *f)


if __name__ == "__main__":
    fig_xml_hierarchy()
    fig_message_id_space()
    fig_wire_reordering()
    fig_v2_extensions()
    print("Всі 4 фігури згенеровано успішно.")