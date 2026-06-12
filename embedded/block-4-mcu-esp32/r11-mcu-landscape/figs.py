# -*- coding: utf-8 -*-
"""
Фігури для розділу r11-mcu-landscape (§4.11 Пейзаж мікроконтролерів).
Запуск: python figs.py
Виводить 16 SVG у ./img/

НЕ переписувати примітиви svgkit — тільки імпортувати.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── Додаткова палітра для цього розділу ──────────────────────────────────────
AVR_C  = "#d68910"; AVR_F  = "#fef9e7"
ARM_C  = "#7d3c98"; ARM_F  = "#f0e6fa"
STM_C  = "#1a5276"; STM_F  = "#d6eaf8"
RPI_C  = "#1e8449"; RPI_F  = "#d5f5e3"
NRF_C  = "#b03a2e"; NRF_F  = "#fce0dc"
ESP_C  = "#2471a3"; ESP_F  = "#d2e4f5"
ECO_C  = "#117a65"; ECO_F  = "#d1f2eb"


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.1.1  Карта пейзажу МК (двовимірне поле)
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_1_1_mcu_map():
    W, H = 820, 500
    p = []

    # Заголовок
    p.append(text(W//2, 26, "Рис. 4.11.1.1  Пейзаж мікроконтролерів: де на ньому ESP32",
                  size=15, bold=True))

    # Осі координат
    ox, oy = 80, 430
    ax_w, ax_h = 680, 360

    # Поле
    p.append(rect(ox, oy - ax_h, ax_w, ax_h, fill="#f8fafc", stroke=MUTED, sw=1, rx=0))

    # Вісь X
    p.append(arrow(ox, oy, ox + ax_w, oy, color=MUTED, sw=1.5))
    p.append(text(ox + ax_w // 2, oy + 22, "Продуктивність / інтеграція →", size=12, color=MUTED))

    # Вісь Y
    p.append(arrow(ox, oy, ox, oy - ax_h - 18, color=MUTED, sw=1.5))
    p.append(text(ox - 12, oy - ax_h // 2, "Спеціалізація ↑", size=12, color=MUTED, anchor="end"))

    # Розмітка осей
    for i, lbl in enumerate(["Мало", "Середньо", "Багато"]):
        x = ox + (i + 1) * ax_w // 4
        p.append(line(x, oy - 6, x, oy + 6, color=MUTED, sw=1))
        p.append(text(x, oy + 16, lbl, size=10, color=MUTED))
    for i, lbl in enumerate(["Загальні", "Вузькі", "Спеці-\nальні"]):
        y = oy - (i + 1) * ax_h // 4
        p.append(line(ox - 6, y, ox + 6, y, color=MUTED, sw=1))
        p.append(text(ox - 10, y + 5, lbl, size=10, color=MUTED, anchor="end"))

    # Чипи на площині
    chips = [
        # (cx, cy, label, fill, stroke)
        (ox + ax_w * 10 // 100, oy - ax_h * 20 // 100, "AVR-клас\n(8-біт)",  AVR_F,  AVR_C),
        (ox + ax_w * 30 // 100, oy - ax_h * 30 // 100, "ARM\nCortex-M\n(ядро)", ARM_F, ARM_C),
        (ox + ax_w * 45 // 100, oy - ax_h * 28 // 100, "STM32-\nклас",         STM_F,  STM_C),
        (ox + ax_w * 50 // 100, oy - ax_h * 48 // 100, "RP2040\n/PIO",         RPI_F,  RPI_C),
        (ox + ax_w * 38 // 100, oy - ax_h * 72 // 100, "nRF-клас\n(BLE)",      NRF_F,  NRF_C),
        (ox + ax_w * 72 // 100, oy - ax_h * 60 // 100, "ESP32\n(Wi-Fi)",       ESP_F,  ESP_C),
    ]

    for cx, cy, lbl, fill, stroke in chips:
        bx, bw, bh = textbox(cx, cy, lbl, size=12, pad=9, fill=fill, stroke=stroke, sw=2, rx=8)
        p.append(bx)

    # Підпис-висновок
    p.append(text(W//2, H - 14,
                  "'Найкращого' МК немає — кожен займає свою нішу. ESP32 — лише одна крапка.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-1-1-mcu-map.svg"), W, H, *p)
    print("OK fig-11-1-1-mcu-map.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.1.2  Шість осей вибору — радар-профіль двох умовних МК
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_1_2_six_axes():
    W, H = 820, 480
    p = []

    p.append(text(W//2, 26, "Рис. 4.11.1.2  Шість осей вибору МК: жоден не 'кращий по всьому'",
                  size=15, bold=True))

    CX, CY, R = 310, 265, 185

    axes = [
        "Периферія",
        "Споживання\n(обернено)",
        "Корпус\n(простота)",
        "Ціна",
        "Доступність",
        "Екосистема",
    ]
    n = len(axes)

    # Павутиння (сітка)
    for k in [0.33, 0.67, 1.0]:
        pts = []
        for i in range(n):
            ang = math.pi / 2 + 2 * math.pi * i / n
            pts.append((CX + R * k * math.cos(ang),
                        CY - R * k * math.sin(ang)))
        poly = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
        p.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="1" stroke-dasharray="4 3"/>'
                 % (poly, MUTED))

    # Осьові лінії + підписи
    for i, lbl in enumerate(axes):
        ang = math.pi / 2 + 2 * math.pi * i / n
        ex = CX + R * math.cos(ang)
        ey = CY - R * math.sin(ang)
        p.append(line(CX, CY, ex, ey, color=MUTED, sw=1, dash="4 3"))
        # підпис ззовні
        lx = CX + (R + 24) * math.cos(ang)
        ly = CY - (R + 24) * math.sin(ang)
        anchor = "start" if lx > CX + 10 else ("end" if lx < CX - 10 else "middle")
        p.append(mtext(lx, ly - 5, lbl.split("\n"), size=12, color=INK, anchor=anchor))

    # Профіль Wi-Fi SoC (ESP32-подібний)
    wifi_vals = [0.80, 0.30, 0.75, 0.55, 0.80, 0.90]   # 1 = максимум по осі
    wifi_pts = []
    for i, v in enumerate(wifi_vals):
        ang = math.pi / 2 + 2 * math.pi * i / n
        wifi_pts.append((CX + R * v * math.cos(ang),
                         CY - R * v * math.sin(ang)))
    poly = " ".join("%.1f,%.1f" % (x, y) for x, y in wifi_pts)
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="2.5"/>'
             % (poly, ESP_C, ESP_C))

    # Профіль 8-бітника (AVR-подібний)
    avr_vals = [0.40, 0.80, 0.90, 0.90, 0.70, 0.50]
    avr_pts = []
    for i, v in enumerate(avr_vals):
        ang = math.pi / 2 + 2 * math.pi * i / n
        avr_pts.append((CX + R * v * math.cos(ang),
                        CY - R * v * math.sin(ang)))
    poly2 = " ".join("%.1f,%.1f" % (x, y) for x, y in avr_pts)
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.20" stroke="%s" stroke-width="2.5"/>'
             % (poly2, AVR_C, AVR_C))

    # Легенда
    lx = 580
    p.append(rect(lx, 100, 200, 120, fill="#f9f9f9", stroke=MUTED, sw=1, rx=8))
    p.append(text(lx + 100, 120, "Легенда", size=13, bold=True))
    p.append(line(lx + 18, 145, lx + 58, 145, color=ESP_C, sw=2.5))
    p.append('<rect x="%d" y="%d" width="40" height="14" fill="%s" fill-opacity="0.25" stroke="%s" stroke-width="1"/>'
             % (lx + 18, 138, ESP_C, ESP_C))
    p.append(text(lx + 70, 149, "Wi-Fi SoC", size=12, color=ESP_C, anchor="start"))
    p.append(line(lx + 18, 175, lx + 58, 175, color=AVR_C, sw=2.5))
    p.append('<rect x="%d" y="%d" width="40" height="14" fill="%s" fill-opacity="0.20" stroke="%s" stroke-width="1"/>'
             % (lx + 18, 168, AVR_C, AVR_C))
    p.append(text(lx + 70, 179, "8-бітний МК", size=12, color=AVR_C, anchor="start"))

    p.append(text(W//2, H - 12,
                  "Продуктивність — лише одна з шести осей. Жоден клас не виграє по всіх одразу.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-1-2-six-axes.svg"), W, H, *p)
    print("OK fig-11-1-2-six-axes.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.1.3  Ціна надлишку — три стовпчикові пари
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_1_3_cost_of_overkill():
    W, H = 760, 420
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.1.3  Ціна надлишку: потужний SoC проти простого МК на елементарній задачі",
                  size=14, bold=True))

    groups = [
        ("Струм спокою\n(мА)", 80, 0.8, "80 мА", "0.8 мА"),
        ("Ціна×1000\n(USD)", 5200, 800, "5200 $", "800 $"),
        ("Час старту\n(мс)", 1800, 15, "1800 мс", "15 мс"),
    ]

    bx0, by0, bw, bh_max = 90, 370, 160, 280

    for gi, (lbl, v_esp, v_avr, s_esp, s_avr) in enumerate(groups):
        cx = bx0 + gi * 230

        max_v = max(v_esp, v_avr)
        h_esp = int(bh_max * v_esp / max_v)
        h_avr = int(bh_max * v_avr / max_v)

        # ESP32 стовпчик
        ex = cx
        p.append(rect(ex, by0 - h_esp, bw * 0.45, h_esp, fill=ESP_F, stroke=ESP_C, sw=2, rx=4))
        p.append(text(ex + bw * 0.45 / 2, by0 - h_esp - 10, s_esp, size=11, color=ESP_C, bold=True))
        p.append(text(ex + bw * 0.45 / 2, by0 + 16, "ESP32", size=11, color=ESP_C))

        # 8-біт стовпчик
        ax = cx + bw * 0.55
        p.append(rect(ax, by0 - h_avr, bw * 0.45, h_avr, fill=AVR_F, stroke=AVR_C, sw=2, rx=4))
        p.append(text(ax + bw * 0.45 / 2, by0 - h_avr - 10, s_avr, size=11, color=AVR_C, bold=True))
        p.append(text(ax + bw * 0.45 / 2, by0 + 16, "8-бітник", size=11, color=AVR_C))

        # Підпис групи
        p.append(mtext(cx + bw / 2, by0 + 34, lbl.split("\n"), size=11, color=INK))

        # Риска базової лінії
        p.append(line(cx - 8, by0, cx + bw + 8, by0, color=MUTED, sw=1))

    p.append(text(W//2, H - 12,
                  "Для масового простого виробу без зв'язку ESP32 програє по всіх трьох осях. Числа орієнтовні.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-1-3-cost-of-overkill.svg"), W, H, *p)
    print("OK fig-11-1-3-cost-of-overkill.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.2.1  Тракт даних AVR-класу (Гарвард, 1 такт/інструкцію)
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_2_1_avr_datapath():
    W, H = 820, 440
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.2.1  8-бітний AVR-клас: Гарвардський тракт, 1 такт на інструкцію",
                  size=14, bold=True))

    # ── AVR (зліва) ──────────────────────────────────────────────────────────
    AVRCX = 210
    blocks = [
        (AVRCX, 80,  220, 50, "Flash-пам'ять коду",      AVR_F, AVR_C),
        (AVRCX, 180, 220, 50, "АЛП 8-бітне + 32 reg",   AVR_F, AVR_C),
        (AVRCX, 280, 220, 50, "SRAM (кілька кБ)",        AVR_F, AVR_C),
        (AVRCX, 370, 220, 38, "GPIO напряму до ніжки",   "#e8f8f0", FIELD),
    ]

    for bx, by, bw, bh, lbl, fill, stroke in blocks:
        p.append(rect(bx - bw//2, by, bw, bh, fill=fill, stroke=stroke, sw=2, rx=6))
        p.append(text(bx, by + bh//2 + 5, lbl, size=12, color=stroke, bold=True))

    # Гарвардські шини (зрозуміло: код і дані окремо)
    p.append(line(AVRCX, 130, AVRCX, 180, color=AVR_C, sw=2.5))
    p.append(text(AVRCX + 8, 160, "шина коду", size=10, color=AVR_C, anchor="start"))
    p.append(line(AVRCX, 230, AVRCX, 280, color=FIELD, sw=2.5))
    p.append(text(AVRCX + 8, 260, "шина даних", size=10, color=FIELD, anchor="start"))
    p.append(line(AVRCX, 330, AVRCX, 370, color=FIELD, sw=2.5))

    # Мітка «1 такт»
    bx_, bw_, bh_ = textbox(AVRCX - 130, 200, "≈1 такт\nна інструкцію", size=13,
                             pad=8, fill="#fff9e6", stroke=AVR_C, sw=2)
    p.append(bx_)
    p.append(arrow(AVRCX - 88, 210, AVRCX - 112, 205, color=AVR_C, sw=1.5))

    # Підпис «AVR-клас»
    p.append(text(AVRCX, 52, "AVR-клас (8-біт)", size=14, bold=True, color=AVR_C))

    # Роздільник
    p.append(line(460, 50, 460, H - 30, color=MUTED, sw=1, dash="6 4"))
    p.append(text(462, 55, "Контраст", size=11, color=MUTED, anchor="start"))

    # ── ESP32 (справа) ───────────────────────────────────────────────────────
    ESPCX = 640
    esp_blocks = [
        (ESPCX, 80,  250, 50, "Flash зовнішня (QSPI)",  ESP_F, ESP_C),
        (ESPCX, 155, 250, 50, "Cache L1 + конвеєр",     ESP_F, ESP_C),
        (ESPCX, 230, 250, 50, "Xtensa LX6/LX7 ядро",   ESP_F, ESP_C),
        (ESPCX, 305, 250, 50, "GPIO matrix + MUX",      ESP_F, ESP_C),
        (ESPCX, 375, 250, 35, "ніжка мікросхеми",       "#e8f8f0", FIELD),
    ]
    for bx, by, bw, bh, lbl, fill, stroke in esp_blocks:
        p.append(rect(bx - bw//2, by, bw, bh, fill=fill, stroke=stroke, sw=2, rx=6))
        p.append(text(bx, by + bh//2 + 5, lbl, size=12, color=stroke, bold=True))
    # Зигзаг з джитером між конвеєром і виходом
    for y_start, y_end in [(130, 155), (205, 230), (280, 305), (340, 375)]:
        p.append(arrow(ESPCX, y_start, ESPCX, y_end, color=ESP_C, sw=1.5))

    bj, _, _ = textbox(ESPCX + 148, 230, "джитер\n(кеш-проміс,\nRTOS)", size=10,
                        pad=7, fill="#fce8e8", stroke=POS, sw=1.5)
    p.append(bj)

    p.append(text(ESPCX, 52, "ESP32 (32-біт + RTOS)", size=14, bold=True, color=ESP_C))

    p.append(text(W//2, H - 12,
                  "Коротший шлях від коду до ніжки → передбачуваний таймінг. Довший → більше потужності, але не детермінізму.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-2-1-avr-datapath.svg"), W, H, *p)
    print("OK fig-11-2-1-avr-datapath.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.2.2  Затримка на тактах: чиста AVR шкала vs «розмита» ESP32
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_2_2_clock_budget():
    W, H = 800, 380
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.2.2  Затримка на AVR рахується до такту; під RTOS/кешем — ні",
                  size=14, bold=True))

    # ── AVR — точна шкала ────────────────────────────────────────────────────
    p.append(text(80, 65, "AVR @ 16 МГц", size=13, bold=True, color=AVR_C, anchor="start"))
    tx0, ty = 80, 90
    tick_w = 50
    N = 8
    for i in range(N):
        x = tx0 + i * tick_w
        col = AVR_C if i % 2 == 0 else AVR_F
        sc = AVR_C if i % 2 == 0 else AVR_C
        p.append(rect(x, ty, tick_w - 2, 36, fill=col, stroke=sc, sw=1.5, rx=3))
        lbl = "DEC" if i % 2 == 0 else "BRNE"
        p.append(text(x + (tick_w - 2) / 2, ty + 22, lbl, size=10,
                      color=BG if i % 2 == 0 else AVR_C))

    # Двостороння стрілка + розмірка
    total_x = tx0 + N * tick_w - 2
    arr_y = ty + 52
    p.append(line(tx0, arr_y, total_x, arr_y, color=AVR_C, sw=1.5))
    p.append(arrow(tx0, arr_y, tx0 - 1, arr_y, color=AVR_C, sw=1.5))
    p.append(arrow(total_x, arr_y, total_x + 1, arr_y, color=AVR_C, sw=1.5))
    p.append(text((tx0 + total_x) / 2, arr_y - 8,
                  "8 ітерацій × 2 такти = 16 тактів = 1.0 мкс (рівно)",
                  size=11, color=AVR_C))

    # Мітка «один такт = 62.5 нс»
    p.append(text(tx0, ty + 78, "1 такт = 62.5 нс → 16 тактів = 1000 нс = 1 мкс  ✓",
                  size=11, color=AVR_C, anchor="start"))

    # ── ESP32 — розмита шкала ────────────────────────────────────────────────
    p.append(text(80, 195, "ESP32 @ 240 МГц + RTOS + кеш-промахи", size=13, bold=True,
                  color=ESP_C, anchor="start"))

    ey = 220
    widths = [18, 22, 14, 35, 16, 28, 12, 40, 19, 11]  # «випадкова» ширина
    ex_cur = tx0
    cols_e = [ESP_F, "#c3d9ef", ESP_F, "#a8c7e5", ESP_F, "#c3d9ef", ESP_F, "#a8c7e5", ESP_F, ESP_F]
    for i, w in enumerate(widths):
        p.append(rect(ex_cur, ey, w - 1, 36, fill=cols_e[i % len(cols_e)], stroke=ESP_C, sw=1, rx=2))
        ex_cur += w

    # Стрілка «джитер ≈ ±кілька мкс»
    jy = ey + 52
    p.append(line(tx0, jy, ex_cur, jy, color=ESP_C, sw=1.5, dash="4 3"))
    p.append(text((tx0 + ex_cur) / 2, jy - 8,
                  "той самий цикл: ~1–5 мкс залежно від кешу і планувальника",
                  size=11, color=ESP_C))

    bj, _, _ = textbox(ex_cur + 40, ey + 18, "джитер\n±кілька мкс", size=11,
                        pad=7, fill="#fce8e8", stroke=POS, sw=1.5)
    p.append(bj)

    p.append(text(W//2, H - 12,
                  "На 8-бітнику такти рахуються і дають точний час. На потужному МК під RTOS — лише межі.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-2-2-clock-budget.svg"), W, H, *p)
    print("OK fig-11-2-2-clock-budget.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.3.1  Модель ліцензування ARM
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_3_1_arm_licensing():
    W, H = 820, 440
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.3.1  Одне ядро — багато виробників: ARM ліцензує Cortex-M",
                  size=14, bold=True))

    # Центральне ядро ARM
    cx, cy = 410, 190
    bx, bw, bh = textbox(cx, cy, "ARM\nCortex-M\n(ядро)", size=15, pad=18,
                          fill=ARM_F, stroke=ARM_C, sw=3, rx=12)
    p.append(bx)

    # Виробники
    vendors = [
        (150, 340, "ST Micro\n→ STM32",  STM_F, STM_C),
        (280, 100, "Nordic\n→ nRF",      NRF_F, NRF_C),
        (540, 100, "Raspberry\n→ RP2040",RPI_F, RPI_C),
        (660, 310, "NXP\n→ iMX RT",     "#f5f0ff", "#6c3483"),
        (680, 160, "Atmel/SAMD\n→ SAMD",AVR_F, AVR_C),
    ]

    for vx, vy, lbl, fill, stroke in vendors:
        vb, _, _ = textbox(vx, vy, lbl, size=12, pad=10, fill=fill, stroke=stroke, sw=2, rx=8)
        p.append(vb)
        p.append(arrow(cx, cy, vx, vy, color=ARM_C, sw=1.5))

    # Підпис «ліцензія»
    lic_b, _, _ = textbox(cx, cy + 150, "IP-ліцензія ARM:\nвиробник платить\nроялті", size=11,
                           pad=8, fill="#f0e6fa", stroke=ARM_C, sw=1.5)
    p.append(lic_b)

    p.append(text(W//2, H - 12,
                  "Вивчив ядро раз → упізнаєш NVIC, SysTick, модель переривань у будь-якому Cortex-M чипі.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-3-1-arm-licensing.svg"), W, H, *p)
    print("OK fig-11-3-1-arm-licensing.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.3.2  Ієрархія Cortex-M (сходи M0→M7) + ESP32 осторонь
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_3_2_cortexm_ladder():
    W, H = 820, 480
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.3.2  Сходи Cortex-M: спільне ядро внизу, продуктивність вгору; ESP32 — осторонь",
                  size=13, bold=True))

    steps = [
        ("M0 / M0+",  "Ощадний 32-біт;\nконкурент AVR",          60, ARM_F, ARM_C),
        ("M3",        "Робоча конячка;\nрозгалуження пришвидшене", 95, ARM_F, ARM_C),
        ("M4",        "M3 + DSP-інструкції\n+ FPU (float апаратно)", 130, ARM_F, ARM_C),
        ("M7",        "Подвійний конвеєр,\nкеш L1, швидко",        165, "#e8e0f5", ARM_C),
    ]

    # Ліва колонка — сходи
    for i, (name, desc, h, fill, stroke) in enumerate(steps):
        bx0 = 60
        bw_step = 320 + i * 30
        by = 380 - i * 80
        p.append(rect(bx0, by, bw_step, h, fill=fill, stroke=stroke, sw=2, rx=6))
        p.append(text(bx0 + 70, by + 22, name, size=14, bold=True, color=stroke))
        p.append(mtext(bx0 + 200, by + 25, desc.split("\n"), size=11, color=INK))

    # «ОДНАКОВЕ в усіх» — права колонка
    rx0 = 500
    same_y = 120
    same_h = 270
    p.append(rect(rx0, same_y, 200, same_h, fill="#f8f4ff", stroke=ARM_C, sw=2, rx=8))
    p.append(text(rx0 + 100, same_y + 22, "Спільне у ВСІХ", size=13, bold=True, color=ARM_C))
    same_items = ["NVIC (контролер переривань)", "SysTick (таймер ядра)",
                  "Модель винятків", "Thumb-2 ISA", "CMSIS-заголовки"]
    for ii, itm in enumerate(same_items):
        p.append(text(rx0 + 14, same_y + 52 + ii * 38, "• " + itm, size=11, color=ARM_C, anchor="start"))

    # ESP32 — осторонь
    eb, _, _ = textbox(700, 70, "ESP32\n(Xtensa LX6)\nНЕ Cortex-M", size=12,
                        pad=10, fill=ESP_F, stroke=ESP_C, sw=2, rx=8)
    p.append(eb)
    p.append(line(700, 108, 700, 130, color=MUTED, sw=1.5, dash="5 3"))
    p.append(text(700, 148, "окрема\nархітектура", size=10, color=MUTED))

    p.append(text(W//2, H - 12,
                  "Що додається вгору по сходах: продуктивність, FPU, кеш. Що незмінне: NVIC, SysTick, ISA.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-3-2-cortexm-ladder.svg"), W, H, *p)
    print("OK fig-11-3-2-cortexm-ladder.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.4.1  STM32 vs ESP32 — порівняння блоків периферії
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_4_1_stm32_vs_esp32_periph():
    W, H = 820, 460
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.4.1  Дві філософії: точна провідна периферія STM32-класу vs радіо+гнучкість ESP32",
                  size=13, bold=True))

    col_w = 310
    hdr_h = 44

    # STM32 — ліва колонка
    sx = 60
    p.append(rect(sx, 55, col_w, hdr_h, fill=STM_F, stroke=STM_C, sw=2.5, rx=8))
    p.append(text(sx + col_w // 2, 55 + hdr_h // 2 + 6, "STM32-клас (Cortex-M)", size=14,
                  bold=True, color=STM_C))

    stm_items = [
        ("Advanced-таймери", "мертвий час, 6 компл. ШІМ\n(трифазний міст)"),
        ("АЦП × 3 синхронно", "запуск від ШІМ (§4.8)"),
        ("DMA багатопотоковий", "12+ незалежних каналів"),
        ("SWD / JTAG", "відлагодження «з коробки'»"),
        ("Без радіо", "→ зовнішній модуль"),
    ]
    for ii, (name, desc) in enumerate(stm_items):
        iy = 110 + ii * 60
        p.append(rect(sx + 8, iy, col_w - 16, 50, fill="#eaf3fc", stroke=STM_C, sw=1.2, rx=5))
        p.append(text(sx + 18, iy + 18, "▸ " + name, size=12, bold=True, color=STM_C, anchor="start"))
        p.append(mtext(sx + 18, iy + 36, desc.split("\n"), size=10, color=MUTED, anchor="start"))

    # ESP32 — права колонка
    ex = 440
    p.append(rect(ex, 55, col_w, hdr_h, fill=ESP_F, stroke=ESP_C, sw=2.5, rx=8))
    p.append(text(ex + col_w // 2, 55 + hdr_h // 2 + 6, "ESP32 (Xtensa / RISC-V)", size=14,
                  bold=True, color=ESP_C))

    esp_items = [
        ("MCPWM / RMT / I2S", "гнучкі, але фіксовані блоки"),
        ("АЦП (нелінійний)", "обмежена точність (§4.8.6)"),
        ("DMA (ESP-IDF)", "прив'язаний до SPI/I2S"),
        ("Wi-Fi + BLE", "на борту — ключова перевага"),
        ("Більший струм спокою", "~10–80 мА без Radio-off"),
    ]
    for ii, (name, desc) in enumerate(esp_items):
        iy = 110 + ii * 60
        p.append(rect(ex + 8, iy, col_w - 16, 50, fill="#e5f0fa", stroke=ESP_C, sw=1.2, rx=5))
        p.append(text(ex + 18, iy + 18, "▸ " + name, size=12, bold=True, color=ESP_C, anchor="start"))
        p.append(mtext(ex + 18, iy + 36, desc.split("\n"), size=10, color=MUTED, anchor="start"))

    p.append(text(W//2, H - 12,
                  "STM32 виграє в точній провідній периферії; ESP32 — у вбудованому радіо та екосистемі.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-4-1-stm32-vs-esp32-periph.svg"), W, H, *p)
    print("OK fig-11-4-1-stm32-vs-esp32-periph.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.4.2  Трифазний міст — скільки каналів потрібно
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_4_2_three_phase_channels():
    W, H = 800, 400
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.4.2  Трифазний міст: 6 узгоджених ШІМ + синхронний захват струму",
                  size=14, bold=True))

    # Схема моста
    ph_colors = [POS, NEG, FIELD]
    ph_names  = ["Фаза A", "Фаза B", "Фаза C"]

    bx_start = 70
    for pi, (pc, pn) in enumerate(zip(ph_colors, ph_names)):
        col_x = bx_start + pi * 180

        # Верхній ключ
        p.append(rect(col_x, 80, 120, 44, fill="#fff", stroke=pc, sw=2.5, rx=5))
        p.append(text(col_x + 60, 106, "Q" + str(2*pi+1) + " верхній", size=11, color=pc, bold=True))

        # Нижній ключ
        p.append(rect(col_x, 180, 120, 44, fill="#fff", stroke=pc, sw=2.5, rx=5))
        p.append(text(col_x + 60, 206, "Q" + str(2*pi+2) + " нижній", size=11, color=pc, bold=True))

        # «Мертвий час»
        p.append(line(col_x + 60, 124, col_x + 60, 180, color=pc, sw=2.5))
        p.append(line(col_x + 50, 152, col_x + 70, 152, color=pc, sw=1.5))
        p.append(text(col_x + 72, 155, "Δt", size=10, color=pc, anchor="start"))

        # Вимір струму
        p.append(rect(col_x, 265, 120, 38, fill="#f5f5ff", stroke=ARM_C, sw=1.5, rx=5))
        p.append(text(col_x + 60, 289, "ADC" + str(pi+1) + " (струм)", size=10,
                      color=ARM_C, bold=True))

        # Мітка фази
        p.append(text(col_x + 60, 325, pn, size=12, bold=True, color=pc))

    # Advanced-таймер = один блок покриває все
    tb, _, _ = textbox(410, 365, "STM32 Advanced-таймер:\n1 блок = 6 ШІМ + dead-time + trigger", size=11,
                        pad=10, fill=STM_F, stroke=STM_C, sw=2, rx=8)
    p.append(tb)

    p.append(text(W//2, H - 12,
                  "6 взаємно залежних ШІМ-виходів і 3 синхронні АЦП-захвати — саме під це STM32 advanced-таймер.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-4-2-three-phase-channels.svg"), W, H, *p)
    print("OK fig-11-4-2-three-phase-channels.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.5.1  PIO vs біт-бенгінг (звільнення ядра)
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_5_1_pio_vs_bitbang():
    W, H = 820, 400
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.5.1  PIO як 'DMA для протоколів': міні-автомати смикають ніжки, ядро вільне",
                  size=14, bold=True))

    # ── ЛІВОРУЧ: біт-бенгінг ─────────────────────────────────────────────────
    bx0 = 50
    p.append(text(bx0 + 150, 60, "Біт-бенгінг ядром", size=13, bold=True, color=POS))

    # ядро — «зайняте»
    p.append(rect(bx0, 80, 300, 80, fill="#fce8e8", stroke=POS, sw=2.5, rx=8))
    p.append(text(bx0 + 150, 108, "Ядро CPU", size=13, bold=True, color=POS))
    p.append(text(bx0 + 150, 132, "(займається протоколом)", size=11, color=POS))

    # стрілка до ніжки
    p.append(arrow(bx0 + 150, 160, bx0 + 150, 210, color=POS, sw=2.5))
    p.append(text(bx0 + 165, 190, "смикає ніжку вручну\n(такт за тактом)", size=10,
                  color=POS, anchor="start"))

    # ніжка
    p.append(rect(bx0 + 90, 210, 120, 40, fill="#fce8e8", stroke=POS, sw=2, rx=5))
    p.append(text(bx0 + 150, 235, "GPIO-ніжка", size=12, color=POS, bold=True))

    # Джитер-сигнал
    sy = 275
    p.append(text(bx0 + 150, sy + 5, "сигнал (джитер)", size=10, color=POS))
    ex = bx0 + 30
    for i in range(8):
        w = 28 + (i % 3) * 5   # нерівні тривалості
        p.append(rect(ex, sy + 15, w - 2, 16, fill=POS if i % 2 == 0 else "#fff",
                      stroke=POS, sw=1, rx=0))
        ex += w

    # «ядро блоковане» мітка
    bbl, _, _ = textbox(bx0 + 150, 340, "ядро ЗАБЛОКОВАНЕ\nна час протоколу", size=11,
                         pad=8, fill="#fce8e8", stroke=POS, sw=2)
    p.append(bbl)

    # Роздільник
    p.append(line(420, 55, 420, H - 20, color=MUTED, sw=1, dash="5 4"))

    # ── ПРАВОРУЧ: PIO ─────────────────────────────────────────────────────────
    px0 = 450
    p.append(text(px0 + 150, 60, "PIO (RP2040)", size=13, bold=True, color=RPI_C))

    # ядро — вільне
    p.append(rect(px0, 80, 300, 80, fill=RPI_F, stroke=RPI_C, sw=2.5, rx=8))
    p.append(text(px0 + 150, 108, "Ядро CPU", size=13, bold=True, color=RPI_C))
    p.append(text(px0 + 150, 132, "(виконує корисну роботу)", size=11, color=RPI_C))

    # PIO-автомат
    p.append(rect(px0 + 80, 185, 140, 44, fill="#c8f7e0", stroke=FIELD, sw=2, rx=6))
    p.append(text(px0 + 150, 212, "PIO state machine", size=11, bold=True, color=FIELD))
    p.append(arrow(px0 + 150, 160, px0 + 150, 185, color=MUTED, sw=1.5))
    p.append(text(px0 + 205, 175, "програма\n(один раз)", size=9, color=MUTED, anchor="start"))
    p.append(arrow(px0 + 150, 229, px0 + 150, 255, color=FIELD, sw=2.5))

    # ніжка
    p.append(rect(px0 + 90, 255, 120, 40, fill=RPI_F, stroke=RPI_C, sw=2, rx=5))
    p.append(text(px0 + 150, 280, "GPIO-ніжка", size=12, color=RPI_C, bold=True))

    # Ідеальний сигнал
    sy2 = 318
    p.append(text(px0 + 150, sy2 + 5, "сигнал (точний)", size=10, color=RPI_C))
    ex2 = px0 + 30
    bit_w = 32
    for i in range(8):
        p.append(rect(ex2 + i * bit_w, sy2 + 15, bit_w - 2, 16,
                      fill=RPI_C if i % 2 == 0 else "#fff", stroke=RPI_C, sw=1, rx=0))

    bf, _, _ = textbox(px0 + 150, 360, "ядро ВІЛЬНЕ\n≈0 навантаження", size=11,
                        pad=8, fill=RPI_F, stroke=RPI_C, sw=2)
    p.append(bf)

    render(os.path.join(OUT, "fig-11-5-1-pio-vs-bitbang.svg"), W, H, *p)
    print("OK fig-11-5-1-pio-vs-bitbang.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.5.2  Бюджет тактів WS2812: біт-бенгінг vs PIO
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_5_2_pio_cpu_budget():
    W, H = 780, 380
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.5.2  Частка ядра: біт-бенгінг WS2812 росте з пікселями, PIO ≈ 0",
                  size=14, bold=True))

    counts = [1, 8, 30, 60, 144, 300]
    # приблизна частка CPU @ 125 МГц (WS2812 800 кГц, 24 біт/піксель, ~8 тактів/біт,
    # + накладні оновлення 30 Гц): load = pix*24*8*30/125e6
    loads = [min(c * 24 * 8 * 30 / 125e6, 1.0) for c in counts]

    bx0, by0, bw_unit = 90, 330, 80
    max_h = 240

    for i, (cnt, load) in enumerate(zip(counts, loads)):
        cx = bx0 + i * (bw_unit + 18)
        bar_h = int(max_h * load)
        pio_h = 6  # символічно ≈0

        # біт-бенгінг
        p.append(rect(cx, by0 - bar_h, bw_unit * 0.42, bar_h, fill=POS, stroke=POS, sw=1, rx=3))
        pct = int(load * 100)
        p.append(text(cx + bw_unit * 0.42 / 2, by0 - bar_h - 10, "%d%%" % pct, size=10,
                      color=POS, bold=True))

        # PIO
        p.append(rect(cx + bw_unit * 0.52, by0 - pio_h, bw_unit * 0.42, pio_h,
                      fill=RPI_C, stroke=RPI_C, sw=1, rx=2))
        p.append(text(cx + bw_unit * 0.52 + bw_unit * 0.42 / 2, by0 - pio_h - 10,
                      "≈0", size=10, color=RPI_C, bold=True))

        # підпис
        p.append(text(cx + bw_unit * 0.5, by0 + 16, str(cnt), size=11, color=INK))
        p.append(text(cx + bw_unit * 0.5, by0 + 28, "пікс.", size=10, color=MUTED))

    # Осі
    p.append(line(bx0 - 12, by0, bx0 + (bw_unit + 18) * len(counts) + 20, by0,
                  color=INK, sw=1.5))
    p.append(arrow(bx0 - 12, by0, bx0 - 12, by0 - max_h - 20, color=INK, sw=1.5))
    p.append(text(bx0 - 20, by0 - max_h // 2, "Частка CPU", size=12, color=INK, anchor="end"))
    for pct_mark in [25, 50, 75, 100]:
        my = by0 - int(max_h * pct_mark / 100)
        p.append(line(bx0 - 18, my, bx0 - 6, my, color=MUTED, sw=1))
        p.append(text(bx0 - 22, my + 4, "%d%%" % pct_mark, size=10, color=MUTED, anchor="end"))

    # Легенда
    p.append(rect(600, 60, 160, 72, fill="#f9f9f9", stroke=MUTED, sw=1, rx=6))
    p.append(rect(618, 76, 20, 14, fill=POS, stroke=POS, sw=1, rx=2))
    p.append(text(648, 87, "Біт-бенгінг", size=11, color=POS, anchor="start"))
    p.append(rect(618, 106, 20, 14, fill=RPI_C, stroke=RPI_C, sw=1, rx=2))
    p.append(text(648, 117, "PIO (RP2040)", size=11, color=RPI_C, anchor="start"))

    p.append(text(W//2, H - 12,
                  "Біт-бенгінг забирає все більше ядра; PIO виносить задачу цілком. Числа — 125 МГц, 30 кадрів/с.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-5-2-pio-cpu-budget.svg"), W, H, *p)
    print("OK fig-11-5-2-pio-cpu-budget.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.6.1  Профіль струму: Wi-Fi-сесія vs BLE-пакет
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_6_1_wifi_vs_ble_current():
    W, H = 800, 400
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.6.1  Заряд на Wi-Fi-сесію vs BLE-пакет (площа під кривою струму)",
                  size=14, bold=True))

    bx0, by0 = 70, 330
    time_w = 620

    # Осі
    p.append(arrow(bx0, by0, bx0 + time_w + 20, by0, color=INK, sw=1.5))
    p.append(text(bx0 + time_w + 30, by0 + 5, "час", size=12, color=INK, anchor="start"))
    p.append(arrow(bx0, by0, bx0, 70, color=INK, sw=1.5))
    p.append(text(bx0 - 10, 75, "I (мА)", size=12, color=INK, anchor="end"))

    # Шкала струму
    for ma, lbl in [(250, "250 мА"), (80, "80 мА"), (10, "10 мА"), (2, "2 мА")]:
        y = by0 - int((by0 - 75) * ma / 280)
        p.append(line(bx0 - 6, y, bx0 + 4, y, color=MUTED, sw=1))
        p.append(text(bx0 - 10, y + 4, lbl, size=10, color=MUTED, anchor="end"))

    # ── Wi-Fi-сесія (широка і висока) ────────────────────────────────────────
    wifi_x = bx0 + 30
    wifi_peak_y = by0 - int((by0 - 75) * 240 / 280)  # ~240 мА
    wifi_w = 240  # ~довга сесія

    # Профіль: підйом, плоско, спуск
    points_wifi = [
        (wifi_x, by0),
        (wifi_x + 8, wifi_peak_y),
        (wifi_x + wifi_w - 8, wifi_peak_y),
        (wifi_x + wifi_w, by0),
    ]
    poly_w = " ".join("%.1f,%.1f" % (x, y) for x, y in points_wifi)
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.30" stroke="%s" stroke-width="2.5"/>'
             % (poly_w, ESP_C, ESP_C))
    p.append(text(wifi_x + wifi_w // 2, wifi_peak_y - 12, "Wi-Fi-сесія\n~100–300 мс", size=11,
                  color=ESP_C, bold=True))
    # площа-підпис
    area_w = (wifi_w * (240 - 0) // 2) // 100  # умовно
    p.append(text(wifi_x + wifi_w // 2, by0 + 30,
                  "Площа ≈ великий заряд (мА·с)", size=10, color=ESP_C))

    # ── BLE-пакет (вузький і нижчий) ─────────────────────────────────────────
    ble_x = bx0 + 340
    ble_peak_y = by0 - int((by0 - 75) * 8 / 280)   # ~8 мА
    ble_w = 28  # ~короткий

    points_ble = [
        (ble_x, by0),
        (ble_x + 2, ble_peak_y),
        (ble_x + ble_w - 2, ble_peak_y),
        (ble_x + ble_w, by0),
    ]
    poly_b = " ".join("%.1f,%.1f" % (x, y) for x, y in points_ble)
    p.append('<polygon points="%s" fill="%s" fill-opacity="0.35" stroke="%s" stroke-width="2.5"/>'
             % (poly_b, NRF_C, NRF_C))
    p.append(text(ble_x + ble_w // 2, ble_peak_y - 14, "BLE-пакет\n~2–5 мс", size=11,
                  color=NRF_C, bold=True))
    p.append(text(ble_x + ble_w // 2, by0 + 30,
                  "Площа ≈ малий заряд", size=10, color=NRF_C))

    # Сон між пакетами (символічно)
    sleep_peak_y = by0 - int((by0 - 75) * 0.01 / 280)
    p.append(line(ble_x + ble_w, by0 - 4, bx0 + time_w - 30, by0 - 4,
                  color=NRF_C, sw=1.5, dash="4 3"))
    p.append(text(bx0 + time_w - 80, by0 - 12, "сон ~1 мкА", size=10, color=NRF_C))

    p.append(text(W//2, H - 12,
                  "Різниця площ — це різниця тижнів батарейки і років від монетки. Числа орієнтовні.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-6-1-wifi-vs-ble-current.svg"), W, H, *p)
    print("OK fig-11-6-1-wifi-vs-ble-current.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.7.1  Екосистема як шари над голим чипом
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_7_1_ecosystem_stack():
    W, H = 820, 460
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.7.1  Що купуєш разом із чипом: шари екосистеми важать більше за мегагерци",
                  size=13, bold=True))

    layers = [
        ("Спільнота & документація",  "#1a5276", "#d6eaf8",  62),
        ("Приклади & бібліотеки",     "#117a65", "#d1f2eb",  62),
        ("SDK / фреймворк",           "#7d3c98", "#f0e6fa",  62),
        ("HAL / драйвери",            "#d68910", "#fef9e7",  62),
        ("Чіп (залізо)",              "#6b7280", "#f4f6f8",  62),
    ]

    # ── Повний стек (зліва) ──────────────────────────────────────────────────
    sx0 = 80
    total_h = sum(lh for _, _, _, lh in layers)
    sy = 80
    p.append(text(sx0 + 200, sy - 14, "Чіп А — з екосистемою", size=13, bold=True, color=ECO_C))
    for name, stroke, fill, lh in layers:
        p.append(rect(sx0, sy, 400, lh, fill=fill, stroke=stroke, sw=2, rx=0))
        p.append(text(sx0 + 200, sy + lh // 2 + 5, name, size=13, bold=True, color=stroke))
        sy += lh

    # ── «Голий» стек (справа) ────────────────────────────────────────────────
    gx0 = 540
    sy = 80
    p.append(text(gx0 + 130, sy - 14, "Чіп Б — 'голий'", size=13, bold=True, color=POS))
    for i, (name, stroke, fill, lh) in enumerate(layers):
        if i == len(layers) - 1:  # тільки сам чіп є
            p.append(rect(gx0, sy, 260, lh, fill=fill, stroke=stroke, sw=2, rx=0))
            p.append(text(gx0 + 130, sy + lh // 2 + 5, name, size=13, bold=True, color=stroke))
        else:
            # порожній / сірий
            p.append(rect(gx0, sy, 260, lh, fill="#f5f5f5", stroke=MUTED, sw=1, rx=0))
            p.append(text(gx0 + 130, sy + lh // 2 + 5, "— відсутній —", size=12, color=MUTED))
        sy += lh

    # «Більше» / «менше» порівняння
    by0_comp = sy + 18
    bb, _, _ = textbox(sx0 + 200, by0_comp, "Більше МГц у чипа Б?", size=13, pad=10,
                        fill="#fff", stroke=MUTED, sw=1.5)
    p.append(bb)
    ba, _, _ = textbox(gx0 + 130, by0_comp, "Але програв по часу\nдо прототипу", size=13, pad=10,
                        fill="#fce8e8", stroke=POS, sw=2)
    p.append(ba)

    p.append(text(W//2, H - 12,
                  "Шари над чипом — це і є реальна цінність платформи. Гарне залізо без них — тупик.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-7-1-ecosystem-stack.svg"), W, H, *p)
    print("OK fig-11-7-1-ecosystem-stack.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.7.2  МГц vs Людино-дні (worked-приклад §4.11.7)
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_7_2_mhz_vs_days():
    W, H = 760, 380
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.7.2  Швидший чіп — довша дорога: час до прототипу й ризик вирішує екосистема",
                  size=13, bold=True))

    metrics = [
        ("Тактова частота\n(МГц)", 240, 180, "240 МГц", "180 МГц", True),   # Б 'виграє'
        ("Час до прото-\nтипу (дні)", 3, 22, "3 дні", "22 дні", False),     # А виграє
        ("Ризик неза-\nвершення", 10, 75, "низький", "високий", False),      # А виграє
    ]

    bx0, by0, bw, max_h = 90, 340, 140, 260

    for gi, (lbl, v_a, v_b, s_a, s_b, b_wins) in enumerate(metrics):
        cx = bx0 + gi * 215
        max_v = max(v_a, v_b)
        ha = int(max_h * v_a / max_v)
        hb = int(max_h * v_b / max_v)

        col_a = ECO_C if not b_wins else MUTED
        col_b = POS if not b_wins else ECO_C

        # Чіп А
        p.append(rect(cx, by0 - ha, bw * 0.44, ha, fill="#d1f2eb", stroke=col_a, sw=2, rx=3))
        p.append(text(cx + bw * 0.44 / 2, by0 - ha - 12, s_a, size=11, color=col_a, bold=True))
        p.append(text(cx + bw * 0.44 / 2, by0 + 14, "Чіп А\n(екосист.)", size=10, color=col_a))

        # Чіп Б
        bxb = cx + bw * 0.56
        p.append(rect(bxb, by0 - hb, bw * 0.44, hb, fill="#fce8e8", stroke=col_b, sw=2, rx=3))
        p.append(text(bxb + bw * 0.44 / 2, by0 - hb - 12, s_b, size=11, color=col_b, bold=True))
        p.append(text(bxb + bw * 0.44 / 2, by0 + 14, "Чіп Б\n(голий)", size=10, color=col_b))

        p.append(line(cx - 6, by0, cx + bw + 6, by0, color=MUTED, sw=1))
        p.append(mtext(cx + bw // 2, by0 + 42, lbl.split("\n"), size=11, color=INK))

    p.append(text(W//2, H - 12,
                  "Тактова частота — єдиний критерій де Б 'виграє'. По суті — програє по всьому важливому.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-7-2-mhz-vs-days.svg"), W, H, *p)
    print("OK fig-11-7-2-mhz-vs-days.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.8.1  Дерево рішень (чеклист вибору МК)
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_8_1_selection_flow():
    W, H = 820, 560
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.8.1  Від вимог до чипа: дерево питань відсікає непридатні класи МК",
                  size=14, bold=True))

    # Питання-вузли (зверху вниз по центру)
    questions = [
        (410, 75,  "Потрібне радіо?",           "Так → §4.11.6\n(ESP32/nRF)",   None),
        (410, 160, "Батарейне + роки?",          "Так → nRF-клас",               None),
        (410, 245, "Складна провідна периферія\n(мертвий час, >3 АЦП синхр.)?",
                                                  "Так → STM32-клас",            None),
        (410, 340, "Нестандартний протокол\nна жорсткому таймінгу?",
                                                  "Так → RP2040/PIO",            None),
        (410, 425, "Прості задачі + мінімум ціни?", "Так → AVR-клас (8-біт)",   None),
    ]

    for i, (qx, qy, qtext, yes_lbl, _) in enumerate(questions):
        # Ромб-питання
        qb, _, _ = textbox(qx, qy, qtext, size=12, pad=10, fill="#f0f4ff",
                            stroke=ARM_C, sw=2, rx=6)
        p.append(qb)

        # «Так» гілка вправо
        p.append(arrow(qx + 200, qy, qx + 290, qy, color=FIELD, sw=2))
        yb, _, _ = textbox(qx + 390, qy, yes_lbl, size=11, pad=8, fill="#d1f2eb",
                            stroke=FIELD, sw=1.5, rx=8)
        p.append(yb)

        # «Ні» стрілка вниз до наступного
        if i < len(questions) - 1:
            next_y = questions[i + 1][1]
            p.append(arrow(qx, qy + 30, qx, next_y - 18, color=MUTED, sw=1.5))
            p.append(text(qx - 20, (qy + next_y) // 2, "Ні", size=11, color=MUTED, anchor="end"))

    # Кінцевий вузол «Загальний 32-бітний МК»
    fb, _, _ = textbox(410, 505, "Загальний Cortex-M (STM32 / SAMD)\nабо перегляньте вимоги", size=11,
                        pad=10, fill="#f8f4ff", stroke=ARM_C, sw=2, rx=8)
    p.append(fb)
    p.append(arrow(410, 455, 410, 488, color=MUTED, sw=1.5))
    p.append(text(390, 473, "Ні", size=11, color=MUTED, anchor="end"))

    p.append(text(W//2, H - 12,
                  "Кожна «Так» — відповідь. Якщо пройшов усі «Ні» — переглянь вимоги або обирай загальний Cortex-M.",
                  size=11, color=MUTED))

    render(os.path.join(OUT, "fig-11-8-1-selection-flow.svg"), W, H, *p)
    print("OK fig-11-8-1-selection-flow.svg")


# ══════════════════════════════════════════════════════════════════════════════
# 4.11.8.2  Два проєкти — два МК (worked-приклад §4.11.8)
# ══════════════════════════════════════════════════════════════════════════════
def fig_11_8_2_two_projects_two_mcus():
    W, H = 820, 480
    p = []

    p.append(text(W//2, 26,
                  "Рис. 4.11.8.2  Один метод — різні відповіді: два проєкти → два різні класи МК",
                  size=14, bold=True))

    # ── Проєкт 1: Датчик повітря на батарейці + BLE ─────────────────────────
    col1_x = 60
    p.append(rect(col1_x, 55, 340, 44, fill=NRF_F, stroke=NRF_C, sw=2.5, rx=8))
    p.append(text(col1_x + 170, 82, "Датчик якості повітря (BLE + батарейка)", size=12,
                  bold=True, color=NRF_C))

    steps1 = [
        ("Радіо?",          "BLE → так",           NRF_C),
        ("Батарейне+роки?", "Роки → так",           NRF_C),
        ("→ nRF-клас",      "✓ Вибір зроблено",     FIELD),
    ]
    sy = 110
    for name, result, col in steps1:
        p.append(rect(col1_x + 10, sy, 155, 38, fill="#f9f9f9", stroke=col, sw=1.5, rx=5))
        p.append(text(col1_x + 88, sy + 14, name, size=11, bold=True, color=col))
        p.append(text(col1_x + 88, sy + 30, result, size=10, color=col))
        p.append(rect(col1_x + 180, sy, 160, 38, fill="#f9f9f9", stroke=FIELD, sw=1, rx=5))
        p.append(text(col1_x + 260, sy + 22, result, size=11, color=FIELD))
        sy += 52
    # Відсів
    killed = [("Wi-Fi SoC (ESP32)", POS, "струм"), ("STM32-клас", STM_C, "немає радіо"),
              ("AVR-клас", AVR_C, "немає BLE")]
    ky = 280
    p.append(text(col1_x + 170, ky - 14, "Відсіяні класи:", size=11, color=MUTED))
    for ki, (kn, kc, kr) in enumerate(killed):
        kb, _, _ = textbox(col1_x + 80 + ki * 85, ky + 14, kn + "\n✗ " + kr, size=9,
                            pad=6, fill="#fce8e8", stroke=kc, sw=1.5, rx=6)
        p.append(kb)

    # ── Роздільник ───────────────────────────────────────────────────────────
    p.append(line(418, 55, 418, H - 30, color=MUTED, sw=1, dash="6 4"))

    # ── Проєкт 2: Драйвер двигуна від мережі ─────────────────────────────────
    col2_x = 440
    p.append(rect(col2_x, 55, 340, 44, fill=STM_F, stroke=STM_C, sw=2.5, rx=8))
    p.append(text(col2_x + 170, 82, "Силовий драйвер двигуна (мережа)", size=12,
                  bold=True, color=STM_C))

    steps2 = [
        ("Радіо?",           "Провід → ні",          MUTED),
        ("Батарейне+роки?",  "Мережа → ні",          MUTED),
        ("Складна перифер.?", "6 ШІМ+3АЦП → так",   STM_C),
        ("→ STM32-клас",     "✓ Вибір зроблено",     FIELD),
    ]
    sy = 110
    for name, result, col in steps2:
        p.append(rect(col2_x + 10, sy, 155, 38, fill="#f9f9f9", stroke=col, sw=1.5, rx=5))
        p.append(text(col2_x + 88, sy + 14, name, size=11, bold=True, color=col))
        p.append(text(col2_x + 88, sy + 30, result, size=10, color=col))
        sy += 46
    sy = 280
    killed2 = [("ESP32", ESP_C, "надлишок"), ("nRF", NRF_C, "немає ШІМ"), ("AVR", AVR_C, "8-біт")]
    p.append(text(col2_x + 170, sy - 14, "Відсіяні класи:", size=11, color=MUTED))
    for ki, (kn, kc, kr) in enumerate(killed2):
        kb2, _, _ = textbox(col2_x + 80 + ki * 85, sy + 14, kn + "\n✗ " + kr, size=9,
                             pad=6, fill="#fce8e8", stroke=kc, sw=1.5, rx=6)
        p.append(kb2)

    # Висновок
    fin_b, _, _ = textbox(W // 2, H - 32,
                           "Метод однаковий — відповіді різні. Вимоги ведуть до класу, не смак.",
                           size=12, pad=10, fill="#f0f8ff", stroke=ARM_C, sw=2, rx=8)
    p.append(fin_b)

    render(os.path.join(OUT, "fig-11-8-2-two-projects-two-mcus.svg"), W, H, *p)
    print("OK fig-11-8-2-two-projects-two-mcus.svg")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    fig_11_1_1_mcu_map()
    fig_11_1_2_six_axes()
    fig_11_1_3_cost_of_overkill()
    fig_11_2_1_avr_datapath()
    fig_11_2_2_clock_budget()
    fig_11_3_1_arm_licensing()
    fig_11_3_2_cortexm_ladder()
    fig_11_4_1_stm32_vs_esp32_periph()
    fig_11_4_2_three_phase_channels()
    fig_11_5_1_pio_vs_bitbang()
    fig_11_5_2_pio_cpu_budget()
    fig_11_6_1_wifi_vs_ble_current()
    fig_11_7_1_ecosystem_stack()
    fig_11_7_2_mhz_vs_days()
    fig_11_8_1_selection_flow()
    fig_11_8_2_two_projects_two_mcus()
    print("=== Всі 16 фігур згенеровано ===")
