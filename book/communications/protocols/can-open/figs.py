# -*- coding: utf-8 -*-
"""Фігури до теми «CANopen».
Запуск: python figs.py → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Структура 11-бітного COB-ID у Pre-defined Connection Set ───────────────
def fig_cob_id_structure():
    W, H = 780, 460
    f = [text(W / 2, 26, "Розподіл 11-бітного COB-ID: Код функції (4 біти) + Вузол (7 бітів)",
              size=14.5, bold=True)]

    # 11-бітне поле COB-ID
    ox = 80
    topY = 55
    step = (W - 160) / 11.0

    # Шапка бітів 10..0
    for k in range(11):
        bit_num = 10 - k
        cx = ox + step * (k + 0.5)
        f.append(text(cx, topY, f"b{bit_num}", size=9.5, color=MUTED))

    # Рамка коду функції (біти 10..7)
    w_fc = step * 4
    f.append(rect(ox, topY + 12, w_fc, 44, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=6))
    f.append(text(ox + w_fc / 2, topY + 38, "Код функції (4 біти)", size=11, bold=True, color=NEG))

    # Рамка ID вузла (біти 6..0)
    w_node = step * 7
    f.append(rect(ox + w_fc + 4, topY + 12, w_node - 4, 44, fill="#fbeee6", stroke=POS, sw=1.8, rx=6))
    f.append(text(ox + w_fc + w_node / 2, topY + 38, "Ідентифікатор вузла Node-ID (1..127)", size=11, bold=True, color=POS))

    # Таблиця канонічних діапазонів COB-ID
    tableY = 135
    rows = [
        ("NMT Master", "0000b", "0x000", "Керування станами мережі (NMT)", NEG),
        ("SYNC / TIME", "0001b", "0x080 / 0x100", "Синхронізація та точний час", FIELD),
        ("EMCY", "0001b", "0x081..0x0FF", "Аварійні повідомлення (0x080 + Node-ID)", POS),
        ("TPDO1 / RPDO1", "0011b / 0100b", "0x181..0x27F", "Кадри даних реального часу PDO1", INK),
        ("SDO (Tx / Rx)", "1011b / 1100b", "0x581..0x6FF", "Конфігурація словника (0x580 / 0x600 + ID)", FIELD),
        ("Heartbeat", "1110b", "0x701..0x7FF", "Контроль працездатності (0x700 + Node-ID)", POS),
    ]

    rowH = 34
    f.append("<g>")
    f.append(rect(60, tableY, W - 120, len(rows) * rowH + 26, fill="#fafbfc", stroke="#d6dde6", sw=1.2, rx=8))
    f.append("</g>")
    f.append(text(100, tableY + 18, "Об'єкт", size=10.5, bold=True, color=MUTED, anchor="start"))
    f.append(text(240, tableY + 18, "Код функції", size=10.5, bold=True, color=MUTED, anchor="start"))
    f.append(text(370, tableY + 18, "Діапазон COB-ID", size=10.5, bold=True, color=MUTED, anchor="start"))
    f.append(text(540, tableY + 18, "Призначення", size=10.5, bold=True, color=MUTED, anchor="start"))
    f.append(line(70, tableY + 24, W - 70, tableY + 24, color="#e1e8f0", sw=1))

    for idx, (obj, fc, cob, desc, col) in enumerate(rows):
        ry = tableY + 42 + idx * rowH
        f.append(text(100, ry, obj, size=11, bold=True, color=col, anchor="start"))
        f.append(text(240, ry, fc, size=10.5, color=INK, anchor="start"))
        f.append(text(370, ry, cob, size=10.5, bold=True, color=col, anchor="start"))
        f.append(text(540, ry, desc, size=10, color=MUTED, anchor="start"))

    b, _, _ = textbox(W / 2, H - 24,
                      "Pre-defined Connection Set гарантує унікальність ID для 127 вузлів без конфліктів арбітражу",
                      size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "cob-id-structure.svg"), W, H, *f)


# ── 2. Скінченний автомат станів NMT ──────────────────────────────────────────
def fig_nmt_state_machine():
    W, H = 780, 430
    f = [text(W / 2, 26, "Скінченний автомат NMT: стани вузла та дозволені канали зв'язку",
              size=14.5, bold=True)]

    # 4 блоки станів
    states = [
        (130, 160, "Initialisation", "Завантаження / Скидання", NEG, "#fdecea",
         "• NMT Boot-up (0x700+ID)\n• PDO/SDO вимкнено"),
        (400, 100, "Pre-Operational", "Конфігурація", FIELD, "#eaf0fd",
         "• SDO працює (параметри)\n• NMT / Heartbeat активні\n• PDO ВИМКНЕНО"),
        (670, 160, "Operational", "Робочий режим", POS, "#eef6ef",
         "• УСІ канали активні\n• PDO дані реального часу\n• SDO / NMT / Heartbeat"),
        (400, 290, "Stopped", "Зупинено (Безпека)", INK, "#f2f4f7",
         "• Тільки NMT та Heartbeat\n• SDO / PDO ВИМКНЕНО"),
    ]

    for cx, cy, title, subtitle, col, fillc, details in states:
        f.append(rect(cx - 95, cy - 45, 190, 90, fill=fillc, stroke=col, sw=1.8, rx=10))
        f.append(text(cx, cy - 26, title, size=12, bold=True, color=col))
        f.append(text(cx, cy - 10, f"({subtitle})", size=9.5, italic=True, color=MUTED))
        lines = details.split('\n')
        for i, l in enumerate(lines):
            f.append(text(cx - 80, cy + 12 + i * 14, l, size=9.5, color=INK, anchor="start"))

    # Стрілки переходів
    f.append(arrow(225, 140, 305, 120, color=MUTED, sw=1.6))
    f.append(text(250, 118, "авто-перехід", size=9, italic=True, color=MUTED))

    f.append(arrow(495, 115, 575, 140, color=POS, sw=2.0))
    f.append(text(535, 115, "Start (0x01)", size=9.5, bold=True, color=POS))

    f.append(arrow(575, 175, 495, 135, color=FIELD, sw=1.6))
    f.append(text(545, 170, "Pre-Op (0x80)", size=9.5, color=FIELD))

    f.append(arrow(600, 205, 495, 275, color=INK, sw=1.6))
    f.append(text(570, 250, "Stop (0x02)", size=9.5, color=INK))

    f.append(arrow(400, 145, 400, 245, color=INK, sw=1.6))
    f.append(text(410, 195, "Stop (0x02)", size=9.5, color=INK, anchor="start"))

    f.append(arrow(320, 270, 320, 145, color=FIELD, sw=1.6))
    f.append(text(310, 210, "Pre-Op (0x80)", size=9.5, color=FIELD, anchor="end"))

    f.append(arrow(400, 335, 150, 205, color=NEG, sw=1.6))
    f.append(text(240, 290, "Reset Node (0x81/0x82)", size=9.5, bold=True, color=NEG))

    b, _, _ = textbox(W / 2, H - 22,
                      "Вузол стартує у Pre-Operational для конфігурації SDO і переходить у Operational для обміну PDO",
                      size=11, fill="#fbeee6", stroke=POS)
    f.append(b)
    render(os.path.join(IMG, "nmt-state-machine.svg"), W, H, *f)


# ── 3. Кадр прискореної SDO-транзакції (Expedited SDO) ───────────────────────
def fig_sdo_expedited_frame():
    W, H = 780, 420
    f = [text(W / 2, 26, "Кадр SDO Expedited (8 байтів payload): Запит / Відповідь до Словника Об'єктів",
              size=14.5, bold=True)]

    ox = 50
    topY = 60
    step = (W - 100) / 8.0

    labels = [
        ("Байт 0", "Команда SDO\n(CCS/SCS, e, s, n)"),
        ("Байт 1", "Індекс LSB\n(0x00..0xFF)"),
        ("Байт 2", "Індекс MSB\n(0x10..0x9F)"),
        ("Байт 3", "Субіндекс\n(0x00..0xFF)"),
        ("Байт 4", "Дані / Abort\nБайт 0 (LSB)"),
        ("Байт 5", "Дані / Abort\nБайт 1"),
        ("Байт 6", "Дані / Abort\nБайт 2"),
        ("Байт 7", "Дані / Abort\nБайт 3 (MSB)"),
    ]

    colors = [NEG, FIELD, FIELD, POS, INK, INK, INK, INK]
    fills = ["#fdecea", "#eaf0fd", "#eaf0fd", "#eef6ef", "#fafbfc", "#fafbfc", "#fafbfc", "#fafbfc"]

    for k in range(8):
        cx = ox + step * k
        cw = step - 4
        col = colors[k]
        fillc = fills[k]
        bname, bdesc = labels[k]
        f.append(rect(cx, topY, cw, 65, fill=fillc, stroke=col, sw=1.6, rx=6))
        f.append(text(cx + cw / 2, topY + 18, bname, size=11, bold=True, color=col))
        f.append(text(cx + cw / 2, topY + 40, bdesc, size=9.5, color=INK))

    cmdY = 160
    f.append("<g>")
    f.append(rect(50, cmdY, W - 100, 160, fill="#fdfbf7", stroke="#d6dde6", sw=1.2, rx=8))
    f.append("</g>")
    f.append(text(W / 2, cmdY + 20, "Дешифрація бітів командного байта (Байт 0)", size=12, bold=True, color=INK))

    bit_specs = [
        ("біти 7..5 (CCS/SCS)", "Специфікатор команди: 001b=Write, 010b=Read Resp, 000b=Write Resp, 100b=Read Req, 1000b=Abort"),
        ("біти 3..2 (n)", "Кількість ВПОРОЖНІЛИХ байтів даних у корисній навантаженості (4 - count)"),
        ("біт 1 (e)", "Expedited flag: 1 = прискорений переказ (дані ≤4B прямо в байтах 4..7); 0 = сегментований"),
        ("біт 0 (s)", "Size indicator: 1 = розмір даних вказано у прапорці n"),
    ]

    for idx, (bname, bdesc) in enumerate(bit_specs):
        yy = cmdY + 46 + idx * 26
        f.append(text(70, yy, bname, size=10.5, bold=True, color=NEG, anchor="start"))
        f.append(text(250, yy, bdesc, size=10, color=INK, anchor="start"))

    b, _, _ = textbox(W / 2, H - 24,
                      "Expedited SDO передає значення до 32 бітів за ОДИН кадр запиту і одне підтвердження",
                      size=11, fill="#eaf0fd", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "sdo-expedited-frame.svg"), W, H, *f)


# ── 4. Механізм динамічного відображення PDO (PDO Mapping) ────────────────────
def fig_pdo_mapping_mechanism():
    W, H = 780, 440
    f = [text(W / 2, 26, "Динамічне відображення PDO: Зв'язок запису 0x1A00 зі Словником Об'єктів",
              size=14.5, bold=True)]

    # 1. Параметри відображення у Словнику Об'єктів (Запис 0x1A00)
    odX = 60
    odY = 65
    f.append(rect(odX, odY, 280, 160, fill="#eaf0fd", stroke=FIELD, sw=1.8, rx=8))
    f.append(text(odX + 140, odY + 22, "Словник Об'єктів: Запис 0x1A00", size=12, bold=True, color=FIELD))
    f.append(text(odX + 140, odY + 38, "(Параметри мапінгу TPDO1)", size=9.5, italic=True, color=MUTED))
    f.append(line(odX + 10, odY + 48, odX + 270, odY + 48, color="#c8d6e5", sw=1))

    f.append(text(odX + 20, odY + 70, "Sub-index 0x00:", size=10, bold=True, color=INK, anchor="start"))
    f.append(text(odX + 130, odY + 70, "2 (кількість елементів)", size=10, color=POS, anchor="start"))

    f.append(text(odX + 20, odY + 98, "Sub-index 0x01:", size=10, bold=True, color=INK, anchor="start"))
    f.append(text(odX + 130, odY + 98, "0x60410010 (32 біти)", size=10.5, bold=True, color=NEG, anchor="start"))
    f.append(text(odX + 20, odY + 114, "   → Індекс 0x6041, Sub 0x00, 16 бітів", size=9, color=MUTED, anchor="start"))

    f.append(text(odX + 20, odY + 138, "Sub-index 0x02:", size=10, bold=True, color=INK, anchor="start"))
    f.append(text(odX + 130, odY + 138, "0x60640020 (32 біти)", size=10.5, bold=True, color=POS, anchor="start"))
    f.append(text(odX + 20, odY + 154, "   → Індекс 0x6064, Sub 0x00, 32 біти", size=9, color=MUTED, anchor="start"))

    # 2. Фактичні змінні Словника Об'єктів
    varX = 440
    varY = 65
    f.append(rect(varX, varY, 280, 160, fill="#fbeee6", stroke=POS, sw=1.8, rx=8))
    f.append(text(varX + 140, varY + 22, "Змінні Словника Об'єктів", size=12, bold=True, color=POS))
    f.append(text(varX + 140, varY + 38, "(Профіль приводу CiA 402)", size=9.5, italic=True, color=MUTED))
    f.append(line(varX + 10, varY + 48, varX + 270, varY + 48, color="#e5c8bd", sw=1))

    f.append(text(varX + 20, varY + 76, "0x6041:00 (Statusword):", size=10, bold=True, color=NEG, anchor="start"))
    f.append(text(varX + 200, varY + 76, "16 бітів (2B)", size=10, color=INK, anchor="start"))

    f.append(text(varX + 20, varY + 126, "0x6064:00 (Position Actual):", size=10, bold=True, color=POS, anchor="start"))
    f.append(text(varX + 200, varY + 126, "32 біти (4B)", size=10, color=INK, anchor="start"))

    # Стрілки вказівників мапінгу
    f.append(arrow(odX + 270, odY + 98, varX + 10, varY + 76, color=NEG, sw=1.8))
    f.append(arrow(odX + 270, odY + 138, varX + 10, varY + 126, color=POS, sw=1.8))

    # 3. Результатуючий кадр TPDO1 на шині CAN
    frameY = 265
    f.append('<g transform="translate(0,0)">')
    f.append(rect(60, frameY, W - 120, 120, fill="#eef6ef", stroke=POS, sw=1.8, rx=8))
    f.append('</g>')
    f.append(text(W / 2, frameY + 22, "Кадр даних TPDO1 на шині CAN (COB-ID = 0x180 + Node-ID)", size=12, bold=True, color=POS))

    # Байти кадру
    bX = 110
    bY = frameY + 45
    f.append(rect(bX, bY, 160, 45, fill="#fdecea", stroke=NEG, sw=1.4, rx=4))
    f.append(text(bX + 80, bY + 18, "Statusword (2 байти)", size=10.5, bold=True, color=NEG))
    f.append(text(bX + 80, bY + 34, "Байт 0..1 (з 0x6041)", size=9, color=MUTED))

    f.append(rect(bX + 170, bY, 320, 45, fill="#eaf0fd", stroke=POS, sw=1.4, rx=4))
    f.append(text(bX + 330, bY + 18, "Position Actual Value (4 байти)", size=10.5, bold=True, color=POS))
    f.append(text(bX + 330, bY + 34, "Байт 2..5 (з 0x6064)", size=9, color=MUTED))

    f.append(rect(bX + 500, bY, 120, 45, fill="#f2f4f7", stroke=MUTED, sw=1.0, rx=4))
    f.append(text(bX + 560, bY + 26, "Вільні 2B", size=10, color=MUTED))

    # Стрілки пакування в кадр
    f.append(arrow(varX + 140, varY + 90, bX + 80, bY - 4, color=NEG, sw=1.6))
    f.append(arrow(varX + 140, varY + 140, bX + 330, bY - 4, color=POS, sw=1.6))

    b, _, _ = textbox(W / 2, H - 22,
                      "Усередині кадру PDO немає заголовочних адресацій: тільки чисті корисні дані у суворій послідовності",
                      size=11, fill="#fafbfc", stroke="#c8d6e5")
    f.append(b)
    render(os.path.join(IMG, "pdo-mapping-mechanism.svg"), W, H, *f)


if __name__ == "__main__":
    fig_cob_id_structure()
    fig_nmt_state_machine()
    fig_sdo_expedited_frame()
    fig_pdo_mapping_mechanism()
    print("OK: 4 figures ->", IMG)
