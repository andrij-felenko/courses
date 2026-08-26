# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARM = "#fdecea"   # світла гаряча заливка (небезпека, помилка)
COOL = "#eaf0fd"   # світла синя заливка
GRN  = "#eaf7ee"   # світла зелена заливка (безпека, коректність)
GOLD = "#caa24a"   # бурштин
GBG  = "#fff7e6"   # світлий бурштин

# ── 1. handler-vs-thread: Вододіл двох світів виконання ───────────────────────
def fig_handler_vs_thread():
    W, H = 760, 360
    p = []
    p.append(text(W/2, 28, "Вододіл контекстів: режим задачі проти режиму переривання", size=15, bold=True))
    p.append(text(W/2, 48, "різні стеки, відсутність TCB в обробника та неможливість блокування",
                  size=11, color=MUTED, italic=True))

    # Ліва колонка: Режим задачі (Thread Mode / PSP)
    x1, y1, w_col, h_col = 35, 70, 330, 225
    p.append(rect(x1, y1, w_col, h_col, fill=COOL, stroke=NEG, sw=1.5, rx=8))
    p.append(text(x1 + w_col/2, y1 + 24, "Режим задачі (Thread Mode)", size=13, color=NEG, bold=True))
    p.append(text(x1 + w_col/2, y1 + 42, "Контекст звичайної задачі RTOS", size=10.5, color=MUTED))

    # Елементи зліва
    b1_items = [
        "Стек задачі: PSP (Process Stack Pointer)",
        "Має власний блок керування (TCB)",
        "Може засинати, чекати та блокуватися",
        "Планувальник перемикає витісненням",
        "Звичайні API (xQueueSend, vTaskDelay)"
    ]
    for i, item in enumerate(b1_items):
        by = y1 + 65 + i * 30
        p.append(rect(x1 + 15, by, w_col - 30, 24, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        p.append(text(x1 + w_col/2, by + 16, item, size=10, color=INK))

    # Права колонка: Режим переривання (Handler Mode / MSP)
    x2 = 395
    p.append(rect(x2, y1, w_col, h_col, fill=WARM, stroke=POS, sw=1.5, rx=8))
    p.append(text(x2 + w_col/2, y1 + 24, "Режим обробника (Handler Mode)", size=13, color=POS, bold=True))
    p.append(text(x2 + w_col/2, y1 + 42, "Контекст апаратного переривання (ISR)", size=10.5, color=MUTED))

    # Елементи справа
    b2_items = [
        "Головний стек: MSP (Main Stack Pointer)",
        "НЕ має власного TCB (не є задачею)",
        "ЗАБОРОНЕНО блокуватися чи засинати",
        "Керується апаратним контролером NVIC",
        "Тільки неблокуючі виклики ...FromISR"
    ]
    for i, item in enumerate(b2_items):
        by = y1 + 65 + i * 30
        p.append(rect(x2 + 15, by, w_col - 30, 24, fill="#ffffff", stroke="#cbd5e1", sw=1, rx=4))
        p.append(text(x2 + w_col/2, by + 16, item, size=10, color=INK, bold=(i == 2)))

    # Нижня рамка синтезу
    p.append(fitbox(50, 305, 660, 42,
                    "Обробник переривання не має власного TCB і виконується на стеку ядра (MSP).\n"
                    "Будь-яка спроба заблокувати ISR пошкоджує випадкову перервану задачу й вішає систему.",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "handler-vs-thread.svg"), W, H, *p)


# ── 2. blocking-in-isr-trap: Чому блокування в ISR руйнівне ───────────────────
def fig_blocking_in_isr_trap():
    W, H = 760, 360
    p = []
    p.append(text(W/2, 26, "Анатомія катастрофи: виклик блокуючого API всередині ISR", size=15, bold=True))
    p.append(text(W/2, 46, "ланцюжок подій при спробі почекати на повну чергу через xQueueSend(..., portMAX_DELAY)",
                  size=11, color=MUTED, italic=True))

    # 4 послідовні кроки аварії
    steps = [
        ("1. Виклик в ISR", "Обробник кличе звичайний\nxQueueSend(..., timeout)\nна заповнену чергу.", WARM, POS),
        ("2. Плутанина TCB", "Ядро намагається заблокувати\n«поточну задачу», але на CPU\nвиконується ISR на MSP!", WARM, POS),
        ("3. Пошкодження стану", "Зіпсовано TCB перерваної\nзадачі; NVIC тримає лінію\nпереривання активною.", WARM, POS),
        ("4. Повний глухий кут", "Всі рівні й нижчі IRQ\nзаблоковані залізом; система\nназавжди зависає.", "#fadbd8", POS)
    ]

    kw = 155
    gap = 25
    x0 = 30
    y0 = 75

    for i, (title, desc, bg_col, brd_col) in enumerate(steps):
        bx = x0 + i * (kw + gap)
        p.append(rect(bx, y0, kw, 195, fill=bg_col, stroke=brd_col, sw=1.5, rx=6))
        p.append(text(bx + kw/2, y0 + 24, title, size=11, color=POS, bold=True))
        p.append(line(bx + 10, y0 + 36, bx + kw - 10, y0 + 36, color=POS, sw=1))
        
        lines = desc.split("\n")
        for li, ln in enumerate(lines):
            p.append(text(bx + kw/2, y0 + 65 + li * 22, ln, size=9.5, color=INK))

        # Стрілка переходу між кроками
        if i < 3:
            ax1 = bx + kw + 3
            ax2 = bx + kw + gap - 3
            ay = y0 + 95
            p.append(arrow(ax1, ay, ax2, ay, color=POS, sw=2))

    # Нижня рамка
    p.append(fitbox(45, 290, 670, 52,
                    "Правило надійності: в обробниках переривань блокування не просто «повільне» — воно фізично\n"
                    "руйнує диспетчеризацію RTOS. Функції FromISR принципово не мають параметра тайм-ауту.",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "blocking-in-isr-trap.svg"), W, H, *p)


# ── 3. fromisr-mechanism: Архітектура функцій FromISR ──────────────────────────
def fig_fromisr_mechanism():
    W, H = 760, 370
    p = []
    p.append(text(W/2, 26, "Архітектура FromISR: неблокуюча дія та прапорець витіснення", size=15, bold=True))
    p.append(text(W/2, 46, "як функція RTOS фіксує пробудження важливої задачі без прямого перемикання контексту",
                  size=11, color=MUTED, italic=True))

    # Блок 1: Виклик FromISR
    p.append(rect(35, 75, 205, 205, fill=COOL, stroke=NEG, sw=1.5, rx=6))
    p.append(text(137.5, 98, "1. Дія в ISR", size=12, color=NEG, bold=True))
    p.append(fitbox(45, 115, 185, 150,
                    "xQueueSendFromISR(\n"
                    "  q, &data,\n"
                    "  &xHigherWoken\n"
                    ");\n\n"
                    "• Запис у буфер за O(1)\n"
                    "• Ніколи не блокується\n"
                    "• Повертає pdPASS / err",
                    size=10, fill="#ffffff", stroke="#cbd5e1", bold=False))

    # Стрілка 1 -> 2
    p.append(arrow(245, 175, 275, 175, color=LINE, sw=1.8))

    # Блок 2: Логіка всередині ядра FreeRTOS
    p.append(rect(280, 75, 215, 205, fill=GRN, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(387.5, 98, "2. Реакція ядра", size=12, color=FIELD, bold=True))
    p.append(fitbox(290, 115, 195, 150,
                    "Черга розблоковує задачу:\n\n"
                    "• Переносить задачу зі\n"
                    "  списку очікування в Ready\n"
                    "• Якщо пріоритет вищий за\n"
                    "  поточний перерваний:\n"
                    "  *pxHigherWoken = pdTRUE;",
                    size=10, fill="#ffffff", stroke="#cbd5e1", bold=False))

    # Стрілка 2 -> 3
    p.append(arrow(500, 175, 530, 175, color=LINE, sw=1.8))

    # Блок 3: Запит на перемикання перед виходом
    p.append(rect(535, 75, 190, 205, fill=GBG, stroke=GOLD, sw=1.5, rx=6))
    p.append(text(630, 98, "3. portYIELD_FROM_ISR", size=12, color=GOLD, bold=True))
    p.append(fitbox(545, 115, 170, 150,
                    "Якщо xHigherWoken:\n\n"
                    "• Виставляє переривання\n"
                    "  PendSV у регістрі ICSR\n"
                    "• Контекст перемкнеться\n"
                    "  МИТТЄВО при виході\n"
                    "  з переривання!",
                    size=10, fill="#ffffff", stroke="#cbd5e1", bold=False))

    # Нижня рамка
    p.append(fitbox(45, 295, 670, 56,
                    "Прапорець pxHigherPriorityTaskWoken запобігає зайвим перемиканням:\n"
                    "якщо розбуджена задача має нижчий пріоритет за перервану, CPU повертається назад без зволікань.\n"
                    "Якщо ж її пріоритет вищий — portYIELD_FROM_ISR() забезпечує негайне витіснення.",
                    size=10.5, fill=COOL, stroke=NEG, bold=True))

    render(os.path.join(OUT, "fromisr-mechanism.svg"), W, H, *p)


# ── 4. pendsv-deferred-switch: Відкладене перемикання через PendSV ─────────────
def fig_pendsv_deferred_switch():
    W, H = 760, 390
    p = []
    p.append(text(W/2, 26, "Відкладене перемикання контексту: механіка PendSV у Cortex-M", size=15, bold=True))
    p.append(text(W/2, 46, "чому перемикання контексту чекає завершення всіх апаратних обробників",
                  size=11, color=MUTED, italic=True))

    # Часова вісь (Timeline)
    y_tl = 85
    p.append(line(50, y_tl, 710, y_tl, color=LINE, sw=2))
    p.append(arrow(690, y_tl, 715, y_tl, color=LINE, sw=2))
    p.append(text(715, y_tl - 8, "Час (t)", size=10, color=MUTED, anchor="end"))

    # Фази виконання вздовж осі часу
    phases = [
        (60, 100, "Задача A\n(низька)", COOL, NEG),
        (170, 140, "Апаратне IRQ\n(UART ISR)", WARM, POS),
        (320, 120, "Вкладене IRQ\n(Timer ISR)", "#fadbd8", POS),
        (450, 90, "Вихід з IRQ\n(завершення)", WARM, POS),
        (550, 70, "PendSV\n(перемикання)", GBG, GOLD),
        (630, 80, "Задача B\n(висока)", GRN, FIELD)
    ]

    for x, w, lbl, f_col, s_col in phases:
        p.append(rect(x, y_tl + 15, w, 55, fill=f_col, stroke=s_col, sw=1.5, rx=5))
        lines = lbl.split("\n")
        p.append(text(x + w/2, y_tl + 37, lines[0], size=10.5, color=INK, bold=True))
        if len(lines) > 1:
            p.append(text(x + w/2, y_tl + 53, lines[1], size=9.5, color=MUTED))
        # Відмітки на часовій осі
        p.append(line(x, y_tl - 5, x, y_tl + 5, color=LINE, sw=1.5))

    # Пояснювальні виноски під фазами
    p.append(text(240, y_tl + 90, "▲ xQueueSendFromISR() будить Задачу B", size=10, color=POS, bold=True))
    p.append(text(240, y_tl + 107, "  portYIELD_FROM_ISR() виставляє біт PendSV", size=9.5, color=MUTED))

    p.append(text(380, y_tl + 130, "▲ Вкладене переривання виконується на MSP", size=10, color=POS))
    p.append(text(380, y_tl + 147, "  PendSV не запускається, бо має найнижчий пріоритет!", size=9.5, color=MUTED))

    p.append(text(585, y_tl + 90, "▲ PendSV виконує зміну TCB", size=10, color=GOLD, bold=True))
    p.append(text(585, y_tl + 107, "  зберігає PSP_A, вантажить PSP_B", size=9.5, color=MUTED))

    # Нижня синтезна рамка
    p.append(fitbox(45, 275, 670, 95,
                    "Чому PendSV на найнижчому пріоритеті: якби перемикання контексту відбувалося прямо в ISR периферії,\n"
                    "воно пошкодило б апаратний стек вкладених переривань. Завдяки PendSV процесор спочатку чисто\n"
                    "завершує всі вкладені обробники, і лише при поверненні в режим потоку (Thread Mode) безпечно\n"
                    "передає керування новорозбудженій високій задачі.",
                    size=10.5, fill=FILL, stroke=LINE, bold=False))

    render(os.path.join(OUT, "pendsv-deferred-switch.svg"), W, H, *p)


# ── 5. interrupt-priority-matrix: Матриця пріоритетів переривань ──────────────
def fig_interrupt_priority_matrix():
    W, H = 760, 360
    p = []
    p.append(text(W/2, 26, "Матриця пріоритетів NVIC та поріг configMAX_SYSCALL_INTERRUPT_PRIORITY", size=14, bold=True))
    p.append(text(W/2, 45, "розподіл рівнів у Cortex-M: нульовий джитер проти викликів RTOS API",
                  size=11, color=MUTED, italic=True))

    # Спектр пріоритетів (вертикальний або горизонтальний)
    # Зліва: шкала чисел NVIC vs логічний пріоритет
    p.append(rect(40, 70, 180, 200, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    p.append(text(130, 92, "Шкала Cortex-M", size=12, color=INK, bold=True))
    p.append(text(130, 115, "Рівень 0 (найвищий)", size=10, color=POS, bold=True))
    p.append(text(130, 133, "Рівень 1 .. 4", size=10, color=POS))
    p.append(line(55, 148, 205, 148, color=GOLD, sw=2, dash="4,3"))
    p.append(text(130, 163, "configMAX_SYSCALL (5)", size=9.5, color=GOLD, bold=True))
    p.append(line(55, 175, 205, 175, color=GOLD, sw=2, dash="4,3"))
    p.append(text(130, 193, "Рівень 6 .. 14", size=10, color=FIELD))
    p.append(text(130, 215, "Рівень 15 (найнижчий)", size=10, color=FIELD, bold=True))
    p.append(text(130, 245, "Число менше → пріоритет вищий!", size=9.5, color=MUTED, italic=True))

    # Справа вгорі: Зона нульового джитеру (Високі апаратні пріоритети)
    p.append(rect(240, 70, 480, 92, fill=WARM, stroke=POS, sw=1.5, rx=6))
    p.append(text(480, 92, "Зона нульового джитеру (Пріоритети 0 .. MAX_SYSCALL - 1)", size=11, color=POS, bold=True))
    p.append(fitbox(250, 102, 460, 52,
                    "• Ніколи не маскуються ядром RTOS (BASEPRI їх не чіпає)\n"
                    "• Миттєвий відгук для керування моторами, ШІМ та аварійного захисту\n"
                    "• КАТЕГОРИЧНО ЗАБОРОНЕНО викликати будь-які функції RTOS FromISR!",
                    size=9.5, fill="#ffffff", stroke="#f5c6cb", bold=False))

    # Справа внизу: Зона взаємодії з RTOS (Безпечні рівні)
    p.append(rect(240, 175, 480, 95, fill=GRN, stroke=FIELD, sw=1.5, rx=6))
    p.append(text(480, 197, "Зона під керуванням RTOS (Пріоритети MAX_SYSCALL .. 15)", size=11, color=FIELD, bold=True))
    p.append(fitbox(250, 207, 460, 55,
                    "• Маскуються під час критичних секцій ядра (BASEPRI = MAX_SYSCALL)\n"
                    "• Мають невеликий джитер (тривалість критичної секції RTOS)\n"
                    "• ПОВНІСТЮ БЕЗПЕЧНО викликати функції xQueueSendFromISR тощо.",
                    size=9.5, fill="#ffffff", stroke="#c3e6cb", bold=False))

    # Нижня синтезна рамка
    p.append(fitbox(40, 285, 680, 58,
                    "Найчастіша фатальна помилка початківців: надати перериванню пріоритет 0 і викликати FromISR API.\n"
                    "Це призводить до хаотичного пошкодження черг RTOS через переривання критичної секції ядра.\n"
                    "Пам'ятайте: в ARM Cortex-M вищий пріоритет позначається МЕНШИМ числом!",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "interrupt-priority-matrix.svg"), W, H, *p)


if __name__ == "__main__":
    fig_handler_vs_thread()
    fig_blocking_in_isr_trap()
    fig_fromisr_mechanism()
    fig_pendsv_deferred_switch()
    fig_interrupt_priority_matrix()
    print("All figures generated successfully.")
