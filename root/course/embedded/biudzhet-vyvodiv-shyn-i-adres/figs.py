# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Figure 1: I2C адреси й апаратний комутатор TCA9548A ─────────────────────
def fig_i2c_multiplexing():
    W, H = 940, 480
    p = []

    # Заголовок блоків
    p.append(text(120, 32, "Мікроконтролер (Master)", size=14, bold=True))
    p.append(text(470, 32, "I2C-комутатор TCA9548A (0x70)", size=14, bold=True))
    p.append(text(810, 32, "Ізольовані субшини I2C", size=14, bold=True))

    # MCU блок
    p.append(rect(30, 55, 180, 390, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(textbox(120, 105, "MCU I2C Master\nSDA / SCL", size=12, bold=True)[0])
    p.append(textbox(120, 235, "GPIO Reset\n(активний 0)", size=11)[0])
    p.append(textbox(120, 365, "Головний домен\nVCC = 3.3 В", size=11, color=MUTED)[0])

    # Комутатор TCA9548A
    p.append(rect(370, 55, 200, 390, fill="#eff6ff", stroke=NEG, sw=2, rx=8))
    p.append(textbox(470, 90, "Регістр керування\n(вибір каналу 0..7)", size=11, bold=True, color=NEG)[0])
    p.append(textbox(470, 155, "ADDR піни A0..A2\n(база 0x70..0x77)", size=10, color=MUTED)[0])

    # Ключі всередині TCA9548A
    p.append(rect(385, 195, 170, 235, fill="#ffffff", stroke="#93c5fd", sw=1.2, rx=6))
    p.append(text(470, 215, "FET-перемикачі", size=11, bold=True, color=NEG))

    channels = [
        ("CH0", 250, "SD0 / SC0", True),
        ("CH1", 300, "SD1 / SC1", False),
        ("CH2", 350, "SD2 / SC2", False),
        ("CH7", 400, "SD7 / SC7", False),
    ]

    for name, y, bus_label, active in channels:
        col = FIELD if active else MUTED
        p.append(rect(395, y - 13, 150, 26, fill="#f0fdf4" if active else "#f9fafb", stroke=col, sw=1.2, rx=4))
        p.append(text(425, y + 4, name, size=11, bold=True, color=col))
        p.append(text(495, y + 4, bus_label, size=10, color=col))

    # Зв'язок MCU -> TCA9548A
    p.append(line(210, 105, 370, 105, color=LINE, sw=2))
    p.append(text(290, 93, "SDA / SCL", size=11, bold=True))
    p.append(text(290, 123, "Спільна шина", size=10, color=MUTED))

    p.append(line(210, 235, 370, 235, color=POS, sw=1.5, dash="4,3"))
    p.append(text(290, 227, "RESET", size=10, color=POS))

    # Субшини та сенсори з однаковою адресою
    sensors = [
        ("CH0", 250, "Датчик IMU #0 (0x68)\nC_bus0 < 50 пФ", FIELD, "#dcfce7"),
        ("CH1", 300, "Датчик IMU #1 (0x68)\nC_bus1 < 50 пФ", MUTED, "#f3f4f6"),
        ("CH2", 350, "Датчик IMU #2 (0x68)\nC_bus2 < 50 пФ", MUTED, "#f3f4f6"),
        ("CH7", 400, "Датчик IMU #7 (0x68)\nC_bus7 < 50 пФ", MUTED, "#f3f4f6"),
    ]

    for ch_name, y, sens_text, col, bg_col in sensors:
        p.append(arrow(570, y, 710, y, color=col, sw=1.6))
        p.append(rect(710, y - 18, 200, 36, fill=bg_col, stroke=col, sw=1.4, rx=6))
        lines = sens_text.split("\n")
        p.append(text(810, y - 3, lines[0], size=11, bold=True, color=col))
        p.append(text(810, y + 11, lines[1], size=9, color=MUTED))

    render(os.path.join(OUT, "i2c-multiplexing.svg"), W, H, *p)


# ── Figure 2: Розширення Chip Select для SPI через 74HC138 ─────────────────
def fig_spi_cs_decoding():
    W, H = 940, 480
    p = []

    # Заголовок блоків
    p.append(text(120, 32, "Мікроконтролер", size=14, bold=True))
    p.append(text(460, 32, "Дешифратор 74HC138 (3 → 8)", size=14, bold=True))
    p.append(text(810, 32, "SPI-периферія (Active-Low CS)", size=14, bold=True))

    # MCU
    p.append(rect(30, 55, 180, 400, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(textbox(120, 105, "Апаратний SPI\nSCK, MOSI, MISO", size=12, bold=True)[0])
    p.append(textbox(120, 235, "3 × GPIO Адреси\n(CS_A0, CS_A1, CS_A2)", size=11, bold=True, color=NEG)[0])
    p.append(textbox(120, 355, "1 × GPIO Enable\n(CS_EN активний 0)", size=11, bold=True, color=POS)[0])

    # 74HC138
    p.append(rect(360, 55, 200, 400, fill="#fefce8", stroke="#ca8a04", sw=2, rx=8))
    p.append(textbox(460, 90, "Логіка дешифрації\n3 входи → 8 виходів", size=11, bold=True, color="#854d0e")[0])
    p.append(textbox(460, 145, "Входи дозволу:\nE1 (HIGH), E2/E3 (LOW)", size=10, color=MUTED)[0])

    # Входи дешифратора
    p.append(line(210, 235, 360, 235, color=NEG, sw=2))
    p.append(text(285, 223, "3 адресні лінії", size=11, bold=True, color=NEG))
    p.append(text(285, 249, "Код 0..7", size=9, color=MUTED))

    p.append(line(210, 355, 360, 355, color=POS, sw=1.8, dash="4,3"))
    p.append(text(285, 343, "Строб дозволу", size=10, color=POS))
    p.append(text(285, 369, "Блокує глічі CS", size=9, color=MUTED))

    # Спільні лінії SPI (проходять повз дешифратор)
    p.append(line(210, 105, 710, 105, color=LINE, sw=2.2))
    p.append(text(340, 93, "Спільні SCK / MOSI / MISO", size=11, bold=True))

    # Виходи CS0..CS7 без вкладених конфліктних рамок
    slaves = [
        ("Y0 (0)", 195, "Flash пам'ять W25Q128\nCS0 = 0 (активний)", FIELD, "#dcfce7"),
        ("Y1 (1)", 245, "SD-карта пам'яті\nCS1 = 1 (неактивний)", MUTED, "#f3f4f6"),
        ("Y2 (2)", 295, "TFT-дисплей ST7789\nCS2 = 1 (неактивний)", MUTED, "#f3f4f6"),
        ("Y3 (3)", 345, "LoRa трансивер SX1262\nCS3 = 1 (неактивний)", MUTED, "#f3f4f6"),
        ("Y7 (7)", 415, "Зовнішній АЦП ADS1220\nCS7 = 1 (неактивний)", MUTED, "#f3f4f6"),
    ]

    p.append(text(460, 382, "...", size=16, bold=True, color=MUTED))

    for y_code, y, dev_text, col, bg_col in slaves:
        p.append(text(410, y + 4, y_code, size=10, bold=True, color=col))
        p.append(text(485, y + 4, "Active-LOW", size=9, color=col))

        p.append(arrow(560, y, 710, y, color=col, sw=1.6))
        p.append(rect(710, y - 18, 200, 36, fill=bg_col, stroke=col, sw=1.4, rx=6))
        lines = dev_text.split("\n")
        p.append(text(810, y - 3, lines[0], size=11, bold=True, color=col))
        p.append(text(810, y + 11, lines[1], size=9, color=MUTED))

    render(os.path.join(OUT, "spi-cs-decoding.svg"), W, H, *p)


# ── Figure 3: GPIO-експандер та асинхронне групове переривання ──────────────
def fig_gpio_expander_interrupt():
    W, H = 940, 480
    p = []

    # Заголовки
    p.append(text(120, 32, "Мікроконтролер (Host)", size=14, bold=True))
    p.append(text(470, 32, "16-бітний експандер MCP23017", size=14, bold=True))
    p.append(text(810, 32, "Периферія та контакти", size=14, bold=True))

    # MCU
    p.append(rect(30, 55, 180, 400, fill="#f8fafc", stroke=LINE, sw=1.8, rx=8))
    p.append(textbox(120, 105, "I2C Master\n(SDA, SCL)", size=12, bold=True)[0])
    p.append(textbox(120, 235, "Зовнішнє переривання\nEXTI (спад фронту)", size=11, bold=True, color=POS)[0])
    p.append(textbox(120, 365, "Обробник подій\n(зчитує INTCAP/GPIO)", size=11, color=MUTED)[0])

    # MCP23017
    p.append(rect(350, 55, 240, 400, fill="#faf5ff", stroke="#9333ea", sw=2, rx=8))
    p.append(textbox(470, 90, "Внутрішні регістри:\nIODIR, GPINTEN, DEFVAL", size=11, bold=True, color="#6b21a8")[0])
    p.append(textbox(470, 155, "Фіксатор переривання:\nINTFA/B (прапорці), INTCAP (стан)", size=10, color=MUTED)[0])

    # Зв'язок I2C
    p.append(line(210, 105, 350, 105, color=LINE, sw=2))
    p.append(text(280, 93, "SDA / SCL", size=11, bold=True))
    p.append(text(280, 123, "Опитування ~30 мкс", size=9, color=MUTED))

    # Зв'язок INT (Wired-OR)
    p.append(line(350, 235, 210, 235, color=POS, sw=2))
    p.append(text(280, 221, "INTA / INTB (Wired-OR)", size=11, bold=True, color=POS))
    p.append(text(280, 249, "Відкритий стік + підтяжка", size=9, color=MUTED))

    # Порти GPA / GPB
    ports = [
        ("GPA0..GPA3", 240, "4 × Кінцеві вимикачі\nGPINTEN = 1 (на зміну)", POS, "#fee2e2"),
        ("GPA4..GPA7", 305, "4 × Сигнальні входи тривоги\nЗафіксовано в INTCAP", POS, "#fee2e2"),
        ("GPB0..GPB7", 380, "8 × Керування реле / LED\nВиходи Push-Pull (OLATB)", FIELD, "#dcfce7"),
    ]

    for p_name, y, p_desc, col, bg_col in ports:
        p.append(rect(370, y - 14, 200, 28, fill="#ffffff", stroke=col, sw=1.2, rx=4))
        p.append(text(470, y + 4, p_name, size=11, bold=True, color=col))

        p.append(arrow(590, y, 710, y, color=col, sw=1.6))
        p.append(rect(710, y - 20, 200, 40, fill=bg_col, stroke=col, sw=1.4, rx=6))
        lines = p_desc.split("\n")
        p.append(text(810, y - 4, lines[0], size=11, bold=True, color=col))
        p.append(text(810, y + 12, lines[1], size=9, color=MUTED))

    render(os.path.join(OUT, "gpio-expander-interrupt.svg"), W, H, *p)


# ── Figure 4: Мультиплексування ліній: Матриця та Чарліплексинг ─────────────
def fig_matrix_and_charlieplexing():
    W, H = 940, 480
    p = []

    # Дві половини порівняння
    p.append(text(240, 32, "Матрична клавіатура (4 рядки + 4 стовпчики)", size=13, bold=True))
    p.append(text(710, 32, "Чарліплексинг (Tri-state керування)", size=13, bold=True))
    p.append(line(470, 20, 470, 460, color="#cbd5e1", sw=1.5, dash="6,4"))

    # Ліва половина: Матрична клавіатура
    p.append(rect(30, 55, 410, 400, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(textbox(235, 90, "8 виводів МК → 16 кнопок (4 × 4)\nСканування: 1 рядок LOW, читання стовпчиків", size=11, bold=True)[0])

    # Малюнок матриці
    for r in range(4):
        yr = 145 + r * 55
        p.append(line(60, yr, 380, yr, color=NEG, sw=1.5))
        p.append(text(50, yr + 4, "R%d" % r, size=10, bold=True, color=NEG, anchor="end"))

    for c in range(4):
        xc = 110 + c * 75
        p.append(line(xc, 125, xc, 330, color=FIELD, sw=1.5))
        p.append(text(xc, 348, "C%d" % c, size=10, bold=True, color=FIELD))

    # Точки перетину з кнопками та діодами
    for r in range(4):
        yr = 145 + r * 55
        for c in range(4):
            xc = 110 + c * 75
            p.append(circle(xc, yr, 4, fill="#ffffff", stroke=LINE, sw=1.5))
            # діод захисту від фантомів
            p.append(rect(xc + 8, yr - 7, 20, 14, fill="#fef3c7", stroke="#d97706", sw=1, rx=2))
            p.append(text(xc + 18, yr + 4, "D", size=9, color="#92400e", bold=True))

    p.append(textbox(235, 410, "Діоди запобігають «фантомним натисканням»\n(Ghosting) при 3+ одночасних клавішах", size=10, color=MUTED)[0])

    # Права половина: Чарліплексинг
    p.append(rect(500, 55, 410, 400, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(textbox(705, 90, "N виводів → N × (N - 1) світлодіодів\n3 виводи МК → 6 LED (Tri-state: H, L, Z)", size=11, bold=True)[0])

    # Таблиця станів
    states = [
        ("LED 1 (P0 → P1)", "P0 = HIGH", "P1 = LOW",  "P2 = Hi-Z"),
        ("LED 2 (P1 → P0)", "P0 = LOW",  "P1 = HIGH", "P2 = Hi-Z"),
        ("LED 3 (P1 → P2)", "P0 = Hi-Z", "P1 = HIGH", "P2 = LOW"),
        ("LED 4 (P2 → P1)", "P0 = Hi-Z", "P1 = LOW",  "P2 = HIGH"),
        ("LED 5 (P0 → P2)", "P0 = HIGH", "P1 = Hi-Z", "P2 = LOW"),
        ("LED 6 (P2 → P0)", "P0 = LOW",  "P1 = Hi-Z", "P2 = HIGH"),
    ]

    p.append(rect(520, 130, 370, 200, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(580, 150, "Цільовий LED", size=10, bold=True))
    p.append(text(675, 150, "Пін 0", size=10, bold=True))
    p.append(text(755, 150, "Пін 1", size=10, bold=True))
    p.append(text(835, 150, "Пін 2", size=10, bold=True))
    p.append(line(520, 160, 890, 160, color="#cbd5e1", sw=1))

    for i, (led, p0, p1, p2) in enumerate(states):
        ys = 180 + i * 23
        p.append(text(580, ys, led, size=10, color=INK))
        p.append(text(675, ys, p0.replace("P0 = ", ""), size=9, bold=("HIGH" in p0), color=POS if "HIGH" in p0 else (NEG if "LOW" in p0 else MUTED)))
        p.append(text(755, ys, p1.replace("P1 = ", ""), size=9, bold=("HIGH" in p1), color=POS if "HIGH" in p1 else (NEG if "LOW" in p1 else MUTED)))
        p.append(text(835, ys, p2.replace("P2 = ", ""), size=9, bold=("HIGH" in p2), color=POS if "HIGH" in p2 else (NEG if "LOW" in p2 else MUTED)))

    p.append(textbox(705, 395, "Шпаруватість 1/N вимагає вищого пікового струму;\nЗворотна напруга вимкнених LED не має перевищувати V_R", size=10, color=MUTED)[0])

    render(os.path.join(OUT, "matrix-and-charlieplexing.svg"), W, H, *p)


if __name__ == "__main__":
    fig_i2c_multiplexing()
    fig_spi_cs_decoding()
    fig_gpio_expander_interrupt()
    fig_matrix_and_charlieplexing()
    print("Figures generated successfully.")
