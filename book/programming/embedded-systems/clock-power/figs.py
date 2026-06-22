# -*- coding: utf-8 -*-
"""Фігури до теми «Тактування й живлення» та її вставок (кварц, дерево тактування).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

GOLD = "#b9851f"   # акцент «увага/число» (теплий), у межах єдиної гами
AMBER_FILL = "#fdf6e3"
GREEN_FILL = "#eef6ef"


# ── 1. Такт як пульс: на кожному фронті ядро робить крок ──────────────────────
def fig_clock_pulse():
    W, H = 760, 320
    f = [text(W / 2, 28, "Такт — спільний пульс чипа: на кожному фронті ядро робить крок", size=16, bold=True)]
    f.append(text(W / 2, 50, "прямокутна хвиля сталої частоти; період T = 1/f", size=12, color=MUTED, italic=True))

    lo, hi = 200, 138       # рівні «0» та «1»
    x0 = 90
    cells = 5               # повних періодів
    cw = 50                 # півперіод
    # меандр
    d = ["M %.0f,%.0f" % (x0, lo)]
    x = x0
    for i in range(cells):
        d.append("V %.0f H %.0f" % (hi, x + cw))      # фронт угору + верх
        d.append("V %.0f H %.0f" % (lo, x + 2 * cw))  # фронт униз + низ
        x += 2 * cw
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6" stroke-linejoin="miter"/>'
             % (" ".join(d), INK))

    # позначки рівнів
    f.append(text(x0 - 8, hi + 6, "1", size=11, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, lo + 6, "0", size=11, color=MUTED, anchor="end"))

    # «крок!» на кожному висхідному фронті
    for i in range(cells):
        fx = x0 + cw + i * 2 * cw
        f.append(circle(fx, hi, 4, fill=POS, stroke=POS, sw=0))
        f.append(arrow(fx, hi - 8, fx, hi - 30, color=POS, sw=1.8))
        f.append(text(fx, hi - 36, "крок", size=10, color=POS, bold=True))

    # період T між двома висхідними фронтами
    a, b = x0 + cw, x0 + 3 * cw
    yT = lo + 26
    f.append(line(a, lo, a, yT + 6, color=MUTED, sw=1, dash="2,3"))
    f.append(line(b, lo, b, yT + 6, color=MUTED, sw=1, dash="2,3"))
    mid = (a + b) / 2
    f.append(arrow(mid, yT, a, yT, color=MUTED, sw=1.4))
    f.append(arrow(mid, yT, b, yT, color=MUTED, sw=1.4))
    f.append(text(mid, yT - 6, "T", size=13, color=INK, bold=True))

    box = fitbox(500, 250, 240, 52, "f = 80 МГц → T = 1/f = 12.5 нс\n80 млн кроків за секунду",
                 size=12, bold=True, fill=AMBER_FILL, stroke=GOLD, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "clock-pulse.svg"), W, H, *f)


# ── 2. Джерела такту: RC, кварц, PLL ──────────────────────────────────────────
def fig_clock_sources():
    W, H = 900, 320
    f = [text(W / 2, 28, "Звідки береться такт: внутрішній RC, кварц і множення PLL", size=17, bold=True)]
    f.append(text(W / 2, 50, "вибір між дешевизною й точністю", size=12, color=MUTED, italic=True))

    # RC
    f.append(rect(40, 84, 250, 150, fill="#fbfbfb", stroke=MUTED, sw=2))
    f.append(text(165, 108, "Внутрішній RC", size=13, color=INK, bold=True))
    f.append('<path d="M 92,146 q 12,-20 24,0 q 12,20 24,0 q 12,-20 24,0" fill="none" stroke="%s" stroke-width="2"/>' % MUTED)
    f.append(text(165, 176, "усередині чипа · миттєвий старт", size=10, color=MUTED))
    f.append(text(165, 196, "дешево, без зовнішніх деталей", size=10, color=MUTED))
    f.append(text(165, 220, "неточно: ±1–5 %", size=12, color=POS, bold=True))

    # Кварц
    f.append(rect(325, 84, 250, 150, fill="#fbfbfb", stroke=NEG, sw=2))
    f.append(text(450, 108, "Кварцовий резонатор", size=13, color=NEG, bold=True))
    f.append(line(420, 134, 420, 162, color=INK, sw=2))
    f.append(rect(428, 132, 44, 32, fill="#eef3ff", stroke=INK, sw=1.6, rx=0))
    f.append(line(480, 134, 480, 162, color=INK, sw=2))
    f.append(text(450, 186, "зовнішня деталь (кристалик)", size=10, color=MUTED))
    f.append(text(450, 206, "повільніший старт, трохи дорожче", size=10, color=MUTED))
    f.append(text(450, 226, "дуже точно: ±10–50 ppm", size=12, color=FIELD, bold=True))

    # PLL
    f.append(rect(610, 84, 250, 150, fill="#fbfbfb", stroke="#cfcfcf", sw=2))
    f.append(text(735, 108, "PLL — множник частоти", size=13, color=INK, bold=True))
    f.append(rect(628, 140, 84, 40, fill=BG, stroke=INK, sw=1.8, rx=4))
    f.append(text(670, 160, "кварц", size=12, color=INK, bold=True))
    f.append(text(670, 176, "40 МГц", size=10, color=MUTED))
    f.append(rect(742, 140, 50, 40, fill=BG, stroke=INK, sw=1.8, rx=4))
    f.append(text(767, 166, "×12", size=12, color=INK, bold=True))
    f.append(arrow(712, 160, 740, 160, color=INK, sw=1.8))
    f.append(rect(628, 192, 164, 30, fill=BG, stroke=INK, sw=1.8, rx=4))
    f.append(text(710, 212, "ядро 240 МГц", size=12, color=INK, bold=True))
    f.append(line(767, 180, 720, 192, color=INK, sw=1.6))

    box = fitbox(120, 270, 660, 36,
                 "Більшість МК мають і внутрішній RC, і вхід для кварцу — джерело обирають під задачу.",
                 size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "clock-sources.svg"), W, H, *f)


# ── 3. Точність такту: коли вона критична (кварц vs RC у зв'язку) ──────────────
def fig_clock_accuracy():
    W, H = 900, 410
    f = [text(W / 2, 28, "Точність такту: коли вона критична", size=18, bold=True)]
    f.append(text(W / 2, 50, "приймач зчитує біти за власним тактом — якщо він «тікає», момент схибить",
                  size=12, color=MUTED, italic=True))

    bits = ["1", "0", "1", "1", "0", "0", "1", "0"]
    bx, by, bw, bh = 80, 92, 92, 40
    f.append(text(bx - 10, by + 27, "дані:", size=11, color=MUTED, anchor="end", bold=True))
    for i, b in enumerate(bits):
        x = bx + i * bw
        f.append(rect(x, by, bw, bh, fill="#f3f6fb", stroke=INK, sw=1.2, rx=0))
        f.append(text(x + bw / 2, by + 27, b, size=14, color=INK, bold=True))

    base = by + bh  # 132
    # кварц — рівні семпли точно в центрах
    f.append(text(bx - 10, 196, "Кварц", size=11, color=FIELD, anchor="end", bold=True))
    f.append(text(bx - 10, 212, "±20 ppm", size=9, color=MUTED, anchor="end"))
    for i in range(len(bits)):
        cx = bx + i * bw + bw / 2
        f.append(circle(cx, 200, 3, fill=FIELD, stroke=FIELD, sw=0))
        f.append(line(cx, 200, cx, base + 2, color=FIELD, sw=1.8))
        f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (cx, 200, cx, base + 2, FIELD))
    f.append(text(bx, 232, "усі біти зчитано вірно", size=12, color=FIELD, anchor="start", bold=True))

    # RC — момент «пливе», семпли зсуваються
    f.append(text(bx - 10, 300, "RC", size=11, color=POS, anchor="end", bold=True))
    f.append(text(bx - 10, 316, "±3 %", size=9, color=MUTED, anchor="end"))
    drift = 13
    for i in range(len(bits)):
        cx = bx + bw / 2 + i * (bw + drift)
        if cx > bx + len(bits) * bw:   # вийшло за останній біт — хибне зчитування
            col = POS
        else:
            col = "#c89b86"
        f.append(circle(cx, 304, 3, fill=col, stroke=col, sw=0))
        f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (cx, 304, cx, base + 2, col))
    f.append(text(bx, 336, "момент «поплив» → хибний біт", size=12, color=POS, anchor="start", bold=True))

    box = fitbox(120, 374, 660, 34,
                 "Кварц відхиляється у тисячі разів менше за RC — для зв'язку це межа між «чисто» і «каша».",
                 size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "clock-accuracy.svg"), W, H, *f)


# ── 4. Тактове дерево: один пульс — багато ритмів ─────────────────────────────
def fig_clock_tree():
    W, H = 880, 440
    f = [text(W / 2, 28, "Тактове дерево: один пульс — багато ритмів", size=18, bold=True)]
    f.append(text(W / 2, 50, "майстер-частота ділиться на простих дільниках для різних споживачів",
                  size=12, color=MUTED, italic=True))

    # майстер
    mx, my = 40, 196
    f.append(rect(mx, my, 150, 76, fill="#fbecec", stroke=POS, sw=1.8, rx=4))
    f.append(text(mx + 75, my + 30, "Майстер", size=13, color=POS, bold=True))
    f.append(text(mx + 75, my + 50, "240 МГц", size=10, color=MUTED))
    root = (mx + 150, my + 38)

    # ядро — напряму
    f.append(line(root[0], root[1], 560, 130, color=FIELD, sw=2.2))
    f.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
             % (root[0], root[1], 558, 132, FIELD))
    f.append(text(380, 120, "напряму", size=10, color=MUTED, italic=True))
    f.append(rect(560, 110, 200, 44, fill=BG, stroke=INK, sw=1.8, rx=4))
    f.append(text(660, 130, "Ядро", size=13, color=INK, bold=True))
    f.append(text(660, 148, "240 МГц", size=10, color=MUTED))

    # гілки через дільники
    branches = [("÷2", "Шина", "120 МГц", 222),
                ("÷8", "Таймер", "30 МГц", 312),
                ("÷64", "UART-такт", "3.75 МГц", 402)]
    for div, name, freq, y in branches:
        f.append(line(root[0], root[1], 360, y + 22, color=MUTED, sw=2))
        f.append(rect(360, y, 70, 44, fill=BG, stroke=INK, sw=1.8, rx=4))
        f.append(text(395, y + 27, div, size=12, color=INK, bold=True))
        f.append('<line x1="430" y1="%.0f" x2="558" y2="%.0f" stroke="%s" stroke-width="2.2" marker-end="url(#arrow)"/>'
                 % (y + 22, y + 22, FIELD))
        f.append(rect(560, y, 200, 44, fill=BG, stroke=INK, sw=1.8, rx=4))
        f.append(text(660, y + 22, name, size=13, color=INK, bold=True))
        f.append(text(660, y + 40, freq, size=10, color=MUTED))

    box = fitbox(150, 414, 580, 30,
                 "Рідше цокає — менше споживає: поділ частоти ще й ощадливий.",
                 size=12, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "clock-tree.svg"), W, H, *f)


# ── 5. Сходи сну: що вимкнено, скільки їсть, як швидко прокидається ────────────
def fig_sleep_modes():
    W, H = 920, 470
    f = [text(W / 2, 28, "Сходи сну: вимикаємо те, що не потрібно", size=18, bold=True)]
    f.append(text(W / 2, 50, "що нижче — то менше споживання, але повільніше прокидання й більше втраченого стану",
                  size=12, color=MUTED, italic=True))

    cols = [("Ядро", 250), ("Периферія", 340), ("RAM", 430), ("Будильник", 525),
            ("споживання", 660), ("прокидання", 820)]
    f.append(text(70, 100, "режим", size=11, color=INK, anchor="start", bold=True))
    for label, x in cols:
        f.append(text(x, 100, label, size=11, color=INK, bold=True))
    f.append(line(60, 112, 880, 112, color="#e4e4e4", sw=1.4))

    # рядки: (назва, [ядро,периф,ram,буд] стани, ширина-бар, колір-бар, текст-бар, прокидання)
    ON, OFF, PART = "on", "off", "part"
    rows = [
        ("Активний",     [ON, ON, ON, ON],     120, POS,  "повне",       "—"),
        ("Легкий сон",   [OFF, ON, ON, ON],     48, GOLD, "середнє",     "миттєво"),
        ("Глибокий сон", [OFF, OFF, PART, ON],   6, FIELD, "мікроампери", "повільніше"),
    ]
    ry, rh = 124, 64
    for ri, (name, states, barw, barc, bartxt, wake) in enumerate(rows):
        y = ry + ri * (rh + 16)
        f.append(rect(60, y, 820, rh, fill="#fcfcfc", stroke="#e4e4e4", sw=1.2, rx=8))
        f.append(text(74, y + 34, name, size=12, color=INK, anchor="start", bold=True))
        cy = y + 30
        for st, (_, cx) in zip(states, cols[:4]):
            if st == ON:
                f.append(circle(cx, cy, 7, fill=FIELD, stroke="#0d5a23", sw=1.2))
            elif st == OFF:
                f.append(circle(cx, cy, 7, fill=BG, stroke=MUTED, sw=1.6))
            else:  # PART
                f.append(circle(cx, cy, 7, fill="#f3d27a", stroke=GOLD, sw=1.4))
        # бар споживання
        f.append(rect(600, y + 20, 120, 18, fill="#f1f1f1", stroke=MUTED, sw=1, rx=0))
        f.append(rect(600, y + 20, barw, 18, fill=barc, stroke=barc, sw=0, rx=0))
        f.append(text(660, y + 56, bartxt, size=10, color=barc, bold=True))
        f.append(text(820, y + 34, wake, size=11, color=INK, bold=True))

    ly = ry + 3 * (rh + 16) + 4
    f.append(text(250, ly, "● увімкнено", size=10, color=FIELD, anchor="start", bold=True))
    f.append(text(380, ly, "○ вимкнено", size=10, color=MUTED, anchor="start", bold=True))
    f.append(text(500, ly, "◐ лише крихта стану", size=10, color=GOLD, anchor="start", bold=True))

    box = fitbox(120, ly + 14, 680, 56,
                 "Прокидає подія: ніжка, маловитратний таймер-будильник або дані.\n"
                 "Робота наскоками (duty cycling): спить ~99 % часу — звідси місяці від батарейки.",
                 size=11, bold=True, fill=GREEN_FILL, stroke=FIELD, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "sleep-modes.svg"), W, H, *f)


# ── 6. Робота наскоками: піки струму на тлі довгого сну ───────────────────────
def fig_duty_cycle():
    W, H = 900, 400
    f = [text(W / 2, 28, "Робота наскоками: короткі піки струму на тлі довгого сну", size=17, bold=True)]
    f.append(text(W / 2, 50, "довгі долини сну тягнуть середній струм донизу", size=12, color=MUTED, italic=True))

    # осі
    ox, oy = 90, 320
    f.append('<line x1="%d" y1="%d" x2="%d" y2="90" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (ox, oy, ox, INK))
    f.append(text(ox - 8, 100, "струм", size=11, color=INK, anchor="end", bold=True))
    f.append('<line x1="%d" y1="%d" x2="860" y2="%d" stroke="%s" stroke-width="2" marker-end="url(#arrow)"/>'
             % (ox, oy, oy, INK))
    f.append(text(852, oy + 18, "час", size=11, color=INK, anchor="start"))

    top = 110
    # «без сну» — пунктир угорі
    f.append(line(ox, top, 840, top, color=MUTED, sw=1.4, dash="6,4"))
    f.append(text(840, top - 6, "без сну: 40 мА весь час", size=10, color=MUTED, anchor="end", italic=True))

    # піки струму
    peaks = [150, 340, 530, 720]
    pw = 16
    d = ["M %d,%d" % (ox, oy)]
    for px in peaks:
        d.append("H %d V %d H %d V %d" % (px, top, px + pw, oy))
    d.append("H 840")
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.4"/>' % (" ".join(d), POS))
    for px in peaks:
        f.append(text(px + pw / 2, top - 8, "40 мА", size=9, color=POS, bold=True))
    f.append(text(peaks[0] + pw / 2, oy + 16, "100 мс", size=9, color=POS))

    # період 10 с
    a, b = peaks[0] + pw / 2, peaks[1] + pw / 2
    mid = (a + b) / 2
    f.append('<line x1="%.0f" y1="350" x2="%.0f" y2="350" stroke="%s" stroke-width="1.4" marker-end="url(#arrow)"/>'
             % (mid, a, MUTED))
    f.append('<line x1="%.0f" y1="350" x2="%.0f" y2="350" stroke="%s" stroke-width="1.4" marker-end="url(#arrow)"/>'
             % (mid, b, MUTED))
    f.append(text(mid, 364, "10 с", size=10, color=INK, bold=True))

    # сон і середній
    f.append(line(ox, 314, 840, 314, color=FIELD, sw=1.8, dash="4,3"))
    f.append(text(840, 308, "сон: 10 мкА", size=10, color=FIELD, anchor="end", bold=True))
    f.append(text(ox + 6, 302, "середній ≈ 0.41 мА", size=11, color=FIELD, anchor="start", bold=True))

    box = fitbox(556, 96, 300, 56,
                 "1000 мА·год / 0.41 мА ≈ 102 доби\nбез сну: лише ~1 доба",
                 size=11, bold=True, fill=AMBER_FILL, stroke=GOLD, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "duty-cycle.svg"), W, H, *f)


# ── 7. Кварц на платі: схема під'єднання (вставка comp-crystal) ────────────────
def fig_crystal_circuit():
    W, H = 900, 400
    f = [text(W / 2, 28, "Як кварц під'єднано: дві ніжки й дві навантажувальні ємності", size=17, bold=True)]
    f.append(text(W / 2, 50, "осцилятор у чипі розгойдує кварц; навантажувальні C задають точну частоту",
                  size=11, color=MUTED, italic=True))

    # чіп
    f.append(rect(70, 138, 200, 172, fill="#f4f7fb", stroke=INK, sw=2.2))
    f.append(text(170, 172, "ESP32", size=13, color=INK, bold=True))
    f.append(text(170, 192, "осцилятор Пірса", size=10, color=MUTED))
    f.append(text(170, 208, "(підсилювач)", size=9, color=MUTED))
    f.append(text(262, 176, "XTAL_P", size=9, color=NEG, anchor="end", bold=True))
    f.append(text(262, 254, "XTAL_N", size=9, color=NEG, anchor="end", bold=True))

    # лінії до кварцу
    f.append(line(270, 180, 540, 180, color=INK, sw=2))
    f.append(line(270, 258, 540, 258, color=INK, sw=2))
    f.append(line(540, 180, 540, 202, color=INK, sw=2))
    f.append(line(540, 258, 540, 236, color=INK, sw=2))
    f.append(line(518, 202, 562, 202, color=INK, sw=2.4))
    f.append(line(518, 236, 562, 236, color=INK, sw=2.4))
    f.append(rect(525, 207, 30, 24, fill="#eef0f5", stroke=INK, sw=2, rx=2))
    f.append(text(572, 214, "кварц", size=11, color=INK, anchor="start", bold=True))
    f.append(text(572, 230, "40 МГц", size=11, color=INK, anchor="start", bold=True))

    # навантажувальні конденсатори
    f.append(circle(400, 180, 3.2, fill=INK, stroke=INK, sw=0))
    f.append(line(400, 180, 400, 212, color=INK, sw=2))
    f.append(line(383, 212, 417, 212, color=INK, sw=2.4))
    f.append(line(383, 220, 417, 220, color=INK, sw=2.4))
    f.append(line(400, 220, 400, 348, color=INK, sw=2))
    f.append(text(384, 170, "C", size=11, color=FIELD, bold=True))

    f.append(circle(470, 258, 3.2, fill=INK, stroke=INK, sw=0))
    f.append(line(470, 258, 470, 290, color=INK, sw=2))
    f.append(line(453, 290, 487, 290, color=INK, sw=2.4))
    f.append(line(453, 298, 487, 298, color=INK, sw=2.4))
    f.append(line(470, 298, 470, 348, color=INK, sw=2))
    f.append(text(486, 222, "C", size=11, color=FIELD, anchor="start", bold=True))

    # земля
    f.append(line(384, 348, 486, 348, color=INK, sw=2.4))
    f.append(line(419, 354, 451, 354, color=INK, sw=2.2))
    f.append(line(425, 360, 445, 360, color=INK, sw=2))
    f.append(line(431, 366, 439, 366, color=INK, sw=1.8))

    # пам'ятка
    f.append(rect(620, 150, 258, 150, fill="#fbfdfb", stroke=FIELD, sw=1.6))
    f.append(text(749, 176, "Пам'ятай", size=11, color=FIELD, bold=True))
    f.append(text(636, 204, "• навантажувальні C ≈ 10 пФ", size=10, color=INK, anchor="start"))
    f.append(text(636, 222, "  (точно — за CL кварцу)", size=9, color=MUTED, anchor="start"))
    f.append(text(636, 246, "• хибне C → частота «пливе»,", size=10, color=INK, anchor="start"))
    f.append(text(636, 264, "  Wi-Fi не під'єднується", size=10, color=POS, anchor="start"))
    f.append(text(636, 288, "• кварц і C — впритул до чипа", size=10, color=INK, anchor="start"))
    render(os.path.join(IMG, "crystal-circuit.svg"), W, H, *f)


# ── 8. Драбина точності: RC vs кварц vs TCXO, поріг для радіо (comp-crystal) ───
def fig_ppm_accuracy():
    W, H = 920, 400
    f = [text(W / 2, 28, "Що таке ppm і чому радіо потребує саме кварц", size=18, bold=True)]
    f.append(text(W / 2, 50, "точність задає дрейф часу — і чи зможе чіп узагалі під'єднатися до Wi-Fi",
                  size=11, color=MUTED, italic=True))

    cols = [("джерело такту", 70, "start"), ("точність", 410, "middle"),
            ("дрейф за добу", 590, "middle"), ("радіо?", 800, "middle")]
    for label, x, anc in cols:
        f.append(text(x, 100, label, size=11, color=INK, anchor=anc, bold=True))
    f.append(line(50, 112, 870, 112, color="#e4e4e4", sw=1.4))

    rows = [
        ("Внутрішній RC", "±1–2 % (~10 000 ppm)", "хвилини / день", "неможливе",
         "#fbecec", POS, POS),
        ("Кварц (crystal)", "±10–20 ppm", "≈ 1 с / день", "працює",
         GREEN_FILL, FIELD, FIELD),
        ("TCXO (з компенсацією)", "±1–2 ppm", "≈ 0.1 с / день", "найкраще",
         "#e9eefb", NEG, NEG),
    ]
    ry, rh = 136, 48
    for ri, (name, acc, drift, radio, fill, stroke, txtc) in enumerate(rows):
        y = ry + ri * (rh + 10)
        f.append(rect(50, y, 820, rh, fill=fill, stroke=stroke, sw=1.6, rx=8))
        f.append(text(70, y + 30, name, size=12, color=txtc, anchor="start", bold=True))
        f.append(text(410, y + 30, acc, size=11, color=INK))
        f.append(text(590, y + 30, drift, size=11, color=INK))
        f.append(text(800, y + 30, radio, size=11, color=txtc, bold=True))

    box = fitbox(120, 330, 680, 50,
                 "Wi-Fi/BT вимагають ≈ ±25 ppm і кращої — тому RC не годиться, потрібен кварц.\n"
                 "Саме радіо й диктує 40 МГц як опорну частоту (CPU 240 МГц робить PLL із неї).",
                 size=11, bold=True, fill=AMBER_FILL, stroke=GOLD, sw=1.4)
    f.append(box)
    render(os.path.join(IMG, "ppm-accuracy.svg"), W, H, *f)


# ── 9. Дерево тактування з PLL: кварц → PLL → дільники (math-clock-tree) ───────
def fig_clock_tree_pll():
    W, H = 920, 420
    f = [text(W / 2, 28, "Дерево тактування: один кварц — багато частот", size=18, bold=True)]
    f.append(text(W / 2, 50, "PLL множить опорну частоту, а дільники ділять її під кожен домен",
                  size=11, color=MUTED, italic=True))

    # кварц
    f.append(rect(50, 180, 150, 64, fill="#e9eefb", stroke=NEG, sw=1.8, rx=4))
    f.append(text(125, 206, "Кварц", size=13, color=NEG, bold=True))
    f.append(text(125, 224, "40 МГц", size=10, color=MUTED))
    f.append(arrow(200, 212, 248, 212, color=INK, sw=2.2))
    # PLL
    f.append(rect(250, 180, 140, 64, fill="#fbecec", stroke=POS, sw=1.8, rx=4))
    f.append(text(320, 206, "PLL", size=13, color=POS, bold=True))
    f.append(text(320, 224, "× 12", size=10, color=MUTED))
    f.append(arrow(390, 212, 452, 212, color=INK, sw=2.2))
    # вузол 480
    f.append(circle(470, 212, 5, fill=INK, stroke=INK, sw=0))
    f.append(text(470, 196, "480 МГц", size=11, color=INK, bold=True))
    f.append(line(470, 212, 470, 255, color=FIELD, sw=4))

    # ÷2 → CPU
    f.append(arrow(470, 180, 540, 180, color=POS, sw=2))
    f.append(rect(540, 160, 64, 40, fill=BG, stroke=POS, sw=1.6, rx=6))
    f.append(text(572, 184, "÷ 2", size=12, color=POS, bold=True))
    f.append(arrow(604, 180, 664, 180, color=POS, sw=2))
    f.append(rect(666, 154, 200, 52, fill="#fbecec", stroke=POS, sw=1.8, rx=4))
    f.append(text(766, 180, "CPU", size=13, color=POS, bold=True))
    f.append(text(766, 198, "240 МГц", size=10, color=MUTED))

    # ÷6 → APB
    f.append(arrow(470, 255, 540, 255, color=NEG, sw=2))
    f.append(rect(540, 235, 64, 40, fill=BG, stroke=NEG, sw=1.6, rx=6))
    f.append(text(572, 259, "÷ 6", size=12, color=NEG, bold=True))
    f.append(arrow(604, 255, 664, 255, color=NEG, sw=2))
    f.append(rect(666, 229, 200, 52, fill="#e9eefb", stroke=NEG, sw=1.8, rx=4))
    f.append(text(766, 255, "APB / шина", size=13, color=NEG, bold=True))
    f.append(text(766, 273, "80 МГц", size=10, color=MUTED))

    # периферія від APB
    f.append(arrow(766, 281, 766, 326, color=FIELD, sw=2))
    f.append(rect(620, 330, 292, 54, fill=GREEN_FILL, stroke=FIELD, sw=1.8, rx=4))
    f.append(text(766, 356, "Периферія: UART, таймери…", size=13, color=FIELD, bold=True))
    f.append(text(766, 374, "свої дільники від 80 МГц", size=10, color=MUTED))
    render(os.path.join(IMG, "clock-tree-pll.svg"), W, H, *f)


# ── 10. Числовий приклад: 40×12=480, ÷2=240, ÷6=80 (math-clock-tree) ───────────
def fig_clock_derive_numbers():
    W, H = 900, 366
    f = [text(W / 2, 28, "Порахуймо: з 40 МГц — у 240 МГц ядра", size=18, bold=True)]
    f.append(text(W / 2, 50, "множення в PLL, потім ділення під кожен домен — усе цілими числами",
                  size=11, color=MUTED, italic=True))

    f.append(rect(250, 78, 400, 44, fill=AMBER_FILL, stroke=GOLD, sw=1.4, rx=10))
    f.append(text(450, 106, "f(домену) = f(кварцу) × N ÷ M", size=13, color=INK, bold=True))

    rows = [
        ("PLL множить", "40 МГц × 12", "= 480 МГц", "#fbecec", POS, POS),
        ("CPU-дільник", "480 МГц ÷ 2", "= 240 МГц", "#fbecec", POS, POS),
        ("APB-дільник", "480 МГц ÷ 6", "= 80 МГц",  "#e9eefb", NEG, NEG),
    ]
    ry, rh = 138, 40
    for ri, (lbl, lhs, rhs, fill, stroke, rhsc) in enumerate(rows):
        y = ry + ri * (rh + 12)
        f.append(text(118, y + 24, lbl, size=11, color=MUTED, anchor="start"))
        f.append(rect(250, y, 400, rh, fill=fill, stroke=stroke, sw=1.4, rx=8))
        f.append(text(300, y + 24, lhs, size=12, color=INK, anchor="start", bold=True))
        f.append(text(622, y + 24, rhs, size=12, color=rhsc, anchor="end", bold=True))

    box = fitbox(140, 322, 620, 32,
                 "Дільники цілі — точно дістати можна не будь-яку частоту; беруть найближчу.",
                 size=11, bold=True, fill="#eef0f2", stroke=MUTED, sw=1.2)
    f.append(box)
    render(os.path.join(IMG, "clock-derive-numbers.svg"), W, H, *f)


if __name__ == "__main__":
    fig_clock_pulse()
    fig_clock_sources()
    fig_clock_accuracy()
    fig_clock_tree()
    fig_sleep_modes()
    fig_duty_cycle()
    fig_crystal_circuit()
    fig_ppm_accuracy()
    fig_clock_tree_pll()
    fig_clock_derive_numbers()
    print("OK: 10 figs -> ./img/")
