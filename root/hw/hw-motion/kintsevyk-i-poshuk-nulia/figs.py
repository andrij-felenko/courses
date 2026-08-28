# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Порівняння 4 типів кінцевиків ──────────────────────────────────────────
def fig_endstop_types():
    W, H = 840, 360
    p = []
    
    # 4 колонки
    cols = [
        ("Механічний (Microswitch)", 40, "#fef6e7", "#d97706", [
            "Пружинний важіль (snap-action)",
            "Прямий розрив контактів",
            "Ресурс: 10⁵–10⁶ спрацювань",
            "Є брязкіт контактів (1–3 мс)",
            "Повторюваність: ±10–50 мкм"
        ]),
        ("Оптичний (Photo-interrupter)", 235, "#eafaf0", FIELD, [
            "ІЧ-діод + фототранзистор",
            "Шторка перекриває промінь",
            "Нескінченний мех. ресурс",
            "Без брязкоту контактів",
            "Вразливий до пилу й бруду",
            "Повторюваність: ±2–10 мкм"
        ]),
        ("Індуктивний (Proximity)", 430, "#eaf0fd", NEG, [
            "ВЧ-генератор + котушка",
            "Вихрові струми у металі",
            "Герметичний (IP67/IP68)",
            "Живлення: 6–36 В (потрібен дільник)",
            "Повторюваність: ±1–5 мкм"
        ]),
        ("Sensorless (StallGuard)", 625, "#fdecea", POS, [
            "Вимірювання проти-ЕРС",
            "Детектування стрибка струму",
            "Нуль дротів до каретки",
            "Ударне навантаження на раму",
            "Повторюваність: ±50–200 мкм"
        ])
    ]
    
    col_w = 175
    for title, x, bg_col, border_col, items in cols:
        p.append(rect(x, 40, col_w, 290, fill=bg_col, stroke=border_col, sw=1.8, rx=8))
        p.append(fitbox(x + 5, 50, col_w - 10, 44, title, size=12, bold=True, color=border_col, fill="#ffffff", stroke=border_col, sw=1.2))
        
        y_text = 115
        for it in items:
            p.append(circle(x + 14, y_text + 4, 3, fill=border_col, stroke="none"))
            p.append(mtext(x + 24, y_text, it, size=10, color=INK, anchor="start", lh=1.2))
            y_text += 28 if len(it) > 24 else 22
            
    p.append(text(W / 2, 20, "Чотири фізичні принципи детектування граничного положення осі", size=13, color=INK, bold=True))
    
    render(os.path.join(OUT, "endstop-types.svg"), W, H, *p,
           title="Типи кінцевих вимикачів")


# ── 2. Схемотехніка NO проти NC (Fail-Safe) ────────────────────────────────────
def fig_circuit_no_nc():
    W, H = 800, 350
    p = []
    
    p.append(text(W / 2, 22, "Схемотехніка кінцевика: надійний NC (Fail-Safe) проти небезпечного NO", size=13, color=INK, bold=True))
    
    # Ліва половина: NC (Нормально замкнений)
    p.append(rect(30, 45, 355, 285, fill="#f4faf5", stroke=FIELD, sw=2, rx=8))
    p.append(text(207, 72, "Нормально замкнений (NC) — СТАНДАРТ", size=12, color=FIELD, bold=True))
    
    # Схема NC
    p.append(rect(50, 95, 315, 140, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(75, 120, "+3.3V", size=11, color=POS, bold=True))
    p.append(line(75, 128, 75, 145, color=POS, sw=1.5))
    p.append(rect(65, 145, 20, 35, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(75, 166, "R_pull", size=9, color=INK))
    p.append(text(100, 166, "1 кОм", size=9, color=MUTED))
    p.append(line(75, 180, 75, 205, color=LINE, sw=1.5))
    p.append(circle(75, 205, 3, fill=INK, stroke="none"))
    
    # Дріт до контакту
    p.append(line(75, 205, 140, 205, color=LINE, sw=1.5))
    p.append(circle(140, 205, 3, fill=INK, stroke=LINE))
    p.append(line(140, 205, 175, 205, color=FIELD, sw=2)) # замкнений контакт
    p.append(circle(175, 205, 3, fill=INK, stroke=LINE))
    p.append(line(175, 205, 195, 205, color=LINE, sw=1.5))
    p.append(line(195, 205, 195, 220, color=LINE, sw=1.5))
    p.append(line(185, 220, 205, 220, color=LINE, sw=2)) # GND
    p.append(text(195, 233, "GND", size=9, color=MUTED))
    p.append(text(157, 193, "NC контакт", size=9, color=FIELD, bold=True))
    
    # Фільтр і тригер Шмітта
    p.append(line(75, 205, 230, 205, color=LINE, sw=1.5))
    p.append(rect(230, 197, 25, 16, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(242, 209, "R_f", size=9, color=INK))
    p.append(line(255, 205, 280, 205, color=LINE, sw=1.5))
    p.append(circle(280, 205, 2.5, fill=INK, stroke="none"))
    p.append(line(280, 205, 280, 220, color=LINE, sw=1.2))
    p.append(line(273, 220, 287, 220, color=LINE, sw=1.5))
    p.append(line(273, 223, 287, 223, color=LINE, sw=1.5))
    p.append(line(280, 223, 280, 228, color=LINE, sw=1.2))
    p.append(text(300, 223, "C_f 100nF", size=9, color=MUTED))
    p.append(line(280, 205, 310, 205, color=LINE, sw=1.5))
    
    # Буфер тригера Шмітта
    p.append(rect(310, 192, 40, 26, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=3))
    p.append(text(330, 209, "MCU", size=9, color=NEG, bold=True))
    
    # Пояснення Fail-Safe
    p.append(rect(50, 245, 315, 70, fill="#ffffff", stroke=FIELD, sw=1, rx=5))
    p.append(text(207, 263, "ПРИ ОБРИВІ ДРОТУ:", size=10, color=FIELD, bold=True))
    p.append(text(207, 281, "Струм зникає → на вході MCU = HIGH (активно)", size=9, color=INK))
    p.append(text(207, 298, "Контролер бачить аварію і негайно зупиняє вісь", size=9, color=FIELD, bold=True))
    
    # Права половина: NO (Нормально розімкнений)
    p.append(rect(415, 45, 355, 285, fill="#fdf2f2", stroke=POS, sw=2, rx=8))
    p.append(text(592, 72, "Нормально розімкнений (NO) — НЕБЕЗПЕЧНО", size=12, color=POS, bold=True))
    
    # Схема NO
    p.append(rect(435, 95, 315, 140, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    p.append(text(460, 120, "+3.3V", size=11, color=POS, bold=True))
    p.append(line(460, 128, 460, 145, color=POS, sw=1.5))
    p.append(rect(450, 145, 20, 35, fill="#f4f6f8", stroke=LINE, sw=1.5))
    p.append(text(460, 166, "R_pull", size=9, color=INK))
    p.append(line(460, 180, 460, 205, color=LINE, sw=1.5))
    p.append(circle(460, 205, 3, fill=INK, stroke="none"))
    
    # Дріт до контакту
    p.append(line(460, 205, 525, 205, color=LINE, sw=1.5))
    p.append(circle(525, 205, 3, fill=INK, stroke=LINE))
    p.append(line(525, 205, 555, 192, color=POS, sw=2)) # розімкнений контакт
    p.append(circle(560, 205, 3, fill=INK, stroke=LINE))
    p.append(line(560, 205, 580, 205, color=LINE, sw=1.5))
    p.append(line(580, 205, 580, 220, color=LINE, sw=1.5))
    p.append(line(570, 220, 590, 220, color=LINE, sw=2))
    p.append(text(580, 233, "GND", size=9, color=MUTED))
    p.append(text(542, 182, "NO контакт", size=9, color=POS, bold=True))
    
    # Вхід MCU
    p.append(line(460, 205, 695, 205, color=LINE, sw=1.5))
    p.append(rect(695, 192, 40, 26, fill="#fdecea", stroke=POS, sw=1.5, rx=3))
    p.append(text(715, 209, "MCU", size=9, color=POS, bold=True))
    
    # Пояснення аварії NO
    p.append(rect(435, 245, 315, 70, fill="#ffffff", stroke=POS, sw=1, rx=5))
    p.append(text(592, 263, "ПРИ ОБРИВІ ДРОТУ:", size=10, color=POS, bold=True))
    p.append(text(592, 281, "На вході завжди HIGH (не спрацьовано)", size=9, color=INK))
    p.append(text(592, 298, "Каретка летить у край і трощить механіку!", size=9, color=POS, bold=True))
    
    render(os.path.join(OUT, "circuit-no-nc.svg"), W, H, *p,
           title="Схемотехніка кінцевика: NO проти NC")


# ── 3. Кінематика пошуку нуля (Homing Sequence) ───────────────────────────────
def fig_homing_sequence():
    W, H = 820, 380
    p = []
    
    p.append(text(W / 2, 22, "Двоетапний алгоритм пошуку нуля: кінематичний профіль v(t)", size=13, color=INK, bold=True))
    
    # Вісь часу t
    p.append(line(60, 280, 780, 280, color=LINE, sw=1.5))
    p.append(arrow(770, 280, 790, 280, color=LINE, sw=1.5))
    p.append(text(785, 298, "t, с", size=11, color=INK, bold=True))
    
    # Вісь швидкості v
    p.append(line(60, 280, 60, 50, color=LINE, sw=1.5))
    p.append(arrow(60, 60, 60, 40, color=LINE, sw=1.5))
    p.append(text(45, 45, "v", size=12, color=INK, bold=True))
    
    # Нульовий рівень швидкості
    p.append(line(55, 200, 780, 200, color=MUTED, sw=1, dash="4,4"))
    p.append(text(40, 204, "0", size=11, color=MUTED))
    
    # Графік швидкості
    # Фаза 1: Fast seek (v_fast = 60 мм/с)
    p.append(line(60, 200, 100, 90, color=POS, sw=2.5)) # розгін
    p.append(line(100, 90, 220, 90, color=POS, sw=2.5)) # рух
    p.append(text(160, 80, "v_fast (60 мм/с)", size=10, color=POS, bold=True))
    
    # Фаза 2: Спрацювання 1 та гальмування
    p.append(line(220, 90, 260, 200, color=POS, sw=2.5)) # гальмування
    p.append(circle(220, 90, 4, fill=POS, stroke="none"))
    p.append(text(220, 65, "Кінцевик спрацював!", size=9, color=POS, bold=True))
    p.append(line(220, 72, 220, 85, color=POS, sw=1))
    
    # Фаза 3: Retract (відкат назад на -15 мм/с)
    p.append(line(260, 200, 280, 200, color=LINE, sw=2.5)) # пауза
    p.append(line(280, 200, 310, 250, color=NEG, sw=2.5)) # розгін назад
    p.append(line(310, 250, 410, 250, color=NEG, sw=2.5)) # відкат 3 мм
    p.append(line(410, 250, 440, 200, color=NEG, sw=2.5)) # зупинка
    p.append(text(360, 268, "v_retract (−15 мм/с, відкат 3 мм)", size=10, color=NEG, bold=True))
    
    # Фаза 4: Slow approach (повільний доїзд на 2 мм/с)
    p.append(line(440, 200, 460, 200, color=LINE, sw=2.5)) # пауза
    p.append(line(460, 200, 480, 175, color=FIELD, sw=2.5)) # розгін
    p.append(line(480, 175, 620, 175, color=FIELD, sw=2.5)) # повільний доїзд
    p.append(text(550, 163, "v_slow (2 мм/с)", size=10, color=FIELD, bold=True))
    
    # Фаза 5: Точна фіксація нуля (Latch)
    p.append(circle(620, 175, 4, fill=FIELD, stroke="none"))
    p.append(line(620, 175, 630, 200, color=FIELD, sw=2.5))
    p.append(text(620, 140, "ТОЧНИЙ НУЛЬ!", size=10, color=FIELD, bold=True))
    p.append(text(620, 153, "Latch: X = 0.000", size=9, color=FIELD))
    p.append(line(620, 157, 620, 170, color=FIELD, sw=1))
    
    # Фаза 6: Паркувальний зазор
    p.append(line(630, 200, 650, 200, color=LINE, sw=2.5))
    p.append(line(650, 200, 670, 220, color=MUTED, sw=2))
    p.append(line(670, 220, 710, 220, color=MUTED, sw=2))
    p.append(line(710, 220, 730, 200, color=MUTED, sw=2))
    p.append(text(690, 238, "Паркування (1 мм)", size=9, color=MUTED))
    p.append(line(730, 200, 770, 200, color=LINE, sw=2.5))
    
    # Підписи фаз знизу
    phases = [
        (60, 260, "1. Швидкий пошук", POS),
        (260, 440, "2. Відкат (вихід із зони гістерезису)", NEG),
        (440, 630, "3. Прецизійний доїзд", FIELD),
        (630, 770, "4. Фіксація і паркування", MUTED)
    ]
    for x1, x2, label, col in phases:
        p.append(line(x1, 315, x2, 315, color=col, sw=2))
        p.append(line(x1, 310, x1, 320, color=col, sw=1.5))
        p.append(line(x2, 310, x2, 320, color=col, sw=1.5))
        p.append(text((x1 + x2) / 2, 335, label, size=10, color=col, bold=True))
        
    render(os.path.join(OUT, "homing-sequence.svg"), W, H, *p,
           title="Кінематичний профіль пошуку нуля")


# ── 4. Механічний гістерезис та розкид повторюваності ─────────────────────────
def fig_hysteresis_repeatability():
    W, H = 820, 360
    p = []
    
    p.append(text(W / 2, 22, "Механічний гістерезис датчика та вплив швидкості на повторюваність", size=13, color=INK, bold=True))
    
    # Ліва частина: петля гістерезису перемикача
    p.append(rect(30, 45, 365, 290, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(212, 70, "Механічний гістерезис перемикача", size=12, color=INK, bold=True))
    
    # Осі
    p.append(line(60, 260, 360, 260, color=LINE, sw=1.2)) # X
    p.append(arrow(350, 260, 370, 260, color=LINE, sw=1.2))
    p.append(text(365, 278, "X, мм", size=10, color=INK, bold=True))
    
    p.append(line(60, 260, 60, 95, color=LINE, sw=1.2)) # Сигнал
    p.append(arrow(60, 105, 60, 85, color=LINE, sw=1.2))
    p.append(text(45, 90, "Сигнал", size=10, color=INK, bold=True))
    p.append(text(45, 130, "HIGH", size=9, color=MUTED))
    p.append(text(45, 220, "LOW", size=9, color=MUTED))
    
    # Петля
    p.append(line(60, 130, 250, 130, color=POS, sw=2)) # рух уперед HIGH
    p.append(line(250, 130, 250, 220, color=POS, sw=2.5)) # перемикання вниз (Trip)
    p.append(circle(250, 130, 3.5, fill=POS, stroke="none"))
    p.append(circle(250, 220, 3.5, fill=POS, stroke="none"))
    p.append(line(250, 220, 340, 220, color=POS, sw=2))
    p.append(text(250, 115, "X_trip (спрацювання)", size=9, color=POS, bold=True))
    
    p.append(line(340, 220, 170, 220, color=NEG, sw=2, dash="4,3")) # рух назад LOW
    p.append(line(170, 220, 170, 130, color=NEG, sw=2.5)) # перемикання вгору (Release)
    p.append(circle(170, 220, 3.5, fill=NEG, stroke="none"))
    p.append(circle(170, 130, 3.5, fill=NEG, stroke="none"))
    p.append(line(170, 130, 60, 130, color=NEG, sw=2, dash="4,3"))
    p.append(text(170, 240, "X_release (відпускання)", size=9, color=NEG, bold=True))
    
    # Стрілка гістерезису
    p.append(line(170, 175, 250, 175, color=FIELD, sw=2))
    p.append(arrow(200, 175, 250, 175, color=FIELD, sw=1.5))
    p.append(arrow(220, 175, 170, 175, color=FIELD, sw=1.5))
    p.append(text(210, 165, "Гістерезис ΔX = 0.2 мм", size=9, color=FIELD, bold=True))
    p.append(text(212, 305, "Фіксувати нуль можна ТІЛЬКИ на одному напрямку руху!", size=9, color=POS, bold=True))
    
    # Права частина: розподіл повторюваності від швидкості
    p.append(rect(420, 45, 370, 290, fill="#fdfefe", stroke=LINE, sw=1.5, rx=8))
    p.append(text(605, 70, "Похибка фіксації точки від швидкості доїзду", size=12, color=INK, bold=True))
    
    # Осі
    p.append(line(450, 260, 760, 260, color=LINE, sw=1.2))
    p.append(arrow(750, 260, 770, 260, color=LINE, sw=1.2))
    p.append(text(765, 278, "X, мм", size=10, color=INK, bold=True))
    
    # Гаусіана швидка (v = 50 мм/с): низький широкий пагорб
    pts_fast = "460,260 500,250 540,220 570,160 600,160 630,220 670,250 710,260"
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="4,3"/>' % (pts_fast, POS))
    p.append(text(500, 135, "v = 50 мм/с: розкид ±80 мкм", size=10, color=POS, bold=True))
    p.append(text(500, 150, "(через затримку опитування 1.5 мс)", size=9, color=MUTED))
    
    # Гаусіана повільна (v = 2 мм/с): високий вузький пік
    pts_slow = "560,260 575,250 585,180 590,105 595,105 600,180 610,250 625,260"
    p.append('<polyline points="%s" fill="#eafaf0" stroke="%s" stroke-width="2.5"/>' % (pts_slow, FIELD))
    p.append(text(592, 85, "v = 2 мм/с: розкид ±2 мкм!", size=10, color=FIELD, bold=True))
    
    # Точний нуль
    p.append(line(592, 95, 592, 265, color=FIELD, sw=1.2, dash="2,2"))
    p.append(text(592, 278, "X₀", size=10, color=FIELD, bold=True))
    
    p.append(text(605, 305, "Повільний доїзд стискає похибку реакції в 25–50 разів", size=9, color=FIELD, bold=True))
    
    render(os.path.join(OUT, "hysteresis-repeatability.svg"), W, H, *p,
           title="Гістерезис та повторюваність кінцевика")


# ── 5. Кінцевий автомат пошуку нуля (Homing FSM) ───────────────────────────────
def fig_homing_fsm():
    W, H = 840, 420
    p = []
    
    p.append(text(W / 2, 22, "Граф станів кінцевого автомата пошуку нуля (Homing FSM)", size=13, color=INK, bold=True))
    
    # Стани
    states = [
        ("HOMING_IDLE", 90, 80, "#f4f6f8", LINE),
        ("HOMING_FAST_SEEK", 280, 80, "#fdecea", POS),
        ("HOMING_DECEL", 480, 80, "#fdecea", POS),
        ("HOMING_RETRACT", 680, 80, "#eaf0fd", NEG),
        ("HOMING_SLOW_APPROACH", 680, 240, "#eafaf0", FIELD),
        ("HOMING_LATCH", 480, 240, "#eafaf0", FIELD),
        ("HOMING_PARK", 280, 240, "#eafaf0", FIELD),
        ("HOMING_DONE", 90, 240, "#eafaf0", FIELD),
        ("HOMING_FAULT", 380, 360, "#fdf2f2", POS)
    ]
    
    box_w, box_h = 140, 48
    for name, cx, cy, fill_c, strk_c in states:
        p.append(rect(cx - box_w / 2, cy - box_h / 2, box_w, box_h, fill=fill_c, stroke=strk_c, sw=1.8, rx=6))
        p.append(fitbox(cx - box_w / 2 + 4, cy - box_h / 2 + 4, box_w - 8, box_h - 8, name, size=10, bold=True, color=strk_c, fill="none", stroke="none"))
        
    # Стрілки переходів
    # IDLE -> FAST_SEEK
    p.append(arrow(160, 80, 210, 80, color=INK, sw=1.8))
    p.append(text(185, 70, "Start", size=9, color=INK))
    
    # FAST_SEEK -> DECEL
    p.append(arrow(350, 80, 410, 80, color=POS, sw=1.8))
    p.append(text(380, 70, "Hit endstop", size=9, color=POS, bold=True))
    
    # DECEL -> RETRACT
    p.append(arrow(550, 80, 610, 80, color=INK, sw=1.8))
    p.append(text(580, 70, "v == 0", size=9, color=INK))
    
    # RETRACT -> SLOW_APPROACH
    p.append(arrow(680, 104, 680, 216, color=NEG, sw=1.8))
    p.append(text(750, 160, "Retract done\n(endstop open)", size=9, color=NEG, bold=True))
    
    # SLOW_APPROACH -> LATCH
    p.append(arrow(610, 240, 550, 240, color=FIELD, sw=1.8))
    p.append(text(580, 230, "Hit endstop", size=9, color=FIELD, bold=True))
    
    # LATCH -> PARK
    p.append(arrow(410, 240, 350, 240, color=FIELD, sw=1.8))
    p.append(text(380, 230, "Pos = 0.000", size=9, color=FIELD, bold=True))
    
    # PARK -> DONE
    p.append(arrow(210, 240, 160, 240, color=FIELD, sw=1.8))
    p.append(text(185, 230, "Parked", size=9, color=FIELD))
    
    # DONE -> IDLE
    p.append(arrow(90, 216, 90, 104, color=FIELD, sw=1.8))
    p.append(text(50, 160, "Ready", size=9, color=FIELD))
    
    # Переходи у FAULT (Timeout / Max travel)
    p.append(arrow(280, 104, 340, 336, color=POS, sw=1.5))
    p.append(arrow(680, 264, 440, 345, color=POS, sw=1.5))
    p.append(text(460, 315, "Timeout / Over-travel / Sensor stuck", size=9, color=POS, bold=True))
    
    render(os.path.join(OUT, "homing-fsm.svg"), W, H, *p,
           title="Кінцевий автомат пошуку нуля")


def main():
    fig_endstop_types()
    fig_circuit_no_nc()
    fig_homing_sequence()
    fig_hysteresis_repeatability()
    fig_homing_fsm()
    print("All 5 figures generated successfully.")


if __name__ == "__main__":
    main()
