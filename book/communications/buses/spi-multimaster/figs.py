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
MUTED_BG = "#f8fafc"
BORDER   = "#cbd5e1"


def polyline(pts, color=LINE, sw=1.5, fill="none"):
    points = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<polyline points="{points}" fill="{fill}" stroke="{color}" stroke-width="{sw:.1f}"/>'


def dashed_rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.5, rx=6, dash="4 4"):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}" stroke-dasharray="{dash}"/>')


def fig_topologies_comparison():
    W, H = 860, 440
    p = []
    
    # 1. Independent CS (Star)
    p.append(rect(20, 45, 260, 360, fill=MUTED_BG, stroke=BORDER, sw=1.5, rx=8))
    p.append(textbox(150, 70, "1. Зірка (Окремі CS)", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    # Master
    p.append(rect(35, 105, 70, 160, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(70, 130, "Master", size=10.5, color=BUS_COL, bold=True))
    p.append(text(70, 160, "CS0", size=9.5, color=INK))
    p.append(text(70, 190, "CS1", size=9.5, color=INK))
    p.append(text(70, 220, "CS2", size=9.5, color=INK))
    p.append(text(70, 250, "Bus", size=9.5, color=MUTED))
    
    # Slaves
    for i, name in enumerate(["Slave 0", "Slave 1", "Slave 2"]):
        sy = 105 + i * 55
        p.append(rect(185, sy, 80, 45, fill="#ffffff", stroke=OK_COL, sw=1.4, rx=4))
        p.append(text(225, sy + 27, name, size=10, color=OK_COL, bold=True))
        # CS lines
        p.append(line(105, 160 + i * 30, 185, sy + 22, color=ACCENT, sw=1.5))
    
    # Bus connection note
    p.append(line(105, 250, 145, 250, color=BUS_COL, sw=2))
    p.append(line(145, 135, 145, 275, color=BUS_COL, sw=1.5, dash="2 2"))
    p.append(text(150, 310, "SCK, MOSI, MISO спільні", size=9.5, color=MUTED, bold=True))
    p.append(text(150, 334, "Ніжки: 3 + N (росте лінійно)", size=9.5, color=INK))
    p.append(text(150, 358, "Доступ: довільний, миттєвий", size=9.5, color=OK_COL, bold=True))
    p.append(text(150, 382, "Режими: різні (динамічні)", size=9.5, color=OK_COL))
    
    # 2. Daisy-Chain
    p.append(rect(300, 45, 260, 360, fill=MUTED_BG, stroke=BORDER, sw=1.5, rx=8))
    p.append(textbox(430, 70, "2. Ланцюг (Daisy-Chain)", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    # Master
    p.append(rect(315, 105, 65, 160, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(347, 130, "Master", size=10.5, color=BUS_COL, bold=True))
    p.append(text(347, 165, "CS (1)", size=9.5, color=ACCENT, bold=True))
    p.append(text(347, 200, "MOSI", size=9.5, color=BUS_COL))
    p.append(text(347, 235, "MISO", size=9.5, color=OK_COL))
    
    # Slaves in series
    p.append(rect(450, 105, 95, 45, fill="#ffffff", stroke=OK_COL, sw=1.4, rx=4))
    p.append(text(497, 132, "Slave 0", size=10, color=OK_COL, bold=True))
    
    p.append(rect(450, 162, 95, 45, fill="#ffffff", stroke=OK_COL, sw=1.4, rx=4))
    p.append(text(497, 189, "Slave 1", size=10, color=OK_COL, bold=True))
    
    p.append(rect(450, 220, 95, 45, fill="#ffffff", stroke=OK_COL, sw=1.4, rx=4))
    p.append(text(497, 247, "Slave 2", size=10, color=OK_COL, bold=True))
    
    # Cascade lines
    p.append(line(380, 200, 450, 127, color=BUS_COL, sw=1.5)) # MOSI -> S0
    p.append(line(497, 150, 497, 162, color=BUS_COL, sw=1.5)) # S0 -> S1
    p.append(line(497, 207, 497, 220, color=BUS_COL, sw=1.5)) # S1 -> S2
    p.append(polyline([(497, 265), (497, 280), (395, 280), (395, 235), (380, 235)], color=OK_COL, sw=1.5)) # S2 -> MISO
    
    # Common CS
    p.append(line(380, 165, 420, 165, color=ACCENT, sw=1.5))
    p.append(line(420, 115, 420, 230, color=ACCENT, sw=1.5))
    p.append(line(420, 115, 450, 115, color=ACCENT, sw=1.5))
    p.append(line(420, 172, 450, 172, color=ACCENT, sw=1.5))
    p.append(line(420, 230, 450, 230, color=ACCENT, sw=1.5))
    
    p.append(text(430, 310, "Єдиний довгий зсувний регістр", size=9.5, color=MUTED, bold=True))
    p.append(text(430, 334, "Ніжки: завжди 4 (фіксовано)", size=9.5, color=OK_COL, bold=True))
    p.append(text(430, 358, "Доступ: послідовний (зсув N слів)", size=9.5, color=WARN_COL))
    p.append(text(430, 382, "Режими: строго однакові", size=9.5, color=WARN_COL))
    
    # 3. Decoder
    p.append(rect(580, 45, 260, 360, fill=MUTED_BG, stroke=BORDER, sw=1.5, rx=8))
    p.append(textbox(710, 70, "3. Дешифратор (74HC138)", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    # Master
    p.append(rect(595, 105, 65, 160, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(627, 130, "Master", size=10.5, color=BUS_COL, bold=True))
    p.append(text(627, 160, "Addr k", size=9.5, color=ACCENT))
    p.append(text(627, 190, "Enable", size=9.5, color=BUS_COL))
    p.append(text(627, 250, "Bus", size=9.5, color=MUTED))
    
    # Decoder 74HC138
    p.append(rect(675, 135, 60, 95, fill="#ffffff", stroke=ACCENT, sw=1.5, rx=4))
    p.append(text(705, 160, "74HC138", size=9.5, color=ACCENT, bold=True))
    p.append(text(705, 180, "3 → 8", size=9.5, color=MUTED))
    p.append(text(705, 205, "Дешифр.", size=9.5, color=INK))
    
    # Lines Master -> Decoder
    p.append(line(660, 160, 675, 160, color=ACCENT, sw=1.5))
    p.append(line(660, 190, 675, 190, color=BUS_COL, sw=1.5))
    
    # Slaves
    for i in range(3):
        sy = 105 + i * 55
        p.append(rect(755, sy, 70, 45, fill="#ffffff", stroke=OK_COL, sw=1.4, rx=4))
        p.append(text(790, sy + 27, f"Slave {i}", size=9.5, color=OK_COL, bold=True))
        p.append(line(735, 155 + i * 25, 755, sy + 22, color=ACCENT, sw=1.3))
    
    p.append(text(710, 310, "Демультиплексування ліній CS", size=9.5, color=MUTED, bold=True))
    p.append(text(710, 334, "Ніжки: 3 + k адрес + Enable", size=9.5, color=INK))
    p.append(text(710, 358, "Доступ: довільний (через строб)", size=9.5, color=OK_COL, bold=True))
    p.append(text(710, 382, "Апаратура: додатковий чіп", size=9.5, color=MUTED))
    
    p.append(text(W / 2, H - 12, "Порівняння трьох базових архітектур масштабування ведених пристроїв на шині SPI", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "topologies-comparison.svg"), W, H, *p, title="Топології підключення ведених на шині SPI")


def fig_miso_tristate_leakage():
    W, H = 860, 400
    p = []
    
    # Left Box: Active vs Inactive Tristate
    p.append(rect(30, 45, 370, 315, fill=MUTED_BG, stroke=BORDER, sw=1.5, rx=8))
    p.append(textbox(215, 70, "Внутрішній вихідний каскад MISO", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    # Circuit schematic inside
    # VCC rail
    p.append(line(100, 110, 330, 110, color=WARN_COL, sw=2))
    p.append(text(215, 100, "VCC (+3.3V)", size=10, color=WARN_COL, bold=True))
    
    # P-MOSFET
    p.append(rect(110, 130, 80, 50, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(150, 150, "P-MOS", size=9.5, color=BUS_COL, bold=True))
    p.append(text(150, 168, "R_on ≈ 30Ω", size=9, color=MUTED))
    p.append(line(150, 110, 150, 130, color=WARN_COL, sw=1.5))
    
    # Output node MISO
    p.append(circle(215, 205, 5, fill=BUS_COL, stroke=BUS_COL))
    p.append(line(150, 180, 215, 205, color=BUS_COL, sw=1.5))
    
    # N-MOSFET
    p.append(rect(110, 230, 80, 50, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(150, 250, "N-MOS", size=9.5, color=BUS_COL, bold=True))
    p.append(text(150, 268, "R_on ≈ 30Ω", size=9, color=MUTED))
    p.append(line(150, 205, 215, 205, color=BUS_COL, sw=1.5))
    p.append(line(150, 280, 150, 310, color=INK, sw=1.5))
    
    # GND rail
    p.append(line(100, 310, 330, 310, color=INK, sw=2))
    p.append(text(215, 330, "GND (0V)", size=10, color=INK, bold=True))
    
    # States description
    p.append(rect(240, 135, 150, 60, fill=OK_BG, stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(315, 153, "CS = 0 (Активний):", size=9.5, color=OK_COL, bold=True))
    p.append(text(315, 170, "Один ключ замкнено,", size=9, color=INK))
    p.append(text(315, 185, "вихід жене 0 або 1", size=9, color=INK))
    
    p.append(rect(240, 220, 150, 60, fill="#fef8ee", stroke=ACCENT, sw=1.2, rx=4))
    p.append(text(315, 238, "CS = 1 (Неактивний):", size=9.5, color=ACCENT, bold=True))
    p.append(text(315, 255, "Обидва ключі ВИМК,", size=9, color=INK))
    p.append(text(315, 270, "стан High-Z (високоомний)", size=9, color=INK))
    
    # Right Box: Bus Loading Model (N Slaves on MISO)
    p.append(rect(430, 45, 400, 315, fill=MUTED_BG, stroke=BORDER, sw=1.5, rx=8))
    p.append(textbox(630, 70, "Еквівалентна схема навантаження MISO", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    # MISO Bus backbone
    p.append(line(450, 130, 810, 130, color=BUS_COL, sw=2.5))
    p.append(text(495, 118, "Спільна лінія MISO", size=9.5, color=BUS_COL, bold=True))
    
    # Master Receiver
    p.append(rect(450, 160, 80, 60, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=4))
    p.append(text(490, 185, "Master RX", size=9.5, color=BUS_COL, bold=True))
    p.append(text(490, 205, "C_in ≈ 5 пФ", size=9, color=MUTED))
    p.append(line(490, 130, 490, 160, color=BUS_COL, sw=1.5))
    
    # Slave 1 (Active)
    p.append(rect(550, 160, 80, 60, fill=OK_BG, stroke=OK_COL, sw=1.5, rx=4))
    p.append(text(590, 180, "Slave 0 (CS=0)", size=9.5, color=OK_COL, bold=True))
    p.append(text(590, 198, "Драйвер ON", size=9, color=OK_COL))
    p.append(text(590, 212, "R_on ≈ 30Ω", size=9, color=MUTED))
    p.append(line(590, 130, 590, 160, color=OK_COL, sw=2))
    
    # Slaves in High-Z (Capacitances & Leakages)
    p.append(rect(650, 160, 80, 60, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(690, 180, "Slave 1 (High-Z)", size=9, color=INK, bold=True))
    p.append(text(690, 198, "C_out ≈ 10 пФ", size=9, color=ACCENT))
    p.append(text(690, 212, "I_leak ≤ 1 мкА", size=9, color=WARN_COL))
    p.append(line(690, 130, 690, 160, color=MUTED, sw=1.2))
    
    p.append(rect(745, 160, 75, 60, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(782, 180, "Slave N (High-Z)", size=9, color=INK, bold=True))
    p.append(text(782, 198, "C_out ≈ 10 пФ", size=9, color=ACCENT))
    p.append(text(782, 212, "I_leak ≤ 1 мкА", size=9, color=WARN_COL))
    p.append(line(782, 130, 782, 160, color=MUTED, sw=1.2))
    
    # Formula box below
    p.append(rect(450, 240, 360, 105, fill="#ffffff", stroke=ACCENT, sw=1.4, rx=6))
    p.append(text(630, 260, "Сумарна ємність та час наростання фронту:", size=9.5, color=ACCENT, bold=True))
    p.append(text(630, 282, "C_total = C_master + N · C_pin + C_trace ≈ 200...400 пФ", size=9, color=INK))
    p.append(text(630, 308, "t_rise ≈ 2.2 · R_on · C_total  →  обмежує частоту шини (f_max)", size=9, color=WARN_COL, bold=True))
    p.append(text(630, 330, "При N > 10 зростання t_rise деформує меандр на SCK/MISO", size=9, color=MUTED))
    
    p.append(text(W / 2, H - 12, "Тристабільна логіка виходу MISO та накопичення паразитної ємності при підключенні десятків мікросхем", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "miso-tristate-leakage.svg"), W, H, *p, title="Фізика лінії MISO: тристабільний вихід та паразитна ємність")


def fig_dynamic_reconfig_timing():
    W, H = 860, 420
    p = []
    
    # Grid lines / Phases
    phases = [
        (40, 200, "Транзакція 1 (Flash: Mode 0, 40 МГц)", OK_BG, OK_COL),
        (200, 480, "ФАЗА РЕКОНФІГУРАЦІЇ (Усі CS = 1)", "#fef2f2", WARN_COL),
        (480, 820, "Транзакція 2 (Sensor: Mode 3, 5 МГц)", OK_BG, OK_COL)
    ]
    for x1, x2, label, bg, col in phases:
        p.append(dashed_rect(x1, 45, x2 - x1, 330, fill=bg, stroke=col, sw=1, rx=4, dash="3 3"))
        p.append(text((x1 + x2) / 2, 65, label, size=9.5, color=col, bold=True))
        
    # Signals Labels
    p.append(text(50, 100, "CS_Flash (Mode 0)", size=9.5, color=INK, bold=True, anchor="start"))
    p.append(text(50, 160, "CS_Sensor (Mode 3)", size=9.5, color=INK, bold=True, anchor="start"))
    p.append(text(50, 230, "SCK (Тактовий сигнал)", size=9.5, color=BUS_COL, bold=True, anchor="start"))
    p.append(text(50, 305, "MOSI (Дані)", size=9.5, color=ACCENT, bold=True, anchor="start"))
    
    # Waveform CS_Flash: Active low in Phase 1, then high
    p.append(polyline([(200, 115), (200, 90), (40, 90)], color=OK_COL, sw=2))
    p.append(polyline([(200, 90), (820, 90)], color=MUTED, sw=1.5))
    
    # Waveform CS_Sensor: High in Phase 1 & 2, active low in Phase 3
    p.append(polyline([(40, 150), (520, 150)], color=MUTED, sw=1.5))
    p.append(polyline([(520, 150), (520, 175), (800, 175), (800, 150)], color=OK_COL, sw=2))
    
    # Waveform SCK:
    # Phase 1 (Mode 0): Clock bursts with Idle = LOW (0V)
    p.append(polyline([
        (40, 245), (60, 245), (70, 220), (80, 245), (90, 220), (100, 245),
        (110, 220), (120, 245), (130, 220), (140, 245), (200, 245)
    ], color=BUS_COL, sw=2))
    
    # Phase 2 (Reconfig): SCK changes idle level from LOW to HIGH!
    p.append(polyline([(200, 245), (330, 245)], color=BUS_COL, sw=2))
    p.append(polyline([(330, 245), (350, 220), (480, 220)], color=WARN_COL, sw=2.5)) # Glitch/Transition in idle state
    
    # Phase 3 (Mode 3): Clock bursts with Idle = HIGH (+3.3V)
    p.append(polyline([
        (480, 220), (540, 220), (560, 245), (580, 220), (600, 245), (620, 220),
        (640, 245), (660, 220), (680, 245), (700, 220), (720, 245), (740, 220),
        (820, 220)
    ], color=BUS_COL, sw=2))
    
    # Critical warning box in Phase 2
    p.append(rect(215, 115, 250, 85, fill="#ffffff", stroke=WARN_COL, sw=1.5, rx=5))
    p.append(text(340, 135, "БЕЗПЕЧНА РЕКОНФІГУРАЦІЯ", size=9.5, color=WARN_COL, bold=True))
    p.append(text(340, 153, "1. CS_Flash піднято у 1 (OFF)", size=9, color=INK))
    p.append(text(340, 170, "2. Зміна CPOL=0 → CPOL=1 генерує", size=9, color=INK))
    p.append(text(340, 187, "перепад SCK при ВИМКНЕНИХ CS!", size=9, color=WARN_COL, bold=True))
    
    # Annotations for setup times
    p.append(line(350, 220, 350, 260, color=WARN_COL, sw=1, dash="2 2"))
    p.append(line(520, 150, 520, 260, color=OK_COL, sw=1, dash="2 2"))
    p.append(line(540, 220, 540, 260, color=OK_COL, sw=1, dash="2 2"))
    
    p.append(text(435, 270, "t_settle (стабілізація рівня)", size=9, color=MUTED, bold=True))
    p.append(text(530, 285, "t_lead", size=9, color=OK_COL, bold=True))
    
    # MOSI line
    p.append(line(40, 305, 200, 305, color=ACCENT, sw=2))
    p.append(line(200, 305, 520, 305, color=MUTED, sw=1.2, dash="3 3"))
    p.append(line(520, 305, 780, 305, color=ACCENT, sw=2))
    
    p.append(text(W / 2, H - 12, "Часова послідовність безпечної динамічної зміни режимів CPOL/CPHA: перепад спокою ізольовано деактивацією CS", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "dynamic-reconfig-timing.svg"), W, H, *p, title="Динамічна реконфігурація регістрів SPI майстра")


def fig_multimaster_collision():
    W, H = 860, 400
    p = []
    
    # Master 1 (Host A)
    p.append(rect(40, 60, 190, 280, fill=MUTED_BG, stroke=BUS_COL, sw=1.8, rx=6))
    p.append(textbox(135, 85, "Master 1 (MCU A)", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    p.append(rect(55, 120, 160, 45, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=4))
    p.append(text(135, 140, "SCK Вихід: HIGH (+3.3V)", size=9.5, color=WARN_COL, bold=True))
    p.append(text(135, 155, "Верхній P-MOS УВІМКНЕНО", size=9, color=INK))
    
    p.append(rect(55, 180, 160, 45, fill=OK_BG, stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(135, 200, "MOSI Вихід: LOW (0V)", size=9.5, color=OK_COL, bold=True))
    p.append(text(135, 215, "Нижній N-MOS УВІМКНЕНО", size=9, color=INK))
    
    p.append(text(135, 275, "Вважає себе єдиним", size=9.5, color=MUTED, italic=True))
    p.append(text(135, 295, "господарем шини!", size=9.5, color=MUTED, italic=True))
    
    # Master 2 (Host B)
    p.append(rect(630, 60, 190, 280, fill=MUTED_BG, stroke=BUS_COL, sw=1.8, rx=6))
    p.append(textbox(725, 85, "Master 2 (MCU B)", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    p.append(rect(645, 120, 160, 45, fill=OK_BG, stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(725, 140, "SCK Вихід: LOW (0V)", size=9.5, color=OK_COL, bold=True))
    p.append(text(725, 155, "Нижній N-MOS УВІМКНЕНО", size=9, color=INK))
    
    p.append(rect(645, 180, 160, 45, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=4))
    p.append(text(725, 200, "MOSI Вихід: HIGH (+3.3V)", size=9.5, color=WARN_COL, bold=True))
    p.append(text(725, 215, "Верхній P-MOS УВІМКНЕНО", size=9, color=INK))
    
    p.append(text(725, 275, "Одночасно почав передачу", size=9.5, color=MUTED, italic=True))
    p.append(text(725, 295, "без арбітражу!", size=9.5, color=MUTED, italic=True))
    
    # Central Contention Bus Wires
    # SCK Line
    p.append(line(230, 142, 630, 142, color=WARN_COL, sw=3))
    p.append(arrow(240, 142, 410, 142, color=WARN_COL, sw=2.5))
    p.append(arrow(620, 142, 450, 142, color=OK_COL, sw=2.5))
    
    # MOSI Line
    p.append(line(230, 202, 630, 202, color=WARN_COL, sw=3))
    p.append(arrow(620, 202, 450, 202, color=WARN_COL, sw=2.5))
    p.append(arrow(240, 202, 410, 202, color=OK_COL, sw=2.5))
    
    # Contention Highlight Box
    p.append(rect(265, 95, 300, 205, fill="#fee2e2", stroke=WARN_COL, sw=2, rx=8))
    p.append(text(415, 120, "⚡ КАТАСТРОФІЧНИЙ КОНФЛІКТ ⚡", size=10.5, color=WARN_COL, bold=True))
    p.append(text(415, 140, "Зустрічне ввімкнення Push-Pull виходів", size=9.5, color=INK, bold=True))
    p.append(text(415, 165, "• Пряме КЗ: VCC ──> P-MOS ──> N-MOS ──> GND", size=9, color=INK))
    p.append(text(415, 187, "• Наскрізний струм: I_short > 60..100 мА", size=9, color=WARN_COL, bold=True))
    p.append(text(415, 207, "• Напруга лінії: невизначені 1.4..1.8 В", size=9, color=INK))
    p.append(text(415, 227, "• Локальний перегрів та деградація виводів", size=9, color=WARN_COL))
    p.append(text(415, 247, "• Руйнування стану всіх підключених ведених", size=9, color=INK))
    p.append(text(415, 267, "• Відсутність арбітражу спалює ключі MCU", size=9, color=WARN_COL, bold=True))
    
    p.append(text(W / 2, H - 12, "Наслідки одночасної передачі двох ведучих на шині SPI без апаратного арбітражу", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "multimaster-collision.svg"), W, H, *p, title="Зустрічне зіткнення виходів у небезпечній топології Multi-Master SPI")


def fig_mode_fault_arbitration():
    W, H = 860, 420
    p = []
    
    # 1. Mode Fault Mechanism (Left)
    p.append(rect(30, 45, 380, 330, fill=MUTED_BG, stroke=BORDER, sw=1.5, rx=8))
    p.append(textbox(220, 70, "Апаратний захист: Mode Fault (MODF)", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    # SPI Controller inside MCU
    p.append(rect(50, 100, 340, 130, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=6))
    p.append(text(130, 122, "MCU SPI Controller (MSTR=1)", size=10, color=BUS_COL, bold=True))
    
    # Pins & Registers
    p.append(rect(65, 140, 90, 40, fill=WARN_BG, stroke=WARN_COL, sw=1.2, rx=4))
    p.append(text(110, 158, "NSS Pin (Вхід)", size=9, color=WARN_COL, bold=True))
    p.append(text(110, 172, "Зовнішній LOW (0V)", size=9, color=INK))
    
    p.append(rect(170, 140, 100, 40, fill="#fef8ee", stroke=ACCENT, sw=1.2, rx=4))
    p.append(text(220, 158, "Логіка MODF", size=9.5, color=ACCENT, bold=True))
    p.append(text(220, 172, "Фіксація колізії", size=9, color=INK))
    
    p.append(rect(285, 140, 95, 40, fill=OK_BG, stroke=OK_COL, sw=1.2, rx=4))
    p.append(text(332, 158, "MSTR = 0", size=9.5, color=OK_COL, bold=True))
    p.append(text(332, 172, "Виходи ──> Hi-Z", size=9, color=OK_COL))
    
    p.append(arrow(155, 160, 170, 160, color=WARN_COL, sw=1.5))
    p.append(arrow(270, 160, 285, 160, color=ACCENT, sw=1.5))
    
    # Steps
    p.append(rect(50, 245, 340, 115, fill="#ffffff", stroke=BORDER, sw=1.2, rx=6))
    p.append(text(220, 265, "Апаратна послідовність при MODF:", size=9.5, color=INK, bold=True))
    p.append(text(220, 285, "1. Інший Master опускає NSS цього контролера в 0", size=9, color=INK))
    p.append(text(220, 303, "2. Апаратура автоматично скидає біт MSTR в 0", size=9, color=OK_COL, bold=True))
    p.append(text(220, 320, "3. SCK/MOSI миттєво відключаються (Hi-Z) без КЗ", size=9, color=OK_COL, bold=True))
    p.append(text(220, 337, "4. Генерується переривання SPI_IRQ (Mode Fault)", size=9, color=ACCENT))
    p.append(text(220, 352, "5. Контролер стає слухачем замість майстра", size=9, color=MUTED))
    
    # 2. Handshake Arbiter Architecture (Right)
    p.append(rect(430, 45, 400, 330, fill=MUTED_BG, stroke=BORDER, sw=1.5, rx=8))
    p.append(textbox(630, 70, "Безпечна архітектура: Лінія BUSY / REQ", size=11, color=BUS_COL, bold=True, fill=BG, stroke=BUS_COL, pad=5)[0])
    
    # Shared BUSY line with Open-Drain
    p.append(line(450, 120, 810, 120, color=ACCENT, sw=2.5))
    p.append(text(630, 110, "Спільна лінія BUS_BUSY (Open-Drain + Підтяжка 4.7 кОм)", size=9.5, color=ACCENT, bold=True))
    
    # Master A
    p.append(rect(450, 150, 160, 100, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=6))
    p.append(text(530, 172, "Master A (MCU 1)", size=10, color=BUS_COL, bold=True))
    p.append(text(530, 195, "1. Перевіряє BUSY==1", size=9, color=INK))
    p.append(text(530, 212, "2. Опускає BUSY=0 (Lock)", size=9, color=OK_COL, bold=True))
    p.append(text(530, 230, "3. Проводить транзакцію", size=9, color=INK))
    p.append(line(530, 120, 530, 150, color=ACCENT, sw=1.5))
    
    # Master B
    p.append(rect(650, 150, 160, 100, fill="#ffffff", stroke=BUS_COL, sw=1.5, rx=6))
    p.append(text(730, 172, "Master B (MCU 2)", size=10, color=BUS_COL, bold=True))
    p.append(text(730, 195, "Бачить BUSY == 0", size=9, color=WARN_COL, bold=True))
    p.append(text(730, 212, "→ Чекає звільнення,", size=9, color=INK))
    p.append(text(730, 230, "виходи тримає в Hi-Z", size=9, color=OK_COL))
    p.append(line(730, 120, 730, 150, color=ACCENT, sw=1.5))
    
    # Bottom Note
    p.append(rect(450, 270, 360, 90, fill=OK_BG, stroke=OK_COL, sw=1.2, rx=6))
    p.append(text(630, 290, "Переваги Handshake арбітражу:", size=9.5, color=OK_COL, bold=True))
    p.append(text(630, 310, "• Нульовий ризик електричного короткого замикання", size=9, color=INK))
    p.append(text(630, 328, "• Повна сумісність зі стандартними SPI веденими", size=9, color=INK))
    p.append(text(630, 346, "• Детермінований час очікування шини", size=9, color=MUTED))
    
    p.append(text(W / 2, H - 12, "Апаратне скидання режиму при помилці MODF та схемотехніка арбітражу через спільну лінію BUSY", size=10.5, color=MUTED, italic=True))
    
    render(os.path.join(OUT, "mode-fault-arbitration.svg"), W, H, *p, title="Апаратний захист Mode Fault та арбітраж шини SPI")


if __name__ == "__main__":
    fig_topologies_comparison()
    fig_miso_tristate_leakage()
    fig_dynamic_reconfig_timing()
    fig_multimaster_collision()
    fig_mode_fault_arbitration()
    print("OK: All 5 figures generated successfully in", OUT)
