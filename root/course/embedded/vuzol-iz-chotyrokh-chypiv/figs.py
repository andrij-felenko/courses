# -*- coding: utf-8 -*-
import sys, os

# Add scripts directory to path (4 levels up from topic folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. node-system-architecture: Структурна схема вузла з чотирма чипами ──
def fig_node_system_architecture():
    W, H = 940, 520
    p = []

    # Фон та заголовок
    p.append(rect(15, 45, 910, 460, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))

    # Головний МК (Центральний блок)
    p.append(rect(340, 100, 260, 360, fill="#edf2f7", stroke=INK, sw=2, rx=8))
    p.append(text(470, 128, "Головний МК (STM32 / ESP32)", size=14, color=INK, bold=True))
    p.append(text(470, 146, "ARM Cortex-M4 @ 80-170 МГц", size=11, color=MUTED))

    # Внутрішні блоки МК
    p.append(fitbox(355, 165, 230, 45, "SPI1 Master Controller\n(DMA TX/RX, до 50 МГц)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(355, 220, 230, 45, "I2C1 Master Controller\n(Standard / Fast Mode 400 кГц)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(355, 275, 230, 45, "EXTI Interrupt Controller\n(Апаратний таймер / будильник)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(355, 330, 230, 45, "USART1 + Hardware DE\n(Автоматичне керування RS-485)", size=11, fill="#ffffff", stroke=MUTED))
    p.append(fitbox(355, 385, 230, 55, "Пам'ять ядра та Event Loop\nКільцевий буфер + Диспетчер", size=11, fill="#e6fffa", stroke=FIELD))

    # Чип 1: SPI Flash W25Q128JV (Вгорі праворуч)
    p.append(rect(670, 75, 235, 120, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(787, 100, "Чип 1: Flash W25Q128JV", size=13, color=FIELD, bold=True))
    p.append(text(787, 118, "NOR Flash 128 Мбіт (16 МБ)", size=11, color=INK))
    p.append(text(787, 136, "SPI Mode 0/3, t_prog=0.8 мс", size=10.5, color=MUTED))
    p.append(text(787, 154, "100k циклів стирання сектора", size=10, color=MUTED))
    p.append(rect(680, 168, 70, 20, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
    p.append(text(715, 182, "C_dec 100n", size=9.5, color=FIELD))

    # Чип 2: Прецизійний датчик BME280 (Вгорі ліворуч)
    p.append(rect(35, 75, 235, 120, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(152, 100, "Чип 2: Датчик BME280", size=13, color=NEG, bold=True))
    p.append(text(152, 118, "T, Вологість, Тиск (MEMS)", size=11, color=INK))
    p.append(text(152, 136, "I2C Addr: 0x76, 20-біт АЦП", size=10.5, color=MUTED))
    p.append(text(152, 154, "IIR фільтр, Burst 8 байтів", size=10, color=MUTED))
    p.append(rect(45, 168, 70, 20, fill="#ffffff", stroke=NEG, sw=1, rx=3))
    p.append(text(80, 182, "C_dec 100n", size=9.5, color=NEG))

    # Чип 3: Прецизійний годинник DS3231 (Внизу ліворуч)
    p.append(rect(35, 260, 235, 135, fill="#fffbeb", stroke="#d97706", sw=1.8, rx=6))
    p.append(text(152, 285, "Чип 3: RTC DS3231", size=13, color="#d97706", bold=True))
    p.append(text(152, 303, "TCXO 32.768 кГц (±2 ppm)", size=11, color=INK))
    p.append(text(152, 321, "I2C Addr: 0x68, Календар", size=10.5, color=MUTED))
    p.append(text(152, 339, "Апаратний будильник / INT#", size=10, color=MUTED))
    p.append(rect(45, 355, 100, 22, fill="#ffffff", stroke="#d97706", sw=1, rx=3))
    p.append(text(95, 370, "CR2032 Батарея", size=9.5, color="#d97706", bold=True))

    # Чип 4: Трансивер RS-485 SN65HVD72 (Внизу праворуч)
    p.append(rect(670, 260, 235, 140, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(787, 285, "Чип 4: RS-485 SN65HVD72", size=13, color=POS, bold=True))
    p.append(text(787, 303, "Напівдуплексний трансивер 3.3V", size=11, color=INK))
    p.append(text(787, 321, "Slew-rate обмеження (250 kbps)", size=10.5, color=MUTED))
    p.append(text(787, 339, "TVS SM712 + Термінація 120R", size=10, color=MUTED))
    p.append(rect(680, 360, 85, 22, fill="#ffffff", stroke=POS, sw=1, rx=3))
    p.append(text(722, 375, "Лінії A / B", size=10, color=POS, bold=True))

    # Зв'язки ліній
    # 1. SPI зв'язок (МК -> Flash)
    p.append(line(585, 175, 670, 135, color=FIELD, sw=2))
    p.append(arrow(585, 175, 665, 135, color=FIELD, sw=2))
    p.append(rect(600, 140, 65, 20, fill="#ffffff", stroke=FIELD, sw=1, rx=3))
    p.append(text(632, 154, "SPI (4 лінії)", size=9.5, color=FIELD, bold=True))

    # 2. I2C зв'язок (МК -> BME280 & DS3231)
    p.append(line(355, 240, 290, 240, color=NEG, sw=2))
    p.append(line(290, 140, 290, 310, color=NEG, sw=2))
    p.append(arrow(290, 140, 270, 140, color=NEG, sw=2))
    p.append(arrow(290, 310, 270, 310, color=NEG, sw=2))
    p.append(rect(265, 210, 50, 20, fill="#ffffff", stroke=NEG, sw=1, rx=3))
    p.append(text(290, 224, "I2C Шина", size=9.5, color=NEG, bold=True))

    # 3. Переривання від RTC (DS3231 -> МК EXTI)
    p.append(arrow(270, 345, 355, 295, color="#d97706", sw=1.8))
    p.append(rect(280, 310, 60, 18, fill="#ffffff", stroke="#d97706", sw=1, rx=3))
    p.append(text(310, 323, "INT / SQW", size=9, color="#d97706", bold=True))

    # 4. UART + DE зв'язок (МК -> RS-485)
    p.append(line(585, 350, 670, 330, color=POS, sw=2))
    p.append(arrow(585, 350, 665, 330, color=POS, sw=2))
    p.append(rect(595, 320, 70, 20, fill="#ffffff", stroke=POS, sw=1, rx=3))
    p.append(text(630, 334, "TX, RX, DE", size=9.5, color=POS, bold=True))

    # Блок живлення 3.3V LDO
    p.append(fitbox(370, 465, 200, 32, "Єдина шина живлення 3.3V LDO + Полігон GND", size=10, fill="#ffffff", stroke=INK))

    render(os.path.join(OUT, "node-system-architecture.svg"), W, H, *p, title="Архітектура системного вузла з 4 чипами")

# ── 2. pcb-layout-zoning: Функціональне зонування друкованої плати та Ground Plane ──
def fig_pcb_layout_zoning():
    W, H = 940, 480
    p = []

    p.append(rect(20, 45, 900, 420, fill="#ffffff", stroke=MUTED, sw=1.5, rx=8))

    # Плата 4 шари: загальна рамка PCB
    p.append(rect(40, 65, 860, 380, fill="#f8fafc", stroke=INK, sw=2, rx=6))
    p.append(text(470, 90, "4-шарова друкована плата (L1: Signals, L2: Solid GND, L3: Power 3.3V, L4: Signals/GND)", size=12.5, color=MUTED))

    # Зона 1: Чутливий аналоговий/MEMS кут (Ліворуч вгорі)
    p.append(rect(60, 115, 230, 230, fill="#eff6ff", stroke=NEG, sw=1.8, rx=6))
    p.append(text(175, 140, "ЗОНА A: MEMS та RTC", size=12.5, color=NEG, bold=True))
    p.append(fitbox(75, 155, 200, 40, "Чип 2: BME280\n(Датчик T / RH / P)", size=10.5, fill="#ffffff", stroke=NEG))
    p.append(fitbox(75, 205, 200, 40, "Чип 3: DS3231 RTC\n(TCXO 32 кГц + Батарея)", size=10.5, fill="#ffffff", stroke=NEG))
    p.append(text(175, 270, "• Віддалено від джерел тепла", size=10, color=MUTED))
    p.append(text(175, 288, "• Підтяжки I2C 2.2 кОм", size=10, color=MUTED))
    p.append(text(175, 306, "• Опорна земля без шумних струмів", size=10, color=MUTED))
    p.append(text(175, 324, "• Захисний екран Guard Ring", size=10, color=MUTED))

    # Зона 2: Цифрове обчислювальне ядро МК (Центр)
    p.append(rect(310, 115, 260, 230, fill="#f3f4f6", stroke=INK, sw=1.8, rx=6))
    p.append(text(440, 140, "ЗОНА B: Цифрове ядро МК", size=12.5, color=INK, bold=True))
    p.append(fitbox(330, 160, 220, 50, "STM32 / ESP32 МК\n(LQFP-48 / QFN-48)", size=11, fill="#ffffff", stroke=INK, bold=True))
    p.append(text(440, 235, "• Блокувальні керамічні C 100 нФ", size=10, color=MUTED))
    p.append(text(440, 255, "  на кожну пару VDD/VSS", size=10, color=MUTED))
    p.append(text(440, 275, "• Кварцовий резонатор 8 МГц", size=10, color=MUTED))
    p.append(text(440, 295, "  з охоронним кільцем GND", size=10, color=MUTED))
    p.append(text(440, 315, "• Короткі перехідні отвори Via", size=10, color=MUTED))

    # Зона 3: Швидкісний SPI Flash (Вгорі праворуч)
    p.append(rect(590, 115, 290, 110, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(735, 138, "ЗОНА C: Швидкісна пам'ять SPI", size=12.5, color=FIELD, bold=True))
    p.append(fitbox(605, 150, 260, 35, "Чип 1: W25Q128JV (SOIC-8, 50 МГц)", size=10.5, fill="#ffffff", stroke=FIELD))
    p.append(text(735, 202, "• Узгоджувальні резистори 22..33 Ом біля МК", size=10, color=MUTED))
    p.append(text(735, 218, "• Довжина траси < 30 мм, правило 3W", size=10, color=MUTED))

    # Зона 4: Польовий інтерфейс RS-485 (Внизу праворуч)
    p.append(rect(590, 235, 290, 110, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(735, 258, "ЗОНА D: Польовий інтерфейс RS-485", size=12.5, color=POS, bold=True))
    p.append(fitbox(605, 270, 260, 35, "Чип 4: SN65HVD72 + TVS SM712", size=10.5, fill="#ffffff", stroke=POS))
    p.append(text(735, 320, "• TVS і термінатор 120R біля роз'єму", size=10, color=MUTED))
    p.append(text(735, 336, "• Імпульсні струми стікають до клеми GND", size=10, color=MUTED))

    # Нижня частина: Суцільний Ground Plane та шляхи повернення струму
    p.append(rect(60, 360, 820, 70, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    p.append(text(470, 385, "СУЦІЛЬНА ПЛОЩИНА ЗЕМЛІ (Layer 2 Solid Ground Plane) — БЕЗ РОЗРІЗІВ", size=12, color=LINE, bold=True))
    p.append(text(470, 405, "Високочастотні зворотні струми SPI і RS-485 локалізуються строго під власними доріжками на L1.", size=10.5, color=INK))
    p.append(text(470, 420, "Функціональне просторове зонування запобігає затіканню цифрового шуму в зону MEMS датчика.", size=10.5, color=FIELD, bold=True))

    render(os.path.join(OUT, "pcb-layout-zoning.svg"), W, H, *p, title="Функціональне зонування 4-чипової плати та топологія шарів")

# ── 3. firmware-event-loop-timing: Часова діаграма та автомат станів прошивки ──
def fig_firmware_event_loop_timing():
    W, H = 940, 460
    p = []

    p.append(rect(15, 45, 910, 400, fill="#ffffff", stroke=MUTED, sw=1.2, rx=8))

    # Стрічка часу (Х-вісь)
    p.append(line(60, 390, 880, 390, color=INK, sw=2))
    p.append(arrow(60, 390, 885, 390, color=INK, sw=2))
    p.append(text(880, 410, "Час (t)", size=11, color=INK, bold=True))

    # Канали сигналів
    signals = [
        ("1. RTC SQW / Alarm", 90, "#d97706"),
        ("2. I2C Bus (BME280)", 160, NEG),
        ("3. SPI Bus (W25Q128)", 230, FIELD),
        ("4. RS-485 Async Modbus", 300, POS)
    ]

    for name, y, col in signals:
        p.append(text(140, y + 5, name, size=11.5, color=col, bold=True, anchor="end"))
        p.append(line(150, y, 860, y, color="#e5e7eb", sw=1, dash="4 4"))

    # Подія 1: RTC Alarm Pulse (1 Гц)
    p.append(line(180, 90, 220, 90, color="#d97706", sw=2))
    p.append(line(220, 90, 220, 70, color="#d97706", sw=2))
    p.append(line(220, 70, 250, 70, color="#d97706", sw=2))
    p.append(line(250, 70, 250, 90, color="#d97706", sw=2))
    p.append(line(250, 90, 860, 90, color="#d97706", sw=2))
    p.append(text(235, 60, "EXTI Alarm", size=10, color="#d97706", bold=True))

    # Подія 2: I2C вичитування BME280 + DS3231
    p.append(line(150, 160, 250, 160, color=NEG, sw=2))
    p.append(rect(250, 140, 140, 35, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(320, 162, "I2C: 0x76 Read 8B\n(T, P, H) + RTC Time", size=10, color=NEG, bold=True))
    p.append(line(390, 160, 860, 160, color=NEG, sw=2))
    p.append(text(320, 190, "t_i2c ≈ 1.2 мс", size=9.5, color=MUTED))

    # Подія 3: SPI запис у Flash W25Q128 (Сторінка 256 байтів або запис структури)
    p.append(line(150, 230, 400, 230, color=FIELD, sw=2))
    p.append(rect(400, 210, 130, 35, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(465, 232, "SPI: Page Program\nLog Record (24 B)", size=10, color=FIELD, bold=True))
    p.append(line(530, 230, 860, 230, color=FIELD, sw=2))
    p.append(text(465, 260, "t_spi ≈ 0.8 мс", size=9.5, color=MUTED))

    # Подія 4: Асинхронний Modbus RTU запит по RS-485
    p.append(line(150, 300, 560, 300, color=POS, sw=2))
    p.append(rect(560, 280, 80, 35, fill="#fff1f2", stroke=POS, sw=1.5, rx=3))
    p.append(text(600, 302, "RS-485 RX\nMaster Req", size=9.5, color=POS))
    p.append(rect(650, 280, 110, 35, fill="#fef2f2", stroke=POS, sw=2, rx=3))
    p.append(text(705, 302, "RS-485 TX (DE=1)\nTelemetry Packet", size=9.5, color=POS, bold=True))
    p.append(line(760, 300, 860, 300, color=POS, sw=2))
    p.append(text(705, 330, "t_resp ≈ 3.5 мс", size=9.5, color=MUTED))

    # Позначення стану сну ядра МК
    p.append(fitbox(200, 345, 180, 30, "Збір: Wakeup по EXTI", size=10, fill="#fef3c7", stroke="#d97706"))
    p.append(fitbox(770, 345, 90, 30, "Sleep Mode\n(I < 20 мкА)", size=10, fill="#f3f4f6", stroke=MUTED))

    render(os.path.join(OUT, "firmware-event-loop-timing.svg"), W, H, *p, title="Часовий профіль обробки подій та розділення доступу до шин")

# ── 4. spi-i2c-crosstalk-mitigation: Механізм перехресних завад та захист ──
def fig_spi_i2c_crosstalk_mitigation():
    W, H = 940, 440
    p = []

    # Лівий блок: Неправильне трасування (Суміжні паралельні доріжки)
    p.append(rect(30, 45, 420, 370, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(240, 75, "НЕПРАВИЛЬНО: Тісне паралельне трасування", size=13, color=POS, bold=True))

    # Доріжка SPI SCK
    p.append(line(70, 130, 400, 130, color=FIELD, sw=3))
    p.append(text(235, 115, "SPI SCK (50 МГц, tr = 1.5 нс, dV/dt > 2 В/нс)", size=10.5, color=FIELD, bold=True))

    # Паразитна ємність Cm
    for x in (140, 200, 260, 320):
        p.append(line(x, 130, x, 190, color=POS, sw=1.5, dash="3 3"))
        p.append(text(x + 12, 160, "Cm", size=9, color=POS))

    # Доріжка I2C SDA
    p.append(line(70, 190, 400, 190, color=NEG, sw=2.5))
    p.append(text(235, 210, "I2C SDA / SCL (Високий імпеданс, R_pullup = 4.7k)", size=10.5, color=NEG, bold=True))

    # Осцилограма завади
    p.append(fitbox(60, 240, 360, 75, "Наслідок: Ємнісний струм Ic = Cm · (dV/dt)\nстворює імпульсний викид V_noise > 0.8 В на лінії I2C.\nДатчик BME280 сприймає заваду як хибний ACK/START!", size=10.5, fill="#ffffff", stroke=POS))

    p.append(fitbox(60, 335, 360, 60, "Результат: Зависання апаратного контролера I2C\nу стані BUSY та збій протоколу зв'язку.", size=10.5, fill="#fee2e2", stroke=POS))

    # Правий блок: Правильне трасування (Правило 3W + Guard Trace)
    p.append(rect(480, 45, 430, 370, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(695, 75, "ПРАВИЛЬНО: Правило 3W + Охоронна земля GND", size=13, color=FIELD, bold=True))

    # Доріжка SPI SCK
    p.append(line(520, 130, 870, 130, color=FIELD, sw=3))
    p.append(text(695, 115, "SPI SCK (Траса шириною W = 0.2 мм)", size=10.5, color=FIELD, bold=True))

    # Охоронна земляна доріжка (Guard Trace)
    p.append(line(520, 165, 870, 165, color=LINE, sw=4))
    p.append(text(695, 155, "GND Guard Trace з прошивними отворами Via на L2", size=10, color=LINE, bold=True))
    for x in (560, 630, 700, 770, 840):
        p.append(circle(x, 165, 3.5, fill="#cbd5e1", stroke=INK, sw=1.2))

    # Доріжка I2C SDA
    p.append(line(520, 205, 870, 205, color=NEG, sw=2.5))
    p.append(text(695, 225, "I2C SDA (Відстань S ≥ 3W = 0.6 мм до SPI)", size=10.5, color=NEG, bold=True))

    # Осцилограма захищеного сигналу
    p.append(fitbox(510, 240, 370, 75, "Захист: Електричні силові лінії замикаються на Guard Trace.\nПаразитна ємність знижується у 15-20 разів.\nАмплітуда завади V_noise < 40 мВ (безпечно для КМОН).", size=10.5, fill="#ffffff", stroke=FIELD))

    p.append(fitbox(510, 335, 370, 60, "Результат: Бездоганна паралельна робота SPI DMA\nта вичитування сенсорів I2C на 400 кГц.", size=10.5, fill="#dcfce7", stroke=FIELD))

    render(os.path.join(OUT, "spi-i2c-crosstalk-mitigation.svg"), W, H, *p, title="Придушення ємнісних перехресних завад між шинами SPI та I2C")

if __name__ == "__main__":
    fig_node_system_architecture()
    fig_pcb_layout_zoning()
    fig_firmware_event_loop_timing()
    fig_spi_i2c_crosstalk_mitigation()
    print("Всі 4 фігури успішно згенеровано у ./img/")
