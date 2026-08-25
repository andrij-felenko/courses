# -*- coding: utf-8 -*-
"""Фігури до теми «Діалекти MAVLink».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

XMLC = "#2457d6"   # опис (XML) — синє/холодне
GENC = "#7d3c98"   # генератор/архітектура — фіолетове
OUTC = "#27ae60"   # вихідні діалекти/повідомлення — зелене
WARNC = "#c0392b"  # несумісність/помилки/IFLAG — червоне
CRCC = "#b9770e"   # контрольні суми/ідентифікатори — охра/золотаве
EXTC = "#0d9488"   # розширення extensions — бірюзове


# ── 1. Ієрархія та спадкування XML-схем MAVLink ──────────────────────────────
def fig_dialect_hierarchy():
    W, H = 940, 520
    f = [text(W / 2, 30, "Ієрархія та спадкування XML-схем MAVLink через тег <include>", size=15, bold=True)]

    # Рівень 1: minimal.xml (верхній лівий)
    min_box, mw, mh = textbox(210, 85, "minimal.xml (Базове ядро)\nHEARTBEAT (#0), PROTOCOL_VERSION (#300)\nMAV_AUTOPILOT, MAV_TYPE, MAV_STATE",
                              size=11.5, pad=12, stroke=XMLC, min_w=340)
    f.append(min_box)

    # Рівень 2: standard.xml
    std_box, sw, sh = textbox(210, 195, "standard.xml (Системні служби)\nSYSTEM_TIME (#2), PING (#4), AUTOPILOT_VERSION (#148)\nБазовий протокол параметрів та місій",
                              size=11.5, pad=12, stroke=XMLC, min_w=340)
    f.append(std_box)
    f.append(arrow(210, 160, 210, 120, color=XMLC, sw=1.8))
    f.append(text(275, 142, "<include> minimal.xml", size=10, color=MUTED, italic=True))

    # Рівень 3: common.xml
    com_box, cw, ch = textbox(210, 315, "common.xml (Загальний стандарт БПЛА)\nATTITUDE (#30), GLOBAL_POSITION_INT (#33), BATTERY_STATUS (#147)\nУніверсальні навігаційні команди MAV_CMD",
                              size=11.5, pad=14, stroke=GENC, min_w=340)
    f.append(com_box)
    f.append(arrow(210, 280, 210, 235, color=XMLC, sw=1.8))
    f.append(text(280, 260, "<include> standard.xml", size=10, color=MUTED, italic=True))

    # Рівень 4: Вендорні та користувацькі діалекти (праві блоки)
    rx = 710
    ard_box, aw, ah = textbox(rx, 100, "ardupilotmega.xml (Діалект ArduPilot)\nEKF_STATUS_REPORT (#193), RALLYPOINT (#175)\nКерування підвісами MOUNT_*, калібрування сенсорів",
                              size=11, pad=10, stroke=OUTC, min_w=360)
    f.append(ard_box)
    f.append(arrow(rx - 180, 100, 390, 295, color=GENC, sw=1.6))

    dev_box, dw, dh = textbox(rx, 225, "development.xml (PX4 / Робоча група)\nACTUATOR_OUTPUT_STATUS (#375), FIGURE_EIGHT (#360)\nЕкспериментальні протоколи перед включенням у common",
                              size=11, pad=10, stroke=OUTC, min_w=360)
    f.append(dev_box)
    f.append(arrow(rx - 180, 225, 390, 315, color=GENC, sw=1.6))

    cus_box, kw, kh = textbox(rx, 355, "my_payload.xml (Користувацький діалект)\nSPECTRAL_SURVEY_STATUS (#42000), LIDAR_SCAN (#42001)\nПриватні сенсори, роботизовані маніпулятори",
                              size=11, pad=10, stroke=EXTC, min_w=360)
    f.append(cus_box)
    f.append(arrow(rx - 180, 355, 390, 335, color=GENC, sw=1.6))

    # Агрегатор: all.xml (нижній блок)
    all_box, alw, alh = textbox(W / 2, 455, "all.xml — агрегатний опис для наземних станцій (QGroundControl, Mission Planner)\nВключає всі публічні діалекти вендорів для декодування будь-якого борту на одній лінії зв'язку",
                                size=11.5, pad=10, stroke=CRCC, min_w=760)
    f.append(all_box)

    f.append(text(W / 2, 500,
                  "Генератор mavgen розгортає ланцюг тегів <include> без дублювання та будує єдине дерево типів.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "dialect-hierarchy.svg"), W, H, *f)


# ── 2. Простір ідентифікаторів повідомлень (Message ID) ──────────────────────
def fig_message_id_allocation():
    W, H = 940, 480
    f = [text(W / 2, 30, "Простір ідентифікаторів Message ID: MAVLink v1 проти MAVLink 2", size=15, bold=True)]

    # Секція MAVLink v1 (8-бітний заголовок)
    f.append(text(80, 75, "MAVLink v1 (8 бітів у заголовку: 0 .. 255)", size=12.5, color=INK, anchor="start", bold=True))

    v1_y = 95
    v1_h = 55
    # 0..149 (58.8% ширини ~ 470px)
    f.append(fitbox(80, v1_y, 470, v1_h, "0 .. 149 (Ядро та Common)\nHEARTBEAT, ATTITUDE, GPS_RAW, COMMAND_LONG",
                    size=11, stroke=XMLC, fill="#edf2f7", bold=True))
    # 150..240 (35.7% ширини ~ 285px)
    f.append(fitbox(555, v1_y, 230, v1_h, "150 .. 240 (Вендори v1)\nArduPilot, MatrixPilot, AutoQuad",
                    size=11, stroke=OUTC, fill="#eafaf1", bold=True))
    # 241..255 (5.5% ширини ~ 75px)
    f.append(fitbox(790, v1_y, 70, v1_h, "241..255\nТести",
                    size=10, stroke=WARNC, fill="#fdf2e9", bold=True))

    f.append(text(W / 2, 175, "У v1 виникали непереборні колізії: вендори призначали однакові номери 150..240 різним повідомленням.",
                  size=11, color=WARNC, italic=True))

    # Секція MAVLink 2 (24-бітний заголовок)
    f.append(text(80, 220, "MAVLink 2 (24 біти у заголовку: 0 .. 16 777 215)", size=12.5, color=INK, anchor="start", bold=True))

    v2_y = 240
    v2_h = 60
    # 0..255 (Сумісність)
    f.append(fitbox(80, v2_y, 110, v2_h, "0 .. 255\nСумісність із v1",
                    size=10.5, stroke=XMLC, fill="#edf2f7", bold=True))
    # 256..9999 (Стандартні MAVLink 2)
    f.append(fitbox(195, v2_y, 195, v2_h, "256 .. 9 999\nРозширення standard / common\n(ODOMETRY, OBSTACLE_DISTANCE)",
                    size=10.5, stroke=GENC, fill="#f4ecf7", bold=True))
    # 10000..41999 (Офіційні простори вендорів)
    f.append(fitbox(395, v2_y, 185, v2_h, "10 000 .. 41 999\nОфіційні вендори\n(PX4, ArduPilot mega v2)",
                    size=10.5, stroke=OUTC, fill="#eafaf1", bold=True))
    # 42000..42999 (Приватні / Користувацькі)
    f.append(fitbox(585, v2_y, 145, v2_h, "42 000 .. 42 999\nПриватні діалекти\n(Custom Payloads)",
                    size=10.5, stroke=EXTC, fill="#e0f2f1", bold=True))
    # 43000..16777215 (Довгостроковий резерв)
    f.append(fitbox(735, v2_y, 125, v2_h, "43 000 .. 16.7M\nСтратегічний\nрезерв",
                    size=10.5, stroke=MUTED, fill="#f8f9fa", bold=True))

    # Виноски та правила
    f.append(text(W / 2, 335,
                  "Правило безпеки: приватні повідомлення завжди реєструють у 24-бітному просторі (наприклад, 42000..42999).",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 360,
                  "Це унеможливлює накладання з офіційними оновленнями common.xml та ardupilotmega.xml.",
                  size=11, color=MUTED, italic=True))

    # Компактна табличка внизу
    tb_y = 395
    f.append(rect(80, tb_y, 780, 55, fill="#fdfefe", stroke=MUTED, sw=1, rx=4))
    f.append(text(100, tb_y + 22, "Діапазон 0..255:", size=11, color=XMLC, anchor="start", bold=True))
    f.append(text(215, tb_y + 22, "пакується в 1 байт у кадрах v1 або в 3 байти в кадрах v2; спільний для обох версій.", size=10.5, color=INK, anchor="start"))
    f.append(text(100, tb_y + 44, "Діапазон 256+:", size=11, color=EXTC, anchor="start", bold=True))
    f.append(text(215, tb_y + 44, "дозволений ВИКЛЮЧНО в MAVLink 2 (маркер кадру 0xFD); у кадр v1 (0xFE) фізично не вміщується.", size=10.5, color=INK, anchor="start"))

    render(os.path.join(IMG, "message-id-allocation.svg"), W, H, *f)


# ── 3. Розкладка полів повідомлення з тегом <extensions> ─────────────────────
def fig_extension_fields_layout():
    W, H = 940, 520
    f = [text(W / 2, 30, "Розкладка полів повідомлення з тегом <extensions> у MAVLink 2", size=15, bold=True)]

    # Верхній блок: XML оголошення
    f.append(text(80, 65, "1. Оголошення в XML-схемі діалекту", size=12, color=INK, anchor="start", bold=True))
    xml_card = ("<message id=\"12000\" name=\"PAYLOAD_STATUS\">\n"
                "  <field type=\"uint32_t\" name=\"time_boot_ms\">Час роботи (мс)</field>\n"
                "  <field type=\"float\"    name=\"temperature\">Температура матриці</field>\n"
                "  <field type=\"uint8_t\"  name=\"sensor_status\">Стан сенсора</field>\n"
                "  <extensions/>\n"
                "  <field type=\"uint32_t\" name=\"exposure_us\">Експозиція кадру (мкс)</field>\n"
                "  <field type=\"uint16_t\" name=\"gain_raw\">Чутливість матриці</field>\n"
                "</message>")
    f.append(fitbox(80, 80, 480, 140, xml_card, size=10.5, stroke=XMLC, fill="#f8fafc"))

    # Пояснення справа
    info_x = 580
    f.append(text(info_x, 95, "Базова частина (до <extensions>):", size=11.5, color=CRCC, anchor="start", bold=True))
    f.append(text(info_x, 115, "• Поля сортуються за спаданням розміру (4B → 4B → 1B).", size=10.5, color=INK, anchor="start"))
    f.append(text(info_x, 133, "• Формують рядок для обчислення CRC_EXTRA.", size=10.5, color=INK, anchor="start"))

    f.append(text(info_x, 165, "Розширена частина (після <extensions>):", size=11.5, color=EXTC, anchor="start", bold=True))
    f.append(text(info_x, 185, "• Поля НЕ сортуються (додаються в порядку оголошення).", size=10.5, color=INK, anchor="start"))
    f.append(text(info_x, 203, "• НЕ входять до CRC_EXTRA (CRC лишається незмінним!).", size=10.5, color=INK, anchor="start"))

    # Середній блок: Розкладка в пам'яті корисних даних
    f.append(text(80, 245, "2. Розкладка байтів у корисних даних (Payload Buffer)", size=12, color=INK, anchor="start", bold=True))

    py = 265
    ph = 50
    # Базові поля (9 байтів: uint32 4B, float 4B, uint8 1B)
    f.append(fitbox(80, py, 150, ph, "time_boot_ms\nuint32_t (зсув 0..3)", size=10.5, stroke=CRCC, fill="#fef9e7", bold=True))
    f.append(fitbox(235, py, 150, ph, "temperature\nfloat (зсув 4..7)", size=10.5, stroke=CRCC, fill="#fef9e7", bold=True))
    f.append(fitbox(390, py, 90, ph, "sensor_status\nuint8_t (8)", size=10, stroke=CRCC, fill="#fef9e7", bold=True))

    # Розділювач extensions
    f.append(line(488, py - 8, 488, py + ph + 8, color=WARNC, sw=2.5, dash="4,3"))
    f.append(text(488, py - 14, "<extensions/>", size=10, color=WARNC, bold=True))

    # Розширені поля (6 байтів: uint32 4B, uint16 2B)
    f.append(fitbox(495, py, 160, ph, "exposure_us [ext]\nuint32_t (зсув 9..12)", size=10.5, stroke=EXTC, fill="#e0f2f1", bold=True))
    f.append(fitbox(660, py, 130, ph, "gain_raw [ext]\nuint16_t (13..14)", size=10.5, stroke=EXTC, fill="#e0f2f1", bold=True))

    # Фігурна дужка / пояснення базових і розширених
    f.append(text(285, py + ph + 20, "Базова довжина = 9 байтів (Захищена CRC_EXTRA)", size=10.5, color=CRCC, bold=True))
    f.append(text(645, py + ph + 20, "Розширена довжина = +6 байтів (Разом 15 байтів)", size=10.5, color=EXTC, bold=True))

    # Нижній блок: Механізм нульового обтинання (Zero-Truncation)
    f.append(text(80, 370, "3. Нульове обтинання в ефірі (Zero-Truncation) та зворотна сумісність", size=12, color=INK, anchor="start", bold=True))

    zy = 390
    zh = 70
    zt_box = ("Старий приймач (знає лише базові 9 байтів) ← отримує 15-байтовий пакет MAVLink 2:\n"
              "• Перевіряє CRC_EXTRA з насінням базової структури → CRC збігається!\n"
              "• Зчитує 9 відомих байтів; додаткові 6 байтів розширення безпечно ігнорує.\n"
              "Новий приймач ← отримує старий 9-байтовий або скорочений пакет (кінцеві нулі обтято):\n"
              "• Розгортає структуру на 15 байтів: поля exposure_us та gain_raw автоматично заповнюються нулями (0x00).")
    f.append(fitbox(80, zy, 780, zh, zt_box, size=10.5, stroke=GENC, fill="#f4f6f8"))

    f.append(text(W / 2, 495,
                  "Тег <extensions> дозволяє додавати нові поля до існуючих повідомлень без зміни діалекту у всій мережі.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "extension-fields-layout.svg"), W, H, *f)


# ── 4. Обробка прапорців MAVLink 2: IFLAG проти CFLAG ────────────────────────
def fig_flags_processing():
    W, H = 940, 480
    f = [text(W / 2, 30, "Обробка прапорців заголовка MAVLink 2: IFLAG проти CFLAG", size=15, bold=True)]

    # Вхідний кадр
    f.append(fitbox(60, 80, 200, 50, "Отримано кадр MAVLink 2\n(STX = 0xFD)", size=11.5, stroke=XMLC, fill="#edf2f7", bold=True))

    # Розгалуження на IFLAG та CFLAG
    f.append(arrow(260, 105, 330, 105, color=LINE, sw=1.8))

    # Блок перевірки IFLAG
    iflag_box, iw, ih = textbox(470, 105, "Перевірка incompat_flags (IFLAG)\nЧи встановлено біти, НЕВІДОМІ цьому приймачеві?\n(Наприклад, біт 0x01 = MAVLINK_IFLAG_SIGNED)",
                                size=11, pad=12, stroke=WARNC, min_w=300)
    f.append(iflag_box)

    # Гілка ТАК (невідомий IFLAG) -> Скинути кадр
    f.append(arrow(470, 145, 470, 220, color=WARNC, sw=2))
    f.append(text(485, 180, "ТАК", size=11, color=WARNC, bold=True))
    f.append(fitbox(370, 220, 200, 50, "ВІДХИЛИТИ КАДР (DROP)\nНесумісний бінарний формат", size=11, stroke=WARNC, fill="#fdecea", color=WARNC, bold=True))

    # Гілка НІ (IFLAG відомий) -> Перевірка CFLAG
    f.append(arrow(625, 105, 690, 105, color=FIELD, sw=1.8))
    f.append(text(655, 92, "НІ", size=11, color=FIELD, bold=True))

    # Блок перевірки CFLAG
    cflag_box, cw, ch = textbox(790, 105, "Аналіз compat_flags (CFLAG)\n(Додаткові необов'язкові опції,\nнаприклад 24-бітний розширений лінк)",
                                size=10.5, pad=10, stroke=GENC, min_w=200)
    f.append(cflag_box)

    # Перехід від CFLAG до декодування
    f.append(arrow(790, 160, 790, 220, color=FIELD, sw=1.8))
    f.append(text(805, 185, "Усі прапорці", size=10, color=MUTED, italic=True))

    # Блок успішного декодування
    ok_box = ("ПРИЙНЯТИ ТА ОБРОБИТИ ПАКЕТ\n"
              "• Невідомі біти CFLAG безпечно ігноруються (сумісність збережено);\n"
              "• Відомі IFLAG активують обов'язкову логіку (перевірку підпису HMAC-SHA256);\n"
              "• Перевіряється контрольна сума кадру з урахуванням CRC_EXTRA діалекту.")
    f.append(fitbox(640, 220, 260, 95, ok_box, size=9.5, stroke=FIELD, fill="#eafaf1"))

    # Порівняльна таблиця внизу
    ty = 345
    f.append(rect(60, ty, 820, 95, fill="#fdfefe", stroke=MUTED, sw=1, rx=6))
    f.append(text(80, ty + 24, "Прапорці несумісності (incompat_flags):", size=11, color=WARNC, anchor="start", bold=True))
    f.append(text(370, ty + 24, "Визначають зміни, без яких парсер НЕ МОЖЕ коректно прочитати байти на дроті.", size=10.5, color=INK, anchor="start"))
    f.append(text(370, ty + 42, "Якщо хоч один біт не підтримується — кадр негайно викидається з черги.", size=10.5, color=INK, anchor="start"))

    f.append(text(80, ty + 68, "Прапорці сумісності (compat_flags):", size=11, color=FIELD, anchor="start", bold=True))
    f.append(text(370, ty + 68, "Позначають необов'язкові системні ознаки (наприклад, пріоритет чи роутинг).", size=10.5, color=INK, anchor="start"))
    f.append(text(370, ty + 86, "Старий або сторонній парсер може сміливо ігнорувати їх і розбирати корисні дані.", size=10.5, color=INK, anchor="start"))

    f.append(text(W / 2, 465,
                  "Механізм IFLAG/CFLAG гарантує еволюцію протоколу без втрати зв'язку між різними версіями прошивок.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "flags-processing.svg"), W, H, *f)


if __name__ == "__main__":
    fig_dialect_hierarchy()
    fig_message_id_allocation()
    fig_extension_fields_layout()
    fig_flags_processing()
    print("All figures generated successfully.")
