# -*- coding: utf-8 -*-
"""
Фігури для r13-low-power.md — Енергоощадність: жити роками від однієї батарейки.

fig-r13-1-1-budget-formula       — резервуар+витік + обернена задача
fig-r13-1-2-pulse-vs-average     — профіль (піки + сон) + середня лінія
fig-r13-2-1-current-map          — карта п'яти споживачів
fig-r13-2-2-dynamic-vs-static    — два стовпці природи струму
fig-r13-2-3-orders-of-magnitude  — логарифмічна шкала ESP32
fig-r13-3-1-sleep-ladder         — драбина режимів сну
fig-r13-3-2-sleep-compare        — порівняльна таблиця режимів
fig-r13-4-1-wakeup-sources       — карта джерел пробудження
fig-r13-4-2-rtc-gpio-pins        — RTC vs звичайні GPIO
fig-r13-5-1-ulp-guard            — потокова діаграма ULP-сторожа
fig-r13-5-2-ulp-economics        — порівняння двох стратегій
fig-r13-6-1-duty-cycle-profile   — анатомія циклу + формула
fig-r13-6-2-two-levers           — два важелі зниження I_сер
fig-r13-7-1-why-multimeter-lies  — мультиметр бреше
fig-r13-7-2-correct-measurement  — правильний вимір
fig-r13-8-1-who-doesnt-sleep     — карта паразитів плати
fig-r13-8-2-quiescent-budget     — бюджет спокою DevKit до/після
fig-r13-9-1-what-survives-deepsleep — карта пам'яті уві сні
fig-r13-9-2-wake-flow            — блок-схема старту після сну
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
os.makedirs(OUT, exist_ok=True)

# Додаткова палітра
ORANGE  = "#e67e22"
LORANGE = "#fdf2e9"
PURPLE  = "#8e44ad"
LPURPLE = "#f5eef8"
TEAL    = "#1a7a73"
LTEAL   = "#e8f8f7"
LGREY   = "#f0f0f0"
DGREY   = "#555555"
YELLOW  = "#f39c12"
LYELLOW = "#fef9e7"
DBLUE   = "#1a5276"
LBLUE   = "#d6eaf8"
GREEN   = "#27ae60"
LGREEN  = "#eafaf1"
RED     = "#c0392b"
LRED    = "#fdecea"


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.1.1 — Резервуар і витік + обернена задача
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_1_1():
    W, H = 760, 380
    frags = []

    # ─── Ліва частина: резервуар ───────────────────────────────────────────────
    tank_cx = 195
    tank_x  = tank_cx - 70
    tank_y  = 70
    tank_w  = 140
    tank_h  = 200

    # Контур бака (без дна)
    frags.append(rect(tank_x, tank_y, tank_w, tank_h, fill="#dbeafe",
                      stroke=NEG, sw=2.5, rx=4))

    # Вода (синя заливка ~65%)
    water_fill = int(tank_h * 0.65)
    frags.append(rect(tank_x + 2, tank_y + tank_h - water_fill,
                      tank_w - 4, water_fill - 2,
                      fill=NEG, stroke="none", sw=0, rx=2))

    # Підпис ємності
    tb1, _, _ = textbox(tank_cx, tank_y + tank_h - water_fill // 2,
                        "C = 220 мА·год\n(CR2032)", size=12, fill="#dbeafe",
                        stroke=NEG, sw=1.5, color=NEG, bold=True)
    frags.append(tb1)

    # Трубка-витік знизу праворуч
    pipe_x1 = tank_x + tank_w
    pipe_y  = tank_y + tank_h - 40
    pipe_x2 = pipe_x1 + 55
    frags.append(rect(pipe_x1, pipe_y - 10, 55, 20, fill=ORANGE, stroke=ORANGE, sw=0, rx=4))
    frags.append(arrow(pipe_x2, pipe_y, pipe_x2 + 30, pipe_y, color=ORANGE, sw=3))

    # Підпис витоку
    frags.append(text(pipe_x2 + 15, pipe_y + 24, "I_сер [мА]", size=12,
                      color=ORANGE, bold=True, anchor="middle"))
    frags.append(text(pipe_x2 + 15, pipe_y + 40, "витік", size=11,
                      color=ORANGE, anchor="middle"))

    # Формула під баком
    form_y = tank_y + tank_h + 35
    tb2, _, _ = textbox(tank_cx, form_y,
                        "t_життя [год] = C [мА·год] / I_сер [мА]",
                        size=14, fill=LGREEN, stroke=GREEN, sw=2, color=GREEN, bold=True)
    frags.append(tb2)

    # Ключова теза
    tb3, _, _ = textbox(tank_cx, form_y + 45,
                        "Вирішує СЕРЕДНІЙ струм — не піковий",
                        size=12, fill=LYELLOW, stroke=YELLOW, sw=1.5, color=INK)
    frags.append(tb3)

    # ─── Роздільник ─────────────────────────────────────────────────────────────
    sep_x = 400
    frags.append(line(sep_x, 55, sep_x, H - 30, color=MUTED, sw=1, dash="6,4"))

    # ─── Права частина: обернена задача ─────────────────────────────────────────
    rx = 430
    frags.append(text(rx + 145, 65, "Обернена задача:", size=14, bold=True, color=INK, anchor="middle"))

    rows = [
        ("Мета:", "прожити 1 рік = 8760 год", INK, LGREY, LINE),
        ("Батарея:", "CR2032 = 220 мА·год", NEG, LBLUE, NEG),
        ("Стеля струму:", "220 / 8760 ≈ 25 мкА", POS, LRED, POS),
    ]
    for i, (lbl, val, vc, fc, sc) in enumerate(rows):
        ry = 90 + i * 62
        frags.append(fitbox(rx, ry, 145, 44, lbl, size=13, bold=True, fill=LGREY, stroke=MUTED))
        frags.append(fitbox(rx + 153, ry, 175, 44, val, size=13, fill=fc, stroke=sc, color=vc, bold=(i == 2)))

    # Висновок
    tb4, _, _ = textbox(rx + 145, 285,
                        "Бюджет = ~25 мкА середнього\n→ мікроамперна дисципліна",
                        size=13, fill=LGREEN, stroke=GREEN, sw=2, color=GREEN, bold=True)
    frags.append(tb4)

    tb5, _, _ = textbox(rx + 145, 345,
                        "ESP32 у передачі = 150–250 мА\n→ у 6000 разів більше бюджету!",
                        size=11, fill=LRED, stroke=POS, sw=1.5, color=INK)
    frags.append(tb5)

    render(os.path.join(OUT, "fig-r13-1-1-budget-formula.svg"), W, H, *frags,
           title="Час життя = ємність ÷ середній струм")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.1.2 — Профіль струму: піки + сон + середня лінія
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_1_2():
    W, H = 720, 360
    frags = []

    PL, PR, PT, PB = 70, 660, 50, 270
    PLOT_W = PR - PL
    PLOT_H = PB - PT

    # Логарифмічна вісь: 1 мкА … 200 000 мкА
    Y_MIN, Y_MAX = 1, 200000

    def logy(ua):
        if ua <= 0: ua = 0.5
        frac = (math.log10(ua) - math.log10(Y_MIN)) / (math.log10(Y_MAX) - math.log10(Y_MIN))
        return PB - frac * PLOT_H

    # Осі
    frags.append(line(PL, PT, PL, PB, color=LINE, sw=1.5))
    frags.append(line(PL, PB, PR, PB, color=LINE, sw=1.5))

    # Y-тіки
    for ua, lbl in [(1, "1 мкА"), (10, "10 мкА"), (100, "100 мкА"),
                    (1000, "1 мА"), (10000, "10 мА"), (100000, "100 мА")]:
        y = logy(ua)
        frags.append(line(PL - 5, y, PL, y, color=MUTED, sw=1))
        frags.append(line(PL, y, PR, y, color=MUTED, sw=0.4, dash="3,4"))
        frags.append(text(PL - 8, y + 4, lbl, size=10, anchor="end", color=MUTED))

    # Профіль: 2 цикли (сон 82%, пік TX 18% по ширині для наочності)
    N_CYC = 2
    CYC_W = PLOT_W / (N_CYC + 0.4)
    SLP_W = CYC_W * 0.78
    ACT_W = CYC_W * 0.22

    I_SLEEP =     10   # мкА — deep-sleep
    I_ACT   = 160000   # мкА — TX пік
    I_AVG   =   2700   # мкА — середній (~2.67 мА, worked-example §4.13.1)

    ys = logy(I_SLEEP)
    ya = logy(I_ACT)
    yavg = logy(I_AVG)

    x = PL
    for _ in range(N_CYC):
        # Сон (синя лінія)
        frags.append(line(x, ys, x + SLP_W, ys, color=NEG, sw=2.5))
        # Підйом
        frags.append(line(x + SLP_W, ys, x + SLP_W, ya, color=POS, sw=1.8))
        # TX-пік (червоний)
        frags.append(line(x + SLP_W, ya, x + SLP_W + ACT_W, ya, color=POS, sw=3))
        # Спуск
        frags.append(line(x + SLP_W + ACT_W, ya, x + SLP_W + ACT_W, ys, color=POS, sw=1.8))
        x += SLP_W + ACT_W

    # Хвіст сну
    frags.append(line(x, ys, PR, ys, color=NEG, sw=2.5))

    # Заштрихована площа під TX (показуємо як прямокутник з прозорістю через overlay)
    # Малюємо прямокутники заливки під піками
    x2 = PL
    for _ in range(N_CYC):
        # Площа під TX
        ax = x2 + SLP_W
        frags.append(rect(ax, ya, ACT_W, PB - ya, fill="#fdecea", stroke="none", sw=0, rx=0))
        x2 += SLP_W + ACT_W

    # Середня лінія
    frags.append(line(PL, yavg, PR, yavg, color=GREEN, sw=2.2, dash="10,5"))
    frags.append(text(PR + 6, yavg + 4, "I_сер", size=12, anchor="start", color=GREEN, bold=True))
    frags.append(text(PR + 6, yavg + 18, "≈ 2.7 мА", size=11, anchor="start", color=GREEN))

    # Підписи рівнів
    frags.append(text(PL + 24, ys - 10, "сон  10 мкА", size=11, anchor="start", color=NEG, bold=True))
    frags.append(text(PL + SLP_W + ACT_W / 2, ya - 14, "TX 160 мА", size=11, anchor="middle", color=POS, bold=True))
    frags.append(text(PL + SLP_W + ACT_W / 2, ya - 28, "2 с / 60 с", size=10, anchor="middle", color=POS))

    # Рамка-теза
    tb, _, _ = textbox(W // 2, H - 28,
                       "Площа під піком (заряд) домінує — навіть рідкісний пік задирає середнє",
                       size=11, fill=LGREEN, stroke=GREEN, sw=1.5, color=INK, pad=8)
    frags.append(tb)

    # Підпис осі Y
    frags.append('<text x="14" y="%d" font-family="%s" font-size="11" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90,14,%d)">струм (лог. шкала)</text>'
                 % (PT + PLOT_H // 2, FONT, MUTED, PT + PLOT_H // 2))

    render(os.path.join(OUT, "fig-r13-1-2-pulse-vs-average.svg"), W, H, *frags,
           title="Вирішує середній струм: площа під піком, а не висота")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.2.1 — Карта п'яти споживачів струму чипа
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_2_1():
    W, H = 720, 380
    frags = []

    # Батарея зліва
    bat_cx = 80
    bat_cy = H // 2
    tb, _, _ = textbox(bat_cx, bat_cy, "Батарея\n(3.7 В)", size=13,
                       fill=LBLUE, stroke=NEG, sw=2.5, color=NEG, bold=True, pad=12)
    frags.append(tb)

    # Стрілка від батареї до LDO
    frags.append(arrow(bat_cx + 55, bat_cy, 180, bat_cy, color=ORANGE, sw=2.5))

    # LDO/PWR домен у центрі
    ldo_cx = 230
    ldo_cy = bat_cy
    tb_ldo, _, _ = textbox(ldo_cx, ldo_cy, "LDO /\nPWR", size=12,
                            fill=LORANGE, stroke=ORANGE, sw=2, color=ORANGE, bold=True, pad=10)
    frags.append(tb_ldo)

    # П'ять споживачів праворуч від LDO
    consumers = [
        ("① ЯДРА\n(CPU0+CPU1)", "~20–40 мА\nу роботі", NEG, LBLUE, 120),
        ("② РАДІО\n(Wi-Fi/BLE PA)", "~150–250 мА\nу TX ← домінант", POS, LRED, 200),
        ("③ ПЕРИФЕРІЯ\n(таймери, АЦП, шини)", "~1–10 мА\nпри тактуванні", TEAL, LTEAL, 280),
        ("④ ВИТОКИ\n(leakage, ↑T°)", "~мкА\n(росте з Т°)", PURPLE, LPURPLE, 340),
        ("⑤ СТАБІЛІЗАТОР\n(Iq втрати)", "1–5 мА\n(спокій LDO)", ORANGE, LORANGE, 400),
    ]

    cx_label = 430
    cx_val   = 620
    for (lbl, val, vc, fc, cy) in consumers:
        # Стрілка від LDO
        frags.append(arrow(ldo_cx + 55, ldo_cy, cx_label - 80, cy, color=MUTED, sw=1.5))
        # Рамка споживача
        tb_c, _, _ = textbox(cx_label, cy, lbl, size=11, fill=fc, stroke=vc, sw=1.8,
                             color=vc, bold=True, pad=8)
        frags.append(tb_c)
        # Струм
        tb_v, _, _ = textbox(cx_val, cy, val, size=11, fill=LGREY, stroke=MUTED, sw=1.2,
                             color=INK, pad=7)
        frags.append(tb_v)

    # Виділити радіо як домінанту
    frags.append(text(cx_label, 215, "← ДОМІНАНТА у TX", size=10, color=POS, anchor="middle"))

    tb_note, _, _ = textbox(W // 2, H - 22,
                             "Перший важіль економії — вимкнути або зрідити РАДІО",
                             size=11, fill=LRED, stroke=POS, sw=1.5, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-2-1-current-map.svg"), W, H, *frags,
           title="Карта споживачів струму чипа: куди тече енергія")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.2.2 — Динамічний vs статичний струм
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_2_2():
    W, H = 660, 380
    frags = []

    col_cx = [175, 490]
    titles = ["ДИНАМІЧНИЙ", "СТАТИЧНИЙ / витоки"]
    col_colors = [NEG, POS]
    col_fill   = [LBLUE, LRED]

    for i, (cx, ttl, vc, fc) in enumerate(zip(col_cx, titles, col_colors, col_fill)):
        frags.append(fitbox(cx - 150, 48, 300, 44, ttl, size=16, bold=True,
                            fill=fc, stroke=vc, sw=2.5, color=vc))

    # Динамічний стовпець
    dyn_items = [
        "∝ частота × C × V²",
        "зникає зі спиненням такту",
        "гейтинг тактів → майже нуль",
        "LIGHT-SLEEP: такти стоять",
        "→ динамічний струм ≈ 0",
    ]
    for j, item in enumerate(dyn_items):
        iy = 115 + j * 38
        tb, _, _ = textbox(col_cx[0], iy, item, size=12, fill=LBLUE, stroke=NEG, sw=1,
                           color=INK if j < 3 else NEG, bold=(j >= 3), pad=8)
        frags.append(tb)

    # Стрілка «гейтинг → зникає»
    frags.append(arrow(col_cx[0], 262, col_cx[0], 298, color=NEG, sw=2))
    tb_d, _, _ = textbox(col_cx[0], 320, "Вимикається ГЕЙТИНГОМ ТАКТІВ\n(light-sleep достатньо!)",
                         size=12, fill=LGREEN, stroke=GREEN, sw=2, color=GREEN, bold=True, pad=8)
    frags.append(tb_d)

    # Статичний стовпець
    stat_items = [
        "тече завжди при наявності V",
        "НЕ залежить від частоти",
        "росте з температурою",
        "прибрати → зняти живлення домену",
        "→ лише DEEP-SLEEP!",
    ]
    for j, item in enumerate(stat_items):
        iy = 115 + j * 38
        tb, _, _ = textbox(col_cx[1], iy, item, size=12, fill=LRED, stroke=POS, sw=1,
                           color=INK if j < 3 else POS, bold=(j >= 3), pad=8)
        frags.append(tb)

    frags.append(arrow(col_cx[1], 262, col_cx[1], 298, color=POS, sw=2))
    tb_s, _, _ = textbox(col_cx[1], 320, "Прибирається лише ЗНАТТЯМ ЖИВЛЕННЯ\n(deep-sleep знеструмлює домен)",
                         size=12, fill=LRED, stroke=POS, sw=2, color=POS, bold=True, pad=8)
    frags.append(tb_s)

    # Роздільник
    frags.append(line(W // 2, 48, W // 2, H - 30, color=MUTED, sw=1, dash="5,4"))

    render(os.path.join(OUT, "fig-r13-2-2-dynamic-vs-static.svg"), W, H, *frags,
           title="Два типи струму: чому сон працює і чому deep — глибше")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.2.3 — Логарифмічна шкала: 5 порядків ESP32
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_2_3():
    W, H = 680, 420
    frags = []

    # Вертикальна логарифмічна шкала
    PL, PR, PT, PB = 170, 580, 55, 340
    PLOT_H = PB - PT
    Y_MIN, Y_MAX = 1, 500000  # мкА

    def logy(ua):
        if ua <= 0: ua = 0.5
        frac = (math.log10(ua) - math.log10(Y_MIN)) / (math.log10(Y_MAX) - math.log10(Y_MIN))
        return PB - frac * PLOT_H

    # Вісь
    frags.append(line(PL, PT, PL, PB, color=LINE, sw=2))
    frags.append(arrow(PL, PB, PL, PT - 10, color=LINE, sw=1.5))
    frags.append(text(PL, PT - 20, "струм (мкА, лог.)", size=12, color=MUTED))

    # Рівні ESP32
    levels = [
        (250000, "Wi-Fi TX пік",        "~250 мА",  POS,    "#fdecea"),
        (35000,  "Активне ядро (без радіо)", "~35 мА", ORANGE, LORANGE),
        (800,    "Light-sleep",          "~0.8 мА",  TEAL,   LTEAL),
        (8,      "Deep-sleep",           "~8 мкА",   NEG,    LBLUE),
        (2.5,    "Hibernation",          "~2.5 мкА", PURPLE, LPURPLE),
    ]

    bar_w = 200
    cx_bar = (PL + PR) // 2

    for (ua, lbl, val, vc, fc) in levels:
        y = logy(ua)
        # Горизонтальна риска
        frags.append(line(PL - 8, y, PL, y, color=vc, sw=2))
        frags.append(line(PL, y, PR, y, color=MUTED, sw=0.5, dash="3,5"))
        # Кружок на осі
        frags.append(circle(PL, y, 5, fill=vc, stroke=vc, sw=0))
        # Рамка з підписом
        tb, _, _ = textbox(cx_bar + 50, y, lbl + "\n" + val, size=12,
                           fill=fc, stroke=vc, sw=1.8, color=vc, bold=True, pad=8)
        frags.append(tb)

    # Скоба «5 порядків»
    y_top = logy(250000)
    y_bot = logy(2.5)
    brace_x = PR - 25
    frags.append(line(brace_x, y_top, brace_x, y_bot, color=GREEN, sw=2.5))
    frags.append(line(brace_x - 8, y_top, brace_x + 8, y_top, color=GREEN, sw=2))
    frags.append(line(brace_x - 8, y_bot, brace_x + 8, y_bot, color=GREEN, sw=2))
    mid_y = (y_top + y_bot) / 2
    tb_5, _, _ = textbox(brace_x + 65, mid_y, "5 порядків\n(10⁵!)", size=13,
                         fill=LGREEN, stroke=GREEN, sw=2, color=GREEN, bold=True, pad=8)
    frags.append(tb_5)

    tb_note, _, _ = textbox(W // 2, H - 22,
                             "Динамічний діапазон 10⁵ — і причина економити сном, і чому вимірювати важко",
                             size=11, fill=LGREY, stroke=MUTED, sw=1.2, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-2-3-orders-of-magnitude.svg"), W, H, *frags,
           title="ESP32: п'ять порядків між TX і hibernation")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.3.1 — Драбина режимів сну
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_3_1():
    W, H = 820, 430
    frags = []

    steps = [
        # (назва, струм, що живе, контекст, колір)
        ("ACTIVE",        "~35–250 мА", "всі ядра + радіо + SRAM",  "повний",         "#c0392b", LRED),
        ("MODEM-SLEEP",   "~20–40 мА",  "ядра + SRAM; радіо вимкнено між TX", "повний", ORANGE, LORANGE),
        ("LIGHT-SLEEP",   "~0.8 мА",   "SRAM жива; ядра стоять; RTC",  "зберігається", TEAL, LTEAL),
        ("DEEP-SLEEP",    "~8–10 мкА", "лише RTC-домен + ULP",       "перезапуск!",    NEG, LBLUE),
        ("HIBERNATION",   "~2.5 мкА",  "тільки RTC-таймер",          "перезапуск!",    PURPLE, LPURPLE),
    ]

    step_h = 62
    step_w = 600
    step_x0 = 100
    step_y0 = 55
    indent = 18  # кожен крок зміщений вправо для «драбини»

    for i, (name, cur, alive, ctx, vc, fc) in enumerate(steps):
        sx = step_x0 + i * indent
        sy = step_y0 + i * (step_h + 8)

        frags.append(rect(sx, sy, step_w - i * indent, step_h, fill=fc, stroke=vc, sw=2.5, rx=6))

        # Назва
        frags.append(text(sx + 12, sy + 22, name, size=14, anchor="start", color=vc, bold=True))
        # Струм
        frags.append(text(sx + 12, sy + 40, "струм: " + cur, size=11, anchor="start", color=INK))
        # Живе / контекст
        frags.append(text(sx + 12, sy + 54, "живе: " + alive[:44], size=10, anchor="start", color=MUTED))

        # Контекст праворуч
        ctx_color = POS if "!" in ctx else GREEN
        frags.append(text(sx + step_w - i * indent - 12, sy + 34, ctx,
                          size=12, anchor="end", color=ctx_color, bold=True))

    # Стрілка «глибше →»
    arrow_x = step_x0 + len(steps) * indent + 25
    frags.append(arrow(arrow_x, step_y0, arrow_x, step_y0 + len(steps) * (step_h + 8) - 10,
                       color=MUTED, sw=2))
    frags.append(text(arrow_x + 12, step_y0 + len(steps) * (step_h + 8) // 2,
                      "менший\nструм", size=11, color=MUTED, anchor="start"))

    tb_note, _, _ = textbox(W // 2, H - 22,
                             "Що глибше — то менший струм, але то більше вимкнено і то дорожче прокидання",
                             size=11, fill=LGREY, stroke=MUTED, sw=1.2, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-3-1-sleep-ladder.svg"), W, H, *frags,
           title="Драбина сну ESP32: глибше = менший струм, але дорожче прокидання")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.3.2 — Порівняльна таблиця режимів (4 режими × 4 осі)
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_3_2():
    W, H = 800, 340
    frags = []

    headers = ["Режим", "Струм", "Що живе", "Час прокидання", "Характер старту"]
    col_w   = [140, 110, 200, 140, 165]
    col_x   = [20]
    for cw in col_w[:-1]:
        col_x.append(col_x[-1] + cw + 4)

    ROW_H = 56
    HEAD_Y = 48
    DATA_Y = HEAD_Y + ROW_H + 4

    # Заголовки
    for j, (hdr, cx) in enumerate(zip(headers, col_x)):
        frags.append(fitbox(cx, 16, col_w[j], 34, hdr, size=13, bold=True,
                            fill=LGREY, stroke=MUTED, sw=1.5, color=INK))

    modes = [
        # (назва,    струм,      що живе,                   час прок,        характер, colr, fill)
        ("MODEM-\nSLEEP",  "~20–40 мА",  "ядра + SRAM\nрадіо вимк між TX", "мікросекунди",  "продовження",   ORANGE, LORANGE),
        ("LIGHT-\nSLEEP",  "~0.8 мА",   "SRAM + RTC\nядра зупинені",       "мікросекунди",  "продовження\n(«пауза»)", TEAL, LTEAL),
        ("DEEP-\nSLEEP",   "~8–10 мкА", "RTC-домен\n+ ULP",                "мс (boot)",     "ПЕРЕЗАПУСК\nз main()",   NEG, LBLUE),
        ("HIBERNATION",    "~2.5 мкА",  "RTC-таймер\n(мінімум)",           "мс (boot)",     "ПЕРЕЗАПУСК\nз main()",   PURPLE, LPURPLE),
    ]

    for i, (name, cur, alive, wake_t, wake_k, vc, fc) in enumerate(modes):
        ry = DATA_Y + i * (ROW_H + 4)
        vals = [name, cur, alive, wake_t, wake_k]
        for j, (v, cx) in enumerate(zip(vals, col_x)):
            is_warn = "ПЕРЕЗАПУСК" in v
            frags.append(fitbox(cx, ry, col_w[j], ROW_H, v, size=11,
                                fill=(LRED if is_warn else fc),
                                stroke=(POS if is_warn else vc), sw=1.8,
                                color=(POS if is_warn else (vc if j == 0 else INK)),
                                bold=(j == 0 or is_warn)))

    render(os.path.join(OUT, "fig-r13-3-2-sleep-compare.svg"), W, H, *frags,
           title="Порівняння режимів сну: струм, що живе, прокидання")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.4.1 — Карта джерел пробудження
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_4_1():
    W, H = 760, 380
    frags = []

    # Сплячий чип у центрі
    chip_cx = 380
    chip_cy = 185
    tb_chip, _, _ = textbox(chip_cx, chip_cy, "Сплячий чип\n(deep-sleep)", size=14,
                            fill=LBLUE, stroke=NEG, sw=2.5, color=NEG, bold=True, pad=16)
    frags.append(tb_chip)

    # Чотири джерела навкруги
    sources = [
        # (назва, тримає живим, +струм, типово, cx, cy, vc, fc)
        ("① ТАЙМЕР\n(RTC timer)",      "RTC-таймер",         "+нА",     "Датчик раз на N хв",   145, 95,  ORANGE, LORANGE),
        ("② GPIO / ext\n(ext0/ext1)",  "RTC-GPIO (~мкА)",    "+1–5 мкА","Кнопка, INT давача",   620, 95,  TEAL,   LTEAL),
        ("③ ДОТИК\n(touch pad)",       "Ємнісний сканер",    "+30 мкА", "Кнопка без механіки",  145, 270, PURPLE, LPURPLE),
        ("④ ULP\n(co-processor)",      "ULP + RTC-АЦП",      "+10 мкА", "Поріг сигналу в сні",  620, 270, GREEN,  LGREEN),
    ]

    for (name, keeps, cost, use, scx, scy, vc, fc) in sources:
        tb_s, _, _ = textbox(scx, scy, name, size=12, fill=fc, stroke=vc, sw=2,
                             color=vc, bold=True, pad=10)
        frags.append(tb_s)
        # Рядок «тримає + струм»
        frags.append(text(scx, scy + 46, keeps + "  " + cost, size=10, color=vc, anchor="middle"))
        frags.append(text(scx, scy + 60, use, size=10, color=MUTED, anchor="middle"))
        # Стрілка до чипа
        frags.append(arrow(scx, scy + 30, chip_cx + (scx - chip_cx) * 0.55,
                           chip_cy + (scy - chip_cy) * 0.55, color=vc, sw=1.8))

    # Підказка про суміщення
    tb_multi, _, _ = textbox(chip_cx, H - 30,
                              "Можна ввімкнути кілька джерел одночасно — після пробудження\nпрошивка питає ПРИЧИНУ: esp_sleep_get_wakeup_cause()",
                              size=11, fill=LGREY, stroke=MUTED, sw=1.2, color=INK, pad=8)
    frags.append(tb_multi)

    render(os.path.join(OUT, "fig-r13-4-1-wakeup-sources.svg"), W, H, *frags,
           title="Джерела пробудження з deep-sleep і їхня ціна")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.4.2 — RTC vs звичайні GPIO у deep-sleep
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_4_2():
    W, H = 680, 340
    frags = []

    # Ліва панель: RTC-GPIO
    frags.append(fitbox(30, 48, 280, 50, "RTC-GPIO (можуть будити)", size=13, bold=True,
                        fill=LGREEN, stroke=GREEN, sw=2.5, color=GREEN))

    rtc_pins = ["GPIO0 (RTC_GPIO11)", "GPIO2 (RTC_GPIO12)", "GPIO4 (RTC_GPIO10)",
                "GPIO12–15, 25–27", "GPIO32–39 (RTC_GPIO0–7)"]
    for j, pin in enumerate(rtc_pins):
        py = 116 + j * 34
        frags.append(fitbox(30, py, 280, 30, pin, size=11, fill=LGREEN, stroke=GREEN, sw=1.2, color=INK))

    frags.append(fitbox(30, 290, 280, 34,
                        "INT давача → мусить бути тут!",
                        size=12, fill=LGREEN, stroke=GREEN, sw=2, bold=True, color=GREEN))

    # Роздільник
    frags.append(line(W // 2, 40, W // 2, H - 20, color=MUTED, sw=1.5, dash="6,4"))

    # Права панель: звичайні GPIO
    frags.append(fitbox(360, 48, 280, 50, "Звичайні GPIO — МЕРТВІ в deep-sleep", size=12, bold=True,
                        fill=LRED, stroke=POS, sw=2.5, color=POS))

    dead_pins = ["GPIO5–11 (SPI flash)", "GPIO16–24", "GPIO28–31", "...більшість пінів"]
    for j, pin in enumerate(dead_pins):
        py = 116 + j * 34
        frags.append(fitbox(360, py, 280, 30, pin, size=11, fill=LRED, stroke=POS, sw=1.2, color=MUTED))

    frags.append(fitbox(360, 290, 280, 34,
                        "Не розводь INT давача сюди — не прокинеш!",
                        size=12, fill=LRED, stroke=POS, sw=2, bold=True, color=POS))

    render(os.path.join(OUT, "fig-r13-4-2-rtc-gpio-pins.svg"), W, H, *frags,
           title="RTC-GPIO будять з deep-sleep; решта пінів у deep-sleep мертва")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.5.1 — Потокова діаграма «ULP-сторож порога»
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_5_1():
    W, H = 680, 480
    frags = []

    # Блок: ULP прокидається
    def box(cx, cy, lbl, fc, vc, bld=False):
        tb, _, _ = textbox(cx, cy, lbl, size=13, fill=fc, stroke=vc, sw=2, color=vc, bold=bld, pad=10)
        frags.append(tb)

    cx = W // 2

    box(cx, 68,  "RTC-таймер → ULP прокидається\n(кожні X мс)", LTEAL, TEAL, True)
    frags.append(arrow(cx, 100, cx, 132, color=TEAL, sw=2))

    box(cx, 158, "Читає RTC-АЦП / RTC-GPIO\n(вимір у мкс)", LTEAL, TEAL)
    frags.append(arrow(cx, 190, cx, 222, color=TEAL, sw=2))

    box(cx, 248, "Порівняти з порогом:\nv ≤ поріг?", LYELLOW, YELLOW)

    # Гілка «так» → продовжити сон
    frags.append(arrow(cx - 100, 248, 90, 248, color=GREEN, sw=2))
    frags.append(text(230, 240, "ТАК (норма)", size=11, color=GREEN, bold=True, anchor="end"))
    box(90, 310, "Записати в\nRTC-пам'ять\nуйти у halt", LGREEN, GREEN)
    frags.append(arrow(90, 355, 90, 390, color=GREEN, sw=2))
    box(90, 410, "Велике ядро\nСПИТЬ", LBLUE, NEG, True)
    frags.append(text(90, 450, "I ≈ мкА", size=11, color=NEG, bold=True, anchor="middle"))

    # Гілка «ні» → будити ядро
    frags.append(arrow(cx + 100, 248, 580, 248, color=POS, sw=2))
    frags.append(text(350, 240, "НІ (поріг!)", size=11, color=POS, bold=True, anchor="start"))
    box(580, 310, "ULP будить\nвелике ядро", LRED, POS, True)
    frags.append(arrow(580, 355, 580, 390, color=POS, sw=2))
    box(580, 410, "Ядро активне\nпередає тривогу", LRED, POS, True)
    frags.append(text(580, 450, "I ≈ мА (коротко!)", size=11, color=POS, bold=True, anchor="middle"))

    # Замкнути цикл від «halt» назад
    frags.append(line(90, 430, 30, 430, color=GREEN, sw=1.8))
    frags.append(line(30, 430, 30, 68, color=GREEN, sw=1.8))
    frags.append(arrow(30, 68, 75, 68, color=GREEN, sw=1.8))

    tb_note, _, _ = textbox(W // 2, H - 22,
                             "99% вимірів ULP відсіює сам — велике ядро не прокидається",
                             size=11, fill=LGREEN, stroke=GREEN, sw=1.5, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-5-1-ulp-guard.svg"), W, H, *frags,
           title="ULP як сторож порога: ядро прокидається лише на подію")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.5.2 — Економіка ULP: дві стратегії
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_5_2():
    W, H = 740, 380
    frags = []

    # Два графіки поряд (а) і (б)
    PL = [50, 400]
    for col in range(2):
        pl = PL[col]
        pr = pl + 300
        pt = 65
        pb = 270

        # Осі
        frags.append(line(pl, pt, pl, pb, color=LINE, sw=1.5))
        frags.append(line(pl, pb, pr, pb, color=LINE, sw=1.5))

        if col == 0:
            # (а): будити ядро раз на секунду на 50 мс
            label = "(а) Ядро будиться щосекунди"
            I_SLEEP = 0.05   # нормалізовано
            I_ACT   = 1.0
            n_pulses = 4
            cyw = (pr - pl) / n_pulses
            slw = cyw * 0.85
            acw = cyw * 0.15
            x = pl
            for _ in range(n_pulses):
                # Сон
                sy = pb - I_SLEEP * (pb - pt)
                frags.append(line(x, sy, x + slw, sy, color=NEG, sw=2.5))
                frags.append(line(x + slw, sy, x + slw, pb - I_ACT * (pb - pt), color=POS, sw=2))
                frags.append(line(x + slw, pb - I_ACT * (pb - pt), x + slw + acw, pb - I_ACT * (pb - pt), color=POS, sw=3))
                frags.append(line(x + slw + acw, pb - I_ACT * (pb - pt), x + slw + acw, sy, color=POS, sw=2))
                x += cyw

            # Площа виділена
            x2 = pl
            for _ in range(n_pulses):
                ax = x2 + slw
                ay = pb - I_ACT * (pb - pt)
                frags.append(rect(ax, ay, acw, pb - ay, fill="#fdecea", stroke="none", sw=0))
                x2 += cyw

            frags.append(text(pl + 150, 290, "I_avg ≈ 15 мА", size=12, color=POS, bold=True, anchor="middle"))
        else:
            # (б): ULP міряє щосекунди, ядро — раз на годину
            label = "(б) ULP міряє, ядро спить"
            I_SLEEP = 0.02
            I_ULP   = 0.04
            I_ACT   = 1.0
            n_pulses = 5
            cyw = (pr - pl) / n_pulses
            slw = cyw * 0.92
            ulp_w = cyw * 0.04
            x = pl
            for _ in range(n_pulses):
                sy = pb - I_SLEEP * (pb - pt)
                frags.append(line(x, sy, x + slw, sy, color=NEG, sw=2.5))
                # Крихітний ULP-пік
                ulp_y = pb - I_ULP * (pb - pt)
                frags.append(line(x + slw, sy, x + slw, ulp_y, color=GREEN, sw=1.5))
                frags.append(line(x + slw, ulp_y, x + slw + ulp_w, ulp_y, color=GREEN, sw=2))
                frags.append(line(x + slw + ulp_w, ulp_y, x + slw + ulp_w, sy, color=GREEN, sw=1.5))
                x += cyw

            # Один рідкісний великий пік справа (ядро раз на тривалий час)
            ax = pr - 20
            ay = pb - I_ACT * (pb - pt)
            frags.append(rect(ax, ay, 15, pb - ay, fill="#fdecea", stroke="none", sw=0))
            frags.append(line(ax, pb, ax, ay, color=POS, sw=2.5))
            frags.append(line(ax, ay, ax + 15, ay, color=POS, sw=3))
            frags.append(line(ax + 15, ay, ax + 15, pb, color=POS, sw=2.5))
            frags.append(text(ax + 7, ay - 8, "ядро\n(рідко)", size=9, color=POS, anchor="middle"))

            frags.append(text(pl + 150, 290, "I_avg ≈ 12 мкА", size=12, color=GREEN, bold=True, anchor="middle"))

        frags.append(text(pl + 150, 47, label, size=12, color=INK, bold=True, anchor="middle"))

    tb_note, _, _ = textbox(W // 2, H - 22,
                             "ULP замість частих пробуджень ядра → виграш струму на 3 порядки",
                             size=11, fill=LGREEN, stroke=GREEN, sw=1.5, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-5-2-ulp-economics.svg"), W, H, *frags,
           title="Економіка ULP: ядро щосекунди (а) проти ULP міряє (б)")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.6.1 — Анатомія циклу: профіль струму + формула
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_6_1():
    W, H = 760, 400
    frags = []

    PL, PR, PT, PB = 70, 680, 55, 290
    PLOT_W = PR - PL
    PLOT_H = PB - PT
    Y_MIN, Y_MAX = 1, 250000

    def logy(ua):
        if ua <= 0: ua = 0.5
        frac = (math.log10(ua) - math.log10(Y_MIN)) / (math.log10(Y_MAX) - math.log10(Y_MIN))
        return PB - frac * PLOT_H

    # Осі
    frags.append(line(PL, PT, PL, PB, color=LINE, sw=1.5))
    frags.append(line(PL, PB, PR, PB, color=LINE, sw=1.5))

    # Y-тіки
    for ua, lbl in [(10, "10 мкА"), (1000, "1 мА"), (10000, "10 мА"), (100000, "100 мА")]:
        y = logy(ua)
        frags.append(line(PL - 5, y, PL, y, color=MUTED, sw=1))
        frags.append(line(PL, y, PR, y, color=MUTED, sw=0.4, dash="3,4"))
        frags.append(text(PL - 8, y + 4, lbl, size=10, anchor="end", color=MUTED))

    # Фази одного циклу T = 600 с (10 хв)
    # Відображаємо лінійно за часом, але «розтягуємо» короткі фази для наочності
    # Реальні тривалості: boot 1.2с, measure 0.2с, TX 0.3с, sleep ~598с
    # Візуальні ширини (пікселів):
    phases = [
        # (назва, I_мкА, ширина_px, колір, колір_заливки)
        ("WAKE\n1.2 с", 120000, 80, ORANGE, LORANGE),
        ("MEASURE\n0.2 с", 25000, 55, TEAL, LTEAL),
        ("RADIO TX\n0.3 с", 180000, 100, POS, LRED),
        ("SLEEP\n~598 с", 10, PLOT_W - 80 - 55 - 100, NEG, LBLUE),
    ]

    x = PL
    phase_data = []
    for (name, ua, pw, vc, fc) in phases:
        y_top = logy(ua)
        # Заливка площі
        frags.append(rect(x, y_top, pw, PB - y_top, fill=fc, stroke="none", sw=0, rx=0))
        # Лінія профілю
        frags.append(line(x, y_top, x + pw, y_top, color=vc, sw=2.5))
        frags.append(line(x, PB, x, y_top, color=vc, sw=1.5))
        frags.append(line(x + pw, PB, x + pw, y_top, color=vc, sw=1.5))
        # Підпис фази
        label_y = max(y_top - 10, PT + 12)
        frags.append(text(x + pw / 2, label_y, name, size=10, anchor="middle", color=vc, bold=True))
        phase_data.append((x, pw, y_top, vc))
        x += pw

    # Середній струм — пунктир
    I_avg = 2700  # мкА (≈ worked-example §4.13.6)
    y_avg = logy(I_avg)
    frags.append(line(PL, y_avg, PR, y_avg, color=GREEN, sw=2.2, dash="10,5"))
    frags.append(text(PR + 6, y_avg + 4, "I_сер", size=12, anchor="start", color=GREEN, bold=True))
    frags.append(text(PR + 6, y_avg + 18, "≈ 2.7 мА", size=11, anchor="start", color=GREEN))

    # Формула
    tb_f, _, _ = textbox(W // 2, H - 50,
                         "I_сер = Q_цикл / T_цикл = (Σ I_фази × t_фази) / T",
                         size=13, fill=LGREEN, stroke=GREEN, sw=2, color=GREEN, bold=True, pad=8)
    frags.append(tb_f)

    tb_note, _, _ = textbox(W // 2, H - 22,
                             "Площа TX домінує — попри коротку тривалість; сон дає найбільший час, але не заряд",
                             size=11, fill=LGREY, stroke=MUTED, sw=1.2, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-6-1-duty-cycle-profile.svg"), W, H, *frags,
           title="Анатомія циклу: середній струм = повний заряд ÷ період")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.6.2 — Два важелі зниження I_сер
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_6_2():
    W, H = 700, 360
    frags = []

    # Базовий профіль зліва
    PL, PT, PB = 50, 70, 220
    PLOT_H = PB - PT

    def draw_profile(x0, n_cyc, slp_w, act_w, i_act_h, label, vc, show_avg, i_avg_h):
        """Намалювати профіль (нормалізований за висотою)."""
        x = x0
        for _ in range(n_cyc):
            # Сон
            frags.append(line(x, PB - 3, x + slp_w, PB - 3, color=NEG, sw=2))
            # Підйом
            frags.append(line(x + slp_w, PB - 3, x + slp_w, PB - i_act_h, color=vc, sw=1.8))
            # Активна фаза
            frags.append(line(x + slp_w, PB - i_act_h, x + slp_w + act_w, PB - i_act_h, color=vc, sw=3))
            # Спуск
            frags.append(line(x + slp_w + act_w, PB - i_act_h, x + slp_w + act_w, PB - 3, color=vc, sw=1.8))
            x += slp_w + act_w
        frags.append(line(x, PB - 3, x0 + n_cyc * (slp_w + act_w) + 10, PB - 3, color=NEG, sw=2))

        if show_avg:
            # Середня лінія
            xr = x0 + n_cyc * (slp_w + act_w)
            frags.append(line(x0, PB - i_avg_h, xr, PB - i_avg_h, color=GREEN, sw=2, dash="8,5"))
            frags.append(text(xr + 4, PB - i_avg_h + 4, "I_сер", size=10, color=GREEN, bold=True, anchor="start"))

        frags.append(text(x0 + n_cyc * (slp_w + act_w) // 2, PT - 14, label, size=12,
                          color=INK, bold=True, anchor="middle"))

    # (а) Базовий
    draw_profile(PL, 3, 70, 30, 130, "(а) Базовий", POS, True, 40)

    # Стрілки двох важелів
    arr_y = PT - 30
    arr_cx = W // 2

    frags.append(text(arr_cx, arr_y, "Два важелі:", size=13, color=INK, bold=True, anchor="middle"))

    # Важіль 1: зменшити висоту піку
    frags.append(text(200, arr_y + 16, "① Менший заряд TX\n(коротша/слабша передача)", size=11,
                      color=POS, anchor="middle"))
    frags.append(arrow(200, arr_y + 38, 200, PT + 8, color=POS, sw=1.8))

    # Важіль 2: розтягнути сон
    frags.append(text(520, arr_y + 16, "② Довший сон\n(рідші прокидання)", size=11,
                      color=NEG, anchor="middle"))
    frags.append(arrow(520, arr_y + 38, 520, PT + 8, color=NEG, sw=1.8))

    # (б) Менший пік
    draw_profile(250, 3, 70, 20, 80, "(б) Менший TX", POS, True, 25)

    # (в) Довший сон
    draw_profile(440, 2, 100, 30, 130, "(в) Довший сон", NEG, True, 25)

    # Пояснення нижче
    tb_note, _, _ = textbox(W // 2, H - 28,
                             "Подвоїв період сну → удвічі менший I_сер; скоротив TX → менший заряд за цикл",
                             size=11, fill=LGREEN, stroke=GREEN, sw=1.5, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-6-2-two-levers.svg"), W, H, *frags,
           title="Два важелі часу життя: менший TX і рідші прокидання")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.7.1 — Чому мультиметр бреше
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_7_1():
    W, H = 720, 360
    frags = []

    PL, PR, PT, PB = 60, 650, 55, 260
    PLOT_W = PR - PL
    PLOT_H = PB - PT
    Y_MIN, Y_MAX = 1, 250000

    def logy(ua):
        if ua <= 0: ua = 0.5
        frac = (math.log10(ua) - math.log10(Y_MIN)) / (math.log10(Y_MAX) - math.log10(Y_MIN))
        return PB - frac * PLOT_H

    frags.append(line(PL, PT, PL, PB, color=LINE, sw=1.5))
    frags.append(line(PL, PB, PR, PB, color=LINE, sw=1.5))

    for ua, lbl in [(10, "10 мкА"), (1000, "1 мА"), (10000, "10 мА"), (100000, "100 мА")]:
        y = logy(ua)
        frags.append(line(PL - 5, y, PL, y, color=MUTED, sw=1))
        frags.append(line(PL, y, PR, y, color=MUTED, sw=0.4, dash="3,4"))
        frags.append(text(PL - 8, y + 4, lbl, size=10, anchor="end", color=MUTED))

    # Реальний профіль
    CYC_W = (PLOT_W) // 3
    SLP_W = int(CYC_W * 0.80)
    ACT_W = CYC_W - SLP_W
    x = PL

    for _ in range(3):
        ys = logy(10)
        ya = logy(180000)
        frags.append(line(x, ys, x + SLP_W, ys, color=NEG, sw=2))
        frags.append(line(x + SLP_W, ys, x + SLP_W, ya, color=POS, sw=1.8))
        frags.append(line(x + SLP_W, ya, x + SLP_W + ACT_W, ya, color=POS, sw=3))
        frags.append(line(x + SLP_W + ACT_W, ya, x + SLP_W + ACT_W, ys, color=POS, sw=1.8))
        x += CYC_W

    # Вікно усереднення мультиметра — широкий прямокутник
    win_x = PL + SLP_W - 20
    win_w = ACT_W + 80
    win_color = YELLOW
    frags.append(rect(win_x, PT + 5, win_w, PB - PT - 10, fill="#fef9e7", stroke=YELLOW, sw=2, rx=4))
    frags.append(text(win_x + win_w // 2, PT + 20, "Вікно\nусереднення\nмультиметра", size=10,
                      color=YELLOW, anchor="middle", bold=True))

    # Показ мультиметра — горизонтальна лінія "3 мА"
    y_mm = logy(3000)
    frags.append(line(win_x, y_mm, win_x + win_w, y_mm, color=YELLOW, sw=2.5, dash="6,4"))
    frags.append(text(win_x + win_w + 6, y_mm + 4, "«3 мА»\n(мультиметр)", size=10,
                      color=YELLOW, bold=True, anchor="start"))

    # Чесне середнє
    y_true = logy(90)  # ~90 мкА
    frags.append(line(PL, y_true, PR, y_true, color=GREEN, sw=2, dash="10,5"))
    frags.append(text(PR + 6, y_true + 4, "~90 мкА\n(реальне середнє)", size=10,
                      color=GREEN, bold=True, anchor="start"))

    tb_note, _, _ = textbox(W // 2, H - 28,
                             "Мультиметр «розмазує» пік і показує ~3 мА — у 30 разів більше від реального 90 мкА",
                             size=11, fill=LYELLOW, stroke=YELLOW, sw=1.5, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-7-1-why-multimeter-lies.svg"), W, H, *frags,
           title="Мультиметр бреше: вікно усереднення розмазує короткі піки TX")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.7.2 — Правильний вимір: шунт + осцилограф
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_7_2():
    W, H = 760, 360
    frags = []

    # Схема кола зліва
    # Батарея → шунт → чип → повернення

    bat_x, bat_y = 50, 100
    tb_bat, _, _ = textbox(bat_x, bat_y, "Батарея\n3.3 В", size=12, fill=LBLUE, stroke=NEG, sw=2, color=NEG, bold=True)
    frags.append(tb_bat)

    # Лінія від батареї до шунта
    frags.append(line(bat_x + 50, bat_y, 170, bat_y, color=LINE, sw=2))

    # Шунт
    shunt_cx = 220
    frags.append(fitbox(shunt_cx - 40, bat_y - 22, 80, 44, "Шунт\n0.1 Ом", size=12,
                        fill=LORANGE, stroke=ORANGE, sw=2, color=ORANGE, bold=True))
    # Напруга на шунті — вертикальна стрілка
    frags.append(line(shunt_cx, bat_y + 22, shunt_cx, bat_y + 60, color=ORANGE, sw=1.5))
    frags.append(text(shunt_cx + 5, bat_y + 50, "V_шунт = I × R", size=10, color=ORANGE, anchor="start"))

    # Від шунта до чипа
    frags.append(line(shunt_cx + 40, bat_y, 330, bat_y, color=LINE, sw=2))

    # Чип
    chip_cx = 390
    tb_chip, _, _ = textbox(chip_cx, bat_y, "ESP32\n(чип)", size=12, fill=LBLUE, stroke=NEG, sw=2, color=NEG, bold=True)
    frags.append(tb_chip)

    # Повернення (GND)
    frags.append(line(chip_cx + 50, bat_y, 520, bat_y, color=LINE, sw=2))
    frags.append(line(520, bat_y, 520, 200, color=LINE, sw=2))
    frags.append(line(520, 200, bat_x, 200, color=LINE, sw=2))
    frags.append(line(bat_x, 200, bat_x, bat_y + 30, color=LINE, sw=2))

    # Осцилограф підключений до шунта
    osc_cx = 220
    osc_cy = 245
    frags.append(line(shunt_cx - 20, bat_y + 22, osc_cx - 60, osc_cy - 25, color=TEAL, sw=1.5, dash="4,3"))
    frags.append(line(shunt_cx + 20, bat_y + 22, osc_cx + 60, osc_cy - 25, color=TEAL, sw=1.5, dash="4,3"))
    tb_osc, _, _ = textbox(osc_cx, osc_cy, "Осцилограф /\nPower Profiler", size=12,
                           fill=LTEAL, stroke=TEAL, sw=2, color=TEAL, bold=True, pad=10)
    frags.append(tb_osc)

    # Виносна формула-коробка справа
    tb_form, _, _ = textbox(600, 120,
                             "I(t) = V_шунт(t) / R\n\nI_сер = ∫I(t)dt / T\n    = площа ÷ час",
                             size=12, fill=LGREEN, stroke=GREEN, sw=2, color=GREEN, bold=True, pad=10)
    frags.append(tb_form)

    # Попередження про burden voltage
    tb_warn, _, _ = textbox(590, 250,
                             "⚠ Burden voltage:\nна піку I×R просаджує\nживлення чипа → brownout",
                             size=11, fill=LYELLOW, stroke=YELLOW, sw=1.5, color=INK, pad=8)
    frags.append(tb_warn)

    tb_note, _, _ = textbox(W // 2, H - 22,
                             "Єдина чесна метрика — площа під профілем струму (інтеграл), а не «що показав дисплей»",
                             size=11, fill=LGREEN, stroke=GREEN, sw=1.5, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-7-2-correct-measurement.svg"), W, H, *frags,
           title="Чесний вимір: шунт + осцилограф, інтеграл профілю = I_сер")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.8.1 — Карта «хто не спить на платі»
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_8_1():
    W, H = 760, 380
    frags = []

    # Батарея зліва
    tb_bat, _, _ = textbox(75, 140, "Батарея", size=12, fill=LBLUE, stroke=NEG, sw=2, color=NEG, bold=True)
    frags.append(tb_bat)
    frags.append(arrow(75 + 50, 140, 170, 140, color=LINE, sw=2))

    # Чип ESP32 (deep-sleep) — маленький струм
    chip_cx = 570
    chip_cy = 140
    tb_chip, _, _ = textbox(chip_cx, chip_cy, "ESP32\ndeep-sleep\n~10 мкА", size=12,
                            fill=LGREEN, stroke=GREEN, sw=2, color=GREEN, bold=True, pad=10)
    frags.append(tb_chip)

    # Паразити — стовпчики
    parasites = [
        # (назва, струм_мА, колір, fill)
        ("Power-LED\n(статус)", 4.0, POS, LRED),
        ("LDO\n(Iq=1.2 мА)", 1.2, ORANGE, LORANGE),
        ("USB-UART\nміст", 0.5, PURPLE, LPURPLE),
        ("Підтяжки\n3×10кОм", 0.3, YELLOW, LYELLOW),
        ("Давач\n(standby)", 0.2, TEAL, LTEAL),
    ]

    bar_x0 = 190
    bar_y_base = 290
    bar_max_h = 160
    max_ma = 4.5
    bar_w = 72
    gap = 10

    x = bar_x0
    for (name, ma, vc, fc) in parasites:
        bh = int(bar_max_h * ma / max_ma)
        by = bar_y_base - bh
        frags.append(rect(x, by, bar_w, bh, fill=fc, stroke=vc, sw=2, rx=4))
        frags.append(text(x + bar_w // 2, by - 14, "%.1f мА" % ma, size=11, color=vc, bold=True, anchor="middle"))
        frags.append(text(x + bar_w // 2, by - 28, name.split("\n")[0], size=10, color=vc, anchor="middle"))
        if "\n" in name:
            frags.append(text(x + bar_w // 2, by - 40, name.split("\n")[1], size=10, color=vc, anchor="middle"))
        x += bar_w + gap

    # Стрілка від паразитів до чипа
    frags.append(line(bar_x0 + len(parasites) * (bar_w + gap) - gap // 2, bar_y_base - 80,
                      chip_cx - 55, chip_cy, color=MUTED, sw=1.5, dash="4,3"))

    # Базова лінія
    frags.append(line(bar_x0 - 5, bar_y_base, x - gap + 5, bar_y_base, color=MUTED, sw=1.5))

    # Чип-стовпчик (майже невидимий)
    chip_bar_x = x
    chip_bh = int(bar_max_h * 0.01 / max_ma + 2)
    frags.append(rect(chip_bar_x, bar_y_base - chip_bh, bar_w, chip_bh, fill=LGREEN, stroke=GREEN, sw=2, rx=2))
    frags.append(text(chip_bar_x + bar_w // 2, bar_y_base - chip_bh - 8, "0.01 мА", size=10, color=GREEN, bold=True, anchor="middle"))
    frags.append(text(chip_bar_x + bar_w // 2, bar_y_base - chip_bh - 20, "ESP32\n(чип)", size=10, color=GREEN, anchor="middle"))

    tb_note, _, _ = textbox(W // 2, H - 22,
                             "Паразити плати ×100–400 більші за сплячий чип — борешся з ПЛАТОЮ, не з чипом",
                             size=11, fill=LRED, stroke=POS, sw=1.5, color=INK, pad=8)
    frags.append(tb_note)

    render(os.path.join(OUT, "fig-r13-8-1-who-doesnt-sleep.svg"), W, H, *frags,
           title="Хто на платі не спить: паразитний струм у порівнянні з чипом")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.8.2 — Бюджет спокою DevKit до/після оптимізації
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_8_2():
    W, H = 740, 380
    frags = []

    categories = [
        ("Power-LED", 4.0, 0.0),
        ("LDO Iq", 1.2, 0.010),   # low-Iq LDO = 10 мкА
        ("USB-міст", 0.5, 0.0),
        ("Підтяжки", 0.3, 0.10),
        ("ESP32", 0.01, 0.010),
    ]

    totals = [sum(b for (_, b, _) in categories), sum(a for (_, _, a) in categories)]

    # Два стовпчики для кожної категорії
    BAR_W = 55
    BAR_GAP = 12
    GROUP_GAP = 28
    Y_BASE = 290
    MAX_H  = 200

    max_val = max(b for (_, b, _) in categories)

    frags.append(text(150, 40, "DevKit «з коробки»", size=13, bold=True, color=POS, anchor="middle"))
    frags.append(text(490, 40, "Після оптимізації", size=13, bold=True, color=GREEN, anchor="middle"))

    # Зірочка-виноска для LED і USB-міст після оптимізації (= 0)
    x = 50
    for (cat, before_ma, after_ma) in categories:
        for col, ma, vc in [(0, before_ma, POS), (1, after_ma, GREEN)]:
            bh = max(int(MAX_H * ma / max_val), 2)
            bx = x + col * (BAR_W + BAR_GAP)
            by = Y_BASE - bh
            fc = LRED if col == 0 else LGREEN
            frags.append(rect(bx, by, BAR_W, bh, fill=fc, stroke=vc, sw=1.8, rx=4))
            if ma >= 0.05:
                frags.append(text(bx + BAR_W // 2, by - 12,
                                  "%.1f мА" % ma if ma >= 0.1 else "%.0f мкА" % (ma * 1000),
                                  size=10, color=vc, bold=True, anchor="middle"))
        # Мітка категорії
        frags.append(text(x + BAR_W + BAR_GAP // 2, Y_BASE + 14, cat,
                          size=10, color=INK, anchor="middle"))
        x += 2 * BAR_W + BAR_GAP + GROUP_GAP

    # Базова лінія
    frags.append(line(45, Y_BASE, x, Y_BASE, color=MUTED, sw=1.5))

    # Загальні суми
    tb_b, _, _ = textbox(150, Y_BASE + 50,
                         "Разом (до): ~6 мА\nt_CR2032 ≈ 37 год",
                         size=12, fill=LRED, stroke=POS, sw=2, color=POS, bold=True, pad=8)
    frags.append(tb_b)

    tb_a, _, _ = textbox(490, Y_BASE + 50,
                         "Разом (після): ~0.12 мА\nt_CR2032 ≈ 1700 год ≈ 45×",
                         size=12, fill=LGREEN, stroke=GREEN, sw=2, color=GREEN, bold=True, pad=8)
    frags.append(tb_a)

    render(os.path.join(OUT, "fig-r13-8-2-quiescent-budget.svg"), W, H, *frags,
           title="Бюджет спокою DevKit: до оптимізації і після (×45 часу життя)")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.9.1 — Що переживає deep-sleep: карта пам'яті
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_9_1():
    W, H = 720, 360
    frags = []

    # Ліва панель: гине
    frags.append(fitbox(20, 45, 310, 46, "ГИНЕ в deep-sleep", size=14, bold=True,
                        fill=LRED, stroke=POS, sw=2.5, color=POS))

    dead_items = [
        "Звичайна SRAM (512 КБ+)",
        "Регістри периферії",
        "Стан Wi-Fi / BLE",
        "Всі глобальні змінні",
        "Стек, heap, стан задач",
    ]
    for j, item in enumerate(dead_items):
        frags.append(fitbox(20, 105 + j * 38, 310, 34, item, size=12,
                            fill=LRED, stroke=POS, sw=1.2, color=INK))

    frags.append(fitbox(20, 306, 310, 36,
                        "→ після пробудження = ПЕРЕЗАПУСК із main()",
                        size=12, bold=True, fill=LRED, stroke=POS, sw=2, color=POS))

    # Роздільник
    frags.append(line(W // 2, 40, W // 2, H - 20, color=MUTED, sw=1.5, dash="6,4"))

    # Права панель: живе
    frags.append(fitbox(380, 45, 310, 46, "ЖИВЕ в deep-sleep (RTC-домен)", size=13, bold=True,
                        fill=LGREEN, stroke=GREEN, sw=2.5, color=GREEN))

    alive_items = [
        "RTC SLOW пам'ять (~8 КБ)",
        "RTC FAST пам'ять (~8 КБ)",
        "RTC-таймер / будильник",
        "RTC-GPIO (підмножина)",
        "ULP-співпроцесор",
    ]
    for j, item in enumerate(alive_items):
        frags.append(fitbox(380, 105 + j * 38, 310, 34, item, size=12,
                            fill=LGREEN, stroke=GREEN, sw=1.2, color=INK))

    frags.append(fitbox(380, 306, 310, 36,
                        "RTC_DATA_ATTR → кладемо 'спомин' сюди",
                        size=12, bold=True, fill=LGREEN, stroke=GREEN, sw=2, color=GREEN))

    render(os.path.join(OUT, "fig-r13-9-1-what-survives-deepsleep.svg"), W, H, *frags,
           title="Що переживає deep-sleep: SRAM гине, RTC-пам'ять живе")


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.13.9.2 — Блок-схема старту після сну
# ═══════════════════════════════════════════════════════════════════════════════
def fig_r13_9_2():
    W, H = 680, 490
    frags = []

    cx = W // 2

    def bx(cy, lbl, fc, vc, bld=False):
        tb, _, _ = textbox(cx, cy, lbl, size=13, fill=fc, stroke=vc, sw=2,
                           color=vc, bold=bld, pad=10)
        frags.append(tb)

    # boot
    bx(55, "boot → app_main()", LGREY, LINE, True)
    frags.append(arrow(cx, 82, cx, 112, color=LINE, sw=2))

    # дізнатись причину
    bx(135, "esp_sleep_get_wakeup_cause()\n(дізнатись причину)", LBLUE, NEG)
    frags.append(arrow(cx, 163, cx, 193, color=LINE, sw=2))

    # Ромб — рішення
    diamond_cy = 218
    d_w, d_h = 180, 44
    frags.append(('<polygon points="%d,%d %d,%d %d,%d %d,%d" fill="%s" stroke="%s" stroke-width="2"/>'
                 % (cx, diamond_cy - d_h // 2,
                    cx + d_w // 2, diamond_cy,
                    cx, diamond_cy + d_h // 2,
                    cx - d_w // 2, diamond_cy,
                    LYELLOW, YELLOW)))
    frags.append(text(cx, diamond_cy + 5, "зі сну?", size=13, color=ORANGE, bold=True, anchor="middle"))

    # Гілка «ТАК» (зі сну) — вниз
    frags.append(text(cx + 10, diamond_cy + d_h // 2 + 18, "ТАК", size=12, color=GREEN, bold=True, anchor="start"))
    frags.append(arrow(cx, diamond_cy + d_h // 2, cx, diamond_cy + d_h // 2 + 30, color=GREEN, sw=2))

    bx(diamond_cy + d_h // 2 + 60, "Читати RTC-стан\n(лічильник, виміри, стан)", LGREEN, GREEN)
    frags.append(arrow(cx, diamond_cy + d_h // 2 + 88, cx, diamond_cy + d_h // 2 + 118, color=GREEN, sw=2))

    bx(diamond_cy + d_h // 2 + 148, "Доробити роботу\n(передати, якщо треба)", LGREEN, GREEN)
    frags.append(arrow(cx, diamond_cy + d_h // 2 + 175, cx, diamond_cy + d_h // 2 + 205, color=GREEN, sw=2))

    bx(diamond_cy + d_h // 2 + 230, "Оновити RTC-стан\n→ esp_deep_sleep_start()", LBLUE, NEG, True)

    # Замкнути цикл
    loop_x = cx + 180
    loop_y_bot = diamond_cy + d_h // 2 + 250
    loop_y_top = 38
    frags.append(line(loop_x, loop_y_bot - 12, loop_x, loop_y_top, color=GREEN, sw=1.8))
    frags.append(line(loop_x, loop_y_top, cx + 70, loop_y_top, color=GREEN, sw=1.8))
    frags.append(arrow(cx + 70, loop_y_top, cx + 70, 42, color=GREEN, sw=1.8))
    frags.append(text(loop_x + 8, (loop_y_top + loop_y_bot) // 2, "наступне\nпрокидання", size=10,
                      color=GREEN, anchor="start"))

    # Гілка «НІ» (холодний старт) — ліворуч
    frags.append(text(cx - d_w // 2 - 8, diamond_cy + 5, "НІ", size=12, color=POS, bold=True, anchor="end"))
    frags.append(arrow(cx - d_w // 2, diamond_cy, cx - d_w // 2 - 60, diamond_cy, color=POS, sw=2))
    bx_cold, _, _ = textbox(cx - d_w // 2 - 130, diamond_cy,
                             "Холодний старт:\nініт RTC-стану з нуля", size=12,
                             fill=LRED, stroke=POS, sw=2, color=POS, pad=8)
    frags.append(bx_cold)

    render(os.path.join(OUT, "fig-r13-9-2-wake-flow.svg"), W, H, *frags,
           title="Патерн пробудження: серія коротких реінкарнацій, зшитих RTC-пам'яттю")


# ═══════════════════════════════════════════════════════════════════════════════
# Головний запуск
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating figures for r13-low-power.md ...")
    fig_r13_1_1()
    print("  OK fig-r13-1-1-budget-formula")
    fig_r13_1_2()
    print("  OK fig-r13-1-2-pulse-vs-average")
    fig_r13_2_1()
    print("  OK fig-r13-2-1-current-map")
    fig_r13_2_2()
    print("  OK fig-r13-2-2-dynamic-vs-static")
    fig_r13_2_3()
    print("  OK fig-r13-2-3-orders-of-magnitude")
    fig_r13_3_1()
    print("  OK fig-r13-3-1-sleep-ladder")
    fig_r13_3_2()
    print("  OK fig-r13-3-2-sleep-compare")
    fig_r13_4_1()
    print("  OK fig-r13-4-1-wakeup-sources")
    fig_r13_4_2()
    print("  OK fig-r13-4-2-rtc-gpio-pins")
    fig_r13_5_1()
    print("  OK fig-r13-5-1-ulp-guard")
    fig_r13_5_2()
    print("  OK fig-r13-5-2-ulp-economics")
    fig_r13_6_1()
    print("  OK fig-r13-6-1-duty-cycle-profile")
    fig_r13_6_2()
    print("  OK fig-r13-6-2-two-levers")
    fig_r13_7_1()
    print("  OK fig-r13-7-1-why-multimeter-lies")
    fig_r13_7_2()
    print("  OK fig-r13-7-2-correct-measurement")
    fig_r13_8_1()
    print("  OK fig-r13-8-1-who-doesnt-sleep")
    fig_r13_8_2()
    print("  OK fig-r13-8-2-quiescent-budget")
    fig_r13_9_1()
    print("  OK fig-r13-9-1-what-survives-deepsleep")
    fig_r13_9_2()
    print("  OK fig-r13-9-2-wake-flow")
    print("Done. All figures written to", OUT)
