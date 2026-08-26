# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. packet-frame-structure: Анатомія двійкового кадру на лінку ─────────────
def fig_packet_frame_structure():
    W, H = 960, 430
    p = []

    # Заголовок фігури
    p.append(text(W / 2, 30, "Анатомія двійкового кадру телеметрії на послідовному лінку", size=16, color=INK, bold=True))

    # Секція 1: Байти кадру
    y_blocks = 70
    h_block = 70

    fields = [
        ("SYNC1", "0xAA", 70, "#fee2e2", POS, "Преамбула"),
        ("SYNC2", "0x55", 70, "#fee2e2", POS, "Преамбула"),
        ("MSG_ID", "0x01..0xFF", 90, "#e0f2fe", "#0284c7", "Тип (ID)"),
        ("SEQ", "0x00..0xFF", 85, "#ede9fe", "#7c3aed", "Лічильник"),
        ("LEN", "N (0..64)", 85, "#fef3c7", "#d97706", "Довжина"),
        ("PAYLOAD (0..N байтів)", "Дані: координати, кути, напруга, прапорці стану", 360, "#f0fdf4", FIELD, "Корисне навантаження"),
        ("CRC_L", "LSB", 80, "#fce7f3", "#db2777", "Контроль"),
        ("CRC_H", "MSB", 80, "#fce7f3", "#db2777", "Контроль"),
    ]

    cur_x = 40
    for name, val, bw, bg_col, stroke_col, role in fields:
        p.append(rect(cur_x, y_blocks, bw, h_block, fill=bg_col, stroke=stroke_col, sw=1.8, rx=6))
        p.append(text(cur_x + bw / 2, y_blocks + 22, name, size=12, color=stroke_col, bold=True))
        p.append(text(cur_x + bw / 2, y_blocks + 42, val, size=10.5, color=INK, bold=(bw < 200)))
        p.append(text(cur_x + bw / 2, y_blocks + 60, role, size=9.5, color=MUTED))
        cur_x += bw + 6

    # Зона охоплення CRC
    crc_start_x = 40 + 70 + 6 + 70 + 6 # MSG_ID start
    crc_end_x = cur_x - (80 + 6 + 80 + 6) # PAYLOAD end
    p.append(line(crc_start_x, y_blocks + h_block + 14, crc_end_x, y_blocks + h_block + 14, color="#db2777", sw=2))
    p.append(line(crc_start_x, y_blocks + h_block + 8, crc_start_x, y_blocks + h_block + 20, color="#db2777", sw=2))
    p.append(line(crc_end_x, y_blocks + h_block + 8, crc_end_x, y_blocks + h_block + 20, color="#db2777", sw=2))
    p.append(text((crc_start_x + crc_end_x) / 2, y_blocks + h_block + 32, "Покриття CRC-16: байти заголовка (MSG_ID, SEQ, LEN) + корисне навантаження PAYLOAD", size=11, color="#db2777", bold=True))

    # Нижня частина: детальний розбір полів
    y_desc = 205
    desc_boxes = [
        ("Синхронізація (0xAA55)", "2 байти з чергуванням бітів (10101010 01010101). Захищає від зсуву фази UART та випадкового шуму лінії.", POS, 270),
        ("Заголовок і довжина", "MSG_ID визначає структуру даних, SEQ відстежує втрату пакетів у каналі, LEN обмежує кадр у статичний буфер.", "#0284c7", 290),
        ("Контроль цілісності (CRC-16)", "Поліном 0x1021 (CCITT), ініціалізація 0xFFFF. Гарантує виявлення 100% пакетних завад довжиною до 16 бітів.", "#db2777", 290),
    ]

    bx = 40
    for title_txt, body_txt, col, bw in desc_boxes:
        p.append(rect(bx, y_desc, bw, 195, fill="#f8fafc", stroke=col, sw=1.4, rx=6))
        p.append(rect(bx, y_desc, bw, 32, fill=col, stroke=col, sw=1.4, rx=6))
        p.append(text(bx + bw / 2, y_desc + 21, title_txt, size=11.5, color="#ffffff", bold=True))
        p.append(mtext(bx + 16, y_desc + 56, body_txt, size=10.5, color=INK, anchor="start", lh=1.45))
        
        # Додатковий технічний інваріант у кожному блоці
        if "Синхронізація" in title_txt:
            p.append(text(bx + 16, y_desc + 145, "Ймовірність хибного шуму:", size=10, color=MUTED, anchor="start"))
            p.append(text(bx + 16, y_desc + 165, "P = 1 / 65536 ≈ 0.0015%", size=10.5, color=POS, bold=True, anchor="start"))
        elif "Заголовок" in title_txt:
            p.append(text(bx + 16, y_desc + 145, "Статичний максимум буфера:", size=10, color=MUTED, anchor="start"))
            p.append(text(bx + 16, y_desc + 165, "MAX_PAYLOAD = 64 байти", size=10.5, color="#0284c7", bold=True, anchor="start"))
        else:
            p.append(text(bx + 16, y_desc + 145, "Невловлені багатобітові завади:", size=10, color=MUTED, anchor="start"))
            p.append(text(bx + 16, y_desc + 165, "P_undetected < 1.5 · 10^(-5)", size=10.5, color="#db2777", bold=True, anchor="start"))

        bx += bw + 15

    render(os.path.join(OUT, "packet-frame-structure.svg"), W, H, *p,
           title="Анатомія двійкового кадру телеметрії")


# ── 2. fsm-parser-states: Скінченний автомат потокового десеріалізатора ────────
def fig_fsm_parser_states():
    W, H = 960, 480
    p = []

    p.append(text(W / 2, 30, "Граф станів потокового скінченного автомата десеріалізації (FSM)", size=16, color=INK, bold=True))

    # 8 станів автомата, розміщені горизонтально по колу / конвеєру
    states = [
        ("WAIT_SYNC1", "Очікування 0xAA", 60, 110, 140, 60, POS),
        ("WAIT_SYNC2", "Очікування 0x55", 280, 110, 140, 60, POS),
        ("GET_MSG_ID", "Читання типу ID", 500, 110, 140, 60, "#0284c7"),
        ("GET_SEQ", "Читання номера SEQ", 720, 110, 140, 60, "#7c3aed"),
        ("GET_LEN", "Читання довжини N", 720, 270, 140, 60, "#d97706"),
        ("GET_PAYLOAD", "Збір N байтів даних", 500, 270, 140, 60, FIELD),
        ("GET_CRC_L", "Читання CRC (LSB)", 280, 270, 140, 60, "#db2777"),
        ("GET_CRC_H", "Читання CRC (MSB)", 60, 270, 140, 60, "#db2777"),
    ]

    for name, sub, sx, sy, sw, sh, col in states:
        p.append(rect(sx, sy, sw, sh, fill="#f8fafc", stroke=col, sw=2, rx=8))
        p.append(text(sx + sw / 2, sy + 25, name, size=11.5, color=col, bold=True))
        p.append(text(sx + sw / 2, sy + 46, sub, size=9.5, color=MUTED))

    # Прямі переходи нормального шляху (HAPPY PATH)
    # 1. WAIT_SYNC1 -> WAIT_SYNC2 (byte == 0xAA)
    p.append(arrow(200, 140, 276, 140, color=FIELD, sw=2))
    p.append(text(238, 130, "0xAA", size=10, color=FIELD, bold=True))

    # 2. WAIT_SYNC2 -> GET_MSG_ID (byte == 0x55)
    p.append(arrow(420, 140, 496, 140, color=FIELD, sw=2))
    p.append(text(458, 130, "0x55", size=10, color=FIELD, bold=True))

    # 3. GET_MSG_ID -> GET_SEQ (будь-який байт ID)
    p.append(arrow(640, 140, 716, 140, color=FIELD, sw=2))
    p.append(text(678, 130, "ID != 0", size=10, color=FIELD, bold=True))

    # 4. GET_SEQ -> GET_LEN (будь-який байт SEQ)
    p.append(arrow(790, 170, 790, 266, color=FIELD, sw=2))
    p.append(text(830, 220, "SEQ (0..255)", size=10, color=FIELD, bold=True))

    # 5. GET_LEN -> GET_PAYLOAD (LEN <= MAX_PAYLOAD і LEN > 0)
    p.append(arrow(720, 300, 644, 300, color=FIELD, sw=2))
    p.append(text(682, 290, "LEN > 0", size=10, color=FIELD, bold=True))

    # 6. Петля GET_PAYLOAD -> GET_PAYLOAD (count < LEN)
    p.append(arrow(550, 330, 590, 330, color=FIELD, sw=1.8))
    p.append(text(570, 355, "++count < LEN", size=9.5, color=MUTED))

    # 7. GET_PAYLOAD -> GET_CRC_L (count == LEN)
    p.append(arrow(500, 300, 424, 300, color=FIELD, sw=2))
    p.append(text(462, 290, "готово", size=10, color=FIELD, bold=True))

    # 8. GET_CRC_L -> GET_CRC_H (читання 1-го байта CRC)
    p.append(arrow(280, 300, 204, 300, color=FIELD, sw=2))
    p.append(text(242, 290, "CRC_L", size=10, color=FIELD, bold=True))

    # 9. GET_CRC_H -> PACKET DISPATCH / RESET (перевірка)
    p.append(arrow(130, 270, 130, 174, color=FIELD, sw=2))
    p.append(text(75, 220, "CRC OK → виклик", size=10, color=FIELD, bold=True))

    # Помилкові переходи / скидання (ERROR / RESYNC PATHS)
    p.append(rect(40, 395, 880, 70, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(55, 416, "ПРАВИЛА САМОВІДНОВЛЕННЯ СИНХРОНІЗАЦІЇ (RESYNCHRONIZATION):", size=11, color=POS, bold=True, anchor="start"))
    
    rules = [
        "1. У стані WAIT_SYNC2 при отриманні 0xAA лишаємось у WAIT_SYNC2 (повтор преамбули). При отриманні іншого байта — перехід у WAIT_SYNC1.",
        "2. У стані GET_LEN якщо LEN > 64 (MAX_PAYLOAD) — миттєве скидання у WAIT_SYNC1 без виділення пам'яті (захист від зависання на смітті).",
        "3. У стані GET_CRC_H якщо обчислена CRC != отриманій — лічильник crc_errors++, скидання у WAIT_SYNC1 (жодних дій не виконується).",
    ]
    ry = 432
    for r_txt in rules:
        p.append(text(55, ry, r_txt, size=10, color=INK, anchor="start"))
        ry += 15

    render(os.path.join(OUT, "fsm-parser-states.svg"), W, H, *p,
           title="Граф переходів автомата потокового розбору")


# ── 3. byte-slip-resync: Зсув байтів та відновлення синхронізації ─────────────
def fig_byte_slip_resync():
    W, H = 960, 440
    p = []

    p.append(text(W / 2, 30, "Механізм захисту від зсуву байтів (Byte-Slip) та самовідновлення FSM", size=16, color=INK, bold=True))

    # Сценарій: Втрата 1 байта в радіоканалі викликає розсинхронізацію наївного парсера
    y_top = 65
    p.append(rect(40, y_top, 880, 150, fill="#fef2f2", stroke=POS, sw=1.6, rx=8))
    p.append(text(55, y_top + 24, "НАЇВНИЙ БЛОКОВИЙ ПАРСЕР (read_exact / memcpy структури): КАТАСТРОФА", size=13, color=POS, bold=True, anchor="start"))

    bx_y = y_top + 40
    p.append(text(55, bx_y + 16, "Потік:", size=11, color=MUTED, anchor="start"))

    raw_stream_1 = [
        ("0xAA", "#dcfce7", FIELD), ("0x55", "#dcfce7", FIELD), ("0x01", "#f1f5f9", LINE),
        ("0x04", "#f1f5f9", LINE), ("0x12", "#f1f5f9", LINE), ("0x34", "#f1f5f9", LINE),
        ("ВТРАЧЕНО", "#fee2e2", POS),
        ("0xAA", "#fef3c7", "#d97706"), ("0x55", "#fef3c7", "#d97706"), ("0x02", "#fef3c7", "#d97706"),
        ("0x04", "#fef3c7", "#d97706"), ("0x99", "#fef3c7", "#d97706"), ("0x88", "#fef3c7", "#d97706"),
    ]

    cx = 110
    for b_name, bg_c, str_c in raw_stream_1:
        w_b = 68 if b_name == "ВТРАЧЕНО" else 48
        p.append(rect(cx, bx_y, w_b, 26, fill=bg_c, stroke=str_c, sw=1.2, rx=4))
        p.append(text(cx + w_b / 2, bx_y + 17, b_name, size=9.5, color=str_c, bold=True))
        cx += w_b + 4

    p.append(text(55, y_top + 95, "1. Втрата лише одного байта зміщує всі подальші зміщення полів у буфері DMA.", size=10.5, color=INK, anchor="start"))
    p.append(text(55, y_top + 115, "2. Наївний парсер читає байти 0xAA 0x55 наступного кадру як шматок PAYLOAD першого кадру!", size=10.5, color=POS, bold=True, anchor="start"))
    p.append(text(55, y_top + 135, "3. Наслідок: битий перший пакет + ВТРАТА всіх наступних пакетів до повного переповнення буфера.", size=10.5, color=POS, bold=True, anchor="start"))

    # Нижній блок: Потоковий автомат FSM (САМОВІДНОВЛЕННЯ)
    y_bot = 235
    p.append(rect(40, y_bot, 880, 185, fill="#f0fdf4", stroke=FIELD, sw=1.6, rx=8))
    p.append(text(55, y_bot + 24, "ПОТОКОВИЙ АВТОМАТ FSM ІЗ КОВЗНИМ ВІКНОМ: САМОВІДНОВЛЕННЯ ЗА 1 КАДР", size=13, color=FIELD, bold=True, anchor="start"))

    bx_y2 = y_bot + 40
    p.append(text(55, bx_y2 + 16, "Потік:", size=11, color=MUTED, anchor="start"))

    raw_stream_2 = [
        ("0xAA", "#dcfce7", FIELD), ("0x55", "#dcfce7", FIELD), ("0x01", "#f1f5f9", LINE),
        ("0x04", "#f1f5f9", LINE), ("0x12", "#f1f5f9", LINE), ("0x34", "#f1f5f9", LINE),
        ("ВТРАЧЕНО", "#fee2e2", POS),
        ("0xAA", "#dcfce7", FIELD), ("0x55", "#dcfce7", FIELD), ("0x02", "#f1f5f9", LINE),
        ("0x04", "#f1f5f9", LINE), ("0x99", "#f1f5f9", LINE), ("0x88", "#f1f5f9", LINE),
        ("CRC1", "#fce7f3", "#db2777"), ("CRC2", "#fce7f3", "#db2777"),
    ]

    cx2 = 110
    for b_name, bg_c, str_c in raw_stream_2:
        w_b = 68 if b_name == "ВТРАЧЕНО" else 42
        p.append(rect(cx2, bx_y2, w_b, 26, fill=bg_c, stroke=str_c, sw=1.2, rx=4))
        p.append(text(cx2 + w_b / 2, bx_y2 + 17, b_name, size=9.5, color=str_c, bold=True))
        cx2 += w_b + 4

    p.append(text(55, y_bot + 95, "Крок 1: Втрата байта порушує довжину першого кадру -> обчислена CRC-16 не зійшлася.", size=10.5, color=INK, anchor="start"))
    p.append(text(55, y_bot + 115, "Крок 2: FSM фіксує помилку контрольної суми, ігнорує пошкоджений кадр і МИТТЄВО повертається у стан WAIT_SYNC1.", size=10.5, color=INK, anchor="start"))
    p.append(text(55, y_bot + 135, "Крок 3: Наступні байти 0xAA 0x55 точно розпізнаються як преамбула свіжого кадру №2.", size=10.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(55, y_bot + 155, "Результат: втрачено лише 1 пошкоджений пакет. Усі наступні кадри декодуються без жодної затримки!", size=10.5, color=FIELD, bold=True, anchor="start"))

    render(os.path.join(OUT, "byte-slip-resync.svg"), W, H, *p,
           title="Відновлення синхронізації парсера при зсуві байтів")


# ── 4. crc16-lfsr-computation: Механізм розрахунку CRC-16 ─────────────────────
def fig_crc16_lfsr_computation():
    W, H = 960, 420
    p = []

    p.append(text(W / 2, 30, "Математичний конвеєр CRC-16-CCITT: зсувний регістр LFSR та табличний прискорювач (LUT)", size=15, color=INK, bold=True))

    lx, ly, lw, lh = 40, 65, 430, 330
    p.append(rect(lx, ly, lw, lh, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(lx + lw / 2, ly + 25, "1. Поліноміальний LFSR (GF(2) ділення)", size=13, color=INK, bold=True))
    p.append(text(lx + lw / 2, ly + 44, "Поліном G(x) = x^16 + x^12 + x^5 + 1 (маска 0x1021)", size=10.5, color=MUTED))

    ry_boxes = ly + 70
    stages = ["b15", "...", "b12", "...", "b5", "...", "b0"]
    sx = lx + 20
    for st in stages:
        w_st = 48 if st != "..." else 34
        p.append(rect(sx, ry_boxes, w_st, 32, fill="#ffffff", stroke="#0284c7", sw=1.4, rx=4))
        p.append(text(sx + w_st / 2, ry_boxes + 21, st, size=11, color="#0284c7", bold=True))
        sx += w_st + 6

    p.append(circle(lx + 155, ry_boxes + 65, 16, fill="#fce7f3", stroke="#db2777", sw=1.5))
    p.append(text(lx + 155, ry_boxes + 69, "XOR", size=9.5, color="#db2777", bold=True))
    p.append(arrow(lx + 155, ry_boxes + 49, lx + 155, ry_boxes + 36, color="#db2777", sw=1.5))

    p.append(circle(lx + 270, ry_boxes + 65, 16, fill="#fce7f3", stroke="#db2777", sw=1.5))
    p.append(text(lx + 270, ry_boxes + 69, "XOR", size=9.5, color="#db2777", bold=True))
    p.append(arrow(lx + 270, ry_boxes + 49, lx + 270, ry_boxes + 36, color="#db2777", sw=1.5))

    p.append(text(lx + 20, ly + 185, "Вхідний бітовий потік зсувається вправо/вліво.", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 205, "При висуванні '1' регістр виконує XOR із 0x1021.", size=10.5, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 230, "Гарантії детекції помилок:", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(lx + 20, ly + 250, "• 100% усіх 1-бітових та 2-бітових помилок", size=10, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 270, "• 100% непарної кількості помилок (множник x+1)", size=10, color=INK, anchor="start"))
    p.append(text(lx + 20, ly + 290, "• 100% пачок завад (bursts) довжиною <= 16 бітів", size=10, color=INK, anchor="start"))

    rx, ry, rw, rh = 490, 65, 430, 330
    p.append(rect(rx, ry, rw, rh, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(rx + rw / 2, ry + 25, "2. Табличний прискорювач (Look-Up Table, LUT)", size=13, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, ry + 44, "256 попередньо обчислених слів у Flash (.rodata)", size=10.5, color=MUTED))

    code_y = ry + 70
    p.append(rect(rx + 20, code_y, rw - 40, 80, fill="#ffffff", stroke="#86efac", sw=1.2, rx=6))
    p.append(text(rx + 32, code_y + 24, "// Оновлення CRC на 1 вхідний байт за 4 такти ядра:", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 32, code_y + 46, "uint8_t idx = (crc ^ byte) & 0xFF;", size=11, color=INK, bold=True, anchor="start"))
    p.append(text(rx + 32, code_y + 66, "crc = (crc >> 8) ^ crc16_table[idx];", size=11, color="#0284c7", bold=True, anchor="start"))

    p.append(text(rx + 20, ry + 185, "Переваги табличного підходу у прошивках:", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(rx + 20, ry + 210, "1. Фіксований час виконання (Deterministic Timing) —", size=10, color=INK, anchor="start"))
    p.append(text(rx + 20, ry + 228, "   без умовних переходів та гілкувань конвеєра.", size=10, color=MUTED, anchor="start"))
    p.append(text(rx + 20, ry + 252, "2. Розмір таблиці у Flash: рівно 512 байтів (256 * 2 Б).", size=10, color=INK, anchor="start"))
    p.append(text(rx + 20, ry + 276, "3. Швидкість на Cortex-M4 @ 168 МГц: > 40 МБ/с,", size=10, color=INK, anchor="start"))
    p.append(text(rx + 20, ry + 294, "   що перекриває потік UART (115200..921600 бод) у 400+ разів.", size=10, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "crc16-lfsr-computation.svg"), W, H, *p,
           title="Розрахунок CRC16 через LFSR та табличний прискорювач")


if __name__ == "__main__":
    fig_packet_frame_structure()
    fig_fsm_parser_states()
    fig_byte_slip_resync()
    fig_crc16_lfsr_computation()
    print("OK: figures ->", OUT)
