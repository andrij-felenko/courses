# -*- coding: utf-8 -*-
"""Фігури для статті shcho-mozhna-povisyty-na-pin («Що можна повісити на пін»).
svgkit імпортуємо зі scripts/, не переписуємо (AUTHORING §5).

    python figs.py    # вивід у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. gpio-push-pull: Внутрішня будова вихідного каскаду GPIO ──────────────
def fig_gpio_push_pull():
    W, H = 820, 440
    p = []

    # Контур мікроконтролера (кристал / внутрішній блок)
    p.append(rect(40, 40, 560, 360, fill="#fcfdfe", stroke=LINE, sw=1.8, rx=8))
    p.append(text(140, 68, "Внутрішня структура GPIO (кристал МК)", size=13, color=MUTED, bold=True))

    # Шина VDD угорі та VSS/GND унизу
    p.append(line(70, 95, 540, 95, color=POS, sw=2.2))
    p.append(text(80, 85, "VDD (+3.3 В)", size=12, color=POS, bold=True, anchor="start"))

    p.append(line(70, 365, 540, 365, color=NEG, sw=2.2))
    p.append(text(80, 385, "VSS / GND (0 В)", size=12, color=NEG, bold=True, anchor="start"))

    # Драйвер керування затворами
    b_ctl, _, _ = textbox(130, 230, "Логіка керування\nі регістри GPIO\n(ODR, MODER)",
                          size=11, fill="#edf2f7", stroke=LINE, sw=1.3, pad=8)
    p.append(b_ctl)

    # Верхнє плече: P-канальний MOSFET (Source)
    p.append(line(210, 195, 270, 195, color=LINE, sw=1.4))  # сигнал на затвор P-MOS
    p.append(text(240, 185, "Затвор P", size=10, color=MUTED))
    b_pmos, _, _ = textbox(320, 160, "P-MOSFET (Source)\nR_DS(on) ≈ 30…50 Ом\nтягне до VDD",
                           size=11, fill="#fdecea", stroke=POS, sw=1.4, color=POS, pad=7)
    p.append(b_pmos)
    p.append(line(320, 95, 320, 125, color=POS, sw=1.8))   # до VDD
    p.append(line(320, 195, 320, 230, color=LINE, sw=1.8))  # до спільної точки виходу

    # Нижнє плече: N-канальний MOSFET (Sink)
    p.append(line(210, 265, 270, 265, color=LINE, sw=1.4))  # сигнал на затвор N-MOS
    p.append(text(240, 280, "Затвор N", size=10, color=MUTED))
    b_nmos, _, _ = textbox(320, 300, "N-MOSFET (Sink)\nR_DS(on) ≈ 20…35 Ом\nтягне до GND",
                           size=11, fill="#eaf0fd", stroke=NEG, sw=1.4, color=NEG, pad=7)
    p.append(b_nmos)
    p.append(line(320, 230, 320, 265, color=LINE, sw=1.8))  # від точки виходу
    p.append(line(320, 335, 320, 365, color=NEG, sw=1.8))  # до GND

    # Спільний вихідний вузол
    p.append(circle(320, 230, 4, fill=LINE, stroke=LINE))
    p.append(line(320, 230, 640, 230, color=LINE, sw=2.2))

    # Захисні ESD-діоди
    # Верхній діод (від виводу до VDD)
    p.append(line(460, 230, 460, 190, color=FIELD, sw=1.5))
    p.append(line(460, 140, 460, 95, color=FIELD, sw=1.5))
    b_desd1, _, _ = textbox(460, 165, "ESD діод\nдо VDD", size=10, fill="#eafaf0",
                            stroke=FIELD, sw=1.2, color=FIELD, pad=4)
    p.append(b_desd1)

    # Нижній діод (від GND до виводу)
    p.append(line(460, 230, 460, 270, color=FIELD, sw=1.5))
    p.append(line(460, 320, 460, 365, color=FIELD, sw=1.5))
    b_desd2, _, _ = textbox(460, 295, "ESD діод\nвід GND", size=10, fill="#eafaf0",
                            stroke=FIELD, sw=1.2, color=FIELD, pad=4)
    p.append(b_desd2)

    # Фізичний вивід (PAD / Pin)
    p.append(rect(640, 210, 40, 40, fill="#fff2cc", stroke="#d6b656", sw=1.8, rx=4))
    p.append(text(660, 235, "PAD", size=11, bold=True, color="#806000"))

    # Провідник назовні до ніжки плати
    p.append(line(680, 230, 780, 230, color=LINE, sw=2.0))
    p.append(circle(780, 230, 6, fill="#ffe699", stroke=LINE, sw=1.8))
    p.append(text(780, 260, "Пін GPIO", size=12, bold=True, color=INK))

    render(os.path.join(OUT, "gpio-push-pull.svg"), W, H, *p,
           title="Внутрішня будова вихідного каскаду GPIO (Push-Pull пара та ESD-захист)")


# ── 2. current-hierarchy: Три рівні струмових обмежень ───────────────────────
def fig_current_hierarchy():
    W, H = 820, 420
    p = []

    # Рівень 3 (зовнішній): Весь чип і шини живлення кристала
    p.append(rect(40, 50, 740, 340, fill="#fdf7f7", stroke=POS, sw=2.0, rx=10))
    p.append(text(60, 80, "РІВЕНЬ 3: Сумарний струм кристала (I_DD_total / I_SS_total ≤ 120…150 мА)",
                  size=13, color=POS, bold=True, anchor="start"))
    p.append(text(60, 100, "Обмеження тонких розварювальних провідників (bond wires) та загального нагріву кремнію",
                  size=11, color=MUTED, anchor="start"))

    # Рівень 2: Порти виводів (Port A, Port B)
    p.append(rect(70, 125, 330, 240, fill="#f4f8ff", stroke=NEG, sw=1.6, rx=8))
    p.append(text(85, 150, "РІВЕНЬ 2: Порт A (I_PORT ≤ 60…80 мА)", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(85, 168, "Спільна шина живлення групи виводів", size=10, color=MUTED, anchor="start"))

    p.append(rect(420, 125, 330, 240, fill="#f4f8ff", stroke=NEG, sw=1.6, rx=8))
    p.append(text(435, 150, "РІВЕНЬ 2: Порт B (I_PORT ≤ 60…80 мА)", size=12, color=NEG, bold=True, anchor="start"))
    p.append(text(435, 168, "Спільна шина живлення групи виводів", size=10, color=MUTED, anchor="start"))

    # Рівень 1: Одиночні піни всередині портів
    # У Порту A
    b_p1, _, _ = textbox(150, 225, "Pin PA0\nI_IO ≤ 8…20 мА", size=11, fill="#ffffff",
                         stroke=LINE, sw=1.3, pad=6)
    b_p2, _, _ = textbox(310, 225, "Pin PA1\nI_IO ≤ 8…20 мА", size=11, fill="#ffffff",
                         stroke=LINE, sw=1.3, pad=6)
    b_p3, _, _ = textbox(150, 310, "Pin PA2\nI_IO ≤ 8…20 мА", size=11, fill="#ffffff",
                         stroke=LINE, sw=1.3, pad=6)
    b_p4, _, _ = textbox(310, 310, "Pin PA3…PA7\n(до 8 виводів)", size=11, fill="#ffffff",
                         stroke=LINE, sw=1.3, pad=6)
    p.extend([b_p1, b_p2, b_p3, b_p4])

    # У Порту B
    b_pb1, _, _ = textbox(500, 225, "Pin PB0\nI_IO ≤ 8…20 мА", size=11, fill="#ffffff",
                          stroke=LINE, sw=1.3, pad=6)
    b_pb2, _, _ = textbox(660, 225, "Pin PB1\nI_IO ≤ 8…20 мА", size=11, fill="#ffffff",
                          stroke=LINE, sw=1.3, pad=6)
    b_pb3, _, _ = textbox(500, 310, "Pin PB2\nI_IO ≤ 8…20 мА", size=11, fill="#ffffff",
                          stroke=LINE, sw=1.3, pad=6)
    b_pb4, _, _ = textbox(660, 310, "Pin PB3…PB7\n(до 8 виводів)", size=11, fill="#ffffff",
                          stroke=LINE, sw=1.3, pad=6)
    p.extend([b_pb1, b_pb2, b_pb3, b_pb4])

    render(os.path.join(OUT, "current-hierarchy.svg"), W, H, *p,
           title="Ієрархія струмових обмежень: одиночний пін → порт → кристал МК")


# ── 3. voh-vol-curves: Просідання VOH та підйом VOL під навантаженням ────────
def fig_voh_vol_curves():
    W, H = 820, 380
    p = []

    # Лівий графік: VOH (Sourcing)
    ox1, oy1 = 90, 290
    gw, gh = 280, 200

    p.append(arrow(ox1, oy1, ox1 + gw + 20, oy1, color=INK, sw=1.5))
    p.append(arrow(ox1, oy1, ox1, oy1 - gh - 20, color=INK, sw=1.5))
    p.append(text(ox1 + gw + 20, oy1 + 20, "I_source (мА)", size=11, italic=True))
    p.append(text(ox1 - 10, oy1 - gh - 15, "V_OH (В)", size=11, bold=True, anchor="end"))

    # Шкала напруги VOH: 0 В, 2.4 В, 2.7 В, 3.3 В
    p.append(text(ox1 - 10, oy1, "0 В", size=10, anchor="end", color=MUTED))
    p.append(line(ox1, oy1 - gh, ox1 + gw, oy1 - gh, color=MUTED, sw=1.0, dash="3 3"))
    p.append(text(ox1 - 10, oy1 - gh, "3.3 В (VDD)", size=10, anchor="end", color=POS))

    # Гарантований поріг V_IH (наприклад 2.0 В або 0.7*VDD = 2.31 В)
    p.append(line(ox1, oy1 - gh * 0.70, ox1 + gw, oy1 - gh * 0.70, color=NEG, sw=1.0, dash="4 3"))
    p.append(text(ox1 + gw, oy1 - gh * 0.70 - 5, "V_IH_min (поріг розпізнавання '1')",
                  size=9, color=NEG, anchor="end"))

    # Крива VOH(I) = VDD - I * R_DS(on)
    # При 0 мА -> 3.3 В, при 20 мА -> 2.6 В
    p.append(line(ox1, oy1 - gh, ox1 + gw * 0.8, oy1 - gh * 0.78, color=POS, sw=2.5))
    p.append(circle(ox1, oy1 - gh, 4, fill=POS, stroke=POS))
    p.append(circle(ox1 + gw * 0.8, oy1 - gh * 0.78, 4, fill=POS, stroke=POS))

    p.append(text(ox1 + gw * 0.4, oy1 - gh * 0.95, "Падіння: ΔV = I · R_DS(on)_P", size=10, color=POS, bold=True))
    p.append(text(ox1 + gw * 0.8, oy1 + 18, "20 мА", size=10, color=MUTED))
    p.append(text(ox1 + gw * 0.82, oy1 - gh * 0.78 + 4, "≈ 2.6…2.7 В", size=10, color=POS, bold=True, anchor="start"))

    # Правий графік: VOL (Sinking)
    ox2, oy2 = 490, 290
    p.append(arrow(ox2, oy2, ox2 + gw + 20, oy2, color=INK, sw=1.5))
    p.append(arrow(ox2, oy2, ox2, oy2 - gh - 20, color=INK, sw=1.5))
    p.append(text(ox2 + gw + 20, oy2 + 20, "I_sink (мА)", size=11, italic=True))
    p.append(text(ox2 - 10, oy2 - gh - 15, "V_OL (В)", size=11, bold=True, anchor="end"))

    # Шкала VOL: 0 В, 0.4 В, 0.8 В
    p.append(text(ox2 - 10, oy2, "0 В (GND)", size=10, anchor="end", color=NEG))
    p.append(line(ox2, oy2 - gh * 0.25, ox2 + gw, oy2 - gh * 0.25, color=POS, sw=1.0, dash="4 3"))
    p.append(text(ox2 + gw, oy2 - gh * 0.25 - 5, "V_IL_max (поріг розпізнавання '0')",
                  size=9, color=POS, anchor="end"))

    # Крива VOL(I) = I * R_DS(on)_N
    # При 0 мА -> 0 В, при 20 мА -> 0.5 В
    p.append(line(ox2, oy2, ox2 + gw * 0.8, oy2 - gh * 0.16, color=NEG, sw=2.5))
    p.append(circle(ox2, oy2, 4, fill=NEG, stroke=NEG))
    p.append(circle(ox2 + gw * 0.8, oy2 - gh * 0.16, 4, fill=NEG, stroke=NEG))

    p.append(text(ox2 + gw * 0.4, oy2 - gh * 0.35, "Підйом: V_OL = I · R_DS(on)_N", size=10, color=NEG, bold=True))
    p.append(text(ox2 + gw * 0.8, oy2 + 18, "20 мА", size=10, color=MUTED))
    p.append(text(ox2 + gw * 0.82, oy2 - gh * 0.16 + 4, "≈ 0.4…0.5 В", size=10, color=NEG, bold=True, anchor="start"))

    render(os.path.join(OUT, "voh-vol-curves.svg"), W, H, *p,
           title="Падіння вихідної напруги V_OH та підйом V_OL як функція струму навантаження")


# ── 4. phantom-powering: Феномен паразитного (фантомного) живлення ───────────
def fig_phantom_powering():
    W, H = 820, 420
    p = []

    # Лівий блок: Зовнішній активний пристрій (наприклад USB-UART або давач з живленням 3.3В)
    p.append(rect(40, 70, 230, 300, fill="#fdfbf7", stroke="#d97706", sw=1.6, rx=8))
    p.append(text(155, 100, "Активний пристрій\n(USB-UART / давач)", size=12, bold=True, color="#b45309"))
    p.append(line(60, 140, 250, 140, color=POS, sw=2.0))
    p.append(text(70, 130, "Власне живлення +3.3 В", size=11, color=POS, bold=True, anchor="start"))

    # Вихідний сигнал TX / OUT = 3.3 В
    b_tx, _, _ = textbox(155, 220, "Вихід TX / Signal\nНапруга = +3.3 В", size=11,
                         fill="#fef3c7", stroke="#d97706", sw=1.3, pad=6)
    p.append(b_tx)

    # Правий блок: Знеструмлений МК (VDD = 0 В)
    p.append(rect(420, 70, 360, 300, fill="#f9fafb", stroke=LINE, sw=1.8, rx=8))
    p.append(text(600, 100, "ЗНЕСТРУМЛЕНИЙ МК (живлення вимкнено)", size=12, bold=True, color=POS))

    # Внутрішня шина живлення МК
    p.append(line(450, 140, 750, 140, color=POS, sw=2.0, dash="5 4"))
    p.append(text(460, 130, "Шина VDD МК (мало бути 0 В!)", size=11, color=POS, bold=True, anchor="start"))

    # Пін RX / GPIO
    p.append(rect(430, 205, 50, 30, fill="#fff2cc", stroke="#d6b656", sw=1.5, rx=3))
    p.append(text(455, 225, "GPIO", size=10, bold=True, color="#806000"))

    # Лінія зв'язку з TX на GPIO
    p.append(arrow(220, 220, 430, 220, color="#d97706", sw=2.2))
    p.append(text(325, 205, "Сигнал 3.3 В", size=11, bold=True, color="#b45309"))

    # Верхній ESD діод всередині МК
    p.append(line(490, 220, 560, 220, color=POS, sw=2.0))
    p.append(line(560, 220, 560, 185, color=POS, sw=2.0))
    p.append(line(560, 145, 560, 140, color=POS, sw=2.0))

    b_esd, _, _ = textbox(560, 165, "Верхній ESD-діод\nВІДКРИВАЄТЬСЯ!", size=10,
                          fill="#fee2e2", stroke=POS, sw=1.4, color=POS, pad=4)
    p.append(b_esd)

    # Струм паразитного живлення перетікає на шину VDD МК
    p.append(arrow(560, 140, 680, 140, color=POS, sw=2.2))
    b_parasitic, _, _ = textbox(650, 230, "Паразитне живлення ядра:\nVDD_par ≈ 3.3В − 0.6В = 2.7 В\n• Зависання процесора\n• Збій Flash/RAM\n• Ризик Latch-up",
                                size=11, fill="#fef2f2", stroke=POS, sw=1.4, color=POS, pad=8)
    p.append(b_parasitic)

    render(os.path.join(OUT, "phantom-powering.svg"), W, H, *p,
           title="Механізм паразитного (фантомного) живлення через верхній захисний ESD-діод")


# ── 5. allowed-vs-forbidden: Зелена vs Червона зона навантажень ───────────────
def fig_allowed_vs_forbidden():
    W, H = 820, 440
    p = []

    # Ліва колонка: ДОЗВОЛЕНО НАПРЯМУ (Зелена зона)
    p.append(rect(40, 50, 350, 360, fill="#f6fcf8", stroke=FIELD, sw=2.0, rx=8))
    p.append(text(215, 80, "ДОЗВОЛЕНО НАПРЯМУ (безпечно)", size=13, bold=True, color=FIELD))

    items_ok = [
        "1. Індикаторні LED (з резистором R ≥ 220 Ом)\n   Струм I ≤ 3…5 мА",
        "2. Цифрові логічні входи (CMOS-входи)\n   Вхідний опір > 10 МОм, струм витоку < 1 мкА",
        "3. Високоомні сенсори та дільники напруги\n   R_div ≥ 10…100 кОм",
        "4. Резистори підтяжки (Pull-Up / Pull-Down)\n   Типові номінали: 2.2 кОм … 47 кОм",
        "5. Малопотужні оптопари (I_F ≤ 3…5 мА)\n   Тільки з розрахунковим резистором",
    ]
    y_ok = 125
    for item in items_ok:
        b, _, bh = textbox(215, y_ok, item, size=10, fill="#ffffff", stroke=FIELD, sw=1.0, color=INK, pad=5, min_w=310)
        p.append(b)
        y_ok += bh + 8

    # Права колонка: СУВОРО ЗАБОРОНЕНО НАПРЯМУ (Червона зона)
    p.append(rect(430, 50, 350, 360, fill="#fdf7f7", stroke=POS, sw=2.0, rx=8))
    p.append(text(605, 80, "СУВОРО ЗАБОРОНЕНО НАПРЯМУ", size=13, bold=True, color=POS))

    items_bad = [
        "1. Індуктивності (реле, мотори, соленоїди)\n   Кидок самоіндукції U = −L·di/dt > 50…200 В!",
        "2. Світлодіодні стрічки та потужні LED\n   Струми від 50 мА до десятків ампер",
        "3. Ємності > 50 пФ без резистора\n   Піковий струм i = C·dv/dt > 100…300 мА!",
        "4. Бази біполярних транзисторів напряму\n   Прямий PN-перехід замикає пін на 0.7 В",
        "5. Сигнали з напругою > VDD + 0.3 В (не-FT)\n   Струм інжекції випалює ESD-діод і чіп",
    ]
    y_bad = 125
    for item in items_bad:
        b, _, bh = textbox(605, y_bad, item, size=10, fill="#ffffff", stroke=POS, sw=1.0, color=INK, pad=5, min_w=310)
        p.append(b)
        y_bad += bh + 8

    render(os.path.join(OUT, "allowed-vs-forbidden.svg"), W, H, *p,
           title="Класифікація навантажень для виводу МК: безпечна зона vs смертельні помилки")


if __name__ == "__main__":
    fig_gpio_push_pull()
    fig_current_hierarchy()
    fig_voh_vol_curves()
    fig_phantom_powering()
    fig_allowed_vs_forbidden()
    print("All 5 figures generated successfully.")
