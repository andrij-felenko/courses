# -*- coding: utf-8 -*-
"""Фігури для статті pershyi-radiokanal-na-dvokh-platakh («Перший радіоканал на двох платах»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. nrf24-pinout-wiring: схема з'єднання МК і радіомодуля з конденсатором ──
def fig_pinout_wiring():
    W, H = 840, 440
    p = []

    # Тло
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Блок 1: Мікроконтролер (MCU)
    mcu_x, mcu_y, mcu_w, mcu_h = 40, 50, 200, 340
    p.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 28, "Мікроконтролер (МК)", size=13, color=INK, bold=True))
    p.append(text(mcu_x + mcu_w / 2, mcu_y + 46, "STM32 / ESP32 / AVR", size=11, color=MUTED))

    # Виводи МК
    mcu_pins = [
        ("3.3V (VCC)", POS, 90),
        ("GND", NEG, 130),
        ("SCK (SPI CLK)", "#2563eb", 170),
        ("MOSI (SPI TX)", "#2563eb", 210),
        ("MISO (SPI RX)", "#2563eb", 250),
        ("CSN (SPI CS#)", "#7c3aed", 290),
        ("CE (Tx/Rx EN)", FIELD, 330),
        ("IRQ (Ext Interrupt)", "#d97706", 365),
    ]

    for name, col, py in mcu_pins:
        p.append(text(mcu_x + mcu_w - 12, py + 4, name, size=11, color=col, bold=True, anchor="end"))
        p.append(circle(mcu_x + mcu_w, py, 3.5, fill=col, stroke=LINE, sw=1.0))

    # Блок 2: Радіомодуль nRF24L01+
    rf_x, rf_y, rf_w, rf_h = 580, 50, 220, 340
    p.append(rect(rf_x, rf_y, rf_w, rf_h, fill="#eff6ff", stroke="#1d4ed8", sw=1.8, rx=8))
    p.append(text(rf_x + rf_w / 2, rf_y + 28, "Модуль nRF24L01+", size=13, color="#1d4ed8", bold=True))
    p.append(text(rf_x + rf_w / 2, rf_y + 46, "2.4 GHz Transceiver", size=11, color=MUTED))

    # Виводи nRF24
    rf_pins = [
        ("VCC (1.9…3.6 В)", POS, 90),
        ("GND", NEG, 130),
        ("SCK", "#2563eb", 170),
        ("MOSI", "#2563eb", 210),
        ("MISO", "#2563eb", 250),
        ("CSN", "#7c3aed", 290),
        ("CE", FIELD, 330),
        ("IRQ", "#d97706", 365),
    ]

    for name, col, py in rf_pins:
        p.append(text(rf_x + 12, py + 4, name, size=11, color=col, bold=True, anchor="start"))
        p.append(circle(rf_x, py, 3.5, fill=col, stroke=LINE, sw=1.0))

    # З'єднувальні лінії
    wire_lines = [
        (mcu_x + mcu_w, 90, rf_x, 90, POS, 1.8),
        (mcu_x + mcu_w, 130, rf_x, 130, NEG, 1.8),
        (mcu_x + mcu_w, 170, rf_x, 170, "#2563eb", 1.4),
        (mcu_x + mcu_w, 210, rf_x, 210, "#2563eb", 1.4),
        (mcu_x + mcu_w, 250, rf_x, 250, "#2563eb", 1.4),
        (mcu_x + mcu_w, 290, rf_x, 290, "#7c3aed", 1.4),
        (mcu_x + mcu_w, 330, rf_x, 330, FIELD, 1.4),
        (mcu_x + mcu_w, 365, rf_x, 365, "#d97706", 1.4),
    ]
    for x1, y1, x2, y2, col, sw in wire_lines:
        p.append(line(x1, y1, x2, y2, color=col, sw=sw))

    # Шунтувальний конденсатор прямо біля nRF24 VCC/GND
    cap_x = 510
    # Вузол VCC
    p.append(circle(cap_x, 90, 4.0, fill=POS, stroke=LINE, sw=1.0))
    p.append(line(cap_x, 90, cap_x, 96, color=POS, sw=1.6))
    # Вузол GND
    p.append(circle(cap_x, 130, 4.0, fill=NEG, stroke=LINE, sw=1.0))
    p.append(line(cap_x, 130, cap_x, 124, color=NEG, sw=1.6))

    # Рамка блоку конденсаторів
    b_cap, bw, bh = textbox(cap_x, 110, "10…47 мкФ + 100 нФ\nпрямо на ніжках!", size=10, bold=True,
                            fill="#fef3c7", stroke="#d97706", sw=1.4, color="#92400e")
    p.append(b_cap)

    # Пояснювальні плашки внизу і вгорі
    p.append(rect(260, 16, 310, 46, fill="#fef2f2", stroke=POS, sw=1.2, rx=4))
    p.append(text(415, 34, "УВАГА: VCC ТІЛЬКИ 3.3 В (НЕ 5 В!)", size=11, color=POS, bold=True))
    p.append(text(415, 52, "Сигнальні ніжки SCK, MOSI, CSN, CE толерантні до 5 В", size=10, color=MUTED))

    p.append(rect(250, 402, 340, 26, fill="#f0fdf4", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(420, 419, "Шина SPI (до 10 МГц, SPI Mode 0: CPOL=0, CPHA=0)", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "nrf24-pinout-wiring.svg"), W, H, *p,
           title="Схема підключення радіомодуля nRF24L01+ до мікроконтролера")


# ── 2. tx-burst-power-dip: осцилограма імпульсного просідання напруги живлення ──
def fig_power_dip():
    W, H = 780, 400
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    ox, oy = 90, 60
    gw, gh = 620, 110

    # ── Графік 1: Струм I_supply (верхня панель) ──
    p.append(rect(ox, oy, gw, gh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(ox - 15, oy + 20, "Струм I", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 15, oy + gh - 10, "0 мА", size=10, color=MUTED, anchor="end"))
    p.append(text(ox - 15, oy + 40, "15 мА (TX)", size=10, color=POS, bold=True, anchor="end"))

    # Базова лінія 0 мА
    base_i = oy + gh - 15
    p.append(line(ox, base_i, ox + gw, base_i, color="#94a3b8", sw=1.0, dash="3 3"))

    # Імпульс струму
    i_pts = [
        (ox, base_i),
        (ox + 120, base_i),
        (ox + 130, oy + 30),
        (ox + 430, oy + 30),
        (ox + 440, base_i),
        (ox + gw, base_i),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in i_pts), POS))
    p.append(text(ox + 280, oy + 22, "Імпульс передачі TX (стрибок за 130 мкс)", size=10, color=POS, bold=True))

    # ── Графік 2: Напруга VCC на модулі (нижня панель) ──
    oy2 = 215
    p.append(rect(ox, oy2, gw, gh, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=4))
    p.append(text(ox - 15, oy2 + 20, "Напруга V", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(ox - 15, oy2 + 35, "3.3 В", size=10, color=FIELD, bold=True, anchor="end"))
    p.append(text(ox - 15, oy2 + 75, "1.9 В", size=10, color=POS, bold=True, anchor="end"))
    p.append(text(ox - 15, oy2 + gh - 10, "0 В", size=10, color=MUTED, anchor="end"))

    # Рівні напруги
    v33 = oy2 + 30
    v19 = oy2 + 75  # Поріг скиду Brownout Reset
    p.append(line(ox, v33, ox + gw, v33, color="#94a3b8", sw=1.0, dash="3 3"))
    p.append(line(ox, v19, ox + gw, v19, color=POS, sw=1.2, dash="5 3"))
    p.append(text(ox + gw - 6, v19 - 6, "Поріг відмови трансивера (1.9 В)", size=10, color=POS, anchor="end", italic=True))

    # Крива 1 (Червона): БЕЗ конденсатора
    v_bad = [
        (ox, v33),
        (ox + 120, v33),
        (ox + 135, oy2 + 95),
        (ox + 160, oy2 + 88),
        (ox + 430, oy2 + 88),
        (ox + 445, v33 - 5),
        (ox + 460, v33),
        (ox + gw, v33),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6 3"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in v_bad), POS))

    # Крива 2 (Зелена): З танталовим/керамічним конденсатором 22 мкФ
    v_good = [
        (ox, v33),
        (ox + 120, v33),
        (ox + 140, v33 + 8),
        (ox + 430, v33 + 8),
        (ox + 450, v33),
        (ox + gw, v33),
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' %
             (" ".join("%.1f,%.1f" % pt for pt in v_good), FIELD))

    # Пояснення до ліній
    p.append(text(ox + 350, oy2 + 98, "БЕЗ конденсатора: VCC провалюється &lt; 1.9 В → перезавантаження модуля!", size=10, color=POS, bold=True))
    p.append(text(ox + 350, v33 - 10, "З конденсатором 22 мкФ: VCC стабільне (3.22 В)", size=10, color=FIELD, bold=True))

    # Вісь часу
    p.append(arrow(ox, oy2 + gh + 15, ox + gw, oy2 + gh + 15, color=INK, sw=1.4))
    p.append(text(ox + gw / 2, oy2 + gh + 32, "Час t (мкс) — тривалість кадру 150…400 мкс", size=11, color=INK, italic=True))

    render(os.path.join(OUT, "tx-burst-power-dip.svg"), W, H, *p,
           title="Імпульсне просідання напруги живлення радіомодуля в момент увімкнення передавача")


# ── 3. multiceiver-pipes: архітектура логічних каналів (Pipes 0..5) ───────────
def fig_multiceiver_pipes():
    W, H = 840, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    tx_nodes = [
        (40, 40, "Вузол 0 (TX)", "0xE7E7E7E7E7", "#2563eb"),
        (40, 100, "Вузол 1 (TX)", "0xC2C2C2C2C2", "#059669"),
        (40, 160, "Вузол 2 (TX)", "0xC2C2C2C2C3", "#d97706"),
        (40, 220, "Вузол 3 (TX)", "0xC2C2C2C2C4", "#7c3aed"),
        (40, 280, "Вузол 4 (TX)", "0xC2C2C2C2C5", "#db2777"),
        (40, 340, "Вузол 5 (TX)", "0xC2C2C2C2C6", "#4b5563"),
    ]

    rx_box_x = 520
    for x, y, title, addr, col in tx_nodes:
        p.append(rect(x, y, 160, 44, fill="#f8fafc", stroke=col, sw=1.6, rx=6))
        p.append(text(x + 80, y + 18, title, size=11, color=col, bold=True))
        p.append(text(x + 80, y + 34, addr, size=10, color=MUTED))
        p.append(arrow(x + 165, y + 22, rx_box_x - 10, y + 22, color=col, sw=1.4))

    rx_w, rx_h = 280, 370
    p.append(rect(rx_box_x, 30, rx_w, rx_h, fill="#eff6ff", stroke="#1d4ed8", sw=2.0, rx=8))
    p.append(text(rx_box_x + rx_w / 2, 54, "Приймач-Концентратор (RX Hub)", size=13, color="#1d4ed8", bold=True))
    p.append(text(rx_box_x + rx_w / 2, 70, "Один радіочастотний тракт (2.4 ГГц)", size=10, color=MUTED))

    pipes = [
        ("Pipe 0", "0xE7E7E7E7E7 (повна 5-байтова)", "#2563eb", 92),
        ("Pipe 1", "0xC2C2C2C2C2 (базова 5-байтова)", "#059669", 148),
        ("Pipe 2", "0xC2C2C2C2[C3] (LSB байт)", "#d97706", 204),
        ("Pipe 3", "0xC2C2C2C2[C4] (LSB байт)", "#7c3aed", 260),
        ("Pipe 4", "0xC2C2C2C2[C5] (LSB байт)", "#db2777", 316),
        ("Pipe 5", "0xC2C2C2C2[C6] (LSB байт)", "#4b5563", 372),
    ]

    for pname, paddr, col, py in pipes:
        p.append(rect(rx_box_x + 15, py - 14, rx_w - 30, 42, fill=BG, stroke=col, sw=1.4, rx=4))
        p.append(text(rx_box_x + 28, py + 4, pname, size=11, color=col, bold=True, anchor="start"))
        p.append(text(rx_box_x + 28, py + 20, paddr, size=9, color=INK, anchor="start"))

    p.append(rect(220, 20, 270, 370, fill="#fefce8", stroke="#ca8a04", sw=1.2, rx=6))
    p.append(text(355, 45, "Правило адресації Multiceiver:", size=11, color="#854d0e", bold=True))
    lines_rule = [
        "1. Pipe 0 та Pipe 1 мають",
        "   повні унікальні 5-байтові",
        "   адреси.",
        "2. Pipe 2…5 ділять 4 старші",
        "   байти адреси (MSB) з Pipe 1,",
        "   і відрізняються лише 1",
        "   молодшим байтом (LSB).",
        "3. Передавач TX перемикається",
        "   на Pipe 0 для прийому ACK.",
    ]
    for i, l in enumerate(lines_rule):
        p.append(text(235, 75 + i * 22, l, size=10, color="#713f12", anchor="start"))

    render(os.path.join(OUT, "multiceiver-pipes.svg"), W, H, *p,
           title="Архітектура логічних каналів Multiceiver (Pipes 0..5) у nRF24L01+")


# ── 4. packet-structure-autoack: структура кадру в ефірі та Auto-ACK ──────────
def fig_packet_autoack():
    W, H = 840, 440
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Структура радіопакета Enhanced ShockBurst (ESB) в ефірі", size=13, color=INK, bold=True))

    fields = [
        (40, "Преамбула", "1 байт (0xAA / 0x55)", 110, "#e0e7ff", "#3730a3"),
        (155, "Адреса (Sync Word)", "3…5 байтів", 155, "#dbeafe", "#1e40af"),
        (315, "Packet Control", "9 бітів (Len, PID, NO_ACK)", 175, "#fef3c7", "#92400e"),
        (495, "Корисне навантаження (Payload)", "0…32 байти (Dynamic Payload)", 200, "#dcfce7", "#166534"),
        (700, "CRC", "1 або 2 байти", 100, "#fee2e2", "#991b1b"),
    ]

    fy = 48
    fh = 52
    for fx, ftitle, fdesc, fw, fbg, fcol in fields:
        p.append(rect(fx, fy, fw, fh, fill=fbg, stroke=fcol, sw=1.5, rx=4))
        p.append(text(fx + fw / 2, fy + 22, ftitle, size=11, color=fcol, bold=True))
        p.append(text(fx + fw / 2, fy + 40, fdesc, size=9, color=fcol))

    pcf_y = 122
    p.append(rect(230, pcf_y, 350, 48, fill="#fffbeb", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(405, pcf_y + 18, "Packet Control Field: 9 бітів", size=11, color="#92400e", bold=True))
    p.append(text(405, pcf_y + 36, "Payload Length (6 біт)  |  PID (2 біти)  |  NO_ACK (1 біт)", size=10, color="#b45309"))
    p.append(arrow(405, pcf_y, 405, fy + fh + 2, color="#d97706", sw=1.2))

    p.append(line(40, 195, W - 40, 195, color="#cbd5e1", sw=1.0))
    p.append(text(W / 2, 215, "Хронологія апаратного підтвердження (Auto-ACK / ARQ)", size=13, color=INK, bold=True))

    tx_line_y = 265
    rx_line_y = 350

    p.append(text(80, tx_line_y - 12, "Передавач (TX Node)", size=11, color=POS, bold=True))
    p.append(line(80, tx_line_y, W - 60, tx_line_y, color=POS, sw=1.8))

    p.append(text(80, rx_line_y + 24, "Приймач (RX Node)", size=11, color=NEG, bold=True))
    p.append(line(80, rx_line_y, W - 60, rx_line_y, color=NEG, sw=1.8))

    p.append(rect(180, tx_line_y - 14, 150, 28, fill="#fee2e2", stroke=POS, sw=1.4, rx=4))
    p.append(text(255, tx_line_y + 4, "Пакет даних (Data)", size=10, color=POS, bold=True))

    p.append(arrow(255, tx_line_y + 16, 310, rx_line_y - 2, color=POS, sw=1.6))

    p.append(rect(310, rx_line_y - 14, 110, 28, fill="#dbeafe", stroke=NEG, sw=1.4, rx=4))
    p.append(text(365, rx_line_y + 4, "Перевірка CRC", size=10, color=NEG, bold=True))

    p.append(rect(430, rx_line_y - 14, 120, 28, fill="#dcfce7", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(490, rx_line_y + 4, "ACK відповідь", size=10, color=FIELD, bold=True))

    p.append(arrow(490, rx_line_y - 16, 550, tx_line_y + 2, color=FIELD, sw=1.6))

    p.append(rect(550, tx_line_y - 14, 180, 28, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(640, tx_line_y + 4, "IRQ: TX_DS (успішна доставка)", size=10, color=FIELD, bold=True))

    p.append(line(180, tx_line_y - 22, 550, tx_line_y - 22, color="#94a3b8", sw=1.0, dash="3 3"))
    p.append(text(365, tx_line_y - 26, "Вікно очікування Auto Retransmit Delay (ARD: 250…4000 мкс)", size=10, color=MUTED, bold=True))

    p.append(text(W / 2, 415, "Якщо ACK не надійшов до кінця ARD — модуль робить повтор (до ARC спроб)", size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "packet-structure-autoack.svg"), W, H, *p,
           title="Структура радіопакета в ефірі та часова шкала апаратного підтвердження Auto-ACK")


# ── 5. rtt-fsm-timeline: вимірювання затримки кругового обігу (RTT) ───────────
def fig_rtt_timeline():
    W, H = 840, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Структура кругової затримки Round-Trip Time (RTT)", size=13, color=INK, bold=True))

    ox = 50
    oy = 85
    bar_w = 740
    bar_h = 56

    p.append(text(ox, oy - 12, "t0: Старт передачі (МК TX)", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(ox + bar_w, oy - 12, "t1: Отримання ACK (IRQ TX_DS)", size=11, color=FIELD, bold=True, anchor="end"))

    # Сегменти RTT
    segs = [
        ("1. SPI Write", "32 B @ 8 МГц\n≈ 32 мкс", 105, "#dbeafe", "#1e40af"),
        ("2. TX Settle", "PLL Lock\n= 130 мкс", 115, "#fee2e2", "#b91c1c"),
        ("3. Air Data", "38 B @ 2 Мбіт/с\n≈ 152 мкс", 145, "#fef3c7", "#b45309"),
        ("4. RX Switch", "Demod & Switch\n≈ 130 мкс", 115, "#f3e8ff", "#6b21a8"),
        ("5. Air ACK", "ESB ACK кадр\n≈ 45 мкс", 100, "#dcfce7", "#15803d"),
        ("6. IRQ + Read", "SPI Read STATUS\n≈ 20 мкс", 160, "#e0e7ff", "#3730a3"),
    ]

    cur_x = ox
    for title, desc, sw, fbg, fcol in segs:
        p.append(rect(cur_x, oy, sw, bar_h, fill=fbg, stroke=fcol, sw=1.5, rx=3))
        lines = desc.split("\n")
        p.append(text(cur_x + sw / 2, oy + 18, title, size=10, color=fcol, bold=True))
        p.append(text(cur_x + sw / 2, oy + 33, lines[0], size=9, color=fcol))
        if len(lines) > 1:
            p.append(text(cur_x + sw / 2, oy + 46, lines[1], size=9, color=fcol))
        cur_x += sw

    p.append(line(ox, oy + bar_h + 16, ox + bar_w, oy + bar_h + 16, color=INK, sw=1.6))
    p.append(circle(ox, oy + bar_h + 16, 3.5, fill=INK, stroke=INK))
    p.append(circle(ox + bar_w, oy + bar_h + 16, 3.5, fill=INK, stroke=INK))

    p.append(text(ox + bar_w / 2, oy + bar_h + 38, "Повний RTT (2 Мбіт/с, 32 байти) = 32 + 130 + 152 + 130 + 45 + 20 ≈ 509 мкс",
                  size=12, color=INK, bold=True))

    ty = 230
    p.append(rect(ox + 30, ty, bar_w - 60, 150, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=6))
    p.append(text(W / 2, ty + 24, "Залежність типового RTT від швидкості радіотракту (для 32 байтів)", size=11, color=INK, bold=True))

    rows = [
        ("2 Мбіт/с", "152 мкс", "≈ 0.5…0.7 мс", "Мінімальна затримка, чутливість −82 dBm"),
        ("1 Мбіт/с", "304 мкс", "≈ 0.8…1.1 мс", "Баланс швидкості та дальності, чутливість −85 dBm"),
        ("250 кбіт/с", "1216 мкс", "≈ 2.8…3.5 мс", "Максимальна дальність зв'язку, чутливість −94 dBm"),
    ]

    for i, (rate, airt, rtt_val, note) in enumerate(rows):
        ry = ty + 54 + i * 30
        p.append(text(ox + 60, ry, rate, size=11, color="#1d4ed8", bold=True, anchor="start"))
        p.append(text(ox + 180, ry, "Час у ефірі: " + airt, size=10, color=MUTED, anchor="start"))
        p.append(text(ox + 360, ry, "RTT: " + rtt_val, size=10, color=POS, bold=True, anchor="start"))
        p.append(text(ox + 480, ry, note, size=9, color=INK, anchor="start"))

    render(os.path.join(OUT, "rtt-fsm-timeline.svg"), W, H, *p,
           title="Хронологічний розбір складових затримки кругового обігу пакета (RTT)")


if __name__ == "__main__":
    fig_pinout_wiring()
    fig_power_dip()
    fig_multiceiver_pipes()
    fig_packet_autoack()
    fig_rtt_timeline()
    print("Усі 5 фігур успішно згенеровано у ./img/")
