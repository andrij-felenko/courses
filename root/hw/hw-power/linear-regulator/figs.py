# -*- coding: utf-8 -*-
"""Фігури до теми «Лінійний регулятор напруги».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

SOFT_G = "#e8f6ed"   # м'яке зелене тло рамки-висновку
SOFT_R = "#fdecea"   # м'яке червоне тло
SOFT_B = "#eef3fd"   # м'яке синє тло
GRID   = "#d1d9e2"


def poly(points, color=LINE, sw=2.0, dash=None):
    """Ламана/крива як <path>."""
    d = "M %.2f %.2f " % points[0] + " ".join("L %.2f %.2f" % p for p in points[1:])
    ds = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f" '
            'stroke-linecap="round" stroke-linejoin="round"%s/>' % (d, color, sw, ds))


def gnd(x, y, color=MUTED):
    """Символ землі: вивід і три риски."""
    f = [line(x, y, x, y + 8, color=color, sw=1.6)]
    for k, half in enumerate((10, 6, 2)):
        f.append(line(x - half, y + 8 + k * 4, x + half, y + 8 + k * 4, color=color, sw=1.6))
    return "".join(f)


# ── 1. Концепція лінійного регулювання ────────────────────────────────────────
def fig_concept():
    W, H = 940, 460
    f = [text(W / 2, 28, "Принцип лінійного регулювання: керований опір у замкненій петлі",
              size=16, bold=True)]

    # Вхідна шина
    f.append(line(60, 100, 240, 100, color=POS, sw=2.5))
    f.append(text(50, 95, "Vвх", size=13, color=POS, bold=True, anchor="start"))
    f.append(text(50, 118, "(нестабільна)", size=10, color=MUTED, anchor="start"))

    # Прохідний елемент як змінний резистор
    f.append(rect(240, 70, 160, 60, fill=FILL, stroke=LINE, sw=2.0, rx=6))
    f.append(text(320, 95, "Прохідний елемент", size=12, bold=True))
    f.append(text(320, 115, "Rпрох (керований)", size=11, color=FIELD, bold=True))
    f.append(arrow(260, 125, 380, 75, color=FIELD, sw=2.0))

    # Вихідна шина
    f.append(line(400, 100, 720, 100, color=FIELD, sw=2.5))
    f.append(text(730, 95, "Vвих", size=13, color=FIELD, bold=True, anchor="start"))
    f.append(text(730, 118, "= const", size=11, color=FIELD, bold=True, anchor="start"))

    # Навантаження
    f.append(line(660, 100, 660, 150, color=FIELD, sw=2.0))
    f.append(rect(640, 150, 40, 70, fill=FILL, stroke=LINE, sw=1.8, rx=4))
    f.append(text(660, 190, "Rнав", size=11, bold=True))
    f.append(line(660, 220, 660, 260, color=MUTED, sw=2.0))
    f.append(gnd(660, 260))
    f.append(text(690, 185, "Інав", size=11, color=MUTED, anchor="start"))
    f.append(arrow(675, 130, 675, 145, color=MUTED, sw=1.6))

    # Дільник зворотного зв'язку
    f.append(line(500, 100, 500, 170, color=FIELD, sw=1.8))
    f.append(rect(485, 170, 30, 45, fill="#ffffff", stroke=MUTED, sw=1.4, rx=3))
    f.append(text(525, 196, "R1", size=11, color=MUTED, anchor="start"))
    f.append(line(500, 215, 500, 255, color=MUTED, sw=1.6))
    f.append(rect(485, 255, 30, 45, fill="#ffffff", stroke=MUTED, sw=1.4, rx=3))
    f.append(text(525, 281, "R2", size=11, color=MUTED, anchor="start"))
    f.append(line(500, 300, 500, 325, color=MUTED, sw=1.6))
    f.append(gnd(500, 325))

    # Підсилювач похибки
    # Вузол FB
    f.append(circle(500, 235, 3.5, fill=INK, stroke=INK))
    f.append(line(500, 235, 360, 235, color=MUTED, sw=1.6))
    f.append(text(430, 225, "Vзз (зворотний зв'язок)", size=10, color=MUTED))

    # Трикутник підсилювача похибки
    f.append(poly([(360, 195), (360, 275), (280, 235), (360, 195)], color=LINE, sw=2.0))
    f.append(rect(280, 195, 80, 80, fill="none", stroke="none")) # простір
    f.append(text(348, 215, "−", size=14, bold=True, color=NEG))
    f.append(text(348, 255, "+", size=14, bold=True, color=POS))
    f.append(text(330, 238, "EA", size=12, bold=True))

    # Опорна напруга
    f.append(line(360, 255, 410, 255, color=POS, sw=1.6))
    f.append(rect(410, 240, 60, 30, fill=SOFT_G, stroke=FIELD, sw=1.4, rx=4))
    f.append(text(440, 259, "Vоп", size=11, bold=True, color=FIELD))
    f.append(text(440, 282, "Bandgap", size=9, color=MUTED))

    # Вихід підсилювача керує прохідним елементом
    f.append(line(280, 235, 200, 235, color=FIELD, sw=1.8))
    f.append(line(200, 235, 200, 130, color=FIELD, sw=1.8))
    f.append(arrow(200, 130, 240, 115, color=FIELD, sw=1.8))
    f.append(text(190, 180, "Керування", size=11, color=FIELD, anchor="end", bold=True))
    f.append(text(190, 198, "Rпрох", size=11, color=FIELD, anchor="end", bold=True))

    # Пояснювальний висновок
    f.append(textbox(470, 395,
                     ["Vвих = Vвх − Інав · Rпрох = Vоп · (1 + R1/R2)",
                      "Підсилювач похибки безперервно змінює опір Rпрох, спалюючи зайву напругу в тепло.",
                      "Будь-який стрибок Vвх чи Інав миттєво компенсується зміною спаду на транзисторі."],
                     size=12, fill=SOFT_G, stroke=FIELD, min_w=820)[0])

    return render(os.path.join(IMG, "linear-reg-concept.svg"), W, H, *f)


# ── 2. Внутрішня архітектура мікросхеми регулятора ────────────────────────────
def fig_architecture():
    W, H = 1040, 580
    f = [text(W / 2, 28, "Внутрішня функціональна схема інтегрального лінійного регулятора",
              size=16, bold=True)]

    # Корпус мікросхеми (пунктир)
    f.append(rect(140, 60, 780, 420, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=12))
    f.append(text(160, 85, "КРИСТАЛ РЕГУЛЯТОРА", size=11, color=MUTED, anchor="start", bold=True))

    # Вхідний і вихідний виводи
    f.append(line(40, 130, 140, 130, color=POS, sw=3.0))
    f.append(text(50, 118, "IN (Vвх)", size=13, color=POS, bold=True, anchor="start"))
    f.append(circle(140, 130, 5, fill=POS, stroke=POS))

    f.append(line(920, 130, 1000, 130, color=FIELD, sw=3.0))
    f.append(text(990, 118, "OUT (Vвих)", size=13, color=FIELD, bold=True, anchor="end"))
    f.append(circle(920, 130, 5, fill=FIELD, stroke=FIELD))

    # Вивід GND
    f.append(line(520, 480, 520, 530, color=MUTED, sw=2.5))
    f.append(text(540, 515, "GND", size=12, color=MUTED, bold=True, anchor="start"))
    f.append(circle(520, 480, 5, fill=MUTED, stroke=MUTED))
    f.append(gnd(520, 530))

    # Силовий прохідний транзистор
    f.append(rect(650, 100, 130, 60, fill=FILL, stroke=LINE, sw=2.0, rx=6))
    f.append(text(715, 126, "Прохідний", size=12, bold=True))
    f.append(text(715, 145, "транзистор Q1", size=11, color=FIELD, bold=True))

    # Струмовий датчик Rsense
    f.append(rect(795, 115, 55, 30, fill="#ffffff", stroke=LINE, sw=1.5, rx=3))
    f.append(text(822, 134, "Rдатч", size=11, bold=True))
    f.append(line(140, 130, 650, 130, color=POS, sw=2.5))
    f.append(line(780, 130, 795, 130, color=FIELD, sw=2.5))
    f.append(line(850, 130, 920, 130, color=FIELD, sw=2.5))

    # Вузол захисту за струмом та Foldback
    f.append(rect(650, 200, 180, 65, fill=SOFT_R, stroke=POS, sw=1.5, rx=6))
    f.append(text(740, 224, "Захист від перевантаження", size=11, bold=True, color=POS))
    f.append(text(740, 245, "Current Limit / Foldback", size=10, color=MUTED))
    f.append(line(780, 130, 780, 200, color=POS, sw=1.4))
    f.append(line(865, 130, 865, 200, color=FIELD, sw=1.4))
    f.append(arrow(650, 232, 590, 185, color=POS, sw=1.6))

    # Тепловий захист (Thermal Shutdown)
    f.append(rect(650, 290, 180, 55, fill=SOFT_R, stroke=POS, sw=1.5, rx=6))
    f.append(text(740, 313, "Тепловий захист", size=11, bold=True, color=POS))
    f.append(text(740, 332, "Сенсор Tj (150°C)", size=10, color=MUTED))
    f.append(arrow(650, 317, 560, 210, color=POS, sw=1.6))

    # Драйвер бази / затвора
    f.append(rect(480, 140, 110, 60, fill=FILL, stroke=LINE, sw=1.8, rx=6))
    f.append(text(535, 166, "Драйвер /", size=11, bold=True))
    f.append(text(535, 184, "зсув рівня", size=11, color=MUTED))
    f.append(arrow(590, 160, 650, 135, color=FIELD, sw=1.8))

    # Підсилювач похибки
    f.append(poly([(420, 180), (420, 260), (340, 220), (420, 180)], color=LINE, sw=2.0))
    f.append(text(408, 202, "+", size=14, bold=True, color=POS))
    f.append(text(408, 242, "−", size=14, bold=True, color=NEG))
    f.append(text(385, 223, "EA", size=12, bold=True))
    f.append(arrow(340, 220, 480, 175, color=FIELD, sw=1.8))

    # Джерело опорної напруги (Bandgap Reference)
    f.append(rect(170, 170, 120, 60, fill=SOFT_G, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(230, 195, "Опора Bandgap", size=11, bold=True, color=FIELD))
    f.append(text(230, 215, "Vоп ≈ 1.25 В", size=10, bold=True))
    f.append(line(290, 200, 420, 200, color=FIELD, sw=1.6))

    # Дільник зворотного зв'язку
    f.append(line(890, 130, 890, 330, color=FIELD, sw=1.8))
    f.append(rect(875, 330, 30, 45, fill="#ffffff", stroke=MUTED, sw=1.4, rx=3))
    f.append(text(865, 355, "R1", size=11, color=MUTED, anchor="end"))
    f.append(line(890, 375, 890, 400, color=MUTED, sw=1.6))
    f.append(rect(875, 400, 30, 45, fill="#ffffff", stroke=MUTED, sw=1.4, rx=3))
    f.append(text(865, 425, "R2", size=11, color=MUTED, anchor="end"))
    f.append(line(890, 445, 890, 465, color=MUTED, sw=1.6))
    f.append(line(520, 465, 890, 465, color=MUTED, sw=1.6))

    # Зв'язок від дільника до інвертуючого входу
    f.append(circle(890, 387, 3.5, fill=INK, stroke=INK))
    f.append(line(890, 387, 470, 387, color=MUTED, sw=1.6))
    f.append(line(470, 387, 470, 242, color=MUTED, sw=1.6))
    f.append(line(470, 242, 430, 242, color=MUTED, sw=1.6))
    f.append(text(620, 377, "Vзз = Vвих · R2 / (R1 + R2)", size=10, color=MUTED))

    # Зовнішні конденсатори
    # Cin
    f.append(line(90, 130, 90, 180, color=POS, sw=1.8))
    f.append(line(75, 180, 105, 180, color=LINE, sw=2.2))
    f.append(line(75, 190, 105, 190, color=LINE, sw=2.2))
    f.append(line(90, 190, 90, 230, color=MUTED, sw=1.8))
    f.append(gnd(90, 230))
    f.append(text(55, 187, "Свх", size=11, bold=True, anchor="end"))

    # Cout
    f.append(line(950, 130, 950, 180, color=FIELD, sw=1.8))
    f.append(line(935, 180, 965, 180, color=LINE, sw=2.2))
    f.append(line(935, 190, 965, 190, color=LINE, sw=2.2))
    f.append(line(950, 190, 950, 210, color=MUTED, sw=1.8))
    f.append(rect(940, 210, 20, 25, fill=FILL, stroke=MUTED, sw=1.2, rx=2))
    f.append(text(970, 225, "ESR", size=9, color=MUTED, anchor="start"))
    f.append(line(950, 235, 950, 260, color=MUTED, sw=1.8))
    f.append(gnd(950, 260))
    f.append(text(985, 187, "Свих", size=11, bold=True, anchor="start"))

    # Підпис внизу
    f.append(textbox(W / 2, 530,
                     ["Повний замкнений контур: джерело опорної напруги задає еталон, підсилювач похибки",
                      "контролює вихідний дільник, а блоки обмеження струму й перегріву захищають кристал."],
                     size=12, fill=SOFT_B, stroke=NEG, min_w=880)[0])

    return render(os.path.join(IMG, "internal-architecture.svg"), W, H, *f)


# ── 3. Порівняння 4 топологій прохідного елемента ─────────────────────────────
def fig_topologies():
    W, H = 1080, 480
    f = [text(W / 2, 28, "Порівняння чотирьох базових топологій прохідного силового елемента",
              size=16, bold=True)]

    panels = [
        dict(px=150, title="NPN Дарлінгтон", chip="LM7805 / LM317",
             drop="Dropout: 1.5 … 2.2 В", dnote="Vdo ≈ 2·Vбе + Vнас",
             iq="Ізем: ~5 мА (сталий)",
             zout="Zвих: ~1/gm (дуже низький)",
             stab="Стійкий з будь-яким Свих",
             fill=FILL, s_col=MUTED),
        dict(px=410, title="Квазі-LDO (PNP+NPN)", chip="LM1117 / AMS1117",
             drop="Dropout: 0.9 … 1.2 В", dnote="Vdo ≈ Vнас(PNP) + Vбе(NPN)",
             iq="Ізем: ~5…10 мА",
             zout="Zвих: ~1/gm (низький)",
             stab="Вимагає танталовий/електроліт",
             fill=FILL, s_col=MUTED),
        dict(px=670, title="PNP LDO", chip="LM2940 / LP2950",
             drop="Dropout: 0.2 … 0.5 В", dnote="Vdo ≈ Vке(нас) (без підлоги)",
             iq="Ізем: росте як Інав/β",
             zout="Zвих: ro || Rнав (високий)",
             stab="Критичний до ESR Свих!",
             fill=SOFT_R, s_col=POS),
        dict(px=930, title="P-MOSFET LDO", chip="TPS799 / LP5907",
             drop="Dropout: 0.05 … 0.2 В", dnote="Vdo = Інав · Rds(on)",
             iq="Ізем: 0.5 … 50 мкА (сталий)",
             zout="Zвих: rds || Rнав (високий)",
             stab="Стабільний з керамікою (MLCC)",
             fill=SOFT_G, s_col=FIELD),
    ]

    for p in panels:
        px = p["px"]
        f.append(rect(px - 115, 60, 230, 390, fill=p["fill"], stroke=p["s_col"], sw=1.6, rx=8))
        f.append(text(px, 86, p["title"], size=13, bold=True))
        f.append(text(px, 106, p["chip"], size=11, color=MUTED))
        f.append(line(px - 95, 118, px + 95, 118, color=GRID, sw=1.2))

        # Спрощена схема прохідного елемента
        f.append(line(px - 80, 145, px + 80, 145, color=POS, sw=2.0))
        f.append(text(px - 85, 140, "Vвх", size=10, color=POS, anchor="end", bold=True))
        f.append(rect(px - 40, 160, 80, 45, fill="#ffffff", stroke=LINE, sw=1.4, rx=4))
        f.append(text(px, 187, p["title"].split()[0], size=11, bold=True))
        f.append(line(px, 145, px, 160, color=POS, sw=1.6))
        f.append(line(px, 205, px, 225, color=FIELD, sw=1.6))
        f.append(line(px - 80, 225, px + 80, 225, color=FIELD, sw=2.0))
        f.append(text(px + 85, 230, "Vвих", size=10, color=FIELD, anchor="start", bold=True))

        # Блоки параметрів
        f.append(fitbox(px - 100, 245, 200, 44, [p["drop"], p["dnote"]], size=11, bold=True, fill="#ffffff"))
        f.append(fitbox(px - 100, 298, 200, 32, [p["iq"]], size=11, fill="#ffffff"))
        f.append(fitbox(px - 100, 338, 200, 32, [p["zout"]], size=10, fill="#ffffff"))
        f.append(fitbox(px - 100, 378, 200, 48, [p["stab"]], size=11, bold=True, fill="#ffffff", stroke=p["s_col"]))

    return render(os.path.join(IMG, "topology-comparison.svg"), W, H, *f)


# ── 4. Захист Foldback ────────────────────────────────────────────────────────
def fig_foldback():
    W, H = 980, 460
    X0, X1 = 100.0, 560.0
    Y0, Y1 = 360.0, 90.0

    f = [text(W / 2, 28, "ВАХ виходу: стандартне обмеження струму проти схеми Foldback",
              size=16, bold=True)]

    # Осі
    f.append(line(X0, Y0, X1 + 20, Y0, color=LINE, sw=1.8))
    f.append(line(X0, Y0, X0, Y1 - 20, color=LINE, sw=1.8))
    f.append(arrow(X1, Y0, X1 + 20, Y0, color=LINE, sw=1.8))
    f.append(arrow(X0, Y1, X0, Y1 - 20, color=LINE, sw=1.8))
    f.append(text(X1 + 15, Y0 + 25, "Струм Івих", size=12, anchor="end", bold=True))
    f.append(text(X0 - 15, Y1 - 10, "Напруга Vвих", size=12, anchor="start", bold=True))

    Vnom_y = 140.0
    Imax_x = 480.0
    Isc_x  = 200.0

    # Рівні
    f.append(line(X0 - 5, Vnom_y, X0, Vnom_y, color=LINE, sw=1.4))
    f.append(text(X0 - 10, Vnom_y + 4, "Vном (5 В)", size=11, color=FIELD, anchor="end", bold=True))
    f.append(line(X0, Vnom_y, Imax_x, Vnom_y, color=FIELD, sw=3.0))

    # Стандартне струмове обмеження (Constant Current Limit)
    f.append(line(Imax_x, Vnom_y, Imax_x, Y0, color=POS, sw=2.5, dash="6 4"))
    f.append(circle(Imax_x, Y0, 5, fill=POS, stroke=POS))
    f.append(text(Imax_x, Y0 + 18, "Імакс = Ікз", size=11, color=POS, bold=True))
    f.append(text(Imax_x, Y0 + 34, "(1.5 А)", size=10, color=MUTED))

    # Схема Foldback
    f.append(line(Imax_x, Vnom_y, Isc_x, Y0, color=NEG, sw=3.0))
    f.append(circle(Imax_x, Vnom_y, 5, fill=NEG, stroke=NEG))
    f.append(circle(Isc_x, Y0, 5, fill=NEG, stroke=NEG))
    f.append(text(Imax_x + 8, Vnom_y - 12, "Іколіна (1.5 А)", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(Isc_x, Y0 + 18, "Ікз (0.3 А)", size=11, color=NEG, bold=True))
    f.append(text(Isc_x, Y0 + 34, "(Foldback)", size=10, color=MUTED))

    # Картки порівняння праворуч від графіка
    f.append(rect(610, 80, 340, 160, fill=SOFT_R, stroke=POS, sw=1.6, rx=8))
    f.append(text(780, 106, "1. Стандартне обмеження (червоний пунктир)", size=12, bold=True, color=POS))
    f.append(fitbox(625, 120, 310, 105,
                    ["• Струм КЗ дорівнює максимальному: Ікз = 1.5 А",
                     "• Розсіювання потужності в КЗ:",
                     "  Ркз = Vвх · Імакс = 15 В · 1.5 А = 22.5 Вт",
                     "• Наслідок: затяжне КЗ руйнує кристал"], size=11, fill="#ffffff"))

    f.append(rect(610, 260, 340, 170, fill=SOFT_B, stroke=NEG, sw=1.6, rx=8))
    f.append(text(780, 286, "2. Захист Foldback (синя лінія)", size=12, bold=True, color=NEG))
    f.append(fitbox(625, 300, 310, 115,
                    ["• Зі спадом Vвих струм зменшується до Ікз = 0.3 А",
                     "• Розсіювання потужності в КЗ:",
                     "  Ркз = Vвх · Ікз = 15 В · 0.3 А = 4.5 Вт",
                     "• Наслідок: потужність падає у 5 разів, кристал",
                     "  лишається в безпечній зоні (SOA)"], size=11, fill="#ffffff"))

    return render(os.path.join(IMG, "protection-foldback.svg"), W, H, *f)


# ── 5. PSRR по частоті ────────────────────────────────────────────────────────
def fig_psrr():
    W, H = 940, 460
    X0, X1 = 100.0, 840.0
    Y0, Y1 = 370.0, 90.0

    f = [text(W / 2, 28, "Коефіцієнт придушення пульсацій живлення (PSRR) по частоті",
              size=16, bold=True)]

    # Логарифмічна вісь частоти
    def FX(f_hz):
        # 10 Гц .. 10 МГц (6 декад)
        return X0 + (X1 - X0) * (math.log10(f_hz) - 1.0) / 6.0

    def FY(db):
        # 0 .. 90 дБ
        return Y0 + (Y1 - Y0) * (db / 90.0)

    # Сітка та позначки
    for db in (0, 20, 40, 60, 80):
        f.append(line(X0, FY(db), X1, FY(db), color=GRID, sw=1.0, dash="3 4"))
        f.append(text(X0 - 10, FY(db) + 4, "%d дБ" % db, size=10, color=MUTED, anchor="end"))

    freqs = [(10, "10 Гц"), (100, "100 Гц"), (1e3, "1 кГц"), (1e4, "10 кГц"),
             (1e5, "100 кГц"), (1e6, "1 МГц"), (1e7, "10 МГц")]
    for hz, lbl in freqs:
        f.append(line(FX(hz), Y0, FX(hz), Y1, color=GRID, sw=1.0, dash="3 4"))
        f.append(text(FX(hz), Y0 + 20, lbl, size=10, color=MUTED))

    f.append(line(X0, Y0, X1, Y0, color=LINE, sw=1.5))
    f.append(line(X0, Y0, X0, Y1, color=LINE, sw=1.5))
    f.append(text((X0 + X1) / 2, Y0 + 42, "Частота пульсацій f (логарифмічна шкала)", size=11, color=MUTED))
    f.append(text(X0 - 15, Y1 - 15, "PSRR = 20·lg(ΔVвх/ΔVвих), дБ", size=11, bold=True, anchor="start"))

    # Крива PSRR
    # Зона 1: 10 Гц..500 Гц: 80 дБ
    # Зона 2: 500 Гц..200 кГц: спад -20 дБ/дек
    # Зона 3: 200 кГц..1 МГц: мінімум (провал до 25 дБ)
    # Зона 4: 1 МГц..5 МГц: підйом за рахунок Cout (до 45 дБ)
    # Зона 5: >5 МГц: спад через ESL
    pts = []
    for k in range(121):
        log_f = 1.0 + 6.0 * k / 120.0
        f_val = 10.0 ** log_f
        if f_val < 500:
            db = 80.0 - 2.0 * (f_val / 500.0)
        elif f_val < 3e5:
            db = 78.0 - 20.0 * (math.log10(f_val) - math.log10(500))
        elif f_val < 1.2e6:
            db = 24.0 + 4.0 * math.sin((math.log10(f_val) - math.log10(3e5)) * math.pi)
        elif f_val < 5e6:
            db = 26.0 + 22.0 * (math.log10(f_val) - math.log10(1.2e6))
        else:
            db = 48.0 - 35.0 * (math.log10(f_val) - math.log10(5e6))
        pts.append((FX(f_val), FY(max(5.0, db))))

    f.append(poly(pts, color=FIELD, sw=3.0))

    # Анотації зон
    f.append(textbox(FX(50), FY(65),
                     ["Зона 1 (НЧ):", "Високе підсилення", "підсилювача похибки", "PSRR > 75 дБ"],
                     size=10, fill=SOFT_G, stroke=FIELD)[0])

    f.append(textbox(FX(2e4), FY(58),
                     ["Зона 2:", "Спад підсилення петлі", "(−20 дБ/декада)"],
                     size=10, fill=FILL, stroke=MUTED)[0])

    f.append(textbox(FX(6e5), FY(15),
                     ["Зона 3: Провал PSRR", "на частоті зрізу петлі fugf"],
                     size=10, fill=SOFT_R, stroke=POS)[0])

    f.append(textbox(FX(4e6), FY(58),
                     ["Зона 4:", "Працює фільтрація", "ємністю Свих"],
                     size=10, fill=SOFT_B, stroke=NEG)[0])

    return render(os.path.join(IMG, "psrr-frequency-curve.svg"), W, H, *f)


# ── 6. Тунель стабільності ESR ────────────────────────────────────────────────
def fig_esr_tunnel():
    W, H = 960, 480
    X0, X1 = 110.0, 850.0
    Y0, Y1 = 390.0, 80.0

    f = [text(W / 2, 28, "Тунель стабільності ESR: область стійкої роботи LDO-регулятора",
              size=16, bold=True)]

    # Логарифмічна вісь струму (1 мА .. 1 А, 3 декади)
    def IX(i_a):
        return X0 + (X1 - X0) * (math.log10(i_a) + 3.0) / 3.0

    # Логарифмічна вісь ESR (1 мОм .. 50 Ом, ~4.7 декад)
    def EY(esr_ohm):
        # 1e-3 .. 50 Ом
        return Y0 + (Y1 - Y0) * (math.log10(esr_ohm) + 3.0) / 4.7

    # Осі
    f.append(line(X0, Y0, X1, Y0, color=LINE, sw=1.6))
    f.append(line(X0, Y0, X0, Y1, color=LINE, sw=1.6))
    f.append(text((X0 + X1) / 2, Y0 + 38, "Струм навантаження Івих (логарифмічна шкала)", size=11, color=MUTED))
    f.append(text(X0 - 15, Y1 - 15, "Еквівалентний послідовний опір (ESR) Свих, Ом", size=11, bold=True, anchor="start"))

    for i_a, lbl in ((1e-3, "1 мА"), (1e-2, "10 мА"), (1e-1, "100 мА"), (1.0, "1 А")):
        f.append(line(IX(i_a), Y0, IX(i_a), Y0 + 5, color=LINE, sw=1.2))
        f.append(text(IX(i_a), Y0 + 20, lbl, size=10, color=MUTED))

    for esr, lbl in ((1e-3, "1 мОм"), (1e-2, "10 мОм"), (1e-1, "0.1 Ом"), (1.0, "1 Ом"), (10.0, "10 Ом")):
        f.append(line(X0 - 5, EY(esr), X0, EY(esr), color=LINE, sw=1.2))
        f.append(text(X0 - 10, EY(esr) + 4, lbl, size=10, color=MUTED, anchor="end"))

    # Полігон тунелю стабільності
    # Верхня межа: ~5 Ом на 1 мА .. 1.5 Ом на 1 А
    # Нижня межа: ~0.05 Ом на 1 мА .. 0.15 Ом на 1 А
    top_pts = [(IX(10.0 ** (-3.0 + 3.0 * k / 30.0)),
                EY(4.5 * (10.0 ** (-3.0 + 3.0 * k / 30.0)) ** (-0.15))) for k in range(31)]
    bot_pts = [(IX(10.0 ** (-3.0 + 3.0 * k / 30.0)),
                EY(0.04 * (10.0 ** (-3.0 + 3.0 * k / 30.0)) ** (0.22))) for k in range(31)]

    # Малюємо стабільну зону
    poly_d = "M %.2f %.2f " % top_pts[0]
    poly_d += " ".join("L %.2f %.2f" % p for p in top_pts[1:])
    poly_d += " " + " ".join("L %.2f %.2f" % p for p in reversed(bot_pts)) + " Z"
    f.append('<path d="%s" fill="%s" stroke="%s" stroke-width="1.8"/>' % (poly_d, SOFT_G, FIELD))

    # Межі
    f.append(poly(top_pts, color=POS, sw=2.0, dash="5 4"))
    f.append(poly(bot_pts, color=POS, sw=2.0, dash="5 4"))

    # Написи в зонах
    f.append(textbox(480, 240,
                     ["ТУНЕЛЬ СТАБІЛЬНОСТІ",
                      "Запас фази > 45°",
                      "Нуль ESR компенсує вихідний полюс:",
                      "z_esr = 1 / (2·π·ESR·Свих)"],
                     size=11, bold=True, fill="#ffffff", stroke=FIELD, min_w=240)[0])

    f.append(textbox(480, 115,
                     ["НЕСТІЙКО: Завеликий ESR", "Надлишкові пульсації та фазовий зсув вторинного полюса"],
                     size=10, fill=SOFT_R, stroke=POS)[0])

    f.append(textbox(480, 360,
                     ["САМОЗБУДЖЕННЯ: Занизький ESR (чиста кераміка MLCC < 10 мОм)",
                      "Нуль z_esr зміщується вище fugf → зрив фази в петлі → генерація!"],
                     size=10, fill=SOFT_R, stroke=POS)[0])

    # Точки реальних компонентів
    f.append(circle(IX(0.1), EY(0.8), 6, fill=FIELD, stroke=INK))
    f.append(text(IX(0.1) + 12, EY(0.8) + 4, "Танталовий (ESR ≈ 0.8 Ом) — СТІЙКИЙ", size=10, color=FIELD, anchor="start", bold=True))

    f.append(circle(IX(0.1), EY(0.008), 6, fill=POS, stroke=INK))
    f.append(text(IX(0.1) + 12, EY(0.008) + 4, "Кераміка MLCC (ESR ≈ 8 мОм) — ЗБУДЖУЄТЬСЯ", size=10, color=POS, anchor="start", bold=True))

    return render(os.path.join(IMG, "esr-stability-tunnel.svg"), W, H, *f)


if __name__ == "__main__":
    print("Генерація фігур...")
    fig_concept()
    fig_architecture()
    fig_topologies()
    fig_foldback()
    fig_psrr()
    fig_esr_tunnel()
    print("Готово. Згенеровано 6 SVG у ./img/")
