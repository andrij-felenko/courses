# -*- coding: utf-8 -*-
"""Фігури для статті vid-natyskannia-do-podii («Від натискання до події»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. contact-bounce-waveform: ідеальний сигнал проти реального брязкоту ───
def fig_contact_bounce():
    W, H = 780, 370
    ox, oy1 = 80, 110
    oy2 = 250
    aw = 580
    p = []

    # Верхній графік: ідеальний сигнал
    p.append(arrow(ox, oy1, ox + aw, oy1, color=INK, sw=1.6))
    p.append(arrow(ox, oy1, ox, oy1 - 70, color=INK, sw=1.6))
    p.append(text(ox + aw - 10, oy1 + 22, "час t", size=12, color=INK, italic=True))
    p.append(text(ox - 12, oy1 - 55, "U (В)", size=12, color=INK, bold=True, italic=True, anchor="end"))
    p.append(text(ox + 10, oy1 - 75, "Ідеальна модель: миттєвий спад напруги", size=13, color=FIELD, bold=True, anchor="start"))

    # Рівні 3.3 В та 0 В
    p.append(line(ox, oy1 - 50, ox + aw, oy1 - 50, color=MUTED, sw=1.0, dash="4 4"))
    p.append(text(ox - 8, oy1 - 46, "3.3 В", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 8, oy1 + 14, "0 В", size=11, color=MUTED, anchor="end"))

    # Ідеальна крива: спад на 180 px
    p.append(line(ox, oy1 - 50, ox + 180, oy1 - 50, color=FIELD, sw=2.5))
    p.append(line(ox + 180, oy1 - 50, ox + 180, oy1, color=FIELD, sw=2.5))
    p.append(line(ox + 180, oy1, ox + aw - 20, oy1, color=FIELD, sw=2.5))

    b1, _, _ = textbox(ox + 380, oy1 - 35, "Один чистий спадний фронт → 1 переривання", size=11, color=FIELD, fill="#eafaf0", stroke=FIELD)
    p.append(b1)

    # Нижній графік: реальний брязкіт контактів
    p.append(arrow(ox, oy2, ox + aw, oy2, color=INK, sw=1.6))
    p.append(arrow(ox, oy2, ox, oy2 - 70, color=INK, sw=1.6))
    p.append(text(ox + aw - 10, oy2 + 22, "час t", size=12, color=INK, italic=True))
    p.append(text(ox - 12, oy2 - 55, "U (В)", size=12, color=INK, bold=True, italic=True, anchor="end"))
    p.append(text(ox + 10, oy2 - 75, "Реальний сигнал: пружний відскік контактів (10 мкс — 10 мс)", size=13, color=POS, bold=True, anchor="start"))

    p.append(line(ox, oy2 - 50, ox + aw, oy2 - 50, color=MUTED, sw=1.0, dash="4 4"))
    p.append(text(ox - 8, oy2 - 46, "3.3 В", size=11, color=MUTED, anchor="end"))
    p.append(text(ox - 8, oy2 + 14, "0 В", size=11, color=MUTED, anchor="end"))

    # Поріг спрацювання логіки
    p.append(line(ox, oy2 - 25, ox + aw, oy2 - 25, color="#d35400", sw=1.2, dash="3 3"))
    p.append(text(ox + aw + 5, oy2 - 22, "V_th (поріг логіки)", size=10, color="#d35400", anchor="start"))

    # Реальна ламана лінія брязкоту
    pts = [
        (ox, oy2 - 50),
        (ox + 180, oy2 - 50),
        (ox + 182, oy2),
        (ox + 192, oy2),
        (ox + 194, oy2 - 48),
        (ox + 204, oy2 - 48),
        (ox + 207, oy2 - 5),
        (ox + 218, oy2 - 5),
        (ox + 221, oy2 - 45),
        (ox + 228, oy2 - 45),
        (ox + 231, oy2),
        (ox + 242, oy2),
        (ox + 245, oy2 - 35),
        (ox + 252, oy2 - 35),
        (ox + 255, oy2),
        (ox + 268, oy2),
        (ox + 270, oy2 - 20),
        (ox + 276, oy2 - 20),
        (ox + 280, oy2),
        (ox + aw - 20, oy2)
    ]
    poly_str = " ".join("%.1f,%.1f" % pt for pt in pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-linejoin="round"/>' % (poly_str, POS))

    # Зона брязкоту (фонова рамка)
    p.append(rect(ox + 180, oy2 - 62, 110, 68, fill="#fdecea", stroke=POS, sw=1.0, rx=4))
    p.append(text(ox + 235, oy2 + 35, "Зона брязкоту", size=11, color=POS, bold=True))
    p.append(text(ox + 235, oy2 + 49, "t_bounce ≈ 1..10 мс", size=10, color=MUTED))

    # Позначення шквалу переривань EXTI
    for tr_x in [182, 194, 207, 221, 231, 245, 255, 270, 280]:
        p.append(arrow(ox + tr_x, oy2 - 65, ox + tr_x, oy2 - 52, color=POS, sw=1.2))

    b2, _, _ = textbox(ox + 460, oy2 - 35, "Шквал хибних переривань EXTI:\nпереповнення черги, збій лічильників", size=11, color=POS, fill="#fff5f5", stroke=POS)
    p.append(b2)

    render(os.path.join(OUT, "contact-bounce-waveform.svg"), W, H, *p,
           title="Осцилограма перехідного процесу механічного контакту")


# ── 2. rc-schmitt-circuit: RC-ланка, діод та тригер Шмітта ─────────────────
def fig_rc_schmitt_circuit():
    W, H = 820, 360
    p = []

    # Ліва половина: принципова схема
    p.append(text(210, 50, "Апаратне придушення: RC-фільтр + тригер Шмітта", size=13, color=INK, bold=True))

    # Живлення VDD
    p.append(line(70, 75, 70, 90, color=POS, sw=2.0))
    p.append(line(55, 75, 85, 75, color=POS, sw=2.0))
    p.append(text(70, 68, "+3.3 В (VDD)", size=11, color=POS, bold=True))

    # Резистор R_pullup (10k)
    p.append(rect(60, 90, 20, 45, fill=FILL, stroke=LINE, sw=1.5, rx=2))
    p.append(text(48, 115, "R1", size=11, color=INK, bold=True, anchor="end"))
    p.append(text(48, 128, "10 кОм", size=10, color=MUTED, anchor="end"))

    # Вузол після R1
    p.append(line(70, 135, 70, 170, color=LINE, sw=1.8))
    p.append(circle(70, 170, 3.5, fill=INK, stroke=INK, sw=1.0))

    # Кнопка до GND
    p.append(line(70, 170, 70, 200, color=LINE, sw=1.8))
    # Контакти кнопки
    p.append(circle(70, 205, 3, fill=BG, stroke=LINE, sw=1.5))
    p.append(circle(70, 235, 3, fill=BG, stroke=LINE, sw=1.5))
    p.append(line(60, 210, 80, 225, color=POS, sw=2.0))  # важіль кнопки
    p.append(text(42, 222, "Кнопка", size=11, color=INK, bold=True, anchor="end"))
    p.append(line(70, 238, 70, 260, color=LINE, sw=1.8))
    # GND
    p.append(line(55, 260, 85, 260, color=LINE, sw=2.0))
    p.append(line(62, 265, 78, 265, color=LINE, sw=1.8))
    p.append(line(67, 270, 73, 270, color=LINE, sw=1.5))

    # Відвід до RC-фільтра
    p.append(line(70, 170, 120, 170, color=LINE, sw=1.8))

    # Резистор R2 (фільтр 1k) та діод D1 паралельно
    p.append(line(120, 170, 135, 170, color=LINE, sw=1.8))
    p.append(rect(135, 158, 40, 24, fill=FILL, stroke=LINE, sw=1.5, rx=2))
    p.append(text(155, 150, "R2 (1 кОм)", size=10, color=INK, bold=True))
    p.append(line(175, 170, 220, 170, color=LINE, sw=1.8))

    # Діод паралельно R2 для швидкого розряду
    p.append(line(125, 170, 125, 205, color=LINE, sw=1.5))
    p.append(line(125, 205, 145, 205, color=LINE, sw=1.5))
    p.append(rect(145, 195, 25, 20, fill="#fff5ea", stroke="#d35400", sw=1.5, rx=2))
    p.append(text(157, 209, "D1", size=10, color="#d35400", bold=True))
    p.append(line(170, 205, 195, 205, color=LINE, sw=1.5))
    p.append(line(195, 205, 195, 170, color=LINE, sw=1.5))
    p.append(text(160, 226, "швидкий розряд C", size=9, color="#d35400"))

    # Конденсатор C1 (100 нФ) на землю
    p.append(circle(220, 170, 3.5, fill=INK, stroke=INK, sw=1.0))
    p.append(line(220, 170, 220, 205, color=LINE, sw=1.8))
    p.append(line(205, 205, 235, 205, color=LINE, sw=2.0))
    p.append(line(205, 212, 235, 212, color=LINE, sw=2.0))
    p.append(text(245, 211, "C1 (100 нФ)", size=10, color=INK, bold=True, anchor="start"))
    p.append(line(220, 212, 220, 260, color=LINE, sw=1.8))
    p.append(line(205, 260, 235, 260, color=LINE, sw=2.0))
    p.append(line(212, 265, 228, 265, color=LINE, sw=1.8))
    p.append(line(217, 270, 223, 270, color=LINE, sw=1.5))

    # Вхід на тригер Шмітта
    p.append(line(220, 170, 270, 170, color=LINE, sw=1.8))
    p.append(rect(270, 140, 70, 60, fill="#edf2f7", stroke=LINE, sw=1.8, rx=4))
    p.append(text(305, 165, "Тригер", size=11, color=INK, bold=True))
    p.append(text(305, 180, "Шмітта", size=11, color=INK, bold=True))
    p.append(circle(345, 170, 4, fill=BG, stroke=LINE, sw=1.5))
    p.append(arrow(349, 170, 395, 170, color=FIELD, sw=2.2))
    p.append(text(398, 164, "До GPIO МК", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(398, 178, "(чистий фронт)", size=10, color=MUTED, anchor="start"))

    # Права половина: передавальна характеристика гістерезису
    px0, py0 = 550, 240
    pw, ph = 210, 150
    p.append(text(px0 + 105, 45, "Передавальна характеристика (гістерезис)", size=13, color=INK, bold=True))

    p.append(arrow(px0, py0, px0 + pw + 20, py0, color=INK, sw=1.6))
    p.append(arrow(px0, py0, px0, py0 - ph - 25, color=INK, sw=1.6))
    p.append(text(px0 + pw + 15, py0 + 18, "U_вх (В)", size=11, color=INK, italic=True))
    p.append(text(px0 - 12, py0 - ph - 15, "U_вих", size=11, color=INK, bold=True, italic=True, anchor="end"))

    # Позначення рівнів VT- та VT+
    vt_minus_x = px0 + 65
    vt_plus_x = px0 + 145
    vh_y = py0 - ph

    p.append(line(vt_minus_x, py0, vt_minus_x, py0 - ph, color=MUTED, sw=1.0, dash="3 3"))
    p.append(line(vt_plus_x, py0, vt_plus_x, py0 - ph, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(vt_minus_x, py0 + 16, "V_T− (1.1 В)", size=10, color=NEG, bold=True))
    p.append(text(vt_plus_x, py0 + 16, "V_T+ (2.0 В)", size=10, color=POS, bold=True))

    # Смуга гістерезису Delta V_T (заливка)
    p.append(rect(vt_minus_x, vh_y, vt_plus_x - vt_minus_x, ph, fill="#f4f6f8", stroke="none"))
    p.append(text(px0 + 105, py0 - ph / 2, "ΔV_T (гістерезис)", size=10, color=INK, bold=True))

    # Петля гістерезису
    p.append(line(px0, vh_y, vt_plus_x, vh_y, color=POS, sw=2.5))
    p.append(line(vt_plus_x, vh_y, vt_plus_x, py0, color=POS, sw=2.5))
    p.append(line(vt_plus_x, py0, px0 + pw, py0, color=POS, sw=2.5))

    p.append(line(px0 + pw, py0, vt_minus_x, py0, color=NEG, sw=2.0, dash="4 3"))
    p.append(line(vt_minus_x, py0, vt_minus_x, vh_y, color=NEG, sw=2.0, dash="4 3"))
    p.append(line(vt_minus_x, vh_y, px0, vh_y, color=NEG, sw=2.0, dash="4 3"))

    # Стрілки напрямку
    p.append(arrow(px0 + 40, vh_y - 8, px0 + 60, vh_y - 8, color=POS, sw=1.5))
    p.append(arrow(px0 + 170, py0 + 8, px0 + 150, py0 + 8, color=NEG, sw=1.5))

    # Блок з поясненням під графіком
    b_hys, _, _ = textbox(px0 + 105, py0 + 55, "Ширина гістерезису ΔV_T = V_T+ − V_T−\n(зона нечутливості до брязкоту й шуму)", size=10, color=INK, fill="#ffffff", stroke=LINE)
    p.append(b_hys)

    render(os.path.join(OUT, "rc-schmitt-circuit.svg"), W, H, *p,
           title="Схема апаратного дебаунсу та характеристика тригера Шмітта")


# ── 3. button-fsm-states: граф переходів скінченного автомата подій ─────────
def fig_button_fsm():
    W, H = 840, 420
    p = []

    st_idle = (130, 90)
    st_debounce = (400, 90)
    st_pressed = (680, 90)
    st_wait_dbl = (400, 260)
    st_long_hold = (680, 260)
    st_repeat = (680, 360)

    b_idle, _, _ = textbox(st_idle[0], st_idle[1], "IDLE\n(Кнопку відпущено)", size=12, bold=True, fill="#eafaf0", stroke=FIELD, pad=12)
    b_deb, _, _ = textbox(st_debounce[0], st_debounce[1], "DEBOUNCE\n(Фільтрація 20 мс)", size=12, bold=True, fill="#fff8e6", stroke="#d35400", pad=12)
    b_press, _, _ = textbox(st_pressed[0], st_pressed[1], "PRESSED\n(Контакт зафіксовано)", size=12, bold=True, fill="#fdecea", stroke=POS, pad=12)
    b_dbl, _, _ = textbox(st_wait_dbl[0], st_wait_dbl[1], "WAIT_DOUBLE_CLICK\n(Пауза до 250 мс)", size=12, bold=True, fill="#eaf0fd", stroke=NEG, pad=12)
    b_long, _, _ = textbox(st_long_hold[0], st_long_hold[1], "LONG_PRESS_HOLD\n(Утримання > 800 мс)", size=12, bold=True, fill="#f3e8fd", stroke="#8e44ad", pad=12)
    b_rep, _, _ = textbox(st_repeat[0], st_repeat[1], "AUTO_REPEAT\n(Повтор що 100 мс)", size=12, bold=True, fill="#fdecea", stroke=POS, pad=10)

    p.append(b_idle)
    p.append(b_deb)
    p.append(b_press)
    p.append(b_dbl)
    p.append(b_long)
    p.append(b_rep)

    # 1. IDLE -> DEBOUNCE
    p.append(arrow(195, 90, 315, 90, color=LINE, sw=1.8))
    p.append(text(255, 78, "Пін = 0 (спад)", size=10, color=INK, bold=True))

    # 2. DEBOUNCE -> IDLE
    p.append(arrow(330, 115, 195, 115, color=MUTED, sw=1.4))
    p.append(text(255, 130, "Пін = 1 (дребезг)", size=9, color=MUTED))

    # 3. DEBOUNCE -> PRESSED
    p.append(arrow(475, 90, 595, 90, color=FIELD, sw=1.8))
    p.append(text(535, 78, "Час ≥ 20 мс", size=10, color=FIELD, bold=True))
    p.append(text(535, 112, "EVENT_PRESS", size=9, color=POS, bold=True))

    # 4. PRESSED -> WAIT_DOUBLE_CLICK
    p.append(arrow(635, 115, 470, 235, color=LINE, sw=1.8))
    p.append(text(575, 185, "Відпущено (< 800 мс)", size=10, color=INK, bold=True))

    # 5. PRESSED -> LONG_PRESS_HOLD
    p.append(arrow(680, 125, 680, 225, color="#8e44ad", sw=1.8))
    p.append(text(745, 175, "Час ≥ 800 мс\nEVENT_LONG_PRESS", size=10, color="#8e44ad", bold=True))

    # 6. LONG_PRESS_HOLD -> AUTO_REPEAT
    p.append(arrow(680, 295, 680, 335, color=POS, sw=1.8))
    p.append(text(745, 318, "Таймер 100 мс", size=9, color=POS))

    # 7. LONG_PRESS / REPEAT -> IDLE
    p.append(line(595, 260, 130, 260, color=MUTED, sw=1.5, dash="4 3"))
    p.append(arrow(130, 260, 130, 125, color=MUTED, sw=1.5))
    p.append(text(250, 275, "Відпущено → EVENT_RELEASE", size=10, color=MUTED))

    # 8. WAIT_DOUBLE_CLICK -> IDLE
    p.append(arrow(320, 260, 170, 120, color=NEG, sw=1.8))
    p.append(text(210, 205, "Таймаут 250 мс →\nEVENT_SHORT_CLICK", size=10, color=NEG, bold=True))

    # 9. WAIT_DOUBLE_CLICK -> IDLE
    p.append(line(400, 295, 400, 350, color=POS, sw=1.8))
    p.append(line(400, 350, 90, 350, color=POS, sw=1.8))
    p.append(arrow(90, 350, 90, 125, color=POS, sw=1.8))
    p.append(text(230, 365, "Друге натискання (< 250 мс) → EVENT_DOUBLE_CLICK", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "button-fsm-states.svg"), W, H, *p,
           title="Скінченний автомат диспетчеризації складних подій кнопки")


# ── 4. quadrature-encoder-phases: фази A і B та послідовність Грея ──────────
def fig_quadrature_encoder():
    W, H = 820, 380
    ox, oy1 = 70, 90
    oy2 = 230
    p = []

    # Верхня частина: CW
    p.append(text(ox, 40, "Обертання за годинниковою стрілкою (CW): Фаза A випереджає фазу B на 90°", size=13, color=POS, bold=True, anchor="start"))

    p.append(text(ox - 10, oy1 - 15, "Фаза A", size=11, color=INK, bold=True, anchor="end"))
    pts_a = [
        (ox, oy1 - 30), (ox + 80, oy1 - 30), (ox + 80, oy1),
        (ox + 160, oy1), (ox + 160, oy1 - 30),
        (ox + 240, oy1 - 30), (ox + 240, oy1),
        (ox + 320, oy1), (ox + 320, oy1 - 30), (ox + 340, oy1 - 30)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % pt for pt in pts_a), POS))

    p.append(text(ox - 10, oy1 + 35, "Фаза B", size=11, color=INK, bold=True, anchor="end"))
    pts_b = [
        (ox, oy1 + 50), (ox + 40, oy1 + 50), (ox + 40, oy1 + 20),
        (ox + 120, oy1 + 20), (ox + 120, oy1 + 50),
        (ox + 200, oy1 + 50), (ox + 200, oy1 + 20),
        (ox + 280, oy1 + 20), (ox + 280, oy1 + 50), (ox + 340, oy1 + 50)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % pt for pt in pts_b), NEG))

    st_cw = ["00", "10", "11", "01", "00", "10", "11", "01"]
    for i in range(8):
        sx = ox + i * 40 + 20
        p.append(line(ox + i * 40, oy1 - 35, ox + i * 40, oy1 + 60, color=MUTED, sw=0.8, dash="2 2"))
        p.append(text(sx, oy1 + 75, st_cw[i], size=11, color=INK, bold=True))

    b_cw, _, _ = textbox(ox + 500, oy1 + 15, "Послідовність станів Грея (CW):\n00 → 10 → 11 → 01 → 00 (+1 крок)\nКожен крок змінює рівно ОДИН біт", size=11, color=POS, fill="#fff5f5", stroke=POS)
    p.append(b_cw)

    # Нижня частина: CCW
    p.append(text(ox, 190, "Обертання проти годинникової стрілки (CCW): Фаза B випереджає фазу A на 90°", size=13, color=NEG, bold=True, anchor="start"))

    p.append(text(ox - 10, oy2 + 20, "Фаза A", size=11, color=INK, bold=True, anchor="end"))
    pts_a2 = [
        (ox, oy2 + 35), (ox + 40, oy2 + 35), (ox + 40, oy2 + 5),
        (ox + 120, oy2 + 5), (ox + 120, oy2 + 35),
        (ox + 200, oy2 + 35), (ox + 200, oy2 + 5),
        (ox + 280, oy2 + 5), (ox + 280, oy2 + 35), (ox + 340, oy2 + 35)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % pt for pt in pts_a2), POS))

    p.append(text(ox - 10, oy2 + 70, "Фаза B", size=11, color=INK, bold=True, anchor="end"))
    pts_b2 = [
        (ox, oy2 + 55), (ox + 80, oy2 + 55), (ox + 80, oy2 + 85),
        (ox + 160, oy2 + 85), (ox + 160, oy2 + 55),
        (ox + 240, oy2 + 55), (ox + 240, oy2 + 85),
        (ox + 320, oy2 + 85), (ox + 320, oy2 + 55), (ox + 340, oy2 + 55)
    ]
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join("%.1f,%.1f" % pt for pt in pts_b2), NEG))

    st_ccw = ["00", "01", "11", "10", "00", "01", "11", "10"]
    for i in range(8):
        sx = ox + i * 40 + 20
        p.append(line(ox + i * 40, oy2, ox + i * 40, oy2 + 95, color=MUTED, sw=0.8, dash="2 2"))
        p.append(text(sx, oy2 + 110, st_ccw[i], size=11, color=INK, bold=True))

    b_ccw, _, _ = textbox(ox + 500, oy2 + 50, "Послідовність станів Грея (CCW):\n00 → 01 → 11 → 10 → 00 (−1 крок)\nЗаборонений перехід: 00 ↔ 11 (брязкіт/збій)", size=11, color=NEG, fill="#eaf0fd", stroke=NEG)
    p.append(b_ccw)

    render(os.path.join(OUT, "quadrature-encoder-phases.svg"), W, H, *p,
           title="Квадратурні фазові діаграми та послідовність коду Грея")


# ── 5. timer-encoder-mode: апаратний інтерфейс енкодера на таймері МК ──────
def fig_timer_encoder_mode():
    W, H = 820, 360
    p = []

    p.append(text(410, 40, "Апаратний режим таймера мікроконтролера (Timer Encoder Mode)", size=14, color=INK, bold=True))

    # Вхід TI1 (Фаза A)
    p.append(text(50, 110, "Вхід TI1 (Фаза A)", size=11, color=POS, bold=True, anchor="start"))
    p.append(arrow(160, 105, 210, 105, color=POS, sw=2.0))

    # Вхід TI2 (Фаза B)
    p.append(text(50, 240, "Вхід TI2 (Фаза B)", size=11, color=NEG, bold=True, anchor="start"))
    p.append(arrow(160, 235, 210, 235, color=NEG, sw=2.0))

    # Цифрові фільтри входів (IC1F / IC2F)
    p.append(rect(210, 75, 110, 60, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=4))
    p.append(text(265, 100, "Цифровий фільтр", size=10, color=INK, bold=True))
    p.append(text(265, 115, "IC1F (N вибірок)", size=9, color=MUTED))

    p.append(rect(210, 205, 110, 60, fill="#f4f6f8", stroke=LINE, sw=1.8, rx=4))
    p.append(text(265, 230, "Цифровий фільтр", size=10, color=INK, bold=True))
    p.append(text(265, 245, "IC2F (N вибірок)", size=9, color=MUTED))

    # Лінії після фільтрів
    p.append(arrow(320, 105, 380, 135, color=POS, sw=1.8))
    p.append(text(345, 100, "TI1FP1", size=9, color=POS, bold=True))

    p.append(arrow(320, 235, 380, 205, color=NEG, sw=1.8))
    p.append(text(345, 240, "TI2FP2", size=9, color=NEG, bold=True))

    # Блок декодера квадратури
    p.append(rect(380, 115, 150, 110, fill="#eaf0fd", stroke=NEG, sw=2.0, rx=6))
    p.append(text(455, 145, "Квадратурний", size=12, color=NEG, bold=True))
    p.append(text(455, 162, "декодер таймера", size=12, color=NEG, bold=True))
    p.append(text(455, 185, "Режими X1, X2, X4", size=10, color=INK))
    p.append(text(455, 200, "Логіка напрямку", size=9, color=MUTED))

    # Вихідні сигнали з декодера на лічильник CNT
    p.append(arrow(530, 145, 610, 145, color=FIELD, sw=2.0))
    p.append(text(570, 135, "CNT_CLK (тактові)", size=9, color=FIELD, bold=True))

    p.append(arrow(530, 195, 610, 195, color="#8e44ad", sw=2.0))
    p.append(text(570, 185, "DIR (напрямок)", size=9, color="#8e44ad", bold=True))

    # Регістр лічильника TIMx_CNT
    p.append(rect(610, 115, 150, 110, fill="#eafaf0", stroke=FIELD, sw=2.0, rx=6))
    p.append(text(685, 145, "Регістр TIMx_CNT", size=12, color=FIELD, bold=True))
    p.append(text(685, 165, "16 / 32-бітний", size=10, color=INK))
    p.append(text(685, 180, "реверсивний лічильник", size=10, color=INK))
    p.append(text(685, 205, "(Без навантаження CPU)", size=9, color=FIELD, bold=True))

    # Підказка знизу
    b_note, _, _ = textbox(410, 310, "Апаратний таймер самостійно інкрементує/декрементує лічильник за кожним кліком,\nвідфільтровуючи високочастотні завади без участі процесора та без викликів ISR", size=11, color=INK, fill="#ffffff", stroke=LINE)
    p.append(b_note)

    render(os.path.join(OUT, "timer-encoder-mode.svg"), W, H, *p,
           title="Апаратний квадратурний декодер таймера мікроконтролера")


if __name__ == "__main__":
    fig_contact_bounce()
    fig_rc_schmitt_circuit()
    fig_button_fsm()
    fig_quadrature_encoder()
    fig_timer_encoder_mode()
    print("Усі 5 фігур успішно згенеровано.")
