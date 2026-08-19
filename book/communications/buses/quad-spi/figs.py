# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми Quad-SPI (QSPI)."""

import sys
import os

# Імпорт svgkit з scripts/ (4 рівні вгору від book/communications/buses/quad-spi)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)


def fig_topology():
    """Фізична топологія шини Quad-SPI: контролер мікроконтролера та мікросхема Flash."""
    w, h = 760, 360
    frags = []

    # Хост: Мікроконтролер (QSPI Controller)
    h_box, _, _ = textbox(130, 180, "Мікроконтролер (MCU)\nАпаратний контролер QSPI\n(Master)", 
                          size=13, pad=12, fill="#eaf2f8", stroke="#2457d6", bold=True)
    frags.append(h_box)

    # Ведений: Зовнішня Flash-пам'ять
    f_box, _, _ = textbox(630, 180, "Flash-пам'ять (NOR)\nКорпус SOIC-8 / WSON-8\n(Slave)", 
                          size=13, pad=12, fill="#fef9e7", stroke="#d4ac0d", bold=True)
    frags.append(f_box)

    # Лінії та підписи
    lines_info = [
        (75, "CS# (Chip Select)", "Однонаправлена (Active Low)", LINE, True),
        (115, "CLK (Serial Clock)", "Синхронізація (до 133 МГц)", LINE, True),
        (160, "IO0 (SI / DI)", "Двонаправлена: Команда / Адреса / Data 0", "#27ae60", False),
        (205, "IO1 (SO / DO)", "Двонаправлена: Data 1", "#27ae60", False),
        (250, "IO2 (WP# / Data 2)", "Двонаправлена: Захист запису або Data 2", "#c0392b", False),
        (295, "IO3 (HOLD# / Data 3)", "Двонаправлена: Призупинення або Data 3", "#c0392b", False),
    ]

    for y, sig, desc, col, unidir in lines_info:
        # Лінія
        if unidir:
            frags.append(arrow(240, y, 510, y, color=col, sw=1.8))
        else:
            # Двонаправлена стрілка (лінія з мітками на обох кінцях або позначенням двонаправленості)
            frags.append(line(240, y, 510, y, color=col, sw=2.0))
            frags.append(circle(245, y, 3.5, fill=col, stroke=col))
            frags.append(circle(505, y, 3.5, fill=col, stroke=col))

        # Текстові мітки над лінією та під нею
        frags.append(text(375, y - 5, sig, size=11, color=INK, bold=True))
        frags.append(text(375, y + 12, desc, size=9.5, color=MUTED, italic=True))

    # Вивід живлення та підтяжок (символічно праворуч)
    frags.append(fitbox(280, 328, 200, 24, "Підтяжка до VDD у стані Hi-Z", size=10, fill="#f4f6f8", stroke=MUTED))

    render(os.path.join(IMG_DIR, "qspi-topology-signals.svg"), w, h, *frags)


def fig_transactions():
    """Порівняння часових діаграм транзакцій швидкого читання: 1-1-1, 1-1-4, 1-4-4 та 0-4-4."""
    w, h = 820, 420
    frags = []

    # Заголовок та легенда
    y_starts = [65, 145, 235, 325]
    modes = [
        ("1-1-1 Fast Read (0x0B)", "40 тактів оверхеду + 256 тактів даних (32 байти)", 6.25),
        ("1-1-4 Quad Output (0x6B)", "40 тактів оверхеду + 64 такти даних (32 байти)", 20.0),
        ("1-4-4 Quad I/O (0xEB)", "20 тактів оверхеду + 64 такти даних (32 байти)", 30.5),
        ("0-4-4 Continuous Mode", "12 тактів оверхеду + 64 такти даних (XIP пропуск опкоду)", 33.7),
    ]

    for idx, (title, desc, _) in enumerate(modes):
        y = y_starts[idx]
        frags.append(text(20, y - 8, title, size=12, color=INK, bold=True, anchor="start"))
        frags.append(text(300, y - 8, desc, size=10.5, color=MUTED, anchor="start"))

        # Блоки фаз транзакції
        x = 20
        if idx == 0:
            # 1-1-1: Cmd(8t, 1-bit) -> Addr(24t, 1-bit) -> Dummy(8t) -> Data(256t)
            frags.append(fitbox(x, y, 70, 32, "Опкод (8t)\n1 лінія", size=10, fill="#fadbd8", stroke="#c0392b"))
            x += 74
            frags.append(fitbox(x, y, 110, 32, "Адреса 24-біт (24t)\n1 лінія (IO0)", size=10, fill="#d4efdf", stroke="#27ae60"))
            x += 114
            frags.append(fitbox(x, y, 70, 32, "Dummy (8t)\nHi-Z стан", size=10, fill="#ebedef", stroke="#7f8c8d"))
            x += 74
            frags.append(fitbox(x, y, 500, 32, "Фаза даних 32 байти (256 тактів @ 1 лінія IO1) — тривала передача", size=11, fill="#d6eaf8", stroke="#2457d6", bold=True))

        elif idx == 1:
            # 1-1-4: Cmd(8t, 1-bit) -> Addr(24t, 1-bit) -> Dummy(8t) -> Data(64t)
            frags.append(fitbox(x, y, 70, 32, "Опкод (8t)\n1 лінія", size=10, fill="#fadbd8", stroke="#c0392b"))
            x += 74
            frags.append(fitbox(x, y, 110, 32, "Адреса 24-біт (24t)\n1 лінія (IO0)", size=10, fill="#d4efdf", stroke="#27ae60"))
            x += 114
            frags.append(fitbox(x, y, 70, 32, "Dummy (8t)\nHi-Z стан", size=10, fill="#ebedef", stroke="#7f8c8d"))
            x += 74
            frags.append(fitbox(x, y, 220, 32, "Дані 32Б (64 такти @ 4 лінії IO0..IO3)", size=11, fill="#d6eaf8", stroke="#2457d6", bold=True))
            x += 224
            frags.append(fitbox(x, y, 276, 32, "Швидкість даних ×4 вища порівняно з 1-1-1", size=10.5, fill="#fcf3cf", stroke="#f39c12"))

        elif idx == 2:
            # 1-4-4: Cmd(8t, 1-bit) -> Addr(6t, 4-bit) -> Mode(2t, 4-bit) -> Dummy(4t) -> Data(64t)
            frags.append(fitbox(x, y, 70, 32, "Опкод (8t)\n1 лінія", size=10, fill="#fadbd8", stroke="#c0392b"))
            x += 74
            frags.append(fitbox(x, y, 70, 32, "Адр (6t)\n4 лінії", size=10, fill="#d4efdf", stroke="#27ae60"))
            x += 74
            frags.append(fitbox(x, y, 65, 32, "Mode (2t)\n0xA5", size=10, fill="#e8daef", stroke="#8e44ad"))
            x += 69
            frags.append(fitbox(x, y, 65, 32, "Dum (4t)\nHi-Z", size=10, fill="#ebedef", stroke="#7f8c8d"))
            x += 69
            frags.append(fitbox(x, y, 220, 32, "Дані 32Б (64 такти @ 4 лінії IO0..IO3)", size=11, fill="#d6eaf8", stroke="#2457d6", bold=True))
            x += 224
            frags.append(fitbox(x, y, 282, 32, "Затримка адресації скорочена на 75% (з 24 до 6 тактів)", size=10.5, fill="#d5f5e3", stroke="#27ae60"))

        elif idx == 3:
            # 0-4-4: Addr(6t, 4-bit) -> Mode(2t, 4-bit) -> Dummy(4t) -> Data(64t)
            frags.append(fitbox(x, y, 70, 32, "[Пропуск]\n0 тактів", size=10, fill="#eaecee", stroke="#bdc3c7", italic=True))
            x += 74
            frags.append(fitbox(x, y, 70, 32, "Адр (6t)\n4 лінії", size=10, fill="#d4efdf", stroke="#27ae60"))
            x += 74
            frags.append(fitbox(x, y, 65, 32, "Mode (2t)\n0xA5", size=10, fill="#e8daef", stroke="#8e44ad"))
            x += 69
            frags.append(fitbox(x, y, 65, 32, "Dum (4t)\nHi-Z", size=10, fill="#ebedef", stroke="#7f8c8d"))
            x += 69
            frags.append(fitbox(x, y, 220, 32, "Дані 32Б (64 такти @ 4 лінії IO0..IO3)", size=11, fill="#d6eaf8", stroke="#2457d6", bold=True))
            x += 224
            frags.append(fitbox(x, y, 282, 32, "Максимальна ефективність XIP для кеш-ліній", size=10.5, fill="#d4efdf", stroke="#229954", bold=True))

    render(os.path.join(IMG_DIR, "transaction-comparison-modes.svg"), w, h, *frags)


def fig_controller_datapath():
    """Внутрішній апаратний тракт QSPI-контролера мікроконтролера та XIP-транслятор."""
    w, h = 800, 390
    frags = []

    # Шина ядра процесора
    frags.append(fitbox(50, 15, 700, 36, "Системна шина мікроконтролера (AHB / AXI Matrix 32/64-біт, до 480 МГц)", 
                        size=13, fill="#eaf2f8", stroke="#2457d6", bold=True))

    # Зв'язок від шини до блоків контролера
    frags.append(arrow(200, 51, 200, 85, color="#2457d6", sw=1.8))
    frags.append(arrow(550, 51, 550, 85, color="#2457d6", sw=1.8))

    # Велика рамка QSPI контролера
    frags.append(rect(40, 85, 720, 230, fill="#fdfefe", stroke="#7f8c8d", sw=1.5, rx=8))
    frags.append(text(400, 105, "Апаратний периферійний модуль QSPI (Регістрова логіка та кінцевий автомат)", 
                      size=13, color="#2c3e50", bold=True))

    # Ліва частина: Memory-Mapped транслятор адреси (XIP)
    frags.append(fitbox(60, 125, 300, 65, "Memory-Mapped Address Decoder\n(Трансляція 0x90000000..0x9FFFFFFF\nу фізичні адреси Flash-пам'яті)", 
                        size=11, fill="#fcf3cf", stroke="#f39c12", bold=True))

    # Права частина: Регістровий блок (CR, DCR, CCR)
    frags.append(fitbox(400, 125, 340, 65, "Керуючі регістри контролера\nQUADSPI_CR (Prescaler, Modes, IRQ)\nQUADSPI_CCR (5 фаз протоколу) · QUADSPI_DCR", 
                        size=11, fill="#e8f8f5", stroke="#1abc9c", bold=True))

    # Середня частина: Кінцевий автомат протоколу та FIFO
    frags.append(fitbox(60, 210, 300, 85, "Апаратний кінцевий автомат (FSM)\n• Генерація опкоду та адрес\n• Керування бітами Mode (0xA5)\n• Відлік Dummy-тактів та реверс ліній", 
                        size=10.5, fill="#f4f6f7", stroke="#34495e"))

    frags.append(fitbox(400, 210, 340, 85, "Блок передачі та буферизації\n• 32-бітний FIFO прийому/передачі (16 слів)\n• 4-бітний зсувний регістр (Shift Engine)\n• Дільник частоти SCK (до 133 МГц)", 
                        size=10.5, fill="#f4f6f7", stroke="#34495e"))

    # Стрілки всередині контролера
    frags.append(arrow(210, 190, 210, 210, color=LINE, sw=1.5))
    frags.append(arrow(570, 190, 570, 210, color=LINE, sw=1.5))
    frags.append(arrow(360, 252, 400, 252, color=LINE, sw=1.5))

    # Вихід на зовнішні виводи
    frags.append(arrow(210, 295, 210, 340, color="#c0392b", sw=2.0))
    frags.append(arrow(570, 295, 570, 340, color="#27ae60", sw=2.0))

    frags.append(fitbox(100, 340, 220, 32, "Керуючі виводи: CS#, CLK", size=11, fill="#fadbd8", stroke="#c0392b", bold=True))
    frags.append(fitbox(460, 340, 220, 32, "Шина даних: IO0, IO1, IO2, IO3", size=11, fill="#d4efdf", stroke="#27ae60", bold=True))

    render(os.path.join(IMG_DIR, "controller-datapath-xip.svg"), w, h, *frags)


def fig_cache_burst():
    """Елімінація латентності XIP за допомогою пакетного кешування рядка (Cache Line Fill)."""
    w, h = 820, 360
    frags = []

    # 1. Сценарій без кешування: випадковий доступ
    frags.append(text(20, 25, "1. Випадковий доступ без кешу (Random XIP Fetch): простої конвеєра ядра", 
                      size=12, color="#c0392b", bold=True, anchor="start"))

    y1 = 45
    # Запит 1
    frags.append(fitbox(20, y1, 130, 30, "Latency: 16 тактів\n(CS + Addr + Dummy)", size=9.5, fill="#fadbd8", stroke="#c0392b"))
    frags.append(fitbox(152, y1, 60, 30, "Word 0\n(2t)", size=9.5, fill="#d6eaf8", stroke="#2457d6"))

    # Запит 2 (перехід)
    frags.append(fitbox(220, y1, 130, 30, "Latency: 16 тактів\n(CS + Addr + Dummy)", size=9.5, fill="#fadbd8", stroke="#c0392b"))
    frags.append(fitbox(352, y1, 60, 30, "Word 1\n(2t)", size=9.5, fill="#d6eaf8", stroke="#2457d6"))

    # Запит 3
    frags.append(fitbox(420, y1, 130, 30, "Latency: 16 тактів\n(CS + Addr + Dummy)", size=9.5, fill="#fadbd8", stroke="#c0392b"))
    frags.append(fitbox(552, y1, 60, 30, "Word 2\n(2t)", size=9.5, fill="#d6eaf8", stroke="#2457d6"))

    frags.append(fitbox(620, y1, 180, 30, "Ефективність: ~11% часу шини\nЯдро очікує 89% часу", size=9.5, fill="#f2d7d5", stroke="#c0392b", bold=True))

    # 2. Сценарій з кешуванням рядка (32 байти / 8 слів): Burst Read
    frags.append(text(20, 130, "2. Кешування рядка (32-byte I-Cache Line Fill): розмиття накладних витрат", 
                      size=12, color="#27ae60", bold=True, anchor="start"))

    y2 = 150
    # Накладні витрати
    frags.append(fitbox(20, y2, 130, 32, "Початкова затримка\n12 тактів (0-4-4)", size=10, fill="#fcf3cf", stroke="#f39c12"))

    # 8 слів поспіль у Burst режимі
    bx = 154
    for i in range(8):
        frags.append(fitbox(bx, y2, 42, 32, "W%d\n(2t)" % i, size=9.5, fill="#d5f5e3", stroke="#27ae60"))
        bx += 44

    frags.append(fitbox(bx + 10, y2, 280, 32, "Суцільний Burst 32Б (16 тактів)\nЗагальний час заповнення: 28 тактів", size=10, fill="#d4efdf", stroke="#229954", bold=True))

    # Подальші виконання з кешу
    frags.append(text(20, 230, "3. Наступні вибірки інструкцій із кешу (Cache Hits @ 480 МГц):", 
                      size=12, color="#2457d6", bold=True, anchor="start"))

    y3 = 250
    frags.append(fitbox(20, y3, 95, 34, "Hit: W0 (0 WS)\n1 такт ядра", size=9.5, fill="#ebf5fb", stroke="#3498db"))
    frags.append(fitbox(120, y3, 95, 34, "Hit: W1 (0 WS)\n1 такт ядра", size=9.5, fill="#ebf5fb", stroke="#3498db"))
    frags.append(fitbox(220, y3, 95, 34, "Hit: W2 (0 WS)\n1 такт ядра", size=9.5, fill="#ebf5fb", stroke="#3498db"))
    frags.append(fitbox(320, y3, 95, 34, "Hit: W3 (0 WS)\n1 такт ядра", size=9.5, fill="#ebf5fb", stroke="#3498db"))
    frags.append(fitbox(420, y3, 95, 34, "Hit: W4..W7\n0 тактів очікування", size=9.5, fill="#ebf5fb", stroke="#3498db"))

    frags.append(fitbox(530, y3, 270, 34, "Продуктивність на рівні внутрішньої Flash\n(Ефективний IPC ядра ≈ 1.25)", size=10.5, fill="#d4efdf", stroke="#27ae60", bold=True))

    # Підсумок знизу
    frags.append(fitbox(20, 305, 780, 26, "Апаратний кеш + режим 0-4-4 перетворює повільний послідовний Flash на пам'ять з нульовими тактами затримки для циклів коду", 
                        size=10.5, fill="#f4f6f8", stroke="#7f8c8d", bold=True))

    render(os.path.join(IMG_DIR, "cache-xip-latency-burst.svg"), w, h, *frags)


def main():
    fig_topology()
    fig_transactions()
    fig_controller_datapath()
    fig_cache_burst()
    print("Всі 4 фігури успішно згенеровано у img/")


if __name__ == "__main__":
    main()
