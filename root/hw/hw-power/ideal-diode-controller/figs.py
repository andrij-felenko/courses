# -*- coding: utf-8 -*-
"""Фігури до статті «Контролер ідеального діода»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def poly(points, color=LINE, sw=2.5, fill="none", dash=None):
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in points)
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s '
            'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, fill, color, sw, d))


def band(x, y, w, h, fill):
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (x, y, w, h, fill)


def gnd(x, y, color=INK):
    """Знак землі: три горизонтальні риски, що коротшають."""
    return (line(x - 14, y, x + 14, y, color=color, sw=2.5) +
            line(x - 9, y + 6, x + 9, y + 6, color=color, sw=2.5) +
            line(x - 4, y + 12, x + 4, y + 12, color=color, sw=2.5))


def cap_plates(x, y, half=15, gap=10, color=INK):
    """Дві пластини конденсатора на вертикальному проводі (центр y)."""
    return (line(x - half, y - gap / 2, x + half, y - gap / 2, color=color, sw=3) +
            line(x - half, y + gap / 2, x + half, y + gap / 2, color=color, sw=3))


def diode_right(cx, cy, color=INK):
    """Гліф діода, що пропускає вправо (трикутник вістрям управо + смужка)."""
    tri = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
           % (cx - 13, cy - 11, cx - 13, cy + 11, cx + 8, cy, color))
    return tri + line(cx + 8, cy - 11, cx + 8, cy + 11, color=color, sw=3)


def diode_left(cx, cy, color=INK):
    """Гліф діода, що пропускає вліво."""
    tri = ('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s"/>'
           % (cx + 13, cy - 11, cx + 13, cy + 11, cx - 8, cy, color))
    return tri + line(cx - 8, cy - 11, cx - 8, cy + 11, color=color, sw=3)


# ── Фігура 1: замкнена петля навколо MOSFET ────────────────────────────────
def fig_loop():
    W, H = 800, 460
    f = []
    # силовий тракт (верхній рейл)
    ry = 96
    f.append(circle(60, ry, 7, fill=POS, stroke=POS))
    f.append(text(60, 74, "Vвх +", size=14, color=POS, bold=True))
    f.append(line(67, ry, 255, ry, color=INK, sw=2.5))
    f.append(arrow(150, ry, 185, ry, color=INK, sw=2.5))
    f.append(text(150, 80, "струм →", size=13, color=MUTED))
    # MOSFET як блок
    f.append(rect(255, 62, 150, 68, fill=FILL, stroke=INK, sw=2))
    f.append(mtext(330, 90, ["MOSFET", "Rds(on)"], size=15, bold=True))
    f.append(text(258, 112, "S", size=12, color=MUTED, anchor="start"))
    f.append(text(402, 112, "D", size=12, color=MUTED, anchor="end"))
    # вихід
    f.append(line(405, ry, 700, ry, color=INK, sw=2.5))
    f.append(circle(710, ry, 7, fill=INK, stroke=INK))
    f.append(mtext(710, 74, ["Vвих →", "навантаж."], size=12, color=MUTED))
    # корпус контролера
    f.append(rect(110, 220, 580, 190, fill="#eef4fb", stroke=NEG, sw=2, rx=12))
    f.append(text(400, 246, "Контролер ідеального діода", size=16, color=NEG, bold=True))
    # три підблоки
    f.append(fitbox(140, 272, 158, 116, "Підсилювач\nпохибки:\nтримає\n~20–30 мВ",
                    size=14, fill=BG, stroke=FIELD, sw=2, bold=True, color=INK))
    f.append(fitbox(322, 272, 158, 116, "Компаратор\nзвороту:\nзакриває затвор\nза ~1 мкс",
                    size=14, fill=BG, stroke=POS, sw=2, bold=True, color=INK))
    f.append(fitbox(504, 272, 158, 116, "Зарядний\nнасос:\nVзатв > Vвх\n(N-канал угорі)",
                    size=14, fill=BG, stroke=NEG, sw=2, bold=True, color=INK))
    # сенсорні лінії VS / VD (відведення вбік від країв блоку)
    f.append(poly([(255, ry), (232, ry), (232, 220)], color=FIELD, sw=2))
    f.append(text(224, 168, "VS", size=13, color=FIELD, anchor="end", bold=True))
    f.append(poly([(405, ry), (428, ry), (428, 220)], color=FIELD, sw=2))
    f.append(text(436, 168, "VD", size=13, color=FIELD, anchor="start", bold=True))
    # драйв затвора
    f.append(line(330, 220, 330, 132, color=NEG, sw=2.5))
    f.append(arrow(330, 175, 330, 138, color=NEG, sw=2.5))
    f.append(text(340, 165, "GATE", size=13, color=NEG, anchor="start", bold=True))
    # підпис-механізм
    f.append(text(400, 438, "Vds = I·Rds(on): знак і величина падіння = напрям і сила струму",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'loop-block.svg'), W, H, *f,
           title="Контролер як швидка петля навколо самого MOSFET")


# ── Фігура 2: V-I характеристика (плато + ом + стіна) ───────────────────────
def fig_vi():
    W, H = 780, 470
    f = []
    x0, xI0, xR = 120, 300, 705      # ліва межа, точка I=0, права межа
    yb, ytop = 385, 90               # baseline (Vds=0), стеля
    xk, yk = 480, 338                # коліно
    ytarget = 338                    # рівень регулювання ~25 мВ
    # тло зворотної зони
    f.append(band(x0, 100, xI0 - x0, yb - 100, "#fdecea"))
    # осі
    f.append(line(x0, yb, xR, yb, color=INK, sw=2))
    f.append(arrow(xR - 30, yb, xR, yb, color=INK, sw=2))
    f.append(text(xR - 6, yb + 24, "струм I →", size=13, color=INK, anchor="end"))
    f.append(line(xI0, yb, xI0, ytop, color=INK, sw=2))
    f.append(arrow(xI0, ytop + 24, xI0, ytop, color=INK, sw=2))
    f.append(text(xI0, ytop - 10, "падіння Vds ↑", size=13, color=INK))
    # пунктир «MOSFET повністю відкритий» (I·Rds від нуля)
    f.append(poly([(xI0, yb), (xk, yk)], color=MUTED, sw=2, dash="6,5"))
    f.append(text(360, 434, "пунктир — MOSFET повністю відкритий", size=12, color=MUTED))
    # плато регулювання
    f.append(poly([(xI0, ytarget), (xk, ytarget)], color=FIELD, sw=4))
    f.append(text(304, ytarget - 16, "петля тримає ~25 мВ", size=13, color=FIELD, anchor="start", bold=True))
    # омічна гілка
    f.append(poly([(xk, yk), (690, 120)], color=INK, sw=4))
    f.append(text(628, 168, "I·Rds(on)", size=14, color=INK, bold=True, anchor="start"))
    # коліно
    f.append(circle(xk, yk, 5, fill=BG, stroke=INK, sw=2))
    f.append(line(xk, yk, xk, yb, color=MUTED, sw=1.2, dash="4,4"))
    f.append(text(xk, yb + 22, "коліно: I·Rds = ціль", size=12, color=MUTED))
    # стіна зворотного струму
    f.append(line(xI0, yb, xI0, 112, color=POS, sw=4))
    f.append(mtext(210, 210, ["зворотний струм", "заблоковано:", "затвор закрито"],
                   size=13, color=POS, bold=True))
    render(os.path.join(IMG, 'vi-characteristic.svg'), W, H, *f,
           title="Що тримає контролер: крихітне падіння вперед, стіна на зворот")


# ── Фігура 3: швидкість відсічення зворотного струму ────────────────────────
def fig_timing():
    W, H = 780, 400
    f = []
    xL, xR, t0 = 110, 705, 300
    # верхня панель — напруга джерела
    f.append(text(xL, 60, "напруга сильнішого джерела", size=13, color=INK, anchor="start"))
    f.append(poly([(xL, 96), (t0, 96), (360, 150), (xR, 150)], color=INK, sw=2.5))
    # t0
    f.append(line(t0, 52, t0, 366, color=MUTED, sw=1.5, dash="5,5"))
    f.append(text(t0, 46, "джерело впало", size=13, color=MUTED))
    # нижня панель — зворотний струм
    yb = 250
    f.append(line(xL, yb, xR, yb, color=INK, sw=1.6))
    f.append(mtext(96, yb - 6, ["зворотний", "струм ↓"], size=12, color=MUTED, anchor="end"))
    # пасивна — велика повільна яма (з заливкою площі = перекачаний заряд)
    passive = [(t0, yb), (316, 322), (338, 306), (392, 282), (470, 262), (560, 252), (660, yb)]
    f.append(poly(passive + [(t0, yb)], color=POS, sw=2.5, fill="#fdecea"))
    f.append(text(470, 344, "пасивна RC-схема: повільний розряд затвора", size=13, color=POS, anchor="middle"))
    f.append(text(566, 240, "~30 мкс", size=12, color=POS, anchor="start"))
    # активна — вузький швидкий зріз
    active = [(t0, yb), (308, 274), (317, 252), (xR, yb)]
    f.append(poly(active, color=FIELD, sw=3))
    f.append(text(330, 224, "з контролером: зріз за ~1 мкс", size=13, color=FIELD, anchor="start", bold=True))
    f.append(text(322, 268, "~1 мкс", size=12, color=FIELD, anchor="start"))
    # вісь часу
    f.append(arrow(xR - 28, 366, xR, 366, color=INK, sw=1.6))
    f.append(text(xR - 4, 384, "час →", size=13, color=INK, anchor="end"))
    render(os.path.join(IMG, 'reverse-timing.svg'), W, H, *f,
           title="Пасивна схема пропускає довгий зворотний імпульс — контролер зрізає його")


# ── Фігура 4 (до вставки hist): три епохи однобічного вентиля ───────────────
def fig_eras():
    W, H = 940, 620
    CW = 270
    y0, hh, rh, gap = 76, 56, 100, 6
    cards = [
        (30, FIELD, "#f2f8f4", "Реле зворотного струму", "з 1910-х", [
            ("як визначає напрям", ["струмова обмотка:", "зворотний струм гасить", "поле — контакти рвуться"]),
            ("падіння при 20 А", ["≈ 20 мВ на контактах", "P ≈ 0.4 Вт"]),
            ("час реакції", ["одиниці мілісекунд"]),
            ("слабке місце", ["дуга й знос контактів,", "потребує регулювання"]),
        ]),
        (335, POS, "#fdf3f2", "Кремнієвий і Шотткі діод", "з 1960-х", [
            ("як визначає напрям", ["ніяк не «визначає» —", "однобічність фізична,", "вбудована в перехід"]),
            ("падіння при 20 А", ["≈ 0.45 В (Шотткі)", "P ≈ 9 Вт"]),
            ("час реакції", ["миттєво, сам перехід"]),
            ("слабке місце", ["постійний нагрів;", "пробій не видно ззовні"]),
        ]),
        (640, NEG, "#eef3fd", "MOSFET + контролер", "з 2000-х", [
            ("як визначає напрям", ["читає знак Vds на", "власному ключі —", "одиниці мілівольтів"]),
            ("падіння при 20 А", ["≈ 40 мВ (2 мОм)", "P ≈ 0.8 Вт"]),
            ("час реакції", ["0.1–1 мікросекунда"]),
            ("слабке місце", ["ціна й складність;", "відмова накоротко —", "треба самодіагностика"]),
        ]),
    ]
    f = []
    for cx0, accent, tint, name, years, rows in cards:
        ch = hh + len(rows) * rh + (len(rows) - 1) * gap + 12
        f.append(rect(cx0, y0, CW, ch, fill=BG, stroke=accent, sw=2, rx=12))
        f.append(rect(cx0, y0, CW, hh, fill=tint, stroke=accent, sw=2, rx=12))
        cxc = cx0 + CW / 2
        f.append(text(cxc, y0 + 25, name, size=15, color=accent, bold=True))
        f.append(text(cxc, y0 + 45, years, size=12, color=MUTED))
        ry = y0 + hh + 6
        for label, lines in rows:
            f.append(rect(cx0 + 10, ry, CW - 20, rh, fill=tint, stroke="none", sw=0, rx=8))
            f.append(text(cx0 + 22, ry + 21, label, size=12, color=MUTED, anchor="start"))
            n = len(lines)
            base = ry + 32 + (rh - 42) / 2 - (n - 1) * 13 * 1.3 / 2 + 13 * 0.35
            f.append(mtext(cxc, base, lines, size=13, color=INK))
            ry += rh + gap
    f.append(text(470, 592,
                  "Активне вимірювання напряму → пасивний перехід → знову активне вимірювання, "
                  "тільки за мікросекунди", size=13, color=MUTED))
    render(os.path.join(IMG, 'three-eras.svg'), W, H, *f,
           title="Однобічний вентиль резервованого живлення: реле, діод, керований ключ")


# ── Фігура 5 (до вставки comp): обв'язка одного тракту ─────────────────────
def fig_hookup_single():
    W, H = 920, 500
    ry = 110
    f = []
    # джерело + його земля
    f.append(circle(70, ry, 7, fill=POS, stroke=POS))
    f.append(text(70, 78, "Vвх", size=14, color=POS, bold=True))
    f.append(line(70, 118, 70, 172, color=INK, sw=2))
    f.append(gnd(70, 172))
    # верхній рейл до ключа
    f.append(line(77, ry, 300, ry, color=INK, sw=2.5))
    f.append(arrow(200, ry, 246, ry, color=INK, sw=2.5))
    f.append(text(206, 92, "струм", size=13, color=MUTED))
    # силовий ключ
    f.append(rect(300, 78, 130, 64, fill=FILL, stroke=INK, sw=2))
    f.append(text(365, 106, "MOSFET", size=15, bold=True))
    f.append(text(307, 132, "S", size=12, color=MUTED, anchor="start"))
    f.append(text(423, 132, "D", size=12, color=MUTED, anchor="end"))
    # рейл після ключа + навантаження
    f.append(line(430, ry, 745, ry, color=INK, sw=2.5))
    f.append(fitbox(745, 80, 130, 62, "навантаження", size=14, fill=FILL, stroke=INK, sw=2))
    f.append(line(810, 142, 810, 190, color=INK, sw=2))
    f.append(gnd(810, 190))
    # корпус контролера
    f.append(rect(180, 250, 460, 150, fill="#eef4fb", stroke=NEG, sw=2, rx=12))
    f.append(text(410, 288, "контролер ідеального діода", size=16, color=NEG, bold=True))
    f.append(text(410, 332, "назви ніжок у різних виробників свої — набір той самий",
                  size=12, color=MUTED))
    # сенсорна пара IN / OUT — просто до площадок ключа
    f.append(circle(290, ry, 4, fill=INK, stroke=INK))
    f.append(line(290, ry, 290, 250, color=FIELD, sw=2))
    f.append(text(282, 240, "IN", size=13, color=FIELD, anchor="end", bold=True))
    f.append(circle(440, ry, 4, fill=INK, stroke=INK))
    f.append(line(440, ry, 440, 250, color=FIELD, sw=2))
    f.append(text(448, 240, "OUT", size=13, color=FIELD, anchor="start", bold=True))
    # затвор
    f.append(line(365, 250, 365, 192, color=NEG, sw=2.5))
    f.append(arrow(365, 192, 365, 146, color=NEG, sw=2.5))
    f.append(text(357, 240, "GATE", size=13, color=NEG, anchor="end", bold=True))
    # живлення чипа — зі спільної шини, а не з власного входу
    f.append(circle(560, ry, 4, fill=INK, stroke=INK))
    f.append(line(560, ry, 560, 250, color=NEG, sw=2))
    f.append(text(568, 240, "VDD", size=13, color=NEG, anchor="start", bold=True))
    # земля чипа
    f.append(line(300, 400, 300, 442, color=INK, sw=2))
    f.append(gnd(300, 442))
    f.append(text(292, 430, "GND", size=13, anchor="end", bold=True))
    # бак зарядного насоса
    f.append(circle(120, ry, 4, fill=INK, stroke=INK))
    f.append(line(120, ry, 120, 205, color=INK, sw=2))
    f.append(cap_plates(120, 210))
    f.append(line(120, 215, 120, 300, color=INK, sw=2))
    f.append(line(120, 300, 180, 300, color=INK, sw=2))
    f.append(text(142, 214, "Cнас ≈ 10·Ciss", size=12, color=MUTED, anchor="start"))
    f.append(text(188, 294, "CPO", size=13, anchor="start", bold=True))
    # дозвіл і доповідь
    f.append(arrow(740, 320, 644, 320, color=INK, sw=2))
    f.append(text(632, 325, "EN", size=13, anchor="end", bold=True))
    f.append(text(748, 325, "дозвіл від логіки", size=12, color=MUTED, anchor="start"))
    f.append(line(640, 370, 740, 370, color=INK, sw=2))
    f.append(text(632, 375, "STAT", size=13, anchor="end", bold=True))
    f.append(mtext(748, 366, ["відкритий стік:", "«цей тракт годує»"],
                   size=12, color=MUTED, anchor="start"))
    f.append(text(460, 478, "IN і OUT — до самих площадок ключа; VDD — зі спільної шини",
                  size=13, color=MUTED))
    render(os.path.join(IMG, 'idc-hookup-single.svg'), W, H, *f,
           title="Один тракт: що навісити навколо контролера")


# ── Фігура 6 (до вставки comp): пара для об'єднання джерел ──────────────────
def fig_oring_pair():
    W, H = 920, 560
    f = []
    for tag, ry, by, name in (("A", 100, 155, "контролер A"), ("B", 460, 315, "контролер B")):
        up = (tag == "A")                      # A: рейл угорі, коробка внизу
        sy = 70 if up else 430                 # блок джерела
        f.append(fitbox(30, sy, 130, 60,
                        ("Джерело A\n12.0 В" if up else "Джерело B\n11.6 В"),
                        size=13, fill=FILL, stroke=INK, sw=2))
        f.append(line(160, ry, 260, ry, color=INK, sw=2.5))
        # силовий ключ
        f.append(rect(260, ry - 32, 120, 64, fill=FILL, stroke=INK, sw=2))
        f.append(text(320, ry - 5, "MOSFET " + tag, size=14, bold=True))
        f.append(text(267, ry + 24, "S", size=12, color=MUTED, anchor="start"))
        f.append(text(373, ry + 24, "D", size=12, color=MUTED, anchor="end"))
        f.append(line(380, ry, 680, ry, color=INK, sw=2.5))
        # корпус контролера
        f.append(rect(190, by, 370, 90, fill="#eef4fb", stroke=NEG, sw=2, rx=10))
        f.append(text(375, by + 51, name, size=15, color=NEG, bold=True))
        edge = by if up else by + 90           # той бік коробки, що дивиться на рейл
        # сенсорна пара
        f.append(circle(248, ry, 4, fill=INK, stroke=INK))
        f.append(line(248, ry, 248, edge, color=FIELD, sw=2))
        f.append(text(240, (145 if up else 428), "IN", size=13, color=FIELD,
                      anchor="end", bold=True))
        f.append(circle(392, ry, 4, fill=INK, stroke=INK))
        f.append(line(392, ry, 392, edge, color=FIELD, sw=2))
        f.append(text(400, (145 if up else 428), "OUT", size=13, color=FIELD,
                      anchor="start", bold=True))
        # затвор
        gtip = (ry + 36) if up else (ry - 36)   # вістря — біля ближчого краю ключа
        f.append(arrow(320, edge, 320, gtip, color=NEG, sw=2.5))
        f.append(text(328, (150 if up else 418), "GATE", size=13, color=NEG,
                      anchor="start", bold=True))
        # живлення чипа — зі спільної шини після ключа
        vy = by + 35 if up else by + 55
        f.append(line(560, vy, 600, vy, color=NEG, sw=2))
        f.append(circle(600, ry, 4, fill=INK, stroke=INK))
        f.append(line(600, vy, 600, ry, color=NEG, sw=2))
        f.append(text(608, (150 if up else 412), "VDD", size=13, color=NEG,
                      anchor="start", bold=True))
    # спільний вузол і навантаження
    f.append(circle(680, 100, 4, fill=INK, stroke=INK))
    f.append(circle(680, 460, 4, fill=INK, stroke=INK))
    f.append(line(680, 100, 680, 460, color=INK, sw=2.5))
    f.append(circle(680, 280, 4, fill=INK, stroke=INK))
    f.append(line(680, 280, 760, 280, color=INK, sw=2.5))
    f.append(fitbox(760, 245, 130, 70, "спільна шина\nз навантаженням",
                    size=13, fill=FILL, stroke=INK, sw=2))
    # підписи-коментарі
    f.append(text(500, 86, "A вище → A годує шину", size=13, color=FIELD, bold=True))
    f.append(text(500, 496, "B нижче на 0.4 В → закритий", size=13, color=POS, bold=True))
    f.append(text(375, 285, "вище з двох тримає шину — нижче автоматично відсічене",
                 size=13, color=MUTED))
    f.append(mtext(790, 372, ["VDD обох — зі спільної", "шини, а не з власного",
                              "входу: інакше контролер", "гасне саме тоді, коли", "мусив би спрацювати"],
                   size=12, color=NEG))
    render(os.path.join(IMG, 'idc-oring-pair.svg'), W, H, *f,
           title="Пара трактів на одну шину: як живиться сам контролер")


# ── Фігура 7 (до вставки comp): орієнтація ключа ────────────────────────────
def _orient_panel(x0, accent, title, cap_lines, forward):
    """Одна панель: рейл, ключ і його body-діод у заданому напрямку."""
    f = []
    f.append(rect(x0, 60, 380, 250, fill=BG, stroke=accent, sw=2, rx=10))
    cx = x0 + 190
    f.append(text(cx, 92, title, size=15, color=accent, bold=True))
    ry = 148
    f.append(line(x0 + 30, ry, x0 + 140, ry, color=INK, sw=2.5))
    f.append(line(x0 + 240, ry, x0 + 360, ry, color=INK, sw=2.5))
    f.append(text(x0 + 32, 132, "вхід", size=12, color=MUTED, anchor="start"))
    f.append(text(x0 + 358, 132, "вихід", size=12, color=MUTED, anchor="end"))
    f.append(rect(x0 + 140, 120, 100, 56, fill=FILL, stroke=INK, sw=2))
    f.append(text(cx, 142, "ключ", size=13, bold=True))
    f.append(text(x0 + 147, 168, ("S" if forward else "D"), size=12, color=MUTED, anchor="start"))
    f.append(text(x0 + 233, 168, ("D" if forward else "S"), size=12, color=MUTED, anchor="end"))
    # паралельна вітка body-діода
    f.append(circle(x0 + 130, ry, 4, fill=INK, stroke=INK))
    f.append(circle(x0 + 250, ry, 4, fill=INK, stroke=INK))
    f.append(line(x0 + 130, ry, x0 + 130, 215, color=accent, sw=2))
    f.append(line(x0 + 250, ry, x0 + 250, 215, color=accent, sw=2))
    f.append(line(x0 + 130, 215, x0 + 177, 215, color=accent, sw=2))
    f.append(line(x0 + 203, 215, x0 + 250, 215, color=accent, sw=2))
    f.append(diode_right(cx, 215, accent) if forward else diode_left(cx, 215, accent))
    f.append(mtext(cx, 252, cap_lines, size=12, color=accent))
    return f


def fig_fet_orientation():
    W, H = 880, 360
    f = []
    f.extend(_orient_panel(40, FIELD, "правильно",
                           ["витік — до входу, стік — до виходу;",
                            "body-діод дивиться вперед, тож до",
                            "відкриття каналу струм іде крізь нього"], True))
    f.extend(_orient_panel(460, POS, "навпаки — катастрофа",
                           ["витік — до виходу, стік — до входу;",
                            "body-діод дивиться назад: зворотний",
                            "струм тече завжди, хоч би що робив чип"], False))
    render(os.path.join(IMG, 'idc-fet-orientation.svg'), W, H, *f,
           title="Орієнтація ключа: помилка, якої не видно на платі")


if __name__ == '__main__':
    fig_loop()
    fig_vi()
    fig_timing()
    fig_eras()
    fig_hookup_single()
    fig_oring_pair()
    fig_fet_orientation()
    print("OK: figures written to", IMG)
