# -*- coding: utf-8 -*-
"""Фігури до теми «Специфікація як документ»
(root/course/embedded/spetsyfikatsiia-iak-dokument).
Запуск: python figs.py -> створює SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


def fig_spec_architecture_pipeline():
    W, H = 1000, 520
    f = []
    f.append(text(W / 2, 28, "Конвеєр кодогенерації з єдиного джерела правди (Single Source of Truth)", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "Автоматична синхронізація прошивки, серверного бекенду, інструментів аналізу та тестових наборів", 12, MUTED, "middle", italic=True))

    # Single Source of Truth Box (Center Top)
    ssot_x, ssot_y, ssot_w, ssot_h = 320, 80, 360, 110
    f.append(rect(ssot_x, ssot_y, ssot_w, ssot_h, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    f.append(text(ssot_x + ssot_w / 2, ssot_y + 24, "Єдине джерело правди (SSOT Репозиторій)", 13, NEG, "middle", bold=True))
    f.append(text(ssot_x + ssot_w / 2, ssot_y + 48, "Декларативна схема: protocol.ksy / protocol.proto", 11.5, INK, "middle"))
    f.append(text(ssot_x + ssot_w / 2, ssot_y + 68, "• Семантичне версіонування (SemVer: v2.4.0)", 10.5, MUTED, "middle"))
    f.append(text(ssot_x + ssot_w / 2, ssot_y + 88, "• Опис типів, діапазонів, таймінгів та помилок", 10.5, MUTED, "middle"))

    # CI/CD Generator Node
    gen_x, gen_y, gen_w, gen_h = 370, 225, 260, 50
    f.append(rect(gen_x, gen_y, gen_w, gen_h, fill="#fff3cd", stroke="#d35400", sw=1.8, rx=6))
    f.append(text(gen_x + gen_w / 2, gen_y + 22, "CI/CD Компілятор схем", 12.5, "#d35400", "middle", bold=True))
    f.append(text(gen_x + gen_w / 2, gen_y + 40, "ksc / protoc / flatc / custom-gen", 11, INK, "middle"))

    # Arrow from SSOT to CI/CD
    f.append(arrow(W / 2, ssot_y + ssot_h, W / 2, gen_y, color=LINE, sw=1.8))
    f.append(text(W / 2 + 55, 208, "git push / tag", 10, MUTED, "middle"))

    # 4 Generated Targets
    targets = [
        ("Прошивка (Firmware)", "#eafaf1", FIELD, [
            "• C / C++ структури та енуми",
            "• Zero-copy парсери без динамічної пам'яті",
            "• Статична валідація зміщень (static_assert)"
        ], 30),
        ("Серверний бекенд / Cloud", "#eaf0fd", NEG, [
            "• Python / Go / Node.js DTO",
            "• Потокові десеріалізатори",
            "• JSON Schema для REST/MQTT шлюзів"
        ], 275),
        ("Інженерний стенд та GUI", "#f3e8fd", "#7d3c98", [
            "• Wireshark Lua Dissector",
            "• Web Dashboard (TypeScript / WASM)",
            "• Скрипти польового калібрування"
        ], 520),
        ("CI Conformance Suite", "#fdecea", POS, [
            "• Золоті тестові вектори (Golden Packets)",
            "• Фаззинг парсерів за граматикою",
            "• Перевірка зворотної сумісності"
        ], 765)
    ]

    tgt_w = 205
    tgt_h = 145
    tgt_y = 315

    for title_str, fill_c, strk_c, lines_list, tx in targets:
        f.append(rect(tx, tgt_y, tgt_w, tgt_h, fill=fill_c, stroke=strk_c, sw=1.8, rx=8))
        f.append(rect(tx, tgt_y, tgt_w, 28, fill=strk_c, stroke=strk_c, sw=1.8, rx=8))
        f.append(rect(tx, tgt_y + 18, tgt_w, 10, fill=strk_c, stroke=strk_c, sw=0, rx=0))
        f.append(text(tx + tgt_w / 2, tgt_y + 19, title_str, 11, BG, "middle", bold=True))

        for j, line_txt in enumerate(lines_list):
            f.append(text(tx + 8, tgt_y + 48 + j * 26, line_txt, 9.5, INK, "start"))

        # Arrow from CI/CD to each target
        src_x = gen_x + gen_w / 2
        src_y = gen_y + gen_h
        dst_x = tx + tgt_w / 2
        dst_y = tgt_y
        f.append(arrow(src_x, src_y, dst_x, dst_y, color=LINE, sw=1.5))

    # Bottom summary banner
    sum_y = 475
    f.append(rect(30, sum_y, W - 60, 36, fill="#f8f9fa", stroke="#bdc3c7", sw=1.2, rx=6))
    f.append(text(W / 2, sum_y + 23, "Результат: нульовий ризик розсинхронізації вирівнювання полів, типів даних та кодів помилок між командами", 11.5, INK, "middle", bold=True))

    render(os.path.join(IMG, "spec-architecture-pipeline.svg"), W, H, *f)


def fig_binary_frame_specification_anatomy():
    W, H = 1000, 500
    f = []
    f.append(text(W / 2, 28, "Анатомія бінарної специфікації пакетного фрейму", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "Побайтове зміщення, порядок байтів (Little Endian), типи даних та масштабування фізичних величин", 12, MUTED, "middle", italic=True))

    # Frame Bytes Visualization
    fields = [
        ("SOF\n0xAA", 70, "#eaf0fd", NEG, "Байт 0", "Start of Frame\nФіксований 0xAA"),
        ("VER\n0x01", 65, "#f4f6f8", MUTED, "Байт 1", "Версія протоколу\n0x01 (v1.x)"),
        ("MSG_ID\n0x20", 75, "#fff3cd", "#d35400", "Байт 2", "Тип повідомлення\n0x20: TELEMETRY"),
        ("SEQ_ID\n0x4A", 75, "#eaf0fd", NEG, "Байт 3", "Номер транзакції\n0..255 (Sequence)"),
        ("LENGTH\n0x0008", 95, "#f3e8fd", "#7d3c98", "Байти 4..5", "Довжина Payload\nuint16_le = 8 B"),
        ("PAYLOAD (ТЕЗИСТАТОР / ДАТЧИКИ)\n8 байтів корисних даних", 360, "#eafaf1", FIELD, "Байти 6..13", "Вміст повідомлення\n(розкладка полів нижче)"),
        ("CRC-16\n0x7F2B", 95, "#fdecea", POS, "Байти 14..15", "CRC-16-CCITT\nuint16_le (Poly 0x1021)"),
        ("EOF\n0x55", 70, "#eaf0fd", NEG, "Байт 16", "End of Frame\nФіксований 0x55")
    ]

    start_x = 45
    y_pos = 85
    box_h = 55
    curr_x = start_x

    for label_str, bw, fill_c, strk_c, byte_idx, desc_str in fields:
        f.append(rect(curr_x, y_pos, bw, box_h, fill=fill_c, stroke=strk_c, sw=1.6, rx=4))
        f.append(text(curr_x + bw / 2, y_pos - 8, byte_idx, 10, MUTED, "middle"))
        f.append(mtext(curr_x + bw / 2, y_pos + 20, label_str.split("\n"), 10.5, INK, "middle", lh=1.2, bold=True))
        curr_x += bw + 8

    # Payload Deep Dive Section
    sub_y = 180
    f.append(rect(45, sub_y, W - 90, 160, fill="#ffffff", stroke="#95a5a6", sw=1.5, rx=8))
    f.append(rect(45, sub_y, W - 90, 28, fill="#2c3e50", stroke="#2c3e50", sw=1.5, rx=8))
    f.append(rect(45, sub_y + 18, W - 90, 10, fill="#2c3e50", stroke="#2c3e50", sw=0, rx=0))
    f.append(text(W / 2, sub_y + 19, "Деталізація структури Payload для MSG_ID = 0x20 (Sensor Telemetry Vector)", 12, BG, "middle", bold=True))

    payload_cols = [
        ("Зміщення", 80),
        ("Назва поля", 150),
        ("Тип (Wire Type)", 120),
        ("Одиниці", 90),
        ("Масштаб (Scale)", 130),
        ("Діапазон / Опис", 290)
    ]

    # Table Header
    th_y = sub_y + 48
    cx = 55
    for cname, cw in payload_cols:
        f.append(text(cx + 4, th_y, cname, 10.5, INK, "start", bold=True))
        cx += cw
    f.append(line(55, th_y + 6, W - 55, th_y + 6, color="#bdc3c7", sw=1))

    # Table Rows
    payload_rows = [
        ("+0 (2B)", "temp_raw", "int16_le", "°C", "scale = 0.01", "-40.00 .. +125.00 °C (цілочисельний код)"),
        ("+2 (2B)", "pressure_hpa", "uint16_le", "hPa", "scale = 0.1", "300.0 .. 1100.0 hPa (зміщення +3000)"),
        ("+4 (2B)", "voltage_mv", "uint16_le", "mV", "scale = 1.0 (raw)", "0 .. 5000 mV (напруга живлення)"),
        ("+6 (1B)", "flags_state", "uint8_t", "bits", "bitmask", "bit[0]: Fan_On, bit[1]: Warning, bit[2]: Alert"),
        ("+7 (1B)", "reserved", "uint8_t", "-", "fixed 0x00", "Вирівнювання розміру до 8 байтів (Padding)")
    ]

    for idx, (offset_s, fname_s, type_s, unit_s, scale_s, desc_s) in enumerate(payload_rows):
        ry = th_y + 24 + idx * 20
        rcx = 55
        f.append(text(rcx + 4, ry, offset_s, 10, MUTED, "start"))
        rcx += 80
        f.append(text(rcx + 4, ry, fname_s, 10, INK, "start", bold=True))
        rcx += 150
        f.append(text(rcx + 4, ry, type_s, 10, NEG, "start"))
        rcx += 120
        f.append(text(rcx + 4, ry, unit_s, 10, INK, "start"))
        rcx += 90
        f.append(text(rcx + 4, ry, scale_s, 10, FIELD, "start"))
        rcx += 130
        f.append(text(rcx + 4, ry, desc_s, 9.5, MUTED, "start"))

    # Bottom Notes
    note_y = 360
    f.append(rect(45, note_y, (W - 100) / 2, 110, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    f.append(text(55, note_y + 22, "⚠️ Пастки, які зобов'язана фіксувати специфікація:", 11, POS, "start", bold=True))
    f.append(text(55, note_y + 44, "• Неявне вирівнювання (Compiler Padding): заборонено сире накладання struct.", 9.5, INK, "start"))
    f.append(text(55, note_y + 64, "• Порядок байтів (Endianness): Little-Endian для ARM Cortex-M та x86-64.", 9.5, INK, "start"))
    f.append(text(55, note_y + 84, "• Знаковість (Sign Extension): різниця між int16_t та uint16_t при парсингу.", 9.5, INK, "start"))

    f.append(rect(45 + (W - 100) / 2 + 10, note_y, (W - 100) / 2, 110, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(55 + (W - 100) / 2 + 10, note_y + 22, "✓ Правила побудови еталонного опису полів:", 11, FIELD, "start", bold=True))
    f.append(text(55 + (W - 100) / 2 + 10, note_y + 44, "1. Фіксовані бінарні зміщення (Byte Offset) для кожного поля.", 9.5, INK, "start"))
    f.append(text(55 + (W - 100) / 2 + 10, note_y + 64, "2. Чіткі формули інженерного масштабування: Value = Raw * Scale + Offset.", 9.5, INK, "start"))
    f.append(text(55 + (W - 100) / 2 + 10, note_y + 84, "3. Резервні байти (Reserved) для вирівнювання з обов'язковим нульовим значенням.", 9.5, INK, "start"))

    render(os.path.join(IMG, "binary-frame-specification-anatomy.svg"), W, H, *f)


def fig_exchange_sequence_and_error_matrix():
    W, H = 1000, 520
    f = []
    f.append(text(W / 2, 28, "Діаграма послідовностей обміну, таймаути та матриця помилок", 16, INK, "middle", bold=True))
    f.append(text(W / 2, 50, "Штатний сценарій, відновлення після помилки CRC, реакція на таймаут та ієрархія кодів помилок", 12, MUTED, "middle", italic=True))

    # Left Side: Sequence Diagram (Width = 540)
    seq_w = 540
    f.append(rect(25, 75, seq_w, 420, fill="#ffffff", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(25 + seq_w / 2, 98, "UML Діаграма послідовності обміну (Sequence)", 13, INK, "middle", bold=True))

    # Lifelines: Host (Client) and MCU (Node)
    h_x = 110
    m_x = 450
    f.append(rect(h_x - 50, 115, 100, 28, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    f.append(text(h_x, 133, "Host (Клієнт)", 11, NEG, "middle", bold=True))
    f.append(line(h_x, 143, h_x, 475, color="#7f8c8d", sw=1.2, dash="4,4"))

    f.append(rect(m_x - 55, 115, 110, 28, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(m_x, 133, "MCU (Пристрій)", 11, FIELD, "middle", bold=True))
    f.append(line(m_x, 143, m_x, 475, color="#7f8c8d", sw=1.2, dash="4,4"))

    # Sequence 1: Happy Path
    f.append(text(25 + seq_w / 2, 160, "1. Успішний запит (Happy Path)", 10, MUTED, "middle", italic=True))
    f.append(arrow(h_x, 175, m_x, 175, color=LINE, sw=1.5))
    f.append(text((h_x + m_x) / 2, 170, "REQ [Seq=1, CMD_SET_CONFIG]", 9.5, INK, "middle"))
    f.append(arrow(m_x, 200, h_x, 200, color=FIELD, sw=1.5))
    f.append(text((h_x + m_x) / 2, 195, "RESP [Seq=1, STATUS_OK, Data]", 9.5, FIELD, "middle"))

    # Sequence 2: Corrupted CRC & NACK
    f.append(text(25 + seq_w / 2, 230, "2. Помилка CRC у каналі зв'язку", 10, POS, "middle", italic=True))
    f.append(arrow(h_x, 245, m_x, 245, color=POS, sw=1.5))
    f.append(text((h_x + m_x) / 2, 240, "REQ [Seq=2, CMD_CALIBRATE] (Спотворений CRC)", 9.5, POS, "middle"))
    f.append(arrow(m_x, 275, h_x, 275, color=POS, sw=1.5))
    f.append(text((h_x + m_x) / 2, 270, "NACK [Seq=2, ERR_INVALID_CRC]", 9.5, POS, "middle"))
    f.append(arrow(h_x, 305, m_x, 305, color=LINE, sw=1.5))
    f.append(text((h_x + m_x) / 2, 300, "RETRY 1 [Seq=3, CMD_CALIBRATE]", 9.5, INK, "middle"))
    f.append(arrow(m_x, 325, h_x, 325, color=FIELD, sw=1.5))
    f.append(text((h_x + m_x) / 2, 320, "RESP [Seq=3, STATUS_OK]", 9.5, FIELD, "middle"))

    # Sequence 3: Timeout & Exponential Backoff
    f.append(text(25 + seq_w / 2, 355, "3. Таймаут відповіді (MCU зайнятий / втрата кадру)", 10, "#d35400", "middle", italic=True))
    f.append(arrow(h_x, 370, m_x, 370, color=LINE, sw=1.5))
    f.append(text((h_x + m_x) / 2, 365, "REQ [Seq=4, CMD_FLASH_ERASE]", 9.5, INK, "middle"))

    # Timeout marker bracket
    f.append(line(h_x - 15, 370, h_x - 15, 420, color="#d35400", sw=1.5))
    f.append(line(h_x - 20, 370, h_x - 10, 370, color="#d35400", sw=1.5))
    f.append(line(h_x - 20, 420, h_x - 10, 420, color="#d35400", sw=1.5))
    f.append(text(h_x - 25, 398, "T_resp_max = 50 ms", 9.5, "#d35400", "end", italic=True))

    f.append(arrow(h_x, 430, m_x, 430, color="#d35400", sw=1.5))
    f.append(text((h_x + m_x) / 2, 425, "RETRY 1 [Seq=4, Backoff=100ms]", 9.5, "#d35400", "middle"))
    f.append(arrow(m_x, 455, h_x, 455, color=FIELD, sw=1.5))
    f.append(text((h_x + m_x) / 2, 450, "RESP [Seq=4, STATUS_OK]", 9.5, FIELD, "middle"))

    # Right Side: Error Code Matrix (Width = 390)
    mat_x = 585
    mat_w = 390
    f.append(rect(mat_x, 75, mat_w, 420, fill="#f8f9fa", stroke="#bdc3c7", sw=1.5, rx=8))
    f.append(text(mat_x + mat_w / 2, 98, "Матриця кодів результату (Status Matrix)", 13, INK, "middle", bold=True))

    err_categories = [
        ("0x00..0x0F: Успіх та системні статуси", [
            ("0x00 STATUS_OK", "Операція виконана успішно"),
            ("0x01 STATUS_ACCEPTED", "Прийнято до виконання (асинхронно)")
        ], "#eafaf1", FIELD),
        ("0x10..0x2F: Транспортні помилки каналу", [
            ("0x10 ERR_INVALID_CRC", "Помилка контрольної суми CRC"),
            ("0x11 ERR_FRAME_FORMAT", "Порушено межі кадру (SOF/EOF/Len)"),
            ("0x12 ERR_TIMEOUT", "Таймаут відповіді апаратного вузла")
        ], "#fdecea", POS),
        ("0x30..0x4F: Синтаксичні та семантичні помилки", [
            ("0x30 ERR_UNKNOWN_MSG_ID", "Невідомий тип повідомлення"),
            ("0x31 ERR_INVALID_PAYLOAD_LEN", "Невідповідна довжина Payload"),
            ("0x32 ERR_PARAM_OUT_OF_RANGE", "Значення параметра поза межами")
        ], "#fff3cd", "#d35400"),
        ("0x50..0x6F: Стан пристрою та апаратні помилки", [
            ("0x50 ERR_DEVICE_BUSY", "Ресурс зайнятий (Flash, I2C DMA)"),
            ("0x51 ERR_HARDWARE_FAULT", "Апаратний збій давача або реле"),
            ("0x52 ERR_UNAUTHORIZED", "Заборонено поточним рівнем доступу")
        ], "#f3e8fd", "#7d3c98")
    ]

    curr_ey = 118
    for cat_title, err_items, cat_fill, cat_strk in err_categories:
        cat_h = 24 + len(err_items) * 19
        f.append(rect(mat_x + 10, curr_ey, mat_w - 20, cat_h, fill=cat_fill, stroke=cat_strk, sw=1.2, rx=5))
        f.append(text(mat_x + 18, curr_ey + 16, cat_title, 10, cat_strk, "start", bold=True))
        for k, (code_name, code_desc) in enumerate(err_items):
            iy = curr_ey + 33 + k * 19
            f.append(text(mat_x + 22, iy, code_name, 9.5, INK, "start", bold=True))
            f.append(text(mat_x + 165, iy, "— " + code_desc, 9.5, MUTED, "start"))
        curr_ey += cat_h + 8

    render(os.path.join(IMG, "exchange-sequence-and-error-matrix.svg"), W, H, *f)


if __name__ == "__main__":
    fig_spec_architecture_pipeline()
    fig_binary_frame_specification_anatomy()
    fig_exchange_sequence_and_error_matrix()
    print("[OK] Generated 3 figures in", IMG)
