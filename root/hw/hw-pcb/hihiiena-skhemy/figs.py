# -*- coding: utf-8 -*-
"""Фігури до теми «Гігієна схеми: аркуші, ієрархія, мітки, позначення».
Запуск:  python figs.py   -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

# Локальні кольори
WIRE       = "#333333"
PWR_COLOR  = "#c0392b"  # червоний для живлення (+3.3V, +5V)
GND_COLOR  = "#2457d6"  # синій для землі
SIG_COLOR  = "#27ae60"  # зелений для інформаційних сигналів
WARN_COLOR = "#d35400"  # помаранчевий для застережень
BUS_COLOR  = "#8e44ad"  # фіолетовий для шин
PANEL_BG   = "#f8f9fa"
BAD_BG     = "#fff5f5"
GOOD_BG    = "#f4faf6"

def gnd_sym(x, y, color=GND_COLOR):
    """Символ землі: три горизонтальні риски, що спадають вниз."""
    return (
        line(x, y, x, y + 10, color=color, sw=2.0) +
        line(x - 12, y + 10, x + 12, y + 10, color=color, sw=2.0) +
        line(x - 8, y + 14, x + 8, y + 14, color=color, sw=1.8) +
        line(x - 4, y + 18, x + 4, y + 18, color=color, sw=1.5)
    )

def vcc_sym(x, y, label="+3.3V", color=PWR_COLOR):
    """Символ шини живлення: стрілка/планка вгору з підписом."""
    return (
        line(x, y, x, y - 10, color=color, sw=2.0) +
        line(x - 8, y - 10, x + 8, y - 10, color=color, sw=2.0) +
        text(x, y - 15, label, size=11, color=color, bold=True)
    )

# ── 1. Потік сигналу та живлення (Ортогональний потік) ─────────────────────────
def fig_signal_power_flow():
    W, H = 880, 480
    f = [
        text(W / 2, 28, "Ортогональний потік: сигнал зліва направо, живлення зверху вниз",
             size=18, bold=True),
        text(W / 2, 50,
             "Сигнал іде від джерела до приймача (X-вісь); струм стікає від VCC до GND (Y-вісь)",
             size=11, color=MUTED, italic=True)
    ]

    # Панель: Правильна конвенція (Еталон гігієни)
    f.append(rect(30, 75, 820, 380, fill=GOOD_BG, stroke=FIELD, sw=1.8, rx=8))
    f.append(text(80, 100, "ПРАВИЛЬНО: читання за напрямком енергії та даних", size=13, color=FIELD, bold=True, anchor="start"))

    # Напрямні осі потоків
    # Горизонтальна вісь сигналу
    f.append(arrow(180, 120, 720, 120, color=SIG_COLOR, sw=2.2))
    f.append(text(450, 112, "Потік сигналу: Вхід -> Фільтрація -> Підсилення -> Обробка (АЦП/MCU) -> Вихід", size=11, color=SIG_COLOR, bold=True))

    # Вертикальна вісь живлення
    f.append(arrow(70, 160, 70, 400, color=PWR_COLOR, sw=2.2))
    f.append(text(75, 280, "Потік живлення: від VCC (+3.3V) зверху вниз до Землі (GND)", size=10.5, color=PWR_COLOR, bold=True, anchor="start"))

    # Схемний каскад:
    # 1. Вхідний роз'єм J1
    f.append(rect(140, 200, 50, 80, fill=BG, stroke=INK, sw=1.6, rx=4))
    f.append(text(165, 230, "J1", size=12, color=INK, bold=True))
    f.append(text(165, 250, "IN", size=10, color=MUTED))
    f.append(line(190, 240, 230, 240, color=SIG_COLOR, sw=2.0))

    # 2. Фільтр низьких частот: R1 (горизонтально) + C1 (вертикально на GND)
    # R1
    f.append(rect(230, 230, 40, 20, fill=BG, stroke=INK, sw=1.5, rx=2))
    f.append(text(250, 222, "R1", size=10.5, color=INK, bold=True))
    f.append(text(250, 262, "1k", size=9.5, color=MUTED))
    f.append(line(270, 240, 310, 240, color=SIG_COLOR, sw=2.0))

    # Т-вузол фільтра
    f.append(circle(310, 240, 3.5, fill=INK, stroke=INK, sw=1))
    f.append(line(310, 240, 310, 280, color=WIRE, sw=1.8))
    # C1 (вертикально)
    f.append(line(300, 280, 320, 280, color=INK, sw=2.0))
    f.append(line(300, 286, 320, 286, color=INK, sw=2.0))
    f.append(text(335, 284, "C1 100nF", size=9.5, color=MUTED, anchor="start"))
    f.append(gnd_sym(310, 286))

    # З'єднання до ОП
    f.append(line(310, 240, 370, 240, color=SIG_COLOR, sw=2.0))

    # 3. Операційний підсилювач U1A
    # Трикутник ОП: входи (370, 230) [+], (370, 250) [-], вихід (430, 240)
    f.append('<polygon points="370,215 370,265 430,240" fill="%s" stroke="%s" stroke-width="1.8"/>' % (BG, INK))
    f.append(text(380, 232, "+", size=12, color=INK, bold=True))
    f.append(text(380, 256, "−", size=14, color=INK, bold=True))
    f.append(text(395, 244, "U1A", size=10, color=INK, bold=True))

    # Живлення ОП: VCC зверху, GND знизу
    f.append(line(395, 225, 395, 175, color=PWR_COLOR, sw=1.8))
    f.append(vcc_sym(395, 175, "+3.3V"))
    # Блокувальний конденсатор ОП
    f.append(line(435, 175, 435, 205, color=PWR_COLOR, sw=1.8))
    f.append(line(395, 175, 435, 175, color=PWR_COLOR, sw=1.8))
    f.append(circle(395, 175, 3, fill=PWR_COLOR, stroke=PWR_COLOR))
    f.append(line(425, 205, 445, 205, color=INK, sw=2.0))
    f.append(line(425, 211, 445, 211, color=INK, sw=2.0))
    f.append(text(455, 209, "C2 100nF", size=9, color=MUTED, anchor="start"))
    f.append(gnd_sym(435, 211))

    f.append(line(395, 255, 395, 320, color=GND_COLOR, sw=1.8))
    f.append(gnd_sym(395, 320))

    # Зворотний зв'язок: R2
    f.append(line(360, 252, 370, 252, color=WIRE, sw=1.8))
    f.append(line(360, 252, 360, 320, color=WIRE, sw=1.8))
    f.append(gnd_sym(360, 320))

    # Вихід ОП -> MCU
    f.append(line(430, 240, 520, 240, color=SIG_COLOR, sw=2.0))
    f.append(text(475, 230, "SIG_FILT", size=10, color=SIG_COLOR, bold=True))

    # 4. Мікроконтролер / АЦП U2
    f.append(rect(520, 180, 110, 140, fill=BG, stroke=INK, sw=1.8, rx=4))
    f.append(text(575, 205, "U2", size=13, color=INK, bold=True))
    f.append(text(575, 223, "MCU / ADC", size=10, color=MUTED))
    f.append(text(530, 244, "ADC_IN0", size=9.5, color=SIG_COLOR, anchor="start"))
    f.append(text(620, 244, "PWM_OUT", size=9.5, color=SIG_COLOR, anchor="end"))
    f.append(text(575, 195, "VDD", size=9, color=PWR_COLOR))
    f.append(text(575, 310, "VSS", size=9, color=GND_COLOR))

    # Живлення MCU
    f.append(line(575, 180, 575, 155, color=PWR_COLOR, sw=1.8))
    f.append(vcc_sym(575, 155, "+3.3V"))
    f.append(line(575, 320, 575, 345, color=GND_COLOR, sw=1.8))
    f.append(gnd_sym(575, 345))

    # 5. Вихідний драйвер Q1 (MOSFET) та навантаження
    f.append(line(630, 240, 690, 240, color=SIG_COLOR, sw=2.0))
    f.append(rect(690, 220, 40, 50, fill=BG, stroke=INK, sw=1.5, rx=3))
    f.append(text(710, 240, "Q1", size=11, color=INK, bold=True))
    f.append(text(710, 258, "NFET", size=9, color=MUTED))
    f.append(line(730, 240, 770, 240, color=SIG_COLOR, sw=2.0))

    # 6. Вихідний роз'єм J2
    f.append(rect(770, 200, 50, 80, fill=BG, stroke=INK, sw=1.6, rx=4))
    f.append(text(795, 230, "J2", size=12, color=INK, bold=True))
    f.append(text(795, 250, "OUT", size=10, color=MUTED))

    # Нижній блок правил-підказок
    f.append(rect(140, 390, 680, 50, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(480, 410, "Золоте правило гігієни: погляд рухається природно (входи ліворуч, виходи праворуч).", size=10.5, color=INK, bold=True))
    f.append(text(480, 428, "Потенціал спадає зверху вниз: верхній край аркуша — живлення (+V), нижній — земля (GND).", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "signal-power-flow.svg"), W, H, *f)

# ── 2. Ієрархічна структура та типи міток ─────────────────────────────────────
def fig_hierarchical_structure():
    W, H = 880, 520
    f = [
        text(W / 2, 28, "Ієрархія схеми: зв'язок аркушів, шин та міток",
             size=18, bold=True),
        text(W / 2, 50,
             "Розмежування областей видимості: локальні мітки, ієрархічні порти та глобальні шини",
             size=11, color=MUTED, italic=True)
    ]

    # Головний аркуш (Root Sheet)
    f.append(rect(40, 75, 800, 425, fill=PANEL_BG, stroke=LINE, sw=1.8, rx=8))
    f.append(text(60, 100, "ГОЛОВНИЙ АРКУШ (Root Sheet: top.kicad_sch)", size=13, color=INK, bold=True, anchor="start"))

    # Блок 1: Живлення (Power Supply Unit)
    f.append(rect(80, 130, 200, 140, fill=BG, stroke=INK, sw=1.6, rx=6))
    f.append(text(180, 155, "БЛОК-АРКУШ: PSU", size=12, color=PWR_COLOR, bold=True))
    f.append(text(180, 172, "file: psu.kicad_sch", size=9.5, color=MUTED))
    # Порти блоку
    f.append(rect(65, 195, 15, 16, fill="none", stroke=WARN_COLOR, sw=1.4))
    f.append(text(90, 207, "VIN", size=9.5, color=INK, anchor="start"))
    f.append(rect(280, 195, 15, 16, fill="none", stroke=PWR_COLOR, sw=1.4))
    f.append(text(270, 207, "+3V3", size=9.5, color=PWR_COLOR, bold=True, anchor="end"))
    f.append(rect(280, 230, 15, 16, fill="none", stroke=GND_COLOR, sw=1.4))
    f.append(text(270, 242, "GND", size=9.5, color=GND_COLOR, bold=True, anchor="end"))

    # Блок 2: Аналоговий фронтенд (Analog Frontend)
    f.append(rect(80, 310, 200, 160, fill=BG, stroke=INK, sw=1.6, rx=6))
    f.append(text(180, 335, "БЛОК-АРКУШ: SENSORS", size=12, color=FIELD, bold=True))
    f.append(text(180, 352, "file: sensors.kicad_sch", size=9.5, color=MUTED))
    # Порти
    f.append(rect(65, 380, 15, 16, fill="none", stroke=FIELD, sw=1.4))
    f.append(text(90, 392, "AIN[0..3]", size=9.5, color=FIELD, bold=True, anchor="start"))
    f.append(rect(280, 380, 15, 16, fill="none", stroke=BUS_COLOR, sw=1.4))
    f.append(text(270, 392, "SPI_BUS", size=9.5, color=BUS_COLOR, bold=True, anchor="end"))
    f.append(rect(280, 420, 15, 16, fill="none", stroke=FIELD, sw=1.4))
    f.append(text(270, 432, "IRQ_ALERT", size=9.5, color=FIELD, bold=True, anchor="end"))

    # Блок 3: Мікроконтролер (MCU Core)
    f.append(rect(380, 130, 240, 340, fill=BG, stroke=INK, sw=1.8, rx=6))
    f.append(text(500, 155, "БЛОК-АРКУШ: MCU_CORE", size=13, color=INK, bold=True))
    f.append(text(500, 172, "file: mcu_core.kicad_sch", size=10, color=MUTED))
    # Порти MCU
    f.append(rect(365, 195, 15, 16, fill="none", stroke=PWR_COLOR, sw=1.4))
    f.append(text(390, 207, "+3V3 (Global)", size=9, color=PWR_COLOR, bold=True, anchor="start"))
    f.append(rect(365, 230, 15, 16, fill="none", stroke=GND_COLOR, sw=1.4))
    f.append(text(390, 242, "GND (Global)", size=9, color=GND_COLOR, bold=True, anchor="start"))

    f.append(rect(365, 380, 15, 16, fill="none", stroke=BUS_COLOR, sw=1.4))
    f.append(text(390, 392, "SPI_BUS", size=9.5, color=BUS_COLOR, bold=True, anchor="start"))
    f.append(rect(365, 420, 15, 16, fill="none", stroke=FIELD, sw=1.4))
    f.append(text(390, 432, "IRQ_ALERT", size=9.5, color=FIELD, bold=True, anchor="start"))

    f.append(rect(620, 260, 15, 16, fill="none", stroke=BUS_COLOR, sw=1.4))
    f.append(text(610, 272, "UART_TXD", size=9.5, color=BUS_COLOR, bold=True, anchor="end"))
    f.append(rect(620, 290, 15, 16, fill="none", stroke=BUS_COLOR, sw=1.4))
    f.append(text(610, 302, "UART_RXD", size=9.5, color=BUS_COLOR, bold=True, anchor="end"))

    # Блок 4: Інтерфейси (Comm & Ports)
    f.append(rect(680, 210, 140, 160, fill=BG, stroke=INK, sw=1.6, rx=6))
    f.append(text(750, 235, "COMM / USB", size=12, color=INK, bold=True))
    f.append(text(750, 250, "file: comm.kicad_sch", size=9, color=MUTED))
    f.append(rect(665, 260, 15, 16, fill="none", stroke=BUS_COLOR, sw=1.4))
    f.append(text(690, 272, "UART_TXD", size=9, color=BUS_COLOR, anchor="start"))
    f.append(rect(665, 290, 15, 16, fill="none", stroke=BUS_COLOR, sw=1.4))
    f.append(text(690, 302, "UART_RXD", size=9, color=BUS_COLOR, anchor="start"))

    # Лінії та шинні з'єднання між блоками
    # Векторна шина SPI_BUS (товста лінія)
    f.append(line(290, 388, 370, 388, color=BUS_COLOR, sw=3.5))
    f.append(text(330, 378, "Шина SPI", size=10, color=BUS_COLOR, bold=True))

    # Одинарний ієрархічний сигнал IRQ_ALERT
    f.append(line(290, 428, 370, 428, color=FIELD, sw=2.0))
    f.append(text(330, 420, "Сигнал", size=9.5, color=FIELD))

    # UART лінії
    f.append(line(630, 268, 670, 268, color=BUS_COLOR, sw=2.0))
    f.append(line(630, 298, 670, 298, color=BUS_COLOR, sw=2.0))

    # Таблиця-легенда типів міток внизу
    f.append(rect(60, 440, 760, 50, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(180, 460, "1. Локальна мітка (Local Net):", size=10, color=INK, bold=True))
    f.append(text(180, 475, "діє ВИКЛЮЧНО на своєму аркуші", size=9, color=MUTED))

    f.append(text(450, 460, "2. Ієрархічний порт (Sheet Pin):", size=10, color=BUS_COLOR, bold=True))
    f.append(text(450, 475, "прокидає ланцюг крізь межу блоку", size=9, color=MUTED))

    f.append(text(700, 460, "3. Глобальна мітка (Power):", size=10, color=PWR_COLOR, bold=True))
    f.append(text(700, 475, "зшиває VCC/GND по всьому проекту", size=9, color=MUTED))

    render(os.path.join(IMG, "hierarchical-structure.svg"), W, H, *f)

if __name__ == "__main__":
    fig_signal_power_flow()
    fig_hierarchical_structure()
    print("OK: 2 SVG generated in img/")
