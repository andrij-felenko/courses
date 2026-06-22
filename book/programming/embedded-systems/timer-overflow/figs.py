# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Період і переповнення (авто-перезавантаження)».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── overflow: лічильник доходить до максимуму й перекидається в нуль ──────────
# Ідея: пилкоподібний графік — значення росте до МАКС, на наступний тік падає в 0.
def fig_overflow():
    W, H = 940, 380
    P = []
    P.append(text(W / 2, 30, "Переповнення: лічильник дійшов до максимуму й обнулився",
                  size=17, bold=True))

    ox, oy = 100, 280            # початок осей
    top = 110                    # рівень «макс»
    right = 870
    P.append(arrow(ox, oy, ox, 90, color=INK, sw=1.8))      # вісь значення
    P.append(arrow(ox, oy, right, oy, color=INK, sw=1.8))   # вісь часу
    P.append(text(ox - 12, 100, "значення", size=11, color=INK, bold=True, anchor="end"))
    P.append(text(right, oy + 22, "час", size=11, color=INK, anchor="end"))

    # лінія «макс»
    P.append(line(ox, top, right, top, color=MUTED, sw=1.2, dash="4,3"))
    P.append(text(ox - 12, top + 4, "макс", size=11, color=POS, bold=True, anchor="end"))
    P.append(text(ox - 12, top - 12, "(2ᴺ − 1)", size=10, color=MUTED, anchor="end"))

    # три зубці пилки
    xs = [ox, 300, 300, 540, 540, 780, 780]
    ys = [oy, top, oy, top, oy, top, oy]
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in zip(xs, ys))
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, FIELD))

    # позначки переповнення на верхівках
    for vx in (300, 540, 780):
        P.append(circle(vx, top, 5, fill=POS, stroke=POS, sw=0))
        P.append(line(vx, top, vx, oy, color=POS, sw=1, dash="2,2"))
        P.append(text(vx, top - 12, "↯ переповнення", size=10, color=POS, bold=True))

    # підпис проміжку
    P.append(text(420, oy + 50, "час між переповненнями = (макс + 1) × тривалість тіку",
                  size=11, color=INK, bold=True))
    render("img/overflow.svg", W, H, *P)


# ── overflow-interrupt: переповнення піднімає переривання → обробник ──────────
# Ідея: ланцюг «лічильник → обнулився → переривання → ISR» — таймер сам сповіщає.
def fig_overflow_interrupt():
    W, H = 940, 300
    P = []
    P.append(text(W / 2, 30, "Переповнення таймер перетворює на переривання",
                  size=17, bold=True))

    cy = 130
    # лічильник (рамка)
    b1, w1, h1 = textbox(150, cy, "лічильник\nросте з тіками", size=12.5, bold=True,
                         fill=FILL, stroke=INK, min_w=170)
    P.append(b1)
    # подія обнулення
    b2, w2, h2 = textbox(400, cy, "↯ обнулився\n(переповнення)", size=12.5, bold=True,
                         color=POS, fill="#fdecea", stroke=POS, min_w=170)
    P.append(b2)
    # переривання
    b3, w3, h3 = textbox(640, cy, "переривання\nтаймера", size=12.5, bold=True,
                         color=NEG, fill="#eaf0fd", stroke=NEG, min_w=150)
    P.append(b3)
    # обробник
    b4, w4, h4 = textbox(840, cy, "обробник\n(ISR)", size=12.5, bold=True,
                         color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=110)
    P.append(b4)

    P.append(arrow(150 + w1 / 2, cy, 400 - w2 / 2, cy, color=INK))
    P.append(arrow(400 + w2 / 2, cy, 640 - w3 / 2, cy, color=POS))
    P.append(arrow(640 + w3 / 2, cy, 840 - w4 / 2, cy, color=NEG))

    P.append(text(W / 2, 230, "таймер лічить час, а переривання миттєво сповіщає, "
                  "коли проміжок минув — без опитування в циклі",
                  size=11.5, color=INK))
    render("img/overflow-interrupt.svg", W, H, *P)


# ── period-reload: авто-перезавантаження на заданому ВЕРХУ ────────────────────
# Ідея: пилка скидається не на повному діапазоні, а на меншому ВЕРХУ → свій період.
def fig_period_reload():
    W, H = 940, 380
    P = []
    P.append(text(W / 2, 30, "Авто-перезавантаження: скид на власному ВЕРХУ задає період",
                  size=17, bold=True))

    ox, oy = 100, 280
    full = 110                   # рівень повного максимуму
    topv = 175                   # рівень ВЕРХУ (нижче за макс)
    right = 870
    P.append(arrow(ox, oy, ox, 90, color=INK, sw=1.8))
    P.append(arrow(ox, oy, right, oy, color=INK, sw=1.8))
    P.append(text(ox - 12, 100, "значення", size=11, color=INK, bold=True, anchor="end"))
    P.append(text(right, oy + 22, "час", size=11, color=INK, anchor="end"))

    # макс (недосяжний) і ВЕРХ
    P.append(line(ox, full, right, full, color=MUTED, sw=1, dash="3,3"))
    P.append(text(ox - 12, full + 4, "макс", size=10, color=MUTED, anchor="end"))
    P.append(line(ox, topv, right, topv, color=FIELD, sw=1.3, dash="5,3"))
    P.append(text(ox - 12, topv + 4, "ВЕРХ", size=11, color=FIELD, bold=True, anchor="end"))

    # чотири короткі зубці до ВЕРХУ
    step = 175
    xs, ys = [ox], [oy]
    x = ox
    for _ in range(4):
        xs += [x + step, x + step]
        ys += [topv, oy]
        x += step
    pts = " ".join("%.1f,%.1f" % (a, b) for a, b in zip(xs, ys))
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, FIELD))

    # позначки «період» між першими двома скидами
    P.append(line(ox, oy + 34, ox + step, oy + 34, color=NEG, sw=1.4))
    P.append(text(ox + step / 2, oy + 50, "один період", size=11, color=NEG, bold=True))
    for vx in (ox + step, ox + 2 * step, ox + 3 * step, ox + 4 * step):
        P.append(circle(vx, topv, 4.5, fill=POS, stroke=POS, sw=0))

    P.append(text(620, oy + 50, "кожне досягнення ВЕРХУ — період і переривання",
                  size=11, color=INK, bold=True))
    render("img/period-reload.svg", W, H, *P)


# ── period-formula: період = ВЕРХ × тривалість тіку ──────────────────────────
# Ідея: дві ручки (передільник→тік, ВЕРХ) множаться в період; конкретний приклад.
def fig_period_formula():
    W, H = 940, 330
    P = []
    P.append(text(W / 2, 30, "Формула періоду: дві ручки — тривалість тіку та ВЕРХ",
                  size=17, bold=True))

    cy = 120
    b1, w1, h1 = textbox(190, cy, "тривалість тіку\n(задає передільник)", size=12.5,
                         bold=True, color=NEG, fill="#eaf0fd", stroke=NEG, min_w=200)
    P.append(b1)
    P.append(text(360, cy + 6, "×", size=24, bold=True, color=INK))
    b2, w2, h2 = textbox(520, cy, "ВЕРХ\n(скільки тіків лічити)", size=12.5,
                         bold=True, color=FIELD, fill="#e9f7ef", stroke=FIELD, min_w=200)
    P.append(b2)
    P.append(text(700, cy + 6, "=", size=24, bold=True, color=INK))
    b3, w3, h3 = textbox(820, cy, "період", size=14, bold=True,
                         fill=FILL, stroke=INK, min_w=120)
    P.append(b3)

    # конкретний приклад ESP32 — моноширинний блок
    bx, by, bw, bh = 150, 195, 640, 100
    P.append(rect(bx, by, bw, bh, fill="#f7f9fb", stroke=MUTED, sw=1.3, rx=8))
    mono = "'Consolas', 'DejaVu Sans Mono', monospace"
    rows = [
        "ESP32: частота 80 МГц, передільник ÷80  →  тік = 1 мкс",
        "ВЕРХ = 1000  →  період = 1000 × 1 мкс = 1 мс",
    ]
    for i, r in enumerate(rows):
        P.append('<text x="%.1f" y="%.1f" font-family="%s" font-size="14" fill="%s">%s</text>'
                 % (bx + 22, by + 38 + i * 30, mono, INK, esc(r)))
    render("img/period-formula.svg", W, H, *P)


# ── choosing: один період = різні пари «тік × ВЕРХ» ──────────────────────────
# Ідея: три рядки множень дають ту саму 1 мс; звичай — дрібний тік + число ВЕРХУ.
def fig_choosing():
    W, H = 940, 340
    P = []
    P.append(text(W / 2, 30, "Один період — різні пари «тік × ВЕРХ»",
                  size=17, bold=True))

    rows = [
        ("тік 1 мкс", "× ВЕРХ 1000", "= 1 мс", True),    # звичний — підсвітити
        ("тік 10 мкс", "× ВЕРХ 100", "= 1 мс", False),
        ("тік 100 мкс", "× ВЕРХ 10", "= 1 мс", False),
    ]
    y0, dy = 95, 62
    for i, (tick, top, res, hi) in enumerate(rows):
        y = y0 + i * dy
        fill = "#e9f7ef" if hi else FILL
        stroke = FIELD if hi else MUTED
        b1, w1, h1 = textbox(230, y, tick, size=13, bold=True, color=NEG,
                             fill="#eaf0fd", stroke=NEG, min_w=150)
        P.append(b1)
        b2, w2, h2 = textbox(440, y, top, size=13, bold=True, color=INK,
                             fill=fill, stroke=stroke, min_w=160)
        P.append(b2)
        b3, w3, h3 = textbox(650, y, res, size=13, bold=True, color=FIELD,
                             fill="#e9f7ef", stroke=FIELD, min_w=110)
        P.append(b3)
        if hi:
            P.append(text(810, y + 4, "← звичай", size=12, color=FIELD, bold=True, anchor="start"))

    fr, w, h = textbox(W / 2, 300,
                       "беруть дрібний тік (тонше зерно), період виставляють числом ВЕРХУ; "
                       "ВЕРХ мусить уміститися в розрядність лічильника",
                       size=11.5, color=INK, fill="#f7f9fb", stroke=MUTED)
    P.append(fr)
    render("img/choosing.svg", W, H, *P)


# ── millis-wraparound: правильне віднімання vs хибне порівняння ───────────────
# Ідея: пилка millis() з wrap; дві рамки — ПРАВИЛЬНО (віднімання) / НЕПРАВИЛЬНО.
def fig_millis_wraparound():
    W, H = 960, 400
    P = []
    P.append(text(W / 2, 30, "Переповнення millis(): чому віднімання все одно працює",
                  size=17, bold=True))

    # маленька пилка millis() згори
    ox, oy = 80, 195
    top = 90
    P.append(arrow(ox, oy, 700, oy, color=INK, sw=1.8))
    xs = [ox, 300, 300, 560, 560]
    ys = [oy, top, oy, top, oy]
    pts = " ".join("%.1f,%.1f" % (a, b) for a, b in zip(xs, ys))
    P.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round" stroke-linecap="round"/>' % (pts, FIELD))
    P.append(line(ox, top, 620, top, color=MUTED, sw=1, dash="3,3"))
    P.append(text(ox - 8, top + 4, "2³²", size=10, color=POS, bold=True, anchor="end"))
    for vx in (300, 560):
        P.append(circle(vx, top, 4, fill=POS, stroke=POS, sw=0))
    P.append(text(300, top - 10, "↯ wrap (~49.7 дня)", size=10, color=POS, bold=True))

    # дві рамки під графіком
    mono = "'Consolas', 'DejaVu Sans Mono', monospace"
    # ПРАВИЛЬНО
    P.append(rect(60, 250, 420, 120, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=10))
    P.append(text(270, 276, "ПРАВИЛЬНО (стійко до wrap)", size=12, color=FIELD, bold=True))
    P.append('<text x="80" y="306" font-family="%s" font-size="14" fill="%s">if (millis() - last >= interval)</text>'
             % (mono, INK))
    P.append(text(270, 334, "беззнакове віднімання саме", size=11, color=INK))
    P.append(text(270, 352, "компенсує wrap — працює завжди", size=11, color=INK))
    # НЕПРАВИЛЬНО
    P.append(rect(500, 250, 420, 120, fill="#fdf2f2", stroke=POS, sw=1.8, rx=10))
    P.append(text(710, 276, "НЕПРАВИЛЬНО (ламається на wrap)", size=12, color=POS, bold=True))
    P.append('<text x="520" y="306" font-family="%s" font-size="14" fill="%s">if (millis() &gt;= last + interval)</text>'
             % (mono, INK))
    P.append(text(710, 334, "після переповнення порівняння", size=11, color=INK))
    P.append(text(710, 352, "збивається — подія застрягає", size=11, color=INK))
    render("img/millis-wraparound.svg", W, H, *P)


# ── clock: беззнакове віднімання по колу (циферблат) ─────────────────────────
# Ідея: кільце 0…2³²; last біля MAX, now обернувся в 4, різниця по колу = 10.
def fig_clock():
    W, H = 900, 340
    P = []
    P.append(text(W / 2, 30, "Беззнакове віднімання — як на циферблаті",
                  size=17, bold=True))

    cx, cy, r = 240, 185, 100
    P.append(circle(cx, cy, r, fill="none", stroke=MUTED, sw=1.8))
    P.append(text(cx, cy - r - 12, "0 / 2³²", size=11, color=INK, bold=True))

    import math
    # last біля MAX (трохи лівіше верху), now обернувся (трохи правіше верху)
    a_last = math.radians(-90 - 18)
    a_now = math.radians(-90 + 14)
    lx, ly = cx + r * math.cos(a_last), cy + r * math.sin(a_last)
    nx, ny = cx + r * math.cos(a_now), cy + r * math.sin(a_now)
    P.append(circle(lx, ly, 6, fill=POS, stroke=POS, sw=1))
    P.append(text(lx - 14, ly - 10, "last ≈ MAX", size=10, color=POS, bold=True, anchor="end"))
    P.append(circle(nx, ny, 6, fill=FIELD, stroke=FIELD, sw=1))
    P.append(text(nx + 14, ny - 10, "now = 4", size=10, color=FIELD, bold=True, anchor="start"))
    P.append(text(cx, cy - 4, "проміжок", size=11, color=INK, bold=True))
    P.append(text(cx, cy + 14, "= 10 мс", size=11, color=INK))

    # пояснення-блок праворуч
    mono = "'Consolas', 'DejaVu Sans Mono', monospace"
    P.append(rect(430, 110, 430, 150, fill="#fbfbfb", stroke=MUTED, sw=1.4, rx=10))
    P.append(text(645, 134, "Через переповнення:", size=12, color=INK, bold=True))
    rows = [
        ("last = 4 294 967 290   (≈ MAX)", INK),
        ("за 10 мс now = 4   (обернувся)", INK),
        ("now − last = (4 − last) mod 2³²", NEG),
        ("= 10  ✓  правильний проміжок", FIELD),
    ]
    for i, (rrow, col) in enumerate(rows):
        P.append('<text x="452" y="%d" font-family="%s" font-size="13" fill="%s">%s</text>'
                 % (162 + i * 24, mono, col, esc(rrow)))
    P.append(text(W / 2, 305, "як на 12-годинному циферблаті: «2 − 10» = 4 години, "
                  "а не −8 — лічильник теж по колу", size=11.5, color=INK))
    render("img/clock.svg", W, H, *P)


# ── right-vs-wrong: правильна форма vs хибна на переповненні (вставка math) ───
# Ідея: пряме зіставлення двох виразів і що стається з кожним на wrap.
def fig_right_vs_wrong():
    W, H = 940, 330
    P = []
    P.append(text(W / 2, 30, "На переповненні: віднімання тримається, порівняння зривається",
                  size=17, bold=True))

    mono = "'Consolas', 'DejaVu Sans Mono', monospace"
    # ліворуч — правильно
    P.append(rect(60, 70, 400, 210, fill="#f3faf4", stroke=FIELD, sw=1.8, rx=10))
    P.append(text(260, 98, "ПРАВИЛЬНО", size=13, color=FIELD, bold=True))
    P.append('<text x="82" y="134" font-family="%s" font-size="15" fill="%s">now - last &gt;= interval</text>'
             % (mono, INK))
    P.append(text(260, 172, "різниця беззнакова — за модулем 2³²", size=11.5, color=INK))
    P.append(text(260, 196, "wrap «само себе компенсує»", size=11.5, color=INK))
    P.append(text(260, 230, "працює через переповнення", size=12, color=FIELD, bold=True))
    P.append(text(260, 254, "(і завжди поза ним)", size=11, color=MUTED))

    # праворуч — хибно
    P.append(rect(480, 70, 400, 210, fill="#fdf2f2", stroke=POS, sw=1.8, rx=10))
    P.append(text(680, 98, "ХИБНО", size=13, color=POS, bold=True))
    P.append('<text x="502" y="134" font-family="%s" font-size="15" fill="%s">now &gt;= last + interval</text>'
             % (mono, INK))
    P.append(text(680, 172, "last + interval теж обертається", size=11.5, color=INK))
    P.append(text(680, 196, "порівняння на мить бреше", size=11.5, color=INK))
    P.append(text(680, 230, "таймер застрягає до обороту", size=12, color=POS, bold=True))
    P.append(text(680, 254, "(побачити в розробці майже нереально)", size=10.5, color=MUTED))

    P.append(arrow(460, 175, 480, 175, color=MUTED))
    render("img/right-vs-wrong.svg", W, H, *P)


if __name__ == "__main__":
    fig_overflow()
    fig_overflow_interrupt()
    fig_period_reload()
    fig_period_formula()
    fig_choosing()
    fig_millis_wraparound()
    fig_clock()
    fig_right_vs_wrong()
    print("OK: 8 figures -> img/")
