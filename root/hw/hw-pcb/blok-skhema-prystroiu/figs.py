# -*- coding: utf-8 -*-
"""Фігури теми «Блок-схема пристрою: вузли, зв'язки, межі». Запуск: python figs.py -> ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_system_block_diagram():
    """Комплексна блок-схема вбудованого промислового приладу з функціональними доменами."""
    f = []
    
    # ── Межі функціональних доменів (фонові рамки) ──
    # 1. Домен живлення (ліворуч зверху)
    f.append(rect(20, 50, 230, 240, fill="#fbfcfd", stroke="#94a3b8", sw=1.5, rx=6))
    f.append(text(135, 68, "Домен живлення (Power Tree)", size=11, color="#475569", bold=True))
    
    # 2. Прецизійний аналоговий домен (ліворуч знизу)
    f.append(rect(20, 305, 230, 235, fill="#f4fbf7", stroke="#27ae60", sw=1.5, rx=6))
    f.append(text(135, 323, "Прецизійний аналоговий домен", size=11, color="#1e8449", bold=True))
    
    # 3. Головний цифровий домен (центр)
    f.append(rect(265, 50, 350, 490, fill="#f8fafc", stroke="#2457d6", sw=1.5, rx=6))
    f.append(text(440, 68, "Цифровий обчислювальний домен", size=11, color="#1e40af", bold=True))
    
    # 4. Ізольований польовий домен та інтерфейси (праворуч)
    f.append(rect(630, 50, 230, 490, fill="#fdf8f6", stroke="#c0392b", sw=1.5, rx=6))
    f.append(text(745, 68, "Польовий інтерфейсний домен", size=11, color="#962d22", bold=True))

    # ── Вузли Домену Живлення ──
    # Вхід живлення
    f.append(rect(35, 80, 200, 40, fill="#fff", stroke=INK, sw=1.5, rx=4))
    f.append(text(135, 96, "Вхід 24V DC + Захист", size=11, bold=True))
    f.append(text(135, 110, "TVS + P-MOSFET + eFuse", size=9, color=MUTED))

    # DC-DC 5V Buck
    f.append(rect(35, 132, 200, 40, fill="#eef3fb", stroke=NEG, sw=1.5, rx=4))
    f.append(text(135, 148, "DC-DC Buck (24V -> 5V)", size=11, bold=True))
    f.append(text(135, 162, "2.5A, ККД = 91%", size=9, color=MUTED))

    # DC-DC 3.3V
    f.append(rect(35, 185, 95, 40, fill="#eef3fb", stroke=NEG, sw=1.5, rx=4))
    f.append(text(82, 201, "DC-DC 3.3V", size=10, bold=True))
    f.append(text(82, 215, "I/O (1.5A)", size=9, color=MUTED))

    # DC-DC 1.2V Core
    f.append(rect(140, 185, 95, 40, fill="#eef3fb", stroke=NEG, sw=1.5, rx=4))
    f.append(text(187, 201, "DC-DC 1.2V", size=10, bold=True))
    f.append(text(187, 215, "Core (1.2A)", size=9, color=MUTED))

    # LDO 3.3V Analog + Ізольований DC-DC
    f.append(rect(35, 238, 95, 38, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(82, 253, "LDO 3.3V_ANA", size=9, bold=True))
    f.append(text(82, 266, "Ultra-Low Noise", size=9, color=MUTED))

    f.append(rect(140, 238, 95, 38, fill="#fbeee6", stroke=POS, sw=1.5, rx=4))
    f.append(text(187, 253, "ISO DC-DC 5V", size=9, bold=True))
    f.append(text(187, 266, "3kVrms бар'єр", size=9, color=MUTED))

    # Зв'язки живлення всередині домену
    f.append(arrow(135, 120, 135, 132, color=POS, sw=1.8))
    f.append(arrow(82, 172, 82, 185, color=POS, sw=1.5))
    f.append(arrow(187, 172, 187, 185, color=POS, sw=1.5))
    f.append(arrow(82, 225, 82, 238, color=FIELD, sw=1.5))
    f.append(arrow(187, 225, 187, 238, color=POS, sw=1.5))

    # ── Вузли Цифрового Домену (Центр) ──
    # Пам'ять (зверху)
    f.append(rect(285, 80, 145, 40, fill="#fff", stroke=INK, sw=1.5, rx=4))
    f.append(text(357, 96, "QSPI NOR Flash", size=11, bold=True))
    f.append(text(357, 110, "32 MB, 133 MHz", size=9, color=MUTED))

    f.append(rect(450, 80, 145, 40, fill="#fff", stroke=INK, sw=1.5, rx=4))
    f.append(text(522, 96, "I2C EEPROM + RTC", size=11, bold=True))
    f.append(text(522, 110, "Калібрування + Час", size=9, color=MUTED))

    # Центральний мікроконтролер / SoC
    f.append(rect(285, 145, 310, 245, fill="#eef3fb", stroke=NEG, sw=2, rx=6))
    f.append(text(440, 168, "Головний MCU (STM32H7 / Cortex-M7)", size=13, color=NEG, bold=True))
    f.append(text(440, 184, "480 MHz · 2 MB Flash · 1 MB SRAM · FPU / DSP", size=10, color=MUTED))
    f.append(line(295, 194, 585, 194, color="#cbd5e1", sw=1))

    # Блоки всередині MCU
    f.append(rect(295, 204, 135, 45, fill="#fff", stroke="#94a3b8", sw=1.2, rx=3))
    f.append(text(362, 221, "DMA + AXI Bus Matrix", size=9, bold=True))
    f.append(text(362, 235, "64-bit інтерконект", size=9, color=MUTED))

    f.append(rect(450, 204, 135, 45, fill="#fff", stroke="#94a3b8", sw=1.2, rx=3))
    f.append(text(517, 221, "Power Mgmt / Clock", size=9, bold=True))
    f.append(text(517, 235, "Sequencing / PLL / WDT", size=9, color=MUTED))

    f.append(rect(295, 258, 135, 45, fill="#fff", stroke="#94a3b8", sw=1.2, rx=3))
    f.append(text(362, 275, "Комунікаційні периферії", size=9, bold=True))
    f.append(text(362, 289, "SPI, I2C, UART, CAN, ETH", size=9, color=MUTED))

    f.append(rect(450, 258, 135, 45, fill="#fff", stroke="#94a3b8", sw=1.2, rx=3))
    f.append(text(517, 275, "Аналогові інтерфейси", size=9, bold=True))
    f.append(text(517, 289, "SPI до АЦП, DAC, Timer", size=9, color=MUTED))

    f.append(rect(295, 312, 290, 64, fill="#fff", stroke="#94a3b8", sw=1.2, rx=3))
    f.append(text(440, 329, "Матриця мультиплексування пінів (Pinmux)", size=10, bold=True))
    f.append(text(440, 345, "Розподіл виводів: 144-LQFP / 176-BGA без апаратних конфліктів", size=9, color=MUTED))
    f.append(text(440, 360, "Рівні: VDD_CORE = 1.2V, VDD_IO = 3.3V, VDDA = 3.3V", size=9, color="#1e40af"))

    # Налагодження та HMI (знизу центру)
    f.append(rect(285, 410, 145, 60, fill="#fff", stroke=INK, sw=1.5, rx=4))
    f.append(text(357, 428, "Debug Header (SWD)", size=10, bold=True))
    f.append(text(357, 444, "SWDIO, SWCLK, SWO", size=9, color=MUTED))
    f.append(text(357, 459, "TVS захист ліній", size=9, color=FIELD))

    f.append(rect(450, 410, 145, 60, fill="#fff", stroke=INK, sw=1.5, rx=4))
    f.append(text(522, 428, "HMI та Статус", size=10, bold=True))
    f.append(text(522, 444, "RGB LEDs + Кнопки", size=9, color=MUTED))
    f.append(text(522, 459, "UART Консоль", size=9, color=MUTED))

    # Зв'язки MCU з пам'яттю
    f.append(line(357, 145, 357, 120, color=INK, sw=1.5))
    f.append(text(377, 133, "QSPI", size=9, color=MUTED))
    f.append(line(522, 145, 522, 120, color=INK, sw=1.5))
    f.append(text(540, 133, "I2C", size=9, color=MUTED))

    # Зв'язки MCU з налагодженням
    f.append(line(357, 390, 357, 410, color=INK, sw=1.5))
    f.append(line(522, 390, 522, 410, color=INK, sw=1.5))

    # ── Вузли Аналогового Домену (Ліворуч знизу) ──
    f.append(rect(35, 335, 200, 42, fill="#fff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(135, 352, "Аналогові входи (4-20mA, 0-10V)", size=10, bold=True))
    f.append(text(135, 367, "TVS + OVP Clamping + Фільтр", size=9, color=MUTED))

    f.append(rect(35, 392, 200, 42, fill="#fff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(135, 409, "Прецизійний Буфер / AAF", size=10, bold=True))
    f.append(text(135, 424, "Low-Noise Op-Amp (OPA2188)", size=9, color=MUTED))

    f.append(rect(35, 450, 95, 42, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(82, 467, "24-bit ADC", size=10, bold=True))
    f.append(text(82, 482, "ADS1256 (SPI)", size=9, color=MUTED))

    f.append(rect(140, 450, 95, 42, fill="#fff", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(187, 467, "VREF 2.5V", size=10, bold=True))
    f.append(text(187, 482, "1 ppm/°C Drift", size=9, color=MUTED))

    f.append(arrow(135, 377, 135, 392, color=FIELD, sw=1.5))
    f.append(arrow(135, 434, 82, 450, color=FIELD, sw=1.5))
    f.append(arrow(140, 471, 130, 471, color=FIELD, sw=1.2))

    # Зв'язок АЦП з MCU через шину SPI
    f.append(arrow(130, 465, 285, 355, color=FIELD, sw=1.5))
    f.append(text(215, 398, "SPI (ізольована)", size=9, color="#1e8449", bold=True))

    # ── Вузли Польового Інтерфейсного Домену (Праворуч) ──
    # Гальванічний бар'єр (вертикальна лінія)
    f.append(line(638, 55, 638, 530, color=POS, sw=2, dash="6,4"))
    f.append(text(648, 535, "Ізоляційний бар'єр 3 кВ", size=9, color=POS, italic=True))

    # Ethernet 10/100
    f.append(rect(650, 75, 195, 55, fill="#fff", stroke=INK, sw=1.5, rx=4))
    f.append(text(747, 94, "Ethernet 10/100 (RMII)", size=11, bold=True))
    f.append(text(747, 110, "PHY (DP83848) + Магнетика", size=9, color=MUTED))
    f.append(text(747, 123, "Трансформатор 1.5kV + RJ45", size=9, color="#1e40af"))

    # Ізольований CAN-FD
    f.append(rect(650, 145, 195, 58, fill="#fff", stroke=POS, sw=1.5, rx=4))
    f.append(text(747, 163, "Ізольований CAN-FD", size=11, bold=True))
    f.append(text(747, 180, "Цифровий ізолятор + Тюнер", size=9, color=MUTED))
    f.append(text(747, 195, "5 Mbps, TVS захист шини", size=9, color=POS))

    # Ізольований RS-485
    f.append(rect(650, 220, 195, 58, fill="#fff", stroke=POS, sw=1.5, rx=4))
    f.append(text(747, 238, "Ізольований RS-485 / Modbus", size=11, bold=True))
    f.append(text(747, 255, "ADM2587E (Вбудований DC-DC)", size=9, color=MUTED))
    f.append(text(747, 270, "Гальванічна розв'язка 2.5kV", size=9, color=POS))

    # USB 2.0
    f.append(rect(650, 295, 195, 50, fill="#fff", stroke=INK, sw=1.5, rx=4))
    f.append(text(747, 313, "USB 2.0 Type-C (FS/HS)", size=11, bold=True))
    f.append(text(747, 330, "ESD Protection (USBLC6-2)", size=9, color=MUTED))

    # Дискретні польові виходи (Реле / SSR)
    f.append(rect(650, 360, 195, 58, fill="#fff", stroke=POS, sw=1.5, rx=4))
    f.append(text(747, 378, "Релейні виходи (4x SSR)", size=11, bold=True))
    f.append(text(747, 395, "Опторозв'язка + Драйвер", size=9, color=MUTED))
    f.append(text(747, 410, "Гасіння індуктивних викидів", size=9, color=MUTED))

    # Польові клеми / Зовнішні роз'єми
    f.append(rect(650, 435, 195, 50, fill="#fff", stroke=INK, sw=1.5, rx=4))
    f.append(text(747, 454, "Гвинтові польові клеми", size=11, bold=True))
    f.append(text(747, 471, "TVS матриці + Самозберігання", size=9, color=FIELD))

    # Зв'язки між MCU та периферійними інтерфейсами
    f.append(line(595, 102, 650, 102, color=INK, sw=1.5))
    f.append(text(622, 95, "RMII", size=9, color=MUTED))

    f.append(line(595, 174, 650, 174, color=POS, sw=1.5))
    f.append(text(622, 167, "CAN", size=9, color=MUTED))

    f.append(line(595, 249, 650, 249, color=POS, sw=1.5))
    f.append(text(622, 242, "UART", size=9, color=MUTED))

    f.append(line(595, 320, 650, 320, color=INK, sw=1.5))
    f.append(text(622, 313, "USB", size=9, color=MUTED))

    f.append(line(595, 389, 650, 389, color=POS, sw=1.5))
    f.append(text(622, 382, "GPIO", size=9, color=MUTED))

    # Силові зв'язки з домену живлення до MCU
    f.append(arrow(82, 185, 285, 185, color=NEG, sw=1.5))
    f.append(text(250, 178, "3.3V", size=9, color=NEG))

    f.append(arrow(235, 205, 285, 205, color=NEG, sw=1.5))
    f.append(text(260, 218, "1.2V", size=9, color=NEG))

    return "".join(f)


def fig_power_tree_architecture():
    """Архітектура дерева живлення (Power Tree) з ККД та послідовністю подачі живлення."""
    f = []
    
    # ── Первинний вхід (Ліворуч) ──
    f.append(rect(20, 150, 140, 95, fill="#fdf8f6", stroke=POS, sw=1.8, rx=6))
    f.append(text(90, 175, "Первинний вхід", size=12, bold=True))
    f.append(text(90, 195, "24V DC (9-36V)", size=11, color=POS, bold=True))
    f.append(text(90, 213, "TVS + P-MOSFET", size=9, color=MUTED))
    f.append(text(90, 230, "eFuse (I_max = 2A)", size=9, color=MUTED))

    # ── Каскад 1: Головний DC-DC Buck (24V -> 5V) ──
    f.append(rect(210, 150, 160, 95, fill="#eef3fb", stroke=NEG, sw=1.8, rx=6))
    f.append(text(290, 173, "DC-DC Buck 1", size=12, bold=True))
    f.append(text(290, 191, "24V -> 5.0V", size=11, color=NEG, bold=True))
    f.append(text(290, 209, "I_out_max = 2.5A", size=9, color=MUTED))
    f.append(text(290, 225, "ККД η = 91%", size=9, color=FIELD, bold=True))
    f.append(text(290, 239, "P_loss = 1.24W", size=9, color=POS))

    # З'єднання входу з Buck 1
    f.append(arrow(160, 197, 210, 197, color=POS, sw=2.5))
    f.append(text(185, 188, "24V", size=10, color=POS, bold=True))

    # Розподільна шина 5.0V (вертикальна вісь)
    f.append(line(410, 70, 410, 420, color=NEG, sw=3))
    f.append(arrow(370, 197, 410, 197, color=NEG, sw=2.5))
    f.append(text(390, 188, "5.0V", size=10, color=NEG, bold=True))

    # ── Каскад 2: Вторинні регулятори та навантаження ──

    # Гілка 1: 1.2V Core Buck (пріоритет №1)
    f.append(rect(450, 45, 170, 80, fill="#eef3fb", stroke=NEG, sw=1.5, rx=5))
    f.append(text(535, 66, "DC-DC Buck 1.2V", size=11, bold=True))
    f.append(text(535, 83, "5.0V -> 1.2V (Core)", size=10, color=NEG, bold=True))
    f.append(text(535, 99, "I_max = 1.2A | ККД = 88%", size=9, color=MUTED))
    f.append(text(535, 114, "P_loss = 0.20W", size=9, color=POS))

    f.append(rect(660, 45, 160, 80, fill="#f8fafc", stroke=INK, sw=1.5, rx=5))
    f.append(text(740, 68, "MCU VDD_CORE", size=11, bold=True))
    f.append(text(740, 88, "Cortex-M7 Ядро", size=10, color=MUTED))
    f.append(text(740, 107, "P_load = 1.44W", size=9, color="#1e40af", bold=True))

    f.append(arrow(410, 85, 450, 85, color=NEG, sw=2))
    f.append(arrow(620, 85, 660, 85, color=NEG, sw=2))
    f.append(text(640, 76, "1.2V", size=9, color=NEG, bold=True))

    # Гілка 2: 3.3V Digital Buck (пріоритет №2)
    f.append(rect(450, 140, 170, 80, fill="#eef3fb", stroke=NEG, sw=1.5, rx=5))
    f.append(text(535, 161, "DC-DC Buck 3.3V", size=11, bold=True))
    f.append(text(535, 178, "5.0V -> 3.3V (Digital)", size=10, color=NEG, bold=True))
    f.append(text(535, 194, "I_max = 1.5A | ККД = 94%", size=9, color=MUTED))
    f.append(text(535, 209, "P_loss = 0.32W", size=9, color=POS))

    f.append(rect(660, 140, 160, 80, fill="#f8fafc", stroke=INK, sw=1.5, rx=5))
    f.append(text(740, 161, "Цифрова периферія", size=11, bold=True))
    f.append(text(740, 179, "MCU I/O, Flash, PHY", size=9, color=MUTED))
    f.append(text(740, 196, "I2C, SPI, Debug", size=9, color=MUTED))
    f.append(text(740, 211, "P_load = 3.63W", size=9, color="#1e40af", bold=True))

    f.append(arrow(410, 180, 450, 180, color=NEG, sw=2))
    f.append(arrow(620, 180, 660, 180, color=NEG, sw=2))
    f.append(text(640, 171, "3.3V", size=9, color=NEG, bold=True))

    # Гілка 3: 3.3V Analog LDO (пріоритет №3)
    f.append(rect(450, 235, 170, 80, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=5))
    f.append(text(535, 256, "LDO 3.3V Analog", size=11, color=FIELD, bold=True))
    f.append(text(535, 273, "5.0V -> 3.3V_ANA", size=10, color=FIELD, bold=True))
    f.append(text(535, 289, "PSRR > 75dB | Low-Noise", size=9, color=MUTED))
    f.append(text(535, 304, "P_loss = 0.25W", size=9, color=POS))

    f.append(rect(660, 235, 160, 80, fill="#f4fbf7", stroke=FIELD, sw=1.5, rx=5))
    f.append(text(740, 256, "Прецизійний аналог", size=11, bold=True))
    f.append(text(740, 275, "24-bit АЦП, VREF", size=9, color=MUTED))
    f.append(text(740, 292, "Буферні ОП (OPA2188)", size=9, color=MUTED))
    f.append(text(740, 307, "P_load = 0.50W", size=9, color="#1e8449", bold=True))

    f.append(arrow(410, 275, 450, 275, color=FIELD, sw=2))
    f.append(arrow(620, 275, 660, 275, color=FIELD, sw=2))
    f.append(text(640, 266, "3.3VA", size=9, color=FIELD, bold=True))

    # Гілка 4: Ізольований DC-DC 5V
    f.append(rect(450, 330, 170, 80, fill="#fdf8f6", stroke=POS, sw=1.5, rx=5))
    f.append(text(535, 351, "Ізольований DC-DC", size=11, color=POS, bold=True))
    f.append(text(535, 368, "5.0V -> 5.0V_ISO", size=10, color=POS, bold=True))
    f.append(text(535, 384, "3kVrms Ізоляція | η = 78%", size=9, color=MUTED))
    f.append(text(535, 399, "P_loss = 0.28W", size=9, color=POS))

    f.append(rect(660, 330, 160, 80, fill="#fdf8f6", stroke=POS, sw=1.5, rx=5))
    f.append(text(740, 351, "Польові трансивери", size=11, bold=True))
    f.append(text(740, 370, "CAN-FD + RS-485", size=9, color=MUTED))
    f.append(text(740, 387, "Ізольована сторона", size=9, color=MUTED))
    f.append(text(740, 402, "P_load = 1.00W", size=9, color=POS, bold=True))

    f.append(arrow(410, 370, 450, 370, color=POS, sw=2))
    f.append(arrow(620, 370, 660, 370, color=POS, sw=2))
    f.append(text(640, 361, "5V_ISO", size=9, color=POS, bold=True))

    # ── Послідовність подачі живлення (Power Sequencing Daisy-Chain) ──
    # Ланцюжок керування Power Good -> Enable
    f.append(rect(20, 430, 800, 40, fill="#f1f5f9", stroke="#64748b", sw=1.2, rx=4))
    f.append(text(80, 454, "Порядок запуску:", size=10, color="#334155", bold=True))
    
    # Кроки послідовності
    f.append(rect(145, 435, 120, 30, fill="#fff", stroke=NEG, sw=1.2, rx=3))
    f.append(text(205, 454, "1. 5.0V Bus (t=0)", size=9, bold=True))

    f.append(arrow(265, 450, 285, 450, color=NEG, sw=1.5))

    f.append(rect(285, 435, 135, 30, fill="#fff", stroke=NEG, sw=1.2, rx=3))
    f.append(text(352, 454, "2. 1.2V Core (t=+1ms)", size=9, bold=True))

    f.append(arrow(420, 450, 440, 450, color=NEG, sw=1.5))

    f.append(rect(440, 435, 135, 30, fill="#fff", stroke=NEG, sw=1.2, rx=3))
    f.append(text(507, 454, "3. 3.3V I/O (t=+3ms)", size=9, bold=True))

    f.append(arrow(575, 450, 595, 450, color=FIELD, sw=1.5))

    f.append(rect(595, 435, 215, 30, fill="#fff", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(702, 454, "4. 3.3V_ANA & Reset High (t=+7ms)", size=9, color=FIELD, bold=True))

    return "".join(f)


if __name__ == "__main__":
    render(os.path.join(OUT, "system-block-diagram.svg"), 880, 560,
           fig_system_block_diagram(),
           title="Функціональна блок-схема вбудованого контролера збору даних")
    render(os.path.join(OUT, "power-tree-architecture.svg"), 840, 480,
           fig_power_tree_architecture(),
           title="Архітектура дерева живлення (Power Tree) та послідовність подачі напруг")
    print("Фігури збережено в", OUT)
