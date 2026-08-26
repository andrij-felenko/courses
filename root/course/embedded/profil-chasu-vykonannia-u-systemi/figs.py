# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми 'Профіль часу виконання в системі пристроїв'."""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_wcet_distribution():
    """Фігура 1: Розподіл часу виконання коду, WCET та часовий дедлайн."""
    w, h = 860, 420
    frags = []

    # Заголовок
    frags.append(text(w / 2, 28, "Розподіл часу виконання: від BCET до Safe WCET Bound", size=16, bold=True))

    # Вісі координат
    ax_x0, ax_y0 = 70, 340
    ax_w, ax_h = 740, 260
    frags.append(line(ax_x0, ax_y0, ax_x0 + ax_w, ax_y0, color=LINE, sw=2))  # Вісь X
    frags.append(line(ax_x0, ax_y0, ax_x0, ax_y0 - ax_h, color=LINE, sw=2))  # Вісь Y

    frags.append(text(ax_x0 + ax_w - 20, ax_y0 + 35, "Час виконання T (мкс)", size=13, bold=True, anchor="end"))
    frags.append(text(ax_x0 - 15, ax_y0 - ax_h + 15, "Ймовірність p(T)", size=13, bold=True, anchor="middle"))

    # Крива розподілу (асиметричний гаус / логнормальний)
    curve_points = []
    fill_points = [(ax_x0 + 40, ax_y0)]
    for x_val in range(40, 560, 5):
        x = ax_x0 + x_val
        # Логнормалеподібна крива з довгим правим хвостом
        norm_x = (x_val - 120) / 75.0
        if norm_x < -1.5:
            val = 0
        else:
            val = math.exp(-0.5 * (norm_x ** 2)) if norm_x <= 0 else math.exp(-0.35 * (norm_x ** 1.5))
        y = ax_y0 - val * 210
        curve_points.append((x, y))
        fill_points.append((x, y))
    fill_points.append((curve_points[-1][0], ax_y0))

    # Заливка області вимірювань
    pts_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in fill_points)
    frags.append(f'<polygon points="{pts_str}" fill="#e8f4fd" stroke="none" opacity="0.7"/>')

    # Лінія розподілу
    pts_curve_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in curve_points)
    frags.append(f'<polyline points="{pts_curve_str}" fill="none" stroke="{NEG}" stroke-width="2.5"/>')

    # Точки та лінії:
    # 1. BCET
    x_bcet = ax_x0 + 75
    frags.append(line(x_bcet, ax_y0, x_bcet, ax_y0 - 70, color=FIELD, sw=2, dash="4,4"))
    frags.append(circle(x_bcet, ax_y0, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(x_bcet, ax_y0 + 20, "BCET", size=12, bold=True, color=FIELD))
    frags.append(text(x_bcet, ax_y0 + 35, "12 мкс", size=11, color=MUTED))

    # 2. ACET (пік)
    x_acet = ax_x0 + 195
    frags.append(line(x_acet, ax_y0, x_acet, ax_y0 - 210, color=NEG, sw=2, dash="4,4"))
    frags.append(circle(x_acet, ax_y0 - 210, 5, fill=NEG, stroke=NEG))
    frags.append(text(x_acet, ax_y0 + 20, "ACET (середній)", size=12, bold=True, color=NEG))
    frags.append(text(x_acet, ax_y0 + 35, "24 мкс", size=11, color=MUTED))

    # 3. Максимум тестів (Observed Max)
    x_obs = ax_x0 + 390
    frags.append(line(x_obs, ax_y0, x_obs, ax_y0 - 45, color=MUTED, sw=1.8, dash="4,4"))
    frags.append(circle(x_obs, ax_y0, 4, fill=MUTED, stroke=MUTED))
    frags.append(text(x_obs, ax_y0 + 20, "Observed Max", size=12, bold=True, color=MUTED))
    frags.append(text(x_obs, ax_y0 + 35, "48 мкс", size=11, color=MUTED))

    # 4. Справжній WCET
    x_wcet = ax_x0 + 490
    frags.append(line(x_wcet, ax_y0, x_wcet, ax_y0 - 120, color=POS, sw=2, dash="4,4"))
    frags.append(circle(x_wcet, ax_y0, 4, fill=POS, stroke=POS))
    frags.append(text(x_wcet, ax_y0 + 20, "True WCET", size=12, bold=True, color=POS))
    frags.append(text(x_wcet, ax_y0 + 35, "62 мкс", size=11, color=MUTED))

    # 5. Safe WCET Bound (Аналітична верхня межа)
    x_bound = ax_x0 + 560
    frags.append(line(x_bound, ax_y0, x_bound, ax_y0 - 160, color="#8e44ad", sw=2, dash="5,5"))
    frags.append(circle(x_bound, ax_y0, 4, fill="#8e44ad", stroke="#8e44ad"))
    frags.append(text(x_bound, ax_y0 + 20, "Safe Bound", size=12, bold=True, color="#8e44ad"))
    frags.append(text(x_bound, ax_y0 + 35, "74 мкс", size=11, color=MUTED))

    # 6. Hard Deadline (Дедлайн)
    x_dead = ax_x0 + 680
    frags.append(line(x_dead, ax_y0 + 10, x_dead, ax_y0 - 240, color=POS, sw=3))
    frags.append(text(x_dead, ax_y0 - 248, "HARD DEADLINE", size=13, bold=True, color=POS))
    frags.append(text(x_dead, ax_y0 + 20, "Дедлайн (D)", size=12, bold=True, color=POS))
    frags.append(text(x_dead, ax_y0 + 35, "100 мкс", size=11, color=MUTED))

    # Зона ризику та запас (Safety Margin)
    box1, _, _ = textbox(525, 120, "Небезпечна зона:\nрідкісні комбінації промахів\nкешу, колізій шин і конвеєра",
                         size=11, fill="#fff3e0", stroke="#f39c12")
    frags.append(box1)
    frags.append(arrow(525, 155, x_wcet, ax_y0 - 15, color="#f39c12", sw=1.5))

    # Буфер безпеки
    frags.append(line(x_bound, 90, x_dead, 90, color=FIELD, sw=2))
    frags.append(arrow(x_dead - 10, 90, x_dead, 90, color=FIELD, sw=2))
    frags.append(arrow(x_bound + 10, 90, x_bound, 90, color=FIELD, sw=2))
    frags.append(text((x_bound + x_dead) / 2, 78, "Запас надійності: 26 мкс (26%)", size=11, bold=True, color=FIELD))

    render(os.path.join(IMG_DIR, "wcet-distribution-budget.svg"), w, h, *frags)


def fig_system_latency_breakdown():
    """Фігура 2: Повна анатомія затримки реакції у багатозадачній RTOS."""
    w, h = 860, 430
    frags = []

    frags.append(text(w / 2, 26, "Анатомія наскрізної затримки реакції системи (End-to-End Latency)", size=16, bold=True))

    # Вісь часу зверху вниз або зліва направо
    y_blocks = 140
    stages = [
        ("Апаратний\nтригер", 45, "#eef2f7", LINE),
        ("Латентність\nNVIC (Stacking)", 110, "#ffebee", POS),
        ("Виконання\nISR", 120, "#e8f8f5", FIELD),
        ("Черга / Подія\nRTOS Notify", 115, "#eaf2f8", NEG),
        ("Планувальник\nPendSV Context", 130, "#fef9e7", "#d4ac0d"),
        ("Очікування\nвищого пріор.", 110, "#f4ecf7", "#8e44ad"),
        ("Виконання\nзадачі Task", 140, "#d5f5e3", FIELD),
    ]

    cur_x = 45
    for i, (name, width, fill_c, stroke_c) in enumerate(stages):
        frags.append(rect(cur_x, y_blocks, width, 65, fill=fill_c, stroke=stroke_c, sw=1.8, rx=4))
        # Текст
        lines = name.split("\n")
        ty = y_blocks + 32 if len(lines) == 1 else y_blocks + 23
        frags.append(mtext(cur_x + width / 2, ty, lines, size=11, bold=True, color=INK))

        # Стрілка між блоками
        if i < len(stages) - 1:
            frags.append(arrow(cur_x + width, y_blocks + 32, cur_x + width + 8, y_blocks + 32, color=LINE, sw=1.5))
        cur_x += width + 8

    total_w = cur_x - 45 - 8

    # Часові маркери та пояснення під блоками
    # 1. Подія
    frags.append(line(45, y_blocks - 30, 45, y_blocks + 140, color=POS, sw=1.5, dash="3,3"))
    frags.append(text(45, y_blocks - 38, "Фізична подія", size=11, bold=True, color=POS))

    # 2. Завершення реакції
    frags.append(line(45 + total_w, y_blocks - 30, 45 + total_w, y_blocks + 140, color=FIELD, sw=1.5, dash="3,3"))
    frags.append(text(45 + total_w, y_blocks - 38, "Керівний вплив", size=11, bold=True, color=FIELD))

    # Загальна стрілка сумарної затримки
    y_tot = y_blocks + 95
    frags.append(line(45, y_tot, 45 + total_w, y_tot, color=LINE, sw=2))
    frags.append(arrow(45 + 15, y_tot, 45, y_tot, color=LINE, sw=2))
    frags.append(arrow(45 + total_w - 15, y_tot, 45 + total_w, y_tot, color=LINE, sw=2))
    frags.append(text(45 + total_w / 2, y_tot - 8, "Повна системна затримка T_response = T_lat + T_isr + T_ctx + T_block + T_exec",
                      size=12, bold=True, color=INK))

    # Джиттер вікно
    y_jit = y_blocks + 160
    frags.append(rect(45 + total_w - 190, y_jit, 190, 45, fill="#fdebd0", stroke="#e67e22", sw=1.5))
    frags.append(mtext(45 + total_w - 95, y_jit + 18, ["Джиттер реакції (Jitter)", "відхилення моменту активації"],
                       size=10, bold=True, color="#a04000"))

    # Блоки-примітки внизу
    b1, _, _ = textbox(200, 350, "Апаратна латентність:\n12 тактів на збереження регістрів R0-R3, R12, LR, PC, xPSR\n+ вивантаження конвеєра та затримки Flash",
                       size=11, min_w=300, fill="#ffffff", stroke=LINE)
    frags.append(b1)

    b2, _, _ = textbox(590, 350, "Програмний оверхед RTOS:\nКритичні секції блокують виклик PendSV.\nВитіснення фоновою задачею породжує джиттер.",
                       size=11, min_w=320, fill="#ffffff", stroke=LINE)
    frags.append(b2)

    render(os.path.join(IMG_DIR, "system-latency-breakdown.svg"), w, h, *frags)


def fig_gpio_multichannel_trace():
    """Фігура 3: Багатоканальне стробування GPIO для логічного аналізатора."""
    w, h = 860, 400
    frags = []

    frags.append(text(w / 2, 26, "Осцилограма багатоканального стробування GPIO в системі з RTOS", size=16, bold=True))

    t_start_x = 180
    trace_w = 640

    channels = [
        ("EXTI / Sensor IRQ", 70, POS),
        ("GPIO D0: ISR Handler", 130, POS),
        ("GPIO D1: RTOS PendSV", 190, "#d4ac0d"),
        ("GPIO D2: Task Motor [High]", 250, FIELD),
        ("GPIO D3: Task Comm [Low]", 310, NEG),
    ]

    for name, y_c, color in channels:
        frags.append(text(t_start_x - 15, y_c + 15, name, size=11, bold=True, color=color, anchor="end"))
        frags.append(line(t_start_x, y_c + 20, t_start_x + trace_w, y_c + 20, color="#d0d0d0", sw=1))

    # Сигнали:
    # 1. EXTI: імпульс на t = 60..75
    x_evt = t_start_x + 60
    frags.append(f'<polyline points="{t_start_x},90 {x_evt},90 {x_evt},70 {x_evt+15},70 {x_evt+15},90 {t_start_x+trace_w},90" fill="none" stroke="{POS}" stroke-width="2"/>')

    # 2. GPIO D0 (ISR): підйом на t = 85 (латентність 25px = 1.2 мкс), спад на t = 160
    x_isr_s = x_evt + 30
    x_isr_e = x_isr_s + 70
    frags.append(f'<polyline points="{t_start_x},150 {x_isr_s},150 {x_isr_s},130 {x_isr_e},130 {x_isr_e},150 {t_start_x+trace_w},150" fill="none" stroke="{POS}" stroke-width="2"/>')

    # 3. GPIO D1 (PendSV Context switch): підйом на t = 165, спад на t = 215
    x_ctx_s = x_isr_e + 8
    x_ctx_e = x_ctx_s + 45
    frags.append(f'<polyline points="{t_start_x},210 {x_ctx_s},210 {x_ctx_s},190 {x_ctx_e},190 {x_ctx_e},210 {t_start_x+trace_w},210" fill="none" stroke="#d4ac0d" stroke-width="2"/>')

    # 4. GPIO D2 (Task Motor): підйом після перемикання контексту t = 215, виконання до t = 440
    x_tsk_s = x_ctx_e
    x_tsk_e = x_tsk_s + 240
    frags.append(f'<polyline points="{t_start_x},270 {x_tsk_s},270 {x_tsk_s},250 {x_tsk_e},250 {x_tsk_e},270 {t_start_x+trace_w},270" fill="none" stroke="{FIELD}" stroke-width="2"/>')

    # 5. GPIO D3 (Task Comm): працював до t = x_evt, витіснений, відновлений на t = 470
    x_comm_res = x_tsk_e + 30
    frags.append(f'<polyline points="{t_start_x},310 {x_evt},310 {x_evt},330 {x_comm_res},330 {x_comm_res},310 {t_start_x+trace_w},310" fill="none" stroke="{NEG}" stroke-width="2"/>')

    # Вимірювальні маркери
    # Маркер 1: Латентність переривання
    frags.append(line(x_evt, 55, x_evt, 165, color="#e74c3c", sw=1.2, dash="3,3"))
    frags.append(line(x_isr_s, 55, x_isr_s, 165, color="#e74c3c", sw=1.2, dash="3,3"))
    frags.append(line(x_evt, 58, x_isr_s, 58, color="#e74c3c", sw=1.5))
    frags.append(text((x_evt + x_isr_s) / 2, 52, "T_irq_lat (1.4 мкс)", size=10, bold=True, color="#e74c3c"))

    # Маркер 2: Тривалість ISR
    frags.append(line(x_isr_s, 120, x_isr_e, 120, color=POS, sw=1.5))
    frags.append(text((x_isr_s + x_isr_e) / 2, 114, "T_isr (3.8 мкс)", size=10, bold=True, color=POS))

    # Маркер 3: Перемикання контексту
    frags.append(line(x_ctx_s, 180, x_ctx_e, 180, color="#b7950b", sw=1.5))
    frags.append(text((x_ctx_s + x_ctx_e) / 2, 174, "T_ctx (2.1 мкс)", size=10, bold=True, color="#b7950b"))

    # Маркер 4: Час виконання задачі WCET
    frags.append(line(x_tsk_s, 240, x_tsk_e, 240, color=FIELD, sw=1.5))
    frags.append(text((x_tsk_s + x_tsk_e) / 2, 234, "T_task (18.6 мкс)", size=11, bold=True, color=FIELD))

    # Шкала внизу
    frags.append(line(t_start_x, 360, t_start_x + trace_w, 360, color=LINE, sw=1.5))
    for tick in range(0, trace_w + 1, 80):
        frags.append(line(t_start_x + tick, 355, t_start_x + tick, 365, color=LINE, sw=1.2))
        frags.append(text(t_start_x + tick, 380, f"{tick * 0.1:.1f} мкс", size=10, color=MUTED))

    render(os.path.join(IMG_DIR, "gpio-multichannel-trace.svg"), w, h, *frags)


def fig_dwt_itm_architecture():
    """Фігура 4: Апаратна структура підсистеми CoreDebug/DWT/ITM у ядрі Cortex-M."""
    w, h = 860, 390
    frags = []

    frags.append(text(w / 2, 26, "Апаратна підсистема внутрішнього профілювання ARM Cortex-M (DWT + ITM)", size=16, bold=True))

    # Контейнер процесорного ядра (Cortex-M Core)
    frags.append(rect(40, 60, 480, 290, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    frags.append(text(280, 85, "Cortex-M Processor Core & Internal Debug Block", size=13, bold=True, color="#334155"))

    # Блок ALU / Pipeline
    b_alu, _, _ = textbox(135, 145, "ALU & Pipeline\nВиконання інструкцій", size=11, min_w=150, fill="#e2e8f0", stroke="#475569")
    frags.append(b_alu)

    # CoreDebug Register Block
    b_dbg, _, _ = textbox(135, 235, "CoreDebug Registers\nDEMCR (TRCENA біт 24)\nDHCSR / DCRSR", size=11, min_w=160, fill="#ede9fe", stroke="#7c3aed")
    frags.append(b_dbg)

    # DWT Block
    b_dwt, _, _ = textbox(370, 145, "DWT (Data Watchpoint & Trace)\nDWT->CYCCNT (32-біт лічильник)\nCPICNT, EXCCNT, SLEEPCNT", size=11, min_w=200, fill="#e0f2fe", stroke="#0284c7")
    frags.append(b_dwt)

    # ITM Block
    b_itm, _, _ = textbox(370, 265, "ITM (Instrumentation Trace)\n32 Стимул-порти (ITM->PORT[0])\nАпаратний буфер FIFO подій", size=11, min_w=200, fill="#fef3c7", stroke="#d97706")
    frags.append(b_itm)

    # Зв'язки всередині ядра
    frags.append(arrow(135, 185, 135, 205, color="#7c3aed", sw=1.5))
    frags.append(arrow(215, 235, 270, 155, color="#0284c7", sw=1.5))
    frags.append(arrow(215, 245, 270, 265, color="#d97706", sw=1.5))
    frags.append(arrow(210, 145, 270, 145, color="#0284c7", sw=1.5))
    frags.append(arrow(370, 195, 370, 225, color="#d97706", sw=1.5))

    # Зовнішній блок TPIU / SWO
    frags.append(rect(570, 100, 240, 200, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    frags.append(text(690, 128, "TPIU & Фізичний вивід", size=13, bold=True, color=FIELD))

    b_swo, _, _ = textbox(690, 185, "TPIU Serial Formatter\nАсинхронний протокол NRZ / Manchester\nШвидкість до 10-50 Мбіт/с", size=10, min_w=210, fill="#ffffff", stroke=FIELD)
    frags.append(b_swo)

    b_pin, _, _ = textbox(690, 265, "Вивід SWO (PB3 / TRACESWO)\nПідключення до J-Link / ST-Link", size=11, bold=True, min_w=210, fill="#dcfce7", stroke=FIELD)
    frags.append(b_pin)

    # Зв'язок ITM -> TPIU
    frags.append(arrow(470, 265, 570, 185, color=LINE, sw=2))
    frags.append(text(525, 210, "Пакети\nтраси", size=10, bold=True, color=INK))

    frags.append(arrow(690, 218, 690, 240, color=FIELD, sw=2))

    render(os.path.join(IMG_DIR, "dwt-itm-architecture.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_wcet_distribution()
    fig_system_latency_breakdown()
    fig_gpio_multichannel_trace()
    fig_dwt_itm_architecture()
    print("Всі фігури згенеровано успішно.")
