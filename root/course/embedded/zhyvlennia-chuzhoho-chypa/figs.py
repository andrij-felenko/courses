# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. multi-rail-topology: домени живлення та розв'язка ──────────────────────
def fig_multi_rail_topology():
    W, H = 760, 400
    p = []

    # Головне джерело (зліва)
    b_src = fitbox(20, 150, 110, 80, "Головна шина\n3.3 В (DC-DC)", size=12, bold=True, fill="#fdecea", stroke=POS)
    p.append(b_src)

    # Розгалуження на три домени
    # Домен 1: VDDIO
    p.append(line(130, 170, 200, 70, color=LINE, sw=2))
    p.append(arrow(200, 70, 250, 70, color=LINE, sw=2))
    b_io = fitbox(250, 40, 150, 60, "Шина VDDIO (3.3 В)\nБуфери вводу-виводу", size=12, fill="#eaf0fd", stroke=NEG)
    p.append(b_io)
    p.append(line(325, 100, 325, 120, color=LINE, sw=1.5))
    p.append(fitbox(290, 120, 70, 26, "C = 100 нФ", size=10, fill=BG, stroke=MUTED))

    # Домен 2: VDD_CORE (через локальний перетворювач)
    p.append(line(130, 190, 190, 190, color=LINE, sw=2))
    b_core_conv = fitbox(190, 165, 100, 50, "LDO / Buck\n1.2 В", size=11, fill="#f4f6f8", stroke=LINE)
    p.append(b_core_conv)
    p.append(arrow(290, 190, 350, 190, color=LINE, sw=2))
    b_core = fitbox(350, 160, 150, 60, "Шина VDD_CORE (1.2 В)\nЦифрове логічне ядро", size=12, fill="#fdf2e9", stroke="#e67e22")
    p.append(b_core)
    p.append(line(425, 220, 425, 240, color=LINE, sw=1.5))
    p.append(fitbox(380, 240, 90, 26, "C = 10 мкФ + 0.1 мкФ", size=10, fill=BG, stroke=MUTED))

    # Домен 3: AVDD (через Ferrite Bead + LC-фільтр)
    p.append(line(130, 210, 180, 310, color=LINE, sw=2))
    p.append(arrow(180, 310, 220, 310, color=LINE, sw=2))
    b_fb = fitbox(220, 285, 100, 50, "Ферит (FB)\n+ LDO 3.3 В", size=11, fill="#eafaf1", stroke=FIELD)
    p.append(b_fb)
    p.append(arrow(320, 310, 370, 310, color=LINE, sw=2))
    b_ana = fitbox(370, 280, 150, 60, "Шина AVDD (3.3 В чиста)\nАЦП, PLL, аналог", size=12, fill="#eafaf1", stroke=FIELD)
    p.append(b_ana)
    p.append(line(445, 340, 445, 360, color=LINE, sw=1.5))
    p.append(fitbox(400, 360, 90, 26, "C = 4.7 мкФ + 10 нФ", size=10, fill=BG, stroke=MUTED))

    # Спільний корпус чипа (справа)
    p.append(rect(540, 30, 200, 330, fill="#ffffff", stroke=LINE, sw=2, rx=8))
    p.append(text(640, 60, "Цільова мікросхема", size=14, bold=True, color=INK))
    p.append(line(550, 75, 730, 75, color=LINE, sw=1))

    # Входи чипа
    p.append(arrow(400, 70, 540, 70, color=NEG, sw=2))
    p.append(text(580, 88, "VDDIO", size=11, bold=True, color=NEG))

    p.append(arrow(500, 190, 540, 190, color="#e67e22", sw=2))
    p.append(text(595, 200, "VDD_CORE", size=11, bold=True, color="#e67e22"))

    p.append(arrow(520, 310, 540, 310, color=FIELD, sw=2))
    p.append(text(580, 320, "AVDD", size=11, bold=True, color=FIELD))

    # Спільна земля під чипом
    p.append(rect(555, 335, 170, 20, fill="#d5dbdb", stroke=LINE, sw=1))
    p.append(text(640, 349, "Суцільний шар GND", size=10, bold=True, color=INK))

    render(os.path.join(OUT, "multi-rail-topology.svg"), W, H, *p,
           title="Архітектура доменів живлення та фільтрація")


# ── 2. latch-up-mechanism: механізм Latch-up та паразитного живлення ──────────
def fig_latch_up_mechanism():
    W, H = 760, 410
    p = []

    # Ліва зона: пін МК та захисний діод
    p.append(rect(20, 45, 280, 345, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    p.append(text(160, 70, "Вхідний каскад GPIO", size=13, bold=True, color=INK))

    # Рейка VDD чипа
    p.append(line(40, 100, 280, 100, color=POS, sw=2))
    p.append(text(90, 93, "Шина VDD (0 В, вимкнена)", size=11, color=POS, bold=True))

    # Вхідний пін
    p.append(line(40, 200, 140, 200, color=LINE, sw=2))
    p.append(text(85, 190, "Пін GPIO (3.3 В)", size=11, color=INK, bold=True))

    # Верхній ESD-діод
    p.append(line(140, 200, 140, 100, color=LINE, sw=1.8))
    # Малюємо діод (трикутник вгору)
    p.append('<polygon points="133,160 147,160 140,140" fill="#fdecea" stroke="%s" stroke-width="1.5"/>' % POS)
    p.append(line(133, 140, 147, 140, color=POS, sw=1.8))
    p.append(text(195, 155, "Верхній ESD-діод\n(пряме зміщення)", size=10, color=POS, bold=True))

    # Стрілка паразитного струму
    p.append(arrow(140, 195, 140, 105, color=POS, sw=2.5))
    p.append(text(80, 225, "I_паразит > 20 мА", size=10, color=POS, bold=True))

    # Нижній ESD-діод
    p.append(line(140, 200, 140, 300, color=LINE, sw=1.8))
    p.append('<polygon points="133,260 147,260 140,280" fill="#eaf0fd" stroke="%s" stroke-width="1.5"/>' % NEG)
    p.append(line(133, 280, 147, 280, color=NEG, sw=1.8))
    p.append(text(195, 275, "Нижній ESD-діод\n(закритий)", size=10, color=MUTED))

    # Земля
    p.append(line(40, 300, 280, 300, color=NEG, sw=2))
    p.append(text(90, 315, "Шина GND (0 В)", size=11, color=NEG, bold=True))

    # Права зона: еквівалентний тиристор (PNPN Latch-up)
    p.append(rect(320, 45, 420, 345, fill="#ffffff", stroke=POS, sw=1.8, rx=6))
    p.append(text(530, 70, "Паразитна тиристорна структура (PNPN)", size=13, bold=True, color=POS))

    # Транзистор PNP (верхній)
    p.append(fitbox(340, 105, 160, 65, "Паразитний PNP\n(p+ емітер у n-well)", size=11, fill="#fdecea", stroke=POS))

    # Транзистор NPN (нижній)
    p.append(fitbox(560, 215, 160, 65, "Паразитний NPN\n(n+ емітер у p-sub)", size=11, fill="#fdecea", stroke=POS))

    # Зв'язки додатно зворотного зв'язку
    p.append(arrow(420, 170, 580, 215, color=POS, sw=2))
    p.append(text(525, 185, "I_кол(PNP) -> I_баз(NPN)", size=10, color=POS, bold=True))

    p.append(arrow(640, 215, 480, 170, color=POS, sw=2))
    p.append(text(540, 160, "I_кол(NPN) -> I_баз(PNP)", size=10, color=POS, bold=True))

    # Висновок внизу рамки
    p.append(rect(340, 300, 380, 75, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(530, 322, "Результат: лавиноподібне закорочування VDD на GND", size=11, bold=True, color=POS))
    p.append(text(530, 342, "Струм зростає до сотень мА / амперів -> термічне вигоряння", size=10, color=INK))
    p.append(text(530, 360, "Скидається лише повним зняттям живлення схеми", size=10, italic=True, color=MUTED))

    render(os.path.join(OUT, "latch-up-mechanism.svg"), W, H, *p,
           title="Фізика Latch-up при випередженні напруги на GPIO")


# ── 3. pulse-current-response: просадка напруги під час імпульсу струму ───────
def fig_pulse_current_response():
    W, H = 760, 400
    p = []

    # Графік 1: Струм навантаження I_load(t)
    p.append(text(50, 65, "Струм I_load", size=12, bold=True, color=POS))
    p.append(line(90, 130, 710, 130, color=INK, sw=1.5)) # вісь t
    p.append(line(90, 130, 90, 50, color=INK, sw=1.5))   # вісь I

    # Підписи струму
    p.append(text(80, 125, "0 A", size=10, color=MUTED, anchor="end"))
    p.append(text(80, 65, "2.0 A", size=10, color=POS, bold=True, anchor="end"))

    # Імпульс струму (прямокутник 577 мкс)
    p.append(line(90, 125, 220, 125, color=POS, sw=2))
    p.append(line(220, 125, 220, 65, color=POS, sw=2))
    p.append(line(220, 65, 520, 65, color=POS, sw=2))
    p.append(line(520, 65, 520, 125, color=POS, sw=2))
    p.append(line(520, 125, 710, 125, color=POS, sw=2))
    p.append(rect(220, 65, 300, 60, fill="#fdecea", stroke="none"))
    p.append(text(370, 95, "Імпульс передавача (Wi-Fi / GSM, 577 мкс)", size=11, bold=True, color=POS))

    # Графік 2: Напруга на рейці V_rail(t)
    p.append(text(50, 205, "Напруга V_rail", size=12, bold=True, color=NEG))
    p.append(line(90, 350, 710, 350, color=INK, sw=1.5)) # вісь t
    p.append(line(90, 350, 90, 190, color=INK, sw=1.5))   # вісь V

    # Номінал 3.3 В
    p.append(line(90, 210, 710, 210, color=MUTED, sw=1, dash="4,4"))
    p.append(text(80, 214, "3.3 В", size=10, color=MUTED, anchor="end"))

    # Поріг скидання Brown-Out Reset (BOR)
    p.append(line(90, 310, 710, 310, color=POS, sw=1.2, dash="3,3"))
    p.append(text(80, 314, "Поріг BOR (2.7 В)", size=10, color=POS, anchor="end"))

    # Крива напруги з просадкою
    # До імпульсу
    p.append(line(90, 210, 220, 210, color=NEG, sw=2.2))
    # Стрибок вниз через ESR: ΔV_ESR = I * ESR
    p.append(line(220, 210, 220, 245, color=POS, sw=2))
    p.append(text(150, 235, "ΔV_ESR = I · ESR", size=10, color=POS, bold=True))

    # Спадання напруги під час розряду конденсатора
    # Похила лінія до моменту реакції LDO
    p.append(line(220, 245, 520, 295, color=NEG, sw=2.2))
    p.append(text(370, 280, "Розряд ємності C_bulk: ΔV_C = I · Δt / C", size=10, color=NEG, bold=True))

    # Відновлення після імпульсу
    p.append(line(520, 295, 520, 260, color=POS, sw=2))
    p.append(line(520, 260, 650, 210, color=NEG, sw=2.2))
    p.append(line(650, 210, 710, 210, color=NEG, sw=2.2))

    # Запас до BOR
    p.append(line(370, 295, 370, 310, color=FIELD, sw=1.5))
    p.append(fitbox(300, 360, 160, 28, "Запас до BOR (без збою)", size=10, bold=True, fill="#eafaf1", stroke=FIELD))

    render(os.path.join(OUT, "pulse-current-response.svg"), W, H, *p,
           title="Динаміка просадки напруги при імпульсному струмі")


# ── 4. high-side-switch: схемотехніка High-Side ключа ─────────────────────────
def fig_high_side_switch():
    W, H = 760, 390
    p = []

    # Джерело живлення V_IN (зліва вгорі)
    p.append(line(30, 70, 120, 70, color=POS, sw=2))
    p.append(fitbox(30, 45, 90, 50, "Живлення V_IN\n(3.3 В .. 5 В)", size=11, bold=True, fill="#fdecea", stroke=POS))

    # P-канальний MOSFET
    p.append(line(120, 70, 300, 70, color=POS, sw=2)) # вивід Source
    p.append(fitbox(300, 45, 110, 50, "P-MOSFET (Q1)\n(Верхній ключ)", size=11, bold=True, fill="#f4f6f8", stroke=LINE))
    p.append(arrow(410, 70, 520, 70, color=POS, sw=2)) # вивід Drain -> V_OUT

    # Резистор підтяжки затвора R_pull (між Source і Gate)
    p.append(line(230, 70, 230, 150, color=LINE, sw=1.5))
    p.append(fitbox(200, 150, 60, 45, "R1\n100 кОм", size=10, fill=BG, stroke=LINE))
    p.append(line(230, 195, 230, 230, color=LINE, sw=1.5))
    p.append(line(230, 230, 355, 230, color=LINE, sw=1.5))
    p.append(line(355, 230, 355, 95, color=LINE, sw=1.5)) # Затвор Q1

    # Ланцюжок повільного відкривання (Slew Rate: R_gate + C_gate)
    p.append(fitbox(280, 208, 60, 44, "C_gate\n10 нФ", size=9, fill="#f4f6f8", stroke=MUTED))

    # N-канальний транзистор керування Q2
    p.append(line(230, 230, 230, 270, color=LINE, sw=1.5))
    p.append(fitbox(200, 270, 60, 45, "R2\n10 кОм", size=10, fill=BG, stroke=LINE))
    p.append(line(230, 315, 230, 330, color=LINE, sw=1.5))

    p.append(fitbox(280, 315, 100, 45, "N-MOSFET (Q2)\nДрайвер рівня", size=10, bold=True, fill="#eaf0fd", stroke=NEG))
    p.append(line(230, 330, 280, 330, color=LINE, sw=1.5))
    p.append(line(330, 360, 330, 375, color=NEG, sw=1.5)) # витік Q2 на GND

    # Пін керування МК
    p.append(arrow(60, 338, 280, 338, color=LINE, sw=1.8))
    p.append(fitbox(30, 315, 120, 45, "GPIO МК (PWR_EN)\nHigh = Увімкнено", size=10, fill="#eafaf1", stroke=FIELD))

    # Вихідна комутована шина V_SWITCHED
    p.append(fitbox(520, 45, 130, 50, "Комутована шина\nV_SWITCHED", size=11, bold=True, fill="#eafaf1", stroke=FIELD))

    # Навантаження (чужий чип)
    p.append(arrow(650, 70, 680, 70, color=FIELD, sw=2))
    p.append(rect(680, 40, 70, 300, fill="#ffffff", stroke=LINE, sw=1.8, rx=6))
    p.append(mtext(715, 120, "Периферійний\nчип\n(Радіо / Давач)", size=11, color=INK, bold=True))

    # Конденсатор і розрядний резистор на виході
    p.append(line(585, 95, 585, 160, color=LINE, sw=1.5))
    p.append(fitbox(550, 160, 70, 40, "C_bulk\n47 мкФ", size=9, fill=BG, stroke=MUTED))
    p.append(line(585, 200, 585, 240, color=LINE, sw=1.5))
    p.append(fitbox(550, 240, 70, 40, "R_dis\n100 кОм", size=9, fill=BG, stroke=MUTED))
    p.append(line(585, 280, 585, 375, color=NEG, sw=1.5))

    # Суцільна нерозривна земля (GND)
    p.append(line(30, 375, 750, 375, color=NEG, sw=2.5))
    p.append(text(390, 365, "Спільна нерозривна земля (GND) — розриваємо лише плюс!", size=11, bold=True, color=NEG))

    render(os.path.join(OUT, "high-side-switch.svg"), W, H, *p,
           title="Схема керованого High-Side P-MOSFET ключа")


# ── 5. phantom-power-path: паразитна інжекція струму через шини ───────────────
def fig_phantom_power_path():
    W, H = 760, 390
    p = []

    # Ліва коробка: Активний мікроконтролер
    p.append(rect(20, 50, 200, 300, fill="#eafaf1", stroke=FIELD, sw=2, rx=8))
    p.append(text(120, 80, "Мікроконтролер (МК)", size=13, bold=True, color=FIELD))
    p.append(text(120, 105, "Працює (V_MCU = 3.3 В)", size=11, color=INK))

    # Піни МК
    p.append(fitbox(40, 140, 160, 35, "GPIO (I2C SDA / SCL)", size=10, fill=BG, stroke=LINE))
    p.append(fitbox(40, 200, 160, 35, "Підтяжка R_pu до 3.3 В", size=10, fill="#fdecea", stroke=POS))

    # Права коробка: Знеструмлений чип
    p.append(rect(480, 50, 260, 300, fill="#f4f6f8", stroke=LINE, sw=2, rx=8))
    p.append(text(610, 80, "Знеструмлена мікросхема", size=13, bold=True, color=INK))
    p.append(text(610, 105, "Ключ OFF (V_SW = 0 В очікується)", size=10, color=MUTED))

    # Внутрішній вузол шини живлення чипа
    p.append(rect(500, 140, 220, 60, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    p.append(text(610, 165, "Внутрішня шина VDD чипа", size=11, bold=True, color=POS))
    p.append(text(610, 185, "Напруга піднімається до ~2.8 В!", size=10, bold=True, color=POS))

    # Верхній ESD-діод всередині чипа
    p.append(line(480, 250, 560, 250, color=POS, sw=2))
    p.append(line(560, 250, 560, 200, color=POS, sw=2))
    p.append('<polygon points="553,230 567,230 560,212" fill="#fdecea" stroke="%s" stroke-width="1.5"/>' % POS)
    p.append(line(553, 212, 567, 212, color=POS, sw=1.8))
    p.append(text(645, 230, "Верхній ESD-діод", size=10, color=POS, bold=True))

    # Лінія зв'язку (SDA / TX / SPI)
    p.append(line(200, 250, 480, 250, color=POS, sw=2.5))
    p.append(arrow(220, 250, 340, 250, color=POS, sw=2.5))
    p.append(arrow(340, 250, 460, 250, color=POS, sw=2.5))
    p.append(text(330, 240, "Паразитний струм фантомного живлення", size=11, bold=True, color=POS))

    # Наслідки внизу
    p.append(rect(20, 310, 720, 65, fill="#fdecea", stroke=POS, sw=1.5, rx=6))
    p.append(text(380, 332, "Наслідки: чип напівзависає в Brown-out стані, батарея розряджається в сні,", size=11, bold=True, color=POS))
    p.append(text(380, 354, "а шина I2C блокується через перекіс рівнів і незакриті ESD-переходи", size=11, color=INK))

    render(os.path.join(OUT, "phantom-power-path.svg"), W, H, *p,
           title="Шлях фантомного паразитного живлення через сигнальні лінії")


if __name__ == "__main__":
    fig_multi_rail_topology()
    fig_latch_up_mechanism()
    fig_pulse_current_response()
    fig_high_side_switch()
    fig_phantom_power_path()
    print("All figures generated successfully.")
