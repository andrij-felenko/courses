# -*- coding: utf-8 -*-
"""Фігури до теми «Давачі оточення».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

import math

# Локальні відтінки понад палітру svgkit
WARM = "#b9770e"     # тепло / ІЧ
PURP = "#8e44ad"     # газ / молекули
GREY = "#8a8a8a"


# ── 1. PIR: піроелемент і лінза Френеля ділять поле на зони ─────────────────
def fig_pir_principle():
    W, H = 720, 300
    f = [text(W / 2, 26, "PIR: лінза Френеля ділить поле зору на зони",
              size=15, bold=True)]

    # давач: корпус + два піроелементи назустріч
    f.append(rect(40, 120, 70, 70, fill="#eef6ef", stroke=FIELD, sw=1.8))
    f.append(rect(56, 134, 16, 18, fill="#fdecea", stroke=POS, sw=1.6))
    f.append(rect(56, 158, 16, 18, fill="#eaf0fd", stroke=NEG, sw=1.6))
    f.append(text(75, 205, "два піроелементи", size=10, color=INK, bold=True))
    f.append(text(75, 220, "назустріч (+ / −)", size=9.5, color=MUTED, italic=True))

    # лінза Френеля — пунктир, що ріже конус
    f.append(line(110, 120, 130, 110, color=WARM, sw=1.4))
    f.append(line(110, 190, 130, 200, color=WARM, sw=1.4))
    f.append(text(130, 250, "лінза Френеля", size=10, color=WARM, bold=True))

    # зони поля зору — віяло смуг
    cx, cy = 120, 155
    zones = 6
    for i in range(zones):
        a0 = -42 + i * (84.0 / zones)
        a1 = -42 + (i + 1) * (84.0 / zones)
        r = 300
        x0 = cx + r * math.cos(math.radians(a0))
        y0 = cy + r * math.sin(math.radians(a0))
        x1 = cx + r * math.cos(math.radians(a1))
        y1 = cy + r * math.sin(math.radians(a1))
        fill = "#fbf2e6" if i % 2 == 0 else "#ffffff"
        f.append('<polygon points="%.1f,%.1f %.1f,%.1f %.1f,%.1f" fill="%s" '
                 'stroke="%s" stroke-width="1" opacity="0.9"/>'
                 % (cx, cy, x0, y0, x1, y1, fill, WARM))
    f.append(text(360, 60, "зони (вузькі смуги поля зору)", size=10.5, color=WARM, italic=True))

    # тепле тіло, що рухається через зони
    f.append(circle(470, 150, 18, fill="#fdecea", stroke=POS, sw=1.8))
    f.append(text(470, 155, "♨", size=18, color=POS))
    f.append(arrow(498, 150, 568, 150, color=POS, sw=1.8))
    f.append(text(540, 138, "рух", size=11, color=POS, bold=True))
    f.append(text(470, 196, "тепле тіло", size=10, color=INK, bold=True))
    f.append(text(470, 211, "(само випромінює ІЧ)", size=9.5, color=MUTED, italic=True))

    f.append(text(W / 2, 282,
                  "тіло перетинає зони → елемент то гріється, то холоне → змінний сигнал",
                  size=11, color=INK, bold=True))
    render(os.path.join(IMG, "pir-principle.svg"), W, H, *f)


# ── 2. PIR бачить рух, а не присутність ─────────────────────────────────────
def fig_pir_motion():
    W, H = 700, 300
    f = [text(W / 2, 26, "PIR — давач зміни: нерухоме тепло згасає до нуля",
              size=14, bold=True)]
    # осі
    f.append(arrow(80, 235, 80, 50, color=INK, sw=1.6))
    f.append(arrow(80, 235, 640, 235, color=INK, sw=1.6))
    f.append(text(74, 60, "сигнал", size=11, color=INK, anchor="end", bold=True))
    f.append(text(620, 253, "час →", size=11, color=INK, bold=True))
    # нульова лінія
    base = 165.0
    f.append(line(80, base, 632, base, color=GREY, sw=1, dash="3,3"))
    f.append(text(96, base - 6, "0", size=10, color=GREY, anchor="end"))

    # фаза руху: сплески; фаза спокою: згасання
    pts = []
    for i in range(0, 561):
        x = 80 + i
        if i < 300:                      # рух — поперемінні сплески
            y = base - 70 * math.sin(i / 18.0) * math.exp(-((i - 150) ** 2) / 40000.0)
        else:                            # спокій — згасання до нуля
            y = base - 18 * math.exp(-(i - 300) / 70.0) * math.cos((i - 300) / 22.0)
        pts.append((x, y))
    poly = " ".join("%.1f,%.1f" % p for p in pts)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" '
             'stroke-linejoin="round"/>' % (poly, POS))

    # підписи фаз
    f.append(line(380, 60, 380, 235, color=GREY, sw=1, dash="5,4"))
    f.append(text(230, 78, "рухається → сплески", size=11, color=POS, bold=True))
    f.append(text(230, 95, "(перетин зон)", size=9.5, color=MUTED, italic=True))
    f.append(text(510, 78, "завмер → згасає", size=11, color=NEG, bold=True))
    f.append(text(510, 95, "«зник для PIR»", size=9.5, color=MUTED, italic=True))
    f.append(text(W / 2, 284,
                  "піроелемент відповідає лише на ЗМІНУ теплового потоку — як п'єзо лише на зміну сили",
                  size=10.5, color=INK, italic=True))
    render(os.path.join(IMG, "pir-motion.svg"), W, H, *f)


# ── 3. Ємнісний давач вологості ─────────────────────────────────────────────
def fig_humidity():
    W, H = 700, 280
    f = [text(W / 2, 26, "Ємнісний давач вологості: полімер вбирає воду, ємність росте",
              size=13.5, bold=True)]
    # конденсатор: дві обкладки, полімер між ними
    px, py, pw, ph = 250, 80, 200, 120
    f.append(rect(px, py, pw, 14, fill="#cfd6de", stroke=INK, sw=1.4))           # верхня обкладка
    f.append(rect(px, py + ph - 14, pw, 14, fill="#cfd6de", stroke=INK, sw=1.4)) # нижня обкладка
    f.append(rect(px, py + 14, pw, ph - 28, fill="#eef3fb", stroke=NEG, sw=1.4)) # полімер
    f.append(text(px + pw / 2, py + ph / 2 - 4, "полімер (вбирає H₂O)", size=11, color=NEG, bold=True))
    f.append(text(px + pw / 2, py + ph / 2 + 14, "велика ε", size=10, color=NEG, italic=True))
    f.append(text(px + pw / 2, py - 8, "обкладка", size=9.5, color=INK))
    f.append(text(px + pw / 2, py + ph + 18, "обкладка", size=9.5, color=INK))

    # молекули води, що дифундують усередину
    for mx, my in [(150, 100), (170, 150), (140, 175), (560, 110), (575, 160), (545, 185)]:
        f.append(circle(mx, my, 6, fill="#d6e6ff", stroke=NEG, sw=1.2))
        f.append(text(mx, my + 3, "•", size=10, color=NEG))
    f.append(arrow(180, 120, px - 6, 120, color=NEG, sw=1.5))
    f.append(arrow(540, 130, px + pw + 6, 130, color=NEG, sw=1.5))
    f.append(text(150, 90, "пара", size=10, color=NEG, bold=True))

    f.append(text(W / 2, 250, "більша вологість → більше води в полімері → більша C",
                  size=11.5, color=INK, bold=True))
    f.append(text(W / 2, 268, "це той самий ємнісний принцип — лише «ручку» ε крутить волога",
                  size=10, color=MUTED, italic=True))
    render(os.path.join(IMG, "humidity.svg"), W, H, *f)


# ── 4. Три фізики газових давачів ───────────────────────────────────────────
def fig_gas_types():
    W, H = 740, 300
    f = [text(W / 2, 26, "Три способи відчути газ — три різні класи перетворювача",
              size=14.5, bold=True)]
    cols = [
        ("MOX", "підігрітий оксид:\nадсорбція міняє опір", "резистивний", POS, 16),
        ("електрохімічний", "газ дає струм у\nмініпаливному елементі", "самогенерувальний", FIELD, 256),
        ("NDIR", "газ поглинає свою\nсмугу ІЧ; міряємо поглинання", "оптичний", PURP, 496),
    ]
    for name, what, kind, col, x in cols:
        f.append(rect(x, 52, 228, 200, fill=FILL, stroke=col, sw=1.6))
        f.append(text(x + 114, 80, name, size=14, color=col, bold=True))
        f.append(mtext(x + 114, 116, what, size=11, color=INK))
        f.append(line(x + 22, 170, x + 206, 170, color="#e4e4e4", sw=1))
        f.append(text(x + 114, 196, "клас:", size=10, color=GREY, bold=True))
        f.append(text(x + 114, 216, kind, size=11.5, color=col, bold=True))
    f.append(text(W / 2, 286, "різні класи — та сама рамка перетворювача",
                  size=11.5, color=INK, italic=True))
    render(os.path.join(IMG, "gas-types.svg"), W, H, *f)


# ── 5. Неселективність: один давач, багато газів ────────────────────────────
def fig_selectivity():
    W, H = 700, 300
    f = [text(W / 2, 26, "Дешевий газовий давач — «нюхач»: реагує на цілий букет газів",
              size=13.5, bold=True)]
    # осі
    f.append(arrow(90, 240, 90, 56, color=INK, sw=1.6))
    f.append(arrow(90, 240, 640, 240, color=INK, sw=1.6))
    f.append(text(84, 66, "сигнал", size=11, color=INK, anchor="end", bold=True))
    # стовпчики відгуку на різні гази — подібні, не розрізнити
    bars = [("чадний газ", 150, POS), ("спирт", 132, WARM),
            ("водень", 160, NEG), ("дим", 140, PURP)]
    bw, x = 90, 150
    for name, h, col in bars:
        f.append(rect(x, 240 - h, bw, h, fill=FILL, stroke=col, sw=1.6))
        f.append(text(x + bw / 2, 258, name, size=10.5, color=col, bold=True))
        f.append(text(x + bw / 2, 240 - h - 8, "↑", size=12, color=col, bold=True))
        x += bw + 30
    f.append(text(W / 2, 286,
                  "відгуки схожі → який саме газ перед ним, давач сказати не може",
                  size=11, color=INK, italic=True))
    render(os.path.join(IMG, "selectivity.svg"), W, H, *f)


# ── 6. Одна рамка перетворювача на всіх ─────────────────────────────────────
def fig_framework():
    W, H = 760, 250
    f = [text(W / 2, 26, "Будь-який давач оточення — той самий ланцюжок питань",
              size=15, bold=True)]
    steps = ["клас\nперетворювача", "передавальна\nхарактеристика",
             "дрейф\nі шум", "калібрування", "узгодження\nз входом"]
    n = len(steps)
    bw, gap = 116, 24
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    y = 90
    for i, s in enumerate(steps):
        x = x0 + i * (bw + gap)
        f.append(rect(x, y, bw, 70, fill=FILL, stroke=FIELD, sw=1.6))
        f.append(mtext(x + bw / 2, y + 30, s, size=11, color=INK, bold=True))
        if i < n - 1:
            f.append(arrow(x + bw + 2, y + 35, x + bw + gap - 2, y + 35, color=FIELD, sw=2))
    # вхідні приклади згори
    f.append(text(W / 2, 180, "рух · температура · волога · газ · тиск · світло",
                  size=12, color=WARM, bold=True))
    f.append(text(W / 2, 210, "нової теорії на кожен давач не треба — лягає кожен",
                  size=11, color=INK, italic=True))
    render(os.path.join(IMG, "framework.svg"), W, H, *f)


if __name__ == "__main__":
    fig_pir_principle()
    fig_pir_motion()
    fig_humidity()
    fig_gas_types()
    fig_selectivity()
    fig_framework()
    print("OK: фігури записано у", IMG)
