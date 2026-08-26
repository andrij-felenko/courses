# -*- coding: utf-8 -*-
"""Фігури до теми «Розбір справжнього падіння».
Запуск: python figs.py
"""
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Діаграма Ісікави (Fishbone Diagram) для аварії вбудованої системи ────
def fig_fishbone_rca():
    W, H = 960, 480
    f = []

    f.append(text(W / 2, 26, "Діаграма Ісікави (Fishbone): комплексний аналіз причин аварії приводу",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 45, "структуризація 6 векторів відмови: від апаратних явищ до дефектів таймерної арифметики",
                  11.5, MUTED, "middle", italic=True))

    # Головний хребет
    spine_y = 260
    f.append(arrow(40, spine_y, 740, spine_y, color=LINE, sw=3.0))

    # Головний блок проблеми (голова риби)
    head_box, hw, hh = textbox(850, spine_y, "Аварійне вимкнення\nприводу і падіння\nна 65.5 с роботи",
                               size=12.5, pad=10, fill="#fdecea", stroke=POS, sw=2.0, color=POS, bold=True)
    f.append(head_box)

    # 3 верхні кістки (нахил 60 град вправо-вниз)
    # 1. Прошивка / Код
    # 2. Живлення / Схематика
    # 3. Протокол / Зв'язок
    top_x_anchors = [180, 390, 600]
    top_y_top = 80

    # Ребро 1: Прошивка / Код
    f.append(line(top_x_anchors[0] - 60, top_y_top, top_x_anchors[0] + 50, spine_y, color=LINE, sw=2.0))
    cat1, _, _ = textbox(top_x_anchors[0] - 70, top_y_top - 5, "Прошивка / Код", size=12.0, pad=6,
                         fill="#fbe9e7", stroke=POS, sw=1.5, color=POS, bold=True)
    f.append(cat1)
    # Дрібні підребра
    f.append(line(top_x_anchors[0] - 80, 125, top_x_anchors[0] - 25, 125, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[0] - 85, 122, "Integer promotion (int16->int32)", 10.0, INK, "end"))
    f.append(line(top_x_anchors[0] - 60, 170, top_x_anchors[0] - 2, 170, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[0] - 65, 167, "Порівняння (now > last + dt)", 10.0, INK, "end"))
    f.append(line(top_x_anchors[0] - 30, 215, top_x_anchors[0] + 25, 215, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[0] - 35, 212, "Блокуючий лог у критичній задачі", 10.0, INK, "end"))

    # Ребро 2: Живлення / Схематика
    f.append(line(top_x_anchors[1] - 60, top_y_top, top_x_anchors[1] + 50, spine_y, color=LINE, sw=2.0))
    cat2, _, _ = textbox(top_x_anchors[1] - 70, top_y_top - 5, "Живлення / Схематика", size=12.0, pad=6,
                         fill="#fff3e0", stroke="#e67e22", sw=1.5, color="#d35400", bold=True)
    f.append(cat2)
    f.append(line(top_x_anchors[1] - 80, 125, top_x_anchors[1] - 25, 125, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[1] - 85, 122, "Кидок зворотної ЕРС інвертора", 10.0, INK, "end"))
    f.append(line(top_x_anchors[1] - 60, 170, top_x_anchors[1] - 2, 170, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[1] - 65, 167, "Просадка VDD нижче 2.7 В (BOR)", 10.0, INK, "end"))
    f.append(line(top_x_anchors[1] - 30, 215, top_x_anchors[1] + 25, 215, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[1] - 35, 212, "Малий запас фільтруючих ємностей", 10.0, INK, "end"))

    # Ребро 3: Протокол / Зв'язок
    f.append(line(top_x_anchors[2] - 60, top_y_top, top_x_anchors[2] + 50, spine_y, color=LINE, sw=2.0))
    cat3, _, _ = textbox(top_x_anchors[2] - 70, top_y_top - 5, "Протокол / Зв'язок", size=12.0, pad=6,
                         fill="#eaf0fd", stroke=NEG, sw=1.5, color=NEG, bold=True)
    f.append(cat3)
    f.append(line(top_x_anchors[2] - 80, 125, top_x_anchors[2] - 25, 125, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[2] - 85, 122, "Хибний таймаут Heartbeat (50 мс)", 10.0, INK, "end"))
    f.append(line(top_x_anchors[2] - 60, 170, top_x_anchors[2] - 2, 170, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[2] - 65, 167, "Панічний скид сесії зв'язку", 10.0, INK, "end"))
    f.append(line(top_x_anchors[2] - 30, 215, top_x_anchors[2] + 25, 215, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[2] - 35, 212, "Переповнення черги телеметрії", 10.0, INK, "end"))

    # 3 нижні кістки (нахил 60 град вправо-вгору)
    # 4. Таймери / Кристал
    # 5. Середовище / Механіка
    # 6. Процес / Тестування
    bot_y_bot = 440

    # Ребро 4: Таймери / Кристал
    f.append(line(top_x_anchors[0] - 60, bot_y_bot, top_x_anchors[0] + 50, spine_y, color=LINE, sw=2.0))
    cat4, _, _ = textbox(top_x_anchors[0] - 70, bot_y_bot + 5, "Таймери / Кристал", size=12.0, pad=6,
                         fill="#e9f7ef", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    f.append(cat4)
    f.append(line(top_x_anchors[0] - 80, 395, top_x_anchors[0] - 25, 395, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[0] - 85, 398, "16-бітний таймер SysTick / TIM", 10.0, INK, "end"))
    f.append(line(top_x_anchors[0] - 60, 350, top_x_anchors[0] - 2, 350, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[0] - 65, 353, "Перехід 65535 -> 0 (Rollover)", 10.0, INK, "end"))
    f.append(line(top_x_anchors[0] - 30, 305, top_x_anchors[0] + 25, 305, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[0] - 35, 308, "Несинхронні шкали мікросекунд", 10.0, INK, "end"))

    # Ребро 5: Середовище / Механіка
    f.append(line(top_x_anchors[1] - 60, bot_y_bot, top_x_anchors[1] + 50, spine_y, color=LINE, sw=2.0))
    cat5, _, _ = textbox(top_x_anchors[1] - 70, bot_y_bot + 5, "Середовище / Механіка", size=12.0, pad=6,
                         fill="#f4f6f8", stroke="#7f8c8d", sw=1.5, color="#2c3e50", bold=True)
    f.append(cat5)
    f.append(line(top_x_anchors[1] - 80, 395, top_x_anchors[1] - 25, 395, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[1] - 85, 398, "Вібрація силової рами", 10.0, INK, "end"))
    f.append(line(top_x_anchors[1] - 60, 350, top_x_anchors[1] - 2, 350, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[1] - 65, 353, "Нагрів ключів MOSFET у польоті", 10.0, INK, "end"))
    f.append(line(top_x_anchors[1] - 30, 305, top_x_anchors[1] + 25, 305, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[1] - 35, 308, "Імпульсні перешкоди від ШІМ", 10.0, INK, "end"))

    # Ребро 6: Процес / Тестування
    f.append(line(top_x_anchors[2] - 60, bot_y_bot, top_x_anchors[2] + 50, spine_y, color=LINE, sw=2.0))
    cat6, _, _ = textbox(top_x_anchors[2] - 70, bot_y_bot + 5, "Процес / Тестування", size=12.0, pad=6,
                         fill="#f3e5f5", stroke="#8e44ad", sw=1.5, color="#8e44ad", bold=True)
    f.append(cat6)
    f.append(line(top_x_anchors[2] - 80, 395, top_x_anchors[2] - 25, 395, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[2] - 85, 398, "Лабораторні тести тривали < 30 с", 10.0, INK, "end"))
    f.append(line(top_x_anchors[2] - 60, 350, top_x_anchors[2] - 2, 350, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[2] - 65, 353, "Відсутній тест на переповнення часу", 10.0, INK, "end"))
    f.append(line(top_x_anchors[2] - 30, 305, top_x_anchors[2] + 25, 305, color=MUTED, sw=1.2))
    f.append(text(top_x_anchors[2] - 35, 308, "Не було Hardware-in-the-Loop тестів", 10.0, INK, "end"))

    render(os.path.join(IMG, "rca-fishbone-diagram.svg"), W, H, *f)


# ── 2. Хронологічний каскад відмови (Timeline Cascade) ──────────────────────
def fig_timeline_cascade():
    W, H = 940, 440
    f = []

    f.append(text(W / 2, 26, "Хронологія аварійного каскаду: як 1 мілісекунда поклала систему",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 45, "посекундна розгортка від переповнення лічильника до просідання шини та апаратного ресету",
                  11.5, MUTED, "middle", italic=True))

    stages = [
        ("t = 65.500 с", "Штатний режим",
         "Лічильник timer_ms = 65500.\nПакет зв'язку отримано.\nМотори тримають оберти,\nструм 14 А, VDD = 3.30 В.",
         "#e9f7ef", FIELD),
        ("t = 65.535 с", "Переповнення таймера",
         "timer_ms переходить у 0x0000.\n(uint16_t now - last_hb)\nчерез int promotion дає\nвід'ємне число -> хибний таймаут!",
         "#fff3e0", "#e67e22"),
        ("t = 65.537 с", "Захлинання буфера",
         "Автомат зв'язку фіксує аварію.\nВиклик panic_dump() шле лог у\nблокуючий UART (115200 бод).\nЧерга RTOS заблокована.",
         "#fdecea", POS),
        ("t = 65.542 с", "Голодування задачі ШІМ",
         "Потік стабілізації мотора\nпропускає 3 цикли (30 мс).\nДрайвер мотора вимикає\nключі на повному ходу.",
         "#fdecea", POS),
        ("t = 65.545 с", "Кидок ЕРС та Brownout",
         "Миттєве зняття струму 14 А ->\nіндуктивний викид на дротах.\nПросадка VDD до 2.45 В.\nBOD перезавантажує MCU!",
         "#fbe9e7", POS),
    ]

    x_step = 172
    start_x = 26
    box_w = 160

    for i, (t_stamp, title, desc, fill_col, border_col) in enumerate(stages):
        cur_x = start_x + i * x_step

        # Часова мітка зверху
        f.append(rect(cur_x, 70, box_w, 30, fill=fill_col, stroke=border_col, sw=1.5, rx=5))
        f.append(text(cur_x + box_w / 2, 90, t_stamp, 12.0, border_col, "middle", bold=True))

        # Стрілка вниз до блоку
        f.append(arrow(cur_x + box_w / 2, 100, cur_x + box_w / 2, 120, color=border_col, sw=1.5))

        # Основний блок події
        f.append(rect(cur_x, 125, box_w, 230, fill="#ffffff", stroke=border_col, sw=1.4, rx=6))
        f.append(rect(cur_x, 125, box_w, 28, fill=fill_col, stroke=border_col, sw=1.2, rx=6))
        f.append(text(cur_x + box_w / 2, 144, title, 11.0, border_col, "middle", bold=True))

        lines = desc.split("\n")
        for line_idx, line_str in enumerate(lines):
            f.append(text(cur_x + box_w / 2, 175 + line_idx * 20, line_str, 10.0, INK, "middle"))

        # Стрілка переходу до наступного кроку
        if i < len(stages) - 1:
            f.append(arrow(cur_x + box_w, 230, cur_x + x_step, 230, color=POS, sw=2.0))

    # Нижній підсумок
    f.append(rect(start_x, 375, W - 2 * start_x, 48, fill="#f4f6f8", stroke="#bdc3c7", sw=1.5, rx=6))
    f.append(text(W / 2, 396, "Першопричина: дефект 16-бітної таймерної арифметики при переповненні.", 11.5, POS, "middle", bold=True))
    f.append(text(W / 2, 412, "Симптом (падіння мотора й ресет) — лише остання ланка каскадної реакції заліза на програмний збій.", 10.5, MUTED, "middle"))

    render(os.path.join(IMG, "rca-timeline-cascade.svg"), W, H, *f)


# ── 3. Арифметика переповнення: Модульне віднімання vs Signed Promotion ─────
def fig_timer_arithmetic():
    W, H = 920, 420
    f = []

    f.append(text(W / 2, 26, "Анатомія пастки переповнення 16-бітного таймера в C/C++",
                  15.5, INK, "middle", bold=True))
    f.append(text(W / 2, 45, "порівняння коректного модульного віднімання та катастрофи неявного приведення типів",
                  11.5, MUTED, "middle", italic=True))

    col_w = 270
    gap = 26
    lefts = [24, 24 + col_w + gap, 24 + 2 * (col_w + gap)]

    # Колонка 1: Безпечне модульне віднімання uint16
    x1 = lefts[0]
    f.append(rect(x1, 68, col_w, 320, fill="#ffffff", stroke=FIELD, sw=1.5, rx=8))
    f.append(rect(x1, 68, col_w, 36, fill="#e9f7ef", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(x1 + col_w / 2, 91, "1. Безпечне: (uint16_t)(now - last)", 12.0, FIELD, "middle", bold=True))

    f.append(text(x1 + 14, 125, "Стан лічильника:", 11.0, MUTED, "start", bold=True))
    f.append(text(x1 + 14, 145, "• last_heartbeat = 65530 (0xFFFA)", 10.5, INK, "start"))
    f.append(text(x1 + 14, 165, "• now = 10 (0x000A) [після wrap]", 10.5, INK, "start"))
    f.append(text(x1 + 14, 185, "• TIMEOUT_MS = 100", 10.5, INK, "start"))

    f.append(rect(x1 + 10, 205, col_w - 20, 70, fill="#f4f6f8", stroke="#bdc3c7", sw=1.2, rx=5))
    f.append(text(x1 + col_w / 2, 225, "uint16_t diff = (uint16_t)(10 - 65530);", 10.0, FIELD, "middle", bold=True))
    f.append(text(x1 + col_w / 2, 245, "0x000A - 0xFFFA mod 2^16 = 16", 10.5, INK, "middle"))
    f.append(text(x1 + col_w / 2, 263, "16 <= 100 -> Таймаут НЕ настав", 10.0, FIELD, "middle", bold=True))

    f.append(rect(x1 + 10, 290, col_w - 20, 85, fill="#e9f7ef", stroke=FIELD, sw=1.2, rx=5))
    f.append(text(x1 + col_w / 2, 310, "Результат: ПРАВИЛЬНО", 11.5, FIELD, "middle", bold=True))
    f.append(text(x1 + col_w / 2, 330, "Беззнакова арифметика за модулем", 10.0, INK, "middle"))
    f.append(text(x1 + col_w / 2, 348, "ідеально обробляє перехід через нуль.", 10.0, INK, "middle"))
    f.append(text(x1 + col_w / 2, 364, "Зв'язок не переривається.", 10.0, FIELD, "middle"))

    # Колонка 2: Пастка Integer Promotion у 32-бітному CPU
    x2 = lefts[1]
    f.append(rect(x2, 68, col_w, 320, fill="#ffffff", stroke=POS, sw=1.5, rx=8))
    f.append(rect(x2, 68, col_w, 36, fill="#fdecea", stroke=POS, sw=1.5, rx=8))
    f.append(text(x2 + col_w / 2, 91, "2. Пастка C99: now - last > TIMEOUT", 12.0, POS, "middle", bold=True))

    f.append(text(x2 + 14, 125, "Неявне приведення до int32:", 11.0, MUTED, "start", bold=True))
    f.append(text(x2 + 14, 145, "• (int)now = 10", 10.5, INK, "start"))
    f.append(text(x2 + 14, 165, "• (int)last = 65530", 10.5, INK, "start"))
    f.append(text(x2 + 14, 185, "• 10 - 65530 = -65520 (знакове)", 10.5, POS, "start"))

    f.append(rect(x2 + 10, 205, col_w - 20, 70, fill="#fdecea", stroke=POS, sw=1.2, rx=5))
    f.append(text(x2 + col_w / 2, 225, "if ((now - last) > (uint32_t)TIMEOUT)", 10.0, POS, "middle", bold=True))
    f.append(text(x2 + col_w / 2, 245, "(uint32_t)(-65520) = 4 294 901 776", 10.0, POS, "middle", bold=True))
    f.append(text(x2 + col_w / 2, 263, "4.29 млрд > 100 -> ХИБНИЙ ТАЙМАУТ!", 10.0, POS, "middle", bold=True))

    f.append(rect(x2 + 10, 290, col_w - 20, 85, fill="#fdecea", stroke=POS, sw=1.2, rx=5))
    f.append(text(x2 + col_w / 2, 310, "Результат: КАТАСТРОФА", 11.5, POS, "middle", bold=True))
    f.append(text(x2 + col_w / 2, 330, "Знаковий мінус перетворюється", 10.0, INK, "middle"))
    f.append(text(x2 + col_w / 2, 348, "на гігантське число 4.29 млрд.", 10.0, INK, "middle"))
    f.append(text(x2 + col_w / 2, 364, "Система негайно вмикає аварію.", 10.0, POS, "middle"))

    # Колонка 3: Пастка порівняння "now > last + TIMEOUT"
    x3 = lefts[2]
    f.append(rect(x3, 68, col_w, 320, fill="#ffffff", stroke="#d35400", sw=1.5, rx=8))
    f.append(rect(x3, 68, col_w, 36, fill="#fff3e0", stroke="#e67e22", sw=1.5, rx=8))
    f.append(text(x3 + col_w / 2, 91, "3. Пастка: now > last + TIMEOUT", 12.0, "#d35400", "middle", bold=True))

    f.append(text(x3 + 14, 125, "Розрахунок точки дедлайну:", 11.0, MUTED, "start", bold=True))
    f.append(text(x3 + 14, 145, "• last = 65530, TIMEOUT = 100", 10.5, INK, "start"))
    f.append(text(x3 + 14, 165, "• last + TIMEOUT = 65630 (в int)", 10.5, INK, "start"))
    f.append(text(x3 + 14, 185, "• now = 10 (після скиду)", 10.5, INK, "start"))

    f.append(rect(x3 + 10, 205, col_w - 20, 70, fill="#fff8e1", stroke="#f39c12", sw=1.2, rx=5))
    f.append(text(x3 + col_w / 2, 225, "if (now > deadline) { ... }", 10.0, "#d35400", "middle", bold=True))
    f.append(text(x3 + col_w / 2, 245, "10 > 65630 -> FALSE", 10.5, INK, "middle"))
    f.append(text(x3 + col_w / 2, 263, "Таймаут «заснув» на 65.5 секунд!", 10.0, "#d35400", "middle", bold=True))

    f.append(rect(x3 + 10, 290, col_w - 20, 85, fill="#fff3e0", stroke="#e67e22", sw=1.2, rx=5))
    f.append(text(x3 + col_w / 2, 310, "Результат: СЛІПОТА СТОРОЖА", 11.5, "#d35400", "middle", bold=True))
    f.append(text(x3 + col_w / 2, 330, "Умова не спрацює, доки лічильник", 10.0, INK, "middle"))
    f.append(text(x3 + col_w / 2, 348, "не зробить повне коло 65 536 мс.", 10.0, INK, "middle"))
    f.append(text(x3 + col_w / 2, 364, "Захист повністю відключено.", 10.0, "#d35400", "middle"))

    render(os.path.join(IMG, "timer-overflow-arithmetic.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fishbone_rca()
    fig_timeline_cascade()
    fig_timer_arithmetic()
    print("All figures generated successfully.")
