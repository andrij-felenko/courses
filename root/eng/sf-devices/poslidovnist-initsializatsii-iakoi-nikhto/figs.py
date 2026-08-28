# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. hardware-power-up-timing-diagram: Часова діаграма перехідних процесів ──
def fig_power_up_timing():
    W, H = 880, 480
    p = []

    # Загальне тло панелі
    p.append(rect(10, 10, 860, 460, fill="#ffffff", stroke=MUTED, sw=1.2, rx=8))

    # Заголовок фігури
    p.append(text(440, 38, "Часова діаграма перехідних процесів живлення та стабілізації периферії", size=14, bold=True, color=INK))

    # Вертикальні часові мітки (X-координати)
    t0 = 190   # Подача живлення (Power ON)
    t1 = 300   # Напруга V_DD досягла номіналу (t_RISE)
    t2 = 450   # Відпускання лінії скидання nRST (t_RESET)
    t3 = 590   # Захоплення частоти PLL (t_LOCK)
    t4 = 730   # Завершення внутрішнього завантаження чипа (t_READY)

    # Вертикальні розділові пунктири
    for tx in [t0, t1, t2, t3, t4]:
        p.append(line(tx, 60, tx, 415, color="#cbd5e1", sw=1.2, dash="4 3"))

    # Підписи часових інтервалів угорі
    p.append(text((t0 + t1) / 2, 75, "t_RISE", size=11, bold=True, color=POS))
    p.append(text((t0 + t1) / 2, 90, "0.1...10 мс", size=9, color=MUTED))

    p.append(text((t1 + t2) / 2, 75, "t_RESET", size=11, bold=True, color=POS))
    p.append(text((t1 + t2) / 2, 90, "≥ 10...50 мс", size=9, color=MUTED))

    p.append(text((t2 + t3) / 2, 75, "t_LOCK", size=11, bold=True, color=NEG))
    p.append(text((t2 + t3) / 2, 90, "1...5 мс", size=9, color=MUTED))

    p.append(text((t3 + t4) / 2, 75, "t_BOOT", size=11, bold=True, color="#b45309"))
    p.append(text((t3 + t4) / 2, 90, "5...50 мс", size=9, color=MUTED))

    p.append(text((t4 + 850) / 2, 75, "READY", size=11, bold=True, color=FIELD))
    p.append(text((t4 + 850) / 2, 90, "Штатна шина", size=9, color=FIELD))

    # ── Рядок 1: Живлення V_DD ──
    y1 = 135
    p.append(text(130, y1 + 4, "Живлення V_DD", size=11, bold=True, color=INK, anchor="end"))
    p.append(line(140, y1 + 12, t0, y1 + 12, color=MUTED, sw=1.5))
    # Наростання напруги
    p.append(line(t0, y1 + 12, t1, y1 - 12, color=POS, sw=2.5))
    p.append(line(t1, y1 - 12, 850, y1 - 12, color=POS, sw=2.5))
    p.append(text(t1 + 35, y1 - 17, "3.3 В (стабільна)", size=10, bold=True, color=POS))
    p.append(text(t0 + 55, y1 + 5, "поріг V_POR", size=9, color=MUTED))
    p.append(line(t0 + 40, y1 + 8, t0 + 80, y1 + 8, color=MUTED, sw=1, dash="2 2"))

    # ── Рядок 2: Апаратне скидання nRST ──
    y2 = 195
    p.append(text(130, y2 + 4, "Скидання nRST", size=11, bold=True, color=INK, anchor="end"))
    p.append(line(140, y2 + 12, t2, y2 + 12, color=POS, sw=2.2)) # LOW
    p.append(line(t2, y2 + 12, t2, y2 - 12, color=POS, sw=2.2))
    p.append(line(t2, y2 - 12, 850, y2 - 12, color=FIELD, sw=2.2)) # HIGH
    p.append(text((t0 + t2) / 2, y2 + 25, "LOW (активне скидання веденого чипа)", size=9, color=POS))
    p.append(text(t2 + 75, y2 - 17, "HIGH (скидання відпущено)", size=9, color=FIELD))

    # ── Рядок 3: Тактування / PLL ──
    y3 = 260
    p.append(text(130, y3 + 4, "Тактування / PLL", size=11, bold=True, color=INK, anchor="end"))
    p.append(line(140, y3 + 12, t2, y3 + 12, color=MUTED, sw=1.5))
    # Фаза розгону генератора
    for step in range(t2, t3, 10):
        p.append(line(step, y3 + 8, step + 5, y3 - 8, color=NEG, sw=1.2))
        p.append(line(step + 5, y3 - 8, step + 10, y3 + 8, color=NEG, sw=1.2))
    # Стабільна сітка тактування
    for step in range(t3, 850, 8):
        p.append(line(step, y3 + 10, step + 4, y3 - 10, color=FIELD, sw=1.6))
        p.append(line(step + 4, y3 - 10, step + 8, y3 + 10, color=FIELD, sw=1.6))
    p.append(text((t2 + t3) / 2, y3 + 24, "Розгін RC та захоплення PLL", size=9, color=NEG))
    p.append(text(t3 + 55, y3 - 16, "Стабільна частота", size=9, color=FIELD))

    # ── Рядок 4: Внутрішній стан чіпа ──
    y4 = 325
    p.append(text(130, y4 + 4, "Внутрішній стан", size=11, bold=True, color=INK, anchor="end"))
    p.append(rect(140, y4 - 12, t2 - 140, 24, fill="#fdecea", stroke=POS, sw=1.2, rx=3))
    p.append(text((140 + t2) / 2, y4 + 4, "Апаратне скидання (POR)", size=9, color=POS, bold=True))

    p.append(rect(t2, y4 - 12, t4 - t2, 24, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=3))
    p.append(text((t2 + t4) / 2, y4 + 4, "Завантаження OTP / ROM / Калібрувань", size=9, color="#92400e", bold=True))

    p.append(rect(t4, y4 - 12, 850 - t4, 24, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=3))
    p.append(text((t4 + 850) / 2, y4 + 4, "READY (Готовий)", size=9, color=FIELD, bold=True))

    # ── Рядок 5: Шина I2C / SPI ──
    y5 = 385
    p.append(text(130, y5 + 4, "Шина I2C / SPI", size=11, bold=True, color=INK, anchor="end"))
    p.append(rect(140, y5 - 12, t4 - 140, 24, fill="#fee2e2", stroke=POS, sw=1.2, rx=3))
    p.append(text((140 + t4) / 2, y5 + 4, "ЗАБОРОНЕНА ЗОНА (Запити дадуть NACK / зависання)", size=9, color=POS, bold=True))

    p.append(rect(t4, y5 - 12, 850 - t4, 24, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=3))
    p.append(text((t4 + 850) / 2, y5 + 4, "Перша транзакція", size=9, color=FIELD, bold=True))

    # Нижня підсумкова плашка
    p.append(rect(30, 430, 820, 26, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
    p.append(text(440, 447, "Запити до настання t_READY — головна причина NACK на I2C та мовчання чіпів при холодному старті.", size=10, bold=True, color=INK))

    render(os.path.join(OUT, "hardware-power-up-timing-diagram.svg"), W, H, *p,
           title="Часова діаграма перехідних процесів живлення, апаратного скидання та стабілізації периферії")


# ── 2. peripheral-initialization-dependency-graph: Граф залежностей ініціалізації ──
def fig_dependency_graph():
    W, H = 860, 530
    p = []

    p.append(rect(10, 10, 840, 510, fill="#ffffff", stroke=MUTED, sw=1.2, rx=8))
    p.append(text(430, 38, "Граф строгого порядку ініціалізації апаратних підсистем мікроконтролера", size=14, bold=True, color=INK))

    col1_x = 240
    col2_x = 640

    steps = [
        ("1. Живлення та Flash Wait States", "V_CORE регулятори, Flash Latency для частоти ядра", 75, "#eff6ff", NEG),
        ("2. Тактове дерево (Clock Tree)", "HSE/HSI -> PLL Lock -> System Clock -> APB/AHB", 135, "#eff6ff", NEG),
        ("3. Тактування шин (RCC Clocks)", "Clock Gating для портів GPIO, DMA та периферії", 195, "#eff6ff", NEG),
        ("4. Виводи: Засувка -> PinMux", "Запис 1 у BSRR для nCS/nRST -> Режим виводу / AF", 255, "#eff6ff", NEG),
        ("5. Пам'ять та канали DMA", "Буфери в RAM -> Конфігурація та старт DMA Stream", 315, "#eff6ff", NEG),
        ("6. Периферія та переривання", "Очищення прапорців -> CR/Baud -> NVIC -> Enable", 375, "#f0fdf4", FIELD),
        ("7. Зняття Reset зовнішнього чипа", "nRST = 1 -> Пауза t_READY -> Перший обмін на шині", 435, "#f0fdf4", FIELD),
    ]

    for i in range(len(steps) - 1):
        y_curr = steps[i][2] + 18
        y_next = steps[i + 1][2] - 18
        p.append(arrow(col1_x, y_curr, col1_x, y_next, color=LINE, sw=1.5))

    for title_txt, sub_txt, y_pos, bg_col, brd_col in steps:
        p.append(rect(col1_x - 190, y_pos - 18, 380, 36, fill=bg_col, stroke=brd_col, sw=1.4, rx=5))
        p.append(text(col1_x, y_pos - 2, title_txt, size=11, bold=True, color=INK))
        p.append(text(col1_x, y_pos + 12, sub_txt, size=9.5, color=MUTED))

    hazards = [
        (105, "PLL увімкнено до Flash WS", "Збій вибірки команд -> HardFault ядра", POS),
        (225, "Регістри периферії до RCC", "Запис у знеструмлений блок -> Bus Fault", POS),
        (285, "PinMux до запису BSRR=1", "Паразитний імпульс (Glitch) на nCS", POS),
        (345, "Периферія (Enable) до DMA", "Втрата першого байта -> Overrun (ORE)", POS),
        (405, "NVIC до скидання прапорців", "Хибний виклик ISR на порожньому буфері", POS),
    ]

    for y_haz, haz_title, haz_desc, haz_col in hazards:
        p.append(line(col1_x + 190, y_haz, col2_x - 170, y_haz, color=haz_col, sw=1.2, dash="3 2"))
        p.append(rect(col2_x - 170, y_haz - 20, 340, 40, fill="#fef2f2", stroke=haz_col, sw=1.3, rx=4))
        p.append(text(col2_x, y_haz - 4, haz_title, size=10, bold=True, color=haz_col))
        p.append(text(col2_x, y_haz + 11, haz_desc, size=9.5, color=INK))

    # Нижня підсумкова плашка
    p.append(rect(30, 480, 800, 24, fill="#f8fafc", stroke=MUTED, sw=1, rx=4))
    p.append(text(430, 496, "Порушення послідовності на будь-якому рівні призводить до апаратних блокувань або збоїв зв'язку.", size=10, bold=True, color=INK))

    render(os.path.join(OUT, "peripheral-initialization-dependency-graph.svg"), W, H, *p,
           title="Граф залежностей ініціалізації мікроконтролера та периферії")


if __name__ == "__main__":
    fig_power_up_timing()
    fig_dependency_graph()
    print("Generated all figures successfully.")
