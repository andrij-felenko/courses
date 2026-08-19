# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN_COL = "#d9534f"
OK_COL   = "#27ae60"
BUS_COL  = "#2457d6"
WARN_BG  = "#fdecea"
OK_BG    = "#eef6ef"
ACCENT   = "#d97706"
PURPLE   = "#8e44ad"
CYAN     = "#0284c7"


def polyline(pts, color=LINE, sw=1.5, fill="none", dash=None):
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{points}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"{d}/>'


def fig_scl_open_drain_circuit():
    W, H = 840, 420
    p = []

    # Frame
    p.append(rect(15, 15, 810, 390, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    # Power rail (+3.3V VDD)
    p.append(line(45, 50, 795, 50, color=POS, sw=2.5))
    p.append(text(50, 40, "VDD (+3.3V)", size=11, color=POS, bold=True, anchor="start"))

    # Pull-up resistor Rp
    p.append(line(420, 50, 420, 72, color=POS, sw=1.8))
    p.append(rect(408, 72, 24, 36, fill="#fff7ed", stroke=ACCENT, sw=1.5, rx=2))
    p.append(text(440, 93, "Rp = 2.2 кОм", size=10, color=ACCENT, bold=True, anchor="start"))
    p.append(line(420, 108, 420, 135, color=ACCENT, sw=1.8))

    # SCL Bus Line
    p.append(line(45, 135, 795, 135, color=ACCENT, sw=2.5))
    p.append(rect(50, 115, 160, 20, fill="#fff7ed", stroke=ACCENT, sw=1, rx=3))
    p.append(text(130, 129, "Лінія SCL: 0.0 В (LOW)", size=10, color=ACCENT, bold=True))

    # Master Block (Left)
    p.append(rect(45, 165, 340, 220, fill=OK_BG, stroke=OK_COL, sw=1.8, rx=6))
    p.append(rect(45, 165, 340, 32, fill="#e2f3e5", stroke=OK_COL, sw=1.2, rx=6))
    p.append(text(215, 186, "Головний пристрій (I2C Master)", size=11.5, color=OK_COL, bold=True))

    # Master SCL Pin Connection on top edge
    p.append(line(90, 135, 90, 215, color=ACCENT, sw=1.8))
    p.append(circle(90, 135, 3.5, fill=ACCENT, stroke=ACCENT))
    p.append(circle(90, 215, 3.5, fill=ACCENT, stroke=ACCENT))
    p.append(text(105, 212, "SCL Pin", size=9.5, color=ACCENT, bold=True, anchor="start"))

    # Master Internal bus
    p.append(line(90, 215, 330, 215, color=ACCENT, sw=1.5))

    # Master MOSFET
    p.append(line(160, 215, 160, 245, color=ACCENT, sw=1.5))
    p.append(circle(160, 215, 3, fill=ACCENT, stroke=ACCENT))
    p.append(rect(120, 245, 80, 50, fill=BG, stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(160, 265, "MOSFET", size=10, color=OK_COL, bold=True))
    p.append(text(160, 282, "Hi-Z (Закритий)", size=9.5, color=OK_COL))
    p.append(line(160, 295, 160, 345, color=LINE, sw=1.5))
    p.append(line(160, 345, 160, 360, color=LINE, sw=1.5))
    p.append(line(148, 360, 172, 360, color=LINE, sw=2))

    # Master Input Buffer
    p.append(line(275, 215, 275, 245, color=ACCENT, sw=1.5))
    p.append(circle(275, 215, 3, fill=ACCENT, stroke=ACCENT))
    p.append(rect(235, 245, 80, 50, fill=BG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(275, 265, "Вхід SCL", size=10, color=NEG, bold=True))
    p.append(text(275, 282, "Рівень: 0 В", size=9.5, color=WARN_COL, bold=True))
    p.append(text(275, 325, "Очікує HIGH!", size=10, color=WARN_COL, bold=True))

    # Slave Block (Right)
    p.append(rect(455, 165, 340, 220, fill=WARN_BG, stroke=WARN_COL, sw=1.8, rx=6))
    p.append(rect(455, 165, 340, 32, fill="#fadbd8", stroke=WARN_COL, sw=1.2, rx=6))
    p.append(text(625, 186, "Ведений пристрій (I2C Slave)", size=11.5, color=WARN_COL, bold=True))

    # Slave SCL Pin Connection
    p.append(line(750, 135, 750, 215, color=ACCENT, sw=1.8))
    p.append(circle(750, 135, 3.5, fill=ACCENT, stroke=ACCENT))
    p.append(circle(750, 215, 3.5, fill=ACCENT, stroke=ACCENT))
    p.append(text(735, 212, "SCL Pin", size=9.5, color=ACCENT, bold=True, anchor="end"))

    # Slave Internal bus
    p.append(line(510, 215, 750, 215, color=ACCENT, sw=1.5))

    # Slave MOSFET (Active Pull-down)
    p.append(line(550, 215, 550, 245, color=ACCENT, sw=1.8))
    p.append(circle(550, 215, 3, fill=ACCENT, stroke=ACCENT))
    p.append(rect(510, 245, 80, 50, fill=BG, stroke=WARN_COL, sw=1.5, rx=4))
    p.append(text(550, 265, "MOSFET", size=10, color=WARN_COL, bold=True))
    p.append(text(550, 282, "ВІДКРИТИЙ (0В)", size=9.5, color=WARN_COL, bold=True))
    p.append(line(550, 295, 550, 345, color=WARN_COL, sw=1.8))
    p.append(line(550, 345, 550, 360, color=LINE, sw=1.5))
    p.append(line(538, 360, 562, 360, color=LINE, sw=2))

    # Slave Hardware Logic
    p.append(rect(615, 245, 155, 75, fill=BG, stroke=LINE, sw=1.2, rx=4))
    p.append(text(692, 265, "Апаратний контролер", size=10, color=INK, bold=True))
    p.append(text(692, 282, "Прапорець ADDR / RXNE", size=9.5, color=MUTED))
    p.append(text(692, 300, "Утримує затвор = 3.3В", size=9.5, color=WARN_COL, bold=True))
    p.append(line(615, 270, 590, 270, color=WARN_COL, sw=1.5, dash="3,2"))

    render(os.path.join(OUT, "scl-open-drain-circuit.svg"), W, H, *p)


def fig_slave_hardware_states():
    W, H = 840, 440
    p = []

    p.append(rect(15, 15, 810, 410, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 40, "Послідовність апаратних станів контролера I2C Slave при розтягуванні такту", size=13, color=INK, bold=True))

    steps = [
        ("1. Стан IDLE / START", "Очікування умови START.\nЗсувний регістр вхідних\nбітів очищено.", 90, OK_COL, OK_BG),
        ("2. Прийом адреси", "Прийом 7-біт адреси + R/W.\nАпаратне порівняння\nз регістром I2C_OAR1.", 240, BUS_COL, "#eff6ff"),
        ("3. Збіг і утримання SCL", "Збіг! Встановлено біт ADDR.\nАпаратний розтяг: SCL = 0.\nГенерація переривання MCU.", 390, WARN_COL, WARN_BG),
        ("4. Обслуговування ISR", "Прошивка читає I2C_ISR/SR1,\nскидає прапорець ADDR\nабо вичитує I2C_RXDR.", 540, PURPLE, "#faf5ff"),
        ("5. Відпускання SCL", "Апаратний MOSFET закривається.\nЛінія SCL піднімається до 3.3В.\nМайстер продовжує такт.", 690, OK_COL, OK_BG)
    ]

    for title, desc, cx, col, bg in steps:
        p.append(rect(cx - 65, 80, 130, 180, fill=bg, stroke=col, sw=1.6, rx=6))
        p.append(text(cx, 105, title.split(". ")[0], size=11, color=col, bold=True))
        p.append(text(cx, 122, title.split(". ")[1], size=10, color=INK, bold=True))
        p.append(line(cx - 55, 132, cx + 55, 132, color=col, sw=1))
        lines = desc.split("\n")
        for i, ln in enumerate(lines):
            p.append(text(cx, 155 + i * 18, ln, size=9.5, color=INK))

    # Arrows between top states
    for cx in (155, 305, 455, 605):
        p.append(line(cx, 170, cx + 20, 170, color=LINE, sw=1.8))
        p.append(polyline([(cx + 15, 166), (cx + 21, 170), (cx + 15, 174)], color=LINE, sw=1.8))

    # Bottom detailed flow: Data Reception Cycle with RXNE stretching
    p.append(rect(30, 285, 780, 125, fill=BG, stroke=LINE, sw=1.2, rx=6))
    p.append(text(45, 308, "Цикл прийому байта даних (Data Phase) та розтягування перед ACK/NACK:", size=11, color=INK, bold=True, anchor="start"))

    sub_boxes = [
        ("8 бітів зсуваються в регістр", "Майстер тактує SCL.\nSlave приймає 8 біт даних.", 130, NEG),
        ("Перенесення в I2C_RXDR", "Дані скопійовано в буфер.\nВстановлюється прапорець RXNE.", 320, CYAN),
        ("Апаратне утримання SCL", "Перед 9-м тактом (ACK) SCL=0.\nШина заморожена до вичитки!", 510, WARN_COL),
        ("Читання RXDR -> ACK", "MCU вичитує RXDR -> SCL=1,\nSlave виставляє ACK (SDA=0).", 700, OK_COL)
    ]

    for title, desc, cx, col in sub_boxes:
        p.append(rect(cx - 85, 322, 170, 75, fill=FILL, stroke=col, sw=1.3, rx=4))
        p.append(text(cx, 340, title, size=9.5, color=col, bold=True))
        lines = desc.split("\n")
        for i, ln in enumerate(lines):
            p.append(text(cx, 358 + i * 16, ln, size=9.5, color=INK))

    for cx in (215, 405, 595):
        p.append(line(cx + 5, 360, cx + 20, 360, color=LINE, sw=1.5))
        p.append(polyline([(cx + 16, 357), (cx + 21, 360), (cx + 16, 363)], color=LINE, sw=1.5))

    render(os.path.join(OUT, "slave-hardware-state-flow.svg"), W, H, *p)


def fig_clock_stretching_timing():
    W, H = 840, 400
    p = []

    p.append(rect(15, 15, 810, 370, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Часова діаграма розтягування такту SCL веденим пристроєм", size=13, color=INK, bold=True))

    # Grid lines
    for x in range(120, 780, 60):
        p.append(line(x, 60, x, 340, color="#f1f5f9", sw=1, dash="2,2"))

    # Labels
    p.append(text(110, 95, "Master Внутрішній Такт", size=10, color=BUS_COL, bold=True, anchor="end"))
    p.append(text(110, 165, "Slave Вихідний MOSFET", size=10, color=WARN_COL, bold=True, anchor="end"))
    p.append(text(110, 235, "Реальний сигнал SCL", size=10, color=ACCENT, bold=True, anchor="end"))
    p.append(text(110, 305, "Лінія даних SDA", size=10, color=PURPLE, bold=True, anchor="end"))

    # Master internal clock waveform
    m_pts = [
        (120, 80), (150, 80), (150, 110), (180, 110), (180, 80), (210, 80), (210, 110),
        (240, 110), (240, 80), (270, 80), (270, 110), (300, 110),
        (300, 80), (330, 80), (330, 110), (360, 110), (360, 80), (390, 80), (390, 110),
        (420, 110), (420, 80), (450, 80), (450, 110), (480, 110), (480, 80), (510, 80),
        (510, 110), (540, 110), (540, 80), (570, 80), (570, 110), (600, 110),
        (600, 80), (630, 80), (630, 110), (660, 110), (660, 80), (690, 80), (690, 110),
        (720, 110), (720, 80), (750, 80)
    ]
    p.append(polyline(m_pts, color=BUS_COL, sw=2))

    # Slave MOSFET
    s_pts = [
        (120, 180), (270, 180), (270, 150), (540, 150), (540, 180), (750, 180)
    ]
    p.append(polyline(s_pts, color=WARN_COL, sw=2))
    p.append(rect(275, 153, 260, 22, fill=WARN_BG, stroke="none", rx=3))
    p.append(text(405, 168, "Slave утримує SCL = 0 (t_stretch)", size=10, color=WARN_COL, bold=True))

    # Actual SCL on bus
    bus_pts = [
        (120, 220), (150, 220), (150, 250), (180, 250), (180, 220), (210, 220), (210, 250),
        (240, 250), (240, 220), (270, 220), (270, 250),
        (540, 250),
        (540, 220), (570, 220), (570, 250),
        (600, 250), (600, 220), (630, 220), (630, 250), (660, 250), (660, 220), (690, 220),
        (690, 250), (720, 250), (720, 220), (750, 220)
    ]
    p.append(polyline(bus_pts, color=ACCENT, sw=2.5))

    # Stretch measurement annotation
    p.append(line(270, 265, 540, 265, color=WARN_COL, sw=1.5))
    p.append(line(270, 260, 270, 270, color=WARN_COL, sw=1.5))
    p.append(line(540, 260, 540, 270, color=WARN_COL, sw=1.5))
    p.append(text(405, 280, "t_stretch (розтягнута фаза LOW)", size=10, color=WARN_COL, bold=True))

    # SDA waveform
    sda_pts = [
        (120, 290), (150, 290), (150, 320), (240, 320), (240, 290), (270, 290),
        (280, 320), (590, 320), (590, 290), (750, 290)
    ]
    p.append(polyline(sda_pts, color=PURPLE, sw=2))
    p.append(text(210, 335, "Біт 7", size=9.5, color=MUTED))
    p.append(text(255, 335, "Біт 8", size=9.5, color=MUTED))
    p.append(text(555, 335, "ACK (0)", size=9.5, color=OK_COL, bold=True))
    p.append(text(645, 335, "Наступний байт", size=9.5, color=MUTED))

    # Master sampling point arrow
    p.append(line(555, 210, 555, 290, color=OK_COL, sw=1.5, dash="3,2"))
    p.append(circle(555, 220, 4, fill=OK_COL, stroke=OK_COL))
    p.append(text(555, 200, "Зчитування ACK", size=9.5, color=OK_COL, bold=True))

    render(os.path.join(OUT, "timing-waveform-stretch.svg"), W, H, *p)


def fig_multimaster_arbitration_stretch():
    W, H = 840, 420
    p = []

    p.append(rect(15, 15, 810, 390, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Синхронізація такту SCL між кількома ведучими та розтягуючим веденим", size=13, color=INK, bold=True))

    # Sub-labels
    p.append(text(120, 85, "Master 1 (Швидкий)", size=10, color=OK_COL, bold=True, anchor="end"))
    p.append(text(120, 155, "Master 2 (Повільніший)", size=10, color=BUS_COL, bold=True, anchor="end"))
    p.append(text(120, 225, "Slave (Розтягує такт)", size=10, color=WARN_COL, bold=True, anchor="end"))
    p.append(text(120, 295, "Спільна лінія SCL", size=10, color=ACCENT, bold=True, anchor="end"))

    # Master 1: short low (30px), short high (30px)
    m1_pts = [
        (130, 70), (160, 70), (160, 100), (190, 100), (190, 70), (220, 70), (220, 100),
        (250, 100), (250, 70), (280, 70), (280, 100), (310, 100), (310, 70), (340, 70),
        (340, 100), (370, 100), (370, 70), (400, 70), (400, 100), (430, 100), (430, 70),
        (460, 70), (460, 100), (490, 100), (490, 70), (520, 70), (520, 100), (550, 100),
        (550, 70), (580, 70), (580, 100), (610, 100), (610, 70), (640, 70), (640, 100),
        (670, 100), (670, 70), (700, 70), (700, 100), (730, 100), (730, 70), (760, 70)
    ]
    p.append(polyline(m1_pts, color=OK_COL, sw=1.8))

    # Master 2: longer low (50px), longer high (50px)
    m2_pts = [
        (130, 140), (180, 140), (180, 170), (230, 170), (230, 140), (280, 140), (280, 170),
        (330, 170), (330, 140), (380, 140), (380, 170), (430, 170), (430, 140), (480, 140),
        (480, 170), (530, 170), (530, 140), (580, 140), (580, 170), (630, 170), (630, 140),
        (680, 140), (680, 170), (730, 170), (730, 140), (760, 140)
    ]
    p.append(polyline(m2_pts, color=BUS_COL, sw=1.8))

    # Slave: stretches SCL low from x=330 to x=560
    sl_pts = [
        (130, 210), (330, 210), (330, 240), (560, 240), (560, 210), (760, 210)
    ]
    p.append(polyline(sl_pts, color=WARN_COL, sw=2))

    # Bus SCL Wired-AND
    bus_scl = [
        (130, 280), (160, 280), (160, 310), (230, 310), (230, 280), (280, 280), (280, 310),
        (560, 310),
        (560, 280), (580, 280), (580, 310), (630, 310), (630, 280), (680, 280), (680, 310),
        (730, 310), (730, 280), (760, 280)
    ]
    p.append(polyline(bus_scl, color=ACCENT, sw=2.5))

    # Explanation boxes below
    p.append(rect(40, 340, 230, 50, fill=OK_BG, stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(155, 358, "1. Синхронізація LOW", size=10, color=OK_COL, bold=True))
    p.append(text(155, 375, "LOW триває, поки хоч ОДИН тримає 0", size=9.5, color=INK))

    p.append(rect(295, 340, 240, 50, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=4))
    p.append(text(415, 358, "2. Slave розтягує такт", size=10, color=WARN_COL, bold=True))
    p.append(text(415, 375, "Обидва Master скидають свої лічильники", size=9.5, color=INK))

    p.append(rect(560, 340, 240, 50, fill="#eff6ff", stroke=BUS_COL, sw=1.2, rx=4))
    p.append(text(680, 358, "3. Відлік HIGH", size=10, color=BUS_COL, bold=True))
    p.append(text(680, 375, "HIGH починається лише коли ВСІ відпустили", size=9.5, color=INK))

    render(os.path.join(OUT, "multimaster-sync-stretch.svg"), W, H, *p)


def fig_bidirectional_isolator_scheme():
    W, H = 840, 420
    p = []

    p.append(rect(15, 15, 810, 390, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))
    p.append(text(420, 38, "Схемотехніка двонаправленого буфера / ізолятора I2C (ISO1540 / PCA9515A)", size=13, color=INK, bold=True))

    # Side A (Master Side)
    p.append(rect(40, 70, 220, 310, fill=OK_BG, stroke=OK_COL, sw=1.5, rx=6))
    p.append(text(150, 95, "Сторона A (Side 1 / Master)", size=11, color=OK_COL, bold=True))
    p.append(text(150, 112, "Стандартні рівні I2C (0...3.3В)", size=9.5, color=MUTED))

    # Side A SCL pin
    p.append(line(260, 160, 320, 160, color=ACCENT, sw=2))
    p.append(text(285, 150, "SCL1", size=10, color=ACCENT, bold=True))
    p.append(circle(260, 160, 4, fill=ACCENT, stroke=ACCENT))

    # Isolation / Buffer Chip in center
    p.append(rect(320, 70, 200, 310, fill=FILL, stroke=LINE, sw=1.8, rx=6))
    p.append(text(420, 95, "Двонаправлений ізолятор", size=11, color=INK, bold=True))
    p.append(text(420, 112, "(ISO1540 / ADuM1250)", size=9.5, color=MUTED))

    # Central Barrier
    p.append(line(420, 130, 420, 360, color=WARN_COL, sw=2, dash="4,4"))
    p.append(text(420, 370, "Гальванічний бар'єр", size=9.5, color=WARN_COL, bold=True))

    # Direction A -> B Channel
    p.append(rect(335, 135, 75, 45, fill=BG, stroke=NEG, sw=1.2, rx=3))
    p.append(text(372, 153, "Компаратор", size=9.5, color=NEG, bold=True))
    p.append(text(372, 168, "V_IL = 0.5 В", size=9.5, color=MUTED))

    p.append(rect(430, 135, 75, 45, fill=BG, stroke=OK_COL, sw=1.2, rx=3))
    p.append(text(467, 153, "Драйвер B", size=9.5, color=OK_COL, bold=True))
    p.append(text(467, 168, "V_OL = 0.2 В", size=9.5, color=MUTED))

    p.append(line(372, 180, 372, 200, color=NEG, sw=1.5))
    p.append(line(372, 200, 467, 200, color=NEG, sw=1.5))
    p.append(line(467, 200, 467, 180, color=NEG, sw=1.5))
    p.append(polyline([(464, 185), (467, 180), (470, 185)], color=NEG, sw=1.5))
    p.append(text(420, 215, "Майстер тактує ->", size=9.5, color=NEG, bold=True))

    # Direction B -> A Channel (Clock Stretching Propagation)
    p.append(rect(430, 235, 75, 52, fill=WARN_BG, stroke=WARN_COL, sw=1.4, rx=3))
    p.append(text(467, 253, "Детектор SCL", size=9.5, color=WARN_COL, bold=True))
    p.append(text(467, 267, "Stretch sensing", size=9.5, color=WARN_COL))
    p.append(text(467, 281, "V_IL = 0.4 В", size=9.5, color=MUTED))

    p.append(rect(335, 235, 75, 52, fill=WARN_BG, stroke=WARN_COL, sw=1.4, rx=3))
    p.append(text(372, 253, "Буфер зі зсувом", size=9.5, color=WARN_COL, bold=True))
    p.append(text(372, 267, "Offset V_OL", size=9.5, color=WARN_COL))
    p.append(text(372, 281, "V_OL = 0.55 В", size=9.5, color=MUTED))

    p.append(line(467, 287, 467, 308, color=WARN_COL, sw=1.5))
    p.append(line(467, 308, 372, 308, color=WARN_COL, sw=1.5))
    p.append(line(372, 308, 372, 287, color=WARN_COL, sw=1.5))
    p.append(polyline([(369, 292), (372, 287), (375, 292)], color=WARN_COL, sw=1.5))
    p.append(text(420, 325, "<- Slave розтягує такт", size=9.5, color=WARN_COL, bold=True))

    # Side B (Slave Side)
    p.append(rect(580, 70, 220, 310, fill=WARN_BG, stroke=WARN_COL, sw=1.5, rx=6))
    p.append(text(690, 95, "Сторона B (Side 2 / Slave)", size=11, color=WARN_COL, bold=True))
    p.append(text(690, 112, "Ізольована сенсорна шина", size=9.5, color=MUTED))

    # Side B SCL pin
    p.append(line(520, 160, 580, 160, color=ACCENT, sw=2))
    p.append(text(555, 150, "SCL2", size=10, color=ACCENT, bold=True))
    p.append(circle(580, 160, 4, fill=ACCENT, stroke=ACCENT))

    # Offset explanation banner
    p.append(rect(50, 340, 200, 30, fill=BG, stroke=OK_COL, sw=1, rx=3))
    p.append(text(150, 360, "Запобігання защіпці (Latch-Up)", size=9.5, color=OK_COL, bold=True))

    p.append(rect(590, 340, 200, 30, fill=BG, stroke=WARN_COL, sw=1, rx=3))
    p.append(text(690, 360, "Slave тримає SCL2 = 0 В", size=9.5, color=WARN_COL, bold=True))

    render(os.path.join(OUT, "bidirectional-isolator-scheme.svg"), W, H, *p)


if __name__ == "__main__":
    fig_scl_open_drain_circuit()
    fig_slave_hardware_states()
    fig_clock_stretching_timing()
    fig_multimaster_arbitration_stretch()
    fig_bidirectional_isolator_scheme()
    print("Figures generated successfully.")
