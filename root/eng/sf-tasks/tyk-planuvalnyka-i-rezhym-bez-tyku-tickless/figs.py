# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми 'Тик планувальника й режим без тику (tickless)'"""

import os
import sys

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT_DIR, exist_ok=True)


def fig_tick_timeline():
    """Фігура 1: Порівняння періодичного SysTick (1000 Гц) та безтикового режиму (Tickless Idle)."""
    w, h = 880, 320
    frags = []

    # Заголовок блоку 1
    frags.append(text(20, 26, "Класичний періодичний тик (SysTick 1000 Гц):", size=13, bold=True, anchor="start", color=INK))

    # Пояснення над віссю
    frags.append(textbox(450, 48, "Постійні переривання ISR будять ядро щомілісекунди, навіть коли всі задачі сплять", size=11, fill="#fff3cd", stroke="#e67e22", color="#7d4a00")[0])

    # Верхня шкала: Класичний SysTick
    axis_y1 = 105
    frags.append(arrow(50, axis_y1, 840, axis_y1, color=LINE, sw=2))
    frags.append(text(845, axis_y1 + 4, "t", size=13, italic=True, bold=True, anchor="start"))

    # Маркери тиків кожні 65 px
    for i in range(11):
        x = 80 + i * 68
        frags.append(line(x, axis_y1 - 12, x, axis_y1 + 12, color=POS, sw=2))
        frags.append(rect(x - 5, axis_y1 - 24, 10, 14, fill="#fdecea", stroke=POS, sw=1.2, rx=2))
        frags.append(text(x, axis_y1 + 25, "%d мс" % i, size=11, color=MUTED, anchor="middle"))

    # Заголовок блоку 2
    frags.append(text(20, 165, "Безтиковий режим (Tickless Idle з LPTIM):", size=13, bold=True, anchor="start", color=INK))

    # Нижня шкала: Tickless Idle
    axis_y2 = 220
    frags.append(arrow(50, axis_y2, 840, axis_y2, color=LINE, sw=2))
    frags.append(text(845, axis_y2 + 4, "t", size=13, italic=True, bold=True, anchor="start"))

    # Початок сну (зупинка SysTick)
    frags.append(line(80, axis_y2 - 14, 80, axis_y2 + 14, color=FIELD, sw=2.5))
    frags.append(text(80, axis_y2 + 25, "0 мс", size=11, color=MUTED, anchor="middle"))
    frags.append(text(80, axis_y2 - 20, "Вхід у сон", size=11, bold=True, color=FIELD, anchor="middle"))

    # Глибокий сон — безперервний інтервал
    sleep_w = 10 * 68
    frags.append(rect(82, axis_y2 - 10, sleep_w - 4, 20, fill="#e8f8f5", stroke=FIELD, sw=1.5, rx=3))
    frags.append(text(80 + sleep_w / 2, axis_y2 + 4, "Глибокий сон (Stop Mode, 1.5 мкА) — SysTick зупинено, працює LPTIM", size=11, color="#0e6251", bold=True, anchor="middle"))

    # Пробудження на 10-му мс (LPTIM Match)
    wake_x = 80 + sleep_w
    frags.append(line(wake_x, axis_y2 - 14, wake_x, axis_y2 + 14, color=POS, sw=2.5))
    frags.append(text(wake_x, axis_y2 + 25, "10 мс", size=11, color=MUTED, anchor="middle"))
    frags.append(text(wake_x, axis_y2 - 20, "Пробудження", size=11, bold=True, color=POS, anchor="middle"))

    # Підсумок внизу
    frags.append(textbox(450, 285, "Планувальник спить 10 мс одним відрізком та одноразово викликає vTaskStepTick(10)", size=11, fill="#eaf2f8", stroke=NEG, color=NEG, bold=True)[0])

    render(os.path.join(OUT_DIR, "tick-timeline.svg"), w, h, *frags)


def fig_energy_profile():
    """Фігура 2: Профіль струму мікроконтролера під час виходу з глибокого сну."""
    w, h = 880, 300
    frags = []

    # Осі I (mA) та t
    frags.append(arrow(80, 235, 80, 30, color=LINE, sw=2))
    frags.append(text(75, 25, "I, струм", size=13, bold=True, anchor="end"))
    frags.append(arrow(80, 235, 840, 235, color=LINE, sw=2))
    frags.append(text(845, 239, "t", size=13, italic=True, bold=True, anchor="start"))

    # Рівні струму (пунктир)
    frags.append(line(80, 75, 820, 75, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(70, 79, "15 мА (Active 80 MHz)", size=11, color=POS, anchor="end", bold=True))

    frags.append(line(80, 140, 820, 140, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(70, 144, "3.5 мА (WFI Sleep)", size=11, color="#e67e22", anchor="end"))

    frags.append(line(80, 220, 820, 220, color=MUTED, sw=1, dash="3,3"))
    frags.append(text(70, 224, "1.5 мкА (Stop)", size=11, color=FIELD, anchor="end", bold=True))

    # Фази профілю струму
    # Сон (80 -> 340, y=220), Пробудження (340 -> 420, y=220->75), Робота (420 -> 640, y=75), Спад (640 -> 660, y=75->220), Сон (660 -> 820)
    curve = '<path d="M 85 220 L 340 220 L 370 150 L 410 85 L 425 75 L 640 75 L 660 220 L 820 220" fill="none" stroke="#2457d6" stroke-width="2.5"/>'
    frags.append(curve)

    # Підписи фаз - розташовані чітко поза лініями
    frags.append(fitbox(100, 155, 220, 48, "Глибокий сон (Stop)\nЯдро й PLL зупинені, I = 1.5 мкА", size=11, fill="#eafaf1", stroke=FIELD, color="#1e8449"))

    frags.append(fitbox(310, 40, 175, 40, "Затримка пробудження:\nстарт HSI/PLL (~80 мкс)", size=10, fill="#fef9e7", stroke="#f39c12", color="#7d6608"))

    frags.append(fitbox(510, 36, 210, 48, "Активна робота задачі:\nобробка події та планувальник\n(I = 15 мА)", size=11, fill="#fdecea", stroke=POS, color=POS, bold=True))

    # Висновок внизу
    frags.append(textbox(460, 270, "Ціна пробудження: кожне перемикання витрачає енергію на перезапуск PLL і живлення ядра", size=11, fill=FILL, stroke=LINE, color=INK)[0])

    render(os.path.join(OUT_DIR, "energy-profile.svg"), w, h, *frags)


def fig_tickless_state():
    """Фігура 3: Послідовність переходу ядра в глибокий сон із зупинкою SysTick та запуском LPTIM."""
    w, h = 880, 260
    frags = []

    steps = [
        ("1. Idle Task", "Планувальник виявляє,\nщо всі задачі заблоковані;\nобчислює N тактів сну"),
        ("2. Блокування", "portDISABLE_INTERRUPTS()\nУсунення стану перегонів\nперед налаштуванням"),
        ("3. Налаштування", "Зупинка SysTick;\nПрограмування LPTIM\nна період N тактів"),
        ("4. Глибокий сон", "__WFI() / Stop Mode;\nВимкнення PLL та HCLK;\nЖивлення LPTIM від LSE"),
        ("5. Пробудження", "Старт PLL;\nvTaskStepTick(N);\nВідновлення SysTick"),
    ]

    box_w = 150
    box_h = 130
    gap = 24
    start_x = 20

    for i, (title, desc) in enumerate(steps):
        bx = start_x + i * (box_w + gap)
        by = 45

        if i == 0:
            fill_c, stroke_c = "#ebf5fb", "#2980b9"
        elif i == 1:
            fill_c, stroke_c = "#fef9e7", "#f39c12"
        elif i == 2:
            fill_c, stroke_c = "#eaf2f8", "#3498db"
        elif i == 3:
            fill_c, stroke_c = "#e8f8f5", FIELD
        else:
            fill_c, stroke_c = "#fdecea", POS

        box_svg = fitbox(bx, by, box_w, box_h, title + "\n\n" + desc, size=11, fill=fill_c, stroke=stroke_c, color=INK, bold=False)
        frags.append(box_svg)

        if i < len(steps) - 1:
            ax1 = bx + box_w
            ay = by + box_h / 2
            ax2 = ax1 + gap
            frags.append(arrow(ax1 + 2, ay, ax2 - 2, ay, color=LINE, sw=2))

    frags.append(textbox(440, 225, "Апаратна послідовність гарантує відсутність втрати часу та пропущених переривань", size=11, fill="#f4f6f8", stroke=LINE, color=INK, bold=True)[0])

    render(os.path.join(OUT_DIR, "tickless-state.svg"), w, h, *frags)


def fig_wakeup_compensation():
    """Фігура 4: Компенсація системного часу vTaskStepTick при передчасному асинхронному пробудженні."""
    w, h = 880, 280
    frags = []

    # Верхня шкала: Планове пробудження (LPTIM Timeout)
    frags.append(text(20, 26, "Сценарій А: Планове пробудження (таймаут LPTIM)", size=13, bold=True, anchor="start", color=INK))
    frags.append(arrow(40, 65, 820, 65, color=LINE, sw=1.8))

    frags.append(line(60, 55, 60, 75, color=FIELD, sw=2))
    frags.append(text(60, 48, "t = 0", size=11, bold=True, color=FIELD, anchor="middle"))

    frags.append(line(660, 55, 660, 75, color=POS, sw=2))
    frags.append(text(660, 48, "t = N (план)", size=11, bold=True, color=POS, anchor="middle"))

    frags.append(rect(62, 58, 596, 14, fill="#e8f8f5", stroke=FIELD, sw=1.2, rx=2))
    frags.append(text(360, 69, "Сон тривав повні N тактів → виклик vTaskStepTick(N)", size=11, color="#0e6251", bold=True, anchor="middle"))

    # Нижня шкала: Передчасне асинхронне пробудження (EXTI / GPIO / UART)
    frags.append(text(20, 125, "Сценарій Б: Передчасне асинхронне пробудження (EXTI / UART / Давач)", size=13, bold=True, anchor="start", color=INK))
    frags.append(arrow(40, 175, 820, 175, color=LINE, sw=1.8))

    frags.append(line(60, 165, 60, 185, color=FIELD, sw=2))
    frags.append(text(60, 158, "t = 0", size=11, bold=True, color=FIELD, anchor="middle"))

    # Передчасне переривання на t = M (M < N)
    frags.append(line(360, 160, 360, 190, color=POS, sw=2.5))
    frags.append(text(360, 153, "t = M (асинхронна подія)", size=11, bold=True, color=POS, anchor="middle"))

    # Запланований кінець N (пунктир)
    frags.append(line(660, 165, 660, 185, color=MUTED, sw=1.5, dash="3,3"))
    frags.append(text(660, 158, "t = N (не досягнуто)", size=11, color=MUTED, anchor="middle"))

    # Фактичний інтервал сну
    frags.append(rect(62, 168, 296, 14, fill="#fef9e7", stroke="#f39c12", sw=1.2, rx=2))
    frags.append(text(210, 179, "Фактичний сон M тактів", size=11, color="#7d6608", bold=True, anchor="middle"))

    # Скасований залишок
    frags.append(rect(362, 168, 296, 14, fill="#f2f3f4", stroke=MUTED, sw=1, rx=2))
    frags.append(text(510, 179, "Недоспаний залишок (N − M)", size=11, color=MUTED, anchor="middle"))

    # Блок алгоритму компенсації
    frags.append(textbox(440, 240, "Зчитування LPTIM_CNT → обчислення M = LPTIM_CNT / counts_per_tick → vTaskStepTick(M) → рестарт SysTick", size=11, fill="#eaf2f8", stroke=NEG, color=NEG, bold=True)[0])

    render(os.path.join(OUT_DIR, "wakeup-compensation.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_tick_timeline()
    fig_energy_profile()
    fig_tickless_state()
    fig_wakeup_compensation()
    print("Фігури успішно згенеровано.")
