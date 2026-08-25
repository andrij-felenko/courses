# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Частоти телеметрії та керування смугою пропускання».
Використовує бібліотеку svgkit з теки scripts/.
Генерує 4 фігури в теку ./img/.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: Опитування (Polling) проти Потокової передачі (Streaming) ──────
def fig_polling_vs_streaming():
    W, H = 940, 440
    P = [
        text(W / 2, 28, "Опитування (Polling) проти Потокової передачі (Streaming)", size=17, bold=True),
        text(W / 2, 48, "Чому запит-відповідь паралізує вузький радіолінк, а періодична підписка зберігає смугу", size=12, color=MUTED)
    ]

    # Ліва колонка: Опитування (Polling)
    col1_x, col1_w = 40, 410
    P.append(rect(col1_x, 65, col1_w, 355, fill="#fdfefe", stroke=POS, sw=1.5, rx=8))
    P.append(text(col1_x + col1_w / 2, 90, "Індивідуальне опитування (Polling)", size=14, color=POS, bold=True))

    # Станція та БПЛА зліва
    P.append(fitbox(col1_x + 20, 115, 100, 30, "GCS (Земля)", size=11, fill="#eef2f7", stroke=INK, bold=True))
    P.append(fitbox(col1_x + col1_w - 120, 115, 100, 30, "БПЛА (Борт)", size=11, fill="#eef2f7", stroke=INK, bold=True))

    # Хронологія опитування
    y_start = 165
    # Запит 1
    P.append(arrow(col1_x + 70, y_start, col1_x + col1_w - 70, y_start + 25, color=POS))
    P.append(text(col1_x + col1_w / 2, y_start + 8, "1. Запит GET(ATTITUDE) [14 B]", size=10.5, color=POS))

    # Відповідь 1
    P.append(arrow(col1_x + col1_w - 70, y_start + 45, col1_x + 70, y_start + 70, color=NEG))
    P.append(text(col1_x + col1_w / 2, y_start + 53, "2. Відповідь ATTITUDE [40 B]", size=10.5, color=NEG))

    # Пауза RTT
    P.append(line(col1_x + 40, y_start + 25, col1_x + 40, y_start + 70, color=MUTED, sw=1, dash="3,3"))
    P.append(text(col1_x + 25, y_start + 50, "RTT", size=9.5, color=MUTED, anchor="end"))

    # Запит 2
    P.append(arrow(col1_x + 70, y_start + 85, col1_x + col1_w - 70, y_start + 110, color=POS))
    P.append(text(col1_x + col1_w / 2, y_start + 93, "3. Запит GET(POSITION) [14 B]", size=10.5, color=POS))

    # Відповідь 2
    P.append(arrow(col1_x + col1_w - 70, y_start + 130, col1_x + 70, y_start + 155, color=NEG))
    P.append(text(col1_x + col1_w / 2, y_start + 138, "4. Відповідь POSITION [40 B]", size=10.5, color=NEG))

    P.append(fitbox(col1_x + 20, 345, col1_w - 40, 60,
                    "Марнування каналу: подвійний трафік у радіоефірі,\n"
                    "напівдуплексні затримки TDD перемикання (30-80 мс RTT),\n"
                    "максимальна частота обмежена кількома герцами!",
                    size=10.5, fill="#fdecea", stroke=POS, color=POS))

    # Права колонка: Потоки (Streaming)
    col2_x, col2_w = 490, 410
    P.append(rect(col2_x, 65, col2_w, 355, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=8))
    P.append(text(col2_x + col2_w / 2, 90, "Потокова підписка (Streaming)", size=14, color=FIELD, bold=True))

    # Станція та БПЛА справа
    P.append(fitbox(col2_x + 20, 115, 100, 30, "GCS (Земля)", size=11, fill="#eef2f7", stroke=INK, bold=True))
    P.append(fitbox(col2_x + col2_w - 120, 115, 100, 30, "БПЛА (Борт)", size=11, fill="#eef2f7", stroke=INK, bold=True))

    # Одноразова конфігурація
    P.append(arrow(col2_x + 70, y_start, col2_x + col2_w - 70, y_start + 20, color=MUTED))
    P.append(text(col2_x + col2_w / 2, y_start + 6, "1. Одноразове налаштування частоти", size=10.5, color=MUTED))

    # Безперервний потік
    P.append(arrow(col2_x + col2_w - 70, y_start + 40, col2_x + 70, y_start + 55, color=FIELD))
    P.append(text(col2_x + col2_w / 2, y_start + 44, "ATTITUDE (t = 0 мс)", size=10, color=FIELD))

    P.append(arrow(col2_x + col2_w - 70, y_start + 65, col2_x + 70, y_start + 80, color=FIELD))
    P.append(text(col2_x + col2_w / 2, y_start + 69, "ATTITUDE (t = 20 мс)", size=10, color=FIELD))

    P.append(arrow(col2_x + col2_w - 70, y_start + 90, col2_x + 70, y_start + 105, color=NEG))
    P.append(text(col2_x + col2_w / 2, y_start + 94, "GLOBAL_POSITION (t = 50 мс)", size=10, color=NEG))

    P.append(arrow(col2_x + col2_w - 70, y_start + 115, col2_x + 70, y_start + 130, color=FIELD))
    P.append(text(col2_x + col2_w / 2, y_start + 119, "ATTITUDE (t = 40 мс)", size=10, color=FIELD))

    P.append(arrow(col2_x + col2_w - 70, y_start + 140, col2_x + 70, y_start + 155, color=MUTED))
    P.append(text(col2_x + col2_w / 2, y_start + 144, "HEARTBEAT (t = 1000 мс)", size=10, color=MUTED))

    P.append(fitbox(col2_x + 20, 345, col2_w - 40, 60,
                    "Ефективна утилізація: контролер шле дані сам за таймером,\n"
                    "вгору йдуть лише короткі команди керування,\n"
                    "частота оновлення телеметрії досягає 50 Гц!",
                    size=10.5, fill="#eafaf1", stroke=FIELD, color=FIELD))

    render("img/polling-vs-streaming.svg", W, H, *P)


# ── Фігура 2: Групи MAV_DATA_STREAM проти MAV_CMD_SET_MESSAGE_INTERVAL ───────
def fig_stream_groups_vs_interval():
    W, H = 940, 430
    P = [
        text(W / 2, 28, "Еволюція керування потоками: Групи проти Індивідуальних інтервалів", size=17, bold=True),
        text(W / 2, 48, "Старий монолітний REQUEST_DATA_STREAM (#66) проти мікросервісу SET_MESSAGE_INTERVAL (#511)", size=12, color=MUTED)
    ]

    # Зліва: Старий метод (Групи)
    x1, w1 = 40, 410
    P.append(rect(x1, 65, w1, 345, fill="#fdfefe", stroke=MUTED, sw=1.5, rx=8))
    P.append(text(x1 + w1 / 2, 90, "Старий метод: REQUEST_DATA_STREAM", size=13.5, bold=True))

    # Схема групи EXTRA1
    P.append(rect(x1 + 25, 110, w1 - 50, 140, fill="#f4f6f8", stroke=MUTED, sw=1.2, rx=6))
    P.append(text(x1 + w1 / 2, 128, "Група MAV_DATA_STREAM_EXTRA1 (10 Гц)", size=11, bold=True))

    P.append(fitbox(x1 + 35, 140, w1 - 70, 22, "ATTITUDE (#30) — потрібен на 30 Гц", size=10, fill="#fdecea", stroke=POS))
    P.append(fitbox(x1 + 35, 166, w1 - 70, 22, "SIMSTATE (#164) — вистачило б 1 Гц", size=10, fill="#ffffff", stroke=MUTED))
    P.append(fitbox(x1 + 35, 192, w1 - 70, 22, "AHRS (#163) — важкі сирі матриці", size=10, fill="#ffffff", stroke=MUTED))
    P.append(fitbox(x1 + 35, 218, w1 - 70, 22, "HWSTATUS (#165) — напруга плати", size=10, fill="#ffffff", stroke=MUTED))

    P.append(fitbox(x1 + 20, 265, w1 - 40, 130,
                    "Вади монолітного підходу:\n"
                    "• Неможливо змінити частоту лише одного повідомлення\n"
                    "• Неможливо вимкнути непотрібне повідомлення з пачки\n"
                    "• Розбіжність прошивок: набір повідомлень у ArduPilot і PX4 різний\n"
                    "• Сміттєвий трафік забиває вузькі канали зв'язку",
                    size=10.5, fill="#fdecea", stroke=POS, color=POS))

    # Справа: Сучасний метод (Message Interval Protocol)
    x2, w2 = 490, 410
    P.append(rect(x2, 65, w2, 345, fill="#fdfefe", stroke=FIELD, sw=1.5, rx=8))
    P.append(text(x2 + w2 / 2, 90, "Сучасний стандарт: SET_MESSAGE_INTERVAL", size=13.5, color=FIELD, bold=True))

    # Індивідуальні налаштування
    y_item = 110
    items = [
        ("ATTITUDE (#30)", "20 000 мкс (50 Гц)", "#eafaf1", FIELD),
        ("GLOBAL_POSITION_INT (#33)", "100 000 мкс (10 Гц)", "#eafaf1", FIELD),
        ("VFR_HUD (#74)", "100 000 мкс (10 Гц)", "#eafaf1", FIELD),
        ("SYS_STATUS (#1)", "1 000 000 мкс (1 Гц)", "#eef2f7", INK),
        ("RAW_IMU (#27)", "-1 (Вимкнено / 0 Гц)", "#fdecea", POS),
    ]

    for name, rate, fill_c, strk_c in items:
        P.append(rect(x2 + 25, y_item, w2 - 50, 26, fill=fill_c, stroke=strk_c, sw=1.2, rx=4))
        P.append(text(x2 + 40, y_item + 17, name, size=10, bold=True, anchor="start"))
        P.append(text(x2 + w2 - 40, y_item + 17, rate, size=10, color=strk_c, bold=True, anchor="end"))
        y_item += 30

    P.append(fitbox(x2 + 20, 265, w2 - 40, 130,
                    "Переваги точкового керування:\n"
                    "• Точний інтервал у мікросекундах для кожного Message ID\n"
                    "• Повне вимкнення непотрібного трафіку значенням -1\n"
                    "• Єдиний протокол взаємодії незалежно від типу автопілота\n"
                    "• Оптимальне підлаштування під швидкість модема (SiK / ELRS / IP)",
                    size=10.5, fill="#eafaf1", stroke=FIELD, color=FIELD))

    render("img/stream-groups-vs-interval.svg", W, H, *P)


# ── Фігура 3: Розподіл смуги пропускання телеметрії (Bandwidth Budget) ────────
def fig_bandwidth_pie_budget():
    W, H = 940, 440
    P = [
        text(W / 2, 28, "Бюджет смуги пропускання телеметрії (SiK Radio 57600 бод)", size=17, bold=True),
        text(W / 2, 48, "Розподіл корисного навантаження, службових заголовків MAVLink v2 та резерву надійності", size=12, color=MUTED)
    ]

    # Стовпчикова діаграма утилізації каналу
    bar_x, bar_y = 50, 85
    bar_w, bar_h = 840, 65

    P.append(rect(bar_x, bar_y, bar_w, bar_h, fill="#ffffff", stroke=INK, sw=1.8, rx=6))

    # Секції смуги (Загальна ємність UART 57600 бод = 5760 Б/с)
    # 1. ATTITUDE 50Hz = 50 * 42 = 2100 B/s (~36.5%)
    w_att = int(bar_w * 0.365)
    P.append(rect(bar_x, bar_y, w_att, bar_h, fill="#2457d6", stroke=INK, sw=1.2, rx=0))
    P.append(text(bar_x + w_att / 2, bar_y + 26, "ATTITUDE (50 Гц)", size=11, color="#ffffff", bold=True))
    P.append(text(bar_x + w_att / 2, bar_y + 46, "2100 Б/с (36.5%)", size=10, color="#ffffff"))

    # 2. POSITION 10Hz = 10 * 42 = 420 B/s (~7.3%)
    x_pos = bar_x + w_att
    w_pos = int(bar_w * 0.073)
    P.append(rect(x_pos, bar_y, w_pos, bar_h, fill="#27ae60", stroke=INK, sw=1.2, rx=0))
    P.append(text(x_pos + w_pos / 2, bar_y + 26, "POS", size=10, color="#ffffff", bold=True))
    P.append(text(x_pos + w_pos / 2, bar_y + 46, "420 Б/с", size=9.5, color="#ffffff"))

    # 3. VFR_HUD 10Hz = 10 * 34 = 340 B/s (~5.9%)
    x_hud = x_pos + w_pos
    w_hud = int(bar_w * 0.059)
    P.append(rect(x_hud, bar_y, w_hud, bar_h, fill="#d35400", stroke=INK, sw=1.2, rx=0))
    P.append(text(x_hud + w_hud / 2, bar_y + 26, "HUD", size=10, color="#ffffff", bold=True))
    P.append(text(x_hud + w_hud / 2, bar_y + 46, "340 Б/с", size=9.5, color="#ffffff"))

    # 4. Стан системи (SYS_STATUS + BATTERY + HEARTBEAT) ~340 B/s (~5.9%)
    x_stat = x_hud + w_hud
    w_stat = int(bar_w * 0.059)
    P.append(rect(x_stat, bar_y, w_stat, bar_h, fill="#8e44ad", stroke=INK, sw=1.2, rx=0))
    P.append(text(x_stat + w_stat / 2, bar_y + 26, "STAT", size=10, color="#ffffff", bold=True))
    P.append(text(x_stat + w_stat / 2, bar_y + 46, "340 Б/с", size=9.5, color="#ffffff"))

    # 5. Резерв під команди, параметри та повторні спроби модема (~44.4%)
    x_res = x_stat + w_stat
    w_res = bar_w - (w_att + w_pos + w_hud + w_stat)
    P.append(rect(x_res, bar_y, w_res, bar_h, fill="#f4f6f8", stroke=FIELD, sw=1.5, rx=0))
    P.append(text(x_res + w_res / 2, bar_y + 26, "РЕЗЕРВ НАДІЙНОСТІ (44.4%)", size=12, color=FIELD, bold=True))
    P.append(text(x_res + w_res / 2, bar_y + 46, "Команди GCS, параметри, місії, FEC радіоефіру", size=10, color=MUTED))

    # Детальні пояснення знизу у трьох блоках
    bw = 270
    # Блок 1
    P.append(rect(50, 175, bw, 235, fill="#fdfefe", stroke=INK, sw=1.2, rx=6))
    P.append(text(50 + bw / 2, 200, "Фізичний ліміт UART", size=12.5, bold=True))
    P.append(fitbox(65, 215, bw - 30, 180,
                    "57600 бод = 5760 Байт/с\n"
                    "(1 старт + 8 біт + 1 стоп = 10 біт/Б)\n\n"
                    "Накладні витрати MAVLink v2:\n"
                    "• 14 байт заголовка і CRC на кожен пакет\n"
                    "• ATTITUDE: 28 Б даних + 14 Б заголовок\n"
                    "  = 42 Байти/пакет\n"
                    "• Заголовки забирають 30-40% смуги!",
                    size=10, fill="#f4f6f8", stroke=MUTED))

    # Блок 2
    P.append(rect(335, 175, bw, 235, fill="#fdfefe", stroke=POS, sw=1.2, rx=6))
    P.append(text(335 + bw / 2, 200, "Золоте правило 60%", size=12.5, color=POS, bold=True))
    P.append(fitbox(350, 215, bw - 30, 180,
                    "Утилізація понад 65% — небезпечна:\n\n"
                    "• Радіоефір напівдуплексний (TDD)\n"
                    "• Стрибки частот FHSS втрачають слоти\n"
                    "• Завади викликають повтори кадрів модема\n"
                    "• Буфер модема переповнюється, ламаючи\n"
                    "  доставку критичних команд керування!",
                    size=10, fill="#fdecea", stroke=POS, color=POS))

    # Блок 3
    P.append(rect(620, 175, bw, 235, fill="#fdfefe", stroke=FIELD, sw=1.2, rx=6))
    P.append(text(620 + bw / 2, 200, "Особливості ELRS / CRSF", size=12.5, color=FIELD, bold=True))
    P.append(fitbox(635, 215, bw - 30, 180,
                    "Вузькі канали керування:\n\n"
                    "• Telemetry Ratio 1:64 @ 250 Гц =\n"
                    "  лише ~3.9 телеметрійних пакетів/с\n"
                    "• Смуга телеметрії: 100-300 Байт/с!\n"
                    "• Потрібне вимкнення Attitude/IMU\n"
                    "  і передача лише Position/Status на 1 Гц",
                    size=10, fill="#eafaf1", stroke=FIELD, color=FIELD))

    render("img/bandwidth-pie-budget.svg", W, H, *P)


# ── Фігура 4: Динамічний адаптивний троттлінг ─────────────────────────────────
def fig_dynamic_throttling():
    W, H = 940, 440
    P = [
        text(W / 2, 28, "Динамічний адаптивний троттлінг телеметрії", size=17, bold=True),
        text(W / 2, 48, "Автоматичне ступінчасте регулювання частот при деградації радіосигналу та заповненні буфера", size=12, color=MUTED)
    ]

    # Три рівні станів
    card_w, card_h = 240, 245
    y_card = 80

    # 1. Рівень: Нормальний (Зелений)
    x_c1 = 40
    P.append(rect(x_c1, y_card, card_w, card_h, fill="#eafaf1", stroke=FIELD, sw=1.8, rx=8))
    P.append(text(x_c1 + card_w / 2, y_card + 26, "РЕЖИМ: ЗВИЧАЙНИЙ", size=12.5, color=FIELD, bold=True))
    P.append(text(x_c1 + card_w / 2, y_card + 46, "RSSI > -75 дБм | txbuf < 40%", size=10, color=MUTED))

    P.append(fitbox(x_c1 + 15, y_card + 60, card_w - 30, 170,
                    "Повні номінальні частоти:\n"
                    "• ATTITUDE: 50 Гц (плавний горизонт)\n"
                    "• POSITION: 10 Гц (траєкторія)\n"
                    "• VFR_HUD: 10 Гц (швидкість)\n"
                    "• SYS_STATUS: 2 Гц\n"
                    "• HEARTBEAT: 1 Гц\n"
                    "• Навантаження: ~3200 Б/с",
                    size=10, fill="#ffffff", stroke=FIELD))

    # Переходи між 1 та 2 (x: 280 .. 350)
    gap1_x1, gap1_x2 = x_c1 + card_w, 350
    gap1_cx = (gap1_x1 + gap1_x2) / 2
    P.append(arrow(gap1_x1, y_card + 85, gap1_x2, y_card + 85, color=POS, sw=1.8))
    P.append(text(gap1_cx, y_card + 75, "txbuf > 60%", size=9.5, color=POS, bold=True))

    P.append(arrow(gap1_x2, y_card + 145, gap1_x1, y_card + 145, color=FIELD, sw=1.8))
    P.append(text(gap1_cx, y_card + 160, "txbuf < 30%", size=9.5, color=FIELD, bold=True))

    # 2. Рівень: Помірний затор (Жовтий)
    x_c2 = 350
    P.append(rect(x_c2, y_card, card_w, card_h, fill="#fefde8", stroke="#f39c12", sw=1.8, rx=8))
    P.append(text(x_c2 + card_w / 2, y_card + 26, "РЕЖИМ: ДЕГРАДАЦІЯ", size=12.5, color="#d35400", bold=True))
    P.append(text(x_c2 + card_w / 2, y_card + 46, "RSSI -75..-90 дБм | txbuf 60-85%", size=10, color=MUTED))

    P.append(fitbox(x_c2 + 15, y_card + 60, card_w - 30, 170,
                    "Зниження навантаження (-65%):\n"
                    "• ATTITUDE: 15 Гц\n"
                    "• POSITION: 4 Гц\n"
                    "• VFR_HUD: 2 Гц\n"
                    "• SYS_STATUS: 1 Гц\n"
                    "• HEARTBEAT: 1 Гц\n"
                    "• Навантаження: ~1100 Б/с",
                    size=10, fill="#ffffff", stroke="#f39c12"))

    # Переходи між 2 та 3 (x: 590 .. 660)
    gap2_x1, gap2_x2 = x_c2 + card_w, 660
    gap2_cx = (gap2_x1 + gap2_x2) / 2
    P.append(arrow(gap2_x1, y_card + 85, gap2_x2, y_card + 85, color=POS, sw=1.8))
    P.append(text(gap2_cx, y_card + 75, "txbuf > 85%", size=9.5, color=POS, bold=True))

    P.append(arrow(gap2_x2, y_card + 145, gap2_x1, y_card + 145, color=FIELD, sw=1.8))
    P.append(text(gap2_cx, y_card + 160, "txbuf < 50%", size=9.5, color=FIELD, bold=True))

    # 3. Рівень: Критичний затор (Червоний)
    x_c3 = 660
    P.append(rect(x_c3, y_card, card_w, card_h, fill="#fdecea", stroke=POS, sw=1.8, rx=8))
    P.append(text(x_c3 + card_w / 2, y_card + 26, "РЕЖИМ: КРИТИЧНИЙ", size=12.5, color=POS, bold=True))
    P.append(text(x_c3 + card_w / 2, y_card + 46, "RSSI < -90 дБм | txbuf > 85%", size=10, color=MUTED))

    P.append(fitbox(x_c3 + 15, y_card + 60, card_w - 30, 170,
                    "Аварійне виживання каналу:\n"
                    "• ATTITUDE: 5 Гц\n"
                    "• POSITION: 1 Гц\n"
                    "• VFR_HUD: 0 Гц (Вимкнено)\n"
                    "• SYS_STATUS: 1 Гц\n"
                    "• HEARTBEAT: 1 Гц (Священний)\n"
                    "• Навантаження: ~350 Б/с",
                    size=10, fill="#ffffff", stroke=POS))

    # Нижній висновок
    P.append(fitbox(40, 350, 860, 60,
                    "Ключовий принцип: Запобігання переповненню буфера радіомодема рятує доставку команд RTL/LAND,\n"
                    "а часовий гістерезис (5 секунд стабільності) виключає коливання частот на межі зон зв'язку.",
                    size=11, fill="#f4f6f8", stroke=INK, bold=True))

    render("img/dynamic-throttling.svg", W, H, *P)


if __name__ == "__main__":
    fig_polling_vs_streaming()
    fig_stream_groups_vs_interval()
    fig_bandwidth_pie_budget()
    fig_dynamic_throttling()
    print("Всі 4 фігури успішно згенеровано у img/.")
