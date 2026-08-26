# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARM = "#fdecea"   # світла тепла заливка
COOL = "#eaf0fd"   # світла холодна заливка
GRN  = "#eaf7ee"   # світла зелена заливка
GOLD = "#caa24a"   # бурштин / попередження
GBG  = "#fff7e6"   # світлий бурштин


# ── 1. cfs-vs-fpps-scheduling: Планування CFS проти FPPS ───────────────────────
def fig_cfs_vs_fpps():
    W, H = 840, 440
    p = []
    p.append(text(W/2, 28, "Цілі планування: справедливий розподіл (CFS) проти суворого витіснення (FPPS)", size=15, bold=True))
    p.append(text(W/2, 48, "Linux CFS мінімізує нерівність vruntime; RTOS FPPS завжди віддає CPU найвищому пріоритету", size=11, color=MUTED, italic=True))

    # Ліва панель: Linux CFS (Red-Black Tree)
    p.append(rect(30, 68, 375, 305, fill=COOL, stroke=NEG, sw=1.5, rx=8))
    p.append(text(217, 92, "Linux CFS (Completely Fair Scheduler)", size=13, color=NEG, bold=True))
    p.append(text(217, 110, "Оптимізація: пропускна здатність і чесність", size=10, color=MUTED, italic=True))

    # Спрощене дерево Червоно-Чорне
    p.append(rect(162, 128, 110, 30, fill=BG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(217, 147, "vruntime = 142 ms", size=10, bold=True))

    # Гілки
    p.append(line(180, 158, 115, 188, color=NEG, sw=1.2))
    p.append(line(255, 158, 320, 188, color=NEG, sw=1.2))

    # Лівий вузол (найменший vruntime - наступний на виконання)
    p.append(rect(55, 188, 120, 42, fill=GRN, stroke=FIELD, sw=1.6, rx=4))
    p.append(text(115, 206, "Потік A (лівий)", size=10, color=FIELD, bold=True))
    p.append(text(115, 221, "vruntime = 98 ms (RUN)", size=9, color=INK))

    # Правий вузол
    p.append(rect(260, 188, 120, 42, fill=BG, stroke=NEG, sw=1.2, rx=4))
    p.append(text(320, 206, "Потік C (правий)", size=10, bold=True))
    p.append(text(320, 221, "vruntime = 195 ms", size=9, color=MUTED))

    p.append(fitbox(45, 246, 345, 112,
                    "• Квант часу розраховується динамічно (sched_latency).\n"
                    "• Кожен потік отримує частку CPU згідно зі своєю вагою (nice).\n"
                    "• Потік, що прокинувся, не витісняє поточний миттєво,\n"
                    "  якщо різниця vruntime менша за поріг гранулярності.\n"
                    "• Орієнтація на інтерактивність та утилізацію ядер.",
                    size=10, fill=BG, stroke=NEG))

    # Права панель: RTOS FPPS (Priority Bitmap)
    p.append(rect(435, 68, 375, 305, fill=GRN, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(622, 92, "RTOS FPPS (Fixed-Priority Preemptive)", size=13, color=FIELD, bold=True))
    p.append(text(622, 110, "Оптимізація: детермінований дедлайн і своєчасність", size=10, color=MUTED, italic=True))

    # Бітова маска пріоритетів
    p.append(text(622, 134, "Ready Bitmap (32 біти пріоритетів):", size=10, bold=True))
    bx = 455
    p.append(rect(bx, 146, 335, 36, fill=BG, stroke=FIELD, sw=1.2, rx=4))
    for i in range(8):
        cx = bx + i * 42
        bit_val = "1" if i == 2 or i == 5 else "0"
        bg_col = WARM if i == 2 else (COOL if i == 5 else BG)
        txt_col = POS if i == 2 else (NEG if i == 5 else MUTED)
        p.append(rect(cx + 2, 148, 38, 32, fill=bg_col, stroke=MUTED, sw=0.6, rx=2))
        p.append(text(cx + 21, 161, "P%d" % (7 - i), size=9, color=MUTED))
        p.append(text(cx + 21, 174, bit_val, size=11, color=txt_col, bold=True))

    p.append(text(622, 201, "Пошук за 1 такт: CLZ (Count Leading Zeros) = O(1)", size=10, color=FIELD, bold=True))
    p.append(text(622, 218, "P5 готова → негайне витіснення поточної P2", size=10, color=POS, bold=True))

    p.append(fitbox(450, 235, 345, 124,
                    "• Абсолютне право витіснення: вищий пріоритет завжди біжить.\n"
                    "• Немає поділу часу між нерівними пріоритетами.\n"
                    "• Затримка старту задачі P5 строго детермінована й дорівнює\n"
                    "  часу перемикання контексту (WCET відомий наперед).\n"
                    "• Низькі пріоритети голодують, доки високі мають роботу.",
                    size=10, fill=BG, stroke=FIELD))

    # Загальний підсумок
    p.append(fitbox(30, 385, 780, 44,
                    "Висновок: CFS гарантує справедливість і пропускну здатність, але не дає детермінізму дедлайнів.\n"
                    "FPPS гарантує своєчасність критичної задачі, свідомо жертвуючи чесністю щодо решти задач.",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "cfs-vs-fpps-scheduling.svg"), W, H, *p)


# ── 2. context-switch-cost-anatomy: Анатомія перемикання контексту ─────────────
def fig_context_switch_anatomy():
    W, H = 840, 480
    p = []
    p.append(text(W/2, 28, "Анатомія перемикання контексту: Linux (GPOS) проти FreeRTOS (MCU)", size=15, bold=True))
    p.append(text(W/2, 48, "Linux виконує зміну простору адрес і скидання кешів; RTOS змінює лише кілька слів у RAM", size=11, color=MUTED, italic=True))

    # Ліва колонка: Linux Kernel Context Switch
    p.append(rect(30, 68, 375, 345, fill=COOL, stroke=NEG, sw=1.5, rx=8))
    p.append(text(217, 92, "Linux на x86-64 / ARM64 (GPOS)", size=13, color=NEG, bold=True))
    p.append(text(217, 110, "Типовий час: 1.5 – 10+ мкс (залежно від кешу)", size=10, color=POS, bold=True))

    steps_linux = [
        ("1. Перехід у ядро (Syscall / Timer IRQ)", "Зміна рівня привілеїв: User Space (Ring 3) → Kernel (Ring 0)"),
        ("2. Збереження регістрів у стек ядра", "push rax..r15, rsp, rip, rflags, оновлення структури TSS"),
        ("3. Виклик __schedule() та CFS", "Балансування дерева vruntime, вибір наступної task_struct"),
        ("4. Зміна віртуальної пам'яті (switch_mm)", "Запис нового значення в регістр CR3 (Page Table Base)"),
        ("5. Інвалідація TLB / зміна ASID", "Очищення або тегування буфера трансляції адрес (TLB)"),
        ("6. Відновлення регістрів і sysret/iret", "Холодний L1/L2 кеш: промахи під час читання нового коду")
    ]

    for i, (title, desc) in enumerate(steps_linux):
        sy = 125 + i * 38
        p.append(rect(45, sy, 345, 34, fill=BG, stroke=NEG, sw=0.8, rx=4))
        p.append(text(55, sy + 13, title, size=9.5, bold=True, anchor="start", color=NEG))
        p.append(text(55, sy + 26, desc, size=9, color=MUTED, anchor="start"))

    p.append(text(217, 370, "Витрати: MMU, зміна сторінок, промахи кешу пам'яті", size=9.5, color=POS, bold=True))
    p.append(text(217, 390, "Затримка залежить від стану кешу та розміру робочого набору", size=9, color=MUTED, italic=True))

    # Права колонка: RTOS Cortex-M Context Switch
    p.append(rect(435, 68, 375, 345, fill=GRN, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(622, 92, "FreeRTOS на ARM Cortex-M (RTOS)", size=13, color=FIELD, bold=True))
    p.append(text(622, 110, "Типовий час: 0.12 – 0.5 мкс (12 – 50 тактів)", size=10, color=FIELD, bold=True))

    steps_rtos = [
        ("1. Апаратне автозбереження (Cortex-M)", "Процесор сам кладе в стек задачі (PSP): R0-R3, R12, LR, PC, xPSR"),
        ("2. Виклик виключення PendSV", "PendSV має найнижчий пріоритет переривання (не блокує ISR)"),
        ("3. Програмне збереження решти регістрів", "Асемблерна інструкція: stmdb r0!, {r4-r11, r14}"),
        ("4. Зміна вказівника TCB у пам'яті", "pxCurrentTCB->pxTopOfStack = PSP; pxCurrentTCB = pxNewTCB;"),
        ("5. Програмне відновлення регістрів", "Асемблерна інструкція: ldmia r0!, {r4-r11, r14}"),
        ("6. Апаратне повернення (bx lr)", "Апаратний вихід: відновлення R0-R3/PC, жодного MMU/TLB")
    ]

    for i, (title, desc) in enumerate(steps_rtos):
        sy = 125 + i * 38
        p.append(rect(450, sy, 345, 34, fill=BG, stroke=FIELD, sw=0.8, rx=4))
        p.append(text(460, sy + 13, title, size=9.5, bold=True, anchor="start", color=FIELD))
        p.append(text(460, sy + 26, desc, size=9, color=MUTED, anchor="start"))

    p.append(text(622, 370, "Витрати: лише читання/запис 16 слів RAM (Cortex-M)", size=9.5, color=FIELD, bold=True))
    p.append(text(622, 390, "Єдиний плоский адресний простір, детермінований час", size=9, color=MUTED, italic=True))

    # Нижній банер
    p.append(fitbox(30, 424, 780, 44,
                    "Ключова різниця: у Linux вартість перемикання недетермінована через кеш і MMU.\n"
                    "В RTOS перемикання є строго фіксованою за часом послідовністю інструкцій збереження в RAM.",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "context-switch-cost-anatomy.svg"), W, H, *p)


# ── 3. stack-memory-model-comparison: Моделі виділення пам'яті під стек ────────
def fig_stack_memory_model():
    W, H = 840, 450
    p = []
    p.append(text(W/2, 28, "Модель виділення стека: динамічний ріст у GPOS проти статичного буфера в RTOS", size=15, bold=True))
    p.append(text(W/2, 48, "Віртуальна пам'ять приховує сторінкові збої (Page Faults); мікроконтролер вимагає точного розрахунку RAM", size=11, color=MUTED, italic=True))

    # Ліва панель: GPOS Virtual Memory Stack
    p.append(rect(30, 68, 375, 315, fill=COOL, stroke=NEG, sw=1.5, rx=8))
    p.append(text(217, 92, "GPOS: Віртуальний стек (8 МБ)", size=12.5, color=NEG, bold=True))

    # Стек GPOS схема
    p.append(rect(130, 115, 175, 30, fill=BG, stroke=NEG, sw=1, rx=3))
    p.append(text(217, 134, "Верхівка стека (RSP)", size=9.5, bold=True))

    p.append(rect(130, 148, 175, 36, fill=GRN, stroke=FIELD, sw=1, rx=3))
    p.append(text(217, 163, "Фізична сторінка 4 КБ", size=9.5, color=FIELD, bold=True))
    p.append(text(217, 176, "Виділена в RAM", size=9, color=MUTED))

    p.append(rect(130, 187, 175, 36, fill=WARM, stroke=POS, sw=1, rx=3))
    p.append(text(217, 202, "Нова сторінка (Немає в RAM)", size=9.5, color=POS, bold=True))
    p.append(text(217, 215, "Дотик → PAGE FAULT (10-100 мкс)", size=9, color=POS, bold=True))

    p.append(rect(130, 226, 175, 26, fill=FILL, stroke=MUTED, sw=0.8, rx=3))
    p.append(text(217, 243, "Невідображений віртуальний простір", size=9, color=MUTED))

    p.append(rect(130, 255, 175, 26, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text(217, 272, "Guard Page (PROT_NONE) → SIGSEGV", size=9, color=POS, bold=True))

    p.append(fitbox(45, 288, 345, 84,
                    "• Виділяється віртуальний діапазон (VMA), фізична пам'ять не резервується.\n"
                    "• Перший запис у нову 4 КБ сторінку викликає Page Fault у ядрі.\n"
                    "• Витрати на Page Fault дають раптові сплески затримки на мікросекунди.\n"
                    "• Вихід за межі стека ловиться захисною сторінкою (Guard Page).",
                    size=9.5, fill=BG, stroke=NEG))

    # Права панель: RTOS Static Stack Buffer
    p.append(rect(435, 68, 375, 315, fill=GRN, stroke=FIELD, sw=1.5, rx=8))
    p.append(text(622, 92, "RTOS: Фіксований буфер RAM (1 – 4 КБ)", size=12.5, color=FIELD, bold=True))

    # Стек RTOS схема
    p.append(rect(535, 115, 175, 30, fill=BG, stroke=FIELD, sw=1, rx=3))
    p.append(text(622, 134, "Початок буфера (Висока адреса)", size=9.5, bold=True))

    p.append(rect(535, 148, 175, 42, fill=COOL, stroke=NEG, sw=1, rx=3))
    p.append(text(622, 165, "Використаний стек (PSP)", size=9.5, color=NEG, bold=True))
    p.append(text(622, 179, "Локальні змінні + фрейми функцій", size=9, color=MUTED))

    p.append(rect(535, 193, 175, 42, fill=GBG, stroke=GOLD, sw=1, rx=3))
    p.append(text(622, 210, "Водяний знак (Watermark)", size=9.5, color=GOLD, bold=True))
    p.append(text(622, 224, "Заповнено шаблоном 0xA5A5A5A5", size=9, color=INK))

    p.append(rect(535, 238, 175, 38, fill=WARM, stroke=POS, sw=1.2, rx=3))
    p.append(text(622, 253, "Низ буфера / Чужі змінні TCB", size=9.5, color=POS, bold=True))
    p.append(text(622, 267, "Переповнення = руйнування пам'яті!", size=9, color=POS, bold=True))

    p.append(fitbox(450, 288, 345, 84,
                    "• Вся пам'ять стека виділяється заздалегідь (масив StackType_t у RAM).\n"
                    "• Жодних сторінкових збоїв — час доступу до стека строго детермінований.\n"
                    "• Небезпека: якщо стек переповниться, пошкоджуються сусідні дані TCB.\n"
                    "• Контроль: перевірка Watermark планувальником або MPU HardFault.",
                    size=9.5, fill=BG, stroke=FIELD))

    # Нижній висновок
    p.append(fitbox(30, 394, 780, 44,
                    "Підсумок: GPOS забезпечує гнучкість за рахунок динамізму та непередбачуваних Page Faults.\n"
                    "RTOS забезпечує нульовий джитер доступу, вимагаючи ретельного статичного аудиту розміру стека.",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "stack-memory-model-comparison.svg"), W, H, *p)


# ── 4. priority-inversion-mechanisms: Протоколи боротьби з інверсією ───────────
def fig_priority_inversion():
    W, H = 840, 450
    p = []
    p.append(text(W/2, 28, "Інверсія пріоритетів: протокол успадкування (PIP) проти стелі пріоритетів (PCP)", size=15, bold=True))
    p.append(text(W/2, 48, "Як RTOS запобігає блокуванню критичної задачі через проміжні фонові потоки", size=11, color=MUTED, italic=True))

    # 1. Некерована інверсія (Unbounded Inversion)
    p.append(rect(30, 68, 250, 310, fill=WARM, stroke=POS, sw=1.4, rx=6))
    p.append(text(155, 88, "1. Без протоколу (Катастрофа)", size=11.5, color=POS, bold=True))
    p.append(text(155, 105, "Необмежене блокування", size=9.5, color=MUTED, italic=True))

    p.append(rect(42, 118, 226, 30, fill=BG, stroke=MUTED, sw=0.8, rx=3))
    p.append(text(155, 137, "Низька (L) захоплює м'ютекс M", size=9.5, bold=True))

    p.append(rect(42, 153, 226, 30, fill=BG, stroke=POS, sw=1, rx=3))
    p.append(text(155, 172, "Висока (H) блокується на M", size=9.5, color=POS, bold=True))

    p.append(rect(42, 188, 226, 40, fill=WARM, stroke=POS, sw=1.2, rx=3))
    p.append(text(155, 204, "Середня (M) витісняє L!", size=9.5, color=POS, bold=True))
    p.append(text(155, 218, "(M не потрібен замок, але він біжить)", size=9, color=MUTED))

    p.append(fitbox(42, 236, 226, 130,
                    "Результат: High чекає\n"
                    "завершення Medium, хоча\n"
                    "Medium має нижчий пріоритет!\n"
                    "Затримка High стає\n"
                    "необмеженою (Unbounded).\n"
                    "Причина збою Mars Pathfinder\n"
                    "у 1997 році на Марсі.",
                    size=9.5, fill=BG, stroke=POS))

    # 2. Успадкування пріоритету (Priority Inheritance, PIP)
    p.append(rect(295, 68, 250, 310, fill=COOL, stroke=NEG, sw=1.4, rx=6))
    p.append(text(420, 88, "2. Успадкування (PIP / FreeRTOS)", size=11.5, color=NEG, bold=True))
    p.append(text(420, 105, "Динамічне підняття пріоритету", size=9.5, color=MUTED, italic=True))

    p.append(rect(307, 118, 226, 30, fill=BG, stroke=MUTED, sw=0.8, rx=3))
    p.append(text(420, 137, "Низька (L) захоплює м'ютекс M", size=9.5, bold=True))

    p.append(rect(307, 153, 226, 32, fill=BG, stroke=NEG, sw=1, rx=3))
    p.append(text(420, 168, "High блокується на M →", size=9.5, color=NEG, bold=True))
    p.append(text(420, 180, "L тимчасово дістає пріоритет High", size=9, color=NEG, bold=True))

    p.append(rect(307, 190, 226, 38, fill=GRN, stroke=FIELD, sw=1.2, rx=3))
    p.append(text(420, 205, "Medium НЕ може витіснити L!", size=9.5, color=FIELD, bold=True))
    p.append(text(420, 219, "L швидко добігає і віддає M", size=9, color=INK))

    p.append(fitbox(307, 236, 226, 130,
                    "Результат: Затримка High\n"
                    "обмежена тривалістю\n"
                    "критичної секції Low.\n"
                    "Особливість:\n"
                    "• Динамічна зміна черг планувальника\n"
                    "• Можливе ланцюгове блокування\n"
                    "  за наявності декількох замків.",
                    size=9.5, fill=BG, stroke=NEG))

    # 3. Стеля пріоритетів (Priority Ceiling, PCP / IPCP)
    p.append(rect(560, 68, 250, 310, fill=GRN, stroke=FIELD, sw=1.4, rx=6))
    p.append(text(685, 88, "3. Стеля пріоритетів (PCP / Zephyr)", size=11.5, color=FIELD, bold=True))
    p.append(text(685, 105, "Статична верхня межа замка", size=9.5, color=MUTED, italic=True))

    p.append(rect(572, 118, 226, 32, fill=BG, stroke=FIELD, sw=1, rx=3))
    p.append(text(685, 133, "М'ютекс має фіксовану стелю", size=9.5, color=FIELD, bold=True))
    p.append(text(685, 145, "Ceiling = max(пріоритети задач)", size=9, color=MUTED))

    p.append(rect(572, 153, 226, 32, fill=BG, stroke=FIELD, sw=1, rx=3))
    p.append(text(685, 168, "L захоплює M → пріоритет L", size=9.5, bold=True))
    p.append(text(685, 180, "миттєво стає рівним Ceiling!", size=9, color=FIELD, bold=True))

    p.append(rect(572, 190, 226, 38, fill=GRN, stroke=FIELD, sw=1.2, rx=3))
    p.append(text(685, 205, "Жодна задача не витісняє L", size=9.5, color=FIELD, bold=True))
    p.append(text(685, 219, "Deadlock неможливий математично", size=9, color=INK))

    p.append(fitbox(572, 236, 226, 130,
                    "Результат: Найсуворіший захист.\n"
                    "• Задача блокується щонайбільше\n"
                    "  один раз за весь час виконання.\n"
                    "• Повне усунення взаємних\n"
                    "  блокувань (Deadlock).\n"
                    "• Проста реалізація без динаміки.",
                    size=9.5, fill=BG, stroke=FIELD))

    # Нижній висновок
    p.append(fitbox(30, 388, 780, 50,
                    "Висновок: Без захисту пріоритет втрачає сенс через втручання фонових задач середнього рівня.\n"
                    "PIP вирішує проблему реактивно в момент конфлікту; PCP запобігає затримкам превентивно.",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "priority-inversion-protocols.svg"), W, H, *p)


# ── 5. latency-jitter-distribution: Розподіл джитеру затримок ──────────────────
def fig_jitter_distribution():
    W, H = 820, 400
    p = []
    p.append(text(W/2, 28, "Розподіл затримки реакції: GPOS проти RTOS під навантаженням", size=15, bold=True))
    p.append(text(W/2, 48, "RTOS дає вузький детермінований пік (WCET відомий); GPOS має «довгий хвіст» випадкових затримок", size=11, color=MUTED, italic=True))

    # Вісь координат
    bx, by = 85, 280
    w_ax, h_ax = 670, 200
    p.append(line(bx, by, bx + w_ax, by, color=INK, sw=1.5))
    p.append(line(bx, by, bx, by - h_ax, color=INK, sw=1.5))
    p.append(text(bx + w_ax - 10, by + 24, "Час реакції на подію (затримка, логарифмічний масштаб) →", size=10, bold=True, anchor="end"))
    p.append(text(bx - 12, by - h_ax + 15, "Ймовірність", size=10, bold=True, anchor="middle"))

    # Позначки осі X
    ticks = [(bx + 50, "1 мкс"), (bx + 160, "10 мкс"), (bx + 290, "100 мкс"), (bx + 430, "1 мс"), (bx + 580, "10 мс")]
    for tx, lbl in ticks:
        p.append(line(tx, by, tx, by + 5, color=MUTED, sw=1))
        p.append(text(tx, by + 18, lbl, size=9.5, color=MUTED))

    # Крива RTOS (Вузький дельта-пік біля 2..5 мкс)
    rtos_poly = [(bx + 40, by), (bx + 55, by - 165), (bx + 68, by - 170), (bx + 80, by - 165), (bx + 95, by)]
    pts_str = " ".join(["%.1f,%.1f" % pt for pt in rtos_poly])
    p.append(f'<polygon points="{pts_str}" fill="{GRN}" stroke="{FIELD}" stroke-width="2"/>')
    p.append(text(bx + 68, by - 178, "RTOS (FreeRTOS / Zephyr)", size=10.5, color=FIELD, bold=True))
    p.append(text(bx + 68, by - 145, "Джитер < 1 мкс", size=9.5, color=FIELD, bold=True))

    # WCET RTOS вертикальна лінія
    p.append(line(bx + 115, by - 180, bx + 115, by, color=FIELD, sw=1.5, dash="4,2"))
    p.append(text(bx + 120, by - 110, "Гарантований WCET RTOS (12 мкс)", size=9.5, color=FIELD, bold=True, anchor="start"))

    # Крива GPOS (Широкий гаусів купол + довгий важкий хвіст праворуч)
    gpos_pts = [
        (bx + 120, by),
        (bx + 180, by - 25),
        (bx + 260, by - 85),
        (bx + 310, by - 95),
        (bx + 370, by - 80),
        (bx + 430, by - 45),
        (bx + 500, by - 25),
        (bx + 580, by - 15),
        (bx + 630, by - 4),
        (bx + 640, by)
    ]
    pts_gpos = " ".join(["%.1f,%.1f" % pt for pt in gpos_pts])
    p.append(f'<polygon points="{pts_gpos}" fill="{COOL}" stroke="{NEG}" stroke-width="2"/>')
    p.append(text(bx + 320, by - 105, "GPOS (Звичайний Linux)", size=10.5, color=NEG, bold=True))
    p.append(text(bx + 320, by - 65, "Середній час: 60 мкс", size=9.5, color=NEG))

    # «Хвіст» GPOS
    p.append(rect(bx + 480, by - 45, 155, 28, fill=WARM, stroke=POS, sw=1, rx=3))
    p.append(text(bx + 557, by - 27, "«Довгий хвіст»: сплески до 15 мс!", size=9, color=POS, bold=True))

    # Лінія Дедлайну системи
    dl_x = bx + 360
    p.append(line(dl_x, by - 180, dl_x, by, color=POS, sw=2, dash="5,3"))
    p.append(text(dl_x, by - 188, "ЖОРСТКИЙ ДЕДЛАЙН (250 мкс)", size=9.5, color=POS, bold=True))

    # Підсумкова плашка
    p.append(fitbox(30, 335, 760, 50,
                    "• RTOS: весь розподіл лежить строго лівіше дедлайну — система на 100% передбачувана.\n"
                    "• GPOS: попри високий середній темп, випадкові сплески перетинають дедлайн, спричиняючи відмову.",
                    size=10.5, fill=GBG, stroke=GOLD, bold=True))

    render(os.path.join(OUT, "latency-jitter-distribution.svg"), W, H, *p)


if __name__ == "__main__":
    fig_cfs_vs_fpps()
    fig_context_switch_anatomy()
    fig_stack_memory_model()
    fig_priority_inversion()
    fig_jitter_distribution()
    print("All figures generated successfully.")
