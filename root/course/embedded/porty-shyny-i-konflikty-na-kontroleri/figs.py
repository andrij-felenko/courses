# -*- coding: utf-8 -*-
"""Фігури до теми «Порти, шини й конфлікти на контролері».
Запуск: python figs.py  → генерує SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Топологія шин та периферії польотного контролера ───────────────────────
def fig_mcu_resource_topology():
    W, H = 940, 580
    f = [text(W / 2, 28, "Апаратна топологія шин і периферії польотного контролера (STM32)",
              size=15, bold=True)]

    # Корпус МК
    mcu_x, mcu_y, mcu_w, mcu_h = 280, 60, 380, 480
    f.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#f8fafc", stroke=MUTED, sw=1.8, rx=12))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 24, "Мікроконтролер STM32 (F4 / F7 / H7)",
                  size=13, bold=True, color=INK))

    # Ядро CPU + Внутрішні шини
    core_x, core_y, core_w, core_h = mcu_x + 25, mcu_y + 42, mcu_w - 50, 70
    f.append(rect(core_x, core_y, core_w, core_h, fill="#e2e8f0", stroke=INK, sw=1.4, rx=6))
    f.append(text(core_x + core_w / 2, core_y + 24, "Cortex-M Core + DMA Controller + NVIC",
                  size=11, bold=True, color=INK))
    f.append(text(core_x + core_w / 2, core_y + 48, "Внутрішня шинна матриця (AHB / APB1 / APB2)",
                  size=10, italic=True, color=MUTED))

    # Периферійні контролери всередині МК
    periphs = [
        ("SPI1 / SPI4", "Високошвидкісні шини (до 42 МГц)", mcu_y + 130, "#e0f2fe", "#0284c7"),
        ("SPI2 / SPI3", "Допоміжні шини пам'яті та OSD", mcu_y + 200, "#e0f2fe", "#0284c7"),
        ("I2C1 / I2C2", "Шина повільних сенсорів (400 кГц)", mcu_y + 270, "#fef3c7", "#d97706"),
        ("UART1..UART8", "Послідовні порти зв'язку", mcu_y + 340, "#f3e8ff", "#9333ea"),
        ("TIM1..TIM8", "Апаратні таймери (PWM / DShot)", mcu_y + 410, "#dcfce7", "#16a34a"),
    ]

    for name, desc, py, bg, bd in periphs:
        f.append(rect(mcu_x + 20, py, mcu_w - 40, 52, fill=bg, stroke=bd, sw=1.3, rx=6))
        f.append(text(mcu_x + 35, py + 22, name, size=11, bold=True, color=bd, anchor="start"))
        f.append(text(mcu_x + 35, py + 40, desc, size=10, color=INK, anchor="start"))

    # Зовнішні пристрої ліворуч (Датчики та інтерфейси)
    left_devs = [
        ("Головний IMU", "ICM-42688-P / BMI270 (8 кГц)", 130, "#e0f2fe", "#0284c7"),
        ("Резервний IMU / Flash", "W25Q128 Flash / OSD MAX7456", 200, "#e0f2fe", "#0284c7"),
        ("Магнітометр + Барометр", "IST8310 + DPS310 (I2C)", 270, "#fef3c7", "#d97706"),
        ("DroneCAN Вузол", "CAN Transceiver / 1 Мбіт/с", 340, "#fee2e2", "#dc2626"),
    ]

    for name, desc, dy, bg, bd in left_devs:
        f.append(rect(25, dy, 225, 52, fill=bg, stroke=bd, sw=1.3, rx=6))
        f.append(text(35, dy + 22, name, size=11, bold=True, color=bd, anchor="start"))
        f.append(text(35, dy + 40, desc, size=10, color=INK, anchor="start"))
        # З'єднувальна лінія
        f.append(line(250, dy + 26, mcu_x + 20, dy + 26, color=bd, sw=1.5))

    # Зовнішні пристрої праворуч (Зв'язок і виконавчі вузли)
    right_devs = [
        ("RC-приймач (CRSF / ELRS)", "UART1 / 420–921 кбод", 130, "#f3e8ff", "#9333ea"),
        ("GNSS Модуль + GPS", "UART3 / 115.2–921.6 кбод", 200, "#f3e8ff", "#9333ea"),
        ("Цифровий VTX / OSD", "UART6 / MSP DisplayPort", 270, "#f3e8ff", "#9333ea"),
        ("ESC Телеметрія", "UART4 / Напівдуплекс", 340, "#f3e8ff", "#9333ea"),
        ("Мотори 1..4 (DShot)", "TIM1 / DMA Burst DShot600", 410, "#dcfce7", "#16a34a"),
        ("LED Strip / Buzzer", "TIM3 / PWM / WS2812B", 480, "#dcfce7", "#16a34a"),
    ]

    for name, desc, dy, bg, bd in right_devs:
        f.append(rect(690, dy, 225, 52, fill=bg, stroke=bd, sw=1.3, rx=6))
        f.append(text(700, dy + 22, name, size=11, bold=True, color=bd, anchor="start"))
        f.append(text(700, dy + 40, desc, size=10, color=INK, anchor="start"))
        # З'єднувальна лінія
        f.append(line(mcu_x + mcu_w - 20, dy + 26, 690, dy + 26, color=bd, sw=1.5))

    render(os.path.join(IMG, "mcu-resource-topology.svg"), W, H, *f)


# ── 2. Конфлікт потоків DMA на STM32F4/F7 проти DMAMUX на STM32H7 ─────────────
def fig_dma_stream_collision():
    W, H = 940, 560
    f = [text(W / 2, 28, "Механіка апаратного конфлікту DMA (STM32F4/F7) проти маршрутизатора DMAMUX (H7)",
              size=14, bold=True)]

    # Ліва частина: STM32F4/F7 жорсткий мультиплексор (Конфлікт)
    lx, ly, lw, lh = 25, 55, 435, 475
    f.append(rect(lx, ly, lw, lh, fill="#fff1f2", stroke="#e11d48", sw=1.6, rx=10))
    f.append(text(lx + lw / 2, ly + 24, "STM32F4 / F7: Фіксована таблиця каналів",
                  size=12, bold=True, color="#e11d48"))
    f.append(text(lx + lw / 2, ly + 44, "Жорсткий мультиплексор: 1 активний Channel на 1 Stream",
                  size=10, italic=True, color=MUTED))

    # Джерела запитів
    f.append(rect(lx + 15, ly + 65, 185, 48, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=6))
    f.append(text(lx + 107, ly + 86, "SPI1_RX (IMU Гіроскоп)", size=10, bold=True, color="#0284c7"))
    f.append(text(lx + 107, ly + 103, "Channel 3 (постійний потік)", size=9, color=INK))

    f.append(rect(lx + 15, ly + 130, 185, 48, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=6))
    f.append(text(lx + 107, ly + 151, "TIM1_UP (DShot Мотори)", size=10, bold=True, color="#16a34a"))
    f.append(text(lx + 107, ly + 168, "Channel 6 (висока частота)", size=9, color=INK))

    f.append(rect(lx + 15, ly + 195, 185, 48, fill="#f3e8ff", stroke="#9333ea", sw=1.2, rx=6))
    f.append(text(lx + 107, ly + 216, "USART6_RX (RC-лінк)", size=10, bold=True, color="#9333ea"))
    f.append(text(lx + 107, ly + 233, "Channel 5 (пакети керування)", size=9, color=INK))

    # Мультиплексор DMA2 Stream 5
    f.append(rect(lx + 235, ly + 95, 185, 120, fill="#fee2e2", stroke="#b91c1c", sw=1.5, rx=8))
    f.append(text(lx + 327, ly + 118, "DMA2 Stream 5", size=11, bold=True, color="#b91c1c"))
    f.append(text(lx + 327, ly + 138, "Селектор каналів 0..7", size=9.5, color=INK))
    f.append(text(lx + 327, ly + 162, "КОНФЛІКТ:", size=10, bold=True, color="#b91c1c"))
    f.append(text(lx + 327, ly + 180, "SPI1_TX (Ch 3) vs", size=9, bold=True, color=INK))
    f.append(text(lx + 327, ly + 196, "TIM1_UP (Ch 6)", size=9, bold=True, color=INK))

    f.append(line(lx + 200, ly + 89, lx + 235, ly + 125, color="#0284c7", sw=1.5))
    f.append(line(lx + 200, ly + 154, lx + 235, ly + 145, color="#16a34a", sw=1.5))
    f.append(line(lx + 200, ly + 219, lx + 235, ly + 165, color="#9333ea", sw=1.5))

    # Наслідки
    f.append(rect(lx + 15, ly + 270, 405, 185, fill="#ffffff", stroke="#e11d48", sw=1.2, rx=6))
    f.append(text(lx + 25, ly + 295, "Наслідки конфлікту на F4 / F7:", size=11, bold=True, color="#e11d48", anchor="start"))
    f.append(text(lx + 25, ly + 322, "1. Один із пристроїв вимикає DMA і переходить на IRQ", size=10, color=INK, anchor="start"))
    f.append(text(lx + 25, ly + 346, "2. Перевантаження CPU перериваннями на високій частоті", size=10, color=INK, anchor="start"))
    f.append(text(lx + 25, ly + 370, "3. Джитер зчитування гіроскопа (падіння з 8 кГц до 2 кГц)", size=10, color=INK, anchor="start"))
    f.append(text(lx + 25, ly + 394, "4. Пропуски кадрів DShot — десинхронізація мотора", size=10, color=INK, anchor="start"))
    f.append(text(lx + 25, ly + 418, "5. Апаратний збій вимагає ручного перепризначення ресурсів", size=10, color=INK, anchor="start"))

    # Права частина: STM32H7 DMAMUX (Гнучка комутація)
    rx_pos, ry, rw, rh = 480, 55, 435, 475
    f.append(rect(rx_pos, ry, rw, rh, fill="#f0fdf4", stroke="#16a34a", sw=1.6, rx=10))
    f.append(text(rx_pos + rw / 2, ry + 24, "STM32H7: Маршрутизатор DMAMUX",
                  size=12, bold=True, color="#16a34a"))
    f.append(text(rx_pos + rw / 2, ry + 44, "Повна матриця перехресних з'єднань (Crossbar Switch)",
                  size=10, italic=True, color=MUTED))

    # Джерела H7
    f.append(rect(rx_pos + 15, ry + 65, 140, 42, fill="#e0f2fe", stroke="#0284c7", sw=1.2, rx=6))
    f.append(text(rx_pos + 85, ry + 90, "SPI1..SPI6", size=10, bold=True, color="#0284c7"))

    f.append(rect(rx_pos + 15, ry + 120, 140, 42, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=6))
    f.append(text(rx_pos + 85, ry + 145, "TIM1..TIM17", size=10, bold=True, color="#16a34a"))

    f.append(rect(rx_pos + 15, ry + 175, 140, 42, fill="#f3e8ff", stroke="#9333ea", sw=1.2, rx=6))
    f.append(text(rx_pos + 85, ry + 200, "USART1..UART8", size=10, bold=True, color="#9333ea"))

    # Матриця DMAMUX
    f.append(rect(rx_pos + 175, ry + 65, 95, 152, fill="#e2e8f0", stroke="#475569", sw=1.4, rx=6))
    f.append(text(rx_pos + 222, ry + 115, "DMAMUX", size=11, bold=True, color="#1e293b"))
    f.append(text(rx_pos + 222, ry + 135, "Crossbar", size=9.5, color="#475569"))
    f.append(text(rx_pos + 222, ry + 155, "Matrix", size=9.5, color="#475569"))

    # Потоки DMA1/DMA2
    f.append(rect(rx_pos + 290, ry + 65, 130, 42, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=6))
    f.append(text(rx_pos + 355, ry + 90, "DMA1 Stream 0", size=10, bold=True, color="#16a34a"))

    f.append(rect(rx_pos + 290, ry + 120, 130, 42, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=6))
    f.append(text(rx_pos + 355, ry + 145, "DMA1 Stream 1", size=10, bold=True, color="#16a34a"))

    f.append(rect(rx_pos + 290, ry + 175, 130, 42, fill="#dcfce7", stroke="#16a34a", sw=1.2, rx=6))
    f.append(text(rx_pos + 355, ry + 200, "DMA2 Stream 0", size=10, bold=True, color="#16a34a"))

    f.append(line(rx_pos + 155, ry + 86, rx_pos + 175, ry + 86, color="#0284c7", sw=1.5))
    f.append(line(rx_pos + 155, ry + 141, rx_pos + 175, ry + 141, color="#16a34a", sw=1.5))
    f.append(line(rx_pos + 155, ry + 196, rx_pos + 175, ry + 196, color="#9333ea", sw=1.5))

    f.append(line(rx_pos + 270, ry + 86, rx_pos + 290, ry + 86, color="#16a34a", sw=1.5))
    f.append(line(rx_pos + 270, ry + 141, rx_pos + 290, ry + 141, color="#16a34a", sw=1.5))
    f.append(line(rx_pos + 270, ry + 196, rx_pos + 290, ry + 196, color="#16a34a", sw=1.5))

    # Переваги H7
    f.append(rect(rx_pos + 15, ry + 270, 405, 185, fill="#ffffff", stroke="#16a34a", sw=1.2, rx=6))
    f.append(text(rx_pos + 25, ry + 295, "Переваги маршрутизації DMAMUX на H7:", size=11, bold=True, color="#16a34a", anchor="start"))
    f.append(text(rx_pos + 25, ry + 322, "1. Довільне з'єднання: будь-який периферійний тригер", size=10, color=INK, anchor="start"))
    f.append(text(rx_pos + 25, ry + 346, "2. Відсутність апаратних колізій Stream/Channel", size=10, color=INK, anchor="start"))
    f.append(text(rx_pos + 25, ry + 370, "3. Одночасна робота SPI IMU, DShot, OSD, Telemetry", size=10, color=INK, anchor="start"))
    f.append(text(rx_pos + 25, ry + 394, "4. Потрібен лише контроль когерентності D-Cache", size=10, color=INK, anchor="start"))
    f.append(text(rx_pos + 25, ry + 418, "5. Висока пропускна здатність шини AXI без затримок", size=10, color=INK, anchor="start"))

    render(os.path.join(IMG, "dma-stream-collision.svg"), W, H, *f)


# ── 3. Таймерні конфлікти: спільний базовий такт і регістр ARR ───────────────
def fig_timer_channel_conflict():
    W, H = 940, 540
    f = [text(W / 2, 28, "Апаратний таймер STM32: спільний Prescaler/ARR та конфлікт протоколів",
              size=14, bold=True)]

    # Загальний блок таймера TIM3
    tx, ty, tw, th = 40, 55, 860, 455
    f.append(rect(tx, ty, tw, th, fill="#f8fafc", stroke=INK, sw=1.6, rx=12))
    f.append(text(tx + 25, ty + 28, "Апаратний таймер загального призначення (наприклад, TIM3 або TIM4)",
                  size=12, bold=True, color=INK, anchor="start"))

    # Базова тактова частина (Спільне ядро таймера)
    bx, by, bw, bh = tx + 20, ty + 45, 820, 85
    f.append(rect(bx, by, bw, bh, fill="#f1f5f9", stroke=MUTED, sw=1.3, rx=8))
    f.append(text(bx + 20, by + 24, "СПІЛЬНЕ ТАКТОВЕ ЯДРО ТАЙМЕРА (Одна спільна часова база)",
                  size=11, bold=True, color="#0f172a", anchor="start"))

    f.append(rect(bx + 20, by + 36, 230, 36, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=4))
    f.append(text(bx + 135, by + 59, "Тактова частота шини APB (84 МГц)", size=10, color=INK))

    f.append(rect(bx + 290, by + 36, 230, 36, fill="#e2e8f0", stroke="#475569", sw=1.2, rx=4))
    f.append(text(bx + 405, by + 59, "Переддільник PSC (Prescaler)", size=10, color=INK))

    f.append(rect(bx + 560, by + 36, 240, 36, fill="#fee2e2", stroke="#dc2626", sw=1.4, rx=4))
    f.append(text(bx + 680, by + 59, "Регістр ARR (Auto-Reload)", size=10, bold=True, color="#dc2626"))

    f.append(line(bx + 250, by + 54, bx + 290, by + 54, color=INK, sw=1.5))
    f.append(line(bx + 520, by + 54, bx + 560, by + 54, color=INK, sw=1.5))

    # 4 вихідні канали
    channels = [
        ("Канал 1 (TIM3_CH1)", "Вихід Motor 1", "DShot600 (Період 1.67 мкс)", "ARR = 140, DMA Burst", "#dcfce7", "#16a34a"),
        ("Канал 2 (TIM3_CH2)", "Вихід Motor 2", "DShot600 (Період 1.67 мкс)", "ARR = 140, DMA Burst", "#dcfce7", "#16a34a"),
        ("Канал 3 (TIM3_CH3)", "Вихід Motor 3", "DShot600 (Період 1.67 мкс)", "ARR = 140, DMA Burst", "#dcfce7", "#16a34a"),
        ("Канал 4 (TIM3_CH4)", "LED Strip (WS2812B)", "КОНФЛІКТ: Потрібен період 1.25 мкс (800 кГц)", "ARR має бути 105, а не 140!", "#fee2e2", "#dc2626"),
    ]

    for i, (ch_name, role, proto, note, bg, bd) in enumerate(channels):
        cy = ty + 145 + i * 62
        f.append(rect(tx + 20, cy, 820, 52, fill=bg, stroke=bd, sw=1.3, rx=6))
        f.append(text(tx + 35, cy + 22, ch_name, size=10.5, bold=True, color=bd, anchor="start"))
        f.append(text(tx + 35, cy + 40, role, size=9.5, color=INK, anchor="start"))

        f.append(text(tx + 260, cy + 22, proto, size=10, bold=True, color=bd, anchor="start"))
        f.append(text(tx + 260, cy + 40, note, size=9.5, italic=True, color=INK, anchor="start"))

        # З'єднання від ARR до кожного каналу
        f.append(line(bx + 680, by + 72, tx + 780, cy + 26, color=bd, sw=1.2, dash="3,3"))

    # Пояснювальний висновок унизу
    f.append(rect(tx + 20, ty + 400, 820, 44, fill="#ffffff", stroke=MUTED, sw=1.2, rx=6))
    f.append(text(tx + 35, ty + 418, "Висновок: канали одного таймера зобов'язані ділити однаковий переддільник PSC та однаковий ліміт ARR.",
                  size=9.5, bold=True, color=INK, anchor="start"))
    f.append(text(tx + 35, ty + 434, "Змішування DShot з WS2812B або звичайним серво-PWM (50 Гц) на одному таймері апаратно неможливе.",
                  size=9.5, italic=True, color="#dc2626", anchor="start"))

    render(os.path.join(IMG, "timer-channel-sharing-conflict.svg"), W, H, *f)


if __name__ == "__main__":
    fig_mcu_resource_topology()
    fig_dma_stream_collision()
    fig_timer_channel_conflict()
    print("Всі 3 фігури згенеровано успішно.")
