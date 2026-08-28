# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми OMA LwM2M (Lightweight Machine to Machine)."""

import os
import sys

# Підключення svgkit із scripts/ (4 рівні вгору від root/com/com-protocol/<slug>)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_lwm2m_architecture():
    """Фігура 1: Архітектура та чотири логічні інтерфейси LwM2M між клієнтом і серверами."""
    w, h = 880, 520
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 30, "Архітектура OMA LwM2M: 4 логічні інтерфейси та стек протоколів", size=15, bold=True))

    # Ліва колонка: LwM2M Client (IoT Device)
    cx_cli = 140
    frags.append(rect(30, 65, 220, 420, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(cx_cli, 92, "LwM2M Клієнт", size=14, bold=True, color=INK))
    frags.append(text(cx_cli, 110, "(Вбудований вузол / MCU)", size=11, color=MUTED))

    # Рівні всередині клієнта
    frags.append(fitbox(45, 130, 190, 48, "IPSO Smart Objects\n(Сенсори, актуатори, стан)", size=11, fill="#e8f8f5", stroke=FIELD, bold=True))
    frags.append(fitbox(45, 186, 190, 48, "LwM2M Core Objects\n(Security, Server, Device, FOTA)", size=11, fill="#eaf0fd", stroke=NEG, bold=True))
    frags.append(fitbox(45, 242, 190, 44, "LwM2M Client Engine\n(Об'єктна модель, TLV/SenML)", size=11, fill="#fef9e7", stroke="#d4ac0d", bold=True))
    frags.append(fitbox(45, 294, 190, 40, "CoAP (RFC 7252 / 7959 / 7641)\nREST, Blockwise, Observe", size=10, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(45, 342, 190, 36, "Безпека: DTLS 1.2 / OSCORE", size=10, fill="#fadbd8", stroke=POS, bold=True))
    frags.append(fitbox(45, 386, 190, 34, "Транспорт: UDP / SMS / TCP", size=10, fill="#f4f6f8", stroke=LINE))
    frags.append(fitbox(45, 428, 190, 42, "Фізичний рівень: NB-IoT,\nLTE-M, LoRaWAN, Wi-Fi", size=10, fill="#ffffff", stroke=MUTED))

    # Права верхня колонка: Bootstrap Server
    cx_srv = 740
    frags.append(rect(630, 65, 220, 150, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(cx_srv, 92, "LwM2M Bootstrap Server", size=13, bold=True, color=POS))
    frags.append(text(cx_srv, 110, "Конфігурація безпеки та серверів", size=10, color=MUTED))
    frags.append(fitbox(645, 125, 190, 36, "Облікові дані DTLS (PSK / RPK / X.509)", size=10, fill="#fadbd8", stroke=POS))
    frags.append(fitbox(645, 167, 190, 36, "Призначення робочих LwM2M серверів", size=10, fill="#ffffff", stroke=MUTED))

    # Права нижня колонка: LwM2M Server (Device Management & Application)
    frags.append(rect(630, 240, 220, 245, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(cx_srv, 268, "LwM2M Server", size=14, bold=True, color=FIELD))
    frags.append(text(cx_srv, 286, "Керування пристроями та сервісами", size=10, color=MUTED))
    frags.append(fitbox(645, 302, 190, 38, "Device Management & Service Enablement\n(Read, Write, Exec, Create, Delete)", size=9, fill="#e8f8f5", stroke=FIELD))
    frags.append(fitbox(645, 346, 190, 38, "Registration Directory\n(Реєстрація, оновлення, дереєстрація)", size=9, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(645, 390, 190, 38, "Information Reporting Handler\n(Observe / Notify, умови pmin/pmax)", size=9, fill="#fef9e7", stroke="#d4ac0d"))
    frags.append(fitbox(645, 434, 190, 38, "Firmware Update Orchestrator\n(FOTA завантаження та перевірка)", size=9, fill="#f4f6f8", stroke=LINE))

    # 4 Інтерфейси (стрілки та плашки посередині)
    mid_x1 = 250
    mid_x2 = 630

    # 1. Bootstrap Interface
    y_bs = 140
    frags.append(arrow(mid_x1, y_bs, mid_x2, y_bs, color=POS, sw=1.8))
    frags.append(arrow(mid_x2, y_bs + 16, mid_x1, y_bs + 16, color=POS, sw=1.8))
    frags.append(textbox(440, y_bs + 8, "1. Bootstrap Interface (Завантаження ключів і адрес)", size=10, fill="#fdecea", stroke=POS, bold=True)[0])

    # 2. Registration Interface
    y_reg = 295
    frags.append(arrow(mid_x1, y_reg, mid_x2, y_reg, color=NEG, sw=1.8))
    frags.append(textbox(440, y_reg - 12, "2. Registration Interface (Register / Update / Deregister)", size=10, fill="#eaf0fd", stroke=NEG, bold=True)[0])

    # 3. Device Management & Service Enablement
    y_dm = 370
    frags.append(arrow(mid_x2, y_dm, mid_x1, y_dm, color=FIELD, sw=1.8))
    frags.append(arrow(mid_x1, y_dm + 16, mid_x2, y_dm + 16, color=FIELD, sw=1.8))
    frags.append(textbox(440, y_dm + 8, "3. Device Management (Read / Write / Exec / Write-Attr)", size=10, fill="#e8f8f5", stroke=FIELD, bold=True)[0])

    # 4. Information Reporting
    y_ir = 445
    frags.append(arrow(mid_x2, y_ir, mid_x1, y_ir, color="#d4ac0d", sw=1.8))
    frags.append(arrow(mid_x1, y_ir + 16, mid_x2, y_ir + 16, color="#d4ac0d", sw=1.8))
    frags.append(textbox(440, y_ir + 8, "4. Information Reporting (Observe / Notify / Cancel)", size=10, fill="#fef9e7", stroke="#d4ac0d", bold=True)[0])

    render(os.path.join(OUT_DIR, "lwm2m-architecture-interfaces.svg"), w, h, *frags)


def fig_lwm2m_object_tree():
    """Фігура 2: Дерево об'єктів LwM2M з URI адресацією."""
    w, h = 880, 500
    frags = []

    frags.append(text(w / 2, 28, "Об'єктно-ресурсна ієрархія OMA LwM2M та IPSO Smart Objects", size=15, bold=True))

    # Корінь URI
    frags.append(textbox(w / 2, 68, "URI Простір: /{Object ID} / {Instance ID} / {Resource ID} / {Resource Instance ID}", size=12, fill="#f4f6f8", stroke=LINE, bold=True, pad=8)[0])

    # 4 головні гілки об'єктів
    cols = [
        {"id": "0", "name": "Security (Об'єкт 0)", "inst": "Екземпляр /0/0", "fill": "#fadbd8", "stroke": POS,
         "res": ["/0/0/0 : LwM2M Server URI (String)", "/0/0/1 : Bootstrap Server (Bool)", "/0/0/2 : Security Mode (0..3)", "/0/0/3 : Public Key / Identity", "/0/0/5 : Secret Key (PSK / PrivKey)"]},
        {"id": "1", "name": "Server (Об'єкт 1)", "inst": "Екземпляр /1/0", "fill": "#eaf0fd", "stroke": NEG,
         "res": ["/1/0/0 : Short Server ID (Int)", "/1/0/1 : Lifetime (Секунди)", "/1/0/2 : Default Min Period (pmin)", "/1/0/3 : Default Max Period (pmax)", "/1/0/8 : Registration Update Trigger [E]"]},
        {"id": "3", "name": "Device (Об'єкт 3)", "inst": "Екземпляр /3/0", "fill": "#e8f8f5", "stroke": FIELD,
         "res": ["/3/0/0 : Manufacturer (String)", "/3/0/1 : Model Number (String)", "/3/0/4 : Reboot [Executable]", "/3/0/9 : Battery Level (% 0..100)", "/3/0/11 : Error Code [Multi-Int]"]},
        {"id": "3303", "name": "IPSO Temp (Об'єкт 3303)", "inst": "Екземпляр /3303/0", "fill": "#fef9e7", "stroke": "#d4ac0d",
         "res": ["/3303/0/5700 : Sensor Value (Float)", "/3303/0/5601 : Min Measured Value", "/3303/0/5602 : Max Measured Value", "/3303/0/5701 : Sensor Units (String: Cel)", "/3303/0/5605 : Reset Min/Max [Exec]"]}
    ]

    col_w = 195
    start_x = 35
    gap_x = 18

    for i, col in enumerate(cols):
        cx = start_x + i * (col_w + gap_x)
        # Лінія від кореня
        frags.append(line(w / 2, 90, cx + col_w / 2, 120, color=MUTED, sw=1.2))

        # Заголовок Об'єкта
        frags.append(fitbox(cx, 120, col_w, 42, col["name"], size=12, fill=col["fill"], stroke=col["stroke"], bold=True))

        # Екземпляр
        frags.append(arrow(cx + col_w / 2, 162, cx + col_w / 2, 185, color=col["stroke"], sw=1.5))
        frags.append(fitbox(cx + 15, 185, col_w - 30, 32, col["inst"], size=11, fill="#ffffff", stroke=col["stroke"], bold=True))

        # Ресурси
        frags.append(line(cx + col_w / 2, 217, cx + col_w / 2, 240, color=col["stroke"], sw=1.5))
        r_y = 240
        for r_text in col["res"]:
            is_exec = "[E" in r_text or "[Exec" in r_text
            r_fill = "#fbeee6" if is_exec else "#ffffff"
            r_stroke = POS if is_exec else "#d5dbdb"
            frags.append(fitbox(cx, r_y, col_w, 40, r_text, size=9.5, fill=r_fill, stroke=r_stroke))
            r_y += 46

    # Нижня плашка з типами операцій
    frags.append(textbox(w / 2, 475, "Операції з ресурсами: Читання (R), Запис (W), Виконання (E). Підтримка одиничних і множинних екземплярів.", size=11, fill="#ffffff", stroke=MUTED)[0])

    render(os.path.join(OUT_DIR, "lwm2m-object-tree.svg"), w, h, *frags)


def fig_lwm2m_tlv_format():
    """Фігура 3: Будова бінарного формату LwM2M TLV (Type-Length-Value)."""
    w, h = 860, 460
    frags = []

    frags.append(text(w / 2, 28, "Двійкове кодування LwM2M TLV: структура байта Type та полів", size=15, bold=True))

    x0 = 50
    y0 = 65
    total_w = 760
    bit_w = total_w / 8.0
    row_h = 52

    # Шкала 8 бітів заголовка Type
    for b in range(8):
        bx = x0 + b * bit_w
        frags.append(text(bx + bit_w / 2, y0 - 8, "Bit %d" % (7 - b), size=11, color=MUTED))

    # Байт Type: 4 підполя
    # Біти 7-6: Identifier Type (2 біти)
    frags.append(fitbox(x0, y0, bit_w * 2, row_h, "Тип ідентифікатора\n(Bits 7-6, 2 біти)", size=11, fill="#eaf0fd", stroke=NEG, bold=True))
    # Біт 5: Length of Identifier (1 біт)
    frags.append(fitbox(x0 + bit_w * 2, y0, bit_w * 1, row_h, "ID Len\n(Bit 5)", size=11, fill="#fef9e7", stroke="#d4ac0d", bold=True))
    # Біти 4-3: Type of Length (2 біти)
    frags.append(fitbox(x0 + bit_w * 3, y0, bit_w * 2, row_h, "Тип довжини\n(Bits 4-3, 2 біти)", size=11, fill="#fbeee6", stroke=POS, bold=True))
    # Біти 2-0: Value Length (3 біти)
    frags.append(fitbox(x0 + bit_w * 5, y0, bit_w * 3, row_h, "Довжина значення (Bits 2-0, 3 біти)\n(0..7 байтів, якщо Bits 4-3 = 00)", size=10.5, fill="#e8f8f5", stroke=FIELD, bold=True))

    # Розшифровка значень бітів
    y_dec = y0 + row_h + 18
    box_w = 180
    gap = 13

    frags.append(fitbox(x0, y_dec, box_w, 95, "Bits 7-6 (Тип):\n00 = Object Instance\n01 = Resource Instance\n10 = Multiple Resource\n11 = Resource with Value", size=10, fill="#eaf0fd", stroke=NEG))
    frags.append(fitbox(x0 + box_w + gap, y_dec, box_w, 95, "Bit 5 (Довжина ID):\n0 = 8-бітний ID (1 байт)\n1 = 16-бітний ID (2 байти)", size=10, fill="#fef9e7", stroke="#d4ac0d"))
    frags.append(fitbox(x0 + (box_w + gap) * 2, y_dec, box_w, 95, "Bits 4-3 (Тип Length):\n00 = довжина у Bits 2-0\n01 = поле Length 8 бітів\n10 = поле Length 16 бітів\n11 = поле Length 24 біти", size=9.5, fill="#fbeee6", stroke=POS))
    frags.append(fitbox(x0 + (box_w + gap) * 3, y_dec, box_w, 95, "Bits 2-0 (Значення):\nЯкщо Bits 4-3 == 00,\nзадає довжину Value\nвід 0 до 7 байтів прямо\nу байті заголовка Type", size=9.5, fill="#e8f8f5", stroke=FIELD))

    # Повна структура пакету TLV
    y_seq = y_dec + 115
    frags.append(text(w / 2, y_seq, "Послідовність полів у бінарному потоці TLV", size=13, bold=True, color=INK))

    y_boxes = y_seq + 15
    f_w1 = total_w * 0.18
    f_w2 = total_w * 0.22
    f_w3 = total_w * 0.22
    f_w4 = total_w * 0.38

    frags.append(fitbox(x0, y_boxes, f_w1, 52, "Type (1 байт)\nБітова маска прапорців", size=11, fill="#f4f6f8", stroke=LINE, bold=True))
    frags.append(fitbox(x0 + f_w1, y_boxes, f_w2, 52, "Identifier (1 або 2 байти)\nResource ID або Instance ID", size=10.5, fill="#fef9e7", stroke="#d4ac0d", bold=True))
    frags.append(fitbox(x0 + f_w1 + f_w2, y_boxes, f_w3, 52, "Length (0, 1, 2 або 3 байти)\nВідсутнє, якщо довжина <= 7", size=10, fill="#fbeee6", stroke=POS, bold=True))
    frags.append(fitbox(x0 + f_w1 + f_w2 + f_w3, y_boxes, f_w4, 52, "Value (L байтів)\nЦіле, Float, String, Boolean або вкладений TLV", size=10.5, fill="#e8f8f5", stroke=FIELD, bold=True))

    frags.append(textbox(w / 2, y_boxes + 75, "Компактність: для числових ресурсів із ID < 256 та довжиною <= 7 заголовок займає лише 2 байти (Type + ID).", size=11, fill="#ffffff", stroke=MUTED)[0])

    render(os.path.join(OUT_DIR, "lwm2m-tlv-format.svg"), w, h, *frags)


def fig_lwm2m_firmware_update_fsm():
    """Фігура 4: Скінченний автомат стану оновлення прошивки (Object 5 FSM)."""
    w, h = 880, 520
    frags = []

    frags.append(text(w / 2, 28, "Автомат станів оновлення прошивки (LwM2M Object 5 FSM)", size=15, bold=True))

    # 4 стани (State /5/0/3)
    states = [
        {"id": 0, "name": "0: IDLE\n(Очікування)", "x": 100, "y": 140, "fill": "#f4f6f8", "stroke": LINE},
        {"id": 1, "name": "1: DOWNLOADING\n(Завантаження)", "x": 340, "y": 140, "fill": "#fef9e7", "stroke": "#d4ac0d"},
        {"id": 2, "name": "2: DOWNLOADED\n(Перевірено)", "x": 580, "y": 140, "fill": "#eaf0fd", "stroke": NEG},
        {"id": 3, "name": "3: UPDATING\n(Прошивання / Своп)", "x": 780, "y": 140, "fill": "#fadbd8", "stroke": POS}
    ]

    box_w, box_h = 135, 60

    for st in states:
        frags.append(fitbox(st["x"] - box_w / 2, st["y"] - box_h / 2, box_w, box_h, st["name"], size=11, fill=st["fill"], stroke=st["stroke"], bold=True))

    # Переходи вперед
    # Idle -> Downloading
    frags.append(arrow(170, 140, 270, 140, color=FIELD, sw=2))
    frags.append(textbox(220, 115, "Write /5/0/0 (Push) або\nWrite /5/0/1 (URI Pull)", size=9.5, fill="#e8f8f5", stroke=FIELD)[0])

    # Downloading -> Downloaded
    frags.append(arrow(410, 140, 510, 140, color=NEG, sw=2))
    frags.append(textbox(460, 115, "Пакет завантажено,\nSHA-256 / підпис OK", size=9.5, fill="#eaf0fd", stroke=NEG)[0])

    # Downloaded -> Updating
    frags.append(arrow(650, 140, 710, 140, color=POS, sw=2))
    frags.append(textbox(680, 115, "Execute /5/0/2\n(Запуск FOTA)", size=9.5, fill="#fadbd8", stroke=POS, bold=True)[0])

    # Updating -> Idle (Успішне оновлення після ребуту)
    frags.append(arrow(780, 172, 780, 245, color=FIELD, sw=2))
    frags.append(line(780, 245, 100, 245, color=FIELD, sw=2))
    frags.append(arrow(100, 245, 100, 172, color=FIELD, sw=2))
    frags.append(textbox(440, 245, "Перезавантаження MCU -> Успішний старт нової версії -> State=0, Update Result=1 (Success)", size=10.5, fill="#e8f8f5", stroke=FIELD, bold=True)[0])

    # Помилки (Update Result /5/0/5) -> повернення в IDLE
    y_err = 320
    frags.append(text(w / 2, y_err, "Обробка помилок: повернення в State 0 (IDLE) з кодом Update Result (/5/0/5)", size=12, bold=True, color=POS))

    # Сітка кодів результатів
    err_box_w = 185
    err_box_h = 42
    errs = [
        ("0: Початковий стан / Дефолт", "#ffffff", MUTED),
        ("1: Успішно оновлено (Success)", "#e8f8f5", FIELD),
        ("2: Бракує пам'яті Flash (Storage)", "#fadbd8", POS),
        ("3: Переповнення RAM (Out of RAM)", "#fadbd8", POS),
        ("4: Втрата зв'язку під час скачування", "#fadbd8", POS),
        ("5: Помилка перевірки цілісності (CRC/Sig)", "#fadbd8", POS),
        ("6: Непідтримуваний тип пакету", "#fadbd8", POS),
        ("7: Некоректний URI або протокол", "#fadbd8", POS),
    ]

    r_start_x = 40
    r_gap_x = 22
    r_start_y = y_err + 20
    r_gap_y = 12

    for idx, (err_text, e_fill, e_stroke) in enumerate(errs):
        row = idx // 4
        col = idx % 4
        ex = r_start_x + col * (err_box_w + r_gap_x)
        ey = r_start_y + row * (err_box_h + r_gap_y)
        frags.append(fitbox(ex, ey, err_box_w, err_box_h, err_text, size=9.5, fill=e_fill, stroke=e_stroke, bold=(idx == 1)))

    # Нижня примітка про захист від збоїв
    frags.append(textbox(w / 2, 480, "Атомарність оновлення: якщо валідація прошивки не пройшла, завантажувач відновлює робочий образ із резервного банку.", size=10.5, fill="#ffffff", stroke=MUTED)[0])

    render(os.path.join(OUT_DIR, "lwm2m-firmware-update-fsm.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_lwm2m_architecture()
    fig_lwm2m_object_tree()
    fig_lwm2m_tlv_format()
    fig_lwm2m_firmware_update_fsm()
    print("Генерація 4 SVG-фігур для LwM2M завершена успішно.")
