# -*- coding: utf-8 -*-
"""Фігури до теми «ROM-завантажувач: як чип приймає прошивку».
Запуск: python figs.py -> генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def fig_memory_remap():
    W, H = 820, 430
    f = [text(W / 2, 30,
              "Апаратний ремапінг: трансляція адреси 0x00000000 при скиданні",
              size=15, bold=True)]

    # Ліва колонка: Ядро процесора та адресний простір 0x00000000
    f.append(rect(40, 70, 180, 290, fill="#fdfefe", stroke=LINE, sw=1.8))
    f.append(text(130, 95, "Ядро Cortex-M", size=13.5, bold=True))
    f.append(text(130, 115, "Читання Reset Vector", size=10.5, color=MUTED))

    # Складові всередині ядра
    f.append(rect(55, 140, 150, 50, fill="#eef2f7", stroke=NEG, sw=1.5))
    f.append(text(130, 160, "MSP: 0x00000000", size=11, bold=True, color=NEG))
    f.append(text(130, 178, "Вказівник стека", size=10, color=MUTED))

    f.append(rect(55, 210, 150, 50, fill="#eef2f7", stroke=POS, sw=1.5))
    f.append(text(130, 230, "PC: 0x00000004", size=11, bold=True, color=POS))
    f.append(text(130, 248, "Вектор скидання", size=10, color=MUTED))

    f.append(rect(55, 285, 150, 55, fill="#f4f6f8", stroke=LINE, sw=1.2))
    f.append(text(130, 305, "Шина AHB / I-Code", size=10.5, bold=True))
    f.append(text(130, 325, "Звернення до 0x00000000", size=9.5, color=MUTED))

    # Центральний блок: Апаратний мультиплексор ремапінгу
    f.append(rect(290, 120, 200, 190, fill="#f9fbfd", stroke="#2457d6", sw=2))
    f.append(text(390, 145, "Мультиплексор Remap", size=13, bold=True, color=NEG))
    f.append(text(390, 165, "SYSCFG / Bus Matrix", size=10.5, color=MUTED))

    # Керуючі сигнали зверху мультиплексора
    f.append(arrow(390, 60, 390, 120, color=POS, sw=1.8))
    f.append(text(390, 50, "Сигнали: BOOT0, BOOT1 / Option Bytes", size=10.5, bold=True, color=POS))

    # З'єднання від ядра до мультиплексора
    f.append(arrow(220, 215, 290, 215, color=LINE, sw=2))
    f.append(text(255, 205, "Адреса", size=10, color=MUTED))

    # Права колонка: Фізичні ділянки пам'яті
    # 1. Main Flash
    f.append(rect(560, 70, 220, 80, fill="#eafaf1", stroke=FIELD, sw=1.8))
    f.append(text(670, 95, "Main Flash (0x08000000)", size=12, bold=True, color=FIELD))
    f.append(text(670, 115, "BOOT0 = 0 (Нормальний старт)", size=10, bold=True))
    f.append(text(670, 135, "Користувацька прошивка", size=10, color=MUTED))

    # 2. System Memory ROM
    f.append(rect(560, 175, 220, 85, fill="#fdecea", stroke=POS, sw=2))
    f.append(text(670, 200, "System Memory (0x1FFFF000)", size=12, bold=True, color=POS))
    f.append(text(670, 220, "BOOT0 = 1, BOOT1 = 0", size=10, bold=True, color=POS))
    f.append(text(670, 240, "Фабричний ROM-завантажувач", size=10, color=MUTED))

    # 3. Embedded SRAM
    f.append(rect(560, 285, 220, 80, fill="#eaf0fd", stroke=NEG, sw=1.8))
    f.append(text(670, 310, "SRAM (0x20000000)", size=12, bold=True, color=NEG))
    f.append(text(670, 330, "BOOT0 = 1, BOOT1 = 1", size=10, bold=True))
    f.append(text(670, 350, "ОЗП для швидкого тестування", size=10, color=MUTED))

    # Стрілки від мультиплексора до блоків пам'яті
    f.append(arrow(490, 170, 560, 110, color=FIELD, sw=1.6))
    f.append(arrow(490, 215, 560, 215, color=POS, sw=2))
    f.append(arrow(490, 260, 560, 325, color=NEG, sw=1.6))

    b, _, _ = textbox(W / 2, 400,
                      "Адреса 0x00000000 є апаратним аліасом. Ядро завжди читає вектори з нуля, "
                      "а фізичне джерело обирає конфігурація BOOT.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "memory-remap.svg"), W, H, *f)


def fig_autobaud_sequence():
    W, H = 820, 380
    f = [text(W / 2, 28,
              "Синхронізація швидкості (Autobauding) та відповідь ACK",
              size=15, bold=True)]

    # Ліва частина: Осцилограма байта 0x7F
    f.append(rect(40, 60, 440, 265, fill="#ffffff", stroke=LINE, sw=1.5))
    f.append(text(260, 85, "Байт 0x7F (01111111b, 8E1) на лінії RX", size=12.5, bold=True))

    # Лінія осцилограми
    y_high, y_low = 140, 200
    points = [
        (60, y_high), (90, y_high),      # Idle
        (90, y_low), (130, y_low),       # Start bit (0)
        (130, y_high), (370, y_high),    # D0..D6 = 1
        (370, y_low), (410, y_low),      # D7 = 0
        (410, y_low), (430, y_low),      # Parity = 0
        (430, y_high), (460, y_high)     # Stop = 1
    ]
    path_d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in points)
    f.append(f'<path d="{path_d}" fill="none" stroke="{POS}" stroke-width="2.5"/>')

    # Підписи бітів
    f.append(text(110, y_low + 22, "START (0)", size=10, bold=True, color=POS))
    f.append(text(250, y_high - 12, "D0 ... D6 = 1 (7 бітових інтервалів)", size=10, bold=True, color=FIELD))
    f.append(text(390, y_low + 22, "D7=0", size=9.5, color=MUTED))
    f.append(text(445, y_high - 12, "STOP=1", size=9.5, color=MUTED))

    # Вимірювальна лінійка під Start bit
    f.append(line(90, 240, 130, 240, color=NEG, sw=1.8))
    f.append(line(90, 235, 90, 245, color=NEG, sw=1.5))
    f.append(line(130, 235, 130, 245, color=NEG, sw=1.5))
    f.append(text(110, 258, "1 біт = T_bit", size=10.5, bold=True, color=NEG))

    # Формула розрахунку
    f.append(rect(60, 275, 400, 40, fill="#f4f6f8", stroke=LINE, sw=1))
    f.append(text(260, 298, "USARTDIV = (f_HSI) / (16 · BaudRate) -> запис у регістр BRR",
                  size=10.5, bold=True, color=INK))

    # Права частина: Кроки обміну хост <-> завантажувач
    f.append(rect(510, 60, 270, 265, fill="#fdfefe", stroke=LINE, sw=1.5))
    f.append(text(645, 85, "Протокольне рукостискання", size=12.5, bold=True))

    # Крок 1: Хост шле 0x7F
    f.append(rect(525, 110, 240, 45, fill="#fdecea", stroke=POS, sw=1.5))
    f.append(text(645, 128, "1. Хост надсилає 0x7F", size=11, bold=True, color=POS))
    f.append(text(645, 144, "Синхронізація швидкості", size=9.5, color=MUTED))

    # Крок 2: Завантажувач міряє
    f.append(rect(525, 170, 240, 45, fill="#eef2f7", stroke=NEG, sw=1.5))
    f.append(text(645, 188, "2. ROM підлаштовує UART", size=11, bold=True, color=NEG))
    f.append(text(645, 204, "Фіксація дільника такту", size=9.5, color=MUTED))

    # Крок 3: Завантажувач шле ACK
    f.append(rect(525, 230, 240, 45, fill="#eafaf1", stroke=FIELD, sw=1.8))
    f.append(text(645, 248, "3. Відповідь: ACK (0x79)", size=11, bold=True, color=FIELD))
    f.append(text(645, 264, "Готовність до команд", size=9.5, color=MUTED))

    f.append(arrow(645, 155, 645, 170, color=LINE, sw=1.4))
    f.append(arrow(645, 215, 645, 230, color=LINE, sw=1.4))

    b, _, _ = textbox(W / 2, 355,
                      "Завдяки перепаду 0 -> 1 на початку байта 0x7F завантажувач безпомилково "
                      "вимірює довжину біта за внутрішнім RC-генератором.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "autobaud-sequence.svg"), W, H, *f)


def fig_boot_polling_loop():
    W, H = 820, 410
    f = [text(W / 2, 28,
              "Цикл сканування та захоплення інтерфейсу в System ROM",
              size=15, bold=True)]

    # Старт
    f.append(circle(90, 190, 40, fill="#eef2f7", stroke=NEG, sw=2))
    f.append(text(90, 185, "Reset", size=12, bold=True, color=NEG))
    f.append(text(90, 202, "BOOT0=1", size=10, color=MUTED))

    # Ініціалізація
    f.append(rect(170, 160, 140, 60, fill="#f9fbfd", stroke=LINE, sw=1.5))
    f.append(text(240, 185, "Старт HSI RC", size=11.5, bold=True))
    f.append(text(240, 205, "Базова тактова", size=10, color=MUTED))

    f.append(arrow(130, 190, 170, 190, color=LINE, sw=1.8))
    f.append(arrow(310, 190, 360, 190, color=LINE, sw=1.8))

    # Блок опитування периферії
    f.append(rect(360, 60, 210, 260, fill="#fdfefe", stroke=LINE, sw=1.8))
    f.append(text(465, 85, "Цикл сканування портів", size=12, bold=True))

    interfaces = [
        ("USART1 / USART2", "Спад RX -> 0x7F?"),
        ("USB DFU", "VBUS / Reset на DP/DM?"),
        ("I2C1", "Address Match (0x52 / 0x72)?"),
        ("SPI1", "Спад NSS / такти SCK?"),
        ("CAN1 / CAN2", "Кадр синхронізації?")
    ]

    for i, (name, cond) in enumerate(interfaces):
        y_box = 105 + i * 40
        f.append(rect(375, y_box, 180, 34, fill="#f4f6f8", stroke=LINE, sw=1.2))
        f.append(text(465, y_box + 14, name, size=10.5, bold=True, color=INK))
        f.append(text(465, y_box + 26, cond, size=9.5, color=MUTED))

    # Стрілка захоплення
    f.append(arrow(570, 190, 630, 190, color=POS, sw=2))
    f.append(text(600, 178, "Активність", size=10, bold=True, color=POS))

    # Правий блок: Блокування порту та обробка протоколу
    f.append(rect(630, 120, 160, 140, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(710, 145, "Port Locking", size=12.5, bold=True, color=FIELD))
    f.append(text(710, 170, "Вимкнення інших", size=10, color=MUTED))
    f.append(text(710, 188, "інтерфейсів", size=10, color=MUTED))
    f.append(text(710, 215, "Вхід у цикл команд", size=10.5, bold=True, color=FIELD))
    f.append(text(710, 235, "GET / WRITE / ERASE", size=9.5, color=MUTED))

    # Зворотна петля опитування (якщо немає активності)
    f.append(f'<path d="M 465 320 L 465 350 L 330 350 L 330 190" fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="4,4"/>')
    f.append(text(395, 365, "Немає активності -> повторне опитування", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 385,
                      "Завантажувач слухає всі доступні шини одночасно. Перший інтерфейс, де отримано "
                      "валідне рукостискання, монополізує чип до наступного скидання.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "boot-polling-loop.svg"), W, H, *f)


def fig_rdp_security_levels():
    W, H = 820, 390
    f = [text(W / 2, 28,
              "Рівні захисту від читання (RDP): стани та апаратні наслідки",
              size=15, bold=True)]

    # 3 блоки рівнів
    # Level 0
    f.append(rect(40, 70, 220, 230, fill="#eafaf1", stroke=FIELD, sw=2))
    f.append(text(150, 98, "Level 0 (0xAA)", size=14, bold=True, color=FIELD))
    f.append(text(150, 118, "Відкритий режим", size=11, color=MUTED))
    f.append(line(55, 130, 245, 130, color=FIELD, sw=1))
    f.append(text(150, 155, "SWD / JTAG: ДОЗВОЛЕНО", size=10.5, bold=True, color=FIELD))
    f.append(text(150, 180, "ROM Bootloader: ПОВНИЙ", size=10.5, bold=True, color=FIELD))
    f.append(text(150, 205, "Читання Flash: ТАК", size=10, color=INK))
    f.append(text(150, 230, "Запис Flash: ТАК", size=10, color=INK))
    f.append(text(150, 265, "Режим розробки та", size=9.5, color=MUTED))
    f.append(text(150, 280, "первинної прошивки", size=9.5, color=MUTED))

    # Level 1
    f.append(rect(300, 70, 220, 230, fill="#fdfefe", stroke=POS, sw=2))
    f.append(text(410, 98, "Level 1 (0x55 / інші)", size=14, bold=True, color=POS))
    f.append(text(410, 118, "Захист від дампу", size=11, color=MUTED))
    f.append(line(315, 130, 505, 130, color=POS, sw=1))
    f.append(text(410, 155, "SWD: БЛОКОВАНО читання", size=10.5, bold=True, color=POS))
    f.append(text(410, 180, "ROM Boot: лише RAM/Option", size=10.5, bold=True, color=POS))
    f.append(text(410, 205, "Виконання з Flash: ТАК", size=10, color=INK))
    f.append(text(410, 230, "Зовнішній доступ: NACK / 0x00", size=10, color=POS))
    f.append(text(410, 265, "Стандартний захист для", size=9.5, color=MUTED))
    f.append(text(410, 280, "серійних виробів", size=9.5, color=MUTED))

    # Level 2
    f.append(rect(560, 70, 220, 230, fill="#fdecea", stroke="#78281f", sw=2.2))
    f.append(text(670, 98, "Level 2 (0xCC)", size=14, bold=True, color="#78281f"))
    f.append(text(670, 118, "Апаратний лок (Chip Lock)", size=11, color=MUTED))
    f.append(line(575, 130, 765, 130, color="#78281f", sw=1))
    f.append(text(670, 155, "SWD / JTAG: ВИМКНЕНО", size=10.5, bold=True, color="#78281f"))
    f.append(text(670, 180, "ROM Boot: ЗАБЛОКОВАНО", size=10.5, bold=True, color="#78281f"))
    f.append(text(670, 205, "Оновлення: лише OTA у Flash", size=10, color=INK))
    f.append(text(670, 230, "Зворотний шлях: НЕМОЖЛИВИЙ", size=10, bold=True, color="#78281f"))
    f.append(text(670, 265, "Незворотне запечатування", size=9.5, color=MUTED))
    f.append(text(670, 280, "фінального кристала", size=9.5, color=MUTED))

    # Стрілки переходів
    # 0 -> 1
    f.append(arrow(260, 150, 300, 150, color=POS, sw=1.8))
    f.append(text(280, 138, "Запис RDP", size=9.5, color=MUTED))

    # 1 -> 0 (Регресія)
    f.append(arrow(300, 210, 260, 210, color=POS, sw=2))
    f.append(text(280, 198, "1 -> 0", size=9.5, bold=True, color=POS))
    f.append(text(280, 226, "Mass Erase!", size=9.5, bold=True, color=POS))

    # 1 -> 2
    f.append(arrow(520, 150, 560, 150, color="#78281f", sw=2))
    f.append(text(540, 138, "Запис 0xCC", size=9.5, color=MUTED))

    b, _, _ = textbox(W / 2, 355,
                      "Зняття захисту з Level 1 на Level 0 апаратно стирає всю Flash-пам'ять і SRAM. "
                      "Перехід на Level 2 є незворотним фізичним блокуванням кристала.",
                      size=11, fill="#f4f6f8", stroke=LINE)
    f.append(b)
    render(os.path.join(IMG, "rdp-security-levels.svg"), W, H, *f)


if __name__ == "__main__":
    fig_memory_remap()
    fig_autobaud_sequence()
    fig_boot_polling_loop()
    fig_rdp_security_levels()
    print("All figures generated successfully.")
