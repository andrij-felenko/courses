# -*- coding: utf-8 -*-
"""Фігури для статті pidniattia-taktiv-pid-svii-kvarts («Підняття тактів під свій кварц»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. clock-tree-pipeline: Тракт тактування мікроконтролера ────────────────
def fig_clock_tree_pipeline():
    W, H = 960, 370
    p = []

    # Заголовок блоків
    p.append(text(W / 2.0, 24, "Тракт тактування мікроконтролера: від резонатора до периферії", size=16, bold=True))

    # Джерела ліворуч
    b_hse, _, _ = textbox(100, 80, "HSE (Кварц)\n8–25 МГц", size=12, pad=8, min_w=140,
                          fill="#fdf2f2", stroke=POS, sw=1.5, color=INK, bold=False)
    b_hsi, _, _ = textbox(100, 155, "HSI (Внутр. RC)\n16 МГц (±1%)", size=12, pad=8, min_w=140,
                          fill="#f4f6f8", stroke=LINE, sw=1.2, color=MUTED, bold=False)
    p.extend([b_hse, b_hsi])

    # Вхідний дільник /M
    b_m, _, _ = textbox(250, 80, "Дільник /M\n(вхід 1–2 МГц)", size=12, pad=8, min_w=110,
                        fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK, bold=False)
    p.append(b_m)
    p.append(arrow(170, 80, 195, 80, color=LINE, sw=1.5))

    # PLL контур
    b_pll, _, _ = textbox(410, 80, "PLL (PFD + VCO ×N)\nДіапазон: 100–432 МГц", size=12, pad=10, min_w=170,
                          fill="#eff6ff", stroke=NEG, sw=1.8, color=INK, bold=True)
    p.append(b_pll)
    p.append(arrow(305, 80, 325, 80, color=LINE, sw=1.5))

    # Вихідні дільники
    b_div_p, _, _ = textbox(580, 80, "Дільник /P\n(SYSCLK 168 МГц)", size=11, pad=6, min_w=130,
                            fill="#fdf2f2", stroke=POS, sw=1.5, color=INK, bold=False)
    b_div_q, _, _ = textbox(580, 155, "Дільник /Q\n(USB 48 МГц / SDIO)", size=11, pad=6, min_w=130,
                            fill="#eafaf0", stroke=FIELD, sw=1.2, color=INK, bold=False)
    p.extend([b_div_p, b_div_q])

    p.append(arrow(495, 80, 515, 80, color=LINE, sw=1.5))
    p.append(arrow(495, 95, 515, 145, color=LINE, sw=1.5))

    # Системний мультиплексор SYSCLK
    b_mux, _, _ = textbox(720, 80, "SYSCLK Мультиплексор\n(SW: HSI / HSE / PLL)", size=11, pad=8, min_w=140,
                          fill="#f4f6f8", stroke=LINE, sw=1.5, color=INK, bold=True)
    p.append(b_mux)
    p.append(arrow(645, 80, 650, 80, color=LINE, sw=1.5))
    p.append(arrow(170, 155, 650, 95, color=MUTED, sw=1.2))

    # Шина AHB (HCLK)
    b_ahb, _, _ = textbox(870, 80, "Шина AHB (HCLK)\nЯдро, Flash, DMA", size=11, pad=8, min_w=120,
                          fill="#eff6ff", stroke=NEG, sw=1.5, color=INK, bold=False)
    p.append(b_ahb)
    p.append(arrow(790, 80, 810, 80, color=LINE, sw=1.5))

    # Нижній рівень шин APB1 / APB2
    b_apb1, _, _ = textbox(720, 245, "Шина APB1 (/4)\nPCLK1 = 42 МГц (макс. 45 МГц)\nТаймери TIM2–TIM7 (×2 = 84 МГц)",
                           size=11, pad=8, min_w=240, fill="#fdf2f2", stroke=POS, sw=1.2, color=INK, bold=False)
    b_apb2, _, _ = textbox(360, 245, "Шина APB2 (/2)\nPCLK2 = 84 МГц (макс. 90 МГц)\nТаймери TIM1, TIM8 (×2 = 168 МГц)",
                           size=11, pad=8, min_w=240, fill="#eafaf0", stroke=FIELD, sw=1.2, color=INK, bold=False)
    p.extend([b_apb1, b_apb2])

    p.append(arrow(870, 115, 780, 215, color=LINE, sw=1.5))
    p.append(arrow(850, 115, 450, 215, color=LINE, sw=1.5))

    # Пояснювальний блок унизу
    b_bot, _, _ = textbox(W / 2.0, 325,
                          "Дільник /M формує частоту порівняння 1–2 МГц; VCO множить її до сотень мегагерц.\n"
                          "Дільники шин гарантують безпечні частоти периферії, а множник таймерів (×2) подвоює тактування при APB > 1.",
                          size=11, pad=8, min_w=860, fill="#fcfcfc", stroke="#d1d5db", sw=1.0, color=MUTED)
    p.append(b_bot)

    render(os.path.join(OUT, "clock-tree-pipeline.svg"), W, H, *p)


# ── 2. clock-startup-sequence: Послідовність підняття частоти ───────────────
def fig_clock_startup_sequence():
    W, H = 920, 290
    p = []

    p.append(text(W / 2.0, 24, "Безпечна послідовність підняття робочої частоти мікроконтролера", size=16, bold=True))

    steps = [
        ("1. Живлення & Flash", "Ввімкнути VOS/Overdrive\nВстановити Flash Latency (WS)", POS),
        ("2. Запуск HSE", "HSEON = 1 у RCC_CR\nЧекати HSERDY + таймаут", INK),
        ("3. Налаштування PLL", "Записати M, N, P, Q\nPLLON = 1, чекати PLLRDY", NEG),
        ("4. Дільники шин", "AHB (/1), APB1 (/4), APB2 (/2)\nу регістрі RCC_CFGR", FIELD),
        ("5. Вибір SYSCLK", "SW = PLL, чекати SWS = PLL\nУвімкнути CSS (Clock Security)", POS),
    ]

    n = len(steps)
    box_w = 150
    gap = 24
    total_w = n * box_w + (n - 1) * gap
    start_x = (W - total_w) / 2.0 + box_w / 2.0
    cy = 110

    for i, (title, sub, color) in enumerate(steps):
        cx = start_x + i * (box_w + gap)
        fill_col = "#fdf2f2" if color == POS else ("#eafaf0" if color == FIELD else ("#eff6ff" if color == NEG else FILL))
        stroke_col = color if color != INK else LINE

        b, bw, bh = textbox(cx, cy, f"{title}\n{sub}", size=11, pad=8, min_w=box_w,
                            fill=fill_col, stroke=stroke_col, sw=1.5, color=INK, bold=False)
        p.append(b)

        if i < n - 1:
            ax1 = cx + box_w / 2.0 + 2
            ax2 = cx + box_w / 2.0 + gap - 2
            p.append(arrow(ax1, cy, ax2, cy, color=LINE, sw=1.5))

    b_bot, _, _ = textbox(W / 2.0, 230,
                          "Критичне правило: латентність Flash та напруга ядра (VOS) збільшуються ДО підняття частоти.\n"
                          "При зниженні частоти порядок суворо зворотний: спершу перемикання SYSCLK, а потім зменшення затримок Flash.",
                          size=11, pad=8, min_w=840, fill="#fcfcfc", stroke="#d1d5db", sw=1.0, color=MUTED)
    p.append(b_bot)

    render(os.path.join(OUT, "clock-startup-sequence.svg"), W, H, *p)


# ── 3. flash-wait-states-hazard: Часові затримки Flash пам'яті ──────────────
def fig_flash_wait_states_hazard():
    W, H = 880, 310
    p = []

    p.append(text(W / 2.0, 24, "Механіка затримок читання Flash (Wait States) при підвищенні частоти", size=16, bold=True))

    # Верхня смуга: 0 WS (Аварія)
    b_title_bad, _, _ = textbox(150, 75, "Без затримок (0 WS)\n168 МГц (T = 5.95 нс)", size=11, pad=6, min_w=180,
                                fill="#fdf2f2", stroke=POS, sw=1.5, color=POS, bold=True)
    p.append(b_title_bad)

    p.append(rect(260, 60, 100, 30, fill="#eff6ff", stroke=NEG, sw=1.2))
    p.append(text(310, 79, "Такт 1 (5.95 нс)", size=10, color=INK, bold=False))

    p.append(rect(365, 60, 160, 30, fill="#fee2e2", stroke=POS, sw=1.5))
    p.append(text(445, 79, "Flash ще зчитує комірку...", size=10, color=POS, bold=False))

    p.append(rect(530, 60, 320, 30, fill="#fef2f2", stroke=POS, sw=1.8))
    p.append(text(690, 79, "Ядро забирає шум ──> HardFault (IBUSERR)", size=11, color=POS, bold=True))

    # Нижня смуга: 5 WS (Коректне читання)
    b_title_ok, _, _ = textbox(150, 165, "Із затримками (5 WS)\n168 МГц (T = 5.95 нс)", size=11, pad=6, min_w=180,
                               fill="#eafaf0", stroke=FIELD, sw=1.5, color=FIELD, bold=True)
    p.append(b_title_ok)

    p.append(rect(260, 150, 80, 30, fill="#eff6ff", stroke=NEG, sw=1.2))
    p.append(text(300, 169, "Такт 0 (Адреса)", size=10, color=INK, bold=False))

    p.append(rect(345, 150, 200, 30, fill="#f4f6f8", stroke=LINE, sw=1.2))
    p.append(text(445, 169, "5 тактів очікування WS (29.75 нс)", size=10, color=MUTED, bold=False))

    p.append(rect(550, 150, 300, 30, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(700, 169, "Дані зафіксовані ──> Валідна інструкція", size=11, color=FIELD, bold=True))

    # Нижній висновок
    b_bot, _, _ = textbox(W / 2.0, 250,
                          "Час доступу матриці Flash становить 25–30 нс. Якщо процесор звертається до пам'яті швидше, ніж завершиться\n"
                          "перехідний процес у чутливих підсилювачах, на шину інструкцій потрапляє сміття, що викликає апаратний збій.",
                          size=11, pad=8, min_w=840, fill="#fcfcfc", stroke="#d1d5db", sw=1.0, color=MUTED)
    p.append(b_bot)

    render(os.path.join(OUT, "flash-wait-states-hazard.svg"), W, H, *p)


# ── 4. clock-security-system-nmi: Аварійне перемикання CSS ─────────────────
def fig_clock_security_system_nmi():
    W, H = 900, 300
    p = []

    p.append(text(W / 2.0, 24, "Аварійне перемикання Clock Security System (CSS) при зриві генерації", size=16, bold=True))

    b1, _, _ = textbox(120, 100, "Зовнішній кварц (HSE)\nЗрив коливань:\nтріщина, обрив, удар",
                       size=11, pad=8, min_w=170, fill="#fdf2f2", stroke=POS, sw=1.5, color=INK, bold=False)
    p.append(b1)

    b2, _, _ = textbox(360, 100, "Апаратний детектор CSS\nRC-таймаут виявив зупинку:\n1. SYSCLK ──> HSI (16 МГц)\n2. PLLON ──> 0 (Вимкнено)",
                       size=11, pad=8, min_w=210, fill="#eff6ff", stroke=NEG, sw=1.5, color=INK, bold=False)
    p.append(b2)
    p.append(arrow(205, 100, 255, 100, color=POS, sw=1.8))

    b3, _, _ = textbox(660, 100, "Генерація NMI винятку\nОбробник NMI_Handler():\n1. Безпечний стан (стоп ШІМ)\n2. Очищення CSSC\n3. Сповіщення або рестарт",
                       size=11, pad=8, min_w=240, fill="#eafaf0", stroke=FIELD, sw=1.5, color=INK, bold=False)
    p.append(b3)
    p.append(arrow(465, 100, 540, 100, color=NEG, sw=1.8))

    b_bot, _, _ = textbox(W / 2.0, 230,
                          "CSS не дає процесору зависнути намертво при фізичній втраті тактового сигналу HSE.\n"
                          "Апаратне перемикання на внутрішній HSI відбувається миттєво, а переривання NMI не можна заблокувати програмно.",
                          size=11, pad=8, min_w=840, fill="#fcfcfc", stroke="#d1d5db", sw=1.0, color=MUTED)
    p.append(b_bot)

    render(os.path.join(OUT, "clock-security-system-nmi.svg"), W, H, *p)


if __name__ == "__main__":
    fig_clock_tree_pipeline()
    fig_clock_startup_sequence()
    fig_flash_wait_states_hazard()
    fig_clock_security_system_nmi()
    print("Всі 4 фігури згенеровано успішно.")
