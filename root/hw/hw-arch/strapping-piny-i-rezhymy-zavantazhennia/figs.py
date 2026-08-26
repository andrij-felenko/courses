# -*- coding: utf-8 -*-
"""figs.py — генератор SVG-фігур для теми «Strapping-піни й режими завантаження».
Використовує svgkit зі scripts/ (не копіювати примітиви).
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Кольорові акценти
WARN_ORANGE = "#d35400"
STATE_LATCH = "#8e44ad"
CYAN_ACCENT = "#16a085"


def fig_reset_latch_timing():
    """Фігура 1: Апаратна засувка (Hardware Reset Latch) та часові діаграми t_su / t_h."""
    W, H = 840, 520
    p = []

    # ── Ліва частина: Внутрішня схемотехніка засувки (x: 20..380) ──
    p.append(rect(20, 20, 360, 480, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(200, 46, "Апаратна структура strapping-вузла в кремнії", size=13, color=INK, bold=True))

    # Пін зовні мікроконтролера
    p.append(rect(35, 170, 75, 42, fill="#fff3e0", stroke=WARN_ORANGE, sw=1.8, rx=4))
    p.append(text(72, 191, "GPIO / Strap", size=11, color=WARN_ORANGE, bold=True))
    p.append(text(72, 205, "(фізичний пін)", size=9.5, color=MUTED))

    # Внутрішні слабкі підтяжки
    p.append(rect(145, 75, 100, 48, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(195, 94, "Weak Pull-Up", size=10.5, color=NEG, bold=True))
    p.append(text(195, 110, "40–100 кОм", size=9.5, color=MUTED))

    p.append(rect(145, 265, 100, 48, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    p.append(text(195, 284, "Weak Pull-Down", size=10.5, color=NEG, bold=True))
    p.append(text(195, 300, "40–100 кОм", size=9.5, color=MUTED))

    # Лінії підтяжок до вхідної магістралі
    p.append(line(195, 123, 195, 191, color=NEG, sw=1.4, dash="3,3"))
    p.append(line(195, 265, 195, 191, color=NEG, sw=1.4, dash="3,3"))
    p.append(arrow(110, 191, 140, 191, color=INK, sw=1.6))
    p.append(circle(140, 191, 3.5, fill=INK, stroke=INK))
    p.append(line(140, 191, 260, 191, color=INK, sw=1.6))

    # D-засувка (Hardware Latch)
    p.append(rect(260, 155, 105, 75, fill="#f5eef8", stroke=STATE_LATCH, sw=1.8, rx=6))
    p.append(text(312, 178, "D-Latch", size=12, color=STATE_LATCH, bold=True))
    p.append(text(275, 198, "D", size=11, color=INK, bold=True))
    p.append(text(348, 198, "Q", size=11, color=INK, bold=True))
    p.append(text(288, 222, "LE / CLK", size=9.5, color=MUTED))

    # Сигнал RESET_N як строб засувки
    p.append(line(200, 360, 312, 360, color=POS, sw=1.6))
    p.append(arrow(312, 360, 312, 230, color=POS, sw=1.6))
    p.append(text(140, 362, "Сигнал RESET_N", size=11, color=POS, bold=True))
    p.append(text(140, 378, "(фронт стробує засувку)", size=9.5, color=MUTED))

    # Вихід засувки до системного регістру
    p.append(arrow(365, 191, 375, 191, color=STATE_LATCH, sw=1.8))

    # Системний конфігураційний регістр
    p.append(rect(45, 420, 325, 60, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(207, 442, "Системний регістр конфігурації", size=11.5, color=FIELD, bold=True))
    p.append(text(207, 460, "ESP32 GPIO_STRAP / i.MX SRC_SBMR / STM32 OPTR", size=9.5, color=INK))
    p.append(arrow(375, 191, 375, 450, color=STATE_LATCH, sw=1.6))
    p.append(line(375, 450, 370, 450, color=STATE_LATCH, sw=1.6))

    # ── Права частина: Часова діаграма (x: 400..820) ──
    p.append(rect(400, 20, 420, 480, fill="#ffffff", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(610, 46, "Часові параметри захоплення рівня (Reset Release)", size=13, color=INK, bold=True))

    # Вісь часу t
    p.append(arrow(430, 470, 800, 470, color=INK, sw=1.5))
    p.append(text(805, 474, "t", size=12, color=INK, italic=True))

    # Рівні сигналів
    # 1. Живлення VDD
    p.append(text(430, 85, "VDD (3.3V)", size=11, color=INK, anchor="start", bold=True))
    p.append(line(510, 100, 550, 70, color=FIELD, sw=2))
    p.append(line(550, 70, 790, 70, color=FIELD, sw=2))

    # 2. Сигнал RESET_N (активний нуль, вихід зі скидання)
    p.append(text(430, 160, "RESET_N", size=11, color=POS, anchor="start", bold=True))
    p.append(line(510, 180, 630, 180, color=POS, sw=2))
    p.append(line(630, 180, 650, 140, color=POS, sw=2))  # фронт відпускання
    p.append(line(650, 140, 790, 140, color=POS, sw=2))

    # Вертикальна лінія відпускання скидання
    p.append(line(650, 60, 650, 450, color=POS, sw=1.5, dash="4,4"))
    p.append(text(650, 462, "Reset Release", size=9.5, color=POS, bold=True))

    # 3. Рівень на Strapping-піні (GPIO)
    p.append(text(430, 240, "Вхід Pin (D)", size=11, color=WARN_ORANGE, anchor="start", bold=True))
    # Зона невизначеності -> стабільний рівень -> вільний перехід у GPIO
    p.append(rect(505, 225, 70, 30, fill="#fdecea", stroke=POS, sw=1, rx=2))
    p.append(text(540, 244, "Перехідний стан", size=9.5, color=POS))
    p.append(line(575, 230, 690, 230, color=WARN_ORANGE, sw=2.2))  # стабільна 1
    p.append(line(690, 230, 720, 255, color=WARN_ORANGE, sw=1.5, dash="2,2"))
    p.append(line(720, 255, 790, 255, color=INK, sw=1.5))
    p.append(text(755, 275, "Режим GPIO", size=9.5, color=INK, italic=True))

    # Інтервали t_su (setup) та t_h (hold)
    p.append(rect(575, 275, 75, 24, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    p.append(text(612, 291, "t_su ≥ 20 нс", size=10, color=NEG, bold=True))
    p.append(line(575, 250, 575, 275, color=NEG, sw=1, dash="2,2"))
    p.append(line(650, 250, 650, 275, color=NEG, sw=1, dash="2,2"))

    p.append(rect(650, 275, 45, 24, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=3))
    p.append(text(672, 291, "t_h", size=10, color=NEG, bold=True))
    p.append(line(695, 250, 695, 275, color=NEG, sw=1, dash="2,2"))

    # 4. Вихід засувки (Latch Output Q)
    p.append(text(430, 350, "Засувка (Q)", size=11, color=STATE_LATCH, anchor="start", bold=True))
    p.append(line(510, 370, 650, 370, color=MUTED, sw=1.5, dash="3,3"))
    p.append(text(575, 360, "Попередній стан", size=9.5, color=MUTED))
    p.append(line(650, 370, 655, 335, color=STATE_LATCH, sw=2.5))
    p.append(line(655, 335, 790, 335, color=STATE_LATCH, sw=2.5))
    p.append(text(725, 325, "Зафіксовано 1 (Latch locked)", size=9.5, color=STATE_LATCH, bold=True))

    # Пояснювальний блок унизу
    p.append(rect(420, 400, 380, 48, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4))
    p.append(text(610, 418, "Засувка стає непрозорою в момент висхідного фронту RESET_N.", size=9.5, color=INK))
    p.append(text(610, 434, "Подальші зміни на піні не впливають на апаратну конфігурацію.", size=9.5, color=INK))

    render(os.path.join(IMG, "reset-latch-timing.svg"), W, H, *p)


def fig_boot_matrix_flow():
    """Фігура 2: Дерево прийняття рішень та матриця режимів завантаження (STM32, ESP32, i.MX RT)."""
    W, H = 840, 520
    p = []

    # Заголовок панелі
    p.append(rect(15, 15, 810, 490, fill="#ffffff", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(420, 42, "Матриця апаратного вибору режимів завантаження", size=15, color=INK, bold=True))

    # Стовпчик 1: STM32 (x: 35..275)
    p.append(rect(35, 65, 245, 425, fill="#fcfdfe", stroke=NEG, sw=1.5, rx=6))
    p.append(rect(35, 65, 245, 35, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6))
    p.append(text(157, 88, "STM32 (Cortex-M)", size=13, color=NEG, bold=True))

    # STM32 логіка
    p.append(textbox(157, 130, "Вхідний пін BOOT0\n(або nBOOT0 Option Byte)", size=10.5, pad=6, fill="#ffffff", stroke=LINE)[0])
    p.append(arrow(157, 155, 157, 185, color=INK, sw=1.4))

    # Гілка BOOT0 = 0
    p.append(rect(50, 190, 105, 65, fill="#eef7f0", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(102, 210, "BOOT0 = 0", size=10, color=FIELD, bold=True))
    p.append(text(102, 226, "Main Flash", size=11, color=INK, bold=True))
    p.append(text(102, 242, "0x08000000", size=9.5, color=MUTED))

    # Гілка BOOT0 = 1
    p.append(rect(165, 190, 105, 65, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(217, 210, "BOOT0 = 1", size=10, color=POS, bold=True))
    p.append(text(217, 226, "Опитування BOOT1", size=10, color=INK, bold=True))
    p.append(text(217, 242, "(або nBOOT1 біт)", size=9.5, color=MUTED))

    p.append(arrow(217, 255, 217, 285, color=INK, sw=1.4))

    p.append(rect(165, 290, 105, 80, fill="#fff3e0", stroke=WARN_ORANGE, sw=1.4, rx=4))
    p.append(text(217, 308, "BOOT1 = 0", size=9.5, color=WARN_ORANGE, bold=True))
    p.append(text(217, 324, "System Memory", size=10.5, color=INK, bold=True))
    p.append(text(217, 340, "ROM Bootloader", size=9.5, color=INK))
    p.append(text(217, 356, "(UART / DFU)", size=9.5, color=MUTED))

    p.append(rect(50, 290, 105, 80, fill="#f5eef8", stroke=STATE_LATCH, sw=1.4, rx=4))
    p.append(text(102, 308, "BOOT1 = 1", size=9.5, color=STATE_LATCH, bold=True))
    p.append(text(102, 324, "Embedded SRAM", size=10.5, color=INK, bold=True))
    p.append(text(102, 340, "Прямий запуск", size=9.5, color=INK))
    p.append(text(102, 356, "0x20000000", size=9.5, color=MUTED))

    p.append(fitbox(45, 395, 225, 80, "Сучасні серії (G0/G4/H7):\nАпаратний BOOT1 вилучено;\nконфігурація задається бітами\nOption Bytes у незмінній Flash.", size=9.5, fill="#f4f6f8", stroke=MUTED))

    # Стовпчик 2: ESP32 родина (x: 295..545)
    p.append(rect(295, 65, 250, 425, fill="#fcfdfe", stroke=WARN_ORANGE, sw=1.5, rx=6))
    p.append(rect(295, 65, 250, 35, fill="#fff3e0", stroke=WARN_ORANGE, sw=1.5, rx=6))
    p.append(text(420, 88, "ESP32 (WROOM / S3 / C3)", size=13, color=WARN_ORANGE, bold=True))

    p.append(textbox(420, 130, "GPIO0 (Strap пін)\n+ стан GPIO2 / GPIO12", size=10.5, pad=6, fill="#ffffff", stroke=LINE)[0])
    p.append(arrow(420, 155, 420, 185, color=INK, sw=1.4))

    # GPIO0 = 1 (Normal SPI Boot)
    p.append(rect(305, 190, 110, 85, fill="#eef7f0", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(360, 210, "GPIO0 = 1", size=10, color=FIELD, bold=True))
    p.append(text(360, 228, "SPI Flash Boot", size=11, color=INK, bold=True))
    p.append(text(360, 246, "Завантаження з", size=9.5, color=INK))
    p.append(text(360, 260, "зовнішньої Flash", size=9.5, color=MUTED))

    # GPIO0 = 0 (Download Mode)
    p.append(rect(425, 190, 110, 85, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    p.append(text(480, 210, "GPIO0 = 0", size=10, color=POS, bold=True))
    p.append(text(480, 228, "Download Mode", size=11, color=INK, bold=True))
    p.append(text(480, 246, "Очікування образу", size=9.5, color=INK))
    p.append(text(480, 260, "UART0 / USB-CDC", size=9.5, color=MUTED))

    # GPIO12 напруга VDD_SDIO
    p.append(rect(305, 290, 230, 90, fill="#fbfcfd", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(420, 310, "GPIO12 (MTDI): Напруга Flash", size=10.5, color=INK, bold=True))
    p.append(text(420, 328, "GPIO12 = 0 -> VDD_SDIO = 3.3V (Норма)", size=9.5, color=FIELD))
    p.append(text(420, 346, "GPIO12 = 1 -> VDD_SDIO = 1.8V (Flash Fail)", size=9.5, color=POS, bold=True))
    p.append(text(420, 364, "Блокування: eFuse VDD_SDIO_FORCE", size=9.5, color=MUTED))

    p.append(fitbox(305, 395, 230, 80, "ESP32-S3 / C3 / C6:\nStrapping на GPIO0, GPIO8, GPIO9;\nвбудований USB-JTAG/Serial\nперемикає bootloader без DTR/RTS.", size=9.5, fill="#f4f6f8", stroke=MUTED))

    # Стовпчик 3: NXP i.MX RT (x: 560..810)
    p.append(rect(560, 65, 250, 425, fill="#fcfdfe", stroke=STATE_LATCH, sw=1.5, rx=6))
    p.append(rect(560, 65, 250, 35, fill="#f5eef8", stroke=STATE_LATCH, sw=1.5, rx=6))
    p.append(text(685, 88, "NXP i.MX RT (Crossover)", size=13, color=STATE_LATCH, bold=True))

    p.append(textbox(685, 130, "BOOT_MODE[1:0] піни\n(00 / 01 / 10 / 11)", size=10.5, pad=6, fill="#ffffff", stroke=LINE)[0])
    p.append(arrow(685, 155, 685, 185, color=INK, sw=1.4))

    # i.MX режими
    p.append(rect(570, 190, 110, 85, fill="#f5eef8", stroke=STATE_LATCH, sw=1.4, rx=4))
    p.append(text(625, 210, "BOOT_MODE = 00", size=9.5, color=STATE_LATCH, bold=True))
    p.append(text(625, 228, "Boot From Fuses", size=10.5, color=INK, bold=True))
    p.append(text(625, 246, "Ігнорує піни,", size=9.5, color=INK))
    p.append(text(625, 260, "читає OTP eFuse", size=9.5, color=MUTED))

    p.append(rect(690, 190, 110, 85, fill="#eef7f0", stroke=FIELD, sw=1.4, rx=4))
    p.append(text(745, 210, "BOOT_MODE = 10", size=9.5, color=FIELD, bold=True))
    p.append(text(745, 228, "Internal Boot", size=10.5, color=INK, bold=True))
    p.append(text(745, 246, "Вибір носія через", size=9.5, color=INK))
    p.append(text(745, 260, "BOOT_CFG піни", size=9.5, color=MUTED))

    p.append(rect(570, 290, 230, 90, fill="#fff3e0", stroke=WARN_ORANGE, sw=1.2, rx=4))
    p.append(text(685, 310, "BOOT_MODE = 01: Serial Downloader", size=10, color=WARN_ORANGE, bold=True))
    p.append(text(685, 328, "Завантаження образу через USB OTG / UART", size=9.5, color=INK))
    p.append(text(685, 346, "Захист у серії: eFuse BT_FUSE_SEL = 1", size=9.5, color=POS, bold=True))
    p.append(text(685, 364, "(блокує зовнішні піни конфігурації)", size=9.5, color=MUTED))

    p.append(fitbox(570, 395, 230, 80, "Гнучкість vs Безпека:\nДля налагодження використовують\nBOOT_CFG; у серійних виробах\nфіксують завантаження через eFuse.", size=9.5, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(IMG, "boot-matrix-flow.svg"), W, H, *p)


def fig_pin_sharing_traps_circuits():
    """Фігура 3: Пастки сумісного використання пінів та схемотехніка безпечної ізоляції."""
    W, H = 840, 520
    p = []

    p.append(rect(15, 15, 810, 490, fill="#ffffff", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(420, 42, "Конфлікти сумісного використання пінів та схеми ізоляції", size=15, color=INK, bold=True))

    # ── Ліва колонка: Пастки (Traps) (x: 30..395) ──
    p.append(rect(30, 65, 370, 425, fill="#fdf7f7", stroke=POS, sw=1.4, rx=6))
    p.append(rect(30, 65, 370, 32, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    p.append(text(215, 86, "ТИПОВІ ПАСТКИ (Критичні збої)", size=12, color=POS, bold=True))

    # Пастка 1: Світлодіод на GPIO0 (тягне до землі)
    p.append(rect(45, 110, 340, 105, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 128, "Пастка 1: Світлодіод на ESP32 GPIO0 (на GND)", size=10.5, color=POS, bold=True))
    p.append(text(80, 155, "GPIO0", size=10, color=INK, bold=True))
    p.append(line(110, 150, 140, 150, color=INK, sw=1.5))
    # Резистор + LED до GND
    p.append(rect(140, 140, 35, 20, fill="#fff", stroke=INK, sw=1.2))
    p.append(text(157, 154, "1k", size=9.5, color=INK))
    p.append(line(175, 150, 200, 150, color=INK, sw=1.5))
    p.append(circle(210, 150, 9, fill="#fee", stroke=POS))
    p.append(text(210, 154, "LED", size=9.5, color=POS))
    p.append(line(219, 150, 235, 150, color=INK, sw=1.5))
    p.append(line(235, 142, 235, 158, color=INK, sw=1.5))  # GND
    p.append(line(238, 145, 238, 155, color=INK, sw=1.2))
    p.append(line(241, 148, 241, 152, color=INK, sw=1))

    p.append(text(215, 180, "Наслідок: Дільник з внутрішнім pull-up садить пін у 0V.", size=9.5, color=POS))
    p.append(text(215, 196, "МК зависає в режимі ROM Bootloader при кожному скиданні.", size=9.5, color=INK))

    # Пастка 2: Pull-up на GPIO12 (MTDI)
    p.append(rect(45, 230, 340, 115, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 248, "Пастка 2: Підтяжка на ESP32 GPIO12 (Реле / I2C)", size=10.5, color=POS, bold=True))
    p.append(text(80, 275, "GPIO12", size=10, color=INK, bold=True))
    p.append(line(120, 270, 150, 270, color=INK, sw=1.5))
    p.append(line(150, 270, 150, 290, color=INK, sw=1.5))
    p.append(rect(135, 290, 30, 22, fill="#fff", stroke=INK, sw=1.2))
    p.append(text(150, 305, "4.7k", size=9.5, color=INK))
    p.append(line(150, 312, 150, 325, color=POS, sw=1.5))
    p.append(text(150, 336, "3.3V", size=9.5, color=POS, bold=True))

    p.append(text(265, 275, "Flash LDO перемикається", size=9.5, color=POS, bold=True))
    p.append(text(265, 290, "з 3.3V на 1.8V!", size=9.5, color=POS, bold=True))
    p.append(text(215, 318, "Наслідок: SPI Flash перестає читатися -> циклічний boot loop.", size=9.5, color=INK))
    p.append(text(215, 332, "Повідомлення ROM: «flash read err, 1000».", size=9.5, color=MUTED))

    # Пастка 3: Відсутність конденсатора на EN
    p.append(rect(45, 360, 340, 115, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(215, 378, "Пастка 3: Відсутність RC-фільтра на піні EN", size=10.5, color=POS, bold=True))
    p.append(text(215, 400, "У схемі автопрошивки DTR/RTS пін EN відпускається", size=9.5, color=INK))
    p.append(text(215, 416, "раніше, ніж GPIO0 встигає сісти в стабільний 0.", size=9.5, color=INK))
    p.append(text(215, 436, "Симптом: «Failed to connect to ESP32: Timed out...»", size=9.5, color=POS, bold=True))
    p.append(text(215, 456, "Лікування: Конденсатор 100 нФ–1 мкФ між EN та GND.", size=9.5, color=FIELD, bold=True))

    # ── Права колонка: Безпечні рішення (Safe Circuits) (x: 420..795) ──
    p.append(rect(420, 65, 390, 425, fill="#f7fbf8", stroke=FIELD, sw=1.4, rx=6))
    p.append(rect(420, 65, 390, 32, fill="#eef7f0", stroke=FIELD, sw=1.4, rx=6))
    p.append(text(615, 86, "БЕЗПЕЧНІ СХЕМИ РОЗВ'ЯЗКИ (Ізоляція)", size=12, color=FIELD, bold=True))

    # Рішення 1: Тристабільний буфер 74LVC1G125
    p.append(rect(435, 110, 360, 110, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(615, 128, "Рішення 1: Тристабільний буфер (74LVC1G125)", size=10.5, color=FIELD, bold=True))
    p.append(text(475, 155, "GPIO0", size=10, color=INK, bold=True))
    p.append(arrow(495, 150, 525, 150, color=INK, sw=1.5))
    # Трикутник буфера
    p.append(rect(525, 135, 45, 30, fill="#edf7ed", stroke=FIELD, sw=1.5, rx=3))
    p.append(text(547, 154, "BUF", size=10, color=FIELD, bold=True))
    p.append(arrow(570, 150, 600, 150, color=INK, sw=1.5))
    p.append(text(640, 155, "Навантаження", size=9.5, color=INK, bold=True))
    # Вхід дозволу OE
    p.append(line(547, 195, 547, 165, color=NEG, sw=1.4))
    p.append(text(547, 207, "~OE (Enable від Reset або прошивки)", size=9.5, color=NEG))
    p.append(text(615, 180, "Під час скидання буфер у стані Hi-Z (високоімпедансний).", size=9.5, color=INK))

    # Рішення 2: N-MOSFET ключ (2N7002)
    p.append(rect(435, 230, 360, 115, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(615, 248, "Рішення 2: N-MOSFET ключ з підтяжкою затвора до GND", size=10.5, color=FIELD, bold=True))
    p.append(text(475, 275, "GPIO12", size=10, color=INK, bold=True))
    p.append(arrow(500, 270, 530, 270, color=INK, sw=1.5))
    # Затвор польовика
    p.append(rect(530, 255, 40, 30, fill="#fff", stroke=INK, sw=1.2, rx=2))
    p.append(text(550, 273, "FET", size=9.5, color=INK))
    p.append(line(550, 285, 550, 305, color=INK, sw=1.2))
    p.append(rect(538, 305, 24, 15, fill="#fff", stroke=INK, sw=1))
    p.append(text(550, 316, "100k", size=9.5, color=MUTED))
    p.append(line(550, 320, 550, 330, color=INK, sw=1.2))  # GND
    p.append(arrow(570, 270, 600, 270, color=INK, sw=1.5))
    p.append(text(650, 275, "Реле / LED", size=9.5, color=INK, bold=True))
    p.append(text(615, 338, "Затвор не навантажує пін під час reset (струм витоку < 1 мкА).", size=9.5, color=INK))

    # Рішення 3: eFuse блокування
    p.append(rect(435, 360, 360, 115, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(615, 378, "Рішення 3: Апаратне спалювання eFuse у продакшні", size=10.5, color=FIELD, bold=True))
    p.append(text(615, 398, "1. espefuse.py set_flash_voltage 3.3V (блокує GPIO12)", size=9.5, color=INK))
    p.append(text(615, 414, "2. eFuse BT_FUSE_SEL = 1 на i.MX RT (блокує BOOT_CFG)", size=9.5, color=INK))
    p.append(text(615, 430, "3. FLASH_OPTR nBOOT_SEL на STM32 (ігнорує BOOT0 пін)", size=9.5, color=INK))
    p.append(text(615, 454, "Результат: Strapping-піни звільняються під 100% вільні GPIO!", size=9.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "pin-sharing-traps-circuits.svg"), W, H, *p)


if __name__ == "__main__":
    print("Генерація SVG-фігур для strapping-piny-i-rezhymy-zavantazhennia...")
    fig_reset_latch_timing()
    fig_boot_matrix_flow()
    fig_pin_sharing_traps_circuits()
    print("Усі фігури успішно згенеровано.")
