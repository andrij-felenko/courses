# -*- coding: utf-8 -*-
"""Генератор ілюстрацій для теми: Профіль часу виконання: цикли, переривання, джитер."""

import sys
import os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

def fig_gpio_oscilloscope_profiling():
    """Ілюстрація 1: Профілювання через стробування GPIO-виводу для осцилографа."""
    W, H = 880, 400
    f = [text(W / 2, 26, "Апаратне профілювання: осцилограма стробування GPIO", size=16, bold=True)]
    
    # Тло блоків сигналів
    f.append(rect(20, 48, 840, 332, fill="#fbfcfd", stroke=LINE, sw=1.2, rx=8))
    
    # ── Сигнал 1: Фізична подія (Датчик / Таймер) ──
    f.append(text(35, 80, "Канал 1: Подія IRQ", size=12, color=POS, bold=True, anchor="start"))
    # Лінія сигналу IRQ
    f.append(line(200, 85, 290, 85, color=POS, sw=2))
    f.append(line(290, 85, 290, 65, color=POS, sw=2))
    f.append(line(290, 65, 480, 65, color=POS, sw=2))
    f.append(line(480, 65, 480, 85, color=POS, sw=2))
    f.append(line(480, 85, 820, 85, color=POS, sw=2))
    f.append(text(290, 58, "Фронт події", size=10, color=POS, anchor="middle"))
    
    # ── Сигнал 2: Тестовий пін GPIO (DEBUG_PIN) ──
    f.append(text(35, 150, "Канал 2: GPIO (Строб)", size=12, color=FIELD, bold=True, anchor="start"))
    # Лінія GPIO
    f.append(line(200, 155, 360, 155, color=FIELD, sw=2.2))
    f.append(line(360, 155, 360, 130, color=FIELD, sw=2.2))
    f.append(line(360, 130, 640, 130, color=FIELD, sw=2.2))
    f.append(line(640, 130, 640, 155, color=FIELD, sw=2.2))
    f.append(line(640, 155, 820, 155, color=FIELD, sw=2.2))
    
    # Позначення GPIO_SET та GPIO_RESET
    f.append(text(360, 122, "SET (Вхід)", size=10, color=FIELD, bold=True, anchor="middle"))
    f.append(text(640, 122, "RESET (Вихід)", size=10, color=FIELD, bold=True, anchor="middle"))
    
    # ── Сигнал 3: Внутрішній стан процесора ──
    f.append(text(35, 225, "Ядро CPU", size=12, color=NEG, bold=True, anchor="start"))
    
    # Блоки стану ядра (рознесені по X без накладання)
    # [200..280] -> cx=240
    b_bg, _, _ = textbox(240, 225, "Thread\nmain()", size=10, pad=4, fill="#f0f3f8", stroke=MUTED, color=INK)
    f.append(b_bg)
    
    # [290..355] -> cx=322
    b_stk, _, _ = textbox(325, 225, "Стекінг\n(12 т.)", size=9.5, pad=4, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_stk)
    
    # [360..635] -> cx=500, w=270
    b_isr, _, _ = textbox(500, 225, "Корисний код обробника (ISR)\nОбчислення, читання периферії", size=10, pad=5, fill="#c6f6d5", stroke=FIELD, color="#1c4532", bold=True)
    f.append(b_isr)
    
    # [642..710] -> cx=676
    b_unstk, _, _ = textbox(675, 225, "Розстек.\n(12 т.)", size=9.5, pad=4, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_unstk)
    
    # [718..810] -> cx=765
    b_bg2, _, _ = textbox(765, 225, "Thread\nmain()", size=10, pad=4, fill="#f0f3f8", stroke=MUTED, color=INK)
    f.append(b_bg2)
    
    # ── Часові виміри та інтервали (розмірні лінії нижче блоків ядра) ──
    # Інтервал 1: Латентність переривання (T_lat)
    f.append(line(290, 90, 290, 200, color=POS, sw=1, dash="2,2"))
    f.append(line(290, 255, 290, 310, color=POS, sw=1, dash="2,2"))
    f.append(line(360, 160, 360, 200, color=FIELD, sw=1, dash="2,2"))
    f.append(line(360, 255, 360, 310, color=FIELD, sw=1, dash="2,2"))
    
    f.append(arrow(325, 305, 290, 305, color=POS, sw=1.4))
    f.append(arrow(325, 305, 360, 305, color=POS, sw=1.4))
    f.append(text(325, 325, "Латентність T_lat", size=10.5, color=POS, bold=True, anchor="middle"))
    f.append(text(325, 340, "(стекінг + вхід)", size=9, color=MUTED, anchor="middle"))
    
    # Інтервал 2: Тривалість імпульсу GPIO (T_exec)
    f.append(line(640, 160, 640, 200, color=FIELD, sw=1, dash="2,2"))
    f.append(line(640, 255, 640, 310, color=FIELD, sw=1, dash="2,2"))
    
    f.append(arrow(500, 305, 360, 305, color=FIELD, sw=1.5))
    f.append(arrow(500, 305, 640, 305, color=FIELD, sw=1.5))
    f.append(text(500, 325, "Час виконання T_exec ≈ T_pulse − 2·T_gpio", size=11, color=FIELD, bold=True, anchor="middle"))
    f.append(text(500, 342, "Ширина імпульсу на осцилографі", size=9.5, color=MUTED, anchor="middle"))
    
    # Інтервал 3: Повна затримка виходу
    f.append(line(710, 245, 710, 310, color=MUTED, sw=1, dash="2,2"))
    f.append(arrow(675, 305, 640, 305, color=MUTED, sw=1.2))
    f.append(arrow(675, 305, 710, 305, color=MUTED, sw=1.2))
    f.append(text(675, 325, "Повернення", size=9.5, color=MUTED, anchor="middle"))
    f.append(text(675, 340, "(12 тактів)", size=9.5, color=MUTED, anchor="middle"))
    
    render(os.path.join(IMG, "gpio-oscilloscope-profiling.svg"), W, H, *f)

def fig_cortex_m_interrupt_latency():
    """Ілюстрація 2: Анатомія латентності переривань Cortex-M, стекінг та Tail-Chaining."""
    W, H = 880, 420
    f = [text(W / 2, 26, "Анатомія затримок переривань Cortex-M: стекінг і Tail-Chaining", size=16, bold=True)]
    
    # ── Блок 1: Стандартний вхід і вихід (без оптимізацій) ──
    f.append(rect(20, 50, 840, 160, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    f.append(text(35, 72, "1. Одиночне переривання: повний цикл збереження та відновлення", size=12.5, color=INK, bold=True, anchor="start"))
    
    # Подія
    f.append(circle(75, 105, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(75, 95, "Запит IRQ", size=10, color=POS, bold=True, anchor="middle"))
    f.append(arrow(75, 108, 75, 125, color=POS, sw=1.5))
    
    # Етапи
    b1_pipe, _, _ = textbox(135, 145, "Конвеєр\n(0..2 т.)", size=9, pad=4, fill="#edf2f7", stroke=MUTED, color=INK)
    f.append(b1_pipe)
    
    b1_stk, _, _ = textbox(285, 145, "Апаратний стекінг (12 тактів)\nPush R0-R3, R12, LR, PC, xPSR", size=9.5, pad=5, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b1_stk)
    
    b1_isr, _, _ = textbox(525, 145, "Виконання коду ISR 1\nКорисна робота функції", size=10, pad=5, fill="#c6f6d5", stroke=FIELD, color="#1c4532", bold=True)
    f.append(b1_isr)
    
    b1_pop, _, _ = textbox(720, 145, "Розстекування (12 т.)\nPop регістрів ядра", size=9.5, pad=5, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b1_pop)
    
    b1_ret, _, _ = textbox(815, 145, "Thread\nmain()", size=9, pad=4, fill="#edf2f7", stroke=MUTED, color=INK)
    f.append(b1_ret)
    
    # Стрілки переходу між блоками
    f.append(arrow(170, 145, 185, 145, color=LINE, sw=1.2))
    f.append(arrow(385, 145, 420, 145, color=LINE, sw=1.2))
    f.append(arrow(630, 145, 645, 145, color=LINE, sw=1.2))
    f.append(arrow(785, 145, 792, 145, color=LINE, sw=1.2))
    
    # ── Блок 2: Оптимізація Tail-Chaining ──
    f.append(rect(20, 225, 840, 175, fill="#f0fff4", stroke=FIELD, sw=1.4, rx=8))
    f.append(text(35, 248, "2. Оптимізація Tail-Chaining: зв'язка двох ISR без повторного стекінгу", size=12.5, color=FIELD, bold=True, anchor="start"))
    
    b2_stk, _, _ = textbox(105, 320, "Стекінг\n(12 т.)", size=9.5, pad=4, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b2_stk)
    
    b2_isr1, _, _ = textbox(235, 320, "Виконання ISR 1\n(наприклад, Timer)", size=9.5, pad=5, fill="#c6f6d5", stroke=FIELD, color="#1c4532", bold=True)
    f.append(b2_isr1)
    
    # Подія 2 під час ISR 1
    f.append(circle(275, 275, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(275, 267, "Запит IRQ 2", size=10, color=POS, bold=True, anchor="middle"))
    f.append(arrow(275, 280, 275, 295, color=POS, sw=1.3))
    
    # Tail-Chain блок
    b2_tc, _, _ = textbox(415, 320, "Tail-Chain (лише 6 тактів!)\nЗамість 12 Pop + 12 Push = 24 т.", size=9.5, pad=5, fill="#feebc8", stroke="#dd6b20", color="#7b341e", bold=True)
    f.append(b2_tc)
    
    b2_isr2, _, _ = textbox(605, 320, "Виконання ISR 2\n(наприклад, UART RX)", size=9.5, pad=5, fill="#c6f6d5", stroke=FIELD, color="#1c4532", bold=True)
    f.append(b2_isr2)
    
    b2_pop, _, _ = textbox(745, 320, "Розстекування\n(12 тактів)", size=9.5, pad=4, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b2_pop)
    
    b2_ret, _, _ = textbox(820, 320, "Thread", size=9, pad=4, fill="#edf2f7", stroke=MUTED, color=INK)
    f.append(b2_ret)
    
    # Стрілки
    f.append(arrow(145, 320, 160, 320, color=LINE, sw=1.2))
    f.append(arrow(310, 320, 318, 320, color=LINE, sw=1.2))
    f.append(arrow(510, 320, 525, 320, color=LINE, sw=1.2))
    f.append(arrow(685, 320, 698, 320, color=LINE, sw=1.2))
    f.append(arrow(785, 320, 795, 320, color=LINE, sw=1.2))
    
    f.append(text(415, 375, "Економія 18 тактів процесора завдяки апаратному Tail-Chaining у NVIC", size=11, color="#7b341e", italic=True, anchor="middle"))
    
    render(os.path.join(IMG, "cortex-m-interrupt-latency.svg"), W, H, *f)

def fig_flash_wait_states_impact():
    """Ілюстрація 3: Вплив Flash Wait States, Prefetch та I-Cache на час виконання інструкцій."""
    W, H = 880, 430
    f = [text(W / 2, 26, "Вплив Flash Wait States, Prefetch та I-Cache на детермінізм", size=16, bold=True)]
    
    # ── Варіант 1: Виконання з Zero-Wait-State RAM / TCM ──
    f.append(rect(20, 50, 840, 105, fill="#f0fff4", stroke=FIELD, sw=1.3, rx=8))
    f.append(text(35, 70, "1. Виконання з RAM / ITCM (0 Wait States): 1 такт на команду, нульовий джитер", size=12, color=FIELD, bold=True, anchor="start"))
    
    ops = ["NOP", "ADD", "LDR", "STR", "B.NE (Branch)", "SUB", "CMP"]
    for i, op in enumerate(ops):
        bx = 85 + i * 110
        b_c, _, _ = textbox(bx, 108, op, size=10, pad=4, fill="#c6f6d5", stroke=FIELD, color="#1c4532", bold=True)
        f.append(b_c)
        if i < len(ops) - 1:
            f.append(arrow(bx + 46, 108, bx + 60, 108, color=FIELD, sw=1.2))
    
    # ── Варіант 2: Flash із 5 Wait States (без кешу при переході) ──
    f.append(rect(20, 168, 840, 120, fill="#fff5f5", stroke=POS, sw=1.3, rx=8))
    f.append(text(35, 188, "2. Flash на частоті 168 МГц (5 Wait States): Prefetch буферизує лінійно, але Branch скидає чергу", size=12, color=POS, bold=True, anchor="start"))
    
    b_f1, _, _ = textbox(70, 235, "ADD (1 т.)", size=9.5, pad=4, fill="#edf2f7", stroke=MUTED, color=INK)
    f.append(b_f1)
    
    b_f2, _, _ = textbox(170, 235, "B.NE (Перехід)", size=9.5, pad=4, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_f2)
    
    b_stall, _, _ = textbox(450, 235, "ПРОСТІЙ КОНВЕЄРА (5 тактів Flash Wait States)\nСкидання Prefetch-буфера та вибірка нової 128-бітної Flash-лінії", size=9.5, pad=5, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_stall)
    
    b_f3, _, _ = textbox(730, 235, "SUB (1 т.)", size=9.5, pad=4, fill="#edf2f7", stroke=MUTED, color=INK)
    f.append(b_f3)
    
    b_f4, _, _ = textbox(815, 235, "CMP (1 т.)", size=9.5, pad=4, fill="#edf2f7", stroke=MUTED, color=INK)
    f.append(b_f4)
    
    f.append(arrow(115, 235, 122, 235, color=LINE, sw=1.2))
    f.append(arrow(222, 235, 230, 235, color=POS, sw=1.2))
    f.append(arrow(670, 235, 685, 235, color=LINE, sw=1.2))
    f.append(arrow(770, 235, 778, 235, color=LINE, sw=1.2))
    
    # ── Варіант 3: I-Cache / ART Accelerator: Cache Hit vs Cache Miss ──
    f.append(rect(20, 300, 840, 115, fill="#ebf8ff", stroke=NEG, sw=1.3, rx=8))
    f.append(text(35, 320, "3. Flash з I-Cache / ART Accelerator: середній час відмінний, але виникає джитер", size=12, color=NEG, bold=True, anchor="start"))
    
    b_h1, _, _ = textbox(140, 362, "Попадання в кеш (Hit)\n0 тактів штрафу (1 такт)", size=9.5, pad=4, fill="#bee3f8", stroke=NEG, color="#2b6cb0", bold=True)
    f.append(b_h1)
    
    b_m, _, _ = textbox(450, 362, "Промах кешу (Cache Miss)\nШтраф 5+ тактів завантаження рядка кешу", size=9.5, pad=4, fill="#fed7d7", stroke=POS, color=POS, bold=True)
    f.append(b_m)
    
    b_h2, _, _ = textbox(740, 362, "Попадання в кеш (Hit)\n0 тактів штрафу (1 такт)", size=9.5, pad=4, fill="#bee3f8", stroke=NEG, color="#2b6cb0", bold=True)
    f.append(b_h2)
    
    f.append(arrow(245, 362, 275, 362, color=NEG, sw=1.2))
    f.append(arrow(625, 362, 645, 362, color=NEG, sw=1.2))
    
    render(os.path.join(IMG, "flash-wait-states-impact.svg"), W, H, *f)

def fig_wcet_vs_bcet_distribution():
    """Ілюстрація 4: Розподіл часу виконання: BCET, ACET, спостережуваний максимум та справжній WCET."""
    W, H = 880, 390
    f = [text(W / 2, 26, "Розподіл часу виконання: BCET, ACET, WCET та часовий дедлайн", size=16, bold=True)]
    
    f.append(rect(20, 48, 840, 322, fill="#ffffff", stroke=LINE, sw=1.2, rx=8))
    
    # Осі координат
    f.append(line(80, 290, 800, 290, color=LINE, sw=1.8))
    f.append(arrow(780, 290, 810, 290, color=LINE, sw=1.8))
    f.append(text(805, 310, "Час виконання (T)", size=11, color=INK, bold=True, anchor="end"))
    
    f.append(line(80, 290, 80, 70, color=LINE, sw=1.8))
    f.append(arrow(80, 90, 80, 65, color=LINE, sw=1.8))
    f.append(text(75, 60, "Ймовірність / Частота появи", size=11, color=INK, bold=True, anchor="start"))
    
    # Крива розподілу ймовірностей (гаусоподібний купол з довгим правим хвостом)
    path_d = ("M 110 290 "
              "C 140 290, 180 280, 210 210 "
              "C 240 140, 270 90, 300 90 "
              "C 330 90, 360 150, 400 200 "
              "C 450 250, 520 275, 590 285 "
              "C 630 288, 680 290, 710 290")
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_d, NEG))
    
    # Заливка під кривою
    path_fill = path_d + " L 710 290 L 110 290 Z"
    f.append('<path d="%s" fill="#ebf8ff" opacity="0.6"/>' % path_fill)
    
    # ── Вертикальні маркери ──
    # 1. BCET (Найкращий час)
    f.append(line(190, 290, 190, 195, color=FIELD, sw=1.5, dash="3,3"))
    f.append(circle(190, 225, 4, fill=FIELD, stroke=FIELD, sw=1))
    f.append(text(190, 182, "BCET", size=12, color=FIELD, bold=True, anchor="middle"))
    f.append(text(190, 168, "Найкращий час", size=9.5, color=FIELD, anchor="middle"))
    
    # 2. ACET (Середній час / Пік вимірів)
    f.append(line(300, 290, 300, 90, color=NEG, sw=1.8, dash="3,3"))
    f.append(circle(300, 90, 4, fill=NEG, stroke=NEG, sw=1))
    f.append(text(300, 80, "ACET (Середній час)", size=12, color=NEG, bold=True, anchor="middle"))
    f.append(text(300, 66, "Типовий результат тестів", size=9.5, color=MUTED, anchor="middle"))
    
    # 3. Виміряний максимум під час тестів (Observed Max)
    f.append(line(490, 290, 490, 220, color="#d69e2e", sw=1.5, dash="3,3"))
    f.append(circle(490, 240, 4, fill="#d69e2e", stroke="#d69e2e", sw=1))
    f.append(text(490, 205, "Виміряний максимум", size=11, color="#b7791f", bold=True, anchor="middle"))
    f.append(text(490, 192, "(Не є гарантією!)", size=9.5, color="#b7791f", italic=True, anchor="middle"))
    
    # 4. Справжній WCET (Worst-Case Execution Time)
    f.append(line(610, 290, 610, 130, color=POS, sw=2, dash="3,3"))
    f.append(circle(610, 280, 4, fill=POS, stroke=POS, sw=1))
    f.append(text(610, 120, "WCET", size=13, color=POS, bold=True, anchor="middle"))
    f.append(text(610, 106, "Найгірший теоретичний час", size=9.5, color=POS, anchor="middle"))
    
    # 5. Дедлайн системи (Deadline)
    f.append(line(730, 290, 730, 80, color="#742a2a", sw=2.2))
    f.append(text(730, 72, "ДЕДЛАЙН СИСТЕМИ", size=11.5, color="#742a2a", bold=True, anchor="middle"))
    
    # Запас надійності (Safety Margin)
    f.append(rect(615, 260, 110, 24, fill="#feebc8", stroke="#dd6b20", sw=1, rx=4))
    f.append(text(670, 276, "Запас надійності", size=9.5, color="#7b341e", bold=True, anchor="middle"))
    
    render(os.path.join(IMG, "wcet-vs-bcet-distribution.svg"), W, H, *f)

def main():
    fig_gpio_oscilloscope_profiling()
    fig_cortex_m_interrupt_latency()
    fig_flash_wait_states_impact()
    fig_wcet_vs_bcet_distribution()
    print("Всі 4 фігури успішно згенеровано.")

if __name__ == "__main__":
    main()
