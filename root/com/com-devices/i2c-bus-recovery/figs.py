# -*- coding: utf-8 -*-
import sys, os

# Add scripts directory to path (4 levels up from topic directory)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Color Palette
WARN_COL  = "#c0392b"
WARN_BG   = "#fdecea"
OK_COL    = "#27ae60"
OK_BG     = "#eef6ef"
BUS_SCL   = "#2457d6"
BUS_SDA   = "#d97706"
MUTED_GRD = "#e5e7eb"
PANEL_BG  = "#f8fafc"
CHIP_BG   = "#f1f5f9"
DIODE_COL = "#8e44ad"

def polyline(pts, color=LINE, sw=1.5, fill="none", dash=None):
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{points}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"{d}/>'

def fig_lockup_sequence():
    W, H = 900, 440
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    # Title
    p.append(text(W / 2, 36, "Механізм апаратного зависання I²C: перезавантаження ведучого посеред читання", size=15, bold=True))

    # Signals levels
    y_scl_hi = 95
    y_scl_lo = 155
    y_sda_hi = 215
    y_sda_lo = 275

    # Signal Labels
    box_scl, _, _ = textbox(55, 125, "SCL\n(Clock)", size=12, pad=6, fill="#eff6ff", stroke=BUS_SCL, bold=True, color=BUS_SCL, min_w=65)
    p.append(box_scl)

    box_sda, _, _ = textbox(55, 245, "SDA\n(Data)", size=12, pad=6, fill="#fff7ed", stroke=BUS_SDA, bold=True, color=BUS_SDA, min_w=65)
    p.append(box_sda)

    # Voltage references
    p.append(line(100, y_scl_hi, 870, y_scl_hi, color=MUTED_GRD, sw=1, dash="3,3"))
    p.append(line(100, y_scl_lo, 870, y_scl_lo, color=MUTED_GRD, sw=1, dash="3,3"))
    p.append(line(100, y_sda_hi, 870, y_sda_hi, color=MUTED_GRD, sw=1, dash="3,3"))
    p.append(line(100, y_sda_lo, 870, y_sda_lo, color=MUTED_GRD, sw=1, dash="3,3"))

    p.append(text(875, y_scl_hi + 4, "3.3V", size=10, color=MUTED, anchor="start"))
    p.append(text(875, y_scl_lo + 4, "0V", size=10, color=MUTED, anchor="start"))
    p.append(text(875, y_sda_hi + 4, "3.3V", size=10, color=MUTED, anchor="start"))
    p.append(text(875, y_sda_lo + 4, "0V", size=10, color=MUTED, anchor="start"))

    # SCL waveform
    pts_scl = [
        (110, y_scl_hi),
        (130, y_scl_hi), (130, y_scl_lo), (160, y_scl_lo), (160, y_scl_hi), # clock 1
        (190, y_scl_hi), (190, y_scl_lo), (220, y_scl_lo), (220, y_scl_hi), # clock 2
        (250, y_scl_hi), (250, y_scl_lo), (280, y_scl_lo), (280, y_scl_hi), # clock 3
        (310, y_scl_hi), (310, y_scl_lo), (340, y_scl_lo), (340, y_scl_hi), # clock 4
        (370, y_scl_hi), (370, y_scl_lo), (400, y_scl_lo), (400, y_scl_hi), # clock 5
        (430, y_scl_hi), (860, y_scl_hi) # Pulled up to 3.3V
    ]
    p.append(polyline(pts_scl, color=BUS_SCL, sw=2.2))

    # SDA waveform
    pts_sda = [
        (110, y_sda_hi),
        (145, y_sda_hi), (145, y_sda_lo), # Bit 7 -> 6
        (205, y_sda_lo), # Bit 6 (0)
        (265, y_sda_lo), # Bit 5 (0)
        (325, y_sda_lo), # Bit 4 (0)
        (860, y_sda_lo)  # STUCK LOW!
    ]
    p.append(polyline(pts_sda, color=BUS_SDA, sw=2.2))

    # Event marker: MCU Reset
    x_crash = 415
    p.append(line(x_crash, 60, x_crash, 310, color=WARN_COL, sw=1.8, dash="4,4"))
    box_crash, _, _ = textbox(x_crash, 70, "ЗБІЙ / СКИДАННЯ МК\n(WDT, Brown-out, HardFault)", size=11, pad=5, fill=WARN_BG, stroke=WARN_COL, bold=True, color=WARN_COL)
    p.append(box_crash)

    # Annotations on waveform
    p.append(text(145, y_sda_hi - 10, "біт 7: '1'", size=10, color=INK))
    p.append(text(205, y_sda_lo + 16, "біт 6: '0'", size=10, color=INK))
    p.append(text(265, y_sda_lo + 16, "біт 5: '0'", size=10, color=INK))
    p.append(text(325, y_sda_lo + 16, "біт 4: '0'", size=10, color=INK))

    # Zone after crash
    p.append(rect(450, 110, 400, 50, fill="#eff6ff", stroke=BUS_SCL, sw=1, rx=4))
    p.append(text(650, 130, "МК перезавантажився, SCL підтягнуто до 3.3 В резистором Rp", size=11, color=BUS_SCL, bold=True))
    p.append(text(650, 148, "Периферія I2C МК бачить SDA = 0 В і виставляє прапорець BUSY", size=10, color=INK))

    p.append(rect(450, 230, 400, 60, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=4))
    p.append(text(650, 252, "ЗАВИСАННЯ: ведений тримає SDA = 0 В (N-MOSFET відкритий)", size=11, color=WARN_COL, bold=True))
    p.append(text(650, 272, "Ведений чекає тактів SCL для видачі решти бітів (3, 2, 1, 0, ACK)", size=10, color=INK))

    # Bottom summary explanation box
    box_bot, _, _ = textbox(W / 2, 370,
        "Чому звичайний рестарт МК безсилий: апаратний модуль I2C не може згенерувати START-умову\n(перепад SDA з HIGH в LOW при високому SCL), оскільки лінія SDA вже фізично заземлена веденим чіпом.\nПрограмний рестарт периферії MCU не надсилає тактових імпульсів на шину.",
        size=12, pad=8, fill=PANEL_BG, stroke=LINE, min_w=820)
    p.append(box_bot)

    render(os.path.join(OUT, "i2c-lockup-sequence.svg"), W, H, *p)

def fig_9clock_recovery():
    W, H = 920, 450
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    # Title
    p.append(text(W / 2, 34, "Алгоритм відновлення шини тактуванням (9-Clock Pulse Sequence + STOP)", size=15, bold=True))

    y_scl_hi = 85
    y_scl_lo = 145
    y_sda_hi = 205
    y_sda_lo = 265

    # Signal Labels
    box_scl, _, _ = textbox(55, 115, "SCL\n(GPIO Bitbang)", size=11, pad=5, fill="#eff6ff", stroke=BUS_SCL, bold=True, color=BUS_SCL, min_w=75)
    p.append(box_scl)

    box_sda, _, _ = textbox(55, 235, "SDA\n(Line State)", size=11, pad=5, fill="#fff7ed", stroke=BUS_SDA, bold=True, color=BUS_SDA, min_w=75)
    p.append(box_sda)

    # Reference grid lines
    p.append(line(100, y_scl_hi, 890, y_scl_hi, color=MUTED_GRD, sw=1, dash="3,3"))
    p.append(line(100, y_scl_lo, 890, y_scl_lo, color=MUTED_GRD, sw=1, dash="3,3"))
    p.append(line(100, y_sda_hi, 890, y_sda_hi, color=MUTED_GRD, sw=1, dash="3,3"))
    p.append(line(100, y_sda_lo, 890, y_sda_lo, color=MUTED_GRD, sw=1, dash="3,3"))

    # 9 Clock Pulses on SCL generated by MCU GPIO
    x_start = 120
    t_step = 55
    pts_scl = [(105, y_scl_hi)]
    for i in range(9):
        x_lo = x_start + i * t_step
        x_hi = x_lo + 25
        pts_scl.extend([(x_lo, y_scl_hi), (x_lo, y_scl_lo), (x_hi, y_scl_lo), (x_hi, y_scl_hi)])
        # Label each pulse
        p.append(text(x_lo + 12, y_scl_lo + 16, f"#{i+1}", size=10, color=BUS_SCL, bold=True))

    # After 9 clocks, SCL goes low for STOP generation, then high
    x_stop_prep = x_start + 9 * t_step
    pts_scl.extend([
        (x_stop_prep, y_scl_hi),
        (x_stop_prep + 15, y_scl_lo),
        (x_stop_prep + 55, y_scl_lo),
        (x_stop_prep + 55, y_scl_hi),
        (880, y_scl_hi)
    ])
    p.append(polyline(pts_scl, color=BUS_SCL, sw=2.2))

    # SDA line behavior
    x_release = x_start + 5 * t_step + 25
    pts_sda = [
        (105, y_sda_lo),
        (x_release, y_sda_lo),
        (x_release + 10, y_sda_hi),
        (x_stop_prep + 30, y_sda_hi),
        (x_stop_prep + 30, y_sda_lo),
        (x_stop_prep + 75, y_sda_lo),
        (x_stop_prep + 75, y_sda_hi),
        (880, y_sda_hi)
    ]
    p.append(polyline(pts_sda, color=BUS_SDA, sw=2.2))

    # Release marker
    p.append(line(x_release + 10, 60, x_release + 10, 290, color=OK_COL, sw=1.5, dash="3,3"))
    box_rel, _, _ = textbox(x_release + 10, 68, "Ведений відпустив SDA (видав '1' або NACK)\nПідтяжка підняла SDA до 3.3 В", size=10, pad=4, fill=OK_BG, stroke=OK_COL, color=OK_COL, bold=True)
    p.append(box_rel)

    # STOP condition box
    x_stop_center = x_stop_prep + 65
    p.append(rect(x_stop_prep + 10, 180, 110, 110, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=4))
    p.append(text(x_stop_center, 198, "Умова STOP", size=11, color="#b45309", bold=True))
    p.append(text(x_stop_center, 216, "SDA 0 → 1", size=10, color=INK))
    p.append(text(x_stop_center, 230, "при SCL = 1", size=10, color=INK))
    p.append(text(x_stop_center, 280, "Скидання автомата", size=9, color=MUTED))

    # Phases indicators at bottom
    p.append(rect(110, 315, 500, 32, fill="#eff6ff", stroke=BUS_SCL, sw=1, rx=4))
    p.append(text(360, 335, "Фаза 1: До 9 імпульсів SCL (виштовхування застряглих бітів)", size=11, color=BUS_SCL, bold=True))

    p.append(rect(620, 315, 260, 32, fill=OK_BG, stroke=OK_COL, sw=1, rx=4))
    p.append(text(750, 335, "Фаза 2: Валідний STOP + перевірка IDLE", size=11, color=OK_COL, bold=True))

    # Bottom summary box
    box_bot, _, _ = textbox(W / 2, 395,
        "Алгоритм: 1) Перевести SCL/SDA в GPIO Open-Drain; 2) Якщо SDA=0, генерувати до 9 тактів на SCL (t_LOW ≥ 5 мкс, t_HIGH ≥ 5 мкс);\n3) Перевіряти SDA на кожному такті; щойно SDA=1 — ведений відпустив шину; 4) Згенерувати умову STOP; 5) Відновити I2C HAL.",
        size=11, pad=6, fill=PANEL_BG, stroke=LINE, min_w=850)
    p.append(box_bot)

    render(os.path.join(OUT, "i2c-9clock-recovery.svg"), W, H, *p)

def fig_phantom_power():
    W, H = 940, 490
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))

    # Title
    p.append(text(W / 2, 32, "Паразитне живлення датчика (Phantom Powering) через ESD-діоди ліній I²C", size=15, bold=True))

    # 1. Left block: Microcontroller (MCU)
    p.append(rect(30, 65, 190, 345, fill=CHIP_BG, stroke=LINE, sw=1.5, rx=6))
    p.append(text(125, 90, "Мікроконтролер (MCU)", size=13, bold=True))
    p.append(text(125, 110, "V_DD_MCU = 3.3 В (ON)", size=10, color=MUTED))

    # MCU Pins
    p.append(rect(160, 155, 50, 24, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    p.append(text(185, 171, "SCL", size=11, bold=True, color=BUS_SCL))

    p.append(rect(160, 225, 50, 24, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    p.append(text(185, 241, "SDA", size=11, bold=True, color=BUS_SDA))

    p.append(rect(160, 325, 50, 24, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    p.append(text(185, 341, "PWR_EN", size=10, bold=True, color=INK))

    # 2. Top-Middle: High-Side Switch (P-MOSFET)
    p.append(rect(270, 65, 270, 75, fill=WARN_BG, stroke=WARN_COL, sw=1.5, rx=6))
    p.append(text(405, 87, "P-MOSFET Ключ (High-Side)", size=12, bold=True, color=WARN_COL))
    p.append(text(405, 105, "СТАН: РОЗІРВАНО (OFF)", size=11, color=WARN_COL, bold=True))
    p.append(text(405, 123, "Прямий шлях живлення розімкнено", size=10, color=MUTED))

    # Wire from MCU PWR_EN to P-MOSFET gate
    p.append(polyline([(210, 337), (245, 337), (245, 102), (270, 102)], color=INK, sw=1.5))
    p.append(text(240, 220, "Керування", size=10, color=INK, anchor="middle"))

    # 3. Middle: Pull-up resistors connected incorrectly to V_DD_MCU!
    p.append(rect(270, 160, 270, 115, fill="#fff1f2", stroke=WARN_COL, sw=1.2, rx=6))
    p.append(text(405, 180, "Помилка: Rp підтягнуті до 3.3 В MCU", size=11, bold=True, color=WARN_COL))

    # Pullup resistors symbols
    p.append(rect(345, 195, 45, 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=2))
    p.append(text(367, 209, "Rp1", size=10, bold=True))
    p.append(rect(420, 195, 45, 20, fill="#ffffff", stroke=LINE, sw=1.2, rx=2))
    p.append(text(442, 209, "Rp2", size=10, bold=True))

    p.append(text(405, 238, "Струм витоку: ~0.5..1.0 мА", size=10, color=WARN_COL))
    p.append(text(405, 256, "I = (3.3 В − 0.6 В) / Rp", size=10, color=MUTED))

    # 4. Right block: Sensor ASIC
    p.append(rect(590, 65, 315, 345, fill=CHIP_BG, stroke=LINE, sw=1.5, rx=6))
    p.append(text(747, 90, "Завислий I²C Давач (Sensor IC)", size=13, bold=True))

    # Sensor internal pins & power rails
    p.append(rect(605, 115, 95, 24, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=3))
    p.append(text(652, 131, "VDD_SENSOR", size=10, bold=True, color=WARN_COL))

    p.append(rect(605, 195, 45, 24, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    p.append(text(627, 211, "SCL", size=11, bold=True, color=BUS_SCL))

    p.append(rect(605, 255, 45, 24, fill="#ffffff", stroke=LINE, sw=1, rx=3))
    p.append(text(627, 271, "SDA", size=11, bold=True, color=BUS_SDA))

    # Internal ESD Clamping Diodes inside Sensor
    p.append(rect(680, 165, 205, 130, fill="#faf5ff", stroke=DIODE_COL, sw=1.2, rx=4))
    p.append(text(782, 185, "ESD-діоди захисту", size=11, bold=True, color=DIODE_COL))

    # ESD Diode 1 (SCL to VDD)
    p.append(circle(725, 235, 10, fill="#ffffff", stroke=DIODE_COL, sw=1.2))
    p.append(text(725, 239, "▲", size=10, color=DIODE_COL))
    p.append(text(725, 257, "ESD1", size=9, color=DIODE_COL))

    # ESD Diode 2 (SDA to VDD)
    p.append(circle(795, 235, 10, fill="#ffffff", stroke=DIODE_COL, sw=1.2))
    p.append(text(795, 239, "▲", size=10, color=DIODE_COL))
    p.append(text(795, 257, "ESD2", size=9, color=DIODE_COL))

    # Phantom voltage label inside Sensor
    p.append(rect(680, 310, 205, 65, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=4))
    p.append(text(782, 330, "ПАРАЗИТНА НАПРУГА:", size=10, bold=True, color=WARN_COL))
    p.append(text(782, 348, "V_DD_SENSOR ≈ 2.7 В", size=13, bold=True, color=WARN_COL))
    p.append(text(782, 365, "Чіп НЕ скидається (немає POR)!", size=9, color=WARN_COL))

    # Wires & Red Current Arrows
    p.append(polyline([(210, 167), (367, 167), (367, 195)], color=WARN_COL, sw=2))
    p.append(polyline([(210, 237), (442, 237), (442, 195)], color=WARN_COL, sw=2))

    # From pullups into SCL & SDA lines
    p.append(polyline([(367, 215), (367, 207), (605, 207)], color=WARN_COL, sw=2))
    p.append(polyline([(442, 215), (442, 267), (605, 267)], color=WARN_COL, sw=2))

    # Inside sensor: from SCL/SDA to bottom of ESD diodes
    p.append(polyline([(650, 207), (725, 207), (725, 225)], color=WARN_COL, sw=2))
    p.append(polyline([(650, 267), (795, 267), (795, 225)], color=WARN_COL, sw=2))

    # Route out from top of diodes around the box on the right side to VDD_SENSOR rail
    p.append(polyline([(725, 245), (725, 280), (845, 280), (845, 127), (700, 127)], color=WARN_COL, sw=2))
    p.append(polyline([(795, 245), (795, 280)], color=WARN_COL, sw=2))

    # Flow annotation badge
    box_flow, _, _ = textbox(405, 310,
        "Шлях струму: 3.3 В MCU → Резистори Rp → Лінії SDA/SCL →\n→ ESD-діоди давача → Внутрішня шина VDD (2.7 В)",
        size=10, pad=5, fill=WARN_BG, stroke=WARN_COL, bold=True, color=WARN_COL)
    p.append(box_flow)

    # Bottom correct engineering rules
    box_bot, _, _ = textbox(W / 2, 448,
        "Як уникнути пастки: 1) Підтяжки Rp підключати до комутованого V_DD_SENSOR (після ключа);\n2) Перед вимкненням живлення МК переводить піни SCL/SDA в LOW (0 В); 3) Встановити розрядний резистор (10–100 кОм) на V_DD_SENSOR.",
        size=11, pad=6, fill=OK_BG, stroke=OK_COL, color=INK, min_w=890)
    p.append(box_bot)

    render(os.path.join(OUT, "phantom-power-path.svg"), W, H, *p)

if __name__ == "__main__":
    fig_lockup_sequence()
    fig_9clock_recovery()
    fig_phantom_power()
    print("All figures successfully generated in img/")
