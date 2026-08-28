# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

COL_MARKERS = (
    '<defs>'
    '<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="%s"/></marker>'
    '</defs>' % (NEG, FIELD, POS)
)

def carrow(x1, y1, x2, y2, color, mid, sw=2.0):
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" '
            'stroke-width="%.1f" marker-end="url(#arr%s)" stroke-linecap="round"/>'
            % (x1, y1, x2, y2, color, sw, mid))

# ── 1. failure-modes: Чотири класи збоїв бортового комп'ютера ────────────────
def fig_failure_modes():
    W, H = 1000, 560
    p = [COL_MARKERS]
    p.append(text(W / 2, 40, "Чотири класи збоїв SBC та їхня трансформація в симптоми на польотному контролері",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 62, "різні фізичні та програмні першопричини зводяться до двох сигналів автопілота: втрата потоку уставок і втрата серцебиття",
                  size=11.5, color=MUTED, italic=True))

    cols = [
        (40, 215, "ПРОГРАМНИЙ КРАХ", ["• Падіння ROS 2 / MAVSDK", "• SIGSEGV / Panic у С++", "• OOM Killer через витік RAM", "• Стек задач завершено"],
         POS, "#fdecea", "Сокет закрито / потік зупинено"),
        (280, 215, "ЗАВИСАННЯ ОС / CPU", ["• Thermal Throttling до 200 МГц", "• 100% CPU starvation", "• Kernel deadlock / RCU stall", "• I/O залочка на Flash/eMMC"],
         "#d98a00", "#fff5e6", "Джиттер > 1 с / фриз петлі"),
        (520, 215, "ЗБІЙ ЛІНІЇ ЗВ'ЯЗКУ", ["• Шуми на UART від моторів", "• RX/TX FIFO buffer overrun", "• Збій USB FTDI драйвера", "• Зрив байтової синхронізації"],
         NEG, "#eef2ff", "CRC помилки / биті кадри"),
        (760, 200, "ПРОСАДКА ЖИВЛЕННЯ", ["• Просідання 5V нижче 4.63V", "• Піковий струм серво/моторів", "• Перегрів імпульсного BEC", "• Brownout Reset процесора"],
         POS, "#fdecea", "Миттєвий рестарт (20-40 с)"),
    ]

    y_top = 95
    h_box = 210

    for x, w, title_txt, items, stroke_col, fill_col, symptom in cols:
        p.append(rect(x, y_top, w, h_box, fill=fill_col, stroke=stroke_col, sw=1.8, rx=10))
        p.append(text(x + w / 2, y_top + 26, title_txt, size=11.5, color=stroke_col, bold=True))
        p.append(line(x + 15, y_top + 38, x + w - 15, y_top + 38, color=stroke_col, sw=1.0, dash="4 3"))
        iy = y_top + 60
        for item in items:
            p.append(text(x + 14, iy, item, size=10.5, color=INK, anchor="start"))
            iy += 22
        p.append(rect(x + 10, y_top + h_box - 42, w - 20, 32, fill=BG, stroke=stroke_col, sw=1.2, rx=6))
        p.append(text(x + w / 2, y_top + h_box - 22, symptom, size=10, color=stroke_col, bold=True))
        p.append(carrow(x + w / 2, y_top + h_box, x + w / 2, 360, stroke_col, "R" if stroke_col == POS else ("B" if stroke_col == NEG else "G"), sw=2.0))

    # Нижній рівень: FMU / FCU Реєстратор симптомів
    p.append(rect(60, 365, 880, 140, fill="#f4f6f8", stroke=INK, sw=2.0, rx=12))
    p.append(text(W / 2, 395, "РЕАКЦІЯ ПОЛЬОТНОГО КОНТРОЛЕРА (FCU / FMU)", size=13.5, color=INK, bold=True))

    p.append(rect(90, 415, 380, 72, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    p.append(text(280, 438, "ТАЙМАУТ ПОТОКУ УСТАВОК (250-500 мс)", size=11, color=POS, bold=True))
    p.append(text(280, 458, "SET_POSITION_TARGET_LOCAL_NED перестали йти", size=10, color=MUTED))
    p.append(text(280, 474, "→ Зрив режиму Offboard / перехід у Hold", size=10.5, color=POS, bold=True))

    p.append(rect(530, 415, 380, 72, fill="#ffffff", stroke=NEG, sw=1.5, rx=8))
    p.append(text(720, 438, "ВТРАТА HEARTBEAT (1.0-3.0 с)", size=11, color=NEG, bold=True))
    p.append(text(720, 458, "MAVLink статус відсутній / відмова шини", size=10, color=MUTED))
    p.append(text(720, 474, "→ Запуск аварійного повернення (RTL / Failsafe)", size=10.5, color=NEG, bold=True))

    p.append(text(W / 2, 535,
                  "FCU не знає причини збою: для нього відсутність пакета через Kernel Panic або через брудний UART виглядає однаково.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "failure-modes.svg"), W, H, *p,
           title="Класифікація збоїв бортового комп'ютера та їх прояв на автопілоті")

# ── 2. heartbeat-timeout-timeline: Часова діаграма спрацювання відкату ────────
def fig_heartbeat_timeout_timeline():
    W, H = 960, 520
    p = [COL_MARKERS]
    p.append(text(W / 2, 38, "Хронологія таймаутів: відмова SBC → зрив Offboard → реакція автопілота",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 60, "два незалежні лічильники часу: швидкий таймаут уставки (контур руху) і повільний таймаут зв'язку (безпека)",
                  size=11.5, color=MUTED, italic=True))

    # Часова шкала
    t_start, t_end = 80, 880
    ty = 230
    p.append(line(t_start, ty, t_end + 20, ty, color=INK, sw=2.5))
    p.append(arrow(t_end + 15, ty, t_end + 30, ty, color=INK, sw=2.5))
    p.append(text(t_end + 35, ty + 5, "t (час)", size=11.5, color=INK, anchor="start", italic=True))

    # Подія відмови (t = 0)
    tx_fail = 260
    p.append(line(tx_fail, 90, tx_fail, 430, color=POS, sw=1.8, dash="5 4"))
    p.append(rect(tx_fail - 75, 95, 150, 44, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(tx_fail, 114, "МОМЕНТ ЗБОЮ SBC", size=11, color=POS, bold=True))
    p.append(text(tx_fail, 130, "t = 0 (паніка / зависання)", size=9.5, color=POS))

    # Фаза 1: Нормальна робота (до t_fail)
    p.append(rect(80, 160, tx_fail - 85, 52, fill="#eafaef", stroke=FIELD, sw=1.5, rx=8))
    p.append(text((80 + tx_fail) / 2, 182, "РЕЖИМ OFFBOARD", size=11.5, color=FIELD, bold=True))
    p.append(text((80 + tx_fail) / 2, 199, "Потік уставок 20-50 Гц + Heartbeat 1 Гц", size=9.5, color=INK))

    # Позначка 1: Втрата уставки (t = 250..500 ms)
    tx_sp = 450
    p.append(line(tx_sp, 150, tx_sp, 430, color="#d98a00", sw=1.6, dash="4 3"))
    p.append(circle(tx_sp, ty, 6, fill="#d98a00", stroke=INK, sw=1.2))
    p.append(text(tx_sp, ty + 24, "t = 250–500 мс", size=11, color="#d98a00", bold=True))
    p.append(rect(tx_sp - 85, 270, 170, 68, fill="#fff5e6", stroke="#d98a00", sw=1.5, rx=8))
    p.append(text(tx_sp, 290, "Offboard Loss Failsafe", size=10.5, color="#d98a00", bold=True))
    p.append(text(tx_sp, 308, "Таймаут уставки вичерпано", size=9.5, color=INK))
    p.append(text(tx_sp, 324, "FCU → HOLD / LOITER", size=10.5, color="#d98a00", bold=True))

    # Фаза 2: Зависання в точці (Hold / Loiter)
    p.append(rect(tx_sp + 5, 160, 250, 52, fill="#fff5e6", stroke="#d98a00", sw=1.5, rx=8))
    p.append(text(tx_sp + 130, 182, "УТРИМАННЯ ПОЗИЦІЇ (HOLD)", size=11, color="#d98a00", bold=True))
    p.append(text(tx_sp + 130, 199, "Дрон зупиняє рух, зависає по GNSS/IMU", size=9.5, color=INK))

    # Позначка 2: Втрата Heartbeat (t = 1.0..3.0 s)
    tx_hb = 710
    p.append(line(tx_hb, 150, tx_hb, 430, color=POS, sw=1.6, dash="4 3"))
    p.append(circle(tx_hb, ty, 6, fill=POS, stroke=INK, sw=1.2))
    p.append(text(tx_hb, ty + 24, "t = 1.5–3.0 с", size=11, color=POS, bold=True))
    p.append(rect(tx_hb - 85, 270, 170, 68, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    p.append(text(tx_hb, 290, "Companion Lost Failsafe", size=10.5, color=POS, bold=True))
    p.append(text(tx_hb, 308, "HEARTBEAT не отримано", size=9.5, color=INK))
    p.append(text(tx_hb, 324, "FCU → RTL / LAND", size=10.5, color=POS, bold=True))

    # Фаза 3: Повернення додому
    p.append(rect(tx_hb + 5, 160, t_end - tx_hb + 10, 52, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    p.append(text((tx_hb + t_end) / 2, 182, "АВТОНОМНЕ ПОВЕРНЕННЯ (RTL)", size=10.5, color=POS, bold=True))
    p.append(text((tx_hb + t_end) / 2, 199, "Набір висоти безпеки й політ на старт", size=9, color=INK))

    # Нижня часова стрілка інтервалу
    p.append(line(tx_fail, 410, tx_sp, 410, color="#d98a00", sw=1.5))
    p.append(text((tx_fail + tx_sp) / 2, 400, "250-500 мс", size=10, color="#d98a00", bold=True))
    p.append(line(tx_fail, 425, tx_hb, 425, color=POS, sw=1.5))
    p.append(text((tx_fail + tx_hb) / 2, 442, "1.5–3.0 с (MAVLink Heartbeat Timeout)", size=10, color=POS, bold=True))

    p.append(text(W / 2, 495,
                  "Дворівневий відкат запобігає ривкам: спочатку плавна зупинка (Hold), і лише якщо комп'ютер не очуняв — повернення додому (RTL).",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "heartbeat-timeout-timeline.svg"), W, H, *p,
           title="Часова шкала спрацювання failsafe при відмові бортового комп'ютера")

# ── 3. hardware-watchdog-circuit: Апаратна схема живлення й сторожа ──────────
def fig_hardware_watchdog_circuit():
    W, H = 980, 520
    p = [COL_MARKERS]
    p.append(text(W / 2, 38, "Апаратне сполучення FCU та SBC: кероване живлення й апаратний сторож",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 60, "польотний контролер може апаратно перезавантажити бортовий комп'ютер через ключ живлення за відсутності строб-сигналу",
                  size=11.5, color=MUTED, italic=True))

    # Лівий блок: Джерело живлення та Ключ MOSFET
    p.append(rect(40, 95, 230, 365, fill="#f4f6f8", stroke=INK, sw=1.6, rx=10))
    p.append(text(155, 122, "ВУЗОЛ ЖИВЛЕННЯ SBC", size=12, color=INK, bold=True))

    p.append(rect(60, 145, 190, 60, fill="#fff5e6", stroke="#d98a00", sw=1.4, rx=8))
    p.append(text(155, 170, "DC-DC BEC 5V / 12V", size=11, color="#d98a00", bold=True))
    p.append(text(155, 188, "Живлення від батареї LiPo", size=9.5, color=MUTED))

    p.append(rect(60, 245, 190, 85, fill="#fdecea", stroke=POS, sw=1.6, rx=8))
    p.append(text(155, 268, "P-MOSFET / Ключ живлення", size=10.5, color=POS, bold=True))
    p.append(text(155, 286, "(High-Side Switch / TPS22810)", size=9, color=MUTED))
    p.append(text(155, 306, "Розриває +5V на SBC", size=9.5, color=POS))

    p.append(carrow(155, 205, 155, 242, "#d98a00", "G", sw=2.0))

    # Центральний блок: Бортовий комп'ютер (SBC - RPi / Jetson)
    p.append(rect(350, 95, 260, 365, fill="#eef2ff", stroke=NEG, sw=1.8, rx=10))
    p.append(text(480, 122, "БОРТОВИЙ КОМП'ЮТЕР (SBC)", size=12.5, color=NEG, bold=True))
    p.append(text(480, 140, "Raspberry Pi 5 / Jetson Orin", size=10, color=MUTED))

    # Порти SBC
    p.append(rect(370, 160, 220, 50, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(480, 181, "5V DC Power IN", size=10.5, color=POS, bold=True))
    p.append(text(480, 197, "Вхід основного живлення", size=9.5, color=MUTED))

    p.append(rect(370, 230, 220, 50, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(480, 251, "UART / TELEM2 (TX/RX/GND)", size=10.5, color=INK, bold=True))
    p.append(text(480, 267, "MAVLink протокол (921600 baud)", size=9.5, color=MUTED))

    p.append(rect(370, 300, 220, 50, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(480, 321, "GPIO OUT: Watchdog Strobe", size=10.5, color=FIELD, bold=True))
    p.append(text(480, 337, "Перемикання 1-10 Гц від демона", size=9.5, color=MUTED))

    p.append(rect(370, 370, 220, 68, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    p.append(text(480, 391, "USER SPACE ДЕМОН", size=10.5, color=INK, bold=True))
    p.append(text(480, 408, "Перевіряє MAVSDK/ROS 2", size=9.5, color=MUTED))
    p.append(text(480, 423, "і смикає GPIO тільки при здоров'ї", size=9.5, color=FIELD))

    # Правий блок: Польотний контролер (FCU - STM32 / Pixhawk)
    p.append(rect(690, 95, 250, 365, fill="#eafaef", stroke=FIELD, sw=1.8, rx=10))
    p.append(text(815, 122, "ПОЛЬОТНИЙ КОНТРОЛЕР (FCU)", size=12.5, color=FIELD, bold=True))
    p.append(text(815, 140, "Pixhawk / STM32H7 (PX4 / ArduPilot)", size=10, color=MUTED))

    # Порти FCU
    p.append(rect(710, 160, 210, 50, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(815, 181, "GPIO OUT: SBC_PWR_EN", size=10.5, color=POS, bold=True))
    p.append(text(815, 197, "Керування затвором ключа", size=9.5, color=MUTED))

    p.append(rect(710, 230, 210, 50, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(815, 251, "TELEM2 UART (RX/TX/GND)", size=10.5, color=INK, bold=True))
    p.append(text(815, 267, "Парсер MAVLink / Offboard", size=9.5, color=MUTED))

    p.append(rect(710, 300, 210, 50, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(815, 321, "GPIO IN: Strobe / Pulse Capture", size=10.5, color=FIELD, bold=True))
    p.append(text(815, 337, "Таймер перевірки імпульсів", size=9.5, color=MUTED))

    p.append(rect(710, 370, 210, 68, fill=BG, stroke=FIELD, sw=1.2, rx=6))
    p.append(text(815, 391, "АВТОНОМНИЙ FSM СТЕК", size=10.5, color=FIELD, bold=True))
    p.append(text(815, 408, "ПІД-регулятори, EKF2, Nav", size=9.5, color=MUTED))
    p.append(text(815, 423, "Повністю незалежне живлення", size=9.5, color=POS))

    # З'єднувальні лінії
    # Живлення від ключа до SBC
    p.append(carrow(250, 287, 368, 185, POS, "R", sw=2.2))
    p.append(text(300, 225, "+5V Power", size=10, color=POS, bold=True))

    # Керування живленням від FCU до ключа (зверху)
    p.append(line(710, 185, 660, 185, color=POS, sw=1.8))
    p.append(line(660, 185, 660, 75, color=POS, sw=1.8))
    p.append(line(660, 75, 155, 75, color=POS, sw=1.8))
    p.append(carrow(155, 75, 155, 242, POS, "R", sw=1.8))
    p.append(text(410, 68, "PWR_EN (FCU скидає живлення при зависанні)", size=9.5, color=POS, bold=True))

    # UART Link (двосторонній)
    p.append(carrow(590, 250, 707, 250, INK, "B", sw=1.8))
    p.append(carrow(710, 260, 593, 260, INK, "B", sw=1.8))
    p.append(text(650, 242, "MAVLink", size=10, color=INK, bold=True))

    # GPIO Strobe від SBC до FCU
    p.append(carrow(590, 325, 707, 325, FIELD, "G", sw=2.0))
    p.append(text(650, 316, "Heartbeat Pulse", size=10, color=FIELD, bold=True))

    p.append(text(W / 2, 495,
                  "Апаратний сторож дає незалежність: якщо процес MAVSDK зависне на SBC, строб припиниться, і FCU перезавантажить живлення SBC.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "hardware-watchdog-circuit.svg"), W, H, *p,
           title="Схема електричного та логічного сполучення FCU і бортового комп'ютера")

# ── 4. reboot-handshake-state-machine: Автомат безпечного підключення ─────────
def fig_reboot_handshake_state_machine():
    W, H = 980, 500
    p = [COL_MARKERS]
    p.append(text(W / 2, 38, "Автомат безпечного підключення та повернення в Offboard після перезапуску SBC",
                  size=14, color=INK, bold=True))
    p.append(text(W / 2, 60, "заборонено миттєво вмикати Offboard: потрібна фаза синхронізації телеметрії та прогріву потоку уставок",
                  size=11.5, color=MUTED, italic=True))

    states = [
        (40, 120, 160, 90, "1. ЗБІЙ І РЕСТАРТ", ["FCU в режимі LOITER", "SBC перезавантажується", "Живлення скинуто"], POS, "#fdecea"),
        (230, 120, 165, 90, "2. СТАРТ СЛУЖОБ", ["Linux завантажився", "ROS 2 / MAVSDK запуск", "UART порт відкрито"], "#d98a00", "#fff5e6"),
        (430, 120, 165, 90, "3. СИНХРОНІЗАЦІЯ", ["Читання поточної позиції", "Звірка режиму польоту", "Оцінка здоров'я EKF"], NEG, "#eef2ff"),
        (630, 120, 165, 90, "4. ПРОГРІВ ПОТОКУ", ["Уставки = поточній точці", "Потік 20 Гц понад 1 с", "Помилка = 0"], FIELD, "#eafaef"),
        (830, 120, 120, 90, "5. OFFBOARD", ["Handshake OK", "Плавний рух", "Місія триває"], FIELD, "#dcfce7"),
    ]

    for x, y, w, h, name, desc, col, fill in states:
        p.append(rect(x, y, w, h, fill=fill, stroke=col, sw=1.8, rx=10))
        p.append(text(x + w / 2, y + 24, name, size=11, color=col, bold=True))
        p.append(line(x + 10, y + 34, x + w - 10, y + 34, color=col, sw=0.8, dash="3 2"))
        dy = y + 50
        for ln in desc:
            p.append(text(x + w / 2, dy, ln, size=9.5, color=INK))
            dy += 15

    # Стрілки переходів між станами
    for i in range(4):
        x1 = states[i][0] + states[i][2]
        x2 = states[i + 1][0]
        p.append(carrow(x1, 165, x2 - 3, 165, INK, "G" if i >= 2 else "B", sw=2.0))

    # Тексти умов над переходами
    labels = [
        "boot complete (~20 с)",
        "MAVLink heartbeat OK",
        "потік стабільний 1 с",
        "FCU switch accept",
    ]
    xs = [195, 397, 597, 797]
    for x, lbl in zip(xs, labels):
        p.append(text(x, 106, lbl, size=9, color=MUTED, italic=True))

    # Нижній блок: Чому небезпечний миттєвий перехід (Bumpless Transfer)
    p.append(rect(80, 270, 820, 160, fill="#f4f6f8", stroke=INK, sw=1.8, rx=12))
    p.append(text(W / 2, 298, "ЧОМУ НЕОБХІДНИЙ ПРОГРІВ ПОТОКУ (BUMPLESS TRANSFER НА ЕТАПІ 4)", size=12.5, color=INK, bold=True))

    p.append(rect(100, 318, 380, 95, fill="#fff3f3", stroke=POS, sw=1.4, rx=8))
    p.append(text(290, 340, "НЕБЕЗПЕЧНО: СТАРТ ЗІ СТАРИМИ УСТАВКАМИ", size=10.5, color=POS, bold=True))
    p.append(text(290, 360, "Якщо SBC надішле ціль до збою, дрон", size=9.5, color=INK))
    p.append(text(290, 376, "зробить різкий ривок на повній швидкості,", size=9.5, color=INK))
    p.append(text(290, 394, "що спричинить зрив потоку або аварію.", size=9.5, color=POS, bold=True))

    p.append(rect(500, 318, 380, 95, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=8))
    p.append(text(690, 340, "БЕЗПЕЧНО: СИНХРОНІЗОВАНЕ ПІДХОПЛЕННЯ", size=10.5, color=FIELD, bold=True))
    p.append(text(690, 360, "SBC читає координату дрона в LOITER,", size=9.5, color=INK))
    p.append(text(690, 376, "формує уставку точно в цю точку, і лише", size=9.5, color=INK))
    p.append(text(690, 394, "потім плавно нарощує вектор траєкторії.", size=9.5, color=FIELD, bold=True))

    p.append(text(W / 2, 475,
                  "Повторний вхід у контур Offboard можливий лише після безшовної синхронізації координат і відсутності похибки позиції.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "reboot-handshake-state-machine.svg"), W, H, *p,
           title="Автомат станів безпечного відновлення зв'язку під час рестарту SBC у польоті")


if __name__ == "__main__":
    fig_failure_modes()
    fig_heartbeat_timeout_timeline()
    fig_hardware_watchdog_circuit()
    fig_reboot_handshake_state_machine()
    print("All figures generated successfully.")
