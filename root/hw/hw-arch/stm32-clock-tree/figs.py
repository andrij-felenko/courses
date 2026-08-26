# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. stm32-clock-tree-overview: загальне дерево тактування ──────────────────
def fig_clock_tree_overview():
    W, H = 880, 520
    p = []

    # Джерела ліворуч (x = 75)
    src_x = 75
    b_hsi, _, _ = textbox(src_x, 90, "HSI RC\n16 МГц", size=10.5, bold=True, fill="#f4f6f8", stroke=INK, pad=8)
    b_hse, _, _ = textbox(src_x, 165, "HSE кварц\n4–26 МГц", size=10.5, bold=True, fill="#eaf0fd", stroke=NEG, pad=8)
    b_lsi, _, _ = textbox(src_x, 395, "LSI RC\n32 кГц", size=10.5, bold=True, fill="#f4f6f8", stroke=INK, pad=8)
    b_lse, _, _ = textbox(src_x, 465, "LSE кварц\n32.768 кГц", size=10.5, bold=True, fill="#eaf0fd", stroke=NEG, pad=8)
    p.extend([b_hsi, b_hse, b_lsi, b_lse])

    # Лінії від джерел до комутаторів
    p.append(line(src_x + 46, 90, 160, 90, color=INK, sw=1.5))
    p.append(line(src_x + 54, 165, 160, 165, color=NEG, sw=1.5))
    p.append(line(160, 90, 160, 150, color=INK, sw=1.5))

    # Мультиплексор входу PLL (cx = 190, cy = 150)
    p.append(arrow(160, 150, 168, 150, color=LINE, sw=1.5))
    pll_mux, _, _ = textbox(190, 150, "MUX\nPLL", size=10, bold=True, fill="#fff9e6", stroke="#e0a800", pad=5)
    p.append(pll_mux)

    # Вузол PLL (cx = 330, cy = 150)
    p.append(arrow(212, 150, 238, 150, color=LINE, sw=1.5))
    pll_box, _, _ = textbox(330, 150, "Головний PLL\n/M · N  (VCO: 100–432 МГц)\n/P (SYSCLK)  |  /Q (48 МГц)", size=10, bold=True, fill="#fdecea", stroke=POS, pad=9)
    p.append(pll_box)

    # Лінія USB 48 MHz від PLL /Q вниз
    p.append(line(375, 185, 375, 320, color=POS, sw=1.5))
    p.append(arrow(375, 320, 480, 320, color=POS, sw=1.5))
    b_usb, _, _ = textbox(575, 320, "USB OTG / SDIO / RNG\n(строго 48 МГц)", size=10, bold=True, fill="#d4edda", stroke=FIELD, pad=8)
    p.append(b_usb)

    # Мультиплексор вибору SYSCLK (cx = 480, cy = 115)
    p.append(line(src_x + 46, 75, 455, 75, color=INK, sw=1.2, dash="3,3")) # HSI bypass
    p.append(line(src_x + 54, 180, 440, 180, color=NEG, sw=1.2, dash="3,3")) # HSE bypass
    p.append(line(440, 180, 440, 125, color=NEG, sw=1.2, dash="3,3"))
    p.append(arrow(422, 135, 456, 122, color=POS, sw=1.5)) # PLL_P output

    sys_mux, _, _ = textbox(480, 115, "SW MUX\nSYSCLK", size=9.5, bold=True, fill="#fff9e6", stroke="#e0a800", pad=5)
    p.append(sys_mux)

    # AHB Prescaler (cx = 585, cy = 115)
    p.append(arrow(504, 115, 528, 115, color=LINE, sw=1.8))
    ahb_box, _, _ = textbox(585, 115, "AHB Prescaler\n/1, /2, /4..512\nHCLK (до 168 МГц)", size=10, bold=True, fill="#eaf0fd", stroke=NEG, pad=7)
    p.append(ahb_box)

    # Відгалуження HCLK на Core, DMA, Flash, SysTick
    p.append(arrow(642, 115, 695, 115, color=NEG, sw=1.8))
    core_box, _, _ = textbox(775, 115, "Ядро Cortex-M\nDMA / Flash (ART)\nSysTick (168 МГц)", size=9.5, bold=True, fill="#eaf0fd", stroke=NEG, pad=7)
    p.append(core_box)

    # Відгалуження HCLK вниз на APB1 та APB2
    p.append(line(585, 145, 585, 240, color=NEG, sw=1.5))
    p.append(arrow(585, 195, 640, 195, color=LINE, sw=1.5))
    p.append(arrow(585, 255, 640, 255, color=LINE, sw=1.5))
    p.append(line(585, 240, 585, 255, color=NEG, sw=1.5))

    # APB2 (High Speed, до 84 МГц)
    apb2_box, _, _ = textbox(750, 195, "APB2 Prescaler (/2) → PCLK2 84 МГц\nПериферія + Таймери (×2 → 168 МГц)", size=9.5, bold=True, fill="#f4f6f8", stroke=INK, pad=7)
    p.append(apb2_box)

    # APB1 (Low Speed, до 42 МГц)
    apb1_box, _, _ = textbox(750, 255, "APB1 Prescaler (/4) → PCLK1 42 МГц\nПериферія + Таймери (×2 → 84 МГц)", size=9.5, bold=True, fill="#f4f6f8", stroke=INK, pad=7)
    p.append(apb1_box)

    # Низькочастотний блок (LSI / LSE) -> RTC & IWDG (y = 430)
    p.append(arrow(src_x + 46, 395, 205, 395, color=INK, sw=1.5))
    b_iwdg, _, _ = textbox(280, 395, "IWDG (Сторож)\nнезалежний від HCLK", size=9.5, bold=True, fill="#f4f6f8", stroke=INK, pad=6)
    p.append(b_iwdg)

    p.append(line(src_x + 54, 465, 370, 465, color=NEG, sw=1.5))
    p.append(line(src_x + 46, 405, 340, 405, color=INK, sw=1.2, dash="3,3"))
    p.append(line(340, 405, 340, 455, color=INK, sw=1.2, dash="3,3"))
    p.append(arrow(340, 455, 360, 455, color=LINE, sw=1.5))

    rtc_mux, _, _ = textbox(385, 465, "RTC\nMUX", size=9.5, bold=True, fill="#fff9e6", stroke="#e0a800", pad=5)
    p.append(rtc_mux)
    p.append(arrow(407, 465, 450, 465, color=LINE, sw=1.5))
    b_rtc, _, _ = textbox(540, 465, "RTC (Годинник реального часу)\nЖивлення від V_BAT (домен резерву)", size=9.5, bold=True, fill="#eaf0fd", stroke=NEG, pad=7)
    p.append(b_rtc)

    render(os.path.join(OUT, "stm32-clock-tree-overview.svg"), W, H, *p,
           title="Архітектура дерева тактування STM32: джерела, PLL та розподіл по доменах")


# ── 2. stm32-pll-internals: внутрішня структура PLL та дільники ───────────────
def fig_pll_internals():
    W, H = 820, 380
    p = []

    # Вхідний комутатор (x = 70, y = 130)
    b_in, _, _ = textbox(70, 130, "Вхід такту\nHSE (8 МГц)\nабо HSI (16 МГц)", size=10.5, bold=True, fill="#eaf0fd", stroke=NEG, pad=8)
    p.append(b_in)

    # Дільник /M (x = 180, y = 130)
    p.append(arrow(120, 130, 145, 130, color=LINE, sw=1.6))
    b_m, _, _ = textbox(185, 130, "Дільник /M\n(2..63)\nЦіль: 1–2 МГц", size=10.5, bold=True, fill="#fff9e6", stroke="#e0a800", pad=8)
    p.append(b_m)

    # Фазочастотний детектор PFD (x = 295, y = 130)
    p.append(arrow(225, 130, 260, 130, color=LINE, sw=1.6))
    p.append(text(242, 118, "f_IN / M = 1..2 МГц", size=9, color=MUTED, anchor="middle"))
    b_pfd, _, _ = textbox(295, 130, "PFD\nФазовий\nдетектор", size=10, bold=True, fill="#f4f6f8", stroke=INK, pad=6)
    p.append(b_pfd)

    # Charge Pump + Loop Filter (x = 395, y = 130)
    p.append(arrow(328, 130, 355, 130, color=LINE, sw=1.6))
    b_cp, _, _ = textbox(395, 130, "CP + LPF\nФільтр петлі\n(напруга V_tune)", size=10, bold=True, fill="#f4f6f8", stroke=INK, pad=6)
    p.append(b_cp)

    # VCO (x = 515, y = 130)
    p.append(arrow(442, 130, 470, 130, color=LINE, sw=1.6))
    b_vco, _, _ = textbox(525, 130, "VCO (ГУН)\nДіапазон: 100–432 МГц\nf_VCO = (f_IN / M) · N", size=10.5, bold=True, fill="#fdecea", stroke=POS, pad=9)
    p.append(b_vco)

    # Зворотний зв'язок: від VCO через дільник /N назад у PFD
    p.append(line(580, 130, 600, 130, color=POS, sw=1.6))
    p.append(line(600, 130, 600, 235, color=POS, sw=1.6))
    p.append(arrow(600, 235, 450, 235, color=POS, sw=1.6))

    b_n, _, _ = textbox(395, 235, "Множник у зворотному зв'язку /N (50..432)\nf_VCO_IN = f_VCO / N", size=10.5, bold=True, fill="#fdecea", stroke=POS, pad=8)
    p.append(b_n)

    p.append(line(340, 235, 295, 235, color=POS, sw=1.6))
    p.append(arrow(295, 235, 295, 160, color=POS, sw=1.6))

    # Вихідні дільники праворуч
    p.append(line(580, 115, 650, 115, color=POS, sw=1.6))
    p.append(arrow(650, 115, 675, 115, color=LINE, sw=1.6))
    b_p, _, _ = textbox(740, 115, "Дільник /P (/2, /4, /6, /8)\nSYSCLK (до 168/180 МГц)", size=10, bold=True, fill="#eaf0fd", stroke=NEG, pad=7)
    p.append(b_p)

    p.append(line(580, 145, 635, 145, color=POS, sw=1.6))
    p.append(line(635, 145, 635, 185, color=POS, sw=1.6))
    p.append(arrow(635, 185, 675, 185, color=LINE, sw=1.6))
    b_q, _, _ = textbox(740, 185, "Дільник /Q (2..15)\nUSB / SDIO / RNG (48 МГц)", size=10, bold=True, fill="#d4edda", stroke=FIELD, pad=7)
    p.append(b_q)

    # Примітка знизу
    p.append(text(W / 2, 335, "Формула системи: f_SYSCLK = ((f_IN / M) · N) / P   |   f_USB = ((f_IN / M) · N) / Q",
                  size=11, color=INK, bold=True, anchor="middle"))

    render(os.path.join(OUT, "stm32-pll-internals.svg"), W, H, *p,
           title="Анатомія PLL у STM32: фазовий автопідстрій, VCO та матриця дільників")


# ── 3. flash-latency-timing: фізика тактів очікування Flash ───────────────────
def fig_flash_latency():
    W, H = 820, 390
    p = []

    # Графік періодів такту ядра vs часу відгуку Flash
    # Рівень 1: Низька частота (16 МГц, T = 62.5 нс > t_Flash = 30 нс) -> 0 WS
    y1 = 80
    p.append(text(60, y1, "HSI 16 МГц (0 WS)", size=11, bold=True, color=FIELD, anchor="start"))
    p.append(text(60, y1 + 16, "T = 62.5 нс > 30 нс", size=9.5, color=MUTED, anchor="start"))

    p.append(rect(230, y1 - 15, 300, 36, fill="#d4edda", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(380, y1 + 6, "1 такт ядра (62.5 нс) — Flash встигає віддати дані", size=10, bold=True, color=FIELD, anchor="middle"))

    # Рівень 2: Висока частота без Latency (168 МГц, T = 5.95 нс < 30 нс) -> Збій!
    y2 = 160
    p.append(text(60, y2, "PLL 168 МГц (0 WS помилка)", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(60, y2 + 16, "T = 5.95 нс « 30 нс", size=9.5, color=MUTED, anchor="start"))

    p.append(rect(230, y2 - 15, 55, 36, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(257, y2 + 6, "1 такт", size=9.5, bold=True, color=POS, anchor="middle"))
    p.append(line(230 + 55, y2 - 15, 230 + 200, y2 - 15, color=POS, sw=1.5, dash="3,3"))
    p.append(line(230 + 200, y2 - 20, 230 + 200, y2 + 25, color=POS, sw=1.8))
    p.append(text(230 + 208, y2 + 6, "Flash ще не готова (t_acc = 30 нс) → сміття на шині!", size=10, bold=True, color=POS, anchor="start"))

    # Рівень 3: Висока частота з 5 Wait States (6 тактів = 35.7 нс > 30 нс)
    y3 = 245
    p.append(text(60, y3, "PLL 168 МГц (5 WS норма)", size=11, bold=True, color=NEG, anchor="start"))
    p.append(text(60, y3 + 16, "6 тактів = 35.7 нс > 30 нс", size=9.5, color=MUTED, anchor="start"))

    ws_start = 230
    for i in range(5):
        p.append(rect(ws_start + i * 42, y3 - 15, 40, 36, fill="#fff9e6", stroke="#e0a800", sw=1.2, rx=3))
        p.append(text(ws_start + i * 42 + 20, y3 + 6, "WS %d" % (i + 1), size=9, bold=True, color="#e0a800", anchor="middle"))

    p.append(rect(ws_start + 5 * 42, y3 - 15, 45, 36, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(ws_start + 5 * 42 + 22, y3 + 6, "DATA", size=9.5, bold=True, color=NEG, anchor="middle"))
    p.append(text(ws_start + 6 * 42 + 10, y3 + 6, "Дані валідні (35.7 нс)", size=10, bold=True, color=NEG, anchor="start"))

    # Блок ART Accelerator знизу
    p.append(rect(60, 315, 700, 48, fill="#f4f6f8", stroke=INK, sw=1.5, rx=6))
    p.append(text(410, 335, "ART Accelerator (ST Adaptive Real-Time): 128-бітний Prefetch Buffer + I-Cache + D-Cache", size=10.5, bold=True, color=INK, anchor="middle"))
    p.append(text(410, 351, "Зчитує 4 інструкції за один доступ до Flash — повертає виконання коду до 0 WS для лінійних ділянок і циклів", size=9.5, color=MUTED, anchor="middle"))

    render(os.path.join(OUT, "flash-latency-timing.svg"), W, H, *p,
           title="Вплив тактової частоти на затримку читання Flash (Wait States) та роль ART-кешу")


# ── 4. clock-init-sequence: алгоритм безпечної ініціалізації RCC ───────────────
def fig_init_sequence():
    W, H = 840, 480
    p = []

    steps = [
        ("1. Увімкнути HSE", "RCC_CR |= HSEON\nОчікування HSERDY", "#eaf0fd", NEG),
        ("2. Живлення PWR", "Увімкнути PWR такт\nРежим VOS = Scale 1", "#f4f6f8", INK),
        ("3. Flash Latency", "FLASH_ACR: 5 WS\nУвімкнути ICEN, DCEN, PRFTEN", "#fff9e6", "#e0a800"),
        ("4. Дільники шин", "RCC_CFGR: AHB /1\nAPB1 /4, APB2 /2", "#f4f6f8", INK),
        ("5. Параметри PLL", "RCC_PLLCFGR:\nM, N, P, Q + PLLSRC_HSE", "#fdecea", POS),
        ("6. Старт PLL", "RCC_CR |= PLLON\nОчікування PLLRDY", "#fdecea", POS),
        ("7. Перемикач SW", "RCC_CFGR: SW = PLL\nОчікування SWS == PLL", "#eaf0fd", NEG),
        ("8. Захист CSS", "RCC_CR |= CSSON\nЗахист від зриву кварцу", "#d4edda", FIELD),
    ]

    # Розташуємо 8 кроків у 2 ряди по 4
    # Ряд 1: x = 110, 310, 510, 710; y = 110
    # Ряд 2: x = 710, 510, 310, 110; y = 280 (зигзагом)
    r1_x = [110, 310, 510, 710]
    r2_x = [710, 510, 310, 110]

    for i in range(4):
        title, desc, fill_c, str_c = steps[i]
        b, bw, bh = textbox(r1_x[i], 110, "%s\n%s" % (title, desc), size=10, bold=True, fill=fill_c, stroke=str_c, pad=8)
        p.append(b)
        if i < 3:
            p.append(arrow(r1_x[i] + 78, 110, r1_x[i + 1] - 78, 110, color=LINE, sw=1.6))

    # Стрілка вниз від кроку 4 до кроку 5
    p.append(line(710, 150, 710, 205, color=LINE, sw=1.6))
    p.append(arrow(710, 205, 710, 240, color=LINE, sw=1.6))

    for i in range(4):
        title, desc, fill_c, str_c = steps[4 + i]
        b, bw, bh = textbox(r2_x[i], 280, "%s\n%s" % (title, desc), size=10, bold=True, fill=fill_c, stroke=str_c, pad=8)
        p.append(b)
        if i < 3:
            p.append(arrow(r2_x[i] - 78, 280, r2_x[i + 1] + 78, 280, color=LINE, sw=1.6))

    # Результат у самому низу (y = 410)
    p.append(arrow(110, 320, 110, 380, color=FIELD, sw=1.8))
    res_box, _, _ = textbox(420, 410, "Готово: Ядро Cortex-M працює на стабільних 168 МГц із захищеним Flash-доступом і робочим USB", size=10.5, bold=True, fill="#d4edda", stroke=FIELD, pad=10)
    p.append(res_box)

    render(os.path.join(OUT, "clock-init-sequence.svg"), W, H, *p,
           title="Послідовність переходу на максимальну частоту тактування STM32")


if __name__ == "__main__":
    fig_clock_tree_overview()
    fig_pll_internals()
    fig_flash_latency()
    fig_init_sequence()
    print("All figures generated successfully.")
