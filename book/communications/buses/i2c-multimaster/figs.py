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


def fig_wired_and_topology():
    W, H = 840, 420
    p = []

    # Title & Subtitle banner
    p.append(rect(20, 20, 800, 380, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    # VDD Rail & Pull-Up Resistors
    p.append(line(50, 55, 790, 55, color=POS, sw=2.5))
    p.append(text(55, 45, "VDD (+3.3V)", size=11, color=POS, bold=True, anchor="start"))

    # Pull-up Resistors (Rp on SCL and SDA)
    # SCL Pull-up
    p.append(line(160, 55, 160, 75, color=POS, sw=1.8))
    p.append(rect(150, 75, 20, 32, fill="#fff7ed", stroke=ACCENT, sw=1.5, rx=2))
    p.append(text(175, 95, "Rp (SCL)", size=10, color=ACCENT, bold=True, anchor="start"))
    p.append(line(160, 107, 160, 135, color=ACCENT, sw=1.8))

    # SDA Pull-up
    p.append(line(260, 55, 260, 75, color=POS, sw=1.8))
    p.append(rect(250, 75, 20, 32, fill="#eff6ff", stroke=BUS_COL, sw=1.5, rx=2))
    p.append(text(275, 95, "Rp (SDA)", size=10, color=BUS_COL, bold=True, anchor="start"))
    p.append(line(260, 107, 260, 175, color=BUS_COL, sw=1.8))

    # Main Bus Rails: SCL (Accent/Orange) and SDA (Blue)
    p.append(line(50, 135, 790, 135, color=ACCENT, sw=2.5))
    p.append(rect(50, 115, 95, 18, fill="#fff7ed", stroke=ACCENT, sw=1, rx=3))
    p.append(text(97, 128, "SCL (Тактова лінія)", size=9.5, color=ACCENT, bold=True))

    p.append(line(50, 175, 790, 175, color=BUS_COL, sw=2.5))
    p.append(rect(50, 155, 95, 18, fill="#eff6ff", stroke=BUS_COL, sw=1, rx=3))
    p.append(text(97, 168, "SDA (Лінія даних)", size=9.5, color=BUS_COL, bold=True))

    # Master 1 (Left)
    p.append(rect(50, 215, 220, 165, fill=OK_BG, stroke=OK_COL, sw=1.8, rx=6))
    p.append(text(160, 238, "Ведучий 1 (Master 1)", size=12, color=OK_COL, bold=True))
    p.append(text(160, 254, "Головний MCU", size=10, color=MUTED, italic=True))
    # Open drain drivers for M1
    p.append(rect(65, 268, 90, 42, fill=BG, stroke=ACCENT, sw=1.2, rx=4))
    p.append(text(110, 285, "SCL Open-Drain", size=9.5, color=ACCENT, bold=True))
    p.append(text(110, 300, "MOSFET + Вхід", size=9.5, color=MUTED))
    p.append(line(110, 268, 110, 135, color=ACCENT, sw=1.5))
    p.append(circle(110, 135, 3.5, fill=ACCENT, stroke=ACCENT))

    p.append(rect(165, 268, 90, 42, fill=BG, stroke=BUS_COL, sw=1.2, rx=4))
    p.append(text(210, 285, "SDA Open-Drain", size=9.5, color=BUS_COL, bold=True))
    p.append(text(210, 300, "MOSFET + Вхід", size=9.5, color=MUTED))
    p.append(line(210, 268, 210, 175, color=BUS_COL, sw=1.5))
    p.append(circle(210, 175, 3.5, fill=BUS_COL, stroke=BUS_COL))

    p.append(text(160, 335, "GND (Спільна земля)", size=9.5, color=LINE))
    p.append(line(160, 342, 160, 360, color=LINE, sw=1.5))
    p.append(line(148, 360, 172, 360, color=LINE, sw=2))

    # Master 2 (Middle)
    p.append(rect(310, 215, 220, 165, fill="#fdf4ff", stroke=PURPLE, sw=1.8, rx=6))
    p.append(text(420, 238, "Ведучий 2 (Master 2)", size=12, color=PURPLE, bold=True))
    p.append(text(420, 254, "Копроцесор живлення", size=10, color=MUTED, italic=True))
    # Open drain drivers for M2
    p.append(rect(325, 268, 90, 42, fill=BG, stroke=ACCENT, sw=1.2, rx=4))
    p.append(text(370, 285, "SCL Open-Drain", size=9.5, color=ACCENT, bold=True))
    p.append(text(370, 300, "MOSFET + Вхід", size=9.5, color=MUTED))
    p.append(line(370, 268, 370, 135, color=ACCENT, sw=1.5))
    p.append(circle(370, 135, 3.5, fill=ACCENT, stroke=ACCENT))

    p.append(rect(425, 268, 90, 42, fill=BG, stroke=BUS_COL, sw=1.2, rx=4))
    p.append(text(470, 285, "SDA Open-Drain", size=9.5, color=BUS_COL, bold=True))
    p.append(text(470, 300, "MOSFET + Вхід", size=9.5, color=MUTED))
    p.append(line(470, 268, 470, 175, color=BUS_COL, sw=1.5))
    p.append(circle(470, 175, 3.5, fill=BUS_COL, stroke=BUS_COL))

    p.append(text(420, 335, "GND (Спільна земля)", size=9.5, color=LINE))
    p.append(line(420, 342, 420, 360, color=LINE, sw=1.5))
    p.append(line(408, 360, 432, 360, color=LINE, sw=2))

    # Slave Target (Right)
    p.append(rect(570, 215, 220, 165, fill="#f8fafc", stroke=MUTED, sw=1.8, rx=6))
    p.append(text(680, 238, "Ведений (Slave Target)", size=12, color=INK, bold=True))
    p.append(text(680, 254, "Давач температури / EEPROM", size=10, color=MUTED, italic=True))

    p.append(rect(585, 268, 90, 42, fill=BG, stroke=ACCENT, sw=1.2, rx=4))
    p.append(text(630, 285, "SCL Stretch In", size=9.5, color=ACCENT, bold=True))
    p.append(text(630, 300, "Вхідний тригер", size=9.5, color=MUTED))
    p.append(line(630, 268, 630, 135, color=ACCENT, sw=1.5))
    p.append(circle(630, 135, 3.5, fill=ACCENT, stroke=ACCENT))

    p.append(rect(685, 268, 90, 42, fill=BG, stroke=BUS_COL, sw=1.2, rx=4))
    p.append(text(730, 285, "SDA Open-Drain", size=9.5, color=BUS_COL, bold=True))
    p.append(text(730, 300, "ACK / Data Out", size=9.5, color=MUTED))
    p.append(line(730, 268, 730, 175, color=BUS_COL, sw=1.5))
    p.append(circle(730, 175, 3.5, fill=BUS_COL, stroke=BUS_COL))

    p.append(text(680, 335, "GND (Спільна земля)", size=9.5, color=LINE))
    p.append(line(680, 342, 680, 360, color=LINE, sw=1.5))
    p.append(line(668, 360, 692, 360, color=LINE, sw=2))

    render(os.path.join(OUT, "wired-and-topology.svg"), W, H, *p, title="Фізична топологія «монтажного І» (Wired-AND) у конфігурації Multi-Master")


def fig_clock_synchronization():
    W, H = 840, 430
    p = []

    # Background card
    p.append(rect(20, 20, 800, 390, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    # Grid vertical reference lines
    t_steps = [
        (130, "t0: Початок LOW"),
        (250, "t1: M2 відпускає SCL"),
        (380, "t2: M1 відпускає SCL"),
        (540, "t3: M1 тягне SCL"),
        (660, "t4: M2 тягне SCL"),
        (760, "t5: Наступний цикл")
    ]
    for tx, tlbl in t_steps:
        p.append(line(tx, 55, tx, 355, color="#e2e8f0", sw=1.2, dash="3 3"))

    # Track 1: Master 1 internal clock generator (Long LOW, Short HIGH)
    p.append(text(35, 92, "Ведучий 1", size=11, color=OK_COL, bold=True, anchor="start"))
    p.append(text(35, 108, "довгий t_LOW", size=9.5, color=MUTED, anchor="start"))
    m1_pts = [(100, 75), (130, 75), (130, 115), (380, 115), (380, 75), (540, 75), (540, 115), (780, 115)]
    p.append(polyline(m1_pts, color=OK_COL, sw=2.2))
    p.append(text(255, 130, "t_LOW1 (довший)", size=9.5, color=OK_COL))
    p.append(text(460, 68, "t_HIGH1 (коротший)", size=9.5, color=OK_COL))

    # Track 2: Master 2 internal clock generator (Short LOW, Long HIGH)
    p.append(text(35, 185, "Ведучий 2", size=11, color=PURPLE, bold=True, anchor="start"))
    p.append(text(35, 201, "короткий t_LOW", size=9.5, color=MUTED, anchor="start"))
    m2_pts = [(100, 170), (130, 170), (130, 210), (250, 210), (250, 170), (660, 170), (660, 210), (780, 210)]
    p.append(polyline(m2_pts, color=PURPLE, sw=2.2))
    p.append(text(190, 225, "t_LOW2 (коротший)", size=9.5, color=PURPLE))
    p.append(text(455, 163, "t_HIGH2 (довший)", size=9.5, color=PURPLE))

    # Track 3: Physical Line SCL (Wired-AND Result)
    p.append(rect(30, 260, 780, 105, fill="#fffbeb", stroke=ACCENT, sw=1.5, rx=6))
    p.append(text(45, 290, "Фізична лінія SCL", size=11, color=ACCENT, bold=True, anchor="start"))
    p.append(text(45, 305, "Wired-AND результат", size=9.5, color=MUTED, anchor="start"))

    scl_pts = [(100, 280), (130, 280), (130, 325), (380, 325), (380, 280), (540, 280), (540, 325), (780, 325)]
    p.append(polyline(scl_pts, color=ACCENT, sw=3))

    # Highlight zones
    p.append(rect(130, 338, 250, 18, fill="#fee2e2", stroke=WARN_COL, sw=1, rx=3))
    p.append(text(255, 351, "Низький період = MAX(t_LOW1, t_LOW2)", size=9.5, color=WARN_COL, bold=True))

    p.append(rect(380, 338, 160, 18, fill="#dcfce7", stroke=OK_COL, sw=1, rx=3))
    p.append(text(460, 351, "Високий період = MIN(t_HIGH1, t_HIGH2)", size=9.5, color=OK_COL, bold=True))

    # Bottom summary
    p.append(text(W / 2, 395, "Синхронізація SCL: лінія тримається LOW найповільнішим ведучим і падає LOW найшвидшим", size=10, color=INK, italic=True))

    render(os.path.join(OUT, "clock-synchronization.svg"), W, H, *p, title="Синхронізація тактових генераторів (Clock Synchronization) на шині SCL")


def fig_data_arbitration():
    W, H = 840, 450
    p = []

    # Card
    p.append(rect(20, 20, 800, 410, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    # Clock Cycles columns (Bit 7, Bit 6, Bit 5, Bit 4, Bit 3, Bit 2)
    cols = [
        (130, 220, "Біт 7 (MSB)", "0 = 0", True),
        (220, 310, "Біт 6", "0 = 0", True),
        (310, 400, "Біт 5", "0 = 0", True),
        (400, 520, "Біт 4 (ВТРАТА)", "1 != 0 (M1 програв)", False),
        (520, 640, "Біт 3", "0 (Тільки M2)", True),
        (640, 760, "Біт 2", "1 (Тільки M2)", True),
    ]

    for x1, x2, b_title, b_status, is_ok in cols:
        bg = "#f0fdf4" if is_ok else "#fef2f2"
        st = "#bbf7d0" if is_ok else "#fecaca"
        p.append(rect(x1, 55, x2 - x1, 315, fill=bg, stroke=st, sw=1))
        p.append(text((x1 + x2) / 2, 70, b_title, size=10, color=INK, bold=True))
        p.append(text((x1 + x2) / 2, 85, b_status, size=9.5, color=OK_COL if is_ok else WARN_COL, bold=True))

    # Track SCL (Clock pulses)
    p.append(text(35, 115, "Тактовий сигнал SCL", size=10.5, color=ACCENT, bold=True, anchor="start"))
    scl_pts = []
    for x1, x2, _, _, _ in cols:
        scl_pts.extend([(x1, 130), (x1 + 15, 130), (x1 + 15, 105), (x2 - 15, 105), (x2 - 15, 130), (x2, 130)])
    p.append(polyline(scl_pts, color=ACCENT, sw=2))

    # Track 1: Master 1 (Transmitting Address 0x38 = 0011 1000b)
    p.append(text(35, 170, "Ведучий 1 (SDA M1)", size=10.5, color=OK_COL, bold=True, anchor="start"))
    p.append(text(35, 186, "Шле 0x38 (0011...)", size=9.5, color=MUTED, anchor="start"))
    m1_sda = [
        (130, 200), (220, 200),
        (220, 200), (310, 200),
        (310, 200), (400, 200),
        (400, 165), (520, 165),
        (520, 185), (760, 185)
    ]
    p.append(polyline(m1_sda[:8], color=OK_COL, sw=2.2))
    p.append(polyline(m1_sda[8:], color=MUTED, sw=1.5, dash="3 3"))
    p.append(text(460, 155, "Видає 1 (відпускає)", size=9.5, color=OK_COL, bold=True))
    p.append(text(640, 180, "SDA вихід вимкнено (High-Z)", size=9.5, color=MUTED, italic=True))

    # Track 2: Master 2 (Transmitting Address 0x18 = 0001 1000b)
    p.append(text(35, 235, "Ведучий 2 (SDA M2)", size=10.5, color=PURPLE, bold=True, anchor="start"))
    p.append(text(35, 251, "Шле 0x18 (0001...)", size=9.5, color=MUTED, anchor="start"))
    m2_sda = [
        (130, 265), (220, 265),
        (220, 265), (310, 265),
        (310, 265), (400, 265),
        (400, 265), (520, 265),
        (520, 230), (640, 230),
        (640, 230), (760, 230)
    ]
    p.append(polyline(m2_sda, color=PURPLE, sw=2.2))
    p.append(text(460, 280, "Видає 0 (притягує)", size=9.5, color=PURPLE, bold=True))

    # Track 3: Physical SDA Bus Line
    p.append(text(35, 310, "Спільна шина SDA", size=10.5, color=BUS_COL, bold=True, anchor="start"))
    p.append(text(35, 326, "Фізичний рівень", size=9.5, color=MUTED, anchor="start"))
    bus_sda = [
        (130, 335), (220, 335),
        (220, 335), (310, 335),
        (310, 335), (400, 335),
        (400, 335), (520, 335),
        (520, 300), (640, 300),
        (640, 300), (760, 300)
    ]
    p.append(polyline(bus_sda, color=BUS_COL, sw=3))

    # Sampling markers in Bit 4
    p.append(circle(460, 335, 4, fill=WARN_COL, stroke=WARN_COL))
    p.append(arrow(460, 175, 460, 325, color=WARN_COL, sw=1.5))
    p.append(rect(400, 375, 250, 36, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=4))
    p.append(text(525, 390, "КОНФЛІКТ: M1 хотів 1, але прочитав 0!", size=9.5, color=WARN_COL, bold=True))
    p.append(text(525, 404, "M1 фіксує ARLO і переходить у режим веденого", size=9.5, color=INK))

    render(os.path.join(OUT, "data-arbitration.svg"), W, H, *p, title="Побітовий арбітраж даних (Data Arbitration) на лінії SDA")


def fig_repeated_start_arbitration():
    W, H = 840, 390
    p = []

    # Card
    p.append(rect(20, 20, 800, 350, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    # Left Box: STOP + START
    p.append(rect(40, 60, 360, 290, fill="#fff5f5", stroke=WARN_COL, sw=1.5, rx=6))
    p.append(text(220, 85, "Звільнення шини через STOP", size=12, color=WARN_COL, bold=True))
    p.append(text(220, 102, "Розрив атомарності транзакції", size=10, color=MUTED, italic=True))

    p.append(polyline([(60, 130), (140, 130), (160, 130), (160, 160), (380, 160)], color=ACCENT, sw=1.8))
    p.append(text(70, 122, "SCL", size=10, color=ACCENT, bold=True, anchor="start"))

    p.append(polyline([(60, 170), (120, 170), (140, 140), (220, 140), (240, 170), (380, 170)], color=BUS_COL, sw=1.8))
    p.append(text(70, 162, "SDA", size=10, color=BUS_COL, bold=True, anchor="start"))

    p.append(text(140, 188, "Умова STOP", size=9.5, color=WARN_COL, bold=True))
    p.append(rect(175, 125, 100, 22, fill="#fee2e2", stroke=WARN_COL, sw=1, rx=3))
    p.append(text(225, 140, "Шина вільна (t_BUF)", size=9.5, color=WARN_COL))

    p.append(circle(240, 170, 3.5, fill=POS, stroke=POS))
    p.append(text(300, 198, "Ведучий 2 вклинюється зі START!", size=9.5, color=POS, bold=True))
    p.append(text(220, 252, "Наслідок: Ведучий 1 налаштував регістр,", size=9.5, color=INK))
    p.append(text(220, 270, "але читання здійснює вже з іншого давача!", size=9.5, color=WARN_COL, bold=True))
    p.append(text(220, 310, "Вразливість до стану гонитви (Race Condition)", size=10, color=WARN_COL, bold=True))

    # Right Box: Repeated START
    p.append(rect(440, 60, 360, 290, fill=OK_BG, stroke=OK_COL, sw=1.5, rx=6))
    p.append(text(620, 85, "Повторний старт (Repeated START, Sr)", size=12, color=OK_COL, bold=True))
    p.append(text(620, 102, "Неподільна (атомарна) транзакція", size=10, color=MUTED, italic=True))

    p.append(polyline([(460, 160), (520, 160), (520, 130), (640, 130), (640, 160), (780, 160)], color=ACCENT, sw=1.8))
    p.append(text(470, 122, "SCL", size=10, color=ACCENT, bold=True, anchor="start"))

    p.append(polyline([(460, 170), (540, 170), (560, 140), (600, 140), (620, 170), (780, 170)], color=BUS_COL, sw=1.8))
    p.append(text(470, 162, "SDA", size=10, color=BUS_COL, bold=True, anchor="start"))

    p.append(circle(620, 170, 4, fill=OK_COL, stroke=OK_COL))
    p.append(text(620, 192, "Умова Sr (Repeated START)", size=9.5, color=OK_COL, bold=True))
    p.append(rect(525, 212, 190, 24, fill="#dcfce7", stroke=OK_COL, sw=1, rx=3))
    p.append(text(620, 228, "Шина жодної миті не є вільною", size=9.5, color=OK_COL, bold=True))

    p.append(text(620, 258, "Ведучий 1 неподільно перемикає напрямок", size=9.5, color=INK))
    p.append(text(620, 276, "з запису адреси регістра на читання даних.", size=9.5, color=INK))
    p.append(text(620, 310, "Жоден інший ведучий не може перехопити шину", size=10, color=OK_COL, bold=True))

    render(os.path.join(OUT, "repeated-start-arbitration.svg"), W, H, *p, title="Захист неподільності операцій: Repeated START проти стану гонитви")


def fig_master_slave_state_machine():
    W, H = 840, 440
    p = []

    # Card
    p.append(rect(20, 20, 800, 400, fill="#fafbfc", stroke=LINE, sw=1.2, rx=8))

    # 1. IDLE
    p.append(rect(340, 45, 160, 45, fill="#f1f5f9", stroke=LINE, sw=1.8, rx=6))
    p.append(text(420, 65, "СТАН: IDLE (Спокій)", size=11, color=INK, bold=True))
    p.append(text(420, 80, "SDA=1, SCL=1", size=9.5, color=MUTED))

    # 2. MASTER_TX
    p.append(rect(50, 140, 210, 65, fill=OK_BG, stroke=OK_COL, sw=1.8, rx=6))
    p.append(text(155, 162, "MASTER: Передача кадру", size=11, color=OK_COL, bold=True))
    p.append(text(155, 178, "Генерація SCL + видача бітів", size=9.5, color=MUTED))
    p.append(text(155, 194, "Порівняння SDA_OUT з SDA_IN", size=9.5, color=OK_COL))

    # Transition IDLE -> MASTER_TX
    p.append(arrow(360, 90, 220, 140, color=OK_COL, sw=1.8))
    p.append(text(270, 108, "START запит", size=9.5, color=OK_COL, bold=True))

    # 3. ARB_LOST
    p.append(rect(50, 260, 210, 65, fill=WARN_BG, stroke=WARN_COL, sw=1.8, rx=6))
    p.append(text(155, 282, "ARBITRATION LOST (ARLO)", size=11, color=WARN_COL, bold=True))
    p.append(text(155, 298, "SDA_OUT=1, але SDA_IN=0", size=9.5, color=WARN_COL))
    p.append(text(155, 314, "Негайне вимкнення виходу SDA", size=9.5, color=MUTED))

    # Transition MASTER_TX -> ARB_LOST
    p.append(arrow(155, 205, 155, 260, color=WARN_COL, sw=2))
    p.append(text(160, 235, "Невідповідність біта", size=9.5, color=WARN_COL, bold=True, anchor="start"))

    # 4. SLAVE_MATCH_CHECK
    p.append(rect(340, 260, 200, 65, fill="#fef3c7", stroke=ACCENT, sw=1.8, rx=6))
    p.append(text(440, 282, "Перевірка адреси веденого", size=11, color=ACCENT, bold=True))
    p.append(text(440, 298, "Чи викликає переможець нас?", size=9.5, color=MUTED))
    p.append(text(440, 314, "Порівняння з власною адресою", size=9.5, color=ACCENT))

    # Transition ARB_LOST -> SLAVE_MATCH_CHECK
    p.append(arrow(260, 292, 340, 292, color=ACCENT, sw=1.8))
    p.append(text(300, 282, "Слухати шину", size=9.5, color=ACCENT, bold=True))

    # 5. SLAVE_RX_TX
    p.append(rect(600, 260, 190, 65, fill="#eff6ff", stroke=BUS_COL, sw=1.8, rx=6))
    p.append(text(695, 282, "SLAVE: Відповідь ведучому", size=11, color=BUS_COL, bold=True))
    p.append(text(695, 298, "Видача ACK на 9 такті", size=9.5, color=BUS_COL))
    p.append(text(695, 314, "Прийом або віддача даних", size=9.5, color=MUTED))

    # Transition SLAVE_MATCH_CHECK -> SLAVE_RX_TX
    p.append(arrow(540, 292, 600, 292, color=BUS_COL, sw=1.8))
    p.append(text(570, 282, "Співпало!", size=9.5, color=BUS_COL, bold=True))

    # 6. BACKOFF_WAIT
    p.append(rect(340, 355, 200, 50, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(440, 374, "Очікування STOP + Backoff", size=10, color=INK, bold=True))
    p.append(text(440, 390, "Псевдовипадкова пауза повтору", size=9.5, color=MUTED))

    # Transition SLAVE_MATCH_CHECK -> BACKOFF_WAIT
    p.append(arrow(440, 325, 440, 355, color=MUTED, sw=1.5))
    p.append(text(445, 342, "Адреса чужа", size=9.5, color=MUTED, anchor="start"))

    # Transition BACKOFF_WAIT -> IDLE
    p.append(polyline([(340, 380), (300, 380), (300, 67), (340, 67)], color=LINE, sw=1.5, dash="3 3"))
    p.append(arrow(300, 67, 340, 67, color=LINE, sw=1.5))
    p.append(text(290, 180, "STOP на шині + таймаут", size=9.5, color=MUTED, anchor="end"))

    # Transition SLAVE_RX_TX -> IDLE
    p.append(polyline([(695, 260), (695, 67), (500, 67)], color=BUS_COL, sw=1.5, dash="3 3"))
    p.append(arrow(540, 67, 500, 67, color=BUS_COL, sw=1.5))
    p.append(text(610, 57, "STOP завершення", size=9.5, color=BUS_COL))

    # Success transfer from MASTER_TX -> IDLE
    p.append(polyline([(155, 140), (155, 67), (340, 67)], color=OK_COL, sw=1.5, dash="3 3"))
    p.append(arrow(260, 67, 340, 67, color=OK_COL, sw=1.5))
    p.append(text(210, 57, "Транзакція OK (STOP)", size=9.5, color=OK_COL))

    render(os.path.join(OUT, "master-slave-state-machine.svg"), W, H, *p, title="Автомат станів апаратного контролера I2C з обробкою арбітражу")


if __name__ == "__main__":
    fig_wired_and_topology()
    fig_clock_synchronization()
    fig_data_arbitration()
    fig_repeated_start_arbitration()
    fig_master_slave_state_machine()
    print("All figures generated successfully!")
