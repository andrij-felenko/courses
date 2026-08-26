# -*- coding: utf-8 -*-
"""Генератор векторних SVG-фігур для статті 'Автомат станів і черга подій у системі пристроїв'."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_state_explosion():
    """Фігура 1: Комбінаторний вибух прапорців проти детермінованого автомата."""
    W, H = 760, 360
    p = []

    # Заголовки двох колонок
    colx = [40, 410]
    p.append(text(colx[0] + 160, 38, "Хаос прапорців: 2ⁿ неявних станів", size=13, bold=True, color=POS))
    p.append(text(colx[1] + 160, 38, "Скінченний автомат: N явних станів", size=13, bold=True, color=FIELD))

    # Ліва колонка: розкидані прапорці та недосяжні/небезпечні комбінації
    flags = [
        "bool is_connected;",
        "bool is_measuring;",
        "bool is_low_power;",
        "bool has_fault;"
    ]
    for i, fl in enumerate(flags):
        p.append(fitbox(colx[0] + 20, 68 + i * 36, 170, 28, fl, size=11, fill="#fff6f5", stroke=POS, sw=1.3, bold=False))

    # Блок комбінаторного простору
    comb_box = (
        "16 комбінацій для 4 прапорців\n"
        "• is_connected && is_low_power?\n"
        "• is_measuring && has_fault?\n"
        "90% комбінацій — невалідні,\n"
        "але код мусить їх фільтрувати"
    )
    p.append(fitbox(colx[0] + 205, 68, 140, 136, comb_box, size=9.5, fill="#fdecea", stroke=POS, sw=1.4, bold=False))

    p.append(fitbox(colx[0] + 20, 220, 325, 80,
                    "if (is_conn && !is_lp && !fault) {\n"
                    "    if (measuring) { /* де перевірити тайм-аут? */ }\n"
                    "} else if (is_lp && fault) { /* конфлікт станів! */ }",
                    size=10, fill="#fff9f8", stroke=POS, sw=1.3, bold=False))

    # Розділювач
    p.append(line(385, 30, 385, 320, color=MUTED, sw=1.0, dash="4,4"))

    # Права колонка: чистий граф станів
    # Стани
    p.append(fitbox(colx[1] + 20, 75, 95, 42, "OFFLINE\n(сон)", size=11, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True))
    p.append(fitbox(colx[1] + 210, 75, 95, 42, "CONNECTING\n(модем)", size=11, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True))
    p.append(fitbox(colx[1] + 210, 185, 95, 42, "ONLINE\n(обмін)", size=11, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True))
    p.append(fitbox(colx[1] + 20, 185, 95, 42, "FAULT\n(аварія)", size=11, fill="#fdecea", stroke=POS, sw=1.6, bold=True))

    # Переходи зі стрілками
    # OFFLINE -> CONNECTING
    p.append(arrow(colx[1] + 115, 96, colx[1] + 208, 96, color=FIELD, sw=1.6))
    p.append(text(colx[1] + 162, 88, "EVT_WAKE", size=9, color=INK, bold=True))

    # CONNECTING -> ONLINE
    p.append(arrow(colx[1] + 257, 117, colx[1] + 257, 183, color=FIELD, sw=1.6))
    p.append(text(colx[1] + 288, 150, "EVT_LINK_UP", size=9, color=INK, bold=True, anchor="middle"))

    # ONLINE -> OFFLINE
    p.append(arrow(colx[1] + 210, 195, colx[1] + 115, 105, color=MUTED, sw=1.4))
    p.append(text(colx[1] + 155, 142, "EVT_SLEEP", size=9, color=MUTED, bold=True))

    # Any -> FAULT
    p.append(arrow(colx[1] + 210, 206, colx[1] + 115, 206, color=POS, sw=1.5))
    p.append(text(colx[1] + 162, 220, "EVT_ERROR", size=9, color=POS, bold=True))

    p.append(fitbox(colx[1] + 20, 255, 285, 45,
                    "enum state_t { OFFLINE, CONNECTING, ONLINE, FAULT };\n"
                    "Рівно 1 активний стан. Неможливі поєднання виключені.",
                    size=10, fill="#f4f6f8", stroke=FIELD, sw=1.2, bold=False))

    p.append(text(W / 2, H - 15,
                  "Порівняння: прапорці плодять комбінаторний вибух, автомат фіксує єдиний активний стан",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "state-explosion.svg"), W, H, *p,
           title="Комбінаторний вибух прапорців проти детермінованого автомата")


def fig_hsm_lca_transition():
    """Фігура 2: Ієрархія станів HSM та послідовність транзакційного переходу через LCA."""
    W, H = 760, 420
    p = []

    # Загальний суперстан Operational
    p.append(rect(40, 35, 680, 260, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    p.append(text(60, 58, "Суперстан: Operational (LCA — спільний предок)", size=12, bold=True, color=INK, anchor="start"))

    # Підстан S1 (Source Composite State)
    p.append(rect(65, 80, 290, 195, fill="#edf2f7", stroke="#4a5568", sw=1.3, rx=6))
    p.append(text(80, 102, "Джерельний суперстан: Active (S1)", size=11, bold=True, color=INK, anchor="start"))

    # Листовий стан S11 (Current Active Leaf)
    p.append(fitbox(90, 125, 240, 60, "Листовий підстан: Measuring (S11)\n[Поточний активний стан]\nexit: stop_adc();",
                    size=10, fill="#fdecea", stroke=POS, sw=1.5, bold=False))
    p.append(text(210, 235, "Active exit: disable_sensor_power();", size=9.5, color=POS, bold=True))

    # Підстан S2 (Target Composite State)
    p.append(rect(405, 80, 290, 195, fill="#edf2f7", stroke="#4a5568", sw=1.3, rx=6))
    p.append(text(420, 102, "Цільовий суперстан: Standby (S2)", size=11, bold=True, color=INK, anchor="start"))
    p.append(text(550, 125, "Standby entry: configure_lp_timer();", size=9.5, color=FIELD, bold=True))

    # Листовий стан S21 (Target Active Leaf)
    p.append(fitbox(430, 145, 240, 60, "Листовий підстан: LowPowerSleep (S21)\n[Цільовий активний стан]\nentry: enter_wfi_mode();",
                    size=10, fill="#eafaf0", stroke=FIELD, sw=1.5, bold=False))
    p.append(text(550, 240, "Initial Transition -> S21", size=9.5, color=FIELD, italic=True))

    # Стрілка переходу від S11 до S21 через LCA
    # 1. Вихід з S11
    p.append(arrow(210, 125, 210, 95, color=POS, sw=1.6))
    p.append(text(145, 110, "1. Exit S11", size=9.5, color=POS, bold=True))

    # 2. Вихід з S1
    p.append(arrow(355, 130, 395, 130, color=POS, sw=1.6))
    p.append(text(375, 120, "2. Exit S1", size=9.5, color=POS, bold=True))

    # 3. Дія переходу на рівні LCA
    p.append(arrow(355, 65, 405, 65, color=LINE, sw=1.8))
    p.append(text(380, 55, "3. Transition Action: log_event()", size=9.5, color=LINE, bold=True))

    # 4. Вхід у S2
    p.append(arrow(405, 100, 425, 100, color=FIELD, sw=1.6))
    p.append(text(375, 90, "4. Entry S2", size=9.5, color=FIELD, bold=True))

    # 5. Вхід у S21
    p.append(arrow(550, 130, 550, 143, color=FIELD, sw=1.6))
    p.append(text(595, 138, "5. Entry S21", size=9.5, color=FIELD, bold=True))

    # Блок пояснення алгоритму кроків
    p.append(fitbox(40, 310, 680, 75,
                    "Порядок транзакції LCA: (1) Exit із Measuring → (2) Exit із Active → (3) Дія переходу →\n"
                    "(4) Entry в Standby → (5) Entry в LowPowerSleep → (6) Виконання Initial переходу вкладеного стану.\n"
                    "Гарантія: жоден стан не лишається у напіввідкритому чи недефінійованому стані.",
                    size=10.5, fill="#f4f6f8", stroke=LINE, sw=1.2, bold=False))

    p.append(text(W / 2, H - 12,
                  "Транзакційний перехід у HSM: порядок виклику дій виходу вгору до LCA та дій входу вниз до цілі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "hsm-lca-transition.svg"), W, H, *p,
           title="Транзакційний перехід у HSM через найменшого спільного предка (LCA)")


def fig_rtc_dispatch_loop():
    """Фігура 3: Run-to-Completion диспетчеризація подій та кільцева черга."""
    W, H = 760, 380
    p = []

    # Ліва частина: Джерела подій (ISR / Tasks)
    p.append(text(120, 35, "Джерела подій (Producer)", size=12, bold=True, color=INK))
    sources = [
        ("UART ISR (байтові кадри)", POS),
        ("GPIO ISR (кнопка / датчик)", POS),
        ("Timer ISR (системний тік)", POS),
        ("Background Task (фонові дані)", FIELD)
    ]
    for i, (src, col) in enumerate(sources):
        y = 60 + i * 45
        p.append(fitbox(40, y, 160, 34, src, size=9.5, fill="#f8fafc", stroke=col, sw=1.3, bold=False))
        p.append(arrow(200, y + 17, 245, 145, color=col, sw=1.3))

    # Середня частина: Статична кільцева черга (Lock-free / Critical Section)
    p.append(rect(250, 45, 230, 200, fill="#edf2f7", stroke="#2d3748", sw=1.5, rx=8))
    p.append(text(365, 68, "Статична черга подій (FIFO)", size=11, bold=True, color=INK))

    # Комірки буфера
    slots = ["evt_0 (WAKE)", "evt_1 (RX_DATA)", "evt_2 (TIMEOUT)", "...", "evt_N-1 (порожньо)"]
    for i, sl in enumerate(slots):
        fill_col = "#e2e8f0" if i < 3 else "#ffffff"
        p.append(fitbox(265, 85 + i * 28, 200, 24, sl, size=9, fill=fill_col, stroke="#718096", sw=1.0))

    p.append(text(365, 232, "head: 0x03  |  tail: 0x00  (RAM: BSS)", size=9.5, color=MUTED, bold=True))

    # Стрілка з черги в диспетчер RTC
    p.append(arrow(480, 145, 525, 145, color=FIELD, sw=1.8))
    p.append(text(502, 135, "pop()", size=9.5, color=FIELD, bold=True))

    # Права частина: RTC Диспетчер та Активний автомат
    p.append(rect(530, 45, 190, 200, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(625, 68, "RTC Диспетчер (Consumer)", size=11, bold=True, color=FIELD))

    p.append(fitbox(545, 85, 160, 40, "1. Вилучення події\ne = queue_pop();", size=9.5, fill="#ffffff", stroke=FIELD, sw=1.2))
    p.append(fitbox(545, 135, 160, 50, "2. Повна обробка (RTC)\nhsm_dispatch(&fsm, &e);\n(Дії виходу/переходу/входу)", size=9.5, fill="#eafaf0", stroke=FIELD, sw=1.5, bold=True))
    p.append(fitbox(545, 195, 160, 40, "3. Фіксація нового стану\nfsm.state = target_state;", size=9.5, fill="#ffffff", stroke=FIELD, sw=1.2))

    # Пояснення внизу
    p.append(fitbox(40, 265, 680, 75,
                    "Семантика Run-to-Completion (RTC):\n"
                    "• Кожна подія обробляється атомарно до повного переходу в новий стабільний стан.\n"
                    "• Нові події з переривань безпечно накопичуються в черзі й не порушують поточний крок.\n"
                    "• Нуль динамічної пам'яті (malloc), нуль гонок пам'яті, строгий детермінізм.",
                    size=10.5, fill="#f4f6f8", stroke=LINE, sw=1.2, bold=False))

    p.append(text(W / 2, H - 12,
                  "Архітектура Run-to-Completion: асинхронні переривання наповнюють кільцеву чергу, диспетчер обробляє квантами",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "rtc-dispatch-loop.svg"), W, H, *p,
           title="Run-to-Completion диспетчеризація подій через статичну кільцеву чергу")


def fig_system_statechart():
    """Фігура 4: Комплексна діаграма ієрархічного автомата польового IoT-пристрою."""
    W, H = 760, 440
    p = []

    # Зовнішній суперстан RootState
    p.append(rect(30, 30, 700, 360, fill="#f8fafc", stroke=LINE, sw=1.6, rx=8))
    p.append(text(50, 52, "RootState (Глобальний суперстан: обробка EVT_RESET, EVT_HARD_FAULT, EVT_LOW_BATTERY)", size=11, bold=True, color=INK, anchor="start"))

    # Суперстан Operational
    p.append(rect(50, 70, 440, 305, fill="#edf2f7", stroke="#4a5568", sw=1.4, rx=6))
    p.append(text(70, 92, "Operational (Суперстан штатної роботи)", size=11, bold=True, color=INK, anchor="start"))

    # Підстан Idle
    p.append(fitbox(70, 115, 170, 60, "Idle (Очікування)\nentry: start_watchdog();\nexit: stop_watchdog();", size=9.5, fill="#ffffff", stroke=LINE, sw=1.2))

    # Підстан Sampling
    p.append(fitbox(280, 115, 190, 60, "Sampling (Збір даних)\nentry: dma_adc_start();\nexit: dma_adc_stop();", size=9.5, fill="#ffffff", stroke=LINE, sw=1.2))

    # Суперстан Communicating всередині Operational
    p.append(rect(70, 195, 400, 165, fill="#ffffff", stroke="#718096", sw=1.2, rx=6))
    p.append(text(85, 215, "Communicating (Суперстан зв'язку: timeout 10s)", size=10, bold=True, color=INK, anchor="start"))

    # Листові підстани зв'язку
    p.append(fitbox(85, 235, 170, 50, "ModemConnecting\nentry: modem_power_on();", size=9, fill="#eafaf0", stroke=FIELD, sw=1.2))
    p.append(fitbox(280, 235, 175, 50, "DataPublishing\nentry: mqtt_publish();", size=9, fill="#eafaf0", stroke=FIELD, sw=1.2))
    p.append(fitbox(180, 298, 180, 48, "AckWaiting\nentry: start_ack_timer();", size=9, fill="#eafaf0", stroke=FIELD, sw=1.2))

    # Стрілки всередині Communicating
    p.append(arrow(255, 260, 278, 260, color=FIELD, sw=1.3))
    p.append(arrow(365, 285, 270, 298, color=FIELD, sw=1.3))

    # Стрілки між підстанами Operational
    p.append(arrow(240, 145, 278, 145, color=LINE, sw=1.4))
    p.append(text(260, 136, "TICK", size=9.5, color=MUTED, bold=True))

    p.append(arrow(375, 175, 375, 193, color=LINE, sw=1.4))
    p.append(text(398, 185, "DATA_READY", size=9.5, color=MUTED, bold=True))

    # Стан Fault (Аварія / Безпечний режим)
    p.append(rect(515, 70, 195, 305, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(612, 92, "FaultState (Аварія)", size=11, bold=True, color=POS))
    p.append(fitbox(530, 115, 165, 70, "SafeMode\nentry: disable_power_relays();\nentry: write_nvs_crashlog();\nentry: blink_sos_led();", size=9.5, fill="#ffffff", stroke=POS, sw=1.2))
    p.append(fitbox(530, 210, 165, 60, "RebootCountdown\nentry: arm_watchdog(3s);\nentry: flush_uart();", size=9.5, fill="#ffffff", stroke=POS, sw=1.2))

    # Стрілка переходу з будь-якого підстану Operational в FaultState
    p.append(arrow(490, 150, 513, 150, color=POS, sw=1.8))
    p.append(text(502, 138, "EVT_ERROR", size=9, color=POS, bold=True))

    p.append(text(W / 2, H - 14,
                  "Ієрархічний автомат польового пристрою: суперстан Operational об'єднує підстани вимірювання та передачі",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "system-statechart.svg"), W, H, *p,
           title="Ієрархічний автомат польового пристрою")


if __name__ == "__main__":
    fig_state_explosion()
    fig_hsm_lca_transition()
    fig_rtc_dispatch_loop()
    fig_system_statechart()
    print("All figures generated successfully.")
