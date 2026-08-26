# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_spaghetti_vs_fsm():
    W, H = 840, 480
    p = []

    # Тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 34, "Сон як локальний виклик функції проти сну як системного автомата", size=15, bold=True, color=INK))

    # ── Лівий блок: Наївний підхід (Локальний sleep) ──
    bx1, by1, bw1, bh1 = 25, 55, 380, 405
    p.append(rect(bx1, by1, bw1, bh1, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(bx1 + bw1 / 2, by1 + 22, "Помилка: delay / sleep у бізнес-функціях", size=12, bold=True, color=POS))
    p.append(text(bx1 + bw1 / 2, by1 + 38, "«Заснути прямо зараз звідси»", size=10, color=MUTED, italic=True))

    # Блоки коду та наслідки
    cy1 = by1 + 55
    steps_bad = [
        ("read_sensor()", "delay_ms(100)", "Блокує потік, ядро марно крутить цикли (15 мА)"),
        ("send_packet()", "enter_sleep()", "DMA ще передає по SPI! Шина обривається"),
        ("flash_write()", "WFI()", "Flash не записана, дані пошкоджено"),
        ("GPIO Pins", "Плаваючий стан", "Витоки струму 1-3 мА через КМОН-буфери"),
    ]
    for i, (fn, act, err) in enumerate(steps_bad):
        yy = cy1 + i * 82
        p.append(rect(bx1 + 15, yy, bw1 - 30, 72, fill="#ffffff", stroke=POS, sw=1, rx=4))
        p.append(text(bx1 + 25, yy + 18, f"{fn} → {act}", size=11, bold=True, color=POS, anchor="start"))
        p.append(text(bx1 + 25, yy + 36, "✖ Не узгоджено з іншими вузлами", size=10, color=POS, anchor="start"))
        p.append(text(bx1 + 25, yy + 54, f"⚠ {err}", size=9, color=MUTED, anchor="start"))

    # ── Правий блок: Системний Power Manager FSM ──
    bx2, by2, bw2, bh2 = 435, 55, 380, 405
    p.append(rect(bx2, by2, bw2, bh2, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 22, "Архітектура: Сон як глобальний стан системи", size=12, bold=True, color=FIELD))
    p.append(text(bx2 + bw2 / 2, by2 + 38, "«Сон — це стан спокою, коли всі узгодили»", size=10, color=MUTED, italic=True))

    cy2 = by2 + 55
    steps_good = [
        ("Модулі програми", "Power Locks (QoS)", "Драйвери тримають блокування лише під час активності"),
        ("Головний цикл", "Арбітраж глибини", "Power Manager обирає найглибший дозволений режим"),
        ("Підготовка сну", "Pre-sleep Callbacks", "DMA flush, паркування шин, GPIO в Analog High-Z"),
        ("Ядро зупинено", "Атомний вхід WFI", "Мікроспоживання 2 мкА, безпечне миттєве пробудження"),
    ]
    for i, (fn, act, ok) in enumerate(steps_good):
        yy = cy2 + i * 82
        p.append(rect(bx2 + 15, yy, bw2 - 30, 72, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
        p.append(text(bx2 + 25, yy + 18, f"{fn} → {act}", size=11, bold=True, color=FIELD, anchor="start"))
        p.append(text(bx2 + 25, yy + 36, "✔ Централізоване узгодження периферії", size=10, color=FIELD, anchor="start"))
        p.append(text(bx2 + 25, yy + 54, f"✓ {ok}", size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "spaghetti-sleep-vs-fsm.svg"), W, H, *p)


def fig_mcu_power_modes_hierarchy():
    W, H = 840, 460
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 34, "Градація режимів енергозбереження сучасного мікроконтролера", size=15, bold=True, color=INK))

    # Стовпчики / шари режимів
    modes = [
        ("ACTIVE (Run)", "10 - 25 мА", "0 мкс", "Ядро на повній частоті (HSE/PLL), усі шини активні, Flash читається", FIELD),
        ("SLEEP (WFI)", "1.5 - 4 мА", "0.5 - 2 мкс", "Ядро зупинено тактовим вентилем, периферія та RAM працюють, Flash активна", "#0284c7"),
        ("STOP / DEEPSLEEP", "2 - 15 мкА", "5 - 30 мкс", "PLL/HSE вимкнено, LP-регулятор, RAM збережено, вихід за EXTI / RTC / LPCOMP", "#7c3aed"),
        ("STANDBY / RTC", "0.8 - 2.5 мкА", "100 - 400 мкс", "Живлення ядра знято, RAM втрачено (лише Backup), пробудження = soft reset", "#d97706"),
        ("SHUTDOWN / OFF", "50 - 200 нА", "1 - 10 мс", "Усе знеструмлено крім пін-тригера / Tamper, повний холодний старт", POS),
    ]

    sy = 60
    rh = 68
    for i, (name, current, latency, desc, col) in enumerate(modes):
        yy = sy + i * (rh + 10)
        # Блок режиму
        p.append(rect(30, yy, W - 60, rh, fill="#f8fafc", stroke=col, sw=1.5, rx=6))

        # Назва
        p.append(rect(45, yy + 12, 180, 44, fill="#ffffff", stroke=col, sw=1, rx=4))
        p.append(text(135, yy + 38, name, size=11, bold=True, color=col))

        # Струм
        p.append(text(275, yy + 30, current, size=13, bold=True, color=col))
        p.append(text(275, yy + 48, "струм споживання", size=9, color=MUTED))

        # Час пробудження
        p.append(text(410, yy + 30, latency, size=12, bold=True, color=INK))
        p.append(text(410, yy + 48, "час пробудження", size=9, color=MUTED))

        # Опис та ресурси
        p.append(text(510, yy + 38, desc, size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "mcu-power-modes-hierarchy.svg"), W, H, *p)


def fig_sleep_wakeup_lifecycle():
    W, H = 840, 500
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 32, "Повний життєвий цикл входу в сон та відновлення системи", size=15, bold=True, color=INK))

    # Фаза 1: Перевірка та підготовка
    # Фаза 2: Атомний сон
    # Фаза 3: Пробудження та відновлення
    phases = [
        ("ФАЗА 1: Узгодження та паркування", 30, 55, 245, 420, FIELD, [
            ("1. Арбітраж блокувань", "Перевірка Power Locks усіх модулів"),
            ("2. Очікування черг", "DMA flush, завершення TX UART/SPI"),
            ("3. Відключення периферії", "Зупинка тактування шин APB/AHB"),
            ("4. Ізоляція GPIO", "Виводи у режим Analog High-Z"),
            ("5. Налаштування джерела", "Таймер RTC / Wakeup EXTI пін"),
        ]),
        ("ФАЗА 2: Атомний перехід у сон", 295, 55, 250, 420, "#7c3aed", [
            ("6. Заборона переривань", "__disable_irq() (встановлення PRIMASK)"),
            ("7. Перевірка прапорців", "Чи не виникла подія в мікросекунду засинання?"),
            ("8. Конфігурація ядра", "SCR.SLEEPDEEP = 1, DSB(), ISB()"),
            ("9. Інструкція зупинки", "Виконання __WFI() ядра Cortex-M"),
            ("10. РЕЖИМ СПОКОЮ", "Струм 2 мкА, ядро чекає переривання"),
        ]),
        ("ФАЗА 3: Пробудження та рестарт", 565, 55, 245, 420, "#0284c7", [
            ("11. Апаратне пробудження", "Сигнал EXTI / RTC піднімає ядро"),
            ("12. Дозвіл переривань", "__enable_irq(), вхід в ISR обробника"),
            ("13. Відновлення тактування", "Старт HSE/MSI, очікування PLL Lock"),
            ("14. Відновлення GPIO", "Повернення режимів AF/Push-Pull"),
            ("15. Запуск диспетчера", "Обробка черги подій у main loop"),
        ]),
    ]

    for title, px, py, pw, ph, col, items in phases:
        p.append(rect(px, py, pw, ph, fill="#f8fafc", stroke=col, sw=1.5, rx=6))
        p.append(text(px + pw / 2, py + 22, title, size=11, bold=True, color=col))

        iy = py + 42
        for idx, (step_t, step_d) in enumerate(items):
            box_y = iy + idx * 72
            p.append(rect(px + 10, box_y, pw - 20, 64, fill="#ffffff", stroke=col, sw=1, rx=4))
            p.append(text(px + 18, box_y + 20, step_t, size=10, bold=True, color=col, anchor="start"))
            p.append(text(px + 18, box_y + 42, step_d, size=9, color=INK, anchor="start"))

    # Стрілки між фазами
    p.append(arrow(275, 260, 295, 260, color=LINE, sw=2))
    p.append(arrow(545, 260, 565, 260, color=LINE, sw=2))

    render(os.path.join(OUT, "sleep-wakeup-lifecycle.svg"), W, H, *p)


def fig_sleep_race_condition():
    W, H = 820, 440
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 34, "Стан гонитви перед сном (Sleep Race Condition) та атомний захист", size=15, bold=True, color=INK))

    # Лівий блок: Небезпечний вхід
    bx1, by1, bw1, bh1 = 25, 60, 370, 360
    p.append(rect(bx1, by1, bw1, bh1, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(bx1 + bw1 / 2, by1 + 22, "Небезпечно: WFI з увімкненими перериваннями", size=11, bold=True, color=POS))

    lines_bad = [
        ("1. if (event_queue_is_empty())", "Черга порожня, вирішено заснути"),
        ("⚡ ПЕРЕРИВАННЯ ISR!", "Датчик дав сигнал: подія додана в чергу"),
        ("2. __WFI();", "Ядро засинає! Подія проігнорована"),
        ("⚠ НАСЛІДОК: Зависання", "Система спить до наступного таймера"),
    ]
    for i, (t, sub) in enumerate(lines_bad):
        yy = by1 + 50 + i * 74
        col = POS if i == 1 or i == 3 else INK
        p.append(rect(bx1 + 15, yy, bw1 - 30, 62, fill="#ffffff", stroke=col, sw=1, rx=4))
        p.append(text(bx1 + 25, yy + 22, t, size=11, bold=True, color=col, anchor="start"))
        p.append(text(bx1 + 25, yy + 44, sub, size=9, color=MUTED, anchor="start"))

    # Правий блок: Атомний вхід Cortex-M
    bx2, by2, bw2, bh2 = 425, 60, 370, 360
    p.append(rect(bx2, by2, bw2, bh2, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 22, "Безпечно: Cortex-M WFI при PRIMASK = 1", size=11, bold=True, color=FIELD))

    lines_good = [
        ("1. __disable_irq();", "PRIMASK = 1 (обробники не перебивають)"),
        ("2. if (event_queue_is_empty())", "Атомарна перевірка черги"),
        ("3. __WFI();", "Очікування: якщо прапорець виставлено — вихід!"),
        ("4. __enable_irq();", "Миттєве виконання ISR без втрати подій"),
    ]
    for i, (t, sub) in enumerate(lines_good):
        yy = by2 + 50 + i * 74
        p.append(rect(bx2 + 15, yy, bw2 - 30, 62, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
        p.append(text(bx2 + 25, yy + 22, t, size=11, bold=True, color=FIELD, anchor="start"))
        p.append(text(bx2 + 25, yy + 44, sub, size=9, color=MUTED, anchor="start"))

    render(os.path.join(OUT, "sleep-race-condition.svg"), W, H, *p)


if __name__ == "__main__":
    fig_spaghetti_vs_fsm()
    fig_mcu_power_modes_hierarchy()
    fig_sleep_wakeup_lifecycle()
    fig_sleep_race_condition()
    print("All figures generated successfully.")
