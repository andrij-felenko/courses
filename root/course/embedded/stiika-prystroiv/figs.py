# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Фігура 1: Архітектура автоматизованої стійки пристроїв ──────────────────
def fig_rack_architecture():
    W, H = 820, 480
    frags = []

    # Заголовок
    frags.append(text(410, 32, "Архітектура автоматизованої тестової стійки (Device Farm)", size=16, bold=True))

    # Ліва частина: CI/CD Сервер / Хост-комп'ютер
    frags.append(rect(30, 60, 200, 380, fill="#edf2f7", stroke=LINE, sw=2, rx=8))
    frags.append(text(130, 90, "Керівний хост (CI/CD)", size=14, bold=True))
    frags.append(fitbox(45, 115, 170, 40, "Pytest / CTest раннер\nОркестратор тестів", size=11, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(45, 170, 170, 40, "Демон стійки (Rackd)\nМенеджер слотів", size=11, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(45, 225, 170, 40, "udev: фіксовані шляхи\n/dev/dut-slot-XX-*", size=11, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(45, 280, 170, 40, "uhubctl / libusb\nКерування USB VBUS", size=11, fill=BG, stroke=MUTED, sw=1.2))
    frags.append(fitbox(45, 345, 170, 65, "Головне живлення стенда\n12 В / 5 В (MeanWell PSU)\nШина струму до 30 А", size=11, fill="#fef3c7", stroke=POS, sw=1.5))

    # Центральна частина: Керовані USB-хаби та шини
    frags.append(fitbox(270, 100, 150, 60, "Керований USB 3.0 Хаб\n(Індивідуальний VBUS,\nFTDI + SWD зонди)", size=11, fill="#e0f2fe", stroke=NEG, sw=1.6))
    frags.append(fitbox(270, 260, 150, 50, "I2C / USB Релейна плата\n(Комутатори живлення,\nINA219 моніторинг)", size=11, fill="#dcfce7", stroke=FIELD, sw=1.6))

    # З'єднання хост -> хаби
    frags.append(arrow(230, 130, 270, 130, color=NEG, sw=2))
    frags.append(text(250, 122, "USB", size=10, color=NEG, bold=True))

    frags.append(arrow(230, 285, 270, 285, color=FIELD, sw=2))
    frags.append(text(250, 277, "I2C", size=10, color=FIELD, bold=True))

    frags.append(arrow(230, 375, 460, 375, color=POS, sw=2.5))
    frags.append(text(345, 365, "Головна шина живлення DC", size=10, color=POS, bold=True))

    # Права частина: Слоти стійки (DUT 1 та DUT N)
    # Слот 1
    frags.append(rect(460, 60, 330, 180, fill="#f8fafc", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(625, 82, "Тестовий слот #1 (Ізольований канал)", size=13, bold=True))

    frags.append(fitbox(475, 98, 140, 32, "SWD / JTAG Зонд", size=10, fill=BG, stroke=NEG, sw=1.2))
    frags.append(fitbox(635, 98, 140, 32, "UART Консоль (FTDI)", size=10, fill=BG, stroke=NEG, sw=1.2))
    frags.append(fitbox(475, 138, 140, 32, "P-FET / Реле + INA219", size=10, fill=BG, stroke=FIELD, sw=1.2))
    frags.append(fitbox(635, 138, 140, 32, "Ізолятор ліній Ioff", size=10, fill=BG, stroke=MUTED, sw=1.2))

    frags.append(fitbox(475, 180, 300, 48, "Плата-зразок (DUT #1) — STM32 / ESP32\nПовністю автономний зразок у петлі тестів", size=11, fill="#fee2e2", stroke=POS, sw=1.6, bold=True))

    # Слот N
    frags.append(rect(460, 260, 330, 180, fill="#f8fafc", stroke=LINE, sw=1.8, rx=6))
    frags.append(text(625, 282, "Тестовий слот #N (Ізольований канал)", size=13, bold=True))

    frags.append(fitbox(475, 298, 140, 32, "SWD / JTAG Зонд", size=10, fill=BG, stroke=NEG, sw=1.2))
    frags.append(fitbox(635, 298, 140, 32, "UART Консоль (FTDI)", size=10, fill=BG, stroke=NEG, sw=1.2))
    frags.append(fitbox(475, 338, 140, 32, "P-FET / Реле + INA219", size=10, fill=BG, stroke=FIELD, sw=1.2))
    frags.append(fitbox(635, 338, 140, 32, "Ізолятор ліній Ioff", size=10, fill=BG, stroke=MUTED, sw=1.2))

    frags.append(fitbox(475, 380, 300, 48, "Плата-зразок (DUT #N) — STM32 / ESP32\nПаралельний прогін регресійних тестів", size=11, fill="#fee2e2", stroke=POS, sw=1.6, bold=True))

    # З'єднання хабів до слотів
    frags.append(arrow(420, 115, 475, 115, color=NEG, sw=1.5))
    frags.append(arrow(420, 145, 475, 315, color=NEG, sw=1.5))

    frags.append(arrow(420, 275, 475, 155, color=FIELD, sw=1.5))
    frags.append(arrow(420, 295, 475, 355, color=FIELD, sw=1.5))

    frags.append(line(460, 375, 475, 155, color=POS, sw=1.5, dash="3 3"))
    frags.append(line(460, 375, 475, 355, color=POS, sw=1.5, dash="3 3"))

    # Нижній висновок
    frags.append(text(410, 462, "Кожен слот має незалежне живлення, виділений програматор і консоль: збій на одній платі не зупиняє стійку", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, 'rack-architecture.svg'), W, H, *frags,
           title="Архітектура автоматизованої тестової стійки")


# ── Фігура 2: Механізм паразитного підживлення (Phantom Backfeeding) ────────
def fig_parasitic_backfeeding():
    W, H = 800, 440
    frags = []

    frags.append(text(400, 32, "Пастка паразитного живлення (Backfeeding) крізь ESD-діоди", size=16, bold=True))

    # Ліва плата: Програматор / UART адаптер (Живлення подано: 3.3 В)
    frags.append(rect(40, 70, 220, 310, fill="#e0f2fe", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(150, 95, "Хост / Програматор", size=13, bold=True))
    frags.append(fitbox(55, 115, 190, 40, "USB-UART / ST-Link\nЖивлення 3.3 В АКТИВНЕ", size=11, fill=BG, stroke=NEG, sw=1.2))

    frags.append(fitbox(55, 180, 190, 35, "UART TX = 3.3 В (High)", size=11, fill="#fef3c7", stroke=POS, sw=1.2, bold=True))
    frags.append(fitbox(55, 230, 190, 35, "SWDIO / SWCLK = 3.3 В", size=11, fill="#fef3c7", stroke=POS, sw=1.2, bold=True))
    frags.append(fitbox(55, 320, 190, 35, "Спільна земля (GND)", size=11, fill=BG, stroke=LINE, sw=1.2))

    # Права плата: DUT (Живлення ВИМКНЕНО реле, VDD = 0 В очікується)
    frags.append(rect(460, 70, 300, 310, fill="#fef2f2", stroke=POS, sw=1.8, rx=6))
    frags.append(text(610, 95, "Знеструмлена плата (DUT)", size=13, bold=True))
    frags.append(fitbox(480, 115, 260, 35, "Реле живлення VCC: РОЗІМКНУТО", size=11, fill="#fee2e2", stroke=POS, sw=1.4, bold=True))

    # Внутрішня структура захисту GPIO всередині чипа
    frags.append(rect(480, 165, 260, 195, fill=BG, stroke=LINE, sw=1.4, rx=4))
    frags.append(text(610, 185, "Вхідний буфер GPIO чипа", size=11, bold=True))

    # ESD Діод верхнього плеча (Pin -> VDD_MCU)
    frags.append(line(520, 215, 590, 215, color=POS, sw=2))
    frags.append(line(590, 215, 590, 230, color=POS, sw=2))
    # Діодний символ
    frags.append(rect(575, 230, 30, 20, fill="#fde68a", stroke=POS, sw=1.4))
    frags.append(text(590, 244, "▲ ESD", size=9, bold=True, color=POS))
    frags.append(line(590, 250, 590, 275, color=POS, sw=2))

    # Внутрішня шина VDD_MCU
    frags.append(line(550, 275, 720, 275, color=POS, sw=2.5))
    frags.append(text(635, 292, "Внутрішня VDD ≈ 2.7–3.0 В !", size=11, color=POS, bold=True))
    frags.append(text(635, 310, "(Чип у стані 'зомбі'/не вимикається)", size=10, color=POS, italic=True))
    frags.append(text(635, 345, "Ядро зависає, Flash не скидається", size=10, color=MUTED))

    # Дроти між лівою та правою платою
    frags.append(arrow(245, 198, 480, 215, color=POS, sw=2))
    frags.append(text(350, 190, "Струм витоку (10-50 мА)", size=11, color=POS, bold=True))

    frags.append(arrow(245, 248, 480, 248, color=POS, sw=1.8))
    frags.append(text(350, 240, "SWD Pull-Up струм", size=10, color=POS))

    frags.append(line(245, 338, 480, 338, color=LINE, sw=2))
    frags.append(text(350, 330, "GND (Спільна)", size=10, color=MUTED))

    # Нижній висновок: як боротися
    frags.append(rect(40, 395, 720, 35, fill="#f0fdf4", stroke=FIELD, sw=1.4, rx=4))
    frags.append(text(400, 417, "Рішення: Буфери з функцією Ioff (SN74LVC1T45) або переведення ліній програматора в Hi-Z при Power-Off", size=11, color=FIELD, bold=True))

    render(os.path.join(IMG, 'parasitic-backfeeding.svg'), W, H, *frags,
           title="Механізм паразитного підживлення крізь ESD-діоди")


# ── Фігура 3: Схема комутатора живлення слота з Soft-Start та захистом ───────
def fig_power_switching_softstart():
    W, H = 820, 440
    frags = []

    frags.append(text(410, 32, "Комутатор живлення слота: P-MOSFET ключ, плавний пуск та моніторинг", size=16, bold=True))

    # Секція 1: Схема ключа
    frags.append(rect(30, 60, 440, 315, fill="#f8fafc", stroke=LINE, sw=1.6, rx=6))
    frags.append(text(250, 85, "Апаратна схема комутації High-Side", size=13, bold=True))

    # Вхід V_MAIN (5 В / 12 В)
    frags.append(fitbox(45, 110, 90, 35, "V_MAIN\n+5 В / +12 В", size=11, fill="#fef3c7", stroke=POS, sw=1.4, bold=True))

    # Ключ P-MOSFET + Soft-Start RC
    frags.append(rect(160, 105, 150, 90, fill=BG, stroke=FIELD, sw=1.6, rx=4))
    frags.append(text(235, 125, "P-MOSFET (AO3401 / IRF7404)", size=10, bold=True))
    frags.append(text(235, 142, "C_gate (100 нФ) + R_gate (100 кОм)", size=9, color=MUTED))
    frags.append(text(235, 160, "Керує dV/dt (Soft-Start ≈ 5 мс)", size=9, color=FIELD, bold=True))
    frags.append(text(235, 180, "N-FET драйвер затвора", size=9, color=MUTED))

    # З'єднання входу з MOSFET
    frags.append(arrow(135, 128, 160, 128, color=POS, sw=2.5))

    # Шунт INA219
    frags.append(fitbox(335, 110, 110, 45, "INA219 Шунт\n(0.05 Ом, I2C)\nВимір I & V", size=10, fill="#e0f2fe", stroke=NEG, sw=1.4))
    frags.append(arrow(310, 128, 335, 128, color=POS, sw=2.5))

    # Сигнал увімкнення GPIO
    frags.append(fitbox(70, 220, 120, 35, "GPIO_PWR_EN\n(Від MCU стійки)", size=10, fill=BG, stroke=LINE, sw=1.2))
    frags.append(arrow(190, 238, 235, 195, color=LINE, sw=1.5))

    # Вихід до DUT
    frags.append(arrow(390, 155, 390, 220, color=POS, sw=2.5))
    frags.append(fitbox(325, 220, 130, 45, "Вихід VCC_DUT\nДо плати зразка\n(Керований пуск)", size=11, fill="#dcfce7", stroke=FIELD, sw=1.6, bold=True))

    # Захисний TVS та конденсатор
    frags.append(fitbox(160, 285, 270, 60, "Захисний каскад на виході:\n- TVS-діод (SMAJ5.0A) проти індуктивних викидів\n- Самовідновний запобіжник eFuse / PTC (2 А)", size=10, fill="#fffbeb", stroke=POS, sw=1.2))

    # Секція 2: Графік струму (Без плавного пуску проти Плавного пуску)
    frags.append(rect(490, 60, 300, 315, fill="#ffffff", stroke=LINE, sw=1.6, rx=6))
    frags.append(text(640, 85, "Осцилограма вхідного струму I_in", size=13, bold=True))

    # Осі графіка
    frags.append(line(520, 320, 760, 320, color=LINE, sw=1.5)) # Вісь t
    frags.append(line(520, 320, 520, 120, color=LINE, sw=1.5)) # Вісь I
    frags.append(text(765, 324, "t", size=12, bold=True))
    frags.append(text(515, 115, "I (A)", size=12, bold=True))

    # Крива 1: Пряме реле без soft-start (Різкий стрибок 30 А)
    frags.append(line(520, 320, 530, 320, color=POS, sw=2))
    frags.append(line(530, 320, 535, 135, color=POS, sw=2.5)) # Стрибок
    frags.append(line(535, 135, 545, 300, color=POS, sw=2))
    frags.append(line(545, 300, 620, 305, color=POS, sw=2))
    frags.append(text(600, 140, "Без Soft-Start: I_pk = 30 А !", size=10, color=POS, bold=True))
    frags.append(text(600, 155, "(Іскріння реле, провал шини 12 В)", size=9, color=POS))

    # Крива 2: З Soft-Start P-FET (Плавне наростання до 1.2 А)
    frags.append(line(520, 320, 540, 320, color=FIELD, sw=2))
    frags.append(line(540, 320, 570, 275, color=FIELD, sw=2.5))
    frags.append(line(570, 275, 620, 280, color=FIELD, sw=2.5))
    frags.append(line(620, 280, 740, 305, color=FIELD, sw=2.5))
    frags.append(text(640, 240, "З Soft-Start RC: I_pk < 1.5 А", size=10, color=FIELD, bold=True))
    frags.append(text(640, 255, "(Плавний заряд ємностей DUT)", size=9, color=FIELD))

    # Нижній висновок
    frags.append(text(410, 410, "Soft-start захищає контакти комутаторів від ерозії та усуває просідання напруги на сусідніх слотах", size=12, color=MUTED, italic=True))

    render(os.path.join(IMG, 'power-switching-softstart.svg'), W, H, *frags,
           title="Схема комутатора живлення слота з Soft-Start та захистом")


# ── Фігура 4: Ланцюг стабільної ідентифікації пристроїв через udev ────────────
def fig_usb_udev_mapping():
    W, H = 820, 420
    frags = []

    frags.append(text(410, 32, "Ланцюг стабільної адресації обладнання стійки через udev", size=16, bold=True))

    # Колонка 1: Фізичний рівень USB
    frags.append(rect(30, 65, 220, 290, fill="#f1f5f9", stroke=LINE, sw=1.6, rx=6))
    frags.append(text(140, 90, "Фізичне дерево USB", size=13, bold=True))

    frags.append(fitbox(45, 110, 190, 45, "Хаб Порт 1-2.1\nСерійник: FT4232_A01_01\n(UART Консоль Слота 1)", size=10, fill=BG, stroke=NEG, sw=1.2))
    frags.append(fitbox(45, 170, 190, 45, "Хаб Порт 1-2.2\nСерійник: JLINK_98765432\n(SWD Зонд Слота 1)", size=10, fill=BG, stroke=NEG, sw=1.2))
    frags.append(fitbox(45, 230, 190, 45, "Хаб Порт 1-2.3\nСерійник: RELAY_PWR_S01\n(Комутатор VCC 1)", size=10, fill=BG, stroke=FIELD, sw=1.2))
    frags.append(fitbox(45, 290, 190, 45, "Хаб Порт 1-3.*\n(Обладнання Слота 2...)", size=10, fill="#f8fafc", stroke=MUTED, sw=1))

    # Колонка 2: Правила udev у Linux
    frags.append(rect(285, 65, 250, 290, fill="#fef3c7", stroke=LINE, sw=1.6, rx=6))
    frags.append(text(410, 90, "/etc/udev/rules.d/99-rack.rules", size=12, bold=True))

    frags.append(fitbox(295, 110, 230, 50, "SUBSYSTEM==\"tty\", \\\nATTRS{serial}==\"FT4232_A01_01\", \\\nSYMLINK+=\"dut-slot-01-uart\"", size=9, fill=BG, stroke=LINE, sw=1.2))
    frags.append(fitbox(295, 170, 230, 50, "SUBSYSTEM==\"usb\", \\\nATTRS{serial}==\"JLINK_98765432\", \\\nSYMLINK+=\"dut-slot-01-swd\"", size=9, fill=BG, stroke=LINE, sw=1.2))
    frags.append(fitbox(295, 230, 230, 50, "SUBSYSTEM==\"tty\", \\\nATTRS{serial}==\"RELAY_PWR_S01\", \\\nSYMLINK+=\"dut-slot-01-pwr\"", size=9, fill=BG, stroke=LINE, sw=1.2))
    frags.append(fitbox(295, 290, 230, 45, "udevadm control --reload\nudevadm trigger", size=10, fill="#fef9c3", stroke=MUTED, sw=1))

    # Колонка 3: Передбачувані точки входу для тестів
    frags.append(rect(570, 65, 220, 290, fill="#f0fdf4", stroke=FIELD, sw=1.6, rx=6))
    frags.append(text(680, 90, "Стабільні симлінки в ОС", size=13, bold=True))

    frags.append(fitbox(585, 115, 190, 40, "/dev/dut-slot-01-uart\n(Консоль завжди тут)", size=10, fill=BG, stroke=FIELD, sw=1.4, bold=True))
    frags.append(fitbox(585, 175, 190, 40, "/dev/dut-slot-01-swd\n(SWD зонд завжди тут)", size=10, fill=BG, stroke=FIELD, sw=1.4, bold=True))
    frags.append(fitbox(585, 235, 190, 40, "/dev/dut-slot-01-pwr\n(Керування живленням)", size=10, fill=BG, stroke=FIELD, sw=1.4, bold=True))
    frags.append(fitbox(585, 295, 190, 45, "Pytest Runner:\npytest --slot=1\n(Жодних колізій портів)", size=10, fill="#dcfce7", stroke=FIELD, sw=1.2))

    # Стрілки трансформації
    frags.append(arrow(250, 132, 295, 132, color=LINE, sw=1.8))
    frags.append(arrow(250, 192, 295, 192, color=LINE, sw=1.8))
    frags.append(arrow(250, 252, 295, 252, color=LINE, sw=1.8))

    frags.append(arrow(525, 132, 585, 132, color=FIELD, sw=2))
    frags.append(arrow(525, 192, 585, 192, color=FIELD, sw=2))
    frags.append(arrow(525, 252, 585, 252, color=FIELD, sw=2))

    # Нижній висновок
    frags.append(text(410, 390, "Жорстка прив'язка через udev усуває хаос динамічних імен /dev/ttyUSB0...N при ребутах та перепідключеннях", size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, 'usb-udev-mapping.svg'), W, H, *frags,
           title="Ланцюг стабільної ідентифікації обладнання стійки через udev")


if __name__ == '__main__':
    fig_rack_architecture()
    fig_parasitic_backfeeding()
    fig_power_switching_softstart()
    fig_usb_udev_mapping()
    print("Усі 4 фігури успішно згенеровано у ./img/")
