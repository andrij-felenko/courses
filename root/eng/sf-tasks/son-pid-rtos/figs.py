# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARM = "#fdecea"   # світла червона заливка (небезпека, помилка, виснаження)
COOL = "#eaf0fd"   # світла синя заливка (задача, логіка)
GRN  = "#eaf7ee"   # світла зелена заливка (енергозбереження, успіх)
GOLD = "#caa24a"   # бурштин / попередження
GBG  = "#fff7e6"   # світлий бурштин
PURP = "#f3e8fd"   # світлий фіолетовий

# ── 1. idle-task-loop: Анатомія та внутрішній цикл фонової задачі Idle Task ───
def fig_idle_task_loop():
    W, H = 760, 390
    p = []
    p.append(text(W/2, 26, "Анатомія та внутрішній цикл фонової задачі Idle Task", size=15, bold=True))
    p.append(text(W/2, 46, "звільнення пам'яті видалених задач, кооперативні поступки та перехід у стан сну",
                  size=11, color=MUTED, italic=True))

    steps = [
        ("1. Очищення пам'яті",
         "prvCheckTasksWaiting\nTermination()\n\n"
         "• Пошук у списку видалених\n"
         "• Виклик vPortFree(TCB)\n"
         "• Звільнення стеку задачі",
         COOL, NEG),
        ("2. Кооперація Yield",
         "configIDLE_SHOULD_YIELD\n\n"
         "• Якщо в Ready є інші задачі\n"
         "  з пріоритетом 0 (Idle):\n"
         "  виклик taskYIELD()\n"
         "• Рівний розподіл кванту",
         GBG, GOLD),
        ("3. Хук застосунку",
         "vApplicationIdleHook()\n\n"
         "• Скидання Watchdog\n"
         "• Підрахунок завантаження\n"
         "• Перевірка фонових CRC\n"
         "• СУВОРО БЕЗ БЛОКУВАНЬ",
         WARM, POS),
        ("4. Вибір режиму сну",
         "configUSE_TICKLESS_IDLE\n\n"
         "• Tickless = 1/2:\n"
         "  portSUPPRESS_TICKS()\n"
         "• Tickless = 0:\n"
         "  виконання __WFI() / __WFE()",
         GRN, FIELD)
    ]

    kw = 155
    gap = 25
    x0 = 30
    y0 = 75

    for i, (title, desc, bg_col, brd_col) in enumerate(steps):
        bx = x0 + i * (kw + gap)
        p.append(rect(bx, y0, kw, 215, fill=bg_col, stroke=brd_col, sw=1.5, rx=6))
        p.append(text(bx + kw/2, y0 + 24, title, size=11, color=brd_col, bold=True))
        p.append(line(bx + 10, y0 + 36, bx + kw - 10, y0 + 36, color=brd_col, sw=1))

        lines = desc.split("\n")
        for li, ln in enumerate(lines):
            p.append(text(bx + kw/2, y0 + 58 + li * 18, ln, size=9.5, color=INK))

        # Стрілка переходу між кроками циклу
        if i < 3:
            ax1 = bx + kw + 3
            ax2 = bx + kw + gap - 3
            ay = y0 + 105
            p.append(arrow(ax1, ay, ax2, ay, color=LINE, sw=1.8))

    # Зворотна дуга нескінченного циклу for(;;)
    p.append(line(640, y0 + 215, 640, y0 + 235, color=LINE, sw=1.5))
    p.append(line(640, y0 + 235, 105, y0 + 235, color=LINE, sw=1.5))
    p.append(arrow(105, y0 + 235, 105, y0 + 215, color=LINE, sw=1.5))
    p.append(text(380, y0 + 250, "Нескінченний цикл планувальника for(;;) — процесор ніколи не залишається без активної задачі",
                  size=10, color=MUTED, bold=True))

    # Нижня синтезна рамка
    p.append(fitbox(40, 310, 680, 65,
                    "Інваріант планувальника: Idle Task має пріоритет 0 і гарантує постійну наявність задачі для CPU.\n"
                    "Саме всередині Idle Task поєднуються очищення пам'яті видалених потоків, обслуговування фонових\n"
                    "хуків та занурення кристала в енергозберігаючий стан WFI або безтиковий сон Tickless Idle.",
                    size=10.5, fill=FILL, stroke=LINE, bold=False))

    render(os.path.join(OUT, "idle-task-loop.svg"), W, H, *p)


# ── 2. idle-memory-starvation: Механіка самовидалення та голодування Idle ───────
def fig_idle_memory_starvation():
    W, H = 760, 380
    p = []
    p.append(text(W/2, 26, "Самовидалення задач і пастка голодування Idle Task", size=15, bold=True))
    p.append(text(W/2, 46, "чому задача не може звільнити власний стек і як активні потоки викликають витік купи",
                  size=11, color=MUTED, italic=True))

    # Ліва колонка: Проблема самовидалення
    p.append(rect(35, 75, 335, 215, fill=WARM, stroke=POS, sw=1.5, rx=8))
    p.append(text(202.5, 98, "Небезпека: блокування очищення", size=12.5, color=POS, bold=True))
    p.append(fitbox(45, 115, 315, 160,
                    "1. Задача кличе vTaskDelete(NULL) для самоліквідації.\n"
                    "2. Задача НЕ може викликати free() для власного\n"
                    "   стеку, бо її код виконується прямо на цьому стеку!\n"
                    "3. Ядро поміщає TCB у список xTasksWaitingTermination.\n"
                    "4. Якщо задачі з пріоритетом >= 1 постійно працюють\n"
                    "   і не блокуються, Idle Task ніколи не отримає CPU.\n"
                    "5. Результат: безперервний витік RAM і падіння купи!",
                    size=10, fill="#ffffff", stroke="#f5c6cb", bold=False))

    # Права колонка: Коректне звільнення через Idle
    p.append(rect(390, 75, 335, 215, fill=GRN, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(557.5, 98, "Штатний процес звільнення пам'яті", size=12.5, color=FIELD, bold=True))
    p.append(fitbox(400, 115, 315, 160,
                    "1. Високорівневі задачі переходять у стан Blocked\n"
                    "   через vTaskDelay(), очікування семафора чи черги.\n"
                    "2. Планувальник перемикає контекст на Idle Task (пріоритет 0).\n"
                    "3. prvCheckTasksWaitingTermination() бере блоки зі списку.\n"
                    "4. Викликаються vPortFree(pxTCB->pxStack) та vPortFree(pxTCB).\n"
                    "5. Купа FreeRTOS повністю повертає виділену пам'ять.",
                    size=10, fill="#ffffff", stroke="#c3e6cb", bold=False))

    # Стрілка посередині
    p.append(arrow(370, 180, 390, 180, color=LINE, sw=1.5))

    # Нижня синтезна рамка
    p.append(fitbox(35, 305, 690, 60,
                    "Золоте правило архітектури FreeRTOS: якщо в системі динамічно створюються й видаляються задачі,\n"
                    "задачі високих пріоритетів обов'язково повинні періодично блокуватися. Голодування Idle Task\n"
                    "унеможливлює вивільнення TCB і стеків, перетворюючи завершені задачі на «зомбі-пам'ять».",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "idle-memory-starvation.svg"), W, H, *p)


# ── 3. sleep-modes-spectrum: Енергетичний спектр режимів мікроконтролера ──────
def fig_sleep_modes_spectrum():
    W, H = 760, 380
    p = []
    p.append(text(W/2, 26, "Спектр енергозберігаючих режимів та поведінка тактування", size=15, bold=True))
    p.append(text(W/2, 46, "порівняння струму споживання, активних генераторів, збереження SRAM та часу пробудження",
                  size=11, color=MUTED, italic=True))

    modes = [
        ("Активний режим (Run)", "80 МГц PLL / HSI / HSE\nВсі шини й периферія\nSRAM повністю активна\n12.0 – 20.0 мА\nЧас виходу: 0 мкс", COOL, NEG),
        ("Неглибокий сон (Sleep)", "Ядро зупинено (__WFI)\nSysTick та HCLK активні\nПериферія працює\n2.5 – 5.0 мА\nЧас виходу: < 1 мкс", GBG, GOLD),
        ("Глибокий сон (Stop 1/2)", "HCLK / PLL зупинено!\nLSE (32 кГц) + LPTIM активні\nSRAM збережена, I/O фіксовані\n1.2 – 2.0 мкА\nЧас виходу: 5 – 15 мкс", GRN, FIELD),
        ("Сплячий режим (Standby)", "Всі генератори OFF (крім RTC)\nЖивлення ядра знято\nSRAM втрачається (крім Backup)\n0.3 – 0.8 мкА\nЧас виходу: повний Reset", PURP, "#8e44ad")
    ]

    kw = 160
    gap = 18
    x0 = 30
    y0 = 75

    for i, (title, desc, bg_col, brd_col) in enumerate(modes):
        bx = x0 + i * (kw + gap)
        p.append(rect(bx, y0, kw, 210, fill=bg_col, stroke=brd_col, sw=1.5, rx=6))
        p.append(text(bx + kw/2, y0 + 22, title, size=10.5, color=brd_col, bold=True))
        p.append(line(bx + 8, y0 + 34, bx + kw - 8, y0 + 34, color=brd_col, sw=1))

        lines = desc.split("\n")
        labels = ["Тактування:", "Периферія:", "Пам'ять:", "Струм:", "Пробудження:"]
        for li, ln in enumerate(lines):
            p.append(text(bx + kw/2, y0 + 54 + li * 30, labels[li], size=9.5, color=MUTED))
            p.append(text(bx + kw/2, y0 + 68 + li * 30, ln, size=9.5, color=INK, bold=(li == 3)))

    # Нижня синтезна рамка
    p.append(fitbox(30, 300, 700, 65,
                    "Чому звичайний SysTick несумісний зі Stop Mode: таймер SysTick розташований у домені ядра\n"
                    "й живиться від шини HCLK. При вході в глибокий сон генератори HCLK зупиняються для зниження струму\n"
                    "до 1.5 мкА. Для відліку часу сну RTOS вимагає перемикання на автономний таймер LPTIM від кварцу LSE.",
                    size=10.5, fill=FILL, stroke=LINE, bold=False))

    render(os.path.join(OUT, "sleep-modes-spectrum.svg"), W, H, *p)


# ── 4. tickless-timing-sync: Синхронізація часу в режимі Tickless ─────────────
def fig_tickless_timing_sync():
    W, H = 760, 400
    p = []
    p.append(text(W/2, 26, "Синхронізація системного часу RTOS у режимі Tickless Idle", size=15, bold=True))
    p.append(text(W/2, 46, "компенсація тактів планувальника через vTaskStepTick() при плановому та асинхронному пробудженні",
                  size=11, color=MUTED, italic=True))

    # Сценарій 1: Планове пробудження (повний таймаут)
    y1 = 80
    p.append(text(35, y1, "Сценарій А: Планове пробудження за таймаутом LPTIM (сон N тактів)", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(line(40, y1 + 35, 710, y1 + 35, color=LINE, sw=1.5))
    p.append(arrow(690, y1 + 35, 715, y1 + 35, color=LINE, sw=1.5))

    # Блоки часу Сценарію 1
    p.append(rect(40, y1 + 15, 110, 42, fill=COOL, stroke=NEG, sw=1.2, rx=4))
    p.append(text(95, y1 + 40, "Idle: старт сну", size=10, color=NEG, bold=True))

    p.append(rect(155, y1 + 15, 380, 42, fill=GRN, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(345, y1 + 33, "Глибокий сон Stop 1 (LPTIM рахує N = 500 тактів)", size=10, color=FIELD, bold=True))
    p.append(text(345, y1 + 48, "SysTick зупинено • HCLK OFF • Споживання 1.5 мкА", size=9.5, color=MUTED))

    p.append(rect(540, y1 + 15, 160, 42, fill=GBG, stroke=GOLD, sw=1.2, rx=4))
    p.append(text(620, y1 + 33, "LPTIM IRQ: пробудження", size=9.5, color=GOLD, bold=True))
    p.append(text(620, y1 + 48, "vTaskStepTick(500)", size=9.5, color=INK))

    # Сценарій 2: Асинхронне передчасне пробудження
    y2 = 190
    p.append(text(35, y2, "Сценарій Б: Передчасне пробудження зовнішньою подією (EXTI / Датчик у момент M < N)", size=11, color=POS, bold=True, anchor="start"))
    p.append(line(40, y2 + 35, 710, y2 + 35, color=LINE, sw=1.5))
    p.append(arrow(690, y2 + 35, 715, y2 + 35, color=LINE, sw=1.5))

    # Блоки часу Сценарію 2
    p.append(rect(40, y2 + 15, 110, 42, fill=COOL, stroke=NEG, sw=1.2, rx=4))
    p.append(text(95, y2 + 40, "Idle: план N=500", size=10, color=NEG, bold=True))

    p.append(rect(155, y2 + 15, 210, 42, fill=GRN, stroke=FIELD, sw=1.2, rx=4))
    p.append(text(260, y2 + 33, "Сон Stop 1 (фактично M = 180 тактів)", size=9.5, color=FIELD, bold=True))
    p.append(text(260, y2 + 48, "Перервано подією EXTI GPIO", size=9.5, color=MUTED))

    p.append(rect(370, y2 + 15, 175, 42, fill=WARM, stroke=POS, sw=1.2, rx=4))
    p.append(text(457.5, y2 + 33, "EXTI IRQ: ядро прокинулося", size=9.5, color=POS, bold=True))
    p.append(text(457.5, y2 + 48, "Зчитування CNT → vTaskStepTick(180)", size=9.5, color=INK))

    p.append(rect(550, y2 + 15, 150, 42, fill=COOL, stroke=NEG, sw=1.2, rx=4))
    p.append(text(625, y2 + 33, "Обробка задачі давача", size=9.5, color=NEG, bold=True))
    p.append(text(625, y2 + 48, "SysTick відновлено", size=9.5, color=MUTED))

    # Нижня синтезна рамка
    p.append(fitbox(35, 295, 690, 85,
                    "Механізм vTaskStepTick() гарантує монотонність і точність системного часу:\n"
                    "при передчасному пробудженні хук зчитує поточний стан лічильника LPTIM, розраховує фактично\n"
                    "прожиті такти, передає їх планувальнику для оновлення черг таймаутів і перезапускає SysTick.\n"
                    "Завдяки цьому жодна затримка не спрацьовує завчасно, а системний час не збивається.",
                    size=10.5, fill=FILL, stroke=LINE, bold=False))

    render(os.path.join(OUT, "tickless-timing-sync.svg"), W, H, *p)


if __name__ == "__main__":
    fig_idle_task_loop()
    fig_idle_memory_starvation()
    fig_sleep_modes_spectrum()
    fig_tickless_timing_sync()
    print("All figures for son-pid-rtos generated successfully.")
