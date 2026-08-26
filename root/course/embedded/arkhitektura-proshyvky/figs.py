# -*- coding: utf-8 -*-
"""Фігури для статті arkhitektura-proshyvky.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_firmware_layers_stack():
    """Чотирирівнева архітектура прошивки: HAL, BSP, Services, Application."""
    W, H = 840, 520
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Заголовок
    p.append(text(W / 2, 28, "Шарувата архітектура вбудованого програмного забезпечення", size=16, color=INK, bold=True))

    layers = [
        ("Рівень застосунку (Application Layer)", 
         "Бізнес-логіка, кінцеві автомати (FSM), політики збору телеметрії, контури керування",
         "#e8f4fd", "#1d6fa5", 60),
        ("Рівень служб і проміжного ПЗ (Services / Middleware)",
         "Диспетчер подій, кільцеві буфери, файлова система (LittleFS), протоколи зв'язку, логи",
         "#f3e8fd", "#7e22ce", 160),
        ("Рівень плати й драйверів пристроїв (BSP / Device Drivers)",
         "Драйвери зовнішніх мікросхем: сенсори (BME280), флеш-пам'ять (W25Q), дисплеї, кнопки",
         "#e8fdf5", "#047857", 260),
        ("Рівень апаратної абстракції чипа (HAL / Low-Level LL)",
         "Контролери периферії MCU: GPIO, I2C, SPI, UART, DMA, таймери, переривання NVIC",
         "#fef3c7", "#b45309", 360),
    ]

    for title, desc, fcol, scol, y in layers:
        p.append(rect(60, y, 720, 76, fill=fcol, stroke=scol, sw=1.8, rx=6))
        p.append(text(420, y + 26, title, size=14, color=scol, bold=True))
        p.append(text(420, y + 54, desc, size=11, color=INK))

    # Стрілки залежностей зліва (Downwards)
    p.append(arrow(35, 95, 35, 400, color=POS, sw=2.0))
    p.append(text(22, 250, "Прямі виклики вниз", size=11, color=POS, bold=True, anchor="middle"))

    # Стрілки подій справа (Upwards - Callbacks / Events)
    p.append(arrow(805, 400, 805, 95, color=FIELD, sw=2.0))
    p.append(text(818, 250, "Події та черги вгору", size=11, color=FIELD, bold=True, anchor="middle"))

    # Апаратний фундамент внизу
    p.append(rect(60, 450, 720, 48, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=6))
    p.append(text(420, 480, "Апаратне забезпечення: Кремній MCU (Cortex-M) + Зовнішні сенсори та шини", size=13, color="#334155", bold=True))

    render(os.path.join(OUT, "firmware-layers-stack.svg"), W, H, *p)


def fig_monolith_vs_modular_coupling():
    """Порівняння монолітного спагеті-коду та модульної шаруватої структури."""
    W, H = 840, 460
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 26, "Зв'язність компонентів: моноліт проти модульної архітектури", size=16, color=INK, bold=True))

    # Ліва колонка — Спагеті-моноліт
    p.append(rect(30, 45, 370, 395, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(215, 72, "Монолітне спагеті (Тісна зв'язність)", size=14, color=POS, bold=True))

    # Центральний вузол main.c
    p.append(rect(140, 100, 150, 42, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(215, 126, "main.c (2500 рядків)", size=12, color=POS, bold=True))

    bad_nodes = [
        ("Регістри I2C/SPI", 50, 190),
        ("Обробка LoRa", 250, 190),
        ("Логіка FSM", 50, 280),
        ("Сенсор BME280", 250, 280),
        ("Прямий доступ GPIO", 140, 355),
    ]

    for name, nx, ny in bad_nodes:
        p.append(rect(nx, ny, 130, 36, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
        p.append(text(nx + 65, ny + 23, name, size=11, color=INK))

    # Хаотичні лінії зв'язку
    p.append(line(215, 142, 115, 190, color=POS, sw=1.2))
    p.append(line(215, 142, 315, 190, color=POS, sw=1.2))
    p.append(line(115, 226, 115, 280, color=POS, sw=1.2))
    p.append(line(315, 226, 315, 280, color=POS, sw=1.2))
    p.append(line(115, 316, 205, 355, color=POS, sw=1.2))
    p.append(line(315, 316, 205, 355, color=POS, sw=1.2))
    p.append(line(180, 208, 250, 298, color=POS, sw=1.0, dash="3,3"))
    p.append(line(180, 298, 250, 208, color=POS, sw=1.0, dash="3,3"))

    p.append(rect(45, 400, 340, 30, fill="#ffffff", stroke="none"))
    p.append(text(215, 420, "Заміна чипа ламає 100% коду; тест на ПК неможливий", size=10, color=POS, bold=True))

    # Права колонка — Модульна архітектура
    p.append(rect(440, 45, 370, 395, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(625, 72, "Модульна шарувата архітектура", size=14, color=FIELD, bold=True))

    good_layers = [
        ("App: Telemetry FSM", 475, 105, "#dcfce7", FIELD),
        ("Service: Event Queue & Bus", 475, 175, "#e0e7ff", "#4338ca"),
        ("BSP: BME280 Driver (Interface)", 475, 245, "#fef3c7", "#b45309"),
        ("HAL: I2C Bus Abstraction", 475, 315, "#fee2e2", "#b91c1c"),
    ]

    for title, gx, gy, gfill, gstroke in good_layers:
        p.append(rect(gx, gy, 300, 40, fill=gfill, stroke=gstroke, sw=1.5, rx=6))
        p.append(text(gx + 150, gy + 25, title, size=12, color=INK, bold=True))

    p.append(arrow(625, 145, 625, 175, color=FIELD, sw=1.8))
    p.append(arrow(625, 215, 625, 245, color=FIELD, sw=1.8))
    p.append(arrow(625, 285, 625, 315, color=FIELD, sw=1.8))

    p.append(rect(455, 370, 340, 58, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(625, 390, "Чіткі інтерфейси, слабка зв'язність", size=11, color=FIELD, bold=True))
    p.append(text(625, 412, "100% бізнес-логіки тестується на ПК з Mock HAL", size=10, color=MUTED))

    render(os.path.join(OUT, "monolith-vs-modular-coupling.svg"), W, H, *p)


def fig_event_driven_pipeline():
    """Конвеєр обробки подій між апаратними перериваннями та модулями."""
    W, H = 840, 440
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    p.append(text(W / 2, 28, "Подійно-орієнтований потік даних: від переривання до FSM", size=16, color=INK, bold=True))

    # Блок 1: Джерела подій (ISR / Тіки)
    p.append(rect(30, 60, 200, 330, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=8))
    p.append(text(130, 88, "Джерела подій", size=14, color="#b45309", bold=True))

    sources = [
        ("UART DMA RX ISR", 120),
        ("Timer SysTick (10 мс)", 185),
        ("GPIO EXTI (Кнопка)", 250),
        ("I2C Transfer Done", 315),
    ]
    for sname, sy in sources:
        p.append(rect(45, sy, 170, 42, fill="#ffffff", stroke="#d97706", sw=1.2, rx=4))
        p.append(text(130, sy + 26, sname, size=11, color=INK, bold=True))

    # Стрілка 1 -> 2
    p.append(arrow(230, 225, 290, 225, color=LINE, sw=2.0))
    p.append(text(260, 210, "post()", size=11, color=POS, bold=True))

    # Блок 2: Черга подій (Services)
    p.append(rect(290, 60, 230, 330, fill="#e0e7ff", stroke="#4338ca", sw=1.5, rx=8))
    p.append(text(405, 88, "Кільцева черга подій", size=14, color="#4338ca", bold=True))
    p.append(text(405, 108, "Критична секція / Lock-free", size=10, color=MUTED))

    # Елементи черги
    q_slots = [
        ("EVT_BTN_PRESSED", "#fee2e2", POS),
        ("EVT_TIMER_10MS", "#fef3c7", "#b45309"),
        ("EVT_TELEMETRY_READY", "#dcfce7", FIELD),
        ("--- Вільний слот ---", "#f1f5f9", MUTED),
    ]
    qy = 135
    for qtitle, qfill, qcol in q_slots:
        p.append(rect(305, qy, 200, 38, fill=qfill, stroke="#4338ca", sw=1.0, rx=4))
        p.append(text(405, qy + 24, qtitle, size=11, color=qcol, bold=True))
        qy += 50

    p.append(rect(305, 340, 200, 36, fill="#ffffff", stroke="#4338ca", sw=1.0, rx=4))
    p.append(text(405, 362, "Queue: 3/16 подій", size=11, color="#4338ca", bold=True))

    # Стрілка 2 -> 3
    p.append(arrow(520, 225, 580, 225, color=LINE, sw=2.0))
    p.append(text(550, 210, "dispatch()", size=11, color=FIELD, bold=True))

    # Блок 3: Обробники застосунку
    p.append(rect(580, 60, 230, 330, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(695, 88, "Диспетчер та FSM", size=14, color=FIELD, bold=True))

    handlers = [
        ("Power Management FSM", 120),
        ("Telemetry Scheduler", 185),
        ("Network Protocol Engine", 250),
        ("UI / LED Indicator", 315),
    ]
    for hname, hy in handlers:
        p.append(rect(595, hy, 200, 42, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
        p.append(text(695, hy + 26, hname, size=11, color=INK, bold=True))

    p.append(rect(30, 400, 780, 30, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(420, 420, "Генератори подій не знають про підписників: повна розв'язка за часом і контекстом виконання", size=11, color=INK))

    render(os.path.join(OUT, "event-driven-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_firmware_layers_stack()
    fig_monolith_vs_modular_coupling()
    fig_event_driven_pipeline()
    print("All figures generated successfully.")
