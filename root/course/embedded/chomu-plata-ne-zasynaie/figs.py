# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_crowbar():
    W, H = 780, 420
    p = []

    # Тло
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 34, "Наскрізний струм (crowbar leakage) у вхідному КМОН-буфері", size=14, bold=True, color=INK))

    # ── Лівий блок: Нормальні цифрові рівні ──
    bx1, by1, bw1, bh1 = 30, 60, 210, 330
    p.append(rect(bx1, by1, bw1, bh1, fill="#f8fafc", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(bx1 + bw1 / 2, by1 + 22, "Визначений рівень", size=12, bold=True, color=FIELD))
    p.append(text(bx1 + bw1 / 2, by1 + 40, "Vin = 0 В або Vin = 3.3 В", size=10, color=MUTED))

    # Стан 0V
    p.append(rect(bx1 + 15, by1 + 60, bw1 - 30, 110, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(bx1 + bw1 / 2, by1 + 80, "Вхід LOW (0 В)", size=11, bold=True, color=INK))
    p.append(text(bx1 + bw1 / 2, by1 + 100, "PMOS: ВВІМКНЕНО (провідний)", size=10, color=FIELD))
    p.append(text(bx1 + bw1 / 2, by1 + 118, "NMOS: ВИМКНЕНО (закритий)", size=10, color=MUTED))
    p.append(text(bx1 + bw1 / 2, by1 + 145, "Витік: < 1 нА (ізоляція)", size=11, bold=True, color=FIELD))

    # Стан 3.3V
    p.append(rect(bx1 + 15, by1 + 185, bw1 - 30, 110, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(bx1 + bw1 / 2, by1 + 205, "Вхід HIGH (3.3 В)", size=11, bold=True, color=INK))
    p.append(text(bx1 + bw1 / 2, by1 + 225, "PMOS: ВИМКНЕНО (закритий)", size=10, color=MUTED))
    p.append(text(bx1 + bw1 / 2, by1 + 243, "NMOS: ВВІМКНЕНО (провідний)", size=10, color=FIELD))
    p.append(text(bx1 + bw1 / 2, by1 + 270, "Витік: < 1 нА (ізоляція)", size=11, bold=True, color=FIELD))

    p.append(text(bx1 + bw1 / 2, by1 + 315, "Один із ключів завжди закритий", size=10, color=MUTED, italic=True))

    # ── Середній блок: Плаваючий вхід (Аварія споживання) ──
    bx2, by2, bw2, bh2 = 260, 60, 270, 330
    p.append(rect(bx2, by2, bw2, bh2, fill="#fdf2f2", stroke=POS, sw=2, rx=6))
    p.append(text(bx2 + bw2 / 2, by2 + 22, "Плаваюча ніжка (Floating)", size=13, bold=True, color=POS))
    p.append(text(bx2 + bw2 / 2, by2 + 40, "Vin зависає на рівні ~1.65 В", size=10, color=POS))

    # Схема інвертора
    cx = bx2 + bw2 / 2
    # VDD шина
    p.append(line(cx - 50, by2 + 65, cx + 50, by2 + 65, color=POS, sw=2))
    p.append(text(cx, by2 + 58, "VDD = 3.3 В", size=11, bold=True, color=POS))

    # PMOS транзистор (верхній)
    py_pmos = by2 + 105
    p.append(rect(cx - 24, py_pmos - 16, 48, 32, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(cx, py_pmos + 4, "PMOS (ON)", size=10, bold=True, color=POS))
    p.append(line(cx, by2 + 65, cx, py_pmos - 16, color=POS, sw=1.8))

    # Вхідний пін
    p.append(line(bx2 + 20, by2 + 155, cx - 35, by2 + 155, color=POS, sw=1.5, dash="4,3"))
    p.append(circle(bx2 + 20, by2 + 155, 4, fill="#ffffff", stroke=POS, sw=2))
    p.append(text(bx2 + 30, by2 + 145, "Vin ~ 1.65 В", size=10, bold=True, color=POS, anchor="start"))
    p.append(text(bx2 + 30, by2 + 170, "(наводки)", size=9, color=MUTED, anchor="start"))

    # З'єднання затворів
    p.append(line(cx - 35, py_pmos, cx - 24, py_pmos, color=POS, sw=1.5))
    p.append(line(cx - 35, by2 + 205, cx - 24, by2 + 205, color=POS, sw=1.5))
    p.append(line(cx - 35, py_pmos, cx - 35, by2 + 205, color=POS, sw=1.5))

    # З'єднання між транзисторами (вихід)
    p.append(line(cx, py_pmos + 16, cx, by2 + 189, color=POS, sw=2))

    # NMOS транзистор (нижній)
    py_nmos = by2 + 205
    p.append(rect(cx - 24, py_nmos - 16, 48, 32, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(cx, py_nmos + 4, "NMOS (ON)", size=10, bold=True, color=POS))

    # GND шина
    p.append(line(cx, py_nmos + 16, cx, by2 + 255, color=POS, sw=1.8))
    p.append(line(cx - 40, by2 + 255, cx + 40, by2 + 255, color=INK, sw=2))
    p.append(line(cx - 25, by2 + 260, cx + 25, by2 + 260, color=INK, sw=1.5))
    p.append(line(cx - 10, by2 + 265, cx + 10, by2 + 265, color=INK, sw=1.2))
    p.append(text(cx, by2 + 278, "GND (0 В)", size=10, color=MUTED))

    # Наскрізна червона стрілка струму
    p.append(line(cx + 45, by2 + 80, cx + 45, by2 + 242, color=POS, sw=2.5, dash="5,3"))
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s"/>'
             % (cx + 45, by2 + 252, cx + 40, by2 + 242, cx + 50, by2 + 242, POS, POS))
    p.append(text(cx + 55, by2 + 150, "I_витік", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(cx + 55, by2 + 168, "100–400 мкА", size=11, bold=True, color=POS, anchor="start"))
    p.append(text(cx + 55, by2 + 184, "на кожен пін!", size=9, color=POS, anchor="start"))

    p.append(rect(bx2 + 12, by2 + 292, bw2 - 24, 30, fill="#fdecea", stroke=POS, sw=1, rx=4))
    p.append(text(cx, by2 + 312, "Обидва транзистори прочинені!", size=10, bold=True, color=POS))

    # ── Правий блок: Рішення — Analog Mode ──
    bx3, by3, bw3, bh3 = 550, 60, 200, 330
    p.append(rect(bx3, by3, bw3, bh3, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(bx3 + bw3 / 2, by3 + 22, "Analog Mode (Hi-Z)", size=12, bold=True, color=FIELD))
    p.append(text(bx3 + bw3 / 2, by3 + 40, "Правильна конфігурація", size=10, color=FIELD))

    # Блок ізоляції
    p.append(rect(bx3 + 15, by3 + 65, bw3 - 30, 90, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(bx3 + bw3 / 2, by3 + 85, "Вхідний буфер", size=11, bold=True, color=INK))
    p.append(text(bx3 + bw3 / 2, by3 + 105, "ВІДРІЗАНО ВІД ПІНА", size=10, bold=True, color=FIELD))
    p.append(text(bx3 + bw3 / 2, by3 + 125, "ключем комутації", size=10, color=MUTED))
    p.append(text(bx3 + bw3 / 2, by3 + 143, "тригер Шмітта вимкнено", size=9, color=MUTED, italic=True))

    p.append(rect(bx3 + 15, by3 + 170, bw3 - 30, 80, fill="#ffffff", stroke=FIELD, sw=1, rx=4))
    p.append(text(bx3 + bw3 / 2, by3 + 190, "Результат у сні:", size=11, bold=True, color=INK))
    p.append(text(bx3 + bw3 / 2, by3 + 212, "Наскрізний струм = 0", size=11, bold=True, color=FIELD))
    p.append(text(bx3 + bw3 / 2, by3 + 232, "Витік: < 0.1 нА", size=10, color=FIELD))

    p.append(rect(bx3 + 10, by3 + 265, bw3 - 20, 55, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    p.append(text(bx3 + bw3 / 2, by3 + 285, "Всі невживані ніжки", size=10, bold=True, color=FIELD))
    p.append(text(bx3 + bw3 / 2, by3 + 303, "→ в режим Analog!", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "crowbar-leakage.svg"), W, H, *p,
           title="Наскрізний струм пари КМОН-інвертора при плаваючому вході")


def fig_phantom():
    W, H = 780, 400
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 34, "Паразитне живлення (Phantom Powering) через ESD-діод датчика", size=14, bold=True, color=INK))

    # ── Лівий блок: МК у сні ──
    mx, my, mw, mh = 30, 60, 210, 220
    p.append(rect(mx, my, mw, mh, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=6))
    p.append(text(mx + mw / 2, my + 24, "Мікроконтролер", size=13, bold=True, color=INK))
    p.append(text(mx + mw / 2, my + 42, "Живлення VDD = 3.3 В (ON)", size=10, color=MUTED))

    p.append(rect(mx + 15, my + 65, mw - 30, 135, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(mx + mw / 2, my + 85, "Помилка конфігурації:", size=11, bold=True, color=POS))
    p.append(text(mx + mw / 2, my + 105, "GPIO TX / MOSI / SDA", size=11, bold=True, color=INK))
    p.append(text(mx + mw / 2, my + 125, "залишено в стані HIGH", size=10, color=POS))
    p.append(rect(mx + 25, my + 140, mw - 50, 28, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(mx + mw / 2, my + 158, "V_pin = 3.3 В", size=11, bold=True, color=POS))
    p.append(text(mx + mw / 2, my + 186, "активний пуш-пул вихід", size=9, color=MUTED, italic=True))

    # Вивідний пін МК
    pin_y = my + 154
    p.append(circle(mx + mw, pin_y, 5, fill=POS, stroke=POS, sw=1.5))

    # ── Лінія зв'язку з паразитною стрілкою струму ──
    sx = 490
    p.append(line(mx + mw, pin_y, sx, pin_y, color=POS, sw=2.5))
    # Стрілка струму
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s"/>'
             % (360, pin_y, 345, pin_y - 5, 345, pin_y + 5, POS, POS))
    p.append(text(350, pin_y - 12, "Паразитний струм: 0.5–4 мА", size=11, bold=True, color=POS))
    p.append(text(350, pin_y + 20, "Сигнальна лінія живить мікросхему", size=9, color=POS, italic=True))

    # ── Правий блок: Вимкнений датчик ──
    sy, sw, sh = 60, 260, 220
    p.append(rect(sx, sy, sw, sh, fill="#fdf2f2", stroke=POS, sw=2, rx=6))
    p.append(text(sx + sw / 2, sy + 24, "Датчик / Периферія", size=13, bold=True, color=POS))

    # Ключ живлення вимкнено
    p.append(rect(sx + 15, sy + 38, sw - 30, 28, fill="#ffffff", stroke=MUTED, sw=1, rx=4))
    p.append(text(sx + sw / 2, sy + 56, "Силове живлення: 0 В (ВИМКНЕНО)", size=10, bold=True, color=MUTED))

    # Внутрішня шина живлення датчика
    rail_y = sy + 95
    p.append(line(sx + 30, rail_y, sx + sw - 30, rail_y, color=POS, sw=2))
    p.append(text(sx + sw / 2 + 25, rail_y - 8, "Внутрішня шина VDD ~ 2.7 В!", size=10, bold=True, color=POS))

    # Вхідний пін датчика
    p.append(circle(sx, pin_y, 5, fill=POS, stroke=POS, sw=1.5))

    # ESD діод від піна до шини живлення
    dx = sx + 45
    p.append(line(sx, pin_y, dx, pin_y, color=POS, sw=2))
    p.append(line(dx, pin_y, dx, rail_y + 14, color=POS, sw=2))
    # Діодний трикутник
    p.append('<path d="M%.1f %.1f L%.1f %.1f L%.1f %.1f Z" fill="%s" stroke="%s" stroke-width="1.5"/>'
             % (dx, rail_y, dx - 8, rail_y + 14, dx + 8, rail_y + 14, "#fdecea", POS))
    p.append(line(dx - 10, rail_y, dx + 10, rail_y, color=POS, sw=2))  # катод
    p.append(text(dx + 18, rail_y + 16, "ESD-діод", size=9, bold=True, color=POS, anchor="start"))
    p.append(text(dx + 18, rail_y + 28, "VF ~ 0.6 В (ON)", size=9, color=POS, anchor="start"))

    # Навантаження всередині датчика
    core_x = sx + 140
    p.append(rect(core_x, rail_y + 15, 95, 75, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(core_x + 47, rail_y + 35, "Логіка датчика", size=10, bold=True, color=INK))
    p.append(text(core_x + 47, rail_y + 52, "Brownout стан", size=9, color=POS))
    p.append(text(core_x + 47, rail_y + 68, "Споживає струм!", size=9, bold=True, color=POS))
    p.append(line(core_x + 47, rail_y, core_x + 47, rail_y + 15, color=POS, sw=1.5))

    # Земля датчика
    p.append(line(core_x + 47, rail_y + 90, core_x + 47, sy + sh - 20, color=INK, sw=1.5))
    p.append(line(core_x + 32, sy + sh - 20, core_x + 62, sy + sh - 20, color=INK, sw=1.5))
    p.append(line(core_x + 37, sy + sh - 16, core_x + 57, sy + sh - 16, color=INK, sw=1.2))
    p.append(line(core_x + 42, sy + sh - 12, core_x + 52, sy + sh - 12, color=INK, sw=1))

    # ── Нижній блок: Правильне лікування ──
    p.append(rect(30, 295, W - 60, 85, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(W / 2, 318, "Правильне рішення: повна ізоляція цифрових ліній перед вимкненням живлення", size=12, bold=True, color=FIELD))
    p.append(text(W / 2, 338, "1. Перевести GPIO МК у стан LOW (0 В) або Hi-Z / Analog перед відкриттям силового ключа", size=10, color=INK))
    p.append(text(W / 2, 356, "2. Для двонапрямних шин (I2C) використовувати Level Shifter з ізоляцією при знеструмленні (Ioff)", size=10, color=INK))
    p.append(text(W / 2, 372, "Результат: V_pin = 0 В → ESD-діод закритий → паразитний струм дорівнює 0 мкА", size=10, bold=True, color=FIELD))

    render(os.path.join(OUT, "phantom-powering.svg"), W, H, *p,
           title="Паразитне живлення вимкненої периферії через ESD-діоди")


def fig_debugger():
    W, H = 800, 400
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke=LINE, sw=1, rx=8))
    p.append(text(W / 2, 34, "Вплив налагоджувача: блокування вимкнення тактових генераторів у сні", size=14, bold=True, color=INK))

    # ── Лівий варіант: Підключено налагоджувач (Пастка розробника) ──
    b1_x, b1_y, b1_w, b1_h = 30, 60, 355, 320
    p.append(rect(b1_x, b1_y, b1_w, b1_h, fill="#fdf2f2", stroke=POS, sw=1.8, rx=6))
    p.append(text(b1_x + b1_w / 2, b1_y + 24, "Налагоджувач ПІДКЛЮЧЕНО (SWD / JTAG)", size=12, bold=True, color=POS))

    # Налагоджувач зонд
    p.append(rect(b1_x + 15, b1_y + 45, 90, 85, fill="#ffffff", stroke=POS, sw=1.2, rx=4))
    p.append(text(b1_x + 60, b1_y + 68, "ST-Link /", size=10, bold=True, color=INK))
    p.append(text(b1_x + 60, b1_y + 83, "J-Link", size=10, bold=True, color=INK))
    p.append(text(b1_x + 60, b1_y + 102, "SWD активний", size=9, color=POS))
    p.append(text(b1_x + 60, b1_y + 118, "C_DEBUGEN=1", size=9, color=MUTED))

    # Лінії SWD
    p.append(line(b1_x + 105, b1_y + 75, b1_x + 140, b1_y + 75, color=POS, sw=1.5))
    p.append(line(b1_x + 105, b1_y + 95, b1_x + 140, b1_y + 95, color=POS, sw=1.5))
    p.append(text(b1_x + 122, b1_y + 70, "SWCLK", size=9, color=POS))
    p.append(text(b1_x + 122, b1_y + 108, "SWDIO", size=9, color=POS))

    # МК блок
    p.append(rect(b1_x + 140, b1_y + 45, 200, 160, fill="#ffffff", stroke=POS, sw=1.5, rx=4))
    p.append(text(b1_x + 240, b1_y + 65, "Мікроконтролер (Сон)", size=11, bold=True, color=INK))

    p.append(rect(b1_x + 150, b1_y + 75, 180, 42, fill="#fdecea", stroke=POS, sw=1, rx=3))
    p.append(text(b1_x + 240, b1_y + 92, "Ядро: виконало WFI()", size=10, bold=True, color=INK))
    p.append(text(b1_x + 240, b1_y + 108, "CPU Core зупинено", size=9, color=MUTED))

    p.append(rect(b1_x + 150, b1_y + 124, 180, 72, fill="#fdecea", stroke=POS, sw=1, rx=3))
    p.append(text(b1_x + 240, b1_y + 142, "Debug Unit (CoreSight)", size=10, bold=True, color=POS))
    p.append(text(b1_x + 240, b1_y + 158, "DBGMCU_CR тримає такти!", size=9, bold=True, color=POS))
    p.append(text(b1_x + 240, b1_y + 173, "FCLK, HCLK, APB активні", size=9, color=POS))
    p.append(text(b1_x + 240, b1_y + 188, "Внутрішній LDO активний", size=9, color=MUTED))

    # Струм лічильника
    p.append(rect(b1_x + 40, b1_y + 220, b1_w - 80, 80, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(text(b1_x + b1_w / 2, b1_y + 245, "Виміряний струм спокою:", size=11, color=INK))
    p.append(text(b1_x + b1_w / 2, b1_y + 272, "5.0 – 9.5 мА", size=18, bold=True, color=POS))
    p.append(text(b1_x + b1_w / 2, b1_y + 292, "Плата не засинає через активний блок налагодження!", size=9, color=POS, italic=True))

    # ── Правий варіант: Чистий автономний виріб ──
    b2_x, b2_y, b2_w, b2_h = 415, 60, 355, 320
    p.append(rect(b2_x, b2_y, b2_w, b2_h, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=6))
    p.append(text(b2_x + b2_w / 2, b2_y + 24, "Чистий автономний пристрій (Isolated)", size=12, bold=True, color=FIELD))

    # Налагоджувач від'єднано
    p.append(rect(b2_x + 15, b2_y + 45, 90, 85, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(b2_x + 60, b2_y + 75, "Налагоджувач", size=10, bold=True, color=MUTED))
    p.append(text(b2_x + 60, b2_y + 95, "ВІД'ЄДНАНО", size=10, bold=True, color=FIELD))
    p.append(text(b2_x + 60, b2_y + 115, "фізично", size=9, color=MUTED, italic=True))

    # МК блок
    p.append(rect(b2_x + 130, b2_y + 45, 210, 160, fill="#ffffff", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(b2_x + 235, b2_y + 65, "Мікроконтролер (Справжній сон)", size=11, bold=True, color=INK))

    p.append(rect(b2_x + 140, b2_y + 75, 190, 42, fill="#eafaf1", stroke=FIELD, sw=1, rx=3))
    p.append(text(b2_x + 235, b2_y + 92, "Ядро: WFI() / Deep-Sleep", size=10, bold=True, color=FIELD))
    p.append(text(b2_x + 235, b2_y + 108, "Тактові дерева вимкнено", size=9, color=MUTED))

    p.append(rect(b2_x + 140, b2_y + 124, 190, 72, fill="#eafaf1", stroke=FIELD, sw=1, rx=3))
    p.append(text(b2_x + 235, b2_y + 142, "Debug Unit вимкнено", size=10, bold=True, color=FIELD))
    p.append(text(b2_x + 235, b2_y + 158, "DBGMCU->CR = 0", size=9, bold=True, color=FIELD))
    p.append(text(b2_x + 235, b2_y + 173, "PLL, HSI, HSE зупинено", size=9, color=FIELD))
    p.append(text(b2_x + 235, b2_y + 188, "Тільки RTC (LSE 32 кГц) активний", size=9, color=MUTED))

    # Струм лічильника
    p.append(rect(b2_x + 40, b2_y + 220, b2_w - 80, 80, fill="#eafaf1", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(b2_x + b2_w / 2, b2_y + 245, "Виміряний струм спокою:", size=11, color=INK))
    p.append(text(b2_x + b2_w / 2, b2_y + 272, "1.8 – 3.2 мкА", size=18, bold=True, color=FIELD))
    p.append(text(b2_x + b2_w / 2, b2_y + 292, "Справжнє мікроамперне енергоспоживання!", size=9, color=FIELD, italic=True))

    render(os.path.join(OUT, "debugger-clock-trap.svg"), W, H, *p,
           title="Вплив підключеного налагоджувача на тактові генератори в сні")


if __name__ == "__main__":
    fig_crowbar()
    fig_phantom()
    fig_debugger()
    print("OK: figures generated in", OUT)
