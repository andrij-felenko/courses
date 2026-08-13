# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Topo: Modbus Master/Slave (Client/Server) over RS-485 ──────────────────
def fig_architecture():
    W, H = 820, 360
    p = []
    
    # Bus line
    bus_y = 170
    p.append(line(80, bus_y - 8, 740, bus_y - 8, color=NEG, sw=2.2))
    p.append(line(80, bus_y + 8, 740, bus_y + 8, color=FIELD, sw=2.2))
    p.append(text(410, bus_y - 18, "Диференційна пара RS-485 (Data+ / Data-)", size=11, color=MUTED, bold=True))
    
    # Termination resistors
    p.append(rect(50, bus_y - 18, 25, 36, fill="#fff3cd", stroke="#856404", sw=1.5, rx=3))
    p.append(text(62, bus_y + 4, "120Ω", size=9.5, color="#856404", bold=True))
    p.append(rect(745, bus_y - 18, 25, 36, fill="#fff3cd", stroke="#856404", sw=1.5, rx=3))
    p.append(text(757, bus_y + 4, "120Ω", size=9.5, color="#856404", bold=True))
    
    # Master node (Client)
    mx, my = 120, 40
    p.append(rect(mx, my, 160, 80, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text(mx + 80, my + 30, "Modbus Master", size=13, color=NEG, bold=True))
    p.append(text(mx + 80, my + 52, "(Клієнт / ПЛК / ПK)", size=10.5, color=MUTED))
    
    # Master tap line
    p.append(line(mx + 80, my + 80, mx + 80, bus_y - 8, color=INK, sw=1.8))
    p.append(circle(mx + 80, bus_y - 8, 4, fill=NEG, stroke=NEG))
    p.append(circle(mx + 80, bus_y + 8, 4, fill=FIELD, stroke=FIELD))
    
    # Request/Response arrows
    p.append(arrow(300, 70, 440, 70, color=NEG, sw=1.8))
    p.append(text(370, 58, "Запит (Запит даних)", size=10.5, color=NEG, bold=True))
    
    p.append(arrow(440, 100, 300, 100, color=FIELD, sw=1.8))
    p.append(text(370, 114, "Відповідь (Дані або Виняток)", size=10.5, color=FIELD, bold=True))
    
    # Slave nodes (Servers)
    slaves = [
        ("Slave 1 (ID=1)", "Датчик тиску", 340),
        ("Slave 2 (ID=2)", "Частотний перетворювач", 520),
        ("Slave N (ID=N)", "Лічильник енергії", 680),
    ]
    
    sy = 230
    for title, desc, sx in slaves:
        p.append(rect(sx - 70, sy, 140, 80, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
        p.append(text(sx, sy + 30, title, size=12, color=FIELD, bold=True))
        p.append(text(sx, sy + 52, desc, size=10, color=MUTED))
        
        # Tap connection
        p.append(line(sx, bus_y + 8, sx, sy, color=INK, sw=1.8))
        p.append(circle(sx, bus_y - 8, 4, fill=NEG, stroke=NEG))
        p.append(circle(sx, bus_y + 8, 4, fill=FIELD, stroke=FIELD))
        
    box, _, _ = textbox(W / 2, 335,
                        "Топологія шини: один Майстер ініціює всі транзакції. Слейви відповідають лише на виклик.",
                        size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, sw=1.4, min_w=740)
    p.append(box)

    render(os.path.join(OUT, "modbus-architecture.svg"), W, H, *p,
           title="Архітектура Modbus: один Master і багато Slave-пристроїв на шині RS-485")


# ── 2. Modbus 4 Memory Tables ──────────────────────────────────────────────────
def fig_data_model():
    W, H = 820, 380
    p = []
    
    tables = [
        ("Discrete Inputs", "0x02 Read-Only", "1 біт (Прапорець)", "10001+ (PDU: 0x0000+)", "Стан кінцевика, реле, кнопка", "#eaf0fd", NEG),
        ("Coils (Котушки)", "0x01, 0x05, 0x0F R/W", "1 біт (Прапорець)", "00001+ (PDU: 0x0000+)", "Увімкнення контактора, LED", "#fdecea", POS),
        ("Input Registers", "0x04 Read-Only", "16 біт (Слово)", "30001+ (PDU: 0x0000+)", "Аналоговий вимір, температура", "#eef6ef", FIELD),
        ("Holding Registers", "0x03, 0x06, 0x10 R/W", "16 біт (Слово)", "40001+ (PDU: 0x0000+)", "Уставка температури, конфігурація", "#fff3cd", "#856404"),
    ]
    
    card_w = 175
    gap = 20
    start_x = 25
    card_h = 240
    y = 50
    
    for i, (name, access, width, addr, example, bg_col, border_col) in enumerate(tables):
        x = start_x + i * (card_w + gap)
        p.append(rect(x, y, card_w, card_h, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        
        p.append(text(x + card_w / 2, y + 25, name, size=12, color=border_col, bold=True))
        p.append(line(x + 10, y + 38, x + card_w - 10, y + 38, color=border_col, sw=1.2, dash="2 2"))
        
        p.append(text(x + 15, y + 60, "Доступ:", size=10, color=MUTED, anchor="start"))
        p.append(text(x + 15, y + 78, access, size=10.5, color=INK, anchor="start", bold=True))
        
        p.append(text(x + 15, y + 105, "Розмірність:", size=10, color=MUTED, anchor="start"))
        p.append(text(x + 15, y + 123, width, size=10.5, color=INK, anchor="start", bold=True))
        
        p.append(text(x + 15, y + 150, "Адресація Modicon:", size=10, color=MUTED, anchor="start"))
        p.append(text(x + 15, y + 168, addr, size=9.5, color=border_col, anchor="start", bold=True))
        
        p.append(text(x + 15, y + 195, "Типовий ужиток:", size=10, color=MUTED, anchor="start"))
        p.append(fitbox(x + 10, y + 203, card_w - 20, 30, example, size=9.5, fill="none", stroke="none", color=INK))

    box, _, _ = textbox(W / 2, 335,
                        "Модель даних Modbus: 4 таблиці розрізняють тип даних (біт/16-біт слово) та рівень доступу (R/O чи R/W).",
                        size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, sw=1.4, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "modbus-data-model.svg"), W, H, *p,
           title="Чотири стандартні таблиці пам'яті Modbus")


# ── 3. PDU and ADU Frame Envelopes (RTU, ASCII, TCP) ───────────────────────────
def fig_adu_pdu():
    W, H = 820, 370
    p = []
    
    y0 = 45
    h_row = 65
    
    # --- PDU ---
    p.append(text(50, y0 + 32, "PDU", size=13, color=NEG, bold=True, anchor="start"))
    p.append(rect(140, y0, 200, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=5))
    p.append(text(240, y0 + 30, "Function Code (1 B)", size=11, color=NEG, bold=True))
    p.append(rect(345, y0, 320, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=5))
    p.append(text(505, y0 + 30, "Data (0..252 Bytes)", size=11, color=NEG, bold=True))
    
    # Bracket showing PDU
    p.append(line(140, y0 + 56, 665, y0 + 56, color=NEG, sw=1.5, dash="4 3"))
    
    # --- Modbus RTU ADU ---
    y1 = y0 + h_row + 20
    p.append(text(50, y1 + 32, "RTU ADU", size=13, color=FIELD, bold=True, anchor="start"))
    p.append(rect(140, y1, 100, 50, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=5))
    p.append(text(190, y1 + 30, "Slave Addr", size=10.5, color=FIELD, bold=True))
    p.append(rect(245, y1, 420, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=5))
    p.append(text(455, y1 + 30, "PDU (Function Code + Data)", size=11, color=NEG, bold=True))
    p.append(rect(670, y1, 110, 50, fill="#fff3cd", stroke="#856404", sw=1.8, rx=5))
    p.append(text(725, y1 + 30, "CRC-16 (2 B)", size=10.5, color="#856404", bold=True))
    
    # --- Modbus TCP ADU ---
    y2 = y1 + h_row + 15
    p.append(text(50, y2 + 32, "TCP ADU", size=13, color=POS, bold=True, anchor="start"))
    # MBAP Header
    p.append(rect(140, y2, 230, 50, fill="#fdecea", stroke=POS, sw=1.8, rx=5))
    p.append(text(255, y2 + 22, "MBAP Header (7 B)", size=11, color=POS, bold=True))
    p.append(text(255, y2 + 38, "[TxID:2, ProtoID:2, Len:2, UnitID:1]", size=9.5, color=POS))
    # PDU
    p.append(rect(375, y2, 405, 50, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=5))
    p.append(text(577, y2 + 30, "PDU (Function Code + Data)", size=11, color=NEG, bold=True))
    
    box, _, _ = textbox(W / 2, 335,
                        "PDU — єдине для всіх транспортів. ADU додає адресу/CRC у RTU або MBAP-заголовок у TCP.",
                        size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, sw=1.4, min_w=750)
    p.append(box)

    render(os.path.join(OUT, "modbus-adu-pdu.svg"), W, H, *p,
           title="Структура PDU і транспортування в кадрах ADU (RTU vs TCP)")


# ── 4. Modbus RTU Silent Interval Timing (t3.5 and t1.5) ──────────────────────
def fig_rtu_timing():
    W, H = 820, 350
    p = []
    
    axis_y = 160
    p.append(arrow(60, axis_y, 760, axis_y, color=INK, sw=1.8))
    p.append(text(770, axis_y + 4, "час", size=11, color=MUTED, italic=True, anchor="start"))
    
    # Frame 1
    p.append(rect(80, axis_y - 50, 200, 45, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    p.append(text(180, axis_y - 23, "Кадр Modbus RTU №1", size=11, color=NEG, bold=True))
    
    # Inter-frame silence t3.5
    p.append(rect(280, axis_y - 50, 180, 45, fill="#fff3cd", stroke="#856404", sw=1.5, rx=4))
    p.append(text(370, axis_y - 30, "Тиша ≥ 3.5 символи (t3.5)", size=10.5, color="#856404", bold=True))
    p.append(text(370, axis_y - 12, "Маркер межі кадру", size=9.5, color=MUTED))
    
    # Frame 2 with internal character gap
    p.append(rect(460, axis_y - 50, 90, 45, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(505, axis_y - 23, "Байт 1..K", size=10, color=FIELD, bold=True))
    
    p.append(rect(550, axis_y - 50, 50, 45, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text(575, axis_y - 30, "t1.5", size=10, color=POS, bold=True))
    p.append(text(575, axis_y - 12, "< 1.5", size=9.5, color=POS))
    
    p.append(rect(600, axis_y - 50, 120, 45, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=4))
    p.append(text(660, axis_y - 23, "Байт K+1..N", size=10, color=FIELD, bold=True))
    
    # Detail calls below
    p.append(line(370, axis_y, 370, axis_y + 40, color="#856404", sw=1.4, dash="3 3"))
    p.append(text(370, axis_y + 55, "t3.5 = 3.5 × (11 біт / бод)", size=11, color="#856404", bold=True))
    p.append(text(370, axis_y + 72, "На 9600 бод ≈ 4.01 мс; при > 19200 бод зафіксовано 1.75 мс", size=9.5, color=MUTED))
    
    p.append(line(575, axis_y, 575, axis_y + 40, color=POS, sw=1.4, dash="3 3"))
    p.append(text(575, axis_y + 55, "Пауза > t1.5 всередині кадру — помилка!", size=10.5, color=POS, bold=True))
    
    box, _, _ = textbox(W / 2, 315,
                        "Маркування кадрів у Modbus RTU здійснюється часовими інтервалами тиші (без стартового/стопового байта).",
                        size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, sw=1.4, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "modbus-rtu-timing.svg"), W, H, *p,
           title="Часові інтервали Modbus RTU: t3.5 (розділювач кадрів) та t1.5 (межа між байтами)")


# ── 5. Modbus Exception Response Frame Format ─────────────────────────────────
def fig_exception_frame():
    W, H = 820, 320
    p = []
    
    y = 50
    # Normal request
    p.append(text(40, y + 25, "Запит:", size=12, color=INK, bold=True, anchor="start"))
    p.append(rect(130, y, 90, 42, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(175, y + 25, "Addr (0x01)", size=10, color=FIELD, bold=True))
    
    p.append(rect(225, y, 110, 42, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
    p.append(text(280, y + 25, "FC (0x03)", size=10.5, color=NEG, bold=True))
    
    p.append(rect(340, y, 220, 42, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
    p.append(text(450, y + 25, "Start Addr & Reg Count", size=10, color=NEG))
    
    p.append(rect(565, y, 100, 42, fill="#fff3cd", stroke="#856404", sw=1.6, rx=4))
    p.append(text(615, y + 25, "CRC-16", size=10, color="#856404"))
    
    # Exception response
    y2 = y + 75
    p.append(text(40, y2 + 25, "Відповідь-виняток:", size=12, color=POS, bold=True, anchor="start"))
    p.append(rect(130, y2, 90, 42, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=4))
    p.append(text(175, y2 + 25, "Addr (0x01)", size=10, color=FIELD, bold=True))
    
    p.append(rect(225, y2, 170, 42, fill="#fdecea", stroke=POS, sw=2, rx=4))
    p.append(text(310, y2 + 25, "FC | 0x80 (0x83)", size=11, color=POS, bold=True))
    
    p.append(rect(400, y2, 160, 42, fill="#fdecea", stroke=POS, sw=2, rx=4))
    p.append(text(480, y2 + 25, "Exception Code (0x02)", size=10.5, color=POS, bold=True))
    
    p.append(rect(565, y2, 100, 42, fill="#fff3cd", stroke="#856404", sw=1.6, rx=4))
    p.append(text(615, y2 + 25, "CRC-16", size=10, color="#856404"))
    
    # Callout for FC | 0x80
    p.append(line(310, y2 + 42, 310, y2 + 80, color=POS, sw=1.4, dash="3 3"))
    p.append(text(310, y2 + 95, "Старший біт (0x80) сигналізує про помилку (0x03 + 0x80 = 0x83)", size=10.5, color=POS, bold=True))
    
    box, _, _ = textbox(W / 2, 280,
                        "Кадр винятку: код функції повертається з виставленим бітом 0x80, а корисне навантаження містить 1 байт коду помилки.",
                        size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, sw=1.4, min_w=760)
    p.append(box)

    render(os.path.join(OUT, "modbus-exception-frame.svg"), W, H, *p,
           title="Формат кадру відповіді з помилкою (Modbus Exception Response)")


if __name__ == "__main__":
    fig_architecture()
    fig_data_model()
    fig_adu_pdu()
    fig_rtu_timing()
    fig_exception_frame()
    print("OK: 5 figures written to", OUT)
