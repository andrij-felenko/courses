# -*- coding: utf-8 -*-
"""Фігури до теми «Super-loop чи RTOS: вибір архітектури прошивки».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Порівняння часових шкалів: Super-loop vs RTOS ──────────────────────────
def fig_superloop_vs_rtos_timeline():
    W, H = 880, 500
    f = [text(W / 2, 28, "Порівняння часової поведінки: кооперативний Super-loop проти витіснення в RTOS",
              size=15, bold=True)]

    # Загальні підписи осей
    f.append(text(60, 70, "Super-loop", size=13, bold=True, color=POS, anchor="start"))
    f.append(text(60, 88, "(кооперативне виконання)", size=10, italic=True, color=MUTED, anchor="start"))

    # Часова вісь 1
    y1 = 150

    # Дедлайни гіроскопа (пунктир вгорі та внизу, не перетинаючи прямокутники)
    for x_dl, label in [(160, "Дедлайн 1 (125 мкс)"), (400, "Дедлайн 2 (250 мкс)"), (720, "Дедлайн 3 (375 мкс)")]:
        f.append(line(x_dl, y1 - 42, x_dl, y1 - 26, color=POS, sw=1.2, dash="3,3"))
        f.append(line(x_dl, y1 + 21, x_dl, y1 + 45, color=POS, sw=1.2, dash="3,3"))
        f.append(text(x_dl, y1 - 48, label, size=9.5, color=POS))

    # Блоки в Super-loop
    # Задача 1: Гіроскоп + PID (60 мкс)
    f.append(rect(160, y1 - 24, 110, 44, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    f.append(text(215, y1 + 3, "Гіро + PID (60 мкс)", size=10, bold=True, color=NEG))

    # Задача 2: Телеметрія MAVLink (80 мкс)
    f.append(rect(275, y1 - 24, 75, 44, fill="#fdf0e6", stroke=POS, sw=1.5, rx=4))
    f.append(text(312, y1 + 3, "MAVLink", size=10, color=INK))

    # Задача 3: Запис у Flash-пам'ять (довгий неблокуючий або блокуючий крок - 220 мкс)
    f.append(rect(355, y1 - 24, 230, 44, fill="#fdecea", stroke=POS, sw=2.0, rx=4))
    f.append(text(470, y1 - 6, "Запис Flash (220 мкс)", size=10.5, bold=True, color=POS))
    f.append(text(470, y1 + 12, "затримує виконання наступного циклу", size=9.5, italic=True, color=POS))

    # Задача 1 пропущена / затримана!
    f.append(rect(590, y1 - 24, 110, 44, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    f.append(text(645, y1 - 6, "Гіро + PID", size=10, bold=True, color=NEG))
    f.append(text(645, y1 + 12, "(з запізненням)", size=9.5, italic=True, color=NEG))

    f.append(arrow(60, y1 + 30, 830, y1 + 30, color=LINE, sw=1.8))
    f.append(text(830, y1 + 48, "час t", size=11, color=MUTED, anchor="end"))

    # Джиттер стрілка
    f.append(line(400, y1 + 65, 590, y1 + 65, color=POS, sw=1.5))
    f.append(line(400, y1 + 58, 400, y1 + 72, color=POS, sw=1.5))
    f.append(line(590, y1 + 58, 590, y1 + 72, color=POS, sw=1.5))
    f.append(text(495, y1 + 82, "Джиттер: запізнення на 190 мкс (пропуск дедлайну)", size=10, bold=True, color=POS))


    # RTOS секція нижче
    y2 = 330
    f.append(text(60, y2 - 55, "Витісняльна RTOS", size=13, bold=True, color=FIELD, anchor="start"))
    f.append(text(60, y2 - 37, "(пріоритетне витіснення)", size=10, italic=True, color=MUTED, anchor="start"))

    # Дедлайни гіроскопа (пунктир вгорі та внизу)
    for x_dl, label in [(160, "Дедлайн 1 (125 мкс)"), (400, "Дедлайн 2 (250 мкс)"), (640, "Дедлайн 3 (375 мкс)")]:
        f.append(line(x_dl, y2 - 42, x_dl, y2 - 26, color=FIELD, sw=1.2, dash="3,3"))
        f.append(line(x_dl, y2 + 21, x_dl, y2 + 45, color=FIELD, sw=1.2, dash="3,3"))
        f.append(text(x_dl, y2 - 48, label, size=9.5, color=FIELD))

    # Високопріоритетна задача Гіро + PID
    f.append(rect(160, y2 - 24, 110, 44, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    f.append(text(215, y2 + 3, "Гіро + PID (пріор. 10)", size=9.5, bold=True, color=NEG))

    # Низькопріоритетний Flash починається
    f.append(rect(275, y2 - 24, 120, 44, fill="#fdf0e6", stroke=POS, sw=1.5, rx=4))
    f.append(text(335, y2 + 3, "Flash (пріор. 2)", size=9.5, color=INK))

    # Витіснення в точці 400 мкс!
    f.append(rect(400, y2 - 24, 110, 44, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    f.append(text(455, y2 - 6, "Гіро + PID", size=10, bold=True, color=NEG))
    f.append(text(455, y2 + 12, "витісняє Flash!", size=9.5, bold=True, color=FIELD))

    # Flash продовжується після витіснення
    f.append(rect(515, y2 - 24, 110, 44, fill="#fdf0e6", stroke=POS, sw=1.5, rx=4))
    f.append(text(570, y2 + 3, "Flash (продовження)", size=9.5, color=INK))

    # Наступний цикл Гіро + PID точно в 640 мкс
    f.append(rect(640, y2 - 24, 110, 44, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=4))
    f.append(text(695, y2 + 3, "Гіро + PID", size=10, bold=True, color=NEG))

    # Часова вісь 2
    f.append(arrow(60, y2 + 30, 830, y2 + 30, color=LINE, sw=1.8))
    f.append(text(830, y2 + 48, "час t", size=11, color=MUTED, anchor="end"))

    # Підпис детермінізму
    f.append(text(455, y2 + 75, "Детермінізм RTOS: швидке перемикання контексту (~2 мкс), дедлайн витримано строго",
                  size=10.5, bold=True, color=FIELD))

    # Виноска внизу
    b, _, _ = textbox(W / 2, H - 28,
                      "Super-loop не може витіснити повільну функцію — виникає джиттер стабілізації.\n"
                      "RTOS негайно віддає ядро високопріоритетній задачі керування польотом.",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "superloop-vs-rtos-timeline.svg"), W, H, *f)


# ── 2. Механіка перемикання контексту ARM Cortex-M ────────────────────────────
def fig_context_switch_arm_stack():
    W, H = 880, 520
    f = [text(W / 2, 28, "Перемикання контексту в ARM Cortex-M: апаратний та програмний стек",
              size=15, bold=True)]

    # Ліва колонка: Задача A (Task A Stack - PSP_A)
    x1 = 90
    w_col = 220
    f.append(rect(x1, 65, w_col, 370, fill="#f9fafb", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x1 + w_col / 2, 90, "Стек Задачі A (PSP_A)", size=12, bold=True, color=NEG))

    # Апаратний фрейм (зберігає процесор автоматично)
    f.append(rect(x1 + 15, 115, w_col - 30, 140, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    f.append(text(x1 + w_col / 2, 135, "Апаратне збереження", size=10.5, bold=True, color=NEG))
    regs_hw = ["xPSR", "PC (Return Address)", "LR (R14)", "R12, R3, R2, R1, R0"]
    for i, r_name in enumerate(regs_hw):
        f.append(text(x1 + 25, 160 + i * 22, r_name, size=9.5, color=INK, anchor="start"))

    # Програмний фрейм (зберігає PendSV у FreeRTOS)
    f.append(rect(x1 + 15, 265, w_col - 30, 140, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(x1 + w_col / 2, 285, "Програмне збереження (PendSV)", size=10, bold=True, color=FIELD))
    regs_sw = ["R11, R10, R9, R8", "R7, R6, R5, R4", "stmdb r0!, {r4-r11}", "Вершина стека SP -> TCB_A"]
    for i, r_name in enumerate(regs_sw):
        f.append(text(x1 + 25, 310 + i * 22, r_name, size=9.5, color=INK, anchor="start"))


    # Центральний блок: Ядро планувальника (PendSV_Handler & TCB)
    cx = 360
    cw = 170
    f.append(rect(cx, 130, cw, 240, fill="#fdf0e6", stroke=POS, sw=2.0, rx=8))
    f.append(text(cx + cw / 2, 155, "Планувальник (PendSV)", size=11, bold=True, color=POS))

    tcb_items = [
        "1. Зберегти PSP_A",
        "2. current_tcb = next",
        "3. Відновити PSP_B",
        "4. ldmia r0!, {r4-r11}",
        "5. bx EXC_RETURN",
        "   (0xFFFFFFFD)"
    ]
    for i, t_text in enumerate(tcb_items):
        f.append(text(cx + 12, 185 + i * 26, t_text, size=9.5, color=INK, anchor="start"))

    # Стрілки перемикання
    f.append(arrow(x1 + w_col, 370, cx, 230, color=NEG, sw=1.8))
    f.append(arrow(cx + cw, 250, 570, 370, color=FIELD, sw=1.8))


    # Права колонка: Задача B (Task B Stack - PSP_B)
    x2 = 570
    f.append(rect(x2, 65, w_col, 370, fill="#f9fafb", stroke=MUTED, sw=1.5, rx=8))
    f.append(text(x2 + w_col / 2, 90, "Стек Задачі B (PSP_B)", size=12, bold=True, color=FIELD))

    # Апаратний фрейм B
    f.append(rect(x2 + 15, 115, w_col - 30, 140, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=6))
    f.append(text(x2 + w_col / 2, 135, "Апаратне відновлення", size=10.5, bold=True, color=NEG))
    for i, r_name in enumerate(regs_hw):
        f.append(text(x2 + 25, 160 + i * 22, r_name, size=9.5, color=INK, anchor="start"))

    # Програмний фрейм B
    f.append(rect(x2 + 15, 265, w_col - 30, 140, fill="#eef6ef", stroke=FIELD, sw=1.6, rx=6))
    f.append(text(x2 + w_col / 2, 285, "Програмне відновлення", size=10, bold=True, color=FIELD))
    regs_sw_b = ["ldmia r0!, {r4-r11}", "Відновлює R4-R11", "msr psp, r0", "Апарат розгортає решту"]
    for i, r_name in enumerate(regs_sw_b):
        f.append(text(x2 + 25, 310 + i * 22, r_name, size=9.5, color=INK, anchor="start"))


    # Пояснення внизу
    b, _, _ = textbox(W / 2, H - 32,
                      "ARM Cortex-M ділить перемикання на дві фази: апарат зберігає R0-R3, R12, LR, PC, xPSR,\n"
                      "а обробник PendSV зберігає R4-R11 й перемикає покажчик у блоці керування задачею (TCB).",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "context-switch-arm-stack.svg"), W, H, *f)


# ── 3. Розподіл пам'яті ОЗП (RAM): Super-loop vs RTOS ─────────────────────────
def fig_ram_budget_comparison():
    W, H = 880, 480
    f = [text(W / 2, 28, "Використання оперативної пам'яті (ОЗП) мікроконтролера",
              size=15, bold=True)]

    # Лівий блок: Super-loop
    bx1, by, bw, bh = 70, 70, 340, 330
    f.append(rect(bx1, by, bw, bh, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(bx1 + bw / 2, by + 26, "Super-loop (Єдиний стек MSP)", size=12.5, bold=True, color=NEG))

    # Складові Super-loop
    f.append(rect(bx1 + 20, by + 50, bw - 40, 45, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=4))
    f.append(text(bx1 + bw / 2, by + 68, "Єдиний спільний стек (~1.0 КБ)", size=10.5, bold=True, color=NEG))
    f.append(text(bx1 + bw / 2, by + 84, "максимальна глибина викликів + 1 кадр ISR", size=9.5, color=MUTED))

    f.append(rect(bx1 + 20, by + 105, bw - 40, 60, fill="#eef6ef", stroke=FIELD, sw=1.5, rx=4))
    f.append(text(bx1 + bw / 2, by + 127, "Статичні змінні .data / .bss (4.0 КБ)", size=10.5, bold=True, color=FIELD))
    f.append(text(bx1 + bw / 2, by + 147, "буфери UART/SPI DMA, структури станів", size=9.5, color=MUTED))

    f.append(rect(bx1 + 20, by + 175, bw - 40, 135, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(bx1 + bw / 2, by + 225, "Вільна ОЗП: ~59.0 КБ (із 64 КБ)", size=12, bold=True, color=FIELD))
    f.append(text(bx1 + bw / 2, by + 248, "92% пам'яті доступно для буферів польотних логів", size=9.5, italic=True, color=MUTED))

    f.append(text(bx1 + bw / 2, by + bh - 14, "Разом зайнято: ~5.0 КБ ОЗП", size=11, bold=True, color=INK))


    # Правий блок: RTOS
    bx2 = 470
    f.append(rect(bx2, by, bw, bh, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    f.append(text(bx2 + bw / 2, by + 26, "Витісняльна RTOS (Стек на кожну задачу)", size=12.5, bold=True, color=POS))

    # Складові RTOS
    tasks_ram = [
        ("Task Gyro/PID Stack", "1.5 КБ"),
        ("Task MAVLink Telemetry Stack", "2.0 КБ"),
        ("Task Flash Blackbox Stack", "2.5 КБ"),
        ("Task GPS / Navigation Stack", "1.5 КБ"),
        ("Task Baro/Mag + Idle/Timer Stacks", "2.0 КБ"),
        ("TCB, черги повідомлень, м'ютекси", "2.2 КБ"),
    ]
    sy = by + 50
    for title, sz in tasks_ram:
        f.append(rect(bx2 + 20, sy, bw - 40, 24, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
        f.append(text(bx2 + 30, sy + 16, title, size=9.5, color=INK, anchor="start"))
        f.append(text(bx2 + bw - 30, sy + 16, sz, size=9.5, bold=True, color=POS, anchor="end"))
        sy += 28

    f.append(rect(bx2 + 20, sy + 4, bw - 40, 30, fill="#eef6ef", stroke=FIELD, sw=1.2, rx=3))
    f.append(text(bx2 + 30, sy + 23, "Статичні змінні .data / .bss", size=9.5, color=INK, anchor="start"))
    f.append(text(bx2 + bw - 30, sy + 23, "4.0 КБ", size=9.5, bold=True, color=FIELD, anchor="end"))

    f.append(rect(bx2 + 20, sy + 40, bw - 40, 42, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=4))
    f.append(text(bx2 + bw / 2, sy + 64, "Вільна ОЗП: ~48.3 КБ (із 64 КБ)", size=11, bold=True, color=MUTED))

    f.append(text(bx2 + bw / 2, by + bh - 14, "Разом зайнято: ~15.7 КБ ОЗП (у 3 рази більше)", size=11, bold=True, color=POS))


    # Пояснення внизу
    b, _, _ = textbox(W / 2, H - 28,
                      "В RTOS кожна задача мусить мати стек під свій найгірший випадок викликів.\n"
                      "Суперцикл використовує один стек повторно, заощаджуючи пам'ять на малих мікроконтролерах.",
                      size=10, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "ram-budget-comparison.svg"), W, H, *f)


# ── 4. Інверсія пріоритетів на спільній шині ──────────────────────────────────
def fig_priority_inversion_mutex():
    W, H = 880, 490
    f = [text(W / 2, 28, "Інверсія пріоритетів на спільній шині SPI та її подолання",
              size=15, bold=True)]

    # Вісь часу
    y_axis = 370
    f.append(arrow(70, y_axis, 820, y_axis, color=LINE, sw=1.8))
    f.append(text(820, y_axis + 22, "час t", size=11, color=MUTED, anchor="end"))

    # Рівні пріоритетів (3 смуги)
    y_high = 90
    y_med  = 180
    y_low  = 270

    f.append(text(65, y_high + 25, "Високий (Гіро/PID)", size=10.5, bold=True, color=POS, anchor="end"))
    f.append(text(65, y_med + 25, "Середній (MAVLink)", size=10.5, bold=True, color=MUTED, anchor="end"))
    f.append(text(65, y_low + 25, "Низький (Flash)", size=10.5, bold=True, color=NEG, anchor="end"))

    # Горизонтальні лінії рівнів
    for y in [y_high + 45, y_med + 45, y_low + 45]:
        f.append(line(75, y, 800, y, color="#eaedf1", sw=1.2, dash="3,3"))

    # Крок 1: Низький пріоритет захоплює SPI м'ютекс
    f.append(rect(90, y_low, 110, 40, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
    f.append(text(145, y_low + 24, "Flash бере SPI Mutex", size=9.5, bold=True, color=NEG))

    # Крок 2: Високий пріоритет прокидається, хоче SPI і БЛОКУЄТЬСЯ
    f.append(rect(210, y_high, 90, 40, fill="#fdecea", stroke=POS, sw=1.6, rx=4))
    f.append(text(255, y_high + 16, "Гіро прокинувся,", size=9.5, bold=True, color=POS))
    f.append(text(255, y_high + 30, "хоче SPI -> Блок!", size=9.5, bold=True, color=POS))

    # Лінія блокування Високого
    f.append(line(300, y_high + 20, 580, y_high + 20, color=POS, sw=1.8, dash="4,4"))
    f.append(text(440, y_high + 12, "ВИСОКИЙ ПРІОРИТЕТ ЗАБЛОКОВАНО!", size=10, bold=True, color=POS))

    # Крок 3: Середній пріоритет прокидається й витісняє Низький!
    f.append(rect(310, y_med, 160, 40, fill="#f4f6f8", stroke=MUTED, sw=1.6, rx=4))
    f.append(text(390, y_med + 16, "MAVLink виконується", size=9.5, bold=True, color=INK))
    f.append(text(390, y_med + 30, "(витісняє Flash без м'ютекса)", size=9.5, color=MUTED))

    # Крок 4: Flash нарешті закінчує після Середнього
    f.append(rect(480, y_low, 100, 40, fill="#eaf0fd", stroke=NEG, sw=1.6, rx=4))
    f.append(text(530, y_low + 24, "Flash віддає Mutex", size=9.5, bold=True, color=NEG))

    # Крок 5: Високий нарешті виконується
    f.append(rect(590, y_high, 120, 40, fill="#eef6ef", stroke=FIELD, sw=2.0, rx=4))
    f.append(text(650, y_high + 16, "Гіро нарешті працює", size=9.5, bold=True, color=FIELD))
    f.append(text(650, y_high + 30, "(величезна затримка!)", size=9.5, italic=True, color=POS))

    # Пояснення механізму успадкування
    b, _, _ = textbox(W / 2, H - 38,
                      "Інверсія пріоритетів: низька задача тримає м'ютекс, середня витісняє її,\n"
                      "а критична висока задача безпорадно чекає. Лікування: протокол успадкування пріоритету (PIP),\n"
                      "який тимчасово піднімає пріоритет задачі Flash до рівня задачі Гіроскопа.",
                      size=9.5, fill=FILL, stroke=LINE)
    f.append(b)

    render(os.path.join(IMG, "priority-inversion-mutex.svg"), W, H, *f)


if __name__ == "__main__":
    fig_superloop_vs_rtos_timeline()
    fig_context_switch_arm_stack()
    fig_ram_budget_comparison()
    fig_priority_inversion_mutex()
    print("All figures generated successfully.")
