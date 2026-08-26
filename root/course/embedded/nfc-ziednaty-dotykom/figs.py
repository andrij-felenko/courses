# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. dual-port-arch: Архітектура дводіапазонного чипа мітки NFC ─────────────
def fig_dual_port_arch():
    W, H = 960, 520
    p = []

    # Загальний фон і рамка кристала мітки NFC (Dual-Interface Tag IC)
    chip_x, chip_y, chip_w, chip_h = 240, 70, 480, 420
    p.append(rect(chip_x, chip_y, chip_w, chip_h, fill="#fafbfc", stroke=LINE, sw=2, rx=12))
    p.append(text(chip_x + chip_w / 2, chip_y + 26, "Динамічний чип мітки NFC (ST25DV / NTAG I2C Plus)", size=15, bold=True, color=INK))

    # Ліва колонка ззовні: Смартфон / NFC Reader та котушка
    p.append(rect(20, 100, 180, 360, fill="#f0f4f8", stroke=NEG, sw=1.8, rx=8))
    p.append(text(110, 130, "Смартфон / Зчитувач", size=13, bold=True, color=NEG))
    p.append(mtext(110, 160, "NFC Initiator\nЧастота: 13.56 МГц\nISO/IEC 14443A / 15693", size=11, color=MUTED))

    # Антена смартфона
    p.append(rect(40, 240, 140, 70, fill="#ffffff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(110, 270, "ВЧ-поле 13.56 МГц", size=12, bold=True, color=NEG))
    p.append(text(110, 290, "Магнітний потік B(t)", size=10, color=MUTED))

    # Стрілка індуктивного зв'язку
    p.append(arrow(180, 275, 235, 275, color=FIELD, sw=2.5))
    p.append(text(210, 260, "B-поле", size=11, bold=True, color=FIELD))

    # Блоки всередині чипа (ліва частина - RF Frontend)
    p.append(rect(260, 110, 130, 90, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(325, 135, "RF Frontend", size=12, bold=True, color=FIELD))
    p.append(mtext(325, 160, "Модулятор навантаження\nДемодулятор АМ/ЧМ", size=10, color=INK))

    p.append(rect(260, 220, 130, 100, fill="#fef3e8", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(325, 245, "Energy Harvesting", size=11, bold=True, color="#d97706"))
    p.append(mtext(325, 270, "Синхронний випрямляч\nОбмежувач напруги\nВихід струму V_OUT", size=10, color=INK))

    p.append(rect(260, 340, 130, 120, fill="#f3f4f6", stroke=LINE, sw=1.2, rx=6))
    p.append(text(325, 365, "RF Контролер", size=12, bold=True, color=INK))
    p.append(mtext(325, 390, "ISO14443-3A / ISO15693\nДекодер команд\nКонтроль сесій RF", size=10, color=MUTED))

    # Центральна частина чипа: Спільна пам'ять та арбітраж
    p.append(rect(410, 110, 140, 160, fill="#e8effc", stroke=NEG, sw=1.8, rx=8))
    p.append(text(480, 135, "Двопортова EEPROM", size=12, bold=True, color=NEG))
    p.append(mtext(480, 165, "1 КБ – 64 КБ\nСпільний масив даних\nNDEF-повідомлення\nЖурнал аварій / конфіг", size=10, color=INK))

    p.append(rect(410, 290, 140, 75, fill="#fdf4ff", stroke="#a21caf", sw=1.5, rx=6))
    p.append(text(480, 312, "SRAM FIFO (Fast Mode)", size=10.5, bold=True, color="#a21caf"))
    p.append(mtext(480, 335, "64 / 256 байтів буфер\nПрямий наскрізний потік", size=10, color=INK))

    p.append(rect(410, 380, 140, 80, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(480, 402, "Апаратний Арбітр", size=11, bold=True, color=POS))
    p.append(mtext(480, 424, "RF/I2C блокування\nСемафори доступу", size=10, color=INK))

    # Права частина чипа: I2C інтерфейс та керування
    p.append(rect(570, 110, 130, 160, fill="#f0f9ff", stroke="#0284c7", sw=1.5, rx=6))
    p.append(text(635, 135, "I2C Slave Вузол", size=12, bold=True, color="#0284c7"))
    p.append(mtext(635, 165, "Стандарт / Fast mode\n100 / 400 / 1000 кГц\nClock Stretching\nАдреса пристрою", size=10, color=INK))

    p.append(rect(570, 290, 130, 80, fill="#fffbeb", stroke="#b45309", sw=1.5, rx=6))
    p.append(text(635, 312, "Field Detect (FD)", size=11, bold=True, color="#b45309"))
    p.append(mtext(635, 334, "Генератор переривань\nПоле є / Дані готові", size=10, color=INK))

    p.append(rect(570, 385, 130, 75, fill="#fef3e8", stroke="#ea580c", sw=1.5, rx=6))
    p.append(text(635, 407, "Керування V_OUT", size=11, bold=True, color="#ea580c"))
    p.append(mtext(635, 430, "Вихід Energy Harvest\n1.8 В – 3.3 В до 5 мА", size=10, color=INK))

    # Права колонка ззовні: Мікроконтролер пристрою (Host MCU)
    p.append(rect(760, 100, 180, 360, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(850, 130, "Мікроконтролер (MCU)", size=13, bold=True, color=INK))
    p.append(mtext(850, 155, "STM32 / ESP32 / nRF52\nХост-процесор пристрою", size=10.5, color=MUTED))

    # Лінії зв'язку між чипом та MCU
    # I2C (SDA/SCL)
    p.append(line(700, 170, 760, 170, color="#0284c7", sw=2))
    p.append(line(700, 200, 760, 200, color="#0284c7", sw=2))
    p.append(text(730, 163, "SDA", size=10, bold=True, color="#0284c7"))
    p.append(text(730, 193, "SCL", size=10, bold=True, color="#0284c7"))

    # FD / INT
    p.append(arrow(700, 330, 760, 330, color="#b45309", sw=2))
    p.append(text(730, 322, "FD / INT", size=10, bold=True, color="#b45309"))

    # V_OUT / EH
    p.append(arrow(700, 420, 760, 420, color="#ea580c", sw=2))
    p.append(text(730, 412, "V_OUT", size=10, bold=True, color="#ea580c"))

    render(os.path.join(OUT, "dual-port-arch.svg"), W, H, *p,
           title="Архітектура дводіапазонної мітки NFC: зв'язок RF та I2C через спільну EEPROM")


# ── 2. ndef-record-layout: Побайтова анатомія NDEF-запису ────────────────────
def fig_ndef_record_layout():
    W, H = 960, 500
    p = []

    # Верхній блок: TLV-обгортка в пам'яті мітки Type 2 / Type 5
    p.append(rect(40, 50, 880, 75, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(480, 72, "Структура TLV у пам'яті NFC-мітки (Capability Container + NDEF TLV)", size=13, bold=True, color=INK))

    tlv_blocks = [
        ("CC (4/8 байтів)", "0xE1 0x40 ...", 115, "#e2e8f0"),
        ("T: 0x03", "NDEF Маркер", 85, "#e0f2fe"),
        ("L: Довжина", "1 або 3 байти", 100, "#e0f2fe"),
        ("V: NDEF Message (Послідовність NDEF-записів)", "Record #1, Record #2 ...", 440, "#dbeafe"),
        ("T: 0xFE", "Термінатор", 85, "#fee2e2"),
    ]
    cur_x = 55
    for title, sub, bw, fill in tlv_blocks:
        p.append(rect(cur_x, 82, bw, 32, fill=fill, stroke=LINE, sw=1.2, rx=4))
        p.append(text(cur_x + bw / 2, 96, title, size=10, bold=True, color=INK))
        p.append(text(cur_x + bw / 2, 108, sub, size=9.5, color=MUTED))
        cur_x += bw + 6

    # Середній блок: Біти заголовка NDEF Record Header (1 байт)
    p.append(rect(40, 140, 880, 145, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(480, 162, "Анатомія першого байта заголовка NDEF-запису (Record Header Byte)", size=13, bold=True, color=FIELD))

    bits = [
        ("MB (біт 7)", "Message Begin", "1 = перший запис\nповідомлення", 95, "#dcfce7"),
        ("ME (біт 6)", "Message End", "1 = останній запис\nповідомлення", 95, "#dcfce7"),
        ("CF (біт 5)", "Chunk Flag", "1 = фрагментований\nзапис", 95, "#f3f4f6"),
        ("SR (біт 4)", "Short Record", "1 = довжина 1 байт\n0 = довжина 4 байти", 105, "#dbeafe"),
        ("IL (біт 3)", "ID Length", "1 = присутнє поле\nID Length та ID", 95, "#f3f4f6"),
        ("TNF (біти 2..0)", "Type Name Format", "0x01: Well-Known (URI/Text)\n0x02: MIME | 0x04: External", 310, "#fef3c7"),
    ]
    cur_x = 55
    for title, name, desc, bw, fill in bits:
        p.append(rect(cur_x, 175, bw, 96, fill=fill, stroke=LINE, sw=1.2, rx=4))
        p.append(text(cur_x + bw / 2, 192, title, size=10.5, bold=True, color=INK))
        p.append(text(cur_x + bw / 2, 207, name, size=9.5, bold=True, color=MUTED))
        p.append(mtext(cur_x + bw / 2, 228, desc, size=9.5, color=INK))
        cur_x += bw + 7

    # Нижні блоки: Поля запису та приклади (URI vs BLE OOB)
    p.append(rect(40, 305, 425, 175, fill="#ffffff", stroke="#0284c7", sw=1.5, rx=8))
    p.append(text(252, 327, "Приклад: URI Record (TNF=0x01, Type='U')", size=12, bold=True, color="#0284c7"))
    uri_fields = [
        ("Header", "0xD1 (MB=1, ME=1, SR=1, TNF=1)", 18),
        ("Type Len", "0x01 (довжина типу 'U' = 1)", 18),
        ("Payload Len", "0x12 (18 байтів корисного навантаження)", 18),
        ("Type", "0x55 ('U' - Well-Known URI)", 18),
        ("Payload", "0x04 ('https://') + 'mydevice.local'", 22),
    ]
    cy = 348
    for fname, fval, fh in uri_fields:
        p.append(rect(55, cy, 395, fh, fill="#f0f9ff", stroke="#bae6fd", sw=1, rx=3))
        p.append(text(105, cy + fh / 2 + 3, fname, size=10, bold=True, color="#0369a1", anchor="start"))
        p.append(text(300, cy + fh / 2 + 3, fval, size=9.5, color=INK, anchor="middle"))
        cy += fh + 5

    p.append(rect(495, 305, 425, 175, fill="#ffffff", stroke="#7c3aed", sw=1.5, rx=8))
    p.append(text(707, 327, "Приклад: BLE OOB (TNF=0x02, MIME)", size=12, bold=True, color="#7c3aed"))
    ble_fields = [
        ("Header", "0xD2 (MB=1, ME=1, SR=1, TNF=2)", 18),
        ("Type Len", "0x20 (32 байти назви MIME)", 18),
        ("Payload Len", "0x24 (36 байтів OOB даних)", 18),
        ("Type", "'application/vnd.bluetooth.ep.oob'", 18),
        ("Payload", "MAC (6B) + LE Role (1B) + TK (16B) + Name", 22),
    ]
    cy = 348
    for fname, fval, fh in ble_fields:
        p.append(rect(510, cy, 395, fh, fill="#faf5ff", stroke="#ddd6fe", sw=1, rx=3))
        p.append(text(560, cy + fh / 2 + 3, fname, size=10, bold=True, color="#6d28d9", anchor="start"))
        p.append(text(755, cy + fh / 2 + 3, fval, size=9.5, color=INK, anchor="middle"))
        cy += fh + 5

    render(os.path.join(OUT, "ndef-record-layout.svg"), W, H, *p,
           title="Анатомія NDEF: біти заголовка, типи TNF та структура корисного навантаження")


# ── 3. ble-oob-flow: Послідовність спаровування BLE OOB в один дотик ──────────
def fig_ble_oob_flow():
    W, H = 960, 500
    p = []

    # Три доріжки учасників
    cols = [
        ("Смартфон (NFC + BLE Central)", 150, "#e0f2fe", "#0284c7"),
        ("Динамічна мітка NFC", 480, "#edf7ed", FIELD),
        ("Мікроконтролер пристрою (BLE)", 810, "#f3f4f6", LINE),
    ]
    for name, cx, fill, stroke in cols:
        p.append(rect(cx - 130, 45, 260, 36, fill=fill, stroke=stroke, sw=1.5, rx=6))
        p.append(text(cx, 68, name, size=12, bold=True, color=INK))
        p.append(line(cx, 81, cx, 470, color="#cbd5e1", sw=1.5, dash="4,4"))

    # Покрокові стрілки обміну
    steps = [
        # (y, from_x, to_x, title, desc, color)
        (110, 150, 480, "1. Наближення смартфона (< 2 см)", "Генерація поля 13.56 МГц (RF Field ON)", FIELD),
        (160, 480, 810, "2. Сигнал Field Detect (FD)", "Переривання GPIO: пробудження MCU з Deep Sleep", "#b45309"),
        (215, 150, 480, "3. Зчитування NDEF через RF", "ISO14443-3A Read -> MIME 'application/vnd.bluetooth.ep.oob'", "#0284c7"),
        (270, 150, 150, "4. Парсинг OOB на смартфоні", "Вилучення Target MAC, LE Role, TK/Confirm Hash", "#6d28d9"),
        (330, 810, 810, "5. MCU вмикає Directed Advertising", "BLE радіо активується на цільовий MAC", "#ea580c"),
        (390, 150, 810, "6. Прямий BLE CONNECT_REQ", "З'єднання на 2.4 ГГц без сканування ефіру", "#0284c7"),
        (445, 150, 810, "7. Автентифікація SMP з OOB ключем", "Шифрований канал без ризику перехоплення MitM", POS),
    ]

    for y, x1, x2, title, desc, color in steps:
        if x1 == x2:
            # Внутрішня дія
            p.append(rect(x1 - 120, y - 16, 240, 32, fill="#ffffff", stroke=color, sw=1.5, rx=6))
            p.append(text(x1, y - 2, title, size=10.5, bold=True, color=color))
            p.append(text(x1, y + 10, desc, size=9.5, color=MUTED))
        else:
            p.append(arrow(x1, y, x2, y, color=color, sw=2))
            mid_x = (x1 + x2) / 2
            p.append(rect(mid_x - 140, y - 22, 280, 20, fill="#ffffff", stroke="#e2e8f0", sw=1, rx=4))
            p.append(text(mid_x, y - 8, title, size=10, bold=True, color=color))
            p.append(text(mid_x, y + 14, desc, size=9.5, color=MUTED))

    render(os.path.join(OUT, "ble-oob-flow.svg"), W, H, *p,
           title="Протокол BLE Out-of-Band Pairing: від піднесення телефона до шифрованого лінка")


# ── 4. energy-harvesting-power: Збір енергії та зчитування без батареї ─────────
def fig_energy_harvesting():
    W, H = 960, 460
    p = []

    # Ліва половина: Схема живлення Energy Harvesting
    p.append(rect(30, 50, 440, 380, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(250, 75, "Вузол збору енергії (Energy Harvesting)", size=13, bold=True, color=INK))

    # Котушка
    p.append(rect(50, 110, 100, 70, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(100, 138, "NFC Антена", size=11, bold=True, color=FIELD))
    p.append(text(100, 158, "13.56 МГц", size=10, color=MUTED))

    # Випрямляч
    p.append(arrow(150, 145, 190, 145, color=LINE, sw=1.5))
    p.append(rect(190, 110, 110, 70, fill="#fffbeb", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(245, 138, "Випрямляч", size=11, bold=True, color="#d97706"))
    p.append(text(245, 158, "RF -> DC", size=10, color=MUTED))

    # Регулятор V_OUT
    p.append(arrow(300, 145, 340, 145, color=LINE, sw=1.5))
    p.append(rect(340, 110, 110, 70, fill="#fef3e8", stroke="#ea580c", sw=1.5, rx=6))
    p.append(text(395, 138, "Пін V_OUT", size=11, bold=True, color="#ea580c"))
    p.append(text(395, 158, "2.8–3.3 В", size=10, color=MUTED))

    # Буферний конденсатор і навантаження
    p.append(arrow(395, 180, 395, 230, color="#ea580c", sw=2))
    p.append(rect(180, 230, 120, 60, fill="#f1f5f9", stroke=LINE, sw=1.2, rx=6))
    p.append(text(240, 255, "Конденсатор C_buf", size=10.5, bold=True, color=INK))
    p.append(text(240, 273, "4.7 – 22 мкФ", size=9.5, color=MUTED))

    p.append(line(395, 260, 300, 260, color="#ea580c", sw=1.5))

    p.append(rect(330, 230, 120, 60, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(390, 255, "Ультра-LP MCU", size=10.5, bold=True, color=FIELD))
    p.append(text(390, 273, "I_act < 1.5 мА", size=9.5, color=MUTED))

    # Спільна EEPROM
    p.append(rect(180, 320, 270, 90, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(315, 345, "Двопортова пам'ять EEPROM", size=11, bold=True, color=NEG))
    p.append(mtext(315, 370, "Чорна скринька: дамп аварій (HardFault)\nСтатистика датчиків, калібрування, серійник\nЧитається навіть при мертвому MCU", size=9.5, color=INK))

    # Права половина: Часова діаграма процесу
    p.append(rect(490, 50, 440, 380, fill="#fafbfc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(710, 75, "Часова діаграма живлення від поля (Zero-Power Boot)", size=12, bold=True, color=INK))

    # Осцилограми
    # 1. RF Field
    p.append(text(510, 115, "RF Поле:", size=10, bold=True, color=FIELD, anchor="start"))
    p.append(line(580, 125, 640, 125, color=FIELD, sw=1.5))
    p.append(line(640, 125, 645, 105, color=FIELD, sw=2))
    p.append(line(645, 105, 870, 105, color=FIELD, sw=2))
    p.append(line(870, 105, 875, 125, color=FIELD, sw=2))
    p.append(line(875, 125, 910, 125, color=FIELD, sw=1.5))

    # 2. V_OUT Voltage
    p.append(text(510, 175, "V_OUT (В):", size=10, bold=True, color="#ea580c", anchor="start"))
    p.append(line(580, 195, 640, 195, color="#ea580c", sw=1.5))
    # Плавний заряд конденсатора
    p.append('<path d="M 640 195 Q 655 160 670 160 L 870 160 Q 885 190 900 195" fill="none" stroke="#ea580c" stroke-width="2"/>')
    p.append(text(675, 150, "3.0 В", size=9.5, bold=True, color="#ea580c"))

    # 3. MCU Activity
    p.append(text(510, 240, "MCU Стан:", size=10, bold=True, color=INK, anchor="start"))
    p.append(rect(580, 225, 90, 28, fill="#f1f5f9", stroke=MUTED, sw=1, rx=3))
    p.append(text(625, 242, "Вимкнено (0V)", size=9.5, color=MUTED))

    p.append(rect(675, 225, 60, 28, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    p.append(text(705, 242, "Boot (2мс)", size=9.5, bold=True, color="#d97706"))

    p.append(rect(740, 225, 125, 28, fill="#dcfce7", stroke=FIELD, sw=1.2, rx=3))
    p.append(text(802, 242, "I2C Запис логів у EEPROM", size=9.5, bold=True, color=FIELD))

    p.append(rect(870, 225, 45, 28, fill="#f1f5f9", stroke=MUTED, sw=1, rx=3))
    p.append(text(892, 242, "Off", size=9.5, color=MUTED))

    # 4. NFC Read
    p.append(text(510, 305, "RF Read:", size=10, bold=True, color=NEG, anchor="start"))
    p.append(rect(770, 290, 120, 28, fill="#dbeafe", stroke=NEG, sw=1.2, rx=3))
    p.append(text(830, 307, "Смартфон читає EEPROM", size=9.5, bold=True, color=NEG))

    # Пояснювальний блок унизу
    p.append(rect(505, 335, 410, 80, fill="#f0f9ff", stroke="#bae6fd", sw=1, rx=6))
    p.append(text(710, 355, "Перевага Zero-Power архітектури:", size=10.5, bold=True, color="#0369a1"))
    p.append(mtext(710, 375, "Прилад без батареї або у глибокому збої живиться від\nтелефона сервісника і віддає повну історію несправностей.", size=9.5, color=INK))

    render(os.path.join(OUT, "energy-harvesting-power.svg"), W, H, *p,
           title="Збір енергії поля (Energy Harvesting) та діагностика повністю знеструмленого приладу")


if __name__ == "__main__":
    fig_dual_port_arch()
    fig_ndef_record_layout()
    fig_ble_oob_flow()
    fig_energy_harvesting()
    print("Figures generated successfully.")
