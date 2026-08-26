# -*- coding: utf-8 -*-
"""Фігури до теми «Сторож, який справді ловить зависання».
Запуск: python figs.py
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Ілюзія захисту: три пастки «годування собаки» ────────────────────────
def fig_failure_modes():
    W, H = 880, 430
    f = []
    f.append(text(W / 2, 28, "Ілюзія захисту: три сценарії, де просте скидання сторожа не рятує від аварії",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "сторож бачить лише факт виклику команди перезаряджання, а не правильність роботи алгоритму",
                  11.5, MUTED, "middle", italic=True))

    col_w = 264
    gap = 24
    lefts = [24, 24 + col_w + gap, 24 + 2 * (col_w + gap)]

    # Колонка 1: Скидання в перериванні (ISR)
    x1 = lefts[0]
    f.append(rect(x1, 68, col_w, 332, fill="#fdfefe", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(rect(x1, 68, col_w, 38, fill="#fbe9e7", stroke=POS, sw=1.5, rx=8))
    f.append(text(x1 + col_w / 2, 92, "1. Скидання в таймері (ISR)", 13, POS, "middle", bold=True))

    # Стан головного циклу
    f.append(rect(x1 + 14, 120, col_w - 28, 54, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(x1 + col_w / 2, 142, "Головний потік: DEADLOCK", 11.5, POS, "middle", bold=True))
    f.append(text(x1 + col_w / 2, 160, "застряг у mutex / очікуванні I2C", 10.5, MUTED, "middle"))

    # SysTick ISR
    f.append(rect(x1 + 14, 192, col_w - 28, 58, fill="#e9f7ef", stroke=FIELD, sw=1.4, rx=6))
    f.append(text(x1 + col_w / 2, 214, "SysTick ISR (кожні 10 мс)", 11.5, FIELD, "middle", bold=True))
    f.append(text(x1 + col_w / 2, 234, "IWDG->KR = 0xAAAA (OK)", 10.5, INK, "middle"))

    f.append(arrow(x1 + col_w / 2, 252, x1 + col_w / 2, 280, color=POS, sw=1.6))

    # Наслідок
    f.append(rect(x1 + 14, 286, col_w - 28, 98, fill="#fff5f5", stroke=POS, sw=1.4, rx=6))
    f.append(text(x1 + col_w / 2, 308, "Апаратний WDT ситий", 11.5, POS, "middle", bold=True))
    f.append(text(x1 + col_w / 2, 328, "Переривання активні, але логіка", 10.5, INK, "middle"))
    f.append(text(x1 + col_w / 2, 346, "керування мертва. Мотор крутить,", 10.5, INK, "middle"))
    f.append(text(x1 + col_w / 2, 364, "ресета немає годинами!", 10.5, POS, "middle", bold=True))

    # Колонка 2: Холостий цикл помилки
    x2 = lefts[1]
    f.append(rect(x2, 68, col_w, 332, fill="#fdfefe", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(rect(x2, 68, col_w, 38, fill="#fff3e0", stroke="#e67e22", sw=1.5, rx=8))
    f.append(text(x2 + col_w / 2, 92, "2. Холостий цикл помилки", 13, "#d35400", "middle", bold=True))

    f.append(rect(x2 + 14, 120, col_w - 28, 54, fill="#fff8e1", stroke="#f39c12", sw=1.4, rx=6))
    f.append(text(x2 + col_w / 2, 142, "while (1) { step(); kick(); }", 11.5, INK, "middle", bold=True))
    f.append(text(x2 + col_w / 2, 160, "step() повертає ERR_TIMEOUT", 10.5, POS, "middle"))

    f.append(rect(x2 + 14, 192, col_w - 28, 58, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(x2 + col_w / 2, 214, "Швидкий холостий біг", 11.5, POS, "middle", bold=True))
    f.append(text(x2 + col_w / 2, 234, "100 000 ітерацій помилки/с", 10.5, MUTED, "middle"))

    f.append(arrow(x2 + col_w / 2, 252, x2 + col_w / 2, 280, color=POS, sw=1.6))

    f.append(rect(x2 + 14, 286, col_w - 28, 98, fill="#fff5f5", stroke=POS, sw=1.4, rx=6))
    f.append(text(x2 + col_w / 2, 308, "WDT скидається в 1000x частіше", 11.0, POS, "middle", bold=True))
    f.append(text(x2 + col_w / 2, 328, "Корисна робота не виконується,", 10.5, INK, "middle"))
    f.append(text(x2 + col_w / 2, 346, "буфери переповнюються, але", 10.5, INK, "middle"))
    f.append(text(x2 + col_w / 2, 364, "сторож не фіксує аварії!", 10.5, POS, "middle", bold=True))

    # Колонка 3: Голодування в RTOS
    x3 = lefts[2]
    f.append(rect(x3, 68, col_w, 332, fill="#fdfefe", stroke="#d0d7de", sw=1.5, rx=8))
    f.append(rect(x3, 68, col_w, 38, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=8))
    f.append(text(x3 + col_w / 2, 92, "3. Голодування потоку в RTOS", 13, NEG, "middle", bold=True))

    f.append(rect(x3 + 14, 120, col_w - 28, 54, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=6))
    f.append(text(x3 + col_w / 2, 142, "Потік A (Priority High): OK", 11.5, NEG, "middle", bold=True))
    f.append(text(x3 + col_w / 2, 160, "захопив 100% CPU й скидає WDT", 10.5, MUTED, "middle"))

    f.append(rect(x3 + 14, 192, col_w - 28, 58, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(x3 + col_w / 2, 214, "Потік B (Priority Low): STARVED", 11.0, POS, "middle", bold=True))
    f.append(text(x3 + col_w / 2, 234, "безпековий монітор не отримує квант", 10.0, POS, "middle"))

    f.append(arrow(x3 + col_w / 2, 252, x3 + col_w / 2, 280, color=POS, sw=1.6))

    f.append(rect(x3 + 14, 286, col_w - 28, 98, fill="#fff5f5", stroke=POS, sw=1.4, rx=6))
    f.append(text(x3 + col_w / 2, 308, "Частковий параліч системи", 11.5, POS, "middle", bold=True))
    f.append(text(x3 + col_w / 2, 328, "Один потік живе й годує WDT,", 10.5, INK, "middle"))
    f.append(text(x3 + col_w / 2, 346, "інші критичні задачі заморожені.", 10.5, INK, "middle"))
    f.append(text(x3 + col_w / 2, 364, "Система деградує непомітно.", 10.5, POS, "middle", bold=True))

    f.append(text(W / 2, H - 12,
                  "Висновок: скидання сторожа має свідчити про успішний крок ВСІХ компонентів системи, а не просто про роботу таймера.",
                  11.0, INK, "middle", italic=True))

    render(os.path.join(IMG, "wdt-failure-modes.svg"), W, H, *f)


# ── 2. IWDG проти WWDG: часове вікно ─────────────────────────────────────────
def fig_iwdg_vs_wwdg():
    W, H = 880, 430
    f = []
    f.append(text(W / 2, 28, "Незалежний сторож (IWDG) проти Віконного сторожа (WWDG)",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "IWDG ловить лише запізніле скидання; WWDG карає перезавантаженням і занадто ранній виклик",
                  11.5, MUTED, "middle", italic=True))

    # Верхній блок: IWDG
    y1 = 82
    f.append(rect(30, y1, W - 60, 140, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(50, y1 + 24, "IWDG (Незалежний сторож — тактування від внутрішнього RC LSI ~32 кГц)", 13, INK, "start", bold=True))

    # Вісь часу / лічильника IWDG
    ax_y = y1 + 75
    f.append(line(70, ax_y, W - 70, ax_y, color=MUTED, sw=1.5))
    f.append(arrow(W - 80, ax_y, W - 50, ax_y, color=MUTED, sw=1.5))
    f.append(text(W - 50, ax_y + 18, "час →", 10.5, MUTED, "end", italic=True))

    # Дозволена зона IWDG
    f.append(rect(70, ax_y - 20, 600, 20, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(370, ax_y - 6, "ДОЗВОЛЕНА ЗОНА СКИДАННЯ (від t = 0 до t_timeout)", 11, FIELD, "middle", bold=True))

    # Зона скидання за таймаутом
    f.append(rect(670, ax_y - 20, 130, 20, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(735, ax_y - 6, "TIMEOUT (RESET)", 10.5, POS, "middle", bold=True))

    f.append(line(70, ax_y - 28, 70, ax_y + 12, color=INK, sw=1.4))
    f.append(text(70, ax_y + 24, "Reload (0xFFF)", 10.5, INK, "middle"))

    f.append(line(670, ax_y - 28, 670, ax_y + 12, color=POS, sw=1.6, dash="3,3"))
    f.append(text(670, ax_y + 24, "0x000 (Аварія)", 10.5, POS, "middle", bold=True))

    f.append(text(50, y1 + 124, "⚠️ Слабкість: runaway code (збій PC) викликає скидання за 5 мкс — IWDG не бачить аномалії.",
                  11, POS, "start", bold=True))

    # Нижній блок: WWDG
    y2 = 242
    f.append(rect(30, y2, W - 60, 150, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(50, y2 + 24, "WWDG (Віконний сторож — тактування від шини APB1)", 13, INK, "start", bold=True))

    ax_y2 = y2 + 75
    f.append(line(70, ax_y2, W - 70, ax_y2, color=MUTED, sw=1.5))
    f.append(arrow(W - 80, ax_y2, W - 50, ax_y2, color=MUTED, sw=1.5))
    f.append(text(W - 50, ax_y2 + 18, "час →", 10.5, MUTED, "end", italic=True))

    # Зона 1: Занадто рано (Window Violation)
    f.append(rect(70, ax_y2 - 20, 240, 20, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(190, ax_y2 - 6, "ЗАБОРОНЕНО: Занадто рано (RESET)", 10.5, POS, "middle", bold=True))

    # Зона 2: Дозволене вікно
    f.append(rect(310, ax_y2 - 20, 360, 20, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(490, ax_y2 - 6, "ДОЗВОЛЕНЕ ВІКНО СКИДАННЯ [W_threshold ... 0x40]", 11, FIELD, "middle", bold=True))

    # Зона 3: Занадто пізно (Underflow)
    f.append(rect(670, ax_y2 - 20, 130, 20, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(735, ax_y2 - 6, "UNDERFLOW (RESET)", 10.5, POS, "middle", bold=True))

    f.append(line(70, ax_y2 - 28, 70, ax_y2 + 12, color=INK, sw=1.4))
    f.append(text(70, ax_y2 + 24, "Старт (0x7F)", 10.5, INK, "middle"))

    f.append(line(310, ax_y2 - 28, 310, ax_y2 + 12, color=NEG, sw=1.6, dash="3,3"))
    f.append(text(310, ax_y2 + 24, "W[6:0] (Поріг вікна)", 10.5, NEG, "middle", bold=True))

    f.append(line(670, ax_y2 - 28, 670, ax_y2 + 12, color=POS, sw=1.6, dash="3,3"))
    f.append(text(670, ax_y2 + 24, "0x3F (Низхідний поріг)", 10.5, POS, "middle", bold=True))

    f.append(text(50, y2 + 134, "🛡 Захист: якщо прошивка зациклилась у швидкому холостому циклі — раннє скидання генерує RESET!",
                  11, FIELD, "start", bold=True))

    f.append(text(W / 2, H - 10,
                  "WWDG вимагає детермінованого періоду виконання: не можна скидати ні занадто пізно, ні занадто рано.",
                  11.0, INK, "middle", italic=True))

    render(os.path.join(IMG, "iwdg-vs-wwdg-timing.svg"), W, H, *f)


# ── 3. Зовнішній апаратний супервізор ────────────────────────────────────────
def fig_hardware_supervisor():
    W, H = 880, 420
    f = []
    f.append(text(W / 2, 28, "Зовнішній апаратний супервізор (TPS3823 / STWD100)", 16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "фізично незалежний кристал захищає від latch-up, збоїв внутрішнього живлення та зависання тактування",
                  11.5, MUTED, "middle", italic=True))

    # Лівий блок: MCU
    mcu_x, mcu_y, mcu_w, mcu_h = 60, 80, 270, 290
    f.append(rect(mcu_x, mcu_y, mcu_w, mcu_h, fill="#f8fafc", stroke="#475569", sw=2, rx=8))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 26, "Мікроконтролер (MCU)", 14, INK, "middle", bold=True))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 44, "Спільна кремнієва підкладка", 10.5, MUTED, "middle"))

    # Внутрішні блоки MCU
    f.append(rect(mcu_x + 20, mcu_y + 60, mcu_w - 40, 50, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 82, "CPU Core + RAM", 12, INK, "middle", bold=True))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 98, "Може зависнути в Latch-up / Brownout", 9.5, POS, "middle"))

    f.append(rect(mcu_x + 20, mcu_y + 120, mcu_w - 40, 46, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 140, "GPIO Pin (WDI Out)", 11.5, FIELD, "middle", bold=True))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 155, "Імпульси здоров'я (Heartbeat)", 9.5, MUTED, "middle"))

    f.append(rect(mcu_x + 20, mcu_y + 176, mcu_w - 40, 46, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 196, "NRST Pin (Вхід скидання)", 11.5, POS, "middle", bold=True))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 211, "Апаратний ресет ядра й периферії", 9.5, MUTED, "middle"))

    f.append(rect(mcu_x + 20, mcu_y + 232, mcu_w - 40, 42, fill="#f1f5f9", stroke="#cbd5e1", sw=1.2, rx=4))
    f.append(text(mcu_x + mcu_w / 2, mcu_y + 258, "VDD (3.3V)", 11.5, INK, "middle", bold=True))

    # Правий блок: Зовнішній Watchdog IC
    ic_x, ic_y, ic_w, ic_h = 550, 80, 270, 290
    f.append(rect(ic_x, ic_y, ic_w, ic_h, fill="#fffdfa", stroke="#d97706", sw=2, rx=8))
    f.append(text(ic_x + ic_w / 2, ic_y + 26, "Апаратний супервізор (WDT IC)", 14, "#b45309", "middle", bold=True))
    f.append(text(ic_x + ic_w / 2, ic_y + 44, "Окремий кремній (TPS3823 / STWD100)", 10.5, MUTED, "middle"))

    f.append(rect(ic_x + 20, ic_y + 60, ic_w - 40, 50, fill="#ffffff", stroke="#fed7aa", sw=1.2, rx=4))
    f.append(text(ic_x + ic_w / 2, ic_y + 82, "Прецизійний генератор + WDT", 11.5, INK, "middle", bold=True))
    f.append(text(ic_x + ic_w / 2, ic_y + 98, "Таймаут t_WD = 1.6 с (фіксований)", 10.0, MUTED, "middle"))

    f.append(rect(ic_x + 20, ic_y + 120, ic_w - 40, 46, fill="#ffffff", stroke="#fed7aa", sw=1.2, rx=4))
    f.append(text(ic_x + ic_w / 2, ic_y + 140, "WDI (Watchdog Input)", 11.5, FIELD, "middle", bold=True))
    f.append(text(ic_x + ic_w / 2, ic_y + 155, "Детектор фронтів (Edge Detector)", 9.5, MUTED, "middle"))

    f.append(rect(ic_x + 20, ic_y + 176, ic_w - 40, 46, fill="#ffffff", stroke="#fed7aa", sw=1.2, rx=4))
    f.append(text(ic_x + ic_w / 2, ic_y + 196, "/RESET Out (Open-Drain)", 11.5, POS, "middle", bold=True))
    f.append(text(ic_x + ic_w / 2, ic_y + 211, "Формувач імпульсу t_RST = 200 мс", 9.5, MUTED, "middle"))

    f.append(rect(ic_x + 20, ic_y + 232, ic_w - 40, 42, fill="#ffffff", stroke="#fed7aa", sw=1.2, rx=4))
    f.append(text(ic_x + ic_w / 2, ic_y + 252, "Компаратор VDD (BOD)", 11.5, POS, "middle", bold=True))
    f.append(text(ic_x + ic_w / 2, ic_y + 266, "Поріг V_IT = 2.93V (1% точність)", 9.5, MUTED, "middle"))

    # З'єднання між MCU та IC
    # 1. Лінія WDI: MCU -> IC
    wdi_y = mcu_y + 143
    f.append(arrow(mcu_x + mcu_w - 20, wdi_y, ic_x + 20, wdi_y, color=FIELD, sw=2.0))
    f.append(text((mcu_x + mcu_w + ic_x) / 2, wdi_y - 7, "Лінія WDI (імпульси)", 11, FIELD, "middle", bold=True))

    # 2. Лінія /RESET: IC -> MCU
    rst_y = mcu_y + 199
    f.append(arrow(ic_x + 20, rst_y, mcu_x + mcu_w - 20, rst_y, color=POS, sw=2.0))
    f.append(text((mcu_x + mcu_w + ic_x) / 2, rst_y - 7, "Лінія /RESET (активний низький)", 11, POS, "middle", bold=True))

    # 3. Шина живлення
    vdd_y = mcu_y + 253
    f.append(line(mcu_x + mcu_w - 20, vdd_y, ic_x + 20, vdd_y, color=INK, sw=1.5, dash="4,4"))
    f.append(text((mcu_x + mcu_w + ic_x) / 2, vdd_y - 7, "Шина живлення 3.3V", 10.5, INK, "middle"))

    f.append(text(W / 2, H - 12,
                  "Зовнішній супервізор гарантує ресет при збої опорного генератора MCU або просадці живлення нижче 2.93 В.",
                  11.0, INK, "middle", italic=True))

    render(os.path.join(IMG, "hardware-watchdog-supervisor.svg"), W, H, *f)


# ── 4. Дворівнева архітектура Task Watchdog Supervisor ─────────────────────
def fig_task_watchdog_architecture():
    W, H = 880, 440
    f = []
    f.append(text(W / 2, 28, "Дворівневий наглядач (Task Watchdog Supervisor) у RTOS / Bare-Metal",
                  16.0, INK, "middle", bold=True))
    f.append(text(W / 2, 48, "потоки відмічаються в таблиці здоров'я; диспетчер оновлює апаратний таймер лише за 100% готовності",
                  11.5, MUTED, "middle", italic=True))

    # Ліва колонка: Робочі потоки (Tasks)
    col1_x, col1_w = 40, 230
    f.append(rect(col1_x, 75, col1_w, 325, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(col1_x + col1_w / 2, 98, "Рівень завдань (Tasks)", 13.5, INK, "middle", bold=True))
    f.append(text(col1_x + col1_w / 2, 114, "Кожен потік має свій таймаут", 10.5, MUTED, "middle"))

    tasks = [
        ("Task 1: Сенсори (50 мс)", "wdt_checkin(ID_SENSORS)", "#eaf0fd", NEG),
        ("Task 2: Керування/PID (10 мс)", "wdt_checkin(ID_CONTROL)", "#eaf0fd", NEG),
        ("Task 3: Телеметрія (200 мс)", "wdt_checkin(ID_TELEMETRY)", "#eaf0fd", NEG),
        ("Task 4: Логування (500 мс)", "wdt_checkin(ID_LOGGER)", "#eaf0fd", NEG),
    ]

    for i, (name, fn, fill_col, border_col) in enumerate(tasks):
        ty = 130 + i * 62
        f.append(rect(col1_x + 12, ty, col1_w - 24, 52, fill=fill_col, stroke=border_col, sw=1.2, rx=6))
        f.append(text(col1_x + col1_w / 2, ty + 20, name, 11.5, INK, "middle", bold=True))
        f.append(text(col1_x + col1_w / 2, ty + 38, fn, 10.5, FIELD, "middle"))

    # Центральна колонка: Диспетчер нагляду (Watchdog Supervisor)
    col2_x, col2_w = 320, 280
    f.append(rect(col2_x, 75, col2_w, 325, fill="#f0fdf4", stroke=FIELD, sw=2, rx=8))
    f.append(text(col2_x + col2_w / 2, 98, "Диспетчер здоров'я (Supervisor)", 13.5, FIELD, "middle", bold=True))
    f.append(text(col2_x + col2_w / 2, 114, "Task із каліброваним пріоритетом", 10.5, MUTED, "middle"))

    # Таблиця дедлайнів всередині диспетчера
    f.append(rect(col2_x + 14, 130, col2_w - 28, 140, fill="#ffffff", stroke="#bbf7d0", sw=1.2, rx=6))
    f.append(text(col2_x + col2_w / 2, 150, "Таблиця контролю дедлайнів", 11.5, INK, "middle", bold=True))
    f.append(line(col2_x + 24, 160, col2_x + col2_w - 24, 160, color="#e2e8f0", sw=1))

    f.append(text(col2_x + 24, 178, "ID 0: Sensors     → 12 ms / 50 ms  [OK]", 10.0, FIELD, "start"))
    f.append(text(col2_x + 24, 196, "ID 1: Control     →  4 ms / 10 ms  [OK]", 10.0, FIELD, "start"))
    f.append(text(col2_x + 24, 214, "ID 2: Telemetry   → 80 ms / 200 ms [OK]", 10.0, FIELD, "start"))
    f.append(text(col2_x + 24, 232, "ID 3: Logger      → 150 ms/ 500 ms [OK]", 10.0, FIELD, "start"))
    f.append(text(col2_x + col2_w / 2, 256, "Усі дедлайни дотримані? (100% OK)", 10.5, FIELD, "middle", bold=True))

    # Логіка рішення
    f.append(rect(col2_x + 14, 280, col2_w - 28, 52, fill="#fdecea", stroke=POS, sw=1.2, rx=6))
    f.append(text(col2_x + col2_w / 2, 300, "Якщо хоч один потік прострочив:", 10.5, POS, "middle", bold=True))
    f.append(text(col2_x + col2_w / 2, 318, "Записати Core Dump у noinit RAM → STOP KICK", 10.0, POS, "middle"))

    f.append(rect(col2_x + 14, 340, col2_w - 28, 48, fill="#e9f7ef", stroke=FIELD, sw=1.2, rx=6))
    f.append(text(col2_x + col2_w / 2, 360, "Якщо всі здорові:", 10.5, FIELD, "middle", bold=True))
    f.append(text(col2_x + col2_w / 2, 376, "hw_wdt_refresh() → скинути залізо", 10.5, FIELD, "middle"))

    # Права колонка: Апаратний WDT
    col3_x, col3_w = 650, 190
    f.append(rect(col3_x, 75, col3_w, 325, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(col3_x + col3_w / 2, 98, "Апаратний WDT", 13.5, INK, "middle", bold=True))
    f.append(text(col3_x + col3_w / 2, 114, "IWDG / WWDG / Ext IC", 10.5, MUTED, "middle"))

    f.append(rect(col3_x + 14, 150, col3_w - 28, 80, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6))
    f.append(text(col3_x + col3_w / 2, 175, "Таймер 1.0 с", 12.5, INK, "middle", bold=True))
    f.append(text(col3_x + col3_w / 2, 195, "Отримує імпульс", 10.5, FIELD, "middle"))
    f.append(text(col3_x + col3_w / 2, 212, "кожні 100 мс", 10.5, FIELD, "middle"))

    f.append(arrow(col3_x + col3_w / 2, 240, col3_x + col3_w / 2, 280, color=POS, sw=1.8))
    f.append(rect(col3_x + 14, 285, col3_w - 28, 95, fill="#fdecea", stroke=POS, sw=1.4, rx=6))
    f.append(text(col3_x + col3_w / 2, 310, "MCU RESET", 13, POS, "middle", bold=True))
    f.append(text(col3_x + col3_w / 2, 330, "Спрацьовує при", 10.5, INK, "middle"))
    f.append(text(col3_x + col3_w / 2, 348, "зависанні БУДЬ-ЯКОГО", 10.5, POS, "middle", bold=True))
    f.append(text(col3_x + col3_w / 2, 366, "зареєстрованого потоку", 10.0, INK, "middle"))

    # Стрілки між колонками
    # Від завдань до диспетчера
    for i in range(4):
        ty = 156 + i * 62
        f.append(arrow(col1_x + col1_w - 12, ty, col2_x + 14, ty, color=NEG, sw=1.5))

    # Від диспетчера до апаратного WDT
    f.append(arrow(col2_x + col2_w - 14, 364, col3_x + 14, 190, color=FIELD, sw=2.0))

    f.append(text(W / 2, H - 12,
                  "Жоден окремий потік не має прямого доступу до апаратного сторожа — лише централізований арбітраж.",
                  11.0, INK, "middle", italic=True))

    render(os.path.join(IMG, "task-watchdog-architecture.svg"), W, H, *f)


if __name__ == "__main__":
    fig_failure_modes()
    fig_iwdg_vs_wwdg()
    fig_hardware_supervisor()
    fig_task_watchdog_architecture()
    print("OK: 4 figures generated in", IMG)
