# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. pin-multiplexing-conflict: Конфлікти матриці GPIO ────────────────────
def fig_pin_multiplexing():
    W, H = 880, 460
    p = []

    p.append(text(W / 2, 26, "Конфлікти альтернативних функцій виводів (GPIO Multiplexing)", size=15, bold=True, color=INK))

    p.append(text(130, 58, "Зовнішній інтерфейс", size=12, bold=True, color=MUTED))
    p.append(text(410, 58, "Вивід МК та альтернативна функція", size=12, bold=True, color=MUTED))
    p.append(text(720, 58, "Апаратний конфлікт та наслідок", size=12, bold=True, color=MUTED))

    pins_data = [
        ("Програматор SWD\n(ST-Link / J-Link)",
         "PA13 / PA14\nSWDIO / SWCLK (Debug)",
         "Якщо зайняти під LED або кнопку —\nблокується SWD-прошивка на стенді",
         POS, "#fdecea"),
        ("TFT-дисплей SPI\n+ Драйвер мотора",
         "PA5\nSPI1_SCK / TIM2_CH1 / ADC_IN5",
         "ШІМ-канал мотора апаратно вимикає\nшвидкісний апаратний SPI для дисплея",
         "#e67e22", "#fef9e7"),
        ("Шина сенсорів I2C\n(IMU, Барометр)",
         "PB6 / PB7\nI2C1_SCL_SDA / USART1_TX_RX",
         "Підключення I2C блокує апаратний UART,\nнеобхідний для налагоджувальної консолі",
         "#8a5fb0", "#f4ecf8"),
        ("Дільник вибору Boot\n+ Лінія скидання",
         "BOOT0 / NRST\nStrapping Pins / System Reset",
         "Недоторканні виводи: резистивні підтяжки\nвизначають старт ядра при подачі живлення",
         NEG, "#eaf0fd"),
    ]

    py = 110
    for ext_desc, pin_desc, conflict_desc, col, fill_col in pins_data:
        b_ext, w_ext, _ = textbox(130, py, ext_desc, size=10, bold=True,
                                  fill=fill_col, stroke=col, sw=1.6, pad=7)
        p.append(b_ext)

        b_pin, w_pin, _ = textbox(410, py, pin_desc, size=10, bold=True,
                                  fill="#ffffff", stroke=col, sw=1.8, pad=8)
        p.append(b_pin)

        p.append(arrow(130 + w_ext / 2 + 5, py, 410 - w_pin / 2 - 5, py, color=col, sw=1.6))

        b_conf, w_conf, _ = textbox(720, py, conflict_desc, size=9, bold=False,
                                    fill="#fdfefe", stroke=col, sw=1.4, pad=7)
        p.append(b_conf)

        p.append(arrow(410 + w_pin / 2 + 5, py, 720 - w_conf / 2 - 5, py, color=col, sw=1.6))

        py += 80

    p.append(text(W / 2, 442, "Виділення виводів під SWD, Boot та критичні шини фіксується до трасування ліній схеми",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "pin-multiplexing-conflict.svg"), W, H, *p,
           title="Конфлікти альтернативних функцій виводів")


# ── 2. six-budgets-interdependence: Взаємозв'язок 6 бюджетів ────────────────
def fig_six_budgets():
    W, H = 920, 520
    p = []

    p.append(text(W / 2, 26, "Взаємозв'язок шести інженерних бюджетів друкованої плати", size=15, bold=True, color=INK))

    cx, cy = W / 2, 255
    r_hex = 185

    nodes = [
        ("1. Бюджет пінів", "GPIO, шини I2C/SPI,\nSWD, Boot, таймери", POS, "#fdecea"),
        ("2. Струмовий бюджет", "Duty cycle, піки струму,\nємність батареї, I_Q", "#e67e22", "#fef9e7"),
        ("3. Тепловий бюджет", "T_j = T_a + P·θ_JA,\nрозсіювання, thermal vias", "#d35400", "#fbeee6"),
        ("4. Бюджет пам'яті", "Dual-bank OTA Flash,\nRAM задач RTOS, буфери", "#27ae60", "#eafaf1"),
        ("5. Габаритний бюджет", "Z-висота, товщина плати,\nроз'єми корпусу, 3D", NEG, "#eaf0fd"),
        ("6. Фінансовий бюджет", "BOM ціна, монтаж Top/Bot,\nтестовий стенд, MOQ", "#8a5fb0", "#f4ecf8"),
    ]

    coords = []
    for i in range(6):
        angle = math.radians(60 * i - 90)
        nx = cx + r_hex * math.cos(angle)
        ny = cy + r_hex * math.sin(angle)
        coords.append((nx, ny))

    for i in range(6):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % 6]
        p.append(line(x1, y1, x2, y2, color="#bdc3c7", sw=1.8, dash="4,4"))

    p.append(line(coords[0][0], coords[0][1], coords[3][0], coords[3][1], color="#d5dbdb", sw=1.5, dash="3,3"))
    p.append(line(coords[1][0], coords[1][1], coords[4][0], coords[4][1], color="#d5dbdb", sw=1.5, dash="3,3"))
    p.append(line(coords[2][0], coords[2][1], coords[5][0], coords[5][1], color="#d5dbdb", sw=1.5, dash="3,3"))

    p.append(circle(cx, cy, 42, fill="#ffffff", stroke=LINE, sw=1.8))
    p.append(text(cx, cy - 10, "Архітектурний", size=10, bold=True, color=INK))
    p.append(text(cx, cy + 6, "баланс", size=10, bold=True, color=INK))
    p.append(text(cx, cy + 22, "(Trade-off)", size=9, color=MUTED, italic=True))

    for (nx, ny), (title, desc, col, fill_col) in zip(coords, nodes):
        b, _, _ = textbox(nx, ny, f"{title}\n{desc}", size=9, bold=True,
                          fill=fill_col, stroke=col, sw=1.8, pad=7)
        p.append(b)

    p.append(text(W / 2, 495, "Зміна будь-якого одного бюджету автоматично зміщує межі та вартість інших п'яти",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "six-budgets-interdependence.svg"), W, H, *p,
           title="Взаємозв'язок шести інженерних бюджетів друкованої плати")


# ── 3. firmware-memory-map-ota: Карта Flash та RAM під OTA ──────────────────
def fig_memory_map():
    W, H = 920, 470
    p = []

    p.append(text(W / 2, 26, "Розподіл бюджету пам'яті: Dual-Bank Flash та динамічна RAM", size=15, bold=True, color=INK))

    # Ліва колонка: Flash (1024 KB)
    fx = 150
    p.append(text(fx, 62, "Flash-пам'ять (1024 КБ)", size=13, bold=True, color=INK))

    flash_blocks = [
        (80, 40, "Bootloader (32 КБ)", "Незмінний сектор запуску, перевірка RSA/SHA", "#eaf0fd", NEG),
        (130, 115, "Slot A / Active Firmware (448 КБ)", "Робоча прошивка (.text, .rodata, .data)", "#eafaf1", FIELD),
        (255, 115, "Slot B / OTA Staging (448 КБ)", "Буфер завантаження нової версії прошивки", "#fef9e7", "#e67e22"),
        (380, 45, "NVS / Storage (96 КБ)", "Калібрування, ключі, логи LittleFS", "#f4ecf8", "#8a5fb0"),
    ]

    for y, h, title, desc, fill_col, stroke_col in flash_blocks:
        p.append(rect(35, y, 230, h, fill=fill_col, stroke=stroke_col, sw=1.6, rx=5))
        p.append(text(150, y + 17, title, size=10, bold=True, color=INK))
        p.append(text(150, y + 33, desc, size=9, color=MUTED))

    # Стрілка вимоги OTA 50%
    p.append(line(275, 140, 295, 140, color="#e67e22", sw=1.6))
    p.append(line(295, 140, 295, 360, color="#e67e22", sw=1.6))
    p.append(arrow(295, 360, 275, 360, color="#e67e22", sw=1.6))
    b_ota_req, _, _ = textbox(380, 245, "Вимога Dual-Bank OTA:\nактивна прошивка ≤ 45% Flash", size=9, bold=True,
                              fill="#ffffff", stroke="#e67e22", sw=1.4, pad=6)
    p.append(b_ota_req)

    # Права колонка: RAM (256 KB)
    rx = 630
    p.append(text(rx, 62, "Оперативна пам'ять RAM (256 КБ)", size=13, bold=True, color=INK))

    ram_blocks = [
        (80, 50, "Статичні дані (48 КБ)", "Змінні .data, нульові .bss, глобальні таблиці", "#eaf0fd", NEG),
        (140, 70, "Буфери мережі / DMA (64 КБ)", "Wi-Fi / BLE пакети, дескриптори шин SPI/UART", "#fef9e7", "#e67e22"),
        (220, 85, "Стеки задач RTOS (80 КБ)", "Task stacks + запас на переривання ISR", "#fdecea", POS),
        (315, 65, "Куча (Heap) та запас (64 КБ)", "Динамічне виділення, захист від OOM", "#eafaf1", FIELD),
    ]

    for y, h, title, desc, fill_col, stroke_col in ram_blocks:
        p.append(rect(515, y, 230, h, fill=fill_col, stroke=stroke_col, sw=1.6, rx=5))
        p.append(text(630, y + 17, title, size=10, bold=True, color=INK))
        p.append(text(630, y + 33, desc, size=9, color=MUTED))

    # Стрілка ризику OOM
    p.append(line(755, 230, 775, 230, color=POS, sw=1.6))
    p.append(line(775, 230, 775, 370, color=POS, sw=1.6))
    p.append(arrow(775, 370, 755, 370, color=POS, sw=1.6))
    b_oom_warn, _, _ = textbox(845, 300, "Ризик Stack Overflow\nта вичерпання Heap", size=9, bold=True,
                               fill="#ffffff", stroke=POS, sw=1.4, pad=6)
    p.append(b_oom_warn)

    p.append(text(W / 2, 448, "Надійне бездротове оновлення (OTA) вимагає резервування щонайменше 50% доступного Flash",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "firmware-memory-map-ota.svg"), W, H, *p,
           title="Розподіл бюджету Flash та RAM")


# ── 4. thermal-via-conduction: Тепловідведення через плату ───────────────────
def fig_thermal_via():
    W, H = 860, 440
    p = []

    p.append(text(W / 2, 26, "Тепловий ланцюг: відведення потужності через полігони та thermal vias", size=15, bold=True, color=INK))

    sx, sy = 40, 65

    # 1. Корпус мікросхеми (IC)
    p.append(rect(sx + 70, sy + 15, 160, 45, fill="#34495e", stroke=LINE, sw=1.8, rx=4))
    p.append(text(sx + 150, sy + 32, "Корпус мікросхеми (IC)", size=10, bold=True, color="#ffffff"))
    # Кристал всередині
    p.append(rect(sx + 105, sy + 38, 90, 16, fill=POS, stroke=POS, sw=1, rx=2))
    p.append(text(sx + 150, sy + 50, "Кристал T_j", size=9, bold=True, color="#ffffff"))

    # 2. Exposed Pad (термопад)
    p.append(rect(sx + 90, sy + 62, 120, 10, fill="#e67e22", stroke="#d35400", sw=1.2, rx=1))
    p.append(text(sx + 150, sy + 70, "Exposed Pad", size=9, bold=True, color="#ffffff"))

    # 3. Шар припою
    p.append(rect(sx + 90, sy + 72, 120, 6, fill="#bdc3c7", stroke=LINE, sw=1, rx=0))

    # 4. Верхній шар міді (Top Copper)
    p.append(rect(sx + 20, sy + 78, 260, 10, fill="#d35400", stroke="#a04000", sw=1.2, rx=1))
    p.append(text(sx + 290, sy + 86, "Верхній мідний полігон (Top Cu)", size=9, color=INK, anchor="left"))

    # 5. Текстоліт FR4
    p.append(rect(sx + 20, sy + 88, 260, 85, fill="#d5f5e3", stroke="#27ae60", sw=1.5, rx=2))
    p.append(text(sx + 45, sy + 135, "Текстоліт FR4 (1.6 мм)", size=9, bold=True, color="#1e8449"))

    for vx in [sx + 110, sx + 150, sx + 190]:
        p.append(rect(vx - 6, sy + 88, 12, 85, fill="#d35400", stroke="#a04000", sw=1, rx=0))
        p.append(rect(vx - 2, sy + 88, 4, 85, fill="#bdc3c7", stroke="none", sw=0, rx=0))
    p.append(text(sx + 150, sy + 160, "Thermal Vias 3×3", size=9, bold=True, color="#ffffff"))

    # 6. Нижній шар міді (Bottom GND Plane)
    p.append(rect(sx + 20, sy + 173, 260, 10, fill="#d35400", stroke="#a04000", sw=1.2, rx=1))
    p.append(text(sx + 290, sy + 181, "Нижній суцільний GND-полігон", size=9, color=INK, anchor="left"))

    for hx in [sx + 50, sx + 100, sx + 150, sx + 200, sx + 250]:
        p.append(arrow(hx, sy + 185, hx, sy + 225, color="#e67e22", sw=1.8))
    p.append(text(sx + 150, sy + 242, "Конвективне розсіювання в повітря T_a", size=9, bold=True, color="#e67e22"))

    # Права частина: Еквівалентна схема
    ex = 540
    p.append(text(ex + 140, sy + 18, "Еквівалентна теплова схема", size=12, bold=True, color=INK))

    p.append(circle(ex + 140, sy + 45, 6, fill=POS, stroke=POS, sw=1.5))
    p.append(text(ex + 155, sy + 49, "Кристал T_j (Джерело тепла P_loss)", size=9, bold=True, color=POS, anchor="left"))

    p.append(line(ex + 140, sy + 51, ex + 140, sy + 75, color=LINE, sw=1.8))
    b_jc, _, _ = textbox(ex + 140, sy + 90, "θ_JC (Кристал → Корпус)", size=9, bold=True, fill="#fef9e7", stroke="#e67e22", pad=5)
    p.append(b_jc)

    p.append(line(ex + 140, sy + 105, ex + 140, sy + 125, color=LINE, sw=1.8))
    b_cs, _, _ = textbox(ex + 140, sy + 140, "θ_CS (Припій + Пад)", size=9, bold=True, fill="#f4f6f8", stroke=LINE, pad=5)
    p.append(b_cs)

    p.append(line(ex + 140, sy + 155, ex + 140, sy + 175, color=LINE, sw=1.8))
    b_vias, _, _ = textbox(ex + 140, sy + 195, "θ_vias || θ_FR4\n(Масив теплових отворів)", size=9, bold=True, fill="#eafaf1", stroke=FIELD, pad=6)
    p.append(b_vias)

    p.append(line(ex + 140, sy + 215, ex + 140, sy + 235, color=LINE, sw=1.8))
    b_sa, _, _ = textbox(ex + 140, sy + 250, "θ_SA (Полігон → Довкілля)", size=9, bold=True, fill="#eaf0fd", stroke=NEG, pad=5)
    p.append(b_sa)

    p.append(line(ex + 140, sy + 265, ex + 140, sy + 285, color=LINE, sw=1.8))
    p.append(circle(ex + 140, sy + 291, 6, fill=NEG, stroke=NEG, sw=1.5))
    p.append(text(ex + 155, sy + 295, "Довкілля T_a (Повітря всередині корпусу)", size=9, bold=True, color=NEG, anchor="left"))

    b_form, _, _ = textbox(ex + 140, sy + 345, "T_j = T_a + P_loss · (θ_JC + θ_CS + θ_board + θ_SA)",
                           size=10, bold=True, fill="#fdecea", stroke=POS, sw=1.5, pad=7)
    p.append(b_form)

    p.append(text(W / 2, 420, "Масив перехідних отворів передає тепло на нижній земляний полігон, зменшуючи результуючий θ_JA у 2–3 рази",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "thermal-via-conduction.svg"), W, H, *p,
           title="Тепловідведення через плату та перехідні отвори")


if __name__ == "__main__":
    fig_pin_multiplexing()
    fig_six_budgets()
    fig_memory_map()
    fig_thermal_via()
    print("All figures generated successfully.")
