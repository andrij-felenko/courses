# -*- coding: utf-8 -*-
"""Фігури для статті avtomat-staniv-i-cherha-podii-u-proshyvtsi.
Згенеровані через svgkit зі scripts/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_spaghetti_vs_fsm():
    """Порівняння лінійного блокуючого коду та подійно-орієнтованого автомата."""
    W, H = 820, 420
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Ліва колонка — Блокуючий лінійний цикл
    p.append(rect(20, 20, 370, 380, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(205, 50, "Лінійний блокуючий код (delay)", size=15, color=POS, bold=True))

    steps_bad = [
        ("1. digitalRead(BTN) == HIGH", "#ffffff", INK),
        ("2. delay(5000)  [чекаємо контактор]", "#fee2e2", POS),
        ("3. uart_read_blocking(&resp)", "#fee2e2", POS),
        ("4. delay(2000)  [стабілізація струму]", "#fee2e2", POS),
        ("5. update_lcd_blocking()", "#ffffff", INK),
    ]
    y = 80
    for title, fcol, tcol in steps_bad:
        p.append(rect(40, y, 330, 38, fill=fcol, stroke=POS if fcol != "#ffffff" else MUTED, sw=1.2, rx=4))
        p.append(text(205, y + 24, title, size=12, color=tcol, bold=(fcol != "#ffffff")))
        if y < 240:
            p.append(arrow(205, y + 38, 205, y + 48, color=POS, sw=1.2))
        y += 50

    p.append(rect(40, 335, 330, 50, fill="#ffffff", stroke=POS, sw=1.0, rx=4))
    p.append(text(205, 355, "Зупинка процесора: 7000+ мс!", size=12, color=POS, bold=True))
    p.append(text(205, 372, "Аварія / кнопка Стоп ігноруються", size=11, color=MUTED))

    # Права колонка — Подійно-орієнтований автомат
    p.append(rect(430, 20, 370, 380, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(615, 50, "Подійно-орієнтований FSM", size=15, color=FIELD, bold=True))

    steps_good = [
        ("1. event = queue_pop()", "#ffffff", INK),
        ("2. fsm_dispatch(&fsm, event)", "#dcfce7", FIELD),
        ("3. Виконання дії стану (< 50 мкс)", "#dcfce7", FIELD),
        ("4. Перехід: current_state = next", "#ffffff", INK),
        ("5. Якщо черга пуста: __WFI() [сон]", "#ffffff", MUTED),
    ]
    y = 80
    for title, fcol, tcol in steps_good:
        p.append(rect(450, y, 330, 38, fill=fcol, stroke=FIELD if fcol != "#ffffff" else MUTED, sw=1.2, rx=4))
        p.append(text(615, y + 24, title, size=12, color=tcol, bold=(fcol != "#ffffff")))
        if y < 240:
            p.append(arrow(615, y + 38, 615, y + 48, color=FIELD, sw=1.2))
        y += 50

    p.append(rect(450, 335, 330, 50, fill="#ffffff", stroke=FIELD, sw=1.0, rx=4))
    p.append(text(615, 355, "Час реакції циклу: < 100 мкс", size=12, color=FIELD, bold=True))
    p.append(text(615, 372, "Миттєва обробка аварійних подій", size=11, color=FIELD))

    render(os.path.join(OUT, "spaghetti-vs-fsm.svg"), W, H, *p)


def fig_fsm_core_loop():
    """Анатомія кроку автомата: стан, подія, вхід/вихід, перехід."""
    W, H = 780, 320
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Стан A
    p.append(rect(30, 110, 160, 100, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(110, 140, "Стан A", size=15, color=NEG, bold=True))
    p.append(line(30, 155, 190, 155, color=NEG, sw=1.0))
    p.append(text(110, 175, "entry / on_enter()", size=11, color=MUTED))
    p.append(text(110, 195, "exit  / on_exit()", size=11, color=MUTED))

    # Стан B
    p.append(rect(590, 110, 160, 100, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(670, 140, "Стан B", size=15, color=NEG, bold=True))
    p.append(line(590, 155, 750, 155, color=NEG, sw=1.0))
    p.append(text(670, 175, "entry / on_enter()", size=11, color=MUTED))
    p.append(text(670, 195, "exit  / on_exit()", size=11, color=MUTED))

    # Перехідна стрілка з подією
    p.append(arrow(190, 160, 590, 160, color=INK, sw=2.0))

    # Картка переходу над стрілкою
    p.append(rect(240, 50, 300, 80, fill="#fef3c7", stroke="#d97706", sw=1.5, rx=6))
    p.append(text(390, 75, "Подія: EVT_START [ guard ]", size=13, color="#d97706", bold=True))
    p.append(text(390, 95, "Дія переходу: do_transition_action()", size=11, color=INK))
    p.append(text(390, 115, "Порядок: Exit(A) -> Action -> Entry(B)", size=11, color=MUTED))

    # Послідовність виконання внизу
    p.append(rect(140, 245, 500, 50, fill="#f8fafc", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(390, 267, "1. A.exit()  →  2. transition_action()  →  3. B.entry()", size=12, color=INK, bold=True))
    p.append(text(390, 285, "Гарантія інваріантів: ресурси A звільнено до входу в B", size=11, color=FIELD))

    render(os.path.join(OUT, "fsm-core-loop.svg"), W, H, *p)


def fig_event_queue_architecture():
    """Архітектура розв'язки переривань та диспетчера подій."""
    W, H = 840, 360
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Зона ISR зліва
    p.append(rect(20, 20, 210, 320, fill="#fdf4ff", stroke="#c026d3", sw=1.5, rx=8))
    p.append(text(125, 45, "Джерела переривань (ISR)", size=13, color="#c026d3", bold=True))

    isrs = [
        ("UART RX ISR", "байт команди"),
        ("GPIO EXTI ISR", "натиск кнопки"),
        ("SysTick Timer", "таймаут 100 мс"),
        ("ADC DMA ISR", "поріг струму"),
    ]
    y = 65
    for title, desc in isrs:
        p.append(rect(35, y, 180, 52, fill="#ffffff", stroke="#c026d3", sw=1.0, rx=4))
        p.append(text(125, y + 22, title, size=12, color=INK, bold=True))
        p.append(text(125, y + 40, desc, size=10, color=MUTED))
        p.append(arrow(215, y + 26, 290, 180, color="#c026d3", sw=1.2))
        y += 64

    # Центральний вузол: Кільцева черга подій
    p.append(rect(300, 70, 220, 220, fill="#eff6ff", stroke=NEG, sw=2.0, rx=8))
    p.append(text(410, 100, "Кільцева черга подій", size=14, color=NEG, bold=True))
    p.append(text(410, 120, "(Event Ring Buffer)", size=11, color=MUTED))

    slots = ["EVT_BTN_DOWN", "EVT_TIMEOUT", "EVT_RX_FRAME", "[ порожньо ]", "[ порожньо ]"]
    sy = 135
    for s in slots:
        is_empty = "[ порожньо ]" in s
        p.append(rect(320, sy, 180, 24, fill="#ffffff" if is_empty else "#dbeafe", stroke=NEG if not is_empty else MUTED, sw=1.0, rx=3))
        p.append(text(410, sy + 16, s, size=10, color=INK if not is_empty else MUTED, bold=(not is_empty)))
        sy += 28

    p.append(text(410, 280, "Атомарний push / pop", size=10, color=FIELD, bold=True))

    # Стрілка з черги в головний цикл
    p.append(arrow(520, 180, 590, 180, color=NEG, sw=2.0))
    p.append(text(555, 170, "pop()", size=11, color=NEG, bold=True))

    # Зона Головного циклу справа
    p.append(rect(600, 20, 220, 320, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(710, 45, "Головний цикл (Super-loop)", size=13, color=FIELD, bold=True))

    p.append(rect(615, 75, 190, 80, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(710, 100, "Диспетчер подій", size=12, color=INK, bold=True))
    p.append(text(710, 120, "while(queue_pop(&e))", size=11, color=MUTED))
    p.append(text(710, 140, "fsm_dispatch(&fsm, &e);", size=11, color=FIELD, bold=True))

    p.append(arrow(710, 155, 710, 185, color=FIELD, sw=1.5))

    p.append(rect(615, 185, 190, 75, fill="#ffffff", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(710, 210, "Автомат станів (FSM)", size=12, color=INK, bold=True))
    p.append(text(710, 230, "Поточний: CHARGING", size=11, color=NEG, bold=True))
    p.append(text(710, 248, "Оновлення виходів / реле", size=10, color=MUTED))

    p.append(rect(615, 275, 190, 50, fill="#ffffff", stroke=MUTED, sw=1.0, rx=4))
    p.append(text(710, 295, "Якщо черга порожня:", size=10, color=MUTED))
    p.append(text(710, 312, "__WFI()  // Сон до ISR", size=11, color=FIELD, bold=True))

    render(os.path.join(OUT, "event-queue-architecture.svg"), W, H, *p)


def fig_hierarchical_states_reduction():
    """Зменшення кількості переходів у HSM (Statecharts) завдяки суперстанам."""
    W, H = 820, 340
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # Зліва: Плоский FSM (Комбінаторний вибух)
    p.append(rect(20, 20, 370, 300, fill="#fff7ed", stroke="#ea580c", sw=1.5, rx=8))
    p.append(text(205, 45, "Плоский FSM: дублювання переходів", size=13, color="#ea580c", bold=True))

    states = [
        (40, 80, "Init"),
        (160, 80, "Auth"),
        (280, 80, "Precharge"),
        (100, 160, "FastCharge"),
        (220, 160, "Balancing"),
    ]
    for sx, sy, sname in states:
        p.append(rect(sx, sy, 80, 40, fill="#ffffff", stroke=INK, sw=1.2, rx=4))
        p.append(text(sx + 40, sy + 25, sname, size=11, color=INK, bold=True))
        # Стрілки до Fault
        p.append(arrow(sx + 40, sy + 40, 205, 240, color=POS, sw=1.0))

    p.append(rect(155, 240, 100, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(205, 268, "FAULT", size=13, color=POS, bold=True))
    p.append(text(205, 305, "5 окремих стрілок на EVT_EMERGENCY_STOP", size=10, color=POS))

    # Справа: Ієрархічний FSM (HSM)
    p.append(rect(430, 20, 370, 300, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    p.append(text(615, 45, "Ієрархічний HSM: наслідування подій", size=13, color=FIELD, bold=True))

    # Суперстан Operational
    p.append(rect(450, 70, 330, 150, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(525, 90, "Суперстан: OPERATIONAL", size=11, color=FIELD, bold=True))

    hstates = [
        (465, 110, "Init"),
        (565, 110, "Auth"),
        (665, 110, "Precharge"),
        (515, 160, "FastCharge"),
        (635, 160, "Balancing"),
    ]
    for sx, sy, sname in hstates:
        p.append(rect(sx, sy, 85, 35, fill="#ffffff", stroke=FIELD, sw=1.0, rx=3))
        p.append(text(sx + 42, sy + 22, sname, size=10, color=INK, bold=True))

    # Одна єдина стрілка від суперстану до FAULT
    p.append(arrow(615, 220, 615, 245, color=POS, sw=2.0))
    p.append(text(710, 235, "EVT_EMERGENCY_STOP", size=10, color=POS, bold=True))

    p.append(rect(565, 245, 100, 45, fill="#fee2e2", stroke=POS, sw=1.5, rx=6))
    p.append(text(615, 273, "FAULT", size=13, color=POS, bold=True))
    p.append(text(615, 305, "1 перехід покриває всі 5 підстанів!", size=10, color=FIELD, bold=True))

    render(os.path.join(OUT, "hierarchical-states-reduction.svg"), W, H, *p)


def fig_evse_state_machine():
    """Діаграма станів контролера зарядної станції (EVSE)."""
    W, H = 840, 400
    p = []
    p.append(rect(0, 0, W, H, fill=BG, stroke="none"))

    # State A: STANDBY
    p.append(rect(40, 60, 180, 90, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(130, 88, "A: STANDBY", size=13, color=NEG, bold=True))
    p.append(line(40, 100, 220, 100, color=NEG, sw=1.0))
    p.append(text(130, 120, "Реле: ВИМК", size=11, color=MUTED))
    p.append(text(130, 138, "Pilot: +12V DC", size=11, color=MUTED))

    # State B: CONNECTED
    p.append(rect(330, 60, 180, 90, fill="#fef3c7", stroke="#d97706", sw=1.8, rx=8))
    p.append(text(420, 88, "B: CONNECTED", size=13, color="#d97706", bold=True))
    p.append(line(330, 100, 510, 100, color="#d97706", sw=1.0))
    p.append(text(420, 120, "Реле: ВИМК", size=11, color=MUTED))
    p.append(text(420, 138, "Pilot: +9V 1kHz ШІМ", size=11, color=MUTED))

    # State C: CHARGING
    p.append(rect(620, 60, 180, 90, fill="#dcfce7", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(710, 88, "C: CHARGING", size=13, color=FIELD, bold=True))
    p.append(line(620, 100, 800, 100, color=FIELD, sw=1.0))
    p.append(text(710, 120, "Реле: УВІМК (230/400V)", size=11, color=POS, bold=True))
    p.append(text(710, 138, "Pilot: +6V 1kHz ШІМ", size=11, color=MUTED))

    # State D: FAULT
    p.append(rect(330, 250, 180, 90, fill="#fee2e2", stroke=POS, sw=1.8, rx=8))
    p.append(text(420, 278, "D: FAULT", size=13, color=POS, bold=True))
    p.append(line(330, 290, 510, 290, color=POS, sw=1.0))
    p.append(text(420, 310, "Реле: Аварійно ВИМК", size=11, color=POS, bold=True))
    p.append(text(420, 328, "Pilot: 0V / Error LED", size=11, color=MUTED))

    # Переходи між A, B, C
    p.append(arrow(220, 90, 330, 90, color=INK, sw=1.5))
    p.append(text(275, 80, "EVT_PLUG_IN", size=10, color=INK, bold=True))

    p.append(arrow(330, 125, 220, 125, color=MUTED, sw=1.2))
    p.append(text(275, 140, "EVT_UNPLUG", size=10, color=MUTED))

    p.append(arrow(510, 90, 620, 90, color=FIELD, sw=1.8))
    p.append(text(565, 80, "EVT_AUTH_OK", size=10, color=FIELD, bold=True))

    p.append(arrow(620, 125, 510, 125, color=MUTED, sw=1.2))
    p.append(text(565, 140, "EVT_CHARGE_STOP", size=10, color=MUTED))

    # Переходи у FAULT
    p.append(arrow(420, 150, 420, 250, color=POS, sw=1.5))
    p.append(text(475, 195, "EVT_PILOT_ERROR", size=10, color=POS))

    p.append(arrow(690, 150, 500, 260, color=POS, sw=1.8))
    p.append(text(645, 220, "EVT_OVERCURRENT / OVERTEMP", size=10, color=POS, bold=True))

    # Скидання з FAULT в STANDBY
    p.append(arrow(330, 295, 130, 150, color=NEG, sw=1.5))
    p.append(text(190, 245, "EVT_MANUAL_RESET", size=10, color=NEG, bold=True))

    render(os.path.join(OUT, "evse-state-machine.svg"), W, H, *p)


if __name__ == "__main__":
    fig_spaghetti_vs_fsm()
    fig_fsm_core_loop()
    fig_event_queue_architecture()
    fig_hierarchical_states_reduction()
    fig_evse_state_machine()
    print("Всі фігури згенеровано успішно.")
